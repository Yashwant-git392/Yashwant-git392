"""Checks for database relationships represented in the report diagrams."""
import importlib.util
from pathlib import Path


def read_diagram(path):
    """Compare UTF-8 text with universal newlines across operating systems."""
    return path.read_text(encoding="utf-8")


def test_diagram_comparison_tolerates_windows_line_endings(tmp_path):
    unix = tmp_path / "unix.drawio"
    windows = tmp_path / "windows.drawio"
    unix.write_bytes(b"<mxfile>\n<diagram/>\n</mxfile>")
    windows.write_bytes(b"<mxfile>\r\n<diagram/>\r\n</mxfile>")
    assert read_diagram(unix) == read_diagram(windows)
    windows.write_bytes(b"<mxfile>\r\n<changed/>\r\n</mxfile>")
    assert read_diagram(unix) != read_diagram(windows)


def test_erd_relationships_match_schema(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parent.parent / "report" / "diagram_data.py"
    spec = importlib.util.spec_from_file_location("diagram_data", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    facts = module.schema_facts()
    relationships = {(table, field, fk["table"]) for table, info in facts.items()
                     for field, fk in info["foreign_keys"].items()}
    assert relationships == {
        ("categories", "department_id", "departments"),
        ("users", "department_id", "departments"),
        ("complaints", "student_id", "users"),
        ("complaints", "category_id", "categories"),
        ("complaints", "department_id", "departments"),
        ("complaint_events", "complaint_id", "complaints"),
        ("complaint_events", "actor_id", "users"),
        ("feedback", "complaint_id", "complaints"),
    }
    assert not facts["users"]["columns"]["department_id"]["notnull"]
    assert not facts["complaint_events"]["columns"]["actor_id"]["notnull"]
    assert facts["feedback"]["columns"]["complaint_id"]["notnull"]
    assert "complaint_id" in facts["feedback"]["unique"]

    # Check that generated native documents remain in sync with the checked-in
    # files and contain editable vertices and connectors rather than flat images.
    import xml.etree.ElementTree as ET
    report_dir = path.parent
    monkeypatch.syspath_prepend(str(report_dir))
    spec = importlib.util.spec_from_file_location("build_drawio", report_dir / "build_drawio.py")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    monkeypatch.setattr(generator, "OUT", tmp_path)
    for build in (generator.architecture, generator.erd, generator.usecase, generator.klass,
                  generator.activity, generator.deployment, generator.modules):
        build()
    assert len(list(tmp_path.glob("*.drawio"))) == 7
    for output in tmp_path.glob("*.drawio"):
        assert read_diagram(output) == read_diagram(report_dir / "diagrams" / output.name)
        graph = ET.parse(output)
        assert graph.getroot().tag == "mxfile"
        assert graph.findall(".//mxCell[@vertex='1']")
        assert graph.findall(".//mxCell[@edge='1']")


def test_usecase_has_separate_editable_actor_pages():
    import xml.etree.ElementTree as ET
    project = Path(__file__).resolve().parent.parent
    root = ET.parse(project / 'report' / 'diagrams' / 'fig-usecase.drawio').getroot()
    pages = root.findall('diagram')
    assert [p.get('name') for p in pages] == ['Student', 'Officer', 'Administrator', 'Public visitor']
    for page, expected_uses in zip(pages, (8, 7, 12, 1)):
        cells = page.findall('.//mxCell')
        actors = [c for c in cells if 'shape=umlActor' in c.get('style', '')]
        uses = [c for c in cells if c.get('style', '').startswith('ellipse;')]
        edges = [c for c in cells if c.get('edge') == '1']
        assert len(actors) == 1 and len(uses) == expected_uses and len(edges) == expected_uses
        assert all(e.get('style', '').find('endArrow=none') >= 0 for e in edges)
        # The actor sits outside the system boundary; each use case is inside it.
        boundary = next(c for c in cells if c.get('style', '').startswith('rounded=0;') and c.find('mxGeometry').get('x') == '350')
        left = float(boundary.find('mxGeometry').get('x'))
        actor = actors[0].find('mxGeometry')
        assert float(actor.get('x')) + float(actor.get('width')) < left
        assert all(float(c.find('mxGeometry').get('x')) > left for c in uses)
    public_values = [c.get('value', '') for c in pages[-1].findall('.//mxCell')]
    assert 'External actor: not a stored user role' in public_values


def test_chen_relationships_and_activity_are_editable_and_connected():
    import xml.etree.ElementTree as ET
    base = Path(__file__).resolve().parent.parent / 'report' / 'diagrams'
    pages = ET.parse(base / 'fig-erd.drawio').getroot().findall('diagram')
    assert len(pages) == 3
    expected = [
        {'defines', 'assigned to', 'classifies'},
        {'assigned', 'receives', 'lodges'},
        {'has feedback', 'records', 'acts on'},
    ]
    for page, names in zip(pages, expected):
        cells = page.findall('.//mxCell')
        diamonds = [c for c in cells if c.get('style', '').startswith('rhombus;')]
        assert {c.get('value') for c in diamonds} == names
        edges = [c for c in cells if c.get('edge') == '1']
        for diamond in diamonds:
            geo = diamond.find('mxGeometry')
            x,y,w,h = (float(geo.get(k)) for k in ('x','y','width','height'))
            ports = {(x+w/2,y), (x+w,y+h/2), (x+w/2,y+h), (x,y+h/2)}
            hits = 0
            for edge in edges:
                for point in edge.findall('mxGeometry/mxPoint'):
                    if point.get('as') in ('sourcePoint', 'targetPoint') and (float(point.get('x')), float(point.get('y'))) in ports:
                        hits += 1
            assert hits == 2, (diamond.get('value'), hits)
        keys = [c for c in cells if c.get('value') == 'id' and c.get('style', '').startswith('ellipse;')]
        assert keys and all('fontStyle=4;' in c.get('style', '') for c in keys)
    activity = ET.parse(base / 'fig-activity.drawio').getroot()
    pages = activity.findall('diagram')
    assert [p.get('name') for p in pages] == ['Submission', 'Resolution', 'Feedback', 'Reopening', 'Admin closure']
    values = {c.get('value') for c in pages[0].findall('.//mxCell')}
    assert {'[invalid]', '[valid]', 'Validate input', 'Save complaint and events'} <= values
    for page in pages:
        cells = page.findall('.//mxCell')
        assert len([c for c in cells if c.get('style', '').startswith('rhombus;')]) == 2
        assert all('fork' not in c.get('style', '').lower() for c in cells)
    for page, expected_action in zip(pages[1:], ('Set Resolved if unchanged', 'Set Closed if unchanged', 'Set In Progress if unchanged', 'Set Closed if unchanged')):
        values = {c.get('value') for c in page.findall('.//mxCell')}
        assert {expected_action, '[no]', '[yes]', '[changed]', '[updated]'} <= values
    classes = ET.parse(base / 'fig-class.drawio').getroot().findall('diagram')
    assert len(classes) == 2
    extra = {c.get('value') for c in classes[1].findall('.//mxCell')}
    assert {'assigned department', 'event actor', 'assigned complaints'} <= extra
