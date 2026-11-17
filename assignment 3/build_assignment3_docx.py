from pathlib import Path
import csv

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assignment3_report.docx"
BLUE = "173F67"
LIGHT = "EAF2F8"
GRAY = "666666"


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def cell_text(cell, text, bold=False, color="000000", size=8.5):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(str(text))
    r.bold = bold
    r.font.name = "Tahoma"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(doc, rows, widths=None, size=8.5):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            cell_text(t.cell(i, j), value, bold=i == 0, color="FFFFFF" if i == 0 else "000000", size=size)
            if i == 0:
                shade(t.cell(i, j), BLUE)
            elif i % 2 == 0:
                shade(t.cell(i, j), LIGHT)
            if widths:
                t.cell(i, j).width = Cm(widths[j])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def para(doc, text, style="Normal"):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.add_run(text)
    return p


def heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    return p


def read_results():
    rows = []
    summaries = {}
    with (ROOT / "results.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("fold"):
                break
            rows.append(row)
    with (ROOT / "results.csv").open(encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == "summary":
                next(reader, None)
                for summary in reader:
                    if summary:
                        summaries[summary[0]] = summary
                break
    return rows, summaries


def build():
    rows, summaries = read_results()
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Cm(2.0); sec.bottom_margin = Cm(1.8); sec.left_margin = Cm(2.2); sec.right_margin = Cm(2.2)
    normal = doc.styles["Normal"]
    normal.font.name = "Tahoma"; normal.font.size = Pt(10.5); normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.line_spacing = 1.15
    for name, size in [("Title", 22), ("Heading 1", 17), ("Heading 2", 13), ("Heading 3", 11)]:
        style = doc.styles[name]; style.font.name = "Tahoma"; style.font.size = Pt(size); style.font.bold = True; style.font.color.rgb = RGBColor(0, 0, 0)
    header = sec.header.paragraphs[0]
    header.text = "Assignment 3 - MLP Training with Genetic Algorithms"
    header.runs[0].font.name = "Tahoma"; header.runs[0].font.size = Pt(8); header.runs[0].font.color.rgb = RGBColor.from_string(GRAY)
    footer = sec.footer.paragraphs[0]; footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT; footer.add_run("Computer Assignment 3"); footer.runs[0].font.size = Pt(8)

    for _ in range(5): doc.add_paragraph()
    p = doc.add_paragraph(style="Title"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run("รายงานการฝึก Multilayer Perceptron\nด้วย Genetic Algorithms")
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; r = p.add_run("การจำแนกข้อมูล Wisconsin Diagnostic Breast Cancer"); r.font.size = Pt(13); r.font.color.rgb = RGBColor.from_string(GRAY)
    for _ in range(5): doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run("Computer Assignment 3\nภาคเรียนที่ 1 ปีการศึกษา 2569").font.size = Pt(12)
    doc.add_page_break()

    heading(doc, "บทคัดย่อ")
    para(doc, "รายงานนี้นำเสนอการฝึก Multilayer Perceptron (MLP) ด้วย Genetic Algorithms โดยเขียนกลไกเครือข่ายประสาท การส่งค่าผ่านเครือข่าย การเข้ารหัสน้ำหนักเป็น chromosome การคัดเลือก การ crossover และการ mutation ด้วย Python มาตรฐาน โดยไม่ใช้ไลบรารี machine learning หรือไลบรารีสำหรับสร้างรูปภาพ ข้อมูลที่ใช้คือ WDBC ซึ่งมี 569 samples, 30 features และ 2 classes ระบบถูกประเมินด้วย stratified 10-fold cross-validation และเปรียบเทียบโครงสร้าง hidden layer และจำนวน nodes 4 รูปแบบ ผลการทดลองพบว่าโครงสร้าง 1 hidden layer 8 nodes ให้ accuracy เฉลี่ยสูงสุด 91.73% ตามด้วย 1 hidden layer 16 nodes ที่ 91.53% ขณะที่โครงสร้างสอง hidden layers ให้ผลต่ำกว่าในรอบการทดลองนี้")
    para(doc, "คำสำคัญ: Multilayer Perceptron, Genetic Algorithms, 10-fold Cross-validation, WDBC")
    heading(doc, "สารบัญ")
    for line in ["1 ลักษณะการทำงานของระบบ", "2 Simulation ผลการทดลอง และการวิเคราะห์", "3 โปรแกรม", "ภาคผนวก โปรแกรม mlp_ga.py"]:
        para(doc, line)
    doc.add_page_break()

    heading(doc, "1 ลักษณะการทำงานของระบบ")
    heading(doc, "1.1 ข้อมูลนำเข้าและการเตรียมข้อมูล", 2)
    para(doc, "ใช้ข้อมูล WDBC จากแหล่งข้อมูลที่โจทย์กำหนด: https://myweb.cmu.ac.th/sansanee.a/IntroCI/dataset/wdbc.data แต่ละแถวมี 32 ค่า ได้แก่ ID, diagnosis และ features จำนวน 30 ค่า ในการทดลองนี้ไม่นำ ID มาเป็น feature เพราะเป็นเพียงตัวระบุ sample ส่วน diagnosis ถูกแปลงเป็น label โดย B = 0 และ M = 1 ก่อนนำข้อมูลเข้าสู่เครือข่าย")
    para(doc, "เพื่อให้การคำนวณของ sigmoid มีเสถียรภาพ โปรแกรมใช้ min-max scaling แยกตาม feature โดย fit ค่า minimum และ maximum จาก training fold เท่านั้น แล้วนำค่าดังกล่าวไปแปลงทั้ง training และ test fold เพื่อป้องกันข้อมูลจาก test fold รั่วไหลเข้าสู่การฝึก")
    heading(doc, "1.2 โครงสร้าง MLP", 2)
    para(doc, "MLP ประกอบด้วย input layer จำนวน 30 nodes, hidden layer ตาม configuration ที่กำหนด และ output layer 1 node โดยใช้ sigmoid activation ทุก layer เอาต์พุตถูกแปลงเป็น class ด้วย threshold 0.5 การคำนวณ bias ถูกเก็บเป็นน้ำหนักตัวสุดท้ายของแต่ละ neuron")
    heading(doc, "1.3 Genetic Algorithms", 2)
    para(doc, "หนึ่ง chromosome แทนค่าน้ำหนักและ bias ทั้งหมดของ MLP การฝึกประกอบด้วยการสร้างประชากรแบบสุ่ม การคำนวณ fitness จาก accuracy หักด้วย 0.05 เท่าของ mean squared error การเก็บ elite การเลือก parent ด้วย tournament selection การทำ arithmetic crossover และ Gaussian mutation กระบวนการทำซ้ำ 20 generations โดยใช้ population 16 ตัวต่อ configuration และ fold")
    heading(doc, "1.4 การตรวจสอบ validity", 2)
    para(doc, "ใช้ stratified 10-fold cross-validation โดยแบ่งตัวอย่างของแต่ละ class กระจายไปยัง 10 folds ใกล้เคียงกัน ในแต่ละรอบใช้ 9 folds เป็น training set และ 1 fold เป็น test set จากนั้นรายงานค่า accuracy, sensitivity, specificity และ mean squared error ของ test fold")
    add_table(doc, [["รายการ", "ค่าที่ใช้"], ["จำนวน samples", "569"], ["จำนวน features", "30"], ["จำนวน classes", "2 (B และ M)"], ["Cross-validation", "Stratified 10-fold"], ["Population / generations", "16 / 20"], ["Mutation", "อัตรา 0.08, sigma 0.25"], ["การเลือก", "Tournament size 3 และ elitism"]], [5.5, 12.5])
    doc.add_page_break()

    heading(doc, "2 Simulation ผลการทดลอง และการวิเคราะห์")
    heading(doc, "2.1 Configurations ที่เปรียบเทียบ", 2)
    add_table(doc, [["Configuration", "Hidden layers", "Nodes"], ["8", "1", "8"], ["16", "1", "16"], ["8-8", "2", "8 + 8"], ["12-6", "2", "12 + 6"]], [4.5, 4.5, 4.5])
    para(doc, "การเปลี่ยน configuration ช่วยให้เห็นผลของจำนวน hidden layer และจำนวน nodes ต่อความสามารถในการเรียนรู้และความแปรผันของผลลัพธ์จาก Genetic Algorithms")
    heading(doc, "2.2 ผลการทดลองแบบ 10-fold cross-validation", 2)
    summary_rows = [["Configuration", "Accuracy mean", "SD", "Sensitivity", "Specificity", "MSE"]]
    for config in ["8", "16", "8-8", "12-6"]:
        row = summaries[config]
        summary_rows.append([config, f"{float(row[2])*100:.2f}%", f"{float(row[3])*100:.2f}%", f"{float(row[4])*100:.2f}%", f"{float(row[5])*100:.2f}%", f"{float(row[6]):.5f}"])
    add_table(doc, summary_rows, [2.8, 3.3, 2.5, 3.1, 3.1, 2.5], 8)
    para(doc, "ตารางที่ 1 ค่าเฉลี่ยผลการทดสอบจาก 10 folds")
    para(doc, "โครงสร้าง 8 nodes มี accuracy เฉลี่ยสูงสุด 91.73% และมีส่วนเบี่ยงเบนมาตรฐาน 4.24 percentage points แสดงว่าผลมีความสม่ำเสมอที่สุดในกลุ่มที่ทดลอง โครงสร้าง 16 nodes ให้ผลใกล้เคียงกันที่ 91.53% แต่ใช้เวลาประมวลผลเฉลี่ยต่อ fold สูงกว่า")
    heading(doc, "2.3 ผลราย fold และ confusion matrix", 2)
    detail_rows = [["Config", "Fold", "Accuracy", "Sensitivity", "Specificity", "TP", "TN", "FP", "FN"]]
    for row in rows:
        if row["fold"] in {"1", "2", "3"}:
            detail_rows.append([row["configuration"], row["fold"], f"{float(row['test_accuracy'])*100:.2f}%", f"{float(row['test_sensitivity'])*100:.2f}%", f"{float(row['test_specificity'])*100:.2f}%", row["tp"], row["tn"], row["fp"], row["fn"]])
    add_table(doc, detail_rows, [2.3, 1.5, 2.7, 3.0, 3.0, 1.5, 1.5, 1.5, 1.5], 7.3)
    para(doc, "ตารางที่ 2 ตัวอย่างผลราย fold ของแต่ละ configuration (fold 1-3)")
    heading(doc, "2.4 การวิเคราะห์", 2)
    para(doc, "ผลที่ได้แสดงว่าโครงสร้างที่ใหญ่ขึ้นไม่ได้รับประกัน accuracy ที่สูงขึ้น ในการทดลองนี้ 1 hidden layer ให้ผลดีกว่า 2 hidden layers โดย 8 nodes ให้ผลดีที่สุดเล็กน้อยเมื่อเทียบกับ 16 nodes สาเหตุหนึ่งอาจมาจากจำนวน generations และ population ที่จำกัด ทำให้โครงสร้างที่มีจำนวน weights มากต้องใช้การค้นหานานขึ้นจึงจะเข้าใกล้ optimum")
    para(doc, "เมื่อพิจารณา sensitivity โครงสร้าง 8 และ 16 nodes มีค่าใกล้เคียงกันประมาณ 87.2% ส่วนโครงสร้าง 8-8 มี sensitivity ต่ำสุด 80.7% จึงพลาด malignant samples มากกว่าในรอบการทดลองนี้ ขณะที่ specificity ของทุก configuration อยู่ใกล้ 94% ซึ่งหมายถึงการจำแนก benign ทำได้ค่อนข้างดี")
    para(doc, "ผลลัพธ์มีความแปรผันระหว่าง folds เพราะ GA เริ่มต้นประชากรแบบสุ่มและการแบ่งข้อมูลแต่ละ fold มีองค์ประกอบต่างกัน ดังนั้นควรรายงานค่าเฉลี่ยร่วมกับส่วนเบี่ยงเบนมาตรฐาน ไม่ควรสรุปจาก fold เดียว")
    doc.add_page_break()

    heading(doc, "3 โปรแกรม")
    para(doc, "โปรแกรมฉบับเต็มที่ใช้ในการทดลองแนบในภาคผนวกด้านล่าง โปรแกรมใช้เฉพาะ Python standard library และไม่มีการใช้ library สำหรับวาดรูปหรือโมเดล machine learning สำเร็จรูป ไฟล์ผลลัพธ์เชิงตารางจากการทดลองเก็บไว้ใน results.csv")
    heading(doc, "3.1 วิธีรันโปรแกรม", 2)
    para(doc, "วางไฟล์ wdbc.data ไว้ในโฟลเดอร์เดียวกับ mlp_ga.py แล้วรันคำสั่ง python mlp_ga.py โปรแกรมจะสร้าง results.csv ซึ่งประกอบด้วยผลราย fold และ summary ของแต่ละ configuration")
    heading(doc, "เอกสารอ้างอิง")
    para(doc, "[1] UCI Machine Learning Repository, Breast Cancer Wisconsin (Diagnostic) Data Set, wdbc.data. https://myweb.cmu.ac.th/sansanee.a/IntroCI/dataset/wdbc.data")
    para(doc, "[2] L. A. Zadeh, Fuzzy Sets, Information and Control, 1965. แนวคิดพื้นฐานของการรายงานผลระบบอัจฉริยะถูกใช้เป็นรูปแบบการจัดโครงสร้างรายงานจาก Assignment 2.")
    doc.add_page_break()
    heading(doc, "ภาคผนวก โปรแกรม mlp_ga.py")
    src = (ROOT / "mlp_ga.py").read_text(encoding="utf-8")
    p = doc.add_paragraph()
    for line in src.splitlines():
        r = p.add_run(line + "\n"); r.font.name = "Consolas"; r.font.size = Pt(6.5)
    doc.save(OUT)
    print(f"สร้าง Word แล้ว: {OUT}")


if __name__ == "__main__":
    build()
