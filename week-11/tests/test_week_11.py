
from pathlib import Path
from coursekit.koan import need
from coursekit.variant import load_variant

ROOT = Path(__file__).resolve().parents[3]
COMPOSE = ROOT / 'weeks' / 'week-11' / 'docker-compose.yml'

def test_compose():
    need(COMPOSE.exists(), f"Создайте docker-compose.yml: {COMPOSE}")
    text = COMPOSE.read_text()
    need('services:' in text, "В compose должен быть раздел services.\nПодсказка: это корневой блок.")
    v = load_variant("11")
    need(v['service']['name'] in text, "В compose должен быть сервис с именем из варианта.\nПодсказка: имя сервиса в YAML должно совпадать.")
    need('healthcheck:' in text, "Добавьте healthcheck для основного сервиса.\nПодсказка: test/interval/timeout.")
    need('depends_on:' in text, "Используйте depends_on для порядка запуска.\nПодсказка: gateway зависит от app.")
    need('networks:' in text, "Добавьте пользовательскую сеть.\nПодсказка: общий network для всех сервисов.")
