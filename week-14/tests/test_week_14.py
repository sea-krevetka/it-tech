
from pathlib import Path
from coursekit.koan import need
from coursekit.variant import load_variant

ROOT = Path(__file__).resolve().parents[3]
CI = ROOT / '.github' / 'workflows' / 'ci.yml'

def test_ci_exists():
    need(CI.exists(), f"CI workflow должен быть в {CI}")
    text = CI.read_text()
    v = load_variant("14")
    need(v['project_code'] in text, "Укажите project_code из варианта в CI (например, как IMAGE_NAME).\nПодсказка: возьмите project_code из JSON варианта.")
    need('cache:' in text and 'pip' in text, "Настройте кеширование pip в CI.\nПодсказка: используйте setup-python cache: pip.")
    need('docker build' in text or 'docker/build-push-action' in text, "CI должен собирать Docker-образ.\nПодсказка: docker build или build-push-action.")
    need('pytest' in text or 'make test' in text, "CI должен запускать тесты.\nПодсказка: pytest или make test.")
    need('upload-artifact' in text, "CI должен публиковать артефакты.\nПодсказка: actions/upload-artifact.")
