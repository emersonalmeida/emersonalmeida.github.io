# @title stores

  

# ===============================================================

# APP+REVIEWS — COLETOR DE AVALIAÇÕES (GOOGLE PLAY + APP STORE)

# v3.2 — Barra de progresso, limite automático e logs otimizados

# ===============================================================

  

!pip install --quiet google-play-scraper requests pandas tabulate tqdm

  

import os

import requests

import pandas as pd

from datetime import datetime

from google_play_scraper import search, reviews, Sort

from tqdm import tqdm

import time

  

# ======================================

# Estilo Terminal (cores)

# ======================================

  

def color(text, code): return f"\033[{code}m{text}\033[0m"

def blue(text): return color(text, "34")

def green(text): return color(text, "32")

def yellow(text): return color(text, "33")

def red(text): return color(text, "31")

def gray(text): return color(text, "90")

  

# ======================================

# Utilitários

# ======================================

  

pd.set_option("display.max_colwidth", None)

  

def now_tag():

return datetime.now().strftime("%Y%m%d_%H%M%S")

  

def ensure_dir(path):

os.makedirs(path, exist_ok=True)

return path

  

def save_results(df, label, name, output_dir):

if df.empty:

print(yellow(f"Nenhum dado para salvar: {label}"))

return

file = os.path.join(output_dir, f"{label}_{name}_{now_tag()}.csv")

df.to_csv(file, index=False, encoding="utf-8-sig")

print(gray(f"Salvo: {file}"))

  

# ======================================

# Apple Store

# ======================================

  

def fetch_apple(term, country="br", limit=20):

try:

r = requests.get(

"https://itunes.apple.com/search",

params={"term": term, "country": country, "entity": "software,iPadSoftware", "limit": limit},

timeout=30

)

r.raise_for_status()

return r.json().get("results", [])

except Exception as e:

print(red(f"Erro ao buscar apps da Apple: {e}"))

return []

  

def apple_df(results):

rows = []

for r in results:

rows.append({

"title": r.get("trackName"),

"developer": r.get("artistName"),

"rating": round(r.get("averageUserRating", 0), 1) if r.get("averageUserRating") else None,

"ratings_count": r.get("userRatingCount") or 0,

"id": r.get("trackId"),

"url": r.get("trackViewUrl")

})

return pd.DataFrame(rows)

  

def fetch_reviews_apple(app_id, country="br", max_reviews=200):

collected, page = [], 1

with tqdm(total=max_reviews, desc=f"Apple Reviews {app_id}", ncols=100) as pbar:

while len(collected) < max_reviews:

url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/page={page}/json"

try:

r = requests.get(url, timeout=30)

r.raise_for_status()

data = r.json()

entries = data.get("feed", {}).get("entry", [])

except Exception as e:

print(red(f"Erro Apple Reviews ({app_id}): {e}"))

break

  

if not entries or not isinstance(entries, list):

break

  

if isinstance(entries[0], dict) and "im:rating" not in entries[0]:

entries = entries[1:]

if not entries:

break

  

for e in entries:

collected.append({

"author": e.get("author", {}).get("name", {}).get("label"),

"rating": int(e.get("im:rating", {}).get("label", 0)),

"title": e.get("title", {}).get("label"),

"content": e.get("content", {}).get("label"),

"votes": int(e.get("im:voteCount", {}).get("label", 0)),

"date": e.get("updated", {}).get("label")

})

pbar.update(len(entries))

if len(entries) < 50:

break

page += 1

return pd.DataFrame(collected[:max_reviews])

  

# ======================================

# Google Play

# ======================================

  

def fetch_google(term, lang="pt", country="br", n=20):

try:

res = search(term, lang=lang, country=country)

except Exception as e:

print(red(f"Erro ao buscar apps do Google Play: {e}"))

return pd.DataFrame()

  

rows = []

for r in res[:n]:

rows.append({

"title": r.get("title"),

"developer": r.get("developer"),

"rating": round(r.get("score", 0), 1) if r.get("score") else None,

"installs": r.get("installs"),

"id": r.get("appId")

})

return pd.DataFrame(rows)

  

def fetch_reviews_google(app_id, lang="pt", country="br", max_reviews=200):

out, token = [], None

with tqdm(total=max_reviews, desc=f"Google Reviews {app_id}", ncols=100) as pbar:

while len(out) < max_reviews:

try:

batch, token = reviews(

app_id,

lang=lang,

country=country,

sort=Sort.NEWEST,

count=min(200, max_reviews - len(out)),

continuation_token=token

)

except Exception as e:

print(red(f"Erro Google Reviews ({app_id}): {e}"))

break

if not batch:

break

out.extend(batch)

pbar.update(len(batch))

time.sleep(0.3)

if not token:

break

return pd.DataFrame(out[:max_reviews])

  

# ======================================

# Ordenação dos reviews

# ======================================

  

def sort_reviews(df, option=1):

if df.empty:

return df

date_col = "date" if "date" in df.columns else "at" if "at" in df.columns else None

rating_col = "rating" if "rating" in df.columns else "score" if "score" in df.columns else None

votes_col = "thumbsUpCount" if "thumbsUpCount" in df.columns else "votes" if "votes" in df.columns else None

if option == 1 and date_col:

return df.sort_values(by=date_col, ascending=False, ignore_index=True)

elif option == 2 and date_col:

return df.sort_values(by=date_col, ascending=True, ignore_index=True)

elif option == 3 and rating_col:

return df.sort_values(by=rating_col, ascending=False, ignore_index=True)

elif option == 4 and rating_col:

return df.sort_values(by=rating_col, ascending=True, ignore_index=True)

elif option == 5 and votes_col:

return df.sort_values(by=votes_col, ascending=False, ignore_index=True)

return df

  

def get_sort_label(opt):

labels = {

1: "Mais recentes",

2: "Mais antigas",

3: "Melhores avaliadas",

4: "Piores avaliadas",

5: "Mais votadas"

}

return labels.get(opt, f"Modo {opt}")

  

# ======================================

# Exibição

# ======================================

  

def print_apps(df, store, top_n=20):

print(blue(f"\n=== {store} — Top {min(top_n, len(df))} Apps ==="))

if df.empty:

print(gray("(nenhum app encontrado)"))

return

for i, r in enumerate(df.itertuples(), 1):

print(f"{green(f'[{i:02d}]')} {r.title} | ⭐ {r.rating or 's/d'} | {r.developer}")

  

def print_reviews(df, store, app_name, top_n=5, limit_text=False):

print(blue(f"\n=== {store} — {app_name} | Top {top_n} Reviews ==="))

if df.empty:

print(gray("(sem comentários)"))

return

df_top = df.head(top_n)

for i, r in enumerate(df_top.itertuples(), 1):

content = getattr(r, "content", getattr(r, "text", ""))

if limit_text and len(content) > 200:

content = content[:200] + " [...]"

rating = getattr(r, "score", getattr(r, "rating", "?"))

votes = getattr(r, "thumbsUpCount", getattr(r, "votes", 0))

print(f"{green(f'[{i}]')} ⭐{rating} | 👍{votes} | {gray(content)}")

  

# ======================================

# Menu de configuração

# ======================================

  

def menu_configuracao():

print(blue("\n=== APP+REVIEWS — MENU DE CONFIGURAÇÃO ===\n"))

  

termo = input("> Termo de busca: ").strip()

if not termo:

print(yellow("É necessário informar um termo de busca."))

return None

  

country = input("> Região (br, us, es, fr, jp) [br]: ").strip() or "br"

lang = input("> Idioma (pt, en, es, fr, ja, auto) [pt]: ").strip() or "pt"

n_apps = int(input("> Quantidade de apps [20]: ").strip() or 20)

lojas = int(input("> Loja (1=Google, 2=Apple, 3=Ambas) [3]: ").strip() or 3)

  

max_reviews = int(input("> Comentários por app [200]: ").strip() or 200)

top_reviews = int(input("> Reviews exibidos [5]: ").strip() or 5)

  

raw = input("> Ordenação (1=Recentes,2=Antigos,3=Melhores,4=Piores,5=Votados) [1]: ").strip() or "1"

sort_opts = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()] or [1]

  

limitar = input("> Limitar texto dos reviews (s/n) [s]: ").strip().lower() or "s"

salvar = input("> Salvar resultados (s/n) [s]: ").strip().lower() or "s"

  

return {

"termo": termo, "country": country, "lang": lang, "n_apps": n_apps, "lojas": lojas,

"max_reviews": max_reviews, "top_reviews": top_reviews,

"sort_opts": sort_opts, "limitar": limitar.startswith("s"), "salvar": salvar.startswith("s")

}

  

# ======================================

# Execução principal

# ======================================

  

def main():

cfg = menu_configuracao()

if not cfg:

return

  

OUT_DIR = ensure_dir(os.path.join("dados", f"apps_reviews_{cfg['termo']}_{now_tag()}"))

  

# Google Play

if cfg["lojas"] in (1, 3):

print(blue("\nColetando apps do Google Play..."))

df_google = fetch_google(cfg["termo"], cfg["lang"], cfg["country"], cfg["n_apps"])

print_apps(df_google, "Google Play", cfg["n_apps"])

if cfg["salvar"]:

save_results(df_google, "apps_google", cfg["termo"], OUT_DIR)

  

for app_id in df_google["id"].dropna():

app_title = df_google.loc[df_google["id"] == app_id, "title"].iloc[0]

print(blue(f"\nColetando reviews de: {app_title}"))

df = fetch_reviews_google(app_id, cfg["lang"], cfg["country"], cfg["max_reviews"])

for opt in cfg["sort_opts"]:

df_sorted = sort_reviews(df, opt)

label = get_sort_label(opt)

print(blue(f"\nExibindo reviews — {label}"))

print_reviews(df_sorted, "Google Play", app_title, cfg["top_reviews"], limit_text=cfg["limitar"])

if cfg["salvar"]:

save_results(df_sorted, f"reviews_google_{label.replace(' ', '_')}", app_id, OUT_DIR)

  

# App Store

if cfg["lojas"] in (2, 3):

print(blue("\nColetando apps da App Store..."))

df_apple = apple_df(fetch_apple(cfg["termo"], cfg["country"], cfg["n_apps"]))

print_apps(df_apple, "App Store", cfg["n_apps"])

if cfg["salvar"]:

save_results(df_apple, "apps_apple", cfg["termo"], OUT_DIR)

  

for app_id in df_apple["id"].dropna():

app_title = df_apple.loc[df_apple["id"] == app_id, "title"].iloc[0]

print(blue(f"\nColetando reviews de: {app_title}"))

df = fetch_reviews_apple(app_id, cfg["country"], cfg["max_reviews"])

for opt in cfg["sort_opts"]:

df_sorted = sort_reviews(df, opt)

label = get_sort_label(opt)

print(blue(f"\nExibindo reviews — {label}"))

print_reviews(df_sorted, "App Store", app_title, cfg["top_reviews"], limit_text=cfg["limitar"])

if cfg["salvar"]:

save_results(df_sorted, f"reviews_apple_{label.replace(' ', '_')}", str(app_id), OUT_DIR)

  

print(yellow("\nFim da coleta!"))

  

# ======================================

# Execução

# ======================================

  

if __name__ == "__main__":

main()