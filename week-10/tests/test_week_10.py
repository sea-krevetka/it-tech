
from pathlib import Path
from coursekit.koan import need
from coursekit.variant import load_variant

ROOT = Path(__file__).resolve().parents[3]
DOCKERFILE = ROOT / 'weeks' / 'week-10' / 'Dockerfile'
DOCKERIGNORE = ROOT / 'weeks' / 'week-10' / '.dockerignore'
REPORT = ROOT / 'weeks' / 'week-10' / 'report.md'

def test_dockerfile():
    need(DOCKERFILE.exists(), f"Создайте Dockerfile: {DOCKERFILE}")
    text = DOCKERFILE.read_text()
    need('FROM' in text and 'CMD' in text, "Dockerfile должен содержать FROM и CMD.\nПодсказка: сначала базовый образ, затем команда запуска.")
    v = load_variant("10")
    need(f"EXPOSE {v['service']['port']}" in text, "Добавьте EXPOSE с портом из варианта.\nПодсказка: EXPOSE должен совпадать с service.port.")
    need(text.upper().count('FROM') >= 2, "Используйте multi-stage: минимум два FROM.\nПодсказка: один FROM для сборки, второй для запуска.")


def test_dockerignore():
    need(DOCKERIGNORE.exists(), f"Создайте .dockerignore: {DOCKERIGNORE}")
    text = DOCKERIGNORE.read_text()
    need('.venv' in text, "Добавьте .venv в .dockerignore.\nПодсказка: не копируйте локальную виртуальную среду.")
    need('__pycache__' in text, "Добавьте __pycache__ в .dockerignore.\nПодсказка: исключите Python кеши.")


def test_report():
    need(REPORT.exists(), f"Создайте отчет: {REPORT}")
    text = REPORT.read_text().lower()
    need('size' in text or 'размер' in text, "В отчёте укажите размер образа.\nПодсказка: возьмите из вывода docker images.")
    need('layer' in text or 'слой' in text, "В отчёте укажите информацию о слоях.\nПодсказка: опишите, какие шаги дают новые слои.")
