# Assignment 2 — ระบบควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic

งานนี้สร้าง simulation ของระบบควบคุมอุณหภูมิน้ำอาบด้วย **Mamdani Fuzzy Inference System** โดยใช้การอนุมานแบบ min/max และแปลงผลลัพธ์กลับเป็นค่าตัวเลขด้วยวิธี centroid

- **Input:** อุณหภูมิน้ำปัจจุบัน (°C) และอุณหภูมิเป้าหมาย (°C)
- **Output:** เปอร์เซ็นต์การเปิดวาล์วน้ำร้อน
- กำหนด membership functions และฐานกฎเพื่อกำหนดปริมาณน้ำร้อนตามสถานการณ์
- จำลองการทำงานและสร้างกราฟ/รายงานประกอบผลการทดลอง

## ไฟล์และโฟลเดอร์สำคัญ

- [`fuzzy_bath_project/`](./fuzzy_bath_project/) — โค้ด simulation, dependencies, ผลลัพธ์ และรายงาน
- `fuzzy_bath_project/fuzzy_controller.py` — ระบบ fuzzy controller และ rule base
- `fuzzy_bath_project/membership.py` — membership functions
- `fuzzy_bath_project/simulate.py` — รัน simulation และสร้างกราฟใน `outputs/`
- `โจทย์และหัวข้อที่เลือกทำ.md` — โจทย์และหัวข้อที่เลือก

## วิธีรัน

เข้าไปที่โฟลเดอร์โปรเจกต์แล้วติดตั้ง dependencies และรันโปรแกรม:

```bash
cd fuzzy_bath_project
pip install -r requirements.txt
python simulate.py
```

ดูคำสั่งสร้างรายงานเพิ่มเติมและรายละเอียดผลลัพธ์ได้ใน [`fuzzy_bath_project/README.md`](./fuzzy_bath_project/README.md)
