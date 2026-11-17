# Assignment 4

## ข้อกำหนดสำคัญ

- ต้องเขียนโปรแกรมเองและทำการทดลองเอง
- ห้ามลอกโปรแกรมหรือเนื้อหาจากแหล่งอื่น
- หากตรวจพบว่าลอกงาน จะได้รับคะแนน 0 ทั้งผู้ให้ลอกและผู้ลอก

## หัวข้อ

จงเขียนโปรแกรมสำหรับการ Train Multilayer Perceptron โดยใช้ Particle Swarm Optimization (PSO) เพื่อทำ prediction ค่า Benzene concentration โดยพยากรณ์ล่วงหน้า 5 วันและ 10 วัน

## Input และ Output

ให้ใช้ attribute หมายเลข 3, 6, 8, 10, 11, 12, 13 และ 14 เป็น input

ให้ใช้ attribute หมายเลข 5 เป็น desired output หรือค่า Benzene concentration

## องค์ประกอบของรายงาน

รายงานต้องประกอบด้วย

1. ลักษณะการทำงานของระบบ
2. Simulation ของระบบ ผลการทดลอง และการวิเคราะห์
3. โปรแกรม

## ชุดข้อมูล

ให้ทำการทดลองกับ [AirQualityUCI](https://myweb.cmu.ac.th/sansanee.a/IntroCI/dataset/AirQualityUCI.xlsx) ซึ่งเป็น Air Quality Data Set จาก UCI Machine Learning Repository

โจทย์ระบุว่าชุดข้อมูลมี 9358 samples และมี 14 attributes โดยรายละเอียดที่ให้มาคือ

| หมายเลข | รายละเอียด |
|---:|---|
| 0 | Date (DD/MM/YYYY) |
| 1 | Time (HH.MM.SS) |
| 2 | True hourly averaged concentration CO in mg/m3 (reference analyzer) |
| 3 | PT08.S1 (tin oxide) hourly averaged sensor response (nominally CO targeted) |
| 4 | True hourly averaged overall Non Metanic HydroCarbons concentration in microg/m3 (reference analyzer) |
| 5 | True hourly averaged Benzene concentration in microg/m3 (reference analyzer) |
| 6 | PT08.S2 (titania) hourly averaged sensor response (nominally NMHC targeted) |
| 7 | True hourly averaged NOx concentration in ppb (reference analyzer) |
| 8 | PT08.S3 (tungsten oxide) hourly averaged sensor response (nominally NOx targeted) |
| 9 | True hourly averaged NO2 concentration in microg/m3 (reference analyzer) |
| 10 | PT08.S4 (tungsten oxide) hourly averaged sensor response (nominally NO2 targeted) |
| 11 | PT08.S5 (indium oxide) hourly averaged sensor response (nominally O3 targeted) |
| 12 | Temperature in °C |
| 13 | Relative Humidity (%) |
| 14 | AH Absolute Humidity |

## การทดลอง

- ใช้ 10% cross-validation เพื่อทดสอบ validity ของ network ที่ได้
- ทดลองเปลี่ยนจำนวน hidden layer
- ทดลองเปลี่ยนจำนวน nodes ใน hidden layer
- ต้องทำ prediction 5 วันล่วงหน้าและ 10 วันล่วงหน้า
- เปรียบเทียบผลการทดลองและวิเคราะห์ผลอย่างมีเหตุผล

## การวัด Error

ให้ใช้ Mean Absolute Error (MAE) ในการวัด error

สูตร:

```text
MAE = (1 / n) * sum(|ค่าจริง - ค่าที่พยากรณ์|)
```

## หมายเหตุ

ควรเขียนรายงานให้อยู่ในรูปแบบรายงานที่ดี และมีการวิเคราะห์ผลการทดลองอย่างละเอียดและมีเหตุผล

## หมายเหตุเรื่องจำนวน attributes

รายการที่โจทย์ให้มามีหมายเลขตั้งแต่ 0 ถึง 14 ซึ่งรวมเป็น 15 คอลัมน์เมื่อรวม Date และ Time ด้วย ขณะที่ข้อความโจทย์ระบุว่ามี 14 attributes ควรตรวจสอบรูปแบบไฟล์จริงและยืนยันวิธีนับคอลัมน์ก่อนเริ่มเขียนโปรแกรม
