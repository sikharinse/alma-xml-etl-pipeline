#!/usr/bin/env bash
set -e

git init
git add .
git commit -m "Initial Alma XML ETL pipeline"
git branch -M main

echo "สร้าง local git repository แล้ว"
echo "ขั้นต่อไป ให้สร้าง GitHub repo ชื่อ alma-xml-etl-pipeline แล้วรัน:"
echo "git remote add origin https://github.com/YOUR_USERNAME/alma-xml-etl-pipeline.git"
echo "git push -u origin main"
