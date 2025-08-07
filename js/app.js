// Bitcoin Simulator - Main Application
class BitcoinSimulator {
    constructor() {
        this.currentTheme = 'dark';
        this.miningInterval = null;
        this.miningStats = {
            hashRate: 0,
            blocksMined: 0,
            totalReward: 0,
            isMining: false
        };
        this.bitcoinData = {
            price: 0,
            marketCap: 0,
            volume24h: 0,
            dominance: 0,
            change24h: 0
        };
        this.chatHistory = [];
        this.assistantResponses = {
            greetings: [
                "Olá! Como posso ajudá-lo com Bitcoin hoje?",
                "Oi! Estou aqui para esclarecer suas dúvidas sobre Bitcoin.",
                "Bem-vindo! Vamos explorar o mundo do Bitcoin juntos."
            ],
            mining: [
                "A mineração de Bitcoin é o processo de validar transações e adicioná-las ao blockchain. Mineradores competem para resolver problemas matemáticos complexos usando poder computacional.",
                "O processo de mineração envolve encontrar um hash que satisfaça critérios específicos. Quanto mais poder computacional, maior a chance de encontrar o hash correto.",
                "A recompensa de mineração atualmente é de 6.25 BTC por bloco, mas será reduzida pela metade no próximo halving."
            ],
            blockchain: [
                "Blockchain é um ledger descentralizado que registra todas as transações Bitcoin de forma imutável e transparente.",
                "Cada bloco contém múltiplas transações e é conectado ao bloco anterior através de um hash, criando uma cadeia.",
                "A descentralização significa que nenhuma entidade central controla a rede Bitcoin."
            ],
            wallet: [
                "Uma carteira Bitcoin armazena suas chaves privadas, que são necessárias para assinar transações.",
                "Existem diferentes tipos de carteiras: hot wallets (conectadas à internet) e cold wallets (offline).",
                "Sempre mantenha suas chaves privadas seguras - quem tem as chaves, tem os Bitcoins!"
            ],
            halving: [
                "Halving é um evento que ocorre a cada 210.000 blocos (aproximadamente 4 anos) onde a recompensa de mineração é reduzida pela metade.",
                "O halving controla a inflação do Bitcoin, criando escassez artificial e potencialmente afetando o preço.",
                "O próximo halving está previsto para 2024, reduzindo a recompensa de 6.25 para 3.125 BTC."
            ],
            price: [
                "O preço do Bitcoin é determinado pela oferta e demanda no mercado, sem controle central.",
                "Fatores que podem afetar o preço incluem adoção institucional, regulamentações, e eventos macroeconômicos.",
                "Bitcoin tem uma oferta máxima de 21 milhões de unidades, criando escassez natural."
            ],
            security: [
                "Bitcoin é extremamente seguro devido à criptografia SHA-256 e ao consenso distribuído.",
                "A rede nunca foi hackeada, mas exchanges e carteiras individuais podem ser vulneráveis.",
                "Sempre use práticas de segurança adequadas: carteiras hardware, backup de chaves, e verificação de endereços."
            ]
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadBitcoinData();
        this.setupChart();
        this.generateRandomPrimaryColor();
        this.updateAssistantMessage();
    }

    setupEventListeners() {
        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Navigation tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchSection(e.target.dataset.section);
            });
        });

        // Concept cards
        document.querySelectorAll('.concept-card').forEach(card => {
            card.addEventListener('click', (e) => {
                this.showConceptDetails(e.currentTarget.dataset.concept);
            });
        });

        // Mining simulator
        document.getElementById('startMining').addEventListener('click', () => {
            this.toggleMining();
        });

        // Transaction simulator
        document.getElementById('sendTransaction').addEventListener('click', () => {
            this.simulateTransaction();
        });

        // FAQ items
        document.querySelectorAll('.faq-question').forEach(question => {
            question.addEventListener('click', (e) => {
                this.toggleFAQ(e.currentTarget.parentElement);
            });
        });

        // Chat functionality
        document.getElementById('sendMessage').addEventListener('click', () => {
            this.sendChatMessage();
        });

        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });

        document.getElementById('chatToggle').addEventListener('click', () => {
            this.toggleChat();
        });

        // Auto-update assistant message
        setInterval(() => {
            this.updateAssistantMessage();
        }, 30000); // Update every 30 seconds
    }

    toggleTheme() {
        const body = document.body;
        const themeIcon = document.querySelector('.theme-icon');
        
        if (this.currentTheme === 'dark') {
            body.classList.remove('dark-mode');
            this.currentTheme = 'light';
            themeIcon.textContent = '☀️';
        } else {
            body.classList.add('dark-mode');
            this.currentTheme = 'dark';
            themeIcon.textContent = '🌙';
        }

        // Update chart colors
        this.updateChartColors();
    }

    switchSection(sectionName) {
        // Remove active class from all tabs and sections
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Add active class to clicked tab and corresponding section
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
        document.getElementById(sectionName).classList.add('active');

        // Update assistant message based on section
        this.updateAssistantMessage(sectionName);
    }

    showConceptDetails(concept) {
        const messages = this.assistantResponses[concept] || this.assistantResponses.greetings;
        const randomMessage = messages[Math.floor(Math.random() * messages.length)];
        
        this.addChatMessage('assistant', `Sobre ${concept}: ${randomMessage}`);
        
        // Highlight the concept card
        const card = document.querySelector(`[data-concept="${concept}"]`);
        card.style.transform = 'scale(1.05)';
        setTimeout(() => {
            card.style.transform = '';
        }, 300);
    }

    toggleMining() {
        const button = document.getElementById('startMining');
        const progressBar = document.getElementById('miningProgress');
        
        if (this.miningStats.isMining) {
            // Stop mining
            this.miningStats.isMining = false;
            button.textContent = 'Iniciar Mineração';
            button.style.background = 'linear-gradient(135deg, var(--primary-color), var(--primary-light))';
            
            if (this.miningInterval) {
                clearInterval(this.miningInterval);
                this.miningInterval = null;
            }
        } else {
            // Start mining
            this.miningStats.isMining = true;
            button.textContent = 'Parar Mineração';
            button.style.background = 'linear-gradient(135deg, var(--error-color), #f87171)';
            
            this.miningInterval = setInterval(() => {
                this.updateMiningStats();
            }, 100);
        }
    }

    updateMiningStats() {
        // Simulate mining process
        this.miningStats.hashRate = Math.floor(Math.random() * 1000) + 100;
        this.miningStats.blocksMined += Math.random() < 0.01 ? 1 : 0; // 1% chance per update
        this.miningStats.totalReward = this.miningStats.blocksMined * 6.25;
        
        // Update UI
        document.getElementById('hashRate').textContent = `${this.miningStats.hashRate.toLocaleString()} H/s`;
        document.getElementById('blocksMined').textContent = this.miningStats.blocksMined;
        document.getElementById('totalReward').textContent = `${this.miningStats.totalReward.toFixed(8)} BTC`;
        
        // Update progress bar
        const progress = (this.miningStats.hashRate / 1000) * 100;
        document.getElementById('miningProgress').style.width = `${Math.min(progress, 100)}%`;
        
        // Add chat message when block is mined
        if (this.miningStats.blocksMined > 0 && this.miningStats.blocksMined % 1 === 0) {
            this.addChatMessage('assistant', `🎉 Bloco minerado! Recompensa: 6.25 BTC. Total: ${this.miningStats.totalReward.toFixed(8)} BTC`);
        }
    }

    simulateTransaction() {
        const amount = parseFloat(document.getElementById('txAmount').value);
        const fee = parseInt(document.getElementById('txFee').value);
        const statusDiv = document.getElementById('txStatus');
        
        if (amount <= 0) {
            statusDiv.textContent = 'Erro: Valor deve ser maior que zero';
            statusDiv.className = 'tx-status error';
            return;
        }
        
        // Simulate transaction processing
        statusDiv.textContent = 'Processando transação...';
        statusDiv.className = 'tx-status';
        
        setTimeout(() => {
            const success = Math.random() > 0.1; // 90% success rate
            
            if (success) {
                const txId = this.generateTransactionId();
                statusDiv.textContent = `✅ Transação confirmada! TX ID: ${txId}`;
                statusDiv.className = 'tx-status success';
                
                this.addChatMessage('assistant', `Transação de ${amount} BTC enviada com sucesso! Taxa: ${fee} sat/byte`);
            } else {
                statusDiv.textContent = '❌ Transação falhou. Tente novamente.';
                statusDiv.className = 'tx-status error';
            }
        }, 2000);
    }

    generateTransactionId() {
        return '0x' + Math.random().toString(16).substr(2, 64);
    }

    toggleFAQ(faqItem) {
        const isActive = faqItem.classList.contains('active');
        
        // Close all FAQ items
        document.querySelectorAll('.faq-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Open clicked item if it wasn't active
        if (!isActive) {
            faqItem.classList.add('active');
        }
    }

    sendChatMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (message) {
            this.addChatMessage('user', message);
            input.value = '';
            
            // Simulate assistant response
            setTimeout(() => {
                this.generateAssistantResponse(message);
            }, 1000);
        }
    }

    addChatMessage(sender, message) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'user' ? '👤' : '🤖';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = `<p>${message}</p>`;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Store in history
        this.chatHistory.push({ sender, message, timestamp: new Date() });
    }

    generateAssistantResponse(userMessage) {
        const lowerMessage = userMessage.toLowerCase();
        let response = '';
        
        if (lowerMessage.includes('mineração') || lowerMessage.includes('mining')) {
            response = this.assistantResponses.mining[Math.floor(Math.random() * this.assistantResponses.mining.length)];
        } else if (lowerMessage.includes('blockchain')) {
            response = this.assistantResponses.blockchain[Math.floor(Math.random() * this.assistantResponses.blockchain.length)];
        } else if (lowerMessage.includes('carteira') || lowerMessage.includes('wallet')) {
            response = this.assistantResponses.wallet[Math.floor(Math.random() * this.assistantResponses.wallet.length)];
        } else if (lowerMessage.includes('halving')) {
            response = this.assistantResponses.halving[Math.floor(Math.random() * this.assistantResponses.halving.length)];
        } else if (lowerMessage.includes('preço') || lowerMessage.includes('price')) {
            response = this.assistantResponses.price[Math.floor(Math.random() * this.assistantResponses.price.length)];
        } else if (lowerMessage.includes('seguro') || lowerMessage.includes('security')) {
            response = this.assistantResponses.security[Math.floor(Math.random() * this.assistantResponses.security.length)];
        } else {
            response = this.assistantResponses.greetings[Math.floor(Math.random() * this.assistantResponses.greetings.length)];
        }
        
        this.addChatMessage('assistant', response);
    }

    toggleChat() {
        const chatContainer = document.getElementById('chatContainer');
        const toggleButton = document.getElementById('chatToggle');
        
        if (chatContainer.classList.contains('minimized')) {
            chatContainer.classList.remove('minimized');
            toggleButton.textContent = '−';
        } else {
            chatContainer.classList.add('minimized');
            toggleButton.textContent = '+';
        }
    }

    updateAssistantMessage(section = null) {
        const assistantMessage = document.getElementById('assistantMessage');
        let message = '';
        
        if (section) {
            switch (section) {
                case 'fundamentals':
                    message = 'Explore os conceitos fundamentais do Bitcoin. Clique em qualquer card para saber mais detalhes!';
                    break;
                case 'simulations':
                    message = 'Experimente simulações interativas de mineração e transações. Veja como funciona na prática!';
                    break;
                case 'analysis':
                    message = 'Acompanhe dados em tempo real do Bitcoin. Os preços são atualizados automaticamente.';
                    break;
                case 'faq':
                    message = 'Encontre respostas para as perguntas mais comuns sobre Bitcoin. Clique para expandir!';
                    break;
                default:
                    message = 'Navegue pelas seções para explorar diferentes aspectos do Bitcoin. Estou aqui para ajudar!';
            }
        } else {
            const messages = [
                'O Bitcoin está revolucionando o sistema financeiro global. Que tal explorarmos juntos?',
                'Interessado em entender como funciona a mineração? Vamos simular!',
                'Dados em tempo real mostram a dinâmica do mercado Bitcoin. Vamos analisar?',
                'Tem dúvidas sobre Bitcoin? Estou aqui para esclarecer tudo!'
            ];
            message = messages[Math.floor(Math.random() * messages.length)];
        }
        
        assistantMessage.querySelector('p').textContent = message;
    }

    async loadBitcoinData() {
        try {
            // Simulate API call with realistic data
            const mockData = {
                price: 45000 + Math.random() * 10000,
                marketCap: 850000000000 + Math.random() * 100000000000,
                volume24h: 25000000000 + Math.random() * 10000000000,
                dominance: 48 + Math.random() * 4,
                change24h: (Math.random() - 0.5) * 10
            };
            
            this.bitcoinData = mockData;
            this.updateBitcoinData();
            
            // Update every 30 seconds
            setInterval(() => {
                this.loadBitcoinData();
            }, 30000);
            
        } catch (error) {
            console.error('Error loading Bitcoin data:', error);
        }
    }

    updateBitcoinData() {
        const { price, marketCap, volume24h, dominance, change24h } = this.bitcoinData;
        
        // Update price display
        const priceAmount = document.querySelector('.price-amount');
        const priceChange = document.querySelector('.price-change');
        
        priceAmount.textContent = `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        priceChange.textContent = `${change24h >= 0 ? '+' : ''}${change24h.toFixed(2)}%`;
        priceChange.className = `price-change ${change24h >= 0 ? 'positive' : 'negative'}`;
        
        // Update other metrics
        document.getElementById('marketCap').textContent = `$${(marketCap / 1e9).toFixed(1)}B`;
        document.getElementById('volume24h').textContent = `$${(volume24h / 1e9).toFixed(1)}B`;
        document.getElementById('dominance').textContent = `${dominance.toFixed(1)}%`;
    }

    setupChart() {
        const ctx = document.getElementById('priceChart').getContext('2d');
        
        // Generate mock price data for the last 30 days
        const labels = [];
        const data = [];
        const basePrice = 45000;
        
        for (let i = 29; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' }));
            
            // Generate realistic price movement
            const randomChange = (Math.random() - 0.5) * 0.1; // ±5% daily change
            const newPrice = basePrice * (1 + randomChange);
            data.push(newPrice);
        }
        
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Preço Bitcoin (USD)',
                    data: data,
                    borderColor: getComputedStyle(document.documentElement).getPropertyValue('--primary-color'),
                    backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--primary-color') + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color')
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary')
                        }
                    },
                    y: {
                        grid: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color')
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary'),
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    updateChartColors() {
        if (this.chart) {
            const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color');
            const borderColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color');
            const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary');
            
            this.chart.data.datasets[0].borderColor = primaryColor;
            this.chart.data.datasets[0].backgroundColor = primaryColor + '20';
            
            this.chart.options.scales.x.grid.color = borderColor;
            this.chart.options.scales.x.ticks.color = textColor;
            this.chart.options.scales.y.grid.color = borderColor;
            this.chart.options.scales.y.ticks.color = textColor;
            
            this.chart.update();
        }
    }

    generateRandomPrimaryColor() {
        // Generate a random color with guaranteed contrast
        const colors = [
            '#6366f1', // Indigo
            '#8b5cf6', // Violet
            '#06b6d4', // Cyan
            '#10b981', // Emerald
            '#f59e0b', // Amber
            '#ef4444', // Red
            '#ec4899', // Pink
            '#84cc16'  // Lime
        ];
        
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        document.documentElement.style.setProperty('--primary-color', randomColor);
        
        // Generate light and dark variants
        const color = randomColor;
        const lightColor = this.adjustColor(color, 20);
        const darkColor = this.adjustColor(color, -20);
        
        document.documentElement.style.setProperty('--primary-light', lightColor);
        document.documentElement.style.setProperty('--primary-dark', darkColor);
    }

    adjustColor(color, amount) {
        const hex = color.replace('#', '');
        const r = Math.max(0, Math.min(255, parseInt(hex.substr(0, 2), 16) + amount));
        const g = Math.max(0, Math.min(255, parseInt(hex.substr(2, 2), 16) + amount));
        const b = Math.max(0, Math.min(255, parseInt(hex.substr(4, 2), 16) + amount));
        
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BitcoinSimulator();
});

// Add some interactive features
document.addEventListener('DOMContentLoaded', () => {
    // Add typing effect to assistant messages
    const typeWriter = (element, text, speed = 50) => {
        let i = 0;
        element.innerHTML = '';
        const timer = setInterval(() => {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
            }
        }, speed);
    };

    // Add hover effects to concept cards
    document.querySelectorAll('.concept-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Add smooth scrolling for navigation
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});