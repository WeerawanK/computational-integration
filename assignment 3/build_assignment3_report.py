"""Create the Assignment 3 PDF report from the pure-Python experiment."""

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Preformatted, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "assignment3_report.pdf"
DATA_SOURCE = "https://myweb.cmu.ac.th/sansanee.a/IntroCI/dataset/wdbc.data"
pdfmetrics.registerFont(TTFont("Thai", r"C:\Windows\Fonts\tahoma.ttf"))

BLUE = colors.HexColor("#173F67")
LIGHT = colors.HexColor("#EAF2F8")
GRAY = colors.HexColor("#666666")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="ThaiBody", fontName="Thai", fontSize=10.2, leading=16, alignment=TA_JUSTIFY, spaceAfter=7))
styles.add(ParagraphStyle(name="ThaiH1", fontName="Thai", fontSize=17, leading=23, textColor=BLUE, spaceBefore=8, spaceAfter=10))
styles.add(ParagraphStyle(name="ThaiH2", fontName="Thai", fontSize=13, leading=18, textColor=BLUE, spaceBefore=8, spaceAfter=6))
styles.add(ParagraphStyle(name="ThaiCaption", fontName="Thai", fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=GRAY, spaceAfter=7))
styles.add(ParagraphStyle(name="ThaiCover", fontName="Thai", fontSize=22, leading=31, alignment=TA_CENTER, textColor=BLUE))
styles.add(ParagraphStyle(name="ThaiSub", fontName="Thai", fontSize=13, leading=20, alignment=TA_CENTER, textColor=GRAY))
styles.add(ParagraphStyle(name="CodeThai", fontName="Thai", fontSize=6.2, leading=7.7))


def P(text, style="ThaiBody"):
    return Paragraph(text, styles[style])


def load_results():
    rows = []
    with (ROOT / "results.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("configuration") == "summary" or not row.get("fold"):
                break
            rows.append(row)
    summaries = {}
    with (ROOT / "results.csv").open(encoding="utf-8") as f:
        in_summary = False
        for row in csv.reader(f):
            if row and row[0] == "summary":
                in_summary = True
                next(f, None)
                continue
            if in_summary and row and row[0] != "configuration":
                summaries[row[0]] = row
    return rows, summaries


def make_table(rows, widths, font_size=8.4):
    data = []
    for i, row in enumerate(rows):
        data.append([Paragraph(str(value), ParagraphStyle(f"cell{i}", fontName="Thai", fontSize=font_size, leading=font_size + 3, alignment=TA_CENTER)) for value in row])
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#7A8A99")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def header_footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(colors.HexColor("#B9D5EA"))
        canvas.line(14 * mm, 287 * mm, 196 * mm, 287 * mm)
        canvas.setFont("Thai", 8)
        canvas.setFillColor(GRAY)
        canvas.drawString(14 * mm, 291 * mm, "Assignment 3 - MLP Training with Genetic Algorithms")
        canvas.drawRightString(196 * mm, 9 * mm, f"หน้า {doc.page}")
    canvas.restoreState()


def build():
    rows, summaries = load_results()
    doc = BaseDocTemplate(str(PDF_PATH), pagesize=A4, rightMargin=14 * mm, leftMargin=14 * mm, topMargin=18 * mm, bottomMargin=15 * mm, title="Assignment 3 MLP Training with Genetic Algorithms")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=header_footer)])
    story = [Spacer(1, 42 * mm), P("รายงานการฝึก Multilayer Perceptron", "ThaiCover"), P("ด้วย Genetic Algorithms", "ThaiCover"), Spacer(1, 8 * mm), P("การจำแนกข้อมูล Wisconsin Diagnostic Breast Cancer", "ThaiSub"), Spacer(1, 35 * mm), P("Computer Assignment 3<br/>ภาคเรียนที่ 1 ปีการศึกษา 2569<br/><br/>ผู้จัดทำ: นางสาววีระวรรณ ก้อนคำ<br/>รหัสนักศึกษา: 670610782<br/>รายวิชา: Introduction to Computational Intelligence<br/>คณะวิศวกรรมศาสตร์ มหาวิทยาลัยเชียงใหม่", "ThaiSub"), PageBreak()]

    story += [P("บทคัดย่อ", "ThaiH1"), P("รายงานนี้นำเสนอการฝึก Multilayer Perceptron (MLP) ด้วย Genetic Algorithms โดยเขียนกลไกเครือข่ายประสาท การส่งค่าผ่านเครือข่าย การเข้ารหัสน้ำหนักเป็น chromosome การคัดเลือก การ crossover และการ mutation ด้วย Python มาตรฐาน โดยไม่ใช้ไลบรารี machine learning หรือไลบรารีสำหรับสร้างรูปภาพ ข้อมูลที่ใช้คือ WDBC ซึ่งมี 569 samples, 30 features และ 2 classes ระบบถูกประเมินด้วย stratified 10-fold cross-validation และเปรียบเทียบโครงสร้าง hidden layer และจำนวน nodes 4 รูปแบบ ผลการทดลองพบว่าโครงสร้าง 1 hidden layer 8 nodes ให้ accuracy เฉลี่ยสูงสุด 91.73% ตามด้วย 1 hidden layer 16 nodes ที่ 91.53% ขณะที่โครงสร้างสอง hidden layers ให้ผลต่ำกว่าในรอบการทดลองนี้"), P("คำสำคัญ: Multilayer Perceptron, Genetic Algorithms, 10-fold Cross-validation, WDBC") , P("สารบัญ", "ThaiH1"), P("1 ลักษณะการทำงานของระบบ ........................................................ 3", "ThaiBody"), P("2 Simulation ผลการทดลอง และการวิเคราะห์ ................................. 7", "ThaiBody"), P("3 โปรแกรม .................................................................................. 11", "ThaiBody"), PageBreak()]

    story += [P("1 ลักษณะการทำงานของระบบ", "ThaiH1"), P("1.1 ข้อมูลนำเข้าและการเตรียมข้อมูล", "ThaiH2"), P(f"ใช้ข้อมูล WDBC จากแหล่งข้อมูลที่โจทย์กำหนด: {DATA_SOURCE} แต่ละแถวมี 32 ค่า ได้แก่ ID, diagnosis และ features จำนวน 30 ค่า ในการทดลองนี้ไม่นำ ID มาเป็น feature เพราะเป็นเพียงตัวระบุ sample ส่วน diagnosis ถูกแปลงเป็น label โดย B = 0 และ M = 1 ก่อนนำข้อมูลเข้าสู่เครือข่าย"), P("เพื่อให้การคำนวณของ sigmoid มีเสถียรภาพ โปรแกรมใช้ min-max scaling แยกตาม feature โดย fit ค่า minimum และ maximum จาก training fold เท่านั้น แล้วนำค่าดังกล่าวไปแปลงทั้ง training และ test fold เพื่อป้องกันข้อมูลจาก test fold รั่วไหลเข้าสู่การฝึก"), P("1.2 โครงสร้าง MLP", "ThaiH2"), P("MLP ประกอบด้วย input layer จำนวน 30 nodes, hidden layer ตาม configuration ที่กำหนด และ output layer 1 node โดยใช้ sigmoid activation ทุก layer เอาต์พุตถูกแปลงเป็น class ด้วย threshold 0.5 การคำนวณ bias ถูกเก็บเป็นน้ำหนักตัวสุดท้ายของแต่ละ neuron"), P("1.3 Genetic Algorithms", "ThaiH2"), P("หนึ่ง chromosome แทนค่าน้ำหนักและ bias ทั้งหมดของ MLP การฝึกประกอบด้วยการสร้างประชากรแบบสุ่ม การคำนวณ fitness จาก accuracy หักด้วย 0.05 เท่าของ mean squared error การเก็บ elite การเลือก parent ด้วย tournament selection การทำ arithmetic crossover และ Gaussian mutation กระบวนการทำซ้ำ 20 generations โดยใช้ population 16 ตัวต่อ configuration และ fold"), P("1.4 การตรวจสอบ validity", "ThaiH2"), P("ใช้ stratified 10-fold cross-validation โดยแบ่งตัวอย่างของแต่ละ class กระจายไปยัง 10 folds ใกล้เคียงกัน ในแต่ละรอบใช้ 9 folds เป็น training set และ 1 fold เป็น test set จากนั้นรายงานค่า accuracy, sensitivity, specificity และ mean squared error ของ test fold"), make_table([["รายการ", "ค่าที่ใช้"], ["จำนวน samples", "569"], ["จำนวน features", "30"], ["จำนวน classes", "2 (B และ M)"], ["Cross-validation", "Stratified 10-fold"], ["Population / generations", "16 / 20"], ["Mutation", "อัตรา 0.08, sigma 0.25"], ["การเลือก", "Tournament size 3 และ elitism"]], [55 * mm, 125 * mm]), PageBreak()]

    story += [P("2 Simulation ผลการทดลอง และการวิเคราะห์", "ThaiH1"), P("2.1 Configurations ที่เปรียบเทียบ", "ThaiH2"), make_table([["Configuration", "Hidden layers", "Nodes"], ["8", "1", "8"], ["16", "1", "16"], ["8-8", "2", "8 + 8"], ["12-6", "2", "12 + 6"]], [45 * mm, 45 * mm, 45 * mm]), P("การเปลี่ยน configuration ช่วยให้เห็นผลของจำนวน hidden layer และจำนวน nodes ต่อความสามารถในการเรียนรู้และความแปรผันของผลลัพธ์จาก Genetic Algorithms"), P("2.2 ผลการทดลองแบบ 10-fold cross-validation", "ThaiH2")]
    summary_rows = [["Configuration", "Accuracy mean", "SD", "Sensitivity", "Specificity", "MSE"]]
    for config in ["8", "16", "8-8", "12-6"]:
        row = summaries[config]
        summary_rows.append([config, f"{float(row[2])*100:.2f}%", f"{float(row[3])*100:.2f}%", f"{float(row[4])*100:.2f}%", f"{float(row[5])*100:.2f}%", f"{float(row[6]):.5f}"])
    story += [make_table(summary_rows, [28 * mm, 34 * mm, 25 * mm, 31 * mm, 31 * mm, 25 * mm], 8), P("ตารางที่ 1 ค่าเฉลี่ยผลการทดสอบจาก 10 folds", "ThaiCaption"), P("โครงสร้าง 8 nodes มี accuracy เฉลี่ยสูงสุด 91.73% และมีส่วนเบี่ยงเบนมาตรฐาน 4.24 percentage points แสดงว่าผลมีความสม่ำเสมอที่สุดในกลุ่มที่ทดลอง โครงสร้าง 16 nodes ให้ผลใกล้เคียงกันที่ 91.53% แต่ใช้เวลาประมวลผลเฉลี่ยต่อ fold สูงกว่า"), P("2.3 ผลราย fold และ confusion matrix", "ThaiH2")]
    detail_rows = [["Config", "Fold", "Accuracy", "Sensitivity", "Specificity", "TP", "TN", "FP", "FN"]]
    for row in rows:
        if row["fold"] in {"1", "2", "3"}:
            detail_rows.append([row["configuration"], row["fold"], f"{float(row['test_accuracy'])*100:.2f}%", f"{float(row['test_sensitivity'])*100:.2f}%", f"{float(row['test_specificity'])*100:.2f}%", row["tp"], row["tn"], row["fp"], row["fn"]])
    story += [make_table(detail_rows, [23 * mm, 16 * mm, 27 * mm, 30 * mm, 30 * mm, 15 * mm, 15 * mm, 15 * mm, 15 * mm], 7.4), P("ตารางที่ 2 ตัวอย่างผลราย fold ของแต่ละ configuration (fold 1-3)", "ThaiCaption"), P("2.4 การวิเคราะห์", "ThaiH2"), P("ผลที่ได้แสดงว่าโครงสร้างที่ใหญ่ขึ้นไม่ได้รับประกัน accuracy ที่สูงขึ้น ในการทดลองนี้ 1 hidden layer ให้ผลดีกว่า 2 hidden layers โดย 8 nodes ให้ผลดีที่สุดเล็กน้อยเมื่อเทียบกับ 16 nodes สาเหตุหนึ่งอาจมาจากจำนวน generations และ population ที่จำกัด ทำให้โครงสร้างที่มีจำนวน weights มากต้องใช้การค้นหานานขึ้นจึงจะเข้าใกล้ optimum"), P("เมื่อพิจารณา sensitivity โครงสร้าง 8 และ 16 nodes มีค่าใกล้เคียงกันประมาณ 87.2% ส่วนโครงสร้าง 8-8 มี sensitivity ต่ำสุด 80.7% จึงพลาด malignant samples มากกว่าในรอบการทดลองนี้ ขณะที่ specificity ของทุก configuration อยู่ใกล้ 94% ซึ่งหมายถึงการจำแนก benign ทำได้ค่อนข้างดี"), P("ผลลัพธ์มีความแปรผันระหว่าง folds เพราะ GA เริ่มต้นประชากรแบบสุ่มและการแบ่งข้อมูลแต่ละ fold มีองค์ประกอบต่างกัน ตัวอย่างเช่น configuration 8-8 มี accuracy ราย fold อยู่ในช่วงประมาณ 73.2%-96.5% ดังนั้นควรรายงานค่าเฉลี่ยร่วมกับส่วนเบี่ยงเบนมาตรฐาน ไม่ควรสรุปจาก fold เดียว"), PageBreak()]

    story += [P("3 โปรแกรม", "ThaiH1"), P("โปรแกรมฉบับเต็มที่ใช้ในการทดลองแนบในภาคผนวกด้านล่าง โปรแกรมใช้เฉพาะ Python standard library และไม่มีการใช้ library สำหรับวาดรูปหรือโมเดล machine learning สำเร็จรูป ไฟล์ผลลัพธ์เชิงตารางจากการทดลองเก็บไว้ใน results.csv"), P("3.1 วิธีรันโปรแกรม", "ThaiH2"), P("วางไฟล์ wdbc.data ไว้ในโฟลเดอร์เดียวกับ mlp_ga.py แล้วรันคำสั่ง python mlp_ga.py โปรแกรมจะสร้าง results.csv ซึ่งประกอบด้วยผลราย fold และ summary ของแต่ละ configuration"), P("เอกสารอ้างอิง", "ThaiH1"), P("[1] UCI Machine Learning Repository, Breast Cancer Wisconsin (Diagnostic) Data Set, wdbc.data. แหล่งข้อมูลตามโจทย์: " + DATA_SOURCE), P("[2] L. A. Zadeh, Fuzzy Sets, Information and Control, 1965. แนวคิดพื้นฐานของการรายงานผลระบบอัจฉริยะถูกใช้เป็นรูปแบบการจัดโครงสร้างรายงานจาก Assignment 2."), PageBreak(), P("ภาคผนวก โปรแกรม mlp_ga.py", "ThaiH1")]
    source = (ROOT / "mlp_ga.py").read_text(encoding="utf-8")
    story.append(Preformatted(source, styles["CodeThai"]))
    doc.build(story)
    print(f"สร้าง PDF แล้ว: {PDF_PATH}")


if __name__ == "__main__":
    build()
