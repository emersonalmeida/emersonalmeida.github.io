"""
Configurações e carregamento de settings
Melhoria #7: Configuração via arquivo YAML/JSON
"""

import os
import json
import yaml
from typing import Dict, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Settings:
    """Gerencia configurações da aplicação"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config: Dict[str, Any] = {}
        self.config_file = config_file
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        else:
            self._load_defaults()
    
    def _load_defaults(self):
        """Carrega configurações padrão"""
        self.config = {
            "base_dir": "dados",
            "delay": 1.0,
            "timeout": 30,
            "max_retries": 3,
            "backoff_factor": 0.3,
            "cache_enabled": True,
            "cache_ttl": 3600,
            "export_formats": ["csv", "json"],
            "quiet_mode": False,
            "verbose_mode": False,
            "proxy": None,
            "notifications": {
                "enabled": False,
                "email": None,
                "slack_webhook": None
            }
        }
    
    def load_from_file(self, filepath: str):
        """Carrega configuração de arquivo YAML ou JSON"""
        path = Path(filepath)
        
        if not path.exists():
            logger.warning(f"Arquivo de configuração não encontrado: {filepath}")
            return
        
        try:
            if path.suffix.lower() in ['.yaml', '.yml']:
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f) or {}
            elif path.suffix.lower() == '.json':
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
            else:
                logger.error(f"Formato de arquivo não suportado: {filepath}")
                return
            
            # Merge com defaults
            self._load_defaults()
            self._deep_update(self.config, file_config)
            self.config_file = filepath
            logger.info(f"Configuração carregada de {filepath}")
        
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
    
    def _deep_update(self, base: Dict, update: Dict):
        """Atualiza dicionário recursivamente"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Define valor de configuração"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_to_file(self, filepath: Optional[str] = None):
        """Salva configuração em arquivo"""
        filepath = filepath or self.config_file
        if not filepath:
            logger.error("Nenhum arquivo especificado para salvar configuração")
            return
        
        path = Path(filepath)
        try:
            if path.suffix.lower() in ['.yaml', '.yml']:
                with open(filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            elif path.suffix.lower() == '.json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
            else:
                logger.error(f"Formato não suportado: {filepath}")
                return
            
            logger.info(f"Configuração salva em {filepath}")
        
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")


def load_config(config_file: Optional[str] = None) -> Settings:
    """Carrega configuração de arquivo ou cria padrão"""
    # Tenta carregar de arquivo padrão
    default_files = [
        "mini_research_config.yaml",
        "mini_research_config.yml",
        "mini_research_config.json",
        os.path.expanduser("~/.mini_research_config.yaml"),
        os.path.expanduser("~/.mini_research_config.json"),
    ]
    
    if not config_file:
        for filepath in default_files:
            if os.path.exists(filepath):
                config_file = filepath
                break
    
    return Settings(config_file)


