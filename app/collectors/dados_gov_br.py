"""
Collector for dados.gov.br (CKAN-based portal)
"""
from typing import List, Dict, Any, Optional
from app.collectors.base import BaseCollector
from config import settings
import logging

logger = logging.getLogger(__name__)


class DadosGovBrCollector(BaseCollector):
    """
    Collector for Brazilian Open Data Portal (dados.gov.br)
    Uses CKAN API
    """

    def __init__(self):
        super().__init__(settings.DADOS_GOV_BR_BASE_URL)
        self.api_url = f"{self.base_url}/api/3/action"

    async def search_datasets(
        self, query: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search datasets using CKAN package_search API
        """
        try:
            params = {
                "rows": limit,
                "start": offset,
            }
            if query:
                params["q"] = query

            response = await self.client.get(
                f"{self.api_url}/package_search", params=params
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                logger.error(f"CKAN API returned success=false: {data}")
                return []

            results = data.get("result", {}).get("results", [])
            return [self._normalize_dataset(dataset) for dataset in results]

        except Exception as e:
            logger.error(f"Error searching datasets on dados.gov.br: {e}")
            return []

    async def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get dataset details using CKAN package_show API
        """
        try:
            params = {"id": dataset_id}
            response = await self.client.get(
                f"{self.api_url}/package_show", params=params
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                raise ValueError(f"Dataset not found: {dataset_id}")

            return self._normalize_dataset(data.get("result", {}))

        except Exception as e:
            logger.error(f"Error fetching dataset {dataset_id}: {e}")
            raise

    async def fetch_dataset_data(
        self, dataset_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Fetch actual dataset data from resources
        """
        try:
            dataset = await self.get_dataset(dataset_id)
            resources = dataset.get("resources", [])

            if not resources:
                raise ValueError(f"No resources found for dataset {dataset_id}")

            # Get the first CSV or JSON resource
            for resource in resources:
                format_type = resource.get("format", "").lower()
                if format_type in ["csv", "json"]:
                    url = resource.get("url")
                    if url:
                        response = await self.client.get(url)
                        response.raise_for_status()

                        if format_type == "json":
                            return response.json()
                        else:
                            return response.text

            raise ValueError("No compatible resource format found (CSV or JSON)")

        except Exception as e:
            logger.error(f"Error fetching data for dataset {dataset_id}: {e}")
            raise

    async def get_organizations(self) -> List[Dict[str, Any]]:
        """
        Get list of organizations from CKAN
        """
        try:
            response = await self.client.get(f"{self.api_url}/organization_list")
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                return data.get("result", [])
            return []

        except Exception as e:
            logger.error(f"Error fetching organizations: {e}")
            return []

    def _normalize_dataset(self, ckan_dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize CKAN dataset format to our internal format
        """
        resources = ckan_dataset.get("resources", [])
        total_size = sum(
            int(r.get("size", 0)) for r in resources if r.get("size")
        )

        return {
            "external_id": ckan_dataset.get("id") or ckan_dataset.get("name"),
            "title": ckan_dataset.get("title") or ckan_dataset.get("name"),
            "description": ckan_dataset.get("notes", ""),
            "source": "dados_gov_br",
            "source_url": f"{self.base_url}/dataset/{ckan_dataset.get('name')}",
            "organization": ckan_dataset.get("organization", {}).get("title"),
            "tags": [tag.get("name") for tag in ckan_dataset.get("tags", [])],
            "format": resources[0].get("format") if resources else None,
            "size_bytes": total_size if total_size > 0 else None,
            "last_updated_source": self._parse_datetime(
                ckan_dataset.get("metadata_modified")
            ),
            "metadata": {
                "author": ckan_dataset.get("author"),
                "maintainer": ckan_dataset.get("maintainer"),
                "license": ckan_dataset.get("license_title"),
                "resources_count": len(resources),
                "resources": [
                    {
                        "id": r.get("id"),
                        "name": r.get("name"),
                        "format": r.get("format"),
                        "url": r.get("url"),
                    }
                    for r in resources
                ],
            },
        }
