# 🐳 Kubernetes Lab — Мониторинг API приложения

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.27+-blue.svg)](https://kubernetes.io/)
[![Prometheus](https://img.shields.io/badge/Prometheus-2.47+-red.svg)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-10.0+-orange.svg)](https://grafana.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

## 📋 О проекте

Лабораторный стенд для изучения **Kubernetes**, **мониторинга** (Prometheus + Grafana) и **API-интеграции**. 

Проект разворачивает:
- ✅ FastAPI приложение с REST API и метриками
- ✅ Prometheus для сбора метрик
- ✅ Grafana с готовым дашбордом
- ✅ Интеграционный клиент, генерирующий тестовый трафик

**Работает на Windows, Linux и macOS!**

---

## 🏗️ Архитектура
┌─────────────────────────────────────────────────────────────┐
│ Ваш компьютер (Хост) │
├─────────────────────────────────────────────────────────────┤
│ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Docker Desktop / Minikube │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ │
│ │ │ FastAPI │ │ Prometheus │ │ Grafana │ │ │
│ │ │ :30080 │ │ :30900 │ │ :30300 │ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Интеграционный клиент (Docker) │ │
│ │ Генерирует запросы к API каждые 15 сек │ │
│ └─────────────────────────────────────────────────────┘ │
│ │
└─────────────────────────────────────────────────────────────┘

## 🚀 Быстрый старт

### Требования

| Компонент | Windows | Linux | macOS |
|-----------|---------|-------|-------|
| Docker Desktop | ✅ | ✅ | ✅ |
| Kubernetes | ✅ (в Docker Desktop) | Minikube/Kind | ✅ (в Docker Desktop) |
| Helm | ✅ | ✅ | ✅ |
| Python 3.11+ | ✅ | ✅ | ✅ |

### Установка


# 1. Клонируйте репозиторий
git clone https://github.com/your-repo/k8s-lab.git
cd k8s-lab

# 2. Установите зависимости Python
pip install -r requirements.txt

# 3. Запустите стенд
python launcher.py --start
После запуска будут доступны сервисы:

Сервис	URL	Логин/Пароль
API приложения	http://localhost:30080	—
Prometheus	http://localhost:30900	—
Grafana	http://localhost:30300	admin / admin123


📁 Структура проекта
text
k8s-lab/
├── launcher.py              # 🚀 Универсальный запускатор (Windows/Linux/macOS)
├── requirements.txt         # 📦 Python зависимости для запускатора
├── README.md                # 📖 Документация
│
├── app/                     # 🐍 FastAPI приложение
│   ├── main.py              # Код API с метриками
│   ├── Dockerfile           # Docker образ приложения
│   └── requirements.txt     # Зависимости FastAPI
│
├── integration/             # 🔄 Интеграционный клиент
│   ├── client.py            # Генератор тестового трафика
│   ├── Dockerfile           # Docker образ клиента
│   └── requirements.txt     # Зависимости клиента
│
├── k8s/                     # ☸️ Kubernetes манифесты
│   ├── app-deployment.yaml  # Деплой приложения
│   └── app-service.yaml     # Сервис приложения
│
└── docker-compose.yml       # 🐳 Запуск интеграционного клиента

🛠️ Использование
Команды запускатора
bash
# Запуск стенда (по умолчанию)
python launcher.py --start
# или просто
python launcher.py

# Частичная очистка (оставляет мониторинг)
python launcher.py --clean

# Полная очистка (удаляет всё)
python launcher.py --clean-all
Что делает каждый режим
Режим	Приложение	ServiceMonitor	Мониторинг (Prom+Graf)	Docker образы
--start	✅ Запускает	✅ Создаёт	✅ Устанавливает	✅ Собирает
--clean	❌ Удаляет	❌ Удаляет	❌ Оставляет	❌ Нет
--clean-all	❌ Удаляет	❌ Удаляет	❌ Удаляет	✅ Очищает
Ручное управление
bash
# Просмотр логов клиента
docker-compose logs -f

# Остановка клиента
docker-compose down

# Проверка состояния Kubernetes
kubectl get pods -A

# Перезапуск приложения
kubectl rollout restart deployment myapp


📊 Мониторинг
Prometheus метрики
Приложение экспортирует следующие метрики:

Метрика	Тип	Описание
http_requests_total	Counter	Общее количество HTTP запросов
http_request_duration_seconds	Histogram	Гистограмма времени ответа
python_gc_*	Counter	Метрики сборщика мусора Python
process_*	Gauge	Метрики процесса (CPU, память)
PromQL запросы для дашборда
promql
# Всего запросов
sum(http_requests_total)

# RPS (запросов в секунду)
sum(rate(http_requests_total[1m]))

# Время ответа (95-й перцентиль)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[1m]))

# Запросы по эндпоинтам
sum(rate(http_requests_total[1m])) by (endpoint)

# Запросы по методам (GET/POST)
sum(rate(http_requests_total[1m])) by (method)
Готовый дашборд
После запуска в Grafana автоматически создаётся дашборд "Мониторинг API приложения" с панелями:

Всего запросов — общее количество запросов

RPS — запросы в секунду

Время ответа (p95) — 95-й перцентиль времени ответа

Запросы по эндпоинтам — распределение по эндпоинтам

Запросы по методам — соотношение GET/POST

🧪 Тестирование API

# Проверка здоровья
curl http://localhost:30080/api/v1/health

# POST запрос
curl -X POST http://localhost:30080/api/v1/data \
  -H "Content-Type: application/json" \
  -d '{"test": 1}'

# GET запрос
curl http://localhost:30080/api/v1/data/1

# Просмотр метрик
curl http://localhost:30080/metrics
Генерация нагрузки

# Генерация 100 запросов
for i in {1..100}; do
  curl -X POST http://localhost:30080/api/v1/data \
    -H "Content-Type: application/json" \
    -d "{\"test\":$i}"
  echo "Запрос $i отправлен"
  sleep 0.1
done


🐛 Устранение неполадок

Проблема: Docker не запущен

Ошибка: ОШИБКА: Docker не запущен!

Решение:

# Windows: Запустите Docker Desktop
# Linux: sudo systemctl start docker
# macOS: Запустите Docker Desktop

Проблема: Kubernetes не доступен

Ошибка: ОШИБКА: Kubernetes недоступен!

Решение:


# Windows: Включите Kubernetes в Docker Desktop (Settings → Kubernetes)
# Linux: minikube start
# macOS: Включите Kubernetes в Docker Desktop

Проблема: Порт уже занят

Ошибка: bind: address already in use

Решение:

# Найти процесс, использующий порт
# Windows: netstat -ano | findstr :30080
# Linux: sudo lsof -i :30080
# Остановить процесс или изменить порт в настройках

Проблема: Grafana не показывает данные

Решение:

Проверьте, что Prometheus видит Targets: http://localhost:30900/targets

Убедитесь, что ServiceMonitor создан: kubectl get servicemonitor -n monitoring

Сгенерируйте трафик: python -c "import requests; [requests.post('http://localhost:30080/api/v1/data', json={'test': i}) for i in range(50)]"

Подождите 1-2 минуты для сбора метрик

📋 Чек-лист запуска

Docker Desktop запущен

Kubernetes включён

Helm установлен

Python 3.11+ установлен

Выполнена команда pip install -r requirements.txt

Запущен python launcher.py --start

🧹 Очистка

Полная очистка (удаляет всё)
python launcher.py --clean-all

Частичная очистка (оставляет мониторинг)
python launcher.py --clean

Ручная очистка

# Остановка клиента
docker-compose down

# Удаление приложения
kubectl delete -f ./k8s/

# Удаление мониторинга
helm uninstall monitoring -n monitoring
kubectl delete namespace monitoring

# Удаление Docker образов
docker rmi myapp:latest
docker system prune -f

📦 Технологии
Компонент	Технология	Версия
API	FastAPI	0.104.1
Метрики	Prometheus Client	0.19.0
Мониторинг	Prometheus + Grafana	kube-prometheus-stack
Оркестрация	Kubernetes	1.27+
Контейнеризация	Docker	24.0+
Язык	Python	3.11+

🤝 Вклад в проект
Форкните репозиторий

Создайте ветку для фичи (git checkout -b feature/amazing)

Зафиксируйте изменения (git commit -m 'Add amazing feature')

Отправьте в репозиторий (git push origin feature/amazing)

Откройте Pull Request