
from pathlib import Path
from coursekit.koan import need
from coursekit.variant import load_variant

ROOT = Path(__file__).resolve().parents[3]
CHECKLIST = ROOT / 'weeks' / 'week-16' / 'checklist.md'
AUDIT = ROOT / 'weeks' / 'week-16' / 'audit.md'

def test_security_docs():
    need(CHECKLIST.exists(), f"Создайте checklist: {CHECKLIST}")
    need(AUDIT.exists(), f"Создайте audit: {AUDIT}")
    text = AUDIT.read_text()
    v = load_variant("16")
    need(v['project_code'] in text, "Укажите project_code из варианта в audit.md.")
