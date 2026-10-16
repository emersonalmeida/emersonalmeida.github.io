# Playbook de Product Design: do problema ao lançamento e à evolução

**Guia prático — atualizado em 6 de outubro de 2026**

## Para quem e para que serve

Este guia organiza o trabalho de Product Design antes, durante e depois de um projeto digital: sistemas, produtos, UX, UI, usabilidade, acessibilidade, pesquisa, estratégia, branding, ideação, prototipagem, validação, documentação, handoff, desenvolvimento, lançamento, marketing, vendas, suporte, métricas e melhoria contínua.

A aplicação principal é um **MVP digital de escopo controlado**, criado por uma equipe multidisciplinar em cerca de um mês, com lançamento acompanhado e evolução nos meses seguintes. O roteiro supõe acesso a pessoas usuárias e decisoras, pelo menos uma pessoa de produto/design e uma de engenharia, infraestrutura de lançamento já disponível ou simples, e autorização para fazer pesquisa. Um mês não torna um produto seguro ou completo por si só: setores regulados, integrações críticas, hardware, riscos físicos, privacidade sensível, pagamentos, IA de alto impacto ou dependências externas podem exigir mais tempo, aprovação e testes.

O cronograma é uma forma de planejar trabalho, não uma promessa de que descoberta, solução e impacto caberão em quatro semanas. Se a pesquisa mostrar que a premissa estava errada, reduzir escopo, adiar lançamento ou mudar a hipótese é uma decisão de produto válida.

## Princípio central: entregar resultado, aprender e assumir responsabilidade

Product Design conecta necessidades humanas, valor para o negócio, viabilidade técnica, qualidade de uso e contexto operacional. O trabalho não termina no Figma nem no lançamento. Um produto é um sistema em operação: pessoas, interfaces, conteúdo, dados, software, infraestrutura, políticas, suporte, marca, distribuição e decisões interagem.

Um projeto deve tornar explícitos:

- **Para quem** existe e quem pode ficar de fora.
- **Qual situação ou necessidade** tenta resolver, com evidências e não somente opinião.
- **Qual resultado** seria valioso para a pessoa e sustentável para a organização.
- **Quais riscos e restrições** existem em tecnologia, negócio, operação, segurança, acessibilidade, dados e prazo.
- **Como saberemos** se a solução ajuda, prejudica ou não muda nada.
- **Quem decide, implementa, atende, mede e mantém** cada parte.

A equipe busca resultados observáveis, não apenas volume de funcionalidades. Discovery e delivery se conectam: a equipe investiga, constrói, testa e aprende em ciclos, em vez de criar uma fase de pesquisa isolada da construção. O [Double Diamond](https://www.designcouncil.org.uk/resources/the-double-diamond/history-of-the-double-diamond/) é uma boa representação de descoberta, definição, desenvolvimento e entrega, com divergência, convergência e iteração; não é uma receita linear. A [ISO 9241-210](https://www.iso.org/standard/77520.html) descreve princípios e atividades de design centrado em pessoas ao longo do ciclo de vida, enquanto a [ISO 9241-220](https://www.iso.org/standard/63462.html) aborda processos organizacionais para sustentá-lo.

## Responsabilidades e colaboração

Product Designer participa da definição do problema, pesquisa e síntese, desenho de interação, conteúdo e estrutura de interface, prototipagem, avaliação, acessibilidade, documentação e acompanhamento. Em equipes maduras, decisões são compartilhadas com produto, engenharia, pesquisa, dados, conteúdo, marca, vendas, suporte, segurança e operação.

| Papel | Contribuição principal | Decisões que deve compartilhar |
|---|---|---|
| Product Designer | Entender necessidades, desenhar e avaliar experiências, estabelecer padrões e acompanhar qualidade de uso | problema, fluxo, acessibilidade, experiência, trade-offs e critérios de qualidade |
| Product Manager/Owner | Estratégia, objetivos, priorização, restrições e coordenação do produto | outcome, escopo, sequência, métricas e investimento |
| Engenharia | Arquitetura, estimativas, implementação, testes, segurança e operação técnica | viabilidade, dependências, qualidade técnica, rollout e rollback |
| Pesquisa/ResearchOps | Planejamento metodológico, recrutamento, ética, sessões e síntese | amostra, evidências, limitações e próximos estudos |
| Conteúdo/Brand/Marketing | Proposta de valor, voz, identidade, informação e distribuição | promessa, posicionamento, conteúdo, marca e campanhas |
| Dados/Analytics | Instrumentação, definições, análise e qualidade dos eventos | funil, coortes, experimento e interpretação de métricas |
| QA/Acessibilidade/Security/Legal | Verificações especializadas, conformidade, risco e mitigação | bloqueios de qualidade, acessibilidade, privacidade, segurança e liberação |
| Vendas/CS/Suporte/Operação | Necessidades do mercado, implantação, atendimento e conhecimento das falhas reais | prontidão, materiais, fluxos de escalonamento e retorno de campo |

Em equipes pequenas, uma pessoa pode acumular papéis; a responsabilidade não desaparece. O Product Designer não é, sozinho, responsável por “fazer o produto dar certo”: autoridade, orçamento, engenharia, aquisição, atendimento e operação precisam estar alinhados ao resultado.

## Antes de começar: preparação e enquadramento

### 1. Receber a demanda e descobrir o pedido real

**Antes:** reunir patrocinador, produto, design, engenharia e quem conhece o atendimento ou a operação. Pedir contexto, origem da demanda, objetivo esperado, prazo, orçamento, limitações e decisões já tomadas.

**Durante:** separar pedido de solução do problema. “Precisamos de um app” é uma proposta; ainda falta entender qual tarefa, necessidade, segmento e resultado justificam o app. Mapear urgência, incentivos e pressupostos de quem solicitou.

**Depois:** registrar entendimento, questões em aberto, risco, pessoas afetadas, sponsor, responsável por decisões e próxima revisão. Se a solicitação é mandatória, documentar a restrição sem fingir que houve descoberta livre.

### 2. Fazer uma triagem de oportunidade, risco e prontidão

Responder em sessão curta:

- Qual mudança ou evidência originou a iniciativa?
- O que acontece hoje? Qual é o custo de manter tudo como está?
- Quem tem o problema, com que frequência, gravidade e alternativas?
- Qual objetivo de negócio e qual benefício para as pessoas estão ligados?
- Já existem produto, concorrentes, dados, reclamações, pesquisas ou protótipos?
- Quais sistemas, parceiros, regras e dados serão afetados?
- Quais dependências ou aprovações podem parar o lançamento?
- O que pode ser testado, automatizado, atendido manualmente ou feito sem software?
- Como a equipe vai observar o produto depois de lançado?

Classificar riscos em produto/mercado, técnico, operacional, segurança/privacidade, legal/regulatório, acessibilidade, marca/reputação e cronograma. A lista inicial não “resolve” os riscos: atribui um responsável e uma forma de investigação.

### 3. Definir um acordo de projeto

Criar um brief de uma página com:

- Problema a investigar, público e contexto de uso.
- Objetivo de produto e objetivo de negócio.
- Outcome principal e métricas de proteção.
- Escopo de primeira versão e não escopo.
- Riscos, dependências e pressupostos.
- Equipe, decisores, capacidade e disponibilidade de usuários.
- Janela de trabalho e data possível de lançamento.
- Critérios de pronto para pesquisa, construção e lançamento.
- Cadência de decisão, comunicação e documentação.

**Portão de decisão:** começar o mês só quando houver uma pergunta relevante, um decisor, acesso razoável a evidências, capacidade de construção e acordo sobre o que pode ser lançado. Caso contrário, o trabalho inicial é reduzir incerteza e conquistar essas condições.

## Fluxo de ponta a ponta com antes, durante e depois

### Etapa A — Observação e pesquisa

**Objetivo:** entender o comportamento atual, as necessidades, as barreiras e o contexto, sem induzir pessoas a confirmar a solução desejada.

**Antes da pesquisa**

1. Transformar dúvidas em perguntas pesquisáveis.
2. Separar o que já se sabe, o que se supõe e o que precisa ser decidido.
3. Escolher método compatível com a dúvida: observação contextual para comportamento e ambiente; entrevista para história e significado; análise de atendimento para problemas recorrentes; survey para estimar distribuição; teste para avaliar uma solução; análise de uso para padrões de comportamento real.
4. Definir segmentos, critérios de recrutamento, acessibilidade, compensação, consentimento, privacidade e gravação.
5. Escrever roteiro neutro, tarefas, protocolo, plano de notas e plano de síntese.
6. Fazer piloto do roteiro e confirmar tecnologia, ambiente e acessibilidade da sessão.

**Durante**

- Observar o que a pessoa faz, não somente o que diz que faria.
- Pedir que mostre a última vez que lidou com a situação; usar artefatos e dados reais quando permitido.
- Perguntar “o que aconteceu depois?”, “o que tornou isso difícil?” e “como resolveu?”.
- Não explicar a interface antes da hora quando o objetivo é medir descoberta ou compreensão.
- Fazer perguntas curtas, evitar indução e permitir que a pessoa recuse perguntas ou encerre a sessão.
- Registrar evidência, interpretação e dúvida como itens distintos.
- Convidar produto, design, engenharia e suporte a observar diretamente, preservando privacidade e conforto dos participantes.

**Depois**

- Debrief imediato: fatos lembrados, surpresas, contradições, limites do método e novas perguntas.
- Agrupar evidências por padrão, contexto, severidade e segmento; manter vínculo com a fonte original.
- Não transformar poucos relatos qualitativos em estimativa de prevalência populacional.
- Compartilhar achados com equipe e decidir qual ação muda no backlog, escopo ou hipótese.
- Armazenar gravações e dados conforme consentimento, retenção definida e política aplicável.

O [manual GOV.UK sobre pesquisa](https://www.gov.uk/service-manual/user-research/plan-user-research-for-your-service) recomenda planejar rodadas e envolver a equipe na observação; a quantidade de participantes depende da pergunta e do método, e estudos qualitativos pequenos não substituem levantamentos quantitativos. Veja também as orientações sobre [pesquisa contextual e observação](https://www.gov.uk/service-manual/user-research/contextual-research-and-observation) e [pesquisa na descoberta](https://www.gov.uk/service-manual/user-research/user-research-in-discovery).

### Etapa B — Síntese, descobertas e definição

**Objetivo:** passar de dados a decisões sem apagar divergências nem exagerar a certeza.

Usar evidências de entrevistas, observação, métricas, atendimento, vendas, mercado e tecnologia. Separar:

- **Observação:** algo que foi visto ou medido.
- **Achado:** padrão interpretado a partir de evidências.
- **Necessidade/oportunidade:** progresso que a pessoa tenta alcançar, incluindo barreiras.
- **Insight:** interpretação que altera entendimento ou decisão.
- **Hipótese:** explicação que ainda precisa ser testada.
- **Decisão:** escolha feita, responsável e condição para revisá-la.

Técnicas úteis: mapa de jornada atual, mapa de serviço, análise de tarefas, afinidade, Jobs to Be Done, mapa de oportunidade/Opportunity Solution Tree, mapa de suposições, árvore de problemas, 5 porquês com cautela, análise de funil e análise de reclamações. Personas só ajudam se representarem diferenças de comportamento relevantes e tiverem evidência; não devem substituir pesquisa nem virar estereótipo decorativo.

Escrever uma definição testável:

> Para **[grupo/contexto]**, que precisa **[necessidade ou progresso]**, hoje **[barreira/alternativa]** produz **[consequência observável]**. Vamos explorar **[oportunidade]** e saber que houve melhoria quando **[resultado e métrica]**, sem piorar **[guardrail]**.

**Depois:** verificar entendimento com equipe e decisor; anotar o que não sabemos; rever escopo à luz das evidências; criar uma lista curta de oportunidades ordenadas por importância, confiança e risco. Uma “descoberta” é uma explicação sustentada que muda escolha, não uma frase de workshop.

### Etapa C — Estratégia, posicionamento, marca e conceito

Produto e marca se sustentam mutuamente. Estratégia esclarece para quem o produto existe, qual benefício promete, por que alguém escolheria e como a organização pode entregar esse valor. Branding dá expressão, reconhecimento, tom e coerência; não corrige uma proposta sem valor nem uma jornada que falha.

**Antes:** pesquisar categoria, concorrentes diretos e substitutos, alternativas improvisadas, linguagem do público, limites da marca e riscos de diferenciação vazia.

**Durante:** explicitar posicionamento, proposta de valor, promessa verificável, razões para acreditar, personalidade, voz, narrativa, princípios de experiência e conceito visual/verbal. Explorar alternativas contrastantes e testar compreensão, credibilidade, distinção e relevância.

**Depois:** registrar decisões e exemplos de aplicação; alinhar nome, identidade, interface, campanha, onboarding, venda e suporte. Se identidade visual completa não é essencial ao MVP, definir um kit mínimo consistente e planejar refinamento.

### Etapa D — Ideação e priorização

**Antes:** levar ao workshop um desafio já baseado em evidências, as restrições conhecidas, os critérios de escolha e as pessoas certas. Evitar ideação antes de definir o problema.

**Durante:** divergir primeiro, depois combinar, criticar e selecionar. Gerar mais de uma solução; mapear o fluxo completo; incluir alternativas sem software, operação manual e conteúdo. Usar desenho, papel e caneta, quadro, cartões ou ferramenta simples.

**Depois:** converter conceitos promissores em hipóteses e experimentos. Priorizar valor para a pessoa, resultado de negócio, evidência, esforço, risco, acessibilidade e dependências. RICE, MoSCoW, impacto/esforço e matrizes valor/risco são apoios de conversa, não máquinas objetivas de decisão.

Perguntas para priorizar:

- Qual oportunidade tem evidência mais forte e dor relevante?
- Que solução resolve a tarefa inteira e quais casos ficam descobertos?
- Qual é a menor experiência que testa a hipótese sem transferir custo injusto para usuário ou suporte?
- O que pode falhar, excluir ou causar dano?
- O que devemos deliberadamente não construir agora?

### Etapa E — Arquitetura, fluxos, conteúdo e interface

**Antes:** confirmar tarefas, conteúdo, dados, regras de negócio, estados, dispositivos, padrão de marca e limitações técnicas. Reutilizar design system onde ele satisfaz o contexto; não copiar componentes sem confirmar comportamento e acessibilidade.

**Durante:** modelar navegação, arquitetura da informação, fluxo principal e exceções, conteúdo, controles, hierarquia, feedback, permissões, estados e mensagens. Desenhar para telas pequenas e grandes quando a plataforma exigir. Definir vazio, carregamento, erro, sucesso, indisponibilidade, cancelamento, confirmação, expiração, permissões e recuperação.

**Depois:** percorrer fluxo como pessoa usuária e como sistema: dados errados/incompletos, baixa conectividade, uso por teclado/leitor de tela, zoom, orientação, múltiplos idiomas, atraso, falha de pagamento, tentativa duplicada e suporte. Identificar o que precisa de decisão técnica ou operacional.

### Etapa F — Prototipagem, teste e validação

**Antes:** declarar o que o teste deve descobrir, qual decisão será afetada, quem participa, qual protótipo é suficiente, tarefas e critérios de observação. Prototipar a incerteza mais perigosa primeiro.

**Durante:** pedir que a pessoa realize tarefas plausíveis em contexto; observar sem ensinar; capturar erros, hesitação, entendimento e estratégias. Avaliar protótipos de baixa fidelidade para estrutura e conceitos; alta fidelidade para interação, visual, conteúdo e estados. Fazer avaliação de acessibilidade com teclado, leitor de tela e outros recursos pertinentes, além de ferramentas automatizadas.

**Depois:** classificar problemas por impacto na tarefa, alcance, recorrência e risco; decidir corrigir, testar de novo, aceitar com mitigação ou remover escopo. Documentar achados e mudanças. Uma amostra pequena pode detectar problemas graves, mas não estima satisfação de todo o mercado.

### Etapa G — Construção, documentação e handoff

Handoff não é despejar arquivo. É colaboração contínua entre design, produto e engenharia para preservar intenção enquanto se resolve viabilidade.

**Documentação mínima viva**

- Problema, outcome, público, escopo e decisões.
- Fluxos, regras, estados, permissões, casos extremos e conteúdo aprovado.
- Protótipos e componentes, referências de comportamento e responsividade.
- Tokens, tipografia, espaçamento, cores, ícones e assets, se aplicável.
- Critérios de aceite e definição de pronto.
- Requisitos de acessibilidade, privacidade e segurança.
- Eventos de analytics, nomes, propriedades, momento de disparo e finalidade.
- Dependências, riscos conhecidos, comportamentos ainda não definidos e plano de fallback.

**Antes da implementação:** conversar com engenharia sobre arquitetura e cenários; revisar esforço e dependências; selecionar critérios de aceite observáveis. **Durante:** responder dúvidas, revisar incrementos e decisões de implementação; ajustar protótipo quando a realidade técnica revela alternativa melhor. **Depois:** comparar build com comportamento esperado, testar na plataforma real e registrar desvios aceitos.

### Etapa H — Testes, qualidade e prontidão de lançamento

Prontidão é multidisciplinar. O checklist depende de produto e risco, mas costuma cobrir:

- Fluxos críticos funcionam de ponta a ponta em dispositivos/navegadores suportados.
- Testes funcionais, regressão, segurança, desempenho, carga e integração conforme risco.
- Conteúdo, estados, links, assets e mensagens revisados.
- Acessibilidade manual e automatizada, com escopo e limitações registrados.
- Privacidade, consentimentos, finalidade e retenção; dados de teste não expõem dados reais.
- Analytics e eventos validados ponta a ponta; painel e responsável definidos.
- Suporte treinado, FAQ e base de conhecimento preparados.
- Marketing, vendas e sucesso do cliente sabem o que é lançado, para quem, limitações e promessa.
- Alertas, logs, rota de escalonamento, incidentes, rollback e responsáveis disponíveis.
- Plano de lançamento: flag, cohort, região ou porcentagem; comunicação interna e externa; horário; critérios para pausar.

O [checklist de lançamento do Google SRE](https://sre.google/sre-book/launch-checklist/) inclui capacidade, dependências externas, limites de taxa, timeouts, retentativas, monitoração, volume esperado e picos. A preparação deve corresponder ao risco do serviço.

### Etapa I — Lançamento, divulgação, venda e suporte

**Antes:** combinar a promessa pública com a capacidade real do produto; preparar demonstração, página, conteúdo, materiais de vendas e suporte; listar dúvidas e objeções; instrumentar fluxo; definir responsáveis pela decisão de interromper o rollout.

**Durante:** liberar por etapas quando viável; acompanhar erros, conversão e suporte; observar primeiras sessões e relatos; evitar interpretar oscilações iniciais sem volume ou contexto; comunicar status conhecido sem esconder limitações. Se ocorrer dano, indisponibilidade ou erro em fluxo crítico, mitigar primeiro e investigar depois.

**Depois:** confirmar operação, entregas de campanha, qualidade de eventos e rotas de suporte; criar registro do que ocorreu; realizar revisão sem culpabilização; atualizar FAQ, backlog, métricas e comunicação.

Marketing e vendas conectam descoberta de mercado, posicionamento, canais, aquisição e expectativa. Product Design ajuda a garantir que promessa, onboarding e experiência correspondam. Vendas/CS trazem padrões de perguntas e objeções; suporte traz falhas e esforço de recuperação. Essas entradas devem voltar a discovery com consentimento e tratamento apropriado dos dados.

### Etapa J — Acompanhamento, análise, aprendizados e evolução

Não esperar um trimestre para ver se a instrumentação funciona. A primeira leitura ocorre após liberação, mas decisões sobre retenção ou valor precisam de volume e janela adequados.

1. Monitorar falhas, latência, disponibilidade, segurança e eventos críticos desde o lançamento.
2. Acompanhar ativação e sucesso da tarefa inicial, não só instalações ou cadastros.
3. Observar retenção, repetição de tarefa, conversão, cancelamento e suporte por segmento/coorte.
4. Rever feedback qualitativo, tickets e observações junto das métricas.
5. Comparar resultados a uma baseline ou hipótese previamente registrada.
6. Distinguir correlação, efeito sazonal, erro de tracking e causalidade.
7. Decidir manter, corrigir, experimentar, ampliar, reposicionar ou retirar.
8. Atualizar roadmap e compartilhar o aprendizado com quem tomou a decisão.

## Cronograma de quatro semanas para chegar a um primeiro lançamento

### Pré-início: 3–5 dias úteis de preparação, antes do relógio do projeto

Confirmar sponsor e responsável; levantar dados e tickets; recrutar participantes; aprovar consentimentos; mapear sistemas, riscos, acessos e dependências; configurar analytics; montar equipe e calendário; preencher brief inicial. Se isso não for possível, a semana 1 precisa resolver prontidão, e o lançamento pode sair do mês.

### Semana 1 — Entender, observar e escolher o problema

| Dia | Design/produto/pesquisa | Engenharia/dados/operação | Saída/decisão |
|---|---|---|---|
| 1 | Kickoff, objetivos, restrições, suposições, escopo de pesquisa | Dependências, arquitetura atual, riscos, instrumentação existente | Brief, perguntas de pesquisa e decision log |
| 2 | Desk research, análise de mercado, jornada atual, roteiro e recrutamento | Viabilidade inicial, fontes de dados e integração | Mapa do que se sabe e lacunas |
| 3 | Entrevistas/observação e leitura de suporte/vendas | Eng observa sessões, valida risco e capacidades | Evidências brutas e padrões iniciais |
| 4 | Mais sessões, síntese colaborativa e contraste de casos | Revisa métricas, dados, restrições e segurança | Achados, contradições e hipóteses |
| 5 | Workshop de definição e priorização | Estima risco/esforço, confirma rota técnica | Problema, segmento, outcome, guardrails e escopo preliminar |

**Gate da semana 1:** todos conseguem explicar o mesmo problema e outcome? Há uma hipótese testável? O público está acessível? O risco e o escopo cabem no restante do mês? Se não, renegociar antes de produzir UI extensa.

### Semana 2 — Explorar conceitos e testar direção

| Dia | Design/produto/pesquisa | Engenharia/marketing/suporte | Saída/decisão |
|---|---|---|---|
| 6 | Ideação individual e em grupo, alternativas | Avalia opções de integração e operação | 2–4 conceitos com hipóteses |
| 7 | Priorização por valor, risco, evidência e acessibilidade | Estima capacidade, identifica dependências | Solução candidata e não escopo |
| 8 | Fluxos, arquitetura, conteúdo e wireframes | Define contratos, modelo de dados e instrumentação | Fluxo ponta a ponta e perguntas abertas |
| 9 | Protótipo clicável/papel e teste rápido | Monta spike técnico se principal risco for técnico | Evidências sobre compreensão e viabilidade |
| 10 | Síntese e refinamento do conceito | Aprova plano de implementação e risco | Decisão de construir, alterar, testar mais ou parar |

**Gate da semana 2:** há evidência de que a solução é compreensível e tecnicamente plausível? Se conceito não funciona, voltar ao problema. Não transformar a data de lançamento em argumento para ignorar evidências.

### Semana 3 — Construir, testar e ajustar em paralelo

| Dia | Design | Engenharia e qualidade | Operação/GTМ |
|---|---|---|---|
| 11–12 | UI do fluxo central, estados, responsividade, conteúdo, assets mínimos de marca | Implementa fatias verticais com testes e eventos | Começa FAQ, demo, mensagens e suporte |
| 13 | Revisão de acessibilidade e teste com build funcional | Testes técnicos, integração, telemetria | Revisa promessa e limites do MVP |
| 14 | Corrige os bloqueios principais e documenta variantes | Implementa correções e monitoração | Prepara onboarding e procedimentos |
| 15 | Nova avaliação curta e check-in de escopo | Demonstra fluxo integrado; classifica bugs | Confirma plano de rollout e owners |

**Gate da semana 3:** fluxo essencial funciona de ponta a ponta? Dados e eventos chegam? Bloqueios de segurança, acessibilidade e uso foram resolvidos ou têm mitigação aprovada? O suporte consegue responder ao caso mais provável?

### Semana 4 — Fechar qualidade, lançar e começar a observar

| Dia | Design/produto | Engenharia/QA/segurança | Marketing/vendas/suporte |
|---|---|---|---|
| 16–17 | Revisa build, conteúdo, estados, WCAG e materiais | Regressão, desempenho, segurança, backup/rollback, alertas | Treinamento, materiais, scripts e FAQ |
| 18 | Teste ponta a ponta com pessoas e suporte | Corrige erros de severidade alta; valida instrumentação | Ensaio de demo e mensagens |
| 19 | Go/no-go com evidências e riscos | Verifica checklist, release e rollback | Confirma responsáveis, canais e cobertura |
| 20 | Liberação controlada e observação | Acompanha erros, latência, eventos | Divulga conforme plano; atende e registra dúvidas |

**Dia 21–30, se o calendário tiver 30 dias corridos:** estabilizar, corrigir problemas críticos, observar coortes iniciais, entrevistar primeiras pessoas, verificar custos e suporte, revisar métricas, registrar aprendizados e montar plano para mês 2. Se o mês tiver somente 20 dias úteis, lançar até o fim da semana 4 e acompanhar estabilização em janela imediatamente posterior.

### Cadência diária leve durante o mês

- 15 minutos para andamento, dependências e bloqueios.
- Bloco de trabalho conjunto de produto, design e engenharia em decisões que cruzam fronteiras.
- Revisão de evidências e decisão quando informação nova chega.
- Uma fonte única para decisões, links, status e próxima ação.
- Pesquisa semanal pequena durante discovery/delivery, quando acesso, risco e agenda permitirem.
- No máximo um responsável por decisão final em cada tema, com as pessoas impactadas ouvidas.

## Meses posteriores ao lançamento

| Período | Foco | Trabalho de Product Design | Critério para avançar |
|---|---|---|---|
| **Mês 2: estabilizar e entender** | Qualidade básica, ativação e falhas | Corrigir fricções, observar uso, entrevistar novos e desistentes, revisar acessibilidade e suporte | Métricas confiáveis e principais falhas conhecidas |
| **Mês 3: melhorar a tarefa e retenção** | Repetição de valor, fluxo e confiança | Priorizar oportunidades, testar alternativas, refinar onboarding/conteúdo, instrumentar coortes e experimentos | Evidência de melhoria sem piora de guardrails |
| **Mês 4: expandir com cautela** | Novos segmentos, canais ou funcionalidades | Testar demanda adjacente, avaliar capacidade e impacto operacional, fortalecer sistema de design | Capacidade de atender crescimento e resultado sustentado |
| **Meses 5–6: evoluir produto e sistema** | Estratégia, arquitetura, sustentabilidade e escala | Rever proposta, marca e roadmap, automatizar processos, reduzir dívida UX/tech, fazer avaliação ampla | Plano de evolução validado com métricas, riscos e investimento |
| **Contínuo** | Cuidar da experiência em produção | Research contínuo, testes, monitoramento, documentação, suporte, acessibilidade e decisões | Ciclo recorrente de observar → decidir → melhorar |

Evitar escalar aquisição se o produto falha na tarefa central, se suporte não consegue absorver demanda ou se métricas e consentimentos não funcionam. Crescimento amplifica valor e também amplifica defeitos.

## Métricas: do resultado à interface

Definir poucas métricas coerentes com a hipótese. Toda métrica precisa de fórmula, população, janela, fonte, owner, frequência, baseline, meta ou intervalo esperado, limitações e ação que desencadeia.

- **Outcome para usuário:** tarefa concluída com sucesso; tempo/esforço; erro; capacidade de concluir sem ajuda; satisfação contextual.
- **Produto:** ativação, repetição, retenção por coorte, adoção de recurso, conversão, abandono e cancelamento.
- **Negócio:** receita, margem, custo de servir, frequência de compra, pipeline ou renovação — conforme modelo.
- **Qualidade/guardrails:** falha, latência, crash, fraude, reclamação, reembolso, carga de suporte, acessibilidade, privacidade, segurança e taxa de erro.
- **Marketing/vendas:** alcance qualificado, conversão por canal, custo de aquisição, lead-to-trial, trial-to-paid, win rate e motivos de perda, quando aplicável.
- **Operação/suporte:** volume e severidade de tickets, tempo de resolução, reabertura, satisfação e problema raiz.

Uma North Star metric, AARRR/funil ou árvore de métricas pode ajudar a organizar conversa; nenhuma é universal. Evitar métricas de vaidade, metas sem baseline e A/B test em tráfego insuficiente ou em tarefas de alto risco sem salvaguardas.

## Decisões, documentação e manutenção do conhecimento

### Registro de decisão

Para cada decisão importante, registrar:

- Data, tema, responsável e pessoas consultadas.
- Pergunta ou decisão necessária.
- Evidências, pressupostos e grau de confiança.
- Alternativas consideradas, trade-offs e impactos.
- Decisão tomada e por que agora.
- Quem executa e dependências.
- Sinal que faria a equipe rever a escolha e data de revisão.

### Registro de pesquisa

Questão → método → participante/critério (sem dado identificável desnecessário) → evidência → achado → interpretação → limitação → implicação → decisão → estado da recomendação. Manter acesso, consentimento e retenção seguros.

### Backlog e roadmap

Backlog descreve problema, resultado esperado, contexto e critérios de aceite; não somente soluções. Roadmap comunica objetivos e hipóteses por horizonte, não uma lista inflexível de telas. Alterar roadmap quando evidências, riscos ou capacidade mudarem e comunicar o motivo.

### Handoff e operação

Manter documentação próxima do código e da interface atual. Marcar componentes obsoletos, versão do design system, regras de conteúdo, acessibilidade e dono da manutenção. Ao arquivar uma hipótese rejeitada, registrar o aprendizado para evitar reabrir a mesma questão sem nova evidência.

## Workshops com poucos recursos

Como você já demonstrou interesse em dinâmicas de Product Design com materiais simples, estas versões funcionam com papel, caneta, post-its ou um quadro compartilhado básico.

| Dinâmica | Tempo | Passos | Saída |
|---|---:|---|---|
| Mapa de pressupostos | 30–45 min | Listar o que acreditamos; marcar impacto e incerteza; escolher o que pesquisar primeiro | Lista de hipóteses e plano de pesquisa |
| Linha do tempo da experiência atual | 45–60 min | Cada pessoa descreve passos, gatilhos, fricções e improvisos; comparar relatos com fatos | Jornada atual e perguntas de observação |
| Síntese de evidências | 45–60 min | Uma nota por evidência; agrupar sem interpretar cedo; escrever padrão, contraexemplo e dúvida | Achados com rastreabilidade |
| “Como poderíamos…?” + 8 ideias | 30–45 min | Reescrever o problema como pergunta aberta; 8 esboços silenciosos; rodada de explicação; combinar e selecionar | Conceitos diversos sem domínio de voz |
| Story map do MVP | 45–60 min | Mapear objetivo, passos da pessoa, tarefas, exceções e menor fatia que completa a tarefa | Escopo vertical e não escopo |
| Pré-mortem de lançamento | 30 min | Imaginar que o lançamento falhou; escrever causas; classificar severidade e prevenção | Riscos, donos, alertas e mitigação |
| Revisão de decisão | 30 min | Relembrar objetivo e evidências; comparar opções; decidir e definir sinal para rever | Decisão registrada e próxima ação |

Boas facilitação: escrever antes de falar; permitir contribuições anônimas; separar geração de ideias de julgamento; incluir quem opera e atende; convidar pessoas afetadas quando apropriado; tornar decisão e responsável visíveis. FigJam, Miro ou qualquer ferramenta são opcionais: o método é mais importante que a ferramenta.

## Padrões, normas e legislação para selecionar conforme produto

Normas ISO são referências técnicas; nem todas são obrigatórias para qualquer produto. Aplicabilidade pode vir de lei, regulamentação setorial, contrato, política interna, edital ou decisão de qualidade. Validar edição vigente e contexto antes de declarar conformidade.

| Referência | Uso prático | Observação de aplicação |
|---|---|---|
| **ISO 9241-210:2019** | Princípios e atividades de design centrado em pessoas durante o ciclo de vida de sistemas interativos | A ISO confirmou a edição em 2025; continua atual no catálogo consultado. |
| **ISO 9241-11:2018** | Definição de usabilidade por eficácia, eficiência e satisfação em contexto de uso | Ajuda a planejar objetivos, tarefas, contexto e medidas. |
| **ISO 9241-220:2019** | Processos para habilitar, executar e avaliar design centrado em pessoas nas organizações | Referência para maturidade de processo, não checklist de tela. |
| **ISO 9241-115:2024** | Orientação para design conceitual, interação, interface e navegação | Ponte prática entre problema, estrutura de interação e UI. |
| **ISO 9241-171:2025** | Requisitos e orientações para software acessível | A edição de 2025 substitui a referência antiga de 2008; considerar junto a WCAG e avaliação com pessoas. |
| **ISO/IEC 25010:2023** | Modelo de qualidade de produto de software/TIC | Apoia definição e avaliação de características e subcaracterísticas de qualidade. |
| **WCAG 2.2** | Critérios de acessibilidade para conteúdo Web, publicados como recomendação W3C em 2023 | Declarar versão/nível; combinar automação, inspeção manual e pesquisa com pessoas. |
| **eMAG 3.1** | Modelo de recomendações para acessibilidade de sítios e portais do governo brasileiro | Aplicação direta em contexto governamental; pode servir como referência mais ampla, sem presumir obrigação universal. |
| **Lei 13.146/2015 (LBI)** | Direitos da pessoa com deficiência e requisitos de acessibilidade no Brasil | Avaliar o texto legal atualizado, jurisdição, serviço e obrigação aplicável. |
| **LGPD — Lei 13.709/2018** | Tratamento de dados pessoais no Brasil | Integrar finalidade, necessidade, transparência, segurança, retenção, direitos e governança ao discovery e à implementação. |
| **ISO/IEC 27001:2022** | Sistema de gestão de segurança da informação | Útil para organizações que adotam gestão formal de segurança; não substitui engenharia de segurança no produto. |

A ISO 9241-210 está vigente após confirmação em 2025; a 9241-220 foi confirmada em 2024; a 9241-171 teve nova edição em 2025; ISO/IEC 25010:2023 modela qualidade de produtos de TIC/software. WCAG 2.2 tornou-se recomendação W3C em 5 de outubro de 2023. Fontes: [ISO 9241-210](https://www.iso.org/standard/77520.html), [ISO 9241-220](https://www.iso.org/standard/63462.html), [ISO 9241-171:2025](https://www.iso.org/standard/86308.html), [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) e [W3C WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/).

## Checklists para copiar e adaptar

### Brief de início

- [ ] Quem é o segmento principal e como será recrutado?
- [ ] Qual é a situação real que motiva o produto?
- [ ] Quais evidências existem e quais são suposições?
- [ ] Qual benefício para a pessoa e resultado de negócio se busca?
- [ ] Qual outcome, baseline e guardrails?
- [ ] Qual é a menor fatia que completa a tarefa?
- [ ] O que fica fora do primeiro lançamento?
- [ ] Quais dependências, riscos e aprovações?
- [ ] Quem decide problema, escopo, qualidade e lançamento?
- [ ] Como haverá observação e melhoria depois?

### Sessão de pesquisa

- [ ] Objetivo e decisão vinculada.
- [ ] Critério de participante, diversidade e acessibilidade.
- [ ] Consentimento, privacidade, gravação e retenção.
- [ ] Roteiro neutro e perguntas abertas.
- [ ] Piloto do roteiro e do protótipo.
- [ ] Moderador, observador e anotador definidos.
- [ ] Notas distinguem evidência de interpretação.
- [ ] Debrief e próxima ação agendados.

### Prontidão para construir

- [ ] Problema e outcome compreendidos pela equipe.
- [ ] Fluxo principal e casos críticos mapeados.
- [ ] Hipóteses de alto risco testadas ou mitigadas.
- [ ] Contratos de dados e dependências discutidos com engenharia.
- [ ] Critérios de aceite verificáveis.
- [ ] Requisitos de acessibilidade e segurança incluídos.
- [ ] Eventos e definições de analytics revisados.

### Prontidão para lançar

- [ ] Fluxos críticos revisados com build real.
- [ ] Testes e bugs priorizados por severidade e impacto.
- [ ] Acessibilidade avaliada por automação e inspeção manual.
- [ ] Privacidade, consentimento, segurança e retenção revisados.
- [ ] Métricas e alertas verificados de ponta a ponta.
- [ ] Suporte, vendas, CS, conteúdo e marketing preparados.
- [ ] Release, rollout gradual e rollback definidos.
- [ ] Critérios de go/no-go e pessoas responsáveis presentes.
- [ ] Janela de observação pós-lançamento agendada.

## Fontes selecionadas

### Design centrado em pessoas, produto e processo

- [ISO 9241-210:2019 — Human-centred design for interactive systems](https://www.iso.org/standard/77520.html)
- [ISO 9241-11:2018 — Usability: definitions and concepts](https://committee.iso.org/standard/63500.html)
- [ISO 9241-220:2019 — Human-centred processes within organizations](https://www.iso.org/standard/63462.html)
- [ISO 9241-115:2024 — Conceptual, interaction, UI and navigation design](https://www.iso.org/standard/80773.html)
- [ISO 9241-171:2025 — Software accessibility](https://www.iso.org/standard/86308.html)
- [ISO/IEC 25010:2023 — Product quality model](https://www.iso.org/standard/78176.html)
- [Design Council — History of the Double Diamond](https://www.designcouncil.org.uk/resources/the-double-diamond/history-of-the-double-diamond/)
- [Silicon Valley Product Group — Product Operating Model](https://www.svpg.com/the-product-operating-model-an-introduction/)
- [Product Talk — Continuous Discovery](https://www.producttalk.org/getting-started-with-discovery/)
- [GOV.UK Service Manual — Plan user research](https://www.gov.uk/service-manual/user-research/plan-user-research-for-your-service)
- [GOV.UK Service Manual — Contextual research and observation](https://www.gov.uk/service-manual/user-research/contextual-research-and-observation)
- [ISO/IEC 27001:2022 — Information security management systems](https://www.iso.org/standard/27001)
- [Manifesto Ágil](https://agilemanifesto.org/iso/ptbr/manifesto.html)
- [Scrum Guide](https://scrumguides.org/scrum-guide.html)

### Acessibilidade, privacidade, qualidade e padrões brasileiros

- [W3C WAI — WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/)
- [W3C WAI — WCAG Evaluation Methodology (WCAG-EM)](https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/)
- [Governo Digital — Acessibilidade Digital](https://www.gov.br/governodigital/pt-br/acessibilidade-e-usuario/acessibilidade-digital)
- [Governo Digital — eMAG](https://www.gov.br/governodigitallogin/pt-br/acessibilidade-e-usuario/acessibilidade-digital/modelo-de-acessibilidade)
- [Câmara dos Deputados — Lei nº 13.146/2015, Lei Brasileira de Inclusão](https://www2.camara.leg.br/legin/fed/lei/2015/lei-13146-6-julho-2015-781174-norma-pl.html)
- [Planalto — Lei nº 13.709/2018, LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [Governo Digital — Design System / Padrão Digital de Governo](https://www.gov.br/ds)
- [Google SRE — Launch Coordination Checklist](https://sre.google/sre-book/launch-checklist/)

