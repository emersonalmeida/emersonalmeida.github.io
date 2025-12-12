# Quick Start - Mini Research v5.0

## 🚀 Início Rápido (5 minutos)

### 1. Configurar API Keys

```bash
export GOOGLE_API_KEY="sua_key_aqui"
export GOOGLE_CX="seu_cx_aqui"
export BRAVE_API_KEY="sua_key_aqui"  # Opcional
export SERPAPI_KEY="sua_key_aqui"    # Opcional
export YOUTUBE_API_KEY="sua_key_aqui" # Opcional
```

### 2. Instalar Dependências

```bash
cd mini_research_v5
pip install -r requirements.txt
```

### 3. Executar

```bash
python main.py
```

Ou via Python:

```python
from mini_research_v5 import main
main()
```

## 📋 Exemplo de Uso Básico

```python
from mini_research_v5 import main
from mini_research_v5.config import load_config, validate_api_keys
from mini_research_v5.sources import SuggestSource

# Validar API keys
keys_status = validate_api_keys()
print(f"API Keys disponíveis: {keys_status}")

# Carregar configuração
settings = load_config("config.example.yaml")

# Criar fonte
config = {
    "regions": ["br"],
    "clients": [1],
    "sources": [1, 2],
    "opcoes": [1],
    "limit": 15,
    "delay": 1.0
}

source = SuggestSource(config)

# Coletar dados
real_time_results = {"suggest": []}
result = source.collect("python", "dados/", real_time_results)

if result.success:
    print(f"✓ Coletados {len(result)} itens")
    for item in result.data[:5]:  # Primeiros 5
        print(f"  - {item['sugestao']}")
```

## 🔧 Configuração Avançada

### Criar arquivo de configuração

```bash
cp config.example.yaml mini_research_config.yaml
```

Edite `mini_research_config.yaml`:

```yaml
base_dir: "meus_dados"
delay: 0.5
cache_enabled: true
export_formats: ["csv", "json", "parquet"]
```

### Usar múltiplas API keys

```bash
export GOOGLE_API_KEY="key1"
export GOOGLE_API_KEY_1="key2"  # Rotação automática
export GOOGLE_API_KEY_2="key3"
```

## 📊 Estrutura de Dados

Os dados são salvos em:

```
dados/
└── coleta_termo_YYYYMMDD_HHMMSS/
    ├── suggest_termo_YYYYMMDD_HHMMSS.csv
    └── ...
```

## 🐛 Troubleshooting

### Erro: "API key não configurada"
```bash
# Verifique se as variáveis estão configuradas
echo $GOOGLE_API_KEY

# Configure se necessário
export GOOGLE_API_KEY="sua_key"
```

### Erro: "Módulo não encontrado"
```bash
# Instale dependências
pip install -r requirements.txt

# Ou instale individualmente
pip install pandas numpy requests pyyaml
```

### Erro: "Configuração inválida"
- Verifique o formato do YAML
- Use `config.example.yaml` como referência
- Valide sintaxe YAML online

## 📚 Próximos Passos

1. Leia `README.md` para documentação completa
2. Veja `IMPLEMENTACAO_STATUS.md` para status das melhorias
3. Consulte `MELHORIAS_SUGERIDAS.md` para lista completa
4. Explore `sources/suggest.py` como exemplo de implementação

## 💡 Dicas

- Use `quiet_mode: true` no config para menos output
- Configure `cache_enabled: true` para reutilizar dados
- Use múltiplas API keys para evitar rate limits
- Salve configurações frequentes em arquivos YAML

## 🆘 Suporte

- Veja documentação em `README.md`
- Consulte exemplos em `sources/suggest.py`
- Verifique logs para detalhes de erros


