# Análise do portfólio de Emerson Almeida — atualização para 2027

Data: 08/10/2026. Repositório: https://github.com/emersonalmeida/emersonalmeida.github.io. Branch: main. Commit analisado: f1bdeba2c1105bd3fc1ac219dd178af7d1d27b78, de 28/09/2026.

## Conclusão

Existe material suficiente para reconstruir o portfólio sem começar os cases do zero. A principal lacuna é editorial: imagens e etapas são apresentadas sem explicar consistentemente problema, decisões, participação e resultado. A atualização deve combinar reconstrução dos cases existentes, uma apresentação profissional clara e um case atual com pesquisa e avaliação documentadas.

O site pode continuar no GitHub Pages. Não há necessidade demonstrada de migrar a hospedagem ou adotar uma aplicação complexa. Templates de conteúdo podem reduzir duplicação sem prejudicar o caráter estático do portfólio.

## Escopo da análise e limites

Foi realizada leitura dos arquivos de HTML, CSS e JavaScript, inventário de todos os arquivos da cópia do repositório, verificação estática de referências locais presentes em atributos HTML ativos e inspeção visual de seis imagens de SOMA, Oi e Arkave. Também foram consultadas páginas publicadas.

Não foi feita auditoria completa em navegador, execução de Lighthouse, medição de Core Web Vitals, teste com leitores de tela ou análise de todos os vídeos e imagens. O tamanho total do repositório não equivale ao volume baixado por cada visita. Sem acesso aos painéis, a presença de scripts de analytics não comprova coleta ativa ou eventos corretamente configurados.

## Inventário

390 arquivos versionados na cópia analisada, com aproximadamente 614,9 MB, excluindo os metadados Git.

| Tipo | Quantidade |
|---|---:|
| HTML | 10 — início e 9 páginas de projetos |
| CSS | 1 |
| JavaScript | 2 |
| JPG/JPEG/PNG/WebP/GIF | 311 |
| MP4 | 50 |
| ZIP | 7 |
| Outros | 9 |

A contagem de imagens inclui backups, variantes, GIFs e materiais que não aparecem no site. Não representa 311 entregas distintas.

| Diretório | Arquivos, todos os tipos | Volume aproximado |
|---|---:|---:|
| img/case | 34 | 307,3 MB |
| img/soma | 72 | 102,2 MB |
| img/home | 62 | 77,3 MB |
| img/missao-genese | 99 | 57,0 MB |
| img/dunker | 25 | 21,6 MB |
| img/oi-controle | 39 | 19,6 MB |
| img/arkave | 23 | 17,7 MB |
| img/technos | 17 | 5,3 MB |
| img/nyte | 2 | 3,6 MB |
| img/nubank | 4 | 3,0 MB |

Há arquivos de backup, ZIPs e um instalador OpenCode Desktop.dmg em img/home. Eles merecem revisão para definir o que integra a publicação. Não é necessário apagar o histórico nem retirar originais antes de preservá-los em um destino apropriado.

## Arquitetura atual

- Site estático em HTML, CSS e JavaScript, com fontes Inter e Roboto Mono.
- Página inicial com cinco projetos: SOMA, Missão Gênese, Dunker, Oi Controle e Arkave.
- Conteúdo de apresentação profissional existe em comentário HTML, portanto não é exibido.
- Bipa Concept, Technos e Nyte possuem entradas comentadas na página inicial. Nubank também tem página no repositório.
- Não foram encontrados README, manifesto de dependências, workflow versionado, sitemap ou robots.txt nos arquivos rastreados. Isso não prova ausência de configuração de publicação no GitHub.
- Navegação centrada em projetos e contato, sem conteúdo ativo dedicado a serviços, experiência, currículo ou versão em inglês.
- Cabeçalhos e títulos repetem “Em Construção” e variam entre Designer e User Interface Designer.

## Diagnóstico editorial por projeto

| Projeto | Evidência existente | Lacuna | Uso recomendado |
|---|---|---|---|
| Grupo SOMA, 2022 | Objetivo, funções, alinhamento, proto-persona, funcionalidades, protótipos, testes e resultados como etapas; fotos e mídia | Explicar o conteúdo de cada etapa, decisões, contribuição e resultados; distinguir colaboração | Case aprofundado de discovery e sistema interno |
| Oi Controle, 2019 | Vínculo pela VML, equipe de negócio/produto/UX/dev, mapas de calor, benchmark e mudanças mobile | Conectar observações a hipóteses e alterações; documentar validação e métricas disponíveis | Case aprofundado de análise e colaboração com engenharia |
| Bipa Concept, 2025 | Texto sobre scripts Python/Colab, fontes de busca, tendências e aplicativos; vídeos e percentuais | Rastreabilidade dos dados, classificação, recorte, limites e passagem de achados a decisões | Precursor do case atual de dados e IA |
| Missão Gênese, 2016 | Propósito educacional, parceria Hospital do Amor/YDreams, equipe e participação em interfaces e design gráfico | Explicar interação, público, limitações e sua contribuição por estação/jogo | Case de experiência interativa e multidisciplinaridade |
| Arkave, 2016 | Moodboard, exploração, construção, cor, tipografia e aplicações | Explicar briefing, critérios e decisões da identidade | Case curto para serviços de branding |
| Dunker, 2015 | Ideação, wireframe, protótipo e MVP, principalmente em mídia | Público, problema, vínculo, participação e estado efetivo do produto | Avaliar após entrevista de reconstrução |
| Technos, 2014 no HTML | Imagens de e-commerce | Contexto ativo e papel individual; divergência com 2015 registrado anteriormente | Case curto ou complementar após confirmação |
| Nyte, 2013 no HTML | Página de app com pouca mídia | Quase todo o contexto e autoria | Arquivo ou trabalho complementar |
| Nubank, 2023 | Identificado como estudo pessoal, duas versões em vídeo | Hipótese, critério de comparação, avaliação e limpeza editorial | Experimento, identificado claramente como pessoal |

### Correções de escopo e autoria

O SOMA é descrito no site como um acervo digital para equipes de Estilo pesquisarem produtos e coleções, analisarem dados e organizarem pastas. Isso não comprova atuação no redesenho integral do PLM. O case deve partir desse problema específico. Há crédito explícito de ideação para @lorenalages; ele deve ser preservado e complementado com a descrição da contribuição de Emerson.

Oi identifica VML como contratante, reduzindo a ambiguidade VML/VLM dos textos anteriores. Missão Gênese e Arkave aparecem com 2016, enquanto as anotações profissionais citam YDreams em 2017. Verificar se são datas de projeto, contratação ou publicação. Não corrigir automaticamente uma fonte para concordar com a outra.

Nubank possui uma referência ativa a somagrupo.com.br que aparenta resíduo de template. Textos longos sobre SOMA em Nubank e sobre Technos em Nyte estão comentados e não devem ser tratados como conteúdo visível. A distinção entre código comentado e conteúdo publicado é relevante.

### Bipa Concept: cautela com os números

O texto ativo apresenta percentuais de intenções e outra agregação de sugestões. A página não explica suficientemente base, data, denominador, classificação, deduplicação ou relação entre essas distribuições. Sugestões de busca não medem diretamente a proporção de pessoas com uma intenção.

Para republicar: recuperar dataset, scripts, período de coleta, fontes, categorias e fórmula dos percentuais. Se isso não for recuperável, substituir afirmações populacionais por observações restritas ao material coletado. Um estudo conceitual não deve sugerir vínculo com a empresa Bipa sem confirmação.

## Diagnóstico técnico

### Acessibilidade e legibilidade

1. Os dez HTML usam lang="en", apesar do conteúdo principal em português. Usar pt-BR e marcar corretamente as futuras versões em inglês.
2. Os dez HTML têm viewport com maximum-scale=1 e user-scalable=no. Remover restrições à ampliação.
3. Nas dez páginas, foram encontrados 75 elementos img, dos quais 65 têm alt vazio. A adequação precisa ser avaliada por função: diagramas, telas e evidências essenciais precisam de alternativas textuais e explicação adjacente; imagens decorativas podem permanecer com alt vazio.
4. Não há loading="lazy" nos elementos img inspecionados. Aplicar às mídias abaixo da primeira dobra, preservando carregamento prioritário da mídia principal quando pertinente.
5. Diversos tamanhos de texto dependem apenas de vw, incluindo valores de 0,7vw. Revisar limites de leitura com unidades relativas e clamp; verificar em dispositivos e níveis de zoom.
6. Conteúdo com data-motion começa invisível em CSS. Sem execução bem-sucedida do JavaScript, partes da navegação/conteúdo podem permanecer ocultas. O padrão deve ser conteúdo visível e animação como melhoria progressiva.
7. Não foi encontrada regra para prefers-reduced-motion. Acrescentar tratamento para reduzir animações; realizar testes reais de teclado e foco antes de afirmar conformidade.

### JavaScript

Em js/scoll-reveal.js, o debounce usa `timeout - setTimeout(later, wait)` em vez de atribuir o temporizador. Isso impede cancelar adequadamente os callbacks anteriores, comprometendo o debounce. Também há console.log no evento de scroll. A correção é pequena; posteriormente avaliar IntersectionObserver para a revelação de conteúdo.

### Performance

O vídeo img/case/02_colab_geral.mp4 tem aproximadamente 76,9 MB. Há GIFs grandes, variantes e backups. Isso é um sinal de oportunidade de otimização, não uma medição de lentidão do site.

Plano: separar originais das versões publicadas, gerar imagens adequadas a cada tamanho de exibição, revisar srcset/sizes, trocar GIFs grandes por vídeos quando adequado, usar poster/preload seletivo e evitar autoplay desnecessário. Medir o resultado em mobile antes e depois.

### SEO, consistência e medição

Títulos contêm “Em Construção”; descrições são genéricas e repetidas. Não foram identificados metadados de compartilhamento Open Graph nos HTML analisados. Criar títulos e descrições específicos, URLs estáveis, sitemap e apresentação para compartilhamento.

Há scripts Hotjar e Google Analytics, além de Clarity na home e no Bipa Concept. Inventariar o propósito de cada ferramenta e configurar eventos necessários: abertura de case, clique de contato e download de currículo, quando esse arquivo existir. Cliques não equivalem a leads qualificados ou contratos; esses resultados exigem acompanhamento separado.

A verificação estática não encontrou referências a arquivos locais inexistentes em href/src/srcset ativos. Não validou todos os destinos externos, âncoras, CSS ou execução de JavaScript. A tentativa inicial de consulta pública de Missão Gênese retornou 404, mas o arquivo existe na branch analisada: tratar como verificação de publicação pendente, sem declarar que falta no repositório.

## Relação com a pesquisa de vagas e os objetivos de contratação

A amostra fornecida reúne principalmente vagas de design geral, gráfico e marketing. Usá-la para selecionar evidências, sem transformá-la em representação de todo o mercado de Product Design ou de contratações globais.

- Comunicação: explicar decisões e colaboração nos cases SOMA, Oi e Missão Gênese.
- Engenharia: recuperar regras, restrições e acompanhamento de implementação em Oi e outros projetos efetivamente entregues.
- Dados: documentar interpretações de mapas de calor e a metodologia de coleta multifontes.
- Portfólio: explicitar autoria, escopo, estágio e evidências.
- Design systems e acessibilidade: mostrar o que foi realmente realizado; usar o novo case para produzir evidências atuais onde as antigas forem insuficientes.

Para clientes, explicitar serviços, escopos e entregas. Para recrutadores, explicitar experiência, contribuição e currículo. Uma mesma base de cases pode atender ambos, com caminhos de navegação distintos. Versão PT-BR e inglês apoiará o objetivo global; não afirmar fluência, disponibilidade internacional ou condições contratuais sem confirmação.

## Curadoria proposta para a versão 2027

1. Novo case principal — DataReview, se confirmado após análise do projeto existente: inteligência e síntese de evidências para uma tarefa específica de produto/pesquisa.
2. SOMA — discovery e acervo digital para equipes de moda.
3. Oi — experiência mobile orientada por observação de comportamento.
4. Missão Gênese — experiência interativa educacional.
5. Arkave — identidade e aplicação de marca, com narrativa mais curta.

Bipa Concept pode aparecer como estudo anterior que motivou aprendizados aplicados ao DataReview. Não é necessário apresentar ambos com narrativas longas e redundantes. Outros trabalhos podem compor uma galeria com contexto breve.

## Brief inicial do case principal

Hipótese: profissionais de produto e pesquisa precisam organizar informações dispersas, conferir sua origem e produzir uma síntese útil para uma decisão.

Validar público e tarefa antes de ampliar fontes. Primeiro fluxo: pergunta → coleta limitada → revisão/deduplicação → organização → síntese rastreável → decisão ou exportação. Incluir resultados vazios, falha de fonte, informação divergente, edição humana e ligação entre afirmação e evidência.

Documentar problema, entrevistas, alternativas, arquitetura da informação, UI, componentes, implementação e testes. Avaliar conclusão da tarefa, erros, tempo observado e capacidade de verificar uma afirmação. Comparações devem utilizar condições explicitadas. Usar IA ou multiagentes onde houver contribuição demonstrável à tarefa, mantendo os limites da análise.

## Ordem recomendada de execução

| Prioridade | Trabalho | Critério de conclusão |
|---|---|---|
| P0 | Confirmar datas, vínculos e escopos dos cases | Fichas de projeto aprovadas por Emerson |
| P0 | Restaurar apresentação profissional e caminhos de contato | Visitante entende perfil, serviços e como conversar |
| P0 | Corrigir zoom, idioma, debounce e dependência de animação | Conteúdo disponível com e sem JS; ampliação e navegação verificadas |
| P1 | Reconstruir SOMA e Oi | Problema, contribuição, decisões e evidência claramente descritos |
| P1 | Organizar e otimizar mídia publicada | Imagens contextualizadas; carga medida e comparada |
| P1 | Desenvolver o novo case com recorte limitado | Fluxo testável e avaliação documentada |
| P2 | Versão em inglês, currículo e metadados | Conteúdo consistente e revisado |
| P2 | Revisar métricas de captação | Diferenciar visitas, contatos, conversas e oportunidades |

O primeiro insumo necessário de Emerson é a reconstrução factual dos projetos. A estrutura de arquivos e as imagens já podem ser inventariadas a partir deste repositório. Esta análise não alterou nem publicou mudanças no código.
