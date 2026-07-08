# Dockerfile
# Image พื้นฐานที่มี Python พร้อมใช้งาน
FROM python:3.12-slim

# ทำให้ log แสดงทันที และไม่สร้างไฟล์ cache .pyc
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# กำหนดโฟลเดอร์ทำงานใน container
WORKDIR /app

# คัดลอก requirements ก่อน เพื่อใช้ Docker cache
COPY requirements.txt .

# ติดตั้ง Python packages
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอก source code เข้า container
COPY src/ ./src/

# สร้างโฟลเดอร์ input/output ภายใน container
# แต่ตอนรันจริงจะ map volume จากเครื่อง host เข้ามาทับ
RUN mkdir -p /app/input /app/output

# คำสั่งเริ่มต้นเมื่อ container ทำงาน
CMD ["python", "src/pipeline.py"]
