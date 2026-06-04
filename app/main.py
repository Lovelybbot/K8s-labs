from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import random
import time

app = FastAPI()

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

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/data")
async def post_data(data: dict):
    # Симуляция обработки
    time.sleep(random.uniform(0.01, 0.1))
    return {
        "status": "ok",
        "received": data,
        "random_value": random.randint(1, 100),
        "timestamp": time.time()
    }

@app.get("/api/v1/data/{item_id}")
async def get_item(item_id: int):
    return {"id": item_id, "value": f"item_{item_id}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)