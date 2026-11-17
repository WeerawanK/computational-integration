from pathlib import Path
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from fuzzy_controller import FuzzyBathController
from simulate import simulate_scenario

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "fuzzy_bath_report.docx"
BLUE = "173F67"
LIGHT = "EAF2F8"
GRAY = "666666"


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def set_cell_text(cell, text, bold=False, color="000000", size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(str(text))
    r.bold = bold
    r.font.name = "Tahoma"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def table(doc, rows, widths=None, size=9):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            set_cell_text(t.cell(i, j), value, bold=(i == 0), color="FFFFFF" if i == 0 else "000000", size=size)
            if i == 0:
                shade(t.cell(i, j), BLUE)
            elif i % 2 == 0:
                shade(t.cell(i, j), LIGHT)
            if widths:
                t.cell(i, j).width = Cm(widths[j])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def add_p(doc, text, style="Normal", bold_prefix=None):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix and text.startswith(bold_prefix):
        r = p.add_run(bold_prefix)
        r.bold = True
        p.add_run(text[len(bold_prefix):])
    else:
        p.add_run(text)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    return p


def add_figure(doc, filename, caption, width=15.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(ROOT / "outputs" / filename), width=Cm(width))
    cp = doc.add_paragraph(caption)
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.runs[0].italic = True
    cp.runs[0].font.size = Pt(9)
    cp.runs[0].font.color.rgb = RGBColor.from_string(GRAY)


def page_break(doc):
    doc.add_page_break()


def build():
    doc = Document()
    controller = FuzzyBathController()
    experiment_rows = [["กรณี", "เป้าหมาย", "อุณหภูมิสุดท้าย", "error", "วาล์วเริ่มต้น", "วาล์วสุดท้าย"]]
    for idx, (label, initial, target) in enumerate([("น้ำเย็น", 10, 32), ("น้ำเย็น", 10, 42), ("น้ำอุ่น", 33, 36)], 1):
        temps, valves = simulate_scenario(controller, initial, target)
        experiment_rows.append([
            f"กรณี {idx} ({label})",
            f"{target:.0f} องศาเซลเซียส",
            f"{temps[-1]:.3f} องศาเซลเซียส",
            f"{abs(target - temps[-1]):.3f}",
            f"{valves[0]:.3f}%",
            f"{valves[-1]:.3f}%",
        ])
    sec = doc.sections[0]
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(1.8)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.2)

    normal = doc.styles["Normal"]
    normal.font.name = "Tahoma"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.line_spacing = 1.15
    for style_name, size, color in [("Title", 22, "000000"), ("Heading 1", 17, "000000"), ("Heading 2", 13, "000000"), ("Heading 3", 11, "000000")]:
        s = doc.styles[style_name]
        s.font.name = "Tahoma"
        s.font.size = Pt(size)
        s.font.color.rgb = RGBColor.from_string(color)
        s.font.bold = True

    # Header and footer
    header = sec.header.paragraphs[0]
    header.text = "รายงานระบบควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic"
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header.runs[0].font.name = "Tahoma"
    header.runs[0].font.size = Pt(8)
    header.runs[0].font.color.rgb = RGBColor.from_string(GRAY)
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer.add_run("Computer Assignment 2")
    footer.runs[0].font.name = "Tahoma"
    footer.runs[0].font.size = Pt(8)

    # Cover
    for _ in range(5):
        doc.add_paragraph()
    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("รายงานการออกแบบและจำลองระบบ\nควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Mamdani Fuzzy Inference System")
    r.font.size = Pt(14); r.font.color.rgb = RGBColor.from_string(GRAY)
    for _ in range(5):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Computer Assignment 2\nภาคเรียนที่ 1 ปีการศึกษา 2569\n\nหัวข้อ: Fuzzy Bath Water Temperature Control").font.size = Pt(12)
    page_break(doc)

    add_heading(doc, "บทคัดย่อ", 1)
    add_p(doc, "รายงานฉบับนี้นำเสนอการออกแบบระบบควบคุมอุณหภูมิน้ำอาบโดยใช้ตรรกศาสตร์คลุมเครือแบบ Mamdani เพื่อคำนวณเปอร์เซ็นต์การเปิดวาล์วน้ำร้อนจากอุณหภูมิน้ำปัจจุบันและอุณหภูมิเป้าหมาย ระบบประกอบด้วยกระบวนการ fuzzification การประเมินกฎ การทำ implication การรวมผลลัพธ์ และการทำ centroid defuzzification จากนั้นนำระบบไปทดสอบด้วยแบบจำลองพลวัตของก๊อกผสมน้ำร้อนและน้ำเย็นแบบ first-order ผลการจำลองจำนวน 40 time steps ใน 3 สถานการณ์พบว่าสามารถปรับอุณหภูมิเข้าใกล้เป้าหมายได้ทุกกรณี โดยมี steady-state error อยู่ในช่วง 0.383-1.500 องศาเซลเซียส")
    add_p(doc, "คำสำคัญ: Fuzzy Logic, Mamdani Inference, Temperature Control, Bath Water")
    add_heading(doc, "สารบัญ", 1)
    for line in ["บทคัดย่อ ........................................................................ 2", "1 บทนำ ............................................................................. 3", "2 ทฤษฎีและงานที่เกี่ยวข้อง ............................................. 4", "3 การออกแบบระบบและวิธีดำเนินงาน .............................. 6", "4 ผลการทดลองและการวิเคราะห์ .................................... 10", "5 สรุปผล ข้อจำกัด และข้อเสนอแนะ ............................... 13", "เอกสารอ้างอิง .................................................................. 15", "ภาคผนวก ก รายการโปรแกรม ......................................... 16"]:
        p = doc.add_paragraph(line)
        p.paragraph_format.left_indent = Cm(0.5)
        p.paragraph_format.space_after = Pt(4)
    page_break(doc)

    add_heading(doc, "1 บทนำ", 1)
    add_heading(doc, "1.1 ที่มาและความสำคัญ", 2)
    add_p(doc, "การควบคุมอุณหภูมิน้ำอาบเป็นตัวอย่างของระบบควบคุมที่ผู้ใช้ต้องการความนุ่มนวลและตอบสนองได้ตามความรู้สึกจริง อุณหภูมิที่เหมาะสมไม่ได้ขึ้นกับค่าความแตกต่างเพียงค่าเดียว แต่เกี่ยวข้องกับอุณหภูมิปัจจุบัน ระดับความร้อนที่ต้องการ และสภาพแวดล้อมของระบบ การใช้ตรรกศาสตร์แบบจริงหรือ crisp logic มักกำหนดจุดตัดที่แข็ง ทำให้คำสั่งเปิดวาล์วเปลี่ยนฉับพลันเมื่ออุณหภูมิข้ามขอบเขต")
    add_p(doc, "Fuzzy Logic เหมาะกับปัญหานี้เพราะสามารถแทนคำอธิบายเชิงภาษาของผู้เชี่ยวชาญ เช่น น้ำเย็น น้ำอุ่น เป้าหมายสูง หรือเปิดวาล์วมาก ให้เป็นฟังก์ชันสมาชิกและกฎเชิงตรรกะ ระบบจึงให้เอาต์พุตที่ต่อเนื่องและตรวจสอบเหตุผลได้ง่าย")
    add_heading(doc, "1.2 วัตถุประสงค์", 2)
    add_p(doc, "1) ออกแบบตัวควบคุมอุณหภูมิน้ำอาบด้วย Mamdani Fuzzy Inference System\n2) สร้างฐานกฎที่สัมพันธ์ระหว่างอุณหภูมิปัจจุบัน อุณหภูมิเป้าหมาย และการเปิดวาล์วน้ำร้อน\n3) จำลองการทำงานแบบ closed-loop และประเมิน error จากสถานการณ์เริ่มต้นที่แตกต่างกัน\n4) วิเคราะห์ข้อดี ข้อจำกัด และแนวทางพัฒนาระบบสำหรับการใช้งานจริง")
    add_heading(doc, "1.3 ขอบเขตของงาน", 2)
    table(doc, [["ประเด็น", "ขอบเขต"], ["อินพุต", "อุณหภูมิปัจจุบัน 0-60 องศาเซลเซียส และอุณหภูมิเป้าหมาย 25-45 องศาเซลเซียส"], ["เอาต์พุต", "เปอร์เซ็นต์การเปิดวาล์วน้ำร้อน 0-100%"], ["วิธีอนุมาน", "Mamdani with min-max composition and centroid"], ["การทดสอบ", "3 สถานการณ์, 40 time steps ต่อสถานการณ์"], ["แบบจำลอง", "ก๊อกผสมน้ำแบบ first-order, k = 0.25"]], [3.5, 13.5])
    add_heading(doc, "1.4 ประโยชน์ที่คาดว่าจะได้รับ", 2)
    add_p(doc, "ได้ต้นแบบระบบควบคุมที่อธิบายได้ด้วยกฎภาษา สามารถตรวจสอบผลกระทบของฟังก์ชันสมาชิกและฐานกฎได้ และเป็นพื้นฐานสำหรับการต่อยอดไปยังระบบควบคุมจริงที่ใช้เซนเซอร์อุณหภูมิและวาล์วไฟฟ้า")
    page_break(doc)

    add_heading(doc, "2 ทฤษฎีและงานที่เกี่ยวข้อง", 1)
    add_heading(doc, "2.1 ตรรกศาสตร์คลุมเครือ", 2)
    add_p(doc, "ตรรกศาสตร์คลุมเครือเป็นวิธีแทนความไม่ชัดเจนของข้อมูลด้วยค่าความเป็นสมาชิกในช่วง 0 ถึง 1 แทนการตัดสินใจแบบเป็นสมาชิกหรือไม่เป็นสมาชิกเพียงสองค่า ฟังก์ชันสมาชิกจึงช่วยให้คำว่า เย็น หรือ อุ่น มีช่วงเปลี่ยนผ่านที่ต่อเนื่องและสะท้อนความรู้เชิงประสบการณ์ได้")
    add_heading(doc, "2.2 Mamdani Fuzzy Inference System", 2)
    add_p(doc, "ระบบ Mamdani ที่ใช้ในงานนี้ประกอบด้วย 5 ขั้นตอน ได้แก่ (1) fuzzification แปลงค่าอินพุตแบบ crisp เป็นค่าความเป็นสมาชิก (2) rule evaluation ประเมินเงื่อนไขของกฎ (3) implication ตัดระดับของผลลัพธ์ตามค่าความจริงของกฎ (4) aggregation รวมผลลัพธ์จากทุกกฎ และ (5) defuzzification แปลงพื้นที่ผลลัพธ์กลับเป็นคำสั่งตัวเลขด้วย centroid")
    add_p(doc, "ค่าคำสั่งวาล์วคำนวณจากจุดศูนย์กลางของพื้นที่ผลลัพธ์ตามสมการ u* = integral(u mu(u)) / integral(mu(u)) โดย u คือเปอร์เซ็นต์การเปิดวาล์วและ mu(u) คือฟังก์ชันสมาชิกผลลัพธ์หลังการรวมกฎ")
    add_heading(doc, "2.3 แบบจำลองอุณหภูมิ", 2)
    add_p(doc, "เพื่อประเมินพฤติกรรมแบบ closed-loop ใช้แบบจำลองอุณหภูมิผสมเป็นสองขั้นตอน ขั้นแรกคำนวณอุณหภูมิน้ำผสม T_mix = T_cold + (u/100)(T_hot - T_cold) จากนั้นจำลองการเปลี่ยนแปลงแบบ first-order ด้วย T(t+1) = T(t) + k(T_mix - T(t)) โดยกำหนด T_hot = 60 องศาเซลเซียส, T_cold = 15 องศาเซลเซียส และ k = 0.25")
    add_heading(doc, "2.4 เกณฑ์ประเมินผล", 2)
    add_p(doc, "ใช้ steady-state error เป็นตัวชี้วัดหลัก โดยคำนวณจากค่าสัมบูรณ์ของผลต่างระหว่างอุณหภูมิเป้าหมายกับอุณหภูมิสุดท้ายของการจำลอง นอกจากนี้พิจารณาทิศทางการตอบสนอง ความต่อเนื่องของคำสั่งวาล์ว และความสมเหตุสมผลของฐานกฎ")
    page_break(doc)

    add_heading(doc, "3 การออกแบบระบบและวิธีดำเนินงาน", 1)
    add_heading(doc, "3.1 โครงสร้างระบบ", 2)
    add_p(doc, "ระบบรับค่าอุณหภูมิปัจจุบันและอุณหภูมิเป้าหมายเข้าสู่ตัวควบคุม จากนั้นประเมินฟังก์ชันสมาชิกและฐานกฎเพื่อสร้างคำสั่งวาล์ว คำสั่งดังกล่าวถูกส่งเข้าแบบจำลองก๊อกผสมเพื่อคำนวณอุณหภูมิใน time step ถัดไป แล้ววนกลับมาเป็น feedback ให้ตัวควบคุม")
    table(doc, [["องค์ประกอบ", "รายละเอียดการออกแบบ"], ["Current temperature", "Cold, Cool, Warm, Hot"], ["Target temperature", "Low, Medium, High"], ["Hot-water valve", "VeryLow, Low, Medium, High, VeryHigh"], ["Inference", "Mamdani with min-max composition"], ["Defuzzification", "Centroid over output universe"]], [4.8, 12.2])
    add_heading(doc, "3.2 ฟังก์ชันสมาชิก", 2)
    add_p(doc, "อุณหภูมิปัจจุบันถูกแบ่งเป็น 4 กลุ่มเพื่อสะท้อนระดับความร้อนตั้งแต่น้ำเย็นจนถึงน้ำร้อน อุณหภูมิเป้าหมายแบ่งเป็น 3 กลุ่มตามระดับที่ผู้ใช้ต้องการ ส่วนเอาต์พุตแบ่งเป็น 5 ระดับเพื่อให้การเปิดวาล์วมีความละเอียดเพียงพอ ฟังก์ชันที่ใช้เป็น triangular และ trapezoidal membership functions ซึ่งมีการซ้อนทับกันเพื่อให้คำสั่งเปลี่ยนอย่างต่อเนื่อง")
    add_figure(doc, "1_membership_functions.png", "รูปที่ 1 ฟังก์ชันสมาชิกของอินพุตและเอาต์พุต", 14.5)
    add_heading(doc, "3.3 ฐานกฎ", 2)
    add_p(doc, "ฐานกฎทั้งหมดมี 12 ข้อ โดยกำหนดทิศทางให้สอดคล้องกับสามัญสำนึก: หากน้ำปัจจุบันเย็นหรือเป้าหมายสูง ให้เปิดวาล์วมากขึ้น และหากน้ำปัจจุบันร้อนหรือเป้าหมายต่ำ ให้ลดการเปิดวาล์ว")
    table(doc, [["ลำดับ", "อุณหภูมิปัจจุบัน", "เป้าหมาย", "วาล์วน้ำร้อน"], [1, "เย็น", "ต่ำ", "ต่ำ"], [2, "เย็น", "ปานกลาง", "สูง"], [3, "เย็น", "สูง", "สูงมาก"], [4, "ค่อนข้างเย็น", "ต่ำ", "ต่ำ"], [5, "ค่อนข้างเย็น", "ปานกลาง", "ปานกลาง"], [6, "ค่อนข้างเย็น", "สูง", "สูง"], [7, "อุ่น", "ต่ำ", "ต่ำมาก"], [8, "อุ่น", "ปานกลาง", "ปานกลาง"], [9, "อุ่น", "สูง", "สูง"], [10, "ร้อน", "ต่ำ", "ต่ำมาก"], [11, "ร้อน", "ปานกลาง", "ต่ำ"], [12, "ร้อน", "สูง", "ปานกลาง"]], [1.5, 5.3, 4.0, 4.5], 8)
    page_break(doc)

    add_heading(doc, "3.4 ขั้นตอนการทดลอง", 2)
    add_p(doc, "การทดลองดำเนินการตามลำดับดังนี้: กำหนดค่าเริ่มต้นและค่าเป้าหมาย, เรียกตัวควบคุมเพื่อคำนวณคำสั่งวาล์ว, ป้อนคำสั่งเข้าสู่แบบจำลองอุณหภูมิ, บันทึกอุณหภูมิและวาล์ว, ทำซ้ำ 40 time steps และสรุปค่าอุณหภูมิสุดท้ายกับ error")
    table(doc, [["สถานการณ์", "ค่าเริ่มต้น", "เป้าหมาย", "ระดับเป้าหมาย"], ["กรณีที่ 1", "10 องศาเซลเซียส", "32 องศาเซลเซียส", "ปานกลาง"], ["กรณีที่ 2", "10 องศาเซลเซียส", "42 องศาเซลเซียส", "สูง"], ["กรณีที่ 3", "33 องศาเซลเซียส", "36 องศาเซลเซียส", "ปานกลาง"]], [3.2, 4.3, 4.3, 3.2])
    add_heading(doc, "3.5 การตรวจสอบความถูกต้องของโปรแกรม", 2)
    add_p(doc, "ตรวจสอบผลการทำงานด้วยกราฟฟังก์ชันสมาชิก กราฟ control surface และกราฟการตอบสนองตามเวลา เพื่อยืนยันว่าอินพุตที่อยู่ในช่วงกำหนดสามารถถูกประมวลผลได้ การตรวจสอบเชิงตรรกะเพิ่มเติมคือเปรียบเทียบแนวโน้มของคำสั่งวาล์วกับกฎ เช่น เมื่ออุณหภูมิปัจจุบันต่ำกว่าค่าเป้าหมายมาก คำสั่งวาล์วควรสูงกว่าเมื่อเข้าใกล้เป้าหมาย")
    add_heading(doc, "3.6 เครื่องมือที่ใช้", 2)
    add_p(doc, "พัฒนาโปรแกรมด้วยภาษา Python และใช้ไลบรารีสำหรับคำนวณเชิงตัวเลขและสร้างกราฟ โครงสร้างโปรแกรมแยกเป็น membership.py สำหรับฟังก์ชันสมาชิก, fuzzy_controller.py สำหรับตัวควบคุม, simulate.py สำหรับแบบจำลอง และ build_pdf.py สำหรับจัดทำรายงาน")
    page_break(doc)

    add_heading(doc, "4 ผลการทดลองและการวิเคราะห์", 1)
    add_heading(doc, "4.1 Control surface", 2)
    add_p(doc, "กราฟพื้นผิวควบคุมแสดงความสัมพันธ์ระหว่างอุณหภูมิปัจจุบัน อุณหภูมิเป้าหมาย และเปอร์เซ็นต์การเปิดวาล์ว พื้นผิวมีแนวโน้มสอดคล้องกับหลักการควบคุม: เมื่ออุณหภูมิปัจจุบันต่ำหรือเป้าหมายสูง คำสั่งวาล์วจะเพิ่มขึ้น ขณะที่เมื่ออุณหภูมิปัจจุบันสูงกว่าค่าเป้าหมาย คำสั่งวาล์วจะลดลง")
    add_figure(doc, "2_control_surface.png", "รูปที่ 2 พื้นผิวควบคุมของระบบ Mamdani", 15.0)
    add_heading(doc, "4.2 ผลการจำลองแบบ closed-loop", 2)
    add_p(doc, "ผลลัพธ์จากการจำลองทั้งสามกรณีแสดงในตารางที่ 2 อุณหภูมิเริ่มต้นที่ต่ำกว่าค่าเป้าหมายทำให้วาล์วเปิดมากในช่วงแรก และลดลงเมื่ออุณหภูมิเข้าใกล้เป้าหมาย การลดคำสั่งอย่างต่อเนื่องช่วยลดโอกาสการแกว่งของระบบ")
    table(doc, experiment_rows, [3.4, 2.7, 3.3, 1.7, 2.7, 2.7], 8)
    add_figure(doc, "3_time_simulation.png", "รูปที่ 3 การเปลี่ยนแปลงอุณหภูมิและเปอร์เซ็นต์วาล์วตามเวลา", 14.5)
    page_break(doc)

    add_heading(doc, "4.3 การวิเคราะห์รายกรณี", 2)
    add_p(doc, "กรณีที่ 1: เริ่มต้นที่ 10 องศาเซลเซียสและมีเป้าหมาย 32 องศาเซลเซียส ระบบเริ่มด้วยการเปิดวาล์วในระดับสูงเพื่อเพิ่มอุณหภูมิ จากนั้นลดการเปิดวาล์วเมื่อเข้าใกล้เป้าหมาย ผลลัพธ์สุดท้ายมี error ประมาณ 0.823 องศาเซลเซียส แสดงว่าระบบสามารถรักษาทิศทางการควบคุมได้ แต่ยังมี error คงค้างจากการแบ่งระดับเอาต์พุตเป็นกลุ่มภาษา")
    add_p(doc, "กรณีที่ 2: เริ่มต้นที่ 10 องศาเซลเซียสและมีเป้าหมาย 42 องศาเซลเซียส เป็นกรณีที่ต้องการความร้อนมากที่สุด ระบบจึงใช้กฎ Cold-High ให้เปิดวาล์วสูงในช่วงต้น ผลลัพธ์มี error ประมาณ 0.383 องศาเซลเซียส ซึ่งต่ำที่สุดในสามกรณี")
    add_p(doc, "กรณีที่ 3: เริ่มต้นที่ 33 องศาเซลเซียสและมีเป้าหมาย 36 องศาเซลเซียส ความแตกต่างระหว่างค่าเริ่มต้นกับเป้าหมายมีไม่มาก แต่ระบบต้องควบคุมอย่างละเอียด ผลลัพธ์มี error ประมาณ 1.500 องศาเซลเซียส ซึ่งสูงที่สุด เนื่องจากไม่มีอินพุต error โดยตรงและมีการแบ่งระดับของฟังก์ชันสมาชิกแบบหยาบในบริเวณใกล้เป้าหมาย")
    add_heading(doc, "4.4 การอภิปรายผล", 2)
    add_p(doc, "ผลการทดลองยืนยันว่าการเลือกฐานกฎและการซ้อนทับของฟังก์ชันสมาชิกมีผลโดยตรงต่อความราบรื่นของคำสั่งวาล์ว จุดแข็งของระบบคือความโปร่งใสของเหตุผลและการตอบสนองที่ไม่เปลี่ยนฉับพลัน อย่างไรก็ตาม ค่า error ที่ยังเหลืออยู่สะท้อนว่าการใช้เพียงอุณหภูมิปัจจุบันและเป้าหมายอาจไม่เพียงพอสำหรับการควบคุมที่ละเอียดมาก โดยเฉพาะช่วงที่ค่าอุณหภูมิใกล้กัน")
    page_break(doc)

    add_heading(doc, "5 สรุปผล ข้อจำกัด และข้อเสนอแนะ", 1)
    add_heading(doc, "5.1 สรุปผล", 2)
    add_p(doc, "งานนี้ออกแบบตัวควบคุมอุณหภูมิน้ำอาบแบบ Mamdani Fuzzy Inference System โดยใช้ข้อมูลอุณหภูมิปัจจุบันและอุณหภูมิเป้าหมายเป็นอินพุต และใช้เปอร์เซ็นต์การเปิดวาล์วน้ำร้อนเป็นเอาต์พุต ระบบมีฐานกฎ 12 ข้อและใช้ centroid defuzzification ผลการจำลองแบบ closed-loop ทั้ง 3 สถานการณ์พบว่าระบบสามารถปรับอุณหภูมิไปในทิศทางที่ถูกต้องและเข้าใกล้เป้าหมายได้ทุกกรณี โดย error สูงสุด 1.500 องศาเซลเซียส")
    add_heading(doc, "5.2 ข้อจำกัดของงาน", 2)
    add_p(doc, "ข้อจำกัดสำคัญคือแบบจำลองยังเป็นแบบ first-order และกำหนดค่าคงที่ของน้ำร้อน น้ำเย็น และอัตราการตอบสนองไว้ล่วงหน้า จึงยังไม่สะท้อนอัตราการไหลจริง ความล่าช้าของวาล์ว การสูญเสียความร้อน อุณหภูมิแวดล้อม และ noise จากเซนเซอร์ นอกจากนี้ ระบบไม่มีอินพุต error หรืออัตราการเปลี่ยนแปลงของ error ทำให้การควบคุมบริเวณใกล้เป้าหมายยังไม่ละเอียดมาก")
    add_heading(doc, "5.3 ข้อเสนอแนะในการพัฒนา", 2)
    add_p(doc, "1) เพิ่ม error และ change-in-error เป็นอินพุตเพื่อให้ระบบรู้ทิศทางการเคลื่อนที่ของอุณหภูมิ\n2) ปรับจุดของฟังก์ชันสมาชิกด้วยข้อมูลจากการทดลองจริงและทำ calibration เซนเซอร์\n3) เพิ่มแบบจำลองอัตราการไหล ความหน่วง และการสูญเสียความร้อน\n4) ทดสอบความทนทานต่อ noise และความเปลี่ยนแปลงของแรงดันน้ำ\n5) กำหนด safety limit เพื่อป้องกันอุณหภูมิสูงเกินไปก่อนสั่งเปิดวาล์วจริง")
    add_heading(doc, "5.4 ข้อสรุปเชิงวิศวกรรม", 2)
    add_p(doc, "ระบบที่พัฒนาขึ้นเหมาะสำหรับเป็นต้นแบบเพื่อสาธิตการประยุกต์ใช้ approximate reasoning กับงานควบคุมอุณหภูมิ จุดเด่นคือโครงสร้างเข้าใจง่าย ตรวจสอบได้ และสามารถปรับฐานกฎได้โดยไม่ต้องสร้างแบบจำลองทางคณิตศาสตร์ที่ซับซ้อนทั้งหมด หากต่อยอดด้วยข้อมูลจากระบบจริงและเพิ่มกลไกความปลอดภัย จะสามารถพัฒนาเป็นต้นแบบระบบควบคุมอุณหภูมิสำหรับอุปกรณ์จริงได้")
    page_break(doc)

    add_heading(doc, "เอกสารอ้างอิง", 1)
    for ref in ["[1] L. A. Zadeh, Fuzzy Sets, Information and Control, vol. 8, no. 3, pp. 338-353, 1965.", "[2] E. H. Mamdani and S. Assilian, An Experiment in Linguistic Synthesis with a Fuzzy Logic Controller, International Journal of Man-Machine Studies, vol. 7, no. 1, pp. 1-13, 1975.", "[3] J. Yen and R. Langari, Fuzzy Logic: Intelligence, Control, and Information. Prentice Hall, 1999.", "[4] Python Software Foundation, Python 3 Documentation, 2026."]:
        add_p(doc, ref)
    page_break(doc)

    add_heading(doc, "ภาคผนวก ก รายการโปรแกรม", 1)
    add_p(doc, "ภาคผนวกนี้แสดงซอร์สโค้ดหลักที่ใช้ในการสร้างฟังก์ชันสมาชิก ตัวควบคุม และการจำลอง เพื่อให้สามารถตรวจสอบและทำซ้ำผลการทดลองได้")
    for filename in ["membership.py", "fuzzy_controller.py", "simulate.py"]:
        add_heading(doc, filename, 2)
        src = (ROOT / filename).read_text(encoding="utf-8")
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.3)
        p.paragraph_format.space_after = Pt(6)
        for line in src.splitlines():
            r = p.add_run(line + "\n")
            r.font.name = "Consolas"
            r.font.size = Pt(7)
        page_break(doc)

    doc.save(OUT)
    print(f"สร้างไฟล์ Word แล้ว: {OUT}")


if __name__ == "__main__":
    build()
