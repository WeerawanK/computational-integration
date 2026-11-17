# fuzzy_controller.py
# ------------------------------------------------------------------
# ระบบควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic (Mamdani Inference System)
#
#   Input  1 : อุณหภูมิน้ำปัจจุบัน   (Current Water Temperature)  หน่วย °C
#   Input  2 : อุณหภูมิเป้าหมาย     (Target Temperature)         หน่วย °C
#   Output   : ปริมาณน้ำร้อนที่เปิด  (Hot Water Valve Opening)   หน่วย %
#
# ขั้นตอน Mamdani:
#   1) Fuzzification  - แปลง input จากค่าตัวเลขเป็นค่าความเป็นสมาชิก
#   2) Rule Evaluation - หาความแรงของกฎ โดยใช้ AND = min
#   3) Implication     - ตัดกราฟ output ตามความแรงของกฎ
#   4) Aggregation     - รวมผลของทุกกฎด้วย OR = max
#   5) Defuzzification - แปลงผลกลับเป็นตัวเลขด้วย Centroid
# ------------------------------------------------------------------

import numpy as np  # ใช้สร้างช่วงข้อมูลและคำนวณ Array
from membership import trimf, trapmf  # นำเข้าฟังก์ชันสมาชิกของโปรเจกต์


class FuzzyBathController:
    """ตัวควบคุมที่รวม Membership Function, Rule Base และการอนุมาน."""

    def __init__(self):
        # Universe คือช่วงค่าที่ระบบยอมรับและใช้คำนวณ Fuzzy Set
        self.now_universe = np.linspace(0, 60, 601)  # อุณหภูมิปัจจุบัน 0-60°C
        self.target_universe = np.linspace(25, 45, 401)  # เป้าหมาย 25-45°C
        self.valve_universe = np.linspace(0, 100, 1001)  # วาล์ว 0-100%

        # Input 1: แบ่งอุณหภูมิปัจจุบันเป็น Cold, Cool, Warm และ Hot
        self.now_mf = {
            "Cold": lambda x: trapmf(x, [0, 0, 10, 20]),  # น้ำเย็นมาก
            "Cool": lambda x: trimf(x, [10, 20, 30]),  # น้ำค่อนข้างเย็น
            "Warm": lambda x: trimf(x, [25, 35, 45]),  # น้ำอุ่น
            "Hot": lambda x: trapmf(x, [40, 50, 60, 60]),  # น้ำร้อนมาก
        }

        # Input 2: แบ่งอุณหภูมิเป้าหมายเป็น Low, Medium และ High
        self.target_mf = {
            "Low": lambda x: trapmf(x, [25, 25, 30, 33]),  # เป้าหมายต่ำ
            "Medium": lambda x: trimf(x, [30, 36, 42]),  # เป้าหมายปานกลาง
            "High": lambda x: trapmf(x, [39, 42, 45, 45]),  # เป้าหมายสูง
        }

        # Output: แบ่งเปอร์เซ็นต์การเปิดวาล์วเป็น 5 ระดับ
        self.valve_mf = {
            "VeryLow": lambda x: trapmf(x, [0, 0, 10, 25]),  # เปิดน้อยมาก
            "Low": lambda x: trimf(x, [10, 25, 40]),  # เปิดน้อย
            "Medium": lambda x: trimf(x, [30, 50, 70]),  # เปิดปานกลาง
            "High": lambda x: trimf(x, [60, 75, 90]),  # เปิดมาก
            "VeryHigh": lambda x: trapmf(x, [75, 90, 100, 100]),  # เปิดมากที่สุด
        }

        # Rule Base: (อุณหภูมิปัจจุบัน, เป้าหมาย, ผลลัพธ์วาล์ว)
        self.rules = [
            ("Cold", "Low", "High"),  # น้ำเย็นและเป้าหมายต่ำ
            ("Cold", "Medium", "VeryHigh"),  # น้ำเย็นและเป้าหมายปานกลาง
            ("Cold", "High", "VeryHigh"),  # น้ำเย็นและเป้าหมายสูง
            ("Cool", "Low", "Medium"),  # น้ำค่อนข้างเย็นและเป้าหมายต่ำ
            ("Cool", "Medium", "High"),  # น้ำค่อนข้างเย็นและเป้าหมายปานกลาง
            ("Cool", "High", "VeryHigh"),  # น้ำค่อนข้างเย็นและเป้าหมายสูง
            ("Warm", "Low", "Low"),  # น้ำอุ่นและเป้าหมายต่ำ
            ("Warm", "Medium", "Medium"),  # น้ำอุ่นและเป้าหมายปานกลาง
            ("Warm", "High", "High"),  # น้ำอุ่นและเป้าหมายสูง
            ("Hot", "Low", "VeryLow"),  # น้ำร้อนและเป้าหมายต่ำ
            ("Hot", "Medium", "VeryLow"),  # น้ำร้อนและเป้าหมายปานกลาง
            ("Hot", "High", "Medium"),  # น้ำร้อนและเป้าหมายสูง
        ]

    def fuzzify_now(self, t_now):
        """คำนวณระดับความเป็นสมาชิกของอุณหภูมิปัจจุบัน."""
        return {name: float(mf(t_now)) for name, mf in self.now_mf.items()}  # คำนวณทุกกลุ่ม

    def fuzzify_target(self, t_target):
        """คำนวณระดับความเป็นสมาชิกของอุณหภูมิเป้าหมาย."""
        return {name: float(mf(t_target)) for name, mf in self.target_mf.items()}  # คำนวณทุกกลุ่ม

    def infer(self, t_now, t_target):
        """ทำ Fuzzification, Rule Evaluation, Implication และ Aggregation."""
        now_degrees = self.fuzzify_now(t_now)  # แปลง input ปัจจุบันเป็น Fuzzy Values
        target_degrees = self.fuzzify_target(t_target)  # แปลงเป้าหมายเป็น Fuzzy Values
        aggregated = np.zeros_like(self.valve_universe)  # เริ่ม output รวมเป็นศูนย์
        fired_rules = []  # เก็บกฎที่ถูกกระตุ้นเพื่อแสดงผล

        for now_term, target_term, valve_term in self.rules:  # ตรวจสอบกฎทีละข้อ
            firing_strength = min(now_degrees[now_term], target_degrees[target_term])  # AND = min
            if firing_strength > 0:  # เก็บเฉพาะกฎที่มีผลจริง
                fired_rules.append((now_term, target_term, valve_term, firing_strength))
            consequent_mf = self.valve_mf[valve_term](self.valve_universe)  # กราฟ output ของกฎ
            clipped = np.minimum(consequent_mf, firing_strength)  # Implication: ตัดยอดกราฟ
            aggregated = np.maximum(aggregated, clipped)  # Aggregation: รวมด้วย max

        return aggregated, fired_rules, now_degrees, target_degrees  # ส่งผลไป Defuzzification

    def defuzzify(self, aggregated):
        """แปลง Fuzzy Output เป็นเปอร์เซ็นต์วาล์วด้วย Centroid."""
        area = np.sum(aggregated)  # พื้นที่โดยประมาณใต้กราฟ output
        if area == 0:  # ป้องกันการหารด้วยศูนย์กรณีไม่มีกฎทำงาน
            return float(np.mean(self.valve_universe))  # ใช้ค่ากึ่งกลาง 50% เป็น fallback
        centroid = np.sum(self.valve_universe * aggregated) / area  # สูตรจุดศูนย์ถ่วง
        return float(centroid)  # คืนค่าเป็น float ปกติ

    def compute(self, t_now, t_target):
        """เรียกกระบวนการควบคุมทั้งหมดและคืนค่า output."""
        t_now = float(np.clip(t_now, self.now_universe[0], self.now_universe[-1]))  # จำกัด input ปัจจุบัน
        t_target = float(np.clip(t_target, self.target_universe[0], self.target_universe[-1]))  # จำกัดเป้าหมาย
        aggregated, fired_rules, now_degrees, target_degrees = self.infer(t_now, t_target)  # อนุมาน
        valve_opening = self.defuzzify(aggregated)  # แปลงผลเป็นเปอร์เซ็นต์วาล์ว
        return valve_opening, aggregated, fired_rules, now_degrees, target_degrees  # คืนผลทั้งหมด
