"""
Dataset schemas for API validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.dataset import DataSourceEnum, DatasetStatusEnum


class DatasetBase(BaseModel):
    title: str
    description: Optional[str] = None
    source: DataSourceEnum
    organization: Optional[str] = None
    tags: Optional[List[str]] = []


class Dataset(DatasetBase):
    id: int
    external_id: str
    source_url: Optional[str] = None
    format: Optional[str] = None
    size_bytes: Optional[int] = None
    record_count: Optional[int] = None
    status: DatasetStatusEnum
    ai_ready: bool
    completeness_score: Optional[float] = None
    last_updated_source: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DatasetSearch(BaseModel):
    query: Optional[str] = None
    source: Optional[DataSourceEnum] = None
    organization: Optional[str] = None
    tags: Optional[List[str]] = []
    ai_ready_only: bool = False
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)


class DatasetRequestCreate(BaseModel):
    dataset_id: int
    format: str = Field(default="json", pattern="^(json|csv|parquet)$")
    filters: Optional[Dict[str, Any]] = {}


class DatasetRequest(BaseModel):
    id: int
    dataset_id: int
    format: str
    status: str
    task_id: Optional[str] = None
    result_url: Optional[str] = None
    result_size_bytes: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DatasetStats(BaseModel):
    total_datasets: int
    datasets_by_source: Dict[str, int]
    ai_ready_count: int
    total_size_gb: float
