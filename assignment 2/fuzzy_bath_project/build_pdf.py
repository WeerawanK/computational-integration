"""สร้างไฟล์ PDF รายงานจากผลจำลองและซอร์สโค้ดปัจจุบัน."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from fuzzy_controller import FuzzyBathController
from simulate import simulate_scenario


ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "fuzzy_bath_report.pdf"
FONT_PATH = Path(r"C:\Windows\Fonts\tahoma.ttf")
pdfmetrics.registerFont(TTFont("Thai", str(FONT_PATH)))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="ThaiBody", parent=styles["BodyText"], fontName="Thai",
                          fontSize=10, leading=15, spaceAfter=7))
styles.add(ParagraphStyle(name="ThaiH1", parent=styles["Title"], fontName="Thai",
                          fontSize=20, leading=28, alignment=TA_CENTER, textColor=colors.HexColor("#174a7e")))
styles.add(ParagraphStyle(name="ThaiH2", parent=styles["Heading2"], fontName="Thai",
                          fontSize=15, leading=20, textColor=colors.HexColor("#174a7e"), spaceBefore=12))
styles.add(ParagraphStyle(name="ThaiH3", parent=styles["Heading3"], fontName="Thai",
                          fontSize=11, leading=15, textColor=colors.HexColor("#174a7e")))
styles.add(ParagraphStyle(name="ThaiCaption", parent=styles["BodyText"], fontName="Thai",
                          fontSize=8, leading=11, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="CodeThai", fontName="Thai", fontSize=7, leading=9))


def P(text, style="ThaiBody"):
    return Paragraph(text, styles[style])


def table(data, widths=None):
    converted = [[P(str(cell), "CodeThai") for cell in row] for row in data]
    result = Table(converted, colWidths=widths, repeatRows=1)
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dceaf7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return result


def build():
    controller = FuzzyBathController()
    story = [
        Spacer(1, 35 * mm),
        P("รายงานการออกแบบและจำลองระบบ<br/>ควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic", "ThaiH1"),
        Spacer(1, 8 * mm),
        P("Mamdani Fuzzy Inference System", "ThaiH2"),
        Spacer(1, 35 * mm),
        P("Computer Assignment 2<br/>ภาคเรียนที่ 1 ปีการศึกษา 2569<br/><br/>หัวข้อ: Fuzzy Bath Water Temperature Control", "ThaiBody"),
        PageBreak(),
        P("บทคัดย่อ", "ThaiH2"),
        P("รายงานนี้นำเสนอระบบควบคุมอุณหภูมิน้ำอาบโดยใช้ตรรกศาสตร์คลุมเครือแบบ Mamdani เพื่อคำนวณเปอร์เซ็นต์การเปิดวาล์วน้ำร้อนจากอุณหภูมิน้ำปัจจุบันและอุณหภูมิเป้าหมาย ระบบใช้ AND = min, implication และ aggregation = max และ defuzzification แบบ centroid ผลการทดลองสามกรณีมี steady-state error อยู่ในช่วง 0.383–1.500°C"),
        P("1. ลักษณะการทำงานของระบบ", "ThaiH2"),
        P("อินพุตมี 2 ค่า ได้แก่ อุณหภูมิน้ำปัจจุบัน (0–60°C) และอุณหภูมิเป้าหมาย (25–45°C) เอาต์พุตคือเปอร์เซ็นต์การเปิดวาล์วน้ำร้อน (0–100%) ขั้นตอนคือ fuzzification, rule evaluation, implication, aggregation และ centroid defuzzification"),
        P("แบบจำลองพลวัต: T_mix = T_cold + (u/100)(T_hot − T_cold) และ T(t+1) = T(t) + k(T_mix − T(t)) โดยใช้ T_hot=60°C, T_cold=15°C และ k=0.25"),
        P("1.1 ฟังก์ชันสมาชิก", "ThaiH3"),
        P("อุณหภูมิปัจจุบันแบ่งเป็น Cold, Cool, Warm, Hot; เป้าหมายแบ่งเป็น Low, Medium, High; วาล์วแบ่งเป็น VeryLow, Low, Medium, High, VeryHigh"),
        Image(str(ROOT / "outputs" / "1_membership_functions.png"), width=160 * mm, height=180 * mm),
        P("รูปที่ 1 ฟังก์ชันสมาชิกของอินพุตและเอาต์พุต", "ThaiCaption"),
        P("1.2 ฐานกฎ", "ThaiH3"),
    ]
    labels = {"Cold": "เย็น", "Cool": "ค่อนข้างเย็น", "Warm": "อุ่น", "Hot": "ร้อน",
              "Low": "ต่ำ", "Medium": "ปานกลาง", "High": "สูง",
              "VeryLow": "ต่ำมาก", "VeryHigh": "สูงมาก"}
    rows = [["ลำดับ", "อุณหภูมิปัจจุบัน", "เป้าหมาย", "วาล์วน้ำร้อน"]]
    for i, (a, b, c) in enumerate(controller.rules, 1):
        rows.append([i, labels[a], labels[b], labels[c]])
    story.append(table(rows, [18 * mm, 48 * mm, 38 * mm, 45 * mm]))
    story += [
        P("2. Simulation ผลการทดลอง และการวิเคราะห์", "ThaiH2"),
        Image(str(ROOT / "outputs" / "2_control_surface.png"), width=160 * mm, height=120 * mm),
        P("รูปที่ 2 ความสัมพันธ์ระหว่างอุณหภูมิปัจจุบัน เป้าหมาย และวาล์ว", "ThaiCaption"),
        P("จำลอง 40 time steps ต่อกรณี โดยคำนวณวาล์วใหม่ทุก step จากอุณหภูมิที่วัดได้", "ThaiBody"),
    ]
    result_rows = [["สภาวะเริ่มต้น", "เป้าหมาย", "สุดท้าย", "error", "วาล์วเริ่ม", "วาล์วสุดท้าย"]]
    scenarios = [("10°C (น้ำเย็น)", 10, 32), ("10°C (น้ำเย็น)", 10, 42), ("33°C (น้ำอุ่น)", 33, 36)]
    for name, initial, target in scenarios:
        temps, valves = simulate_scenario(controller, initial, target)
        result_rows.append([name, f"{target}°C", f"{temps[-1]:.2f}°C", f"{abs(target-temps[-1]):.3f}°C",
                            f"{valves[0]:.2f}%", f"{valves[-1]:.2f}%"])
    story.append(table(result_rows, [38 * mm, 23 * mm, 25 * mm, 24 * mm, 28 * mm, 28 * mm]))
    story += [
        Image(str(ROOT / "outputs" / "3_time_simulation.png"), width=165 * mm, height=150 * mm),
        P("รูปที่ 3 อุณหภูมิและเปอร์เซ็นต์วาล์วตลอดการจำลอง", "ThaiCaption"),
        P("การวิเคราะห์: กรณีเป้าหมาย 42°C มี error ต่ำสุด 0.383°C เพราะกฎ Cold–High ให้ความร้อนสูง กรณีเป้าหมาย 32°C มี error 0.823°C ส่วนกรณีเริ่มที่ 33°C และเป้าหมาย 36°C มี error สูงสุด 1.500°C เนื่องจากระบบใช้สมดุลน้ำร้อน/น้ำเย็นและไม่มีอินพุต error โดยตรง ข้อจำกัดของแบบจำลองคือยังไม่รวมอัตราการไหลจริง การสูญเสียความร้อน และ noise ของเซนเซอร์", "ThaiBody"),
        P("3. สรุปผล", "ThaiH2"),
        P("ระบบ Mamdani สามารถแปลงอุณหภูมิแบบ crisp เป็นคำสั่งเปิดวาล์วน้ำร้อนอย่างต่อเนื่องและอธิบายได้ด้วยฐานกฎ 12 ข้อ ระบบเข้าใกล้เป้าหมายในทุกกรณี โดย error สูงสุด 1.500°C เหมาะสำหรับเป็นต้นแบบระบบควบคุมแบบ approximate reasoning", "ThaiBody"),
        PageBreak(),
        P("ภาคผนวก: โปรแกรม", "ThaiH2"),
    ]
    for filename in ["membership.py", "fuzzy_controller.py", "simulate.py"]:
        story += [P(filename, "ThaiH3"),
                  Preformatted((ROOT / filename).read_text(encoding="utf-8"),
                               ParagraphStyle(f"code-{filename}", fontName="Thai", fontSize=6.2, leading=7.2))]
    SimpleDocTemplate(str(PDF_PATH), pagesize=A4, rightMargin=14 * mm, leftMargin=14 * mm,
                      topMargin=12 * mm, bottomMargin=12 * mm, title="Fuzzy Bath Water Temperature Control").build(story)
    print(f"สร้าง PDF แล้ว: {PDF_PATH}")


if __name__ == "__main__":
    build()
