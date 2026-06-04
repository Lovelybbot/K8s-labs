# clean.ps1 - Очистка лабораторного стенда
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Очистка лабораторного стенда" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

# 1. Остановка интеграционного клиента
Write-Host "`n[1/4] Остановка интеграционного клиента..." -ForegroundColor Yellow
docker-compose down
Write-Host "ГОТОВО: Клиент остановлен" -ForegroundColor Green

# 2. Удаление ServiceMonitor (ВАЖНО!)
Write-Host "`n[2/4] Удаление ServiceMonitor..." -ForegroundColor Yellow
kubectl delete servicemonitor myapp-monitor -n monitoring --ignore-not-found
kubectl delete podmonitor myapp-podmonitor -n monitoring --ignore-not-found
Write-Host "ГОТОВО: ServiceMonitor удалён" -ForegroundColor Green

# 3. Удаление Kubernetes ресурсов (опционально)
Write-Host "`n[3/4] Удалить Kubernetes ресурсы приложения? (Y/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq 'Y') {
    Write-Host "Удаление ресурсов..." -ForegroundColor Yellow
    kubectl delete -f ./k8s/ --ignore-not-found=true
    Write-Host "ГОТОВО: Ресурсы приложения удалены" -ForegroundColor Green
} else {
    Write-Host "Пропуск удаления ресурсов приложения" -ForegroundColor Gray
}

# 4. Удаление мониторинга (опционально)
Write-Host "`n[4/4] Удалить мониторинг (Prometheus+Grafana)? (Y/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq 'Y') {
    Write-Host "Удаление мониторинга..." -ForegroundColor Yellow
    helm uninstall monitoring -n monitoring --ignore-not-found
    kubectl delete pvc -n monitoring --all --ignore-not-found
    Write-Host "ГОТОВО: Мониторинг удалён" -ForegroundColor Green
} else {
    Write-Host "Мониторинг оставлен (можно удалить позже: helm uninstall monitoring -n monitoring)" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Очистка завершена!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green