"""
Dataset endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.dataset import DataSourceEnum
from app.schemas.dataset import (
    Dataset,
    DatasetSearch,
    DatasetStats,
    DatasetRequestCreate,
    DatasetRequest,
)
from app.services.dataset_service import DatasetService
from app.utils.security import verify_api_key
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.get("/search", response_model=List[Dataset])
async def search_datasets(
    query: Optional[str] = Query(None, description="Search query"),
    source: Optional[DataSourceEnum] = Query(None, description="Filter by data source"),
    organization: Optional[str] = Query(None, description="Filter by organization"),
    ai_ready_only: bool = Query(False, description="Only AI-ready datasets"),
    limit: int = Query(20, le=100, description="Results limit"),
    offset: int = Query(0, ge=0, description="Results offset"),
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_api_key),
):
    """
    Search datasets across all sources
    """
    service = DatasetService(db)

    try:
        datasets = service.search_datasets(
            query=query,
            source=source,
            organization=organization,
            ai_ready_only=ai_ready_only,
            limit=limit,
            offset=offset,
        )
        return datasets
    finally:
        await service.close_collectors()


@router.get("/stats", response_model=DatasetStats)
def get_dataset_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_api_key),
):
    """
    Get dataset statistics
    """
    service = DatasetService(db)
    return service.get_dataset_stats()


@router.get("/{dataset_id}", response_model=Dataset)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_api_key),
):
    """
    Get dataset details by ID
    """
    from app.models.dataset import Dataset as DatasetModel

    dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return dataset


@router.post("/fetch/{dataset_id}")
async def fetch_dataset_data(
    dataset_id: int,
    format: str = Query("json", regex="^(json|csv|parquet)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_api_key),
):
    """
    Fetch dataset data in specified format

    Supported formats:
    - json: JSON format
    - csv: CSV format
    - parquet: Parquet format (optimized for AI/ML)
    """
    service = DatasetService(db)

    try:
        data = await service.fetch_dataset_data(dataset_id, format=format)

        # Update user usage
        current_user.current_usage += 1
        db.commit()

        return {"dataset_id": dataset_id, "format": format, "data": data}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching dataset data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching dataset data")
    finally:
        await service.close_collectors()


@router.post("/sync/{source}")
async def sync_datasets(
    source: DataSourceEnum,
    limit: int = Query(100, le=1000, description="Max datasets to sync"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_api_key),
):
    """
    Synchronize datasets from a specific source

    Admin only endpoint to populate the database
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    service = DatasetService(db)

    try:
        count = await service.sync_datasets_from_source(source, limit=limit)
        return {"source": source, "synced_count": count}
    except Exception as e:
        logger.error(f"Error syncing datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.close_collectors()
