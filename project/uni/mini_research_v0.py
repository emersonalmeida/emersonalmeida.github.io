#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Research v0 - Coletor de Dados Multi-Fonte (Versão Melhorada)
Baseado no mini-research.md

Melhorias v0:
- Delay configurável (padrão 1s no completo)
- Exibição fluida e em tempo real
- Coleta de configurações no início (modo personalizado)
- Exibição completa de todos os dados coletados
"""

import os
import re
import string
import time
import warnings
import requests
import pandas as pd
from datetime import datetime
from itertools import product
from functools import lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from collections import defaultdict

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

def parse_list(s, default): 
    return [x.strip() for x in s.split(",") if x.strip()] if s else [default]

def print_section(title):
    print(cyan("\n" + "="*70))
    print(cyan(f"  {title}"))
    print(cyan("="*70 + "\n"))

def print_progress(message):
    """Exibe mensagem de progresso"""
    print(f"{blue('⏳')} {gray(message)}")

def print_success(message, count=None):
    """Exibe mensagem de sucesso"""
    if count:
        print(f"{green('✓')} {message} {green(f'({count} itens)')}")
    else:
        print(f"{green('✓')} {message}")

def print_info(message):
    """Exibe informação"""
    print(f"{cyan('ℹ')} {message}")

BASE_DIR = "dados"

# ======================================
# 📦 MÓDULO 1: GOOGLE SUGGEST
# ======================================

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"
REGIONS = ["br", "us", "fr", "de", "jp"]
CLIENTS = ["chrome", "firefox"]
SOURCES = {"web": "", "youtube": "yt", "news": "n", "shopping": "sh"}

CATEGORIES = {
    3: ("Outros", [
        "o que ", "é ", "nao é", "faz", "nao faz", "como ", "por que ", "porque ",
        "onde ", "quando ", "quanto", "qual ", "de ", "para ", "com ", "sem ", "vs", "ou",
    ])
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

@lru_cache(maxsize=256)
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
    except Exception as e:
        return []

def run_suggest_completo(termo, output_dir, delay=1.0):
    """Executa Google Suggest com configurações máximas"""
    print_section(f"GOOGLE SUGGEST — {termo}")
    print_progress("Iniciando coleta de sugestões...")
    
    resultados = []
    total_consultas = 0
    
    # Configurações otimizadas para modo completo
    regions_limited = ["br", "us"]  # Reduzido para não demorar muito
    clients_limited = ["chrome"]  # Apenas chrome
    sources_limited = ["web", "youtube"]  # Principais fontes
    
    for region in regions_limited:
        for client in clients_limited:
            for source_name, source_code in SOURCES.items():
                if source_name not in sources_limited:
                    continue
                
                # Sugestões padrão
                sugs = get_suggestions(termo, region, client, source_code, "", 20)
                total_consultas += 1
                for s, r in sugs:
                    resultados.append({
                        "termo": termo,
                        "sugestao": s,
                        "relevancia": r,
                        "regiao": region,
                        "cliente": client,
                        "fonte": source_name,
                        "tipo": "padrao"
                    })
                time.sleep(delay)
                
                # Expansões limitadas
                for letter in string.ascii_lowercase[:5] + "0123456789":
                    q = f"{termo} {letter}"
                    sugs = get_suggestions(q, region, client, source_code, "", 10)
                    total_consultas += 1
                    for s, r in sugs:
                        resultados.append({
                            "termo": termo,
                            "sugestao": s,
                            "relevancia": r,
                            "regiao": region,
                            "cliente": client,
                            "fonte": source_name,
                            "tipo": f"expansao_{letter}"
                        })
                    time.sleep(delay * 0.5)  # Delay menor para expansões
                
                # Categorias limitadas
                for name, words in CATEGORIES.values():
                    for w in words[:3]:  # Apenas 3 primeiras palavras
                        q = f"{termo} {w}"
                        sugs = get_suggestions(q, region, client, source_code, "", 10)
                        total_consultas += 1
                        for s, r in sugs:
                            resultados.append({
                                "termo": termo,
                                "sugestao": s,
                                "relevancia": r,
                                "regiao": region,
                                "cliente": client,
                                "fonte": source_name,
                                "tipo": f"categoria_{w.strip()}"
                            })
                        time.sleep(delay * 0.5)
    
    print_progress(f"Coleta concluída: {total_consultas} consultas realizadas")
    
    # Salvar
    if resultados:
        df = pd.DataFrame(resultados)
        file = os.path.join(output_dir, f"suggest_{termo}_{now_tag()}.csv")
        df.to_csv(file, index=False, encoding="utf-8-sig")
        print_success(f"Salvo: {file}", len(resultados))
    
    return resultados

def run_suggest_personalizado(termo, output_dir, config, delay=1.0):
    """Executa Google Suggest com configuração personalizada"""
    print_section(f"GOOGLE SUGGEST — {termo}")
    print_progress("Iniciando coleta...")
    
    resultados = []
    total_consultas = 0
    
    region_list = config.get("regions", ["br"])
    client_list = config.get("clients", ["chrome"])
    source_list = config.get("sources", ["web"])
    opcao = config.get("opcao", "1")
    limit = config.get("limit", 10)
    
    for region in region_list:
        for client in client_list:
            for source_name in source_list:
                source_code = SOURCES.get(source_name, "")
                
                if opcao in ["1", "4"]:
                    sugs = get_suggestions(termo, region, client, source_code, "", limit)
                    total_consultas += 1
                    for s, r in sugs:
                        resultados.append({
                            "termo": termo,
                            "sugestao": s,
                            "relevancia": r,
                            "regiao": region,
                            "cliente": client,
                            "fonte": source_name,
                            "tipo": "padrao"
                        })
                    time.sleep(delay)
                
                if opcao in ["2", "4"]:
                    for letter in string.ascii_lowercase[:5] + "0123456789":
                        q = f"{termo} {letter}"
                        sugs = get_suggestions(q, region, client, source_code, "", limit)
                        total_consultas += 1
                        for s, r in sugs:
                            resultados.append({
                                "termo": termo,
                                "sugestao": s,
                                "relevancia": r,
                                "regiao": region,
                                "cliente": client,
                                "fonte": source_name,
                                "tipo": f"expansao_{letter}"
                            })
                        time.sleep(delay * 0.5)
                
                if opcao in ["3", "4"]:
                    for name, words in CATEGORIES.values():
                        for w in words[:5]:
                            q = f"{termo} {w}"
                            sugs = get_suggestions(q, region, client, source_code, "", limit)
                            total_consultas += 1
                            for s, r in sugs:
                                resultados.append({
                                    "termo": termo,
                                    "sugestao": s,
                                    "relevancia": r,
                                    "regiao": region,
                                    "cliente": client,
                                    "fonte": source_name,
                                    "tipo": f"categoria_{w.strip()}"
                                })
                            time.sleep(delay * 0.5)
    
    if resultados:
        df = pd.DataFrame(resultados)
        file = os.path.join(output_dir, f"suggest_{termo}_{now_tag()}.csv")
        df.to_csv(file, index=False, encoding="utf-8-sig")
        print_success(f"Salvo: {file}", len(resultados))
    
    return resultados

# ======================================
# 📦 MÓDULO 2: GOOGLE TRENDS
# ======================================

def save_results_trends(df, label, terms, output_dir):
    terms_tag = "_".join([t.replace(" ", "_") for t in terms])
    file = os.path.join(output_dir, f"{label}_{terms_tag}_{now_tag()}.csv")
    df.to_csv(file, index=False, encoding="utf-8-sig")
    return file

def run_trends_completo(termo, output_dir, delay=1.0):
    """Executa Google Trends com configurações máximas"""
    if not HAS_PYTRENDS:
        print(yellow("[!] pytrends não instalado. Pulando Google Trends."))
        return []
    
    print_section(f"GOOGLE TRENDS — {termo}")
    print_progress("Iniciando coleta de tendências...")
    
    OUTPUT_DIR = ensure_dir(os.path.join(output_dir, "trends"))
    pytrends = TrendReq(hl="pt-BR", tz=0)
    
    # Configurações otimizadas
    gtypes = ["", "youtube"]  # Web e YouTube apenas
    timeframe = "today 12-m"
    
    resultados = []
    arquivos_salvos = []
    
    for gtype in gtypes:
        tipo_nome = gtype or "web"
        print_progress(f"Processando {tipo_nome}...")
        
        try:
            pytrends.build_payload([termo], timeframe=timeframe, geo="BR", gprop=gtype)
        except Exception as e:
            print(red(f"  [ERRO] {e}"))
            continue
        
        # Top / Rising
        try:
            related = pytrends.related_queries()
            r = related.get(termo, {})
            
            if r and "top" in r and r["top"] is not None:
                df = r["top"].head(25).copy()
                file = save_results_trends(df, f"top_{tipo_nome}", [termo], OUTPUT_DIR)
                arquivos_salvos.append(file)
                resultados.append({"tipo": "top", "fonte": tipo_nome, "dados": df})
            
            if r and "rising" in r and r["rising"] is not None:
                df = r["rising"].head(25).copy()
                file = save_results_trends(df, f"rising_{tipo_nome}", [termo], OUTPUT_DIR)
                arquivos_salvos.append(file)
                resultados.append({"tipo": "rising", "fonte": tipo_nome, "dados": df})
        except Exception as e:
            pass
        
        # Regiões
        try:
            regioes = pytrends.interest_by_region(resolution="country", inc_low_vol=True)
            if not regioes.empty:
                serie = regioes[termo].sort_values(ascending=False).head(25)
                df = pd.DataFrame({"regiao": serie.index, "valor": serie.values})
                file = save_results_trends(df, f"regioes_{tipo_nome}", [termo], OUTPUT_DIR)
                arquivos_salvos.append(file)
                resultados.append({"tipo": "regioes", "fonte": tipo_nome, "dados": df})
        except Exception as e:
            pass
        
        # Tempo
        try:
            df_time = pytrends.interest_over_time()
            if not df_time.empty:
                df = pd.DataFrame({"data": df_time.index, "valor": df_time[termo].values})
                file = save_results_trends(df, f"tempo_{tipo_nome}", [termo], OUTPUT_DIR)
                arquivos_salvos.append(file)
                resultados.append({"tipo": "tempo", "fonte": tipo_nome, "dados": df})
        except Exception as e:
            pass
        
        time.sleep(delay)
    
    print_success(f"Google Trends concluído", len(arquivos_salvos))
    return resultados

def run_trends_personalizado(termo, output_dir, config, delay=1.0):
    """Executa Google Trends com configuração personalizada"""
    if not HAS_PYTRENDS:
        print(yellow("[!] pytrends não instalado."))
        return []
    
    print_section(f"GOOGLE TRENDS — {termo}")
    print_progress("Iniciando coleta...")
    
    region = config.get("region", "BR")
    lang = config.get("lang", "pt")
    gtypes = config.get("gtypes", [""])
    timeframe = config.get("timeframe", "today 12-m")
    topn = config.get("topn", 25)
    
    OUTPUT_DIR = ensure_dir(os.path.join(output_dir, "trends"))
    pytrends = TrendReq(hl=f"{lang}-{region}" if region else lang, tz=0)
    
    resultados = []
    arquivos_salvos = []
    
    tipos_map = {"": "web", "images": "images", "news": "news", "youtube": "youtube"}
    
    for gtype in gtypes:
        tipo_nome = tipos_map.get(gtype, "web")
        print_progress(f"Processando {tipo_nome}...")
        
        try:
            pytrends.build_payload([termo], timeframe=timeframe, geo=region, gprop=gtype)
        except Exception as e:
            continue
        
        try:
            related = pytrends.related_queries()
            r = related.get(termo, {})
            if r and "top" in r and r["top"] is not None:
                df = r["top"].head(topn).copy()
                file = save_results_trends(df, f"top_{tipo_nome}", [termo], OUTPUT_DIR)
                arquivos_salvos.append(file)
            if r and "rising" in r and r["rising"] is not None:
                df = r["rising"].head(topn).copy()
                file = save_results_trends(df, f"rising_{tipo_nome}", [termo], OUTPUT_DIR)
                arquivos_salvos.append(file)
        except:
            pass
        
        time.sleep(delay)
    
    print_success(f"Google Trends concluído", len(arquivos_salvos))
    return resultados

# ======================================
# 📦 MÓDULO 3: SERP
# ======================================

GOOGLE_API_KEY = ""
GOOGLE_CX = ""
BRAVE_API_KEY = ""
SERPAPI_KEY = ""

def coletar_duckduckgo(term, region="br", limite=10):
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

def coletar_google(term, region="br", lang="pt", limite=10):
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

def coletar_brave(term, region="br", limite=10):
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

def coletar_bing(term, region="br", limite=10):
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

def run_serp_completo(termo, output_dir, delay=1.0):
    """Executa SERP com todos os buscadores disponíveis"""
    print_section(f"SERP — {termo}")
    print_progress("Iniciando busca em múltiplos buscadores...")
    
    SERP_DIR = ensure_dir(os.path.join(output_dir, "serp"))
    resultados = []
    limite = 20
    
    # DuckDuckGo (sempre disponível)
    print_progress("Buscando no DuckDuckGo...")
    ddg_res = coletar_duckduckgo(termo, "br", limite)
    time.sleep(delay)
    
    # Google
    print_progress("Buscando no Google...")
    ggl_res = coletar_google(termo, "br", "pt", limite)
    time.sleep(delay)
    
    # Brave
    print_progress("Buscando no Brave...")
    brv_res = coletar_brave(termo, "br", limite)
    time.sleep(delay)
    
    # Bing
    print_progress("Buscando no Bing...")
    bing_res = coletar_bing(termo, "br", limite)
    time.sleep(delay)
    
    # Salvar resultados
    if ddg_res:
        df = pd.DataFrame(ddg_res)
        file = os.path.join(SERP_DIR, f"duckduckgo_{termo}.csv")
        df.to_csv(file, index=False, encoding="utf-8-sig")
        resultados.extend(ddg_res)
        print_success(f"DuckDuckGo: {file}", len(ddg_res))
    
    if ggl_res:
        df = pd.DataFrame(ggl_res)
        file = os.path.join(SERP_DIR, f"google_{termo}.csv")
        df.to_csv(file, index=False, encoding="utf-8-sig")
        resultados.extend(ggl_res)
        print_success(f"Google: {file}", len(ggl_res))
    else:
        print(yellow("  [!] Google não disponível (faltam API keys)"))
    
    if brv_res:
        df = pd.DataFrame(brv_res)
        file = os.path.join(SERP_DIR, f"brave_{termo}.csv")
        df.to_csv(file, index=False, encoding="utf-8-sig")
        resultados.extend(brv_res)
        print_success(f"Brave: {file}", len(brv_res))
    else:
        print(yellow("  [!] Brave não disponível (faltam API keys)"))
    
    if bing_res:
        df = pd.DataFrame(bing_res)
        file = os.path.join(SERP_DIR, f"bing_{termo}.csv")
        df.to_csv(file, index=False, encoding="utf-8-sig")
        resultados.extend(bing_res)
        print_success(f"Bing: {file}", len(bing_res))
    else:
        print(yellow("  [!] Bing não disponível (faltam API keys)"))
    
    # Consolidado
    if resultados:
        df = pd.DataFrame(resultados)
        file = os.path.join(SERP_DIR, f"serp_consolidado_{termo}.csv")
        df.to_csv(file, index=False, encoding="utf-8-sig")
        print_success(f"Consolidado: {file}", len(resultados))
    
    return resultados

def run_serp_personalizado(termo, output_dir, config, delay=1.0):
    """Executa SERP com configuração personalizada"""
    print_section(f"SERP — {termo}")
    print_progress("Iniciando busca...")
    
    region = config.get("region", "br")
    limite = config.get("limite", 20)
    buscadores = config.get("buscadores", [1])
    
    SERP_DIR = ensure_dir(os.path.join(output_dir, "serp"))
    resultados = []
    
    if 1 in buscadores or 5 in buscadores:
        print_progress("Buscando no DuckDuckGo...")
        ddg_res = coletar_duckduckgo(termo, region, limite)
        if ddg_res:
            df = pd.DataFrame(ddg_res)
            file = os.path.join(SERP_DIR, f"duckduckgo_{termo}.csv")
            df.to_csv(file, index=False, encoding="utf-8-sig")
            resultados.extend(ddg_res)
            print_success(f"DuckDuckGo: {file}", len(ddg_res))
        time.sleep(delay)
    
    if 2 in buscadores or 5 in buscadores:
        print_progress("Buscando no Google...")
        ggl_res = coletar_google(termo, region, "pt", limite)
        if ggl_res:
            df = pd.DataFrame(ggl_res)
            file = os.path.join(SERP_DIR, f"google_{termo}.csv")
            df.to_csv(file, index=False, encoding="utf-8-sig")
            resultados.extend(ggl_res)
            print_success(f"Google: {file}", len(ggl_res))
        time.sleep(delay)
    
    if 3 in buscadores or 5 in buscadores:
        print_progress("Buscando no Brave...")
        brv_res = coletar_brave(termo, region, limite)
        if brv_res:
            df = pd.DataFrame(brv_res)
            file = os.path.join(SERP_DIR, f"brave_{termo}.csv")
            df.to_csv(file, index=False, encoding="utf-8-sig")
            resultados.extend(brv_res)
            print_success(f"Brave: {file}", len(brv_res))
        time.sleep(delay)
    
    if 4 in buscadores or 5 in buscadores:
        print_progress("Buscando no Bing...")
        bing_res = coletar_bing(termo, region, limite)
        if bing_res:
            df = pd.DataFrame(bing_res)
            file = os.path.join(SERP_DIR, f"bing_{termo}.csv")
            df.to_csv(file, index=False, encoding="utf-8-sig")
            resultados.extend(bing_res)
            print_success(f"Bing: {file}", len(bing_res))
        time.sleep(delay)
    
    if resultados:
        df = pd.DataFrame(resultados)
        file = os.path.join(SERP_DIR, f"serp_consolidado_{termo}.csv")
        df.to_csv(file, index=False, encoding="utf-8-sig")
        print_success(f"Consolidado: {file}", len(resultados))
    
    return resultados

# ======================================
# 📦 MÓDULO 4: YOUTUBE
# ======================================

YOUTUBE_API_KEY = ""

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

def run_youtube_completo(termo, output_dir, delay=1.0):
    """Executa YouTube com configurações máximas"""
    print_section(f"YOUTUBE — {termo}")
    print_progress("Buscando vídeos...")
    
    YOUTUBE_DIR = ensure_dir(os.path.join(output_dir, "youtube"))
    
    videos = buscar_videos(termo, "br", "pt", "relevance", 15)
    time.sleep(delay)
    
    if not videos:
        print(yellow("  [!] Nenhum vídeo encontrado"))
        return []
    
    print_success(f"Vídeos encontrados", len(videos))
    
    # Salvar vídeos
    df_videos = pd.DataFrame(videos)
    file = os.path.join(YOUTUBE_DIR, f"videos_{termo}.csv")
    df_videos.to_csv(file, index=False, encoding="utf-8-sig")
    print_success(f"Salvo: {file}", len(videos))
    
    # Comentários dos top 3 vídeos
    print_progress("Coletando comentários dos top 3 vídeos...")
    comentarios_todos = []
    
    for i, vid in enumerate(videos[:3], 1):
        print_progress(f"  Vídeo {i}/3: {vid['titulo'][:50]}...")
        comentarios = buscar_comentarios(vid["videoId"], 15)
        if comentarios:
            for c in comentarios:
                c["video_id"] = vid["videoId"]
                c["video_titulo"] = vid["titulo"]
            comentarios_todos.extend(comentarios)
        time.sleep(delay)
    
    if comentarios_todos:
        df_comentarios = pd.DataFrame(comentarios_todos)
        file = os.path.join(YOUTUBE_DIR, f"comentarios_{termo}.csv")
        df_comentarios.to_csv(file, index=False, encoding="utf-8-sig")
        print_success(f"Comentários salvos: {file}", len(comentarios_todos))
    
    return {"videos": videos, "comentarios": comentarios_todos}

def run_youtube_personalizado(termo, output_dir, config, delay=1.0):
    """Executa YouTube com configuração personalizada"""
    print_section(f"YOUTUBE — {termo}")
    print_progress("Buscando vídeos...")
    
    region = config.get("region", "br")
    lang = config.get("lang", "pt")
    order = config.get("order", "relevance")
    limite_videos = config.get("limite_videos", 10)
    coletar_comentarios = config.get("coletar_comentarios", False)
    limite_comentarios = config.get("limite_comentarios", 10)
    videos_selecionados = config.get("videos_selecionados", [1])
    
    YOUTUBE_DIR = ensure_dir(os.path.join(output_dir, "youtube"))
    
    videos = buscar_videos(termo, region, lang, order, limite_videos)
    time.sleep(delay)
    
    if not videos:
        print(yellow("  [!] Nenhum vídeo encontrado"))
        return []
    
    print_success(f"Vídeos encontrados", len(videos))
    
    df_videos = pd.DataFrame(videos)
    file = os.path.join(YOUTUBE_DIR, f"videos_{termo}.csv")
    df_videos.to_csv(file, index=False, encoding="utf-8-sig")
    print_success(f"Salvo: {file}", len(videos))
    
    comentarios_todos = []
    if coletar_comentarios:
        print_progress("Coletando comentários...")
        if videos_selecionados == "t":
            indices_list = range(1, len(videos) + 1)
        else:
            indices_list = videos_selecionados
        
        for i in indices_list:
            if i <= len(videos):
                vid = videos[i - 1]
                print_progress(f"  Vídeo {i}: {vid['titulo'][:50]}...")
                comentarios = buscar_comentarios(vid["videoId"], limite_comentarios)
                if comentarios:
                    for c in comentarios:
                        c["video_id"] = vid["videoId"]
                        c["video_titulo"] = vid["titulo"]
                    comentarios_todos.extend(comentarios)
                time.sleep(delay)
        
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

def run_stores_completo(termo, output_dir, delay=1.0):
    """Executa App Stores com configurações máximas"""
    if not HAS_PLAY_SCRAPER:
        print(yellow("[!] google-play-scraper não instalado. Pulando App Stores."))
        return []
    
    print_section(f"APP STORES — {termo}")
    print_progress("Buscando apps...")
    
    STORES_DIR = ensure_dir(os.path.join(output_dir, "stores"))
    
    # Google Play
    print_progress("Buscando no Google Play...")
    df_google = fetch_google(termo, "pt", "br", 15)
    time.sleep(delay)
    
    if not df_google.empty:
        print_success(f"Google Play: {len(df_google)} apps encontrados")
        file = os.path.join(STORES_DIR, f"apps_google_{termo}.csv")
        df_google.to_csv(file, index=False, encoding="utf-8-sig")
        print_success(f"Salvo: {file}", len(df_google))
        
        # Reviews dos top 2 apps
        print_progress("Coletando reviews dos top 2 apps do Google Play...")
        for app_id in df_google["id"].head(2).dropna():
            app_title = df_google.loc[df_google["id"] == app_id, "title"].iloc[0]
            print_progress(f"  {app_title}...")
            df_reviews = fetch_reviews_google(app_id, "pt", "br", 50)
            if not df_reviews.empty:
                file = os.path.join(STORES_DIR, f"reviews_google_{app_id}.csv")
                df_reviews.to_csv(file, index=False, encoding="utf-8-sig")
                print_success(f"  Reviews: {file}", len(df_reviews))
            time.sleep(delay)
    
    # App Store
    print_progress("Buscando na App Store...")
    df_apple = apple_df(fetch_apple(termo, "br", 15))
    time.sleep(delay)
    
    if not df_apple.empty:
        print_success(f"App Store: {len(df_apple)} apps encontrados")
        file = os.path.join(STORES_DIR, f"apps_apple_{termo}.csv")
        df_apple.to_csv(file, index=False, encoding="utf-8-sig")
        print_success(f"Salvo: {file}", len(df_apple))
        
        # Reviews dos top 2 apps
        print_progress("Coletando reviews dos top 2 apps da App Store...")
        for app_id in df_apple["id"].head(2).dropna():
            app_title = df_apple.loc[df_apple["id"] == app_id, "title"].iloc[0]
            print_progress(f"  {app_title}...")
            df_reviews = fetch_reviews_apple(app_id, "br", 50)
            if not df_reviews.empty:
                file = os.path.join(STORES_DIR, f"reviews_apple_{app_id}.csv")
                df_reviews.to_csv(file, index=False, encoding="utf-8-sig")
                print_success(f"  Reviews: {file}", len(df_reviews))
            time.sleep(delay)
    
    return {"google": df_google, "apple": df_apple}

def run_stores_personalizado(termo, output_dir, config, delay=1.0):
    """Executa App Stores com configuração personalizada"""
    if not HAS_PLAY_SCRAPER:
        print(yellow("[!] google-play-scraper não instalado."))
        return []
    
    print_section(f"APP STORES — {termo}")
    print_progress("Buscando apps...")
    
    country = config.get("country", "br")
    lang = config.get("lang", "pt")
    n_apps = config.get("n_apps", 20)
    lojas = config.get("lojas", 3)
    max_reviews = config.get("max_reviews", 100)
    coletar_reviews = config.get("coletar_reviews", True)
    apps_selecionados = config.get("apps_selecionados", "todos")
    
    STORES_DIR = ensure_dir(os.path.join(output_dir, "stores"))
    
    if lojas in (1, 3):
        print_progress("Buscando no Google Play...")
        df_google = fetch_google(termo, lang, country, n_apps)
        time.sleep(delay)
        
        if not df_google.empty:
            print_success(f"Google Play: {len(df_google)} apps encontrados")
            file = os.path.join(STORES_DIR, f"apps_google_{termo}.csv")
            df_google.to_csv(file, index=False, encoding="utf-8-sig")
            
            if coletar_reviews:
                print_progress("Coletando reviews do Google Play...")
                apps_ids = df_google["id"].dropna() if apps_selecionados == "todos" else df_google["id"].head(3).dropna()
                for app_id in apps_ids:
                    app_title = df_google.loc[df_google["id"] == app_id, "title"].iloc[0]
                    print_progress(f"  {app_title}...")
                    df_reviews = fetch_reviews_google(app_id, lang, country, max_reviews)
                    if not df_reviews.empty:
                        file = os.path.join(STORES_DIR, f"reviews_google_{app_id}.csv")
                        df_reviews.to_csv(file, index=False, encoding="utf-8-sig")
                        print_success(f"  Reviews: {file}", len(df_reviews))
                    time.sleep(delay)
    
    if lojas in (2, 3):
        print_progress("Buscando na App Store...")
        df_apple = apple_df(fetch_apple(termo, country, n_apps))
        time.sleep(delay)
        
        if not df_apple.empty:
            print_success(f"App Store: {len(df_apple)} apps encontrados")
            file = os.path.join(STORES_DIR, f"apps_apple_{termo}.csv")
            df_apple.to_csv(file, index=False, encoding="utf-8-sig")
            
            if coletar_reviews:
                print_progress("Coletando reviews da App Store...")
                apps_ids = df_apple["id"].dropna() if apps_selecionados == "todos" else df_apple["id"].head(3).dropna()
                for app_id in apps_ids:
                    app_title = df_apple.loc[df_apple["id"] == app_id, "title"].iloc[0]
                    print_progress(f"  {app_title}...")
                    df_reviews = fetch_reviews_apple(app_id, country, max_reviews)
                    if not df_reviews.empty:
                        file = os.path.join(STORES_DIR, f"reviews_apple_{app_id}.csv")
                        df_reviews.to_csv(file, index=False, encoding="utf-8-sig")
                        print_success(f"  Reviews: {file}", len(df_reviews))
                    time.sleep(delay)
    
    return []

# ======================================
# 📊 EXIBIÇÃO DE RESULTADOS
# ======================================

def exibir_resultados(resultados, termo):
    """Exibe todos os dados coletados de forma organizada"""
    print_section(f"RESULTADOS COLETADOS — {termo.upper()}")
    
    # Google Suggest
    if "suggest" in resultados and resultados["suggest"]:
        print(cyan("\n📋 GOOGLE SUGGEST"))
        print("-" * 70)
        sugestoes = resultados["suggest"]
        print(green(f"Total de sugestões: {len(sugestoes)}"))
        print("\nTop 20 sugestões mais relevantes:")
        df_sug = pd.DataFrame(sugestoes)
        df_sug_sorted = df_sug.sort_values("relevancia", ascending=False).head(20)
        for i, row in enumerate(df_sug_sorted.itertuples(), 1):
            print(f"  {i:2d}. {row.sugestao} {gray(f'(relevância: {row.relevancia})')}")
    
    # Google Trends
    if "trends" in resultados and resultados["trends"]:
        print(cyan("\n📈 GOOGLE TRENDS"))
        print("-" * 70)
        for item in resultados["trends"]:
            if isinstance(item, dict) and "dados" in item:
                df = item["dados"]
                tipo = item.get("tipo", "")
                fonte = item.get("fonte", "")
                print(green(f"\n{tipo.upper()} - {fonte}: {len(df)} itens"))
                if not df.empty and len(df) > 0:
                    for i, row in enumerate(df.head(10).itertuples(), 1):
                        if hasattr(row, 'query'):
                            print(f"  {i:2d}. {row.query} {gray(f'({row.value})')}")
                        elif hasattr(row, 'regiao'):
                            print(f"  {i:2d}. {row.regiao} {gray(f'({row.valor})')}")
    
    # SERP
    if "serp" in resultados and resultados["serp"]:
        print(cyan("\n🔍 SERP (RESULTADOS DE BUSCA)"))
        print("-" * 70)
        serp_results = resultados["serp"]
        print(green(f"Total de resultados: {len(serp_results)}"))
        print("\nTop 15 resultados:")
        df_serp = pd.DataFrame(serp_results)
        for i, row in enumerate(df_serp.head(15).itertuples(), 1):
            engine = getattr(row, 'engine', 'unknown')
            rank_str = f"[{engine.upper()}]"
            print(f"  {i:2d}. {green(rank_str)} {row.title}")
            print(f"      {gray(row.link)}")
    
    # YouTube
    if "youtube" in resultados and resultados["youtube"]:
        print(cyan("\n📺 YOUTUBE"))
        print("-" * 70)
        yt_data = resultados["youtube"]
        if isinstance(yt_data, dict):
            videos = yt_data.get("videos", [])
            comentarios = yt_data.get("comentarios", [])
            
            if videos:
                print(green(f"\nVídeos encontrados: {len(videos)}"))
                print("\nTop 10 vídeos:")
                for i, v in enumerate(videos[:10], 1):
                    print(f"  {i:2d}. {v['titulo']}")
                    print(f"      Canal: {v.get('canal', 'N/A')} | Link: {gray(v['link'])}")
            
            if comentarios:
                print(green(f"\nComentários coletados: {len(comentarios)}"))
                print("\nTop 10 comentários:")
                df_com = pd.DataFrame(comentarios)
                for i, row in enumerate(df_com.head(10).itertuples(), 1):
                    autor = getattr(row, 'autor', 'N/A')
                    comentario = getattr(row, 'comentario', '')[:100]
                    likes = getattr(row, 'likes', 0)
                    print(f"  {i:2d}. {autor}: {comentario}... {gray(f'({likes} likes)')}")
    
    # App Stores
    if "stores" in resultados and resultados["stores"]:
        print(cyan("\n📱 APP STORES"))
        print("-" * 70)
        stores_data = resultados["stores"]
        if isinstance(stores_data, dict):
            df_google = stores_data.get("google", pd.DataFrame())
            df_apple = stores_data.get("apple", pd.DataFrame())
            
            if not df_google.empty:
                print(green(f"\nGoogle Play: {len(df_google)} apps"))
                print("\nTop 10 apps:")
                for i, row in enumerate(df_google.head(10).itertuples(), 1):
                    print(f"  {i:2d}. {row.title} | ⭐ {row.rating or 's/d'} | {row.developer}")
            
            if not df_apple.empty:
                print(green(f"\nApp Store: {len(df_apple)} apps"))
                print("\nTop 10 apps:")
                for i, row in enumerate(df_apple.head(10).itertuples(), 1):
                    print(f"  {i:2d}. {row.title} | ⭐ {row.rating or 's/d'} | {row.developer}")
    
    print(cyan("\n" + "="*70 + "\n"))

# ======================================
# 🚀 FUNÇÕES PRINCIPAIS
# ======================================

def coletar_configuracao_personalizada(termo):
    """Coleta todas as configurações do modo personalizado no início"""
    print(cyan("\n" + "="*70))
    print(cyan("  CONFIGURAÇÃO PERSONALIZADA"))
    print(cyan("="*70))
    
    config = {"termo": termo}
    
    # Delay
    delay_input = input("\n> Delay entre requisições em segundos [1.0]: ").strip()
    config["delay"] = float(delay_input) if delay_input else 1.0
    
    # Fontes
    print("\n> Selecione as fontes de dados:")
    print(f"  {green('1')}. Google Suggest")
    print(f"  {green('2')}. Google Trends")
    print(f"  {green('3')}. SERP (Buscadores)")
    print(f"  {green('4')}. YouTube")
    print(f"  {green('5')}. App Stores")
    print(f"  {green('6')}. Todas")
    
    escolha_fontes = input("\n> Selecione (separado por vírgula) [6]: ").strip() or "6"
    fontes = [int(x) for x in escolha_fontes.split(",") if x.isdigit()] if escolha_fontes != "6" else [1, 2, 3, 4, 5]
    config["fontes"] = fontes
    
    # Google Suggest
    if 1 in fontes:
        print(cyan("\n--- Google Suggest ---"))
        region_in = input("> Regiões (br,us,fr,de,jp) [br]: ").strip() or "br"
        config["suggest"] = {
            "regions": parse_list(region_in, "br"),
            "clients": parse_list(input("> Clientes (chrome,firefox) [chrome]: ").strip() or "chrome", "chrome"),
            "sources": parse_list(input("> Fontes (web,youtube,news,shopping) [web]: ").strip() or "web", "web"),
            "opcao": input("> Opções (1=padrão,2=expansões,3=categorias,4=tudo) [1]: ").strip() or "1",
            "limit": int(input("> Limite por consulta [10]: ").strip() or 10)
        }
    
    # Google Trends
    if 2 in fontes:
        print(cyan("\n--- Google Trends ---"))
        config["trends"] = {
            "region": input("> Região [BR]: ").strip().upper() or "BR",
            "lang": input("> Idioma [pt]: ").strip() or "pt",
            "gtypes": [{"": "", "images": "images", "news": "news", "youtube": "youtube"}.get(input("> Tipo (web,images,news,youtube) [web]: ").strip() or "web", "")],
            "timeframe": {"1": "now 7-d", "2": "today 1-m", "3": "today 3-m", "4": "today 12-m", "5": "today 5-y", "6": "all"}.get(input("> Período (1-6) [4]: ").strip() or "4", "today 12-m"),
            "topn": int(input("> Resultados [25]: ").strip() or 25)
        }
    
    # SERP
    if 3 in fontes:
        print(cyan("\n--- SERP ---"))
        config["serp"] = {
            "region": input("> Região [br]: ").strip().lower() or "br",
            "limite": int(input("> Resultados por buscador [20]: ").strip() or 20),
            "buscadores": [int(x) for x in input("> Buscadores (1=DDG,2=Google,3=Brave,4=Bing,5=todos) [1]: ").strip().split(",") if x.isdigit()] or [1]
        }
    
    # YouTube
    if 4 in fontes:
        print(cyan("\n--- YouTube ---"))
        coletar_comentarios = input("> Coletar comentários? (s/n) [n]: ").strip().lower() == "s"
        config["youtube"] = {
            "region": input("> Região [br]: ").strip().lower() or "br",
            "lang": input("> Idioma [pt]: ").strip().lower() or "pt",
            "order": input("> Ordenar por (relevance,date,viewCount) [relevance]: ").strip() or "relevance",
            "limite_videos": int(input("> Quantos vídeos? [10]: ").strip() or 10),
            "coletar_comentarios": coletar_comentarios,
            "limite_comentarios": int(input("> Comentários por vídeo [10]: ").strip() or 10) if coletar_comentarios else 0,
            "videos_selecionados": []
        }
        if coletar_comentarios:
            videos_sel = input("> Quais vídeos? (1,2,3 ou 't' para todos) [1]: ").strip() or "1"
            config["youtube"]["videos_selecionados"] = [int(x) for x in videos_sel.split(",") if x.isdigit()] if videos_sel != "t" else "t"
        else:
            config["youtube"]["videos_selecionados"] = [1]
    
    # App Stores
    if 5 in fontes:
        print(cyan("\n--- App Stores ---"))
        config["stores"] = {
            "country": input("> Região (br, us, es, fr, jp) [br]: ").strip() or "br",
            "lang": input("> Idioma (pt, en, es, fr, ja) [pt]: ").strip() or "pt",
            "n_apps": int(input("> Quantidade de apps [20]: ").strip() or 20),
            "lojas": int(input("> Loja (1=Google, 2=Apple, 3=Ambas) [3]: ").strip() or 3),
            "max_reviews": int(input("> Comentários por app [100]: ").strip() or 100),
            "coletar_reviews": input("> Coletar reviews? (s/n) [s]: ").strip().lower() != "n",
            "apps_selecionados": input("> Apps para reviews (todos ou número) [todos]: ").strip() or "todos"
        }
    
    return config

def modo_completo(termo, delay=1.0):
    """Executa coleta completa de todas as fontes"""
    print(cyan("\n" + "="*70))
    print(cyan(f"  MODO COMPLETO — {termo.upper()}"))
    print(cyan("="*70))
    print(yellow(f"\n[!] Delay padrão: {delay}s entre requisições"))
    print(yellow("[!] Este modo coletará o máximo de dados possível de todas as fontes."))
    print(yellow("[!] Pode levar vários minutos para completar.\n"))
    
    output_dir = ensure_dir(os.path.join(BASE_DIR, f"coleta_completa_{termo}_{now_tag()}"))
    
    resultados = {}
    
    # 1. Google Suggest
    try:
        resultados["suggest"] = run_suggest_completo(termo, output_dir, delay)
    except Exception as e:
        print(red(f"[ERRO] Google Suggest: {e}"))
        resultados["suggest"] = []
    
    # 2. Google Trends
    try:
        resultados["trends"] = run_trends_completo(termo, output_dir, delay)
    except Exception as e:
        print(red(f"[ERRO] Google Trends: {e}"))
        resultados["trends"] = []
    
    # 3. SERP
    try:
        resultados["serp"] = run_serp_completo(termo, output_dir, delay)
    except Exception as e:
        print(red(f"[ERRO] SERP: {e}"))
        resultados["serp"] = []
    
    # 4. YouTube
    try:
        resultados["youtube"] = run_youtube_completo(termo, output_dir, delay)
    except Exception as e:
        print(red(f"[ERRO] YouTube: {e}"))
        resultados["youtube"] = []
    
    # 5. App Stores
    try:
        resultados["stores"] = run_stores_completo(termo, output_dir, delay)
    except Exception as e:
        print(red(f"[ERRO] App Stores: {e}"))
        resultados["stores"] = []
    
    # Exibir resultados
    time.sleep(0.5)  # Pequeno delay antes de exibir
    exibir_resultados(resultados, termo)
    
    print(cyan("="*70))
    print(cyan("  COLETA COMPLETA FINALIZADA"))
    print(cyan("="*70))
    print(green(f"\n[✓] Todos os dados salvos em: {output_dir}\n"))
    
    return resultados

def modo_personalizado(termo, config):
    """Executa coleta com configuração personalizada"""
    print(cyan("\n" + "="*70))
    print(cyan(f"  MODO PERSONALIZADO — {termo.upper()}"))
    print(cyan("="*70))
    print(green("\n[✓] Configurações coletadas. Iniciando coleta...\n"))
    
    output_dir = ensure_dir(os.path.join(BASE_DIR, f"coleta_personalizada_{termo}_{now_tag()}"))
    delay = config.get("delay", 1.0)
    
    resultados = {}
    fontes = config.get("fontes", [1, 2, 3, 4, 5])
    
    if 1 in fontes:
        try:
            resultados["suggest"] = run_suggest_personalizado(termo, output_dir, config.get("suggest", {}), delay)
        except Exception as e:
            print(red(f"[ERRO] Google Suggest: {e}"))
            resultados["suggest"] = []
    
    if 2 in fontes:
        try:
            resultados["trends"] = run_trends_personalizado(termo, output_dir, config.get("trends", {}), delay)
        except Exception as e:
            print(red(f"[ERRO] Google Trends: {e}"))
            resultados["trends"] = []
    
    if 3 in fontes:
        try:
            resultados["serp"] = run_serp_personalizado(termo, output_dir, config.get("serp", {}), delay)
        except Exception as e:
            print(red(f"[ERRO] SERP: {e}"))
            resultados["serp"] = []
    
    if 4 in fontes:
        try:
            resultados["youtube"] = run_youtube_personalizado(termo, output_dir, config.get("youtube", {}), delay)
        except Exception as e:
            print(red(f"[ERRO] YouTube: {e}"))
            resultados["youtube"] = []
    
    if 5 in fontes:
        try:
            resultados["stores"] = run_stores_personalizado(termo, output_dir, config.get("stores", {}), delay)
        except Exception as e:
            print(red(f"[ERRO] App Stores: {e}"))
            resultados["stores"] = []
    
    # Exibir resultados
    time.sleep(0.5)
    exibir_resultados(resultados, termo)
    
    print(cyan("="*70))
    print(cyan("  COLETA PERSONALIZADA FINALIZADA"))
    print(cyan("="*70))
    print(green(f"\n[✓] Dados salvos em: {output_dir}\n"))
    
    return resultados

def main():
    print(cyan("\n" + "="*70))
    print(cyan("  MINI RESEARCH v0 - COLETOR DE DADOS MULTI-FONTE"))
    print(cyan("="*70))
    
    # Solicitar termo
    termo = input("\n> Digite o termo de busca: ").strip()
    if not termo:
        print(red("Termo não pode estar vazio!"))
        return
    
    if check_exit(termo):
        print(yellow("\nEncerrado.\n"))
        return
    
    # Selecionar modo
    print("\n> Selecione o modo de pesquisa:")
    print(f"  {green('1')}. Modo Completo (coleta máxima de todas as fontes)")
    print(f"  {green('2')}. Modo Personalizado (configure cada aspecto)")
    
    modo = input("\n> Selecione [1]: ").strip() or "1"
    
    if modo == "1":
        delay = input("\n> Delay entre requisições em segundos [1.0]: ").strip()
        delay = float(delay) if delay else 1.0
        modo_completo(termo, delay)
    elif modo == "2":
        config = coletar_configuracao_personalizada(termo)
        modo_personalizado(termo, config)
    else:
        print(red("Opção inválida!"))

if __name__ == "__main__":
    main()




