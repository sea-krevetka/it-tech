import importlib.util
from pathlib import Path
from fastapi.testclient import TestClient
from coursekit.variant import load_variant
from coursekit.koan import need

WEEK = "01"
ROOT = Path(__file__).resolve().parents[3]
APP_PATH = ROOT / 'weeks' / 'week-01' / 'app' / 'main.py'

def _load_app():
    need(APP_PATH.exists(), f"Файл приложения не найден: {APP_PATH}. Убедитесь, что вы создали файл в нужной директории.")
    spec = importlib.util.spec_from_file_location('week01_app', APP_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    need(hasattr(mod, 'app'), "В файле main.py должен быть объект FastAPI с именем `app`.")
    return mod.app

def _sample_value(t):
    return {
        'str': 'demo_string',
        'int': 42,
        'float': 9.99,
        'bool': True,
    }[t]

def test_rest_create_and_get():
    v = load_variant(WEEK)
    resource = v['resource']
    extra = v['extra_field']

    app = _load_app()
    client = TestClient(app)

    payload = {
        'name': 'Test Object',
        extra['name']: _sample_value(extra['type']),
    }

    # Тестируем создание (POST)
    r = client.post(f"/{resource}", json=payload)
    need(r.status_code == 201, f"Метод POST /{resource} должен возвращать статус 201 Created, а вернул {r.status_code}.")
    
    data = r.json()
    need('id' in data, "Ответ сервера на POST запрос должен содержать поле `id` с идентификатором созданного объекта.")

    # Тестируем получение (GET)
    rid = data['id']
    r = client.get(f"/{resource}/{rid}")
    need(r.status_code == 200, f"Метод GET /{resource}/{{id}} должен возвращать статус 200 OK, а вернул {r.status_code}.")
