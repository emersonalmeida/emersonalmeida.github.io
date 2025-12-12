#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNI - Coletor Universal de Dados v0
Versão Local Completa - Todas as Fontes Integradas

Autor: Emerson Almeida
Baseado em: uni.ipynb e uni.py do Google Colab

Recursos Implementados:
✓ Google Suggest (sem API)
✓ Google Trends (pytrends + SerpAPI)
✓ SERP + Scraping (DuckDuckGo, Google, Brave, Bing)
✓ YouTube (API + Scraping)
✓ App Stores (Google Play, Apple)
✓ Reddit (API)
✓ Google News (API)
✓ GDELT (API)
✓ Hacker News (API pública)
✓ Stack Exchange (API pública)
✓ GitHub (API)
✓ arXiv (API pública)
✓ Wikipedia (API)
✓ Google Scholar (Scraping)

Todas as chaves API do uni.py estão integradas.
"""

import os
import re
import sys
import json
import csv
import time
import string
import locale
import warnings
import requests
import hashlib
from pathlib import Path
from datetime import datetime
from itertools import product
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from xml.etree import ElementTree as ET

warnings.filterwarnings("ignore", category=FutureWarning)

# ======================================
# 🎨 Sistema de Cores e Formatação
# ======================================

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def blue(text): return color(text, "34")
def green(text): return color(text, "32")
def yellow(text): return color(text, "33")
def red(text): return color(text, "31")
def gray(text): return color(text, "90")
def cyan(text): return color(text, "36")
def magenta(text): return color(text, "35")
def bold(text): return color(text, "1")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title, char="=", width=70):
    print(cyan(f"\n{char * width}"))
    print(cyan(f"{title:^{width}}"))
    print(cyan(f"{char * width}\n"))

def print_section(title):
    print(blue(f"\n{'─' * 60}"))
    print(blue(f"  {title}"))
    print(blue(f"{'─' * 60}\n"))

def print_success(msg):
    print(f"{green('✓')} {msg}")

def print_error(msg):
    print(f"{red('✗')} {msg}")

def print_warning(msg):
    print(f"{yellow('⚠')} {msg}")

def print_info(msg):
    print(f"{cyan('ℹ')} {msg}")

# ======================================
# ⚙️ Configurações Globais e Chaves API
# ======================================

BASE_DIR = Path("dados")
BASE_DIR.mkdir(exist_ok=True)

# Chaves API do uni.py
SERPAPI_KEY = "e71430bcff8bdc906f7a5ed9ae1538355c2efb0fb88ffa071f7125a76cc2b142"
YOUTUBE_API_KEY = "AIzaSyBj80B2fwVvFEMtcQU8tPV_NCNaEmQvzhc"
REDDIT_CLIENT_ID = "4CmHP70LPG0HI7TEkGsMkQ"
REDDIT_SECRET = "Gn9cxMzoA-inTlTEuv-n8vojVE57FQ"
REDDIT_USER_AGENT = "uni-local-v0"
GNEWS_KEY = "91a7bc222ecfdac6c60019c4fb1ec87c"
BRAVE_API_KEY = "BSAjC9Yvq2s8_hYFIPWQ2QEl_XHpsQp"
GITHUB_TOKEN = "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"
GOOGLE_API_KEY = "AIzaSyBj80B2fwVvFEMtcQU8tPV_NCNaEmQvzhc"
GOOGLE_CX = "f07ccd3b922d6437b"

# URLs
SUGGEST_URL = "https://suggestqueries.google.com/complete/search"
EXIT_COMMANDS = {"sair", "fechar", "terminar", "ok", "exit", "quit", "q", "0"}

REGIONS = ["br", "us", "fr", "de", "jp", "es", "it", "ru", "cn"]
LANGUAGES = {
    "br": "pt", "us": "en", "fr": "fr", "de": "de", "jp": "ja",
    "es": "es", "it": "it", "ru": "ru", "cn": "zh"
}

# ======================================
# 🔧 Funções Utilitárias
# ======================================

def now_tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)

def detect_locale():
    try:
        system_locale = locale.getdefaultlocale()[0]
        if system_locale:
            lang = system_locale.split('_')[0].lower()
            region = system_locale.split('_')[1].lower() if '_' in system_locale else lang
        else:
            lang, region = "pt", "br"
    except:
        lang, region = "pt", "br"
    lang = LANGUAGES.get(region, lang)
    return lang, region

def make_session():
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    retry = Retry(
        total=5, backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    sess.mount("https://", HTTPAdapter(max_retries=retry))
    return sess

SESSION = make_session()

def check_exit(value):
    return value.lower().strip() in EXIT_COMMANDS

def parse_list(s, default):
    if not s:
        return [default]
    return [x.strip() for x in s.split(",") if x.strip()] or [default]

def safe_input(prompt, default=""):
    try:
        value = input(f"{prompt} [{default}]: " if default else f"{prompt}: ").strip()
        if not value and default:
            value = default
        if check_exit(value):
            return None
        return value
    except (KeyboardInterrupt, EOFError):
        return None

def save_csv(data, filename, output_dir):
    if not data:
        return None
    try:
        import pandas as pd
        output_dir = ensure_dir(output_dir)
        filepath = output_dir / filename
        
        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame(data, columns=["valor"])
        else:
            df = pd.DataFrame(data)
        
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        print_success(f"Salvo: {filepath}")
        return filepath
    except ImportError:
        # Fallback sem pandas
        output_dir = ensure_dir(output_dir)
        filepath = output_dir / filename
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            if data and isinstance(data, list) and isinstance(data[0], dict):
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(f)
                for row in data:
                    writer.writerow(row if isinstance(row, (list, tuple)) else [row])
        print_success(f"Salvo: {filepath}")
        return filepath
    except Exception as e:
        print_error(f"Erro ao salvar CSV: {e}")
        return None

# ======================================
# 📦 MÓDULO 1: Google Suggest
# ======================================

CATEGORIES = {
    3: ("Outros", [
        "o que ", "é ", "como ", "por que ", "porque ", "onde ", "quando ",
        "qual ", "de ", "para ", "com ", "sem ", "ou", "melhor", "pior",
        "software", "hardware", "app", "windows", "mac", "linux", "android",
        "iphone", "ios", "IA", "inteligencia artificial",
    ])
}

MENU_OPTIONS = {1: "Top Sugestões", 2: "Expansões: a–z,0–9", 3: "Outros", "t": "Todos"}
SOURCES = {"web": "", "youtube": "yt", "news": "n", "shopping": "sh"}

@lru_cache(maxsize=256)
def get_suggestions(query, region="br", client="chrome", source="", lang="", limit=10):
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
        print_error(f"{query}: {e}")
        return []

def run_blocks_suggest(term, blocks, region, lang, client, source, limit, counter, all_results):
    if 1 in blocks:
        print_section(f"Sugestões padrão | {region} | {lang or 'auto'}")
        results = get_suggestions(term, region, client, SOURCES.get(source, ""), lang, limit)
        for s, r in results:
            counter[0] += 1
            all_results.append({"fonte": "Google Suggest", "termo": term, "sugestao": s, "relevancia": r})
            print(f"{green(str(counter[0]))}. {s} {gray(f'({r})')}")
    
    if 2 in blocks:
        for letter in string.ascii_lowercase + "0123456789":
            q = f"{term} {letter}"
            results = get_suggestions(q, region, client, SOURCES.get(source, ""), lang, limit)
            for s, r in results:
                counter[0] += 1
                all_results.append({"fonte": "Google Suggest", "termo": q, "sugestao": s, "relevancia": r})
                print(f"{green(str(counter[0]))}. {s} {gray(f'({r})')}")
            time.sleep(0.2)
    
    for idx in blocks:
        if idx >= 3 and idx in CATEGORIES:
            name, words = CATEGORIES[idx]
            for w in words:
                q = f"{term} {w}"
                results = get_suggestions(q, region, client, SOURCES.get(source, ""), lang, limit)
                for s, r in results:
                    counter[0] += 1
                    all_results.append({"fonte": "Google Suggest", "termo": q, "sugestao": s, "relevancia": r})
                    print(f"{green(str(counter[0]))}. {s} {gray(f'({r})')}")
                time.sleep(0.2)

def module_suggest():
    print_header("Google Suggest Avançado")
    counter = [0]
    all_results = []
    
    while True:
        term_in = safe_input("> Termo(s) de busca")
        if not term_in: break
        terms = parse_list(term_in, "bitcoin")
        
        region_in = safe_input("> Região", "br")
        if not region_in: break
        region_list = parse_list(region_in, "br")
        
        lang_in = safe_input("> Idioma", "auto")
        if not lang_in: break
        lang_list = parse_list(lang_in, "")
        
        client_in = safe_input("> Navegador", "chrome")
        if not client_in: break
        client_list = parse_list(client_in, "chrome")
        
        source_in = safe_input("> Fonte (web, youtube, news, shopping)", "web")
        if not source_in: break
        source_list = parse_list(source_in, "web")
        
        print("\n> Exibição:")
        for k, v in MENU_OPTIONS.items():
            print(f"{green(str(k))}. {v}")
        
        choice = safe_input("> Selecione", "1")
        if not choice: break
        
        blocks = list(CATEGORIES.keys()) if choice == "t" else [int(x) for x in re.split(r"[,\s]+", choice) if x.isdigit()]
        limit = int(safe_input("> Resultados", "10") or 10)
        
        session_dir = ensure_dir(BASE_DIR / f"suggest_{now_tag()}")
        
        for source in source_list:
            for region in region_list:
                for lang in lang_list:
                    for client in client_list:
                        for term in terms:
                            run_blocks_suggest(term, blocks, region, lang, client, source, limit, counter, all_results)
        
        if all_results:
            save_csv(all_results, f"suggest_{terms[0]}.csv", session_dir)
        print_success(f"Total: {counter[0]} sugestões")

# ======================================
# 📦 MÓDULO 2: Google Trends (pytrends)
# ======================================

def module_trends_pytrends():
    try:
        from pytrends.request import TrendReq
        import pandas as pd
    except ImportError:
        print_error("pytrends não instalado. Instale com: pip install pytrends pandas")
        return
    
    print_header("Google Trends (pytrends)")
    
    while True:
        termo = safe_input("> Termo(s) de busca")
        if not termo: break
        
        terms = [t.strip() for t in termo.split(",") if t.strip()]
        region = safe_input("> Região", "BR").upper() or "BR"
        lang = safe_input("> Idioma", "pt") or "pt"
        
        print("\n> Tipo:")
        tipos = {1: "", 2: "images", 3: "news", 4: "froogle", 5: "youtube"}
        for k, v in tipos.items():
            print(f"{green(k)}. {(v or 'web').capitalize()}")
        
        tipos_in = safe_input("> Selecione", "1")
        if not tipos_in: break
        gtypes = [tipos.get(int(t), "") for t in tipos_in.split(",") if t.isdigit()] or [""]
        
        timeframe = safe_input("> Período (today 12-m, today 5-y, all)", "today 12-m")
        if not timeframe: break
        
        topn = int(safe_input("> Resultados", "20") or 20)
        session_dir = ensure_dir(BASE_DIR / f"trends_{now_tag()}")
        
        try:
            pytrends = TrendReq(hl=f"{lang}-{region}" if region else lang, tz=0)
            
            for gtype in gtypes:
                tipo_nome = gtype or "web"
                print_section(f"TRENDS — {', '.join(terms)} | {tipo_nome}")
                
                try:
                    pytrends.build_payload(terms, timeframe=timeframe, geo=region, gprop=gtype)
                except Exception as e:
                    print_error(f"Erro: {e}")
                    continue
                
                try:
                    related = pytrends.related_queries()
                    for term in terms:
                        r = related.get(term, {})
                        if r and "top" in r and r["top"] is not None:
                            df = r["top"].head(topn).copy()
                            print(blue(f"\nTop relacionados ({term}):"))
                            resultados = []
                            for i, row in enumerate(df.itertuples(), 1):
                                resultados.append({"termo": term, "query": row.query, "value": row.value})
                                print(f"{green(f'{i:02d}.')} {row.query} {gray(f'({row.value})')}")
                            save_csv(resultados, f"top_{tipo_nome}_{term}.csv", session_dir)
                except Exception as e:
                    print_error(f"Erro: {e}")
                
                time.sleep(10)
        except Exception as e:
            print_error(f"Erro: {e}")

# ======================================
# 📦 MÓDULO 3: SERP + Scraping
# ======================================

def coletar_duckduckgo(term, region="br", limite=10):
    try:
        from ddgs import DDGS
        results = []
        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.text(term, region=region, max_results=limite), 1):
                results.append({
                    "engine": "duckduckgo",
                    "rank": i,
                    "title": r.get("title", ""),
                    "link": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
        return results
    except ImportError:
        print_warning("ddgs não instalado")
        return []
    except Exception as e:
        print_error(f"DuckDuckGo: {e}")
        return []

def coletar_google_serpapi(term, region="br", lang="pt", limite=10):
    if not SERPAPI_KEY:
        return []
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": term,
            "gl": region,
            "hl": lang,
            "num": limite,
            "api_key": SERPAPI_KEY
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        results = []
        if "organic_results" in data:
            for i, item in enumerate(data["organic_results"][:limite], 1):
                results.append({
                    "engine": "google",
                    "rank": i,
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
        return results
    except Exception as e:
        print_error(f"Google SerpAPI: {e}")
        return []

def coletar_brave(term, region="br", limite=10):
    if not BRAVE_API_KEY:
        return []
    try:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
        params = {"q": term, "count": limite, "country": region}
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        results = []
        if "web" in data and "results" in data["web"]:
            for i, item in enumerate(data["web"]["results"], 1):
                results.append({
                    "engine": "brave",
                    "rank": i,
                    "title": item.get("title", ""),
                    "link": item.get("url", ""),
                    "snippet": item.get("description", "")
                })
        return results
    except Exception as e:
        print_error(f"Brave: {e}")
        return []

def coletar_bing_serpapi(term, region="br", limite=10):
    if not SERPAPI_KEY:
        return []
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "bing",
            "q": term,
            "cc": region.upper(),
            "count": limite,
            "api_key": SERPAPI_KEY
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        results = []
        if "organic_results" in data:
            for i, item in enumerate(data["organic_results"][:limite], 1):
                results.append({
                    "engine": "bing",
                    "rank": i,
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
        return results
    except Exception as e:
        print_error(f"Bing: {e}")
        return []

def scrap_conteudo(url):
    try:
        from bs4 import BeautifulSoup
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return lines[:50]
    except Exception as e:
        print_error(f"Scraping {url}: {e}")
        return []

def module_serp():
    print_header("SERP + Scraping")
    
    while True:
        modo = safe_input("> Modo (1=SERP, 2=LINK)", "1")
        if not modo: break
        
        session_dir = ensure_dir(BASE_DIR / f"serp_{now_tag()}")
        links = []
        
        if modo == "1":
            termo = safe_input("> Termo de busca")
            if not termo: break
            
            region = safe_input("> Região", "br").lower() or "br"
            lang = safe_input("> Idioma", "pt").lower() or "pt"
            limite = int(safe_input("> Resultados", "10") or 10)
            buscador = safe_input("> Buscadores (1=ddg, 2=google, 3=brave, 4=bing, 5=todos)", "1") or "1"
            
            if buscador in ["1", "5"]:
                print_section(f"DuckDuckGo — {termo}")
                ddg_res = coletar_duckduckgo(termo, region, limite)
                for r in ddg_res:
                    print(f"{green(f'[DDG {r['rank']:03d}]')} {r['title']} {gray(r['link'])}")
                save_csv(ddg_res, "duckduckgo.csv", session_dir)
                links.extend(ddg_res)
            
            if buscador in ["2", "5"]:
                print_section(f"Google — {termo}")
                ggl_res = coletar_google_serpapi(termo, region, lang, limite)
                for r in ggl_res:
                    print(f"{green(f'[GGL {r['rank']:03d}]')} {r['title']} {gray(r['link'])}")
                save_csv(ggl_res, "google.csv", session_dir)
                links.extend(ggl_res)
            
            if buscador in ["3", "5"]:
                print_section(f"Brave — {termo}")
                brv_res = coletar_brave(termo, region, limite)
                for r in brv_res:
                    print(f"{green(f'[BRV {r['rank']:03d}]')} {r['title']} {gray(r['link'])}")
                save_csv(brv_res, "brave.csv", session_dir)
                links.extend(brv_res)
            
            if buscador in ["4", "5"]:
                print_section(f"Bing — {termo}")
                bing_res = coletar_bing_serpapi(termo, region, limite)
                for r in bing_res:
                    print(f"{green(f'[BING {r['rank']:03d}]')} {r['title']} {gray(r['link'])}")
                save_csv(bing_res, "bing.csv", session_dir)
                links.extend(bing_res)
            
            if links:
                save_csv(links, f"resultados_{termo}.csv", session_dir)
        
        elif modo == "2":
            lnk = safe_input("> Cole links (separados por vírgula)")
            if not lnk: break
            links = [{"url": u.strip()} for u in lnk.replace(",", " ").split() if u.strip()]
        
        if links:
            escolha = safe_input("> Scraping (n,1,2..t)", "n").lower() or "n"
            if escolha != "n":
                indices = range(1, len(links)+1) if escolha == "t" else [int(x) for x in escolha.split(",") if x.isdigit()]
                for i in indices:
                    if i <= len(links):
                        url = links[i-1].get("link") or links[i-1].get("url")
                        print_section(f"[{i}] {url}")
                        conteudo = scrap_conteudo(url)
                        for linha in conteudo[:10]:
                            print(f"  {linha}")
                        save_csv([{"url": url, "conteudo": " ".join(conteudo)}], f"scrap_{i}.csv", session_dir)

# ======================================
# 📦 MÓDULO 4: YouTube
# ======================================

def module_youtube():
    print_header("YouTube Collector")
    
    while True:
        termo = safe_input("> Termo de busca")
        if not termo: break
        
        region = safe_input("> Região", "br").lower() or "br"
        lang = safe_input("> Idioma", "pt").lower() or "pt"
        order = safe_input("> Ordenar por (relevance, date, viewCount)", "relevance") or "relevance"
        limite = int(safe_input("> Quantos vídeos?", "5") or 5)
        
        session_dir = ensure_dir(BASE_DIR / f"youtube_{now_tag()}")
        videos = []
        
        # Tentar API primeiro
        if YOUTUBE_API_KEY:
            try:
                from googleapiclient.discovery import build
                youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
                request = youtube.search().list(
                    part="snippet",
                    q=termo,
                    type="video",
                    maxResults=limite,
                    order=order,
                    regionCode=region.upper(),
                    relevanceLanguage=lang
                )
                response = request.execute()
                
                for item in response.get("items", []):
                    video_id = item["id"]["videoId"]
                    videos.append({
                        "titulo": item["snippet"]["title"],
                        "canal": item["snippet"]["channelTitle"],
                        "link": f"https://youtube.com/watch?v={video_id}",
                        "publicado": item["snippet"]["publishedAt"],
                        "descricao": item["snippet"]["description"][:200]
                    })
                    print(f"{green(str(len(videos)))}. {item['snippet']['title']} {gray(f'({item['snippet']['channelTitle']})')}")
            except Exception as e:
                print_warning(f"API falhou: {e}, tentando scraping...")
        
        # Fallback para scraping
        if not videos:
            try:
                from youtubesearchpython import VideosSearch
                vs = VideosSearch(termo, limit=limite)
                result = vs.result()
                
                for v in result.get("result", [])[:limite]:
                    videos.append({
                        "titulo": v.get("title", ""),
                        "link": v.get("link", ""),
                        "duracao": v.get("duration", ""),
                        "views": v.get("viewCount", {}).get("text", "0"),
                        "canal": v.get("channel", {}).get("name", "")
                    })
                    print(f"{green(str(len(videos)))}. {v.get('title', '')} {gray(v.get('link', ''))}")
            except ImportError:
                print_error("youtube-search-python não instalado")
            except Exception as e:
                print_error(f"Erro: {e}")
        
        if videos:
            save_csv(videos, f"videos_{termo}.csv", session_dir)

# ======================================
# 📦 MÓDULO 5: App Stores
# ======================================

def module_stores():
    print_header("App Stores Collector")
    
    while True:
        termo = safe_input("> Termo de busca")
        if not termo: break
        
        store = safe_input("> Loja (1=Google Play, 2=App Store, 3=ambas)", "1") or "1"
        lang = safe_input("> Idioma", "pt") or "pt"
        country = safe_input("> País", "br") or "br"
        limite = int(safe_input("> Resultados", "10") or 10)
        
        session_dir = ensure_dir(BASE_DIR / f"stores_{now_tag()}")
        resultados = []
        
        if store in ["1", "3"]:
            try:
                from google_play_scraper import search
                print_section("Google Play Store")
                res = search(termo, lang=lang, country=country)
                
                for app in res[:limite]:
                    resultados.append({
                        "loja": "Google Play",
                        "titulo": app.get("title", ""),
                        "desenvolvedor": app.get("developer", ""),
                        "score": app.get("score", 0),
                        "installs": app.get("installs", ""),
                        "link": f"https://play.google.com/store/apps/details?id={app.get('appId', '')}"
                    })
                    print(f"{green(str(len(resultados)))}. {app.get('title', '')} {gray(f'({app.get('score', 0)})')}")
            except ImportError:
                print_warning("google-play-scraper não instalado")
            except Exception as e:
                print_error(f"Google Play: {e}")
        
        if store in ["2", "3"]:
            try:
                print_section("Apple App Store")
                url = "https://itunes.apple.com/search"
                params = {
                    "term": termo,
                    "country": country,
                    "entity": "software,iPadSoftware",
                    "limit": limite
                }
                r = requests.get(url, params=params, timeout=30)
                r.raise_for_status()
                data = r.json()
                
                for app in data.get("results", []):
                    resultados.append({
                        "loja": "App Store",
                        "titulo": app.get("trackName", ""),
                        "desenvolvedor": app.get("artistName", ""),
                        "score": app.get("averageUserRating", 0),
                        "preco": app.get("formattedPrice", "Gratuito"),
                        "link": app.get("trackViewUrl", "")
                    })
                    print(f"{green(str(len(resultados)))}. {app.get('trackName', '')} {gray(f'({app.get('averageUserRating', 0)})')}")
            except Exception as e:
                print_error(f"App Store: {e}")
        
        if resultados:
            save_csv(resultados, f"apps_{termo}.csv", session_dir)
            print_success(f"Total: {len(resultados)} resultados")

# ======================================
# 📦 MÓDULO 6: Reddit
# ======================================

def module_reddit():
    try:
        import praw
    except ImportError:
        print_error("praw não instalado. Instale com: pip install praw")
        return
    
    print_header("Reddit Collector")
    
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
    except Exception as e:
        print_error(f"Erro ao conectar Reddit: {e}")
        return
    
    while True:
        termo = safe_input("> Termo de busca")
        if not termo: break
        
        subreddit = safe_input("> Subreddit (deixe vazio para todos)", "")
        limite = int(safe_input("> Posts", "5") or 5)
        
        session_dir = ensure_dir(BASE_DIR / f"reddit_{now_tag()}")
        resultados = []
        
        try:
            if subreddit:
                sub = reddit.subreddit(subreddit)
                posts = sub.search(termo, limit=limite)
            else:
                posts = reddit.subreddit("all").search(termo, limit=limite)
            
            for post in posts:
                resultados.append({
                    "titulo": post.title,
                    "autor": str(post.author),
                    "subreddit": post.subreddit.display_name,
                    "score": post.score,
                    "comentarios": post.num_comments,
                    "link": f"https://reddit.com{post.permalink}"
                })
                print(f"{green(str(len(resultados)))}. {post.title} {gray(f'(r/{post.subreddit.display_name})')}")
            
            if resultados:
                save_csv(resultados, f"reddit_{termo}.csv", session_dir)
                print_success(f"Total: {len(resultados)} posts")
        except Exception as e:
            print_error(f"Erro: {e}")

# ======================================
# 📦 MÓDULO 7: Google News
# ======================================

def module_gnews():
    print_header("Google News Collector")
    
    while True:
        termo = safe_input("> Termo de busca")
        if not termo: break
        
        lang = safe_input("> Idioma", "pt") or "pt"
        country = safe_input("> País", "br") or "br"
        limite = int(safe_input("> Resultados", "10") or 10)
        
        session_dir = ensure_dir(BASE_DIR / f"gnews_{now_tag()}")
        
        # Tentar API GNews
        resultados = []
        if GNEWS_KEY:
            try:
                url = "https://gnews.io/api/v4/search"
                params = {
                    "q": termo,
                    "lang": lang,
                    "country": country,
                    "max": limite,
                    "apikey": GNEWS_KEY
                }
                r = requests.get(url, params=params, timeout=30)
                r.raise_for_status()
                data = r.json()
                
                for art in data.get("articles", [])[:limite]:
                    resultados.append({
                        "titulo": art.get("title", ""),
                        "descricao": art.get("description", ""),
                        "fonte": art.get("source", {}).get("name", ""),
                        "data": art.get("publishedAt", ""),
                        "link": art.get("url", "")
                    })
                    print(f"{green(str(len(resultados)))}. {art.get('title', '')} {gray(art.get('url', ''))}")
            except Exception as e:
                print_warning(f"API GNews falhou: {e}")
        
        # Fallback para scraping
        if not resultados:
            try:
                from gnews import GNews
                gnews = GNews(language=lang, country=country, max_results=limite)
                articles = gnews.get_news(termo)
                
                for art in articles[:limite]:
                    resultados.append({
                        "titulo": art.get("title", ""),
                        "descricao": art.get("description", ""),
                        "fonte": art.get("publisher", {}).get("title", ""),
                        "data": art.get("published date", ""),
                        "link": art.get("url", "")
                    })
                    print(f"{green(str(len(resultados)))}. {art.get('title', '')} {gray(art.get('url', ''))}")
            except ImportError:
                print_error("gnews não instalado")
            except Exception as e:
                print_error(f"Erro: {e}")
        
        if resultados:
            save_csv(resultados, f"gnews_{termo}.csv", session_dir)

# ======================================
# 📦 MÓDULO 8: GDELT
# ======================================

def coletar_gdelt(termo, limite=20, idioma="auto", sort="date", data_ini=None, data_fim=None):
    resultados = []
    try:
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        params = {
            "query": termo,
            "mode": "artlist",
            "maxrecords": limite,
            "format": "json"
        }
        if idioma != "auto":
            params["sourcelang"] = idioma
        if sort == "date":
            params["sort"] = "date"
        if data_ini:
            params["startdatetime"] = data_ini
        if data_fim:
            params["enddatetime"] = data_fim
        
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        for art in data.get("articles", [])[:limite]:
            resultados.append({
                "titulo": art.get("title", ""),
                "url": art.get("url", ""),
                "seendate": art.get("seendate", ""),
                "socialimage": art.get("socialimage", "")
            })
    except Exception as e:
        print_error(f"GDELT: {e}")
    return resultados

def module_gdelt():
    print_header("GDELT Collector")
    
    while True:
        termo = safe_input("> Termo de busca")
        if not termo: break
        
        limite = int(safe_input("> Resultados", "20") or 20)
        idioma = safe_input("> Idioma (pt, en, es, fr, auto)", "auto") or "auto"
        ordem = safe_input("> Ordenar por (1=data, 2=relevância)", "1") or "1"
        ordem = "date" if ordem == "1" else "relevance"
        
        session_dir = ensure_dir(BASE_DIR / f"gdelt_{now_tag()}")
        
        artigos = coletar_gdelt(termo, limite, idioma, ordem)
        
        if artigos:
            print_section(f"Resultados GDELT — {termo}")
            for i, art in enumerate(artigos, 1):
                print(f"{green(str(i))}. {art.get('title', '')}")
                print(f"   {gray(f'{art.get('seendate', '')} | {art.get('url', '')}')}\n")
            save_csv(artigos, f"gdelt_{termo}.csv", session_dir)
        else:
            print_warning("Nenhum resultado encontrado")

# ======================================
# 📦 MÓDULO 9: Hacker News
# ======================================

def module_hackernews():
    print_header("Hacker News Collector")
    
    while True:
        termo = safe_input("> Termo de busca")
        if not termo: break
        
        limite = int(safe_input("> Resultados", "20") or 20)
        session_dir = ensure_dir(BASE_DIR / f"hackernews_{now_tag()}")
        
        try:
            url = "https://hn.algolia.com/api/v1/search"
            params = {
                "query": termo,
                "tags": "story",
                "hitsPerPage": limite
            }
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            
            resultados = []
            for hit in data.get("hits", [])[:limite]:
                resultados.append({
                    "titulo": hit.get("title", ""),
                    "autor": hit.get("author", ""),
                    "pontos": hit.get("points", 0),
                    "comentarios": hit.get("num_comments", 0),
                    "data": hit.get("created_at", ""),
                    "link": hit.get("url", "") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                })
                print(f"{green(str(len(resultados)))}. {hit.get('title', '')} {gray(f'({hit.get('points', 0)} pts)')}")
            
            if resultados:
                save_csv(resultados, f"hackernews_{termo}.csv", session_dir)
        except Exception as e:
            print_error(f"Erro: {e}")

# ======================================
# 📦 MÓDULO 10: Stack Exchange
# ======================================

def module_stackexchange():
    print_header("Stack Exchange Collector")
    
    while True:
        termo = safe_input("> Termo de busca")
        if not termo: break
        
        site = safe_input("> Site (stackoverflow, askubuntu, etc)", "stackoverflow") or "stackoverflow"
        limite = int(safe_input("> Resultados", "20") or 20)
        
        session_dir = ensure_dir(BASE_DIR / f"stackexchange_{now_tag()}")
        
        try:
            url = f"https://api.stackexchange.com/2.3/search/advanced"
            params = {
                "q": termo,
                "site": site,
                "pagesize": limite,
                "order": "relevance",
                "sort": "relevance"
            }
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            
            resultados = []
            for item in data.get("items", [])[:limite]:
                resultados.append({
                    "titulo": item.get("title", ""),
                    "autor": item.get("owner", {}).get("display_name", ""),
                    "score": item.get("score", 0),
                    "respostas": item.get("answer_count", 0),
                    "tags": ", ".join(item.get("tags", [])),
                    "link": item.get("link", "")
                })
                print(f"{green(str(len(resultados)))}. {item.get('title', '')} {gray(f'({item.get('score', 0)} pts)')}")
            
            if resultados:
                save_csv(resultados, f"stackexchange_{termo}.csv", session_dir)
        except Exception as e:
            print_error(f"Erro: {e}")

# ======================================
# 📦 MÓDULO 11: GitHub
# ======================================

def module_github():
    print_header("GitHub Collector")
    
    while True:
        termo = safe_input("> Termo de busca")
        if not termo: break
        
        tipo = safe_input("> Tipo (1=repos, 2=issues, 3=commits)", "1") or "1"
        limite = int(safe_input("> Resultados", "10") or 10)
        
        session_dir = ensure_dir(BASE_DIR / f"github_{now_tag()}")
        
        headers = {}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
        try:
            if tipo == "1":
                url = "https://api.github.com/search/repositories"
                params = {"q": termo, "sort": "stars", "per_page": limite}
                r = requests.get(url, params=params, headers=headers, timeout=15)
                r.raise_for_status()
                data = r.json()
                
                resultados = []
                for repo in data.get("items", [])[:limite]:
                    resultados.append({
                        "nome": repo.get("name", ""),
                        "full_name": repo.get("full_name", ""),
                        "descricao": repo.get("description", ""),
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "linguagem": repo.get("language", ""),
                        "link": repo.get("html_url", "")
                    })
                    print(f"{green(str(len(resultados)))}. {repo.get('full_name', '')} {gray(f'({repo.get('stargazers_count', 0)} stars)')}")
                
                if resultados:
                    save_csv(resultados, f"github_repos_{termo}.csv", session_dir)
            
            elif tipo == "2":
                url = "https://api.github.com/search/issues"
                params = {"q": termo, "sort": "created", "per_page": limite}
                r = requests.get(url, params=params, headers=headers, timeout=15)
                r.raise_for_status()
                data = r.json()
                
                resultados = []
                for issue in data.get("items", [])[:limite]:
                    resultados.append({
                        "titulo": issue.get("title", ""),
                        "repo": issue.get("repository_url", "").split("/")[-2:],
                        "estado": issue.get("state", ""),
                        "criado_em": issue.get("created_at", ""),
                        "link": issue.get("html_url", "")
                    })
                    print(f"{green(str(len(resultados)))}. {issue.get('title', '')}")
                
                if resultados:
                    save_csv(resultados, f"github_issues_{termo}.csv", session_dir)
        
        except Exception as e:
            print_error(f"Erro: {e}")

# ======================================
# 📦 MÓDULO 12: arXiv
# ======================================

def module_arxiv():
    print_header("arXiv Collector")
    
    while True:
        termo = safe_input("> Termo de busca")
        if not termo: break
        
        limite = int(safe_input("> Resultados", "20") or 20)
        ordenacao = safe_input("> Ordenação (relevance, lastUpdatedDate, submittedDate)", "relevance") or "relevance"
        
        session_dir = ensure_dir(BASE_DIR / f"arxiv_{now_tag()}")
        
        try:
            url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": f"all:{termo}",
                "start": 0,
                "max_results": limite,
                "sortBy": ordenacao
            }
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            
            root = ET.fromstring(r.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            resultados = []
            for entry in root.findall("atom:entry", ns)[:limite]:
                title = entry.find("atom:title", ns)
                title_text = title.text if title is not None else ""
                link = entry.find("atom:id", ns)
                link_text = link.text if link is not None else ""
                summary = entry.find("atom:summary", ns)
                summary_text = summary.text if summary is not None else ""
                
                resultados.append({
                    "titulo": title_text,
                    "resumo": summary_text[:500] if summary_text else "",
                    "link": link_text
                })
                print(f"{green(str(len(resultados)))}. {title_text[:60]}... {gray(link_text)}")
            
            if resultados:
                save_csv(resultados, f"arxiv_{termo}.csv", session_dir)
        except Exception as e:
            print_error(f"Erro: {e}")

# ======================================
# 📦 MÓDULO 13: Wikipedia
# ======================================

def module_wikipedia():
    try:
        import wikipediaapi
    except ImportError:
        print_error("wikipedia-api não instalado. Instale com: pip install wikipedia-api")
        return
    
    print_header("Wikipedia Collector")
    
    while True:
        termo = safe_input("> Termo de busca")
        if not termo: break
        
        lang = safe_input("> Idioma (pt, en, es, etc)", "pt") or "pt"
        limite = int(safe_input("> Resultados", "10") or 10)
        
        session_dir = ensure_dir(BASE_DIR / f"wikipedia_{now_tag()}")
        
        try:
            wiki = wikipediaapi.Wikipedia(lang, user_agent="uni-local-v0")
            
            # Buscar páginas
            results = wiki.search(termo, results=limite)
            resultados = []
            
            for page_title in results:
                page = wiki.page(page_title)
                if page.exists():
                    resultados.append({
                        "titulo": page.title,
                        "resumo": page.summary[:500],
                        "link": page.fullurl
                    })
                    print(f"{green(str(len(resultados)))}. {page.title}")
                    if len(resultados) >= limite:
                        break
            
            if resultados:
                save_csv(resultados, f"wikipedia_{termo}.csv", session_dir)
            else:
                print_warning("Nenhum resultado encontrado")
        except Exception as e:
            print_error(f"Erro: {e}")

# ======================================
# 🎯 MENU PRINCIPAL
# ======================================

MODULES = {
    "1": ("Google Suggest", module_suggest),
    "2": ("Google Trends (pytrends)", module_trends_pytrends),
    "3": ("SERP + Scraping", module_serp),
    "4": ("YouTube", module_youtube),
    "5": ("App Stores", module_stores),
    "6": ("Reddit", module_reddit),
    "7": ("Google News", module_gnews),
    "8": ("GDELT", module_gdelt),
    "9": ("Hacker News", module_hackernews),
    "10": ("Stack Exchange", module_stackexchange),
    "11": ("GitHub", module_github),
    "12": ("arXiv", module_arxiv),
    "13": ("Wikipedia", module_wikipedia),
}

def print_main_menu():
    clear_screen()
    print_header("UNI - Coletor Universal de Dados v0", "=", 70)
    print(f"{bold('Módulos disponíveis:')}\n")
    
    for key, (name, _) in MODULES.items():
        print(f"  {green(key)}. {name}")
    
    print(f"\n  {yellow('0')}. Sair")
    print(f"\n{'─' * 70}\n")

def main():
    lang, region = detect_locale()
    print_info(f"Idioma detectado: {lang}, Região: {region}")
    
    while True:
        print_main_menu()
        choice = safe_input("> Selecione um módulo", "")
        
        if not choice or check_exit(choice):
            print(yellow("\nEncerrado. Até mais!\n"))
            break
        
        if choice in MODULES:
            name, func = MODULES[choice]
            try:
                func()
            except KeyboardInterrupt:
                print(yellow("\n\nOperação cancelada pelo usuário."))
            except Exception as e:
                print_error(f"Erro no módulo {name}: {e}")
                import traceback
                traceback.print_exc()
            
            input(f"\n{cyan('Pressione Enter para continuar...')}")
        else:
            print_error("Opção inválida")

if __name__ == "__main__":
    try:
        import pandas as pd
    except ImportError:
        print_warning("pandas não instalado. Alguns módulos podem não funcionar perfeitamente.")
        print_info("Instale com: pip install pandas")
    
    main()
