"""Build the editable DOCX and printable PDF from the Markdown study guide.

Dependencies: fpdf2, python-docx, Pillow. The PDF uses DejaVu fonts.
Run: python study/build_guide.py
"""
from pathlib import Path
import re
from fpdf import FPDF
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image

BASE = Path(__file__).resolve().parent
SOURCE = BASE / 'Campus_Shikayat_Setu_Study_and_Viva_Guide.md'
PDF = SOURCE.with_suffix('.pdf')
DOCX = SOURCE.with_suffix('.docx')
FONT = Path('/usr/share/fonts/truetype/dejavu')

class GuidePDF(FPDF):
    def __init__(self):
        super().__init__(unit='mm', format='A4')
        self.set_margins(17, 17, 17)
        self.set_auto_page_break(True, margin=19)
        self.add_font('DejaVu', '', str(FONT / 'DejaVuSans.ttf'))
        self.add_font('DejaVu', 'B', str(FONT / 'DejaVuSans-Bold.ttf'))
        self.add_font('DejaVu', 'I', str(FONT / 'DejaVuSans.ttf'))
        self.add_font('DejaVu', 'BI', str(FONT / 'DejaVuSans-Bold.ttf'))
        self.add_font('Mono', '', str(FONT / 'DejaVuSansMono.ttf'))
    def header(self):
        if self.page_no() > 1:
            self.set_font('DejaVu','',8); self.set_text_color(90,105,115)
            self.cell(0,5,'Campus Shikayat Setu  |  Study and Viva Guide', align='R')
            self.ln(8)
    def footer(self):
        self.set_y(-13); self.set_draw_color(190,202,202); self.line(17,self.get_y(),193,self.get_y())
        self.set_y(-11); self.set_font('DejaVu','',8); self.set_text_color(90,105,115)
        self.cell(0,5,f'Learning guide  •  Page {self.page_no()}',align='R')
    def need(self, mm):
        if self.get_y()+mm > self.h-self.b_margin: self.add_page()

def clean(s):
    return s.replace('`','')

def pdf_build(lines):
    pdf=GuidePDF(); pdf.add_page(); code=False
    for line in lines:
        line=line.rstrip()
        pdf.set_x(17)
        if line.startswith('```'):
            code=not code; pdf.ln(2); continue
        if code:
            pdf.set_font('Mono','',8.5); pdf.set_text_color(35,51,60)
            pdf.multi_cell(0,5,line or ' '); continue
        if not line or line=='---':
            pdf.ln(2); continue
        image=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line)
        if image:
            img=(BASE/image.group(2)).resolve()
            with Image.open(img) as im: w,h=im.size
            width=172; height=width*h/w
            pdf.need(height+12); pdf.image(str(img),w=width,x=19); pdf.ln(2)
            pdf.set_font('DejaVu','I',8); pdf.set_text_color(85,100,110); pdf.multi_cell(0,4,image.group(1),align='C'); pdf.ln(2); continue
        heading=re.match(r'^(#{1,3})\s+(.+)$',line)
        if heading:
            level=len(heading.group(1)); title=clean(heading.group(2))
            pdf.need(32 if level == 1 else 25 if level == 2 else 17); pdf.ln(2 if level<3 else 1)
            pdf.set_font('DejaVu','B',{1:17,2:13,3:10.4}[level]); pdf.set_text_color(20,45,60) if level!=2 else pdf.set_text_color(20,106,102)
            pdf.multi_cell(0,{1:8,2:6.5,3:5.3}[level],title); pdf.ln(1); continue
        pdf.need(8); pdf.set_font('DejaVu','',9.3); pdf.set_text_color(30,40,48)
        if line.startswith('- '):
            pdf.set_x(20); pdf.multi_cell(170,5,'•  '+clean(line[2:]),markdown=True,align='L'); pdf.ln(.8)
        else:
            pdf.multi_cell(0,5,clean(line),markdown=True,align='L'); pdf.ln(1.7)
    pdf.output(PDF)

def add_runs(p,text):
    for token in re.split(r'(\*\*.*?\*\*|`[^`]+`)',text):
        if not token: continue
        if token.startswith('**') and token.endswith('**'):
            r=p.add_run(token[2:-2]); r.bold=True
        elif token.startswith('`') and token.endswith('`'):
            r=p.add_run(token[1:-1]); r.font.name='Consolas'
        else: p.add_run(token)

def docx_build(lines):
    doc=Document(); sec=doc.sections[0]
    sec.top_margin=Inches(.7); sec.bottom_margin=Inches(.7); sec.left_margin=Inches(.8); sec.right_margin=Inches(.8)
    styles=doc.styles
    styles['Normal'].font.name='Calibri'; styles['Normal'].font.size=Pt(10.5)
    styles['Normal'].paragraph_format.space_after=Pt(5)
    for h in ('Title','Heading 1','Heading 2','Heading 3'):
        styles[h].font.name='Calibri'; styles[h].font.color.rgb=RGBColor.from_string('173C48')
    styles['Heading 1'].font.size=Pt(18); styles['Heading 2'].font.size=Pt(14); styles['Heading 3'].font.size=Pt(11)
    styles['Heading 3'].paragraph_format.keep_with_next=True
    foot=sec.footer.paragraphs[0]; foot.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    foot.add_run('Campus Shikayat Setu  |  Page ')
    fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); foot._p.append(fld)
    code=False
    for line in lines:
        line=line.rstrip()
        if line.startswith('```'): code=not code; continue
        if not line or line=='---': continue
        if code:
            p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(0); r=p.add_run(line); r.font.name='Consolas'; r.font.size=Pt(9); continue
        image=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line)
        if image:
            p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str((BASE/image.group(2)).resolve()),width=Inches(6.6))
            c=doc.add_paragraph(image.group(1),style='Caption'); c.alignment=WD_ALIGN_PARAGRAPH.CENTER; continue
        h=re.match(r'^(#{1,3})\s+(.+)$',line)
        if h:
            p=doc.add_paragraph(style=f'Heading {len(h.group(1))}'); add_runs(p,h.group(2)); continue
        if line.startswith('- '): p=doc.add_paragraph(style='List Bullet'); add_runs(p,line[2:])
        else: p=doc.add_paragraph(); add_runs(p,line)
    doc.save(DOCX)

if __name__=='__main__':
    lines=SOURCE.read_text(encoding='utf-8').splitlines()
    pdf_build(lines); docx_build(lines)
    print('Built', PDF, 'and', DOCX)
