"""
Data collectors for various Brazilian federal data sources
"""
from app.collectors.base import BaseCollector
from app.collectors.dados_gov_br import DadosGovBrCollector
from app.collectors.portal_transparencia import PortalTransparenciaCollector
from app.collectors.ibge import IBGECollector

__all__ = [
    "BaseCollector",
    "DadosGovBrCollector",
    "PortalTransparenciaCollector",
    "IBGECollector",
]
