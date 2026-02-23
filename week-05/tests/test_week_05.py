
from pathlib import Path
from coursekit.variant import load_variant
from coursekit.koan import need

WEEK = "05"
ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / 'weeks' / 'week-05' / 'app' / 'schema.graphql'

def test_schema_exists():
    v = load_variant(WEEK)
    need(SCHEMA.exists(), f"Создайте GraphQL схему: {SCHEMA}")
    text = SCHEMA.read_text()
    need(v['graphql']['type'] in text, "В схеме должен быть тип из варианта.")
    need(v['graphql']['mutation'] in text, "В схеме должна быть мутация из варианта.")
