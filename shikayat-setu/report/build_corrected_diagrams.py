"""Generate editable diagrams.net documents and matching PNGs for the report.

Diagrams are manually specified as model elements in code; they are not claimed
as reverse-engineered UML models or hand-drawn in a particular commercial tool.
"""
from pathlib import Path
import math
import html
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
INK = '#183044'; TEAL = '#147b75'; BG = '#eef7f5'; LINE = '#344b5c'

class Canvas:
    def __init__(self, title, subtitle, w=1400, h=1050):
        self.w, self.h = w, h
        self.page = ET.Element('diagram', name=title, id=title.replace(' ', '-'))
        model = ET.SubElement(self.page, 'mxGraphModel', dx=str(w), dy=str(h), grid='1', gridSize='10', page='1', pageScale='1', pageWidth=str(w), pageHeight=str(h))
        self.root = ET.SubElement(model, 'root')
        ET.SubElement(self.root, 'mxCell', id='0'); ET.SubElement(self.root, 'mxCell', id='1', parent='0')
        self.n=1
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/>']
        self.text(30, 12, w-60, 48, title, 30, True)
        self.text(30, 62, w-60, 32, subtitle, 17, False, '#536875')
    def shape(self, typ, x,y,w,h,label='',size=20,fill='white',bold=False,underline=False):
        self.n+=1
        styles={'rect':'rounded=0;', 'round':'rounded=1;arcSize=12;', 'ellipse':'ellipse;', 'diamond':'rhombus;'}
        style=(styles[typ]+'whiteSpace=wrap;html=0;'+f'fillColor={fill};strokeColor={INK};strokeWidth=2;fontFamily=Arial;fontSize={size};fontColor={INK};fontStyle={1 if bold else 4 if underline else 0};align=center;verticalAlign=middle;')
        cell=ET.SubElement(self.root,'mxCell',id=str(self.n),value=label,style=style,vertex='1',parent='1')
        ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
        if typ in ('rect','round'):
            svg=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{12 if typ=="round" else 0}" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'
        elif typ=='ellipse': svg=f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'
        else: svg=f'<polygon points="{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'
        self.svg.append(svg)
        if label: self._svgtext(x,y,w,h,label,size,bold,INK,underline)
    def _svgtext(self,x,y,w,h,label,size,bold,color,underline=False):
        lines=label.split('\n'); lineheight=size*1.2
        yy=y+h/2 - (len(lines)-1)*lineheight/2 + size*.35
        for line in lines:
            decoration=' text-decoration="underline"' if underline else ''
            self.svg.append(f'<text x="{x+w/2}" y="{yy}" text-anchor="middle" font-family="Arial,DejaVu Sans,sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}"{decoration}>{html.escape(line)}</text>')
            if underline:
                half=max(7,len(line)*size*.27); self.svg.append(f'<line x1="{x+w/2-half}" y1="{yy+4}" x2="{x+w/2+half}" y2="{yy+4}" stroke="{color}" stroke-width="1.5"/>')
            yy+=lineheight
    def text(self,x,y,w,h,label,size=18,bold=False,color=INK,align='center'):
        self.n+=1; cell=ET.SubElement(self.root,'mxCell',id=str(self.n),value=label,style=f'text;html=0;align={align};verticalAlign=middle;whiteSpace=wrap;strokeColor=none;fillColor=none;fontFamily=Arial;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};',vertex='1',parent='1')
        ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
        self._svgtext(x,y,w,h,label,size,bold,color)
    def edge(self,points,arrow=False,dashed=False):
        self.n+=1; c=ET.SubElement(self.root,'mxCell',id=str(self.n),value='',style=f'edgeStyle=none;rounded=0;strokeColor={LINE};strokeWidth=2;endArrow={"open" if arrow else "none"};endFill=0;dashed={1 if dashed else 0};',edge='1',parent='1')
        g=ET.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'})
        ET.SubElement(g,'mxPoint',x=str(points[0][0]),y=str(points[0][1]),**{'as':'sourcePoint'})
        if len(points)>2:
            a=ET.SubElement(g,'Array',**{'as':'points'})
            for x,y in points[1:-1]: ET.SubElement(a,'mxPoint',x=str(x),y=str(y))
        ET.SubElement(g,'mxPoint',x=str(points[-1][0]),y=str(points[-1][1]),**{'as':'targetPoint'})
        pts=' '.join(f'{x},{y}' for x,y in points)
        if dashed:
            # Emit individual dashes because some SVG renderers ignore dasharray.
            for (x1,y1),(x2,y2) in zip(points,points[1:]):
                length=math.hypot(x2-x1,y2-y1)
                if not length: continue
                for start in range(0, int(math.ceil(length)), 14):
                    end=min(start+8,length)
                    sx=x1+(x2-x1)*start/length; sy=y1+(y2-y1)*start/length
                    ex=x1+(x2-x1)*end/length; ey=y1+(y2-y1)*end/length
                    self.svg.append(f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" stroke="{LINE}" stroke-width="2.5"/>')
        else:
            self.svg.append(f'<polyline points="{pts}" fill="none" stroke="{LINE}" stroke-width="2.5"/>')
        if arrow:
            x,y=points[-1]; px,py=points[-2]; ang=math.atan2(y-py,x-px); length=13
            a=(x-length*math.cos(ang-.48),y-length*math.sin(ang-.48)); b=(x-length*math.cos(ang+.48),y-length*math.sin(ang+.48))
            self.svg.append(f'<polyline points="{a[0]},{a[1]} {x},{y} {b[0]},{b[1]}" fill="none" stroke="{LINE}" stroke-width="2.5"/>')
    def actor(self,x,y,w,h):
        # A standard stick-figure actor, recorded as one editable UML actor shape.
        self.n+=1
        cell=ET.SubElement(self.root,'mxCell',id=str(self.n),value='',style=f'shape=umlActor;html=0;fillColor=white;strokeColor={INK};strokeWidth=2;',vertex='1',parent='1')
        ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
        cx=x+w/2; r=w*.19; head=y+r
        self.svg.append(f'<circle cx="{cx}" cy="{head}" r="{r}" fill="white" stroke="{INK}" stroke-width="2.5"/>')
        self.svg.append(f'<path d="M {cx} {head+r} L {cx} {y+h*.69} M {x} {y+h*.45} L {x+w} {y+h*.45} M {cx} {y+h*.69} L {x+w*.12} {y+h} M {cx} {y+h*.69} L {x+w*.88} {y+h}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    def dot(self,cx,cy,final=False):
        self.shape('ellipse',cx-13,cy-13,26,26,'',fill=INK)
        if final: self.shape('ellipse',cx-21,cy-21,42,42,'',fill='none'); self.shape('ellipse',cx-13,cy-13,26,26,'',fill=INK)
    def save_png(self,path):
        import pymupdf
        svg=''.join(self.svg)+'</svg>'
        doc=pymupdf.open(stream=svg.encode(),filetype='svg')
        doc[0].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5), alpha=False).save(str(path)); doc.close()

def attach_connectors(canvas):
    """Attach matching line ends to diagram vertices, retaining fixed waypoints.

    Large swimlane and boundary rectangles and text-only vertices are excluded.
    Explicit connection points preserve the drawn layout when opened in draw.io.
    """
    shapes=[]
    for cell in canvas.root.findall('mxCell'):
        if cell.get('vertex') != '1': continue
        style=cell.get('style','')
        if not style.startswith(('rounded=0;', 'rounded=1;', 'ellipse;', 'rhombus;', 'shape=umlActor;')): continue
        geo=cell.find('mxGeometry')
        x,y,w,h=(float(geo.get(k)) for k in ('x','y','width','height'))
        if w >= 600 or h >= 800: continue
        shapes.append((cell,x,y,w,h))
    for edge in canvas.root.findall("mxCell[@edge='1']"):
        geometry=edge.find('mxGeometry')
        for which in ('source','target'):
            point=geometry.find(f"mxPoint[@as='{which}Point']")
            if point is None: continue
            px,py=float(point.get('x')),float(point.get('y'))
            candidates=[]
            for cell,x,y,w,h in shapes:
                if not (x-1 <= px <= x+w+1 and y-1 <= py <= y+h+1): continue
                distance=min(abs(px-x),abs(px-x-w),abs(py-y),abs(py-y-h))
                if distance <= 1 or (cell.get('style','').startswith('shape=umlActor;') and abs(px-(x+w/2)) < 1):
                    candidates.append((distance,w*h,cell,x,y,w,h))
            if not candidates: continue
            _,_,cell,x,y,w,h=min(candidates,key=lambda item:(item[0],item[1]))
            edge.set(which,cell.get('id'))
            prefix='exit' if which=='source' else 'entry'
            rx=(px-x)/w;ry=(py-y)/h
            edge.set('style',edge.get('style')+f'{prefix}X={rx:.4f};{prefix}Y={ry:.4f};{prefix}Perimeter=0;')

def write_doc(pages,path):
    root=ET.Element('mxfile',host='app.diagrams.net',version='32.6.10',type='device')
    for p in pages:
        attach_connectors(p)
        root.append(p.page)
    ET.indent(root); ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

def entity(c,x,y,name,key,field):
    """Selected actual attributes; full schema is documented in the table section."""
    extra={'Department':'email','Category':'default_priority','User':'username',
           'Complaint':'status','Feedback':'comment','Complaint Event':'created_at'}[name]
    c.shape('rect',x,y,230,70,name,23,BG,True)
    bottom=y>500
    oval_y=y+90 if bottom else y-95
    for offset,label in zip((7,115,223),(key,field,extra)):
        c.edge([(x+offset,y+70 if bottom else y),(x+offset,y+90 if bottom else y-45)])
        c.shape('ellipse',x+offset-52,oval_y,104,50,label,13 if len(label)>10 else 16,underline=label==key)

def rel(c,x,y,label): c.shape('diamond',x,y,170,90,label,18,'#fdf6e8')
def legend(c,text): c.text(35,940,1330,50,text,17,False,'#536875')

def erd_pages():
    from diagram_data import schema_facts
    facts=schema_facts()
    actual={(table, field, fk['table']) for table, data in facts.items() for field, fk in data['foreign_keys'].items()}
    expected={('categories','department_id','departments'), ('users','department_id','departments'), ('complaints','student_id','users'), ('complaints','category_id','categories'), ('complaints','department_id','departments'), ('complaint_events','complaint_id','complaints'), ('complaint_events','actor_id','users'), ('feedback','complaint_id','complaints')}
    if actual != expected or 'complaint_id' not in facts['feedback']['unique'] or facts['users']['columns']['department_id']['notnull'] or facts['complaint_events']['columns']['actor_id']['notnull']:
        raise ValueError('Schema changed; review the conceptual ER diagrams.')
    # Multiplicities use per-entity participation: (min,max) at that entity's end.
    c=Canvas('ER diagram 1 of 3 — Category and assignment','Chen notation • selected attributes • (min,max) relationships per entity')
    entity(c,90,300,'Department','id','name'); entity(c,1080,300,'Category','id','name'); entity(c,585,760,'Complaint','id','code')
    c.edge([(320,335),(615,335)]); c.edge([(785,335),(1080,335)]); rel(c,615,290,'defines')
    c.text(385,300,110,25,'(0,N)',18); c.text(900,300,110,25,'(1,1)',18)
    c.edge([(210,370),(210,625),(615,625)]); c.edge([(700,670),(700,760)]); rel(c,615,580,'assigned to')
    c.text(120,450,100,30,'(0,N)',18); c.text(720,705,100,30,'(1,1)',18)
    c.edge([(1190,370),(1190,625),(1170,625)]); c.edge([(1000,625),(900,625),(900,795),(815,795)]); rel(c,1000,580,'classifies')
    c.text(1200,450,100,30,'(0,N)',18); c.text(820,760,100,30,'(1,1)',18)
    legend(c,'Each complaint has one category and one assigned department; reassignment can change the department independently.')
    a=c
    c=Canvas('ER diagram 2 of 3 — Users and complaints','Chen notation • selected attributes • (min,max) relationships per entity')
    entity(c,95,300,'Department','id','name'); entity(c,1070,300,'User','id','role'); entity(c,585,760,'Complaint','id','code')
    c.edge([(325,335),(615,335)]); c.edge([(785,335),(1070,335)]); rel(c,615,290,'assigned')
    c.text(390,300,100,25,'(0,N)',18); c.text(900,300,100,25,'(0,1)',18)
    c.edge([(114,370),(114,625),(300,625)]); c.edge([(470,625),(500,625),(500,795),(585,795)]); rel(c,300,580,'receives')
    c.text(25,465,100,25,'(0,N)',18); c.text(495,760,100,25,'(1,1)',18)
    c.edge([(1185,370),(1185,625),(1145,625)]); c.edge([(975,625),(900,625),(900,795),(815,795)]); rel(c,975,580,'lodges')
    c.text(1190,465,100,25,'(0,N)',18); c.text(815,760,100,25,'(1,1)',18)
    legend(c,'A complaint stores one submitting user. The student role is enforced by application logic, not by the foreign key alone.')
    b=c
    c=Canvas('ER diagram 3 of 3 — History and feedback','Chen notation • selected attributes • (min,max) relationships per entity')
    entity(c,90,300,'Complaint','id','code'); entity(c,1080,300,'Feedback','id','rating'); entity(c,90,760,'User','id','role'); entity(c,1080,760,'Complaint Event','id','event_type')
    c.edge([(320,335),(615,335)]); c.edge([(785,335),(1080,335)]); rel(c,615,290,'has feedback')
    c.text(390,300,100,25,'(0,1)',18); c.text(900,300,100,25,'(1,1)',18)
    c.edge([(205,370),(205,590),(615,590)]); c.edge([(785,590),(1195,590),(1195,760)]); rel(c,615,545,'records')
    c.text(110,445,100,25,'(0,N)',18); c.text(1200,680,100,25,'(1,1)',18)
    c.edge([(320,795),(615,795)]); c.edge([(785,795),(1080,795)]); rel(c,615,750,'acts on')
    c.text(390,760,100,25,'(0,N)',18); c.text(900,760,100,25,'(0,1)',18)
    legend(c,'An event may have no recorded actor. Feedback is optional and unique for a complaint.')
    return [a,b,c]

def usecase_pages():
    # Actor associations are deliberately plain lines: include/extend is not
    # inferred merely because a route requires a login or validates input.
    groups=[
        ('Student', 'Stored user role: student', ['Register an account','Sign in / sign out','Lodge a complaint','View own complaints','Track with code and roll number','Confirm and rate resolution','Reopen own resolved complaint','Change password'], 'Reopening requires an eligible resolved complaint; public tracking is also available.'),
        ('Officer', 'Stored user role: officer', ['Sign in / sign out','View department queue','Acknowledge a complaint','Start work','Resolve with a remark','Add a remark','Change password'], 'Officer complaint access is restricted to the assigned department.'),
        ('Administrator', 'Stored user role: admin', ['Sign in / sign out','View queue and console','Create officers / toggle users','Reassign department','Escalate priority','Acknowledge / start / resolve','Add a remark','Submit feedback (route only)','Force-close resolved complaint','View and print reports','Track without roll check','Change password'], 'Admin feedback is accepted by the route but has no admin form. Force-close requires Resolved status.'),
        ('Public visitor', 'External actor: not a stored user role', ['Track with code and roll number'], 'Public tracking normally requires a complaint code and the matching roll number.'),
    ]
    pages=[]
    for name,subtitle,uses,note in groups:
        c=Canvas('Use-case diagram — '+name,subtitle,1400,1120)
        c.page.set('name',name);c.page.set('id','usecase-'+name.lower().replace(' ','-'))
        c.shape('rect',350,125,1000,865,'',fill='white')
        c.text(510,135,680,40,'CAMPUS SHIKAYAT SETU',23,True,TEAL)
        # A single actor represents the role; associations are individually
        # attached and ordered to avoid crossing one another.
        gap=61 if len(uses)>9 else 85
        top=190+(750-(len(uses)-1)*gap-52)/2
        center=round(top+(len(uses)-1)*gap/2+26)
        c.actor(115,center-55,85,110)
        c.text(15,center+58,250,30,name,18,True)
        for i,label in enumerate(uses):
            y=round(top+i*gap)
            c.edge([(157.5,center),(650,y+26)])
            c.shape('ellipse',650,y,500,52,label,20,'white')
        c.text(20,1015,1360,75,note,17,False,'#536875')
        pages.append(c)
    return pages

def activity_page():
    c=Canvas('Activity diagram — Lodge a complaint','Scope: student submission, validation, routing and storage',1400,1450)
    # partitions run from top to bottom; all actions are within the correct responsible lane.
    c.shape('rect',60,120,570,1240,'',fill='white'); c.shape('rect',630,120,710,1240,'',fill='white')
    c.text(60,130,570,42,'STUDENT',23,True,TEAL); c.text(630,130,710,42,'FLASK APPLICATION',23,True,TEAL)
    c.dot(345,200); c.edge([(345,213),(345,225)],True)
    c.shape('diamond',315,225,60,45,'',20,'white'); c.edge([(345,270),(345,290)],True)
    c.shape('round',180,290,330,76,'Enter complaint details',21,BG,True)
    c.edge([(345,366),(345,390),(840,390),(840,430)],True)
    c.shape('round',700,430,280,72,'Validate input',21,BG,True)
    c.edge([(840,502),(840,545)],True); c.shape('diamond',755,545,170,100,'Valid?',20,'#fdf6e8')
    c.edge([(755,595),(130,595),(130,247),(315,247)],True); c.text(440,560,140,30,'[invalid]',18,True)
    c.edge([(840,645),(840,695)],True); c.text(845,652,140,30,'[valid]',18,True)
    c.shape('round',655,695,370,76,'Select category by keyword score',19,BG,True)
    c.edge([(840,771),(840,810)],True)
    c.shape('round',655,810,370,76,'Assign priority and deadline',20,BG,True)
    c.edge([(840,886),(840,925)],True)
    c.shape('round',655,925,370,76,'Save complaint and events',20,BG,True)
    c.edge([(840,1001),(840,1040)],True)
    c.shape('round',655,1040,370,76,'Return complaint code',20,BG,True)
    c.edge([(655,1078),(345,1078),(345,1140)],True)
    c.shape('round',180,1140,330,76,'View confirmation',21,BG,True)
    c.edge([(345,1216),(345,1265)],True); c.dot(345,1286,True)
    c.text(80,1370,1240,45,'If no stronger keyword match is found, the student-selected category is retained.',17)
    return c

def operation_activity(title, role, open_action, submit_action, check_action, update_action, finish_action, note):
    """A single request; alternate rejection and stale-update flows terminate separately."""
    c=Canvas('Activity diagram — '+title,'One request by an authorised '+role.lower()+'; rejected requests may be retried',1400,1550)
    c.shape('rect',60,120,570,1300,'',fill='white'); c.shape('rect',630,120,710,1300,'',fill='white')
    c.text(60,130,570,42,role.upper(),23,True,TEAL); c.text(630,130,710,42,'FLASK APPLICATION',23,True,TEAL)
    c.dot(345,200);c.edge([(345,213),(345,245)],True)
    c.shape('round',140,245,410,72,open_action,19,BG,True)
    c.edge([(345,317),(345,350)],True);c.shape('round',140,350,410,72,submit_action,19,BG,True)
    c.edge([(345,422),(345,455),(920,455),(920,480)],True)
    c.shape('round',700,480,440,80,check_action,18,BG,True)
    c.edge([(920,560),(920,600)],True);c.shape('diamond',825,600,190,100,'Eligible?',19,'#fdf6e8')
    c.edge([(825,650),(345,650),(345,745)],True);c.text(430,615,130,30,'[no]',18,True)
    c.shape('round',150,745,390,72,'View rejection message',19,BG,True)
    c.edge([(345,817),(345,865)],True);c.dot(345,886,True)
    c.edge([(920,700),(920,745)],True);c.text(930,705,140,30,'[yes]',18,True)
    c.shape('round',700,745,440,80,update_action,18,BG,True)
    c.edge([(920,825),(920,865)],True);c.shape('diamond',825,865,190,100,'Updated?',19,'#fdf6e8')
    c.edge([(825,915),(345,915),(345,1010)],True);c.text(460,880,140,30,'[changed]',18,True)
    c.shape('round',150,1010,390,72,'View stale-change warning',19,BG,True)
    c.edge([(345,1082),(345,1130)],True);c.dot(345,1151,True)
    c.edge([(920,965),(920,1010)],True);c.text(940,970,150,30,'[updated]',18,True)
    c.shape('round',700,1010,440,80,finish_action,18,BG,True)
    c.edge([(920,1090),(920,1135)],True)
    c.shape('round',700,1135,440,72,'Return success message',19,BG,True)
    c.edge([(920,1207),(920,1250)],True);c.dot(920,1271,True)
    c.text(55,1435,1290,75,note,17,False,'#536875')
    return c

def activity_pages():
    pages=[activity_page()]
    pages.append(operation_activity('Resolve a complaint','Officer / Admin','Open an accessible complaint','Submit resolution remark',
      'Check status and remark length', 'Set Resolved if unchanged', 'Record event and commit',
      'Submitted, Acknowledged or In Progress may be resolved; remark needs 10 characters. Acknowledge/start are optional.'))
    pages.append(operation_activity('Confirm and rate resolution','Student','Open an accessible complaint','Submit rating and optional comment',
      'Check ownership, status and rating', 'Set Closed if unchanged', 'Save feedback and events; commit',
      'Student must own the resolved complaint; rating must be 1 to 5. Admin feedback is supported by the route only.'))
    pages.append(operation_activity('Reopen a complaint','Student','Open own resolved complaint','Submit reopening reason',
      'Check owner, reason and resolution age', 'Set In Progress if unchanged', 'Record reopening event; commit',
      'Reason needs 10 characters; invalid timestamps are rejected. The code checks elapsed whole days, not exactly 168 hours.'))
    pages.append(operation_activity('Force-close a complaint','Administrator','Open an accessible complaint','Request force-close',
      'Check status is Resolved', 'Set Closed if unchanged', 'Record closure event; commit',
      'Admin force-close checks Resolved status; it does not enforce a waiting period.'))
    for i,page in enumerate(pages):
        page.page.set('name',('Submission','Resolution','Feedback','Reopening','Admin closure')[i])
        page.page.set('id','activity-'+str(i+1))
    return pages

def klass_page():
    c=Canvas('Class diagram — Conceptual domain model','Domain types and selected associations; not implemented ORM classes',1400,1050)
    # Diagrams deliberately contain no invented class operations or inheritance.
    boxes=[(55,190,'Department','id : Integer\nname : String\nemail : String'),(545,190,'Category','id : Integer\nname : String\ndefault_priority : String'),(1035,190,'User','id : Integer\nrole : String\nusername : String\nfull_name : String'),(545,650,'Complaint','id : Integer\ncode : String\ntitle : String\npriority : String\nstatus : String'),(55,650,'Feedback','id : Integer\nrating : Integer\ncomment : String'),(1035,650,'ComplaintEvent','id : Integer\nevent_type : String\nnote : String')]
    for x,y,name,body in boxes:
        c.shape('rect',x,y,310,180,'',fill='white'); c.shape('rect',x,y,310,46,name,21,BG,True); c.text(x+20,y+52,270,115,body,18,align='left')
    # Relationship lines and UML end multiplicities.
    for pts in [[(365,260),(545,260)],[(700,370),(700,650)],[(1035,300),(930,300),(930,570),(855,570),(855,690)],[(365,730),(545,730)],[(855,730),(1035,730)]]: c.edge(pts)
    c.text(375,225,75,30,'1',19);c.text(470,225,75,30,'0..*',19)
    c.text(710,385,80,30,'1',19);c.text(710,610,80,30,'0..*',19)
    c.text(945,260,75,30,'1',19);c.text(860,580,80,30,'0..*',19)
    c.text(375,695,75,30,'0..1',19);c.text(465,695,75,30,'1',19)
    c.text(865,695,75,30,'1',19);c.text(955,695,75,30,'0..*',19)
    c.text(30,900,1340,75,'Selected associations only; the ER diagrams show all eight foreign-key relationships.\nUser represents all roles; a complaint is lodged by a student in application logic.',18)
    return c

def klass_supplement():
    c=Canvas('Class diagram — Additional associations','Conceptual domain model • multiplicities correspond to the SQLite constraints')
    boxes=[(80,210,'User','id : Integer\nrole : String'),(1010,210,'Department','id : Integer\nname : String'),(80,670,'ComplaintEvent','id : Integer\nevent_type : String'),(1010,670,'Complaint','id : Integer\ncode : String')]
    for x,y,name,body in boxes:
        c.shape('rect',x,y,310,170,'',fill='white');c.shape('rect',x,y,310,46,name,21,BG,True);c.text(x+10,y+52,290,100,body,19)
    c.edge([(390,295),(1010,295)]);c.text(400,260,90,30,'0..*',19);c.text(900,260,90,30,'0..1',19)
    c.text(545,260,300,30,'assigned department',18)
    c.edge([(235,380),(235,670)]);c.text(245,390,90,30,'0..1',19);c.text(245,630,90,30,'0..*',19)
    c.text(270,495,250,30,'event actor',18)
    c.edge([(1165,380),(1165,670)]);c.text(1175,390,90,30,'1',19);c.text(1175,630,90,30,'0..*',19)
    c.text(900,495,250,30,'assigned complaints',18)
    c.text(35,905,1330,45,'These are the remaining associations; refer also to the first class diagram.',18)
    return c

def deployment_page():
    c=Canvas('Deployment diagram — Local demonstration','Single-computer setup • development server • not production deployment')
    c.shape('rect',85,155,1230,690,'',fill='white'); c.text(110,165,1180,40,'«device» Demo computer',24,True)
    c.shape('rect',135,260,330,330,'',fill=BG); c.text(145,275,310,50,'«executionEnvironment»\nWeb browser',20,True)
    c.shape('rect',765,260,470,330,'',fill=BG); c.text(775,275,450,60,'«executionEnvironment»\nPython / Flask development server',20,True)
    c.shape('rect',825,400,350,72,'«artifact» Application files',20,'white')
    c.shape('rect',825,665,350,72,'«artifact» SQLite database file',19,'white')
    c.edge([(465,440),(765,440)]);c.text(510,400,220,30,'HTTP :5001',20,True)
    c.edge([(1000,472),(1000,665)],True,True);c.text(1020,595,190,35,'«use» sqlite3',18)
    legend(c,'Browser and application can run on the same computer. LAN access is optional and depends on network settings.')
    return c

def modules_page():
    c=Canvas('Module hierarchy — Project structure','Logical grouping of implemented files • lines indicate grouping, not direct imports')
    c.shape('rect',470,140,460,80,'Campus Shikayat Setu',24,BG,True)
    for x in (60,390,720,1050): c.edge([(700,220),(700,285),(x+145,285),(x+145,340)])
    blocks=[(60,'Startup','run.py\nstart_project.py'),(390,'Application','app.py\nrouting.py'),(720,'Data storage','database.py\nschema.sql'),(1050,'Presentation','templates/\nstatic/css/\nstatic/js/')]
    for x,title,body in blocks:
        c.shape('rect',x,340,290,270,'',fill='white');c.shape('rect',x,340,290,55,title,21,BG,True);c.text(x+15,410,260,175,body,20)
    c.text(70,700,1260,80,'app.py defines routes and reports; routing.py contains matching and SLA rules.\ndatabase.py manages SQLite; templates and static assets provide the interface.',19)
    return c

def build(name,out,images=None):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if name=='fig-erd': pages=erd_pages()
    elif name=='fig-usecase': pages=usecase_pages()
    elif name=='fig-activity': pages=activity_pages()
    elif name=='fig-class': pages=[klass_page(),klass_supplement()]
    else: pages=[dict(fig_deployment=deployment_page,fig_modules=modules_page)[name.replace('-','_')]()]
    write_doc(pages,out/(name+'.drawio'))
    if images is not None:
        raise ValueError('Export PNGs with render_drawio.js to match the editable files.')

if __name__=='__main__':
    for name in ('fig-erd','fig-usecase','fig-activity','fig-class','fig-deployment','fig-modules'):
        build(name,HERE/'diagrams')
