# Assignment 1 — Multilayer Perceptron และ Backpropagation

งานนี้ศึกษาโครงข่ายประสาทเทียมแบบ Multilayer Perceptron (MLP) และการฝึกด้วย Backpropagation (Generalized Delta Rule) โดยเขียนอัลกอริทึมขึ้นเองด้วย Python standard library ไม่พึ่งไลบรารี Machine Learning

## งานทดลอง

- **Flood prediction:** ใช้ข้อมูล `data/Flood_dataset.txt` เพื่อพยากรณ์ระดับน้ำที่สะพานนวรัฐล่วงหน้า (t+7) และประเมินผลด้วย 10-fold cross-validation กับค่า MAE
- **Classification:** ใช้ข้อมูล `data/cross.pat` จำแนกข้อมูล 2 คลาสที่มี 2 features ประเมินด้วย 10-fold cross-validation, accuracy และ confusion matrix
- เปรียบเทียบโครงสร้าง hidden layer, learning rate, momentum และค่าเริ่มต้นของน้ำหนัก

## ไฟล์สำคัญ

- `mlp.py` — MLP, sigmoid, forward pass, backpropagation และ momentum
- `data_utils.py` — โหลดและจัดการข้อมูล รวมถึงฟังก์ชันแบ่ง fold และวัดผล
- `run_flood.py` — การทดลองพยากรณ์ระดับน้ำ
- `run_cross.py` — การทดลองจำแนกข้อมูล
- `run_experiments.py` — รันชุดเปรียบเทียบค่าพารามิเตอร์และบันทึกผล CSV
- `data/` — ชุดข้อมูลสำหรับทั้งสองการทดลอง
- `results/` — ผลการทดลองที่บันทึกไว้
- `reportCI.pdf` — รายงานของงาน

## วิธีรัน

ใช้ Python 3 โดยไม่ต้องติดตั้งไลบรารีภายนอก งานโหลดข้อมูลด้วย path แบบ relative ดังนั้นให้รันคำสั่งจากโฟลเดอร์นี้:

```bash
python run_flood.py
python run_cross.py
python run_experiments.py
```

การรัน `run_experiments.py` จะรันชุดทดลองทั้ง Flood และ `cross.pat` และสร้างไฟล์ CSV ใน `results/` ซึ่งอาจใช้เวลาประมวลผล

> ชื่อโฟลเดอร์ `assisgnment 1` สะกดตามชื่อเดิมใน repository
