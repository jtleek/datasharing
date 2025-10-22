"""
Dataset models for tracking available datasets and user requests
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class DataSourceEnum(str, enum.Enum):
    DADOS_GOV_BR = "dados_gov_br"
    PORTAL_TRANSPARENCIA = "portal_transparencia"
    IBGE = "ibge"
    INEP = "inep"
    ANS = "ans"
    ANVISA = "anvisa"
    CUSTOM = "custom"


class DatasetStatusEnum(str, enum.Enum):
    AVAILABLE = "available"
    COLLECTING = "collecting"
    PROCESSING = "processing"
    CACHED = "cached"
    ERROR = "error"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)

    # Dataset identification
    external_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)

    # Source information
    source = Column(Enum(DataSourceEnum), nullable=False, index=True)
    source_url = Column(String)

    # Metadata
    organization = Column(String, index=True)
    tags = Column(JSON)  # Array of tag strings
    metadata = Column(JSON)  # Additional flexible metadata

    # Data characteristics
    format = Column(String)  # csv, json, xml, etc.
    size_bytes = Column(Integer)
    record_count = Column(Integer)

    # Quality metrics
    completeness_score = Column(Float)  # 0-1 score
    last_updated_source = Column(DateTime(timezone=True))
    update_frequency = Column(String)  # daily, weekly, monthly, yearly

    # Status
    status = Column(Enum(DatasetStatusEnum), default=DatasetStatusEnum.AVAILABLE)

    # AI readiness
    ai_ready = Column(Boolean, default=False)
    ai_format = Column(String)  # parquet, tfrecord, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_collected_at = Column(DateTime(timezone=True))

    # Relationships
    requests = relationship("DatasetRequest", back_populates="dataset")


class DatasetRequest(Base):
    __tablename__ = "dataset_requests"

    id = Column(Integer, primary_key=True, index=True)

    # User and dataset
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)

    # Request details
    format = Column(String, nullable=False)  # json, csv, parquet
    filters = Column(JSON)  # Optional filters applied

    # Status and processing
    status = Column(String, default="pending")  # pending, processing, completed, failed
    task_id = Column(String, unique=True, index=True)  # Celery task ID

    # Result
    result_url = Column(String)
    result_size_bytes = Column(Integer)
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="dataset_requests")
    dataset = relationship("Dataset", back_populates="requests")
