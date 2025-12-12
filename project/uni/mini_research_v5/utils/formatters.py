"""
Formatadores de dados
Melhoria #4: Mascarar dados sensíveis em logs
"""

import re
from datetime import datetime
from typing import Any, Optional

# Padrões para detectar dados sensíveis
SENSITIVE_PATTERNS = [
    (re.compile(r'AIza[0-9A-Za-z_-]{35}'), 'API_KEY'),  # Google API Key
    (re.compile(r'[0-9a-f]{32}'), 'HASH'),  # MD5 hash
    (re.compile(r'[0-9a-f]{40}'), 'SHA1'),  # SHA1 hash
    (re.compile(r'[0-9a-f]{64}'), 'SHA256'),  # SHA256 hash
    (re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'), 'CARD'),  # Credit card
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), 'SSN'),  # SSN
]


def mask_sensitive_data(text: str) -> str:
    """
    Mascara dados sensíveis em strings
    Melhoria #4: Logging seguro
    """
    if not isinstance(text, str):
        text = str(text)
    
    masked = text
    for pattern, mask_type in SENSITIVE_PATTERNS:
        if pattern.search(masked):
            masked = pattern.sub(f'[{mask_type}_MASKED]', masked)
    
    return masked


def format_number(value: Any, decimals: int = 2) -> str:
    """Formata número com separadores"""
    try:
        num = float(value)
        return f"{num:,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return str(value)


def format_date(date_str: Optional[str], format_in: str = "%Y-%m-%d", format_out: str = "%d/%m/%Y") -> str:
    """Formata data"""
    if not date_str:
        return ""
    
    try:
        dt = datetime.strptime(date_str, format_in)
        return dt.strftime(format_out)
    except (ValueError, TypeError):
        return str(date_str)


