"""
Shipments Service for Docker Compose
project_code: shipments-s01
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import datetime
import os
import redis
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Shipments Service")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "shipments")
DB_USER = os.getenv("DB_USER", "shipments_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret_password")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

class ShipmentCreate(BaseModel):
    tracking_number: str
    origin: str
    destination: str
    weight: float
    description: Optional[str] = None


class Shipment(ShipmentCreate):
    id: str
    status: str
    created_at: str
    updated_at: str


# In-memory cache (для примера)
shipments_db = {}


def get_redis():
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=5
        )
        r.ping()
        return r
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return None


@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "service": "shipments-svc-s01",
        "project_code": "shipments-s01",
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Проверка Redis
    redis_client = get_redis()
    if redis_client:
        health_status["redis"] = "connected"
    else:
        health_status["redis"] = "disconnected"
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/api/shipments", response_model=List[Shipment])
async def get_shipments():
    """Получение всех отправок"""
    return list(shipments_db.values())


@app.get("/api/shipments/{shipment_id}", response_model=Shipment)
async def get_shipment(shipment_id: str):
    """Получение отправки по ID"""
    shipment = shipments_db.get(shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@app.post("/api/shipments", response_model=Shipment, status_code=201)
async def create_shipment(shipment: ShipmentCreate):
    """Создание новой отправки"""
    now = datetime.datetime.now().isoformat()
    shipment_id = str(uuid.uuid4())[:8]
    
    new_shipment = Shipment(
        id=shipment_id,
        tracking_number=shipment.tracking_number,
        origin=shipment.origin,
        destination=shipment.destination,
        weight=shipment.weight,
        description=shipment.description,
        status="CREATED",
        created_at=now,
        updated_at=now
    )
    
    shipments_db[shipment_id] = new_shipment.dict()
    
    # Сохраняем в Redis (кэш)
    redis_client = get_redis()
    if redis_client:
        redis_client.setex(
            f"shipment:{shipment_id}",
            3600,
            str(new_shipment.dict())
        )
    
    return new_shipment


@app.put("/api/shipments/{shipment_id}", response_model=Shipment)
async def update_shipment(shipment_id: str, status: str):
    """Обновление статуса отправки"""
    if shipment_id not in shipments_db:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    shipments_db[shipment_id]["status"] = status
    shipments_db[shipment_id]["updated_at"] = datetime.datetime.now().isoformat()
    
    return Shipment(**shipments_db[shipment_id])


@app.delete("/api/shipments/{shipment_id}")
async def delete_shipment(shipment_id: str):
    """Удаление отправки"""
    if shipment_id not in shipments_db:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    del shipments_db[shipment_id]
    
    # Удаляем из Redis
    redis_client = get_redis()
    if redis_client:
        redis_client.delete(f"shipment:{shipment_id}")
    
    return {"message": "Shipment deleted"}


@app.on_event("startup")
async def startup():
    print("=" * 60)
    print("Shipments Service started")
    print(f"project_code: shipments-s01")
    print(f"Port: 8210")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"Redis: {REDIS_HOST}:{REDIS_PORT}")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8210)