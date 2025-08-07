# ₿ Bitcoin Simulator - Assistente Virtual Inteligente

Um simulador web interativo e educativo sobre Bitcoin com design minimalista, assistente virtual inteligente e simulações práticas.

## 🌟 Características

### Design Minimalista
- **Dark/Light Mode**: Alternância suave entre temas escuro e claro
- **Cores Dinâmicas**: Cor primária aleatória com contraste garantido
- **Animações Suaves**: Transições fluidas e efeitos visuais elegantes
- **Responsivo**: Funciona perfeitamente em desktop, tablet e mobile

### Assistente Virtual Inteligente
- **Chat Interativo**: Conversa em tempo real sobre Bitcoin
- **Respostas Contextuais**: Responde baseado no conteúdo da pergunta
- **Guias Inteligentes**: Orienta o usuário através de cada seção
- **Histórico de Conversas**: Mantém registro das interações

### Simulações Interativas
- **Simulador de Mineração**: Experimente o processo de mineração Bitcoin
- **Simulador de Transações**: Envie transações simuladas
- **Dados em Tempo Real**: Preços e métricas atualizadas
- **Gráficos Dinâmicos**: Visualização de preços com Chart.js

### Conteúdo Educativo
- **Fundamentos**: Conceitos básicos do Bitcoin
- **FAQ Interativo**: Perguntas frequentes com respostas detalhadas
- **Análises**: Dados de mercado e insights
- **Exemplos Práticos**: Demonstrações visuais de conceitos

## 🚀 Como Usar

### Instalação
1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/bitcoin-simulator.git
cd bitcoin-simulator
```

2. Abra o arquivo `index.html` em seu navegador ou use um servidor local:
```bash
# Usando Python
python -m http.server 8000

# Usando Node.js
npx serve .

# Usando PHP
php -S localhost:8000
```

3. Acesse `http://localhost:8000` no seu navegador

### Navegação
- **Fundamentos**: Explore conceitos básicos do Bitcoin
- **Simulações**: Experimente mineração e transações
- **Análises**: Veja dados de mercado em tempo real
- **FAQ**: Encontre respostas para dúvidas comuns

### Assistente Virtual
- Clique no chat no canto inferior direito
- Digite suas perguntas sobre Bitcoin
- Receba respostas contextuais e informativas

## 🛠️ Tecnologias Utilizadas

- **HTML5**: Estrutura semântica e acessível
- **CSS3**: Design responsivo com CSS Grid e Flexbox
- **JavaScript ES6+**: Funcionalidades interativas e dinâmicas
- **Chart.js**: Gráficos e visualizações de dados
- **Google Fonts**: Tipografia Inter para melhor legibilidade

## 🎨 Design System

### Cores
- **Primária**: Gerada aleatoriamente com contraste garantido
- **Escalas**: 20% a 80% de branco/preto
- **Temas**: Dark mode e Light mode
- **Estados**: Success, Warning, Error, Info

### Tipografia
- **Fonte Principal**: Inter (Google Fonts)
- **Hierarquia**: Títulos, subtítulos, corpo, legendas
- **Pesos**: 300, 400, 500, 600, 700

### Espaçamento
- **Sistema**: Baseado em rem (0.25rem, 0.5rem, 1rem, 1.5rem, 2rem, 3rem)
- **Consistência**: Padrão uniforme em todo o projeto

### Animações
- **Transições**: 0.15s, 0.3s, 0.5s
- **Easing**: Funções suaves e naturais
- **Hover Effects**: Feedback visual interativo

## 📱 Responsividade

### Breakpoints
- **Desktop**: > 768px
- **Tablet**: 768px - 480px
- **Mobile**: < 480px

### Adaptações
- Layout flexível com CSS Grid
- Navegação otimizada para mobile
- Chat responsivo
- Gráficos adaptáveis

## 🔧 Funcionalidades Técnicas

### Simulador de Mineração
- Hash rate em tempo real
- Progresso visual
- Recompensas calculadas
- Estatísticas dinâmicas

### Simulador de Transações
- Validação de entrada
- Processamento simulado
- IDs de transação únicos
- Feedback de status

### Sistema de Chat
- Histórico persistente
- Respostas contextuais
- Interface intuitiva
- Minimização/maximização

### Dados em Tempo Real
- Preços simulados
- Market cap dinâmico
- Volume 24h
- Dominância de mercado

## 📊 Estrutura de Dados

### Bitcoin Data
```javascript
{
  price: number,
  marketCap: number,
  volume24h: number,
  dominance: number,
  change24h: number
}
```

### Mining Stats
```javascript
{
  hashRate: number,
  blocksMined: number,
  totalReward: number,
  isMining: boolean
}
```

### Chat History
```javascript
{
  sender: 'user' | 'assistant',
  message: string,
  timestamp: Date
}
```

## 🎯 Conceitos Bitcoin Explicados

### Blockchain
- Ledger descentralizado
- Imutabilidade
- Transparência
- Consenso distribuído

### Mineração
- Validação de transações
- Proof of Work
- Recompensas
- Dificuldade ajustável

### Carteiras
- Chaves privadas
- Endereços públicos
- Segurança
- Tipos de carteiras

### Halving
- Redução de recompensas
- Controle de inflação
- Impacto no preço
- Ciclos de 4 anos

## 🔒 Segurança

- **Dados Simulados**: Nenhum dado real é processado
- **Sem Armazenamento**: Dados não são persistidos
- **Cliente-Side**: Execução local no navegador
- **Sem APIs Reais**: Simulações para fins educativos

## 🚀 Melhorias Futuras

- [ ] Integração com APIs reais de Bitcoin
- [ ] Mais simulações (Lightning Network, Smart Contracts)
- [ ] Modo offline
- [ ] Exportação de dados
- [ ] Múltiplos idiomas
- [ ] Modo de teste avançado
- [ ] Integração com carteiras reais (read-only)

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, leia as diretrizes de contribuição antes de submeter pull requests.

## 📞 Suporte

Para dúvidas, sugestões ou problemas:
- Abra uma issue no GitHub
- Entre em contato através do chat do simulador

---

**Desenvolvido com ❤️ para educar sobre Bitcoin**