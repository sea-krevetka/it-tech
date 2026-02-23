
from pathlib import Path
from coursekit.koan import need
from coursekit.variant import load_variant

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / 'weeks' / 'week-15' / 'analysis.md'

def test_analysis():
    need(REPORT.exists(), f"Создайте анализ: {REPORT}")
    text = REPORT.read_text()
    need('latency' in text.lower(), "Укажите latency в анализе.")
    v = load_variant("15")
    need(v['project_code'] in text, "Укажите project_code из варианта в анализе.")
