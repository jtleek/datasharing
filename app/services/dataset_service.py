"""
Dataset service for managing dataset operations
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime

from app.models.dataset import Dataset, DatasetRequest, DataSourceEnum, DatasetStatusEnum
from app.models.user import User
from app.collectors import DadosGovBrCollector, PortalTransparenciaCollector, IBGECollector
from app.utils.data_transform import DataTransformer
import logging

logger = logging.getLogger(__name__)


class DatasetService:
    """
    Service for managing datasets
    """

    def __init__(self, db: Session):
        self.db = db
        self.collectors = {
            DataSourceEnum.DADOS_GOV_BR: DadosGovBrCollector(),
            DataSourceEnum.PORTAL_TRANSPARENCIA: PortalTransparenciaCollector(),
            DataSourceEnum.IBGE: IBGECollector(),
        }

    async def sync_datasets_from_source(
        self, source: DataSourceEnum, limit: int = 100
    ) -> int:
        """
        Synchronize datasets from a specific source

        Args:
            source: Data source to sync from
            limit: Maximum datasets to sync

        Returns:
            Number of datasets synced
        """
        collector = self.collectors.get(source)
        if not collector:
            raise ValueError(f"Unknown source: {source}")

        try:
            datasets = await collector.search_datasets(limit=limit)
            synced_count = 0

            for dataset_data in datasets:
                existing = (
                    self.db.query(Dataset)
                    .filter(Dataset.external_id == dataset_data["external_id"])
                    .first()
                )

                if existing:
                    # Update existing dataset
                    for key, value in dataset_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new dataset
                    new_dataset = Dataset(**dataset_data)
                    self.db.add(new_dataset)

                synced_count += 1

            self.db.commit()
            logger.info(f"Synced {synced_count} datasets from {source}")
            return synced_count

        except Exception as e:
            logger.error(f"Error syncing datasets from {source}: {e}")
            self.db.rollback()
            raise

    def search_datasets(
        self,
        query: Optional[str] = None,
        source: Optional[DataSourceEnum] = None,
        organization: Optional[str] = None,
        tags: Optional[List[str]] = None,
        ai_ready_only: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dataset]:
        """
        Search datasets in database

        Args:
            query: Search query
            source: Filter by data source
            organization: Filter by organization
            tags: Filter by tags
            ai_ready_only: Only return AI-ready datasets
            limit: Results limit
            offset: Results offset

        Returns:
            List of datasets
        """
        query_obj = self.db.query(Dataset)

        # Apply filters
        if query:
            search = f"%{query}%"
            query_obj = query_obj.filter(
                or_(
                    Dataset.title.ilike(search),
                    Dataset.description.ilike(search),
                )
            )

        if source:
            query_obj = query_obj.filter(Dataset.source == source)

        if organization:
            query_obj = query_obj.filter(Dataset.organization.ilike(f"%{organization}%"))

        if tags:
            # Filter by tags (PostgreSQL JSON array contains)
            for tag in tags:
                query_obj = query_obj.filter(
                    func.jsonb_path_exists(Dataset.tags, f'$[*] ? (@ == "{tag}")')
                )

        if ai_ready_only:
            query_obj = query_obj.filter(Dataset.ai_ready == True)

        # Order by updated_at descending
        query_obj = query_obj.order_by(Dataset.updated_at.desc())

        # Apply pagination
        return query_obj.offset(offset).limit(limit).all()

    def get_dataset_stats(self) -> Dict[str, Any]:
        """
        Get dataset statistics

        Returns:
            Dictionary with statistics
        """
        total = self.db.query(func.count(Dataset.id)).scalar()

        # Count by source
        by_source = (
            self.db.query(Dataset.source, func.count(Dataset.id))
            .group_by(Dataset.source)
            .all()
        )

        datasets_by_source = {source.value: count for source, count in by_source}

        # AI-ready count
        ai_ready = (
            self.db.query(func.count(Dataset.id))
            .filter(Dataset.ai_ready == True)
            .scalar()
        )

        # Total size
        total_size_bytes = self.db.query(func.sum(Dataset.size_bytes)).scalar() or 0
        total_size_gb = total_size_bytes / (1024**3)

        return {
            "total_datasets": total or 0,
            "datasets_by_source": datasets_by_source,
            "ai_ready_count": ai_ready or 0,
            "total_size_gb": round(total_size_gb, 2),
        }

    async def fetch_dataset_data(
        self, dataset_id: int, format: str = "json", filters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Fetch dataset data from source

        Args:
            dataset_id: Dataset ID
            format: Desired output format (json, csv, parquet)
            filters: Optional filters

        Returns:
            Dataset data in requested format
        """
        dataset = self.db.query(Dataset).filter(Dataset.id == dataset_id).first()

        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_id}")

        collector = self.collectors.get(dataset.source)
        if not collector:
            raise ValueError(f"No collector for source: {dataset.source}")

        # Fetch raw data
        raw_data = await collector.fetch_dataset_data(dataset.external_id, filters)

        # Transform data
        transformer = DataTransformer()

        if format == "json":
            return transformer.to_json(raw_data)
        elif format == "csv":
            return transformer.to_csv(raw_data)
        elif format == "parquet":
            return transformer.to_parquet(raw_data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def close_collectors(self):
        """Close all collectors"""
        for collector in self.collectors.values():
            await collector.close()
