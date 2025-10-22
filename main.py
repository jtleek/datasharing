"""
Brazilian Federal Data Collector SaaS - Main Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from config import settings
from app.database import engine, Base
from app.api import auth, datasets, api_keys

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Brazilian Federal Data Collector SaaS...")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    yield

    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    🇧🇷 Brazilian Federal Data Collector SaaS

    A comprehensive platform for accessing and managing Brazilian public federal datasets
    optimized for AI and machine learning applications.

    ## Features

    * **Multiple Data Sources**: Access dados.gov.br, Portal da Transparência, IBGE, and more
    * **AI-Ready Formats**: Download data in JSON, CSV, or Parquet formats
    * **Data Quality Metrics**: Get completeness scores and quality assessments
    * **API Key Management**: Secure access with personal API keys
    * **Rate Limiting**: Fair usage with quota management
    * **Real-time Sync**: Keep datasets updated from official sources

    ## Data Sources

    1. **dados.gov.br** - Brazilian Open Data Portal (CKAN)
    2. **Portal da Transparência** - Government transparency data
    3. **IBGE** - Brazilian Institute of Geography and Statistics

    ## Quick Start

    1. Register an account: `POST /api/v1/auth/register`
    2. Login to get access token: `POST /api/v1/auth/login`
    3. Create an API key: `POST /api/v1/api-keys`
    4. Search datasets: `GET /api/v1/datasets/search`
    5. Fetch dataset data: `POST /api/v1/datasets/fetch/{dataset_id}`
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(datasets.router, prefix=settings.API_V1_PREFIX)
app.include_router(api_keys.router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/")
def root():
    """
    Root endpoint with API information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_prefix": settings.API_V1_PREFIX,
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
