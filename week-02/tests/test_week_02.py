
import importlib.util
from pathlib import Path
from fastapi.testclient import TestClient
from coursekit.variant import load_variant
from coursekit.koan import need

WEEK = "02"
ROOT = Path(__file__).resolve().parents[3]
APP_PATH = ROOT / 'weeks' / 'week-02' / 'app' / 'main.py'

def _load_app():
    need(APP_PATH.exists(), f"Создайте приложение FastAPI: {APP_PATH}")
    spec = importlib.util.spec_from_file_location('week02_app', APP_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    need(hasattr(mod, 'app'), "В модуле должен быть объект FastAPI с именем `app`.")
    return mod.app

def _sample_value(t):
    return {
        'str': 'demo',
        'int': 10,
        'float': 1.5,
        'bool': False,
    }[t]

def test_put_and_delete():
    v = load_variant(WEEK)
    resource = v['resource']
    extra = v['extra_field']

    app = _load_app()
    client = TestClient(app)

    payload = {'name': 'Bob', extra['name']: _sample_value(extra['type'])}
    r = client.post(f"/{resource}", json=payload)
    need(r.status_code == 201, "POST должен возвращать 201.")
    rid = r.json()['id']

    updated = {'name': 'Bob Updated', extra['name']: _sample_value(extra['type'])}
    r = client.put(f"/{resource}/{rid}", json=updated)
    need(r.status_code == 200, "PUT должен возвращать 200.")

    r = client.delete(f"/{resource}/{rid}")
    need(r.status_code in (200, 204), "DELETE должен возвращать 200 или 204.")
