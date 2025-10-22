"""
Celery application for async task processing
"""
from celery import Celery
from config import settings

# Create Celery app
celery_app = Celery(
    "datasharing",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
)


@celery_app.task(name="sync_datasets")
def sync_datasets_task(source: str, limit: int = 100):
    """
    Async task to sync datasets from a source

    Args:
        source: Data source name
        limit: Maximum datasets to sync

    Returns:
        Dictionary with sync results
    """
    from app.database import SessionLocal
    from app.services.dataset_service import DatasetService
    from app.models.dataset import DataSourceEnum
    import asyncio

    db = SessionLocal()
    service = DatasetService(db)

    try:
        source_enum = DataSourceEnum(source)
        count = asyncio.run(service.sync_datasets_from_source(source_enum, limit))

        return {
            "status": "success",
            "source": source,
            "synced_count": count,
        }
    except Exception as e:
        return {
            "status": "error",
            "source": source,
            "error": str(e),
        }
    finally:
        asyncio.run(service.close_collectors())
        db.close()


@celery_app.task(name="fetch_dataset")
def fetch_dataset_task(dataset_id: int, format: str = "json", filters: dict = None):
    """
    Async task to fetch dataset data

    Args:
        dataset_id: Dataset ID
        format: Output format
        filters: Optional filters

    Returns:
        Dataset data
    """
    from app.database import SessionLocal
    from app.services.dataset_service import DatasetService
    import asyncio

    db = SessionLocal()
    service = DatasetService(db)

    try:
        data = asyncio.run(service.fetch_dataset_data(dataset_id, format, filters))
        return {
            "status": "success",
            "dataset_id": dataset_id,
            "format": format,
            "data": data,
        }
    except Exception as e:
        return {
            "status": "error",
            "dataset_id": dataset_id,
            "error": str(e),
        }
    finally:
        asyncio.run(service.close_collectors())
        db.close()


if __name__ == "__main__":
    celery_app.start()
