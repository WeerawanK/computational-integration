from pathlib import Path
import csv

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


FOLDER = Path(__file__).parent
OUTPUT = FOLDER / "assignment4_report.docx"


def set_cell_shading(cell, fill):
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def set_cell_text(cell, text, bold=False, color=None, size=10):
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(str(text))
    run.bold = bold
    run.font.name = "Tahoma"
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(document, headers, rows):
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for index, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[index], header, bold=True, color=None, size=9)
        set_cell_shading(table.rows[0].cells[index], "D9EAF7")
    for row in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            set_cell_text(cells[index], value, size=9)
    document.add_paragraph()
    return table


def add_code(document, source):
    for line in source.splitlines():
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 1.0
        run = paragraph.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(7)


def read_summary():
    with open(FOLDER / "summary.csv", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def main():
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

    styles = document.styles
    styles["Normal"].font.name = "Tahoma"
    styles["Normal"].font.size = Pt(11)
    for style_name in ["Heading 1", "Heading 2", "Heading 3"]:
        styles[style_name].font.name = "Tahoma"
        styles[style_name].font.color.rgb = None

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.style = "Title"
    title.add_run("การพยากรณ์ความเข้มข้น Benzene ด้วย MLP และ PSO")
    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run("Prediction of Benzene Concentration using Multilayer Perceptron and Particle Swarm Optimization")
    for text in [
        "Computer Assignment 4",
        "ผู้จัดทำ: นางสาววีระวรรณ ก้อนคำ รหัสนักศึกษา 670610782",
        "รายวิชา Introduction to Computational Intelligence",
        "ภาคเรียนที่ 1 ปีการศึกษา 2569",
        "คณะวิศวกรรมศาสตร์ มหาวิทยาลัยเชียงใหม่",
    ]:
        p = document.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(text)

    document.add_page_break()
    document.add_heading("รายละเอียดรายงาน", level=1)
    document.add_paragraph("หัวข้อ: การพยากรณ์ค่า Benzene ล่วงหน้า 5 วันและ 10 วัน")
    document.add_paragraph("ชุดข้อมูล: AirQualityUCI จาก UCI Machine Learning Repository")
    document.add_paragraph("วิธีการฝึก: Multilayer Perceptron ที่ปรับน้ำหนักด้วย Particle Swarm Optimization")
    document.add_paragraph("ตัวชี้วัด: Mean Absolute Error (MAE)")

    document.add_heading("บทคัดย่อ", level=1)
    document.add_paragraph(
        "รายงานนี้นำเสนอการสร้างโปรแกรมสำหรับฝึก Multilayer Perceptron (MLP) "
        "ด้วย Particle Swarm Optimization (PSO) เพื่อพยากรณ์ค่า Benzene ในชุดข้อมูล AirQualityUCI "
        "ล่วงหน้า 5 วันและ 10 วัน โดยใช้ attribute หมายเลข 3, 6, 8, 10, 11, 12, 13 และ 14 เป็น input "
        "และใช้ attribute หมายเลข 5 เป็น output โปรแกรมอ่านไฟล์ Excel ด้วยโครงสร้าง zip และ XML ของ Python "
        "จากนั้นตัดข้อมูลที่เป็น -200 ซึ่งหมายถึง missing value ออก ปรับขนาดข้อมูลโดยใช้สถิติของ training set "
        "และประเมินด้วย 10-fold cross-validation ผลการทดลองวัดด้วย MAE ในหน่วยของ Benzene เดิม "
        "โดยเปรียบเทียบเครือข่ายที่มีทั้ง 1 และ 2 hidden layers"
    )

    document.add_heading("สารบัญ", level=1)
    for line in [
        "บทที่ 1 บทนำ",
        "บทที่ 2 ทฤษฎีที่เกี่ยวข้อง",
        "บทที่ 3 การออกแบบระบบและวิธีดำเนินงาน",
        "บทที่ 4 ผลการทดลองและการวิเคราะห์",
        "บทที่ 5 สรุปผล ข้อจำกัด และข้อเสนอแนะ",
        "เอกสารอ้างอิง",
        "ภาคผนวก โปรแกรม mlp_pso.py",
    ]:
        document.add_paragraph(line)

    document.add_page_break()
    document.add_heading("บทที่ 1 บทนำ", level=1)
    document.add_heading("1.1 ที่มาและความสำคัญ", level=2)
    document.add_paragraph(
        "การตรวจวัดคุณภาพอากาศมีข้อมูลหลายตัวแปรและเปลี่ยนแปลงตามเวลา ค่า Benzene เป็นหนึ่งในสารมลพิษ "
        "ที่ต้องติดตาม การพยากรณ์ล่วงหน้าช่วยให้สามารถเตรียมการเฝ้าระวังได้ก่อนเกิดค่าที่สูงขึ้น "
        "ในงานนี้จึงนำ MLP มาใช้เป็นแบบจำลองความสัมพันธ์แบบไม่เชิงเส้น และใช้ PSO ค้นหาน้ำหนักของ network "
        "แทนการใช้ backpropagation"
    )
    document.add_heading("1.2 วัตถุประสงค์", level=2)
    document.add_paragraph("1. สร้าง MLP สำหรับพยากรณ์ค่า Benzene ล่วงหน้า 5 วันและ 10 วัน")
    document.add_paragraph("2. ใช้ PSO สำหรับค้นหาน้ำหนักและ bias ของ MLP")
    document.add_paragraph("3. เปรียบเทียบจำนวน hidden layers และจำนวน nodes ด้วย 10-fold cross-validation")
    document.add_paragraph("4. วิเคราะห์ผลด้วย Mean Absolute Error (MAE)")
    document.add_heading("1.3 ขอบเขตของงาน", level=2)
    document.add_paragraph(
        "ใช้ input 8 ตัวตามโจทย์ ได้แก่ PT08.S1, PT08.S2, PT08.S3, PT08.S4, PT08.S5, Temperature, "
        "Relative Humidity และ Absolute Humidity โดยพยากรณ์ค่า Benzene ที่อยู่ห่างไป 120 และ 240 ชั่วโมง"
    )

    document.add_heading("บทที่ 2 ทฤษฎีที่เกี่ยวข้อง", level=1)
    document.add_heading("2.1 Multilayer Perceptron", level=2)
    document.add_paragraph(
        "MLP เป็น feed-forward neural network ประกอบด้วย input layer, hidden layer และ output layer "
        "แต่ละ neuron คำนวณ weighted sum ของ input รวมกับ bias ใน hidden layer ใช้ sigmoid เพื่อสร้างความสัมพันธ์ "
        "แบบไม่เชิงเส้น ส่วน output layer ใช้ค่าตรง ๆ เพราะโจทย์เป็น regression"
    )
    document.add_heading("2.2 Particle Swarm Optimization", level=2)
    document.add_paragraph(
        "PSO มองน้ำหนักทั้งหมดของ MLP เป็นตำแหน่งของ particle แต่ละ particle มีตำแหน่งและความเร็ว "
        "ในแต่ละรอบจะประเมิน MSE ของตำแหน่งนั้น แล้วปรับความเร็วจากประสบการณ์ที่ดีที่สุดของ particle เอง "
        "และตำแหน่งที่ดีที่สุดของฝูง จากนั้นจึงเลื่อนตำแหน่งเพื่อค้นหาน้ำหนักที่ดีขึ้น"
    )
    document.add_heading("2.3 Mean Absolute Error", level=2)
    document.add_paragraph("MAE = (1 / n) × Σ |ค่าจริง - ค่าที่พยากรณ์|")
    document.add_paragraph(
        "MAE มีหน่วยเดียวกับค่า Benzene และตีความได้โดยตรงว่าโดยเฉลี่ยแบบจำลองพยากรณ์คลาดเคลื่อนกี่หน่วย"
    )

    document.add_page_break()
    document.add_heading("บทที่ 3 การออกแบบระบบและวิธีดำเนินงาน", level=1)
    document.add_heading("3.1 ชุดข้อมูล", level=2)
    document.add_paragraph(
        "ใช้ไฟล์ AirQualityUCI.xlsx จากลิงก์ที่กำหนดในโจทย์ โดยโปรแกรมอ่านข้อมูลที่มีค่าในตารางได้ 9,357 แถว "
        "และพบค่า -200 ซึ่งใช้แทน missing value จากนั้นสร้างตัวอย่างแบบ supervised สำหรับแต่ละระยะพยากรณ์ "
        "โดยเหลือ 8,505 ตัวอย่างสำหรับ 5 วัน และ 8,395 ตัวอย่างสำหรับ 10 วัน"
    )
    add_table(document, ["บทบาท", "Attribute", "รายละเอียด"], [
        ["Input", "3", "PT08.S1"], ["Input", "6", "PT08.S2"], ["Input", "8", "PT08.S3"],
        ["Input", "10", "PT08.S4"], ["Input", "11", "PT08.S5"], ["Input", "12-14", "T, RH, AH"],
        ["Output", "5", "Benzene"],
    ])
    document.add_heading("3.2 การเตรียมข้อมูล", level=2)
    document.add_paragraph(
        "ข้อมูลที่มีค่า -200 ใน input หรือ target จะถูกตัดออก การสร้าง target ใช้ค่า Benzene ที่อยู่ถัดไป 120 ชั่วโมง "
        "สำหรับ 5 วัน และ 240 ชั่วโมงสำหรับ 10 วัน ก่อนฝึกแต่ละ fold โปรแกรมคำนวณ mean และ standard deviation "
        "จาก training set เท่านั้น แล้วใช้ค่าเดียวกันกับ test set เพื่อป้องกัน data leakage"
    )
    document.add_heading("3.3 รูปแบบ network ที่ทดลอง", level=2)
    add_table(document, ["Configuration", "Network", "Hidden layers", "จำนวน weight และ bias"], [
        ["8", "8-8-1", "1", "81"],
        ["16", "8-16-1", "1", "161"],
        ["8-8", "8-8-8-1", "2", "153"],
        ["12-6", "8-12-6-1", "2", "193"],
    ])
    document.add_heading("3.4 ขั้นตอนของ PSO", level=2)
    for item in [
        "สร้าง particle จำนวน 12 ตัว โดยสุ่มตำแหน่งน้ำหนักเริ่มต้นในช่วง -1 ถึง 1",
        "คำนวณ MSE ของแต่ละ particle บน training set",
        "บันทึกตำแหน่งที่ดีที่สุดของแต่ละ particle และของฝูง",
        "ปรับ velocity และ position ด้วยค่า inertia, cognitive และ social",
        "ทำซ้ำ 15 iterations แล้วนำ global best ไปประเมินผล",
    ]:
        document.add_paragraph(item, style="List Number")
    document.add_heading("3.5 การตรวจสอบความถูกต้อง", level=2)
    document.add_paragraph(
        "ใช้ 10-fold cross-validation โดยสุ่ม index ด้วย seed คงที่ 2026 ในแต่ละระยะพยากรณ์และแต่ละ configuration "
        "แต่ละ fold ใช้ 9 ส่วนฝึกและ 1 ส่วนทดสอบ จากนั้นรายงานค่า MAE ของ train และ test พร้อมค่าเฉลี่ยและส่วนเบี่ยงเบนมาตรฐาน"
    )

    document.add_page_break()
    document.add_heading("บทที่ 4 ผลการทดลองและการวิเคราะห์", level=1)
    document.add_heading("4.1 ผลการทดลอง", level=2)
    summaries = read_summary()
    rows = []
    for row in summaries:
        rows.append([
            "5 วัน" if row["horizon"] == "5_days" else "10 วัน",
            row["configuration"],
            f"{float(row['train_mae_mean']):.4f}",
            f"{float(row['test_mae_mean']):.4f}",
            f"{float(row['test_mae_stdev']):.4f}",
            f"{float(row['seconds_mean']):.2f}",
        ])
    add_table(document, ["ระยะ", "Configuration", "Train MAE", "Test MAE", "SD", "เวลาเฉลี่ย (วินาที)"], rows)
    document.add_paragraph(
        "ตารางแสดงผลจาก 10 folds ของแต่ละ configuration ค่า Test MAE ใช้ตัดสินความสามารถในการพยากรณ์ข้อมูลที่ไม่เคยเห็น "
        "ดังนั้นค่าที่ต่ำกว่าหมายถึงพยากรณ์ได้ดีกว่า"
    )
    document.add_heading("4.2 การวิเคราะห์ผล", level=2)
    document.add_paragraph(
        "สำหรับการพยากรณ์ล่วงหน้า 5 วัน configuration 8 ให้ค่า Test MAE เฉลี่ยต่ำที่สุดที่ 5.2655 "
        "ขณะที่ 16, 8-8 และ 12-6 มีค่า 5.3657, 5.3476 และ 5.3378 ตามลำดับ แสดงว่าในชุดการทดลองนี้ "
        "การเพิ่มจำนวน nodes หรือเพิ่ม hidden layer ยังไม่ช่วยให้ค่า MAE ลดลง"
    )
    document.add_paragraph(
        "สำหรับการพยากรณ์ล่วงหน้า 10 วัน configuration 8 ให้ค่า Test MAE ต่ำที่สุดที่ 5.2560 "
        "ตามด้วย 8-8 ที่ 5.3206, 16 ที่ 5.3241 และ 12-6 ที่ 5.2722 โดย configuration 12-6 ให้ผลใกล้เคียงกับ 8 "
        "แต่มีความแปรปรวนและเวลาในการฝึกแตกต่างกัน การเปรียบเทียบนี้เป็นแนวโน้มจากชุดทดลอง ไม่ควรสรุปว่า "
        "จำนวน layer ที่มากกว่าจะด้อยกว่าในทุกกรณี"
    )
    document.add_paragraph(
        "เมื่อเปรียบเทียบระยะพยากรณ์ ค่า MAE ของทั้งสองระยะอยู่ใกล้เคียงกันมาก การพยากรณ์ 10 วันไม่ได้แย่กว่า 5 วันอย่างชัดเจน "
        "ซึ่งอาจเกิดจากความสัมพันธ์ของค่า Benzene กับ sensor และสภาพอากาศในข้อมูล รวมถึงข้อจำกัดของจำนวน iteration ของ PSO"
    )
    document.add_heading("4.3 ข้อสังเกตด้านการทดลอง", level=2)
    document.add_paragraph(
        "ค่า MAE ของ train และ test ใกล้กันในทุก configuration จึงยังไม่เห็นสัญญาณ overfitting ที่รุนแรง "
        "อย่างไรก็ตาม ค่า MAE ประมาณ 5 หน่วยควรตีความตามช่วงของ Benzene ในชุดข้อมูล และควรใช้ผลนี้เป็นเครื่องมือช่วยวิเคราะห์ "
        "ไม่ใช่การแทนที่การวัดจากเครื่องมือจริง"
    )

    document.add_page_break()
    document.add_heading("บทที่ 5 สรุปผล ข้อจำกัด และข้อเสนอแนะ", level=1)
    document.add_heading("5.1 สรุปผล", level=2)
    document.add_paragraph(
        "โปรแกรมสามารถฝึก MLP ด้วย PSO และประเมินผลด้วย 10-fold cross-validation ได้ครบทั้งการพยากรณ์ล่วงหน้า 5 วันและ 10 วัน "
        "จากผลการทดลอง configuration 8 ให้ค่า Test MAE เฉลี่ยต่ำที่สุดทั้งสองระยะ คือ 5.2655 และ 5.2560 ตามลำดับ"
    )
    document.add_heading("5.2 ข้อจำกัด", level=2)
    for item in [
        "PSO ใช้ population 12 ตัวและ 15 iterations จึงอาจยังค้นหาน้ำหนักได้ไม่ทั่วพื้นที่",
        "ตัดแถวที่มี missing value ออก ทำให้จำนวนตัวอย่างลดลงจากข้อมูลต้นฉบับ",
        "การแบ่ง fold แบบสุ่มอาจทำให้ข้อมูลเวลาที่อยู่ใกล้กันอยู่ทั้ง train และ test",
        "ยังไม่ได้เปรียบเทียบกับวิธีมาตรฐานอื่น เช่น linear regression หรือ MLP ที่ฝึกด้วย backpropagation",
    ]:
        document.add_paragraph(item, style="List Bullet")
    document.add_heading("5.3 ข้อเสนอแนะ", level=2)
    document.add_paragraph(
        "การทดลองต่อไปอาจเพิ่มจำนวน iterations ปรับ inertia แบบลดลงตามรอบ ใช้การแบ่งข้อมูลแบบ time-series split "
        "และเปรียบเทียบกับ baseline ที่ทำนายด้วยค่า Benzene ล่าสุด นอกจากนี้ควรรายงานค่าความคลาดเคลื่อนในช่วงเวลาอื่น "
        "เพื่อดูว่าแบบจำลองทำงานดีเฉพาะบางช่วงหรือไม่"
    )

    document.add_heading("เอกสารอ้างอิง", level=1)
    document.add_paragraph("[1] UCI Machine Learning Repository, Air Quality Data Set, AirQualityUCI.xlsx.")
    document.add_paragraph("[2] J. Kennedy and R. Eberhart, Particle Swarm Optimization, Proceedings of ICNN, 1995.")
    document.add_paragraph("[3] S. Haykin, Neural Networks and Learning Machines, 3rd ed., Pearson, 2009.")
    document.add_paragraph("[4] Python Software Foundation, Python Standard Library Documentation.")

    document.add_page_break()
    document.add_heading("ภาคผนวก โปรแกรม mlp_pso.py", level=1)
    source = (FOLDER / "mlp_pso.py").read_text(encoding="utf-8")
    add_code(document, source)

    document.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
