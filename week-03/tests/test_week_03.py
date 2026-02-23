
from pathlib import Path
from coursekit.variant import load_variant
from coursekit.koan import need

WEEK = "03"
ROOT = Path(__file__).resolve().parents[3]
CONF = ROOT / 'weeks' / 'week-03' / 'infra' / 'nginx.conf'

def test_gateway_config():
    v = load_variant(WEEK)
    need(CONF.exists(), f"Создайте конфиг Nginx: {CONF}")
    text = CONF.read_text()
    route = v['gateway']['routes'][0]['path']
    need(route in text, "В конфиге должен быть маршрут для вашего ресурса.")
