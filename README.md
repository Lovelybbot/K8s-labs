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

## 🚀 Быстрый старт

### Требования

| Компонент | Windows | Linux | macOS |
|-----------|---------|-------|-------|
| Docker | ✅ (Desktop) | ✅ (Engine) | ✅ (Desktop) |
| Kubernetes | ✅ (в Docker Desktop) | Minikube/Kind | ✅ (в Docker Desktop) |
| Helm | ✅ | ✅ | ✅ |
| Python 3.11+ | ✅ | ✅ | ✅ |

### Установка

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/your-repo/k8s-lab.git
cd k8s-lab

# 2. Установите зависимости Python
pip install -r requirements.txt

# 3. Запустите стенд
python launcher.py --start
Доступ к сервисам
Сервис	URL	Логин/Пароль
API приложения	http://localhost:30080	—
Prometheus	http://localhost:30900	—
Grafana	http://localhost:30300	admin / admin123
📁 Структура проекта
text
k8s-lab/
├── launcher.py              # 🚀 Универсальный запускатор
├── requirements.txt         # 📦 Python зависимости
├── README.md                # 📖 Документация
├── traffic_gui.py           # 🎛 Графический генератор трафика
│
├── app/                     # 🐍 FastAPI приложение
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── integration/             # 🔄 Интеграционный клиент
│   ├── client.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── k8s/                     # ☸️ Kubernetes манифесты
│   ├── app-deployment.yaml
│   └── app-service.yaml
│
└── docker-compose.yml       # 🐳 Запуск клиента
🛠️ Использование
Команды запускатора
bash
# Запуск стенда
python launcher.py --start

# Частичная очистка (оставляет мониторинг)
python launcher.py --clean

# Полная очистка (удаляет всё)
python launcher.py --clean-all
Что делает каждый режим
Режим	Приложение	PodMonitor	Мониторинг	Docker образы
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
📚 API Документация
После запуска стенда доступна интерактивная документация API:

Документация	URL
Swagger UI	http://localhost:30080/docs
ReDoc	http://localhost:30080/redoc
OpenAPI JSON	http://localhost:30080/openapi.json
Доступные эндпоинты
Метод	Эндпоинт	Описание
GET	/api/v1/health	Проверка здоровья сервиса
GET	/api/v1/data	Получение списка записей (с пагинацией)
GET	/api/v1/data/{id}	Получение записи по ID
POST	/api/v1/data	Создание новой записи
GET	/metrics	Prometheus метрики
📊 Мониторинг
Prometheus метрики
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
Ручные запросы
bash
# Проверка здоровья
curl http://localhost:30080/api/v1/health

# POST запрос
curl -X POST http://localhost:30080/api/v1/data \
  -H "Content-Type: application/json" \
  -d '{"test": 1}'

# GET запрос
curl http://localhost:30080/api/v1/data/1

# GET список (пагинация)
curl "http://localhost:30080/api/v1/data?limit=5&offset=0"

# Просмотр метрик
curl http://localhost:30080/metrics
Генерация нагрузки
bash
# 200 POST запросов
for i in {1..200}; do
  curl -s -X POST http://localhost:30080/api/v1/data \
    -H "Content-Type: application/json" \
    -d "{\"test\":$i}" > /dev/null
  echo "Запрос $i отправлен"
done
Графический генератор трафика
bash
# Установка tkinter (Linux)
sudo apt install python3-tk

# Запуск GUI
python traffic_gui.py
Возможности GUI:

POST / GET / смешанный / бесконечный режимы

Настройка количества запросов и задержки

Многопоточность (до 20 потоков)

Лог с цветовой маркировкой

🔧 Универсальный клиент
Клиент автоматически определяет окружение (Windows/Linux/WSL2) и корректно подключается к API без ручной настройки.

🐛 Устранение неполадок
Проблема: Docker не запущен
Ошибка: ОШИБКА: Docker не запущен!

Решение:

Windows: Запустите Docker Desktop

Linux: sudo systemctl start docker

macOS: Запустите Docker Desktop

Проблема: Kubernetes не доступен
Ошибка: ОШИБКА: Kubernetes недоступен!

Решение:

Windows: Включите Kubernetes в Docker Desktop (Settings → Kubernetes)

Linux: minikube start --driver=docker

macOS: Включите Kubernetes в Docker Desktop

Проблема: ImagePullBackOff в Minikube
Решение:

bash
minikube image load myapp:latest
kubectl rollout restart deployment myapp
Проблема: Порт уже занят
Ошибка: bind: address already in use

Решение:

bash
# Найти процесс, использующий порт
# Windows: netstat -ano | findstr :30080
# Linux: sudo lsof -i :30080

# Остановить процесс или изменить порт в настройках
Проблема: Grafana не показывает данные
Решение:

Проверьте Targets в Prometheus: http://localhost:30900/targets

Убедитесь, что PodMonitor создан: kubectl get podmonitor -n monitoring

Проверьте аннотации подов: kubectl get pod -l app=myapp -o yaml | grep prometheus.io

Сгенерируйте трафик:

bash
for i in {1..50}; do curl -s -X POST http://localhost:30080/api/v1/data -H "Content-Type: application/json" -d "{\"test\":$i}" > /dev/null; done
Подождите 1-2 минуты для сбора метрик

Проблема: Нет Targets myapp в Prometheus
Решение:

bash
# Проверить PodMonitor
kubectl get podmonitor -n monitoring

# Проверить метку release
kubectl get podmonitor myapp-podmonitor -n monitoring --show-labels

# Перезапустить Prometheus
kubectl delete pod -n monitoring -l app.kubernetes.io/name=prometheus
Проблема: Клиент не подключается на Linux/WSL2
Решение: Клиент теперь автоматически определяет окружение. Убедитесь, что обновлены файлы:

bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f
Проблема: Docker не запущен в WSL2
Решение (Docker Engine, не Desktop):

bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Перезагрузить WSL
📋 Чек-лист запуска
Docker запущен

Kubernetes включён (Docker Desktop) или Minikube запущен

Helm установлен

Python 3.11+ установлен

Выполнена команда pip install -r requirements.txt

Запущен python launcher.py --start

🧹 Очистка
Полная очистка (удаляет всё)
bash
python launcher.py --clean-all
Частичная очистка (оставляет мониторинг)
bash
python launcher.py --clean
Ручная очистка
bash
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
Документация API	Swagger/OpenAPI	—
🤝 Вклад в проект
Форкните репозиторий

Создайте ветку для фичи (git checkout -b feature/amazing)

Зафиксируйте изменения (git commit -m 'feat: add amazing feature')

Отправьте в репозиторий (git push origin feature/amazing)

Откройте Pull Request

📄 Лицензия
MIT

🙏 Благодарности
FastAPI

Prometheus

Grafana

Kubernetes

kube-prometheus-stack

⭐ Если проект оказался полезным, поставьте звезду на GitHub!