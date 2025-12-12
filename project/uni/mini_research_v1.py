#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Research v1 - Coletor de Dados Multi-Fonte
Versão melhorada com foco em UX/UI seguindo heurísticas de Nielsen

Melhorias v1:
- Menu unificado sem modos (tudo configurável)
- Parâmetros globais e específicos separados
- Exibição em tempo real dos dados coletados
- Padrão de listagem numerada (1,2,3,t)
- Múltiplas seleções por vírgula
- Ordem lógica de configuração (jornada do usuário)
- Chaves API do arquivo uni.py
"""

import os
import re
import string
import time
import warnings
import requests
import pandas as pd
from datetime import datetime
from functools import lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from collections import defaultdict
import sys

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
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

warnings.filterwarnings("ignore", category=FutureWarning)

# ======================================
# 🔑 CHAVES API (do arquivo uni.py)
# ======================================

GOOGLE_API_KEY = "AIzaSyBj80B2fwVvFEMtcQU8tPV_NCNaEmQvzhc"
GOOGLE_CX = "f07ccd3b922d6437b"
BRAVE_API_KEY = "BSAjC9Yvq2s8_hYFIPWQ2QEl_XHpsQp"
SERPAPI_KEY = "e71430bcff8bdc906f7a5ed9ae1538355c2efb0fb88ffa071f7125a76cc2b142"
YOUTUBE_API_KEY = "AIzaSyBj80B2fwVvFEMtcQU8tPV_NCNaEmQvzhc"

# ======================================
# 🎨 Estilo Terminal (cores)
# ======================================

def color(text, code): return f"\033[{code}m{text}\033[0m"
def blue(text): return color(text, "34")
def green(text): return color(text, "32")
def yellow(text): return color(text, "33")
def red(text): return color(text, "31")
def gray(text): return color(text, "90")
def cyan(text): return color(text, "36")
def magenta(text): return color(text, "35")
def bold(text): return color(text, "1")

# ======================================
# 🛠️ Funções Utilitárias
# ======================================

def now_tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def check_exit(value): 
    return value.lower() in {"sair", "fechar", "terminar", "ok", "exit", "quit", "q"}

def parse_multi_input(s, default=None, map_func=None):
    """Parse múltiplas entradas separadas por vírgula"""
    if not s or s.strip() == "":
        return [default] if default is not None else []
    
    s = s.strip().lower()
    
    # Se for "t" ou "todos", retorna lista especial
    if s in ["t", "todos", "all"]:
        return "todos"
    
    # Parse números ou strings
    items = [x.strip() for x in s.split(",") if x.strip()]
    
    if map_func:
        items = [map_func(x) for x in items if x]
    
    return items if items else ([default] if default is not None else [])

def print_header(title, char="=", width=70):
    """Cabeçalho padronizado"""
    print(cyan("\n" + char * width))
    print(cyan(f"  {title}"))
    print(cyan(char * width + "\n"))

def print_menu(title, options, default=None):
    """Menu padronizado numerado"""
    print(cyan(f"\n{title}"))
    print("-" * 70)
    
    for key, value in options.items():
        if key == "t":
            print(f"  {green('t')}. {value} (todos)")
        else:
            marker = green(f"{key}") if key == default else f"{key}"
            print(f"  {marker}. {value}")
    
    print("-" * 70)

def print_progress(message, icon="⏳"):
    """Mensagem de progresso"""
    print(f"{blue(icon)} {gray(message)}")

def print_success(message, count=None):
    """Mensagem de sucesso"""
    if count is not None:
        print(f"{green('✓')} {message} {green(f'({count} itens)')}")
    else:
        print(f"{green('✓')} {message}")

def print_data_item(index, item, prefix=""):
    """Exibe um item de dados formatado"""
    print(f"  {green(f'{index:2d}.')} {prefix}{item}")

def flush_output():
    """Força flush da saída para exibição em tempo real"""
    sys.stdout.flush()

BASE_DIR = "dados"

# ======================================
# 📦 MÓDULO 1: GOOGLE SUGGEST
# ======================================

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"
REGIONS_AVAILABLE = ["br", "us", "fr", "de", "jp", "es", "it", "uk"]
CLIENTS_AVAILABLE = ["chrome", "firefox"]
SOURCES_AVAILABLE = {"web": "", "youtube": "yt", "news": "n", "shopping": "sh"}

CATEGORIES = {
    1: ("Questões", ["o que ", "é ", "não é", "como ", "por que ", "onde ", "quando ", "qual ", "quanto "]),
    2: ("Preposições", ["de ", "para ", "com ", "sem ", "sobre ", "contra ", "até "]),
    3: ("Comparações", ["vs ", "melhor que ", "pior que ", "ou ", "e "]),
}

def make_session():
    sess = requests.Session()
    sess.headers.update({"User-Agent": "Mozilla/5.0 Chrome/140.0"})
    retry = Retry(total=5, backoff_factor=0.3,
                  status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=["GET"])
    sess.mount("https://", HTTPAdapter(max_retries=retry))
    return sess

SESSION = make_session()

@lru_cache(maxsize=512)
def get_suggestions(query, region="br", client="chrome", source="", lang="", limit=10):
    """Consulta a API do Google Suggest (com cache)"""
    params = {"q": query, "gl": region, "client": client}
    if lang: params["hl"] = lang
    if source: params["ds"] = source
    
    try:
        r = SESSION.get(SUGGEST_URL, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        suggestions = data[1] if len(data) > 1 else []
        relevance = data[4].get("google:suggestrelevance", [0]*len(suggestions)) if len(data) > 4 and isinstance(data[4], dict) else [0]*len(suggestions)
        return list(zip(suggestions, relevance))[:limit]
    except:
        return []

def run_suggest(termo, config, output_dir, resultados_tempo_real):
    """Executa Google Suggest"""
    print_header(f"GOOGLE SUGGEST — {termo}")
    
    regions = config.get("regions", ["br"])
    clients = config.get("clients", ["chrome"])
    sources = config.get("sources", ["web"])
    opcoes = config.get("opcoes", [1])
    limit = config.get("limit", 15)
    delay = config.get("delay", 1.0)
    
    resultados = []
    counter = 0
    
    print_progress("Iniciando coleta de sugestões...")
    flush_output()
    
    for region in regions:
        for client in clients:
            for source_name in sources:
                source_code = SOURCES_AVAILABLE.get(source_name, "")
                
                # Top sugestões
                if 1 in opcoes or "todos" in opcoes:
                    print_progress(f"Coletando top sugestões [{region}/{client}/{source_name}]...")
                    sugs = get_suggestions(termo, region, client, source_code, "", limit)
                    flush_output()
                    
                    for s, r in sugs:
                        counter += 1
                        item = {
                            "termo": termo,
                            "sugestao": s,
                            "relevancia": r,
                            "regiao": region,
                            "cliente": client,
                            "fonte": source_name,
                            "tipo": "top"
                        }
                        resultados.append(item)
                        resultados_tempo_real["suggest"].append(item)
                        print_data_item(counter, s, f"[{gray(f'{r}')}] ")
                        flush_output()
                    time.sleep(delay)
                
                # Expansões a-z
                if 2 in opcoes or "todos" in opcoes:
                    print_progress(f"Coletando expansões a-z [{region}/{client}/{source_name}]...")
                    for letter in string.ascii_lowercase:
                        q = f"{termo} {letter}"
                        sugs = get_suggestions(q, region, client, source_code, "", limit)
                        flush_output()
                        for s, r in sugs:
                            counter += 1
                            item = {
                                "termo": termo,
                                "sugestao": s,
                                "relevancia": r,
                                "regiao": region,
                                "cliente": client,
                                "fonte": source_name,
                                "tipo": f"expansao_{letter}"
                            }
                            resultados.append(item)
                            resultados_tempo_real["suggest"].append(item)
                            print_data_item(counter, s, f"[{gray(f'{r}')}] ")
                            flush_output()
                        time.sleep(delay * 0.3)
                
                # Expansões 0-9
                if 3 in opcoes or "todos" in opcoes:
                    print_progress(f"Coletando expansões 0-9 [{region}/{client}/{source_name}]...")
                    for digit in "0123456789":
                        q = f"{termo} {digit}"
                        sugs = get_suggestions(q, region, client, source_code, "", limit)
                        flush_output()
                        for s, r in sugs:
                            counter += 1
                            item = {
                                "termo": termo,
                                "sugestao": s,
                                "relevancia": r,
                                "regiao": region,
                                "cliente": client,
                                "fonte": source_name,
                                "tipo": f"expansao_{digit}"
                            }
                            resultados.append(item)
                            resultados_tempo_real["suggest"].append(item)
                            print_data_item(counter, s, f"[{gray(f'{r}')}] ")
                            flush_output()
                        time.sleep(delay * 0.3)
                
                # Categorias
                if 4 in opcoes or "todos" in opcoes:
                    print_progress(f"Coletando categorias [{region}/{client}/{source_name}]...")
                    for cat_id, (cat_name, words) in CATEGORIES.items():
                        for w in words:
                            q = f"{termo} {w}"
                            sugs = get_suggestions(q, region, client, source_code, "", limit)
                            flush_output()
                            for s, r in sugs:
                                counter += 1
                                item = {
                                    "termo": termo,
                                    "sugestao": s,
                                    "relevancia": r,
                                    "regiao": region,
                                    "cliente": client,
                                    "fonte": source_name,
                                    "tipo": f"categoria_{cat_name}_{w.strip()}"
                                }
                                resultados.append(item)
                                resultados_tempo_real["suggest"].append(item)
                                print_data_item(counter, s, f"[{gray(f'{r}')}] ")
                                flush_output()
                            time.sleep(delay * 0.3)
    
    # Salvar
    if resultados:
        df = pd.DataFrame(resultados)
        file = os.path.join(output_dir, f"suggest_{termo}_{now_tag()}.csv")
        df.to_csv(file, index=False, encoding="utf-8-sig")
        print_success(f"Salvo: {file}", len(resultados))
    
    return resultados

# ======================================
# 📦 MÓDULO 2: GOOGLE TRENDS
# ======================================

def run_trends(termo, config, output_dir, resultados_tempo_real):
    """Executa Google Trends"""
    if not HAS_PYTRENDS:
        print(yellow("[!] pytrends não instalado. Pulando Google Trends."))
        return []
    
    print_header(f"GOOGLE TRENDS — {termo}")
    
    region = config.get("region", "BR")
    lang = config.get("lang", "pt")
    gtypes = config.get("gtypes", [""])
    timeframe = config.get("timeframe", "today 12-m")
    topn = config.get("topn", 20)
    opcoes = config.get("opcoes", [1, 2, 3, 4])
    delay = config.get("delay", 1.0)
    
    OUTPUT_DIR = ensure_dir(os.path.join(output_dir, "trends"))
    pytrends = TrendReq(hl=f"{lang}-{region}" if region else lang, tz=0)
    
    resultados = []
    tipos_map = {"": "web", "images": "images", "news": "news", "youtube": "youtube"}
    
    for gtype in gtypes:
        tipo_nome = tipos_map.get(gtype, "web")
        print_progress(f"Processando {tipo_nome}...")
        flush_output()
        
        try:
            pytrends.build_payload([termo], timeframe=timeframe, geo=region, gprop=gtype)
        except Exception as e:
            print(red(f"  [ERRO] {e}"))
            continue
        
        # Top
        if 1 in opcoes or "todos" in opcoes:
            try:
                related = pytrends.related_queries()
                r = related.get(termo, {})
                if r and "top" in r and r["top"] is not None:
                    df = r["top"].head(topn).copy()
                    print_progress(f"Top relacionados ({tipo_nome}): {len(df)} itens")
                    flush_output()
                    
                    for i, row in enumerate(df.itertuples(), 1):
                        item = {"tipo": "top", "fonte": tipo_nome, "query": row.query, "value": row.value}
                        resultados.append(item)
                        resultados_tempo_real["trends"].append(item)
                        print_data_item(i, f"{row.query} {gray(f'({row.value})')}")
                        flush_output()
                    
                    file = os.path.join(OUTPUT_DIR, f"top_{tipo_nome}_{termo}_{now_tag()}.csv")
                    df.to_csv(file, index=False, encoding="utf-8-sig")
                    print_success(f"Salvo: {file}", len(df))
            except:
                pass
        
        # Rising
        if 2 in opcoes or "todos" in opcoes:
            try:
                related = pytrends.related_queries()
                r = related.get(termo, {})
                if r and "rising" in r and r["rising"] is not None:
                    df = r["rising"].head(topn).copy()
                    print_progress(f"Rising relacionados ({tipo_nome}): {len(df)} itens")
                    flush_output()
                    
                    for i, row in enumerate(df.itertuples(), 1):
                        item = {"tipo": "rising", "fonte": tipo_nome, "query": row.query, "value": row.value}
                        resultados.append(item)
                        resultados_tempo_real["trends"].append(item)
                        print_data_item(i, f"{row.query} {gray(f'({row.value})')}")
                        flush_output()
                    
                    file = os.path.join(OUTPUT_DIR, f"rising_{tipo_nome}_{termo}_{now_tag()}.csv")
                    df.to_csv(file, index=False, encoding="utf-8-sig")
                    print_success(f"Salvo: {file}", len(df))
            except:
                pass
        
        # Regiões
        if 3 in opcoes or "todos" in opcoes:
            try:
                regioes = pytrends.interest_by_region(resolution="country", inc_low_vol=True)
                if not regioes.empty:
                    serie = regioes[termo].sort_values(ascending=False).head(topn)
                    print_progress(f"Interesse por regiões ({tipo_nome}): {len(serie)} itens")
                    flush_output()
                    
                    for i, (reg, val) in enumerate(serie.items(), 1):
                        item = {"tipo": "regioes", "fonte": tipo_nome, "regiao": reg, "valor": val}
                        resultados.append(item)
                        resultados_tempo_real["trends"].append(item)
                        print_data_item(i, f"{reg} {gray(f'({val})')}")
                        flush_output()
                    
                    df = pd.DataFrame({"regiao": serie.index, "valor": serie.values})
                    file = os.path.join(OUTPUT_DIR, f"regioes_{tipo_nome}_{termo}_{now_tag()}.csv")
                    df.to_csv(file, index=False, encoding="utf-8-sig")
                    print_success(f"Salvo: {file}", len(serie))
            except:
                pass
        
        # Tempo
        if 4 in opcoes or "todos" in opcoes:
            try:
                df_time = pytrends.interest_over_time()
                if not df_time.empty:
                    print_progress(f"Interesse ao longo do tempo ({tipo_nome}): {len(df_time)} pontos")
                    flush_output()
                    
                    for i, (idx, val) in enumerate(df_time[termo].items(), 1):
                        item = {"tipo": "tempo", "fonte": tipo_nome, "data": idx.strftime("%Y-%m-%d"), "valor": val}
                        resultados.append(item)
                        resultados_tempo_real["trends"].append(item)
                        if i <= 10:  # Exibir apenas primeiros 10
                            print_data_item(i, f"{idx.strftime('%Y-%m-%d')} → {gray(val)}")
                            flush_output()
                    
                    df = pd.DataFrame({"data": df_time.index, "valor": df_time[termo].values})
                    file = os.path.join(OUTPUT_DIR, f"tempo_{tipo_nome}_{termo}_{now_tag()}.csv")
                    df.to_csv(file, index=False, encoding="utf-8-sig")
                    print_success(f"Salvo: {file}", len(df_time))
            except:
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
                    resultados.append({
                        "engine": "duckduckgo",
                        "rank": i,
                        "title": r["title"],
                        "link": r["href"]
                    })
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

def run_serp(termo, config, output_dir, resultados_tempo_real):
    """Executa SERP"""
    print_header(f"SERP — {termo}")
    
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
    
    if "todos" in buscadores or 5 in buscadores:
        buscadores = [1, 2, 3, 4]
    
    for bus_id in buscadores:
        if bus_id not in buscadores_map:
            continue
        
        nome, func, disponivel = buscadores_map[bus_id]
        
        if not disponivel:
            print(yellow(f"  [!] {nome} não disponível (faltam API keys)"))
            continue
        
        print_progress(f"Buscando no {nome}...")
        flush_output()
        
        if bus_id == 2:  # Google precisa de lang
            res = func(termo, region, "pt", limite)
        else:
            res = func(termo, region, limite)
        
        time.sleep(delay)
        
        if res:
            print_progress(f"{nome}: {len(res)} resultados encontrados")
            flush_output()
            
            for r in res:
                resultados.append(r)
                resultados_tempo_real["serp"].append(r)
                rank_str = f"[{r['engine'].upper()}]"
                print_data_item(r['rank'], f"{r['title']}", f"{green(rank_str)} ")
                print(f"      {gray(r['link'])}")
                flush_output()
            
            df = pd.DataFrame(res)
            file = os.path.join(SERP_DIR, f"{nome.lower()}_{termo}.csv")
            df.to_csv(file, index=False, encoding="utf-8-sig")
            print_success(f"Salvo: {file}", len(res))
    
    if resultados:
        df = pd.DataFrame(resultados)
        file = os.path.join(SERP_DIR, f"serp_consolidado_{termo}.csv")
        df.to_csv(file, index=False, encoding="utf-8-sig")
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

def buscar_videos_api(query, region, lang, order="relevance", max_results=10):
    if not youtube:
        return []
    try:
        request = youtube.search().list(q=query, part="snippet", type="video", regionCode=region.upper(), relevanceLanguage=lang.lower(), order=order, maxResults=max_results)
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

def buscar_videos(query, region, lang, order="relevance", max_results=10):
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

def run_youtube(termo, config, output_dir, resultados_tempo_real):
    """Executa YouTube"""
    print_header(f"YOUTUBE — {termo}")
    
    region = config.get("region", "br")
    lang = config.get("lang", "pt")
    order = config.get("order", "relevance")
    limite_videos = config.get("limite_videos", 50)
    coletar_comentarios = config.get("coletar_comentarios", False)
    limite_comentarios = config.get("limite_comentarios", 50)
    videos_selecionados = config.get("videos_selecionados", [1])
    delay = config.get("delay", 1.0)
    
    YOUTUBE_DIR = ensure_dir(os.path.join(output_dir, "youtube"))
    
    print_progress("Buscando vídeos...")
    flush_output()
    
    videos = buscar_videos(termo, region, lang, order, limite_videos)
    time.sleep(delay)
    
    if not videos:
        print(yellow("  [!] Nenhum vídeo encontrado"))
        return []
    
    print_progress(f"Vídeos encontrados: {len(videos)}")
    flush_output()
    
    for i, v in enumerate(videos, 1):
        item = {"video": v, "tipo": "video"}
        resultados_tempo_real["youtube"].append(item)
        print_data_item(i, v['titulo'])
        print(f"      Canal: {v.get('canal', 'N/A')} | Link: {gray(v['link'])}")
        flush_output()
    
    df_videos = pd.DataFrame(videos)
    file = os.path.join(YOUTUBE_DIR, f"videos_{termo}.csv")
    df_videos.to_csv(file, index=False, encoding="utf-8-sig")
    print_success(f"Salvo: {file}", len(videos))
    
    comentarios_todos = []
    if coletar_comentarios:
        print_progress("Coletando comentários...")
        flush_output()
        
        if videos_selecionados == "todos" or videos_selecionados == "t":
            indices_list = range(1, len(videos) + 1)
        else:
            indices_list = videos_selecionados
        
        for i in indices_list:
            if i <= len(videos):
                vid = videos[i - 1]
                print_progress(f"  Vídeo {i}: {vid['titulo'][:50]}...")
                flush_output()
                
                comentarios = buscar_comentarios(vid["videoId"], limite_comentarios)
                time.sleep(delay)
                
                if comentarios:
                    for j, c in enumerate(comentarios, 1):
                        c["video_id"] = vid["videoId"]
                        c["video_titulo"] = vid["titulo"]
                        comentarios_todos.append(c)
                        resultados_tempo_real["youtube"].append({"comentario": c, "tipo": "comentario"})
                        if j <= 10:  # Exibir apenas primeiros 10 por vídeo
                            likes_str = f"({c['likes']} likes)"
                            print_data_item(j, f"{c['autor']}: {c['comentario'][:60]}... {gray(likes_str)}")
                            flush_output()
        
        if comentarios_todos:
            df_comentarios = pd.DataFrame(comentarios_todos)
            file = os.path.join(YOUTUBE_DIR, f"comentarios_{termo}.csv")
            df_comentarios.to_csv(file, index=False, encoding="utf-8-sig")
            print_success(f"Comentários salvos: {file}", len(comentarios_todos))
    
    return {"videos": videos, "comentarios": comentarios_todos}

# ======================================
# 📦 MÓDULO 5: APP STORES
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

def run_play_store(termo, config, output_dir, resultados_tempo_real):
    """Executa Google Play Store"""
    if not HAS_PLAY_SCRAPER:
        print(yellow("[!] google-play-scraper não instalado. Pulando Google Play Store."))
        return []
    
    print_header(f"GOOGLE PLAY STORE — {termo}")
    
    country = config.get("country", "br")
    lang = config.get("lang", "pt")
    n_apps = config.get("n_apps", 50)
    max_reviews = config.get("max_reviews", 50)
    coletar_reviews = config.get("coletar_reviews", False)
    apps_selecionados = config.get("apps_selecionados", [1, 2, 3])
    delay = config.get("delay", 1.0)
    
    STORES_DIR = ensure_dir(os.path.join(output_dir, "play_store"))
    
    print_progress("Buscando apps no Google Play...")
    flush_output()
    
    df_google = fetch_google(termo, lang, country, n_apps)
    time.sleep(delay)
    
    if df_google.empty:
        print(yellow("  [!] Nenhum app encontrado"))
        return []
    
    print_progress(f"Apps encontrados: {len(df_google)}")
    flush_output()
    
    for i, row in enumerate(df_google.itertuples(), 1):
        item = {"app": {"title": row.title, "developer": row.developer, "rating": row.rating, "installs": row.installs}, "tipo": "app"}
        resultados_tempo_real["play_store"].append(item)
        print_data_item(i, f"{row.title} | ⭐ {row.rating or 's/d'} | {row.developer}")
        print(f"      Downloads: {row.installs}")
        flush_output()
    
    file = os.path.join(STORES_DIR, f"apps_google_{termo}.csv")
    df_google.to_csv(file, index=False, encoding="utf-8-sig")
    print_success(f"Salvo: {file}", len(df_google))
    
    if coletar_reviews:
        print_progress("Coletando reviews...")
        flush_output()
        
        if apps_selecionados == "todos" or apps_selecionados == "t":
            apps_ids = df_google["id"].dropna().tolist()
        else:
            apps_ids = [df_google.iloc[i-1]["id"] for i in apps_selecionados if i <= len(df_google)]
        
        for app_id in apps_ids:
            app_title = df_google.loc[df_google["id"] == app_id, "title"].iloc[0]
            print_progress(f"  {app_title}...")
            flush_output()
            
            df_reviews = fetch_reviews_google(app_id, lang, country, max_reviews)
            time.sleep(delay)
            
            if not df_reviews.empty:
                for j, row in enumerate(df_reviews.head(10).itertuples(), 1):
                    item = {"review": {"app": app_title, "rating": row.score, "content": row.content[:60]}, "tipo": "review"}
                    resultados_tempo_real["play_store"].append(item)
                    print_data_item(j, f"⭐{row.score} | {row.content[:60]}...")
                    flush_output()
                
                file = os.path.join(STORES_DIR, f"reviews_google_{app_id}.csv")
                df_reviews.to_csv(file, index=False, encoding="utf-8-sig")
                print_success(f"  Reviews: {file}", len(df_reviews))
    
    return {"apps": df_google}

def run_app_store(termo, config, output_dir, resultados_tempo_real):
    """Executa Apple App Store"""
    print_header(f"APPLE APP STORE — {termo}")
    
    country = config.get("country", "br")
    n_apps = config.get("n_apps", 50)
    max_reviews = config.get("max_reviews", 50)
    coletar_reviews = config.get("coletar_reviews", False)
    apps_selecionados = config.get("apps_selecionados", [1, 2, 3])
    delay = config.get("delay", 1.0)
    
    STORES_DIR = ensure_dir(os.path.join(output_dir, "app_store"))
    
    print_progress("Buscando apps na App Store...")
    flush_output()
    
    df_apple = apple_df(fetch_apple(termo, country, n_apps))
    time.sleep(delay)
    
    if df_apple.empty:
        print(yellow("  [!] Nenhum app encontrado"))
        return []
    
    print_progress(f"Apps encontrados: {len(df_apple)}")
    flush_output()
    
    for i, row in enumerate(df_apple.itertuples(), 1):
        item = {"app": {"title": row.title, "developer": row.developer, "rating": row.rating, "ratings_count": row.ratings_count}, "tipo": "app"}
        resultados_tempo_real["app_store"].append(item)
        print_data_item(i, f"{row.title} | ⭐ {row.rating or 's/d'} | {row.developer}")
        print(f"      Avaliações: {row.ratings_count}")
        flush_output()
    
    file = os.path.join(STORES_DIR, f"apps_apple_{termo}.csv")
    df_apple.to_csv(file, index=False, encoding="utf-8-sig")
    print_success(f"Salvo: {file}", len(df_apple))
    
    if coletar_reviews:
        print_progress("Coletando reviews...")
        flush_output()
        
        if apps_selecionados == "todos" or apps_selecionados == "t":
            apps_ids = df_apple["id"].dropna().tolist()
        else:
            apps_ids = [df_apple.iloc[i-1]["id"] for i in apps_selecionados if i <= len(df_apple)]
        
        for app_id in apps_ids:
            app_title = df_apple.loc[df_apple["id"] == app_id, "title"].iloc[0]
            print_progress(f"  {app_title}...")
            flush_output()
            
            df_reviews = fetch_reviews_apple(app_id, country, max_reviews)
            time.sleep(delay)
            
            if not df_reviews.empty:
                for j, row in enumerate(df_reviews.head(10).itertuples(), 1):
                    item = {"review": {"app": app_title, "rating": row.rating, "content": row.content[:60]}, "tipo": "review"}
                    resultados_tempo_real["app_store"].append(item)
                    print_data_item(j, f"⭐{row.rating} | {row.content[:60]}...")
                    flush_output()
                
                file = os.path.join(STORES_DIR, f"reviews_apple_{app_id}.csv")
                df_reviews.to_csv(file, index=False, encoding="utf-8-sig")
                print_success(f"  Reviews: {file}", len(df_reviews))
    
    return {"apps": df_apple}

# ======================================
# 🎯 CONFIGURAÇÃO (Jornada do Usuário)
# ======================================

def coletar_configuracao():
    """Coleta todas as configurações em ordem lógica (jornada do usuário)"""
    print_header("CONFIGURAÇÃO DE COLETA")
    
    config = {}
    
    # 1. Termo de busca (obrigatório)
    print(cyan("\n1. TERMO DE BUSCA"))
    print("-" * 70)
    termo = input("> Digite o termo de busca: ").strip()
    if not termo:
        print(red("Termo não pode estar vazio!"))
        return None
    config["termo"] = termo
    
    # 2. Parâmetros globais
    print(cyan("\n2. PARÂMETROS GLOBAIS"))
    print("-" * 70)
    
    print_menu("Regiões disponíveis:", {i+1: reg for i, reg in enumerate(REGIONS_AVAILABLE[:8])}, default=1)
    regions_input = input("> Selecione regiões (ex: 1,2 ou 't' para todas) [1]: ").strip() or "1"
    regions_selected = parse_multi_input(regions_input, default=1, map_func=lambda x: REGIONS_AVAILABLE[int(x)-1] if x.isdigit() and 1 <= int(x) <= len(REGIONS_AVAILABLE) else None)
    if regions_selected == "todos":
        config["regions"] = REGIONS_AVAILABLE
    else:
        config["regions"] = [r for r in regions_selected if r]
    
    config["delay"] = float(input("> Delay entre requisições em segundos [1.0]: ").strip() or 1.0)
    
    # 3. Fontes de dados
    print(cyan("\n3. FONTES DE DADOS"))
    print("-" * 70)
    print_menu("Selecione as fontes:", {
        1: "Google Suggest",
        2: "Google Trends",
        3: "SERP (Buscadores)",
        4: "YouTube",
        5: "Google Play Store",
        6: "Apple App Store",
    }, default=None)
    
    fontes_input = input("> Selecione fontes (ex: 1,2,4 ou 't' para todas) [t]: ").strip() or "t"
    fontes = parse_multi_input(fontes_input, default=None, map_func=int)
    if fontes == "todos":
        config["fontes"] = [1, 2, 3, 4, 5, 6]
    else:
        config["fontes"] = [f for f in fontes if isinstance(f, int) and 1 <= f <= 6]
    
    # 4. Configurações específicas por fonte
    print(cyan("\n4. CONFIGURAÇÕES ESPECÍFICAS POR FONTE"))
    print("-" * 70)
    
    # Google Suggest
    if 1 in config["fontes"]:
        print(cyan("\n--- Google Suggest ---"))
        print_menu("Clientes:", {i+1: cli for i, cli in enumerate(CLIENTS_AVAILABLE)}, default=1)
        clients_input = input("> Selecione clientes [1]: ").strip() or "1"
        clients = parse_multi_input(clients_input, default=1, map_func=lambda x: CLIENTS_AVAILABLE[int(x)-1] if x.isdigit() else None)
        config["suggest"] = {
            "clients": clients if clients != "todos" else CLIENTS_AVAILABLE,
            "sources": parse_multi_input(input("> Fontes (web,youtube,news,shopping) [web]: ").strip() or "web", default="web"),
            "opcoes": parse_multi_input(input("> Opções (1=top,2=a-z,3=0-9,4=categorias) [1]: ").strip() or "1", default=1, map_func=int),
            "limit": int(input("> Resultados por consulta [15]: ").strip() or 15),
        }
        if config["suggest"]["opcoes"] == "todos":
            config["suggest"]["opcoes"] = [1, 2, 3, 4]
    
    # Google Trends
    if 2 in config["fontes"]:
        print(cyan("\n--- Google Trends ---"))
        config["trends"] = {
            "gtypes": parse_multi_input(input("> Tipos (web,images,news,youtube) [web]: ").strip() or "web", default="web"),
            "timeframe": {"1": "now 7-d", "2": "today 1-m", "3": "today 3-m", "4": "today 12-m", "5": "today 5-y", "6": "all"}.get(input("> Período (1-6) [4]: ").strip() or "4", "today 12-m"),
            "opcoes": parse_multi_input(input("> Opções (1=top,2=rising,3=regiões,4=tempo) [1,2,3,4]: ").strip() or "1,2,3,4", default=1, map_func=int),
            "topn": int(input("> Resultados [20]: ").strip() or 20),
        }
        if config["trends"]["opcoes"] == "todos":
            config["trends"]["opcoes"] = [1, 2, 3, 4]
    
    # SERP
    if 3 in config["fontes"]:
        print(cyan("\n--- SERP ---"))
        print_menu("Buscadores:", {
            1: "DuckDuckGo (sem API key)",
            2: "Google (requer API key)",
            3: "Brave (requer API key)",
            4: "Bing (requer API key)",
        }, default=1)
        buscadores_input = input("> Selecione buscadores [1]: ").strip() or "1"
        buscadores = parse_multi_input(buscadores_input, default=1, map_func=int)
        config["serp"] = {
            "buscadores": buscadores if buscadores != "todos" else [1, 2, 3, 4],
            "limite": int(input("> Resultados por buscador [20]: ").strip() or 20),
        }
    
    # YouTube
    if 4 in config["fontes"]:
        print(cyan("\n--- YouTube ---"))
        config["youtube"] = {
            "order": input("> Ordenar por (relevance,date,viewCount) [relevance]: ").strip() or "relevance",
            "limite_videos": int(input("> Quantos vídeos? [50]: ").strip() or 50),
            "coletar_comentarios": input("> Coletar comentários? (s/n) [n]: ").strip().lower() == "s",
        }
        if config["youtube"]["coletar_comentarios"]:
            config["youtube"]["limite_comentarios"] = int(input("> Comentários por vídeo [50]: ").strip() or 50)
            videos_sel = input("> Quais vídeos? (1,2,3 ou 't' para todos) [1]: ").strip() or "1"
            config["youtube"]["videos_selecionados"] = parse_multi_input(videos_sel, default=1, map_func=int) if videos_sel != "t" else "todos"
        else:
            config["youtube"]["limite_comentarios"] = 0
            config["youtube"]["videos_selecionados"] = [1]
    
    # Google Play Store
    if 5 in config["fontes"]:
        print(cyan("\n--- Google Play Store ---"))
        config["play_store"] = {
            "n_apps": int(input("> Quantidade de apps [50]: ").strip() or 50),
            "coletar_reviews": input("> Coletar reviews? (s/n) [n]: ").strip().lower() == "s",
        }
        if config["play_store"]["coletar_reviews"]:
            config["play_store"]["max_reviews"] = int(input("> Reviews por app [50]: ").strip() or 50)
            apps_sel = input("> Quais apps? (1,2,3 ou 't' para todos) [1,2,3]: ").strip() or "1,2,3"
            config["play_store"]["apps_selecionados"] = parse_multi_input(apps_sel, default=1, map_func=int) if apps_sel != "t" else "todos"
        else:
            config["play_store"]["max_reviews"] = 0
            config["play_store"]["apps_selecionados"] = [1]
    
    # Apple App Store
    if 6 in config["fontes"]:
        print(cyan("\n--- Apple App Store ---"))
        config["app_store"] = {
            "n_apps": int(input("> Quantidade de apps [50]: ").strip() or 50),
            "coletar_reviews": input("> Coletar reviews? (s/n) [n]: ").strip().lower() == "s",
        }
        if config["app_store"]["coletar_reviews"]:
            config["app_store"]["max_reviews"] = int(input("> Reviews por app [50]: ").strip() or 50)
            apps_sel = input("> Quais apps? (1,2,3 ou 't' para todos) [1,2,3]: ").strip() or "1,2,3"
            config["app_store"]["apps_selecionados"] = parse_multi_input(apps_sel, default=1, map_func=int) if apps_sel != "t" else "todos"
        else:
            config["app_store"]["max_reviews"] = 0
            config["app_store"]["apps_selecionados"] = [1]
    
    # Adicionar parâmetros globais às configurações específicas
    for fonte_config in ["suggest", "trends", "serp", "youtube", "play_store", "app_store"]:
        if fonte_config in config:
            config[fonte_config]["region"] = config["regions"][0] if config["regions"] else "br"
            config[fonte_config]["lang"] = "pt"
            config[fonte_config]["country"] = config["regions"][0] if config["regions"] else "br"
            config[fonte_config]["delay"] = config["delay"]
    
    return config

# ======================================
# 🚀 FUNÇÃO PRINCIPAL
# ======================================

def main():
    print_header("MINI RESEARCH v1 - COLETOR DE DADOS MULTI-FONTE")
    print(cyan("Versão melhorada com foco em UX/UI seguindo heurísticas de Nielsen\n"))
    
    # Coletar configuração
    config = coletar_configuracao()
    if not config:
        print(red("\nConfiguração cancelada."))
        return
    
    termo = config["termo"]
    output_dir = ensure_dir(os.path.join(BASE_DIR, f"coleta_{termo}_{now_tag()}"))
    
    # Dicionário para resultados em tempo real
    resultados_tempo_real = {
        "suggest": [],
        "trends": [],
        "serp": [],
        "youtube": [],
        "play_store": [],
        "app_store": []
    }
    
    print_header("INICIANDO COLETA")
    print(green(f"[✓] Configuração concluída. Iniciando coleta para: {bold(termo)}\n"))
    
    resultados = {}
    
    # Executar fontes selecionadas
    if 1 in config["fontes"]:
        try:
            resultados["suggest"] = run_suggest(termo, config.get("suggest", {}), output_dir, resultados_tempo_real)
        except Exception as e:
            print(red(f"[ERRO] Google Suggest: {e}"))
            resultados["suggest"] = []
    
    if 2 in config["fontes"]:
        try:
            resultados["trends"] = run_trends(termo, config.get("trends", {}), output_dir, resultados_tempo_real)
        except Exception as e:
            print(red(f"[ERRO] Google Trends: {e}"))
            resultados["trends"] = []
    
    if 3 in config["fontes"]:
        try:
            resultados["serp"] = run_serp(termo, config.get("serp", {}), output_dir, resultados_tempo_real)
        except Exception as e:
            print(red(f"[ERRO] SERP: {e}"))
            resultados["serp"] = []
    
    if 4 in config["fontes"]:
        try:
            resultados["youtube"] = run_youtube(termo, config.get("youtube", {}), output_dir, resultados_tempo_real)
        except Exception as e:
            print(red(f"[ERRO] YouTube: {e}"))
            resultados["youtube"] = []
    
    if 5 in config["fontes"]:
        try:
            resultados["play_store"] = run_play_store(termo, config.get("play_store", {}), output_dir, resultados_tempo_real)
        except Exception as e:
            print(red(f"[ERRO] Google Play Store: {e}"))
            resultados["play_store"] = []
    
    if 6 in config["fontes"]:
        try:
            resultados["app_store"] = run_app_store(termo, config.get("app_store", {}), output_dir, resultados_tempo_real)
        except Exception as e:
            print(red(f"[ERRO] Apple App Store: {e}"))
            resultados["app_store"] = []
    
    print_header("COLETA FINALIZADA")
    print(green(f"[✓] Todos os dados salvos em: {output_dir}\n"))
    
    # Resumo final
    print(cyan("RESUMO DA COLETA:"))
    print("-" * 70)
    for fonte, dados in resultados.items():
        if dados:
            if isinstance(dados, dict):
                count = sum(len(v) if isinstance(v, (list, pd.DataFrame)) else 1 for v in dados.values())
            elif isinstance(dados, list):
                count = len(dados)
            else:
                count = 1
            print(f"  {green('✓')} {fonte.replace('_', ' ').title()}: {count} itens")
    print("-" * 70 + "\n")

if __name__ == "__main__":
    main()




