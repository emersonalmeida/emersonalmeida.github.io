# 📋 CHANGELOG - UNI v7.3
## Correções Críticas e Melhorias de UX/UI/CLI

---

## 🔴 CORREÇÕES CRÍTICAS

### 1. ✅ CORRIGIDO: `AttributeError: OLDEST`
**Problema:** Biblioteca `google-play-scraper` não possui `Sort.OLDEST`

**Solução Implementada:**
- Removido `Sort.OLDEST` do mapeamento
- Implementado fallback: coletar com `Sort.NEWEST` e ordenar manualmente por data
- Adicionado tratamento específico para `AttributeError` com retry automático
- Mensagem amigável: "Ordenação 'oldest' não disponível - usando 'newest' + ordenação manual"

**Impacto:** ✅ Crítico resolvido - Reviews "oldest" agora funcionam

---

### 2. ✅ CORRIGIDO: Qualidade média 186.3%
**Problema:** Cálculo incorreto de completude estava somando valores incorretamente

**Solução Implementada:**
```python
# Antes (incorreto):
nao_vazios = df[col].notna().sum() + (df[col] == "").sum()

# Depois (correto):
nao_vazios = ((df[col].notna()) & (df[col] != "")).sum()
qualidade["completude"][col] = min(100.0, max(0.0, (nao_vazios / total * 100)))
```

**Impacto:** ✅ Bug corrigido - Qualidade agora mostra 0-100% corretamente

---

### 3. ✅ CORRIGIDO: Reddit 404 (Autor deletado)
**Problema:** Erro 404 ao acessar perfil de autor deletado interrompia coleta

**Solução Implementada:**
- Criada função `_safe_get_author_attr()` para acesso seguro a atributos do autor
- Tratamento específico de `NotFound` (404) - continua sem interromper
- Valores padrão quando autor não existe: `"[deleted]"` e strings vazias

**Impacto:** ✅ Coleta do Reddit não é mais interrompida por autores deletados

---

## 🟡 MELHORIAS DE UX/UI/CLI

### 4. ✅ Agregador de Erros (Suprime Repetições)
**Implementado:** Classe `ErrorAggregator`
- Agrupa erros similares
- Exibe apenas primeira ocorrência
- Mostra contador quando erro se repete
- Resumo consolidado no final

**Exemplo:**
```
# Antes:
ERROR - Google Play Reviews: Erro inesperado: OLDEST
ERROR - Google Play Reviews: Erro inesperado: OLDEST
[repetido 20x]

# Depois:
ERROR - Google Play Reviews: Erro inesperado: OLDEST
[Erro repetido 20x - suprimindo mensagens futuras]
```

**Impacto:** ✅ Output muito mais limpo e legível

---

### 5. ✅ Mensagens de Erro Mais Amigáveis
**Implementado:**
- Mensagens técnicas convertidas para linguagem amigável
- Explicação do problema e solução aplicada
- Indicadores visuais claros (✓, ⚠, ❌, ℹ, 🔄)

**Exemplos:**
```python
# Antes:
ERROR - AttributeError: OLDEST

# Depois:
⚠ Google Play Reviews: Ordenação 'oldest' não disponível
  → Usando 'newest' como alternativa
  → Reviews serão ordenados manualmente após coleta
```

**Impacto:** ✅ Usuário entende problemas e soluções

---

### 6. ✅ Progresso Mais Informativo
**Implementado:**
- Tempo decorrido por fonte
- Taxa de coleta (itens/segundo)
- Informações contextuais durante progresso

**Exemplo:**
```
✓ YouTube: 20 resultado(s) encontrado(s)
  → Tempo: 3.2s | Taxa: 6.2 itens/s
```

**Impacto:** ✅ Feedback mais rico sobre performance

---

### 7. ✅ Resumo de Erros no Final
**Implementado:**
- Seção dedicada no resumo final
- Lista consolidada de erros/avisos
- Contagem de ocorrências
- Top 10 erros mais frequentes

**Exemplo:**
```
⚠ Resumo de Avisos e Erros:
  ⚠ Google Play Reviews: Ordenação 'oldest' não disponível... (20 ocorrências)
  ⚠ Reddit: Autor deletado/inexistente... (5 ocorrências)
```

**Impacto:** ✅ Visão consolidada de problemas

---

### 8. ✅ Tratamento Melhorado de Rate Limit
**Implementado:**
- Backoff exponencial mais agressivo para Semantic Scholar
- Mensagens informativas sobre rate limit
- Delay progressivo (10s, 20s, 30s... até 60s max)

**Exemplo:**
```
⚠ Google Scholar: Rate limit (429) detectado - aguardando 15s...
```

**Impacto:** ✅ Melhor recuperação de rate limits

---

### 9. ✅ Tratamento de HTTP Errors
**Implementado:**
- Tratamento específico para 429 (rate limit)
- Mensagens diferenciadas por tipo de erro
- Uso de `ErrorAggregator` para evitar spam

**Impacto:** ✅ Erros HTTP tratados de forma inteligente

---

## 📊 COMPARAÇÃO ANTES/DEPOIS

| Aspecto | Antes (v7.2) | Depois (v7.3) |
|---------|--------------|---------------|
| **Erro OLDEST** | ❌ Falha completa | ✅ Fallback automático |
| **Qualidade média** | ❌ 186.3% (bug) | ✅ 0-100% correto |
| **Reddit 404** | ❌ Interrompe coleta | ✅ Continua normalmente |
| **Erros repetidos** | ❌ 20+ mensagens | ✅ 1 mensagem + contador |
| **Mensagens** | ❌ Técnicas | ✅ Amigáveis |
| **Progresso** | ⚠ Básico | ✅ Informativo |
| **Resumo erros** | ❌ Não existe | ✅ Consolidado no final |
| **Rate limit** | ⚠ Retry simples | ✅ Backoff inteligente |

---

## 🔧 MUDANÇAS TÉCNICAS

### Novas Classes/Funções

1. **`ErrorAggregator`**
   - Agrega erros similares
   - Suprime repetições
   - Gera resumo consolidado

2. **`_safe_get_author_attr(post, attr_name, default)`**
   - Acesso seguro a atributos do autor
   - Trata 404, deletados, restritos
   - Retorna valores padrão

### Funções Atualizadas

1. **`coletar_reviews_google_play()`**
   - Fallback para `oldest` (NEWEST + ordenação manual)
   - Tratamento específico de `AttributeError`
   - Retry automático com fallback

2. **`coletar_reddit()`**
   - Uso de `_safe_get_author_attr()`
   - Tratamento de 404 sem interrupção
   - Mensagens mais amigáveis

3. **`coletar_scholar()`**
   - Backoff exponencial melhorado
   - Mensagens informativas sobre rate limit
   - Delay progressivo até 60s

4. **`analisar_qualidade_dados()`**
   - Cálculo de completude corrigido
   - Garantia de valores 0-100%

5. **`coletar_fonte_com_exibicao()`**
   - Progresso mais informativo
   - Tempo e taxa de coleta

6. **`modo_personalizado()`**
   - Resumo de erros no final
   - Métricas consolidadas

---

## 🚀 PRÓXIMAS MELHORIAS (v7.4+)

1. Validação pré-coleta de configurações
2. Fallback alternativo para Apple App Store
3. Investigar e corrigir Google News (0 resultados)
4. Modo quiet/verbose configurável
5. Tratamento de interrupção (Ctrl+C)
6. Indicadores visuais melhorados
7. Estimativas de tempo mais precisas

---

**Versão:** 7.3
**Data:** 2024-12-12
**Status:** ✅ Correções críticas aplicadas



