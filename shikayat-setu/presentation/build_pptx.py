#!/usr/bin/env python3
"""Create the editable 16:9 Campus Shikayat Setu presentation.

Uses python-pptx's Office-compatible base template with a custom indigo/coral
corporate theme. All infographic elements and slide text are PowerPoint shapes;
application screenshots remain raster images. No network resources are used.
"""
from pathlib import Path
import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / 'report' / 'images'
OUT = ROOT / 'presentation' / 'CampusShikayatSetu_MCA-Mini-Project_Review.pptx'

# Neutral corporate template: dark ink, porcelain, indigo and a coral accent.
INK = RGBColor.from_string('20263A')
MUTED = RGBColor.from_string('5E6980')
DEEP = RGBColor.from_string('1F2242')
INDIGO = RGBColor.from_string('4B4B98')
VIOLET = RGBColor.from_string('7267B4')
CORAL = RGBColor.from_string('DF6D5D')
PALE = RGBColor.from_string('F5F6FA')
PALE_PURPLE = RGBColor.from_string('EDEBFA')
PALE_CORAL = RGBColor.from_string('FAEAE6')
WHITE = RGBColor.from_string('FFFFFF')
BORDER = RGBColor.from_string('DEE2EC')
GREEN = RGBColor.from_string('397968')
FONT = 'Arial'
SLIDE_W, SLIDE_H = 13.333333, 7.5
TOTAL = 16

prs = Presentation()  # PowerPoint-compatible Office base template
prs.slide_width = Inches(SLIDE_W); prs.slide_height = Inches(SLIDE_H)
BLANK = prs.slide_layouts[6]
prs.core_properties.title = 'Campus Shikayat Setu — Project Presentation'
prs.core_properties.subject = 'College grievance redressal system'
prs.core_properties.author = 'Yashwant Santosh Ahire'


def shape(slide, x, y, w, h, color, radius=False, stroke=None):
    item = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                  Inches(x), Inches(y), Inches(w), Inches(h))
    if radius:
        item.adjustments[0] = 0.07
    item.fill.solid(); item.fill.fore_color.rgb = color
    if stroke is None:
        item.line.fill.background()
    else:
        item.line.color.rgb = stroke; item.line.width = Pt(0.9)
    return item


def circle(slide, x, y, d, fill, outline=None):
    item = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    item.fill.solid(); item.fill.fore_color.rgb = fill
    if outline:
        item.line.color.rgb = outline; item.line.width = Pt(1.1)
    else:
        item.line.fill.background()
    return item


def text(slide, x, y, w, h, value, size=18, color=INK, bold=False,
         align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame; frame.clear(); frame.word_wrap = True
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
    frame.vertical_anchor = valign
    for i, line in enumerate(value.split('\n')):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        p.alignment = align; p.line_spacing = 1.08; p.space_after = Pt(0)
        r = p.add_run(); r.text = line; r.font.name = FONT; r.font.size = Pt(size)
        r.font.bold = bold; r.font.color.rgb = color
    return box


def line(slide, x1, y1, x2, y2, color=BORDER, width=1.6):
    item = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    item.line.color.rgb = color; item.line.width = Pt(width)
    return item


def arrow(slide, x, y, w=0.34, color=CORAL):
    return text(slide, x, y, w, 0.42, '→', 24, color, True, PP_ALIGN.CENTER)


def pill(slide, x, y, w, label, color=PALE_PURPLE, foreground=INDIGO):
    shape(slide, x, y, w, 0.36, color, radius=True)
    text(slide, x+0.06, y, w-0.12, 0.36, label, 10, foreground, True,
         PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)


def panel(slide, x, y, w, h, fill=WHITE, stroke=BORDER):
    return shape(slide, x, y, w, h, fill, radius=True, stroke=stroke)


def slide(title, section, number, subtitle=None):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = PALE
    shape(s, 0, 0, 0.13, SLIDE_H, DEEP)
    text(s, 0.58, 0.26, 9.0, 0.25, section.upper(), 10, INDIGO, True)
    text(s, 0.58, 0.63, 11.95, 0.62, title, 31, DEEP, True)
    if subtitle:
        text(s, 0.60, 1.26, 11.9, 0.45, subtitle, 15, MUTED)
    line(s, 0.58, 6.99, 12.78, 6.99, BORDER, 0.8)
    text(s, 0.60, 7.10, 9.5, 0.20, 'CAMPUS SHIKAYAT SETU  /  MCA MINI PROJECT', 9, MUTED, True)
    text(s, 11.78, 7.09, 0.95, 0.22, f'{number:02d} / {TOTAL:02d}', 10, MUTED,
         align=PP_ALIGN.RIGHT)
    return s


def note(s, content):
    s.notes_slide.notes_text_frame.text = content


def picture(s, filename, x, y, w, h):
    path = IMG / filename
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(w/iw, h/ih)
    pw, ph = iw*scale, ih*scale
    s.shapes.add_picture(str(path), Inches(x+(w-pw)/2), Inches(y+(h-ph)/2), Inches(pw), Inches(ph))


def ncard(s, x, y, w, h, number, title, detail, accent=INDIGO):
    panel(s, x, y, w, h)
    circle(s, x+0.23, y+0.23, 0.44, PALE_PURPLE if accent != CORAL else PALE_CORAL)
    text(s, x+0.23, y+0.23, 0.44, 0.44, number, 12, accent, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    text(s, x+0.23, y+0.86, w-0.46, 0.44, title, 19, DEEP, True)
    text(s, x+0.23, y+1.39, w-0.46, h-1.50, detail, 15, MUTED)


# 01 / cover
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = DEEP
shape(s, 0, 0, 0.17, 7.5, CORAL)
text(s, 0.68, 0.55, 7.5, 0.3, 'MCA MINI PROJECT  /  2026–27', 11, RGBColor.from_string('C8C6EE'), True)
text(s, 0.68, 1.30, 7.9, 1.4, 'Campus\nShikayat Setu', 48, WHITE, True)
text(s, 0.70, 3.16, 7.4, 0.48, 'College Grievance Redressal System', 22, RGBColor.from_string('DCDDEF'))
shape(s, 0.70, 4.00, 1.10, 0.06, CORAL)
text(s, 0.70, 4.37, 7.0, 0.36, 'Yashwant Santosh Ahire', 20, WHITE, True)
text(s, 0.70, 4.86, 7.45, 0.73, 'MCA-I  ·  Semester I  ·  SPPU\nDr. B. V. Hiray College of Management & Research Centre', 14, RGBColor.from_string('D3D7E8'))
text(s, 0.70, 6.03, 7.8, 0.36, 'Roll No.: ____________     Guide: ____________________', 13, RGBColor.from_string('D3D7E8'))
# Editable abstract workflow motif.
shape(s, 9.12, 1.22, 3.33, 4.74, RGBColor.from_string('303353'), radius=True)
for j, (n, label, detail) in enumerate([('01','LODGE','Capture a grievance'),('02','ROUTE','Assign a department'),('03','RESOLVE','Track the outcome')]):
    yy = 1.62 + j*1.28
    circle(s, 9.47, yy, 0.52, CORAL if j == 0 else VIOLET)
    text(s, 9.47, yy, 0.52, 0.52, n, 12, WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    text(s, 10.18, yy+0.02, 1.85, 0.28, label, 14, WHITE, True)
    text(s, 10.18, yy+0.35, 1.92, 0.28, detail, 11, RGBColor.from_string('D5D8E7'))
    if j<2: line(s, 9.73, yy+0.56, 9.73, yy+1.24, RGBColor.from_string('898BB0'), 1.3)
note(s, 'Introduce the project as a local mini-project demo for complaint submission, department routing, tracking, resolution and administrative reporting. The semester remains as in the project report.')

# 02 / context
s = slide('Why a grievance system?', 'Context', 2, 'An illustrative manual-process baseline — not a verified description of the college.')
for i,(num,heading,desc) in enumerate([
    ('01','Visibility','Paper-based progress can be difficult to track.'),
    ('02','Ownership','Manual forwarding can delay department assignment.'),
    ('03','Insights','Aggregating status and trends takes additional effort.')]):
    ncard(s, 0.62+i*4.12, 1.90, 3.88, 3.05, num, heading, desc, CORAL if i==1 else INDIGO)
shape(s, 0.62, 5.35, 12.12, 0.83, DEEP, radius=True)
text(s, 0.91, 5.55, 11.55, 0.38, 'A focused workflow connects submission, ownership and status history.', 19, WHITE, True)
note(s, 'The manual baseline is an assumption used for comparison; the current college process has not been surveyed. Explain the potential problems, not unverified claims about the institution.')

# 03 / overview
s = slide('A complete grievance workflow', 'Solution overview', 3, 'Four capabilities, one local web application.')
for i,(n,t,d) in enumerate([
    ('01','Submit','Validated complaint with optional anonymity.'),
    ('02','Assign','Keyword scoring and department routing.'),
    ('03','Resolve','Officer actions and an event timeline.'),
    ('04','Review','Feedback and six administrative reports.')]):
    ncard(s, 0.62+i*3.07, 1.92, 2.84, 3.38, n, t, d, CORAL if i==2 else INDIGO)
for i in range(3): arrow(s, 3.47+i*3.07, 3.15, 0.20, CORAL)
pill(s, 0.66, 5.72, 2.32, '3 SIGNED-IN ROLES')
pill(s, 3.11, 5.72, 2.32, 'PUBLIC TRACKING')
pill(s, 5.57, 5.72, 2.23, '6 PRINT REPORTS')
text(s, 8.15, 5.78, 4.3, 0.30, 'Designed as a single-campus demo', 15, MUTED, align=PP_ALIGN.RIGHT)
note(s, 'Summarise the implemented workflow, not a production deployment. Privacy is role-dependent and the free text of an anonymous complaint can reveal identity.')

# 04 / users
s = slide('Who uses the system?', 'Actors', 4, 'Three stored roles plus a public visitor.')
actors = [
 ('STUDENT','Lodge, track, rate or reopen own complaints.'),
 ('OFFICER','Review the assigned department queue and resolve.'),
 ('ADMINISTRATOR','Manage users, routing, priorities and reports.'),
 ('PUBLIC VISITOR','Track a complaint with code and matching roll number.')]
for i,(title_,detail) in enumerate(actors):
    x=0.62+(i%2)*6.14; y=1.92+(i//2)*1.95
    panel(s,x,y,5.91,1.68)
    shape(s,x+0.23,y+0.26,0.07,1.12,CORAL if i==3 else INDIGO,radius=True)
    text(s,x+0.51,y+0.26,4.95,0.34,title_,16,DEEP,True)
    text(s,x+0.51,y+0.75,4.95,0.67,detail,16,MUTED)
note(s, 'Students see their own complaints; officers are scoped to their department; administrators have college-wide access. A public visitor is an external actor, not a stored role. Signed-in admins can track without a roll match.')

# 05 / lifecycle
s = slide('From submission to closure', 'Complaint lifecycle', 5, 'Acknowledgement and progress can be skipped when resolving a complaint.')
stages=[('01','Submitted'),('02','Acknowledged'),('03','In Progress'),('04','Resolved'),('05','Closed')]
for i,(n,t) in enumerate(stages):
    x=0.62+i*2.46
    panel(s,x,2.25,2.22,1.76, fill=DEEP if i==4 else WHITE, stroke=DEEP if i==4 else BORDER)
    text(s,x+0.15,2.49,1.92,0.32,n,13,CORAL if i==4 else INDIGO,True,PP_ALIGN.CENTER)
    text(s,x+0.12,3.02,1.98,0.50,t,17,WHITE if i==4 else DEEP,True,PP_ALIGN.CENTER)
    if i<4: arrow(s,x+2.24,2.89,0.20,CORAL)
shape(s,0.65,4.47,12.07,0.89,PALE_PURPLE,radius=True)
text(s,0.91,4.64,11.55,0.53,'Acknowledgement and progress are optional; eligible students can reopen a resolved complaint.',16,INDIGO,True)
text(s,0.69,5.72,11.75,0.49,'Complaint events are recorded in the application timeline.',17,MUTED)
note(s, 'A department officer can acknowledge, start work directly from Submitted, or resolve directly from Submitted or Acknowledged as allowed by the application. Feedback closes a resolved complaint. Reopen uses the resolution timestamp and a whole-day age check. Admin force-close is available only for a Resolved complaint; a waiting period is not enforced.')

# 06 / routing
s=slide('How automatic routing works','Routing engine',6,'Deterministic keyword scoring — not machine learning.')
for i,(n,t,d) in enumerate([
 ('01','Read the text','The title is counted twice alongside the description.'),
 ('02','Score keywords','Category keyword hits receive weighted scores.'),
 ('03','Select category','Keep the chosen category unless a stronger match exists.')]):
    ncard(s,0.62+i*4.12,1.90,3.88,3.18,n,t,d,CORAL if i==2 else INDIGO)
for i in range(2): arrow(s,4.53+i*4.12,3.19,0.18,CORAL)
shape(s,0.62,5.48,12.12,0.78,DEEP,radius=True)
text(s,0.92,5.67,11.55,0.38,'Safety terms can set High priority; mass-impact phrases can raise it one level.',16,WHITE,True)
note(s,'The router checks category keyword lists with boundary-aware matching. Multi-word keywords carry greater weight and the title is duplicated before scoring. If another category does not have a stronger score, the student-selected category is retained. Safety and mass-impact phrases affect priority separately.')

# 07 / SLA
s=slide('Priority determines the deadline','SLA rules',7,'The deadline is stamped when the complaint is submitted.')
for i,(label,time,sub,col) in enumerate([('HIGH','24','hours',CORAL),('MEDIUM','72','hours',INDIGO),('LOW','168','hours · 7 days',GREEN)]):
 x=0.62+i*4.12;panel(s,x,1.93,3.87,3.32);pill(s,x+0.24,2.20,1.30,label,PALE_CORAL if i==0 else PALE_PURPLE,col)
 text(s,x+0.24,2.85,2.95,1.02,time,50,DEEP,True);text(s,x+0.28,4.10,3.08,0.38,sub,17,MUTED)
text(s,0.68,5.68,11.9,0.57,'Overdue is calculated from the deadline; escalation does not recalculate the stored SLA.',16,INDIGO,True)
note(s,'High, medium and low priority map to 24, 72 and 168 hours. The deadline is set at submission. Escalation can raise priority to High but does not change the stored deadline. The interface derives overdue status rather than storing an overdue flag.')

# 08 / architecture
s=slide('Simple three-layer architecture','Architecture',8,'A server-rendered application with a local relational database.')
arch=[('BROWSER','HTML · CSS · JavaScript','Forms and routing preview'),('FLASK APP','Python · Jinja2','Validation, routing and roles'),('SQLITE','Local database file','Six related tables')]
for i,(a,b,c) in enumerate(arch):
 x=0.66+i*4.08;panel(s,x,2.03,3.65,2.67)
 circle(s,x+0.26,2.32,0.58,PALE_PURPLE);text(s,x+0.26,2.32,0.58,0.58,str(i+1),15,INDIGO,True,PP_ALIGN.CENTER,MSO_ANCHOR.MIDDLE)
 text(s,x+0.26,3.11,3.1,0.39,a,19,DEEP,True);text(s,x+0.26,3.62,3.1,0.35,b,15,INDIGO,True);text(s,x+0.26,4.08,3.1,0.35,c,14,MUTED)
 if i<2:arrow(s,x+3.73,3.10,0.28,CORAL)
text(s,0.70,5.32,11.8,0.60,'Browser requests are validated by the application before database operations.',17,MUTED)
note(s,'The browser communicates over HTTP with a Flask/Jinja application. The application checks access and validates requests, calls the keyword router, and reads or writes the SQLite file. The Flask development server is for a local demo, not production.')

# 09 / data
s=slide('Six tables support the workflow','Data model',9,'Simplified view of the implemented SQLite schema.')
nodes=[('DEPARTMENTS','Responsible teams'),('CATEGORIES','Keywords + default priority'),('USERS','Students, officers, admins'),('COMPLAINTS','Code, status, SLA, routing'),('EVENTS','Action history'),('FEEDBACK','Rating + comment')]
for i,(t,d) in enumerate(nodes):
 x=0.62+(i%3)*4.12;y=1.92+(i//3)*1.73
 panel(s,x,y,3.88,1.48,fill=WHITE);shape(s,x,y,0.08,1.48,CORAL if i==3 else INDIGO,radius=True)
 text(s,x+0.26,y+0.23,3.35,0.34,t,17,DEEP,True);text(s,x+0.26,y+0.79,3.35,0.46,d,15,MUTED)
text(s,0.69,5.80,11.9,0.45,'Foreign keys link categories, complaints and events; each complaint has at most one feedback record.',15,INDIGO,True)
note(s,'The six tables are departments, categories, users, complaints, complaint_events and feedback. Complaint records reference student, category and assigned department. Event actors may be nullable. The feedback complaint key is unique. The full ERD is in the project report.')

# 10 / student screens
s=slide('Student experience','Application screens',10,'A guided submission and an overview of the student’s own complaints.')
for i,(file,title_,desc) in enumerate([('screen-lodge.png','LODGE A COMPLAINT','Enter details, select a category and submit.'),('screen-dashboard.png','STUDENT DASHBOARD','See status counts and open a complaint.')]):
 x=0.62+i*6.14;panel(s,x,1.78,5.90,4.72);text(s,x+0.20,1.98,5.5,0.30,title_,15,INDIGO,True)
 picture(s,file,x+0.18,2.40,5.54,2.90)
 text(s,x+0.20,5.57,5.48,0.64,desc,15,MUTED)
note(s,'These are application screenshots using illustrative seed data. A student enters a title, description and category; location and anonymous flag are optional. The preview is advisory and routing is recalculated on submission. The dashboard shows the signed-in student’s own complaints.')

# 11 / staff screens
s=slide('Department and administrator views','Application screens',11,'Officers work assigned complaints; administrators manage the wider queue.')
for i,(file,title_,desc) in enumerate([('screen-queue.png','OFFICER QUEUE','Review complaints assigned to the department.'),('screen-console.png','ADMIN CONSOLE','Filter the register and open a complaint.')]):
 x=0.62+i*6.14;panel(s,x,1.78,5.90,4.72);text(s,x+0.20,1.98,5.5,0.30,title_,15,INDIGO,True)
 picture(s,file,x+0.18,2.40,5.54,2.90)
 text(s,x+0.20,5.57,5.48,0.64,desc,15,MUTED)
note(s,'Officers see their department queue and may take permitted actions. Administrators can reassign departments, escalate priority and force-close a Resolved complaint. These screens show synthetic data.')

# 12 / reports
s=slide('Six printable management reports','Reporting',12,'A compact view of workload, service levels and outcomes.')
reports=[('01','Department pendency','Open status and overdue'),('02','SLA compliance','On-time resolution by department'),('03','Resolution time','Average hours by category'),('04','Monthly trend','Submissions and current status'),('05','Feedback summary','Ratings and recent comments'),('06','Routing audit','Mode totals and complaint details')]
for i,(n,t,d) in enumerate(reports):
 x=0.62+(i%3)*4.12;y=1.88+(i//3)*1.81
 panel(s,x,y,3.88,1.55);text(s,x+0.21,y+0.20,0.48,0.31,n,13,CORAL,True)
 text(s,x+0.75,y+0.18,2.90,0.38,t,16,DEEP,True);text(s,x+0.75,y+0.76,2.89,0.52,d,14,MUTED)
text(s,0.69,5.87,11.9,0.48,'Fresh synthetic seed: 37 routing-detail records; the mode summary has two rows.',15,INDIGO,True)
note(s,'There are six print-ready administrative report types. The fresh seed has at least five groups or records per report; the routing summary contains the only two routing modes and a separate table with 37 complaint-level records. Real data can yield fewer rows.')

# 13 / testing
s=slide('Testing the implemented system','Evidence',13,'Recorded test results for the local demo.')
panel(s,0.62,1.90,3.35,3.57,fill=DEEP,stroke=DEEP)
text(s,0.95,2.17,2.7,1.12,'114',52,WHITE,True);text(s,0.95,3.36,2.75,0.77,'automated tests\npassed',19,RGBColor.from_string('E0E0EF'))
for i,(t,d) in enumerate([('UNIT','Routing, priority and validation'),('INTEGRATION','Roles, status changes and reports'),('BROWSER / PRINT','Chromium on Linux and six report views')]):
 y=1.90+i*1.23;panel(s,4.23,y,8.49,1.04)
 text(s,4.50,y+0.16,2.25,0.34,t,15,INDIGO,True);text(s,6.79,y+0.16,5.55,0.62,d,16,MUTED)
text(s,0.69,5.86,11.8,0.51,'Passing checks do not establish production readiness or the absence of defects.',15,INDIGO,True)
note(s,'The documented source and extracted-package runs each recorded 114 passing tests. Automated tests use isolated seeded SQLite databases. Browser and print checks were performed in Linux/Chromium; they are not penetration, load, accessibility, native Windows or production-readiness tests.')

# 14 / constraints
s=slide('Know the current limitations','Privacy & limitations',14,'The implementation is a demonstration, not a production service.')
items=[('ANONYMITY','Officers see masked identity fields; free text can still identify a student.'),('TRACKING','Complaint code and roll number are not strong secrets.'),('WORKFLOW','Reopen uses whole days; admin force-close has no enforced waiting period.'),('DEPLOYMENT','Demo credentials and the development server are not production-ready.')]
for i,(t,d) in enumerate(items):
 x=0.62+(i%2)*6.14;y=1.89+(i//2)*2.02;panel(s,x,y,5.91,1.77)
 shape(s,x+0.24,y+0.25,0.07,1.18,CORAL,radius=True);text(s,x+0.53,y+0.25,4.95,0.35,t,16,DEEP,True);text(s,x+0.53,y+0.77,4.92,0.78,d,15,MUTED)
note(s,'Anonymous identity fields are hidden from officers but visible to administrators; the complaint text itself may expose identity. Public tracking errors may reveal whether a code exists. Native Windows, penetration testing and production capacity were not verified. The application does not enforce an admin waiting period before force-close.')

# 15 / improvements
s=slide('Where the system could go next','Proposed enhancements',15,'These are future ideas, not implemented features.')
for i,(n,t,d) in enumerate([('01','Notifications','Email or SMS updates for status changes.'),('02','Attachments','Evidence uploads with file validation.'),('03','Configuration','Admin interface for categories and keywords.'),('04','Deployment','Hardened hosting, backups and database scaling.')]):
 ncard(s,0.62+i*3.07,1.95,2.84,3.38,n,t,d,CORAL if i==3 else INDIGO)
text(s,0.69,5.81,11.9,0.52,'Each enhancement requires design, security review and testing.',16,INDIGO,True)
note(s,'Notifications, attachments, administrative category management and production deployment are proposed enhancements only. They are not implemented. Scaling beyond SQLite requires adaptation of schema, queries and connection handling.')

# 16 / close
s=prs.slides.add_slide(BLANK);s.background.fill.solid();s.background.fill.fore_color.rgb=DEEP
shape(s,0,0,0.17,7.5,CORAL)
text(s,0.71,0.67,9.0,0.34,'CAMPUS SHIKAYAT SETU',12,RGBColor.from_string('C8C6EE'),True)
text(s,0.70,1.50,8.6,1.03,'Thank you.',52,WHITE,True)
text(s,0.73,2.80,8.8,0.56,'Questions & discussion',22,RGBColor.from_string('DCDDEF'))
shape(s,0.73,3.57,1.08,0.06,CORAL)
text(s,0.73,4.02,7.6,0.95,'Submit  →  Route  →  Resolve  →  Review',21,WHITE,True)
text(s,0.73,6.38,9.0,0.38,'Yashwant Santosh Ahire  ·  MCA-I Semester I',14,RGBColor.from_string('D3D7E8'))
shape(s,9.15,1.20,3.15,4.50,RGBColor.from_string('303353'),radius=True)
for i,(n,label) in enumerate([('01','Role-based workflow'),('02','Transparent routing'),('03','Status and reporting')]):
 y=1.69+i*1.22;circle(s,9.48,y,0.50,CORAL if i==1 else VIOLET)
 text(s,9.48,y,0.50,0.50,n,11,WHITE,True,PP_ALIGN.CENTER,MSO_ANCHOR.MIDDLE)
 text(s,10.16,y+0.06,1.85,0.55,label,15,WHITE,True)
note(s,'Conclude with the implemented features and answer questions. The project is a local demonstration with the limitations already described.')


def apply_office_theme(path):
    """Set the Office theme palette/fonts for editable PowerPoint shapes."""
    ns = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
    with zipfile.ZipFile(path) as src:
        payload = [(entry, src.read(entry.filename)) for entry in src.infolist()]
    fd, tmp = tempfile.mkstemp(suffix='.pptx', dir=path.parent); os.close(fd)
    try:
        with zipfile.ZipFile(tmp, 'w') as dst:
            for info, data in payload:
                if info.filename == 'ppt/theme/theme1.xml':
                    root = ET.fromstring(data)
                    root.set('name', 'Campus Professional')
                    clr = root.find('.//a:clrScheme', ns)
                    if clr is not None:
                        clr.set('name','Campus Professional')
                        for key,val in {'dk2':'1F2242','lt2':'F5F6FA','accent1':'4B4B98','accent2':'DF6D5D','accent3':'7267B4','accent4':'397968','accent5':'5E6980','accent6':'DEE2EC'}.items():
                            entry = clr.find('a:'+key,ns)
                            if entry is not None and len(entry):
                                entry[0].set('val',val)
                    for font in root.findall('.//a:majorFont/a:latin',ns)+root.findall('.//a:minorFont/a:latin',ns):
                        font.set('typeface',FONT)
                    data = ET.tostring(root,encoding='utf-8',xml_declaration=True)
                dst.writestr(info,data)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


if __name__ == '__main__':
    assert len(prs.slides) == TOTAL
    prs.save(OUT)
    apply_office_theme(OUT)
    print(f'Saved: {OUT} | {len(prs.slides)} slides')
