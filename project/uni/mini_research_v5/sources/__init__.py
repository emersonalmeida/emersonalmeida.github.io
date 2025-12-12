"""
Fontes de dados
Melhoria #6: Padrão Strategy para fontes
"""

from .base import DataSource, DataSourceResult
from .suggest import SuggestSource
from .trends import TrendsSource
from .serp import SERPSource
from .youtube import YouTubeSource
from .stores import StoresSource

__all__ = [
    "DataSource", "DataSourceResult",
    "SuggestSource", "TrendsSource", "SERPSource",
    "YouTubeSource", "StoresSource"
]


