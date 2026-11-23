#!/usr/bin/env python3
"""Make presentation-sized PDF and Word companions of the report diagrams."""
from pathlib import Path
from PIL import Image
import pymupdf
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION_START
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt

HERE=Path(__file__).resolve().parent
OUT=HERE/'Campus_Shikayat_Setu_Project_Diagrams.pdf'
FILES=['fig-erd.png','fig-erd-b.png','fig-erd-c.png',
       'fig-usecase-student.png','fig-usecase-officer.png','fig-usecase-administrator.png','fig-usecase-public-visitor.png',
       'fig-class.png','fig-class-b.png','fig-activity.png','fig-activity-b.png','fig-activity-c.png','fig-activity-d.png','fig-activity-e.png','fig-deployment.png','fig-modules.png']

def main():
    pdf=pymupdf.open(); doc=Document(); sec=doc.sections[0]
    current_orientation = None
    for index,name in enumerate(FILES):
        path=HERE/'images'/name
        with Image.open(path) as img: w,h=img.size
        portrait = h > w
        orientation = WD_ORIENT.PORTRAIT if portrait else WD_ORIENT.LANDSCAPE
        changed = orientation != current_orientation
        if changed and current_orientation is not None:
            sec = doc.add_section(WD_SECTION_START.NEW_PAGE)
        sec.orientation=orientation
        sec.page_width=Mm(210 if portrait else 297)
        sec.page_height=Mm(297 if portrait else 210)
        sec.left_margin=sec.right_margin=Mm(10); sec.top_margin=sec.bottom_margin=Mm(10)
        current_orientation = orientation
        pw,ph=(595,842) if portrait else (842,595)
        page=pdf.new_page(width=pw,height=ph)
        page.insert_image(pymupdf.Rect(22,22,pw-22,ph-22),filename=str(path),keep_proportion=True)
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before=p.paragraph_format.space_after=Pt(0)
        p.paragraph_format.line_spacing=1
        p.paragraph_format.page_break_before=index>0 and not changed
        max_width=190 if portrait else 277
        max_height=267 if portrait else 180
        picture=p.add_run().add_picture(str(path),width=Mm(min(max_width,max_height*w/h)))
        picture._inline.docPr.set('descr',name.replace('.png','').replace('-',' '))
    pdf.save(str(OUT),deflate=True);pdf.close()
    doc.core_properties.title='Campus Shikayat Setu — Project Diagrams'; doc.save(OUT.with_suffix('.docx'))
    print(f'Created {len(FILES)} diagram pages in {OUT.name} and Word companion.')
if __name__=='__main__':main()
