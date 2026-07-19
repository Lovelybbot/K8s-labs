#!/usr/bin/env python3
"""
Универсальный запускатор Kubernetes Lab
Работает на Windows, Linux и macOS
"""

import os
import sys
import platform
import subprocess
import time
import json
import tempfile
import argparse

class Colors:
    """Цвета для вывода в терминале"""
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def print_color(text, color=Colors.CYAN):
    """Вывод цветного текста"""
    print(f"{color}{text}{Colors.RESET}")

def detect_environment():
    """Определяет окружение: Docker Desktop или Minikube"""
    system = platform.system()
    
    # Windows с Docker Desktop
    if system == "Windows":
        return "docker-desktop"
    
    # Linux с Minikube
    if system == "Linux":
        success, stdout, stderr = run_command("minikube status")
        if success and "Running" in stdout:
            return "minikube"
        return "minikube-needs-start"
    
    return "unknown"

def run_command(cmd, shell=False):
    """Выполнение команды и возврат результата"""
    try:
        if isinstance(cmd, str):
            if shell:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            else:
                # Разбиваем строку на аргументы
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_dependencies():
    """Проверка и установка необходимых Python пакетов"""
    print_color("\n[0/8] Проверка зависимостей...", Colors.YELLOW)
    
    try:
        import requests
        print_color("ГОТОВО: Все зависимости установлены", Colors.GREEN)
        return True
    except ImportError:
        print_color("Установка необходимых пакетов (requests)...", Colors.YELLOW)
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "requests"], 
                          capture_output=True, check=True)
            print_color("ГОТОВО: Пакеты установлены", Colors.GREEN)
            return True
        except Exception as e:
            print_color(f"ОШИБКА: Не удалось установить пакеты: {e}", Colors.RED)
            print_color("Пожалуйста, выполните: pip install requests", Colors.YELLOW)
            return False

def check_docker():
    """Проверка работы Docker"""
    print_color("\n[1/8] Проверка Docker...", Colors.YELLOW)
    success, stdout, stderr = run_command("docker info")
    if success:
        print_color("ГОТОВО: Docker работает", Colors.GREEN)
        return True
    else:
        print_color("ОШИБКА: Docker не запущен!", Colors.RED)
        if platform.system() == "Windows":
            print_color("Пожалуйста, запустите Docker Desktop", Colors.YELLOW)
        else:
            print_color("Пожалуйста, запустите Docker: sudo systemctl start docker", Colors.YELLOW)
        return False

def check_kubernetes():
    """Проверка доступности Kubernetes"""
    print_color("\n[2/8] Проверка Kubernetes...", Colors.YELLOW)
    
    env = detect_environment()
    
    if env == "docker-desktop":
        success, stdout, stderr = run_command("kubectl cluster-info")
        if success:
            print_color("ГОТОВО: Kubernetes (Docker Desktop) работает", Colors.GREEN)
            return True
    
    elif env == "minikube":
        print_color("ГОТОВО: Minikube уже запущен", Colors.GREEN)
        return True
    
    elif env == "minikube-needs-start":
        print_color("Запуск Minikube...", Colors.YELLOW)
        run_command("minikube start --driver=docker")
        print_color("ГОТОВО: Minikube запущен", Colors.GREEN)
        return True
    
    print_color("ОШИБКА: Kubernetes недоступен!", Colors.RED)
    return False

def get_docker_host():
    """Получение адреса хоста Docker для разных платформ"""
    system = platform.system()
    if system == "Windows":
        return "host.docker.internal"
    elif system == "Linux":
        if os.path.exists('/.dockerenv'):
            return "host.docker.internal"
        return "localhost"
    elif system == "Darwin":
        return "host.docker.internal"
    else:
        return "localhost"

def deploy_app():
    """Деплой приложения в Kubernetes.

    Образ не собирается локально: манифест ссылается на
    ghcr.io/lovelybbot/k8s-labs/myapp, который собирает и публикует
    CI-пайплайн (.github/workflows/ci.yml) при каждом push в main.
    Кластер сам скачивает образ из реестра.
    """
    print_color("\n[3/8] Деплой приложения в Kubernetes...", Colors.YELLOW)

    # Применяем манифесты
    run_command("kubectl apply -f ./k8s/app-deployment.yaml")
    run_command("kubectl apply -f ./k8s/app-service.yaml")

    print_color("Ожидание раскатки (образ скачивается из GHCR)...", Colors.YELLOW)
    success, stdout, stderr = run_command("kubectl rollout status deployment/myapp --timeout=180s")
    if success:
        print_color("ГОТОВО: Приложение запущено", Colors.GREEN)
        return True
    else:
        print_color("Предупреждение: Поды могут быть ещё не готовы", Colors.YELLOW)
        print_color("Проверьте: kubectl get pods -l app=myapp", Colors.YELLOW)
        return True

def install_monitoring():
    """Установка Prometheus и Grafana"""
    print_color("\n[4/8] Установка Prometheus + Grafana...", Colors.YELLOW)
    
    success, stdout, stderr = run_command("helm list -n monitoring")
    if "monitoring" in stdout:
        print_color("ГОТОВО: Мониторинг уже установлен", Colors.GREEN)
        return True
    
    run_command("helm repo add prometheus-community https://prometheus-community.github.io/helm-charts")
    run_command("helm repo update")
    
    cmd = ('helm install monitoring prometheus-community/kube-prometheus-stack '
           '--namespace monitoring --create-namespace '
           '--set grafana.service.type=NodePort '
           '--set grafana.service.nodePort=30300 '
           '--set grafana.adminPassword=admin123 '
           '--set prometheus.service.type=NodePort '
           '--set prometheus.service.nodePort=30900')
    
    success, stdout, stderr = run_command(cmd)
    if success:
        print_color("Ожидание запуска мониторинга (120 секунд)...", Colors.YELLOW)
        time.sleep(120)
        print_color("ГОТОВО: Мониторинг установлен", Colors.GREEN)
        return True
    else:
        print_color(f"Предупреждение: {stderr}", Colors.YELLOW)
        return True

def create_podmonitor():
    """Создание PodMonitor для myapp"""
    print_color("\n[5/8] Создание PodMonitor...", Colors.YELLOW)
    
    run_command("kubectl delete podmonitor myapp-podmonitor -n monitoring --ignore-not-found")
    
    pm_yaml = """apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: myapp-podmonitor
  namespace: monitoring
  labels:
    release: monitoring
spec:
  selector:
    matchLabels:
      app: myapp
  namespaceSelector:
    matchNames:
    - default
  podMetricsEndpoints:
  - port: http
    path: /metrics
    interval: 15s
"""
    
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, "podmonitor_temp.yaml")
    
    with open(temp_file, "w") as f:
        f.write(pm_yaml)
    
    try:
        success, stdout, stderr = run_command(f'kubectl apply -f "{temp_file}"')
        if success:
            print_color("ГОТОВО: PodMonitor создан", Colors.GREEN)
            return True
        else:
            print_color(f"Предупреждение: {stderr}", Colors.YELLOW)
            return True
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def start_client():
    """Запуск интеграционного клиента"""
    print_color("\n[6/8] Запуск интеграционного клиента...", Colors.YELLOW)
    
    run_command("docker-compose down")
    
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_compose = os.path.join(temp_dir, "docker-compose-temp.yml")
    
    docker_host = get_docker_host()
    
    compose_content = f"""services:
  integration-client:
    build: ./integration
    container_name: api-integration-client
    environment:
      - APP_URL=http://{docker_host}:30080
      - PROMETHEUS_URL=http://{docker_host}:30900
      - GRAFANA_URL=http://{docker_host}:30300
      - GRAFANA_PASSWORD=admin123
    restart: unless-stopped
    stdin_open: true
    tty: true
    extra_hosts:
      - "host.docker.internal:host-gateway"
"""
    
    with open(temp_compose, "w") as f:
        f.write(compose_content)
    
    try:
        success, stdout, stderr = run_command(f'docker-compose -f "{temp_compose}" up -d')
        if success:
            print_color("ГОТОВО: Клиент запущен", Colors.GREEN)
            return True
        else:
            print_color(f"Предупреждение: {stderr}", Colors.YELLOW)
            return True
    finally:
        if os.path.exists(temp_compose):
            os.remove(temp_compose)

def setup_grafana():
    """Настройка Grafana: добавление источника данных и дашборда"""
    print_color("\n[7/8] Настройка Grafana...", Colors.YELLOW)
    
    import requests
    
    print_color("Ожидание готовности Grafana...", Colors.YELLOW)
    
    grafana_url = "http://localhost:30300"
    max_retries = 30
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{grafana_url}/api/health", timeout=5)
            if response.status_code == 200:
                print_color("Grafana готова!", Colors.GREEN)
                break
        except:
            pass
        time.sleep(2)
    else:
        print_color("Предупреждение: Grafana может быть ещё не готова", Colors.YELLOW)
    
    time.sleep(5)
    
    grafana_user = "admin"
    grafana_password = "admin123"
    
    session = requests.Session()
    
    try:
        login_url = f"{grafana_url}/login"
        auth_data = {"user": grafana_user, "password": grafana_password}
        session.post(login_url, json=auth_data)
        
        datasources_url = f"{grafana_url}/api/datasources"
        response = session.get(datasources_url)
        
        prometheus_exists = False
        if response.status_code == 200:
            datasources = response.json()
            for ds in datasources:
                if ds.get("name") == "Prometheus":
                    prometheus_exists = True
                    break
        
        if not prometheus_exists:
            datasource_payload = {
                "name": "Prometheus",
                "type": "prometheus",
                "url": "http://monitoring-kube-prometheus-prometheus:9090",
                "access": "proxy",
                "isDefault": True,
                "basicAuth": False,
                "jsonData": {
                    "timeInterval": "15s",
                    "httpMethod": "POST"
                }
            }
            
            response = session.post(datasources_url, json=datasource_payload)
            if response.status_code in [200, 409]:
                print_color("ГОТОВО: Источник данных Prometheus добавлен", Colors.GREEN)
            else:
                print_color(f"Предупреждение: Не удалось добавить источник: {response.text}", Colors.YELLOW)
        else:
            print_color("ГОТОВО: Источник данных Prometheus уже существует", Colors.GREEN)
        
        dashboard_json = {
            "dashboard": {
                "title": "Мониторинг API приложения",
                "tags": ["kubernetes", "fastapi", "prometheus"],
                "timezone": "browser",
                "refresh": "30s",
                "time": {"from": "now-1h", "to": "now"},
                "panels": [
                    {
                        "id": 1,
                        "title": "Всего запросов",
                        "type": "stat",
                        "gridPos": {"h": 4, "w": 4, "x": 0, "y": 0},
                        "targets": [{
                            "expr": "sum(http_requests_total)",
                            "legendFormat": "Всего"
                        }],
                        "options": {
                            "colorMode": "value",
                            "graphMode": "none",
                            "justifyMode": "center"
                        },
                        "fieldConfig": {
                            "defaults": {
                                "unit": "short",
                                "decimals": 0,
                                "color": {"mode": "thresholds"},
                                "thresholds": {
                                    "steps": [
                                        {"color": "green", "value": None}
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": 2,
                        "title": "RPS (запросов в секунду)",
                        "type": "timeseries",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4},
                        "targets": [{
                            "expr": "sum(rate(http_requests_total[1m]))",
                            "legendFormat": "RPS"
                        }],
                        "options": {
                            "legend": {"displayMode": "list", "placement": "bottom"},
                            "tooltip": {"mode": "multi", "sort": "none"}
                        },
                        "fieldConfig": {
                            "defaults": {
                                "unit": "rps",
                                "decimals": 2
                            }
                        }
                    },
                    {
                        "id": 3,
                        "title": "Время ответа (p95)",
                        "type": "timeseries",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4},
                        "targets": [{
                            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[1m]))",
                            "legendFormat": "p95"
                        }],
                        "options": {
                            "legend": {"displayMode": "list", "placement": "bottom"}
                        },
                        "fieldConfig": {
                            "defaults": {
                                "unit": "s",
                                "decimals": 3
                            }
                        }
                    },
                    {
                        "id": 4,
                        "title": "Запросы по эндпоинтам",
                        "type": "barchart",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12},
                        "targets": [{
                            "expr": "sum(rate(http_requests_total[1m])) by (endpoint)",
                            "legendFormat": "{{endpoint}}"
                        }],
                        "options": {
                            "orientation": "horizontal",
                            "displayMode": "gradient",
                            "legend": {"displayMode": "list", "placement": "right"}
                        },
                        "fieldConfig": {
                            "defaults": {
                                "unit": "rps",
                                "decimals": 2
                            }
                        }
                    },
                    {
                        "id": 5,
                        "title": "Запросы по методам",
                        "type": "piechart",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12},
                        "targets": [{
                            "expr": "sum(rate(http_requests_total[1m])) by (method)",
                            "legendFormat": "{{method}}"
                        }],
                        "options": {
                            "displayLabels": ["name", "percent"],
                            "legend": {"displayMode": "list", "placement": "right"},
                            "pieType": "pie"
                        },
                        "fieldConfig": {
                            "defaults": {
                                "unit": "rps",
                                "decimals": 2
                            }
                        }
                    }
                ],
                "schemaVersion": 36
            },
            "overwrite": True
        }
        
        dashboard_url = f"{grafana_url}/api/dashboards/db"
        response = session.post(dashboard_url, json=dashboard_json)
        
        if response.status_code in [200, 409]:
            print_color("ГОТОВО: Дашборд создан", Colors.GREEN)
        else:
            print_color(f"Предупреждение: Не удалось создать дашборд: {response.text}", Colors.YELLOW)
        
        return True
        
    except Exception as e:
        print_color(f"Предупреждение: Ошибка настройки Grafana: {e}", Colors.YELLOW)
        print_color("Вы можете подключиться к Grafana вручную: http://localhost:30300", Colors.YELLOW)
        print_color("Логин: admin / Пароль: admin123", Colors.YELLOW)
        return True

# ============================================================
# ФУНКЦИИ ОЧИСТКИ
# ============================================================

def clean_all():
    """Полная очистка всех ресурсов"""
    print_color("="*50, Colors.CYAN)
    print_color("ОЧИСТКА ЛАБОРАТОРНОГО СТЕНДА", Colors.CYAN)
    print_color("="*50, Colors.CYAN)
    
    # 1. Остановка интеграционного клиента
    print_color("\n[1/5] Остановка интеграционного клиента...", Colors.YELLOW)
    run_command("docker-compose down")
    print_color("ГОТОВО: Клиент остановлен", Colors.GREEN)
    

    # 2. Удаление PodMonitor
    print_color("\n[2/5] Удаление PodMonitor...", Colors.YELLOW)
    run_command("kubectl delete podmonitor myapp-podmonitor -n monitoring --ignore-not-found")
    print_color("ГОТОВО: PodMonitor удалён", Colors.GREEN)
    
    # 3. Удаление ресурсов приложения
    print_color("\n[3/5] Удаление ресурсов приложения...", Colors.YELLOW)
    run_command("kubectl delete -f ./k8s/app-deployment.yaml --ignore-not-found")
    run_command("kubectl delete -f ./k8s/app-service.yaml --ignore-not-found")
    print_color("ГОТОВО: Ресурсы приложения удалены", Colors.GREEN)
    
    # 4. Удаление мониторинга
    print_color("\n[4/5] Удаление мониторинга (Prometheus + Grafana)...", Colors.YELLOW)
    run_command("helm uninstall monitoring -n monitoring --ignore-not-found")
    run_command("kubectl delete pvc -n monitoring --all --ignore-not-found")
    run_command("kubectl delete namespace monitoring --ignore-not-found")
    print_color("ГОТОВО: Мониторинг удалён", Colors.GREEN)
    
    # 5. Очистка Docker
    print_color("\n[5/5] Очистка Docker...", Colors.YELLOW)
    run_command("docker system prune -f")
    print_color("ГОТОВО: Docker очищен", Colors.GREEN)
    
    print_color("\n" + "="*50, Colors.GREEN)
    print_color("ОЧИСТКА ЗАВЕРШЕНА!", Colors.GREEN)
    print_color("="*50, Colors.GREEN)
    print_color("\nВсе ресурсы удалены. Для повторного запуска выполните:", Colors.YELLOW)
    print_color("  python launcher.py --start", Colors.WHITE)

def clean_partial():
    """Частичная очистка (оставляет мониторинг)"""
    print_color("="*50, Colors.CYAN)
    print_color("ЧАСТИЧНАЯ ОЧИСТКА (мониторинг остаётся)", Colors.CYAN)
    print_color("="*50, Colors.CYAN)
    
    # 1. Остановка интеграционного клиента
    print_color("\n[1/3] Остановка интеграционного клиента...", Colors.YELLOW)
    run_command("docker-compose down")
    print_color("ГОТОВО: Клиент остановлен", Colors.GREEN)
    
    # 2. Удаление ServiceMonitor
    print_color("\n[2/3] Удаление ServiceMonitor...", Colors.YELLOW)
    run_command("kubectl delete servicemonitor myapp-monitor -n monitoring --ignore-not-found")
    run_command("kubectl delete servicemonitor myapp-monitor -n default --ignore-not-found")
    print_color("ГОТОВО: ServiceMonitor удалён", Colors.GREEN)
    
    # 3. Удаление ресурсов приложения
    print_color("\n[3/3] Удаление ресурсов приложения...", Colors.YELLOW)
    run_command("kubectl delete -f ./k8s/app-deployment.yaml --ignore-not-found")
    run_command("kubectl delete -f ./k8s/app-service.yaml --ignore-not-found")
    print_color("ГОТОВО: Ресурсы приложения удалены", Colors.GREEN)
    
    print_color("\n" + "="*50, Colors.GREEN)
    print_color("ЧАСТИЧНАЯ ОЧИСТКА ЗАВЕРШЕНА!", Colors.GREEN)
    print_color("="*50, Colors.GREEN)
    print_color("\nМониторинг (Prometheus + Grafana) остаётся.", Colors.YELLOW)
    print_color("Для полной очистки выполните: python launcher.py --clean-all", Colors.WHITE)

def print_info():
    """Вывод информации о доступе к сервисам"""
    print_color("\n" + "="*50, Colors.CYAN)
    print_color("ГОТОВО! Доступ к сервисам:", Colors.GREEN)
    print_color("="*50, Colors.CYAN)
    print_color("  API приложения: http://localhost:30080", Colors.WHITE)
    print_color("  Prometheus: http://localhost:30900", Colors.WHITE)
    print_color("  Grafana: http://localhost:30300 (admin/admin123)", Colors.WHITE)
    print_color("="*50, Colors.CYAN)
    print_color("\nДашборд 'Мониторинг API приложения' готов!", Colors.GREEN)
    print_color("\nПолезные команды:", Colors.YELLOW)
    print_color("  Логи клиента: docker-compose logs -f", Colors.WHITE)
    print_color("  Остановка клиента: docker-compose down", Colors.WHITE)
    print_color("  Полная очистка: python launcher.py --clean-all", Colors.WHITE)
    print_color("  Частичная очистка: python launcher.py --clean", Colors.WHITE)

def main():
    """Главная функция с поддержкой аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Kubernetes Lab - Управление стендом')
    parser.add_argument('--start', action='store_true', help='Запуск стенда')
    parser.add_argument('--clean', action='store_true', help='Частичная очистка (оставляет мониторинг)')
    parser.add_argument('--clean-all', action='store_true', help='Полная очистка (удаляет всё)')
    
    args = parser.parse_args()
    
    # Если нет аргументов или указан --start, запускаем стенд
    if not any([args.start, args.clean, args.clean_all]):
        args.start = True
    
    if args.clean_all:
        clean_all()
        return
    elif args.clean:
        clean_partial()
        return
    elif args.start:
        print_color("="*50, Colors.CYAN)
        print_color("Kubernetes Lab - Универсальный запускатор", Colors.CYAN)
        print_color("="*50, Colors.CYAN)
        print_color(f"Платформа: {platform.system()} {platform.release()}", Colors.YELLOW)
        
        # Проверка зависимостей
        if not check_dependencies():
            sys.exit(1)
        
        steps = [
            check_docker,
            check_kubernetes,
            deploy_app,
            install_monitoring,
            create_podmonitor,
            start_client,
            setup_grafana
        ]
        
        for step in steps:
            if not step():
                print_color("\nОСТАНОВКА! Произошла ошибка...", Colors.RED)
                sys.exit(1)
        
        print_info()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\n\nПрервано пользователем", Colors.YELLOW)
        sys.exit(0)