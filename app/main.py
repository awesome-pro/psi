import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.middleware import setup_middlewares
from app.core.logging import logger, log_error
import uuid
from prometheus_fastapi_instrumentator import Instrumentator
from rich.console import Console
import better_exceptions

# Enable better exceptions
better_exceptions.hook()

# Setup enhanced logging
console = Console()

def create_application() -> FastAPI:
    # Enable remote debugging if in debug mode
    if os.getenv("DEBUG") == "1":
        try:
            import debugpy
            debugpy.listen(("0.0.0.0", 5678))
            logger.info("🔍 Remote debugging enabled on port 5678")
        except Exception as e:
            logger.error(f"⚠️ Failed to enable remote debugging: {str(e)}")
            log_error(e, {"context": "remote_debugging_setup"})

    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        version="1.0.0",
        debug=bool(os.getenv("DEBUG", False)),
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )
    
    # Store settings in app state
    application.state.settings = settings
    logger.info("📝 Application settings loaded", settings=settings.dict())
    
    # Setup middlewares
    setup_middlewares(application)
    logger.info("🔧 Middlewares configured")
    
    # Setup Prometheus metrics
    Instrumentator().instrument(application).expose(application)
    logger.info("📊 Prometheus metrics enabled")

    @application.middleware("http")
    async def request_middleware(request: Request, call_next):
        # Generate request ID
        request_id = uuid.uuid4()
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            f"→ {request.method} {request.url}",
            request_id=str(request_id),
            method=request.method,
            url=str(request.url),
            client_host=request.client.host if request.client else None,
        )
        
        try:
            response = await call_next(request)
            # Log response
            logger.info(
                f"← {response.status_code} {request.url}",
                request_id=str(request_id),
                status_code=response.status_code,
                method=request.method,
                url=str(request.url),
            )
            return response
        except Exception as e:
            # Log error with context
            log_error(e, {
                "request_id": str(request_id),
                "method": request.method,
                "url": str(request.url),
                "client_host": request.client.host if request.client else None,
            })
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": str(request_id)
                }
            )
    
    return application

app = create_application()

# Include routers
from app.src.routers import api_router
from app.src.routers.auth import router as auth_router

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(api_router, prefix=settings.API_V1_STR)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_error(exc, {
        "path": str(request.url),
        "method": request.method,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "path_params": request.path_params,
        "request_id": str(getattr(request.state, "request_id", uuid.uuid4())),
    })
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": str(getattr(request.state, "request_id", uuid.uuid4()))
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    logger.info("💓 Health check requested")
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting FastAPI application...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
