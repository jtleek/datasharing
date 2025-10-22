"""
Collector for IBGE (Brazilian Institute of Geography and Statistics) API
"""
from typing import List, Dict, Any, Optional
from app.collectors.base import BaseCollector
from config import settings
import logging

logger = logging.getLogger(__name__)


class IBGECollector(BaseCollector):
    """
    Collector for IBGE statistical data and geographic information
    """

    def __init__(self):
        super().__init__(settings.IBGE_API_BASE_URL)

    async def search_datasets(
        self, query: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Return available IBGE datasets/APIs
        """
        datasets = [
            {
                "external_id": "localidades",
                "title": "Localidades",
                "description": "Informações geográficas sobre estados, municípios, regiões",
                "endpoint": "/localidades",
            },
            {
                "external_id": "agregados",
                "title": "Agregados",
                "description": "Dados agregados de pesquisas do IBGE (SIDRA)",
                "endpoint": "/agregados",
            },
            {
                "external_id": "malhas",
                "title": "Malhas Territoriais",
                "description": "Malhas geográficas em diversos formatos",
                "endpoint": "/malhas",
            },
            {
                "external_id": "noticias",
                "title": "Notícias",
                "description": "Notícias e releases do IBGE",
                "endpoint": "/noticias",
            },
            {
                "external_id": "populacao",
                "title": "População",
                "description": "Dados populacionais e projeções",
                "endpoint": "/agregados",
                "metadata": {"tipo": "população"},
            },
            {
                "external_id": "economia",
                "title": "Indicadores Econômicos",
                "description": "Indicadores econômicos (PIB, inflação, etc.)",
                "endpoint": "/agregados",
                "metadata": {"tipo": "economia"},
            },
        ]

        if query:
            query_lower = query.lower()
            datasets = [
                d for d in datasets
                if query_lower in d["title"].lower()
                or query_lower in d["description"].lower()
            ]

        start = offset
        end = offset + limit
        datasets = datasets[start:end]

        return [self._normalize_dataset(d) for d in datasets]

    async def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get IBGE dataset details
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
        Fetch data from IBGE API
        """
        try:
            dataset = await self.get_dataset(dataset_id)
            endpoint = dataset.get("metadata", {}).get("endpoint")

            if not endpoint:
                raise ValueError(f"No endpoint found for dataset {dataset_id}")

            params = filters or {}

            # Special handling for different endpoints
            if dataset_id == "localidades":
                # Get all states
                url = f"{self.base_url}/localidades/estados"
            elif dataset_id in ["populacao", "economia"]:
                # For aggregated data, we need specific aggregate ID
                aggregate_id = params.get("agregado_id", "1")
                url = f"{self.base_url}/agregados/{aggregate_id}/periodos/-1/variaveis"
            else:
                url = f"{self.base_url}{endpoint}"

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Error fetching data from IBGE: {e}")
            raise

    async def get_estados(self) -> List[Dict[str, Any]]:
        """
        Get list of Brazilian states
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/localidades/estados"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching estados: {e}")
            return []

    async def get_municipios(self, uf: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of municipalities, optionally filtered by state
        """
        try:
            url = f"{self.base_url}/localidades"
            if uf:
                url += f"/estados/{uf}/municipios"
            else:
                url += "/municipios"

            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching municípios: {e}")
            return []

    def _normalize_dataset(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize IBGE dataset to internal format
        """
        return {
            "external_id": dataset.get("external_id"),
            "title": dataset.get("title"),
            "description": dataset.get("description"),
            "source": "ibge",
            "source_url": "https://www.ibge.gov.br",
            "organization": "Instituto Brasileiro de Geografia e Estatística (IBGE)",
            "tags": ["ibge", "estatística", "geografia", "brasil"],
            "format": "json",
            "metadata": {
                "endpoint": dataset.get("endpoint"),
                "api_docs": "https://servicodados.ibge.gov.br/api/docs",
                **dataset.get("metadata", {}),
            },
        }
