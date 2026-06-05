# 🐳 Kubernetes Lab — API Monitoring Playground

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Kubernetes](https://img.shields.io/badge/Kubernetes-1.27+-326CE5.svg)
![Prometheus](https://img.shields.io/badge/Prometheus-2.47+-E6522C.svg)
![Grafana](https://img.shields.io/badge/Grafana-10+-F46800.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)

Лабораторный стенд для изучения **Kubernetes**, **Prometheus**, **Grafana** и мониторинга REST API.

</div>

---

## ✨ Возможности

- 🚀 FastAPI приложение с REST API
- 📊 Экспорт метрик Prometheus
- 📈 Grafana с готовым Dashboard
- 🔄 Генератор тестового трафика
- ☸️ Развёртывание в Kubernetes
- 🖥️ Поддержка Windows / Linux / macOS

---

## 📦 Стек технологий

| Компонент | Версия |
|-----------|----------|
| Python | 3.11+ |
| FastAPI | 0.104+ |
| Kubernetes | 1.27+ |
| Docker | 24+ |
| Prometheus | 2.47+ |
| Grafana | 10+ |

---

## 🚀 Быстрый запуск

### Требования

- Docker Desktop
- Kubernetes (Docker Desktop / Minikube / Kind)
- Helm
- Python 3.11+

### 1. Клонирование

```bash
git clone https://github.com/your-repo/k8s-lab.git
cd k8s-lab
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Запуск проекта

```bash
python launcher.py --start
```

---

## 🌐 Доступные сервисы

| Сервис | URL | Данные для входа |
|----------|----------------------------|----------------|
| API | <http://localhost:30080> | - |
| Prometheus | <http://localhost:30900> | - |
| Grafana | <http://localhost:30300> | `admin / admin123` |

---

## 📁 Структура проекта

```text
k8s-lab/
│
├── launcher.py
├── requirements.txt
├── README.md
│
├── app/
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── integration/
│   ├── client.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── k8s/
│   ├── app-deployment.yaml
│   └── app-service.yaml
│
└── docker-compose.yml
```

---

## 🛠️ Основные команды

### Запуск

```bash
python launcher.py
# или
python launcher.py --start
```

### Частичная очистка

```bash
python launcher.py --clean
```

### Полная очистка

```bash
python launcher.py --clean-all
```

---

## 📊 Метрики

Приложение экспортирует:

- `http_requests_total`
- `http_request_duration_seconds`
- `python_gc_*`
- `process_*`

### Полезные PromQL запросы

```promql
sum(http_requests_total)
```

```promql
sum(rate(http_requests_total[1m]))
```

```promql
histogram_quantile(
  0.95,
  rate(http_request_duration_seconds_bucket[1m])
)
```

---

## 🧪 Проверка API

### Health Check

```bash
curl http://localhost:30080/api/v1/health
```

### POST запрос

```bash
curl -X POST http://localhost:30080/api/v1/data \
-H "Content-Type: application/json" \
-d '{"test":1}'
```

### Метрики

```bash
curl http://localhost:30080/metrics
```

---

## 🐛 Troubleshooting

<details>
<summary><b>Docker не запущен</b></summary>

```text
ОШИБКА: Docker не запущен!
```

Запустите Docker Desktop или:

```bash
sudo systemctl start docker
```

</details>

<details>
<summary><b>Kubernetes недоступен</b></summary>

```bash
minikube start
```

или включите Kubernetes в Docker Desktop.

</details>

<details>
<summary><b>Grafana не отображает данные</b></summary>

Проверьте:

```bash
kubectl get servicemonitor -n monitoring
```

и наличие Targets в Prometheus.

</details>

---

## 🧹 Очистка

```bash
python launcher.py --clean-all
```

или вручную:

```bash
docker-compose down
kubectl delete -f ./k8s/
helm uninstall monitoring -n monitoring
kubectl delete namespace monitoring
docker system prune -f
```

---

## 🤝 Contributing

```bash
git checkout -b feature/amazing-feature
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

Создайте Pull Request 🚀

---

<div align="center">

**⭐ Если проект оказался полезным — поставьте звезду репозиторию.**

</div>
