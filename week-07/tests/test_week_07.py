
from pathlib import Path
from coursekit.variant import load_variant
from coursekit.koan import need

WEEK = "07"
ROOT = Path(__file__).resolve().parents[3]
PROTO = ROOT / 'weeks' / 'week-07' / 'proto' / 'service.proto'

def test_proto():
    v = load_variant(WEEK)
    need(PROTO.exists(), f"Создайте .proto файл: {PROTO}")
    text = PROTO.read_text()
    need(v['grpc']['service'] in text, "В .proto должен быть сервис из варианта.")
