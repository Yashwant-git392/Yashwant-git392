"""Checks for database relationships represented in the report diagrams."""
import importlib.util
from pathlib import Path


def test_erd_relationships_match_schema():
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
