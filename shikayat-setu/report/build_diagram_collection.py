#!/usr/bin/env python3
"""Make presentation-sized PDF and Word companions of the report diagrams."""
from pathlib import Path
from PIL import Image
import pymupdf
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt

HERE=Path(__file__).resolve().parent
OUT=HERE/'Campus_Shikayat_Setu_Project_Diagrams.pdf'
FILES=['fig-erd.png','fig-erd-b.png','fig-erd-c.png',
       'fig-usecase-student.png','fig-usecase-officer.png','fig-usecase-administrator.png','fig-usecase-public-visitor.png',
       'fig-class.png','fig-class-b.png','fig-activity.png','fig-activity-b.png','fig-activity-c.png','fig-activity-d.png','fig-activity-e.png','fig-deployment.png','fig-modules.png']

def main():
    pdf=pymupdf.open(); doc=Document(); sec=doc.sections[0]
    sec.orientation=WD_ORIENT.LANDSCAPE; sec.page_width=Mm(297); sec.page_height=Mm(210)
    sec.left_margin=sec.right_margin=Mm(10); sec.top_margin=sec.bottom_margin=Mm(10)
    for index,name in enumerate(FILES):
        path=HERE/'images'/name
        with Image.open(path) as img: w,h=img.size
        page=pdf.new_page(width=842,height=595)
        page.insert_image(pymupdf.Rect(22,22,820,573),filename=str(path),keep_proportion=True)
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before=p.paragraph_format.space_after=Pt(0)
        p.paragraph_format.line_spacing=1
        p.paragraph_format.page_break_before=index>0
        picture=p.add_run().add_picture(str(path),width=Mm(min(277,180*w/h)))
        picture._inline.docPr.set('descr',name.replace('.png','').replace('-',' '))
    pdf.save(str(OUT),deflate=True);pdf.close()
    doc.core_properties.title='Campus Shikayat Setu — Project Diagrams'; doc.save(OUT.with_suffix('.docx'))
    print(f'Created {len(FILES)} diagram pages in {OUT.name} and Word companion.')
if __name__=='__main__':main()
