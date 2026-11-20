"""Create editable diagrams.net XML from checked project facts.

Layout and labels are generated programmatically. Render the .drawio files with
Diagrams.net; the sources are intentionally uncompressed for easy inspection.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
from diagram_data import schema_facts

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

def erd():
    facts=schema_facts()
    actual={(t,k,v['table']) for t,f in facts.items() for k,v in f['foreign_keys'].items()}
    expected={('categories','department_id','departments'),('users','department_id','departments'),('complaints','student_id','users'),('complaints','category_id','categories'),('complaints','department_id','departments'),('complaint_events','complaint_id','complaints'),('complaint_events','actor_id','users'),('feedback','complaint_id','complaints')}
    if actual!=expected or 'complaint_id' not in facts['feedback']['unique']: raise ValueError('Schema changed; review ERD')
    d=Diagram('Entity–relationship diagram','Actual SQLite relationships • selected columns • cardinality is named at both ends')
    d.table(40,160,335,160,'departments','PK  id\nUQ  name\nhead_name, email, location')
    d.table(535,160,335,170,'categories','PK  id      UQ  name\nFK  department_id  NOT NULL\ndefault_priority, keywords')
    d.table(1025,160,335,175,'users','PK  id      UQ  username, roll_no\nFK  department_id  NULL\nrole, full_name, status')
    d.table(535,490,335,205,'complaints','PK  id      UQ  code\nFK  student_id, category_id\nFK  department_id  (all NOT NULL)\npriority, status, dates')
    d.table(40,740,335,160,'feedback','PK  id\nFK/UQ  complaint_id  NOT NULL\nrating, comment, created_at')
    d.table(1025,740,335,160,'complaint_events','PK  id\nFK  complaint_id  NOT NULL\nFK  actor_id  NULL\nevent_type, note, created_at')
    # Labels explicitly say which endpoint each multiplicity refers to.
    d.edge(375,220,535,220,arrow=False); d.text(390,180,130,36,'dept 1 | 0..* categories',14)
    d.edge(210,160,1192,160,[(210,115),(1192,115)],False); d.text(485,80,430,30,'department 0..1  |  users 0..*',15)
    d.edge(210,320,535,565,[(210,565)],False); d.text(225,525,270,33,'department 1 | 0..* complaints',14)
    d.edge(702,330,702,490,arrow=False); d.text(710,380,160,38,'category 1\ncomplaints 0..*',14)
    d.edge(1192,335,870,565,[(1192,400),(945,400),(945,565)],False); d.text(950,410,235,38,'student 1 | 0..* complaints',14)
    d.edge(535,640,375,815,[(465,640),(465,815)],False); d.text(280,700,180,45,'complaint 1\nfeedback 0..1',14)
    d.edge(870,640,1025,815,[(950,640),(950,815)],False); d.text(955,700,175,45,'complaint 1\nevents 0..*',14)
    d.edge(1360,245,1360,815,[(1390,245),(1390,815)],False); d.text(1190,550,185,44,'actor 0..1\nevents 0..*',14)
    d.note(40,930,1320,65,'FK = foreign key; UQ = unique. Category and assigned department are stored separately. Admin reassignment changes the department, not the category.',15)
    d.save('fig-erd')

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

def activity():
    d=Diagram('Complaint lifecycle','Submission flow and the transitions implemented by app.py')
    d.text(45,120,350,35,'1  SUBMIT A COMPLAINT',19,True,TEAL,'left')
    for x,title,body in [(45,'Enter details','Title, description, category'),(380,'Validate','Invalid input returns to form'),(715,'Select category','Compare keyword scores'),(1050,'Save complaint','Priority, SLA, code and events')]:
        d.box(x,170,290,125,title,body)
    for x in (335,670,1005): d.edge(x,232,x+45,232,color=TEAL)
    d.text(70,320,1260,35,'No stronger keyword match? Keep the category selected by the student.',17)
    d.text(45,365,500,35,'2  STATUS TRANSITIONS',19,True,TEAL,'left')
    states=[(45,'Submitted'),(305,'Acknowledged'),(565,'In Progress'),(825,'Resolved'),(1085,'Closed')]
    for x,t in states: d.box(x,470,210,100,t,'',PALE)
    for x in (255,515,775,1035): d.edge(x,520,x+50,520,color=TEAL)
    for x,label in [(255,'acknowledge'),(520,'start'),(780,'resolve'),(1034,'feedback /\nadmin close')]: d.text(x-22,435,100,30,label,14)
    d.edge(150,470,670,470,[(150,410),(670,410)],color=LINE); d.text(315,410,210,30,'start work directly',14)
    d.edge(150,570,930,570,[(150,650),(930,650)],color=LINE); d.text(320,650,220,30,'resolve directly',15)
    d.edge(410,570,930,570,[(410,620),(930,620)],color=LINE); d.text(580,620,220,30,'resolve directly',15)
    d.edge(930,570,670,570,[(930,725),(670,725)],color='#aa6b24'); d.text(695,730,210,30,'student reopens',15,color='#8d5a18')
    d.note(45,795,1310,100,'Resolve requires a remark of at least 10 characters. Reopen requires an eligible student and a reason of at least 10 characters.\nReopen uses a whole-day age check; an invalid timestamp blocks reopening. Admin force-close does not enforce a waiting period.',16)
    d.save('fig-activity')

def klass():
    d=Diagram('Conceptual class / record model','SQLite rows shown as conceptual records, not implemented Python or ORM classes')
    for x,y,t,b in [(40,160,'User','id, role, username\npassword_hash, full_name\nroll_no, phone, status\ndepartment_id [FK]'),(530,160,'Complaint','id, code, student_id [FK]\ncategory_id, department_id [FK]\ntitle, description, status\npriority, routing, sla_due_at'),(1020,160,'Department','id, name\nhead_name, email, location'),(40,510,'Category','id, name\ndepartment_id [FK]\ndefault_priority, keywords'),(530,510,'ComplaintEvent','id, complaint_id [FK]\nevent_type, note\nactor_id [FK], created_at'),(1020,510,'Feedback','id, complaint_id [FK/UQ]\nrating, comment, created_at')]:
        d.table(x,y,340,210,'«record»  '+t,b)
    d.edge(380,260,530,260,arrow=False);d.text(390,215,130,30,'student_id',15)
    d.edge(870,260,1020,260,arrow=False);d.text(875,215,140,30,'department_id',15)
    d.edge(210,510,600,370,[(210,445),(600,445)],False);d.text(300,410,200,30,'category_id',15)
    d.edge(700,370,700,510,arrow=False);d.text(710,410,160,30,'complaint_id',15)
    d.edge(800,370,1190,510,[(800,460),(1190,460)],False);d.text(900,425,200,30,'complaint_id',15)
    d.note(45,780,1310,70,'Selected associations only. For all eight foreign keys and cardinalities, refer to the ERD. app.py and routing.py contain functions, not ORM classes.',16)
    d.save('fig-class')

def deployment():
    d=Diagram('Deployment diagram','Local demonstration setup — not a production deployment')
    d.box(80,235,350,220,'«device» Browser','Same computer or LAN client\nhttp://SERVER:5001')
    d.box(690,190,620,310,'«device» Demo computer','run.py / Flask development server\n0.0.0.0:5001 (default)\nTemplates and static files\nSQLite: app/shikayat_setu.db',PALE)
    d.edge(430,345,690,345,color=TEAL);d.text(500,300,120,35,'HTTP',18,True)
    d.note(100,620,1200,95,'Local address: http://127.0.0.1:5001. LAN access depends on network and firewall settings.\nThere is no external database server or background worker in this demo.')
    d.save('fig-deployment')

def modules():
    d=Diagram('Module hierarchy','Project files and responsibilities — logical groups, not Flask blueprints')
    d.box(530,150,340,125,'run.py','Initialize, seed, launch',PALE)
    blocks=[(35,'app/app.py','Flask routes and helpers\nauth, complaints, queue\nconsole, users, reports'),(380,'app/routing.py','Keyword scoring\nPriority and SLA rules'),(725,'app/database.py','SQLite connection\nSchema setup and demo seed'),(1070,'templates/ + static/','Jinja templates\nCSS and vanilla JavaScript')]
    for x,title,body in blocks:
        d.edge(700,275,x+150,390,[(700,330),(x+150,330)],False,color='#869c9d')
        d.box(x,390,300,180,title,body)
    d.note(70,690,1260,85,'run.py imports the application and database modules. app.py imports routing.py; database.py reads schema.sql.\nFlask renders templates and serves static assets; tests/ exercises the application.')
    d.save('fig-modules')

if __name__=='__main__':
    for func in (architecture,erd,usecase,klass,activity,deployment,modules): func()
    print('Wrote seven editable diagrams to',OUT)
