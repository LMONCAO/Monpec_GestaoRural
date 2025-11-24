/**
 * Super Tela Curral - Funcionalidades Avançadas
 * MONPEC - Sistema de Gestão Pecuária
 */

class CurralSuperTelaEnhanced {
    constructor() {
        this.sessionStartTime = new Date();
        this.animalsProcessed = 0;
        this.totalTime = 0;
        this.alerts = [];
        this.predictions = {};
        this.performanceMetrics = {
            animalsPerHour: 0,
            avgTimePerAnimal: 0,
            estimatedCompletion: null
        };
        
        this.init();
    }

    init() {
        this.setupPerformanceDashboard();
        this.setupIntelligentAlerts();
        this.setupVoiceCommands();
        this.setupDataValidation();
        this.setupDarkMode();
        this.setupPredictions();
        this.setupAutoAparteRecommendation();
        this.startPerformanceTracking();
    }

    // ==================== DASHBOARD DE PERFORMANCE ====================
    setupPerformanceDashboard() {
        const dashboardHTML = `
            <div class="performance-dashboard" id="performanceDashboard">
                <div class="perf-header">
                    <h3><i class="fas fa-tachometer-alt"></i> Performance da Sessão</h3>
                    <button class="btn-toggle-perf" id="togglePerfBtn">
                        <i class="fas fa-chevron-down"></i>
                    </button>
                </div>
                <div class="perf-content" id="perfContent">
                    <div class="perf-grid">
                        <div class="perf-card">
                            <div class="perf-icon primary">
                                <i class="fas fa-cow"></i>
                            </div>
                            <div class="perf-info">
                                <div class="perf-value" id="animalsProcessedCount">0</div>
                                <div class="perf-label">Animais Processados</div>
                            </div>
                        </div>
                        <div class="perf-card">
                            <div class="perf-icon success">
                                <i class="fas fa-clock"></i>
                            </div>
                            <div class="perf-info">
                                <div class="perf-value" id="animalsPerHour">0</div>
                                <div class="perf-label">Animais/Hora</div>
                            </div>
                        </div>
                        <div class="perf-card">
                            <div class="perf-icon warning">
                                <i class="fas fa-stopwatch"></i>
                            </div>
                            <div class="perf-info">
                                <div class="perf-value" id="avgTimePerAnimal">0s</div>
                                <div class="perf-label">Tempo Médio</div>
                            </div>
                        </div>
                        <div class="perf-card">
                            <div class="perf-icon info">
                                <i class="fas fa-hourglass-half"></i>
                            </div>
                            <div class="perf-info">
                                <div class="perf-value" id="estimatedCompletion">--:--</div>
                                <div class="perf-label">Previsão Término</div>
                            </div>
                        </div>
                    </div>
                    <div class="perf-progress">
                        <div class="perf-progress-label">
                            <span>Progresso da Sessão</span>
                            <span id="progressPercentage">0%</span>
                        </div>
                        <div class="perf-progress-bar">
                            <div class="perf-progress-fill" id="progressFill" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Insere o dashboard antes do work-form-container
        const container = document.querySelector('.work-form-container');
        if (container) {
            container.insertAdjacentHTML('beforebegin', dashboardHTML);
        }

        // Toggle do dashboard
        const toggleBtn = document.getElementById('togglePerfBtn');
        const perfContent = document.getElementById('perfContent');
        if (toggleBtn && perfContent) {
            toggleBtn.addEventListener('click', () => {
                perfContent.classList.toggle('collapsed');
                toggleBtn.querySelector('i').classList.toggle('fa-chevron-down');
                toggleBtn.querySelector('i').classList.toggle('fa-chevron-up');
            });
        }
    }

    startPerformanceTracking() {
        setInterval(() => {
            this.updatePerformanceMetrics();
        }, 1000);
    }

    updatePerformanceMetrics() {
        const elapsed = (new Date() - this.sessionStartTime) / 1000; // segundos
        const hours = elapsed / 3600;
        
        this.performanceMetrics.animalsPerHour = hours > 0 ? (this.animalsProcessed / hours).toFixed(1) : 0;
        this.performanceMetrics.avgTimePerAnimal = this.animalsProcessed > 0 
            ? (this.totalTime / this.animalsProcessed).toFixed(1) 
            : 0;

        // Atualiza UI
        const animalsPerHourEl = document.getElementById('animalsPerHour');
        const avgTimeEl = document.getElementById('avgTimePerAnimal');
        const animalsCountEl = document.getElementById('animalsProcessedCount');
        
        if (animalsPerHourEl) animalsPerHourEl.textContent = this.performanceMetrics.animalsPerHour;
        if (avgTimeEl) avgTimeEl.textContent = `${this.performanceMetrics.avgTimePerAnimal}s`;
        if (animalsCountEl) animalsCountEl.textContent = this.animalsProcessed;
    }

    recordAnimalProcessed(processingTime) {
        this.animalsProcessed++;
        this.totalTime += processingTime;
        this.updatePerformanceMetrics();
    }

    // ==================== ALERTAS INTELIGENTES ====================
    setupIntelligentAlerts() {
        this.alertContainer = document.createElement('div');
        this.alertContainer.className = 'intelligent-alerts-container';
        this.alertContainer.id = 'intelligentAlerts';
        document.body.appendChild(this.alertContainer);
    }

    checkIntelligentAlerts(animalData, pesoAtual) {
        const alerts = [];

        // Alerta: Ganho de peso abaixo do esperado
        if (animalData.ultimoPeso && pesoAtual) {
            const ganho = pesoAtual - animalData.ultimoPeso;
            const diasDesdeUltima = animalData.diasDesdeUltima || 30;
            const ganhoDiarioEsperado = 0.8; // kg/dia esperado
            const ganhoDiarioAtual = ganho / diasDesdeUltima;
            
            if (ganhoDiarioAtual < ganhoDiarioEsperado * 0.7) {
                alerts.push({
                    type: 'warning',
                    icon: 'fas fa-exclamation-triangle',
                    title: 'Ganho de Peso Abaixo do Esperado',
                    message: `Este animal está ganhando ${ganhoDiarioAtual.toFixed(2)} kg/dia, abaixo da média esperada de ${ganhoDiarioEsperado} kg/dia. Verifique saúde e nutrição.`,
                    priority: 'high'
                });
            }
        }

        // Alerta: Peso muito diferente do histórico
        if (animalData.ultimoPeso && pesoAtual) {
            const diferenca = Math.abs(pesoAtual - animalData.ultimoPeso);
            const percentualDiferenca = (diferenca / animalData.ultimoPeso) * 100;
            
            if (percentualDiferenca > 15) {
                alerts.push({
                    type: 'error',
                    icon: 'fas fa-exclamation-circle',
                    title: 'Peso Muito Diferente do Histórico',
                    message: `O peso registrado (${pesoAtual} kg) difere ${percentualDiferenca.toFixed(1)}% do último peso (${animalData.ultimoPeso} kg). Confirme se está correto.`,
                    priority: 'critical',
                    action: 'confirm'
                });
            }
        }

        // Alerta: Vacina pendente
        if (animalData.vacinaPendente) {
            alerts.push({
                type: 'info',
                icon: 'fas fa-syringe',
                title: 'Vacina Pendente',
                message: `${animalData.vacinaPendente.nome} está atrasada há ${animalData.vacinaPendente.diasAtraso} dias.`,
                priority: 'medium'
            });
        }

        // Alerta: Animal pronto para venda
        if (pesoAtual >= 380) {
            alerts.push({
                type: 'success',
                icon: 'fas fa-check-circle',
                title: 'Animal Pronto para Venda',
                message: `Este animal atingiu ${pesoAtual} kg e está classificado como Boiada. Considere apartação para venda.`,
                priority: 'low'
            });
        }

        // Exibe alertas
        alerts.forEach(alert => this.showAlert(alert));
    }

    showAlert(alert) {
        const alertEl = document.createElement('div');
        alertEl.className = `intelligent-alert alert-${alert.type} priority-${alert.priority}`;
        alertEl.innerHTML = `
            <div class="alert-icon">
                <i class="${alert.icon}"></i>
            </div>
            <div class="alert-content">
                <div class="alert-title">${alert.title}</div>
                <div class="alert-message">${alert.message}</div>
            </div>
            <button class="alert-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        this.alertContainer.appendChild(alertEl);

        // Auto-remove após 10 segundos (exceto críticos)
        if (alert.priority !== 'critical') {
            setTimeout(() => {
                if (alertEl.parentElement) {
                    alertEl.remove();
                }
            }, 10000);
        }
    }

    // ==================== COMANDOS DE VOZ AVANÇADOS ====================
    setupVoiceCommands() {
        if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.voiceRecognition = new SpeechRecognition();
        this.voiceRecognition.continuous = true;
        this.voiceRecognition.interimResults = false;
        this.voiceRecognition.lang = 'pt-BR';

        this.voiceCommands = {
            'próximo animal': () => this.executeCommand('nextAnimal'),
            'próximo': () => this.executeCommand('nextAnimal'),
            'salvar': () => this.executeCommand('save'),
            'salvar e próximo': () => this.executeCommand('saveAndNext'),
            'limpar': () => this.executeCommand('clear'),
            'peso': (value) => this.executeCommand('setWeight', value),
            'mostrar histórico': () => this.executeCommand('showHistory'),
            'mostrar alertas': () => this.executeCommand('showAlerts'),
            'fechar': () => this.executeCommand('close'),
        };

        this.voiceRecognition.onresult = (event) => {
            const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
            this.processVoiceCommand(transcript);
        };

        this.voiceRecognition.onerror = (event) => {
            console.error('Erro no reconhecimento de voz:', event.error);
        };
    }

    processVoiceCommand(transcript) {
        // Procura por comandos conhecidos
        for (const [command, handler] of Object.entries(this.voiceCommands)) {
            if (transcript.includes(command)) {
                // Extrai valor se houver (ex: "peso 350")
                const match = transcript.match(/peso\s+(\d+(?:[.,]\d+)?)/);
                if (match) {
                    const value = parseFloat(match[1].replace(',', '.'));
                    handler(value);
                } else {
                    handler();
                }
                return;
            }
        }

        // Comando não reconhecido - tenta interpretar
        this.interpretNaturalCommand(transcript);
    }

    interpretNaturalCommand(transcript) {
        // Interpreta comandos naturais
        if (transcript.includes('próximo') || transcript.includes('seguinte')) {
            this.executeCommand('nextAnimal');
        } else if (transcript.includes('salvar') && transcript.includes('próximo')) {
            this.executeCommand('saveAndNext');
        } else if (transcript.includes('limpar') || transcript.includes('limpa')) {
            this.executeCommand('clear');
        }
    }

    executeCommand(command, value = null) {
        switch (command) {
            case 'nextAnimal':
                const nextBtn = document.getElementById('nextAnimalBtn');
                if (nextBtn) nextBtn.click();
                break;
            case 'save':
                const saveBtn = document.getElementById('saveBtn');
                if (saveBtn) saveBtn.click();
                break;
            case 'saveAndNext':
                const saveBtn2 = document.getElementById('saveBtn');
                if (saveBtn2) {
                    saveBtn2.click();
                    setTimeout(() => {
                        const nextBtn2 = document.getElementById('nextAnimalBtn');
                        if (nextBtn2) nextBtn2.click();
                    }, 500);
                }
                break;
            case 'clear':
                const clearBtn = document.getElementById('limparPesoBtn');
                if (clearBtn) clearBtn.click();
                break;
            case 'setWeight':
                if (value) {
                    const pesoInput = document.getElementById('manualPesoInput');
                    if (pesoInput) {
                        pesoInput.value = value;
                        pesoInput.dispatchEvent(new Event('input'));
                    }
                }
                break;
            case 'showHistory':
                this.showAnimalHistory();
                break;
            case 'showAlerts':
                this.showAllAlerts();
                break;
        }
    }

    startVoiceRecognition() {
        if (this.voiceRecognition) {
            this.voiceRecognition.start();
        }
    }

    stopVoiceRecognition() {
        if (this.voiceRecognition) {
            this.voiceRecognition.stop();
        }
    }

    // ==================== VALIDAÇÃO AUTOMÁTICA ====================
    setupDataValidation() {
        // Valida peso ao ser inserido
        const pesoInput = document.getElementById('manualPesoInput');
        if (pesoInput) {
            pesoInput.addEventListener('blur', (e) => {
                this.validateWeight(parseFloat(e.target.value));
            });
        }

        // Valida brinco ao ser inserido
        const brincoInput = document.getElementById('brincoInput');
        if (brincoInput) {
            brincoInput.addEventListener('blur', (e) => {
                this.validateBrinco(e.target.value);
            });
        }
    }

    validateWeight(peso) {
        if (!peso || isNaN(peso)) return;

        // Busca último peso do animal (simulado - deve vir do backend)
        const animalBrinco = document.getElementById('brincoInput')?.value;
        if (!animalBrinco) return;

        // Simulação - em produção, buscar do backend
        const ultimoPeso = 350; // Exemplo
        const diferenca = Math.abs(peso - ultimoPeso);
        const percentual = (diferenca / ultimoPeso) * 100;

        if (percentual > 20) {
            const confirmar = confirm(
                `⚠️ ATENÇÃO: O peso registrado (${peso} kg) difere ${percentual.toFixed(1)}% do último peso conhecido (${ultimoPeso} kg).\n\n` +
                `Isso pode indicar:\n` +
                `- Erro de digitação\n` +
                `- Problema de saúde do animal\n` +
                `- Balança descalibrada\n\n` +
                `Deseja confirmar este peso?`
            );

            if (!confirmar) {
                const pesoInput = document.getElementById('manualPesoInput');
                if (pesoInput) pesoInput.value = '';
                return false;
            }
        }

        return true;
    }

    validateBrinco(brinco) {
        if (!brinco || brinco.length < 4) return;

        // Verifica se brinco já foi processado na sessão
        // Em produção, verificar no backend
        const registrosSessao = window.registrosSessao || [];
        const jaProcessado = registrosSessao.some(r => r.brinco === brinco);

        if (jaProcessado) {
            const continuar = confirm(
                `⚠️ Este animal (${brinco}) já foi processado nesta sessão.\n\n` +
                `Deseja continuar mesmo assim?`
            );

            if (!continuar) {
                const brincoInput = document.getElementById('brincoInput');
                if (brincoInput) brincoInput.value = '';
                return false;
            }
        }

        return true;
    }

    // ==================== TEMA ESCURO ====================
    setupDarkMode() {
        const darkModeToggle = document.createElement('button');
        darkModeToggle.className = 'dark-mode-toggle';
        darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        darkModeToggle.title = 'Alternar tema escuro';
        darkModeToggle.addEventListener('click', () => this.toggleDarkMode());

        // Insere o botão no header
        const formHeader = document.querySelector('.form-header');
        if (formHeader) {
            formHeader.appendChild(darkModeToggle);
        }

        // Carrega preferência salva
        const saved = localStorage.getItem('curralDarkMode');
        if (saved === 'true') {
            this.enableDarkMode();
        }
    }

    toggleDarkMode() {
        const isDark = document.body.classList.contains('dark-mode');
        if (isDark) {
            this.disableDarkMode();
        } else {
            this.enableDarkMode();
        }
    }

    enableDarkMode() {
        document.body.classList.add('dark-mode');
        localStorage.setItem('curralDarkMode', 'true');
    }

    disableDarkMode() {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('curralDarkMode', 'false');
    }

    // ==================== PREDIÇÕES ====================
    setupPredictions() {
        // Predição de peso futuro baseada em histórico
        // Em produção, usar algoritmo de ML
    }

    predictFutureWeight(currentWeight, history) {
        if (!history || history.length < 2) return null;

        // Cálculo simples de tendência linear
        const weights = history.map(h => h.peso);
        const dates = history.map(h => new Date(h.data));
        
        // Calcula ganho médio diário
        let totalGain = 0;
        let totalDays = 0;
        
        for (let i = 1; i < weights.length; i++) {
            const gain = weights[i] - weights[i - 1];
            const days = (dates[i] - dates[i - 1]) / (1000 * 60 * 60 * 24);
            if (days > 0) {
                totalGain += gain;
                totalDays += days;
            }
        }

        const avgDailyGain = totalDays > 0 ? totalGain / totalDays : 0.8; // padrão 0.8 kg/dia

        // Predições para 30, 60, 90 dias
        return {
            em30dias: currentWeight + (avgDailyGain * 30),
            em60dias: currentWeight + (avgDailyGain * 60),
            em90dias: currentWeight + (avgDailyGain * 90),
            ganhoDiarioMedio: avgDailyGain
        };
    }

    // ==================== RECOMENDAÇÃO DE APARTE ====================
    setupAutoAparteRecommendation() {
        // Recomenda apartação baseada em múltiplos fatores
    }

    recommendAparte(peso, ganhoDiario, idade, historicoReprodutivo) {
        const recomendacoes = [];

        // Baseado em peso
        if (peso >= 380) {
            recomendacoes.push({
                tipo: 'Boiada',
                motivo: 'Peso ideal para venda atingido',
                prioridade: 'alta'
            });
        } else if (peso >= 300) {
            recomendacoes.push({
                tipo: 'Cabeceira',
                motivo: 'Próximo do peso de venda',
                prioridade: 'media'
            });
        }

        // Baseado em ganho de peso
        if (ganhoDiario < 0.5) {
            recomendacoes.push({
                tipo: 'Refugo',
                motivo: 'Ganho de peso abaixo do esperado',
                prioridade: 'alta'
            });
        }

        return recomendacoes;
    }

    // ==================== UTILITÁRIOS ====================
    showAnimalHistory() {
        // Mostra histórico do animal em modal
        alert('Funcionalidade de histórico será implementada em breve.');
    }

    showAllAlerts() {
        // Mostra todos os alertas em modal
        const alerts = this.alertContainer.querySelectorAll('.intelligent-alert');
        if (alerts.length === 0) {
            alert('Nenhum alerta ativo no momento.');
        }
    }
}

// Inicializa quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.curralEnhanced = new CurralSuperTelaEnhanced();
    });
} else {
    window.curralEnhanced = new CurralSuperTelaEnhanced();
}







