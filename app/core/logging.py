import sys
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
import logging
from loguru import logger
from rich.console import Console
from rich.theme import Theme
from rich.traceback import install as rich_traceback_install
from rich.logging import RichHandler

# Custom theme for rich console
CONSOLE_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "critical": "red bold reverse",
    "timestamp": "green",
    "logger.name": "blue",
    "path": "cyan",
    "line": "cyan",
    "exception": "red",
    "exc_info": "red",
})

# Create console with custom theme
console = Console(theme=CONSOLE_THEME, highlight=True)

# Configure rich traceback
rich_traceback_install(
    console=console,
    show_locals=True,
    locals_max_length=5,
    locals_max_string=60,
    suppress=[],
    max_frames=10,
)

class EnhancedInterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller frame
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # Extract exception info
        exc_info = record.exc_info
        exception_details = None
        if exc_info:
            exception = exc_info[1]
            exception_details = {
                "type": exc_info[0].__name__,
                "message": str(exception),
                "traceback": record.exc_text,
            }

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
            error_details=exception_details
        )

def format_error_record(record: Dict[str, Any]) -> str:
    """Enhanced format for error records with visual appeal."""
    # Base format with timestamp and level
    format_string = ""
    
    # Add timestamp with custom styling
    format_string += "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    
    # Add log level with dynamic color based on severity
    format_string += "<level>{level: <8}</level> | "
    
    # Add location info
    format_string += "<blue>{name}</blue>:<cyan>{function}</cyan>:<green>{line}</green> "
    
    # Add main message
    if record["level"].name in ("ERROR", "CRITICAL"):
        format_string += "\n\u256d\u2500\u2500\u2500 Error Details \u2500\u2500\u2500\u2500\u256e\n"
        format_string += "\u2502 <red>{message}</red>\n"
        
        # Add exception details if available
        if "error_details" in record["extra"]:
            error = record["extra"]["error_details"]
            format_string += "\u251c\u2500 Type: <yellow>{extra[error_details][type]}</yellow>\n"
            format_string += "\u251c\u2500 Message: <red>{extra[error_details][message]}</red>\n"
            if error.get("traceback"):
                format_string += "\u2570\u2500\u2500 Traceback \u2500\u2500\u256f\n{extra[error_details][traceback]}"
            else:
                format_string += "\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f"
    else:
        format_string += "<level>{message}</level>"

    return format_string

def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """Enhanced error logging with context."""
    error_context = {
        "error_type": error.__class__.__name__,
        "error_details": str(error),
        "timestamp": datetime.now().isoformat(),
    }
    
    if context:
        error_context.update(context)
    
    logger.opt(exception=True).error(
        "An error occurred",
        error_details=error_context
    )
    
def setup_logging() -> None:
    """Configure logging with loguru and rich."""
    # Remove default logger
    logger.remove()
    
    # Add rich handler for console output
    logger.add(
        backtrace=True,
        diagnose=True,
        level="INFO",
        colorize=True,
        format=format_error_record
        catch=True,
        newline=True
    )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[EnhancedInterceptHandler()], level=0, force=True)
    
    # Intercept uvicorn logging
    for uvicorn_logger in ("uvicorn.asgi", "uvicorn.access"):
        logging.getLogger(uvicorn_logger).handlers = [EnhancedInterceptHandler()]

def log_request(request, response=None, error=None):
    """Log request and response details."""
    request_id = str(request.state.request_id)
    log_dict = {
        "request_id": request_id,
        "method": request.method,
        "url": str(request.url),
        "client_host": request.client.host if request.client else None,
        "headers": dict(request.headers),
        "path_params": request.path_params,
        "query_params": dict(request.query_params),
        "timestamp": datetime.now().isoformat(),
    }
    
    if response:
        log_dict.update({
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
        })
    
    if error:
        log_dict.update({
            "error": str(error),
            "error_detail": error.__class__.__name__,
        })
    
    logger.bind(request=log_dict).info(
        "Request {request_id} | {method} {url} | Status: {status}",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        status=response.status_code if response else "ERROR",
    )
