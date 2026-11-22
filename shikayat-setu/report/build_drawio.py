"""Create editable diagrams.net XML from checked project facts.

Layout and labels are generated programmatically. Render the .drawio files with
Diagrams.net; the sources are intentionally uncompressed for easy inspection.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent / 'diagrams'
INK='#172b3a'; TEAL='#187b77'; LINE='#50616b'; PALE='#eaf4f3'; LIGHT='#f6f8fa'

class Diagram:
    def __init__(self, title, subtitle):
        self.doc=ET.Element('mxfile', host='app.diagrams.net', version='32.6.10', type='device')
        d=ET.SubElement(self.doc,'diagram',name=title,id='page-1')
        m=ET.SubElement(d,'mxGraphModel',dx='1400',dy='950',grid='1',gridSize='10',guides='1',tooltips='1',connect='1',arrows='1',fold='1',page='1',pageScale='1',pageWidth='1450',pageHeight='1100',math='0',shadow='0')
        self.root=ET.SubElement(m,'root'); ET.SubElement(self.root,'mxCell',id='0'); ET.SubElement(self.root,'mxCell',id='1',parent='0')
        self.count=1
        self.text(30,10,1340,45,title,28,bold=True)
        self.text(30,53,1340,30,subtitle,16,color='#536670')
    def v(self,x,y,w,h,value='',style=''):
        self.count+=1; c=ET.SubElement(self.root,'mxCell',id=str(self.count),value=value,style=style,vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'}); return str(self.count)
    def text(self,x,y,w,h,value,size=17,bold=False,color=INK,align='center'):
        return self.v(x,y,w,h,value,f'text;html=1;align={align};verticalAlign=middle;whiteSpace=wrap;rounded=0;strokeColor=none;fillColor=none;fontFamily=Arial;fontSize={size};fontStyle={1 if bold else 0};fontColor={color};')
    def box(self,x,y,w,h,title,body='',fill=LIGHT):
        self.v(x,y,w,h,'',f'rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={TEAL};strokeWidth=2;')
        self.text(x+8,y+10,w-16,34,title,20,True)
        if body: self.text(x+12,y+47,w-24,h-54,body,16,color='#344c57')
    def table(self,x,y,w,h,title,body):
        self.v(x,y,w,h,'',f'rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor={INK};strokeWidth=2;')
        self.v(x,y,w,40,title,f'rounded=0;whiteSpace=wrap;html=1;fillColor={INK};strokeColor={INK};fontColor=#ffffff;fontStyle=1;fontSize=18;fontFamily=Arial;')
        self.text(x+12,y+48,w-24,h-56,body,16,align='left')
    def edge(self,x1,y1,x2,y2,points=(),arrow=True,color=LINE,dashed=False):
        self.count+=1; c=ET.SubElement(self.root,'mxCell',id=str(self.count),value='',style=f'edgeStyle=none;rounded=0;html=1;strokeColor={color};strokeWidth=2;endArrow={"block" if arrow else "none"};endFill=1;dashed={1 if dashed else 0};',edge='1',parent='1')
        g=ET.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'})
        ET.SubElement(g,'mxPoint',x=str(x1),y=str(y1),**{'as':'sourcePoint'})
        if points:
            a=ET.SubElement(g,'Array',**{'as':'points'})
            for x,y in points: ET.SubElement(a,'mxPoint',x=str(x),y=str(y))
        ET.SubElement(g,'mxPoint',x=str(x2),y=str(y2),**{'as':'targetPoint'})
    def note(self,x,y,w,h,text,size=16):
        self.v(x,y,w,h,text,f'rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=#fff9e9;strokeColor=#c6a650;fontFamily=Arial;fontSize={size};fontColor={INK};spacing=8;')
    def save(self,name):
        OUT.mkdir(exist_ok=True); ET.indent(self.doc); ET.ElementTree(self.doc).write(OUT/(name+'.drawio'),encoding='utf-8',xml_declaration=True)

def architecture():
    d=Diagram('Application architecture','Server-rendered Flask application with a local SQLite database')
    d.box(70,250,320,190,'Browser','Forms, local CSS and JavaScript\nOptional routing preview')
    d.box(530,250,340,190,'Flask application','app.py and Jinja templates\nrouting.py and database.py',PALE)
    d.box(1010,250,320,190,'SQLite database','Local database file\nSix related tables')
    d.edge(390,345,530,345); d.text(415,300,90,30,'HTTP',17,True)
    d.edge(870,345,1010,345); d.text(895,300,90,30,'sqlite3',17,True)
    d.note(150,550,1100,90,'run.py initializes and seeds the database before starting the Flask development server.\nThe server validates requests and enforces access rules.')
    d.save('fig-architecture')

def usecase():
    """Four separately drawn, editable pages in one diagrams.net document."""
    groups = [
        ('Student', 'Stored user role: student', [
            'Register an account', 'Sign in / sign out', 'Lodge a complaint',
            'View own complaints', 'Confirm and rate resolution', 'Reopen own resolved complaint',
            'Change password'],
         'Students may also use the public tracker. Reopening is subject to the implemented age check.'),
        ('Officer', 'Stored user role: officer', [
            'Sign in / sign out', 'View department queue', 'Acknowledge a complaint',
            'Start work', 'Resolve with a remark', 'Add a remark', 'Change password'],
         'Officers can access complaints assigned to their own department.'),
        ('Administrator', 'Stored user role: admin', [
            'Sign in / sign out', 'View and filter console', 'Manage user accounts',
            'Reassign department', 'Escalate priority', 'Acknowledge / start / resolve',
            'Add a remark', 'Submit feedback', 'Force-close resolved complaint',
            'View and print reports', 'Track without roll check', 'Change password'],
         'Admin can perform officer actions and submit feedback. Force-close requires Resolved status.'),
        ('Public visitor', 'External actor: not a stored user role', [
            'Track with code and roll number'],
         'Public tracking normally requires both the complaint code and the matching student roll number.'),
    ]
    doc = ET.Element('mxfile', host='app.diagrams.net', version='32.6.10', type='device')
    for number, (role, subtitle, uses, note) in enumerate(groups, 1):
        d = Diagram(f'Use-case diagram — {role}', subtitle)
        # Each page is a standalone use-case diagram: actor outside the system boundary.
        d.v(350, 125, 1000, 820, '', 'rounded=0;fillColor=#ffffff;strokeColor=#187b77;strokeWidth=2;')
        d.text(620, 136, 460, 36, 'CAMPUS SHIKAYAT SETU', 21, True, TEAL)
        d.v(85, 400, 100, 155, '', 'shape=umlActor;html=1;outlineConnect=0;strokeColor=#172b3a;strokeWidth=2;')
        d.text(20, 575, 230, 38, role, 22, True)
        spacing = 59 if len(uses) > 9 else 88
        total = 50 + (len(uses) - 1) * spacing
        top = 200 + (680 - total) / 2
        for index, label in enumerate(uses):
            y = round(top + index * spacing)
            # Straight individual associations fan out from the actor, without shared trunks.
            d.edge(185, 452, 670, y + 25, arrow=False, color=LINE)
            d.v(670, y, 520, 50, label,
                'ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#172b3a;strokeWidth=2;fontFamily=Arial;fontSize=20;fontColor=#172b3a;')
        d.note(40, 970, 1320, 70, note, 16)
        page = d.doc.find('diagram')
        page.set('name', role)
        page.set('id', f'usecase-{number}')
        doc.append(page)
    OUT.mkdir(exist_ok=True)
    ET.indent(doc)
    ET.ElementTree(doc).write(OUT / 'fig-usecase.drawio', encoding='utf-8', xml_declaration=True)

# Corrected diagrams are generated from shared drawing primitives.
# Keep the original entry points for callers and regenerate matching PNGs with
# build_corrected_diagrams.py separately.
def _corrected(name):
    from build_corrected_diagrams import build
    build(name, OUT)

def erd(): _corrected('fig-erd')
def klass(): _corrected('fig-class')
def activity(): _corrected('fig-activity')
def deployment(): _corrected('fig-deployment')
def modules(): _corrected('fig-modules')

if __name__=='__main__':
    for func in (architecture,erd,usecase,klass,activity,deployment,modules): func()
    print('Wrote seven editable diagrams to',OUT)
