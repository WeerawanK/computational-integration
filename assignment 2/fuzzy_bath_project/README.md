# ระบบควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic (Mamdani)

โปรแกรมจำลอง (simulation) สำหรับ Computer Assignment 2
วิชา Fuzzy Logic / Approximate Reasoning

## หัวข้อระบบ
ระบบควบคุมอุณหภูมิน้ำอาบ (Fuzzy Bath Water Temperature Control)
- Input 1: อุณหภูมิน้ำปัจจุบัน (Current Water Temperature, °C)
- Input 2: อุณหภูมิเป้าหมาย (Target Temperature, °C)
- Output : ปริมาณน้ำร้อน / วาล์วน้ำร้อน (Hot Water Valve Opening, %)

ใช้ระบบ **Mamdani Fuzzy Inference** พร้อม defuzzification แบบ **Centroid**

## โครงสร้างไฟล์
```
fuzzy_bath_project/
├── membership.py       # ฟังก์ชันสมาชิก (triangular, trapezoidal)
├── fuzzy_controller.py # ตัวระบบ Fuzzy Logic (fuzzification, rule base, inference, defuzzification)
├── simulate.py          # โปรแกรมหลัก: รันการจำลอง + สร้างกราฟทั้งหมด
├── build_report.py      # สร้างรายงาน HTML พร้อมภาคผนวกโปรแกรม
├── build_pdf.py         # สร้างรายงาน PDF สำหรับส่งงาน
├── requirements.txt
└── outputs/             # กราฟผลลัพธ์ (สร้างขึ้นหลังรันโปรแกรม)
    ├── 1_membership_functions.png
    ├── 2_control_surface.png
    └── 3_time_simulation.png
```

## วิธีรัน
ต้องมี Python 3 พร้อม numpy และ matplotlib (ดู requirements.txt)

```bash
pip install -r requirements.txt
python simulate.py
python build_report.py
python build_pdf.py
```

โปรแกรมจะพิมพ์ผลตัวอย่างการ inference ทีละขั้นตอน (fuzzification, กฎที่ถูกกระตุ้น,
ผล defuzzification) ออกทาง console และบันทึกกราฟทั้งหมดไว้ในโฟลเดอร์ `outputs/`

ไฟล์ `fuzzy_bath_report.pdf` เป็นรายงานฉบับพร้อมส่ง ประกอบด้วยบทคัดย่อ
วิธีการทำงาน ฐานกฎ ผลการทดลอง การวิเคราะห์ กราฟ และภาคผนวกโปรแกรมครบถ้วน

## แนวทางเขียนรายงาน (ตามโจทย์ 3 ข้อ)
1. **ลักษณะการทำงานของระบบ + rules** → อธิบายตาม `fuzzy_controller.py`
   (membership function ของแต่ละตัวแปร + ตาราง/รายการกฎ 12 ข้อ)
2. **Simulation + ผลการทดลอง + วิเคราะห์** → ใช้กราฟใน `outputs/` ทั้ง 3 รูป
   พร้อมตัวเลข error/steady-state ที่พิมพ์ออกมาตอนรันโปรแกรม เป็นข้อมูลวิเคราะห์
3. **โปรแกรม (ภาคผนวก)** → copy-paste เนื้อหาไฟล์ `membership.py`, `fuzzy_controller.py`,
   `simulate.py` ทั้งหมด (มี comment อธิบายทุกส่วนแล้ว)

## หมายเหตุเกี่ยวกับโมเดลจำลอง
การจำลองใน `simulate.py` ใช้แบบจำลองก๊อกผสมน้ำร้อน/เย็น (mixing valve) ซึ่งวาล์ว
ที่คำนวณได้จาก fuzzy controller จะกำหนดสัดส่วนน้ำร้อนในน้ำที่ไหลเข้าอ่าง ทำให้ระบบมี
จุดสมดุล (equilibrium) ตามธรรมชาติ และมักจะมี steady-state error เล็กน้อย
(ประมาณ 0.5-1.5 °C ในตัวอย่างที่ทดสอบ) ซึ่งเป็นประเด็นที่สามารถนำไปวิเคราะห์เพิ่มเติม
ในรายงานได้ เช่น ผลของจำนวนกฎ, ความละเอียดของ membership function, หรือ
การเปลี่ยนไปใช้ Sugeno-type FIS
