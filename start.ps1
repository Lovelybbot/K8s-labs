# start.ps1 - Главный скрипт запуска
cd C:\k8s-lab

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Запуск Kubernetes Lab на Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Проверка Docker Desktop
Write-Host "`n[1/8] Проверка Docker Desktop..." -ForegroundColor Yellow
$dockerStatus = docker info 2>$null
if (-not $dockerStatus) {
    Write-Host "ОШИБКА: Docker Desktop не запущен!" -ForegroundColor Red
    exit 1
}
Write-Host "ГОТОВО: Docker Desktop работает" -ForegroundColor Green

# 2. Проверка Kubernetes
Write-Host "`n[2/8] Проверка Kubernetes..." -ForegroundColor Yellow
kubectl cluster-info 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Kubernetes недоступен!" -ForegroundColor Red
    exit 1
}
Write-Host "ГОТОВО: Kubernetes работает" -ForegroundColor Green

# 3. Сборка образа приложения
Write-Host "`n[3/8] Сборка образа myapp..." -ForegroundColor Yellow
docker build -t myapp:latest ./app
Write-Host "ГОТОВО: Образ собран" -ForegroundColor Green

# 4. Деплой приложения
Write-Host "`n[4/8] Деплой приложения в Kubernetes..." -ForegroundColor Yellow
kubectl apply -f ./k8s/app-deployment.yaml
kubectl apply -f ./k8s/app-service.yaml

# Ожидание подов
Write-Host "Ожидание подов myapp..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=myapp --timeout=60s 2>$null
Write-Host "ГОТОВО: Приложение запущено" -ForegroundColor Green

# 5. Установка мониторинга (если не установлен)
Write-Host "`n[5/8] Установка Prometheus + Grafana..." -ForegroundColor Yellow
$monitoringExists = helm list -n monitoring 2>$null | Select-String "monitoring"
if (-not $monitoringExists) {
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>$null
    helm repo update 2>$null
    helm install monitoring prometheus-community/kube-prometheus-stack `
        --namespace monitoring `
        --create-namespace `
        --set grafana.service.type=NodePort `
        --set grafana.service.nodePort=30300 `
        --set grafana.adminPassword=admin123 `
        --set prometheus.service.type=NodePort `
        --set prometheus.service.nodePort=30900 2>$null
    
    Write-Host "Ожидание запуска мониторинга (120 секунд)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 120
} else {
    Write-Host "ГОТОВО: Мониторинг уже установлен" -ForegroundColor Green
}

# 6. Создание ServiceMonitor для myapp (ВАЖНО!)
Write-Host "`n[6/8] Создание ServiceMonitor для myapp..." -ForegroundColor Yellow

# Удалить старый, если есть
kubectl delete servicemonitor myapp-monitor -n monitoring --ignore-not-found 2>$null

# Создать новый с правильной меткой release=monitoring
kubectl apply -f - @"
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp-monitor
  namespace: monitoring
  labels:
    release: monitoring
spec:
  selector:
    matchLabels:
      app: myapp
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
  namespaceSelector:
    matchNames:
    - default
"@

Write-Host "ГОТОВО: ServiceMonitor создан" -ForegroundColor Green

# 7. Перезапуск Prometheus (чтобы подхватил ServiceMonitor)
Write-Host "`n[7/8] Перезапуск Prometheus..." -ForegroundColor Yellow
kubectl delete pod -n monitoring -l app.kubernetes.io/name=prometheus 2>$null
Start-Sleep -Seconds 30
Write-Host "ГОТОВО: Prometheus перезапущен" -ForegroundColor Green

# 8. Запуск интеграционного клиента
Write-Host "`n[8/8] Запуск интеграционного клиента..." -ForegroundColor Yellow
docker-compose down 2>$null
docker-compose build --no-cache 2>$null
docker-compose up -d 2>$null
Write-Host "ГОТОВО: Клиент запущен" -ForegroundColor Green

# Информация о доступе
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ГОТОВО! Доступ к сервисам:" -ForegroundColor Green
Write-Host "  API Приложения: http://localhost:30080" -ForegroundColor White
Write-Host "    - POST /api/v1/data" -ForegroundColor Gray
Write-Host "    - GET /api/v1/data/{id}" -ForegroundColor Gray
Write-Host "    - GET /api/v1/health" -ForegroundColor Gray
Write-Host "    - GET /metrics" -ForegroundColor Gray
Write-Host ""
Write-Host "  Prometheus: http://localhost:30900" -ForegroundColor White
Write-Host "    - Targets: http://localhost:30900/targets" -ForegroundColor Gray
Write-Host ""
Write-Host "  Grafana: http://localhost:30300" -ForegroundColor White
Write-Host "    - Логин: admin" -ForegroundColor Gray
Write-Host "    - Пароль: admin123" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Логи клиента: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "Остановка клиента: docker-compose down" -ForegroundColor Yellow
Write-Host "Полная очистка: .\clean.ps1" -ForegroundColor Yellow
Write-Host ""

# Показать логи
Write-Host "Логи интеграционного клиента:" -ForegroundColor Cyan
docker-compose logs -f --tail=20