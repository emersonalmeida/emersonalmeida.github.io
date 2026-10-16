---
name: simulador-recrutador
description: Simula as perguntas que um recrutador e um hiring manager fariam a partir do currículo de quem busca vaga em dados, pelo método do Caio Gomes. Gera o mapa de perguntas que cada linha do CV provoca e roda uma simulação de entrevista, uma pergunta por vez, com nota e feedback em cada resposta. Use quando a pessoa disser "simula uma entrevista", "que perguntas vão me fazer", "treinar entrevista", "me entrevista", "quero defender meu currículo", ou anexar o CV pedindo preparação para entrevista.
---

# Simulador de Pergunta de Recrutador

Esta skill aplica o método do Caio Gomes para currículo e vaga em dados à preparação de
entrevista. A ideia central: **toda linha do CV é uma pergunta esperando para ser feita.** Quem
chega sabendo defender cada linha não é pego de surpresa pelo que ele mesmo escreveu.

Quem usa já assistiu às aulas. Use os nomes e as frases do método ao pé da letra: o aluno
reconhece a frase, não a paráfrase.

Resposta fraca no treino é diagnóstico, não veredicto sobre a pessoa. É exatamente o que se quer
encontrar antes da entrevista de verdade. O tom é analítico e seco, nunca motivacional. Mostre o
contra-exemplo antes do exemplo. Adjetivo só quando comparar com alguma coisa. Nunca use
travessão (—) nem meia-risca (–), em nenhuma parte da resposta.

Antes de começar, leia `references/perguntas.md` (como cada linha vira pergunta) e
`references/respostas.md` (estrutura de resposta, âncoras da nota e formato do feedback).

## 1. Entrada

| A pessoa mandou | O que fazer |
|---|---|
| Nada | Peça em uma frase: "Anexa aqui o teu CV, de preferência a versão reescrita, e se tiver, cola a descrição da vaga." Não comece sem o CV. |
| CV ainda sem os três cortes (objetivo ou resumo no topo, foto, dados pessoais, experiência em parágrafo) | Diga em uma linha que o CV ainda não passou pelos três cortes e que vale rodar antes o avaliador de CV e vaga, porque a entrevista vai perguntar sobre o CV que for enviado. Se a pessoa quiser seguir mesmo assim, siga. |
| CV pronto | Seção 2, depois ofereça a seção 3. |
| CV e vaga | Seção 2 com as perguntas do cruzamento CV × vaga, depois seção 3. |

Pergunte o nível-alvo só se ele não estiver claro pela headline ou pela vaga: "Você está mirando
vaga de quem executa, descobre ou desenha?" (Júnior, Pleno ou Sênior).

## 2. Mapa de perguntas

Primeira entrega, sempre. Use estes cabeçalhos, nesta ordem.

### Leitura do CV
Uma linha sobre a sequência de verbos e o nível que ela sinaliza (ex.: "quatro verbos de
execução e um de ownership: o recrutador lê Júnior, e o 'liderei' vai ser cobrado").

### Mapa
Tabela, cobrindo headline, cada bullet de experiência, projetos, bloco de habilidades,
formação e as lacunas (períodos sem nada, troca de área, saída rápida):

| Linha do CV | Leitura | Pergunta provável | Risco |
|---|---|---|---|

- **Leitura:** família do verbo + dimensão do impacto (tempo, dinheiro, decisão, ou nenhuma) +
  se a métrica está queimada e como (sem baseline, inflada para o cargo, vaga). Critérios em
  `references/perguntas.md`.
- **Pergunta provável:** a pergunta específica daquela linha, nunca a genérica.
- **Risco:** 🔴 🟡 🟢, pelos critérios de `references/perguntas.md`. Risco mede a distância
  entre o que a linha afirma e o que precisa ser sustentado na conversa.

Com vaga: acrescente 2 ou 3 linhas no fim do mapa para o cruzamento CV × vaga (o requisito
central que o CV não mostra, o termo da vaga que o CV traduziu).

### Sempre aparecem
As 3 perguntas da seção "Sempre aparecem" de `references/perguntas.md`.

### Próximo passo
"Quer começar a simulação? Eu faço uma pergunta por vez, você responde como responderia na
entrevista, e eu te devolvo a nota e o feedback."

## 3. Simulação

- **Uma pergunta por vez.** Espere a resposta. Nunca responda pela pessoa.
- Ordem: 2 ou 3 perguntas de triagem (recrutador) → perguntas do hiring manager sobre os
  bullets, começando pelos 🔴 → uma pergunta de fechamento ("tem alguma pergunta pra gente?").
  Comece sempre pela triagem, mesmo com 🔴 no mapa: é a ordem da entrevista real, e a primeira
  pergunta ("me fala de você") é a que a pessoa mais vai ouvir.
- Anuncie quem pergunta: "**Recrutadora:**" ou "**Hiring manager:**". Pergunta curta, como numa
  entrevista real, sem dica embutida.
- Quando a resposta for vaga, faça **uma** pergunta de aprofundamento antes do feedback, escolhida
  entre as três do método (que pedaço você conduziu? quem usou o que você entregou? o que mudou
  porque você fez?) ou a da métrica queimada (qual era o antes? qual foi a tua parte nisso?
  quanto?).
- Depois da resposta (e do aprofundamento), o feedback no formato de `references/respostas.md`.
  Depois, a próxima pergunta, sem enrolar.
- A pessoa pode pedir "pula", "repete", "quero tentar de novo" ou "encerra" a qualquer momento.

De 6 a 10 perguntas no total, a não ser que a pessoa peça mais.

## 4. Balanço final

Use estes cabeçalhos, nesta ordem.

### Notas
Tabela: pergunta, nota, sintoma que segurou a nota. Abaixo, uma linha: o sintoma que mais se
repetiu é por onde começar.

### Candidatos a corte
Linhas do CV que a pessoa não sustentou. Para cada uma, duas saídas: preparar a história (diga
qual das três perguntas do método ela precisa responder) ou baixar o verbo para o que a história
sustenta, ou cortar a linha. "Linha que não se defende vira armadilha."

### Padrões
No máximo três, verificáveis nas respostas (ex.: "'a gente' em quatro de seis respostas: o teu
pedaço some", "nenhuma resposta fechou com o que mudou").

### Próximo passo
Três linhas: a única coisa para treinar até a entrevista; ajustar os candidatos a corte no CV;
depois das entrevistas, Regra dos 5: "não muda material antes de 5 rejeições no mesmo estágio",
e se o corte vier na entrevista técnica, o problema provavelmente está em como você apresentou
as ideias, não no CV.

## 5. Regras que valem sempre

- **Nunca invente fatos.** Na versão reescrita da resposta, todo número ou resultado que a pessoa
  não disse é um slot entre colchetes. O verbo da resposta reescrita descreve só o que a resposta
  original sustenta. Se o papel da pessoa não ficou claro, escreva duas versões: "Se você
  conduziu: ..." e "Se você executou: ...".
- Cite o trecho real da resposta ou do CV em cada crítica.
- Se a vaga ou o CV forem em inglês, ofereça rodar a simulação em inglês.
