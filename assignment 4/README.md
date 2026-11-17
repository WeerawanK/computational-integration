# Assignment 4 — พยากรณ์ค่า Benzene ด้วย MLP และ PSO

งานนี้ใช้ **Particle Swarm Optimization (PSO)** เพื่อหาน้ำหนักของ **Multilayer Perceptron (MLP)** สำหรับพยากรณ์ความเข้มข้น Benzene จากชุดข้อมูล AirQualityUCI

## ข้อมูลและการทดลอง

- ใช้ข้อมูลจาก `AirQualityUCI.xlsx` โดยใช้ attributes 3, 6, 8, 10, 11, 12, 13 และ 14 เป็น input และ attribute 5 (Benzene) เป็น target
- ทดลองพยากรณ์ล่วงหน้า **5 วัน (120 ชั่วโมง)** และ **10 วัน (240 ชั่วโมง)**
- เปรียบเทียบโครงสร้าง MLP ที่มี hidden layer เดียวหรือสองชั้น
- ประเมินด้วย 10-fold cross-validation และ Mean Absolute Error (MAE)
- `mlp_pso.py` มีการอ่านไฟล์ XLSX และคำนวณ MLP/PSO; NumPy ใช้สำหรับการคำนวณตัวเลขและเมทริกซ์

## ไฟล์สำคัญ

- `mlp_pso.py` — โหลดข้อมูล ฝึก MLP ด้วย PSO ประเมินผลและบันทึก CSV
- `AirQualityUCI.xlsx` — ชุดข้อมูลทดลอง
- `results.csv` — ผลการทดลองแยกตาม fold
- `summary.csv` — ผลสรุปการทดลอง
- `assignment4.pdf` และ `assignment4_report.docx` — รายงาน
- `โจทย์_assignment_4.md` — โจทย์และรายละเอียดข้อมูล

## วิธีรัน

ต้องมี Python 3 และ NumPy ติดตั้งแล้ว รันจากโฟลเดอร์นี้:

```bash
python -m pip install numpy
python mlp_pso.py
```

โปรแกรมจะอ่าน `AirQualityUCI.xlsx` ที่อยู่ในโฟลเดอร์เดียวกัน แล้วเขียนผลลง `results.csv` และ `summary.csv` การทดลองทำ cross-validation หลายชุด จึงอาจใช้เวลาประมวลผล
