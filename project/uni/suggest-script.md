# @title suggest

  

import re

import string

import time

import requests

from itertools import product

from requests.adapters import HTTPAdapter

from urllib3.util.retry import Retry

from functools import lru_cache

  

# ======================================

# ⚙️ Configurações

# ======================================

  

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"

  

REGIONS = ["br", "us", "fr", "de", "jp"]

CLIENTS = ["chrome", "firefox"]

SOURCES = {"web": "", "youtube": "yt", "news": "n", "shopping": "sh"}

  

EXIT_COMMANDS = {"sair", "fechar", "terminar", "ok", "exit", "quit", "q"}

  

# ======================================

# 🎨 Estilo Terminal (cores)

# ======================================

  

def color(text, code): return f"\033[{code}m{text}\033[0m"

def blue(text): return color(text, "34")

def green(text): return color(text, "32")

def yellow(text): return color(text, "33")

def red(text): return color(text, "31")

def gray(text): return color(text, "90")

  

# ======================================

# 📂 Categorias de Busca

# ======================================

  

# CATEGORIES = {

# 1: ("Questões", ["o que ", "é ", "não é", "são ", "não são", "como ", "quem ", "por que ", "onde ", "quando ", "qual ", "quanto "]),

# 2: ("Preposições", ["de ","para ","com ", "sem ", "sobre ", "contra ", "até ", "tipo "]),

# 3: ("Comparações", ["e ", "ou ", "vs ", "melhor que ", "pior que "]),

# 4: ("Verbos", ["comprar", "vender", "usar", "criar", "fazer", "ganhar", "perder"]),

# 5: ("Adjetivos", ["bom", "ruim", "seguro", "caro", "barato", "fácil", "difícil"]),

# 6: ("Problemas", ["erro", "bug", "travado", "golpe", "fraude", "scam", "funciona", "não funciona"]),

# 7: ("Tutoriais", ["tutorial", "aula", "dicas", "iniciante", "passo a passo", "guia", "manual", "curso"]),

# 10: ("Uso prático (Bitcoin)", ["comprar bitcoin", "vender bitcoin", "taxa bitcoin", "sacar bitcoin"]),

# 11: ("Segurança (wallets, seed…)", ["chave privada", "seed", "cold wallet", "2FA", "recuperar acesso"]),

# 12: ("Onboarding (iniciante, vale a pena…)", ["como começar com bitcoin", "vale a pena investir", "bitcoin para iniciantes"]),

# 13: ("Tecnologia (blockchain, LN, web3…)", ["blockchain", "lightning network", "defi", "node", "minerar bitcoin"]),

# 14: ("Valor & Comparações", ["bitcoin vs ethereum", "bitcoin vs dólar", "melhor cripto"]),

# 15: ("Narrativas & Críticas", ["bitcoin é golpe", "bitcoin é seguro", "bitcoin futuro"]),

# }

  

# MENU_OPTIONS = {

# 1: "Top Sugestões",

# 2: "Expansões: a–z,0–9",

# 3: "Questões",

# 4: "Preposições",

# 5: "Comparações",

# 6: "Verbos",

# 7: "Adjetivos",

# 8: "Problemas",

# 9: "Tutoriais",

# 10: "Uso prático (bitcoin)",

# 11: "Segurança (wallets, seed…)",

# 12: "Onboarding",

# 13: "Tecnologia",

# 14: "Valor & Comparações",

# 15: "Narrativas & Críticas",

# "t": "Todos"

# }

  

CATEGORIES = {

3: ("Outros", [

"o que ", "é ", "nao é","faz", "nao faz","como ", "por que ", "porque ","onde ", "quando ", "quanto","qual ", "de ", "para ", "com ", "sem ", "vs","ou",

])

}

  

MENU_OPTIONS = {

1: "Top Sugestões",

2: "Expansões: a–z,0–9",

3: "Outros",

"t": "Todos"

}

  

# ======================================

# 🔧 Sessão HTTP com Retry

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

  

# ======================================

# ⚡ Funções Principais

# ======================================

  

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

print(red(f"[ERRO] {query} ({region}/{client}/{source}): {e}"))

return []

  

# ======================================

# 🧩 Funções Auxiliares

# ======================================

  

def check_exit(value): return value.lower() in EXIT_COMMANDS

def parse_list(s, default): return [x.strip() for x in s.split(",") if x.strip()] if s else [default]

  

def print_header(title, region, lang, client, source):

print(gray(f"\n{'='*60}\n{title} | {region} | {lang or 'auto'} | {client} | {source}\n{'='*60}\n"))

  

def print_list_numbered(rows, counter):

for s, r in rows:

counter[0] += 1

print(f"{green(str(counter[0]))}. {s} {gray(f'({r})')}")

  

# ======================================

# 🔄 Execução de Blocos

# ======================================

  

def run_blocks(term, blocks, region, lang, client, source, limit, counter):

"""Executa apenas os blocos selecionados"""

if 1 in blocks:

print_header("Sugestões padrão", region, lang, client, source)

print_list_numbered(get_suggestions(term, region, client, SOURCES.get(source, ""), lang, limit), counter)

  

if 2 in blocks:

for letter in string.ascii_lowercase + "0123456789":

q = f"{term} {letter}"

print_header(f"Expansão {letter.upper()}", region, lang, client, source)

print_list_numbered(get_suggestions(q, region, client, SOURCES.get(source, ""), lang, limit), counter)

time.sleep(0.2)

  

for idx in blocks:

if idx >= 3 and idx in CATEGORIES:

name, words = CATEGORIES[idx]

print_header(name, region, lang, client, source)

for w in words:

q = f"{term} {w}"

print_header(f'Expansão "{w.strip()}"', region, lang, client, source)

print_list_numbered(get_suggestions(q, region, client, SOURCES.get(source, ""), lang, limit), counter)

time.sleep(0.2)

  

# ======================================

# 🚀 Loop Principal (ordem agrupada por fonte)

# ======================================

  

def main():

print(blue("\n=== Google Suggest ==="))

print("Digite 'sair' para finalizar.\n")

  

counter = [0]

  

while True:

term_in = input("> Termo(s) de busca: ").strip()

if check_exit(term_in): break

terms = parse_list(term_in, "bitcoin")

  

region_in = input("> Região [br]: ").strip()

if check_exit(region_in): break

region_list = parse_list(region_in, "br")

  

lang_in = input("> Idioma [auto]: ").strip()

if check_exit(lang_in): break

lang_list = parse_list(lang_in, "")

  

client_in = input("> Navegador [chrome]: ").strip()

if check_exit(client_in): break

client_list = parse_list(client_in, "chrome")

  

source_in = input("> Fonte [web]: ").strip()

if check_exit(source_in): break

source_list = parse_list(source_in, "web")

  

print("\n> Exibição:")

for k, v in MENU_OPTIONS.items():

print(f"{green(str(k))}. {v}")

  

choice = input("> Selecione: [1] ").strip().lower()

if check_exit(choice): break

  

blocks = list(CATEGORIES.keys()) if choice == "t" else [int(x) for x in re.split(r"[,\s]+", choice) if x.isdigit()]

  

limit_in = input("> Resultados [10]: ").strip()

if check_exit(limit_in): break

limit = int(limit_in or 10)

  

for source in source_list:

print(blue(f"\n\n==============================="))

print(blue(f"🌐 Iniciando bloco da fonte: {source.upper()}"))

print(blue(f"===============================\n"))

  

for region in region_list:

for lang in lang_list:

for client in client_list:

for term in terms:

print_header(f"Execução '{term}'", region, lang, client, source)

run_blocks(term, blocks, region, lang, client, source, limit, counter)

  

print(yellow("\nEncerrado. Até mais!\n"))

  

# ======================================

# ▶️ Execução

# ======================================

  

if __name__ == "__main__":

main()