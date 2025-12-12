#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coletor Universal de Dados - Pipeline em Tempo Real
Coleta dados de múltiplas fontes simultaneamente, exibe em tempo real e salva automaticamente
"""

import os
import sys
import json
import csv
import time
import locale
import requests
import threading
from datetime import datetime
from pathlib import Path
from queue import Queue
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
def magenta(text): return color(text, "35")
def bold(text): return color(text, "1")

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
                "link": "",
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        pass  # Erro será tratado no pipeline
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
                    "link": "",
                    "timestamp": datetime.now().isoformat()
                })
    except Exception as e:
        pass
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
                    "link": item.get("link", ""),
                    "timestamp": datetime.now().isoformat()
                })
    except Exception as e:
        pass
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
                "link": v.get("link", ""),
                "timestamp": datetime.now().isoformat()
            })
    except ImportError:
        pass
    except Exception as e:
        pass
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
                "link": f"https://play.google.com/store/apps/details?id={app.get('appId', '')}",
                "timestamp": datetime.now().isoformat()
            })
    except ImportError:
        pass
    except Exception as e:
        pass
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
                "link": app.get("trackViewUrl", ""),
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        pass
    return resultados

# ======================================
# 🔄 PIPELINE DE COLETA EM TEMPO REAL
# ======================================

class PipelineColeta:
    """Pipeline de coleta, exibição e salvamento em tempo real"""
    
    def __init__(self, termo, region="br", lang="pt"):
        self.termo = termo
        self.region = region
        self.lang = lang
        self.resultados = []
        self.resultados_lock = threading.Lock()
        self.fila_exibicao = Queue()
        self.fila_salvamento = Queue()
        self.fontes_completas = set()
        self.fontes_lock = threading.Lock()
        
        # Preparar diretório de salvamento
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        termo_clean = termo.replace(" ", "_")
        self.session_dir = DADOS_DIR / f"coleta_{termo_clean}_{timestamp}"
        self.session_dir.mkdir(exist_ok=True)
        
        # Preparar arquivos de salvamento
        self.arquivo_csv = self.session_dir / "resultados.csv"
        self.arquivo_txt = self.session_dir / "resultados.txt"
        self.arquivo_md = self.session_dir / "resultados.md"
        
        # Inicializar arquivos
        self._inicializar_arquivos()
        
        # Estatísticas
        self.total_coletado = 0
        self.inicio = time.time()
    
    def _inicializar_arquivos(self):
        """Inicializa os arquivos de saída"""
        # CSV
        with open(self.arquivo_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["fonte", "termo", "titulo", "relevancia", "link", "timestamp"])
        
        # TXT
        with open(self.arquivo_txt, 'w', encoding='utf-8') as f:
            f.write(f"COLETA DE DADOS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Termo: {self.termo}\n")
            f.write("Coleta em tempo real...\n\n")
        
        # MD
        with open(self.arquivo_md, 'w', encoding='utf-8') as f:
            f.write(f"# Coleta de Dados\n\n")
            f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Termo:** {self.termo}\n\n")
            f.write(f"**Status:** Coleta em tempo real...\n\n")
    
    def coletar_fonte(self, nome_fonte, funcao_coleta):
        """Coleta dados de uma fonte específica"""
        try:
            print(f"\n{cyan('→')} {bold(blue(nome_fonte))}: {yellow('Iniciando coleta...')}")
            dados = funcao_coleta()
            
            if dados:
                with self.resultados_lock:
                    self.resultados.extend(dados)
                    self.total_coletado += len(dados)
                
                # Exibir e salvar cada resultado imediatamente
                for item in dados:
                    # Exibir em tempo real
                    self.exibir_resultado(nome_fonte, item)
                    # Salvar imediatamente
                    self.salvar_resultado([item])
                
                print(f"{cyan('→')} {bold(blue(nome_fonte))}: {green('✓')} {bold(str(len(dados)))} resultados coletados")
            else:
                print(f"{cyan('→')} {bold(blue(nome_fonte))}: {gray('Nenhum resultado encontrado')}")
            
            with self.fontes_lock:
                self.fontes_completas.add(nome_fonte)
                
        except Exception as e:
            print(f"{cyan('→')} {bold(blue(nome_fonte))}: {red('✗')} Erro: {str(e)[:60]}")
            with self.fontes_lock:
                self.fontes_completas.add(nome_fonte)
    
    def exibir_resultado(self, nome_fonte, item):
        """Exibe um resultado individual em tempo real"""
        titulo = item.get("titulo", "")[:80]
        link = item.get("link", "")
        relevancia = item.get("relevancia", "")
        
        # Exibir título
        print(f"  {green('✓')} {magenta('•')} {bold(titulo)}")
        
        # Exibir link se houver
        if link:
            print(f"     {gray('🔗')} {cyan(link)}")
        
        # Exibir relevância se houver
        if relevancia and str(relevancia) != "0":
            print(f"     {gray('📊 Relevância:')} {yellow(str(relevancia))}")
        
        print()  # Linha em branco para separar
    
    def salvar_resultado(self, dados):
        """Salva resultados no arquivo em tempo real"""
        try:
            # Salvar no CSV
            with open(self.arquivo_csv, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                for item in dados:
                    writer.writerow([
                        item.get("fonte", ""),
                        item.get("termo", ""),
                        item.get("titulo", ""),
                        item.get("relevancia", ""),
                        item.get("link", ""),
                        item.get("timestamp", "")
                    ])
        except Exception as e:
            pass
    
    def processar_exibicao(self):
        """Thread para processar exibição em tempo real (mantida para compatibilidade)"""
        # Esta função não é mais necessária pois exibimos diretamente na coleta
        # Mas mantemos para não quebrar o código
        while True:
            try:
                item = self.fila_exibicao.get(timeout=0.1)
                if item[0] == "fim":
                    break
                self.fila_exibicao.task_done()
            except:
                with self.fontes_lock:
                    if len(self.fontes_completas) >= 6:  # Todas as fontes completas
                        if self.fila_exibicao.empty():
                            break
                continue
    
    def processar_salvamento(self):
        """Thread para processar salvamento em tempo real"""
        while True:
            try:
                item = self.fila_salvamento.get(timeout=0.1)
                if item[0] == "dados":
                    _, dados = item
                    self.salvar_resultado(dados)
                elif item[0] == "fim":
                    break
                self.fila_salvamento.task_done()
            except:
                with self.fontes_lock:
                    if len(self.fontes_completas) >= 6:
                        if self.fila_salvamento.empty():
                            break
                continue
    
    def finalizar_arquivos(self):
        """Finaliza os arquivos de saída com resumo completo"""
        # Atualizar TXT
        with open(self.arquivo_txt, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Total: {len(self.resultados)} resultados\n")
            f.write(f"Tempo de coleta: {time.time() - self.inicio:.2f} segundos\n\n")
            
            for fonte in ["Google Suggest", "Google Trends", "SERP", "YouTube", "Google Play", "App Store"]:
                items = [r for r in self.resultados if r.get("fonte") == fonte]
                if items:
                    f.write(f"\n{fonte}:\n")
                    f.write("-" * 60 + "\n")
                    for item in items:
                        f.write(f"  • {item.get('titulo', '')}\n")
        
        # Atualizar MD
        with open(self.arquivo_md, 'a', encoding='utf-8') as f:
            f.write(f"**Total:** {len(self.resultados)} resultados\n\n")
            f.write(f"**Tempo de coleta:** {time.time() - self.inicio:.2f} segundos\n\n")
            
            for fonte in ["Google Suggest", "Google Trends", "SERP", "YouTube", "Google Play", "App Store"]:
                items = [r for r in self.resultados if r.get("fonte") == fonte]
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
    
    def executar(self):
        """Executa o pipeline completo"""
        print(f"\n{bold('='*70)}")
        print(f"{bold('COLETANDO DADOS EM TEMPO REAL')}")
        print(f"{bold('='*70)}\n")
        print(f"{cyan('Termo de busca:')} {bold(yellow(self.termo))}\n")
        print(f"{gray('Iniciando coleta de múltiplas fontes simultaneamente...')}\n")
        
        # Definir fontes
        fontes = [
            ("Google Suggest", lambda: coletar_suggest(self.termo, self.region, self.lang)),
            ("Google Trends", lambda: coletar_trends(self.termo, self.region, self.lang)),
            ("SERP", lambda: coletar_serp(self.termo, self.region, self.lang)),
            ("YouTube", lambda: coletar_youtube(self.termo, self.region, self.lang)),
            ("Google Play", lambda: coletar_play_store(self.termo, self.lang, self.region)),
            ("App Store", lambda: coletar_app_store(self.termo, self.region))
        ]
        
        # Iniciar threads de processamento (mantidas para salvamento em background)
        thread_salvamento = threading.Thread(target=self.processar_salvamento, daemon=True)
        thread_salvamento.start()
        
        # Iniciar coleta de todas as fontes simultaneamente
        threads_coleta = []
        for nome_fonte, funcao_coleta in fontes:
            thread = threading.Thread(
                target=self.coletar_fonte,
                args=(nome_fonte, funcao_coleta),
                daemon=True
            )
            thread.start()
            threads_coleta.append(thread)
        
        # Aguardar todas as coletas terminarem
        for thread in threads_coleta:
            thread.join()
        
        # Aguardar processamento de salvamento
        time.sleep(0.5)
        self.fila_salvamento.put(("fim",))
        thread_salvamento.join(timeout=2)
        
        # Finalizar arquivos
        self.finalizar_arquivos()
        
        # Exibir resumo final
        tempo_total = time.time() - self.inicio
        print(f"\n{bold('='*70)}")
        print(f"{green('✓')} {bold('COLETA CONCLUÍDA')}")
        print(f"{bold('='*70)}")
        print(f"{cyan('Total de resultados:')} {bold(green(str(len(self.resultados))))}")
        print(f"{cyan('Tempo total:')} {bold(green(f'{tempo_total:.2f} segundos'))}")
        print(f"{cyan('Dados salvos em:')} {gray(str(self.session_dir))}")
        print(f"{bold('='*70)}\n")

# ======================================
# 🚀 LOOP PRINCIPAL
# ======================================

def main():
    """Loop principal do pipeline"""
    print(f"\n{bold(cyan('╔═══════════════════════════════════════════════════════════════╗'))}")
    print(f"{bold(cyan('║'))}  {bold('COLETOR UNIVERSAL DE DADOS - PIPELINE EM TEMPO REAL')}  {bold(cyan('║'))}")
    print(f"{bold(cyan('╚═══════════════════════════════════════════════════════════════╝'))}\n")
    
    lang, region = detect_locale()
    
    # Se um termo foi passado como argumento, executa uma vez e sai
    if len(sys.argv) > 1:
        termo = " ".join(sys.argv[1:]).strip()
        if termo:
            try:
                pipeline = PipelineColeta(termo, region, lang)
                pipeline.executar()
            except Exception as e:
                print(f"\n{red('✗')} Erro: {str(e)}\n")
        return
    
    # Modo interativo
    while True:
        try:
            termo = input(f"{cyan('Digite o termo de busca')} (ou 'sair' para encerrar): ").strip()
            
            if not termo or termo.lower() in ["sair", "q", "quit", "exit"]:
                print(f"\n{gray('Encerrando o sistema...')}\n")
                break
            
            # Criar e executar pipeline
            pipeline = PipelineColeta(termo, region, lang)
            pipeline.executar()
            
            msg = "Pressione Enter para nova busca ou digite 'sair' para encerrar..."
            print(f"{gray(msg)}\n")
            
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{gray('Interrompido pelo usuário. Encerrando...')}\n")
            break
        except Exception as e:
            print(f"\n{red('✗')} Erro: {str(e)}\n")

if __name__ == "__main__":
    main()





