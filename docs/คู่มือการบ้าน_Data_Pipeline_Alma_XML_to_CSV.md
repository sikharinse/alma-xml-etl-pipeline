# คู่มือการบ้าน: Data Pipeline อ่านไฟล์ Alma XML แล้วบันทึกเป็น CSV ด้วย Docker

เอกสารนี้อธิบายโปรเจกต์การบ้านแบบเริ่มจากศูนย์ สำหรับคนที่ยังไม่คุ้นกับคำว่า Data Pipeline, ETL, Docker, Docker Compose, Volume Mapping และ GitHub

โปรเจกต์นี้ทำหน้าที่อ่านไฟล์ XML ชื่อ `alma_response.xml` แล้วใช้ Python แปลงข้อมูลออกมาเป็นไฟล์ CSV ชื่อ `alma_output.csv` โดยรันผ่าน Docker และทำให้ไฟล์ output ออกมาอยู่ข้างนอก container ด้วย Docker volume mapping

---

## 1. ภาพรวมของโปรเจกต์

โปรเจกต์นี้เป็นตัวอย่างของ **Data Pipeline** แบบง่าย

```text
input/alma_response.xml
        ↓
Python ETL Pipeline
        ↓
Extract → Transform → Load
        ↓
output/alma_output.csv
```

ความหมายคือ

1. มีไฟล์ข้อมูลต้นทางเป็น XML
2. Python อ่านข้อมูลจาก XML
3. Python แปลงข้อมูลให้อยู่ในรูปแบบที่ต้องการ
4. Python เขียนผลลัพธ์ออกมาเป็น CSV
5. Docker ช่วยให้โปรเจกต์รันได้เหมือนกันทุกเครื่อง
6. Docker volume mapping ช่วยให้ไฟล์ CSV ที่สร้างใน container ออกมาอยู่บนเครื่องจริง

---

## 2. Data Pipeline คืออะไร

**Data Pipeline** คือกระบวนการไหลของข้อมูลจากต้นทางไปยังปลายทาง

ในโปรเจกต์นี้ ข้อมูลไหลแบบนี้

```text
XML File → Python Script → CSV File
```

ถ้าเทียบกับงานจริงของห้องสมุด ข้อมูลอาจมาจาก Alma API, XML, CSV, Excel หรือ Database แล้วถูกแปลงเพื่อนำไปทำรายงาน Dashboard หรือส่งต่อให้ระบบอื่น

---

## 3. ETL คืออะไร

**ETL** ย่อมาจาก

```text
Extract → Transform → Load
```

แปลแบบง่ายคือ

| ขั้นตอน | ความหมาย | ในโปรเจกต์นี้ |
|---|---|---|
| Extract | ดึงข้อมูลจากต้นทาง | อ่านไฟล์ `alma_response.xml` |
| Transform | แปลงข้อมูล | map field เช่น title, author, isbn |
| Load | บันทึกข้อมูลปลายทาง | สร้างไฟล์ `alma_output.csv` |

ดังนั้นโปรเจกต์นี้คือ ETL ขนาดเล็กที่ทำงานกับไฟล์ XML และ CSV

---

## 4. โครงสร้างโปรเจกต์

โครงสร้างไฟล์ของโปรเจกต์เป็นแบบนี้

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
│   └── alma_output.csv
├── scripts/
│   ├── init_git_repo.sh
│   └── create_github_repo_with_gh_cli.sh
└── src/
    └── pipeline.py
```

หน้าที่ของแต่ละไฟล์

| ไฟล์ / โฟลเดอร์ | หน้าที่ |
|---|---|
| `Dockerfile` | สูตรสำหรับสร้าง Docker image |
| `docker-compose.yml` | ไฟล์สำหรับสั่งรัน container และ map volume |
| `requirements.txt` | รายชื่อ Python package ที่ต้องติดตั้ง |
| `input/` | โฟลเดอร์เก็บไฟล์ XML ต้นทาง |
| `output/` | โฟลเดอร์เก็บไฟล์ CSV ผลลัพธ์ |
| `src/pipeline.py` | โค้ด Python สำหรับทำ ETL |
| `.gitignore` | ระบุไฟล์ที่ไม่ต้องการให้ Git track |
| `README.md` | คำอธิบายโปรเจกต์ |

---

## 5. ไฟล์ input: alma_response.xml

ไฟล์ `alma_response.xml` อยู่ในโฟลเดอร์ `input`

ตัวอย่างข้อมูล

```xml
<?xml version="1.0" encoding="UTF-8"?>
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

ข้อมูลนี้เปรียบเหมือน response จากระบบ Alma ที่ถูก export ออกมาเป็น XML

---

## 6. ไฟล์ output: alma_output.csv

เมื่อรัน pipeline สำเร็จ ระบบจะสร้างไฟล์ CSV ที่

```text
output/alma_output.csv
```

ตัวอย่าง output

```csv
mms_id,title,author,isbn,publisher,publication_year,material_type,etl_timestamp
990000000000000000,Introduction to Library Data Pipeline,Mahidol University Library,9786160000000,MULKC Press,2026,Book,2026-07-08T08:39:51
```

field ที่ export ออกมา ได้แก่

| Field | ความหมาย |
|---|---|
| `mms_id` | รหัสระเบียนจาก Alma |
| `title` | ชื่อเรื่อง |
| `author` | ผู้แต่ง |
| `isbn` | ISBN |
| `publisher` | สำนักพิมพ์ |
| `publication_year` | ปีพิมพ์ |
| `material_type` | ประเภททรัพยากร |
| `etl_timestamp` | เวลาที่ pipeline ทำงาน |

---

## 7. อธิบายไฟล์ Python: src/pipeline.py

ไฟล์ `src/pipeline.py` คือหัวใจของระบบ

หน้าที่หลักคือ

1. อ่าน path ของไฟล์ input และ output
2. ตรวจสอบว่าไฟล์ XML มีอยู่จริง
3. อ่าน XML ด้วย Python
4. ดึงข้อมูล field ที่ต้องการ
5. แปลงข้อมูลให้อยู่ในรูปแบบที่เหมาะสม
6. เขียนข้อมูลออกเป็น CSV

ภาพรวมการทำงานของไฟล์ Python

```text
main()
 ├── อ่าน INPUT_XML
 ├── อ่าน OUTPUT_CSV
 ├── เปิดไฟล์ XML
 ├── extract_record_from_xml()
 ├── load_to_csv()
 └── จบการทำงาน
```

ในโค้ดมีการใช้ environment variable สองตัว

```text
INPUT_XML=/app/input/alma_response.xml
OUTPUT_CSV=/app/output/alma_output.csv
```

เหตุผลที่ใช้ environment variable คือทำให้เปลี่ยน path ได้ง่ายโดยไม่ต้องแก้โค้ด Python

---

## 8. อธิบาย Dockerfile

ไฟล์ `Dockerfile` คือสูตรสำหรับสร้าง Docker image

ตัวอย่าง

```dockerfile
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN mkdir -p /app/input /app/output

CMD ["python", "src/pipeline.py"]
```

อธิบายทีละส่วน

### `FROM python:3.12-slim`

เลือก image พื้นฐานที่มี Python 3.12 ติดตั้งมาให้แล้ว

คำว่า `slim` หมายถึง image ขนาดเล็กกว่าแบบเต็ม เหมาะกับงาน script หรือ ETL

### `ENV PYTHONUNBUFFERED=1`

ทำให้ log หรือข้อความจาก Python แสดงออกมาทันที ไม่ค้างอยู่ใน buffer

เวลา container ทำงาน เราจะเห็น log ชัดเจน

### `ENV PYTHONDONTWRITEBYTECODE=1`

บอก Python ว่าไม่ต้องสร้างไฟล์ cache เช่น `.pyc` หรือ `__pycache__`

ช่วยให้ container สะอาดขึ้น

### `WORKDIR /app`

กำหนดโฟลเดอร์ทำงานใน container เป็น `/app`

คำสั่งถัดไปจะทำงานในโฟลเดอร์นี้

### `COPY requirements.txt .`

คัดลอกไฟล์ `requirements.txt` จากเครื่องเราเข้าไปใน container

### `RUN pip install --no-cache-dir -r requirements.txt`

ติดตั้ง Python packages ตามที่ระบุใน `requirements.txt`

### `COPY src/ ./src/`

คัดลอกโค้ด Python จากโฟลเดอร์ `src` เข้าไปใน container

### `RUN mkdir -p /app/input /app/output`

สร้างโฟลเดอร์ `input` และ `output` ภายใน container

แต่ตอนรันจริง โฟลเดอร์นี้จะถูก map กับโฟลเดอร์บนเครื่อง host

### `CMD ["python", "src/pipeline.py"]`

กำหนดคำสั่งเริ่มต้นเมื่อ container ทำงาน

แปลว่าเมื่อ container ถูกสั่งรัน มันจะสั่ง

```bash
python src/pipeline.py
```

---

## 9. อธิบาย docker-compose.yml

ไฟล์ `docker-compose.yml` ใช้สำหรับสั่งรัน container แบบสะดวก โดยไม่ต้องพิมพ์คำสั่ง Docker ยาว ๆ

ตัวอย่าง

```yaml
services:
  alma-xml-etl:
    build: .
    container_name: alma-xml-etl-pipeline
    environment:
      INPUT_XML: /app/input/alma_response.xml
      OUTPUT_CSV: /app/output/alma_output.csv
    volumes:
      - ./input:/app/input
      - ./output:/app/output
    restart: "no"
```

อธิบายแต่ละส่วน

### `services:`

ประกาศรายชื่อ service หรือ container ที่จะให้ Docker Compose จัดการ

### `alma-xml-etl:`

ชื่อ service ของโปรเจกต์นี้

เวลา run จะใช้คำสั่ง

```bash
docker compose run --rm alma-xml-etl
```

### `build: .`

บอกให้ Docker Compose สร้าง image จาก `Dockerfile` ที่อยู่ในโฟลเดอร์ปัจจุบัน

### `container_name: alma-xml-etl-pipeline`

ตั้งชื่อ container ให้อ่านง่าย

### `environment:`

กำหนด environment variable ที่ส่งเข้าไปใน container

```yaml
INPUT_XML: /app/input/alma_response.xml
OUTPUT_CSV: /app/output/alma_output.csv
```

Python จะอ่านค่านี้เพื่อรู้ว่าไฟล์ input อยู่ที่ไหน และจะเขียน output ไปที่ไหน

### `volumes:`

ส่วนนี้สำคัญที่สุดของการบ้าน

```yaml
volumes:
  - ./input:/app/input
  - ./output:/app/output
```

หมายความว่า

```text
./input  บนเครื่องเรา  → /app/input  ใน container
./output บนเครื่องเรา  → /app/output ใน container
```

ดังนั้นเมื่อ Python ใน container เขียนไฟล์ที่

```text
/app/output/alma_output.csv
```

ไฟล์จะออกมาอยู่บนเครื่องเราที่

```text
output/alma_output.csv
```

นี่คือสิ่งที่เรียกว่า **Docker volume mapping**

### `restart: "no"`

บอกว่า container ไม่ต้อง restart เอง

เหมาะกับงาน ETL เพราะงาน ETL มักรันเป็นรอบ ๆ แล้วจบ ไม่ได้รันค้างเหมือน web server

---

## 10. ทำไมต้องใช้ Docker volume mapping

ถ้าไม่มี volume mapping ไฟล์ output จะอยู่ใน container

ปัญหาคือ container อาจถูกลบทิ้งเมื่อรันจบ โดยเฉพาะเมื่อใช้คำสั่ง

```bash
docker compose run --rm alma-xml-etl
```

คำว่า `--rm` หมายถึงรันเสร็จแล้วลบ container ทิ้ง

ถ้าไฟล์ output อยู่เฉพาะใน container ไฟล์อาจหายไปด้วย

แต่เมื่อใช้ volume mapping

```yaml
- ./output:/app/output
```

ไฟล์ที่ container สร้างใน `/app/output` จะถูกเขียนลงโฟลเดอร์ `output` บนเครื่อง host ทันที

สรุปคือ

```text
Container ทำงาน
แต่ไฟล์ input/output อยู่บนเครื่องจริง
```

---

## 11. วิธีรันโปรเจกต์

เปิด Terminal แล้วเข้าไปในโฟลเดอร์โปรเจกต์

```bash
cd ~/Desktop/alma-xml-etl-pipeline
```

จากนั้น build image

```bash
docker compose build
```

เมื่อ build สำเร็จ ให้รัน pipeline

```bash
docker compose run --rm alma-xml-etl
```

ถ้าสำเร็จจะเห็นข้อความประมาณนี้

```text
Alma XML ETL Pipeline started
Input XML : /app/input/alma_response.xml
Output CSV: /app/output/alma_output.csv
ETL completed successfully
```

---

## 12. วิธีตรวจสอบ output

หลังรันสำเร็จ ให้ตรวจสอบไฟล์ output

```bash
ls -la output
```

เปิดดูเนื้อหา CSV

```bash
cat output/alma_output.csv
```

ควรเห็นข้อมูลประมาณนี้

```csv
mms_id,title,author,isbn,publisher,publication_year,material_type,etl_timestamp
990000000000000000,Introduction to Library Data Pipeline,Mahidol University Library,9786160000000,MULKC Press,2026,Book,2026-07-08T08:39:51
```

---

## 13. คำสั่ง Git สำหรับสร้าง repository

เริ่มต้น Git repository ในเครื่อง

```bash
git init
git add .
git commit -m "Initial Alma XML ETL pipeline"
git branch -M main
```

ถ้ายังไม่มี repository บน GitHub ให้สร้างก่อน

ถ้าใช้ GitHub CLI

```bash
gh repo create alma-xml-etl-pipeline --public --source=. --remote=origin --push
```

ถ้าสร้างผ่านเว็บ GitHub แล้ว ให้ใช้คำสั่งนี้

```bash
git remote add origin https://github.com/sikharinse/alma-xml-etl-pipeline.git
git push -u origin main
```

ถ้ามี remote อยู่แล้ว และต้องการแก้ URL

```bash
git remote set-url origin https://github.com/sikharinse/alma-xml-etl-pipeline.git
git push -u origin main
```

---

## 14. Error ที่เจอบ่อยและวิธีแก้

### Error: Cannot connect to the Docker daemon

ข้อความ error

```text
Cannot connect to the Docker daemon
Is the docker daemon running?
```

สาเหตุคือ Docker Desktop ยังไม่เปิด หรือ Docker daemon ยังไม่พร้อม

วิธีแก้บน Mac

```bash
open -a Docker
```

รอให้ Docker Desktop เปิดเสร็จ แล้วลองใหม่

```bash
docker compose build
docker compose run --rm alma-xml-etl
```

---

### Error: Repository not found

ข้อความ error

```text
remote: Repository not found.
fatal: repository 'https://github.com/YOUR_USERNAME/alma-xml-etl-pipeline.git/' not found
```

สาเหตุที่เป็นไปได้

1. ยังไม่ได้สร้าง repo บน GitHub
2. ใช้ URL ผิด
3. ยังใช้คำว่า `YOUR_USERNAME` อยู่
4. ไม่มีสิทธิ์ push repo นั้น

วิธีแก้

สร้าง repo ก่อน หรือใช้ GitHub username จริง

ตัวอย่าง username

```text
sikharinse
```

remote ที่ถูกต้อง

```bash
git remote set-url origin https://github.com/sikharinse/alma-xml-etl-pipeline.git
```

จากนั้น push

```bash
git push -u origin main
```

---

### Error: Unable to add remote "origin"

ข้อความ error

```text
X Unable to add remote "origin"
```

สาเหตุคือใน local git มี remote ชื่อ `origin` อยู่แล้ว

วิธีแก้

```bash
git remote set-url origin https://github.com/sikharinse/alma-xml-etl-pipeline.git
git push -u origin main
```

หรือถ้าต้องการลบแล้วเพิ่มใหม่

```bash
git remote remove origin
git remote add origin https://github.com/sikharinse/alma-xml-etl-pipeline.git
git push -u origin main
```

---

## 15. สรุปการทำงานของระบบแบบสั้น

ระบบนี้เป็น Data Pipeline สำหรับอ่านข้อมูลจากไฟล์ XML ของ Alma แล้วแปลงเป็นไฟล์ CSV โดยใช้ Python ทำขั้นตอน ETL ได้แก่ Extract อ่านไฟล์ `alma_response.xml`, Transform แปลงและ map field เช่น `mms_id`, `title`, `author`, `isbn`, `publisher`, `publication_year` และ Load บันทึกเป็นไฟล์ `alma_output.csv`

โปรเจกต์นี้รันผ่าน Docker เพื่อให้สภาพแวดล้อมเหมือนกันทุกเครื่อง และใช้ Docker Compose เพื่อกำหนดค่า container รวมถึงทำ volume mapping ระหว่างโฟลเดอร์ `input` และ `output` บนเครื่อง host กับใน container ทำให้ไฟล์ CSV ที่สร้างจาก container ออกมาอยู่ข้างนอก container ในโฟลเดอร์ `output`

---

## 16. บทพูดสั้น ๆ สำหรับอธิบายให้อาจารย์ฟัง

โปรเจกต์นี้เป็นตัวอย่าง Data Pipeline ที่ใช้ Python อ่านไฟล์ `alma_response.xml` ซึ่งเป็นข้อมูล XML จากระบบ Alma แล้วแปลงข้อมูลสำคัญ เช่น mms_id, title, author, isbn, publisher และ publication_year ออกมาเป็นไฟล์ CSV ชื่อ `alma_output.csv`

ระบบถูกหุ้มด้วย Docker เพื่อให้รันได้เหมือนกันทุกเครื่อง และใช้ `docker-compose.yml` ในการกำหนดค่า container รวมถึงทำ volume mapping โดย map โฟลเดอร์ `input` และ `output` ของเครื่องจริงเข้าไปใน container ทำให้เมื่อ container ประมวลผลเสร็จ ไฟล์ CSV จะออกมาอยู่ในโฟลเดอร์ `output` บนเครื่อง host สามารถเปิดดูและนำไปใช้ต่อได้ทันที

---

## 17. Checklist สำหรับส่งการบ้าน

ก่อนส่งงาน ควรตรวจสอบรายการนี้

- [ ] มีไฟล์ `Dockerfile`
- [ ] มีไฟล์ `docker-compose.yml`
- [ ] มีไฟล์ `src/pipeline.py`
- [ ] มีไฟล์ `input/alma_response.xml`
- [ ] มีโฟลเดอร์ `output`
- [ ] รัน `docker compose build` ได้
- [ ] รัน `docker compose run --rm alma-xml-etl` ได้
- [ ] มีไฟล์ `output/alma_output.csv` ถูกสร้างออกมา
- [ ] push ขึ้น GitHub repository แล้ว
- [ ] README หรือเอกสาร Markdown อธิบายการทำงานของระบบแล้ว

---

## 18. คำสั่งรวมแบบรวบรัด

ใช้ชุดนี้สำหรับทบทวนเร็ว ๆ

```bash
cd ~/Desktop/alma-xml-etl-pipeline

docker compose build
docker compose run --rm alma-xml-etl

ls -la output
cat output/alma_output.csv

git status
git add .
git commit -m "Add Alma XML ETL pipeline guide"
git push
```

---

## 19. สรุปสุดท้าย

โปรเจกต์นี้แสดงแนวคิดสำคัญของงาน Data Pipeline คือการนำข้อมูลจากต้นทางมาแปลงให้อยู่ในรูปแบบที่พร้อมใช้งาน โดยใช้ Python ทำ ETL และใช้ Docker ช่วยควบคุม environment ให้รันได้เหมือนกันทุกเครื่อง จุดสำคัญของการบ้านคือการใช้ Docker volume mapping เพื่อให้ไฟล์ output ที่สร้างภายใน container ถูกบันทึกออกมาอยู่บนเครื่อง host ภายนอก container ได้จริง
