# simulate.py
# ------------------------------------------------------------------
# โปรแกรมจำลองการทำงานของระบบควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic
# (Mamdani Fuzzy Inference System)
#
# โปรแกรมนี้จะ
#   1) วาดกราฟ Membership Function ของ input และ output
#   2) วาด Control Surface ความสัมพันธ์ระหว่าง input กับ output
#   3) จำลองการเปลี่ยนอุณหภูมิตามเวลาในหลายสถานการณ์
#   4) พิมพ์รายละเอียด Fuzzification และกฎที่ถูกกระตุ้น
#
# ผลลัพธ์ทุกกราฟจะถูกบันทึกไว้ในโฟลเดอร์ outputs/
# ------------------------------------------------------------------

import os  # ใช้สร้างโฟลเดอร์ผลลัพธ์

import matplotlib.pyplot as plt  # ใช้วาดกราฟ
import numpy as np  # ใช้จัดการข้อมูลตัวเลขและช่วงเวลา
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (เปิดใช้งานกราฟ 3D)

from fuzzy_controller import FuzzyBathController  # นำเข้าตัวควบคุม Fuzzy

OUT_DIR = "outputs"  # โฟลเดอร์สำหรับเก็บรูปผลลัพธ์
plt.rcParams["font.family"] = "Tahoma"  # ฟอนต์ที่รองรับภาษาไทยบน Windows
plt.rcParams["axes.unicode_minus"] = False  # แก้ปัญหาเครื่องหมายลบในกราฟ


def plot_membership_functions(fc: FuzzyBathController):
    """วาด Membership Function ของ input และ output ทั้งหมด."""
    fig, axes = plt.subplots(3, 1, figsize=(8, 9))  # สร้างกราฟ 3 แถว

    for name, mf in fc.now_mf.items():  # วนผ่านกลุ่มอุณหภูมิปัจจุบัน
        axes[0].plot(fc.now_universe, mf(fc.now_universe), label=name)  # วาดเส้นกลุ่มนั้น
    axes[0].set_title("Input 1: อุณหภูมิน้ำปัจจุบัน (Current Water Temperature, °C)")
    axes[0].set_xlabel("Temperature (°C)")  # ชื่อแกนนอน
    axes[0].set_ylabel("Membership Degree")  # ชื่อแกนตั้ง
    axes[0].legend()  # แสดงชื่อเส้น
    axes[0].grid(alpha=0.3)  # แสดงเส้นตารางจาง ๆ

    for name, mf in fc.target_mf.items():  # วนผ่านกลุ่มอุณหภูมิเป้าหมาย
        axes[1].plot(fc.target_universe, mf(fc.target_universe), label=name)  # วาดเส้นกลุ่มนั้น
    axes[1].set_title("Input 2: อุณหภูมิเป้าหมาย (Target Temperature, °C)")
    axes[1].set_xlabel("Temperature (°C)")  # ชื่อแกนนอน
    axes[1].set_ylabel("Membership Degree")  # ชื่อแกนตั้ง
    axes[1].legend()  # แสดงชื่อเส้น
    axes[1].grid(alpha=0.3)  # แสดงเส้นตาราง

    for name, mf in fc.valve_mf.items():  # วนผ่านกลุ่มเปอร์เซ็นต์วาล์ว
        axes[2].plot(fc.valve_universe, mf(fc.valve_universe), label=name)  # วาดเส้นกลุ่มนั้น
    axes[2].set_title("Output: ปริมาณน้ำร้อน (Hot Water Valve Opening, %)")
    axes[2].set_xlabel("Valve Opening (%)")  # ชื่อแกนนอน
    axes[2].set_ylabel("Membership Degree")  # ชื่อแกนตั้ง
    axes[2].legend()  # แสดงชื่อเส้น
    axes[2].grid(alpha=0.3)  # แสดงเส้นตาราง

    fig.tight_layout()  # จัดระยะห่างของกราฟ
    fig.savefig(f"{OUT_DIR}/1_membership_functions.png", dpi=150)  # บันทึกกราฟ
    plt.close(fig)  # ปิดกราฟและคืนหน่วยความจำ


def plot_control_surface(fc: FuzzyBathController):
    """วาด Control Surface แบบสามมิติของระบบ."""
    now_range = np.linspace(fc.now_universe[0], fc.now_universe[-1], 40)  # ตัวอย่าง current temp
    target_range = np.linspace(fc.target_universe[0], fc.target_universe[-1], 40)  # ตัวอย่าง target
    NOW, TARGET = np.meshgrid(now_range, target_range)  # สร้างคู่ input ทุกคู่
    VALVE = np.zeros_like(NOW)  # เตรียมตารางเก็บ output

    for i in range(NOW.shape[0]):  # วนทุกแถวของตาราง
        for j in range(NOW.shape[1]):  # วนทุกคอลัมน์ของตาราง
            valve_opening, *_ = fc.compute(NOW[i, j], TARGET[i, j])  # คำนวณวาล์ว
            VALVE[i, j] = valve_opening  # เก็บ output ลงตำแหน่งเดียวกัน

    fig = plt.figure(figsize=(8, 6))  # สร้างพื้นที่กราฟ
    ax = fig.add_subplot(111, projection="3d")  # เพิ่มแกนสามมิติ
    surf = ax.plot_surface(NOW, TARGET, VALVE, cmap="viridis", edgecolor="none")  # วาดพื้นผิว
    ax.set_xlabel("อุณหภูมิน้ำปัจจุบัน (°C)")  # ชื่อแกน X
    ax.set_ylabel("อุณหภูมิเป้าหมาย (°C)")  # ชื่อแกน Y
    ax.set_zlabel("ปริมาณน้ำร้อน (%)")  # ชื่อแกน Z
    ax.set_title("Control Surface ของระบบ Fuzzy Logic")  # ชื่อกราฟ
    fig.colorbar(surf, shrink=0.6, aspect=12, label="Valve Opening (%)")  # แถบสี
    fig.tight_layout()  # จัดรูปแบบกราฟ
    fig.savefig(f"{OUT_DIR}/2_control_surface.png", dpi=150)  # บันทึกกราฟ
    plt.close(fig)  # ปิดกราฟ


def simulate_scenario(fc: FuzzyBathController, t_now_init, t_target,
                      t_hot=60.0, t_cold=15.0, k=0.25, steps=40):
    """จำลองการผสมน้ำแบบ First-order ตามจำนวน time step."""
    t_now = t_now_init  # อุณหภูมิเริ่มต้นในอ่าง
    temps = [t_now]  # เก็บอุณหภูมิ รวมค่าเริ่มต้น
    valves = []  # เก็บค่าเปิดวาล์วของแต่ละรอบ

    for _ in range(steps):  # ทำซ้ำตามจำนวนรอบ
        valve_opening, *_ = fc.compute(t_now, t_target)  # ให้ Fuzzy คำนวณวาล์ว
        valves.append(valve_opening)  # บันทึกค่าเปิดวาล์ว
        t_mix_in = t_cold + (valve_opening / 100.0) * (t_hot - t_cold)  # อุณหภูมิน้ำผสมเข้า
        t_now = t_now + k * (t_mix_in - t_now)  # อัปเดตอุณหภูมิแบบ First-order
        temps.append(t_now)  # บันทึกอุณหภูมิใหม่

    return np.array(temps), np.array(valves)  # คืนผลเป็น NumPy Array


def plot_simulation_scenarios(fc: FuzzyBathController):
    """จำลอง 3 สถานการณ์และวาดอุณหภูมิกับวาล์วเทียบเวลา."""
    scenarios = [  # เลือกกรณีทดสอบให้ครอบคลุมหลายระดับ
        {"label": "น้ำเย็นเริ่มต้น 10°C, เป้าหมาย 32°C (Low)", "t_now": 10, "t_target": 32},
        {"label": "น้ำเย็นเริ่มต้น 10°C, เป้าหมาย 42°C (High)", "t_now": 10, "t_target": 42},
        {"label": "น้ำอุ่นเริ่มต้น 33°C, เป้าหมาย 36°C (Medium)", "t_now": 33, "t_target": 36},
    ]
    fig, axes = plt.subplots(len(scenarios), 2, figsize=(11, 10))  # กราฟ 3 แถว 2 คอลัมน์

    for row, sc in enumerate(scenarios):  # วนทีละสถานการณ์
        temps, valves = simulate_scenario(fc, sc["t_now"], sc["t_target"])  # รัน simulation
        t_axis_temp = np.arange(len(temps))  # แกนเวลาของอุณหภูมิ
        t_axis_valve = np.arange(len(valves))  # แกนเวลาของวาล์ว

        axes[row, 0].plot(t_axis_temp, temps, color="tab:red", marker="o", markersize=3)  # อุณหภูมิ
        axes[row, 0].axhline(sc["t_target"], color="black", linestyle="--", label="Target")  # เป้าหมาย
        axes[row, 0].set_title(f"อุณหภูมิน้ำ vs เวลา\n{sc['label']}")  # ชื่อกราฟ
        axes[row, 0].set_xlabel("Time step")  # ชื่อแกนนอน
        axes[row, 0].set_ylabel("Temperature (°C)")  # ชื่อแกนตั้ง
        axes[row, 0].legend()  # แสดงคำอธิบาย
        axes[row, 0].grid(alpha=0.3)  # แสดงตาราง

        axes[row, 1].plot(t_axis_valve, valves, color="tab:blue", marker="o", markersize=3)  # วาล์ว
        axes[row, 1].set_title(f"ปริมาณน้ำร้อน (วาล์ว %) vs เวลา\n{sc['label']}")  # ชื่อกราฟ
        axes[row, 1].set_xlabel("Time step")  # ชื่อแกนนอน
        axes[row, 1].set_ylabel("Valve Opening (%)")  # ชื่อแกนตั้ง
        axes[row, 1].grid(alpha=0.3)  # แสดงตาราง

        final_temp = temps[-1]  # อ่านอุณหภูมิสุดท้าย
        error = abs(sc["t_target"] - final_temp)  # คำนวณ error แบบค่าสัมบูรณ์
        print(f"[Scenario] {sc['label']}")  # แสดงชื่อกรณีใน console
        print(f"    -> อุณหภูมิสุดท้ายหลัง {len(temps)-1} step = {final_temp:.2f} °C "
              f"(ค่าคลาดเคลื่อนจากเป้าหมาย = {error:.3f} °C)")  # แสดงผลวิเคราะห์

    fig.tight_layout()  # จัดระยะห่าง
    fig.savefig(f"{OUT_DIR}/3_time_simulation.png", dpi=150)  # บันทึกกราฟ
    plt.close(fig)  # ปิดกราฟ


def print_example_inference(fc: FuzzyBathController, t_now, t_target):
    """พิมพ์รายละเอียด Fuzzification และกฎของตัวอย่าง."""
    valve_opening, _, fired_rules, now_deg, target_deg = fc.compute(t_now, t_target)  # เรียก Fuzzy
    print("=" * 60)  # เส้นคั่น
    print(f"ตัวอย่างการคำนวณ: T_now = {t_now} °C, T_target = {t_target} °C")  # แสดง input
    print("-" * 60)  # เส้นคั่นย่อย
    print("ค่าความเป็นสมาชิกของ Input 1 (อุณหภูมิน้ำปัจจุบัน):")  # หัวข้อ
    for k, v in now_deg.items():  # วนค่าของ current temperature
        print(f"    {k:8s} = {v:.3f}")  # แสดง membership
    print("ค่าความเป็นสมาชิกของ Input 2 (อุณหภูมิเป้าหมาย):")  # หัวข้อ
    for k, v in target_deg.items():  # วนค่าของ target temperature
        print(f"    {k:8s} = {v:.3f}")  # แสดง membership
    print("กฎที่ถูกกระตุ้น (Firing strength > 0):")  # หัวข้อกฎ
    for now_term, target_term, valve_term, strength in fired_rules:  # วนกฎที่ทำงาน
        print(f"    IF now={now_term:5s} AND target={target_term:6s} "
              f"THEN valve={valve_term:8s}   (firing strength = {strength:.3f})")  # แสดงกฎ
    print(f"ผลลัพธ์หลัง Defuzzification (Centroid): ปริมาณน้ำร้อน = {valve_opening:.2f} %")  # output
    print("=" * 60)  # ปิดส่วนแสดงผล


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)  # สร้างโฟลเดอร์ output ถ้ายังไม่มี
    fc = FuzzyBathController()  # สร้างตัวควบคุม
    print("กำลังวาดกราฟฟังก์ชันสมาชิก (membership functions) ...")  # แจ้งสถานะ
    plot_membership_functions(fc)  # สร้างกราฟ Membership
    print("กำลังวาด control surface ...")  # แจ้งสถานะ
    plot_control_surface(fc)  # สร้างกราฟ Control Surface
    print("กำลังจำลองการทำงานของระบบตามเวลา (time-domain simulation) ...")  # แจ้งสถานะ
    plot_simulation_scenarios(fc)  # สร้างกราฟ simulation
    print()  # เว้นบรรทัด
    print_example_inference(fc, t_now=15, t_target=40)  # แสดงตัวอย่าง inference
    print()  # เว้นบรรทัด
    print(f"บันทึกกราฟทั้งหมดไว้ในโฟลเดอร์ '{OUT_DIR}/' เรียบร้อยแล้ว")  # แจ้งผลสำเร็จ
