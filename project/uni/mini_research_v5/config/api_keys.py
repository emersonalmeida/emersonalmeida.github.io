"""
Gerenciamento seguro de API Keys
Melhoria #1: Remover API keys hardcoded e implementar rotação
"""

import os
import logging
from typing import Optional, List, Dict
from secrets import compare_digest

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Gerencia API keys de forma segura com rotação"""
    
    def __init__(self):
        self._keys: Dict[str, List[str]] = {}
        self._current_index: Dict[str, int] = {}
        self._load_keys()
    
    def _load_keys(self):
        """Carrega API keys de variáveis de ambiente"""
        # Google API
        google_keys = self._get_env_list("GOOGLE_API_KEY")
        if google_keys:
            self._keys["google"] = google_keys
            self._current_index["google"] = 0
        
        # Google CX
        google_cx = os.getenv("GOOGLE_CX")
        if google_cx:
            self._keys["google_cx"] = [google_cx]
            self._current_index["google_cx"] = 0
        
        # Brave API
        brave_keys = self._get_env_list("BRAVE_API_KEY")
        if brave_keys:
            self._keys["brave"] = brave_keys
            self._current_index["brave"] = 0
        
        # SERP API
        serp_keys = self._get_env_list("SERPAPI_KEY")
        if serp_keys:
            self._keys["serpapi"] = serp_keys
            self._current_index["serpapi"] = 0
        
        # YouTube API
        youtube_keys = self._get_env_list("YOUTUBE_API_KEY")
        if youtube_keys:
            self._keys["youtube"] = youtube_keys
            self._current_index["youtube"] = 0
    
    def _get_env_list(self, base_name: str) -> List[str]:
        """Obtém lista de keys de variáveis de ambiente"""
        keys = []
        # Tenta base_name
        key = os.getenv(base_name)
        if key:
            keys.append(key)
        
        # Tenta base_name_1, base_name_2, etc.
        i = 1
        while True:
            env_name = f"{base_name}_{i}"
            key = os.getenv(env_name)
            if not key:
                break
            keys.append(key)
            i += 1
        
        return keys
    
    def get_key(self, service: str, rotate: bool = False) -> Optional[str]:
        """
        Obtém API key para um serviço
        
        Args:
            service: Nome do serviço (google, brave, serpapi, youtube)
            rotate: Se True, rotaciona para próxima key
        
        Returns:
            API key ou None se não disponível
        """
        if service not in self._keys or not self._keys[service]:
            logger.warning(f"Nenhuma API key configurada para {service}")
            return None
        
        keys = self._keys[service]
        index = self._current_index.get(service, 0)
        
        if rotate and len(keys) > 1:
            # Rotaciona para próxima key
            index = (index + 1) % len(keys)
            self._current_index[service] = index
            logger.info(f"Rotacionando {service} key para índice {index}")
        
        return keys[index]
    
    def validate_key(self, service: str, key: str) -> bool:
        """Valida se uma key está configurada"""
        if service not in self._keys:
            return False
        return any(compare_digest(k, key) for k in self._keys[service])
    
    def get_status(self) -> Dict[str, bool]:
        """Retorna status de todas as API keys"""
        return {
            "google": "google" in self._keys and len(self._keys["google"]) > 0,
            "google_cx": "google_cx" in self._keys and len(self._keys["google_cx"]) > 0,
            "brave": "brave" in self._keys and len(self._keys["brave"]) > 0,
            "serpapi": "serpapi" in self._keys and len(self._keys["serpapi"]) > 0,
            "youtube": "youtube" in self._keys and len(self._keys["youtube"]) > 0,
        }
    
    def rotate_key(self, service: str) -> Optional[str]:
        """Força rotação de key para um serviço"""
        return self.get_key(service, rotate=True)


# Instância global
_key_manager = APIKeyManager()


def get_api_key(service: str, rotate: bool = False) -> Optional[str]:
    """Função helper para obter API key"""
    return _key_manager.get_key(service, rotate)


def validate_api_keys() -> Dict[str, bool]:
    """Valida disponibilidade de todas as API keys"""
    return _key_manager.get_status()


