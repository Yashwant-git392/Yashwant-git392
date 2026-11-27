"""Create exact image references and an editable transcription of official pages.

The supplied PDF is image-only and sanitized only for document metadata.
The separate reference DOCX retains page images; the report uses editable text
and tables with a cropped image logo, so its layout may differ.
"""
from io import BytesIO
from pathlib import Path
import pymupdf
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt

HERE = Path(__file__).resolve().parent
OFFICIAL = HERE / 'reference' / 'PROJECT REPORT Sequence Yashwant.pdf'


def add_official_pages(doc):
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.left_margin = sec.right_margin = sec.top_margin = sec.bottom_margin = Mm(0)
    with pymupdf.open(OFFICIAL) as source:
        if len(source) != 4:
            raise ValueError('The supplied official front matter must have four pages.')
        for index, page in enumerate(source):
            pix = page.get_pixmap(matrix=pymupdf.Matrix(2.5, 2.5), alpha=False)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.page_break_before = index > 0
            p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1
            run = p.add_run()
            run.font.size = Pt(1)
            picture = run.add_picture(BytesIO(pix.tobytes('png')), width=Mm(205))
            picture._inline.docPr.set('descr', f'Official supplied page {index+1}')


def build_reference_docx():
    doc = Document()
    add_official_pages(doc)
    doc.core_properties.title = 'Supplied official front matter — Campus Shikayat Setu'
    doc.save(OFFICIAL.with_suffix('.docx'))


# The supplied PDF remains the exact visual reference. This transcription makes
# the report's front matter editable in Word; it is not a pixel-identical scan.
INDEX_ROWS = [
    ('1', '', 'Introduction'),
    ('', '1.1', 'Abstract'),
    ('', '1.2', 'Existing System & Need for System'),
    ('', '1.3', 'Scope of System'),
    ('', '1.4', 'Operating Environment-Hardware and Software'),
    ('', '1.5', 'Brief Description of Technology used\nOperating System used (Window/Unix)\nRDBMS/No Sql used to build database(MySQL/Oracle,Teradata,etc)'),
    ('2', '', 'Proposed System'),
    ('', '2.1', 'Study of Similar Systems (if required research paper can be included)'),
    ('', '2.2', 'Feasibility Study'),
    ('', '2.3', 'Objective of Proposed System'),
    ('', '2.4', 'Users of System'),
    ('3', '', 'System Analysis and Design'),
    ('', '3.1', 'Systems requirements(Functional & non-functional requirements)'),
    ('', '3.2', 'Entity Relationship Diagram(ERD)'),
    ('', '3.3', 'Table Structure'),
    ('', '3.4', 'Use Case Diagram'),
    ('', '3.5', 'Class Diagram'),
    ('', '3.6', 'Activity Diagram'),
    ('', '3.7', 'Deployment Diagram'),
    ('', '3.8', 'Module Hierarchy Diagram'),
    ('', '3.9', 'Sample Input & Output Screens (Screens must have valid Data. All reports must have at-least five valid records)'),
    ('4', '', 'Coding'),
    ('', '4.1', 'Code Snippets'),
    ('5', '', 'Testing'),
    ('', '5.1', 'Test Strategy'),
    ('', '5.2', 'Unit Test Plan'),
    ('', '5.3', 'Acceptance Test Plan'),
    ('', '5.4', 'Test Case / Test Script'),
    ('6', '', 'Limitations of Proposed System'),
    ('7', '', 'Proposed Enhancements'),
    ('8', '', 'Conclusion'),
    ('9', '', 'Bibliography'),
    ('10', '', 'User Manual(All Screens with proper description/purpose details about validation related to data to be entered)'),
]


def add_editable_official_pages(doc):
    """Append editable, manually transcribed front pages and an editable index.

    The logo is an image cropped from the supplied cover; all wording and table
    cells are normal Word text. Start each page explicitly; Word may reflow.
    """
    from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.left_margin = sec.right_margin = Mm(20)
    sec.top_margin = sec.bottom_margin = Mm(15)

    def para(text='', *, size=12, bold=False, italic=False, center=False,
             right=False, before=0, after=0, page=False, spacing=1.0):
        p = doc.add_paragraph()
        p.alignment = (WD_ALIGN_PARAGRAPH.CENTER if center else
                       WD_ALIGN_PARAGRAPH.RIGHT if right else WD_ALIGN_PARAGRAPH.LEFT)
        fmt = p.paragraph_format
        fmt.page_break_before = page
        fmt.space_before, fmt.space_after = Pt(before), Pt(after)
        fmt.line_spacing = spacing
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), 'Times New Roman')
        run.font.size, run.font.bold, run.font.italic = Pt(size), bold, italic
        return p

    # Cover: guide remains blank, as on the supplied page.
    para('A', bold=True, center=True, before=10, after=10)
    para('PROJECT REPORT', bold=True, center=True, after=10)
    para('ON', bold=True, center=True, after=10)
    para('Campus Shikayat Setu - College Grievance Redressal System', bold=True, center=True, after=10)
    para('Submitted By', bold=True, center=True, after=10)
    para('Yashwant Santosh Ahire', size=16, bold=True, center=True, after=10)
    para('MCA –I SEM – I', bold=True, center=True, after=28)
    para('UNDER THE GUIDANCE OF', bold=True, center=True, after=28)
    para('MCA (MANAGEMENT)', bold=True, center=True, after=28)
    para('In Partial Fulfillment of', bold=True, center=True, after=10)
    para('SAVITRIBAI PHULE PUNE UNIVERSITY ‘MASTER IN COMPUTER APPLICATION’', bold=True, center=True, after=28)
    para('K.B.H.S.S. Trust’s', size=16, bold=True, center=True, after=10)
    para('Dr.B.V.Hiray College of Management & Research Centre', size=16, bold=True, center=True, after=18)
    with pymupdf.open(OFFICIAL) as source:
        # Crop just the logo, retaining the official pages untouched elsewhere.
        logo = source[0].get_pixmap(matrix=pymupdf.Matrix(3, 3),
                                    clip=pymupdf.Rect(260, 606, 373, 726), alpha=False)
        p = para(center=True, after=12)
        image = p.add_run().add_picture(BytesIO(logo.tobytes('png')), width=Mm(33))
        image._inline.docPr.set('descr', 'College logo from supplied cover')
    para('2026-2027', size=14, bold=True, center=True)

    para('DECLARATION', size=15, bold=True, center=True, page=True, before=10, after=20)
    para('This is to declare that I  YASHWANT SANTOSH AHIRE student of Master of Computer '
         'Application 2026-2027, have given original data information to the best of my knowledge in the '
         'report title “ CAMPUS SHIKAYAT SETU - College Grievance Redressal System ”. '
         'Report Presented here is my own work done and has not been duplicated from any other source.',
         size=13, spacing=1.8, after=28)
    para('Thanking You.', size=13, after=85)
    para('Yours Sincerely', size=13, right=True, after=18)
    para('(Student Name)', size=13, right=True)

    p = para('ACKNOWLEDGEMENT', size=15, bold=True, center=True, page=True, before=22, after=30)
    p.runs[0].font.underline = True
    para('With the complete work undertaken .I would like to take this opportunity to thank all those who helped me to complete this project with their guidance, co-operation and support. This project would no have been materialized without the help from many quarters.', size=13, spacing=1.8, after=14)
    para('I would like to thank the Director, Dr. Subhash J. Jadhav, and my Project Guide Mr. /Ms. __________________________as well as all my faculty members of Dr. B. V. Hiray College of Management & Research Center, Malegaon.', size=13, spacing=1.8, after=14)
    para('I owe my special thanks to my friends for providing the friendly and cordial environment to achieve the goal. Without their valuable contribution this project would not have been a success.', size=13, spacing=1.8, after=14)
    para('Lastly, I would like to thank my parents for their guidance and support  due to which I have put the best efforts in this project.', size=13, spacing=1.8, after=14)
    para('Date:', size=13, bold=True, after=18)
    para('Place: Malegaon.', size=13)

    para('INDEX', size=16, bold=True, center=True, page=True, after=8)
    table = doc.add_table(rows=0, cols=4)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    widths = (Mm(22), Mm(16), Mm(112), Mm(20))
    for col, width in zip(table.columns, widths):
        col.width = width
    for row_index, values in enumerate([('Chapter\nNo', '', 'Details', 'Page No')] + [(a, b, c, '') for a, b, c in INDEX_ROWS]):
        cells = table.add_row().cells
        for i, (cell, value, width) in enumerate(zip(cells, values, widths)):
            cell.width = width
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in (0, 1, 3) or row_index == 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(value)
            run.font.name = 'Times New Roman'
            run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'), 'Times New Roman')
            run.font.size = Pt(10.5)
            run.font.bold = row_index == 0 or (bool(values[0]) and i in (0, 2))


if __name__ == '__main__':
    build_reference_docx()
