"""
Google Suggest Source
Implementação usando padrão Strategy
"""

from typing import Dict, List, Any
from datetime import datetime
import time
import string
import requests
from functools import lru_cache

from .base import DataSource, DataSourceResult
from ..config.api_keys import get_api_key
from ..utils.validators import sanitize_term, validate_data
from ..utils.colors import *
from ..utils.formatters import mask_sensitive_data
import logging

logger = logging.getLogger(__name__)

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"

CATEGORIES = {
    1: ("Questões", ["o que ", "é ", "não é", "como ", "por que ", "onde ", "quando ", "qual ", "quanto "]),
    2: ("Preposições", ["de ", "para ", "com ", "sem ", "sobre ", "contra ", "até "]),
    3: ("Comparações", ["vs ", "melhor que ", "pior que ", "ou ", "e "]),
}

CLIENTS_MAP = {1: "chrome", 2: "firefox", 3: "safari", 4: "chrome"}
SOURCES_MAP = {1: "web", 2: "youtube", 3: "news", 4: "shopping"}
SOURCES_CODE_MAP = {"web": "", "youtube": "yt", "news": "n", "shopping": "sh"}


def make_session():
    """Cria sessão HTTP com retry"""
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    sess = requests.Session()
    sess.headers.update({"User-Agent": "Mozilla/5.0 Chrome/140.0"})
    
    try:
        retry = Retry(
            total=5,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
    except TypeError:
        try:
            retry = Retry(
                total=5,
                backoff_factor=0.3,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["GET"]
            )
        except TypeError:
            retry = Retry(
                total=5,
                backoff_factor=0.3,
                status_forcelist=[429, 500, 502, 503, 504]
            )
    
    sess.mount("https://", HTTPAdapter(max_retries=retry))
    return sess

SESSION = make_session()


@lru_cache(maxsize=512)
def get_suggestions(query: str, region: str = "br", client: str = "chrome", 
                   source: str = "", lang: str = "", limit: int = 10) -> List[tuple]:
    """Consulta API do Google Suggest com cache"""
    params = {"q": query, "gl": region, "client": client}
    if lang:
        params["hl"] = lang
    if source:
        params["ds"] = source
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            r = SESSION.get(SUGGEST_URL, params=params, timeout=8)
            r.raise_for_status()
            data = r.json()
            
            if not isinstance(data, list) or len(data) < 2:
                logger.warning(f"Resposta inválida do Google Suggest: {mask_sensitive_data(str(data))}")
                return []
            
            suggestions = data[1] if len(data) > 1 else []
            if not isinstance(suggestions, list):
                return []
            
            relevance = []
            if len(data) > 4 and isinstance(data[4], dict):
                relevance = data[4].get("google:suggestrelevance", [0]*len(suggestions))
            else:
                relevance = [0]*len(suggestions)
            
            if len(relevance) != len(suggestions):
                relevance = [0]*len(suggestions)
            
            max_possible = 1000
            limit_efetivo = min(limit, max_possible)
            return list(zip(suggestions, relevance))[:limit_efetivo]
        
        except Exception as e:
            logger.error(f"Erro ao buscar sugestões (tentativa {attempt+1}/{max_retries}): {mask_sensitive_data(str(e))}")
            if attempt < max_retries - 1:
                time.sleep(0.5 * (attempt + 1))
                continue
            return []
    
    return []


class SuggestSource(DataSource):
    """Fonte de dados Google Suggest"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(1, "Google Suggest", config)
    
    def validate_config(self) -> bool:
        """Valida configuração"""
        required = ["regions", "clients", "sources", "opcoes", "limit"]
        return all(key in self.config for key in required)
    
    def collect(self, term: str, output_dir: str, real_time_results: Dict) -> DataSourceResult:
        """Coleta sugestões do Google"""
        try:
            term = sanitize_term(term)
            regions = self.config.get("regions", ["br"])
            clients = [CLIENTS_MAP.get(c, "chrome") for c in self.config.get("clients", [1])]
            sources = [SOURCES_MAP.get(s, "web") for s in self.config.get("sources", [1])]
            opcoes = self.config.get("opcoes", [1])
            limit = self.config.get("limit", 15)
            delay = self.config.get("delay", 1.0)
            
            resultados = []
            
            for region in regions:
                for client in clients:
                    for source_name in sources:
                        source_code = SOURCES_CODE_MAP.get(source_name, "")
                        
                        if 1 in opcoes:  # Top sugestões
                            sugs = get_suggestions(term, region, client, source_code, "", limit)
                            for s, r in sugs:
                                item = {
                                    "termo": term,
                                    "sugestao": s,
                                    "relevancia": r,
                                    "regiao": region,
                                    "cliente": client,
                                    "fonte": source_name,
                                    "tipo": "top"
                                }
                                resultados.append(item)
                                real_time_results["suggest"].append(item)
                            time.sleep(delay)
                        
                        if 2 in opcoes:  # A-Z
                            for letter in string.ascii_lowercase:
                                q = f"{term} {letter}"
                                sugs = get_suggestions(q, region, client, source_code, "", limit)
                                for s, r in sugs:
                                    item = {
                                        "termo": term,
                                        "sugestao": s,
                                        "relevancia": r,
                                        "regiao": region,
                                        "cliente": client,
                                        "fonte": source_name,
                                        "tipo": f"expansao_{letter}"
                                    }
                                    resultados.append(item)
                                    real_time_results["suggest"].append(item)
                                time.sleep(delay * 0.3)
            
            if not validate_data(resultados, "Google Suggest"):
                return DataSourceResult(
                    source_id=1,
                    source_name="Google Suggest",
                    data=[],
                    metadata={},
                    timestamp=datetime.now(),
                    success=False,
                    error="Dados inválidos"
                )
            
            return DataSourceResult(
                source_id=1,
                source_name="Google Suggest",
                data=resultados,
                metadata={"total": len(resultados)},
                timestamp=datetime.now(),
                success=True
            )
        
        except Exception as e:
            logger.error(f"Erro ao coletar Google Suggest: {mask_sensitive_data(str(e))}", exc_info=True)
            return DataSourceResult(
                source_id=1,
                source_name="Google Suggest",
                data=[],
                metadata={},
                timestamp=datetime.now(),
                success=False,
                error=str(e)
            )


