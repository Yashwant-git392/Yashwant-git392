"""Checks for database relationships represented in the report diagrams."""
import importlib.util
from pathlib import Path


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
        assert output.read_bytes() == (report_dir / "diagrams" / output.name).read_bytes()
        graph = ET.parse(output)
        assert graph.getroot().tag == "mxfile"
        assert graph.findall(".//mxCell[@vertex='1']")
        assert graph.findall(".//mxCell[@edge='1']")
