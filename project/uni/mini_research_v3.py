#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mini Research v3 - Coletor de Dados Multi-Fonte
Versão completamente padronizada e otimizada

Melhorias v3:
- Menus 100% padronizados (sempre numéricos, mesmo formato)
- Delay como última pergunta antes de iniciar
- Ordem: configurar → coletar → exibir
- Configurações de lojas unificadas
- Títulos amigáveis com descrições
- Melhorias de UX/UI/CLI
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
# 🔑 CHAVES API
# ======================================

GOOGLE_API_KEY = "AIzaSyBj80B2fwVvFEMtcQU8tPV_NCNaEmQvzhc"
GOOGLE_CX = "f07ccd3b922d6437b"
BRAVE_API_KEY = "BSAjC9Yvq2s8_hYFIPWQ2QEl_XHpsQp"
SERPAPI_KEY = "e71430bcff8bdc906f7a5ed9ae1538355c2efb0fb88ffa071f7125a76cc2b142"
YOUTUBE_API_KEY = "AIzaSyBj80B2fwVvFEMtcQU8tPV_NCNaEmQvzhc"

# ======================================
# 🎨 Estilo Terminal
# ======================================

def color(text, code): return f"\033[{code}m{text}\033[0m"
def blue(text): return color(text, "34")
def green(text): return color(text, "32")
def yellow(text): return color(text, "33")
def red(text): return color(text, "31")
def gray(text): return color(text, "90")
def cyan(text): return color(text, "36")
def bold(text): return color(text, "1")

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

def parse_numeric_input(input_str, options_dict, default=None):
    """
    Parse entrada numérica padronizada
    - Aceita: "1", "1,2,3", "t" (todos)
    - Retorna: lista de chaves selecionadas
    """
    if not input_str or not input_str.strip():
        if default is not None:
            return [default]
        return []
    
    input_str = input_str.strip().lower()
    
    # "t" ou "todos" = todas as opções
    if input_str in ["t", "todos", "all"]:
        return list(options_dict.keys())
    
    # Parse números
    selected = []
    for item in input_str.split(","):
        item = item.strip()
        if item.isdigit():
            key = int(item)
            if key in options_dict:
                selected.append(key)
    
    return selected if selected else ([default] if default is not None else [])

def print_header(title, description=""):
    """Cabeçalho padronizado com descrição"""
    print(cyan("\n" + "="*70))
    print(cyan(f"  {title}"))
    if description:
        print(gray(f"  {description}"))
    print(cyan("="*70 + "\n"))

def print_menu(title, description, options, default=None):
    """
    Menu padronizado - SEMPRE numérico
    Formato padronizado: 1. Opção, 2. Opção, ..., t. Todos
    """
    print(cyan(f"\n{title}"))
    if description:
        print(gray(f"  {description}"))
    print("-" * 70)
    
    # Separar chaves int e str para ordenar corretamente
    int_keys = [k for k in options.keys() if isinstance(k, int)]
    str_keys = [k for k in options.keys() if isinstance(k, str)]
    
    # Ordenar chaves int
    for key in sorted(int_keys):
        value = options[key]
        marker = green(f"{key}") if key == default else f"{key}"
        print(f"  {marker}. {value}")
    
    # Adicionar opção "t" no final se existir
    if "t" in str_keys:
        marker = green("t")
        print(f"  {marker}. {options['t']} (seleciona todas as opções acima)")
    
    print("-" * 70)
    print(gray("  💡 Dica: Digite números separados por vírgula (ex: 1,2,3) ou 't' para todos"))

def print_config_summary(config):
    """Exibe resumo do que está sendo configurado"""
    print(cyan("\n📋 RESUMO DA CONFIGURAÇÃO"))
    print("-" * 70)
    print(f"  Termo: {bold(config.get('termo', 'N/A'))}")
    print(f"  Região: {', '.join(config.get('regions', []))}")
    print(f"  Fontes selecionadas: {len(config.get('fontes', []))} fonte(s)")
    for i, fonte_id in enumerate(sorted(config.get('fontes', [])), 1):
        fonte_nome = {1: "Google Suggest", 2: "Google Trends", 3: "SERP", 4: "YouTube", 5: "Google Play Store", 6: "Apple App Store"}.get(fonte_id, "Desconhecida")
        print(f"    {i}. {fonte_nome}")
    print("-" * 70)

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
    """Exibe um item de dados formatado"""
    print(f"  {green(f'{index:2d}.')} {prefix}{item}")
    flush_output()

def flush_output():
    """Força flush da saída para exibição em tempo real"""
    sys.stdout.flush()

BASE_DIR = "dados"

# ======================================
# 📦 CONSTANTES E CONFIGURAÇÕES
# ======================================

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"

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
}

SOURCES_OPTIONS = {
    1: "Web",
    2: "YouTube",
    3: "Notícias",
    4: "Shopping",
}

FONTES_OPTIONS = {
    1: "Google Suggest",
    2: "Google Trends",
    3: "SERP (Buscadores)",
    4: "YouTube",
    5: "App Stores (Google Play + Apple)",
}

SUGGEST_OPCOES = {
    1: "Top Sugestões",
    2: "Expansões a-z",
    3: "Expansões 0-9",
    4: "Categorias (questões, preposições, comparações)",
}

TRENDS_OPCOES = {
    1: "Top relacionados",
    2: "Rising relacionados",
    3: "Interesse por regiões",
    4: "Interesse ao longo do tempo",
}

TRENDS_TIPOS = {
    1: "Web",
    2: "Imagens",
    3: "Notícias",
    4: "YouTube",
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
    1: "DuckDuckGo (sem API key)",
    2: "Google (requer API key)",
    3: "Brave (requer API key)",
    4: "Bing (requer API key)",
}

YOUTUBE_ORDER = {
    1: "Relevância",
    2: "Data de publicação",
    3: "Número de visualizações",
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
    print_header(f"GOOGLE SUGGEST — {termo}", "Coletando sugestões de busca do Google")
    
    regions = config.get("regions", ["br"])
    clients_map = {1: "chrome", 2: "firefox"}
    sources_map = {1: "web", 2: "youtube", 3: "news", 4: "shopping"}
    sources_code_map = {"web": "", "youtube": "yt", "news": "n", "shopping": "sh"}
    
    clients = [clients_map[c] for c in config.get("clients", [1])]
    sources = [sources_map[s] for s in config.get("sources", [1])]
    opcoes = config.get("opcoes", [1])
    limit = config.get("limit", 15)
    delay = config.get("delay", 1.0)
    
    resultados = []
    counter = 0
    
    print_progress("Iniciando coleta de sugestões...")
    
    for region in regions:
        for client in clients:
            for source_name in sources:
                source_code = sources_code_map.get(source_name, "")
                
                # Top sugestões
                if 1 in opcoes:
                    print_progress(f"Coletando top sugestões [{region}/{client}/{source_name}]...")
                    sugs = get_suggestions(termo, region, client, source_code, "", limit)
                    
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
                    time.sleep(delay)
                
                # Expansões a-z
                if 2 in opcoes:
                    print_progress(f"Coletando expansões a-z [{region}/{client}/{source_name}]...")
                    for letter in string.ascii_lowercase:
                        q = f"{termo} {letter}"
                        sugs = get_suggestions(q, region, client, source_code, "", limit)
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
                        time.sleep(delay * 0.3)
                
                # Expansões 0-9
                if 3 in opcoes:
                    print_progress(f"Coletando expansões 0-9 [{region}/{client}/{source_name}]...")
                    for digit in "0123456789":
                        q = f"{termo} {digit}"
                        sugs = get_suggestions(q, region, client, source_code, "", limit)
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
                        time.sleep(delay * 0.3)
                
                # Categorias
                if 4 in opcoes:
                    print_progress(f"Coletando categorias [{region}/{client}/{source_name}]...")
                    for cat_id, (cat_name, words) in CATEGORIES.items():
                        for w in words:
                            q = f"{termo} {w}"
                            sugs = get_suggestions(q, region, client, source_code, "", limit)
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
                            time.sleep(delay * 0.3)
    
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
    
    print_header(f"GOOGLE TRENDS — {termo}", "Analisando tendências e interesse de busca")
    
    region_map = {"br": "BR", "us": "US", "fr": "FR", "de": "DE", "jp": "JP", "es": "ES", "it": "IT", "uk": "GB"}
    region = region_map.get(config.get("region", "br"), "BR")
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
        except Exception as e:
            print(red(f"  [ERRO] {e}"))
            continue
        
        # Top
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
                        print_data_item(i, f"{row.query} {gray(f'({row.value})')}")
                    
                    file = os.path.join(OUTPUT_DIR, f"top_{tipo_nome}_{termo}_{now_tag()}.csv")
                    df.to_csv(file, index=False, encoding="utf-8-sig")
                    print_success(f"Salvo: {file}", len(df))
            except:
                pass
        
        # Rising
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
                        print_data_item(i, f"{row.query} {gray(f'({row.value})')}")
                    
                    file = os.path.join(OUTPUT_DIR, f"rising_{tipo_nome}_{termo}_{now_tag()}.csv")
                    df.to_csv(file, index=False, encoding="utf-8-sig")
                    print_success(f"Salvo: {file}", len(df))
            except:
                pass
        
        # Regiões
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
                        print_data_item(i, f"{reg} {gray(f'({val})')}")
                    
                    df = pd.DataFrame({"regiao": serie.index, "valor": serie.values})
                    file = os.path.join(OUTPUT_DIR, f"regioes_{tipo_nome}_{termo}_{now_tag()}.csv")
                    df.to_csv(file, index=False, encoding="utf-8-sig")
                    print_success(f"Salvo: {file}", len(serie))
            except:
                pass
        
        # Tempo
        if 4 in opcoes:
            try:
                df_time = pytrends.interest_over_time()
                if not df_time.empty:
                    print_progress(f"Interesse ao longo do tempo ({tipo_nome}): {len(df_time)} pontos")
                    
                    for i, (idx, val) in enumerate(df_time[termo].items(), 1):
                        item = {"tipo": "tempo", "fonte": tipo_nome, "data": idx.strftime("%Y-%m-%d"), "valor": val}
                        resultados.append(item)
                        resultados_tempo_real["trends"].append(item)
                        if i <= 10:
                            print_data_item(i, f"{idx.strftime('%Y-%m-%d')} → {gray(val)}")
                    
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
    print_header(f"SERP — {termo}", "Buscando resultados em múltiplos buscadores")
    
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
                rank_str = f"[{r['engine'].upper()}]"
                print_data_item(r['rank'], f"{r['title']}", f"{green(rank_str)} ")
                print(f"      {gray(r['link'])}")
            
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

def run_youtube(termo, config, output_dir, resultados_tempo_real):
    """Executa YouTube"""
    print_header(f"YOUTUBE — {termo}", "Buscando vídeos e coletando comentários")
    
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
        return []
    
    print_progress(f"Vídeos encontrados: {len(videos)}")
    
    for i, v in enumerate(videos, 1):
        item = {"video": v, "tipo": "video"}
        resultados_tempo_real["youtube"].append(item)
        print_data_item(i, v['titulo'])
        print(f"      Canal: {v.get('canal', 'N/A')} | Link: {gray(v['link'])}")
    
    df_videos = pd.DataFrame(videos)
    file = os.path.join(YOUTUBE_DIR, f"videos_{termo}.csv")
    df_videos.to_csv(file, index=False, encoding="utf-8-sig")
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
                print_progress(f"  Vídeo {i}: {vid['titulo'][:50]}...")
                
                comentarios = buscar_comentarios(vid["videoId"], limite_comentarios)
                time.sleep(delay)
                
                if comentarios:
                    for j, c in enumerate(comentarios, 1):
                        c["video_id"] = vid["videoId"]
                        c["video_titulo"] = vid["titulo"]
                        comentarios_todos.append(c)
                        resultados_tempo_real["youtube"].append({"comentario": c, "tipo": "comentario"})
                        if j <= 10:
                            likes_str = f"({c['likes']} likes)"
                            print_data_item(j, f"{c['autor']}: {c['comentario'][:60]}... {gray(likes_str)}")
        
        if comentarios_todos:
            df_comentarios = pd.DataFrame(comentarios_todos)
            file = os.path.join(YOUTUBE_DIR, f"comentarios_{termo}.csv")
            df_comentarios.to_csv(file, index=False, encoding="utf-8-sig")
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

def run_stores(termo, config, output_dir, resultados_tempo_real):
    """Executa App Stores (Google Play + Apple App Store)"""
    if not HAS_PLAY_SCRAPER:
        print(yellow("[!] google-play-scraper não instalado. Pulando App Stores."))
        return {}
    
    print_header(f"APP STORES — {termo}", "Buscando apps e coletando avaliações")
    
    country = config.get("country", "br")
    lang = config.get("lang", "pt")
    n_apps = config.get("n_apps", 50)
    max_reviews = config.get("max_reviews", 50)
    coletar_reviews = config.get("coletar_reviews", False)
    apps_selecionados = config.get("apps_selecionados", [1, 2, 3])
    lojas = config.get("lojas", [1, 2])  # 1=Google Play, 2=Apple App Store
    delay = config.get("delay", 1.0)
    
    STORES_DIR = ensure_dir(os.path.join(output_dir, "stores"))
    resultados = {}
    
    # Google Play Store
    if 1 in lojas:
        print_progress("Buscando apps no Google Play...")
        
        df_google = fetch_google(termo, lang, country, n_apps)
        time.sleep(delay)
        
        if not df_google.empty:
            print_progress(f"Google Play: {len(df_google)} apps encontrados")
            
            for i, row in enumerate(df_google.itertuples(), 1):
                item = {"app": {"title": row.title, "developer": row.developer, "rating": row.rating, "installs": row.installs}, "tipo": "app", "loja": "google_play"}
                resultados_tempo_real["stores"].append(item)
                print_data_item(i, f"{row.title} | ⭐ {row.rating or 's/d'} | {row.developer}")
                print(f"      Downloads: {row.installs}")
            
            file = os.path.join(STORES_DIR, f"apps_google_{termo}.csv")
            df_google.to_csv(file, index=False, encoding="utf-8-sig")
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
                        for j, row in enumerate(df_reviews.head(10).itertuples(), 1):
                            item = {"review": {"app": app_title, "rating": row.score, "content": row.content[:60]}, "tipo": "review", "loja": "google_play"}
                            resultados_tempo_real["stores"].append(item)
                            print_data_item(j, f"⭐{row.score} | {row.content[:60]}...")
                        
                        file = os.path.join(STORES_DIR, f"reviews_google_{app_id}.csv")
                        df_reviews.to_csv(file, index=False, encoding="utf-8-sig")
                        print_success(f"  Reviews: {file}", len(df_reviews))
        else:
            resultados["google_play"] = pd.DataFrame()
    
    # Apple App Store
    if 2 in lojas:
        print_progress("Buscando apps na App Store...")
        
        df_apple = apple_df(fetch_apple(termo, country, n_apps))
        time.sleep(delay)
        
        if not df_apple.empty:
            print_progress(f"App Store: {len(df_apple)} apps encontrados")
            
            for i, row in enumerate(df_apple.itertuples(), 1):
                item = {"app": {"title": row.title, "developer": row.developer, "rating": row.rating, "ratings_count": row.ratings_count}, "tipo": "app", "loja": "app_store"}
                resultados_tempo_real["stores"].append(item)
                print_data_item(i, f"{row.title} | ⭐ {row.rating or 's/d'} | {row.developer}")
                print(f"      Avaliações: {row.ratings_count}")
            
            file = os.path.join(STORES_DIR, f"apps_apple_{termo}.csv")
            df_apple.to_csv(file, index=False, encoding="utf-8-sig")
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
                        for j, row in enumerate(df_reviews.head(10).itertuples(), 1):
                            item = {"review": {"app": app_title, "rating": row.rating, "content": row.content[:60]}, "tipo": "review", "loja": "app_store"}
                            resultados_tempo_real["stores"].append(item)
                            print_data_item(j, f"⭐{row.rating} | {row.content[:60]}...")
                        
                        file = os.path.join(STORES_DIR, f"reviews_apple_{app_id}.csv")
                        df_reviews.to_csv(file, index=False, encoding="utf-8-sig")
                        print_success(f"  Reviews: {file}", len(df_reviews))
        else:
            resultados["app_store"] = pd.DataFrame()
    
    return resultados

# ======================================
# 🎯 CONFIGURAÇÃO (Ordem Lógica Melhorada)
# ======================================

def coletar_configuracao():
    """Coleta configuração em ordem lógica: termo → região → fontes → configurações → delay"""
    print_header("CONFIGURAÇÃO DE COLETA", "Siga a ordem para configurar sua pesquisa")
    
    config = {}
    
    # 1. TERMO (obrigatório)
    print_header("1️⃣  TERMO DE BUSCA", "Digite o termo ou frase que deseja pesquisar")
    termo = input("> Digite o termo de busca: ").strip()
    if not termo:
        print(red("❌ Termo não pode estar vazio!"))
        return None
    if check_exit(termo):
        return None
    config["termo"] = termo
    print(green(f"✓ Termo configurado: {bold(termo)}\n"))
    
    # 2. REGIÃO (global)
    print_menu(
        "2️⃣  REGIÃO",
        "Selecione as regiões onde deseja buscar (afeta todas as fontes)",
        REGIONS_OPTIONS,
        default=1
    )
    regions_input = input("> Selecione regiões (ex: 1,2 ou 't' para todas) [1]: ").strip() or "1"
    regions_selected = parse_numeric_input(regions_input, REGIONS_OPTIONS, default=1)
    region_map = {1: "br", 2: "us", 3: "fr", 4: "de", 5: "jp", 6: "es", 7: "it", 8: "uk"}
    config["regions"] = [region_map[r] for r in regions_selected]
    print(green(f"✓ Regiões configuradas: {', '.join(config['regions'])}\n"))
    
    # 3. FONTES DE DADOS
    print_menu(
        "3️⃣  FONTES DE DADOS",
        "Selecione quais fontes de dados deseja coletar",
        FONTES_OPTIONS,
        default=None
    )
    fontes_input = input("> Selecione fontes (ex: 1,2,4 ou 't' para todas) [t]: ").strip() or "t"
    fontes = parse_numeric_input(fontes_input, FONTES_OPTIONS, default=None)
    config["fontes"] = fontes
    print(green(f"✓ Fontes selecionadas: {len(fontes)} fonte(s)\n"))
    
    # 4. CONFIGURAÇÕES ESPECÍFICAS POR FONTE
    print_header("4️⃣  CONFIGURAÇÕES ESPECÍFICAS POR FONTE", "Configure apenas as fontes que você selecionou acima")
    
    # Google Suggest
    if 1 in config["fontes"]:
        print_menu(
            "--- Google Suggest ---",
            "Configure como coletar sugestões de busca",
            CLIENTS_OPTIONS,
            default=1
        )
        clients_input = input("> Selecione clientes [1]: ").strip() or "1"
        print_menu("Fontes", "Selecione as fontes de busca", SOURCES_OPTIONS, default=1)
        sources_input = input("> Selecione fontes [1]: ").strip() or "1"
        print_menu("Opções", "Selecione quais tipos de sugestões coletar", SUGGEST_OPCOES, default=1)
        opcoes_input = input("> Selecione opções [1]: ").strip() or "1"
        config["suggest"] = {
            "clients": parse_numeric_input(clients_input, CLIENTS_OPTIONS, default=1),
            "sources": parse_numeric_input(sources_input, SOURCES_OPTIONS, default=1),
            "opcoes": parse_numeric_input(opcoes_input, SUGGEST_OPCOES, default=1),
            "limit": int(input("> Resultados por consulta [15]: ").strip() or 15),
        }
        print(green("✓ Google Suggest configurado\n"))
    
    # Google Trends
    if 2 in config["fontes"]:
        print_menu(
            "--- Google Trends ---",
            "Configure tipos de pesquisa e período",
            TRENDS_TIPOS,
            default=1
        )
        tipos_input = input("> Selecione tipos [1]: ").strip() or "1"
        print_menu(
            "Período",
            "Selecione o período de análise",
            TRENDS_PERIODOS,
            default=4
        )
        periodo_input = input("> Selecione período [4]: ").strip() or "4"
        print_menu(
            "Opções",
            "Selecione quais dados coletar",
            TRENDS_OPCOES,
            default=1
        )
        opcoes_input = input("> Selecione opções [1,2,3,4]: ").strip() or "1,2,3,4"
        config["trends"] = {
            "gtypes": parse_numeric_input(tipos_input, TRENDS_TIPOS, default=1),
            "timeframe": parse_numeric_input(periodo_input, TRENDS_PERIODOS, default=4)[0],
            "opcoes": parse_numeric_input(opcoes_input, TRENDS_OPCOES, default=1),
            "topn": int(input("> Resultados [20]: ").strip() or 20),
        }
        print(green("✓ Google Trends configurado\n"))
    
    # SERP
    if 3 in config["fontes"]:
        print_menu(
            "--- SERP (Buscadores) ---",
            "Selecione quais buscadores usar",
            SERP_BUSCADORES,
            default=1
        )
        buscadores_input = input("> Selecione buscadores [1]: ").strip() or "1"
        config["serp"] = {
            "buscadores": parse_numeric_input(buscadores_input, SERP_BUSCADORES, default=1),
            "limite": int(input("> Resultados por buscador [20]: ").strip() or 20),
        }
        print(green("✓ SERP configurado\n"))
    
    # YouTube
    if 4 in config["fontes"]:
        print_menu(
            "--- YouTube ---",
            "Configure busca de vídeos e comentários",
            YOUTUBE_ORDER,
            default=1
        )
        order_input = input("> Selecione ordenação [1]: ").strip() or "1"
        config["youtube"] = {
            "order": parse_numeric_input(order_input, YOUTUBE_ORDER, default=1)[0],
            "limite_videos": int(input("> Quantos vídeos? [50]: ").strip() or 50),
            "coletar_comentarios": input("> Coletar comentários? (s/n) [n]: ").strip().lower() == "s",
        }
        if config["youtube"]["coletar_comentarios"]:
            config["youtube"]["limite_comentarios"] = int(input("> Comentários por vídeo [50]: ").strip() or 50)
            print_menu("Vídeos", "Selecione quais vídeos coletar comentários", {1: "Vídeo 1", 2: "Vídeo 2", 3: "Vídeo 3", "t": "Todos os vídeos"}, default=1)
            videos_sel = input("> Selecione vídeos (ex: 1,2,3 ou 't' para todos) [1]: ").strip() or "1"
            if videos_sel.lower() in ["t", "todos"]:
                config["youtube"]["videos_selecionados"] = "todos"
            else:
                config["youtube"]["videos_selecionados"] = [int(x) for x in videos_sel.split(",") if x.strip().isdigit()]
        else:
            config["youtube"]["limite_comentarios"] = 0
            config["youtube"]["videos_selecionados"] = [1]
        print(green("✓ YouTube configurado\n"))
    
    # App Stores (UNIFICADO)
    if 5 in config["fontes"]:
        print_menu(
            "--- App Stores (Google Play + Apple App Store) ---",
            "Configure busca de apps e reviews (aplica para ambas as lojas)",
            {1: "Google Play Store", 2: "Apple App Store", 3: "Ambas"},
            default=3
        )
        lojas_input = input("> Selecione lojas [3]: ").strip() or "3"
        lojas_selected = parse_numeric_input(lojas_input, {1: "Google Play", 2: "Apple", 3: "Ambas"}, default=3)
        if 3 in lojas_selected:
            config["stores"] = {"lojas": [1, 2]}
        else:
            config["stores"] = {"lojas": lojas_selected}
        
        config["stores"]["n_apps"] = int(input("> Quantidade de apps por loja [50]: ").strip() or 50)
        config["stores"]["coletar_reviews"] = input("> Coletar reviews? (s/n) [n]: ").strip().lower() == "s"
        
        if config["stores"]["coletar_reviews"]:
            config["stores"]["max_reviews"] = int(input("> Reviews por app [50]: ").strip() or 50)
            print_menu("Apps", "Selecione quais apps coletar reviews", {1: "App 1", 2: "App 2", 3: "App 3", "t": "Todos os apps"}, default=1)
            apps_sel = input("> Selecione apps (ex: 1,2,3 ou 't' para todos) [1,2,3]: ").strip() or "1,2,3"
            if apps_sel.lower() in ["t", "todos"]:
                config["stores"]["apps_selecionados"] = "todos"
            else:
                config["stores"]["apps_selecionados"] = [int(x) for x in apps_sel.split(",") if x.strip().isdigit()]
        else:
            config["stores"]["max_reviews"] = 0
            config["stores"]["apps_selecionados"] = [1, 2, 3]
        print(green("✓ App Stores configurado\n"))
    
    # Aplicar parâmetros globais
    for fonte_config in ["suggest", "trends", "serp", "youtube", "stores"]:
        if fonte_config in config:
            config[fonte_config]["region"] = config["regions"][0]
            config[fonte_config]["lang"] = "pt"
            config[fonte_config]["country"] = config["regions"][0]
    
    # 5. DELAY (última pergunta antes de iniciar)
    print_header("5️⃣  CONFIGURAÇÃO FINAL", "Última configuração antes de iniciar a coleta")
    delay_input = input("> Delay entre requisições em segundos [1.0]: ").strip()
    config["delay"] = float(delay_input) if delay_input else 1.0
    
    # Aplicar delay a todas as fontes
    for fonte_config in ["suggest", "trends", "serp", "youtube", "stores"]:
        if fonte_config in config:
            config[fonte_config]["delay"] = config["delay"]
    
    print(green(f"✓ Delay configurado: {config['delay']}s\n"))
    
    # Resumo final
    print_config_summary(config)
    
    confirm = input("\n> Confirmar e iniciar coleta? (s/n) [s]: ").strip().lower() or "s"
    if confirm != "s":
        print(yellow("Configuração cancelada."))
        return None
    
    return config

# ======================================
# 🚀 FUNÇÃO PRINCIPAL
# ======================================

def main():
    print_header("MINI RESEARCH v3 - COLETOR DE DADOS MULTI-FONTE", "Versão completamente padronizada e otimizada")
    
    # Coletar configuração
    config = coletar_configuracao()
    if not config:
        print(red("\n❌ Configuração cancelada ou inválida."))
        return
    
    termo = config["termo"]
    output_dir = ensure_dir(os.path.join(BASE_DIR, f"coleta_{termo}_{now_tag()}"))
    
    # Dicionário para resultados em tempo real
    resultados_tempo_real = {
        "suggest": [],
        "trends": [],
        "serp": [],
        "youtube": [],
        "stores": []
    }
    
    print_header("INICIANDO COLETA", f"Coletando dados para: {bold(termo)}")
    print(green(f"✓ Configuração concluída. Iniciando coleta...\n"))
    
    resultados = {}
    
    # Executar fontes selecionadas na ordem: suggest → trends → serp → youtube → stores
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
            resultados["stores"] = run_stores(termo, config.get("stores", {}), output_dir, resultados_tempo_real)
        except Exception as e:
            print(red(f"[ERRO] App Stores: {e}"))
            resultados["stores"] = {}
    
    print_header("COLETA FINALIZADA", f"Todos os dados foram coletados e salvos")
    print(green(f"✓ Dados salvos em: {output_dir}\n"))
    
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
            fonte_nome = fonte.replace('_', ' ').title()
            print(f"  {green('✓')} {fonte_nome}: {count} itens")
    print("-" * 70 + "\n")

if __name__ == "__main__":
    main()




