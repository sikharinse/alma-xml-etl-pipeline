"""
Alma XML ETL Pipeline

โจทย์:
- อ่านไฟล์ XML ชื่อ alma_response.xml
- แปลงข้อมูล XML เป็น records
- บันทึกออกเป็น CSV
- ใช้ Docker volume mapping เพื่อให้ output CSV ออกมาอยู่นอก container

ค่า path อ่านจาก environment variable:
- INPUT_XML  default = /app/input/alma_response.xml
- OUTPUT_CSV default = /app/output/alma_output.csv
"""

from __future__ import annotations

import csv
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any


def remove_namespace(tag: str) -> str:
    """
    XML จากระบบจริงมักมี namespace เช่น
    {http://www.loc.gov/MARC21/slim}record

    ฟังก์ชันนี้ตัด namespace ออกให้เหลือแค่ชื่อ tag เช่น record
    """
    return tag.split("}", 1)[-1] if "}" in tag else tag


def text_or_empty(element: ET.Element | None) -> str:
    """คืนค่า text ของ XML element ถ้าไม่มีให้คืน string ว่าง"""
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def normalize_space(value: str) -> str:
    """ลบช่องว่างซ้ำ และจัดข้อความให้อ่านง่าย"""
    return re.sub(r"\s+", " ", value).strip()


def find_first_text(root: ET.Element, tag_name: str) -> str:
    """
    หา text จาก tag ตัวแรกที่ชื่อ tag ตรงกัน โดยไม่สน namespace
    เช่น title, author, mms_id
    """
    for element in root.iter():
        if remove_namespace(element.tag) == tag_name:
            return normalize_space(text_or_empty(element))
    return ""


def get_subfield_text(datafield: ET.Element, code: str) -> str:
    """
    อ่าน subfield จาก MARC XML
    เช่น <subfield code="a">Introduction to ETL</subfield>
    """
    values: list[str] = []

    for child in datafield:
        if remove_namespace(child.tag) == "subfield" and child.attrib.get("code") == code:
            value = normalize_space(text_or_empty(child))
            if value:
                values.append(value)

    return " ".join(values)


def find_marc_datafield(root: ET.Element, tag: str) -> list[ET.Element]:
    """หา MARC datafield ตาม tag เช่น 245, 100, 260, 264"""
    results: list[ET.Element] = []

    for element in root.iter():
        if remove_namespace(element.tag) == "datafield" and element.attrib.get("tag") == tag:
            results.append(element)

    return results


def find_marc_controlfield(root: ET.Element, tag: str) -> str:
    """หา MARC controlfield ตาม tag เช่น 001"""
    for element in root.iter():
        if remove_namespace(element.tag) == "controlfield" and element.attrib.get("tag") == tag:
            return normalize_space(text_or_empty(element))
    return ""


def extract_record_from_xml(root: ET.Element) -> dict[str, Any]:
    """
    Extract + Transform:
    รองรับทั้ง XML แบบง่าย และ XML แบบ MARC/Alma

    output fields:
    - mms_id
    - title
    - author
    - isbn
    - publisher
    - publication_year
    - material_type
    - etl_timestamp
    """

    # 1) ลองอ่านจาก XML แบบง่ายก่อน
    simple_mms_id = find_first_text(root, "mms_id")
    simple_title = find_first_text(root, "title")
    simple_author = find_first_text(root, "author")
    simple_isbn = find_first_text(root, "isbn")
    simple_publisher = find_first_text(root, "publisher")
    simple_year = find_first_text(root, "publication_year") or find_first_text(root, "year")
    simple_material_type = find_first_text(root, "material_type")

    # 2) ถ้าเป็น MARC XML ให้ดึงจาก tag มาตรฐาน
    marc_mms_id = find_marc_controlfield(root, "001")

    title = simple_title
    author = simple_author
    isbn = simple_isbn
    publisher = simple_publisher
    publication_year = simple_year

    # MARC 245 = title
    if not title:
        fields_245 = find_marc_datafield(root, "245")
        if fields_245:
            title = normalize_space(
                f"{get_subfield_text(fields_245[0], 'a')} {get_subfield_text(fields_245[0], 'b')}"
            ).rstrip(" /")

    # MARC 100 = main author
    if not author:
        fields_100 = find_marc_datafield(root, "100")
        if fields_100:
            author = get_subfield_text(fields_100[0], "a").rstrip(",")

    # MARC 020 = ISBN
    if not isbn:
        fields_020 = find_marc_datafield(root, "020")
        if fields_020:
            isbn = get_subfield_text(fields_020[0], "a")

    # MARC 260 หรือ 264 = publisher/year
    fields_260 = find_marc_datafield(root, "260")
    fields_264 = find_marc_datafield(root, "264")
    publication_field = fields_264[0] if fields_264 else (fields_260[0] if fields_260 else None)

    if publication_field is not None:
        if not publisher:
            publisher = get_subfield_text(publication_field, "b").rstrip(",")
        if not publication_year:
            publication_year = get_subfield_text(publication_field, "c").strip(" .,")

    return {
        "mms_id": simple_mms_id or marc_mms_id,
        "title": title,
        "author": author,
        "isbn": isbn,
        "publisher": publisher,
        "publication_year": publication_year,
        "material_type": simple_material_type,
        "etl_timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def load_to_csv(record: dict[str, Any], output_csv: Path) -> None:
    """Load: บันทึก record เป็น CSV"""
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with output_csv.open("w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(record.keys()))
        writer.writeheader()
        writer.writerow(record)


def main() -> None:
    input_xml = Path(os.getenv("INPUT_XML", "/app/input/alma_response.xml"))
    output_csv = Path(os.getenv("OUTPUT_CSV", "/app/output/alma_output.csv"))

    print("Alma XML ETL Pipeline started")
    print(f"Input XML : {input_xml}")
    print(f"Output CSV: {output_csv}")

    if not input_xml.exists():
        print(f"ERROR: input file not found: {input_xml}", file=sys.stderr)
        sys.exit(1)

    tree = ET.parse(input_xml)
    root = tree.getroot()

    record = extract_record_from_xml(root)
    load_to_csv(record, output_csv)

    print("ETL completed successfully")
    print(record)


if __name__ == "__main__":
    main()
