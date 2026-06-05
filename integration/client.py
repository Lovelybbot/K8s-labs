import os
import sys
import platform
import requests
import time
import random
from datetime import datetime

def get_service_url(service_name, default_port):
    """Определяет правильный URL для сервиса в зависимости от ОС"""
    env_url = os.getenv(f"{service_name}_URL")
    if env_url:
        return env_url
    
    system = platform.system()
    
    # Проверяем, запущены ли мы внутри контейнера
    in_container = os.path.exists('/.dockerenv')
    
    if in_container:
        # Внутри Docker контейнера
        if system == "Linux":
            # Для Linux пробуем host.docker.internal, если не работает — localhost
            try:
                import socket
                socket.gethostbyname("host.docker.internal")
                return f"http://host.docker.internal:{default_port}"
            except:
                return f"http://localhost:{default_port}"
        else:
            # Windows/macOS
            return f"http://host.docker.internal:{default_port}"
    else:
        # На хосте (не в контейнере)
        return f"http://localhost:{default_port}"

# Определяем URL сервисов
APP_URL = get_service_url("APP", 30080)
PROMETHEUS_URL = get_service_url("PROMETHEUS", 30900)
GRAFANA_URL = get_service_url("GRAFANA", 30300)

def log(message, level="INFO"):
    colors = {
        "INFO": "\033[92m",
        "WARN": "\033[93m",
        "ERROR": "\033[91m",
    }
    reset = "\033[0m"
    color = colors.get(level, "")
    print(f"{color}[{datetime.now().strftime('%H:%M:%S')}] [{level}] {message}{reset}")

def call_app_api():
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
        log(f"Ошибка: {e}", "ERROR")
        return False

def query_prometheus_metric(metric_name):
    try:
        resp = requests.get(f"{PROMETHEUS_URL}/api/v1/query", 
                           params={"query": metric_name}, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            if data['data']['result']:
                return float(data['data']['result'][0]['value'][1])
        return None
    except Exception as e:
        log(f"Ошибка Prometheus: {e}", "ERROR")
        return None

def main():
    log(f"API URL: {APP_URL}")
    log(f"Prometheus URL: {PROMETHEUS_URL}")
    log(f"Grafana URL: {GRAFANA_URL}")
    log(f"Platform: {platform.system()}")
    
    iteration = 0
    while True:
        iteration += 1
        log(f"--- Итерация {iteration} ---")
        
        for _ in range(3):
            call_app_api()
            time.sleep(1)
        
        value = query_prometheus_metric("http_requests_total")
        if value is not None:
            log(f"http_requests_total: {value}")
        
        time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Остановка клиента")