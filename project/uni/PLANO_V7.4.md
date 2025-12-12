# 📋 PLANO DE MELHORIAS - UNI v7.4
## Padronização, Remoção de Redundâncias e Melhorias UX/UI/CLI

---

## 🎯 OBJETIVOS

1. **Remover símbolos de layout excessivos** (====, ####, ----)
2. **Padronizar menus** conforme anotações do usuário
3. **Padronizar formatação** de prompts, inputs, exibição
4. **Remover redundâncias** de código
5. **Melhorar UX/UI/CLI** para experiência fluida

---

## 📊 ANÁLISE ATUAL

### Problemas Identificados

1. **Símbolos de Layout Excessivos**
   - `print_header()` usa `=====` repetidamente
   - Múltiplos `----` em submenus
   - Inconsistência entre `====`, `----`, `####`

2. **Menus Não Padronizados**
   - Formato varia entre seções
   - Alguns usam `print_header()`, outros não
   - Numeração inconsistente (01., 02., vs sem numeração)

3. **Formatação Inconsistente**
   - Prompts: `>`, `> `, `[default]:`, `[default]`
   - Opções: `1.`, ` 1.`, `[1]`, `1:`
   - Cores: mistura de `cyan()`, `blue()`, `green()`, `yellow()`

4. **Redundâncias**
   - Múltiplas funções similares para exibir menus
   - Código duplicado em `configurar_*`
   - Lógica repetida para validação de inputs

5. **Exibição de Resultados**
   - Formato varia entre fontes
   - Uso excessivo de emojis e símbolos
   - Falta padronização de layout

---

## 🔧 MELHORIAS PROPOSTAS

### 1. Padronização de Layout

**Antes:**
```python
print_header("01. TERMOS DE BUSCA", "=", 70)
print(f"{cyan('Separe múltiplos termos por vírgula')}\n")
```

**Depois:**
```python
print_section("01. Termos de busca")
print_hint("Separe múltiplos termos por vírgula")
```

**Funções Padronizadas:**
- `print_section(title)` - Seção principal (sem símbolos)
- `print_subsection(title)` - Subseção (indentada)
- `print_hint(text)` - Dica/instrução (cinza)
- `print_option(key, label)` - Opção de menu padronizada

---

### 2. Padronização de Menus

**Formato Padrão:**
```
01. Termos de busca
  Separe múltiplos termos por vírgula
> bitcoin

02. Região
  1. Brasil (br)
  2. Estados Unidos (us)
  ...
  t. Todos
> [1]: 
```

**Características:**
- Numeração consistente (01., 02., ...)
- Título sem símbolos
- Instrução em linha separada (cinza)
- Opções numeradas (1., 2., ...)
- "t. Todos" sempre no final
- Prompt padronizado: `> [default]:`

---

### 3. Padronização de Prompts

**Padrão:**
- `> [default]:` para inputs com default
- `> ` para inputs obrigatórios
- `> [s/n] [s]:` para sim/não

**Exemplos:**
```python
input(f"> [bitcoin]: ")  # Com default
input(f"> ")  # Sem default
input(f"> Coletar comentários? (s/n) [s]: ")  # Sim/Não
```

---

### 4. Padronização de Cores

**Esquema de Cores:**
- **Títulos de seção**: `cyan()` ou sem cor
- **Instruções/dicas**: `gray()`
- **Prompts**: `blue()` ou sem cor
- **Opções**: `green()` para "t" (Todos), normal para números
- **Sucesso**: `green()` com ✓
- **Avisos**: `yellow()` com ⚠
- **Erros**: `red()` com ✗

---

### 5. Remoção de Redundâncias

**Consolidar Funções:**
- `print_header()` → `print_section()` (simplificado)
- Múltiplos `print_*` → funções padronizadas
- Lógica de validação → função única
- Formatação de opções → função única

**Exemplo:**
```python
def print_menu_section(title: str, hint: str = None):
    """Exibe seção de menu padronizada"""
    print(f"\n{title}")
    if hint:
        print(f"  {gray(hint)}")

def print_menu_options(options: Dict[str, str], default: str = None):
    """Exibe opções de menu padronizadas"""
    for key, label in options.items():
        marker = green(key) if key == "t" else key
        print(f"  {marker}. {label}")
    if default:
        print(f"\n> [{default}]: ", end="")
```

---

### 6. Padronização de Exibição de Resultados

**Formato Padrão:**
```
✓ Fonte: X resultado(s) encontrado(s)
  → Tempo: Xs | Taxa: X itens/s
```

**Sem emojis excessivos, símbolos consistentes**

---

### 7. Padronização de Salvamento

**Nomes de Arquivos:**
- Padrão: `{fonte}_{termo}_{timestamp}.csv`
- Consolidado: `base_dados_{termo}_{timestamp}.csv`
- Metadados: `metadados_{termo}_{timestamp}.json`

**Estrutura de Diretórios:**
```
dados/
  {termo}/
    {timestamp}/
      por_fonte/
      consolidado/
      metadados/
```

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Funções Base
- [ ] Criar `print_section()` (substitui `print_header()`)
- [ ] Criar `print_subsection()`
- [ ] Criar `print_hint()`
- [ ] Criar `print_menu_options()`
- [ ] Criar `print_prompt()`

### Fase 2: Padronização de Menus
- [ ] Atualizar `configurar_termos()` - formato padrão
- [ ] Atualizar `configurar_regioes()` - formato padrão
- [ ] Atualizar `configurar_plataformas()` - formato padrão
- [ ] Atualizar `configurar_suggest()` - formato padrão
- [ ] Atualizar `configurar_trends()` - formato padrão
- [ ] Atualizar `configurar_serp()` - formato padrão
- [ ] Atualizar `configurar_youtube()` - formato padrão
- [ ] Atualizar `configurar_app_stores()` - formato padrão

### Fase 3: Padronização de Exibição
- [ ] Padronizar `exibir_resultados_tempo_real()`
- [ ] Padronizar mensagens de progresso
- [ ] Padronizar mensagens de sucesso/erro
- [ ] Remover emojis excessivos

### Fase 4: Padronização de Salvamento
- [ ] Padronizar nomes de arquivos
- [ ] Padronizar estrutura de diretórios
- [ ] Padronizar formato de CSVs

### Fase 5: Remoção de Redundâncias
- [ ] Consolidar funções de formatação
- [ ] Remover código duplicado
- [ ] Simplificar lógica repetida

---

## 🎨 EXEMPLOS DE TRANSFORMAÇÃO

### Exemplo 1: Menu de Termos

**Antes:**
```python
print_header("01. TERMOS DE BUSCA", "=", 70)
print(f"{cyan('Separe múltiplos termos por vírgula')}\n")
termos_input = input(f"{blue('>')} ").strip()
```

**Depois:**
```python
print_section("01. Termos de busca")
print_hint("Separe múltiplos termos por vírgula")
termos_input = input_prompt("bitcoin")
```

---

### Exemplo 2: Menu de Regiões

**Antes:**
```python
print_header("02. REGIÃO", "=", 70)
for key, value in opcoes.items():
    if key == "t":
        print(f"  {green('t')}. {value}")
    else:
        print(f"  {key}. {value}")
print()
selecionados = input_multiple_choice(f"{blue('>')}", opcoes, ["1"], True)
```

**Depois:**
```python
print_section("02. Região")
print_menu_options(opcoes)
selecionados = input_multiple_choice("1", opcoes)
```

---

### Exemplo 3: Exibição de Resultados

**Antes:**
```python
print(f"{green('✓')} {fonte_nome}: {len(resultados_validos)} resultado(s) encontrado(s)")
print(f"  {gray(f'→ Tempo: {elapsed:.1f}s | Taxa: {taxa:.1f} itens/s')}")
```

**Depois:**
```python
print_success(f"{fonte_nome}: {len(resultados_validos)} resultado(s) encontrado(s)")
print_info(f"Tempo: {elapsed:.1f}s | Taxa: {taxa:.1f} itens/s")
```

---

## 📊 MÉTRICAS DE SUCESSO

- [ ] Redução de 50%+ no uso de símbolos de layout
- [ ] 100% dos menus seguem formato padrão
- [ ] 100% dos prompts seguem formato padrão
- [ ] Redução de 30%+ em código duplicado
- [ ] Experiência de usuário mais fluida e consistente

---

**Versão:** 7.4
**Data:** 2024-12-12
**Status:** 📋 Planejamento completo



