"""
Validação e sanitização
Melhoria #3: Sanitização aprimorada
"""

import re
from typing import Any, Optional
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Whitelist de caracteres permitidos (melhoria #3)
ALLOWED_CHARS_PATTERN = re.compile(r'^[a-zA-Z0-9\sáàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ\-_.,!?;:()\[\]{}\'"@#$%&*+=/\\|<>~`]+$')


def sanitize_term(term: str, max_length: int = 200) -> str:
    """
    Sanitiza termo de busca com validação rigorosa
    
    Melhoria #3: Validação mais rigorosa e whitelist de caracteres
    """
    if not isinstance(term, str):
        term = str(term)
    
    # Remove caracteres problemáticos mas mantém acentos e espaços
    term = re.sub(r'[<>"\'\\]', '', term)
    term = term.strip()
    
    # Validação com whitelist
    if not ALLOWED_CHARS_PATTERN.match(term):
        logger.warning(f"Termo contém caracteres não permitidos: {term}")
        # Remove caracteres não permitidos
        term = re.sub(r'[^a-zA-Z0-9\sáàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ\-_.,!?;:()\[\]{}\'"@#$%&*+=/\\|<>~`]', '', term)
    
    # Limitar tamanho
    if len(term) > max_length:
        term = term[:max_length]
        logger.warning(f"Termo truncado para {max_length} caracteres")
    
    # Validar que não está vazio após sanitização
    if not term:
        raise ValueError("Termo não pode estar vazio após sanitização")
    
    return term


def validate_url(url: str) -> bool:
    """Valida se uma URL é válida"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_data(data: Any, source_name: str) -> bool:
    """Valida dados antes de processar"""
    if data is None:
        logger.warning(f"Dados de {source_name} são None")
        return False
    
    if isinstance(data, list):
        if len(data) == 0:
            logger.warning(f"Lista de {source_name} está vazia")
            return False
    
    elif isinstance(data, dict):
        if len(data) == 0:
            logger.warning(f"Dicionário de {source_name} está vazio")
            return False
    
    return True


