"""
Interface base para fontes de dados
Melhoria #6: Padrão Strategy
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DataSourceResult:
    """Resultado padronizado de uma fonte de dados"""
    source_id: int
    source_name: str
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: datetime
    success: bool
    error: Optional[str] = None
    
    def __len__(self) -> int:
        return len(self.data)
    
    def is_empty(self) -> bool:
        return len(self.data) == 0


class DataSource(ABC):
    """
    Interface base para todas as fontes de dados
    Melhoria #6: Permite adicionar novas fontes facilmente
    """
    
    def __init__(self, source_id: int, source_name: str, config: Dict[str, Any]):
        self.source_id = source_id
        self.source_name = source_name
        self.config = config
    
    @abstractmethod
    def collect(self, term: str, output_dir: str, real_time_results: Dict) -> DataSourceResult:
        """
        Coleta dados da fonte
        
        Args:
            term: Termo de busca
            output_dir: Diretório de saída
            real_time_results: Dicionário para armazenar resultados em tempo real
        
        Returns:
            DataSourceResult com dados coletados
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Valida configuração da fonte"""
        pass
    
    def get_name(self) -> str:
        """Retorna nome da fonte"""
        return self.source_name
    
    def get_id(self) -> int:
        """Retorna ID da fonte"""
        return self.source_id


