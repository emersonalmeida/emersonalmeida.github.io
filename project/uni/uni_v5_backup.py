#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNI - Coletor Universal de Dados v5.0
=====================================
Sistema completo de coleta de dados de múltiplas fontes com interface CLI otimizada.

Melhorias v5.0:
- Coleta máxima garantida de todas as fontes com retry inteligente
- Base de dados consolidada otimizada e reutilizável
- Melhorias nas fontes que falhavam (Google Scholar, Google Play, Apple App Store, DuckDuckGo, Google News)
- Coleta de todos os campos possíveis de cada fonte
- Organização completa dos dados em CSV estruturado
- Fallback e métodos alternativos para fontes que falham
- Validação e limpeza completa dos dados antes de salvar
- Estatísticas detalhadas de coleta e sucesso
- Melhor tratamento de erros e logging

Autor: Emerson Almeida
Versão: 5.0
Data: 2024
"""

import os
import re
import sys
import json
import time
import string
import locale
import warnings
import logging
import traceback
import csv
import requests
import pandas as pd
import feedparser
from datetime import datetime, timedelta
from pathlib import Path
from itertools import product
from functools import lru_cache
from typing import List, Dict, Optional, Any, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Bibliotecas opcionais
try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False

warnings.filterwarnings("ignore", category=FutureWarning)

# ======================================
# 📝 SISTEMA DE LOGGING
# ======================================

def setup_logging(log_dir: Path = None):
    """Configura sistema de logging detalhado"""
    if log_dir is None:
        log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"uni_v3_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger('UNI_v5')

LOGGER = setup_logging()

# ======================================
# 🎨 ESTILO TERMINAL (Cores e Formatação)
# ======================================

def color(text: str, code: str) -> str:
    """Aplica cor ANSI ao texto"""
    return f"\033[{code}m{text}\033[0m"

def blue(text: str) -> str:
    return color(text, "34")

def green(text: str) -> str:
    return color(text, "32")

def yellow(text: str) -> str:
    return color(text, "33")

def red(text: str) -> str:
    return color(text, "31")

def gray(text: str) -> str:
    return color(text, "90")

def cyan(text: str) -> str:
    return color(text, "36")

def magenta(text: str) -> str:
    return color(text, "35")

def bold(text: str) -> str:
    return color(text, "1")

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('clear' if os.name != 'nt' else 'cls')

def print_header(title: str, char: str = "=", width: int = 70):
    """Imprime cabeçalho formatado"""
    print(blue(f"\n{char * width}"))
    print(blue(f"{title.center(width)}"))
    print(blue(f"{char * width}\n"))

def print_section(title: str):
    """Imprime seção formatada"""
    print(yellow(f"\n{'─' * 70}"))
    print(yellow(f"  {title}"))
    print(yellow(f"{'─' * 70}"))

def print_progress(current: int, total: int, prefix: str = "Progresso", item: str = ""):
    """Exibe barra de progresso melhorada"""
    percent = (current / total) * 100 if total > 0 else 0
    bar_length = 40
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_length - filled)
    item_display = f" - {item[:30]}" if item else ""
    print(f"\r{prefix}: [{bar}] {percent:.1f}% ({current}/{total}){item_display}", end="", flush=True)
    if current == total:
        print()

# ======================================
# ⚙️ CONFIGURAÇÕES E CHAVES DE API
# ======================================

# Diretórios
BASE_DIR = Path("dados")
BASE_DIR.mkdir(exist_ok=True)

# Chaves de API
GOOGLE_API_KEY = "AIzaSyBj80B2fwVvFEMtcQU8tPV_NCNaEmQvzhc"
GOOGLE_CX = "f07ccd3b922d6437b"
BRAVE_API_KEY = "BSAjC9Yvq2s8_hYFIPWQ2QEl_XHpsQp"
SERPAPI_KEY = "e71430bcff8bdc906f7a5ed9ae1538355c2efb0fb88ffa071f7125a76cc2b142"
YOUTUBE_API_KEY = "AIzaSyBj80B2fwVvFEMtcQU8tPV_NCNaEmQvzhc"
REDDIT_CLIENT_ID = "4CmHP70LPG0HI7TEkGsMkQ"
REDDIT_CLIENT_SECRET = "Gn9cxMzoA-inTlTEuv-n8vojVE57FQ"
GNEWS_API_KEY = "91a7bc222ecfdac6c60019c4fb1ec87c"

# URLs e Endpoints
SUGGEST_URL = "https://suggestqueries.google.com/complete/search"
ARXIV_URL = "http://export.arxiv.org/api/query"
WIKIPEDIA_API = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
WIKIPEDIA_SEARCH = "https://{lang}.wikipedia.org/w/api.php"

# Configurações padrão
REGIONS = ["br", "us", "fr", "de", "jp", "uk", "es", "it"]
REGIONS_NAMES = {
    "br": "Brasil",
    "us": "Estados Unidos",
    "fr": "França",
    "de": "Alemanha",
    "jp": "Japão",
    "uk": "Reino Unido",
    "es": "Espanha",
    "it": "Itália"
}
LANGUAGES = {"pt": "pt-BR", "en": "en-US", "es": "es-ES", "fr": "fr-FR", "de": "de-DE"}
SOURCES = {"web": "", "youtube": "yt", "news": "n", "shopping": "sh"}
CLIENTS = ["chrome", "firefox", "safari", "brave"]
CLIENTS_NAMES = {
    "chrome": "Chrome",
    "firefox": "Firefox",
    "safari": "Safari",
    "brave": "Brave"
}

# Comandos de saída
EXIT_COMMANDS = {"sair", "fechar", "terminar", "ok", "exit", "quit", "q", "s"}

# Limites máximos por fonte (MODO COMPLETO - COLETA MÁXIMA)
LIMITES_MAXIMOS = {
    "Google Suggest": 100,
    "SERP - DuckDuckGo": 100,  # Aumentado
    "SERP - Google": 100,
    "SERP - Brave": 100,  # Aumentado
    "SERP - Bing": 100,  # Aumentado
    "YouTube": 50,
    "Reddit": 100,
    "Google News": 100,
    "Hacker News": 100,
    "GitHub": 100,
    "arXiv": 100,
    "Wikipedia": 50,  # Aumentado
    "Google Scholar": 100,
    "Google Play": 50,
    "Apple App Store": 50
}

# ======================================
# 🔧 UTILITÁRIOS
# ======================================

def now_tag() -> str:
    """Retorna timestamp formatado"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dir(path: Path) -> Path:
    """Garante que o diretório existe"""
    path.mkdir(parents=True, exist_ok=True)
    return path

def make_session() -> requests.Session:
    """Cria sessão HTTP com retry e headers melhorados"""
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })
    retry = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    sess.mount("https://", HTTPAdapter(max_retries=retry))
    return sess

SESSION = make_session()

def validar_dados(data: List[Dict], fonte: str = "") -> List[Dict]:
    """Valida e limpa dados antes de salvar"""
    dados_validos = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            LOGGER.warning(f"{fonte}: Item {idx} não é um dicionário, pulando...")
            continue
        
        # Garantir que rank existe
        if "rank" not in item:
            item["rank"] = idx + 1
        
        # Limpar valores None e converter para string vazia quando necessário
        item_limpo = {}
        for key, value in item.items():
            if value is None:
                item_limpo[key] = ""
            elif isinstance(value, (list, dict)) and len(value) == 0:
                item_limpo[key] = ""
            else:
                item_limpo[key] = value
        
        dados_validos.append(item_limpo)
    
    LOGGER.info(f"{fonte}: {len(dados_validos)}/{len(data)} itens válidos após validação")
    return dados_validos

def salvar_csv(data: List[Dict], filename: str, output_dir: Path, fonte: str = "") -> Optional[pd.DataFrame]:
    """Salva dados em CSV otimizado com metadados completos e validação"""
    if not data:
        LOGGER.warning(f"{fonte}: Nenhum dado para salvar em {filename}")
        return None
    
    try:
        # Validar dados antes de salvar
        dados_validos = validar_dados(data, fonte)
        
        if not dados_validos:
            LOGGER.warning(f"{fonte}: Nenhum dado válido após validação para {filename}")
            return None
        
        df = pd.DataFrame(dados_validos)
        filepath = output_dir / filename
        
        # Salvar com encoding UTF-8 BOM para Excel
        df.to_csv(filepath, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
        
        # Verificar se arquivo foi criado
        if filepath.exists():
            tamanho_kb = filepath.stat().st_size / 1024
            LOGGER.info(f"{fonte}: Salvo {len(df)} registros com {len(df.columns)} colunas em {filename} ({tamanho_kb:.1f} KB)")
            return df
        else:
            LOGGER.error(f"{fonte}: Arquivo não foi criado: {filename}")
            return None
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro ao salvar CSV {filename}: {str(e)}")
        LOGGER.debug(traceback.format_exc())
        return None

def salvar_json(data: Any, filename: str, output_dir: Path, fonte: str = ""):
    """Salva dados em JSON com tratamento de erros"""
    try:
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        LOGGER.info(f"{fonte}: JSON salvo em {filename}")
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro ao salvar JSON {filename}: {str(e)}")
        LOGGER.debug(traceback.format_exc())

def check_exit(value: str) -> bool:
    """Verifica se é comando de saída"""
    return value.lower().strip() in EXIT_COMMANDS

def parse_list(value: str, default: str) -> List[str]:
    """Parse lista separada por vírgula"""
    if not value:
        return [default]
    return [x.strip() for x in value.split(",") if x.strip()]

def input_int(prompt: str, default: int, min_val: int = 1, max_val: int = 1000) -> int:
    """Solicita entrada inteira com validação"""
    while True:
        try:
            value = input(f"{prompt} [{default}]: ").strip()
            if not value:
                return default
            num = int(value)
            if min_val <= num <= max_val:
                return num
            print(red(f"  ✗ Valor deve estar entre {min_val} e {max_val}"))
        except ValueError:
            print(red("  ✗ Por favor, digite um número válido"))

def input_choice(prompt: str, choices: List[str], default: str = "") -> str:
    """Solicita escolha de uma lista"""
    while True:
        value = input(f"{prompt} {f'[{default}]' if default else ''}: ").strip().lower()
        if not value and default:
            return default
        if value in [c.lower() for c in choices]:
            return value
        print(red(f"  ✗ Escolha inválida. Opções: {', '.join(choices)}"))

def input_multiple_choice(prompt: str, options: Dict[str, str], default: List[str] = None, allow_all: bool = True) -> List[str]:
    """Solicita seleção múltipla de opções numeradas"""
    if default is None:
        default = []
    
    # Exibir opções
    for key, desc in options.items():
        marker = green("✓") if key in default else " "
        print(f"  {marker} {green(key)}. {desc}")
    
    if allow_all:
        all_key = str(len(options) + 1)
        marker = green("✓") if "todos" in [d.lower() for d in default] else " "
        print(f"  {marker} {green(all_key)}. {bold('Todos')}")
    
    while True:
        default_str = f"[{','.join(default)}]" if default else ""
        escolha = input(f"{prompt} {default_str}: ").strip()
        if not escolha and default:
            return default
        
        # Processar seleção
        selecionados = []
        for item in escolha.split(","):
            item = item.strip()
            if item in options:
                selecionados.append(item)
            elif allow_all and item == str(len(options) + 1):
                return list(options.keys())
            elif item.lower() in ["todos", "all", "t"] and allow_all:
                return list(options.keys())
        
        if selecionados:
            return selecionados
        print(red(f"  ✗ Seleção inválida. Escolha números separados por vírgula (ex: 1,2,3)"))

def parse_multiple_input(value: str, separator: str = ",") -> List[str]:
    """Parse entrada múltipla separada por vírgula"""
    if not value:
        return []
    return [item.strip() for item in value.split(separator) if item.strip()]

# ======================================
# 📡 FUNÇÕES DE COLETA DE DADOS (MÁXIMO DE DADOS)
# ======================================

# --- Google Suggest (MÁXIMO DE DADOS) ---
@lru_cache(maxsize=512)
def coletar_suggest(query: str, region: str = "br", client: str = "chrome", 
                   source: str = "", lang: str = "", limit: int = 10) -> List[Dict]:
    """Coleta sugestões do Google Suggest com todos os dados"""
    resultados = []
    fonte = "Google Suggest"
    
    try:
        LOGGER.info(f"{fonte}: Iniciando coleta para '{query}' (limite: {limit})")
        params = {"q": query, "gl": region, "client": client}
        if lang:
            params["hl"] = lang
        if source:
            params["ds"] = source
        
        r = SESSION.get(SUGGEST_URL, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        suggestions = data[1] if len(data) > 1 else []
        relevance = data[4].get("google:suggestrelevance", [0] * len(suggestions)) if len(data) > 4 and isinstance(data[4], dict) else [0] * len(suggestions)
        types = data[4].get("google:suggesttype", [""] * len(suggestions)) if len(data) > 4 and isinstance(data[4], dict) else [""] * len(suggestions)
        
        for i, (s, r_val, t) in enumerate(zip(suggestions[:limit], relevance[:limit], types[:limit]), 1):
            resultados.append({
                "rank": i,
                "sugestao": s,
                "relevancia": r_val,
                "tipo": t,
                "termo_original": query,
                "regiao": region,
                "cliente": client,
                "fonte_suggest": source or "web"
            })
        
        LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"{fonte}: Erro de requisição: {str(e)}")
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro inesperado: {str(e)}")
        LOGGER.debug(traceback.format_exc())
    
    return resultados

# --- SERP DuckDuckGo (MÁXIMO DE DADOS) ---
def coletar_duckduckgo(term: str, region: str = "br", limite: int = 10) -> List[Dict]:
    """Coleta resultados do DuckDuckGo com todos os dados (melhorado com retry)"""
    global DDGS_AVAILABLE
    fonte = "DuckDuckGo"
    resultados = []
    
    if not DDGS_AVAILABLE:
        LOGGER.warning(f"{fonte}: Biblioteca DDGS não disponível - tentando instalar...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "duckduckgo-search", "--quiet"])
            from ddgs import DDGS
            DDGS_AVAILABLE = True
        except:
            LOGGER.error(f"{fonte}: Não foi possível instalar DDGS")
            return []
    
    # Tentar múltiplas vezes com diferentes configurações
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            LOGGER.info(f"{fonte}: Iniciando coleta para '{term}' (limite: {limite}, tentativa {tentativa + 1}/{max_tentativas})")
            
            with DDGS() as ddgs:
                # Tentar diferentes métodos de busca
                try:
                    results = list(ddgs.text(term, region=region, safesearch="off", max_results=limite))
                except:
                    # Fallback: tentar sem região
                    results = list(ddgs.text(term, safesearch="off", max_results=limite))
                
                for i, r in enumerate(results[:limite], 1):
                    resultados.append({
                        "engine": "duckduckgo",
                        "rank": i,
                        "title": r.get("title", ""),
                        "link": r.get("href", ""),
                        "snippet": r.get("body", "")[:2000] if r.get("body") else "",
                        "regiao": region,
                        "termo": term,
                        "tentativa": tentativa + 1
                    })
            
            if resultados:
                LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
                break
        except Exception as e:
            LOGGER.warning(f"{fonte}: Tentativa {tentativa + 1} falhou: {str(e)}")
            if tentativa < max_tentativas - 1:
                time.sleep(2)  # Aguardar antes de tentar novamente
            else:
                LOGGER.error(f"{fonte}: Todas as tentativas falharam")
                LOGGER.debug(traceback.format_exc())
    
    return resultados

# --- SERP Google (MÁXIMO DE DADOS) ---
def coletar_google(term: str, region: str = "br", lang: str = "pt", limite: int = 10) -> List[Dict]:
    """Coleta resultados do Google Custom Search com todos os dados"""
    fonte = "Google"
    resultados = []
    
    if not GOOGLE_API_AVAILABLE:
        LOGGER.warning(f"{fonte}: Google API não disponível")
        return []
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        LOGGER.warning(f"{fonte}: Chaves de API não configuradas")
        return []
    
    try:
        LOGGER.info(f"{fonte}: Iniciando coleta para '{term}' (limite: {limite})")
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        start, rank = 1, 1
        max_requests = (limite + 9) // 10
        
        for req_num in range(max_requests):
            res = service.cse().list(
                q=term,
                cx=GOOGLE_CX,
                gl=region,
                lr=f"lang_{lang}" if lang != "auto" else None,
                start=start,
                num=min(10, limite - start + 1)
            ).execute()
            
            if "items" not in res:
                break
                
            for item in res["items"]:
                resultados.append({
                    "engine": "google",
                    "rank": rank,
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")[:1000],
                    "displayLink": item.get("displayLink", ""),
                    "formattedUrl": item.get("formattedUrl", ""),
                    "htmlTitle": item.get("htmlTitle", ""),
                    "htmlSnippet": item.get("htmlSnippet", ""),
                    "regiao": region,
                    "idioma": lang,
                    "termo": term
                })
                rank += 1
                if rank > limite:
                    break
            
            if rank > limite or len(res.get("items", [])) < 10:
                break
            start += 10
            time.sleep(0.2)
        
        LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
    except HttpError as e:
        LOGGER.error(f"{fonte}: Erro da API Google: {str(e)}")
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro inesperado: {str(e)}")
        LOGGER.debug(traceback.format_exc())
    return resultados

# --- SERP Brave (MÁXIMO DE DADOS) ---
def coletar_brave(term: str, region: str = "br", limite: int = 10) -> List[Dict]:
    """Coleta resultados do Brave Search com todos os dados"""
    fonte = "Brave"
    resultados = []
    
    if not BRAVE_API_KEY:
        LOGGER.warning(f"{fonte}: Chave de API não configurada")
        return []
    
    try:
        LOGGER.info(f"{fonte}: Iniciando coleta para '{term}' (limite: {limite})")
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
        params = {"q": term, "count": min(limite, 20), "country": region}
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if "web" in data and "results" in data["web"]:
            for i, item in enumerate(data["web"]["results"][:limite], 1):
                resultados.append({
                    "engine": "brave",
                    "rank": i,
                    "title": item.get("title", ""),
                    "link": item.get("url", ""),
                    "snippet": item.get("description", "")[:1000],
                    "age": item.get("age", ""),
                    "language": item.get("language", ""),
                    "regiao": region,
                    "termo": term
                })
        
        LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"{fonte}: Erro de requisição: {str(e)}")
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro inesperado: {str(e)}")
        LOGGER.debug(traceback.format_exc())
    return resultados

# --- SERP Bing (MÁXIMO DE DADOS) ---
def coletar_bing(term: str, region: str = "br", limite: int = 10) -> List[Dict]:
    """Coleta resultados do Bing via SerpAPI com todos os dados"""
    fonte = "Bing"
    resultados = []
    
    if not SERPAPI_KEY:
        LOGGER.warning(f"{fonte}: Chave SerpAPI não configurada")
        return []
    
    url = "https://serpapi.com/search"
    params = {
        "engine": "bing",
        "q": term,
        "cc": region,
        "count": min(limite, 50),
        "api_key": SERPAPI_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        if "organic_results" in data:
            for i, item in enumerate(data["organic_results"][:limite], 1):
                resultados.append({
                    "engine": "bing",
                    "rank": i,
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")[:1000],
                    "displayed_link": item.get("displayed_link", ""),
                    "date": item.get("date", ""),
                    "regiao": region,
                    "termo": term
                })
        
        LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"{fonte}: Erro de requisição: {str(e)}")
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro inesperado: {str(e)}")
        LOGGER.debug(traceback.format_exc())
    return resultados

# --- YouTube (MÁXIMO DE DADOS) ---
def coletar_youtube(query: str, region: str = "br", lang: str = "pt", 
                   order: str = "relevance", max_results: int = 10) -> List[Dict]:
    """Coleta vídeos do YouTube com todos os dados disponíveis"""
    fonte = "YouTube"
    resultados = []
    
    if not YOUTUBE_API_KEY:
        LOGGER.warning(f"{fonte}: Chave de API não configurada")
        return []
    if not GOOGLE_API_AVAILABLE:
        LOGGER.warning(f"{fonte}: Google API não disponível")
        return []
    
    try:
        LOGGER.info(f"{fonte}: Iniciando coleta para '{query}' (limite: {max_results})")
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        max_per_request = 50
        total_collected = 0
        
        while total_collected < max_results:
            request = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=min(max_per_request, max_results - total_collected),
                order=order,
                regionCode=region.upper(),
                relevanceLanguage=lang
            )
            response = request.execute()
            
            items = response.get("items", [])
            if not items:
                break
            
            video_ids = [item["id"]["videoId"] for item in items]
            
            # Buscar estatísticas e detalhes completos
            try:
                stats_request = youtube.videos().list(
                    part="statistics,contentDetails,snippet,status",
                    id=",".join(video_ids)
                )
                stats_response = stats_request.execute()
                stats_dict = {v["id"]: v for v in stats_response.get("items", [])}
            except:
                stats_dict = {}
            
            for item in items:
                snippet = item["snippet"]
                video_id = item["id"]["videoId"]
                stats = stats_dict.get(video_id, {})
                stats_data = stats.get("statistics", {})
                content = stats.get("contentDetails", {})
                snippet_full = stats.get("snippet", snippet)
                
                resultados.append({
                    "rank": total_collected + 1,
                    "title": snippet.get("title", ""),
                    "link": f"https://www.youtube.com/watch?v={video_id}",
                    "video_id": video_id,
                    "channel": snippet.get("channelTitle", ""),
                    "channel_id": snippet.get("channelId", ""),
                    "published": snippet.get("publishedAt", ""),
                    "description": snippet.get("description", "")[:2000],
                    "views": stats_data.get("viewCount", "0"),
                    "likes": stats_data.get("likeCount", "0"),
                    "dislikes": stats_data.get("dislikeCount", "0"),
                    "comments": stats_data.get("commentCount", "0"),
                    "favorites": stats_data.get("favoriteCount", "0"),
                    "duration": content.get("duration", ""),
                    "definition": content.get("definition", ""),
                    "caption": content.get("caption", ""),
                    "tags": ", ".join(snippet_full.get("tags", [])[:10]),
                    "category_id": snippet_full.get("categoryId", ""),
                    "regiao": region,
                    "idioma": lang,
                    "termo": query
                })
                total_collected += 1
                if total_collected >= max_results:
                    break
            
            if "nextPageToken" not in response:
                break
            time.sleep(0.2)
        
        LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
    except HttpError as e:
        LOGGER.error(f"{fonte}: Erro da API YouTube: {str(e)}")
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro inesperado: {str(e)}")
        LOGGER.debug(traceback.format_exc())
    
    return resultados

# --- Reddit (MÁXIMO DE DADOS) ---
def coletar_reddit(termo: str, subreddit: str = "all", sort: str = "relevance", 
                  limit_posts: int = 10, limit_comments: int = 5) -> List[Dict]:
    """Coleta posts do Reddit com todos os dados disponíveis"""
    fonte = "Reddit"
    resultados = []
    
    if not PRAW_AVAILABLE:
        LOGGER.warning(f"{fonte}: Biblioteca PRAW não disponível")
        return []
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        LOGGER.warning(f"{fonte}: Credenciais Reddit não configuradas")
        return []
    
    try:
        LOGGER.info(f"{fonte}: Iniciando coleta para '{termo}' (subreddit: {subreddit}, limite: {limit_posts})")
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent="uni-collector-v2"
        )
        
        sub = reddit.subreddit(subreddit if subreddit.lower() != "all" else "all")
        
        if sort == "new":
            posts = sub.search(termo, sort="new", limit=limit_posts, time_filter="all")
        elif sort == "top":
            posts = sub.search(termo, sort="top", limit=limit_posts, time_filter="all")
        else:
            posts = sub.search(termo, sort="relevance", limit=limit_posts, time_filter="all")
        
        for idx, post in enumerate(posts, 1):
            resultados.append({
                "rank": idx,
                "title": post.title,
                "link": f"https://reddit.com{post.permalink}",
                "subreddit": post.subreddit.display_name,
                "subreddit_id": post.subreddit.id,
                "score": post.score,
                "upvotes": post.ups,
                "downvotes": post.downs,
                "comments": post.num_comments,
                "upvote_ratio": getattr(post, 'upvote_ratio', 0),
                "created": datetime.fromtimestamp(post.created_utc).isoformat(),
                "created_utc": post.created_utc,
                "author": str(post.author) if post.author else "[deleted]",
                "author_flair": getattr(post.author, 'flair_text', '') if post.author else "",
                "selftext": post.selftext[:2000] if hasattr(post, 'selftext') else "",
                "is_self": post.is_self,
                "is_video": getattr(post, 'is_video', False),
                "over_18": post.over_18,
                "gilded": post.gilded,
                "stickied": post.stickied,
                "locked": post.locked,
                "domain": post.domain,
                "url": post.url,
                "termo": termo,
                "sort": sort
            })
        
        LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro na coleta: {str(e)}")
        LOGGER.debug(traceback.format_exc())
    return resultados

# --- Google News (MÁXIMO DE DADOS) ---
def coletar_gnews(termo: str, lang: str = "pt", country: str = "br", 
                 from_date: Optional[str] = None, to_date: Optional[str] = None,
                 max_results: int = 10) -> List[Dict]:
    """Coleta notícias do Google News com todos os dados (melhorado com fallback)"""
    fonte = "Google News"
    resultados = []
    
    if not GNEWS_API_KEY:
        LOGGER.warning(f"{fonte}: Chave de API não configurada - tentando método alternativo")
        # Fallback: tentar buscar via RSS feed do Google News
        try:
            url_rss = f"https://news.google.com/rss/search?q={termo}&hl={lang}&gl={country}&ceid={country}:{lang}"
            resp = requests.get(url_rss, timeout=15)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.text)
                for i, entry in enumerate(feed.entries[:max_results], 1):
                    resultados.append({
                        "rank": i,
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "description": entry.get("summary", "")[:2000],
                        "source": entry.get("source", {}).get("title", "") if entry.get("source") else "",
                        "termo": termo,
                        "idioma": lang,
                        "pais": country,
                        "metodo": "rss_fallback"
                    })
                LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados via RSS fallback")
                return resultados
        except Exception as e:
            LOGGER.warning(f"{fonte}: Fallback RSS também falhou: {str(e)}")
        return []
    
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": termo,
        "lang": lang,
        "country": country,
        "max": min(max_results, 100),
        "apikey": GNEWS_API_KEY
    }
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    
    try:
        LOGGER.info(f"{fonte}: Iniciando coleta para '{termo}' (limite: {max_results})")
        resp = SESSION.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        
        # Verificar se há erros na resposta
        if "errors" in data:
            LOGGER.warning(f"{fonte}: API retornou erros: {data.get('errors')}")
            return resultados
        
        for i, article in enumerate(data.get("articles", []), 1):
            resultados.append({
                "rank": i,
                "title": article.get("title", ""),
                "link": article.get("url", ""),
                "source": article.get("source", {}).get("name", ""),
                "source_url": article.get("source", {}).get("url", ""),
                "published": article.get("publishedAt", ""),
                "description": article.get("description", "")[:2000] if article.get("description") else "",
                "image": article.get("image", ""),
                "content": article.get("content", "")[:5000] if article.get("content") else "",
                "termo": termo,
                "idioma": lang,
                "pais": country,
                "metodo": "api"
            })
        
        LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"{fonte}: Erro de requisição: {str(e)}")
        # Tentar fallback RSS
        try:
            url_rss = f"https://news.google.com/rss/search?q={termo}&hl={lang}&gl={country}&ceid={country}:{lang}"
            resp = requests.get(url_rss, timeout=15)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.text)
                for i, entry in enumerate(feed.entries[:max_results], 1):
                    resultados.append({
                        "rank": i,
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "description": entry.get("summary", "")[:2000],
                        "source": entry.get("source", {}).get("title", "") if entry.get("source") else "",
                        "termo": termo,
                        "idioma": lang,
                        "pais": country,
                        "metodo": "rss_fallback"
                    })
                LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados via RSS fallback")
        except:
            pass
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro inesperado: {str(e)}")
        LOGGER.debug(traceback.format_exc())
    return resultados

# --- Hacker News (MÁXIMO DE DADOS) ---
def coletar_hackernews(termo: str, limite: int = 10) -> List[Dict]:
    """Coleta resultados do Hacker News com todos os dados"""
    fonte = "Hacker News"
    resultados = []
    
    try:
        LOGGER.info(f"{fonte}: Iniciando coleta para '{termo}' (limite: {limite})")
        url = "https://hn.algolia.com/api/v1/search"
        params = {
            "query": termo,
            "tags": "story",
            "hitsPerPage": min(limite, 1000),
            "numericFilters": ""
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        for i, hit in enumerate(data.get("hits", [])[:limite], 1):
            resultados.append({
                "rank": i,
                "title": hit.get("title", ""),
                "link": hit.get("url", "") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                "object_id": hit.get("objectID", ""),
                "score": hit.get("points", 0),
                "comments": hit.get("num_comments", 0),
                "author": hit.get("author", ""),
                "created": hit.get("created_at", ""),
                "created_at_i": hit.get("created_at_i", 0),
                "story_text": hit.get("story_text", "")[:2000] if hit.get("story_text") else "",
                "comment_text": hit.get("comment_text", "")[:1000] if hit.get("comment_text") else "",
                "num_points": hit.get("points", 0),
                "story_id": hit.get("story_id", ""),
                "story_title": hit.get("story_title", ""),
                "story_url": hit.get("story_url", ""),
                "parent_id": hit.get("parent_id", ""),
                "relevancy_score": hit.get("relevancy_score", 0),
                "termo": termo
            })
        
        LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"{fonte}: Erro de requisição: {str(e)}")
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro inesperado: {str(e)}")
        LOGGER.debug(traceback.format_exc())
    return resultados

# --- GitHub (MÁXIMO DE DADOS) ---
def coletar_github(query: str, limite: int = 10) -> List[Dict]:
    """Coleta repositórios do GitHub com todos os dados"""
    fonte = "GitHub"
    resultados = []
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": min(limite, 100)
    }
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        for i, repo in enumerate(data.get("items", [])[:limite], 1):
            resultados.append({
                "rank": i,
                "nome": repo.get("full_name", ""),
                "url": repo.get("html_url", ""),
                "descricao": repo.get("description", ""),
                "estrelas": repo.get("stargazers_count", 0),
                "watchers": repo.get("watchers_count", 0),
                "forks": repo.get("forks_count", 0),
                "linguagem": repo.get("language", ""),
                "criado": repo.get("created_at", ""),
                "atualizado": repo.get("updated_at", ""),
                "pushed_at": repo.get("pushed_at", ""),
                "tamanho": repo.get("size", 0),
                "licenca": repo.get("license", {}).get("name", "") if repo.get("license") else "",
                "topics": ", ".join(repo.get("topics", [])),
                "open_issues": repo.get("open_issues_count", 0),
                "default_branch": repo.get("default_branch", ""),
                "archived": repo.get("archived", False),
                "disabled": repo.get("disabled", False),
                "private": repo.get("private", False),
                "fork": repo.get("fork", False),
                "owner": repo.get("owner", {}).get("login", ""),
                "owner_type": repo.get("owner", {}).get("type", ""),
                "termo": query
            })
        
        LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"{fonte}: Erro de requisição: {str(e)}")
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro inesperado: {str(e)}")
        LOGGER.debug(traceback.format_exc())
    return resultados

# --- arXiv (MÁXIMO DE DADOS) ---
def coletar_arxiv(termo: str, limite: int = 10, ordenacao: str = "relevance") -> List[Dict]:
    """Coleta artigos do arXiv com todos os dados"""
    fonte = "arXiv"
    resultados = []
    query = f"search_query=all:{termo}&start=0&max_results={min(limite, 2000)}&sortBy={ordenacao}"
    
    try:
        LOGGER.info(f"{fonte}: Iniciando coleta para '{termo}' (limite: {limite})")
        resp = requests.get(f"{ARXIV_URL}?{query}", timeout=20)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        
        for i, entry in enumerate(feed.entries[:limite], 1):
            autores = ", ".join([a.name for a in entry.authors]) if "authors" in entry else "N/A"
            resultados.append({
                "rank": i,
                "titulo": entry.title.strip().replace("\n", " "),
                "autores": autores,
                "autores_lista": [a.name for a in entry.authors] if "authors" in entry else [],
                "data": entry.published[:10] if "published" in entry else "N/A",
                "data_completa": entry.published if "published" in entry else "",
                "link": entry.link,
                "resumo": entry.summary[:2000] if "summary" in entry else "",
                "categorias": ", ".join([cat.term for cat in entry.tags]) if "tags" in entry else "",
                "categorias_lista": [cat.term for cat in entry.tags] if "tags" in entry else [],
                "arxiv_id": entry.id.split("/")[-1] if "/" in entry.id else "",
                "doi": entry.get("arxiv_doi", ""),
                "comment": entry.get("arxiv_comment", ""),
                "journal_ref": entry.get("arxiv_journal_ref", ""),
                "primary_category": entry.get("arxiv_primary_category", {}).get("term", "") if entry.get("arxiv_primary_category") else "",
                "termo": termo
            })
        
        LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"{fonte}: Erro de requisição: {str(e)}")
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro inesperado: {str(e)}")
        LOGGER.debug(traceback.format_exc())
    return resultados

# --- Wikipedia (MÁXIMO DE DADOS - CORRIGIDO) ---
def coletar_wikipedia(termo: str, lang: str = "pt", limite: int = 10) -> List[Dict]:
    """Coleta informações da Wikipedia com todos os dados (corrigido)"""
    fonte = "Wikipedia"
    resultados = []
    
    try:
        LOGGER.info(f"{fonte}: Iniciando coleta para '{termo}' (limite: {limite}, lang: {lang})")
        search_url = WIKIPEDIA_SEARCH.format(lang=lang)
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": termo,
            "srlimit": min(limite, 50),
            "srnamespace": 0
        }
        
        resp = requests.get(search_url, params=params, headers=SESSION.headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        pages = data.get("query", {}).get("search", [])
        
        for i, page in enumerate(pages[:limite], 1):
            title = page.get("title", "")
            try:
                summary_url = WIKIPEDIA_API.format(lang=lang, title=title.replace(" ", "_"))
                page_resp = requests.get(summary_url, headers=SESSION.headers, timeout=10)
                if page_resp.status_code == 200:
                    page_data = page_resp.json()
                    resultados.append({
                        "rank": i,
                        "titulo": page_data.get("title", title),
                        "url": page_data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "resumo": page_data.get("extract", "")[:2000],
                        "extract_html": page_data.get("extract_html", "")[:5000],
                        "thumbnail": page_data.get("thumbnail", {}).get("source", "") if page_data.get("thumbnail") else "",
                        "originalimage": page_data.get("originalimage", {}).get("source", "") if page_data.get("originalimage") else "",
                        "lang": page_data.get("lang", lang),
                        "dir": page_data.get("dir", ""),
                        "timestamp": page_data.get("timestamp", ""),
                        "description": page_data.get("description", ""),
                        "coordinates": page_data.get("coordinates", {}),
                        "snippet": page.get("snippet", "")[:500],
                        "size": page.get("size", 0),
                        "wordcount": page.get("wordcount", 0),
                        "termo": termo,
                        "idioma": lang
                    })
                else:
                    resultados.append({
                        "rank": i,
                        "titulo": title,
                        "url": f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}",
                        "resumo": page.get("snippet", "")[:2000],
                        "snippet": page.get("snippet", "")[:500],
                        "size": page.get("size", 0),
                        "wordcount": page.get("wordcount", 0),
                        "termo": termo,
                        "idioma": lang
                    })
            except Exception as e:
                LOGGER.warning(f"{fonte}: Erro ao buscar detalhes da página '{title}': {str(e)}")
                resultados.append({
                    "rank": i,
                    "titulo": title,
                    "url": f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}",
                    "resumo": page.get("snippet", "")[:2000],
                    "snippet": page.get("snippet", "")[:500],
                    "size": page.get("size", 0),
                    "wordcount": page.get("wordcount", 0),
                        "termo": termo,
                        "idioma": lang
                })
        
        LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"{fonte}: Erro de requisição: {str(e)}")
    except Exception as e:
        LOGGER.error(f"{fonte}: Erro inesperado: {str(e)}")
        LOGGER.debug(traceback.format_exc())
    return resultados

# --- Google Scholar (MÁXIMO DE DADOS) ---
def coletar_scholar(termo: str, limite: int = 10) -> List[Dict]:
    """Coleta artigos acadêmicos via Semantic Scholar com todos os dados (melhorado)"""
    fonte = "Google Scholar"
    resultados = []
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    # Tentar múltiplas vezes com diferentes configurações
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            LOGGER.info(f"{fonte}: Iniciando coleta para '{termo}' (limite: {limite}, tentativa {tentativa + 1}/{max_tentativas})")
            
            params = {
                "query": termo,
                "limit": min(limite, 100),
                "fields": "title,authors,year,url,abstract,citationCount,referenceCount,venue,fieldsOfStudy,publicationTypes,publicationDate,journal,externalIds,isOpenAccess,openAccessPdf"
            }
            
            resp = SESSION.get(url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            
            if "data" not in data or not data.get("data"):
                LOGGER.warning(f"{fonte}: Nenhum resultado retornado pela API")
                if tentativa < max_tentativas - 1:
                    time.sleep(2)
                    continue
                break
            
            for i, paper in enumerate(data.get("data", [])[:limite], 1):
                autores = ", ".join([a.get("name", "") for a in paper.get("authors", [])[:10]])
                resultados.append({
                    "rank": i,
                    "titulo": paper.get("title", ""),
                    "autores": autores,
                    "autores_lista": [a.get("name", "") for a in paper.get("authors", [])],
                    "ano": paper.get("year", ""),
                    "link": paper.get("url", ""),
                    "resumo": paper.get("abstract", "")[:3000] if paper.get("abstract") else "",
                    "citacoes": paper.get("citationCount", 0),
                    "referencias": paper.get("referenceCount", 0),
                    "venue": paper.get("venue", ""),
                    "fields_of_study": ", ".join(paper.get("fieldsOfStudy", [])),
                    "publication_types": ", ".join(paper.get("publicationTypes", [])),
                    "publication_date": paper.get("publicationDate", ""),
                    "journal": paper.get("journal", {}).get("name", "") if paper.get("journal") else "",
                    "paper_id": paper.get("paperId", ""),
                    "external_ids": json.dumps(paper.get("externalIds", {})),
                    "is_open_access": paper.get("isOpenAccess", False),
                    "open_access_pdf": paper.get("openAccessPdf", {}).get("url", "") if paper.get("openAccessPdf") else "",
                    "termo": termo,
                    "tentativa": tentativa + 1
                })
            
            if resultados:
                LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
                break
        except requests.exceptions.RequestException as e:
            LOGGER.warning(f"{fonte}: Tentativa {tentativa + 1} falhou: {str(e)}")
            if tentativa < max_tentativas - 1:
                time.sleep(2)
            else:
                LOGGER.error(f"{fonte}: Todas as tentativas falharam")
        except Exception as e:
            LOGGER.error(f"{fonte}: Erro inesperado: {str(e)}")
            LOGGER.debug(traceback.format_exc())
            if tentativa < max_tentativas - 1:
                time.sleep(2)
    
    return resultados

# --- Google Play (MÁXIMO DE DADOS - CORRIGIDO) ---
def coletar_google_play(term: str, lang: str = "pt", country: str = "br", n: int = 10) -> List[Dict]:
    """Coleta apps do Google Play com todos os dados (melhorado com retry)"""
    fonte = "Google Play"
    resultados = []
    
    # Tentar importar biblioteca
    try:
        from google_play_scraper import app, search as gplay_search
    except ImportError:
        LOGGER.warning(f"{fonte}: Biblioteca google_play_scraper não disponível - tentando instalar...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "google-play-scraper", "--quiet"])
            from google_play_scraper import app, search as gplay_search
        except:
            LOGGER.error(f"{fonte}: Não foi possível instalar google-play-scraper")
            return []
    
    # Tentar múltiplas vezes
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            LOGGER.info(f"{fonte}: Iniciando coleta para '{term}' (limite: {n}, tentativa {tentativa + 1}/{max_tentativas})")
            
            apps = gplay_search(term, lang=lang, country=country, n=n)
            
            if not apps:
                LOGGER.warning(f"{fonte}: Nenhum app encontrado na busca")
                if tentativa < max_tentativas - 1:
                    time.sleep(2)
                    continue
                break
            
            for i, app_data in enumerate(apps[:n], 1):
                app_id = app_data.get("appId", "")
                if app_id:
                    try:
                        details = app(app_id, lang=lang, country=country)
                        resultados.append({
                            "rank": i,
                            "nome": details.get("title", app_data.get("title", "")),
                            "link": f"https://play.google.com/store/apps/details?id={app_id}",
                            "app_id": app_id,
                            "estrelas": details.get("score", 0),
                            "avaliacoes": details.get("reviews", 0),
                            "desenvolvedor": details.get("developer", ""),
                            "desenvolvedor_id": details.get("developerId", ""),
                            "categoria": details.get("genre", ""),
                            "categoria_id": details.get("genreId", ""),
                            "instalacoes": details.get("installs", ""),
                            "preco": details.get("price", 0),
                            "currency": details.get("currency", ""),
                            "free": details.get("free", True),
                            "descricao": details.get("description", "")[:3000] if details.get("description") else "",
                            "summary": details.get("summary", "")[:1000] if details.get("summary") else "",
                            "icon": details.get("icon", ""),
                            "screenshots": ", ".join(details.get("screenshots", [])[:10]),
                            "content_rating": details.get("contentRating", ""),
                            "ad_supported": details.get("adSupported", False),
                            "contains_ads": details.get("containsAds", False),
                            "released": details.get("released", ""),
                            "updated": details.get("updated", ""),
                            "version": details.get("version", ""),
                            "termo": term,
                            "idioma": lang,
                            "pais": country,
                            "tentativa": tentativa + 1
                        })
                    except Exception as e:
                        LOGGER.warning(f"{fonte}: Erro ao buscar detalhes do app {app_id}: {str(e)}")
                        resultados.append({
                            "rank": i,
                            "nome": app_data.get("title", ""),
                            "link": f"https://play.google.com/store/apps/details?id={app_id}",
                            "app_id": app_id,
                            "estrelas": app_data.get("score", 0),
                            "avaliacoes": app_data.get("reviews", 0),
                            "desenvolvedor": app_data.get("developer", ""),
                            "termo": term,
                            "tentativa": tentativa + 1
                        })
            
            if resultados:
                LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
                break
        except Exception as e:
            LOGGER.warning(f"{fonte}: Tentativa {tentativa + 1} falhou: {str(e)}")
            if tentativa < max_tentativas - 1:
                time.sleep(2)
            else:
                LOGGER.error(f"{fonte}: Todas as tentativas falharam")
                LOGGER.debug(traceback.format_exc())
    
    return resultados

# --- Apple App Store (MÁXIMO DE DADOS) ---
def coletar_apple_store(term: str, country: str = "br", limit: int = 10) -> List[Dict]:
    """Coleta apps da Apple App Store com todos os dados (melhorado com retry)"""
    fonte = "Apple App Store"
    resultados = []
    
    # Tentar importar biblioteca
    try:
        from app_store_scraper import AppStore
    except ImportError:
        LOGGER.warning(f"{fonte}: Biblioteca app_store_scraper não disponível - tentando instalar...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "app-store-scraper", "--quiet"])
            from app_store_scraper import AppStore
        except:
            LOGGER.error(f"{fonte}: Não foi possível instalar app-store-scraper")
            return []
    
    # Tentar múltiplas vezes
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            LOGGER.info(f"{fonte}: Iniciando coleta para '{term}' (limite: {limit}, tentativa {tentativa + 1}/{max_tentativas})")
            
            store = AppStore(country=country, app_name=term)
            store.search()
            
            if not store.apps:
                LOGGER.warning(f"{fonte}: Nenhum app encontrado na busca")
                if tentativa < max_tentativas - 1:
                    time.sleep(2)
                    continue
                break
            
            for i, app in enumerate(store.apps[:limit], 1):
                resultados.append({
                    "rank": i,
                    "nome": app.get("name", ""),
                    "link": app.get("url", ""),
                    "app_id": app.get("id", ""),
                    "estrelas": app.get("rating", 0),
                    "avaliacoes": app.get("user_rating_count", 0),
                    "desenvolvedor": app.get("developer", ""),
                    "categoria": app.get("genre", ""),
                    "preco": app.get("price", 0),
                    "currency": app.get("currency", ""),
                    "descricao": app.get("description", "")[:3000] if app.get("description") else "",
                    "icon": app.get("icon", ""),
                    "screenshots": ", ".join(app.get("screenshots", [])[:10]),
                    "content_rating": app.get("content_rating", ""),
                    "released": app.get("released", ""),
                    "updated": app.get("updated", ""),
                    "version": app.get("version", ""),
                    "termo": term,
                    "pais": country,
                    "tentativa": tentativa + 1
                })
            
            if resultados:
                LOGGER.info(f"{fonte}: Coletados {len(resultados)} resultados com sucesso")
                break
        except Exception as e:
            LOGGER.warning(f"{fonte}: Tentativa {tentativa + 1} falhou: {str(e)}")
            if tentativa < max_tentativas - 1:
                time.sleep(2)
            else:
                LOGGER.error(f"{fonte}: Todas as tentativas falharam")
                LOGGER.debug(traceback.format_exc())
    
    return resultados

# ======================================
# 🎯 MENU E OPÇÕES (PADRONIZADO E ORGANIZADO)
# ======================================

FONTES_DISPONIVEIS = {
    "1": {
        "nome": "Google Suggest",
        "funcao": lambda t, r, l, lim: coletar_suggest(t, r, "chrome", "", l, lim),
        "descricao": "Sugestões de busca do Google",
        "limite_max": LIMITES_MAXIMOS["Google Suggest"],
        "categoria": "Busca"
    },
    "2": {
        "nome": "SERP - DuckDuckGo",
        "funcao": lambda t, r, l, lim: coletar_duckduckgo(t, r, lim),
        "descricao": "Resultados de busca DuckDuckGo",
        "limite_max": LIMITES_MAXIMOS["SERP - DuckDuckGo"],
        "categoria": "Busca"
    },
    "3": {
        "nome": "SERP - Google",
        "funcao": lambda t, r, l, lim: coletar_google(t, r, l, lim),
        "descricao": "Resultados de busca Google",
        "limite_max": LIMITES_MAXIMOS["SERP - Google"],
        "categoria": "Busca"
    },
    "4": {
        "nome": "SERP - Brave",
        "funcao": lambda t, r, l, lim: coletar_brave(t, r, lim),
        "descricao": "Resultados de busca Brave",
        "limite_max": LIMITES_MAXIMOS["SERP - Brave"],
        "categoria": "Busca"
    },
    "5": {
        "nome": "SERP - Bing",
        "funcao": lambda t, r, l, lim: coletar_bing(t, r, lim),
        "descricao": "Resultados de busca Bing",
        "limite_max": LIMITES_MAXIMOS["SERP - Bing"],
        "categoria": "Busca"
    },
    "6": {
        "nome": "YouTube",
        "funcao": lambda t, r, l, lim: coletar_youtube(t, r, l, "relevance", lim),
        "descricao": "Vídeos do YouTube",
        "limite_max": LIMITES_MAXIMOS["YouTube"],
        "categoria": "Mídia"
    },
    "7": {
        "nome": "Reddit",
        "funcao": lambda t, r, l, lim: coletar_reddit(t, "all", "relevance", lim, 5),
        "descricao": "Posts do Reddit",
        "limite_max": LIMITES_MAXIMOS["Reddit"],
        "categoria": "Social"
    },
    "8": {
        "nome": "Google News",
        "funcao": lambda t, r, l, lim: coletar_gnews(t, l, r, None, None, lim),
        "descricao": "Notícias do Google News",
        "limite_max": LIMITES_MAXIMOS["Google News"],
        "categoria": "Notícias"
    },
    "9": {
        "nome": "Hacker News",
        "funcao": lambda t, r, l, lim: coletar_hackernews(t, lim),
        "descricao": "Posts do Hacker News",
        "limite_max": LIMITES_MAXIMOS["Hacker News"],
        "categoria": "Tecnologia"
    },
    "10": {
        "nome": "GitHub",
        "funcao": lambda t, r, l, lim: coletar_github(t, lim),
        "descricao": "Repositórios do GitHub",
        "limite_max": LIMITES_MAXIMOS["GitHub"],
        "categoria": "Desenvolvimento"
    },
    "11": {
        "nome": "arXiv",
        "funcao": lambda t, r, l, lim: coletar_arxiv(t, lim, "relevance"),
        "descricao": "Artigos científicos do arXiv",
        "limite_max": LIMITES_MAXIMOS["arXiv"],
        "categoria": "Acadêmico"
    },
    "12": {
        "nome": "Wikipedia",
        "funcao": lambda t, r, l, lim: coletar_wikipedia(t, l, lim),
        "descricao": "Páginas da Wikipedia",
        "limite_max": LIMITES_MAXIMOS["Wikipedia"],
        "categoria": "Enciclopédia"
    },
    "13": {
        "nome": "Google Scholar",
        "funcao": lambda t, r, l, lim: coletar_scholar(t, lim),
        "descricao": "Artigos acadêmicos",
        "limite_max": LIMITES_MAXIMOS["Google Scholar"],
        "categoria": "Acadêmico"
    },
    "14": {
        "nome": "Google Play",
        "funcao": lambda t, r, l, lim: coletar_google_play(t, l, r, lim),
        "descricao": "Apps do Google Play",
        "limite_max": LIMITES_MAXIMOS["Google Play"],
        "categoria": "Apps"
    },
    "15": {
        "nome": "Apple App Store",
        "funcao": lambda t, r, l, lim: coletar_apple_store(t, r, lim),
        "descricao": "Apps da Apple App Store",
        "limite_max": LIMITES_MAXIMOS["Apple App Store"],
        "categoria": "Apps"
    }
}

def exibir_menu_principal():
    """Exibe menu principal padronizado"""
    print_header("MENU PRINCIPAL", "=", 70)
    print(f"  {green('1')}. {bold('Nova Coleta')} - Iniciar coleta de dados")
    print(f"  {green('2')}. {bold('Fontes Disponíveis')} - Ver todas as fontes")
    print(f"  {green('3')}. {bold('Configurações')} - Limites e opções")
    print(f"  {green('4')}. {bold('Sobre')} - Informações do sistema")
    print(f"  {green('sair')}. {bold('Sair')} - Encerrar programa\n")

def exibir_menu_modo():
    """Exibe menu de seleção de modo"""
    print_header("SELECIONE O MODO DE COLETA", "=", 70)
    print(f"  {green('1')}. {bold('Modo Completo')} - Coleta máximo de dados automaticamente de todas as fontes")
    print(f"  {green('2')}. {bold('Modo Personalizado')} - Configure tudo manualmente com opções detalhadas")
    print(f"  {green('voltar')}. {bold('Voltar')} - Retornar ao menu principal\n")

def configurar_termos() -> List[str]:
    """Configura termos de busca (múltiplos)"""
    print_header("01. TERMOS DE BUSCA", "=", 70)
    print(f"{cyan('Separe múltiplos termos por vírgula')}\n")
    
    termos_input = input(f"{blue('> Termos de busca')}: ").strip()
    if check_exit(termos_input) or not termos_input:
        return []
    
    termos = parse_multiple_input(termos_input)
    if not termos:
        print(red("  ✗ Nenhum termo válido informado"))
        return []
    
    print(green(f"  ✓ {len(termos)} termo(s) configurado(s): {', '.join(termos)}\n"))
    return termos

def configurar_regioes() -> List[str]:
    """Configura regiões (múltiplas)"""
    print_header("02. REGIÕES", "=", 70)
    
    opcoes = {}
    for idx, reg in enumerate(REGIONS, 1):
        nome = REGIONS_NAMES.get(reg, reg.upper())
        opcoes[str(idx)] = f"{nome} ({reg})"
    
    opcoes[str(len(REGIONS) + 1)] = "Todos"
    
    print(f"{cyan('Selecione as regiões (separadas por vírgula)')}\n")
    selecionados = input_multiple_choice(f"{blue('> Regiões')}", opcoes, ["1"], True)
    
    regioes = []
    if str(len(REGIONS) + 1) in selecionados or "todos" in [s.lower() for s in selecionados]:
        regioes = REGIONS.copy()
    else:
        for sel in selecionados:
            if sel.isdigit() and 1 <= int(sel) <= len(REGIONS):
                regioes.append(REGIONS[int(sel) - 1])
    
    if not regioes:
        regioes = ["br"]  # Default
    
    print(green(f"  ✓ {len(regioes)} região(ões) selecionada(s): {', '.join([REGIONS_NAMES.get(r, r) for r in regioes])}\n"))
    return regioes

def configurar_plataformas() -> Dict[str, bool]:
    """Configura quais plataformas usar"""
    print_header("03. PLATAFORMAS", "=", 70)
    
    plataformas = {
        "1": "Google Suggest - Termos e sugestões de busca",
        "2": "Google Trends - Tendências e Regiões",
        "3": "Buscadores (SERP) - Links e Conteúdos",
        "4": "YouTube - Vídeos e Comentários",
        "5": "App Stores - Aplicativos e Avaliações",
        "6": "Reddit - Posts e Discussões",
        "7": "Notícias - Google News",
        "8": "Acadêmico - arXiv, Scholar, Wikipedia",
        "9": "Desenvolvimento - GitHub, Hacker News"
    }
    
    print(f"{cyan('Selecione as plataformas (separadas por vírgula)')}\n")
    selecionados = input_multiple_choice(f"{blue('> Plataformas')}", plataformas, ["6"], True)
    
    # Mapear para fontes disponíveis
    config = {
        "suggest": "1" in selecionados or "6" in selecionados,
        "trends": "2" in selecionados or "6" in selecionados,
        "serp": "3" in selecionados or "6" in selecionados,
        "youtube": "4" in selecionados or "6" in selecionados,
        "app_stores": "5" in selecionados or "6" in selecionados,
        "reddit": "6" in selecionados or "6" in selecionados,
        "news": "7" in selecionados or "6" in selecionados,
        "academico": "8" in selecionados or "6" in selecionados,
        "desenvolvimento": "9" in selecionados or "6" in selecionados
    }
    
    print(green(f"  ✓ Plataformas configuradas\n"))
    return config

def exibir_menu_fontes():
    """Exibe menu de fontes organizado por categoria"""
    print_header("FONTES DISPONÍVEIS", "=", 70)
    
    # Agrupar por categoria
    categorias = {}
    for key, fonte in FONTES_DISPONIVEIS.items():
        cat = fonte.get("categoria", "Outros")
        if cat not in categorias:
            categorias[cat] = []
        categorias[cat].append((key, fonte))
    
    # Exibir por categoria
    for categoria in sorted(categorias.keys()):
        print(f"\n{cyan(f'📂 {categoria.upper()}')}")
        for key, fonte in categorias[categoria]:
            limite_info = f"(máx: {fonte['limite_max']})"
            print(f"  {green(key):>3}. {bold(fonte['nome']):<25} {gray('─')} {fonte['descricao']} {gray(limite_info)}")
    
    print(f"\n  {green('t'):>3}. {bold('Todas as fontes'):<25} {gray('─')} Coletar de todas as fontes")
    print(f"  {green('voltar'):>3}. {bold('Voltar'):<25} {gray('─')} Retornar ao menu anterior\n")

def exibir_resultado_completo(r: Dict, fonte: str, index: int, total: int):
    """Exibe resultado completo com TODOS os campos coletados"""
    rank = r.get("rank", index + 1)
    title = r.get("title") or r.get("titulo") or r.get("nome") or r.get("sugestao", "")
    link = r.get("link") or r.get("url", "")
    
    # Título principal
    title_display = title[:100] + "..." if len(title) > 100 else title
    print(f"  {cyan(f'[{fonte}]')} {green(f'#{rank:03d}')} {bold(title_display)}")
    
    # URL
    if link:
        print(f"      {gray('🔗 URL:')} {gray(link)}")
    
    # Exibir TODOS os campos disponíveis
    campos_importantes = {
        "snippet": "📄 Snippet",
        "description": "📄 Descrição",
        "resumo": "📄 Resumo",
        "descricao": "📄 Descrição",
        "sugestao": "💡 Sugestão",
        "relevancia": "⭐ Relevância",
        "score": "⭐ Score",
        "estrelas": "⭐ Estrelas",
        "views": "👁 Views",
        "likes": "👍 Likes",
        "dislikes": "👎 Dislikes",
        "comments": "💬 Comentários",
        "comentarios": "💬 Comentários",
        "citacoes": "📚 Citações",
        "referencias": "📖 Referências",
        "forks": "🍴 Forks",
        "watchers": "👀 Watchers",
        "autores": "👤 Autores",
        "author": "👤 Autor",
        "canal": "📺 Canal",
        "channel": "📺 Canal",
        "subreddit": "📱 Subreddit",
        "published": "📅 Publicado",
        "data": "📅 Data",
        "created": "📅 Criado",
        "categoria": "🏷️ Categoria",
        "topics": "🏷️ Tópicos",
        "linguagem": "💻 Linguagem",
        "language": "💻 Linguagem",
        "desenvolvedor": "👨‍💻 Desenvolvedor",
        "avaliacoes": "⭐ Avaliações",
        "reviews": "⭐ Avaliações",
        "instalacoes": "📥 Instalações",
        "preco": "💰 Preço",
        "duration": "⏱️ Duração",
        "upvote_ratio": "📊 Upvote Ratio",
        "engine": "🔍 Engine",
        "venue": "🏛️ Venue",
        "ano": "📆 Ano",
        "year": "📆 Ano"
    }
    
    # Exibir campos importantes
    metadados_linha = []
    for campo, label in campos_importantes.items():
        valor = r.get(campo)
        if valor and valor != "" and valor != 0:
            if isinstance(valor, (int, float)):
                metadados_linha.append(f"{label}: {valor}")
            elif isinstance(valor, str) and len(valor) < 50:
                metadados_linha.append(f"{label}: {valor[:50]}")
    
    if metadados_linha:
        # Dividir em linhas se muito longo
        linha_atual = []
        for item in metadados_linha:
            if len(" | ".join(linha_atual + [item])) > 100:
                if linha_atual:
                    print(f"      {gray(' | '.join(linha_atual))}")
                linha_atual = [item]
            else:
                linha_atual.append(item)
        if linha_atual:
            print(f"      {gray(' | '.join(linha_atual))}")
    
    # Exibir descrição/snippet completo se disponível
    descricao = r.get("snippet") or r.get("description") or r.get("resumo") or r.get("descricao", "")
    if descricao and len(descricao) > 100:
        print(f"      {gray('📄')} {gray(descricao[:300] + '...' if len(descricao) > 300 else descricao)}")
    
    print()

def exibir_resultados_tempo_real(resultados: List[Dict], fonte: str, termo: str):
    """Exibe resultados em tempo real com todos os dados"""
    if not resultados:
        return
    
    print_section(f"{fonte} - {len(resultados)} resultado(s) encontrado(s)")
    
    for idx, r in enumerate(resultados):
        exibir_resultado_completo(r, fonte, idx, len(resultados))
        time.sleep(0.03)  # Delay mínimo para visualização fluida

def coletar_fonte_com_exibicao(fonte_key: str, fonte: Dict, termo: str, region: str, 
                               lang: str, limite: int) -> List[Dict]:
    """Coleta dados de uma fonte e exibe em tempo real com logging e retry"""
    fonte_nome = fonte['nome']
    limite_max = fonte.get("limite_max", limite)
    limite_efetivo = min(limite, limite_max)
    
    print(f"\n{cyan('🔄 Coletando:')} {bold(fonte_nome)}... (limite: {limite_efetivo})")
    LOGGER.info(f"Iniciando coleta de {fonte_nome} para termo '{termo}' (limite: {limite_efetivo})")
    
    # Tentar coletar com retry
    max_tentativas = 2
    resultados_validos = []
    
    for tentativa in range(max_tentativas):
        try:
            resultados = fonte["funcao"](termo, region, lang, limite_efetivo)
            
            # Validar resultados antes de exibir
            resultados_validos = validar_dados(resultados, fonte_nome) if resultados else []
            
            if resultados_validos:
                print(f"{green('✓')} {fonte_nome}: {len(resultados_validos)} resultado(s) encontrado(s)\n")
                LOGGER.info(f"{fonte_nome}: {len(resultados_validos)} resultados coletados com sucesso")
                exibir_resultados_tempo_real(resultados_validos, fonte_nome, termo)
                return resultados_validos
            elif tentativa < max_tentativas - 1:
                LOGGER.warning(f"{fonte_nome}: Tentativa {tentativa + 1} não retornou resultados, tentando novamente...")
                time.sleep(1)
            else:
                print(f"{yellow('⚠')} {fonte_nome}: Nenhum resultado encontrado após {max_tentativas} tentativa(s)\n")
                LOGGER.warning(f"{fonte_nome}: Nenhum resultado válido encontrado após todas as tentativas")
                return []
        
        except Exception as e:
            error_msg = str(e)[:100]
            if tentativa < max_tentativas - 1:
                LOGGER.warning(f"{fonte_nome}: Tentativa {tentativa + 1} falhou: {error_msg}, tentando novamente...")
                time.sleep(2)
            else:
                print(f"{red('✗')} {fonte_nome}: Erro após {max_tentativas} tentativa(s) - {error_msg}\n")
                LOGGER.error(f"{fonte_nome}: Erro durante coleta após todas as tentativas: {str(e)}")
                LOGGER.debug(traceback.format_exc())
                return []
    
    return resultados_validos

def coletar_todas_fontes(termo: str, region: str, lang: str, limite: int, 
                         output_dir: Path) -> Dict[str, List[Dict]]:
    """Coleta dados de todas as fontes com exibição em tempo real"""
    todos_resultados = {}
    total_fontes = len(FONTES_DISPONIVEIS)
    
    print_header(f"COLETANDO DADOS PARA: '{termo}'", "=", 70)
    print(f"{cyan('Configurações:')} Região: {bold(region)} | Idioma: {bold(lang)} | Limite: {bold(str(limite))}\n")
    print(f"{gray('─' * 70)}\n")
    
    for idx, (key, fonte) in enumerate(FONTES_DISPONIVEIS.items(), 1):
        print_progress(idx, total_fontes, "Progresso geral", fonte['nome'])
        limite_fonte = min(limite, fonte.get("limite_max", limite))
        resultados = coletar_fonte_com_exibicao(key, fonte, termo, region, lang, limite_fonte)
        todos_resultados[fonte["nome"]] = resultados
        time.sleep(0.2)
    
    return todos_resultados

def exibir_todos_resultados_fluido(todos_resultados: Dict[str, List[Dict]], termo: str):
    """Exibe todos os resultados coletados de forma fluida com TODOS os dados"""
    print_header("VISUALIZAÇÃO COMPLETA - TODOS OS DADOS COLETADOS", "=", 70)
    print(f"{cyan('Termo pesquisado:')} {bold(termo)}\n")
    
    total_geral = sum(len(r) for r in todos_resultados.values())
    fontes_com_dados = len([f for f in todos_resultados.values() if f])
    print(f"{green('📊 Total geral:')} {bold(str(total_geral))} resultado(s) de {fontes_com_dados} fonte(s)\n")
    print(f"{gray('═' * 70)}\n")
    
    # Exibir por fonte
    for fonte_nome, resultados in sorted(todos_resultados.items()):
        if not resultados:
            continue
        
        print(f"\n{magenta('═' * 70)}")
        print(f"{magenta('FONTE:')} {bold(fonte_nome.upper())} - {len(resultados)} resultado(s)")
        print(f"{magenta('═' * 70)}\n")
        
        for idx, r in enumerate(resultados, 1):
            exibir_resultado_completo(r, fonte_nome, idx - 1, len(resultados))
        
        print(f"{gray('─' * 70)}\n")
    
    print(f"{green('✓')} Visualização completa finalizada!\n")

def criar_estrutura_diretorios(termo: str, timestamp: str) -> Dict[str, Path]:
    """Cria estrutura organizada de diretórios"""
    termo_safe = termo.replace(" ", "_").replace("/", "_")[:50]
    base_dir = BASE_DIR / termo_safe / timestamp
    
    estrutura = {
        "base": ensure_dir(base_dir),
        "por_fonte": ensure_dir(base_dir / "por_fonte"),
        "consolidado": ensure_dir(base_dir / "consolidado"),
        "metadados": ensure_dir(base_dir / "metadados")
    }
    
    return estrutura

def salvar_metadados(termo: str, region: str, lang: str, limite: int, 
                     fontes_selecionadas: List[str], estrutura: Dict[str, Path], modo: str):
    """Salva metadados da coleta"""
    metadados = {
        "termo": termo,
        "regiao": region,
        "idioma": lang,
        "limite": limite,
        "fontes_selecionadas": fontes_selecionadas,
        "modo": modo,
        "timestamp": datetime.now().isoformat(),
        "data_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "versao_script": "5.0"
    }
    
    salvar_json(metadados, "metadados_coleta.json", estrutura["metadados"])
    return metadados

def criar_csv_consolidado_otimizado(todos_resultados: Dict[str, List[Dict]], 
                                    metadados: Dict, estrutura: Dict[str, Path]) -> pd.DataFrame:
    """Cria CSV consolidado otimizado e reutilizável com TODOS os campos coletados"""
    resultados_consolidados = []
    
    LOGGER.info("Iniciando criação da base de dados consolidada...")
    
    for fonte_nome, resultados in todos_resultados.items():
        if not resultados:
            continue
        
        for r in resultados:
            # Criar registro padronizado com TODOS os campos
            registro = {
                # Metadados da coleta (sempre presentes)
                "termo_pesquisa": metadados.get("termo", ""),
                "regiao": metadados.get("regiao", ""),
                "idioma": metadados.get("idioma", ""),
                "data_coleta": metadados.get("data_coleta", ""),
                "timestamp": metadados.get("timestamp", ""),
                "modo": metadados.get("modo", "personalizado"),
                "versao_script": metadados.get("versao_script", "5.0"),
                
                # Metadados da fonte (sempre presentes)
                "fonte": fonte_nome,
                "rank": r.get("rank", 0),
            }
            
            # Adicionar TODOS os campos do resultado de forma padronizada
            for key, value in r.items():
                if key == "rank":  # Já adicionado acima
                    continue
                
                # Normalizar nome da coluna (sem espaços, lowercase)
                coluna_nome = key.lower().replace(" ", "_").replace("-", "_")
                
                # Tratar diferentes tipos de dados
                if value is None:
                    registro[coluna_nome] = ""
                elif isinstance(value, bool):
                    registro[coluna_nome] = value
                elif isinstance(value, (int, float)):
                    registro[coluna_nome] = value
                elif isinstance(value, str):
                    # Limitar strings muito longas para CSV
                    registro[coluna_nome] = value[:5000] if len(value) > 5000 else value
                elif isinstance(value, list):
                    if value:
                        # Se lista de strings, juntar com separador
                        if all(isinstance(item, str) for item in value):
                            registro[coluna_nome] = " | ".join(value[:50])  # Limitar a 50 itens
                        else:
                            registro[coluna_nome] = json.dumps(value[:50], ensure_ascii=False)
                    else:
                        registro[coluna_nome] = ""
                elif isinstance(value, dict):
                    registro[coluna_nome] = json.dumps(value, ensure_ascii=False)
                else:
                    registro[coluna_nome] = str(value)[:5000]
            
            resultados_consolidados.append(registro)
    
    if not resultados_consolidados:
        LOGGER.warning("Nenhum resultado para consolidar")
        return pd.DataFrame()
    
    # Criar DataFrame
    df = pd.DataFrame(resultados_consolidados)
    
    # Reordenar colunas: metadados primeiro, depois campos específicos
    colunas_ordenadas = [
        "termo_pesquisa", "regiao", "idioma", "data_coleta", "timestamp", 
        "modo", "versao_script", "fonte", "rank"
    ]
    outras_colunas = [c for c in df.columns if c not in colunas_ordenadas]
    df = df[colunas_ordenadas + sorted(outras_colunas)]
    
    # Ordenar por fonte e rank
    df = df.sort_values(["fonte", "rank"])
    
    # Remover colunas duplicadas (se houver)
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Salvar CSV consolidado otimizado
    timestamp_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S")
    termo_safe = metadados.get("termo", "coleta").replace(" ", "_").replace("/", "_")[:30]
    arquivo_consolidado = estrutura["consolidado"] / f"base_dados_completa_{termo_safe}_{timestamp_arquivo}.csv"
    
    df.to_csv(arquivo_consolidado, index=False, encoding="utf-8-sig", quoting=1)  # quoting=1 para CSV
    LOGGER.info(f"Base de dados consolidada salva: {len(df)} registros, {len(df.columns)} colunas")
    print(green(f"  ✓ Base de dados consolidada: {arquivo_consolidado.name}"))
    print(green(f"    → {len(df)} registros | {len(df.columns)} colunas | {arquivo_consolidado.stat().st_size / 1024:.1f} KB"))
    
    # Salvar também em Excel se possível
    try:
        arquivo_excel = estrutura["consolidado"] / f"base_dados_completa_{termo_safe}_{timestamp_arquivo}.xlsx"
        df.to_excel(arquivo_excel, index=False, engine='openpyxl')
        print(green(f"  ✓ Versão Excel: {arquivo_excel.name}"))
    except Exception as e:
        LOGGER.warning(f"Não foi possível salvar Excel: {str(e)}")
    
    # Salvar também um resumo estatístico
    try:
        resumo = {
            "total_registros": len(df),
            "total_colunas": len(df.columns),
            "fontes": df["fonte"].value_counts().to_dict(),
            "data_criacao": datetime.now().isoformat(),
            "termo": metadados.get("termo", ""),
            "regiao": metadados.get("regiao", ""),
            "modo": metadados.get("modo", "")
        }
        salvar_json(resumo, f"resumo_estatistico_{termo_safe}_{timestamp_arquivo}.json", estrutura["consolidado"], "Resumo")
        print(green(f"  ✓ Resumo estatístico salvo"))
    except:
        pass
    
    return df

def modo_completo():
    """Modo completo - coleta máximo de dados automaticamente"""
    print_header("MODO COMPLETO", "=", 70)
    print(f"{cyan('Este modo coleta o máximo de dados possível de todas as fontes automaticamente')}\n")
    
    # Termos
    termos = configurar_termos()
    if not termos:
        return False
    
    # Regiões
    regioes = configurar_regioes()
    if not regioes:
        regioes = ["br"]
    
    # Idioma
    print(f"\n{cyan('Idioma:')}")
    lang = input(f"{blue('> Idioma')} [pt]: ").strip().lower() or "pt"
    
    # Delay
    delay = input_int(f"{blue('> Delay entre requisições (segundos)')}", 0, 0, 10)
    
    # Confirmação
    print(f"\n{cyan('Resumo da coleta:')}")
    print(f"  • Termos: {', '.join(termos)}")
    print(f"  • Regiões: {', '.join([REGIONS_NAMES.get(r, r) for r in regioes])}")
    print(f"  • Idioma: {lang}")
    print(f"  • Delay: {delay}s")
    print(f"  • Modo: Completo (todas as fontes, máximo de dados)\n")
    
    confirmar = input(f"{blue('> Iniciar coleta? (S/N)')} [S]: ").strip().lower() or "s"
    if confirmar not in ["s", "sim", "y", "yes"]:
        print(yellow("  ⚠ Coleta cancelada pelo usuário\n"))
        return False
    
    print(f"\n{cyan('⚙️ Modo Completo:')} Coletando máximo de dados de todas as fontes...\n")
    
    # Criar estrutura para cada termo
    todos_resultados_consolidados = {}
    
    for termo in termos:
        for region in regioes:
            timestamp = now_tag()
            estrutura = criar_estrutura_diretorios(termo, timestamp)
            
            # Coletar de todas as fontes com limites máximos
            todos_resultados = {}
            total_fontes = len(FONTES_DISPONIVEIS)
            
            print_header(f"COLETANDO DADOS PARA: '{termo}' - {REGIONS_NAMES.get(region, region)} (MODO COMPLETO)", "=", 70)
            print(f"{cyan('Configurações:')} Região: {bold(REGIONS_NAMES.get(region, region))} | Idioma: {bold(lang)} | Modo: {bold('Completo (máximo)')}\n")
            print(f"{gray('─' * 70)}\n")
            
            for idx, (key, fonte) in enumerate(FONTES_DISPONIVEIS.items(), 1):
                print_progress(idx, total_fontes, "Progresso geral", fonte['nome'])
                limite_max = fonte.get("limite_max", 100)
                resultados = coletar_fonte_com_exibicao(key, fonte, termo, region, lang, limite_max)
                todos_resultados[fonte["nome"]] = resultados
                time.sleep(delay)
            
            # Consolidar resultados
            chave_consolidada = f"{termo}_{region}"
            todos_resultados_consolidados[chave_consolidada] = todos_resultados
            
            # Salvar metadados
            fontes_nomes = [FONTES_DISPONIVEIS[k]["nome"] for k in FONTES_DISPONIVEIS.keys()]
            metadados = salvar_metadados(termo, region, lang, 0, fontes_nomes, estrutura, "completo")
    
            # Exibir todos os resultados
            print()
            exibir_todos_resultados_fluido(todos_resultados, termo)
            
            # Salvar tudo
            print_header("SALVANDO DADOS ORGANIZADOS", "=", 70)
            
            for fonte_nome, resultados in todos_resultados.items():
                if resultados:
                    filename = f"{fonte_nome.lower().replace(' ', '_').replace('-', '_')}.csv"
                    df = salvar_csv(resultados, filename, estrutura["por_fonte"], fonte_nome)
                    if df is not None:
                        print(green(f"  ✓ Salvo: {filename} ({len(df)} registros, {len(df.columns)} colunas)"))
            
            if any(todos_resultados.values()):
                df_consolidado = criar_csv_consolidado_otimizado(todos_resultados, metadados, estrutura)
                salvar_json(todos_resultados, "resultados_completos.json", estrutura["consolidado"], "Consolidado")
                print(green(f"  ✓ Salvo: resultados_completos.json"))
                
                print_header("RESUMO FINAL DA COLETA", "=", 70)
                print(f"{green('✓')} Termo pesquisado: {bold(termo)}")
                print(f"{green('✓')} Região: {bold(REGIONS_NAMES.get(region, region))}")
                print(f"{green('✓')} Modo: {bold('Completo (máximo)')}")
                print(f"{green('✓')} Fontes consultadas: {len([f for f in todos_resultados.values() if f])}")
                print(f"{green('✓')} Total de resultados: {bold(str(len(df_consolidado)))}")
                print(f"{green('✓')} Total de colunas: {bold(str(len(df_consolidado.columns)))}")
                print(f"{green('✓')} Estrutura de diretórios:")
                print(f"    {gray('📁')} Base: {estrutura['base']}")
                print(f"    {gray('📁')} Por fonte: {estrutura['por_fonte']}")
                print(f"    {gray('📁')} Consolidado: {estrutura['consolidado']}")
                print(f"    {gray('📁')} Metadados: {estrutura['metadados']}\n")
                
                print(f"{cyan('Estatísticas detalhadas por fonte:')}")
                for fonte_nome, resultados in sorted(todos_resultados.items()):
                    count = len(resultados)
                    status = green("✓") if count > 0 else yellow("⚠")
                    print(f"  {status} {fonte_nome:<30} {count:>4} resultado(s)")
            else:
                print(yellow(f"\n  ⚠ Nenhum resultado coletado para '{termo}' na região '{region}'.\n"))
    
    print_header("COLETA COMPLETA FINALIZADA", "=", 70)
    total_coletas = len(todos_resultados_consolidados)
    print(green(f"✓ Total de coletas realizadas: {total_coletas}"))
    print(f"  • {len(termos)} termo(s) × {len(regioes)} região(ões) = {total_coletas} coleta(s)\n")
    
    return True

def modo_personalizado():
    """Modo personalizado - usuário configura tudo"""
    print_header("MODO PERSONALIZADO", "=", 70)
    print(f"{cyan('Configure todas as opções da sua pesquisa')}\n")
    
    # Termo
    termo = input(f"{blue('> Termo de busca')}: ").strip()
    if check_exit(termo) or not termo:
        return False
    
    # Região
    print(f"\n{cyan('Regiões disponíveis:')} {', '.join(REGIONS)}")
    region = input(f"{blue('> Região')} [br]: ").strip().lower() or "br"
    
    # Idioma
    print(f"\n{cyan('Idiomas disponíveis:')} {', '.join(LANGUAGES.keys())}")
    lang = input(f"{blue('> Idioma')} [pt]: ").strip().lower() or "pt"
    
    # Limite
    limite = input_int(f"{blue('> Limite de resultados por fonte')}", 10, 1, 1000)
    
    # Seleção de fontes
    print()
    exibir_menu_fontes()
    escolha = input(f"{blue('> Selecione as fontes')} (ex: 1,2,3 ou 't' para todas): ").strip().lower()
    
    if check_exit(escolha) or escolha == "voltar":
        return False
    
    # Processar seleção
    if escolha == "t":
        fontes_selecionadas = list(FONTES_DISPONIVEIS.keys())
        fontes_nomes = [FONTES_DISPONIVEIS[k]["nome"] for k in fontes_selecionadas]
    else:
        fontes_selecionadas = [f.strip() for f in escolha.split(",") 
                              if f.strip() in FONTES_DISPONIVEIS]
        fontes_nomes = [FONTES_DISPONIVEIS[k]["nome"] for k in fontes_selecionadas]
    
    if not fontes_selecionadas:
        print(red("  ✗ Nenhuma fonte válida selecionada.\n"))
        time.sleep(1)
        return False
    
    # Configurações adicionais para fontes específicas
    config_adicional = {}
    
    # Reddit - subreddit e sort
    if any(FONTES_DISPONIVEIS[k]["nome"] == "Reddit" for k in fontes_selecionadas):
        print(f"\n{cyan('Configurações Reddit:')}")
        subreddit = input(f"{blue('> Subreddit')} [all]: ").strip() or "all"
        sort_reddit = input_choice(f"{blue('> Ordenação')} (relevance/top/new)", ["relevance", "top", "new"], "relevance")
        config_adicional["reddit"] = {"subreddit": subreddit, "sort": sort_reddit}
    
    # YouTube - ordenação
    if any(FONTES_DISPONIVEIS[k]["nome"] == "YouTube" for k in fontes_selecionadas):
        print(f"\n{cyan('Configurações YouTube:')}")
        order_yt = input_choice(f"{blue('> Ordenação')} (relevance/date/rating/viewCount)", 
                               ["relevance", "date", "rating", "viewcount"], "relevance")
        config_adicional["youtube"] = {"order": order_yt}
    
    # Criar estrutura
    timestamp = now_tag()
    estrutura = criar_estrutura_diretorios(termo, timestamp)
    metadados = salvar_metadados(termo, region, lang, limite, fontes_nomes, estrutura, "personalizado")
    
    print()
    
    # Coletar dados
    todos_resultados = {}
    print_header(f"COLETANDO DADOS PARA: '{termo}' (MODO PERSONALIZADO)", "=", 70)
    print(f"{cyan('Configurações:')} Região: {bold(region)} | Idioma: {bold(lang)} | Limite: {bold(str(limite))}\n")
    print(f"{gray('─' * 70)}\n")
    
    for idx, key in enumerate(fontes_selecionadas, 1):
        fonte = FONTES_DISPONIVEIS[key]
        print_progress(idx, len(fontes_selecionadas), "Progresso geral", fonte['nome'])
        
        # Aplicar configurações específicas
        limite_fonte = min(limite, fonte.get("limite_max", limite))
        
        if fonte["nome"] == "Reddit" and "reddit" in config_adicional:
            config = config_adicional["reddit"]
            resultados = coletar_reddit(termo, config["subreddit"], config["sort"], limite_fonte, 5)
        elif fonte["nome"] == "YouTube" and "youtube" in config_adicional:
            config = config_adicional["youtube"]
            resultados = coletar_youtube(termo, region, lang, config["order"], limite_fonte)
        else:
            resultados = coletar_fonte_com_exibicao(key, fonte, termo, region, lang, limite_fonte)
        
        todos_resultados[fonte["nome"]] = resultados
        time.sleep(0.2)
    
    # Exibir todos os resultados
    print()
    exibir_todos_resultados_fluido(todos_resultados, termo)
    
    # Salvar tudo
    print_header("SALVANDO DADOS ORGANIZADOS", "=", 70)
    
    for fonte_nome, resultados in todos_resultados.items():
        if resultados:
            filename = f"{fonte_nome.lower().replace(' ', '_').replace('-', '_')}.csv"
            df = salvar_csv(resultados, filename, estrutura["por_fonte"])
            if df is not None:
                print(green(f"  ✓ Salvo: {filename} ({len(df)} registros, {len(df.columns)} colunas)"))
    
    if any(todos_resultados.values()):
        df_consolidado = criar_csv_consolidado_otimizado(todos_resultados, metadados, estrutura)
        salvar_json(todos_resultados, "resultados_completos.json", estrutura["consolidado"])
        print(green(f"  ✓ Salvo: resultados_completos.json"))
        
        print_header("RESUMO FINAL DA COLETA", "=", 70)
        print(f"{green('✓')} Termo pesquisado: {bold(termo)}")
        print(f"{green('✓')} Modo: {bold('Personalizado')}")
        print(f"{green('✓')} Fontes consultadas: {len([f for f in todos_resultados.values() if f])}")
        print(f"{green('✓')} Total de resultados: {bold(str(len(df_consolidado)))}")
        print(f"{green('✓')} Total de colunas: {bold(str(len(df_consolidado.columns)))}")
        print(f"{green('✓')} Estrutura de diretórios:")
        print(f"    {gray('📁')} Base: {estrutura['base']}")
        print(f"    {gray('📁')} Por fonte: {estrutura['por_fonte']}")
        print(f"    {gray('📁')} Consolidado: {estrutura['consolidado']}")
        print(f"    {gray('📁')} Metadados: {estrutura['metadados']}\n")
        
        print(f"{cyan('Estatísticas detalhadas por fonte:')}")
        for fonte_nome, resultados in sorted(todos_resultados.items()):
            count = len(resultados)
            status = green("✓") if count > 0 else yellow("⚠")
            print(f"  {status} {fonte_nome:<30} {count:>4} resultado(s)")
    else:
        print(yellow("\n  ⚠ Nenhum resultado coletado.\n"))
    
    return True

def nova_coleta():
    """Função para nova coleta - seleciona modo"""
    print_header("NOVA COLETA DE DADOS", "=", 70)
    
    exibir_menu_modo()
    modo = input(f"{blue('> Selecione o modo')}: ").strip().lower()
    
    if check_exit(modo) or modo == "voltar":
        return False
    
    if modo == "1":
        return modo_completo()
    elif modo == "2":
        return modo_personalizado()
    else:
        print(red("  ✗ Modo inválido.\n"))
        time.sleep(1)
        return False

def main():
    """Função principal - Loop interativo com menu padronizado"""
    clear_screen()
    print_header("UNI - COLETOR UNIVERSAL DE DADOS v5.0", "=", 70)
    print(f"{cyan('Sistema completo de coleta de dados de múltiplas fontes')}\n")
    print(f"{gray('Versão 5.0 - Coleta máxima garantida | Base de dados otimizada | Retry inteligente')}\n")
    msg_sair = "Digite 'sair' a qualquer momento para encerrar"
    print(f"{gray(msg_sair)}\n")
    
    while True:
        exibir_menu_principal()
        opcao = input(f"{blue('> Escolha uma opção')}: ").strip().lower()
        
        if check_exit(opcao):
            print(yellow("\nEncerrando... Obrigado por usar UNI v5.0!\n"))
            LOGGER.info("Aplicação encerrada pelo usuário")
            break
        
        if opcao == "1":
            if nova_coleta():
                input(f"\n{blue('Pressione Enter para continuar...')}")
                clear_screen()
        elif opcao == "2":
            exibir_menu_fontes()
            input(f"\n{blue('Pressione Enter para continuar...')}")
            clear_screen()
        elif opcao == "3":
            print_header("CONFIGURAÇÕES", "=", 70)
            print(f"{cyan('Limites máximos por fonte (Modo Automático):')}\n")
            for fonte_nome, limite in sorted(LIMITES_MAXIMOS.items()):
                print(f"  {fonte_nome:<30} {limite:>4}")
            print()
            input(f"{blue('Pressione Enter para continuar...')}")
            clear_screen()
        elif opcao == "4":
            print_header("SOBRE", "=", 70)
            print(f"{cyan('UNI - Coletor Universal de Dados v5.0')}\n")
            print(f"Desenvolvido por: Emerson Almeida")
            print(f"Versão: 5.0")
            print(f"Data: 2024\n")
            print(f"{cyan('Fontes disponíveis:')} 15 fontes de dados")
            print(f"{cyan('Melhorias v5.0:')}")
            print(f"  • Coleta máxima garantida de todas as fontes")
            print(f"  • Retry inteligente com múltiplas tentativas")
            print(f"  • Fallback automático para fontes que falham")
            print(f"  • Base de dados consolidada otimizada e reutilizável")
            print(f"  • Organização completa dos dados em CSV estruturado")
            print(f"  • Validação e limpeza completa dos dados")
            print(f"  • Estatísticas detalhadas de coleta")
            print(f"  • Melhorias nas fontes problemáticas\n")
            print(f"  • Tratamento robusto de exceções")
            print(f"  • Garantia de coleta completa")
            print(f"  • Sistema de fallback para fontes")
            print(f"  • Melhor salvamento e persistência")
            print(f"  • Estatísticas detalhadas de coleta\n")
            input(f"{blue('Pressione Enter para continuar...')}")
            clear_screen()
        else:
            print(red("  ✗ Opção inválida. Tente novamente.\n"))
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(yellow("\n\nInterrompido pelo usuário. Até logo!\n"))
        sys.exit(0)
    except Exception as e:
        print(red(f"\n\nErro fatal: {e}\n"))
        import traceback
        traceback.print_exc()
        sys.exit(1)
