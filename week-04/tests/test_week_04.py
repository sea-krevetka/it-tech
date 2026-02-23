
import importlib.util
from pathlib import Path
from coursekit.koan import need_eq, need
from coursekit.variant import load_variant

ROOT = Path(__file__).resolve().parents[3]
APP_PATH = ROOT / 'weeks' / 'week-04' / 'app' / 'saga.py'

def _load():
    need(APP_PATH.exists(), f"Создайте файл: {APP_PATH}")
    spec = importlib.util.spec_from_file_location('week04_saga', APP_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_saga_transitions():
    mod = _load()
    need(hasattr(mod, 'next_state'), "Определите функцию next_state(state, event).")
    need_eq(mod.next_state('NEW', 'PAY_OK'), 'PAID', "Состояние NEW + PAY_OK должно переходить в PAID.")
    need_eq(mod.next_state('NEW', 'PAY_FAIL'), 'CANCELLED', "Состояние NEW + PAY_FAIL -> CANCELLED.")


def test_saga_notes_contains_project_code():
    notes = ROOT / 'weeks' / 'week-04' / 'saga.md'
    need(notes.exists(), f"Добавьте описание: {notes}")
    text = notes.read_text()
    v = load_variant("04")
    need(v['project_code'] in text, "Укажите project_code из варианта в описании саги.")
