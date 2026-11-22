"""Generate editable diagrams.net documents and matching PNGs for the report.

Diagrams are manually specified as model elements in code; they are not claimed
as reverse-engineered UML models or hand-drawn in a particular commercial tool.
"""
from pathlib import Path
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
    def text(self,x,y,w,h,label,size=18,bold=False,color=INK):
        self.n+=1; cell=ET.SubElement(self.root,'mxCell',id=str(self.n),value=label,style=f'text;html=0;align=center;verticalAlign=middle;whiteSpace=wrap;strokeColor=none;fillColor=none;fontFamily=Arial;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};',vertex='1',parent='1')
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
        dash = ' stroke-dasharray="8 6"' if dashed else ''
        self.svg.append(f'<polyline points="{pts}" fill="none" stroke="{LINE}" stroke-width="2.5"{dash}/>')
        if arrow:
            import math
            x,y=points[-1]; px,py=points[-2]; ang=math.atan2(y-py,x-px); length=13
            a=(x-length*math.cos(ang-.48),y-length*math.sin(ang-.48)); b=(x-length*math.cos(ang+.48),y-length*math.sin(ang+.48))
            self.svg.append(f'<polyline points="{a[0]},{a[1]} {x},{y} {b[0]},{b[1]}" fill="none" stroke="{LINE}" stroke-width="2.5"/>')
    def dot(self,cx,cy,final=False):
        self.shape('ellipse',cx-13,cy-13,26,26,'',fill=INK)
        if final: self.shape('ellipse',cx-21,cy-21,42,42,'',fill='none'); self.shape('ellipse',cx-13,cy-13,26,26,'',fill=INK)
    def save_png(self,path):
        import pymupdf
        svg=''.join(self.svg)+'</svg>'
        doc=pymupdf.open(stream=svg.encode(),filetype='svg')
        doc[0].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5), alpha=False).save(str(path)); doc.close()

def write_doc(pages,path):
    root=ET.Element('mxfile',host='app.diagrams.net',version='32.6.10',type='device')
    for p in pages: root.append(p.page)
    ET.indent(root); ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

def entity(c,x,y,name,key,field):
    c.shape('rect',x,y,230,70,name,23,BG,True)
    if y > 500:
        c.edge([(x+25,y+70),(x+25,y+90)]); c.edge([(x+205,y+70),(x+205,y+90)])
        oval_y=y+90
    else:
        c.edge([(x+25,y),(x+25,y-45)]); c.edge([(x+205,y),(x+205,y-45)])
        oval_y=y-95
    c.shape('ellipse',x-50,oval_y,150,50,key,18,underline=True)
    c.shape('ellipse',x+130,oval_y,150,50,field,18)

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

def klass_page():
    c=Canvas('Class diagram — Conceptual domain model','Domain types and selected associations; not implemented ORM classes',1400,1050)
    # Diagrams deliberately contain no invented class operations or inheritance.
    boxes=[(55,190,'Department','id : Integer\nname : String'),(545,190,'Category','id : Integer\nname : String'),(1035,190,'User','id : Integer\nrole : String'),(545,650,'Complaint','id : Integer\ncode : String\nstatus : String'),(55,650,'Feedback','id : Integer\nrating : Integer'),(1035,650,'ComplaintEvent','id : Integer\neventType : String')]
    for x,y,name,body in boxes:
        c.shape('rect',x,y,310,180,'',fill='white'); c.shape('rect',x,y,310,46,name,21,BG,True); c.text(x+10,y+52,290,115,body,19)
    # Relationship lines and UML end multiplicities.
    for pts in [[(365,260),(545,260)],[(700,370),(700,650)],[(1035,300),(930,300),(930,570),(855,570),(855,690)],[(365,730),(545,730)],[(855,730),(1035,730)]]: c.edge(pts)
    c.text(375,225,75,30,'1',19);c.text(470,225,75,30,'0..*',19)
    c.text(710,385,80,30,'1',19);c.text(710,610,80,30,'0..*',19)
    c.text(945,260,75,30,'1',19);c.text(860,580,80,30,'0..*',19)
    c.text(375,695,75,30,'0..1',19);c.text(465,695,75,30,'1',19)
    c.text(865,695,75,30,'1',19);c.text(955,695,75,30,'0..*',19)
    c.text(30,900,1340,75,'Selected associations only; the ER diagrams show all eight foreign-key relationships.\nUser represents all roles; a complaint is lodged by a student in application logic.',18)
    return c

def deployment_page():
    c=Canvas('Deployment diagram — Local demonstration','Single-computer setup • development server • not production deployment')
    c.shape('rect',85,155,1230,690,'',fill='white'); c.text(110,165,1180,40,'«device» Demo computer',24,True)
    c.shape('rect',135,260,330,330,'',fill=BG); c.text(145,275,310,50,'«executionEnvironment»\nWeb browser',20,True)
    c.shape('rect',765,260,470,460,'',fill=BG); c.text(775,275,450,60,'«executionEnvironment»\nPython / Flask development server',20,True)
    c.shape('rect',825,400,350,72,'«artifact» Application files',20,'white')
    c.shape('rect',825,530,350,72,'«artifact» SQLite database file',19,'white')
    c.edge([(465,440),(765,440)]);c.text(510,400,220,30,'HTTP :5001',20,True)
    c.edge([(1000,472),(1000,530)],True,True);c.text(1020,485,190,35,'«access» sqlite3',18)
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
    pages=erd_pages() if name=='fig-erd' else [dict(fig_activity=activity_page,fig_class=klass_page,fig_deployment=deployment_page,fig_modules=modules_page)[name.replace('-','_')]()]
    write_doc(pages,out/(name+'.drawio'))
    if images is not None:
        images=Path(images);images.mkdir(parents=True,exist_ok=True)
        for i,page in enumerate(pages):
            filename=(('fig-erd.png' if i == 0 else f'fig-erd-{chr(97+i)}.png') if name=='fig-erd' else name+'.png')
            page.save_png(images/filename)

if __name__=='__main__':
    for name in ('fig-erd','fig-activity','fig-class','fig-deployment','fig-modules'):
        build(name,HERE/'diagrams',HERE/'images')
