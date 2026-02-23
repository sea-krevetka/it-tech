
from pathlib import Path
import yaml
from coursekit.variant import load_variant
from coursekit.koan import need

WEEK = "12"
ROOT = Path(__file__).resolve().parents[3]
DEPLOY = ROOT / 'weeks' / 'week-12' / 'k8s' / 'deployment.yaml'
SERVICE = ROOT / 'weeks' / 'week-12' / 'k8s' / 'service.yaml'

def test_k8s_deployment():
    v = load_variant(WEEK)
    need(DEPLOY.exists(), f"Создайте deployment: {DEPLOY}")
    data = yaml.safe_load(DEPLOY.read_text())
    need(isinstance(data, dict), "Файл должен быть корректным YAML объектом.")
    need(data.get('kind') == 'Deployment', "kind должен быть Deployment.\nПодсказка: apps/v1 + Deployment.")
    need(data.get('metadata', {}).get('name') == v['k8s']['app'], "metadata.name должен совпадать с вариантом.\nПодсказка: используйте k8s.app.")
    text = DEPLOY.read_text()
    need('livenessProbe' in text, "Добавьте livenessProbe в Deployment.\nПодсказка: httpGet /health.")
    need('readinessProbe' in text, "Добавьте readinessProbe в Deployment.\nПодсказка: httpGet /health.")
    need('resources' in text, "Добавьте requests/limits в resources.\nПодсказка: cpu/memory.")
    need('/health' in text, "Используйте /health в probe (httpGet path).")


def test_k8s_service():
    need(SERVICE.exists(), f"Создайте service: {SERVICE}")
    data = yaml.safe_load(SERVICE.read_text())
    need(isinstance(data, dict), "Service должен быть корректным YAML объектом.")
    need(data.get('kind') == 'Service', "kind должен быть Service.\nПодсказка: v1 + Service.")
