
from pathlib import Path
from coursekit.koan import need
from coursekit.variant import load_variant

ROOT = Path(__file__).resolve().parents[3]
CHART = ROOT / 'weeks' / 'week-13' / 'chart' / 'Chart.yaml'
VALUES = ROOT / 'weeks' / 'week-13' / 'chart' / 'values.yaml'
TEMPLATES = ROOT / 'weeks' / 'week-13' / 'chart' / 'templates'
DEPLOY_TPL = TEMPLATES / 'deployment.yaml'
SVC_TPL = TEMPLATES / 'service.yaml'
VALUES_DEV = ROOT / 'weeks' / 'week-13' / 'chart' / 'values-dev.yaml'
VALUES_STAGE = ROOT / 'weeks' / 'week-13' / 'chart' / 'values-stage.yaml'
VALUES_PROD = ROOT / 'weeks' / 'week-13' / 'chart' / 'values-prod.yaml'

def test_helm_chart():
    need(CHART.exists(), f"Создайте Helm Chart: {CHART}")
    text = CHART.read_text()
    need('apiVersion' in text and 'name:' in text, "Chart.yaml должен содержать apiVersion и name.\nПодсказка: это базовые поля Helm.")
    v = load_variant("13")
    need(f"name: {v['k8s']['app']}" in text, "Имя чарта должно соответствовать варианту.\nПодсказка: возьмите k8s.app из варианта.")


def test_templates_and_values():
    need(VALUES.exists(), f"Создайте values.yaml: {VALUES}")
    need(VALUES_DEV.exists(), f"Создайте overrides файл: {VALUES_DEV}\nПодсказка: dev окружение.")
    need(VALUES_STAGE.exists(), f"Создайте overrides файл: {VALUES_STAGE}\nПодсказка: stage окружение.")
    need(VALUES_PROD.exists(), f"Создайте overrides файл: {VALUES_PROD}\nПодсказка: prod окружение.")
    need(TEMPLATES.exists(), f"Создайте каталог templates: {TEMPLATES}")
    need(DEPLOY_TPL.exists(), f"Создайте шаблон Deployment: {DEPLOY_TPL}")
    need(SVC_TPL.exists(), f"Создайте шаблон Service: {SVC_TPL}")
    values_text = VALUES.read_text()
    need('image' in values_text, "В values.yaml должен быть блок image.\nПодсказка: repository и tag.")
    need('replicaCount' in values_text, "В values.yaml должен быть replicaCount.\nПодсказка: число реплик.")
    deploy_text = DEPLOY_TPL.read_text()
    need('{{' in deploy_text, "Deployment шаблон должен содержать Helm-переменные.\nПодсказка: используйте .Values.")
