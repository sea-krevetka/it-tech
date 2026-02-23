
from pathlib import Path
from coursekit.koan import need
from coursekit.variant import load_variant

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / 'weeks' / 'week-08' / 'bench' / 'results.md'

def test_bench_report():
    need(REPORT.exists(), f"Создайте отчет замеров: {REPORT}")
    text = REPORT.read_text()
    need('gRPC' in text and 'REST' in text, "В отчёте должны быть сравнения gRPC и REST.")
    v = load_variant("08")
    need(v['project_code'] in text, "Укажите project_code из варианта в отчёте.")
