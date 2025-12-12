#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNI - Coletor Universal de Dados v1.0
=====================================
Sistema completo de coleta de dados de múltiplas fontes com interface CLI otimizada.

Autor: Emerson Almeida
Versão: 1.0
Data: 2024

Fontes disponíveis:
- Google Suggest, Trends
- SERP (DuckDuckGo, Google, Brave, Bing)
- YouTube
- Reddit
- Google News
- GDELT
- Hacker News
- Stack Exchange
- GitHub
- arXiv
- Wikipedia
- Google Scholar
- App Stores (Google Play, Apple)
"""

import os
import re
import sys
import json
import time
import string
import locale
import warnings
import requests
import pandas as pd
import feedparser
from datetime import datetime
from pathlib import Path
from itertools import product
from functools import lru_cache
from typing import List, Dict, Optional, Any
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

def print_progress(current: int, total: int, prefix: str = "Progresso"):
    """Exibe barra de progresso"""
    percent = (current / total) * 100 if total > 0 else 0
    bar_length = 40
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r{prefix}: [{bar}] {percent:.1f}% ({current}/{total})", end="", flush=True)
    if current == total:
        print()

# ======================================
# ⚙️ CONFIGURAÇÕES E CHAVES DE API
# ======================================

# Diretórios
BASE_DIR = Path("dados")
BASE_DIR.mkdir(exist_ok=True)

# Chaves de API (do notebook)
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

# Configurações padrão
REGIONS = ["br", "us", "fr", "de", "jp", "uk", "es"]
LANGUAGES = {"pt": "pt-BR", "en": "en-US", "es": "es-ES", "fr": "fr-FR", "de": "de-DE"}
SOURCES = {"web": "", "youtube": "yt", "news": "n", "shopping": "sh"}
CLIENTS = ["chrome", "firefox"]

# Comandos de saída
EXIT_COMMANDS = {"sair", "fechar", "terminar", "ok", "exit", "quit", "q", "s"}

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
    """Cria sessão HTTP com retry"""
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    retry = Retry(
        total=5,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    sess.mount("https://", HTTPAdapter(max_retries=retry))
    return sess

SESSION = make_session()

def salvar_csv(data: List[Dict], filename: str, output_dir: Path) -> Optional[pd.DataFrame]:
    """Salva dados em CSV com metadados completos"""
    if not data:
        print(yellow(f"  ⚠ Nenhum dado para salvar em {filename}."))
        return None
    
    df = pd.DataFrame(data)
    filepath = output_dir / filename
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(green(f"  ✓ Salvo: {filepath} ({len(df)} registros)"))
    return df

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
                     fontes_selecionadas: List[str], estrutura: Dict[str, Path]):
    """Salva metadados da coleta"""
    metadados = {
        "termo": termo,
        "regiao": region,
        "idioma": lang,
        "limite": limite,
        "fontes_selecionadas": fontes_selecionadas,
        "timestamp": datetime.now().isoformat(),
        "data_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "versao_script": "1.0"
    }
    
    salvar_json(metadados, "metadados_coleta.json", estrutura["metadados"])
    return metadados

def criar_csv_consolidado_otimizado(todos_resultados: Dict[str, List[Dict]], 
                                    metadados: Dict, estrutura: Dict[str, Path]) -> pd.DataFrame:
    """Cria CSV consolidado otimizado com todas as colunas padronizadas"""
    resultados_consolidados = []
    
    for fonte_nome, resultados in todos_resultados.items():
        for r in resultados:
            # Padronizar estrutura
            registro = {
                # Metadados da coleta
                "termo_pesquisa": metadados["termo"],
                "regiao": metadados["regiao"],
                "idioma": metadados["idioma"],
                "data_coleta": metadados["data_coleta"],
                "timestamp": metadados["timestamp"],
                
                # Metadados da fonte
                "fonte": fonte_nome,
                "rank": r.get("rank", 0),
                
                # Conteúdo principal (padronizado)
                "titulo": r.get("title") or r.get("titulo") or r.get("nome") or r.get("sugestao", ""),
                "url": r.get("link") or r.get("url", ""),
                "descricao": r.get("snippet") or r.get("description") or r.get("resumo") or r.get("descricao") or r.get("descricao", ""),
                
                # Metadados específicos (quando disponíveis)
                "score": r.get("score", ""),
                "estrelas": r.get("estrelas", ""),
                "views": r.get("views", ""),
                "comentarios": r.get("comments") or r.get("comentarios", ""),
                "autor": r.get("author") or r.get("autores", ""),
                "canal": r.get("channel", ""),
                "subreddit": r.get("subreddit", ""),
                "publicado": r.get("published") or r.get("data") or r.get("created", ""),
                "forks": r.get("forks", ""),
                "linguagem": r.get("linguagem") or r.get("language", ""),
                "ano": r.get("ano") or r.get("year", ""),
                "desenvolvedor": r.get("desenvolvedor", ""),
                "avaliacoes": r.get("avaliacoes") or r.get("reviews", ""),
                "engine": r.get("engine", ""),
                "relevancia": r.get("relevancia", ""),
                
                # Campos adicionais (JSON string para flexibilidade)
                "dados_extras": json.dumps({k: v for k, v in r.items() 
                                           if k not in ["rank", "title", "titulo", "nome", "sugestao", 
                                                        "link", "url", "snippet", "description", "resumo", 
                                                        "descricao", "score", "estrelas", "views", "comments", 
                                                        "comentarios", "author", "autores", "channel", 
                                                        "subreddit", "published", "data", "created", "forks", 
                                                        "linguagem", "language", "ano", "year", "desenvolvedor", 
                                                        "avaliacoes", "reviews", "engine", "relevancia"]}, 
                                          ensure_ascii=False)
            }
            resultados_consolidados.append(registro)
    
    df = pd.DataFrame(resultados_consolidados)
    
    # Ordenar por fonte e rank
    df = df.sort_values(["fonte", "rank"])
    
    # Salvar CSV consolidado
    arquivo_consolidado = estrutura["consolidado"] / "base_dados_completa.csv"
    df.to_csv(arquivo_consolidado, index=False, encoding="utf-8-sig")
    print(green(f"  ✓ Base de dados consolidada: {arquivo_consolidado} ({len(df)} registros)"))
    
    # Salvar também em Excel se possível
    try:
        arquivo_excel = estrutura["consolidado"] / "base_dados_completa.xlsx"
        df.to_excel(arquivo_excel, index=False, engine='openpyxl')
        print(green(f"  ✓ Versão Excel: {arquivo_excel}"))
    except:
        pass
    
    return df

def salvar_json(data: Any, filename: str, output_dir: Path):
    """Salva dados em JSON"""
    filepath = output_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(green(f"  ✓ Salvo: {filepath}"))

def check_exit(value: str) -> bool:
    """Verifica se é comando de saída"""
    return value.lower().strip() in EXIT_COMMANDS

def parse_list(value: str, default: str) -> List[str]:
    """Parse lista separada por vírgula"""
    if not value:
        return [default]
    return [x.strip() for x in value.split(",") if x.strip()]

# ======================================
# 📡 FUNÇÕES DE COLETA DE DADOS
# ======================================

# --- Google Suggest ---
@lru_cache(maxsize=256)
def coletar_suggest(query: str, region: str = "br", client: str = "chrome", 
                   source: str = "", lang: str = "", limit: int = 10) -> List[Dict]:
    """Coleta sugestões do Google Suggest"""
    params = {"q": query, "gl": region, "client": client}
    if lang:
        params["hl"] = lang
    if source:
        params["ds"] = source
    
    try:
        r = SESSION.get(SUGGEST_URL, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        suggestions = data[1] if len(data) > 1 else []
        relevance = data[4].get("google:suggestrelevance", [0] * len(suggestions)) if len(data) > 4 and isinstance(data[4], dict) else [0] * len(suggestions)
        return [{"sugestao": s, "relevancia": r} for s, r in zip(suggestions[:limit], relevance[:limit])]
    except Exception as e:
        print(red(f"  ✗ Erro Google Suggest: {e}"))
        return []

# --- SERP (Search Engine Results Pages) ---
def coletar_duckduckgo(term: str, region: str = "br", limite: int = 10) -> List[Dict]:
    """Coleta resultados do DuckDuckGo"""
    if not DDGS_AVAILABLE:
        print(yellow("  ⚠ DuckDuckGo não disponível (instale: pip install duckduckgo-search)"))
        return []
    
    resultados = []
    try:
        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.text(term, region=region, safesearch="off", max_results=limite), 1):
                if "title" in r and "href" in r:
                    resultados.append({
                        "engine": "duckduckgo",
                        "rank": i,
                        "title": r["title"],
                        "link": r["href"],
                        "snippet": r.get("body", "")
                    })
    except Exception as e:
        print(red(f"  ✗ Erro DuckDuckGo: {e}"))
    return resultados

def coletar_google(term: str, region: str = "br", lang: str = "pt", limite: int = 10) -> List[Dict]:
    """Coleta resultados do Google Custom Search"""
    if not GOOGLE_API_AVAILABLE or not GOOGLE_API_KEY or not GOOGLE_CX:
        print(yellow("  ⚠ Google desativado (faltam API_KEY e CX)"))
        return []
    
    resultados = []
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        start, rank = 1, 1
        while start <= limite:
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
                    "snippet": item.get("snippet", "")
                })
                rank += 1
            start += 10
    except HttpError as e:
        print(red(f"  ✗ Erro Google API: {e}"))
    except Exception as e:
        print(red(f"  ✗ Erro Google: {e}"))
    return resultados

def coletar_brave(term: str, region: str = "br", limite: int = 10) -> List[Dict]:
    """Coleta resultados do Brave Search"""
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
                resultados.append({
                    "engine": "brave",
                    "rank": i,
                    "title": item.get("title", ""),
                    "link": item.get("url", ""),
                    "snippet": item.get("description", "")
                })
    except Exception as e:
        print(red(f"  ✗ Erro Brave: {e}"))
    return resultados

def coletar_bing(term: str, region: str = "br", limite: int = 10) -> List[Dict]:
    """Coleta resultados do Bing via SerpAPI"""
    resultados = []
    url = "https://serpapi.com/search"
    params = {
        "engine": "bing",
        "q": term,
        "cc": region,
        "count": limite,
        "api_key": SERPAPI_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        if "organic_results" in data:
            for i, item in enumerate(data["organic_results"], 1):
                resultados.append({
                    "engine": "bing",
                    "rank": i,
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
    except Exception as e:
        print(red(f"  ✗ Erro Bing: {e}"))
    return resultados

# --- YouTube ---
def coletar_youtube(query: str, region: str = "br", lang: str = "pt", 
                   order: str = "relevance", max_results: int = 10) -> List[Dict]:
    """Coleta vídeos do YouTube"""
    resultados = []
    
    if YOUTUBE_API_KEY and GOOGLE_API_AVAILABLE:
        try:
            youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
            request = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results,
                order=order,
                regionCode=region.upper(),
                relevanceLanguage=lang
            )
            response = request.execute()
            
            for i, item in enumerate(response.get("items", []), 1):
                snippet = item["snippet"]
                resultados.append({
                    "rank": i,
                    "title": snippet.get("title", ""),
                    "link": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    "channel": snippet.get("channelTitle", ""),
                    "published": snippet.get("publishedAt", ""),
                    "description": snippet.get("description", "")
                })
        except Exception as e:
            print(red(f"  ✗ Erro YouTube API: {e}"))
    
    return resultados

# --- Reddit ---
def coletar_reddit(termo: str, subreddit: str = "all", sort: str = "relevance", 
                  limit_posts: int = 10, limit_comments: int = 5) -> List[Dict]:
    """Coleta posts do Reddit"""
    if not PRAW_AVAILABLE:
        print(yellow("  ⚠ Reddit não disponível (instale: pip install praw)"))
        return []
    
    resultados = []
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent="uni-collector-v1"
        )
        
        sub = reddit.subreddit(subreddit if subreddit.lower() != "all" else "all")
        
        if sort == "new":
            posts = sub.search(termo, sort="new", limit=limit_posts)
        elif sort == "top":
            posts = sub.search(termo, sort="top", limit=limit_posts)
        else:
            posts = sub.search(termo, sort="hot", limit=limit_posts)
        
        for idx, post in enumerate(posts, 1):
            resultados.append({
                "rank": idx,
                "title": post.title,
                "link": f"https://reddit.com{post.permalink}",
                "subreddit": post.subreddit.display_name,
                "score": post.score,
                "comments": post.num_comments,
                "created": datetime.fromtimestamp(post.created_utc).isoformat()
            })
    except Exception as e:
        print(red(f"  ✗ Erro Reddit: {e}"))
    return resultados

# --- Google News ---
def coletar_gnews(termo: str, lang: str = "pt", country: str = "br", 
                 from_date: Optional[str] = None, to_date: Optional[str] = None,
                 max_results: int = 10) -> List[Dict]:
    """Coleta notícias do Google News"""
    resultados = []
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": termo,
        "lang": lang,
        "country": country,
        "max": max_results,
        "apikey": GNEWS_API_KEY
    }
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        for i, article in enumerate(data.get("articles", []), 1):
            resultados.append({
                "rank": i,
                "title": article.get("title", ""),
                "link": article.get("url", ""),
                "source": article.get("source", {}).get("name", ""),
                "published": article.get("publishedAt", ""),
                "description": article.get("description", "")
            })
    except Exception as e:
        print(red(f"  ✗ Erro Google News: {e}"))
    return resultados

# --- Hacker News ---
def coletar_hackernews(termo: str, limite: int = 10) -> List[Dict]:
    """Coleta resultados do Hacker News"""
    resultados = []
    try:
        # Busca na API do Algolia
        url = "https://hn.algolia.com/api/v1/search"
        params = {
            "query": termo,
            "tags": "story",
            "hitsPerPage": limite
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        for i, hit in enumerate(data.get("hits", []), 1):
            resultados.append({
                "rank": i,
                "title": hit.get("title", ""),
                "link": hit.get("url", "") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                "score": hit.get("points", 0),
                "comments": hit.get("num_comments", 0),
                "author": hit.get("author", ""),
                "created": hit.get("created_at", "")
            })
    except Exception as e:
        print(red(f"  ✗ Erro Hacker News: {e}"))
    return resultados

# --- GitHub ---
def coletar_github(query: str, limite: int = 10) -> List[Dict]:
    """Coleta repositórios do GitHub"""
    resultados = []
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limite
    }
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        for i, repo in enumerate(data.get("items", []), 1):
            resultados.append({
                "rank": i,
                "nome": repo.get("full_name", ""),
                "url": repo.get("html_url", ""),
                "descricao": repo.get("description", ""),
                "estrelas": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "linguagem": repo.get("language", ""),
                "criado": repo.get("created_at", "")
            })
    except Exception as e:
        print(red(f"  ✗ Erro GitHub: {e}"))
    return resultados

# --- arXiv ---
def coletar_arxiv(termo: str, limite: int = 10, ordenacao: str = "relevance") -> List[Dict]:
    """Coleta artigos do arXiv"""
    resultados = []
    query = f"search_query=all:{termo}&start=0&max_results={limite}&sortBy={ordenacao}"
    try:
        resp = requests.get(f"{ARXIV_URL}?{query}", timeout=20)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        
        for i, entry in enumerate(feed.entries, 1):
            autores = ", ".join([a.name for a in entry.authors]) if "authors" in entry else "N/A"
            resultados.append({
                "rank": i,
                "titulo": entry.title.strip().replace("\n", " "),
                "autores": autores,
                "data": entry.published[:10] if "published" in entry else "N/A",
                "link": entry.link,
                "resumo": entry.summary[:200] if "summary" in entry else ""
            })
    except Exception as e:
        print(red(f"  ✗ Erro arXiv: {e}"))
    return resultados

# --- Wikipedia ---
def coletar_wikipedia(termo: str, lang: str = "pt") -> List[Dict]:
    """Coleta informações da Wikipedia"""
    resultados = []
    try:
        # Busca páginas
        search_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/search"
        params = {"q": termo, "limit": 5}
        resp = requests.get(search_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        for i, page in enumerate(data.get("pages", []), 1):
            title = page.get("title", "")
            api_url = WIKIPEDIA_API.format(lang=lang, title=title.replace(" ", "_"))
            try:
                page_resp = requests.get(api_url, timeout=10)
                page_data = page_resp.json()
                resultados.append({
                    "rank": i,
                    "titulo": page_data.get("title", title),
                    "url": page_data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "resumo": page_data.get("extract", "")[:500],
                    "idioma": lang
                })
            except:
                pass
    except Exception as e:
        print(red(f"  ✗ Erro Wikipedia: {e}"))
    return resultados

# --- Google Scholar (via Semantic Scholar) ---
def coletar_scholar(termo: str, limite: int = 10) -> List[Dict]:
    """Coleta artigos acadêmicos via Semantic Scholar"""
    resultados = []
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": termo,
        "limit": limite,
        "fields": "title,authors,year,url,abstract"
    }
    
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        for i, paper in enumerate(data.get("data", []), 1):
            autores = ", ".join([a.get("name", "") for a in paper.get("authors", [])])
            resultados.append({
                "rank": i,
                "titulo": paper.get("title", ""),
                "autores": autores,
                "ano": paper.get("year", ""),
                "link": paper.get("url", ""),
                "resumo": paper.get("abstract", "")[:300] if paper.get("abstract") else ""
            })
    except Exception as e:
        print(red(f"  ✗ Erro Scholar: {e}"))
    return resultados

# --- App Stores ---
def coletar_google_play(term: str, lang: str = "pt", country: str = "br", n: int = 10) -> List[Dict]:
    """Coleta apps do Google Play"""
    resultados = []
    try:
        from google_play_scraper import search
        apps = search(term, lang=lang, country=country, n_results=n)
        for i, app in enumerate(apps, 1):
            resultados.append({
                "rank": i,
                "nome": app.get("title", ""),
                "link": f"https://play.google.com/store/apps/details?id={app.get('appId', '')}",
                "estrelas": app.get("score", 0),
                "avaliacoes": app.get("reviews", 0),
                "desenvolvedor": app.get("developer", "")
            })
    except ImportError:
        print(yellow("  ⚠ Google Play Scraper não disponível (instale: pip install google-play-scraper)"))
    except Exception as e:
        print(red(f"  ✗ Erro Google Play: {e}"))
    return resultados

def coletar_apple_store(term: str, country: str = "br", limit: int = 10) -> List[Dict]:
    """Coleta apps da Apple App Store"""
    resultados = []
    try:
        from app_store_scraper import AppStore
        store = AppStore(country=country, app_name=term)
        store.search()
        
        for i, app in enumerate(store.apps[:limit], 1):
            resultados.append({
                "rank": i,
                "nome": app.get("name", ""),
                "link": app.get("url", ""),
                "estrelas": app.get("rating", 0),
                "avaliacoes": app.get("user_rating_count", 0),
                "desenvolvedor": app.get("developer", "")
            })
    except ImportError:
        print(yellow("  ⚠ App Store Scraper não disponível (instale: pip install app-store-scraper)"))
    except Exception as e:
        print(red(f"  ✗ Erro Apple Store: {e}"))
    return resultados

# ======================================
# 🎯 MENU PRINCIPAL E INTERFACE
# ======================================

FONTES_DISPONIVEIS = {
    "1": {
        "nome": "Google Suggest",
        "funcao": lambda t, r, l, lim: coletar_suggest(t, r, "chrome", "", l, lim),
        "descricao": "Sugestões de busca do Google"
    },
    "2": {
        "nome": "SERP - DuckDuckGo",
        "funcao": lambda t, r, l, lim: coletar_duckduckgo(t, r, lim),
        "descricao": "Resultados de busca DuckDuckGo"
    },
    "3": {
        "nome": "SERP - Google",
        "funcao": lambda t, r, l, lim: coletar_google(t, r, l, lim),
        "descricao": "Resultados de busca Google"
    },
    "4": {
        "nome": "SERP - Brave",
        "funcao": lambda t, r, l, lim: coletar_brave(t, r, lim),
        "descricao": "Resultados de busca Brave"
    },
    "5": {
        "nome": "SERP - Bing",
        "funcao": lambda t, r, l, lim: coletar_bing(t, r, lim),
        "descricao": "Resultados de busca Bing"
    },
    "6": {
        "nome": "YouTube",
        "funcao": lambda t, r, l, lim: coletar_youtube(t, r, l, "relevance", lim),
        "descricao": "Vídeos do YouTube"
    },
    "7": {
        "nome": "Reddit",
        "funcao": lambda t, r, l, lim: coletar_reddit(t, "all", "relevance", lim, 5),
        "descricao": "Posts do Reddit"
    },
    "8": {
        "nome": "Google News",
        "funcao": lambda t, r, l, lim: coletar_gnews(t, l, r, None, None, lim),
        "descricao": "Notícias do Google News"
    },
    "9": {
        "nome": "Hacker News",
        "funcao": lambda t, r, l, lim: coletar_hackernews(t, lim),
        "descricao": "Posts do Hacker News"
    },
    "10": {
        "nome": "GitHub",
        "funcao": lambda t, r, l, lim: coletar_github(t, lim),
        "descricao": "Repositórios do GitHub"
    },
    "11": {
        "nome": "arXiv",
        "funcao": lambda t, r, l, lim: coletar_arxiv(t, lim, "relevance"),
        "descricao": "Artigos científicos do arXiv"
    },
    "12": {
        "nome": "Wikipedia",
        "funcao": lambda t, r, l, lim: coletar_wikipedia(t, l),
        "descricao": "Páginas da Wikipedia"
    },
    "13": {
        "nome": "Google Scholar",
        "funcao": lambda t, r, l, lim: coletar_scholar(t, lim),
        "descricao": "Artigos acadêmicos"
    },
    "14": {
        "nome": "Google Play",
        "funcao": lambda t, r, l, lim: coletar_google_play(t, l, r, lim),
        "descricao": "Apps do Google Play"
    },
    "15": {
        "nome": "Apple App Store",
        "funcao": lambda t, r, l, lim: coletar_apple_store(t, r, lim),
        "descricao": "Apps da Apple App Store"
    }
}

def exibir_menu_fontes():
    """Exibe menu de fontes disponíveis"""
    print_header("FONTES DISPONÍVEIS", "=", 70)
    for key, fonte in FONTES_DISPONIVEIS.items():
        print(f"  {green(key):>3}. {bold(fonte['nome']):<25} {gray('─')} {fonte['descricao']}")
    print(f"\n  {green('t'):>3}. {bold('Todas as fontes'):<25} {gray('─')} Coletar de todas as fontes")
    print(f"  {green('sair'):>3}. {bold('Sair'):<25} {gray('─')} Encerrar o programa\n")

def exibir_resultado_item(r: Dict, fonte: str, index: int, total: int):
    """Exibe um único resultado de forma fluida"""
    rank = r.get("rank", index + 1)
    title = r.get("title") or r.get("titulo") or r.get("nome") or r.get("sugestao", "")
    link = r.get("link") or r.get("url", "")
    snippet = r.get("snippet") or r.get("description") or r.get("resumo") or r.get("descricao", "")
    
    # Formatação do título
    title_display = title[:80] + "..." if len(title) > 80 else title
    
    print(f"  {cyan(f'[{fonte}]')} {green(f'#{rank:03d}')} {bold(title_display)}")
    if link:
        print(f"      {gray('🔗')} {gray(link)}")
    if snippet:
        snippet_display = snippet[:150] + "..." if len(snippet) > 150 else snippet
        print(f"      {gray('📄')} {gray(snippet_display)}")
    
    # Metadados adicionais
    metadados = []
    if "score" in r:
        metadados.append(f"⭐ {r['score']}")
    if "estrelas" in r:
        metadados.append(f"⭐ {r['estrelas']}")
    if "views" in r:
        metadados.append(f"👁 {r['views']}")
    if "comments" in r or "comentarios" in r:
        count = r.get("comments") or r.get("comentarios", 0)
        metadados.append(f"💬 {count}")
    if "published" in r or "data" in r or "created" in r:
        data = r.get("published") or r.get("data") or r.get("created", "")
        if data:
            metadados.append(f"📅 {data[:10]}")
    
    if metadados:
        print(f"      {gray(' | '.join(metadados))}")
    print()

def exibir_resultados_tempo_real(resultados: List[Dict], fonte: str, termo: str):
    """Exibe resultados em tempo real durante a coleta"""
    if not resultados:
        print(yellow(f"  ⚠ {fonte}: Nenhum resultado encontrado para '{termo}'\n"))
        return
    
    print_section(f"{fonte} - {len(resultados)} resultado(s) encontrado(s)")
    
    for idx, r in enumerate(resultados):
        exibir_resultado_item(r, fonte, idx, len(resultados))
        time.sleep(0.1)  # Pequeno delay para visualização fluida

def coletar_fonte_com_exibicao(fonte_key: str, fonte: Dict, termo: str, region: str, 
                               lang: str, limite: int) -> List[Dict]:
    """Coleta dados de uma fonte e exibe em tempo real"""
    print(f"\n{cyan('🔄 Coletando:')} {bold(fonte['nome'])}...")
    
    try:
        resultados = fonte["funcao"](termo, region, lang, limite)
        
        if resultados:
            print(f"{green('✓')} {fonte['nome']}: {len(resultados)} resultado(s) encontrado(s)\n")
            # Exibir resultados em tempo real
            exibir_resultados_tempo_real(resultados, fonte['nome'], termo)
        else:
            print(f"{yellow('⚠')} {fonte['nome']}: Nenhum resultado encontrado\n")
        
        return resultados
    except Exception as e:
        print(f"{red('✗')} {fonte['nome']}: Erro - {e}\n")
        return []

def coletar_todas_fontes(termo: str, region: str, lang: str, limite: int, 
                         output_dir: Path) -> Dict[str, List[Dict]]:
    """Coleta dados de todas as fontes com exibição em tempo real"""
    todos_resultados = {}
    total_fontes = len(FONTES_DISPONIVEIS)
    
    print_header(f"COLETANDO DADOS PARA: '{termo}'", "=", 70)
    print(f"{cyan('Configurações:')} Região: {bold(region)} | Idioma: {bold(lang)} | Limite: {bold(str(limite))}\n")
    print(f"{gray('─' * 70)}\n")
    
    for idx, (key, fonte) in enumerate(FONTES_DISPONIVEIS.items(), 1):
        print_progress(idx, total_fontes, f"Progresso geral")
        resultados = coletar_fonte_com_exibicao(key, fonte, termo, region, lang, limite)
        todos_resultados[fonte["nome"]] = resultados
        time.sleep(0.3)  # Delay para evitar rate limiting
    
    return todos_resultados

def exibir_todos_resultados_fluido(todos_resultados: Dict[str, List[Dict]], termo: str):
    """Exibe todos os resultados coletados de forma fluida e organizada"""
    print_header("VISUALIZAÇÃO COMPLETA - TODOS OS DADOS COLETADOS", "=", 70)
    print(f"{cyan('Termo pesquisado:')} {bold(termo)}\n")
    
    total_geral = sum(len(r) for r in todos_resultados.values())
    print(f"{green('📊 Total geral:')} {bold(str(total_geral))} resultado(s) de {len([f for f in todos_resultados.values() if f])} fonte(s)\n")
    print(f"{gray('═' * 70)}\n")
    
    # Exibir por fonte
    for fonte_nome, resultados in sorted(todos_resultados.items()):
        if not resultados:
            continue
        
        print(f"\n{magenta('═' * 70)}")
        print(f"{magenta('FONTE:')} {bold(fonte_nome.upper())} - {len(resultados)} resultado(s)")
        print(f"{magenta('═' * 70)}\n")
        
        for idx, r in enumerate(resultados, 1):
            exibir_resultado_item(r, fonte_nome, idx - 1, len(resultados))
        
        print(f"{gray('─' * 70)}\n")
    
    print(f"{green('✓')} Visualização completa finalizada!\n")

def main():
    """Função principal - Loop interativo com fluxo otimizado"""
    clear_screen()
    print_header("UNI - COLETOR UNIVERSAL DE DADOS v1.0", "=", 70)
    print(f"{cyan('Sistema completo de coleta de dados de múltiplas fontes')}\n")
    msg_sair = "Digite 'sair' a qualquer momento para encerrar"
    print(f"{gray(msg_sair)}\n")
    
    while True:
        # PASSO 1: Solicitar termo e região primeiro
        print_header("CONFIGURAÇÃO INICIAL", "=", 70)
        termo = input(f"{blue('> Termo de busca')}: ").strip()
        
        if check_exit(termo):
            print(yellow("\nEncerrando... Até logo!\n"))
            break
        
        if not termo:
            print(red("  ✗ Termo não pode estar vazio.\n"))
            continue
        
        # Configurações padrão
        region = input(f"{blue('> Região')} [br]: ").strip().lower() or "br"
        lang = input(f"{blue('> Idioma')} [pt]: ").strip().lower() or "pt"
        limite_input = input(f"{blue('> Limite de resultados por fonte')} [10]: ").strip()
        limite = int(limite_input) if limite_input.isdigit() else 10
        
        print()
        
        # PASSO 2: Seleção de fontes
        exibir_menu_fontes()
        escolha = input(f"{blue('> Selecione as fontes')} (ex: 1,2,3 ou 't' para todas): ").strip().lower()
        
        if check_exit(escolha):
            break
        
        # Processar seleção
        if escolha == "t":
            fontes_selecionadas = list(FONTES_DISPONIVEIS.keys())
            fontes_nomes = [FONTES_DISPONIVEIS[k]["nome"] for k in fontes_selecionadas]
        else:
            fontes_selecionadas = [f.strip() for f in escolha.split(",") 
                                  if f.strip() in FONTES_DISPONIVEIS]
            fontes_nomes = [FONTES_DISPONIVEIS[k]["nome"] for k in fontes_selecionadas]
        
        if not fontes_selecionadas:
            print(red("  ✗ Nenhuma fonte válida selecionada. Tente novamente.\n"))
            time.sleep(1)
            continue
        
        # Criar estrutura de diretórios organizada
        timestamp = now_tag()
        estrutura = criar_estrutura_diretorios(termo, timestamp)
        
        # Salvar metadados
        metadados = salvar_metadados(termo, region, lang, limite, fontes_nomes, estrutura)
        
        print()
        
        # PASSO 3: Coletar dados com exibição em tempo real
        todos_resultados = {}
        
        if escolha == "t":
            # Coletar todas as fontes
            todos_resultados = coletar_todas_fontes(termo, region, lang, limite, estrutura["base"])
        else:
            # Coletar fontes selecionadas
            print_header(f"COLETANDO DADOS PARA: '{termo}'", "=", 70)
            print(f"{cyan('Configurações:')} Região: {bold(region)} | Idioma: {bold(lang)} | Limite: {bold(str(limite))}\n")
            print(f"{gray('─' * 70)}\n")
            
            for idx, key in enumerate(fontes_selecionadas, 1):
                fonte = FONTES_DISPONIVEIS[key]
                print_progress(idx, len(fontes_selecionadas), "Progresso geral")
                resultados = coletar_fonte_com_exibicao(key, fonte, termo, region, lang, limite)
                todos_resultados[fonte["nome"]] = resultados
                time.sleep(0.3)
        
        # PASSO 4: Exibir todos os dados coletados de forma fluida
        print()
        exibir_todos_resultados_fluido(todos_resultados, termo)
        
        # PASSO 5: Salvar tudo organizado
        print_header("SALVANDO DADOS ORGANIZADOS", "=", 70)
        
        # Salvar por fonte
        for fonte_nome, resultados in todos_resultados.items():
            if resultados:
                filename = f"{fonte_nome.lower().replace(' ', '_').replace('-', '_')}.csv"
                salvar_csv(resultados, filename, estrutura["por_fonte"])
        
        # Criar CSV consolidado otimizado
        if any(todos_resultados.values()):
            df_consolidado = criar_csv_consolidado_otimizado(todos_resultados, metadados, estrutura)
            
            # Salvar JSON completo
            salvar_json(todos_resultados, "resultados_completos.json", estrutura["consolidado"])
            
            # Resumo final
            print_header("RESUMO FINAL DA COLETA", "=", 70)
            print(f"{green('✓')} Termo pesquisado: {bold(termo)}")
            print(f"{green('✓')} Fontes consultadas: {len([f for f in todos_resultados.values() if f])}")
            print(f"{green('✓')} Total de resultados: {bold(str(len(df_consolidado)))}")
            print(f"{green('✓')} Estrutura de diretórios:")
            print(f"    {gray('📁')} Base: {estrutura['base']}")
            print(f"    {gray('📁')} Por fonte: {estrutura['por_fonte']}")
            print(f"    {gray('📁')} Consolidado: {estrutura['consolidado']}")
            print(f"    {gray('📁')} Metadados: {estrutura['metadados']}\n")
            
            # Estatísticas por fonte
            print(f"{cyan('Estatísticas detalhadas por fonte:')}")
            for fonte_nome, resultados in sorted(todos_resultados.items()):
                count = len(resultados)
                status = green("✓") if count > 0 else yellow("⚠")
                print(f"  {status} {fonte_nome:<30} {count:>4} resultado(s)")
        else:
            print(yellow("\n  ⚠ Nenhum resultado coletado.\n"))
        
        # Continuar?
        print()
        continuar = input(f"{blue('> Deseja fazer outra busca?')} (s/n) [s]: ").strip().lower()
        if continuar in ["n", "nao", "não", "no"]:
            print(yellow("\nEncerrando... Obrigado por usar UNI!\n"))
            break
        print()
        clear_screen()

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



