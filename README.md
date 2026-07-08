# Alma XML ETL Pipeline

โปรเจกต์ตัวอย่างสำหรับการบ้าน/การสอนเรื่อง **Data Pipeline / ETL** โดยใช้ Python อ่านไฟล์ `alma_response.xml` แล้วบันทึกผลลัพธ์เป็นไฟล์ CSV ผ่าน Docker

## สิ่งที่โปรเจกต์นี้ทำ

```text
input/alma_response.xml
        ↓
Python ETL Pipeline
        ↓
Extract → Transform → Load
        ↓
output/alma_output.csv
```

## โครงสร้างโปรเจกต์

```text
alma-xml-etl-pipeline/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── .gitignore
├── input/
│   └── alma_response.xml
├── output/
│   └── .gitkeep
├── scripts/
│   ├── init_git_repo.sh
│   └── create_github_repo_with_gh_cli.sh
└── src/
    └── pipeline.py
```

## Data Pipeline คืออะไรในโปรเจกต์นี้

ในงานนี้ Data Pipeline คือกระบวนการไหลของข้อมูลตั้งแต่ต้นทางถึงปลายทาง

```text
XML File → Python Script → CSV File
```

โดยแบ่งเป็น ETL ได้ดังนี้

| ขั้นตอน | ความหมาย | ในโปรเจกต์นี้ |
|---|---|---|
| Extract | ดึงข้อมูลจากต้นทาง | อ่าน `alma_response.xml` |
| Transform | แปลง/จัดรูปข้อมูล | map field เช่น title, author, isbn |
| Load | บันทึกข้อมูลปลายทาง | เขียนเป็น `alma_output.csv` |

## Docker volume mapping

ใน `docker-compose.yml` มีส่วนนี้

```yaml
volumes:
  - ./input:/app/input
  - ./output:/app/output
```

ความหมายคือ

```text
./input  บนเครื่องเรา  → /app/input  ใน container
./output บนเครื่องเรา  → /app/output ใน container
```

ดังนั้นเมื่อ container สร้างไฟล์ CSV ที่ `/app/output/alma_output.csv` ไฟล์จะปรากฏบนเครื่องเราที่

```text
output/alma_output.csv
```

นี่คือเหตุผลที่ต้องใช้ volume mapping เพราะถ้าไม่ map volume ไฟล์ที่สร้างใน container อาจอยู่เฉพาะใน container และดูจากเครื่อง host ได้ไม่สะดวก

## วิธีรัน

### 1. Build image

```bash
docker compose build
```

### 2. Run pipeline

```bash
docker compose run --rm alma-xml-etl
```

### 3. ดูผลลัพธ์

หลังรันสำเร็จ จะได้ไฟล์

```text
output/alma_output.csv
```

ไฟล์นี้ถูกสร้างอยู่นอก container เพราะมีการ map volume จาก `/app/output` ใน container ออกมายัง `./output` บนเครื่อง host

## ตัวอย่าง input

ไฟล์ `input/alma_response.xml`

```xml
<bib>
  <mms_id>990000000000000000</mms_id>
  <title>Introduction to Library Data Pipeline</title>
  <author>Mahidol University Library</author>
  <isbn>9786160000000</isbn>
  <publisher>MULKC Press</publisher>
  <publication_year>2026</publication_year>
  <material_type>Book</material_type>
</bib>
```

## ตัวอย่าง output CSV

```csv
mms_id,title,author,isbn,publisher,publication_year,material_type,etl_timestamp
990000000000000000,Introduction to Library Data Pipeline,Mahidol University Library,9786160000000,MULKC Press,2026,Book,2026-07-08T15:00:00
```

## สร้าง GitHub repository

หากใช้ GitHub CLI สามารถสร้าง repo และ push ขึ้น GitHub ได้ด้วยคำสั่ง

```bash
gh repo create alma-xml-etl-pipeline --public --source=. --remote=origin --push
```

หรือสร้าง repository เปล่าบน GitHub ก่อน แล้วใช้คำสั่ง

```bash
git init
git add .
git commit -m "Initial Alma XML ETL pipeline"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/alma-xml-etl-pipeline.git
git push -u origin main
```

## คำอธิบายสั้นสำหรับส่งการบ้าน

โปรเจกต์นี้เป็นตัวอย่าง Data Pipeline สำหรับแปลงข้อมูลจากไฟล์ XML ของ Alma เป็นไฟล์ CSV โดยใช้ Python ทำขั้นตอน ETL ได้แก่ Extract อ่านไฟล์ `alma_response.xml`, Transform แปลงข้อมูลและ map field ที่ต้องการ เช่น `mms_id`, `title`, `author`, `isbn`, `publisher`, `publication_year`, และ Load บันทึกผลลัพธ์เป็น `alma_output.csv` ภายในโฟลเดอร์ `output` นอกจากนี้ยังใช้ Docker เพื่อให้สภาพแวดล้อมการรันเหมือนกันทุกเครื่อง และใช้ Docker volume mapping เพื่อเชื่อมโฟลเดอร์ `input` และ `output` ระหว่างเครื่อง host กับ container ทำให้ไฟล์ CSV ที่สร้างจาก container แสดงอยู่ภายนอก container ได้
