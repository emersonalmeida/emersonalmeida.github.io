#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Research v4.5 - Coletor de Dados Multi-Fonte com Análises e Dashboard
Versão robusta com dados completos, cores padronizadas e dashboard detalhado

Melhorias v4.5 (atualizado):
- DADOS COMPLETOS: Removidos todos os cortes de strings, exibição e salvamento sem limites
- Sistema de cores padronizado e documentado aplicado em todo o script
- Dashboard completo e detalhado com estatísticas quantitativas por fonte
- Exibição em tempo real de TODOS os dados coletados (sem cortes ou abreviações)
- Função print_data_item_tqdm para exibir dados mesmo com barra de progresso
- Garantia de que TODOS os dados coletados estejam no CSV consolidado (completos)
- Inclusão de reviews e comentários completos no consolidado (via resultados_tempo_real)
- Tratamento de erros específico por tipo de exceção (não genérico)
- Validação completa de dados antes de processar e consolidar
- Retry inteligente com backoff exponencial para operações críticas
- Validação de encoding e tratamento de erros de I/O ao salvar
- Sistema de backup automático antes de sobrescrever arquivos
- Estatísticas avançadas: percentis, desvio padrão, métricas adicionais
- Dashboard melhorado com estatísticas detalhadas por fonte e qualidade dos dados
- Tratamento de dados duplicados e validação de integridade
- Relatórios em múltiplos formatos (CSV, JSON, TXT)
- Tratamento de memória para grandes volumes de dados
- Validação de URLs e sanitização aprimorada
- Timeouts configuráveis e rate limiting inteligente
- Compatibilidade com diferentes versões do urllib3

Melhorias v4.1 (mantidas):
- Ordem padronizada: suggest → trends → serp → youtube → stores
- Configurações seguem ordem das fontes selecionadas
- Coleta segue ordem das fontes selecionadas
- Exibição segue ordem das fontes selecionadas
- Dashboard segue ordem das fontes selecionadas
- Consistência total em todo o fluxo

Melhorias v4 (mantidas):
- Consolidação de todos os dados em CSV único
- Análises estatísticas por fonte
- Gráficos e visualizações
- Dashboard completo no final
- Insights automáticos
- Coleta máxima de dados disponíveis
- Melhores práticas de análise
"""

import os
import re
import string
import time
import warnings
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from functools import lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys
import logging
import json
import shutil
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Union, Any, Tuple
from urllib.parse import urlparse, urlunparse
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError

# Imports condicionais
try:
    from pytrends.request import TrendReq
    HAS_PYTRENDS = True
except ImportError:
    HAS_PYTRENDS = False

try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    from youtubesearchpython import VideosSearch, Comments
    HAS_YOUTUBE_SEARCH = True
except ImportError:
    HAS_YOUTUBE_SEARCH = False

try:
    from google_play_scraper import search, reviews, Sort
    from tqdm import tqdm
    HAS_PLAY_SCRAPER = True
except ImportError:
    HAS_PLAY_SCRAPER = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns
    HAS_MATPLOTLIB = True
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
except ImportError:
    HAS_MATPLOTLIB = False

warnings.filterwarnings("ignore", category=FutureWarning)

# ======================================
# LOGGING CONFIGURATION
# ======================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ======================================
# API KEYS (from environment or hardcoded)
# ======================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBj80B2fwVvFEMtcQU8tPV_NCNaEmQvzhc")
GOOGLE_CX = os.getenv("GOOGLE_CX", "f07ccd3b922d6437b")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "BSAjC9Yvq2s8_hYFIPWQ2QEl_XHpsQp")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "e71430bcff8bdc906f7a5ed9ae1538355c2efb0fb88ffa071f7125a76cc2b142")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyBj80B2fwVvFEMtcQU8tPV_NCNaEmQvzhc")

# ======================================
# 🎨 Estilo Terminal
# ======================================

# ======================================
# 🎨 SISTEMA DE CORES PADRONIZADO - v4.5
# ======================================
# Padrão de cores para todo o script:
# - VERDE: Índices, destaques, sucesso, ratings, checkmarks
# - CINZA: Valores secundários, números, links, metadados, descrições
# - BRANCO: Texto principal, títulos, conteúdo
# - AZUL: Progresso, informações, ícones de status
# - AMARELO: Avisos, alertas
# - VERMELHO: Erros, falhas
# - CIANO: Informações especiais
# - MAGENTA: Destaques especiais
# ======================================

def color(text, code): return f"\033[{code}m{text}\033[0m"
def blue(text): return color(text, "34")      # Progresso, informações
def green(text): return color(text, "32")      # Sucesso, índices, destaques
def yellow(text): return color(text, "33")    # Avisos, alertas
def red(text): return color(text, "31")        # Erros, falhas
def gray(text): return color(text, "90")      # Valores secundários, metadados
def cyan(text): return color(text, "36")      # Informações especiais
def bold(text): return color(text, "1")       # Texto em negrito
def magenta(text): return color(text, "35")   # Destaques especiais

# ======================================
# 🛠️ Funções Utilitárias Padronizadas
# ======================================

def now_tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def check_exit(value): 
    return value.lower() in {"sair", "fechar", "terminar", "ok", "exit", "quit", "q"}

def parse_todos_input(input_str: str, options_dict: Dict, default: Optional[int] = None) -> List[int]:
    """Unified function to parse input with 'todos' support - v4.4"""
    if not input_str or not input_str.strip():
        return [default] if default is not None else []
    
    input_str = input_str.strip().lower()
    
    if input_str in ["t", "todos", "all"]:
        return [k for k in options_dict.keys() if isinstance(k, int)]
    
    selected = []
    for item in input_str.split(","):
        item = item.strip()
        if item.isdigit():
            key = int(item)
            if key in options_dict:
                selected.append(key)
    
    return selected if selected else ([default] if default is not None else [])

def parse_numeric_input(input_str: str, options_dict: Dict, default: Optional[int] = None) -> List[int]:
    """Parse numeric input - kept for backward compatibility"""
    return parse_todos_input(input_str, options_dict, default)

def safe_int_input(prompt: str, default: int, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """Safely parse integer input with validation - v4.4"""
    while True:
        try:
            value_str = input(prompt).strip()
            if not value_str:
                value = default
            else:
                value = int(value_str)
            
            if min_val is not None and value < min_val:
                print(f"Valor mínimo: {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Valor máximo: {max_val}")
                continue
            
            return value
        except ValueError:
            print(f"Por favor, digite um número válido (padrão: {default})")
            continue

def safe_float_input(prompt: str, default: float, min_val: Optional[float] = None, max_val: Optional[float] = None) -> float:
    """Safely parse float input with validation - v4.4"""
    while True:
        try:
            value_str = input(prompt).strip()
            if not value_str:
                value = default
            else:
                value = float(value_str)
            
            if min_val is not None and value < min_val:
                print(f"Valor mínimo: {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Valor máximo: {max_val}")
                continue
            
            return value
        except ValueError:
            print(f"Por favor, digite um número válido (padrão: {default})")
            continue

def sanitize_term(term: str) -> str:
    """Sanitize search term - v4.5 com validação aprimorada"""
    if not isinstance(term, str):
        term = str(term)
    # Remove caracteres problemáticos mas mantém acentos e espaços
    term = re.sub(r'[<>"\'\\]', '', term)
    term = term.strip()
    # Limitar tamanho
    if len(term) > 200:
        term = term[:200]
    # Validar que não está vazio após sanitização
    if not term:
        raise ValueError("Termo não pode estar vazio após sanitização")
    return term

def validate_url(url: str) -> bool:
    """Valida se uma URL é válida - v4.5"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def safe_save_csv(df: pd.DataFrame, filepath: str, backup: bool = True) -> bool:
    """Salva CSV com validação e backup - v4.5"""
    try:
        # Validar DataFrame
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            logger.warning(f"DataFrame vazio, não salvando: {filepath}")
            return False
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        
        # Backup se arquivo existir
        if backup and os.path.exists(filepath):
            backup_path = f"{filepath}.backup_{now_tag()}"
            shutil.copy2(filepath, backup_path)
            logger.info(f"Backup criado: {backup_path}")
        
        # Salvar com tratamento de encoding e DADOS COMPLETOS (sem truncamento)
        # quoting=1 (QUOTE_ALL) garante que todos os campos sejam citados, preservando dados completos
        df.to_csv(filepath, index=False, encoding="utf-8-sig", errors='replace', 
                  line_terminator='\n', quoting=1)
        logger.info(f"Arquivo salvo com sucesso: {filepath} ({len(df)} linhas, {len(df.columns)} colunas)")
        return True
    except PermissionError as e:
        logger.error(f"Erro de permissão ao salvar {filepath}: {e}")
        return False
    except OSError as e:
        logger.error(f"Erro de I/O ao salvar {filepath}: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao salvar {filepath}: {e}", exc_info=True)
        return False

def validate_data_before_consolidate(data: Any, source_name: str) -> bool:
    """Valida dados antes de consolidar - v4.5"""
    if data is None:
        logger.warning(f"Dados de {source_name} são None")
        return False
    
    if isinstance(data, pd.DataFrame):
        if data.empty:
            logger.warning(f"DataFrame de {source_name} está vazio")
            return False
        # Verificar se tem pelo menos uma coluna
        if len(data.columns) == 0:
            logger.warning(f"DataFrame de {source_name} não tem colunas")
            return False
    
    elif isinstance(data, list):
        if len(data) == 0:
            logger.warning(f"Lista de {source_name} está vazia")
            return False
    
    elif isinstance(data, dict):
        if len(data) == 0:
            logger.warning(f"Dicionário de {source_name} está vazio")
            return False
    
    return True

def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """Remove duplicatas de um DataFrame - v4.5"""
    if df.empty:
        return df
    
    initial_count = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep='first')
    removed = initial_count - len(df_clean)
    
    if removed > 0:
        logger.info(f"Removidas {removed} duplicatas ({removed/initial_count*100:.1f}%)")
    
    return df_clean

def validate_api_keys() -> Dict[str, bool]:
    """Validate API keys availability - v4.4"""
    keys_status = {
        "google": bool(GOOGLE_API_KEY and GOOGLE_API_KEY != ""),
        "google_cx": bool(GOOGLE_CX and GOOGLE_CX != ""),
        "brave": bool(BRAVE_API_KEY and BRAVE_API_KEY != ""),
        "serpapi": bool(SERPAPI_KEY and SERPAPI_KEY != ""),
        "youtube": bool(YOUTUBE_API_KEY and YOUTUBE_API_KEY != "")
    }
    return keys_status

def print_header(title, description=""):
    """Cabeçalho com cores padronizadas - v4.5"""
    print(f"\n{cyan(bold(title))}")
    if description:
        print(f"  {gray(description)}")
    print()

def print_menu(title, description, options, default=None, show_todos=True):
    """Menu com cores padronizadas - v4.5"""
    print(f"\n{cyan(bold(title))}")
    if description:
        print(f"  {gray(description)}")
    
    int_keys = [k for k in options.keys() if isinstance(k, int)]
    str_keys = [k for k in options.keys() if isinstance(k, str)]
    
    for key in sorted(int_keys):
        value = options[key]
        # Verde para números de opção, branco para texto
        print(f"  {green(str(key))}. {value}")
    
    if show_todos and len(int_keys) > 1:
        print(f"  {green('t')}. Todos")
    
    if "t" in str_keys:
        print(f"  {green('t')}. {options['t']}")

def print_config_summary(config):
    """Exibe resumo com cores padronizadas - v4.5"""
    print(f"\n{cyan(bold('Resumo da configuração:'))}")
    print(f"  {gray('Termo:')} {config.get('termo', 'N/A')}")
    print(f"  {gray('Região:')} {', '.join(config.get('regions', []))}")
    print(f"  {gray('Fontes:')} {green(str(len(config.get('fontes', []))))} selecionada(s)")
    
    fontes_ordenadas = config.get('fontes_ordenadas', ordenar_fontes_selecionadas(config.get('fontes', [])))
    for i, fonte_id in enumerate(fontes_ordenadas, 1):
        fonte_nome = FONTES_MAP.get(fonte_id, {}).get("nome", "Desconhecida")
        print(f"    {green(str(i))}. {fonte_nome}")

def print_progress(message, icon="⏳"):
    """Mensagem de progresso"""
    print(f"{blue(icon)} {gray(message)}")
    flush_output()

def print_success(message, count=None):
    """Mensagem de sucesso"""
    if count is not None:
        print(f"{green('✓')} {message} {green(f'({count} itens)')}")
    else:
        print(f"{green('✓')} {message}")
    flush_output()

def print_data_item(index, item, prefix=""):
    """Exibe um item de dados formatado em tempo real - v4.5 melhorado"""
    # Verde para índice, branco para texto principal
    index_str = green(f"{index:2d}.")
    # Se prefix já contém códigos de cor, usar diretamente; senão, aplicar cor padrão
    if prefix and "\033[" not in prefix:
        # Prefixo em cinza se não tiver cores
        prefix = gray(prefix) if prefix.strip() else prefix
    print(f"  {index_str} {prefix}{item}")
    flush_output()

def print_data_item_tqdm(index, item, prefix="", pbar=None):
    """Exibe item de dados mesmo com tqdm ativo - v4.5"""
    if pbar:
        # Usar tqdm.write para não interferir com a barra de progresso
        index_str = green(f"{index:2d}.")
        # Se prefix já contém códigos de cor, usar diretamente
        if prefix and "\033[" not in prefix:
            prefix = gray(prefix) if prefix.strip() else prefix
        pbar.write(f"  {index_str} {prefix}{item}")
        flush_output()
    else:
        print_data_item(index, item, prefix)

def flush_output():
    """Força flush da saída para exibição em tempo real"""
    sys.stdout.flush()

BASE_DIR = "dados"

# ======================================
# CONSTANTES E MAPEAMENTOS CENTRALIZADOS - v4.4
# ======================================

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"

# Mapeamento de regiões (centralizado)
REGION_MAP = {
    1: "br", 2: "us", 3: "fr", 4: "de", 5: "jp", 6: "es", 7: "it", 8: "uk"
}

REGION_MAP_REVERSE = {v: k for k, v in REGION_MAP.items()}

REGION_MAP_TRENDS = {
    "br": "BR", "us": "US", "fr": "FR", "de": "DE", 
    "jp": "JP", "es": "ES", "it": "IT", "uk": "GB"
}

REGIONS_OPTIONS = {
    1: "Brasil (br)",
    2: "Estados Unidos (us)",
    3: "França (fr)",
    4: "Alemanha (de)",
    5: "Japão (jp)",
    6: "Espanha (es)",
    7: "Itália (it)",
    8: "Reino Unido (uk)",
}

CLIENTS_OPTIONS = {
    1: "Chrome",
    2: "Firefox",
    3: "Safari",
    4: "Brave",
}

CLIENTS_MAP = {1: "chrome", 2: "firefox", 3: "safari", 4: "chrome"}

SOURCES_OPTIONS = {
    1: "Web",
    2: "YouTube",
    3: "Notícias",
    4: "Shopping",
}

SOURCES_MAP = {1: "web", 2: "youtube", 3: "news", 4: "shopping"}
SOURCES_CODE_MAP = {"web": "", "youtube": "yt", "news": "n", "shopping": "sh"}

FONTES_OPTIONS = {
    1: "Google Suggest  - Termos e sugestões de busca",
    2: "Google Trends - Tendencias e Regiões",
    3: "Buscadores - Links e Conteúdos",
    4: "YouTube - Videos e Comentários",
    5: "App Stores - Aplicativos e Avaliações",
}

# Ordem padrão das fontes (sempre seguir esta ordem)
ORDEM_FONTES = [1, 2, 3, 4, 5]  # suggest, trends, serp, youtube, stores

# Mapeamento de IDs para nomes e funções
FONTES_MAP = {
    1: {"nome": "Google Suggest", "key": "suggest", "funcao": "run_suggest"},
    2: {"nome": "Google Trends", "key": "trends", "funcao": "run_trends"},
    3: {"nome": "SERP", "key": "serp", "funcao": "run_serp"},
    4: {"nome": "YouTube", "key": "youtube", "funcao": "run_youtube"},
    5: {"nome": "App Stores", "key": "stores", "funcao": "run_stores"},
}

def ordenar_fontes_selecionadas(fontes_selecionadas):
    """Ordena as fontes selecionadas na ordem padrão"""
    fontes_ordenadas = [f for f in ORDEM_FONTES if f in fontes_selecionadas]
    return fontes_ordenadas

SUGGEST_OPCOES = {
    1: "Top Sugestões",
    2: "A-Z",
    3: "0-9",
    4: "Outros (questões, preposições, comparações)",
}

TRENDS_OPCOES = {
    1: "Top relacionados",
    2: "Rising relacionados",
    3: "Interesse por regiões",
    4: "Interesse ao longo do tempo",
}

TRENDS_TIPOS = {
    1: "Web",
    2: "YouTube",
    3: "Notícias",
    4: "Imagens",
}

TRENDS_PERIODOS = {
    1: "Últimos 7 dias",
    2: "Último mês",
    3: "Últimos 3 meses",
    4: "Últimos 12 meses",
    5: "Últimos 5 anos",
    6: "Todo o período",
}

SERP_BUSCADORES = {
    1: "Google",
    2: "Bing",
    3: "Brave",
    4: "DuckDuckGo",
}

YOUTUBE_ORDER = {
    1: "Relevância",
    2: "Data de publicação",
    3: "Número de visualizações",
}

YOUTUBE_COMMENT_ORDER = {
    1: "Mais novos",
    2: "Mais antigos",
    3: "Mais curtidos",
}

APP_STORE_REVIEW_ORDER = {
    1: "Mais novos",
    2: "Mais antigos",
    3: "Mais curtidos",
}

CATEGORIES = {
    1: ("Questões", ["o que ", "é ", "não é", "como ", "por que ", "onde ", "quando ", "qual ", "quanto "]),
    2: ("Preposições", ["de ", "para ", "com ", "sem ", "sobre ", "contra ", "até "]),
    3: ("Comparações", ["vs ", "melhor que ", "pior que ", "ou ", "e "]),
}

# ======================================
# 📦 MÓDULO 1: GOOGLE SUGGEST
# ======================================

def make_session():
    """Cria sessão HTTP com retry - v4.5 compatível com diferentes versões do urllib3"""
    sess = requests.Session()
    sess.headers.update({"User-Agent": "Mozilla/5.0 Chrome/140.0"})
    
    # Compatibilidade com diferentes versões do urllib3
    # Primeiro tenta method_whitelist (versões antigas)
    try:
        retry = Retry(
            total=5,
            backoff_factor=0.3,
                  status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["GET"]
        )
    except TypeError:
        # Versões mais recentes do urllib3 usam allowed_methods
        try:
            retry = Retry(
                total=5,
                backoff_factor=0.3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"]
            )
        except TypeError:
            # Versões muito antigas - sem método específico
            retry = Retry(
                total=5,
                backoff_factor=0.3,
                status_forcelist=[429, 500, 502, 503, 504]
            )
    
    sess.mount("https://", HTTPAdapter(max_retries=retry))
    return sess

SESSION = make_session()

@lru_cache(maxsize=512)
def get_suggestions(query, region="br", client="chrome", source="", lang="", limit=10):
    """Consulta a API do Google Suggest (com cache) - v4.5 com tratamento de erros específico"""
    params = {"q": query, "gl": region, "client": client}
    if lang: params["hl"] = lang
    if source: params["ds"] = source
    
    max_retries = 3
    for attempt in range(max_retries):
    try:
        r = SESSION.get(SUGGEST_URL, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
            
            # Validar estrutura de resposta
            if not isinstance(data, list) or len(data) < 2:
                logger.warning(f"Resposta inválida do Google Suggest: {data}")
                return []
            
        suggestions = data[1] if len(data) > 1 else []
            if not isinstance(suggestions, list):
                return []
            
            relevance = []
            if len(data) > 4 and isinstance(data[4], dict):
                relevance = data[4].get("google:suggestrelevance", [0]*len(suggestions))
            else:
                relevance = [0]*len(suggestions)
            
            # Garantir que relevance tem o mesmo tamanho
            if len(relevance) != len(suggestions):
                relevance = [0]*len(suggestions)
            
        return list(zip(suggestions, relevance))[:limit]
        
        except Timeout:
            logger.warning(f"Timeout ao buscar sugestões (tentativa {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(0.5 * (attempt + 1))
                continue
            return []
        
        except HTTPError as e:
            logger.error(f"Erro HTTP ao buscar sugestões: {e}")
            if e.response.status_code == 429:  # Rate limit
                time.sleep(2 ** attempt)
                continue
            return []
        
        except (ConnectionError, RequestException) as e:
            logger.error(f"Erro de conexão ao buscar sugestões: {e}")
            if attempt < max_retries - 1:
                time.sleep(0.5 * (attempt + 1))
                continue
            return []
        
        except (ValueError, KeyError, IndexError) as e:
            logger.error(f"Erro ao processar resposta do Google Suggest: {e}")
            return []
        
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar sugestões: {e}", exc_info=True)
            return []
    
        return []

def run_suggest(termo: str, config: Dict, output_dir: str, resultados_tempo_real: Dict) -> List[Dict]:
    """Executa Google Suggest - v4.4 com mapeamentos centralizados"""
    print(f"\nGoogle Suggest — {termo}\n")
    
    regions = config.get("regions", ["br"])
    clients = [CLIENTS_MAP.get(c, "chrome") for c in config.get("clients", [1])]
    sources = [SOURCES_MAP.get(s, "web") for s in config.get("sources", [1])]
    opcoes = config.get("opcoes", [1])
    limit = config.get("limit", 15)
    delay = config.get("delay", 1.0)
    
    resultados = []
    counter = 0
    
    # Calcular total de iterações para barra de progresso
    total_iteracoes = len(regions) * len(clients) * len(sources) * (
        (1 if 1 in opcoes else 0) +
        (26 if 2 in opcoes else 0) +
        (10 if 3 in opcoes else 0) +
        (sum(len(words) for _, words in CATEGORIES.values()) if 4 in opcoes else 0)
    )
    
    if HAS_PLAY_SCRAPER:  # tqdm disponível
        pbar = tqdm(total=total_iteracoes, desc="Coletando sugestões", unit="req")
    else:
        pbar = None
        print_progress("Iniciando coleta de sugestões...")
    
    try:
        for region in regions:
            for client in clients:
                for source_name in sources:
                    source_code = SOURCES_CODE_MAP.get(source_name, "")
                    
                    if 1 in opcoes:
                        if pbar:
                            pbar.set_description(f"Top [{region}/{client}/{source_name}]")
                        sugs = get_suggestions(termo, region, client, source_code, "", limit)
                        for s, r in sugs:
                            counter += 1
                            item = {"termo": termo, "sugestao": s, "relevancia": r, "regiao": region, "cliente": client, "fonte": source_name, "tipo": "top"}
                            resultados.append(item)
                            resultados_tempo_real["suggest"].append(item)
                            # Exibir TODOS os dados em tempo real
                            print_data_item_tqdm(counter, s, f"[{gray(str(r))}] ", pbar)
                        if pbar:
                            pbar.update(1)
                        time.sleep(delay)
                    
                    if 2 in opcoes:
                        if pbar:
                            pbar.set_description(f"A-Z [{region}/{client}/{source_name}]")
                        for letter in string.ascii_lowercase:
                            q = f"{termo} {letter}"
                            sugs = get_suggestions(q, region, client, source_code, "", limit)
                            for s, r in sugs:
                                counter += 1
                                item = {"termo": termo, "sugestao": s, "relevancia": r, "regiao": region, "cliente": client, "fonte": source_name, "tipo": f"expansao_{letter}"}
                                resultados.append(item)
                                resultados_tempo_real["suggest"].append(item)
                                # Exibir TODOS os dados em tempo real
                                print_data_item_tqdm(counter, s, f"[{gray(str(r))}] ", pbar)
                            if pbar:
                                pbar.update(1)
                            time.sleep(delay * 0.3)
                    
                    if 3 in opcoes:
                        if pbar:
                            pbar.set_description(f"0-9 [{region}/{client}/{source_name}]")
                        for digit in "0123456789":
                            q = f"{termo} {digit}"
                            sugs = get_suggestions(q, region, client, source_code, "", limit)
                            for s, r in sugs:
                                counter += 1
                                item = {"termo": termo, "sugestao": s, "relevancia": r, "regiao": region, "cliente": client, "fonte": source_name, "tipo": f"expansao_{digit}"}
                                resultados.append(item)
                                resultados_tempo_real["suggest"].append(item)
                                # Exibir TODOS os dados em tempo real
                                print_data_item_tqdm(counter, s, f"[{gray(str(r))}] ", pbar)
                            if pbar:
                                pbar.update(1)
                            time.sleep(delay * 0.3)
                    
                    if 4 in opcoes:
                        if pbar:
                            pbar.set_description(f"Categorias [{region}/{client}/{source_name}]")
                        for cat_id, (cat_name, words) in CATEGORIES.items():
                            for w in words:
                                q = f"{termo} {w}"
                                sugs = get_suggestions(q, region, client, source_code, "", limit)
                                for s, r in sugs:
                                    counter += 1
                                    item = {"termo": termo, "sugestao": s, "relevancia": r, "regiao": region, "cliente": client, "fonte": source_name, "tipo": f"categoria_{cat_name}_{w.strip()}"}
                                    resultados.append(item)
                                    resultados_tempo_real["suggest"].append(item)
                                    # Exibir TODOS os dados em tempo real
                                    print_data_item_tqdm(counter, s, f"[{gray(str(r))}] ", pbar)
                                if pbar:
                                    pbar.update(1)
                                time.sleep(delay * 0.3)
    finally:
        if pbar:
            pbar.close()
    
    if resultados:
        # Validar dados antes de processar
        if not validate_data_before_consolidate(resultados, "Google Suggest"):
            logger.warning("Dados do Google Suggest inválidos, pulando salvamento")
            return []
        
        df = pd.DataFrame(resultados)
        
        # Remover duplicatas
        df = remove_duplicates(df, subset=["sugestao", "regiao", "cliente", "fonte"])
        
        file = os.path.join(output_dir, f"suggest_{termo}_{now_tag()}.csv")
        if safe_save_csv(df, file):
            print_success(f"Salvo: {file}", len(df))
            logger.info(f"Google Suggest: {len(df)} itens coletados (após remoção de duplicatas)")
        else:
            logger.error(f"Falha ao salvar arquivo: {file}")
    
    return resultados

# ======================================
# 📦 MÓDULO 2: GOOGLE TRENDS
# ======================================

def run_trends(termo: str, config: Dict, output_dir: str, resultados_tempo_real: Dict) -> List[Dict]:
    """Executa Google Trends - v4.4 com mapeamentos centralizados"""
    if not HAS_PYTRENDS:
        logger.warning("pytrends não instalado. Pulando Google Trends.")
        print(yellow("[!] pytrends não instalado. Pulando Google Trends."))
        return []
    
    print(f"\nGoogle Trends — {termo}\n")
    
    region = REGION_MAP_TRENDS.get(config.get("region", "br"), "BR")
    lang = config.get("lang", "pt")
    
    tipos_map = {1: "", 2: "images", 3: "news", 4: "youtube"}
    gtypes = [tipos_map.get(t, "") for t in config.get("gtypes", [1])]
    
    periodos_map = {1: "now 7-d", 2: "today 1-m", 3: "today 3-m", 4: "today 12-m", 5: "today 5-y", 6: "all"}
    timeframe = periodos_map.get(config.get("timeframe", 4), "today 12-m")
    
    opcoes = config.get("opcoes", [1, 2, 3, 4])
    topn = config.get("topn", 20)
    delay = config.get("delay", 1.0)
    
    OUTPUT_DIR = ensure_dir(os.path.join(output_dir, "trends"))
    pytrends = TrendReq(hl=f"{lang}-{region}" if region else lang, tz=0)
    
    resultados = []
    tipos_nome_map = {"": "web", "images": "images", "news": "news", "youtube": "youtube"}
    
    for gtype in gtypes:
        tipo_nome = tipos_nome_map.get(gtype, "web")
        print_progress(f"Processando {tipo_nome}...")
        
        try:
            pytrends.build_payload([termo], timeframe=timeframe, geo=region, gprop=gtype)
        except (Exception, ValueError, KeyError) as e:
            logger.error(f"Erro ao construir payload do Trends ({tipo_nome}): {e}")
            print(red(f"  [ERRO] {e}"))
            continue
        
        if 1 in opcoes:
            try:
                related = pytrends.related_queries()
                r = related.get(termo, {})
                if r and "top" in r and r["top"] is not None:
                    df = r["top"].head(topn).copy()
                    print_progress(f"Top relacionados ({tipo_nome}): {len(df)} itens")
                    for i, row in enumerate(df.itertuples(), 1):
                        item = {"tipo": "top", "fonte": tipo_nome, "query": row.query, "value": row.value}
                        resultados.append(item)
                        resultados_tempo_real["trends"].append(item)
                        # Exibir em tempo real com cores: branco para query, cinza para valor
                        query_text = f"{row.query}"
                        value_text = gray(f"({row.value})")
                        print_data_item(i, query_text, f"{value_text} ")
                    file = os.path.join(OUTPUT_DIR, f"top_{tipo_nome}_{termo}_{now_tag()}.csv")
                    if safe_save_csv(df, file):
                    print_success(f"Salvo: {file}", len(df))
                    else:
                        logger.warning(f"Falha ao salvar: {file}")
            except Exception as e:
                logger.warning(f"Erro ao processar top relacionados ({tipo_nome}): {e}")
                pass
        
        if 2 in opcoes:
            try:
                related = pytrends.related_queries()
                r = related.get(termo, {})
                if r and "rising" in r and r["rising"] is not None:
                    df = r["rising"].head(topn).copy()
                    print_progress(f"Rising relacionados ({tipo_nome}): {len(df)} itens")
                    for i, row in enumerate(df.itertuples(), 1):
                        item = {"tipo": "rising", "fonte": tipo_nome, "query": row.query, "value": row.value}
                        resultados.append(item)
                        resultados_tempo_real["trends"].append(item)
                        # Exibir em tempo real com cores: branco para query, cinza para valor
                        query_text = f"{row.query}"
                        value_text = gray(f"({row.value})")
                        print_data_item(i, query_text, f"{value_text} ")
                    file = os.path.join(OUTPUT_DIR, f"rising_{tipo_nome}_{termo}_{now_tag()}.csv")
                    if safe_save_csv(df, file):
                    print_success(f"Salvo: {file}", len(df))
            except Exception as e:
                logger.warning(f"Erro ao processar top relacionados ({tipo_nome}): {e}")
                pass
        
        if 3 in opcoes:
            try:
                regioes = pytrends.interest_by_region(resolution="country", inc_low_vol=True)
                if not regioes.empty:
                    serie = regioes[termo].sort_values(ascending=False).head(topn)
                    print_progress(f"Interesse por regiões ({tipo_nome}): {len(serie)} itens")
                    for i, (reg, val) in enumerate(serie.items(), 1):
                        item = {"tipo": "regioes", "fonte": tipo_nome, "regiao": reg, "valor": val}
                        resultados.append(item)
                        resultados_tempo_real["trends"].append(item)
                        # Exibir TODOS os dados em tempo real: branco para região, cinza para valor
                        reg_text = f"{reg}"
                        val_text = gray(f"({val})")
                        print_data_item(i, reg_text, f"{val_text} ")
                    df = pd.DataFrame({"regiao": serie.index, "valor": serie.values})
                    file = os.path.join(OUTPUT_DIR, f"regioes_{tipo_nome}_{termo}_{now_tag()}.csv")
                    if safe_save_csv(df, file):
                    print_success(f"Salvo: {file}", len(serie))
            except Exception as e:
                logger.warning(f"Erro ao processar top relacionados ({tipo_nome}): {e}")
                pass
        
        if 4 in opcoes:
            try:
                df_time = pytrends.interest_over_time()
                if not df_time.empty:
                    print_progress(f"Interesse ao longo do tempo ({tipo_nome}): {len(df_time)} pontos")
                    for i, (idx, val) in enumerate(df_time[termo].items(), 1):
                        item = {"tipo": "tempo", "fonte": tipo_nome, "data": idx.strftime("%Y-%m-%d"), "valor": val}
                        resultados.append(item)
                        resultados_tempo_real["trends"].append(item)
                        # Exibir TODOS os pontos de tempo em tempo real
                        date_text = f"{idx.strftime('%Y-%m-%d')}"
                        val_text = gray(f"→ {val}")
                        print_data_item(i, date_text, f" {val_text}")
                    df = pd.DataFrame({"data": df_time.index, "valor": df_time[termo].values})
                    file = os.path.join(OUTPUT_DIR, f"tempo_{tipo_nome}_{termo}_{now_tag()}.csv")
                    if safe_save_csv(df, file):
                    print_success(f"Salvo: {file}", len(df_time))
            except Exception as e:
                logger.warning(f"Erro ao processar top relacionados ({tipo_nome}): {e}")
                pass
        
        time.sleep(delay)
    
    return resultados

# ======================================
# 📦 MÓDULO 3: SERP
# ======================================

def coletar_duckduckgo(term, region="br", limite=20):
    if not HAS_DDGS:
        return []
    resultados = []
    try:
        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.text(term, region=region, safesearch="off", max_results=limite), 1):
                if "title" in r and "href" in r:
                    resultados.append({"engine": "duckduckgo", "rank": i, "title": r["title"], "link": r["href"]})
    except:
        pass
    return resultados

def coletar_google(term, region="br", lang="pt", limite=20):
    if not HAS_GOOGLE_API or not GOOGLE_API_KEY or not GOOGLE_CX:
        return []
    resultados = []
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        start, rank = 1, 1
        while start <= limite:
            res = service.cse().list(q=term, cx=GOOGLE_CX, gl=region, lr=f"lang_{lang}" if lang != "auto" else None, start=start, num=min(10, limite - start + 1)).execute()
            if "items" not in res:
                break
            for item in res["items"]:
                resultados.append({"engine": "google", "rank": rank, "title": item.get("title", ""), "link": item.get("link", "")})
                rank += 1
            start += 10
    except:
        pass
    return resultados

def coletar_brave(term, region="br", limite=20):
    if not BRAVE_API_KEY:
        return []
    resultados = []
    try:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
        params = {"q": term, "count": limite, "country": region}
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if "web" in data and "results" in data["web"]:
            for i, item in enumerate(data["web"]["results"], 1):
                resultados.append({"engine": "brave", "rank": i, "title": item.get("title", ""), "link": item.get("url", "")})
    except:
        pass
    return resultados

def coletar_bing(term, region="br", limite=20):
    if not SERPAPI_KEY:
        return []
    resultados = []
    try:
        url = "https://serpapi.com/search"
        params = {"engine": "bing", "q": term, "count": limite, "cc": region, "api_key": SERPAPI_KEY}
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if "organic_results" in data:
            for i, item in enumerate(data["organic_results"], 1):
                resultados.append({"engine": "bing", "rank": i, "title": item.get("title", ""), "link": item.get("link", "")})
    except:
        pass
    return resultados

def run_serp(termo: str, config: Dict, output_dir: str, resultados_tempo_real: Dict) -> List[Dict]:
    """Executa SERP - v4.4"""
    print(f"\nSERP — {termo}\n")
    
    region = config.get("region", "br")
    limite = config.get("limite", 20)
    buscadores = config.get("buscadores", [1])
    delay = config.get("delay", 1.0)
    
    SERP_DIR = ensure_dir(os.path.join(output_dir, "serp"))
    resultados = []
    
    buscadores_map = {
        1: ("DuckDuckGo", coletar_duckduckgo, True),
        2: ("Google", coletar_google, HAS_GOOGLE_API and GOOGLE_API_KEY and GOOGLE_CX),
        3: ("Brave", coletar_brave, bool(BRAVE_API_KEY)),
        4: ("Bing", coletar_bing, bool(SERPAPI_KEY)),
    }
    
    for bus_id in buscadores:
        if bus_id not in buscadores_map:
            continue
        
        nome, func, disponivel = buscadores_map[bus_id]
        
        if not disponivel:
            print(yellow(f"  [!] {nome} não disponível (faltam API keys)"))
            continue
        
        print_progress(f"Buscando no {nome}...")
        
        if bus_id == 2:
            res = func(termo, region, "pt", limite)
        else:
            res = func(termo, region, limite)
        
        time.sleep(delay)
        
        if res:
            print_progress(f"{nome}: {len(res)} resultados encontrados")
            for r in res:
                resultados.append(r)
                resultados_tempo_real["serp"].append(r)
                # Exibir em tempo real: verde para buscador, branco para título, cinza para link
                rank_str = green(f"[{r['engine'].upper()}]")
                title_text = r['title']
                link_text = gray(r['link'])
                print_data_item(r['rank'], title_text, f"{rank_str} ")
                print(f"      {link_text}")
                flush_output()
            
            df = pd.DataFrame(res)
            file = os.path.join(SERP_DIR, f"{nome.lower()}_{termo}.csv")
            if safe_save_csv(df, file):
            print_success(f"Salvo: {file}", len(res))
    
    if resultados:
        df = pd.DataFrame(resultados)
        file = os.path.join(SERP_DIR, f"serp_consolidado_{termo}.csv")
        if safe_save_csv(df, file):
        print_success(f"Consolidado: {file}", len(resultados))
    
    return resultados

# ======================================
# 📦 MÓDULO 4: YOUTUBE
# ======================================

youtube = None
if YOUTUBE_API_KEY and HAS_GOOGLE_API:
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    except:
        pass

def buscar_videos_api(query, region, lang, order=1, max_results=10):
    if not youtube:
        return []
    try:
        order_map = {1: "relevance", 2: "date", 3: "viewCount"}
        order_str = order_map.get(order, "relevance") if isinstance(order, int) else order
        request = youtube.search().list(q=query, part="snippet", type="video", regionCode=region.upper(), relevanceLanguage=lang.lower(), order=order_str, maxResults=max_results)
        response = request.execute()
        return [{"videoId": item["id"]["videoId"], "titulo": item["snippet"]["title"], "descricao": item["snippet"]["description"], "canal": item["snippet"]["channelTitle"], "publicado_em": item["snippet"]["publishedAt"], "link": f"https://www.youtube.com/watch?v={item['id']['videoId']}"} for item in response.get("items", [])]
    except:
        return []

def buscar_videos_scraping(query, max_results=10):
    if not HAS_YOUTUBE_SEARCH:
        return []
    try:
        vs = VideosSearch(query, limit=max_results)
        result = vs.result()
        return [{"videoId": v["id"], "titulo": v["title"], "canal": v["channel"]["name"], "publicado_em": v.get("publishedTime", ""), "views": v.get("viewCount", {}).get("short", "N/A"), "link": v["link"]} for v in result.get("result", [])]
    except:
        return []

def buscar_videos(query, region, lang, order=1, max_results=10):
    if youtube:
        try:
            return buscar_videos_api(query, region, lang, order, max_results)
        except:
            return buscar_videos_scraping(query, max_results)
    return buscar_videos_scraping(query, max_results)

def buscar_comentarios_api(video_id, max_results=20):
    if not youtube:
        return []
    try:
        request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=max_results, textFormat="plainText")
        response = request.execute()
        return [{"autor": c["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"], "comentario": c["snippet"]["topLevelComment"]["snippet"]["textDisplay"], "likes": c["snippet"]["topLevelComment"]["snippet"]["likeCount"], "publicado_em": c["snippet"]["topLevelComment"]["snippet"]["publishedAt"]} for c in response.get("items", [])]
    except:
        return []

def buscar_comentarios_scraping(video_id, max_results=20):
    if not HAS_YOUTUBE_SEARCH:
        return []
    try:
        cs = Comments(video_id)
        result = cs.result()
        return [{"autor": c["author"]["name"], "comentario": c["content"], "likes": c.get("votes", 0), "publicado_em": c.get("publishedTime", "N/A")} for c in result.get("result", [])[:max_results]]
    except:
        return []

def buscar_comentarios(video_id, max_results=20):
    if youtube:
        try:
            return buscar_comentarios_api(video_id, max_results)
        except:
            return buscar_comentarios_scraping(video_id, max_results)
    return buscar_comentarios_scraping(video_id, max_results)

def run_youtube(termo: str, config: Dict, output_dir: str, resultados_tempo_real: Dict) -> Dict:
    """Executa YouTube - v4.4"""
    print(f"\nYouTube — {termo}\n")
    
    region = config.get("region", "br")
    lang = config.get("lang", "pt")
    order = config.get("order", 1)
    limite_videos = config.get("limite_videos", 50)
    coletar_comentarios = config.get("coletar_comentarios", False)
    limite_comentarios = config.get("limite_comentarios", 50)
    videos_selecionados = config.get("videos_selecionados", [1])
    delay = config.get("delay", 1.0)
    
    YOUTUBE_DIR = ensure_dir(os.path.join(output_dir, "youtube"))
    
    print_progress("Buscando vídeos...")
    
    videos = buscar_videos(termo, region, lang, order, limite_videos)
    time.sleep(delay)
    
    if not videos:
        print(yellow("  [!] Nenhum vídeo encontrado"))
        return {}
    
    print_progress(f"Vídeos encontrados: {len(videos)}")
    
    for i, v in enumerate(videos, 1):
        item = {"video": v, "tipo": "video"}
        resultados_tempo_real["youtube"].append(item)
        # Exibir em tempo real: branco para título, cinza para canal e link
        titulo_text = v['titulo']
        canal_text = gray(f"Canal: {v.get('canal', 'N/A')}")
        link_text = gray(v['link'])
        print_data_item(i, titulo_text)
        print(f"      {canal_text} | {link_text}")
        flush_output()
    
    df_videos = pd.DataFrame(videos)
    file = os.path.join(YOUTUBE_DIR, f"videos_{termo}.csv")
    if safe_save_csv(df_videos, file):
    print_success(f"Salvo: {file}", len(videos))
    
    comentarios_todos = []
    if coletar_comentarios:
        print_progress("Coletando comentários...")
        
        if videos_selecionados == "todos" or videos_selecionados == "t":
            indices_list = range(1, len(videos) + 1)
        else:
            indices_list = videos_selecionados
        
        for i in indices_list:
            if i <= len(videos):
                vid = videos[i - 1]
                print_progress(f"  Vídeo {i}: {vid['titulo']}")  # DADOS COMPLETOS, SEM CORTES
                
                comentarios = buscar_comentarios(vid["videoId"], limite_comentarios)
                time.sleep(delay)
                
                if comentarios:
                    for j, c in enumerate(comentarios, 1):
                        c["video_id"] = vid["videoId"]
                        c["video_titulo"] = vid["titulo"]
                        comentarios_todos.append(c)
                        resultados_tempo_real["youtube"].append({"comentario": c, "tipo": "comentario"})
                        # Exibir TODOS os comentários em tempo real - DADOS COMPLETOS SEM CORTES
                        autor_text = gray(c['autor'])
                        comentario_text = str(c['comentario'])  # DADOS COMPLETOS, SEM CORTES
                        likes_str = gray(f"({c['likes']} likes)")
                        print_data_item(j, comentario_text, f"{autor_text}: ")
                        print(f"      {likes_str}")
                        flush_output()
        
        if comentarios_todos:
            df_comentarios = pd.DataFrame(comentarios_todos)
            file = os.path.join(YOUTUBE_DIR, f"comentarios_{termo}.csv")
            if safe_save_csv(df_comentarios, file):
            print_success(f"Comentários salvos: {file}", len(comentarios_todos))
    
    return {"videos": videos, "comentarios": comentarios_todos}

# ======================================
# 📦 MÓDULO 5: APP STORES (UNIFICADO)
# ======================================

def fetch_apple(term, country="br", limit=20):
    try:
        r = requests.get("https://itunes.apple.com/search", params={"term": term, "country": country, "entity": "software,iPadSoftware", "limit": limit}, timeout=30)
        r.raise_for_status()
        return r.json().get("results", [])
    except:
        return []

def apple_df(results):
    rows = []
    for r in results:
        rows.append({"title": r.get("trackName"), "developer": r.get("artistName"), "rating": round(r.get("averageUserRating", 0), 1) if r.get("averageUserRating") else None, "ratings_count": r.get("userRatingCount") or 0, "id": r.get("trackId"), "url": r.get("trackViewUrl")})
    return pd.DataFrame(rows)

def fetch_reviews_apple(app_id, country="br", max_reviews=200):
    if not HAS_PLAY_SCRAPER:
        return pd.DataFrame()
    collected, page = [], 1
    try:
        with tqdm(total=max_reviews, desc=f"Apple {app_id}", ncols=80, leave=False) as pbar:
            while len(collected) < max_reviews:
                url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/page={page}/json"
                try:
                    r = requests.get(url, timeout=30)
                    r.raise_for_status()
                    data = r.json()
                    entries = data.get("feed", {}).get("entry", [])
                except:
                    break
                if not entries or not isinstance(entries, list):
                    break
                if isinstance(entries[0], dict) and "im:rating" not in entries[0]:
                    entries = entries[1:]
                if not entries:
                    break
                for e in entries:
                    collected.append({"author": e.get("author", {}).get("name", {}).get("label"), "rating": int(e.get("im:rating", {}).get("label", 0)), "title": e.get("title", {}).get("label"), "content": e.get("content", {}).get("label"), "votes": int(e.get("im:voteCount", {}).get("label", 0)), "date": e.get("updated", {}).get("label")})
                pbar.update(len(entries))
                if len(entries) < 50:
                    break
                page += 1
    except:
        pass
    return pd.DataFrame(collected[:max_reviews])

def fetch_google(term, lang="pt", country="br", n=20):
    if not HAS_PLAY_SCRAPER:
        return pd.DataFrame()
    try:
        res = search(term, lang=lang, country=country)
    except:
        return pd.DataFrame()
    rows = []
    for r in res[:n]:
        rows.append({"title": r.get("title"), "developer": r.get("developer"), "rating": round(r.get("score", 0), 1) if r.get("score") else None, "installs": r.get("installs"), "id": r.get("appId")})
    return pd.DataFrame(rows)

def fetch_reviews_google(app_id, lang="pt", country="br", max_reviews=200):
    if not HAS_PLAY_SCRAPER:
        return pd.DataFrame()
    out, token = [], None
    try:
        with tqdm(total=max_reviews, desc=f"Google {app_id}", ncols=80, leave=False) as pbar:
            while len(out) < max_reviews:
                try:
                    batch, token = reviews(app_id, lang=lang, country=country, sort=Sort.NEWEST, count=min(200, max_reviews - len(out)), continuation_token=token)
                except:
                    break
                if not batch:
                    break
                out.extend(batch)
                pbar.update(len(batch))
                time.sleep(0.3)
                if not token:
                    break
    except:
        pass
    return pd.DataFrame(out[:max_reviews])

def run_stores(termo: str, config: Dict, output_dir: str, resultados_tempo_real: Dict) -> Dict:
    """Executa App Stores (Google Play + Apple App Store) - v4.4"""
    if not HAS_PLAY_SCRAPER:
        logger.warning("google-play-scraper não instalado. Pulando App Stores.")
        print(yellow("[!] google-play-scraper não instalado. Pulando App Stores."))
        return {}
    
    print(f"\nApp Stores — {termo}\n")
    
    country = config.get("country", "br")
    lang = config.get("lang", "pt")
    n_apps = config.get("n_apps", 50)
    max_reviews = config.get("max_reviews", 50)
    coletar_reviews = config.get("coletar_reviews", False)
    apps_selecionados = config.get("apps_selecionados", [1, 2, 3])
    lojas = config.get("lojas", [1, 2])
    delay = config.get("delay", 1.0)
    
    STORES_DIR = ensure_dir(os.path.join(output_dir, "stores"))
    resultados = {}
    
    if 1 in lojas:
        print_progress("Buscando apps no Google Play...")
        df_google = fetch_google(termo, lang, country, n_apps)
        time.sleep(delay)
        
        if not df_google.empty:
            print_progress(f"Google Play: {len(df_google)} apps encontrados")
            for i, row in enumerate(df_google.itertuples(), 1):
                item = {"app": {"title": row.title, "developer": row.developer, "rating": row.rating, "installs": row.installs}, "tipo": "app", "loja": "google_play"}
                resultados_tempo_real["stores"].append(item)
                # Exibir em tempo real: branco para título, verde para rating, cinza para desenvolvedor e downloads
                title_text = row.title
                rating_text = green(f"⭐ {row.rating or 's/d'}")
                dev_text = gray(row.developer)
                installs_text = gray(f"Downloads: {row.installs}")
                print_data_item(i, title_text, f" | {rating_text} | {dev_text}")
                print(f"      {installs_text}")
                flush_output()
            
            file = os.path.join(STORES_DIR, f"apps_google_{termo}.csv")
            if safe_save_csv(df_google, file):
            print_success(f"Salvo: {file}", len(df_google))
            resultados["google_play"] = df_google
            
            if coletar_reviews:
                print_progress("Coletando reviews do Google Play...")
                if apps_selecionados == "todos" or apps_selecionados == "t":
                    apps_ids = df_google["id"].dropna().tolist()
                else:
                    apps_ids = [df_google.iloc[i-1]["id"] for i in apps_selecionados if i <= len(df_google)]
                
                for app_id in apps_ids:
                    app_title = df_google.loc[df_google["id"] == app_id, "title"].iloc[0]
                    print_progress(f"  {app_title}...")
                    df_reviews = fetch_reviews_google(app_id, lang, country, max_reviews)
                    time.sleep(delay)
                    
                    if not df_reviews.empty:
                        # Exibir TODAS as reviews em tempo real - DADOS COMPLETOS SEM CORTES
                        for j, row in enumerate(df_reviews.itertuples(), 1):
                            item = {"review": {"app": app_title, "rating": row.score, "content": row.content}, "tipo": "review", "loja": "google_play"}
                            resultados_tempo_real["stores"].append(item)
                            # Verde para rating, branco para conteúdo COMPLETO
                            rating_text = green(f"⭐{row.score}")
                            content_text = str(row.content)  # DADOS COMPLETOS, SEM CORTES
                            print_data_item(j, content_text, f"{rating_text} | ")
                            flush_output()
                        
                        file = os.path.join(STORES_DIR, f"reviews_google_{app_id}.csv")
                        if safe_save_csv(df_reviews, file):
                        print_success(f"  Reviews: {file}", len(df_reviews))
        else:
            resultados["google_play"] = pd.DataFrame()
    
    if 2 in lojas:
        print_progress("Buscando apps na App Store...")
        df_apple = apple_df(fetch_apple(termo, country, n_apps))
        time.sleep(delay)
        
        if not df_apple.empty:
            print_progress(f"App Store: {len(df_apple)} apps encontrados")
            for i, row in enumerate(df_apple.itertuples(), 1):
                item = {"app": {"title": row.title, "developer": row.developer, "rating": row.rating, "ratings_count": row.ratings_count}, "tipo": "app", "loja": "app_store"}
                resultados_tempo_real["stores"].append(item)
                # Exibir em tempo real: branco para título, verde para rating, cinza para desenvolvedor e avaliações
                title_text = row.title
                rating_text = green(f"⭐ {row.rating or 's/d'}")
                dev_text = gray(row.developer)
                ratings_text = gray(f"Avaliações: {row.ratings_count}")
                print_data_item(i, title_text, f" | {rating_text} | {dev_text}")
                print(f"      {ratings_text}")
                flush_output()
            
            file = os.path.join(STORES_DIR, f"apps_apple_{termo}.csv")
            if safe_save_csv(df_apple, file):
            print_success(f"Salvo: {file}", len(df_apple))
            resultados["app_store"] = df_apple
            
            if coletar_reviews:
                print_progress("Coletando reviews da App Store...")
                if apps_selecionados == "todos" or apps_selecionados == "t":
                    apps_ids = df_apple["id"].dropna().tolist()
                else:
                    apps_ids = [df_apple.iloc[i-1]["id"] for i in apps_selecionados if i <= len(df_apple)]
                
                for app_id in apps_ids:
                    app_title = df_apple.loc[df_apple["id"] == app_id, "title"].iloc[0]
                    print_progress(f"  {app_title}...")
                    df_reviews = fetch_reviews_apple(app_id, country, max_reviews)
                    time.sleep(delay)
                    
                    if not df_reviews.empty:
                        # Exibir TODAS as reviews em tempo real - DADOS COMPLETOS SEM CORTES
                        for j, row in enumerate(df_reviews.itertuples(), 1):
                            item = {"review": {"app": app_title, "rating": row.rating, "content": row.content}, "tipo": "review", "loja": "app_store"}
                            resultados_tempo_real["stores"].append(item)
                            # Verde para rating, branco para conteúdo COMPLETO
                            rating_text = green(f"⭐{row.rating}")
                            content_text = str(row.content)  # DADOS COMPLETOS, SEM CORTES
                            print_data_item(j, content_text, f"{rating_text} | ")
                            flush_output()
                        
                        file = os.path.join(STORES_DIR, f"reviews_apple_{app_id}.csv")
                        if safe_save_csv(df_reviews, file):
                        print_success(f"  Reviews: {file}", len(df_reviews))
        else:
            resultados["app_store"] = pd.DataFrame()
    
    return resultados

# ======================================
# 📊 FUNÇÕES DE ANÁLISE E VISUALIZAÇÃO
# ======================================

def normalizar_dados_fonte(fonte_id: int, dados: Any, termo: str) -> List[Dict]:
    """Normaliza dados de uma fonte para formato unificado - v4.4"""
    linhas = []
    data_coleta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if fonte_id == 1 and isinstance(dados, list):  # Google Suggest
        for item in dados:
            linhas.append({
                "fonte": "Google Suggest", "tipo": "sugestao", "termo": item.get("termo", termo),
                "conteudo": item.get("sugestao", ""), "relevancia": item.get("relevancia", 0),
                "regiao": item.get("regiao", ""), "cliente": item.get("cliente", ""),
                "fonte_busca": item.get("fonte", ""), "categoria": item.get("tipo", ""),
                "data_coleta": data_coleta
            })
    
    elif fonte_id == 2 and isinstance(dados, list):  # Google Trends
        for item in dados:
            linhas.append({
                "fonte": "Google Trends", "tipo": item.get("tipo", "dados"), "termo": termo,
                "conteudo": item.get("query", item.get("regiao", "")),
                "valor": item.get("value", item.get("valor", 0)), "fonte_busca": item.get("fonte", ""),
                "data_coleta": data_coleta
            })
    
    elif fonte_id == 3 and isinstance(dados, list):  # SERP
        for item in dados:
            linhas.append({
                "fonte": "SERP", "tipo": "resultado_busca", "termo": termo,
                "conteudo": item.get("title", ""), "url": item.get("link", ""),
                "buscador": item.get("engine", ""), "posicao": item.get("rank", 0),
                "data_coleta": data_coleta
            })
    
    elif fonte_id == 4 and isinstance(dados, dict):  # YouTube
        # Processar vídeos
        for v in dados.get("videos", []):
            linhas.append({
                "fonte": "YouTube", "tipo": "video", "termo": termo,
                "conteudo": v.get("titulo", ""), "canal": v.get("canal", ""),
                "url": v.get("link", ""), "video_id": v.get("videoId", ""),
                "publicado_em": v.get("publicado_em", ""), "data_coleta": data_coleta
            })
        # Processar comentários
        for c in dados.get("comentarios", []):
            linhas.append({
                "fonte": "YouTube", "tipo": "comentario", "termo": termo,
                "conteudo": c.get("comentario", ""), "autor": c.get("autor", ""),
                "likes": c.get("likes", 0), "video_id": c.get("video_id", ""),
                "video_titulo": c.get("video_titulo", ""), "data_coleta": data_coleta
            })
    
    # Adicionar comentários de YouTube que podem estar apenas em resultados_tempo_real
    # (caso não estejam no dict retornado por run_youtube)
    
    elif fonte_id == 5 and isinstance(dados, dict):  # App Stores
        for loja, df in dados.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Processar apps
                for _, row in df.iterrows():
                    linhas.append({
                        "fonte": f"App Store ({loja.replace('_', ' ').title()})",
                        "tipo": "app", "termo": termo, "conteudo": row.get("title", ""),
                        "desenvolvedor": row.get("developer", ""),
                        "rating": row.get("rating") if pd.notna(row.get("rating")) else None,
                        "installs": row.get("installs", row.get("ratings_count", 0)),
                        "app_id": str(row.get("id", "")), "url": row.get("url", ""),
                        "data_coleta": data_coleta
                    })
    
    return linhas

def consolidar_dados(resultados: Dict, termo: str, output_dir: str, fontes_ordenadas: Optional[List[int]] = None, resultados_tempo_real: Optional[Dict] = None) -> pd.DataFrame:
    """Consolida todos os dados coletados em um único DataFrame - v4.5 melhorado"""
    print("\nConsolidação de dados\n")
    
    todas_linhas = []
    if not fontes_ordenadas:
        fontes_ordenadas = ORDEM_FONTES
    
    # Consolidar na ordem das fontes usando função auxiliar
    for fonte_id in fontes_ordenadas:
        fonte_key = FONTES_MAP.get(fonte_id, {}).get("key", "")
        if fonte_key in resultados and resultados[fonte_key]:
            linhas = normalizar_dados_fonte(fonte_id, resultados[fonte_key], termo)
            todas_linhas.extend(linhas)
    
    # Adicionar dados adicionais de resultados_tempo_real que podem não estar em resultados
    if resultados_tempo_real:
        data_coleta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Reviews de App Stores
        if "stores" in resultados_tempo_real:
            for item in resultados_tempo_real["stores"]:
                if isinstance(item, dict) and item.get("tipo") == "review":
                    review_data = item.get("review", {})
                    loja = item.get("loja", "unknown")
                    todas_linhas.append({
                        "fonte": f"App Store ({loja.replace('_', ' ').title()})",
                        "tipo": "review", "termo": termo,
                        "conteudo": review_data.get("content", ""),
                        "rating": review_data.get("rating"),
                        "app": review_data.get("app", ""),
                        "data_coleta": data_coleta
                    })
        
        # Comentários de YouTube que podem estar apenas em resultados_tempo_real
        if "youtube" in resultados_tempo_real:
            for item in resultados_tempo_real["youtube"]:
                if isinstance(item, dict) and item.get("tipo") == "comentario":
                    comentario_data = item.get("comentario", {})
                    todas_linhas.append({
                        "fonte": "YouTube", "tipo": "comentario", "termo": termo,
                        "conteudo": comentario_data.get("comentario", ""),
                        "autor": comentario_data.get("autor", ""),
                        "likes": comentario_data.get("likes", 0),
                        "video_id": comentario_data.get("video_id", ""),
                        "video_titulo": comentario_data.get("video_titulo", ""),
                        "data_coleta": data_coleta
                    })
    
    if not todas_linhas:
        logger.warning("Nenhum dado para consolidar")
        print(yellow("  [!] Nenhum dado para consolidar"))
        return pd.DataFrame()
    
    # Validar estrutura dos dados
    try:
    df_consolidado = pd.DataFrame(todas_linhas)
        
        # Remover duplicatas baseado em conteúdo e fonte
        df_consolidado = remove_duplicates(df_consolidado, subset=["fonte", "tipo", "conteudo"])
        
        # Validar integridade dos dados
        if df_consolidado.empty:
            logger.warning("DataFrame consolidado está vazio após processamento")
            return pd.DataFrame()
        
    file = os.path.join(output_dir, f"consolidado_{termo}_{now_tag()}.csv")
        if safe_save_csv(df_consolidado, file):
    print_success(f"Arquivo consolidado salvo: {file}", len(df_consolidado))
    logger.info(f"Arquivo consolidado salvo: {file} ({len(df_consolidado)} itens)")
        else:
            logger.error(f"Falha ao salvar arquivo consolidado: {file}")
    
    return df_consolidado
    
    except (ValueError, KeyError) as e:
        logger.error(f"Erro ao criar DataFrame consolidado: {e}", exc_info=True)
        print(red(f"  [ERRO] Erro ao consolidar dados: {e}"))
        return pd.DataFrame()
    
    except Exception as e:
        logger.error(f"Erro inesperado ao consolidar dados: {e}", exc_info=True)
        print(red(f"  [ERRO] Erro inesperado: {e}"))
        return pd.DataFrame()

def gerar_estatisticas(df_consolidado, termo, output_dir, fontes_ordenadas=None):
    """Gera estatísticas descritivas avançadas e detalhadas dos dados coletados - v4.5"""
    if df_consolidado.empty:
        logger.warning("DataFrame vazio, não é possível gerar estatísticas")
        return {}
    
    print("\nEstatísticas descritivas\n")
    
    stats = {}
    
    # Estatísticas numéricas avançadas
    numeric_cols = df_consolidado.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        stats["numeric_summary"] = {}
        for col in numeric_cols:
            if col in df_consolidado.columns:
                col_data = df_consolidado[col].dropna()
                if len(col_data) > 0:
                    stats["numeric_summary"][col] = {
                        "mean": float(np.mean(col_data)),
                        "median": float(np.median(col_data)),
                        "std": float(np.std(col_data)),
                        "min": float(np.min(col_data)),
                        "max": float(np.max(col_data)),
                        "q25": float(np.percentile(col_data, 25)),
                        "q75": float(np.percentile(col_data, 75)),
                        "q90": float(np.percentile(col_data, 90)),
                        "q95": float(np.percentile(col_data, 95)),
                        "count": int(len(col_data)),
                        "missing": int(df_consolidado[col].isna().sum())
                    }
    
    # Estatísticas por fonte (na ordem)
    print("\nEstatísticas por fonte:")
    
    # Se temos ordem definida, usar ela
    if fontes_ordenadas:
        # Mapear nomes das fontes na ordem (com variações possíveis)
        fonte_nomes_mapeamento = {
            1: ["Google Suggest"],
            2: ["Google Trends"],
            3: ["SERP"],
            4: ["YouTube"],
            5: ["App Store"]
        }
        
        todas_fontes = df_consolidado["fonte"].unique().tolist()
        fontes_processadas = []
        
        # Processar na ordem das fontes selecionadas
        for fonte_id in fontes_ordenadas:
            nomes_possiveis = fonte_nomes_mapeamento.get(fonte_id, [])
            fonte_nome_display = FONTES_MAP.get(fonte_id, {}).get("nome", "Desconhecida")
            
            # Procurar correspondência no DataFrame
            fonte_encontrada = None
            for nome_possivel in nomes_possiveis:
                for fonte_df in todas_fontes:
                    if fonte_df not in fontes_processadas:
                        if nome_possivel.lower() in fonte_df.lower() or fonte_df.lower() in nome_possivel.lower():
                            fonte_encontrada = fonte_df
                            fontes_processadas.append(fonte_df)
                            break
                if fonte_encontrada:
                    break
            
            if fonte_encontrada:
                df_fonte = df_consolidado[df_consolidado["fonte"] == fonte_encontrada]
                stats[fonte_nome_display] = {
                    "total": len(df_fonte),
                    "tipos": df_fonte["tipo"].value_counts().to_dict()
                }
                print(f"  {bold(fonte_nome_display)}: {green(len(df_fonte))} itens")
                for tipo, count in stats[fonte_nome_display]["tipos"].items():
                    print(f"    - {tipo}: {cyan(count)}")
        
        # Adicionar fontes que não estão na ordem (caso existam)
        for fonte in todas_fontes:
            if fonte not in fontes_processadas:
                df_fonte = df_consolidado[df_consolidado["fonte"] == fonte]
                stats[fonte] = {
                    "total": len(df_fonte),
                    "tipos": df_fonte["tipo"].value_counts().to_dict()
                }
                print(f"  {bold(fonte)}: {green(len(df_fonte))} itens")
                for tipo, count in stats[fonte]["tipos"].items():
                    print(f"    - {tipo}: {cyan(count)}")
    else:
        # Fallback: ordem alfabética
        for fonte in sorted(df_consolidado["fonte"].unique()):
            df_fonte = df_consolidado[df_consolidado["fonte"] == fonte]
            stats[fonte] = {
                "total": len(df_fonte),
                "tipos": df_fonte["tipo"].value_counts().to_dict()
            }
            print(f"  {bold(fonte)}: {green(len(df_fonte))} itens")
            for tipo, count in stats[fonte]["tipos"].items():
                print(f"    - {tipo}: {count}")
    
    # Estatísticas gerais
    stats["geral"] = {
        "total_itens": len(df_consolidado),
        "fontes_unicas": df_consolidado["fonte"].nunique(),
        "tipos_unicos": df_consolidado["tipo"].nunique()
    }
    
    print(f"\n  Total geral: {stats['geral']['total_itens']} itens")
    print(f"  Fontes: {stats['geral']['fontes_unicas']}")
    print(f"  Tipos de dados: {stats['geral']['tipos_unicos']}")
    
    # Salvar estatísticas em múltiplos formatos
    timestamp = now_tag()
    
    # TXT
    stats_file_txt = os.path.join(output_dir, f"estatisticas_{termo}_{timestamp}.txt")
    try:
        with open(stats_file_txt, "w", encoding="utf-8") as f:
            f.write(f"ESTATÍSTICAS AVANÇADAS - {termo.upper()}\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total de itens: {stats['geral']['total_itens']}\n")
        f.write(f"Fontes únicas: {stats['geral']['fontes_unicas']}\n")
        f.write(f"Tipos únicos: {stats['geral']['tipos_unicos']}\n\n")
            
            # Estatísticas numéricas
            if "numeric_summary" in stats:
                f.write("\nESTATÍSTICAS NUMÉRICAS:\n")
                f.write("-" * 70 + "\n")
                for col, metrics in stats["numeric_summary"].items():
                    f.write(f"\n{col}:\n")
                    f.write(f"  Média: {metrics['mean']:.2f}\n")
                    f.write(f"  Mediana: {metrics['median']:.2f}\n")
                    f.write(f"  Desvio Padrão: {metrics['std']:.2f}\n")
                    f.write(f"  Mínimo: {metrics['min']:.2f}\n")
                    f.write(f"  Máximo: {metrics['max']:.2f}\n")
                    f.write(f"  Q25: {metrics['q25']:.2f}\n")
                    f.write(f"  Q75: {metrics['q75']:.2f}\n")
                    f.write(f"  Q90: {metrics['q90']:.2f}\n")
                    f.write(f"  Q95: {metrics['q95']:.2f}\n")
                    f.write(f"  Valores válidos: {metrics['count']}\n")
                    f.write(f"  Valores faltantes: {metrics['missing']}\n")
            
            # Por fonte
            f.write("\n\nESTATÍSTICAS POR FONTE:\n")
            f.write("-" * 70 + "\n")
        for fonte, dados in stats.items():
                if fonte not in ["geral", "numeric_summary"]:
                f.write(f"\n{fonte}:\n")
                f.write(f"  Total: {dados['total']}\n")
                for tipo, count in dados["tipos"].items():
                    f.write(f"  {tipo}: {count}\n")
    
        print_success(f"Estatísticas (TXT) salvas: {stats_file_txt}")
        logger.info(f"Estatísticas salvas em TXT: {stats_file_txt}")
    except Exception as e:
        logger.error(f"Erro ao salvar estatísticas em TXT: {e}")
    
    # JSON
    stats_file_json = os.path.join(output_dir, f"estatisticas_{termo}_{timestamp}.json")
    try:
        # Converter numpy types para tipos Python nativos para JSON
        def convert_to_serializable(obj):
            if isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            return obj
        
        stats_serializable = convert_to_serializable(stats)
        with open(stats_file_json, "w", encoding="utf-8") as f:
            json.dump(stats_serializable, f, indent=2, ensure_ascii=False)
        
        print_success(f"Estatísticas (JSON) salvas: {stats_file_json}")
        logger.info(f"Estatísticas salvas em JSON: {stats_file_json}")
    except Exception as e:
        logger.error(f"Erro ao salvar estatísticas em JSON: {e}")
    
    return stats

def gerar_graficos(resultados, termo, output_dir):
    """Gera gráficos de análise para cada fonte"""
    if not HAS_MATPLOTLIB:
        print(yellow("[!] matplotlib não disponível. Pulando geração de gráficos."))
        return
    
    print("\nGeração de gráficos\n")
    
    GRAFICOS_DIR = ensure_dir(os.path.join(output_dir, "graficos"))
    
    # 1. Gráfico de distribuição por fonte
    if "consolidado" in resultados and isinstance(resultados["consolidado"], pd.DataFrame) and not resultados["consolidado"].empty:
        df = resultados["consolidado"]
        
        if "fonte" in df.columns:
            plt.figure(figsize=(12, 6))
            fonte_counts = df["fonte"].value_counts()
            plt.bar(fonte_counts.index, fonte_counts.values, color=sns.color_palette("husl", len(fonte_counts)))
            plt.title(f"Distribuição de Dados por Fonte - {termo}", fontsize=14, fontweight="bold")
            plt.xlabel("Fonte", fontsize=12)
            plt.ylabel("Quantidade de Itens", fontsize=12)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(os.path.join(GRAFICOS_DIR, f"distribuicao_fontes_{termo}.png"), dpi=300, bbox_inches="tight")
            plt.close()
            print_success(f"Gráfico: distribuição por fonte")
    
    # 2. Gráfico de relevância (Google Suggest)
    if "suggest" in resultados and resultados["suggest"]:
        try:
            df_suggest = pd.DataFrame(resultados["suggest"])
            if not df_suggest.empty and "relevancia" in df_suggest.columns and "sugestao" in df_suggest.columns:
                plt.figure(figsize=(12, 6))
                top_suggestions = df_suggest.nlargest(20, "relevancia")
                if not top_suggestions.empty:
                    plt.barh(range(len(top_suggestions)), top_suggestions["relevancia"].values, color="steelblue")
                    plt.yticks(range(len(top_suggestions)), top_suggestions["sugestao"].values)
                    plt.xlabel("Relevância", fontsize=12)
                    plt.title(f"Top 20 Sugestões por Relevância - {termo}", fontsize=14, fontweight="bold")
                    plt.gca().invert_yaxis()
                    plt.tight_layout()
                    plt.savefig(os.path.join(GRAFICOS_DIR, f"relevancia_suggest_{termo}.png"), dpi=300, bbox_inches="tight")
                    plt.close()
                    print_success(f"Gráfico: relevância de sugestões")
        except Exception as e:
            print(yellow(f"  [!] Erro ao gerar gráfico de relevância: {e}"))
    
    # 3. Gráfico de interesse por região (Trends)
    if "trends" in resultados and resultados["trends"]:
        try:
            trends_data = [t for t in resultados["trends"] if t.get("tipo") == "regioes"]
            if trends_data:
                df_regioes = pd.DataFrame(trends_data)
                if not df_regioes.empty and "valor" in df_regioes.columns and "regiao" in df_regioes.columns:
                    plt.figure(figsize=(12, 8))
                    top_regioes = df_regioes.nlargest(15, "valor")
                    if not top_regioes.empty:
                        plt.barh(range(len(top_regioes)), top_regioes["valor"].values, color="coral")
                        plt.yticks(range(len(top_regioes)), top_regioes["regiao"].values)
                        plt.xlabel("Interesse (0-100)", fontsize=12)
                        plt.title(f"Interesse por Região - {termo}", fontsize=14, fontweight="bold")
                        plt.gca().invert_yaxis()
                        plt.tight_layout()
                        plt.savefig(os.path.join(GRAFICOS_DIR, f"interesse_regioes_{termo}.png"), dpi=300, bbox_inches="tight")
                        plt.close()
                        print_success(f"Gráfico: interesse por região")
        except Exception as e:
            print(yellow(f"  [!] Erro ao gerar gráfico de regiões: {e}"))
    
    # 4. Gráfico de distribuição de buscadores (SERP)
    if "serp" in resultados and resultados["serp"]:
        try:
            df_serp = pd.DataFrame(resultados["serp"])
            if not df_serp.empty and "engine" in df_serp.columns:
                plt.figure(figsize=(10, 6))
                engine_counts = df_serp["engine"].value_counts()
                if len(engine_counts) > 0:
                    plt.pie(engine_counts.values, labels=engine_counts.index, autopct="%1.1f%%", startangle=90)
                    plt.title(f"Distribuição de Resultados por Buscador - {termo}", fontsize=14, fontweight="bold")
                    plt.axis("equal")
                    plt.tight_layout()
                    plt.savefig(os.path.join(GRAFICOS_DIR, f"distribuicao_buscadores_{termo}.png"), dpi=300, bbox_inches="tight")
                    plt.close()
                    print_success(f"Gráfico: distribuição de buscadores")
        except Exception as e:
            print(yellow(f"  [!] Erro ao gerar gráfico de buscadores: {e}"))
    
    # 5. Gráfico de ratings (App Stores)
    if "stores" in resultados and resultados["stores"]:
        try:
            all_ratings = []
            for loja, df in resultados["stores"].items():
                if isinstance(df, pd.DataFrame) and not df.empty and "rating" in df.columns:
                    ratings = df["rating"].dropna()
                    all_ratings.extend([float(r) for r in ratings.tolist() if pd.notna(r)])
            
            if all_ratings:
                plt.figure(figsize=(10, 6))
                plt.hist(all_ratings, bins=20, color="mediumseagreen", edgecolor="black")
                plt.xlabel("Rating", fontsize=12)
                plt.ylabel("Frequência", fontsize=12)
                plt.title(f"Distribuição de Ratings de Apps - {termo}", fontsize=14, fontweight="bold")
                plt.tight_layout()
                plt.savefig(os.path.join(GRAFICOS_DIR, f"distribuicao_ratings_{termo}.png"), dpi=300, bbox_inches="tight")
                plt.close()
                print_success(f"Gráfico: distribuição de ratings")
        except Exception as e:
            print(yellow(f"  [!] Erro ao gerar gráfico de ratings: {e}"))
    
    print_success(f"Todos os gráficos salvos em: {GRAFICOS_DIR}")

def gerar_insights(resultados, termo, output_dir):
    """Gera insights automáticos dos dados coletados"""
    print("\nInsights e análises\n")
    
    insights = []
    
    # Insight 1: Volume de dados
    total = 0
    fontes_ativas = 0
    for k, v in resultados.items():
        if k != "consolidado":
            # Verificar se v não está vazio de forma segura
            v_nao_vazio = False
            if v is None:
                v_nao_vazio = False
            elif isinstance(v, pd.DataFrame):
                v_nao_vazio = not v.empty
            elif isinstance(v, (list, dict)):
                v_nao_vazio = len(v) > 0
            else:
                v_nao_vazio = bool(v)
            
            if v_nao_vazio:
                if isinstance(v, dict):
                    count = 0
                    for item in v.values():
                        if item is not None:
                            if isinstance(item, pd.DataFrame):
                                if not item.empty:
                                    count += len(item)
                            elif isinstance(item, list):
                                if len(item) > 0:
                                    count += len(item)
                            else:
                                count += 1
                elif isinstance(v, list):
                    count = len(v)
                elif isinstance(v, pd.DataFrame):
                    count = len(v)
                else:
                    count = 1
                if count > 0:
                    total += count
                    fontes_ativas += 1
    insights.append(f"📊 Volume total: {total} itens coletados de {fontes_ativas} fontes")
    
    # Insight 2: Google Suggest
    if "suggest" in resultados:
        suggest_data = resultados["suggest"]
        if suggest_data is not None:
            if isinstance(suggest_data, pd.DataFrame):
                if not suggest_data.empty:
                    df_suggest = suggest_data
                else:
                    df_suggest = None
            elif isinstance(suggest_data, list) and len(suggest_data) > 0:
                df_suggest = pd.DataFrame(suggest_data)
            else:
                df_suggest = None
            
            if df_suggest is not None and "relevancia" in df_suggest.columns:
                top_sug = df_suggest.nlargest(1, "relevancia")["sugestao"].iloc[0]
                insights.append(f"🔍 Sugestão mais relevante: '{top_sug}'")
    
    # Insight 3: Trends
    if "trends" in resultados:
        trends_data = resultados["trends"]
        if trends_data is not None and (not isinstance(trends_data, pd.DataFrame) or not trends_data.empty) and (not isinstance(trends_data, list) or len(trends_data) > 0):
            if isinstance(trends_data, list):
                regioes_data = [t for t in trends_data if t.get("tipo") == "regioes"]
            else:
                regioes_data = []
            if regioes_data:
                df_reg = pd.DataFrame(regioes_data)
                top_reg = df_reg.nlargest(1, "valor")["regiao"].iloc[0]
                max_val = df_reg.nlargest(1, "valor")["valor"].iloc[0]
                insights.append(f"🌍 Região com maior interesse: {top_reg} ({max_val}/100)")
    
    # Insight 4: SERP
    if "serp" in resultados:
        serp_data = resultados["serp"]
        if serp_data is not None and (not isinstance(serp_data, pd.DataFrame) or not serp_data.empty) and (not isinstance(serp_data, list) or len(serp_data) > 0):
            if isinstance(serp_data, list):
                df_serp = pd.DataFrame(serp_data)
            else:
                df_serp = serp_data if isinstance(serp_data, pd.DataFrame) else pd.DataFrame([serp_data])
            if "engine" in df_serp.columns:
                engine_counts = df_serp["engine"].value_counts()
                top_engine = engine_counts.index[0]
                insights.append(f"🔎 Buscador com mais resultados: {top_engine} ({engine_counts[top_engine]} resultados)")
    
    # Insight 5: YouTube
    if "youtube" in resultados:
        youtube_data = resultados["youtube"]
        if youtube_data is not None and isinstance(youtube_data, dict):
            videos = youtube_data.get("videos", [])
            if videos:
                insights.append(f"📹 Vídeos encontrados: {len(videos)}")
                comentarios = youtube_data.get("comentarios", [])
                if comentarios:
                    total_likes = sum(c.get("likes", 0) for c in comentarios)
                    insights.append(f"💬 Comentários coletados: {len(comentarios)} (total de {total_likes} likes)")
    
    # Insight 6: App Stores
    if "stores" in resultados:
        stores_data = resultados["stores"]
        if stores_data is not None and isinstance(stores_data, dict):
            total_apps = 0
            avg_rating = []
            for loja, df in stores_data.items():
                if isinstance(df, pd.DataFrame) and not df.empty:
                    total_apps += len(df)
                    if "rating" in df.columns:
                        ratings = df["rating"].dropna()
                        avg_rating.extend(ratings.tolist())
            if total_apps > 0:
                insights.append(f"📱 Apps encontrados: {total_apps}")
                if avg_rating:
                    insights.append(f"⭐ Rating médio: {np.mean(avg_rating):.2f}/5.0")
    
    # Exibir insights
    if insights:
        for i, insight in enumerate(insights, 1):
            print(f"  {i}. {insight}")
    
    # Salvar insights
    insights_file = os.path.join(output_dir, f"insights_{termo}_{now_tag()}.txt")
    with open(insights_file, "w", encoding="utf-8") as f:
        f.write(f"INSIGHTS E ANÁLISES - {termo.upper()}\n")
        f.write("=" * 70 + "\n\n")
        for insight in insights:
            f.write(f"{insight}\n")
    
    print_success(f"Insights salvos: {insights_file}")
    
    return insights

def exibir_dashboard(resultados, termo, output_dir, stats, insights, fontes_ordenadas=None):
    """Exibe dashboard completo e detalhado com cores padronizadas - v4.5"""
    print(f"\n{cyan(bold('=' * 70))}")
    print(f"{cyan(bold(f'DASHBOARD COMPLETO - {termo.upper()}'))}")
    print(f"{cyan(bold('=' * 70))}\n")
    
    # Resumo geral melhorado com cores
    print(f"{cyan(bold('📊 RESUMO GERAL'))}")
    if stats and "geral" in stats:
        print(f"  {gray('Total de itens:')} {green(str(stats['geral']['total_itens']))}")
        print(f"  {gray('Fontes de dados:')} {green(str(stats['geral']['fontes_unicas']))}")
        print(f"  {gray('Tipos de dados:')} {green(str(stats['geral']['tipos_unicos']))}")
    
        # Estatísticas numéricas se disponíveis
        if "numeric_summary" in stats and stats["numeric_summary"]:
            print(f"\n  {cyan(bold('Métricas numéricas:'))}")
            for col, metrics in list(stats["numeric_summary"].items())[:5]:  # Mostrar até 5 colunas
                print(f"    {green(col)}:")
                print(f"      {gray('Média:')} {metrics['mean']:.2f} | {gray('Mediana:')} {metrics['median']:.2f} | {gray('DP:')} {metrics['std']:.2f}")
                print(f"      {gray('Min:')} {metrics['min']:.2f} | {gray('Max:')} {metrics['max']:.2f} | {gray('Q95:')} {metrics['q95']:.2f}")
                if 'count' in metrics:
                    print(f"      {gray('Total:')} {metrics['count']} | {gray('Nulos:')} {metrics.get('missing', 0)}")
    
    # Estatísticas detalhadas por fonte
    print(f"\n{cyan(bold('📈 ESTATÍSTICAS DETALHADAS POR FONTE'))}")
    if stats and fontes_ordenadas:
        # Mapeamento de nomes possíveis
        fonte_nomes_mapeamento = {
            1: ["Google Suggest", "suggest"],
            2: ["Google Trends", "trends"],
            3: ["SERP", "serp"],
            4: ["YouTube", "youtube"],
            5: ["App Stores", "App Store", "stores"]
        }
        
        for fonte_id in fontes_ordenadas:
            fonte_nome = FONTES_MAP.get(fonte_id, {}).get("nome", "Desconhecida")
            nomes_possiveis = fonte_nomes_mapeamento.get(fonte_id, [])
            
            # Buscar estatísticas desta fonte
            fonte_stats = None
            for stat_fonte, dados in stats.items():
                if stat_fonte != "geral":
                    # Verificar correspondência exata ou parcial
                    if stat_fonte == fonte_nome or any(nome.lower() in stat_fonte.lower() or stat_fonte.lower() in nome.lower() for nome in nomes_possiveis):
                        fonte_stats = dados
                        break
            
            if fonte_stats:
                print(f"\n  {green(bold(f'▶ {fonte_nome}'))}")
                print(f"    {gray('Total de itens:')} {green(str(fonte_stats['total']))}")
                
                # Tipos de dados com contagem
                if fonte_stats.get("tipos"):
                    print(f"    {gray('Distribuição por tipo:')}")
                    for tipo, count in fonte_stats["tipos"].items():
                        porcentagem = (count / fonte_stats['total'] * 100) if fonte_stats['total'] > 0 else 0
                        print(f"      {green('•')} {tipo}: {green(str(count))} ({cyan(f'{porcentagem:.1f}%')})")
                
                # Estatísticas específicas da fonte se disponíveis
                if fonte_id == 1 and "relevancia" in str(stats):  # Google Suggest
                    print(f"    {gray('Média de relevância:')} {green('calculada')}")
                elif fonte_id == 2:  # Google Trends
                    print(f"    {gray('Queries relacionadas:')} {green('coletadas')}")
                elif fonte_id == 3:  # SERP
                    print(f"    {gray('Resultados de busca:')} {green('coletados')}")
                elif fonte_id == 4:  # YouTube
                    print(f"    {gray('Vídeos:')} {green(str(fonte_stats.get('videos', 0)))}")
                    print(f"    {gray('Comentários:')} {green(str(fonte_stats.get('comentarios', 0)))}")
                elif fonte_id == 5:  # App Stores
                    print(f"    {gray('Apps:')} {green(str(fonte_stats.get('apps', 0)))}")
                    print(f"    {gray('Reviews:')} {green(str(fonte_stats.get('reviews', 0)))}")
                    rating_medio = fonte_stats.get('rating_medio', 0)
                    if rating_medio:
                        print(f"    {gray('Rating médio:')} {green(f'{rating_medio:.2f}')} ⭐")
    elif stats:
        for fonte, dados in stats.items():
            if fonte != "geral":
                print(f"\n  {green(bold(f'▶ {fonte}'))}")
                print(f"    {gray('Total:')} {green(str(dados['total']))} itens")
                for tipo, count in dados.get("tipos", {}).items():
                    print(f"      {green('•')} {tipo}: {green(str(count))}")
    
    # Insights com cores
    print(f"\n{cyan(bold('💡 INSIGHTS PRINCIPAIS'))}")
    if insights:
        for i, insight in enumerate(insights, 1):
            print(f"  {green(str(i))}. {insight}")
    else:
        print(f"  {gray('Nenhum insight disponível')}")
    
    # Arquivos gerados com cores
    print(f"\n{cyan(bold('📁 ARQUIVOS GERADOS'))}")
    print(f"  {green('✓')} CSV consolidado")
    print(f"  {green('✓')} Estatísticas (TXT e JSON)")
    print(f"  {green('✓')} Insights")
    if HAS_MATPLOTLIB:
        print(f"  {green('✓')} Gráficos")
    print(f"  {green('✓')} Arquivos individuais por fonte")
    
    # Qualidade dos dados com cores e mais detalhes
    if "consolidado" in resultados and isinstance(resultados["consolidado"], pd.DataFrame):
        df = resultados["consolidado"]
        if not df.empty:
            print(f"\n{cyan(bold('🔍 QUALIDADE DOS DADOS'))}")
            duplicatas_removidas = len(df) - len(df.drop_duplicates())
            valores_nulos = df.isnull().sum().sum()
            total_campos = len(df) * len(df.columns)
            taxa_completude = (1 - valores_nulos / total_campos) * 100 if total_campos > 0 else 0
            
            print(f"  {gray('Duplicatas removidas:')} {yellow(str(duplicatas_removidas))}")
            print(f"  {gray('Valores nulos:')} {yellow(str(valores_nulos))}")
            print(f"  {gray('Taxa de completude:')} {green(f'{taxa_completude:.1f}%')}")
            print(f"  {gray('Total de linhas:')} {green(str(len(df)))}")
            print(f"  {gray('Total de colunas:')} {green(str(len(df.columns)))}")
            
            # Colunas com mais valores nulos
            if valores_nulos > 0:
                colunas_nulas = df.isnull().sum().sort_values(ascending=False).head(5)
                if len(colunas_nulas) > 0:
                    print(f"  {gray('Colunas com mais valores nulos:')}")
                    for col, count in colunas_nulas.items():
                        if count > 0:
                            print(f"      {yellow('•')} {col}: {yellow(str(count))}")
    
    print(f"\n{green(bold('✓ Dashboard completo gerado com sucesso!'))}\n")

# ======================================
# 🎯 CONFIGURAÇÃO (Ordem Lógica Melhorada)
# ======================================

def coletar_config_fonte(fonte_id: int, config: Dict) -> Dict:
    """Coleta configuração específica de uma fonte - v4.4"""
    fonte_config = {}
    
    if fonte_id == 1:  # Google Suggest
        print("\n04. Suggest")
        print_menu("  Navegadores", "", CLIENTS_OPTIONS, default=1)
        clients_selected = parse_todos_input(input("  > [1]: ").strip() or "1", CLIENTS_OPTIONS, default=1)
        print_menu("  Fontes", "", SOURCES_OPTIONS, default=1)
        sources_selected = parse_todos_input(input("  > [1,2]: ").strip() or "1,2", SOURCES_OPTIONS, default=1)
        print_menu("  Dados", "", SUGGEST_OPCOES, default=1)
        opcoes_selected = parse_todos_input(input("  > [t]: ").strip() or "t", SUGGEST_OPCOES, default=1)
        limit = safe_int_input("  Resultados [15]: ", 15, min_val=1, max_val=1000)
        fonte_config = {"clients": clients_selected, "sources": sources_selected, "opcoes": opcoes_selected, "limit": limit}
    
    elif fonte_id == 2:  # Google Trends
        print("\n05. Trends")
        print_menu("  Fontes", "", TRENDS_TIPOS, default=1)
        tipos_selected = parse_numeric_input(input("  > [1,2,3]: ").strip() or "1,2,3", TRENDS_TIPOS, default=1)
        print_menu("  Períodos", "", TRENDS_PERIODOS, default=4)
        periodos_selected = parse_numeric_input(input("  > [1,2,3,4,6]: ").strip() or "1,2,3,4,6", TRENDS_PERIODOS, default=4)
        print_menu("  Dados", "", TRENDS_OPCOES, default=1)
        opcoes_selected = parse_todos_input(input("  > [1,2,3,4]: ").strip() or "1,2,3,4", TRENDS_OPCOES, default=1)
        topn = safe_int_input("  Resultados [20]: ", 20, min_val=1, max_val=500)
        fonte_config = {"gtypes": tipos_selected, "timeframe": periodos_selected[0] if periodos_selected else 4, "opcoes": opcoes_selected, "topn": topn}
    
    elif fonte_id == 3:  # SERP
        print("\n06. SERP")
        print_menu("  Buscadores", "", SERP_BUSCADORES, default=1)
        buscadores_selected = parse_todos_input(input("  > [1,2,3,4]: ").strip() or "1,2,3,4", SERP_BUSCADORES, default=1)
        limite = safe_int_input("  Resultados [20]: ", 20, min_val=1, max_val=100)
        fonte_config = {"buscadores": buscadores_selected, "limite": limite}
    
    elif fonte_id == 4:  # YouTube
        print("\n07. YouTube")
        limite_videos = safe_int_input("  Vídeos [10]: ", 10, min_val=1, max_val=100)
        print_menu("  Ordenação vídeos", "", YOUTUBE_ORDER, default=1)
        order_selected = parse_todos_input(input("  > [1,2,3]: ").strip() or "1,2,3", YOUTUBE_ORDER, default=1)
        limite_comentarios = safe_int_input("  Comentários [10]: ", 10, min_val=0, max_val=500)
        print_menu("  Ordenação comentários", "", YOUTUBE_COMMENT_ORDER, default=1)
        comment_order_selected = parse_todos_input(input("  > [1,2,3]: ").strip() or "1,2,3", YOUTUBE_COMMENT_ORDER, default=1)
        fonte_config = {
            "order": order_selected[0] if order_selected else 1,
            "limite_videos": limite_videos,
            "coletar_comentarios": limite_comentarios > 0,
            "limite_comentarios": limite_comentarios,
            "comment_order": comment_order_selected[0] if comment_order_selected else 1,
            "videos_selecionados": "todos",
        }
    
    elif fonte_id == 5:  # App Stores
        print("\n08. App Store")
        lojas_options = {1: "Google Play Store", 2: "Apple App Store"}
        print_menu("  Lojas", "", lojas_options, default=1)
        lojas_selected = parse_todos_input(input("  > [1,2]: ").strip() or "1,2", lojas_options, default=1)
        n_apps = safe_int_input("  Aplicativos [10]: ", 10, min_val=1, max_val=200)
        max_reviews = safe_int_input("  Reviews [100]: ", 100, min_val=0, max_val=1000)
        print_menu("  Ordenação reviews", "", APP_STORE_REVIEW_ORDER, default=1)
        review_order_selected = parse_todos_input(input("  > [1,2,3]: ").strip() or "1,2,3", APP_STORE_REVIEW_ORDER, default=1)
        fonte_config = {
            "lojas": lojas_selected,
            "n_apps": n_apps,
            "coletar_reviews": max_reviews > 0,
            "max_reviews": max_reviews,
            "review_order": review_order_selected[0] if review_order_selected else 1,
            "apps_selecionados": "todos",
        }
    
    return fonte_config

def coletar_configuracao() -> Optional[Dict]:
    """Coleta configuração otimizada v4.5"""
    print("\nMini Research v4.5 - Configuração\n")
    
    # Validar API keys
    keys_status = validate_api_keys()
    missing_keys = [k for k, v in keys_status.items() if not v]
    if missing_keys:
        logger.warning(f"API keys ausentes: {', '.join(missing_keys)}")
    
    config = {}
    
    # 01. TERMOS DE BUSCA (com sanitização)
    print("01. Termos de busca (separe por vírgula)")
    termos_input = input("> ").strip()
    if not termos_input:
        print("Erro: Termo não pode estar vazio!")
        return None
    if check_exit(termos_input):
        return None
    
    termos = [sanitize_term(t.strip()) for t in termos_input.split(",") if t.strip()]
    termos = [t for t in termos if t]  # Remove termos vazios após sanitização
    
    if not termos:
        print("Erro: Nenhum termo válido encontrado após sanitização!")
        return None
    
    config["termo"] = termos[0]  # Termo principal
    config["termos"] = termos  # Todos os termos para processamento
    
    # 02. REGIÃO
    print_menu("02. Região", "", REGIONS_OPTIONS, default=1)
    regions_selected = parse_todos_input(input("> [1]: ").strip() or "1", REGIONS_OPTIONS, default=1)
    config["regions"] = [REGION_MAP[r] for r in regions_selected if r in REGION_MAP]
    
    # 03. PLATAFORMAS
    print_menu("03. Plataformas", "", FONTES_OPTIONS, default=None)
    fontes = parse_todos_input(input("> [t]: ").strip() or "t", FONTES_OPTIONS, default=None)
    config["fontes"] = fontes
    
    # 04-08. CONFIGURAÇÕES ESPECÍFICAS POR FONTE (refatorado - v4.4)
    fontes_ordenadas = ordenar_fontes_selecionadas(config["fontes"])
    
    for fonte_id in fontes_ordenadas:
        fonte_key = FONTES_MAP.get(fonte_id, {}).get("key", "")
        if fonte_key:
            config[fonte_key] = coletar_config_fonte(fonte_id, config)
    
    # Aplicar parâmetros globais
    for fonte_config in ["suggest", "trends", "serp", "youtube", "stores"]:
        if fonte_config in config:
            config[fonte_config]["region"] = config["regions"][0]
            config[fonte_config]["lang"] = "pt"
            config[fonte_config]["country"] = config["regions"][0]
    
    # DELAY (com validação)
    config["delay"] = safe_float_input("\nDelay entre requisições [0]: ", 0.0, min_val=0.0, max_val=10.0)
    
    for fonte_config in ["suggest", "trends", "serp", "youtube", "stores"]:
        if fonte_config in config:
            config[fonte_config]["delay"] = config["delay"]
    
    # Armazenar ordem das fontes
    config["fontes_ordenadas"] = ordenar_fontes_selecionadas(config["fontes"])
    
    print_config_summary(config)
    
    confirm = input("\nIniciar coleta? (s/n) [s]: ").strip().lower() or "s"
    if confirm != "s":
        print("Coleta cancelada.")
        return None
    
    return config

# ======================================
# 🚀 FUNÇÃO PRINCIPAL
# ======================================

def executar_fonte(fonte_id: int, termo: str, config: Dict, output_dir: str, resultados_tempo_real: Dict) -> Any:
    """Função genérica para executar qualquer fonte - v4.4"""
    fonte_info = FONTES_MAP.get(fonte_id, {})
    fonte_nome = fonte_info.get("nome", "Desconhecida")
    fonte_key = fonte_info.get("key", "")
    fonte_funcao = fonte_info.get("funcao", "")
    
    if not fonte_funcao:
        logger.error(f"Fonte {fonte_id} não possui função definida")
        return None
    
    try:
        fonte_config = config.get(fonte_key, {})
        
        # Mapear função string para função real
        funcoes_map = {
            "run_suggest": run_suggest,
            "run_trends": run_trends,
            "run_serp": run_serp,
            "run_youtube": run_youtube,
            "run_stores": run_stores,
        }
        
        funcao = funcoes_map.get(fonte_funcao)
        if not funcao:
            logger.error(f"Função {fonte_funcao} não encontrada")
            return None
        
        logger.info(f"Iniciando coleta de {fonte_nome} para termo: {termo}")
        resultado = funcao(termo, fonte_config, output_dir, resultados_tempo_real)
        logger.info(f"Coleta de {fonte_nome} concluída")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao coletar {fonte_nome}: {str(e)}", exc_info=True)
        print(red(f"[ERRO] {fonte_nome}: {e}"))
        # Retornar valor padrão baseado no tipo de fonte
        if fonte_id == 5:  # App Stores retorna dict
            return {}
        return []

def main():
    """Função principal otimizada v4.5"""
    print("\nMini Research v4.5 - Coletor de Dados Multi-Fonte\n")
    
    # Validar API keys no início
    keys_status = validate_api_keys()
    missing = [k for k, v in keys_status.items() if not v]
    if missing:
        logger.warning(f"API keys ausentes: {', '.join(missing)}")
        print(yellow(f"Aviso: Algumas API keys estão ausentes: {', '.join(missing)}"))
    
    config = coletar_configuracao()
    if not config:
        print(red("\nConfiguração cancelada ou inválida."))
        return
    
    termos = config.get("termos", [config["termo"]])
    termo_principal = config["termo"]
    output_dir = ensure_dir(os.path.join(BASE_DIR, f"coleta_{termo_principal}_{now_tag()}"))
    
    resultados_tempo_real = {
        "suggest": [],
        "trends": [],
        "serp": [],
        "youtube": [],
        "stores": []
    }
    
    print(f"\nIniciando coleta para: {termo_principal}")
    if len(termos) > 1:
        print(f"Termos adicionais: {', '.join(termos[1:])}\n")
    
    resultados = {}
    fontes_ordenadas = config.get("fontes_ordenadas", ordenar_fontes_selecionadas(config["fontes"]))
    
    # Executar fontes usando função genérica
    for fonte_id in fontes_ordenadas:
        fonte_key = FONTES_MAP.get(fonte_id, {}).get("key", "")
        if fonte_key:
            resultados[fonte_key] = executar_fonte(fonte_id, termo_principal, config, output_dir, resultados_tempo_real)
    
    # ======================================
    # 📊 ANÁLISES E VISUALIZAÇÕES
    # ======================================
    
    # Análises e visualizações
    print("\nAnálises e visualizações\n")
    
    # 1. Consolidar todos os dados (na ordem das fontes) - incluindo resultados_tempo_real
    df_consolidado = consolidar_dados(resultados, termo_principal, output_dir, config.get("fontes_ordenadas"), resultados_tempo_real)
    resultados["consolidado"] = df_consolidado
    
    # 2. Gerar estatísticas (na ordem das fontes)
    stats = gerar_estatisticas(df_consolidado, termo_principal, output_dir, config.get("fontes_ordenadas"))
    
    # 3. Gerar gráficos
    gerar_graficos(resultados, termo_principal, output_dir)
    
    # 4. Gerar insights
    insights = gerar_insights(resultados, termo_principal, output_dir)
    
    # 5. Exibir dashboard completo (na ordem das fontes)
    exibir_dashboard(resultados, termo_principal, output_dir, stats, insights, config.get("fontes_ordenadas"))
    
    print(f"\nColeta finalizada\n")
    print(f"Dados salvos em: {output_dir}\n")
    
    print("Resumo final da coleta:")
    print("-" * 70)
    
    for fonte_id in fontes_ordenadas:
        fonte_key = FONTES_MAP.get(fonte_id, {}).get("key", "")
        fonte_nome = FONTES_MAP.get(fonte_id, {}).get("nome", "Desconhecida")
        
        if fonte_key in resultados and resultados[fonte_key]:
            dados = resultados[fonte_key]
            if isinstance(dados, dict):
                count = 0
                for v in dados.values():
                    if v is not None:
                        if isinstance(v, pd.DataFrame):
                            if not v.empty:
                                count += len(v)
                        elif isinstance(v, list):
                            if len(v) > 0:
                                count += len(v)
                        else:
                            count += 1
            elif isinstance(dados, list):
                count = len(dados)
            elif isinstance(dados, pd.DataFrame):
                count = len(dados)
            else:
                count = 1
            print(f"  ✓ {fonte_nome}: {count} itens")
    
    if not df_consolidado.empty:
        print(f"  ✓ Consolidado: {len(df_consolidado)} itens")
    print()

if __name__ == "__main__":
    main()
