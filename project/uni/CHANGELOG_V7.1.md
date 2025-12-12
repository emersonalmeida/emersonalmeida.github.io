# 📋 CHANGELOG - UNI v7.1
## Melhorias de Configuração Implementadas

---

## ✅ MELHORIAS IMPLEMENTADAS

### 1. ✅ Mapeamento Automático de Idioma por Região
- **Implementado:** Função `mapear_idioma_por_regiao()`
- **Mapeamento:** br→pt-BR, us→en-US, fr→fr-FR, de→de-DE, jp→ja-JP, es→es-ES, it→it-IT, uk→en-GB
- **Uso:** Automático ao selecionar regiões
- **Benefício:** Elimina passo manual de escolha de idioma

### 2. ✅ Respeitar Ordem de Seleção
- **Implementado:** `input_multiple_choice()` mantém ordem original
- **Aplicado em:**
  - YouTube ordenação de vídeos
  - YouTube ordenação de comentários
  - App Store lojas
  - App Store ordenação de reviews
  - Suggest navegadores, fontes, tipos
- **Benefício:** Usuário controla ordem de coleta

### 3. ✅ Coleta por Item
- **YouTube:** Coleta X vídeos por cada ordenação (não total)
- **App Store:** Coleta X apps por cada loja (não total)
- **Reviews:** Coleta X reviews por app por ordenação
- **Comentários:** Coleta X comentários por vídeo por ordenação
- **Benefício:** Muito mais dados coletados

### 4. ✅ Atalho "t" para Todos
- **Implementado:** Aceita "t" ou "todos" em todas as seleções
- **Aplicado em:** Todas as funções `input_multiple_choice()`
- **Benefício:** UX mais fluida

### 5. ✅ Limites Máximos Inteligentes
- **Implementado:** `input_int()` com parâmetros `limite_max_fonte`
- **Comportamento:** Ajusta automaticamente se solicitado > máximo
- **Feedback:** Avisa quando ajusta limite
- **Benefício:** Evita erros e otimiza coleta

### 6. ✅ Validação de Entradas
- **Implementado:** Validação robusta em `input_int()` e `input_multiple_choice()`
- **Features:**
  - Valida range de números
  - Valida seleções múltiplas
  - Mensagens de erro claras
- **Benefício:** Previne erros de configuração

### 7. ✅ Categorias de Suggest
- **Implementado:** Função `categorizar_suggest()`
- **Categorias:**
  - Top (maior relevância)
  - A-Z (começam com letras)
  - 0-9 (começam com números)
  - Outros (questões, preposições, comparações)
- **Uso:** Filtra sugestões por categoria
- **Benefício:** Organização melhor dos dados

---

## 🔧 MUDANÇAS TÉCNICAS

### Funções Atualizadas

1. **`mapear_idioma_por_regiao(regioes: List[str]) -> Dict[str, str]`**
   - Novo: Mapeia automaticamente idioma para cada região

2. **`input_multiple_choice()`**
   - Atualizado: Aceita "t" para todos
   - Atualizado: Mantém ordem original da entrada
   - Melhorado: Validação mais robusta

3. **`input_int()`**
   - Atualizado: Parâmetros `fonte` e `limite_max_fonte`
   - Novo: Ajuste automático de limites
   - Novo: Feedback quando ajusta

4. **`categorizar_suggest(sugestao: str) -> str`**
   - Novo: Categoriza sugestões automaticamente

5. **`coletar_suggest()`**
   - Atualizado: Parâmetro `tipo` para filtrar categorias
   - Novo: Campo `categoria` nos resultados

### Lógica de Coleta Atualizada

- **YouTube:** Respeita ordem de ordenações, coleta por ordenação
- **App Store:** Respeita ordem de lojas, coleta por loja
- **Reviews/Comentários:** Respeita ordem de ordenações, coleta por ordenação
- **Suggest:** Usa idioma mapeado automaticamente

---

## 📊 EXEMPLOS DE USO

### Exemplo 1: Múltiplas Regiões
```
Regiões: 1,2 (Brasil, Estados Unidos)
→ Idiomas mapeados: br→pt-BR, us→en-US
→ Coleta usa idioma correto para cada região
```

### Exemplo 2: Ordem de Coleta YouTube
```
Ordenação: 3,2,1 (Visualizações, Data, Relevância)
→ Coleta nessa ordem exata
→ 20 vídeos por visualizações + 20 por data + 20 por relevância = 60 total
```

### Exemplo 3: App Store com Múltiplas Lojas
```
Lojas: 2,1 (Apple, Google Play)
→ Coleta nessa ordem
→ 20 apps Apple + 20 apps Google = 40 total
→ 100 reviews por app por ordenação
```

### Exemplo 4: Limite Ajustado
```
Limite solicitado: 1000 vídeos
Limite máximo YouTube: 50
→ Ajustado automaticamente para 50
→ Aviso: "⚠ YouTube: Limite ajustado de 1000 para 50"
```

---

## 🚀 PRÓXIMAS MELHORIAS (v7.2+)

1. Padrão hierárquico completo para outras fontes (Reddit, News, etc)
2. Feedback visual melhorado com barras de progresso por item
3. Defaults inteligentes baseados em histórico
4. Validação de configuração antes de iniciar
5. Preview de configuração antes de confirmar

---

**Versão:** 7.1
**Data:** 2024-12-12
**Status:** ✅ Implementado e testado



