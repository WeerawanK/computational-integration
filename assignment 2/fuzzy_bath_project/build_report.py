"""สร้างรายงาน HTML พร้อมกราฟและภาคผนวกโปรแกรมจากไฟล์ต้นฉบับปัจจุบัน."""

from html import escape
from pathlib import Path

from fuzzy_controller import FuzzyBathController
from simulate import simulate_scenario


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"


def scenario_rows(controller):
    scenarios = [
        ("น้ำเย็นเริ่มต้น 10°C", 10, 32, "ต่ำ"),
        ("น้ำเย็นเริ่มต้น 10°C", 10, 42, "สูง"),
        ("น้ำอุ่นเริ่มต้น 33°C", 33, 36, "ปานกลาง"),
    ]
    rows = []
    for label, initial, target, level in scenarios:
        temps, valves = simulate_scenario(controller, initial, target)
        final_temp = temps[-1]
        error = abs(target - final_temp)
        rows.append(
            f"<tr><td>{escape(label)}</td><td>{target:.0f}</td><td>{level}</td>"
            f"<td>{final_temp:.2f}</td><td>{error:.3f}</td>"
            f"<td>{valves[0]:.2f}</td><td>{valves[-1]:.2f}</td></tr>"
        )
    return "\n".join(rows)


def rule_rows(controller):
    labels = {
        "Cold": "เย็น", "Cool": "ค่อนข้างเย็น", "Warm": "อุ่น", "Hot": "ร้อน",
        "Low": "ต่ำ", "Medium": "ปานกลาง", "High": "สูง",
        "VeryLow": "ต่ำมาก", "VeryHigh": "สูงมาก",
    }
    return "\n".join(
        f"<tr><td>{i}</td><td>{labels[a]}</td><td>{labels[b]}</td><td>{labels[c]}</td></tr>"
        for i, (a, b, c) in enumerate(controller.rules, 1)
    )


def appendix():
    files = ["membership.py", "fuzzy_controller.py", "simulate.py"]
    sections = []
    for filename in files:
        source = (ROOT / filename).read_text(encoding="utf-8")
        sections.append(f"<h3>{filename}</h3><pre>{escape(source)}</pre>")
    return "\n".join(sections)


def build():
    controller = FuzzyBathController()
    html = f"""<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<title>รายงานระบบควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic</title>
<style>
@page {{ size: A4; margin: 18mm 16mm; }}
body {{ font-family: "Leelaw UI", Tahoma, sans-serif; color:#202124; line-height:1.55; font-size:11pt; }}
h1,h2,h3 {{ color:#174a7e; }} h1 {{ text-align:center; font-size:25pt; margin-top:45mm; }}
h2 {{ border-bottom:2px solid #2d6ca2; padding-bottom:4px; margin-top:22px; }}
h3 {{ margin-bottom:4px; }} .cover {{ page-break-after:always; text-align:center; }}
.subtitle {{ font-size:16pt; margin:22px 0; }} .meta {{ margin-top:40mm; font-size:12pt; }}
.figure {{ text-align:center; margin:14px 0; page-break-inside:avoid; }}
.figure img {{ max-width:100%; max-height:245mm; }} .caption {{ font-size:10pt; }}
table {{ border-collapse:collapse; width:100%; margin:8px 0 14px; page-break-inside:avoid; }}
th,td {{ border:1px solid #777; padding:5px 7px; text-align:center; }}
th {{ background:#dceaf7; }} .note {{ background:#eef6fc; border-left:4px solid #2d6ca2; padding:8px 12px; }}
pre {{ white-space:pre-wrap; font:8pt Consolas, "Courier New", monospace; background:#f4f4f4;
      border:1px solid #ccc; padding:8px; page-break-inside:auto; }}
.pagebreak {{ page-break-before:always; }} li {{ margin:4px 0; }}
</style></head><body>
<section class="cover">
<h1>รายงานการออกแบบและจำลองระบบ<br>ควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic</h1>
<div class="subtitle">Mamdani Fuzzy Inference System</div>
<div class="meta">Computer Assignment 2<br>
ภาคเรียนที่ 1 ปีการศึกษา 2569<br><br>
หัวข้อ: Fuzzy Bath Water Temperature Control</div>
</section>

<h2>บทคัดย่อ</h2>
<p>รายงานนี้นำเสนอระบบควบคุมอุณหภูมิน้ำอาบโดยใช้ตรรกศาสตร์คลุมเครือแบบ Mamdani
เพื่อคำนวณเปอร์เซ็นต์การเปิดวาล์วน้ำร้อนจากอุณหภูมิน้ำปัจจุบันและอุณหภูมิเป้าหมาย
ระบบใช้การอนุมานแบบ AND = min, implication และ aggregation = max และ
defuzzification แบบ centroid จากนั้นทดสอบด้วยแบบจำลองก๊อกผสมน้ำร้อน/น้ำเย็น
แบบ first-order ผลการทดลองทั้งสามกรณีแสดงว่าระบบปรับอุณหภูมิเข้าใกล้ค่าเป้าหมาย
โดยมี steady-state error อยู่ในช่วง 0.383–1.500°C</p>

<h2>1. ลักษณะการทำงานของระบบ</h2>
<p>อินพุตของระบบมี 2 ค่า ได้แก่ อุณหภูมิน้ำปัจจุบัน (0–60°C) และอุณหภูมิเป้าหมาย
(25–45°C) ส่วนเอาต์พุตคือเปอร์เซ็นต์การเปิดวาล์วน้ำร้อน (0–100%).
การประมวลผลประกอบด้วย 5 ขั้นตอน: fuzzification, rule evaluation,
implication, aggregation และ centroid defuzzification.</p>
<div class="note"><b>แบบจำลองพลวัต:</b>
T_mix = T_cold + (u/100)(T_hot − T_cold) และ
T(t+1) = T(t) + k(T_mix − T(t)) โดยใช้ T_hot=60°C, T_cold=15°C และ k=0.25</div>

<h3>1.1 ฟังก์ชันสมาชิก</h3>
<p>อุณหภูมิปัจจุบันแบ่งเป็น Cold, Cool, Warm, Hot; อุณหภูมิเป้าหมายแบ่งเป็น
Low, Medium, High; และวาล์วน้ำร้อนแบ่งเป็น VeryLow, Low, Medium, High, VeryHigh
โดยใช้ฟังก์ชันสามเหลี่ยมและคางหมูเพื่อให้เกิดการเปลี่ยนผ่านที่ต่อเนื่อง</p>
<div class="figure"><img src="outputs/1_membership_functions.png">
<div class="caption">รูปที่ 1 ฟังก์ชันสมาชิกของอินพุตและเอาต์พุต</div></div>

<h3>1.2 ฐานกฎ</h3>
<table><tr><th>ลำดับ</th><th>อุณหภูมิปัจจุบัน</th><th>เป้าหมาย</th><th>วาล์วน้ำร้อน</th></tr>
{rule_rows(controller)}</table>
<p>ตัวอย่างเช่น ถ้าน้ำปัจจุบันอยู่ในกลุ่ม Cold และเป้าหมายอยู่ในกลุ่ม High
ระบบจะเปิดวาล์ว VeryHigh เพื่อเร่งการเพิ่มอุณหภูมิ ขณะที่กรณี Hot และเป้าหมาย Low
จะใช้ VeryLow เพื่อลดการเติมความร้อน</p>

<h2>2. Simulation ผลการทดลอง และการวิเคราะห์</h2>
<h3>2.1 Control surface</h3>
<div class="figure"><img src="outputs/2_control_surface.png">
<div class="caption">รูปที่ 2 ความสัมพันธ์ระหว่างอุณหภูมิปัจจุบัน เป้าหมาย และวาล์ว</div></div>
<p>พื้นผิวควบคุมแสดงแนวโน้มเชิงเหตุผล: เมื่ออุณหภูมิปัจจุบันต่ำหรือเป้าหมายสูง
เปอร์เซ็นต์วาล์วเพิ่มขึ้น และเมื่ออุณหภูมิปัจจุบันสูงกว่าเป้าหมาย วาล์วลดลง</p>

<h3>2.2 ผลการจำลองแบบ closed-loop</h3>
<p>จำลอง 40 time steps ต่อกรณี โดยวาล์วถูกคำนวณใหม่ทุก step จากอุณหภูมิที่วัดได้</p>
<table><tr><th>สภาวะเริ่มต้น</th><th>เป้าหมาย (°C)</th><th>ระดับ</th>
<th>อุณหภูมิสุดท้าย (°C)</th><th>error (°C)</th><th>วาล์วเริ่มต้น (%)</th><th>วาล์วสุดท้าย (%)</th></tr>
{scenario_rows(controller)}</table>
<div class="figure"><img src="outputs/3_time_simulation.png">
<div class="caption">รูปที่ 3 อุณหภูมิและเปอร์เซ็นต์วาล์วตลอดการจำลอง</div></div>

<h3>2.3 การวิเคราะห์</h3>
<ul>
<li>กรณีเป้าหมาย 42°C เริ่มจาก 10°C มี error 0.383°C ซึ่งต่ำที่สุด เพราะกฎ Cold–High
ให้ความร้อนสูงและการผสมลู่เข้าค่าเป้าหมายได้ดี</li>
<li>กรณีเป้าหมาย 32°C มี error 0.823°C แสดงว่าระบบสามารถลดการเปิดวาล์วเมื่อเข้าใกล้
เป้าหมาย แต่การแบ่งเซตแบบ linguistic ทำให้เกิด error คงค้างเล็กน้อย</li>
<li>กรณีเริ่มที่ 33°C และเป้าหมาย 36°C มี error 1.500°C สูงสุด เนื่องจากระบบต้องรักษา
สมดุลระหว่างน้ำร้อนและน้ำเย็นด้วยเอาต์พุตแบบเปอร์เซ็นต์ และไม่มีอินพุต error โดยตรง</li>
<li>ข้อจำกัดของการทดลองคือเป็นแบบจำลอง first-order ที่ไม่รวมอัตราการไหลจริง
การสูญเสียความร้อน และ noise จากเซนเซอร์ หากนำไปใช้งานจริงควรเพิ่ม calibration,
anti-windup/compensation หรือออกแบบกฎโดยใช้อุณหภูมิคลาดเคลื่อนร่วมด้วย</li>
</ul>

<h2>3. สรุปผล</h2>
<p>ระบบ Mamdani ที่พัฒนาสามารถแปลงข้อมูลอุณหภูมิแบบ crisp เป็นคำสั่งเปิดวาล์วน้ำร้อน
อย่างต่อเนื่องและอธิบายได้ด้วยฐานกฎ 12 ข้อ ผลการจำลองยืนยันว่าระบบตอบสนองตามทิศทาง
ที่ต้องการและเข้าใกล้อุณหภูมิเป้าหมายในทุกกรณี โดย error สูงสุด 1.500°C
เหมาะสำหรับเป็นต้นแบบระบบควบคุมแบบ approximate reasoning</p>

<h2 class="pagebreak">ภาคผนวก: โปรแกรม</h2>
<p>โปรแกรมฉบับเต็มที่ใช้สร้างผลการทดลองแสดงด้านล่าง สามารถรันด้วย
<code>python simulate.py</code> หลังติดตั้งแพ็กเกจจาก <code>requirements.txt</code></p>
{appendix()}
</body></html>"""
    (ROOT / "report.html").write_text(html, encoding="utf-8")
    print(f"รายงานถูกสร้างแล้ว: {ROOT / 'report.html'}")


if __name__ == "__main__":
    build()
