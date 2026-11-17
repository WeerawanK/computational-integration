"""Build a formal Thai academic report for the fuzzy bath controller."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    Image, Table, TableStyle, KeepTogether, Preformatted,
)

from fuzzy_controller import FuzzyBathController
from simulate import simulate_scenario


ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "fuzzy_bath_report.pdf"
FONT_PATH = Path(r"C:\Windows\Fonts\tahoma.ttf")
pdfmetrics.registerFont(TTFont("Thai", str(FONT_PATH)))

BLUE = colors.HexColor("#173F67")
LIGHT_BLUE = colors.HexColor("#EAF2F8")
MID_BLUE = colors.HexColor("#B9D5EA")
GRAY = colors.HexColor("#666666")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", fontName="Thai", fontSize=22, leading=31,
                          alignment=TA_CENTER, textColor=BLUE, spaceAfter=14))
styles.add(ParagraphStyle(name="CoverSub", fontName="Thai", fontSize=14, leading=20,
                          alignment=TA_CENTER, textColor=GRAY))
styles.add(ParagraphStyle(name="BodyThai", fontName="Thai", fontSize=10.5, leading=17,
                          alignment=TA_JUSTIFY, spaceAfter=8))
styles.add(ParagraphStyle(name="BodySmall", fontName="Thai", fontSize=9, leading=13,
                          alignment=TA_JUSTIFY, spaceAfter=5))
styles.add(ParagraphStyle(name="H1Thai", fontName="Thai", fontSize=17, leading=23,
                          textColor=BLUE, spaceBefore=8, spaceAfter=12))
styles.add(ParagraphStyle(name="H2Thai", fontName="Thai", fontSize=13, leading=19,
                          textColor=BLUE, spaceBefore=9, spaceAfter=7))
styles.add(ParagraphStyle(name="H3Thai", fontName="Thai", fontSize=11, leading=16,
                          textColor=BLUE, spaceBefore=7, spaceAfter=5))
styles.add(ParagraphStyle(name="CaptionThai", fontName="Thai", fontSize=8.5, leading=12,
                          alignment=TA_CENTER, textColor=GRAY, spaceAfter=8))
styles.add(ParagraphStyle(name="TOC", fontName="Thai", fontSize=10, leading=18,
                          leftIndent=8, rightIndent=8))
styles.add(ParagraphStyle(name="CodeThai", fontName="Thai", fontSize=6.6, leading=8.2,
                          leftIndent=5, rightIndent=5))


def P(text, style="BodyThai"):
    return Paragraph(text, styles[style])


def make_table(rows, widths, font_size=8.3):
    cell_style = ParagraphStyle("Cell", parent=styles["BodySmall"], fontName="Thai",
                                fontSize=font_size, leading=font_size + 3,
                                alignment=TA_CENTER, spaceAfter=0)
    data = [[Paragraph(str(c), cell_style) for c in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#7A8A99")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BLUE]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def figure(filename, caption, width=155 * mm, height=None):
    path = ROOT / "outputs" / filename
    img = Image(str(path), width=width, height=height) if height else Image(str(path), width=width)
    return [Spacer(1, 3 * mm), img, P(caption, "CaptionThai")]


def header_footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(MID_BLUE)
        canvas.line(14 * mm, 287 * mm, 196 * mm, 287 * mm)
        canvas.setFont("Thai", 8)
        canvas.setFillColor(GRAY)
        canvas.drawString(14 * mm, 291 * mm, "รายงานระบบควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic")
        canvas.drawRightString(196 * mm, 9 * mm, f"หน้า {doc.page}")
    canvas.restoreState()


def build():
    controller = FuzzyBathController()
    labels = {"Cold": "เย็น", "Cool": "ค่อนข้างเย็น", "Warm": "อุ่น", "Hot": "ร้อน",
              "Low": "ต่ำ", "Medium": "ปานกลาง", "High": "สูง",
              "VeryLow": "ต่ำมาก", "VeryHigh": "สูงมาก"}

    doc = BaseDocTemplate(str(PDF_PATH), pagesize=A4, rightMargin=14 * mm, leftMargin=14 * mm,
                          topMargin=18 * mm, bottomMargin=15 * mm,
                          title="รายงานการออกแบบและจำลองระบบควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic",
                          author="TANPIHCHA PAIBOON")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=header_footer)])
    story = []

    # Cover
    story += [Spacer(1, 43 * mm), P("รายงานการออกแบบและจำลองระบบ", "CoverTitle"),
              P("ควบคุมอุณหภูมิน้ำอาบด้วย Fuzzy Logic", "CoverTitle"),
              Spacer(1, 6 * mm), P("Mamdani Fuzzy Inference System", "CoverSub"),
              Spacer(1, 42 * mm), P("Computer Assignment 2<br/>ภาคเรียนที่ 1 ปีการศึกษา 2569", "CoverSub"),
              Spacer(1, 14 * mm), P("หัวข้อ: Fuzzy Bath Water Temperature Control", "CoverSub"),
              PageBreak()]

    # Front matter
    story += [P("บทคัดย่อ", "H1Thai"),
              P("รายงานฉบับนี้นำเสนอการออกแบบระบบควบคุมอุณหภูมิน้ำอาบโดยใช้ตรรกศาสตร์คลุมเครือแบบ Mamdani เพื่อคำนวณเปอร์เซ็นต์การเปิดวาล์วน้ำร้อนจากอุณหภูมิน้ำปัจจุบันและอุณหภูมิเป้าหมาย ระบบประกอบด้วยกระบวนการ fuzzification การประเมินกฎ การทำ implication การรวมผลลัพธ์ และการทำ centroid defuzzification จากนั้นนำระบบไปทดสอบด้วยแบบจำลองพลวัตของก๊อกผสมน้ำร้อนและน้ำเย็นแบบ first-order ผลการจำลองจำนวน 40 time steps ใน 3 สถานการณ์พบว่าสามารถปรับอุณหภูมิเข้าใกล้เป้าหมายได้ทุกกรณี โดยมี steady-state error อยู่ในช่วง 0.383-1.500 องศาเซลเซียส จุดเด่นของระบบคือความสามารถในการอธิบายการตัดสินใจด้วยกฎภาษาและการเปลี่ยนคำสั่งควบคุมอย่างต่อเนื่อง อย่างไรก็ตาม การนำไปใช้งานจริงควรเพิ่มแบบจำลองอัตราการไหล การสูญเสียความร้อน และสัญญาณรบกวนของเซนเซอร์", "BodyThai"),
              P("คำสำคัญ: Fuzzy Logic, Mamdani Inference, Temperature Control, Bath Water", "BodySmall"),
              Spacer(1, 5 * mm), P("สารบัญ", "H1Thai"),
              P("บทคัดย่อ ........................................................................................................ 2", "TOC"),
              P("1 บทนำ ............................................................................................................. 4", "TOC"),
              P("2 ทฤษฎีและงานที่เกี่ยวข้อง ............................................................................... 5", "TOC"),
              P("3 การออกแบบระบบและวิธีดำเนินงาน .............................................................. 7", "TOC"),
              P("4 ผลการทดลองและการวิเคราะห์ .................................................................... 11", "TOC"),
              P("5 สรุปผล ข้อจำกัด และข้อเสนอแนะ ............................................................... 15", "TOC"),
              P("เอกสารอ้างอิง .................................................................................................. 17", "TOC"),
              P("ภาคผนวก ก รายการโปรแกรม ......................................................................... 18", "TOC"),
              PageBreak()]

    # Chapter 1
    story += [P("1 บทนำ", "H1Thai"),
              P("1.1 ที่มาและความสำคัญ", "H2Thai"),
              P("การควบคุมอุณหภูมิน้ำอาบเป็นตัวอย่างของระบบควบคุมที่ผู้ใช้ต้องการความนุ่มนวลและตอบสนองได้ตามความรู้สึกจริง อุณหภูมิที่เหมาะสมไม่ได้ขึ้นกับค่าความแตกต่างเพียงค่าเดียว แต่เกี่ยวข้องกับอุณหภูมิปัจจุบัน ระดับความร้อนที่ต้องการ และสภาพแวดล้อมของระบบ การใช้ตรรกศาสตร์แบบจริงหรือ crisp logic มักกำหนดจุดตัดที่แข็ง ทำให้คำสั่งเปิดวาล์วเปลี่ยนฉับพลันเมื่ออุณหภูมิข้ามขอบเขต", "BodyThai"),
              P("Fuzzy Logic เหมาะกับปัญหานี้เพราะสามารถแทนคำอธิบายเชิงภาษาของผู้เชี่ยวชาญ เช่น น้ำเย็น น้ำอุ่น เป้าหมายสูง หรือเปิดวาล์วมาก ให้เป็นฟังก์ชันสมาชิกและกฎเชิงตรรกะ ระบบจึงให้เอาต์พุตที่ต่อเนื่องและตรวจสอบเหตุผลได้ง่าย", "BodyThai"),
              P("1.2 วัตถุประสงค์", "H2Thai"),
              P("1) ออกแบบตัวควบคุมอุณหภูมิน้ำอาบด้วย Mamdani Fuzzy Inference System<br/>2) สร้างฐานกฎที่สัมพันธ์ระหว่างอุณหภูมิปัจจุบัน อุณหภูมิเป้าหมาย และการเปิดวาล์วน้ำร้อน<br/>3) จำลองการทำงานแบบ closed-loop และประเมิน error จากสถานการณ์เริ่มต้นที่แตกต่างกัน<br/>4) วิเคราะห์ข้อดี ข้อจำกัด และแนวทางพัฒนาระบบสำหรับการใช้งานจริง", "BodyThai"),
              P("1.3 ขอบเขตของงาน", "H2Thai"),
              make_table([["ประเด็น", "ขอบเขต"], ["อินพุต", "อุณหภูมิปัจจุบัน 0-60 องศาเซลเซียส และอุณหภูมิเป้าหมาย 25-45 องศาเซลเซียส"], ["เอาต์พุต", "เปอร์เซ็นต์การเปิดวาล์วน้ำร้อน 0-100%"], ["วิธีอนุมาน", "Mamdani, AND = min, aggregation = max, centroid"], ["การทดสอบ", "3 สถานการณ์, 40 time steps ต่อสถานการณ์"], ["แบบจำลอง", "ก๊อกผสมน้ำแบบ first-order, k = 0.25"]], [35 * mm, 135 * mm]),
              P("1.4 ประโยชน์ที่คาดว่าจะได้รับ", "H2Thai"),
              P("ได้ต้นแบบระบบควบคุมที่อธิบายได้ด้วยกฎภาษา สามารถตรวจสอบผลกระทบของฟังก์ชันสมาชิกและฐานกฎได้ และเป็นพื้นฐานสำหรับการต่อยอดไปยังระบบควบคุมจริงที่ใช้เซนเซอร์อุณหภูมิและวาล์วไฟฟ้า", "BodyThai"), PageBreak()]

    # Chapter 2
    story += [P("2 ทฤษฎีและงานที่เกี่ยวข้อง", "H1Thai"),
              P("2.1 ตรรกศาสตร์คลุมเครือ", "H2Thai"),
              P("ตรรกศาสตร์คลุมเครือเป็นวิธีแทนความไม่ชัดเจนของข้อมูลด้วยค่าความเป็นสมาชิกในช่วง 0 ถึง 1 แทนการตัดสินใจแบบเป็นสมาชิกหรือไม่เป็นสมาชิกเพียงสองค่า ฟังก์ชันสมาชิกจึงช่วยให้คำว่า เย็น หรือ อุ่น มีช่วงเปลี่ยนผ่านที่ต่อเนื่องและสะท้อนความรู้เชิงประสบการณ์ได้", "BodyThai"),
              P("2.2 Mamdani Fuzzy Inference System", "H2Thai"),
              P("ระบบ Mamdani ที่ใช้ในงานนี้ประกอบด้วย 5 ขั้นตอน ได้แก่ (1) fuzzification แปลงค่าอินพุตแบบ crisp เป็นค่าความเป็นสมาชิก (2) rule evaluation ประเมินเงื่อนไขของกฎ (3) implication ตัดระดับของผลลัพธ์ตามค่าความจริงของกฎ (4) aggregation รวมผลลัพธ์จากทุกกฎ และ (5) defuzzification แปลงพื้นที่ผลลัพธ์กลับเป็นคำสั่งตัวเลขด้วย centroid", "BodyThai"),
              P("ค่าคำสั่งวาล์วคำนวณจากจุดศูนย์กลางของพื้นที่ผลลัพธ์ตามสมการ u* = integral(u mu(u)) / integral(mu(u)) โดย u คือเปอร์เซ็นต์การเปิดวาล์วและ mu(u) คือฟังก์ชันสมาชิกผลลัพธ์หลังการรวมกฎ", "BodyThai"),
              P("2.3 แบบจำลองอุณหภูมิ", "H2Thai"),
              P("เพื่อประเมินพฤติกรรมแบบ closed-loop ใช้แบบจำลองอุณหภูมิผสมเป็นสองขั้นตอน ขั้นแรกคำนวณอุณหภูมิน้ำผสม T_mix = T_cold + (u/100)(T_hot - T_cold) จากนั้นจำลองการเปลี่ยนแปลงแบบ first-order ด้วย T(t+1) = T(t) + k(T_mix - T(t)) โดยกำหนด T_hot = 60 องศาเซลเซียส, T_cold = 15 องศาเซลเซียส และ k = 0.25", "BodyThai"),
              P("2.4 เกณฑ์ประเมินผล", "H2Thai"),
              P("ใช้ steady-state error เป็นตัวชี้วัดหลัก โดยคำนวณจากค่าสัมบูรณ์ของผลต่างระหว่างอุณหภูมิเป้าหมายกับอุณหภูมิสุดท้ายของการจำลอง นอกจากนี้พิจารณาทิศทางการตอบสนอง ความต่อเนื่องของคำสั่งวาล์ว และความสมเหตุสมผลของฐานกฎ", "BodyThai"),
              PageBreak()]

    # Chapter 3
    story += [P("3 การออกแบบระบบและวิธีดำเนินงาน", "H1Thai"),
              P("3.1 โครงสร้างระบบ", "H2Thai"),
              P("ระบบรับค่าอุณหภูมิปัจจุบันและอุณหภูมิเป้าหมายเข้าสู่ตัวควบคุม จากนั้นประเมินฟังก์ชันสมาชิกและฐานกฎเพื่อสร้างคำสั่งวาล์ว คำสั่งดังกล่าวถูกส่งเข้าแบบจำลองก๊อกผสมเพื่อคำนวณอุณหภูมิใน time step ถัดไป แล้ววนกลับมาเป็น feedback ให้ตัวควบคุม", "BodyThai"),
              make_table([["องค์ประกอบ", "รายละเอียดการออกแบบ"], ["Current temperature", "Cold, Cool, Warm, Hot"], ["Target temperature", "Low, Medium, High"], ["Hot-water valve", "VeryLow, Low, Medium, High, VeryHigh"], ["Inference", "Mamdani with min-max composition"], ["Defuzzification", "Centroid over output universe"]], [48 * mm, 122 * mm]),
              P("3.2 ฟังก์ชันสมาชิก", "H2Thai"),
              P("อุณหภูมิปัจจุบันถูกแบ่งเป็น 4 กลุ่มเพื่อสะท้อนระดับความร้อนตั้งแต่น้ำเย็นจนถึงน้ำร้อน อุณหภูมิเป้าหมายแบ่งเป็น 3 กลุ่มตามระดับที่ผู้ใช้ต้องการ ส่วนเอาต์พุตแบ่งเป็น 5 ระดับเพื่อให้การเปิดวาล์วมีความละเอียดเพียงพอ ฟังก์ชันที่ใช้เป็น triangular และ trapezoidal membership functions ซึ่งมีการซ้อนทับกันเพื่อให้คำสั่งเปลี่ยนอย่างต่อเนื่อง", "BodyThai"),
              *figure("1_membership_functions.png", "รูปที่ 1 ฟังก์ชันสมาชิกของอินพุตและเอาต์พุต", 150 * mm, 145 * mm),
              P("3.3 ฐานกฎ", "H2Thai"),
              P("ฐานกฎทั้งหมดมี 12 ข้อ โดยกำหนดทิศทางให้สอดคล้องกับสามัญสำนึก: หากน้ำปัจจุบันเย็นหรือเป้าหมายสูง ให้เปิดวาล์วมากขึ้น และหากน้ำปัจจุบันร้อนหรือเป้าหมายต่ำ ให้ลดการเปิดวาล์ว", "BodyThai")]
    rule_rows = [["ลำดับ", "อุณหภูมิปัจจุบัน", "เป้าหมาย", "วาล์วน้ำร้อน"]]
    for i, (a, b, c) in enumerate(controller.rules, 1):
        rule_rows.append([i, labels[a], labels[b], labels[c]])
    story += [make_table(rule_rows, [18 * mm, 50 * mm, 38 * mm, 44 * mm]),
              P("ตัวอย่างกฎ: ถ้าอุณหภูมิปัจจุบันอยู่ในกลุ่ม Cold และอุณหภูมิเป้าหมายอยู่ในกลุ่ม High ให้ผลลัพธ์เป็น VeryHigh เพื่อเร่งการเพิ่มอุณหภูมิ ในทางกลับกัน ถ้าปัจจุบันอยู่ในกลุ่ม Hot และเป้าหมายอยู่ในกลุ่ม Low ให้ผลลัพธ์เป็น VeryLow", "BodyThai"), PageBreak()]

    # Chapter 3 continued / method
    story += [P("3.4 ขั้นตอนการทดลอง", "H2Thai"),
              P("การทดลองดำเนินการตามลำดับดังนี้: กำหนดค่าเริ่มต้นและค่าเป้าหมาย, เรียกตัวควบคุมเพื่อคำนวณคำสั่งวาล์ว, ป้อนคำสั่งเข้าสู่แบบจำลองอุณหภูมิ, บันทึกอุณหภูมิและวาล์ว, ทำซ้ำ 40 time steps และสรุปค่าอุณหภูมิสุดท้ายกับ error", "BodyThai"),
              make_table([["สถานการณ์", "ค่าเริ่มต้น", "เป้าหมาย", "ระดับเป้าหมาย"], ["กรณีที่ 1", "10 องศาเซลเซียส", "32 องศาเซลเซียส", "ปานกลาง"], ["กรณีที่ 2", "10 องศาเซลเซียส", "42 องศาเซลเซียส", "สูง"], ["กรณีที่ 3", "33 องศาเซลเซียส", "36 องศาเซลเซียส", "ปานกลาง"]], [32 * mm, 43 * mm, 43 * mm, 32 * mm]),
              P("3.5 การตรวจสอบความถูกต้องของโปรแกรม", "H2Thai"),
              P("ตรวจสอบผลการทำงานด้วยกราฟฟังก์ชันสมาชิก กราฟ control surface และกราฟการตอบสนองตามเวลา เพื่อยืนยันว่าอินพุตที่อยู่ในช่วงกำหนดสามารถถูกประมวลผลได้ การตรวจสอบเชิงตรรกะเพิ่มเติมคือเปรียบเทียบแนวโน้มของคำสั่งวาล์วกับกฎ เช่น เมื่ออุณหภูมิปัจจุบันต่ำกว่าค่าเป้าหมายมาก คำสั่งวาล์วควรสูงกว่าเมื่อเข้าใกล้เป้าหมาย", "BodyThai"),
              P("3.6 เครื่องมือที่ใช้", "H2Thai"),
              P("พัฒนาโปรแกรมด้วยภาษา Python และใช้ไลบรารีสำหรับคำนวณเชิงตัวเลขและสร้างกราฟ โครงสร้างโปรแกรมแยกเป็น membership.py สำหรับฟังก์ชันสมาชิก, fuzzy_controller.py สำหรับตัวควบคุม, simulate.py สำหรับแบบจำลอง และ build_pdf.py สำหรับจัดทำรายงาน", "BodyThai"),
              PageBreak()]

    # Chapter 4
    story += [P("4 ผลการทดลองและการวิเคราะห์", "H1Thai"),
              P("4.1 Control surface", "H2Thai"),
              P("กราฟพื้นผิวควบคุมแสดงความสัมพันธ์ระหว่างอุณหภูมิปัจจุบัน อุณหภูมิเป้าหมาย และเปอร์เซ็นต์การเปิดวาล์ว พื้นผิวมีแนวโน้มสอดคล้องกับหลักการควบคุม: เมื่ออุณหภูมิปัจจุบันต่ำหรือเป้าหมายสูง คำสั่งวาล์วจะเพิ่มขึ้น ขณะที่เมื่ออุณหภูมิปัจจุบันสูงกว่าค่าเป้าหมาย คำสั่งวาล์วจะลดลง", "BodyThai"),
              *figure("2_control_surface.png", "รูปที่ 2 พื้นผิวควบคุมของระบบ Mamdani", 155 * mm, 110 * mm),
              P("4.2 ผลการจำลองแบบ closed-loop", "H2Thai"),
              P("ผลลัพธ์จากการจำลองทั้งสามกรณีแสดงในตารางที่ 2 อุณหภูมิเริ่มต้นที่ต่ำกว่าค่าเป้าหมายทำให้วาล์วเปิดมากในช่วงแรก และลดลงเมื่ออุณหภูมิเข้าใกล้เป้าหมาย การลดคำสั่งอย่างต่อเนื่องช่วยลดโอกาสการแกว่งของระบบ", "BodyThai")]
    result_rows = [["กรณี", "เป้าหมาย", "อุณหภูมิสุดท้าย", "error", "วาล์วเริ่มต้น", "วาล์วสุดท้าย"]]
    results = []
    for idx, (name, initial, target) in enumerate([("น้ำเย็น", 10, 32), ("น้ำเย็น", 10, 42), ("น้ำอุ่น", 33, 36)], 1):
        temps, valves = simulate_scenario(controller, initial, target)
        err = abs(target - temps[-1])
        results.append((idx, name, initial, target, temps[-1], err, valves[0], valves[-1]))
        result_rows.append([f"กรณี {idx} ({name})", f"{target:.0f} องศาเซลเซียส", f"{temps[-1]:.2f} องศาเซลเซียส", f"{err:.3f}", f"{valves[0]:.2f}%", f"{valves[-1]:.2f}%"])
    story += [make_table(result_rows, [34 * mm, 29 * mm, 35 * mm, 21 * mm, 29 * mm, 29 * mm], 7.5),
              P("ตารางที่ 2 ผลการจำลองแบบ closed-loop", "CaptionThai"),
              *figure("3_time_simulation.png", "รูปที่ 3 การเปลี่ยนแปลงอุณหภูมิและเปอร์เซ็นต์วาล์วตามเวลา", 150 * mm, 138 * mm), PageBreak()]

    story += [P("4.3 การวิเคราะห์รายกรณี", "H2Thai"),
              P("กรณีที่ 1: เริ่มต้นที่ 10 องศาเซลเซียสและมีเป้าหมาย 32 องศาเซลเซียส ระบบเริ่มด้วยการเปิดวาล์วในระดับสูงเพื่อเพิ่มอุณหภูมิ จากนั้นลดการเปิดวาล์วเมื่อเข้าใกล้เป้าหมาย ผลลัพธ์สุดท้ายมี error ประมาณ 0.823 องศาเซลเซียส แสดงว่าระบบสามารถรักษาทิศทางการควบคุมได้ แต่ยังมี error คงค้างจากการแบ่งระดับเอาต์พุตเป็นกลุ่มภาษา", "BodyThai"),
              P("กรณีที่ 2: เริ่มต้นที่ 10 องศาเซลเซียสและมีเป้าหมาย 42 องศาเซลเซียส เป็นกรณีที่ต้องการความร้อนมากที่สุด ระบบจึงใช้กฎ Cold-High ให้เปิดวาล์วสูงในช่วงต้น ผลลัพธ์มี error ประมาณ 0.383 องศาเซลเซียส ซึ่งต่ำที่สุดในสามกรณี", "BodyThai"),
              P("กรณีที่ 3: เริ่มต้นที่ 33 องศาเซลเซียสและมีเป้าหมาย 36 องศาเซลเซียส ความแตกต่างระหว่างค่าเริ่มต้นกับเป้าหมายมีไม่มาก แต่ระบบต้องควบคุมอย่างละเอียด ผลลัพธ์มี error ประมาณ 1.500 องศาเซลเซียส ซึ่งสูงที่สุด เนื่องจากไม่มีอินพุต error โดยตรงและมีการแบ่งระดับของฟังก์ชันสมาชิกแบบหยาบในบริเวณใกล้เป้าหมาย", "BodyThai"),
              P("4.4 การอภิปรายผล", "H2Thai"),
              P("ผลการทดลองยืนยันว่าการเลือกฐานกฎและการซ้อนทับของฟังก์ชันสมาชิกมีผลโดยตรงต่อความราบรื่นของคำสั่งวาล์ว จุดแข็งของระบบคือความโปร่งใสของเหตุผลและการตอบสนองที่ไม่เปลี่ยนฉับพลัน อย่างไรก็ตาม ค่า error ที่ยังเหลืออยู่สะท้อนว่าการใช้เพียงอุณหภูมิปัจจุบันและเป้าหมายอาจไม่เพียงพอสำหรับการควบคุมที่ละเอียดมาก โดยเฉพาะช่วงที่ค่าอุณหภูมิใกล้กัน", "BodyThai"),
              PageBreak()]

    # Chapter 5
    story += [P("5 สรุปผล ข้อจำกัด และข้อเสนอแนะ", "H1Thai"),
              P("5.1 สรุปผล", "H2Thai"),
              P("งานนี้ออกแบบตัวควบคุมอุณหภูมิน้ำอาบแบบ Mamdani Fuzzy Inference System โดยใช้ข้อมูลอุณหภูมิปัจจุบันและอุณหภูมิเป้าหมายเป็นอินพุต และใช้เปอร์เซ็นต์การเปิดวาล์วน้ำร้อนเป็นเอาต์พุต ระบบมีฐานกฎ 12 ข้อและใช้ centroid defuzzification ผลการจำลองแบบ closed-loop ทั้ง 3 สถานการณ์พบว่าระบบสามารถปรับอุณหภูมิไปในทิศทางที่ถูกต้องและเข้าใกล้เป้าหมายได้ทุกกรณี โดย error สูงสุด 1.500 องศาเซลเซียส", "BodyThai"),
              P("5.2 ข้อจำกัดของงาน", "H2Thai"),
              P("ข้อจำกัดสำคัญคือแบบจำลองยังเป็นแบบ first-order และกำหนดค่าคงที่ของน้ำร้อน น้ำเย็น และอัตราการตอบสนองไว้ล่วงหน้า จึงยังไม่สะท้อนอัตราการไหลจริง ความล่าช้าของวาล์ว การสูญเสียความร้อน อุณหภูมิแวดล้อม และ noise จากเซนเซอร์ นอกจากนี้ ระบบไม่มีอินพุต error หรืออัตราการเปลี่ยนแปลงของ error ทำให้การควบคุมบริเวณใกล้เป้าหมายยังไม่ละเอียดมาก", "BodyThai"),
              P("5.3 ข้อเสนอแนะในการพัฒนา", "H2Thai"),
              P("1) เพิ่ม error และ change-in-error เป็นอินพุตเพื่อให้ระบบรู้ทิศทางการเคลื่อนที่ของอุณหภูมิ<br/>2) ปรับจุดของฟังก์ชันสมาชิกด้วยข้อมูลจากการทดลองจริงและทำ calibration เซนเซอร์<br/>3) เพิ่มแบบจำลองอัตราการไหล ความหน่วง และการสูญเสียความร้อน<br/>4) ทดสอบความทนทานต่อ noise และความเปลี่ยนแปลงของแรงดันน้ำ<br/>5) กำหนด safety limit เพื่อป้องกันอุณหภูมิสูงเกินไปก่อนสั่งเปิดวาล์วจริง", "BodyThai"),
              P("5.4 ข้อสรุปเชิงวิศวกรรม", "H2Thai"),
              P("ระบบที่พัฒนาขึ้นเหมาะสำหรับเป็นต้นแบบเพื่อสาธิตการประยุกต์ใช้ approximate reasoning กับงานควบคุมอุณหภูมิ จุดเด่นคือโครงสร้างเข้าใจง่าย ตรวจสอบได้ และสามารถปรับฐานกฎได้โดยไม่ต้องสร้างแบบจำลองทางคณิตศาสตร์ที่ซับซ้อนทั้งหมด หากต่อยอดด้วยข้อมูลจากระบบจริงและเพิ่มกลไกความปลอดภัย จะสามารถพัฒนาเป็นต้นแบบระบบควบคุมอุณหภูมิสำหรับอุปกรณ์จริงได้", "BodyThai"),
              PageBreak()]

    # References and appendices
    story += [P("เอกสารอ้างอิง", "H1Thai"),
              P("[1] L. A. Zadeh, \"Fuzzy Sets,\" Information and Control, vol. 8, no. 3, pp. 338-353, 1965.", "BodyThai"),
              P("[2] E. H. Mamdani and S. Assilian, \"An Experiment in Linguistic Synthesis with a Fuzzy Logic Controller,\" International Journal of Man-Machine Studies, vol. 7, no. 1, pp. 1-13, 1975.", "BodyThai"),
              P("[3] J. Yen and R. Langari, Fuzzy Logic: Intelligence, Control, and Information. Prentice Hall, 1999.", "BodyThai"),
              P("[4] Python Software Foundation, Python 3 Documentation, 2026.", "BodyThai"),
              Spacer(1, 18 * mm), P("ภาคผนวก ก รายการโปรแกรม", "H1Thai"),
              P("ภาคผนวกนี้แสดงซอร์สโค้ดหลักที่ใช้ในการสร้างฟังก์ชันสมาชิก ตัวควบคุม และการจำลอง เพื่อให้สามารถตรวจสอบและทำซ้ำผลการทดลองได้", "BodyThai")]
    for filename in ["membership.py", "fuzzy_controller.py", "simulate.py"]:
        source = (ROOT / filename).read_text(encoding="utf-8")
        story += [P(filename, "H2Thai"), Preformatted(source, styles["CodeThai"]), PageBreak()]

    doc.build(story)
    print(f"สร้างรายงานฉบับปรับปรุงแล้ว: {PDF_PATH}")


if __name__ == "__main__":
    build()
