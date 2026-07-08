#!/usr/bin/env bash
set -e

# ต้องติดตั้ง GitHub CLI และ login ก่อนด้วยคำสั่ง:
# gh auth login

gh repo create alma-xml-etl-pipeline --public --source=. --remote=origin --push
