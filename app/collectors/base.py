"""
Base collector class for all data sources
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime


class BaseCollector(ABC):
    """
    Abstract base class for data collectors
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    @abstractmethod
    async def search_datasets(
        self, query: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for datasets

        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of dataset metadata dictionaries
        """
        pass

    @abstractmethod
    async def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific dataset

        Args:
            dataset_id: Unique identifier for the dataset

        Returns:
            Dictionary with dataset metadata
        """
        pass

    @abstractmethod
    async def fetch_dataset_data(
        self, dataset_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Fetch actual dataset data

        Args:
            dataset_id: Unique identifier for the dataset
            filters: Optional filters to apply

        Returns:
            Dataset data (format depends on source)
        """
        pass

    async def get_organizations(self) -> List[Dict[str, Any]]:
        """
        Get list of organizations providing datasets

        Returns:
            List of organization metadata
        """
        return []

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """
        Calculate data completeness score (0-1)

        Args:
            data: Dataset metadata

        Returns:
            Completeness score between 0 and 1
        """
        required_fields = ["title", "description", "format", "source_url"]
        present_fields = sum(1 for field in required_fields if data.get(field))
        return present_fields / len(required_fields)
