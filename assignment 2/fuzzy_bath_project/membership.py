# membership.py
# ------------------------------------------------------------------
# ฟังก์ชันสมาชิก (Membership Function) พื้นฐานที่ใช้ในระบบ Fuzzy Logic
# รองรับ 2 รูปแบบ:
#   - Triangular (สามเหลี่ยม) ใช้พารามิเตอร์ [a, b, c]
#   - Trapezoidal (คางหมู) ใช้พารามิเตอร์ [a, b, c, d]
# ------------------------------------------------------------------

import numpy as np  # ใช้คำนวณตัวเลขและ Array


def trimf(x, params):
    """คำนวณค่าความเป็นสมาชิกของฟังก์ชันรูปสามเหลี่ยม."""
    a, b, c = params  # จุดเริ่ม จุดยอด และจุดสิ้นสุดของสามเหลี่ยม
    x = np.asarray(x, dtype=float)  # รองรับทั้งค่าเดียวและ NumPy Array

    left = np.zeros_like(x)  # เตรียมค่าด้านซ้าย
    right = np.zeros_like(x)  # เตรียมค่าด้านขวา

    if b != a:
        left = (x - a) / (b - a)  # ความชันจาก 0 ที่ a ไป 1 ที่ b
    else:
        left = np.where(x >= a, 1.0, 0.0)  # กรณีขอบซ้ายชนกัน

    if c != b:
        right = (c - x) / (c - b)  # ความชันจาก 1 ที่ b ไป 0 ที่ c
    else:
        right = np.where(x <= c, 1.0, 0.0)  # กรณีขอบขวาชนกัน

    y = np.minimum(left, right)  # ต้องผ่านทั้งด้านซ้ายและด้านขวา จึงใช้ค่าที่น้อยกว่า
    y = np.clip(y, 0.0, 1.0)  # Membership ต้องอยู่ระหว่าง 0 ถึง 1
    return y


def trapmf(x, params):
    """คำนวณค่าความเป็นสมาชิกของฟังก์ชันรูปคางหมู."""
    a, b, c, d = params  # ขอบซ้าย ช่วงราบ และขอบขวาของคางหมู
    x = np.asarray(x, dtype=float)  # รองรับทั้งค่าเดียวและ NumPy Array

    left = np.ones_like(x)  # ค่าเริ่มต้นด้านซ้ายเป็น 1
    right = np.ones_like(x)  # ค่าเริ่มต้นด้านขวาเป็น 1

    if b != a:
        left = (x - a) / (b - a)  # ความชันขึ้นจาก 0 ไป 1
    if d != c:
        right = (d - x) / (d - c)  # ความชันลงจาก 1 ไป 0

    y = np.minimum(np.minimum(left, right), 1.0)  # รวมด้านซ้ายและด้านขวา
    y = np.clip(y, 0.0, 1.0)  # ป้องกันค่าเกินช่วงมาตรฐาน
    return y
