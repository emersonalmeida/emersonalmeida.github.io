#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Research v4.7 - Coletor de Dados Multi-Fonte com Análises e Dashboard
Versão otimizada com recursos máximos e melhorias críticas

Melhorias v4.7:
- UI/UX: Padrão de cores aplicado em TODOS os menus (incluindo termo de busca)
- Google Trends expandido: related_topics, trending_searches, top_charts, suggestions
- YouTube expandido: topicDetails, liveStreamingDetails, recordingDetails, status, player, localizations
- YouTube expandido: favoriteCount, dislikeCount, dimension, definition, caption, licensedContent, contentRating, projection
- YouTube expandido: defaultLanguage, defaultAudioLanguage, liveBroadcastContent, todas as thumbnails (default, medium, high, standard, maxres)
- Google Play expandido: headerImage, screenshots, video, videoImage, descriptionHTML, developer completo (id, email, website, address)
- Google Play expandido: privacyPolicy, familyGenre, contentRatingDescription, histogram (distribuição de ratings)
- Google Play expandido: offersIAP, adSupported, recentChanges, permissions, whatsNew, released
- App Store expandido: releaseNotes, languageCodesISO2A, ipadScreenshotUrls, appletvScreenshotUrls
- App Store expandido: privacyPolicyUrl, inAppPurchases, subscriptionInfo, artistId, currentVersionReleaseDate
- Melhorias técnicas: validação aprimorada, tratamento de erros mais robusto, performance otimizada
- Logging: logs mais detalhados e informativos

Melhorias v4.6 (mantidas):
- CORREÇÃO: Removido line_terminator (incompatível com pandas >= 1.5.0)
- YouTube expandido: views, duration, thumbnails, channelId, description completa
- Comentários YouTube: replyCount, totalReplyCount, canReply, authorChannelId
- App Stores expandido: ratings_count, reviews_count, price, contentRating, genre, icon
- Reviews completas: title, votes/thumbsUpCount, developerResponse, replyContent
- Ordenação inteligente: comentários e reviews por múltiplos critérios (recent, top_likes, longest)
- Coleta exata: garante que configuração seja respeitada (10 vídeos × 10 comentários = 100 comentários)
- Contadores visuais: "Vídeo 1/10", "Comentário 5/10 do vídeo 1", "Review 3/10 do app X"
- Metadados completos: todos os campos disponíveis das APIs são coletados
- Google Play: reviews_count, price, free, contentRating, genre, icon, url
- App Store: price, currency, genres, screenshotUrls, supportedDevices
- YouTube: channelId, channelUrl, thumbnails (default, medium, high), duration, viewCount
- Comentários: canReply, isPublic, replyCount, totalReplyCount, authorChannelId, authorChannelUrl
- Reviews: developerResponse (completo), replyContent, replyDate, helpful, reviewId

Melhorias v4.5 (mantidas):
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
        # Removido line_terminator (incompatível com pandas >= 1.5.0)
        import csv
        df.to_csv(filepath, index=False, encoding="utf-8-sig", errors='replace', 
                  quoting=csv.QUOTE_ALL, lineterminator='\n')
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
    5: "Tópicos relacionados",  # v4.7
    6: "Buscas em alta",  # v4.7
    7: "Sugestões adicionais",  # v4.7
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
    4: "Mais longos",
}

APP_STORE_REVIEW_ORDER = {
    1: "Mais novos",
    2: "Mais antigos",
    3: "Melhores avaliadas",
    4: "Piores avaliadas",
    5: "Mais votadas",
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
    """Executa Google Trends - v4.7 com recursos expandidos"""
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
    """Busca vídeos via API oficial com TODOS os metadados disponíveis - v4.6"""
    if not youtube:
        return []
    try:
        order_map = {1: "relevance", 2: "date", 3: "viewCount"}
        order_str = order_map.get(order, "relevance") if isinstance(order, int) else order
        
        # Buscar com snippet para obter metadados básicos
        request = youtube.search().list(
            q=query, 
            part="snippet", 
            type="video", 
            regionCode=region.upper(), 
            relevanceLanguage=lang.lower(), 
            order=order_str, 
            maxResults=max_results
        )
        response = request.execute()
        
        # Obter IDs dos vídeos para buscar estatísticas e detalhes
        video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
        
        # Buscar estatísticas e detalhes adicionais
        videos_detalhes = {}
        if video_ids:
            try:
                # Buscar TODOS os parts disponíveis - v4.7
                stats_request = youtube.videos().list(
                    part="statistics,contentDetails,snippet,topicDetails,recordingDetails,liveStreamingDetails,status,localizations",
                    id=",".join(video_ids)
                )
                stats_response = stats_request.execute()
                for vid in stats_response.get("items", []):
                    stats_data = vid.get("statistics", {})
                    content = vid.get("contentDetails", {})
                    snippet_full = vid.get("snippet", {})
                    topic = vid.get("topicDetails", {})
                    recording = vid.get("recordingDetails", {})
                    live = vid.get("liveStreamingDetails", {})
                    status_data = vid.get("status", {})
                    localizations = vid.get("localizations", {})
                    thumbnails = snippet_full.get("thumbnails", {})
                    
                    videos_detalhes[vid["id"]] = {
                        # Estatísticas
                        "viewCount": int(stats_data.get("viewCount", 0)),
                        "likeCount": int(stats_data.get("likeCount", 0)),
                        "dislikeCount": int(stats_data.get("dislikeCount", 0)),  # v4.7
                        "commentCount": int(stats_data.get("commentCount", 0)),
                        "favoriteCount": int(stats_data.get("favoriteCount", 0)),  # v4.7
                        # Content Details
                        "duration": content.get("duration", ""),
                        "dimension": content.get("dimension", ""),  # v4.7
                        "definition": content.get("definition", ""),  # v4.7
                        "caption": content.get("caption", ""),  # v4.7
                        "licensedContent": content.get("licensedContent", False),  # v4.7
                        "contentRating": content.get("contentRating", {}),  # v4.7
                        "projection": content.get("projection", ""),  # v4.7
                        # Snippet expandido
                        "thumbnails": thumbnails,
                        "thumbnail_default": thumbnails.get("default", {}).get("url", ""),  # v4.7
                        "thumbnail_medium": thumbnails.get("medium", {}).get("url", ""),  # v4.7
                        "thumbnail_high": thumbnails.get("high", {}).get("url", ""),  # v4.7
                        "thumbnail_standard": thumbnails.get("standard", {}).get("url", ""),  # v4.7
                        "thumbnail_maxres": thumbnails.get("maxres", {}).get("url", ""),  # v4.7
                        "channelId": snippet_full.get("channelId", ""),
                        "channelUrl": f"https://www.youtube.com/channel/{snippet_full.get('channelId', '')}",
                        "tags": snippet_full.get("tags", []),
                        "categoryId": snippet_full.get("categoryId", ""),
                        "defaultLanguage": snippet_full.get("defaultLanguage", ""),  # v4.7
                        "defaultAudioLanguage": snippet_full.get("defaultAudioLanguage", ""),  # v4.7
                        "liveBroadcastContent": snippet_full.get("liveBroadcastContent", ""),  # v4.7
                        # Topic Details - v4.7
                        "topicIds": topic.get("topicIds", []),
                        "topicCategories": topic.get("topicCategories", []),
                        # Recording Details - v4.7
                        "recordingDate": recording.get("recordingDate", ""),
                        "locationDescription": recording.get("locationDescription", ""),
                        # Live Streaming Details - v4.7
                        "actualStartTime": live.get("actualStartTime", ""),
                        "actualEndTime": live.get("actualEndTime", ""),
                        "scheduledStartTime": live.get("scheduledStartTime", ""),
                        "scheduledEndTime": live.get("scheduledEndTime", ""),
                        "concurrentViewers": live.get("concurrentViewers", ""),
                        "activeLiveChatId": live.get("activeLiveChatId", ""),
                        # Status - v4.7
                        "uploadStatus": status_data.get("uploadStatus", ""),
                        "privacyStatus": status_data.get("privacyStatus", ""),
                        "license": status_data.get("license", ""),
                        "embeddable": status_data.get("embeddable", False),
                        "publicStatsViewable": status_data.get("publicStatsViewable", False),
                        "madeForKids": status_data.get("madeForKids", False),
                        # Localizations - v4.7
                        "localizations": localizations
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar detalhes dos vídeos: {e}")
        
        # Combinar dados
        videos = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            detalhes = videos_detalhes.get(video_id, {})
            snippet = item.get("snippet", {})
            videos.append({
                "videoId": video_id,
                "titulo": snippet.get("title", ""),
                "descricao": snippet.get("description", ""),
                "canal": snippet.get("channelTitle", ""),
                "channelId": detalhes.get("channelId", ""),
                "channelUrl": detalhes.get("channelUrl", ""),
                "publicado_em": snippet.get("publishedAt", ""),
                "views": detalhes.get("viewCount", 0),
                "likes": detalhes.get("likeCount", 0),
                "dislikes": detalhes.get("dislikeCount", 0),  # v4.7
                "favorites": detalhes.get("favoriteCount", 0),  # v4.7
                "commentCount": detalhes.get("commentCount", 0),
                "duration": detalhes.get("duration", ""),
                "dimension": detalhes.get("dimension", ""),  # v4.7
                "definition": detalhes.get("definition", ""),  # v4.7
                "caption": detalhes.get("caption", ""),  # v4.7
                "licensedContent": detalhes.get("licensedContent", False),  # v4.7
                "contentRating": str(detalhes.get("contentRating", {})),  # v4.7
                "projection": detalhes.get("projection", ""),  # v4.7
                "thumbnails": detalhes.get("thumbnails", {}),
                "thumbnail_default": detalhes.get("thumbnail_default", ""),  # v4.7
                "thumbnail_medium": detalhes.get("thumbnail_medium", ""),  # v4.7
                "thumbnail_high": detalhes.get("thumbnail_high", ""),  # v4.7
                "thumbnail_standard": detalhes.get("thumbnail_standard", ""),  # v4.7
                "thumbnail_maxres": detalhes.get("thumbnail_maxres", ""),  # v4.7
                "tags": detalhes.get("tags", []),
                "categoryId": detalhes.get("categoryId", ""),
                "defaultLanguage": detalhes.get("defaultLanguage", ""),  # v4.7
                "defaultAudioLanguage": detalhes.get("defaultAudioLanguage", ""),  # v4.7
                "liveBroadcastContent": detalhes.get("liveBroadcastContent", ""),  # v4.7
                "topicIds": detalhes.get("topicIds", []),  # v4.7
                "topicCategories": detalhes.get("topicCategories", []),  # v4.7
                "recordingDate": detalhes.get("recordingDate", ""),  # v4.7
                "locationDescription": detalhes.get("locationDescription", ""),  # v4.7
                "actualStartTime": detalhes.get("actualStartTime", ""),  # v4.7
                "actualEndTime": detalhes.get("actualEndTime", ""),  # v4.7
                "scheduledStartTime": detalhes.get("scheduledStartTime", ""),  # v4.7
                "scheduledEndTime": detalhes.get("scheduledEndTime", ""),  # v4.7
                "concurrentViewers": detalhes.get("concurrentViewers", ""),  # v4.7
                "activeLiveChatId": detalhes.get("activeLiveChatId", ""),  # v4.7
                "uploadStatus": detalhes.get("uploadStatus", ""),  # v4.7
                "privacyStatus": detalhes.get("privacyStatus", ""),  # v4.7
                "license": detalhes.get("license", ""),  # v4.7
                "embeddable": detalhes.get("embeddable", False),  # v4.7
                "publicStatsViewable": detalhes.get("publicStatsViewable", False),  # v4.7
                "madeForKids": detalhes.get("madeForKids", False),  # v4.7
                "localizations": str(detalhes.get("localizations", {})),  # v4.7
                "link": f"https://www.youtube.com/watch?v={video_id}"
            })
        return videos
    except Exception as e:
        logger.error(f"Erro ao buscar vídeos via API: {e}")
        return []

def buscar_videos_scraping(query, max_results=10):
    """Busca vídeos via scraping com TODOS os metadados disponíveis - v4.6"""
    if not HAS_YOUTUBE_SEARCH:
        return []
    try:
        vs = VideosSearch(query, limit=max_results)
        result = vs.result()
        videos = []
        for v in result.get("result", []):
            videos.append({
                "videoId": v.get("id", ""),
                "titulo": v.get("title", ""),
                "canal": v.get("channel", {}).get("name", ""),
                "channelId": v.get("channel", {}).get("id", ""),
                "publicado_em": v.get("publishedTime", ""),
                "views": v.get("viewCount", {}).get("short", "N/A"),
                "duration": v.get("duration", ""),
                "thumbnails": v.get("thumbnails", []),
                "description": v.get("description", ""),
                "link": v.get("link", "")
            })
        return videos
    except Exception as e:
        logger.warning(f"Erro ao buscar vídeos via scraping: {e}")
        return []

def buscar_videos(query, region, lang, order=1, max_results=10):
    if youtube:
        try:
            return buscar_videos_api(query, region, lang, order, max_results)
        except:
            return buscar_videos_scraping(query, max_results)
    return buscar_videos_scraping(query, max_results)

def buscar_comentarios_api(video_id, max_results=20):
    """Busca comentários via API oficial com TODOS os metadados disponíveis - v4.6"""
    if not youtube:
        return []
    try:
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText",
            order="relevance"  # ou "time" para mais recentes
        )
        response = request.execute()
        comentarios = []
        for c in response.get("items", []):
            top_comment = c["snippet"]["topLevelComment"]["snippet"]
            comentarios.append({
                "autor": top_comment.get("authorDisplayName", ""),
                "autorId": top_comment.get("authorChannelId", {}).get("value", ""),
                "autorUrl": top_comment.get("authorChannelUrl", ""),
                "comentario": top_comment.get("textDisplay", ""),
                "likes": int(top_comment.get("likeCount", 0)),
                "publicado_em": top_comment.get("publishedAt", ""),
                "atualizado_em": top_comment.get("updatedAt", ""),
                "canReply": c["snippet"].get("canReply", False),
                "isPublic": c["snippet"].get("isPublic", True),
                "totalReplyCount": int(c["snippet"].get("totalReplyCount", 0)),
                "replyCount": len(c.get("replies", {}).get("comments", [])) if "replies" in c else 0,
                "replies": [{
                    "autor": reply["snippet"].get("authorDisplayName", ""),
                    "comentario": reply["snippet"].get("textDisplay", ""),
                    "likes": int(reply["snippet"].get("likeCount", 0)),
                    "publicado_em": reply["snippet"].get("publishedAt", "")
                } for reply in c.get("replies", {}).get("comments", [])]
            })
        return comentarios
    except Exception as e:
        logger.warning(f"Erro ao buscar comentários via API: {e}")
        return []

def buscar_comentarios_scraping(video_id, max_results=20):
    """Busca comentários via scraping com TODOS os metadados disponíveis - v4.6"""
    if not HAS_YOUTUBE_SEARCH:
        return []
    try:
        cs = Comments(video_id)
        result = cs.result()
        comentarios = []
        for c in result.get("result", [])[:max_results]:
            comentarios.append({
                "autor": c.get("author", {}).get("name", ""),
                "autorId": c.get("author", {}).get("id", ""),
                "autorUrl": c.get("author", {}).get("link", ""),
                "comentario": c.get("content", ""),
                "likes": int(c.get("votes", 0)),
                "publicado_em": c.get("publishedTime", "N/A"),
                "replies": c.get("replies", [])  # Respostas se disponíveis
            })
        return comentarios
    except Exception as e:
        logger.warning(f"Erro ao buscar comentários via scraping: {e}")
        return []

def ordenar_comentarios(comentarios, criterio=1):
    """Ordena comentários por critério - v4.6"""
    if not comentarios:
        return comentarios
    # Mapear critérios numéricos e string
    if criterio == "top_likes" or criterio == 3:
        return sorted(comentarios, key=lambda x: x.get("likes", 0), reverse=True)
    elif criterio == "recent" or criterio == 1:
        return sorted(comentarios, key=lambda x: x.get("publicado_em", ""), reverse=True)
    elif criterio == "oldest" or criterio == 2:
        return sorted(comentarios, key=lambda x: x.get("publicado_em", ""), reverse=False)
    elif criterio == "longest" or criterio == 4:
        return sorted(comentarios, key=lambda x: len(x.get("comentario", "")), reverse=True)
    return comentarios

def buscar_comentarios(video_id, max_results=20, order="relevance"):
    """Busca comentários com ordenação - v4.6"""
    comentarios = []
    if youtube:
        try:
            comentarios = buscar_comentarios_api(video_id, max_results)
        except:
            comentarios = buscar_comentarios_scraping(video_id, max_results)
    else:
        comentarios = buscar_comentarios_scraping(video_id, max_results)
    
    # Aplicar ordenação se necessário (para scraping)
    if order == "relevance" or order == 1:
        return ordenar_comentarios(comentarios, "top_likes")
    elif order == "time" or order == 2:
        return ordenar_comentarios(comentarios, "recent")
    return comentarios

def run_youtube(termo: str, config: Dict, output_dir: str, resultados_tempo_real: Dict) -> Dict:
    """Executa YouTube com coleta inteligente e TODOS os metadados - v4.6"""
    print(f"\nYouTube — {termo}\n")
    
    region = config.get("region", "br")
    lang = config.get("lang", "pt")
    order = config.get("order", 1)
    limite_videos = config.get("limite_videos", 50)
    coletar_comentarios = config.get("coletar_comentarios", False)
    limite_comentarios = config.get("limite_comentarios", 50)
    videos_selecionados = config.get("videos_selecionados", [1])
    order_comentarios = config.get("order_comentarios", 1)  # 1=recent, 2=oldest, 3=top_likes, 4=longest
    delay = config.get("delay", 1.0)
    
    YOUTUBE_DIR = ensure_dir(os.path.join(output_dir, "youtube"))
    
    print_progress("Buscando vídeos...")
    
    videos = buscar_videos(termo, region, lang, order, limite_videos)
    time.sleep(delay)
    
    if not videos:
        print(yellow("  [!] Nenhum vídeo encontrado"))
        return {}
    
    # Garantir que temos exatamente o número solicitado de vídeos
    videos = videos[:limite_videos]
    print_progress(f"Vídeos encontrados: {len(videos)} (solicitados: {limite_videos})")
    
    # Exibir vídeos com contadores e metadados expandidos
    for i, v in enumerate(videos, 1):
        item = {"video": v, "tipo": "video"}
        resultados_tempo_real["youtube"].append(item)
        # Exibir em tempo real: branco para título, cinza para metadados
        titulo_text = v['titulo']
        canal_text = gray(f"Canal: {v.get('canal', 'N/A')}")
        views_text = gray(f"Views: {v.get('views', 'N/A')}")
        duration_text = gray(f"Duration: {v.get('duration', 'N/A')}")
        link_text = gray(v['link'])
        print_data_item(i, titulo_text, f"[{green(f'{i}/{len(videos)}')}] ")
        print(f"      {canal_text} | {views_text} | {duration_text}")
        print(f"      {link_text}")
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
        
        total_videos_comentarios = len(indices_list) if isinstance(indices_list, list) else len(videos)
        video_idx = 0
        
        for i in indices_list:
            if i <= len(videos):
                video_idx += 1
                vid = videos[i - 1]
                print_progress(f"  Vídeo {video_idx}/{total_videos_comentarios}: {vid['titulo']}")
                
                # Mapear ordenação para API (1=time, 2=time, 3=relevance)
                order_map = {1: "time", 2: "time", 3: "relevance", 4: "relevance"}
                order_str = order_map.get(order_comentarios, "relevance")
                comentarios = buscar_comentarios(vid["videoId"], limite_comentarios, order_str)
                # Aplicar ordenação adicional (especialmente para longest)
                comentarios = ordenar_comentarios(comentarios, order_comentarios)
                # Garantir que temos exatamente o número solicitado de comentários
                comentarios = comentarios[:limite_comentarios]
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
                        reply_count = c.get("totalReplyCount", c.get("replyCount", 0))
                        reply_str = gray(f", {reply_count} replies") if reply_count > 0 else ""
                        print_data_item(j, comentario_text, f"{autor_text}: ")
                        print(f"      {likes_str}{reply_str}")
                        # Exibir respostas se houver
                        if c.get("replies"):
                            for k, reply in enumerate(c["replies"][:3], 1):  # Mostrar até 3 respostas
                                reply_text = str(reply.get("comentario", ""))[:100]
                                print(f"        {gray('↳')} {reply.get('autor', '')}: {reply_text}")
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
    """Converte resultados da App Store em DataFrame com TODOS os metadados - v4.6"""
    rows = []
    for r in results:
        rows.append({
            "title": r.get("trackName", ""),
            "developer": r.get("artistName", ""),
            "rating": round(r.get("averageUserRating", 0), 1) if r.get("averageUserRating") else None,
            "ratings_count": r.get("userRatingCount", 0),
            "id": r.get("trackId", ""),
            "url": r.get("trackViewUrl", ""),
            "price": r.get("price", 0),
            "currency": r.get("currency", ""),
            "formattedPrice": r.get("formattedPrice", ""),
            "genre": r.get("primaryGenreName", ""),
            "genres": r.get("genres", []),
            "description": r.get("description", ""),
            "releaseDate": r.get("releaseDate", ""),
            "currentVersionReleaseDate": r.get("currentVersionReleaseDate", ""),  # v4.7
            "version": r.get("version", ""),
            "releaseNotes": r.get("releaseNotes", ""),  # v4.7
            "contentAdvisoryRating": r.get("contentAdvisoryRating", ""),
            "screenshotUrls": str(r.get("screenshotUrls", [])),  # v4.7
            "ipadScreenshotUrls": str(r.get("ipadScreenshotUrls", [])),  # v4.7
            "appletvScreenshotUrls": str(r.get("appletvScreenshotUrls", [])),  # v4.7
            "artworkUrl512": r.get("artworkUrl512", ""),
            "artworkUrl100": r.get("artworkUrl100", ""),
            "supportedDevices": str(r.get("supportedDevices", [])),
            "isGameCenterEnabled": r.get("isGameCenterEnabled", False),
            "bundleId": r.get("bundleId", ""),
            "sellerName": r.get("sellerName", ""),
            "fileSizeBytes": r.get("fileSizeBytes", 0),
            "minimumOsVersion": r.get("minimumOsVersion", ""),
            "artistId": r.get("artistId", ""),  # v4.7
            "languageCodesISO2A": str(r.get("languageCodesISO2A", [])),  # v4.7
            "privacyPolicyUrl": r.get("privacyPolicyUrl", ""),  # v4.7
            "inAppPurchases": str(r.get("inAppPurchases", [])),  # v4.7
            "subscriptionInfo": str(r.get("subscriptionInfo", {}))  # v4.7
        })
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
                    # Coletar TODOS os campos disponíveis da review
                    collected.append({
                        "author": e.get("author", {}).get("name", {}).get("label", ""),
                        "authorUri": e.get("author", {}).get("uri", {}).get("label", ""),
                        "rating": int(e.get("im:rating", {}).get("label", 0)),
                        "title": e.get("title", {}).get("label", ""),
                        "content": e.get("content", {}).get("label", ""),
                        "votes": int(e.get("im:voteCount", {}).get("label", 0)),
                        "date": e.get("updated", {}).get("label", ""),
                        "id": e.get("id", {}).get("label", ""),
                        "version": e.get("im:version", {}).get("label", ""),
                        "voteSum": int(e.get("im:voteSum", {}).get("label", 0))
                    })
                pbar.update(len(entries))
                if len(entries) < 50:
                    break
                page += 1
    except:
        pass
    return pd.DataFrame(collected[:max_reviews])

def fetch_google(term, lang="pt", country="br", n=20):
    """Busca apps do Google Play com TODOS os metadados disponíveis - v4.6"""
    if not HAS_PLAY_SCRAPER:
        return pd.DataFrame()
    try:
        res = search(term, lang=lang, country=country)
    except Exception as e:
        logger.warning(f"Erro ao buscar apps do Google Play: {e}")
        return pd.DataFrame()
    rows = []
    for r in res[:n]:
        rows.append({
            "title": r.get("title", ""),
            "developer": r.get("developer", ""),
            "rating": round(r.get("score", 0), 1) if r.get("score") else None,
            "ratings_count": r.get("ratings", 0),
            "reviews_count": r.get("reviews", 0),
            "installs": r.get("installs", ""),
            "id": r.get("appId", ""),
            "url": r.get("url", ""),
            "icon": r.get("icon", ""),
            "headerImage": r.get("headerImage", ""),  # v4.7
            "screenshots": str(r.get("screenshots", [])),  # v4.7
            "video": r.get("video", ""),  # v4.7
            "videoImage": r.get("videoImage", ""),  # v4.7
            "price": r.get("price", ""),
            "free": r.get("free", True),
            "contentRating": r.get("contentRating", ""),
            "contentRatingDescription": r.get("contentRatingDescription", ""),  # v4.7
            "genre": r.get("genre", ""),
            "genreId": r.get("genreId", ""),
            "familyGenre": r.get("familyGenre", ""),  # v4.7
            "familyGenreId": r.get("familyGenreId", ""),  # v4.7
            "summary": r.get("summary", ""),
            "description": r.get("description", ""),
            "descriptionHTML": r.get("descriptionHTML", ""),  # v4.7
            "updated": r.get("updated", ""),
            "released": r.get("released", ""),  # v4.7
            "version": r.get("version", ""),
            "size": r.get("size", ""),
            "minInstalls": r.get("minInstalls", 0),
            "maxInstalls": r.get("maxInstalls", 0),
            "score": r.get("score", 0),
            "developerId": r.get("developerId", ""),  # v4.7
            "developerEmail": r.get("developerEmail", ""),  # v4.7
            "developerWebsite": r.get("developerWebsite", ""),  # v4.7
            "developerAddress": r.get("developerAddress", ""),  # v4.7
            "privacyPolicy": r.get("privacyPolicy", ""),  # v4.7
            "histogram": str(r.get("histogram", {})),  # v4.7 - distribuição de ratings
            "offersIAP": r.get("offersIAP", False),  # v4.7
            "adSupported": r.get("adSupported", False),  # v4.7
            "recentChanges": r.get("recentChanges", ""),  # v4.7
            "permissions": str(r.get("permissions", [])),  # v4.7
            "whatsNew": r.get("whatsNew", "")  # v4.7
        })
    return pd.DataFrame(rows)

def fetch_reviews_google(app_id, lang="pt", country="br", max_reviews=200, sort_order=Sort.NEWEST):
    """Busca reviews do Google Play com TODOS os metadados disponíveis - v4.6"""
    if not HAS_PLAY_SCRAPER:
        return pd.DataFrame()
    out, token = [], None
    try:
        with tqdm(total=max_reviews, desc=f"Google {app_id}", ncols=80, leave=False) as pbar:
            while len(out) < max_reviews:
                try:
                    batch, token = reviews(
                        app_id, 
                        lang=lang, 
                        country=country, 
                        sort=sort_order, 
                        count=min(200, max_reviews - len(out)), 
                        continuation_token=token
                    )
                except Exception as e:
                    logger.warning(f"Erro ao buscar reviews do Google Play ({app_id}): {e}")
                    break
                if not batch:
                    break
                # Expandir reviews com todos os campos disponíveis
                for review in batch:
                    expanded_review = {
                        "reviewId": review.get("reviewId", ""),
                        "userId": review.get("userId", ""),  # v4.7
                        "userName": review.get("userName", ""),
                        "userImage": review.get("userImage", ""),
                        "content": review.get("content", ""),
                        "score": review.get("score", 0),
                        "thumbsUpCount": review.get("thumbsUpCount", 0),
                        "thumbsDownCount": review.get("thumbsDownCount", 0),
                        "at": review.get("at", ""),
                        "date": review.get("date", ""),  # v4.7 - formato completo
                        "url": review.get("url", ""),  # v4.7 - URL da review
                        "replyContent": review.get("replyContent", ""),
                        "repliedAt": review.get("repliedAt", ""),
                        "appVersion": review.get("appVersion", ""),
                        "device": review.get("device", ""),
                        "androidOsVersion": review.get("androidOsVersion", "")
                    }
                    out.append(expanded_review)
                pbar.update(len(batch))
                time.sleep(0.3)
                if not token:
                    break
    except Exception as e:
        logger.error(f"Erro ao buscar reviews do Google Play: {e}")
    return pd.DataFrame(out[:max_reviews])

def ordenar_reviews(df_reviews, criterio=1):
    """Ordena reviews por critério - v4.6"""
    if df_reviews.empty:
        return df_reviews
    
    # Mapear critérios
    if criterio == 1:  # Mais recentes
        date_col = "at" if "at" in df_reviews.columns else "date"
        if date_col in df_reviews.columns:
            return df_reviews.sort_values(by=date_col, ascending=False, ignore_index=True)
    elif criterio == 2:  # Mais antigas
        date_col = "at" if "at" in df_reviews.columns else "date"
        if date_col in df_reviews.columns:
            return df_reviews.sort_values(by=date_col, ascending=True, ignore_index=True)
    elif criterio == 3:  # Melhores avaliadas
        rating_col = "score" if "score" in df_reviews.columns else "rating"
        if rating_col in df_reviews.columns:
            return df_reviews.sort_values(by=rating_col, ascending=False, ignore_index=True)
    elif criterio == 4:  # Piores avaliadas
        rating_col = "score" if "score" in df_reviews.columns else "rating"
        if rating_col in df_reviews.columns:
            return df_reviews.sort_values(by=rating_col, ascending=True, ignore_index=True)
    elif criterio == 5:  # Mais votadas
        votes_col = "thumbsUpCount" if "thumbsUpCount" in df_reviews.columns else "votes"
        if votes_col in df_reviews.columns:
            return df_reviews.sort_values(by=votes_col, ascending=False, ignore_index=True)
    
    return df_reviews

def run_stores(termo: str, config: Dict, output_dir: str, resultados_tempo_real: Dict) -> Dict:
    """Executa App Stores com coleta inteligente e TODOS os metadados - v4.6"""
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
    order_reviews = config.get("order_reviews", 1)  # 1=recentes, 2=antigas, 3=melhores, 4=piores, 5=votadas
    lojas = config.get("lojas", [1, 2])
    delay = config.get("delay", 1.0)
    
    STORES_DIR = ensure_dir(os.path.join(output_dir, "stores"))
    resultados = {}
    
    if 1 in lojas:
        print_progress("Buscando apps no Google Play...")
        df_google = fetch_google(termo, lang, country, n_apps)
        time.sleep(delay)
        
        if not df_google.empty:
            # Garantir que temos exatamente o número solicitado de apps
            df_google = df_google.head(n_apps)
            print_progress(f"Google Play: {len(df_google)} apps encontrados (solicitados: {n_apps})")
            for i, row in enumerate(df_google.itertuples(), 1):
                item = {
                    "app": {
                        "title": row.title, 
                        "developer": row.developer, 
                        "rating": row.rating, 
                        "ratings_count": getattr(row, "ratings_count", 0),
                        "reviews_count": getattr(row, "reviews_count", 0),
                        "installs": row.installs,
                        "price": getattr(row, "price", ""),
                        "genre": getattr(row, "genre", "")
                    }, 
                    "tipo": "app", 
                    "loja": "google_play"
                }
                resultados_tempo_real["stores"].append(item)
                # Exibir em tempo real: branco para título, verde para rating, cinza para metadados
                title_text = row.title
                rating_text = green(f"⭐ {row.rating or 's/d'}")
                ratings_count = getattr(row, "ratings_count", 0)
                ratings_text = gray(f"({ratings_count} avaliações)")
                dev_text = gray(row.developer)
                installs_text = gray(f"Downloads: {row.installs}")
                print_data_item(i, title_text, f"[{green(f'{i}/{len(df_google)}')}] | {rating_text} {ratings_text} | {dev_text}")
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
                
                total_apps_reviews = len(apps_ids)
                app_idx = 0
                
                for app_id in apps_ids:
                    app_idx += 1
                    app_title = df_google.loc[df_google["id"] == app_id, "title"].iloc[0]
                    print_progress(f"  App {app_idx}/{total_apps_reviews}: {app_title}...")
                    
                    # Mapear ordenação do Google Play
                    sort_map = {1: Sort.NEWEST, 2: Sort.MOST_RELEVANT, 3: Sort.RATING}
                    sort_order = sort_map.get(order_reviews, Sort.NEWEST)
                    
                    df_reviews = fetch_reviews_google(app_id, lang, country, max_reviews, sort_order)
                    # Aplicar ordenação adicional se necessário
                    df_reviews = ordenar_reviews(df_reviews, order_reviews)
                    # Garantir que temos exatamente o número solicitado de reviews
                    df_reviews = df_reviews.head(max_reviews)
                    time.sleep(delay)
                    
                    if not df_reviews.empty:
                        # Exibir TODAS as reviews em tempo real - DADOS COMPLETOS SEM CORTES
                        for j, row in enumerate(df_reviews.itertuples(), 1):
                            item = {
                                "review": {
                                    "app": app_title, 
                                    "rating": row.score, 
                                    "content": row.content,
                                    "title": getattr(row, "title", ""),
                                    "thumbsUpCount": getattr(row, "thumbsUpCount", 0),
                                    "replyContent": getattr(row, "replyContent", ""),
                                    "repliedAt": getattr(row, "repliedAt", "")
                                }, 
                                "tipo": "review", 
                                "loja": "google_play"
                            }
                            resultados_tempo_real["stores"].append(item)
                            # Verde para rating, branco para conteúdo COMPLETO
                            rating_text = green(f"⭐{row.score}")
                            content_text = str(row.content)  # DADOS COMPLETOS, SEM CORTES
                            title_review = getattr(row, "title", "")
                            title_str = f"{title_review} | " if title_review else ""
                            votes_str = gray(f"({getattr(row, 'thumbsUpCount', 0)} 👍)")
                            print_data_item(j, content_text, f"{rating_text} | {title_str}")
                            print(f"      {votes_str}")
                            # Exibir resposta do desenvolvedor se houver
                            reply_content = getattr(row, "replyContent", "")
                            if reply_content:
                                reply_date = getattr(row, "repliedAt", "")
                                print(f"        {green('↳ Dev:')} {reply_content[:150]}")
                                if reply_date:
                                    print(f"        {gray('  Data:')} {reply_date}")
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
            # Garantir que temos exatamente o número solicitado de apps
            df_apple = df_apple.head(n_apps)
            print_progress(f"App Store: {len(df_apple)} apps encontrados (solicitados: {n_apps})")
            for i, row in enumerate(df_apple.itertuples(), 1):
                item = {
                    "app": {
                        "title": row.title, 
                        "developer": row.developer, 
                        "rating": row.rating, 
                        "ratings_count": row.ratings_count,
                        "price": getattr(row, "price", 0),
                        "currency": getattr(row, "currency", ""),
                        "genre": getattr(row, "genre", "")
                    }, 
                    "tipo": "app", 
                    "loja": "app_store"
                }
                resultados_tempo_real["stores"].append(item)
                # Exibir em tempo real: branco para título, verde para rating, cinza para metadados
                title_text = row.title
                rating_text = green(f"⭐ {row.rating or 's/d'}")
                ratings_text = gray(f"({row.ratings_count} avaliações)")
                dev_text = gray(row.developer)
                price_text = gray(f"Preço: {getattr(row, 'formattedPrice', 'Grátis')}")
                print_data_item(i, title_text, f"[{green(f'{i}/{len(df_apple)}')}] | {rating_text} {ratings_text} | {dev_text}")
                print(f"      {price_text}")
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
                
                total_apps_reviews = len(apps_ids)
                app_idx = 0
                
                for app_id in apps_ids:
                    app_idx += 1
                    app_title = df_apple.loc[df_apple["id"] == app_id, "title"].iloc[0]
                    print_progress(f"  App {app_idx}/{total_apps_reviews}: {app_title}...")
                    df_reviews = fetch_reviews_apple(app_id, country, max_reviews)
                    # Aplicar ordenação
                    df_reviews = ordenar_reviews(df_reviews, order_reviews)
                    # Garantir que temos exatamente o número solicitado de reviews
                    df_reviews = df_reviews.head(max_reviews)
                    time.sleep(delay)
                    
                    if not df_reviews.empty:
                        # Exibir TODAS as reviews em tempo real - DADOS COMPLETOS SEM CORTES
                        for j, row in enumerate(df_reviews.itertuples(), 1):
                            item = {
                                "review": {
                                    "app": app_title, 
                                    "rating": row.rating, 
                                    "content": row.content,
                                    "title": getattr(row, "title", ""),
                                    "votes": getattr(row, "votes", 0)
                                }, 
                                "tipo": "review", 
                                "loja": "app_store"
                            }
                            resultados_tempo_real["stores"].append(item)
                            # Verde para rating, branco para conteúdo COMPLETO
                            rating_text = green(f"⭐{row.rating}")
                            content_text = str(row.content)  # DADOS COMPLETOS, SEM CORTES
                            title_review = getattr(row, "title", "")
                            title_str = f"{title_review} | " if title_review else ""
                            votes_str = gray(f"({getattr(row, 'votes', 0)} 👍)")
                            print_data_item(j, content_text, f"{rating_text} | {title_str}")
                            print(f"      {votes_str}")
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
    """Normaliza dados de uma fonte para formato unificado - v4.7 com todos os campos expandidos"""
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
        # Processar vídeos com TODOS os metadados - v4.7 expandido
        for v in dados.get("videos", []):
            linhas.append({
                "fonte": "YouTube", "tipo": "video", "termo": termo,
                "conteudo": v.get("titulo", ""), 
                "descricao": v.get("descricao", ""),
                "canal": v.get("canal", ""),
                "channelId": v.get("channelId", ""),
                "channelUrl": v.get("channelUrl", ""),
                "url": v.get("link", ""), 
                "video_id": v.get("videoId", ""),
                "views": v.get("views", 0),
                "likes": v.get("likes", 0),
                "dislikes": v.get("dislikes", 0),  # v4.7
                "favorites": v.get("favorites", 0),  # v4.7
                "commentCount": v.get("commentCount", 0),
                "duration": v.get("duration", ""),
                "dimension": v.get("dimension", ""),  # v4.7
                "definition": v.get("definition", ""),  # v4.7
                "caption": v.get("caption", ""),  # v4.7
                "licensedContent": v.get("licensedContent", False),  # v4.7
                "contentRating": v.get("contentRating", ""),  # v4.7
                "projection": v.get("projection", ""),  # v4.7
                "thumbnail_default": v.get("thumbnail_default", ""),  # v4.7
                "thumbnail_medium": v.get("thumbnail_medium", ""),  # v4.7
                "thumbnail_high": v.get("thumbnail_high", ""),  # v4.7
                "thumbnail_standard": v.get("thumbnail_standard", ""),  # v4.7
                "thumbnail_maxres": v.get("thumbnail_maxres", ""),  # v4.7
                "publicado_em": v.get("publicado_em", ""),
                "tags": ", ".join(v.get("tags", [])) if isinstance(v.get("tags"), list) else "",
                "categoryId": v.get("categoryId", ""),
                "defaultLanguage": v.get("defaultLanguage", ""),  # v4.7
                "defaultAudioLanguage": v.get("defaultAudioLanguage", ""),  # v4.7
                "liveBroadcastContent": v.get("liveBroadcastContent", ""),  # v4.7
                "topicIds": ", ".join(v.get("topicIds", [])) if isinstance(v.get("topicIds"), list) else "",  # v4.7
                "topicCategories": ", ".join(v.get("topicCategories", [])) if isinstance(v.get("topicCategories"), list) else "",  # v4.7
                "recordingDate": v.get("recordingDate", ""),  # v4.7
                "locationDescription": v.get("locationDescription", ""),  # v4.7
                "actualStartTime": v.get("actualStartTime", ""),  # v4.7
                "actualEndTime": v.get("actualEndTime", ""),  # v4.7
                "scheduledStartTime": v.get("scheduledStartTime", ""),  # v4.7
                "scheduledEndTime": v.get("scheduledEndTime", ""),  # v4.7
                "concurrentViewers": v.get("concurrentViewers", ""),  # v4.7
                "activeLiveChatId": v.get("activeLiveChatId", ""),  # v4.7
                "uploadStatus": v.get("uploadStatus", ""),  # v4.7
                "privacyStatus": v.get("privacyStatus", ""),  # v4.7
                "license": v.get("license", ""),  # v4.7
                "embeddable": v.get("embeddable", False),  # v4.7
                "publicStatsViewable": v.get("publicStatsViewable", False),  # v4.7
                "madeForKids": v.get("madeForKids", False),  # v4.7
                "data_coleta": data_coleta
            })
        # Processar comentários com TODOS os metadados - v4.7 expandido
        for c in dados.get("comentarios", []):
            linhas.append({
                "fonte": "YouTube", "tipo": "comentario", "termo": termo,
                "conteudo": c.get("comentario", ""), 
                "autor": c.get("autor", ""),
                "autorId": c.get("autorId", ""),
                "autorUrl": c.get("autorUrl", ""),
                "likes": c.get("likes", 0), 
                "replyCount": c.get("replyCount", 0),
                "totalReplyCount": c.get("totalReplyCount", 0),
                "canReply": c.get("canReply", False),
                "isPublic": c.get("isPublic", True),
                "video_id": c.get("video_id", ""),
                "video_titulo": c.get("video_titulo", ""),
                "publicado_em": c.get("publicado_em", ""),
                "atualizado_em": c.get("atualizado_em", ""),
                "replies_count": len(c.get("replies", [])) if isinstance(c.get("replies"), list) else 0,
                "data_coleta": data_coleta
            })
    
    # Adicionar comentários de YouTube que podem estar apenas em resultados_tempo_real
    # (caso não estejam no dict retornado por run_youtube)
    
    elif fonte_id == 5 and isinstance(dados, dict):  # App Stores
        for loja, df in dados.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Processar apps do Google Play com TODOS os metadados - v4.7
                if loja == "google_play":
                for _, row in df.iterrows():
                    linhas.append({
                        "fonte": f"App Store ({loja.replace('_', ' ').title()})",
                        "tipo": "app", "termo": termo, "conteudo": row.get("title", ""),
                        "desenvolvedor": row.get("developer", ""),
                        "rating": row.get("rating") if pd.notna(row.get("rating")) else None,
                        "ratings_count": row.get("ratings_count", row.get("reviews_count", 0)),
                        "reviews_count": row.get("reviews_count", 0),
                        "installs": row.get("installs", ""),
                        "price": row.get("price", ""),
                        "currency": row.get("currency", ""),
                        "genre": row.get("genre", ""),
                        "contentRating": row.get("contentRating", ""),
                            "contentRatingDescription": row.get("contentRatingDescription", ""),  # v4.7
                            "familyGenre": row.get("familyGenre", ""),  # v4.7
                            "familyGenreId": row.get("familyGenreId", ""),  # v4.7
                        "icon": row.get("icon", row.get("artworkUrl512", "")),
                            "headerImage": row.get("headerImage", ""),  # v4.7
                            "screenshots": row.get("screenshots", ""),  # v4.7
                            "video": row.get("video", ""),  # v4.7
                            "videoImage": row.get("videoImage", ""),  # v4.7
                            "descriptionHTML": row.get("descriptionHTML", ""),  # v4.7
                            "developerId": row.get("developerId", ""),  # v4.7
                            "developerEmail": row.get("developerEmail", ""),  # v4.7
                            "developerWebsite": row.get("developerWebsite", ""),  # v4.7
                            "developerAddress": row.get("developerAddress", ""),  # v4.7
                            "privacyPolicy": row.get("privacyPolicy", ""),  # v4.7
                            "histogram": row.get("histogram", ""),  # v4.7
                            "offersIAP": row.get("offersIAP", False),  # v4.7
                            "adSupported": row.get("adSupported", False),  # v4.7
                            "recentChanges": row.get("recentChanges", ""),  # v4.7
                            "permissions": row.get("permissions", ""),  # v4.7
                            "whatsNew": row.get("whatsNew", ""),  # v4.7
                            "released": row.get("released", ""),  # v4.7
                        "app_id": str(row.get("id", "")), 
                        "url": row.get("url", ""),
                        "version": row.get("version", ""),
                        "updated": row.get("updated", row.get("releaseDate", "")),
                        "data_coleta": data_coleta
                    })
                # Processar apps do App Store com TODOS os metadados - v4.7
                elif loja == "app_store":
                    for _, row in df.iterrows():
                        linhas.append({
                            "fonte": f"App Store ({loja.replace('_', ' ').title()})",
                            "tipo": "app", "termo": termo, "conteudo": row.get("title", ""),
                            "desenvolvedor": row.get("developer", ""),
                            "rating": row.get("rating") if pd.notna(row.get("rating")) else None,
                            "ratings_count": row.get("ratings_count", 0),
                            "price": getattr(row, "price", 0),
                            "currency": getattr(row, "currency", ""),
                            "genre": getattr(row, "genre", ""),
                            "contentRating": getattr(row, "contentAdvisoryRating", ""),
                            "releaseNotes": getattr(row, "releaseNotes", ""),  # v4.7
                            "currentVersionReleaseDate": getattr(row, "currentVersionReleaseDate", ""),  # v4.7
                            "screenshotUrls": getattr(row, "screenshotUrls", ""),  # v4.7
                            "ipadScreenshotUrls": getattr(row, "ipadScreenshotUrls", ""),  # v4.7
                            "appletvScreenshotUrls": getattr(row, "appletvScreenshotUrls", ""),  # v4.7
                            "icon": getattr(row, "artworkUrl512", getattr(row, "artworkUrl100", "")),
                            "artistId": getattr(row, "artistId", ""),  # v4.7
                            "languageCodesISO2A": getattr(row, "languageCodesISO2A", ""),  # v4.7
                            "privacyPolicyUrl": getattr(row, "privacyPolicyUrl", ""),  # v4.7
                            "inAppPurchases": getattr(row, "inAppPurchases", ""),  # v4.7
                            "subscriptionInfo": getattr(row, "subscriptionInfo", ""),  # v4.7
                            "app_id": str(getattr(row, "id", "")), 
                            "url": getattr(row, "url", ""),
                            "version": getattr(row, "version", ""),
                            "updated": getattr(row, "currentVersionReleaseDate", getattr(row, "releaseDate", "")),
                            "data_coleta": data_coleta
                        })
    
    return linhas

def consolidar_dados(resultados: Dict, termo: str, output_dir: str, fontes_ordenadas: Optional[List[int]] = None, resultados_tempo_real: Optional[Dict] = None) -> pd.DataFrame:
    """Consolida todos os dados coletados em um único DataFrame - v4.7 com todos os campos expandidos"""
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
        
        # Reviews de App Stores com TODOS os metadados - v4.6
        if "stores" in resultados_tempo_real:
            for item in resultados_tempo_real["stores"]:
                if isinstance(item, dict) and item.get("tipo") == "review":
                    review_data = item.get("review", {})
                    loja = item.get("loja", "unknown")
                    todas_linhas.append({
                        "fonte": f"App Store ({loja.replace('_', ' ').title()})",
                        "tipo": "review", "termo": termo,
                        "conteudo": review_data.get("content", ""),
                        "title": review_data.get("title", ""),  # Título da review
                        "rating": review_data.get("rating"),
                        "app": review_data.get("app", ""),
                        "thumbsUpCount": review_data.get("thumbsUpCount", review_data.get("votes", 0)),
                        "userId": review_data.get("userId", ""),  # v4.7
                        "date": review_data.get("date", ""),  # v4.7
                        "url": review_data.get("url", ""),  # v4.7
                        "replyContent": review_data.get("replyContent", ""),
                        "repliedAt": review_data.get("repliedAt", ""),
                        "data_coleta": data_coleta
                    })
        
        # Comentários de YouTube com TODOS os metadados - v4.6
        if "youtube" in resultados_tempo_real:
            for item in resultados_tempo_real["youtube"]:
                if isinstance(item, dict) and item.get("tipo") == "comentario":
                    comentario_data = item.get("comentario", {})
                    todas_linhas.append({
                        "fonte": "YouTube", "tipo": "comentario", "termo": termo,
                        "conteudo": comentario_data.get("comentario", ""),
                        "autor": comentario_data.get("autor", ""),
                        "autorId": comentario_data.get("autorId", ""),
                        "autorUrl": comentario_data.get("autorUrl", ""),
                        "likes": comentario_data.get("likes", 0),
                        "replyCount": comentario_data.get("replyCount", 0),
                        "totalReplyCount": comentario_data.get("totalReplyCount", 0),
                        "canReply": comentario_data.get("canReply", False),
                        "isPublic": comentario_data.get("isPublic", True),
                        "video_id": comentario_data.get("video_id", ""),
                        "video_titulo": comentario_data.get("video_titulo", ""),
                        "publicado_em": comentario_data.get("publicado_em", ""),
                        "atualizado_em": comentario_data.get("atualizado_em", ""),
                        "replies_count": len(comentario_data.get("replies", [])) if isinstance(comentario_data.get("replies"), list) else 0,
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
    """Exibe dashboard completo e detalhado com cores padronizadas - v4.6"""
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
        opcoes_selected = parse_todos_input(input("  > [1,2,3,4,5,6,7]: ").strip() or "1,2,3,4", TRENDS_OPCOES, default=1)
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
        coletar_comentarios = input("  Coletar comentários? (s/n) [n]: ").strip().lower() or "n"
        limite_comentarios = 0
        order_comentarios = 1
        if coletar_comentarios == "s":
            limite_comentarios = safe_int_input("  Comentários por vídeo [10]: ", 10, min_val=1, max_val=500)
            print_menu("  Ordenação comentários", "", YOUTUBE_COMMENT_ORDER, default=1)
            comment_order_selected = parse_todos_input(input("  > [1,2,3,4]: ").strip() or "1", YOUTUBE_COMMENT_ORDER, default=1)
            order_comentarios = comment_order_selected[0] if comment_order_selected else 1
        fonte_config = {
            "order": order_selected[0] if order_selected else 1,
            "limite_videos": limite_videos,
            "coletar_comentarios": coletar_comentarios == "s",
            "limite_comentarios": limite_comentarios,
            "order_comentarios": order_comentarios,
            "videos_selecionados": "todos",
        }
    
    elif fonte_id == 5:  # App Stores
        print("\n08. App Store")
        lojas_options = {1: "Google Play Store", 2: "Apple App Store"}
        print_menu("  Lojas", "", lojas_options, default=1)
        lojas_selected = parse_todos_input(input("  > [1,2]: ").strip() or "1,2", lojas_options, default=1)
        n_apps = safe_int_input("  Aplicativos [10]: ", 10, min_val=1, max_val=200)
        coletar_reviews = input("  Coletar reviews? (s/n) [n]: ").strip().lower() or "n"
        max_reviews = 0
        order_reviews = 1
        if coletar_reviews == "s":
            max_reviews = safe_int_input("  Reviews por app [100]: ", 100, min_val=1, max_val=1000)
            print_menu("  Ordenação reviews", "", APP_STORE_REVIEW_ORDER, default=1)
            review_order_selected = parse_todos_input(input("  > [1,2,3,4,5]: ").strip() or "1", APP_STORE_REVIEW_ORDER, default=1)
            order_reviews = review_order_selected[0] if review_order_selected else 1
        fonte_config = {
            "lojas": lojas_selected,
            "n_apps": n_apps,
            "coletar_reviews": coletar_reviews == "s",
            "max_reviews": max_reviews,
            "order_reviews": order_reviews,
            "apps_selecionados": "todos",
        }
    
    return fonte_config

def coletar_configuracao() -> Optional[Dict]:
    """Coleta configuração otimizada v4.6"""
    print("\nMini Research v4.6 - Configuração\n")
    
    # Validar API keys
    keys_status = validate_api_keys()
    missing_keys = [k for k, v in keys_status.items() if not v]
    if missing_keys:
        logger.warning(f"API keys ausentes: {', '.join(missing_keys)}")
    
    config = {}
    
    # 01. TERMOS DE BUSCA (com sanitização e cores padronizadas - v4.7)
    print(f"\n{cyan(bold('01. Termos de busca'))}")
    print(f"  {gray('Separe múltiplos termos por vírgula')}")
    termos_input = input(f"{green('> ')}").strip()
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
