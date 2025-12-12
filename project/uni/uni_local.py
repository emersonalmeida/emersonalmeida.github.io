#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coletor Universal de Dados - Versão Minimalista
Coleta dados de múltiplas fontes automaticamente
"""

import os
import re
import json
import csv
import time
import locale
import requests
from datetime import datetime
from pathlib import Path
from itertools import product
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from functools import lru_cache

# ======================================
# 🎨 Cores
# ======================================
def color(text, code): return f"\033[{code}m{text}\033[0m"
def blue(text): return color(text, "34")
def green(text): return color(text, "32")
def yellow(text): return color(text, "33")
def red(text): return color(text, "31")
def gray(text): return color(text, "90")
def cyan(text): return color(text, "36")

# ======================================
# ⚙️ Configurações
# ======================================
DADOS_DIR = Path("dados")
DADOS_DIR.mkdir(exist_ok=True)

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"
SERPAPI_KEY = "e71430bcff8bdc906f7a5ed9ae1538355c2efb0fb88ffa071f7125a76cc2b142"

def detect_locale():
    """Detecta idioma e região do sistema"""
    try:
        system_locale = locale.getdefaultlocale()[0]
        if system_locale:
            lang = system_locale.split('_')[0].lower()
            region = system_locale.split('_')[1].lower() if '_' in system_locale else lang
        else:
            lang, region = "pt", "br"
    except:
        lang, region = "pt", "br"
    
    lang_map = {"pt": "pt", "en": "en", "es": "es", "fr": "fr", "de": "de", "ja": "ja"}
    region_map = {"pt": "br", "en": "us", "es": "es", "fr": "fr", "de": "de", "ja": "jp"}
    
    lang = lang_map.get(lang, "pt")
    region = region_map.get(region, region_map.get(lang, "br"))
    
    return lang, region

def make_session():
    """Cria sessão HTTP com retry"""
    sess = requests.Session()
    sess.headers.update({"User-Agent": "Mozilla/5.0 Chrome/140.0"})
    retry = Retry(total=3, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504])
    sess.mount("https://", HTTPAdapter(max_retries=retry))
    return sess

SESSION = make_session()

# ======================================
# 📊 COLETA DE DADOS
# ======================================

def coletar_suggest(termo, region="br", lang="pt", limit=10):
    """Google Suggest"""
    resultados = []
    try:
        params = {"q": termo, "gl": region, "client": "chrome"}
        if lang:
            params["hl"] = lang
        r = SESSION.get(SUGGEST_URL, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        suggestions = data[1] if len(data) > 1 else []
        relevance = data[4].get("google:suggestrelevance", [0]*len(suggestions)) if len(data) > 4 and isinstance(data[4], dict) else [0]*len(suggestions)
        
        for sugestao, relevancia in zip(suggestions[:limit], relevance[:limit]):
            resultados.append({
                "fonte": "Google Suggest",
                "termo": termo,
                "titulo": sugestao,
                "relevancia": relevancia,
                "link": ""
            })
    except Exception as e:
        print(f"  {red('✗')} Erro: {str(e)[:50]}")
    return resultados

def coletar_trends(termo, region="br", lang="pt"):
    """Google Trends (via SerpAPI)"""
    resultados = []
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_trends",
            "q": termo,
            "geo": region.upper(),
            "hl": lang,
            "api_key": SERPAPI_KEY
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        # Processa related queries
        if "related_queries" in data:
            for item in data["related_queries"].get("rising", [])[:10]:
                resultados.append({
                    "fonte": "Google Trends",
                    "termo": termo,
                    "titulo": item.get("query", ""),
                    "relevancia": item.get("value", 0),
                    "link": ""
                })
    except Exception as e:
        print(f"  {red('✗')} Erro: {str(e)[:50]}")
    return resultados

def coletar_serp(termo, region="br", lang="pt", limit=10):
    """SERP - Google Search Results (via SerpAPI)"""
    resultados = []
    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": termo,
            "gl": region,
            "hl": lang,
            "num": limit,
            "api_key": SERPAPI_KEY
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        if "organic_results" in data:
            for i, item in enumerate(data["organic_results"][:limit], 1):
                resultados.append({
                    "fonte": "SERP",
                    "termo": termo,
                    "titulo": item.get("title", ""),
                    "relevancia": i,
                    "link": item.get("link", "")
                })
    except Exception as e:
        print(f"  {red('✗')} Erro: {str(e)[:50]}")
    return resultados

def coletar_youtube(termo, region="br", lang="pt", limit=10):
    """YouTube (via scraping)"""
    resultados = []
    try:
        from youtubesearchpython import VideosSearch
        vs = VideosSearch(termo, limit=limit)
        result = vs.result()
        
        for v in result.get("result", [])[:limit]:
            resultados.append({
                "fonte": "YouTube",
                "termo": termo,
                "titulo": v.get("title", ""),
                "relevancia": v.get("viewCount", {}).get("text", "0"),
                "link": v.get("link", "")
            })
    except ImportError:
        print(f"  {yellow('⚠')} youtube-search-python não instalado")
    except Exception as e:
        print(f"  {red('✗')} Erro: {str(e)[:50]}")
    return resultados

def coletar_play_store(termo, lang="pt", country="br", limit=10):
    """Google Play Store"""
    resultados = []
    try:
        from google_play_scraper import search
        res = search(termo, lang=lang, country=country)
        
        for app in res[:limit]:
            resultados.append({
                "fonte": "Google Play",
                "termo": termo,
                "titulo": app.get("title", ""),
                "relevancia": app.get("score", 0),
                "link": f"https://play.google.com/store/apps/details?id={app.get('appId', '')}"
            })
    except ImportError:
        print(f"  {yellow('⚠')} google-play-scraper não instalado")
    except Exception as e:
        print(f"  {red('✗')} Erro: {str(e)[:50]}")
    return resultados

def coletar_app_store(termo, country="br", limit=10):
    """Apple App Store"""
    resultados = []
    try:
        url = "https://itunes.apple.com/search"
        params = {
            "term": termo,
            "country": country,
            "entity": "software,iPadSoftware",
            "limit": limit
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        for app in data.get("results", []):
            resultados.append({
                "fonte": "App Store",
                "termo": termo,
                "titulo": app.get("trackName", ""),
                "relevancia": app.get("averageUserRating", 0),
                "link": app.get("trackViewUrl", "")
            })
    except Exception as e:
        print(f"  {red('✗')} Erro: {str(e)[:50]}")
    return resultados

# ======================================
# 💾 SALVAR RESULTADOS
# ======================================

def salvar_resultados(resultados, termo):
    """Salva em CSV, TXT e MD"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    termo_clean = termo.replace(" ", "_")
    session_dir = DADOS_DIR / f"coleta_{termo_clean}_{timestamp}"
    session_dir.mkdir(exist_ok=True)
    
    # CSV
    arquivo_csv = session_dir / "resultados.csv"
    with open(arquivo_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["fonte", "termo", "titulo", "relevancia", "link"])
        for item in resultados:
            writer.writerow([
                item.get("fonte", ""),
                item.get("termo", ""),
                item.get("titulo", ""),
                item.get("relevancia", ""),
                item.get("link", "")
            ])
    
    # TXT
    arquivo_txt = session_dir / "resultados.txt"
    with open(arquivo_txt, 'w', encoding='utf-8') as f:
        f.write(f"COLETA DE DADOS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Termo: {termo}\n")
        f.write(f"Total: {len(resultados)} resultados\n\n")
        
        for fonte in ["Google Suggest", "Google Trends", "SERP", "YouTube", "Google Play", "App Store"]:
            items = [r for r in resultados if r.get("fonte") == fonte]
            if items:
                f.write(f"\n{fonte}:\n")
                f.write("-" * 60 + "\n")
                for item in items:
                    f.write(f"  • {item.get('titulo', '')}\n")
    
    # MD
    arquivo_md = session_dir / "resultados.md"
    with open(arquivo_md, 'w', encoding='utf-8') as f:
        f.write(f"# Coleta de Dados\n\n")
        f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Termo:** {termo}\n\n")
        f.write(f"**Total:** {len(resultados)} resultados\n\n")
        
        for fonte in ["Google Suggest", "Google Trends", "SERP", "YouTube", "Google Play", "App Store"]:
            items = [r for r in resultados if r.get("fonte") == fonte]
            if items:
                f.write(f"## {fonte}\n\n")
                for item in items:
                    link = item.get("link", "")
                    titulo = item.get("titulo", "")
                    if link:
                        f.write(f"- [{titulo}]({link})\n")
                    else:
                        f.write(f"- {titulo}\n")
                f.write("\n")
    
    return session_dir

# ======================================
# 🚀 LOOP PRINCIPAL
# ======================================

def main():
    """Loop principal minimalista"""
    print(f"{cyan('Coletor Universal')} {gray('v1.0')}\n")
    
    lang, region = detect_locale()
    
    while True:
        termo = input(f"{cyan('Termo')}: ").strip()
        
        if not termo or termo.lower() in ["sair", "q", "quit", "exit"]:
            print(f"{gray('Saindo...')}")
            break
        
        print()
        print(f"{blue('Coletando')} {termo}...")
        
        resultados = []
        fontes = [
            ("Google Suggest", lambda: coletar_suggest(termo, region, lang)),
            ("Google Trends", lambda: coletar_trends(termo, region, lang)),
            ("SERP", lambda: coletar_serp(termo, region, lang)),
            ("YouTube", lambda: coletar_youtube(termo, region, lang)),
            ("Google Play", lambda: coletar_play_store(termo, lang, region)),
            ("App Store", lambda: coletar_app_store(termo, region))
        ]
        
        for nome_fonte, funcao in fontes:
            print(f"  {nome_fonte}...", end="", flush=True)
            dados = funcao()
            resultados.extend(dados)
            print(f" {green('✓')} {len(dados)}")
            time.sleep(0.3)  # Rate limiting
        
        # Exibir resumo
        print()
        print(f"{green('✓')} Total: {len(resultados)} resultados")
        
        # Salvar
        print(f"{cyan('Salvando')}...", end="", flush=True)
        session_dir = salvar_resultados(resultados, termo)
        print(f" {green('✓')} {gray(str(session_dir))}")
        print()

if __name__ == "__main__":
    main()
