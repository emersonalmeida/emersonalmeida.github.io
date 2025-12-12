# Mini Research - Coletor de Dados Multi-Fonte

Script Python unificado para coleta de dados de múltiplas fontes, baseado no `mini-research.md`.

## 📦 Instalação

```bash
pip install -r requirements.txt
```

## 🚀 Uso

Execute o script:

```bash
python mini_research.py
```

## 📋 Módulos Disponíveis

### 1. Google Suggest
- Busca sugestões do Google Suggest
- Expansões por letras/números
- Categorias personalizadas
- Múltiplas regiões e fontes (web, youtube, news, shopping)

### 2. Google Trends
- Análise de tendências do Google
- Termos relacionados (top e rising)
- Interesse por região
- Evolução temporal
- Gráficos (opcional)

### 3. SERP (Search Engine Results Page)
- Busca em múltiplos motores:
  - DuckDuckGo (sem API key)
  - Google (requer API key)
  - Brave Search (requer API key)
  - Bing via SerpApi (requer API key)
- Scraping de conteúdo das páginas

### 4. YouTube
- Busca de vídeos
- Coleta de comentários
- Ordenação por relevância, data, visualizações
- API oficial ou scraping como fallback

### 5. App Stores
- Google Play Store
- Apple App Store
- Busca de apps
- Coleta de avaliações/reviews
- Ordenação por data, rating, votos

## ⚙️ Configuração de API Keys

Para usar algumas funcionalidades, configure as chaves de API no arquivo `mini_research.py`:

```python
# Google Custom Search
GOOGLE_API_KEY = "sua_chave_aqui"
GOOGLE_CX = "seu_cx_aqui"

# Brave Search
BRAVE_API_KEY = "sua_chave_aqui"

# SerpApi (para Bing)
SERPAPI_KEY = "sua_chave_aqui"

# YouTube API (opcional)
YOUTUBE_API_KEY = "sua_chave_aqui"
```

## 📁 Estrutura de Saída

Todos os dados são salvos na pasta `dados/` com estrutura:

```
dados/
├── suggest_[termo]_[timestamp]/
├── trends_[termo]_[timestamp]/
├── serp_scrap_[timestamp]/
├── youtube_[timestamp]/
└── apps_reviews_[termo]_[timestamp]/
```

## 🔧 Dependências Opcionais

O script funciona mesmo sem algumas dependências, mas com funcionalidades limitadas:

- **pytrends**: Necessário para Google Trends
- **matplotlib**: Necessário para gráficos
- **duckduckgo-search**: Necessário para DuckDuckGo
- **google-api-python-client**: Necessário para Google Search e YouTube API
- **beautifulsoup4**: Necessário para scraping
- **youtube-search-python**: Necessário para YouTube scraping
- **google-play-scraper**: Necessário para App Stores
- **tqdm**: Necessário para barras de progresso

## 📝 Notas

- O script detecta automaticamente quais dependências estão instaladas
- Funcionalidades que requerem API keys funcionam em modo limitado sem as chaves
- Todos os dados são salvos em CSV com encoding UTF-8
- O script mantém o mesmo estilo e funcionalidades do arquivo original




