import importlib.util
from pathlib import Path
from coursekit.koan import need
from coursekit.variant import load_variant

ROOT = Path(__file__).resolve().parents[3]
APP_PATH = ROOT / 'weeks' / 'week-06' / 'app' / 'client.py'


def _load():
    need(APP_PATH.exists(), f"Создайте файл клиента: {APP_PATH}")
    spec = importlib.util.spec_from_file_location('week06_client', APP_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_build_payload():
    mod = _load()
    need(hasattr(mod, 'build_payload'), "Реализуйте функцию build_payload(query, variables).")
    payload = mod.build_payload('query { ping }', {'x': 1})
    need('query' in payload and 'variables' in payload, "Payload должен содержать query и variables.")


def test_client_has_project_code():
    text = APP_PATH.read_text()
    v = load_variant("06")
    need(v['project_code'] in text, "Добавьте project_code из варианта в client.py (например, как константу).")
