# Assignment 3

งานนี้เป็นการฝึก Multilayer Perceptron ด้วย Genetic Algorithms บนชุดข้อมูล WDBC

## ไฟล์สำคัญ

- `wdbc.data` ชุดข้อมูลที่ใช้ทดลอง
- `mlp_ga.py` โปรแกรม MLP และ Genetic Algorithms ที่เขียนด้วย Python standard library
- `results.csv` ผลการทดลอง 10-fold cross-validation ที่ตรงกับ `mlp_ga.py`
- `assignment3_report.pdf` รายงานสำหรับตรวจ/ส่งเป็น PDF
- `assignment3_report.docx` รายงาน Word สำหรับแก้ไข
- `โจทย์_assignment_3.md` โจทย์และข้อกำหนดของอาจารย์

รายงานใช้ตารางผลการทดลองแทนกราฟ เพื่อไม่ต้องแนบโปรแกรมวาดรูปหรือโค้ดที่ซับซ้อนเกินความจำเป็น

## วิธีรันการทดลอง

```text
python mlp_ga.py
```

โปรแกรมจะอ่าน `wdbc.data` และเขียนผลลัพธ์ลง `results.csv` โดยใช้เฉพาะ Python standard library ไม่ใช้ไลบรารี machine learning และไม่ใช้ไลบรารีหรือโปรแกรมสำหรับวาดรูป
