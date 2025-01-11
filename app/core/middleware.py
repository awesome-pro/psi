from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
from .logging import logger

class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(
            f"Request processed in {process_time:.2f} seconds",
            extra={
                "process_time": process_time,
                "path": str(request.url),
                "method": request.method
            }
        )
        return response

def setup_middlewares(app: FastAPI) -> None:
    """Configure all middleware for the application."""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this based on your needs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("✅ CORS middleware configured")
    
    # Add GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    logger.info("✅ GZip middleware configured")
    
    # Add request timing middleware
    app.add_middleware(RequestTimingMiddleware)
    logger.info("✅ Request timing middleware configured")
