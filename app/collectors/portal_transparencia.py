"""
Collector for Portal da Transparência API
"""
from typing import List, Dict, Any, Optional
from app.collectors.base import BaseCollector
from config import settings
import logging

logger = logging.getLogger(__name__)


class PortalTransparenciaCollector(BaseCollector):
    """
    Collector for Portal da Transparência do Governo Federal
    Provides access to government spending, contracts, salaries, etc.
    """

    def __init__(self):
        super().__init__(settings.PORTAL_TRANSPARENCIA_BASE_URL)

    async def search_datasets(
        self, query: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Return predefined datasets from Portal da Transparência
        This API doesn't have a search endpoint, so we return known datasets
        """
        datasets = [
            {
                "external_id": "despesas",
                "title": "Despesas Públicas",
                "description": "Despesas realizadas pelo Governo Federal",
                "endpoint": "/despesas",
            },
            {
                "external_id": "receitas",
                "title": "Receitas Públicas",
                "description": "Receitas do Governo Federal",
                "endpoint": "/receitas",
            },
            {
                "external_id": "servidores",
                "title": "Servidores Públicos",
                "description": "Informações sobre servidores públicos federais",
                "endpoint": "/servidores",
            },
            {
                "external_id": "contratos",
                "title": "Contratos Públicos",
                "description": "Contratos firmados pelo Governo Federal",
                "endpoint": "/contratos",
            },
            {
                "external_id": "convenios",
                "title": "Convênios",
                "description": "Convênios e transferências voluntárias",
                "endpoint": "/convenios",
            },
            {
                "external_id": "empresas-sancionadas",
                "title": "Empresas Sancionadas",
                "description": "Empresas sancionadas e impedidas de contratar",
                "endpoint": "/empresas-sancionadas",
            },
        ]

        # Apply query filter if provided
        if query:
            query_lower = query.lower()
            datasets = [
                d for d in datasets
                if query_lower in d["title"].lower()
                or query_lower in d["description"].lower()
            ]

        # Apply pagination
        start = offset
        end = offset + limit
        datasets = datasets[start:end]

        return [self._normalize_dataset(d) for d in datasets]

    async def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get dataset details
        """
        datasets = await self.search_datasets()
        for dataset in datasets:
            if dataset.get("external_id") == dataset_id:
                return dataset

        raise ValueError(f"Dataset not found: {dataset_id}")

    async def fetch_dataset_data(
        self, dataset_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Fetch data from Portal da Transparência API

        Common filters:
        - mesAno: Month/Year (MM/YYYY)
        - codigoOrgao: Organization code
        - pagina: Page number
        """
        try:
            dataset = await self.get_dataset(dataset_id)
            endpoint = dataset.get("metadata", {}).get("endpoint")

            if not endpoint:
                raise ValueError(f"No endpoint found for dataset {dataset_id}")

            params = filters or {}
            params.setdefault("pagina", 1)

            response = await self.client.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Error fetching data from Portal da Transparência: {e}")
            raise

    def _normalize_dataset(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize dataset to internal format
        """
        return {
            "external_id": dataset.get("external_id"),
            "title": dataset.get("title"),
            "description": dataset.get("description"),
            "source": "portal_transparencia",
            "source_url": "https://portaldatransparencia.gov.br",
            "organization": "Controladoria-Geral da União (CGU)",
            "tags": ["transparência", "governo federal", "dados abertos"],
            "format": "json",
            "metadata": {
                "endpoint": dataset.get("endpoint"),
                "api_docs": "https://api.portaldatransparencia.gov.br/swagger-ui.html",
            },
        }
