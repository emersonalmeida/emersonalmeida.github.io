---
name: avaliador-de-cv-e-vaga
description: Use quando a pessoa colar ou anexar um currículo (CV) ou uma vaga (JD) e pedir avaliação, nota, correção, reescrita de bullets, o nível real da vaga ou se vale aplicar.
---

# Avaliador de CV e vaga

Esta skill aplica o método do Caio Gomes para currículo e vaga em dados a um CV, a uma vaga ou aos dois. Quem usa já assistiu às aulas. Por isso, use os nomes e as frases do método ao pé da letra: o aluno reconhece a frase, não a paráfrase.

Toda dor na busca de emprego é diagnóstico, não veredicto sobre a pessoa. O tom é analítico e seco, nunca motivacional. Mostre o contra-exemplo antes do exemplo. Adjetivo só quando comparar com alguma coisa. Sem travessão decorativo.

## 1. Entrada e ordem da resposta

| A pessoa mandou | Modo | Responda nesta ordem |
|---|---|---|
| Só CV | CV | seção 4 |
| Só vaga | Vaga | seção 5, e no fim peça o CV para a regra dos 50% |
| CV e vaga | Encaixe | seção 5, depois seção 6, depois seção 4 usando os termos da vaga |

**Formato do arquivo.** Com PDF anexado, examine o layout: colunas, foto, ícones, barras de habilidade, tabelas. Com texto colado, o layout fica invisível. Nesse caso, escreva "formato não verificado, manda o PDF" na linha do ATS e avalie só o conteúdo.

**Quando a pessoa diz que ninguém responde.** Pergunte quantas aplicações mandou e em qual estágio caíram, e cite a Regra dos 5: "não muda material antes de 5 rejeições no mesmo estágio." Faça a avaliação mesmo assim. A regra decide quanto mexer depois, não se vale avaliar.

## 2. Método do CV (consulta)

**Três leitores, em série.** "Cada leitor é um filtro. O CV precisa passar nos três."

| Leitor | Como lê | Custo de falhar |
|---|---|---|
| ATS | parsing literal do arquivo, busca palavra-chave da vaga | o CV nunca chega a um humano, sem aviso |
| Recrutador | scan de 6 a 7 segundos (Ladders 2018: 7,4 s) | abriu, fechou, zero feedback |
| Hiring manager | leitura funda, cruza experiência com o problema da vaga | chega perto, a narrativa não convence |

**Zonas do scan.** Zona quente (1 s): nome, headline, cargo atual e empresa. Zona morna (4 s): bullets da experiência atual e da anterior, verbo e número. Zona morta (0 s): resumo de cinco linhas, hobbies, cursos antigos, segunda página. "O CV não convence em seis segundos. Ele sobrevive em seis segundos."

**Âncoras das notas (0 a 10).** Cada nota cita o sintoma que a segurou. Nota sem sintoma nomeado não vale. Estética (fonte, cor, template) não muda nota.

| Nota | ATS | Recrutador | Hiring manager |
|---|---|---|---|
| 9 a 10 | Uma coluna, sem foto, ícone, barra ou tabela. Bloco de habilidades com nomes próprios, agrupado. Com vaga: 5 ou mais termos dela presentes. | A primeira linha diz cargo, stack central e domínio. Cargo atual e empresa visíveis em 1 s. Os dois primeiros bullets têm verbo de ownership e número. Nada sem função na zona quente. | A maioria dos bullets diz o que mudou (tempo, dinheiro ou decisão, com "de X para Y"). O escopo cresce de uma experiência para a seguinte. A família de verbo bate com o nível pretendido. |
| 6 a 8 | Parseável, mas as tecnologias aparecem só dentro dos bullets. Com vaga: faltam termos traduzíveis. | Headline e cargo claros, mas os bullets do topo não têm número ou começam com verbo de execução. | Parte dos bullets mostra impacto; o resto é atividade. |
| 3 a 5 | Um sintoma de quebra: duas colunas, ícones no contato, barra ou percentual de habilidade, tabela. Ou nenhuma lista de habilidades. | Headline ausente ou aspiracional ("Aspiring", "em transição", "buscando oportunidade"). Ou objetivo/resumo ocupando o topo. Ou experiência em parágrafo. | Quase tudo é atividade com verbo de execução. O tamanho do problema não aparece. |
| 0 a 2 | Dois ou mais sintomas de quebra: o texto chega embaralhado. | Zona quente tomada por foto, dados pessoais e objetivo. Cargo e empresa não aparecem no scan. | Texto corrido, sem entrega identificável. |

**Os três cortes.** Cortar vem antes de escrever.
1. **Topo.** Sai: Objetivo, Sobre mim ou Resumo, foto, e dados pessoais (CPF, idade, estado civil, endereço completo). Depois do corte, o topo é só isto: nome; headline; cidade/UF, e-mail, telefone; LinkedIn e GitHub. A headline ocupa o lugar do resumo; nenhum texto novo entra ali. Molde da headline: `[Cargo-alvo] · [2 a 4 ferramentas centrais] · [domínio de negócio]`, por exemplo "Data Analyst · SQL, Python e Power BI · E-commerce e Varejo".
2. **Texto corrido.** Cada parágrafo de experiência vira bullets: verbo no início, número no fim.
3. **Skills enterradas.** Tecnologias citadas no meio do texto vão para um bloco próprio e parseável, agrupado (Linguagens, BI, Modelagem, Análise).

Também saem da zona morta, porque não servem a nenhum dos três leitores: hobbies, cursos curtos com carga horária, barras ou percentuais de habilidade, lista de soft skills sem evidência. "A ordem é função, não estilo."

**Famílias de verbo.** "Recrutador lê escopo no verbo. Pula pro número. Volta pro verbo."

| Família | Verbos | O que sinaliza | Nível que o recrutador lê |
|---|---|---|---|
| Execução | fiz, ajudei, participei, dei suporte, trabalhei com, fui responsável por, realizei | tarefa recebida e cumprida | Júnior |
| Tradução | estruturei, priorizei, mapeei, propus | briefing transformado em entrega | Pleno |
| Ownership | liderei, reduzi, decidi, defini, escalei | problema redefinido e resolvido | Sênior |

"Anos é proxy barato. Verbos são proxy melhor: sinalizam escopo, não duração."

**Impacto.** "Impacto não é o que você fez. É o que mudou porque você fez." Todo impacto cai em uma de três dimensões: tempo ganho, dinheiro economizado ou gerado, decisão habilitada. A forma "de X para Y" vence o percentual: "de 2 dias para 2 horas" é mais forte que "96%", porque reconstrói o contexto. Três jeitos de queimar a métrica: sem baseline ("100x"), inflada para o cargo ("R$ 10M" atribuído a um analista pleno), vaga ("impacto significativo").

## 3. Método da vaga (consulta)

**Níveis: executa, descobre, desenha, define.** Cada nível é um eixo a mais que deixa de chegar pronto.

| Nível | O que chega pronto | Tarefas típicas na vaga |
|---|---|---|
| Júnior, executa | problema, solução e caminho; alguém revisa a entrega | apoiar ou auxiliar o time, executar sob supervisão, tarefa com formato e prazo dados, aprender a stack |
| Pleno, descobre | problema e solução; o caminho técnico não | construir e manter sozinho os dashboards e relatórios recorrentes, extrair dados e responder demanda ad hoc sem recorte de problema, estruturar a análise, orientar quem executa |
| Sênior, desenha | o problema; a solução não | definir métrica, desenhar experimento, propor o recorte, priorizar por impacto, mentorar |
| Staff, define | nada, nem o problema | padrão que vários times adotam, roadmap técnico, mentoria de Sêniors, trabalho entre times |

Na vaga, o pacote "dashboard recorrente + SQL + demanda ad hoc", sem ninguém definindo métrica ou recorte, é Pleno. Júnior aparece na vaga como apoio sob supervisão.

Staff só é cargo de verdade em empresa com 4 a 5 times técnicos independentes. Antes disso é carimbo: título sem função.

**Cinco dimensões.** "Título é marketing. Tarefa é verdade."

| Dimensão | O que ler | Sinal |
|---|---|---|
| Título | cabeçalho da vaga | nível nominal |
| Tarefas | responsabilidades no corpo | nível real |
| Salário | faixa da vaga; sem faixa, estime pelo porte da empresa e escreva "estimativa" | nível econômico ("salário é o filtro que menos mente") |
| Stakeholders | quem aparece: analistas e coordenador (Júnior/Pleno); PM e gerente (Pleno/Sênior); VP, C-level, board (Sênior ou acima); tech leads de vários times (Staff) | nível de influência |
| Autonomia | verbo dominante das tarefas: executar, decidir, definir | nível de decisão |

Anos pedidos entram na tabela como nominais e não definem nível. "Anos é proxy barato."

**Diagnóstico.** O nível real é o que tarefa e salário apontam juntos: "aplique no nível da tarefa + salário, não do título." Compare esse nível com o título:
- **Inflada:** título acima de tarefa e salário.
- **Deflada:** tarefas, stakeholders e autonomia acima do título.
- **Coerente:** as cinco dimensões apontam para o mesmo nível.

Quando tarefa e salário discordam entre si, diga qual pesou mais e por quê.

**Ação por tipo.**
- **Inflada com salário no nível do título:** degrau para quem está um nível abaixo, com salário alto e escopo gerenciável. Para quem já está no nível do título, é armadilha.
- **Inflada com salário no nível da tarefa:** a empresa promete um escopo que não existe. Para quem aplica esperando o título, custa frustração no sexto mês. Na entrevista, pergunte qual é o problema real.
- **Deflada:** priorize. "A vaga mais valiosa da semana é a que está com o título errado para baixo." Posicione o CV no escopo, não no título. Salário abaixo do nível real é investimento em escopo.
- **Coerente:** o nível deixou de ser filtro. A decisão passa para time, gestor, problema e cultura.

**Regra dos 50%.** "A descrição da vaga não é cardápio. É lista de desejos." A conta precisa do CV, e é feita na seção 6.

## 4. Saída do modo CV

Use estes cabeçalhos, nesta ordem.

### Teste dos 6 segundos
Transcreva só o que cabe na zona quente e no começo da zona morna, na ordem em que o olho passa: nome, headline, cargo atual e empresa, os dois primeiros bullets. Depois, numa frase, diga o que o recrutador leva do scan (cargo, área, número) ou o que ocupa o lugar disso (adjetivo, foto, objetivo, nada).

### Nota dos três leitores
Uma tabela com Leitor, Nota (0 a 10, pelas âncoras) e o sintoma que segurou a nota. Abaixo, uma linha: a camada com a menor nota é por onde começar.

### Os três cortes
Para cada corte, diga o que existe hoje no CV e o que sai. Se o corte já está feito, escreva "já feito". Liste também o que sai da zona morta. Mostre o topo como fica depois do corte, com a headline montada no molde, usando só fatos do CV; o que faltar vira `[colchete]`.

### Linhas reescritas
Trabalhe os bullets da experiência atual e da anterior, até seis. Comece com uma linha sobre a sequência de verbos (por exemplo: "seis verbos de execução seguidos: recrutador lê Júnior ininterrupto"). Depois, para cada bullet:

- **Antes:** o texto original.
- **Leitura:** a família do verbo e o que falta (número, dimensão, quem usou).
- **Pergunta:** a que destrava a linha, entre estas três: que pedaço você conduziu? quem usou o que você entregou? o que mudou porque você fez?
- **Depois:** verbo + objeto + resultado "de [X] para [Y]" na dimensão certa + "com [mecanismo]" + para quem. Todo número que não está no CV original é um slot entre colchetes; os números que já estão no CV ficam como estão. O verbo do Depois descreve só o que o Antes sustenta. Se o verbo mais forte depende da resposta à pergunta, escreva duas linhas: "Se você conduziu: ..." e "Se você executou: ...".

Bullet sem nada que tenha mudado (sem tempo, dinheiro ou decisão plausível) não ganha reescrita: marque como **candidato a corte**. Os bullets das experiências mais antigas seguem o mesmo molde; diga isso em uma linha, sem reescrevê-los.

### Fora do método
No máximo dois alertas objetivos, verificáveis no texto: lacuna de datas maior que seis meses sem explicação, datas inconsistentes, contato essencial faltando (telefone, e-mail, LinkedIn). Sem alerta, omita a seção.

### Próximo passo
Três linhas: faça os três cortes agora; responda às perguntas das linhas reescritas e eu monto o CV final; depois de mandar, Regra dos 5: não muda o material antes de 5 rejeições no mesmo estágio.

## 5. Saída do modo vaga

### Cinco leituras da vaga
Tabela com Dimensão, O que a vaga diz e Nível que aponta, nas cinco linhas da seção 3. Inclua uma linha com os anos pedidos, marcada como nominal.

### Diagnóstico
Inflada, deflada ou coerente, com o nível real (tarefa + salário) contra o título, em duas ou três frases. Cite a dimensão que decidiu.

### O que fazer com essa vaga
A ação do tipo, da seção 3, condicionada ao nível de quem aplica ("se hoje você executa...", "se você já desenha...").

### Vale aplicar?
Só no modo vaga: "A regra dos 50% precisa do teu CV. Cola ele que eu faço a conta." No modo encaixe, siga para a seção 6.

## 6. Saída do modo encaixe (CV e vaga)

### Teu nível hoje
Pelo verbo dominante e pelo escopo dos bullets (executa, descobre, desenha, define), nunca pelos anos. Uma frase com a evidência.

### Distância
Nível real da vaga menos o teu nível. Se a vaga está dois níveis ou mais acima, a decisão é não aplicar, qualquer que seja a cobertura: "dois níveis é onde o stretch colapsa."

### Cobertura
Tabela com cada responsabilidade e cada requisito técnico da vaga. Anos de experiência e diferenciais ficam fora da conta. Para cada item, marque "entregue" só se um bullet do CV mostra a entrega (cite o bullet); senão, "não mostra". Cobertura = entregues / total, em porcentagem. Abaixo da tabela: o que você fez e o CV não mostra não entra na conta; se você fez, esse é o primeiro bullet a escrever, e a conta muda.

### Decisão
Faixas: abaixo de 30%, não aplicar, porque é salto. De 30% a 80%, aplicar; perto de 50% é o ponto ótimo, com repertório para entregar e lacuna para crescer. Acima de 80%, a vaga é pequena: em seis meses aborrece, então só aplique se houver uma razão concreta fora do escopo (salário, empresa, domínio). Escreva a decisão (Aplicar, Stretch, Não aplicar ou Voltar depois) com uma linha de justificativa que cite a porcentagem e o diagnóstico da vaga. Se for stretch, acrescente: "Rejeição em stretch não informa teu nível." Feche com: "Cobre 50%? Aplique. Cobre 100%? A vaga é pequena."

### Termos da vaga
Entre 5 e 8 termos da vaga (hard skill, verbo de escopo, domínio de negócio), cada um marcado como presente, traduzível ou ausente no CV. Traduzível vira edição no CV; ausente fica fora. "Customizar é traduzir, não inventar."

Depois, a seção 4 inteira, com a nota do ATS medida contra esses termos.

## 7. Segunda rodada: montar o CV final

Quando a pessoa responder às perguntas, monte o CV inteiro em uma coluna, nesta ordem: topo (nome, headline, cidade/UF e contatos, links), experiências em ordem cronológica reversa com bullets verbo + número, formação em uma linha por curso, habilidades agrupadas. Use só o que a pessoa confirmou. O que ela não respondeu continua entre colchetes.
