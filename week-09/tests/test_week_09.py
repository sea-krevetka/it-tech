
from pathlib import Path
from coursekit.koan import need
from coursekit.variant import load_variant

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / 'weeks' / 'week-09' / 'client' / 'index.html'

def test_webrtc_client():
    need(INDEX.exists(), f"Создайте клиент: {INDEX}")
    text = INDEX.read_text()
    need('RTCPeerConnection' in text, "В клиенте должен использоваться RTCPeerConnection.")
    v = load_variant("09")
    need(v['project_code'] in text, "Укажите project_code из варианта в HTML (например, в title).")
