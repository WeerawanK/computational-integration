from pathlib import Path
from docx import Document


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "assignment3_report.docx"


def insert_after(paragraph, text):
    """แทรกย่อหน้าใหม่ต่อจากย่อหน้าที่กำหนด"""
    new_paragraph = paragraph._parent.add_paragraph(text)
    paragraph._p.addnext(new_paragraph._p)
    return new_paragraph


def main():
    document = Document(str(REPORT))

    # ------------------------------------------------------------------
    # 1) เติมข้อมูลผู้จัดทำลงบนหน้าปก
    # ------------------------------------------------------------------
    # ใช้ข้อมูลที่มีอยู่ในหน้ารายละเอียดของรายงานฉบับนี้
    for paragraph in document.paragraphs:
        if paragraph.text.startswith("Computer Assignment 3"):
            paragraph.text = (
                "Computer Assignment 3\n"
                "ภาคเรียนที่ 1 ปีการศึกษา 2569\n\n"
                "ผู้จัดทำ: นางสาววีระวรรณ ก้อนคำ\n"
                "รหัสนักศึกษา: 670610782\n"
                "รายวิชา: Introduction to Computational Intelligence\n"
                "คณะวิศวกรรมศาสตร์ มหาวิทยาลัยเชียงใหม่\n\n"
                "หัวข้อ: Breast Cancer Classification on WDBC Dataset"
            )
            break

    # ------------------------------------------------------------------
    # 2) เปลี่ยนชื่อบทให้เป็นรูปแบบเดียวกับรายงาน Assignment 2
    # ------------------------------------------------------------------
    chapter_names = {
        "1 บทนำ": "บทที่ 1 บทนำ",
        "2 ทฤษฎีและงานที่เกี่ยวข้อง": "บทที่ 2 ทฤษฎีและงานที่เกี่ยวข้อง",
        "3 การออกแบบระบบและวิธีดำเนินงาน": "บทที่ 3 การออกแบบระบบและวิธีดำเนินงาน",
        "4 ผลการทดลองและการวิเคราะห์": "บทที่ 4 ผลการทดลองและการวิเคราะห์",
        "5 สรุปผล ข้อจำกัด และข้อเสนอแนะ": "บทที่ 5 สรุปผล ข้อจำกัด และข้อเสนอแนะ",
    }
    for paragraph in document.paragraphs:
        if paragraph.text in chapter_names:
            paragraph.text = chapter_names[paragraph.text]
        for old, new in chapter_names.items():
            if paragraph.text.startswith(old + "\t"):
                paragraph.text = paragraph.text.replace(old, new, 1)

    # ------------------------------------------------------------------
    # 3) แก้ข้อความวิเคราะห์ให้สรุปตามหลักฐานทางสถิติ
    # ------------------------------------------------------------------
    for paragraph in document.paragraphs:
        text = paragraph.text

        if text.startswith("จำนวน hidden layer:"):
            paragraph.text = (
                "จำนวน hidden layer: โครงสร้าง 1 hidden layer มีแนวโน้มให้ accuracy เฉลี่ย "
                "91.53%-91.73% สูงกว่า 2 hidden layers ที่ได้ 89.27%-89.84% และมี SD ต่ำกว่า "
                "แต่ความแตกต่างยังไม่เพียงพอที่จะสรุปว่า 1 hidden layer ดีกว่าอย่างมีนัยสำคัญ "
                "เมื่อดู training accuracy ในตารางที่ 6 พบว่า 2 hidden layers ก็ต่ำกว่าเช่นกัน "
                "ขณะที่ผลต่างระหว่าง training และ test accuracy อยู่ที่ประมาณ 1-2 จุดในทุก configuration "
                "จึงอาจสะท้อนว่าเครือข่ายสองชั้นยังถูกค้นหาน้ำหนักได้ไม่ดีพอภายใต้งบการค้นหา "
                "320 fitness evaluations ต่อ fold มากกว่าจะเป็น overfitting"
            )

        if text.startswith("จำนวน nodes:"):
            paragraph.text = paragraph.text.replace(
                "แต่ทำให้ใช้เวลาเพิ่มเป็นประมาณ 1.9 เท่า",
                "แต่ทำให้ 16 nodes ใช้เวลามากกว่า 8 nodes ประมาณ 1.9 เท่า",
            )

        if text.startswith("โครงสร้าง 12-6"):
            paragraph.text = paragraph.text.replace(
                "ซึ่งต่ำสุดในสี่ configuration",
                "ซึ่งมี specificity ต่ำสุดในสี่ configuration",
            )

        if text.startswith("งานนี้พัฒนา MLP"):
            paragraph.text = paragraph.text.replace(
                "แต่ 8 nodes ใช้เวลาน้อยกว่าประมาณ 1.9 เท่า ส่วนโครงสร้างสองชั้นให้ผลต่ำกว่าและแปรผันมากกว่าในงบการค้นหาที่กำหนด",
                "แต่ 16 nodes ใช้เวลามากกว่า 8 nodes ประมาณ 1.9 เท่า ส่วนโครงสร้างสองชั้นมีแนวโน้มให้ผลต่ำกว่าและแปรผันมากกว่าในงบการค้นหาที่กำหนด แต่ยังสรุปความแตกต่างอย่างมีนัยสำคัญไม่ได้",
            )

    # เพิ่มผล paired t-test เพื่อรองรับการอภิปรายเรื่อง hidden layers
    discussion_end = None
    for paragraph in document.paragraphs:
        if paragraph.text.startswith("ความแปรผันระหว่าง folds:"):
            discussion_end = paragraph
            break
    if discussion_end is not None:
        insert_after(
            discussion_end,
            "การทดสอบความแตกต่างแบบ paired t-test จาก accuracy ของทั้ง 10 folds "
            "ให้ค่า |t| ไม่เกิน 1.06 ในทุกคู่ที่เปรียบเทียบ ขณะที่ค่า critical value ที่ระดับนัยสำคัญ "
            "0.05 และองศาอิสระ 9 เท่ากับ 2.262 ดังนั้นยังไม่พบหลักฐานว่าความแตกต่างระหว่าง configuration "
            "มีนัยสำคัญทางสถิติ ข้อสรุปที่เหมาะสมคือแต่ละ configuration มีแนวโน้มแตกต่างกัน "
            "แต่ผลจากการทดลองชุดนี้ยังยืนยันผู้ชนะที่ชัดเจนไม่ได้",
        )

    # ------------------------------------------------------------------
    # 4) ลบเอกสารอ้างอิง [6] เพราะไม่มีการอ้างในเนื้อหา
    # ------------------------------------------------------------------
    for paragraph in list(document.paragraphs):
        if paragraph.text.startswith("[6] Python Software Foundation"):
            paragraph._element.getparent().remove(paragraph._element)

    document.save(str(REPORT))
    print(f"แก้รายงานแล้ว: {REPORT}")


if __name__ == "__main__":
    main()
