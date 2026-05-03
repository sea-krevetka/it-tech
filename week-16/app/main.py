from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

from app.config import settings
from app.routes import router
from app.schemas import ProductCreate, ProductUpdate, ProductResponse

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Создание приложения
app = FastAPI(
    title="Products Service",
    description="Service for managing products",
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Middleware для безопасности
if not settings.DEBUG:
    # Ограничение доверенных хостов
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "products.example.com"]
    )
    
    # CORS только для доверенных доменов
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://products.example.com"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=True,
        max_age=3600
    )

# Подключение маршрутов
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "debug": settings.DEBUG,
        "service": "products-svc-s01"
    }


@app.get("/")
async def root():
    return {
        "message": "Products Service",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "disabled in production",
        "project_code": "products-s01"
    }


# Обработчик ошибок - не выводим детали в production
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if settings.DEBUG:
        # В debug режиме показываем детали
        return await http_exception_handler_original(request, exc)
    else:
        # В production скрываем детали
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": "An error occurred"}
        )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    if settings.DEBUG:
        raise exc
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )