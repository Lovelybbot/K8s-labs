import os
import requests
import time
import random
from datetime import datetime

# URL сервисов (через переменные окружения или значения по умолчанию)
APP_URL = os.getenv("APP_URL", "http://host.docker.internal:30080")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://host.docker.internal:30900")
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://host.docker.internal:30300")

def log(message, level="INFO"):
    colors = {
        "INFO": "\033[92m",   # Зелёный
        "WARN": "\033[93m",   # Жёлтый
        "ERROR": "\033[91m",  # Красный
    }
    reset = "\033[0m"
    color = colors.get(level, "")
    print(f"{color}[{datetime.now().strftime('%H:%M:%S')}] [{level}] {message}{reset}")

def call_app_api():
    """Вызов API приложения (генерация трафика)"""
    endpoints = [
        ("POST", "/api/v1/data", {"test": random.randint(1, 100)}),
        ("GET", f"/api/v1/data/{random.randint(1, 50)}", None),
        ("GET", "/api/v1/health", None),
    ]
    
    method, path, data = random.choice(endpoints)
    url = f"{APP_URL}{path}"
    
    try:
        if method == "POST":
            resp = requests.post(url, json=data, timeout=2)
        else:
            resp = requests.get(url, timeout=2)
        
        log(f"{method} {path} -> {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        log(f"Ошибка вызова {method} {path}: {e}", "ERROR")
        return False

def query_prometheus_metric(metric_name):
    """Запрос метрики из Prometheus"""
    try:
        resp = requests.get(f"{PROMETHEUS_URL}/api/v1/query", 
                           params={"query": metric_name}, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            if data['data']['result']:
                value = data['data']['result'][0]['value'][1]
                return float(value)
        return None
    except Exception as e:
        log(f"Ошибка запроса Prometheus: {e}", "ERROR")
        return None

def check_grafana_health():
    """Проверка доступности Grafana"""
    try:
        resp = requests.get(f"{GRAFANA_URL}/api/health", timeout=2)
        if resp.status_code == 200:
            log(f"Grafana доступна: {GRAFANA_URL}", "INFO")
            return True
        else:
            log(f"Grafana ответила с кодом: {resp.status_code}", "WARN")
            return False
    except Exception as e:
        log(f"Grafana недоступна: {e}", "WARN")
        return False

def get_grafana_dashboard_info():
    """Получение информации о дашбордах Grafana (опционально)"""
    try:
        # Запрос к API Grafana (требует аутентификации)
        auth = ("admin", os.getenv("GRAFANA_PASSWORD", "admin123"))
        resp = requests.get(f"{GRAFANA_URL}/api/search", auth=auth, timeout=2)
        if resp.status_code == 200:
            dashboards = resp.json()
            log(f"Найдено дашбордов в Grafana: {len(dashboards)}", "INFO")
            return dashboards
        return None
    except Exception as e:
        log(f"Не удалось получить дашборды Grafana: {e}", "WARN")
        return None

def main():
    log("=" * 50, "INFO")
    log("🚀 Запуск интеграционного клиента", "INFO")
    log("=" * 50, "INFO")
    log(f"📡 API приложения: {APP_URL}", "INFO")
    log(f"📊 Prometheus: {PROMETHEUS_URL}", "INFO")
    log(f"📈 Grafana: {GRAFANA_URL}", "INFO")
    log("=" * 50, "INFO")
    
    # Проверка доступности Grafana
    check_grafana_health()
    
    iteration = 0
    while True:
        iteration += 1
        log(f"--- Итерация {iteration} ---", "INFO")
        
        # 1. Вызываем API приложения (генерация трафика)
        success_count = 0
        for _ in range(5):
            if call_app_api():
                success_count += 1
            time.sleep(0.5)
        
        # 2. Получаем метрики из Prometheus
        metrics_to_check = [
            ('http_requests_total', 'HTTP запросы всего'),
            ('up{job="kubernetes-pods"}', 'Статус подов'),
            ('container_memory_usage_bytes', 'Потребление памяти'),
        ]
        
        for metric, description in metrics_to_check:
            value = query_prometheus_metric(metric)
            if value is not None:
                log(f"📊 {description} ({metric}): {value}", "INFO")
        
        # 3. Статистика
        log(f"✅ Успешных вызовов API: {success_count}/5", "INFO")
        log(f"💤 Пауза 15 секунд...", "INFO")
        
        time.sleep(15)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("👋 Остановка клиента", "INFO")