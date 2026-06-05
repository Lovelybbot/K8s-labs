from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import random
import time

# Добавляем метаданные для Swagger
app = FastAPI(
    title="API приложения",
    description="Лабораторный стенд для изучения Kubernetes, мониторинга и API-интеграции",
    version="1.0.0",
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc
    openapi_url="/openapi.json" # OpenAPI схема
)

REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'Request duration', ['endpoint'])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUESTS.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.labels(endpoint=request.url.path).observe(duration)
    
    return response

@app.get("/metrics")
async def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/v1/health", tags=["Health"])
async def health():
    """
    Проверка здоровья сервиса
    
    Returns:
        dict: Статус сервиса
    """
    return {"status": "healthy"}

@app.post("/api/v1/data", tags=["Data"])
async def post_data(data: dict):
    """
    Создание записи
    
    Args:
        data (dict): Данные для записи
    
    Returns:
        dict: Результат операции с random_value
    """
    time.sleep(random.uniform(0.01, 0.1))
    return {
        "status": "ok",
        "received": data,
        "random_value": random.randint(1, 100),
        "timestamp": time.time()
    }

@app.get("/api/v1/data/{item_id}", tags=["Data"])
async def get_item(item_id: int):
    """
    Получение записи по ID
    
    Args:
        item_id (int): ID записи
    
    Returns:
        dict: Данные записи
    """
    return {"id": item_id, "value": f"item_{item_id}"}

@app.get("/api/v1/data", tags=["Data"])
async def get_all_items(limit: int = 10, offset: int = 0):
    """
    Получение списка записей с пагинацией
    
    Args:
        limit (int): Количество записей
        offset (int): Смещение
    
    Returns:
        dict: Список записей и метаинформация
    """
    # Пример данных
    items = [{"id": i, "value": f"item_{i}"} for i in range(offset, offset + limit)]
    return {
        "items": items,
        "total": 100,
        "limit": limit,
        "offset": offset
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)