/**
 * Tela Única Curral - JavaScript Principal
 * MONPEC - Sistema de Gestão Pecuária
 * Integra todas as funcionalidades em uma tela única
 */

class CurralTelaUnica {
    constructor() {
        this.animalAtual = null;
        this.pesoAtual = 0;
        this.tabAtiva = 'pesagem';
        this.isOnline = navigator.onLine;
        this.recognition = null;
        this.scanStream = null;
        this.charts = {};
        this.metricas = {
            animais: 0,
            pesagens: 0,
            tratamentos: 0,
            ganhoMedio: 0
        };
        this.sessaoAtiva = null;
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupTabs();
        this.setupScanner();
        this.setupPesagem();
        this.setupForms();
        this.setupOfflineDetection();
        this.setupVoiceRecognition();
        this.setupCameraScan();
        this.setupMetricas();
        this.setupSessaoAtiva();
        this.setupAlertas();
        this.setupQuickActions();
        this.setupHistorico();
        
        // Inicializa IndexedDB se disponível
        if (window.offlineDB) {
            await window.offlineDB.init();
        }
        
        // Carrega métricas iniciais
        await this.carregarMetricas();
        await this.carregarSessaoAtiva();
    }

    // ==================== EVENT LISTENERS ====================
    setupEventListeners() {
        // Botão de sincronização
        const btnSync = document.getElementById('btnSync');
        if (btnSync) {
            btnSync.addEventListener('click', () => this.sincronizar());
        }

        // Botão de fechar animal
        const btnCloseAnimal = document.getElementById('btnCloseAnimal');
        if (btnCloseAnimal) {
            btnCloseAnimal.addEventListener('click', () => this.fecharAnimal());
        }

        // Detecção de mudança de conexão
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
    }

    // ==================== TABS ====================
    setupTabs() {
        // Suporta tanto os botões antigos (.tab-btn) quanto os novos cards (.processo-card)
        const tabBtns = document.querySelectorAll('.tab-btn, .processo-card');
        const tabContents = document.querySelectorAll('.tab-content');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.getAttribute('data-tab');
                if (tabId) {
                    this.ativarTab(tabId);
                }
            });
        });
    }

    ativarTab(tabId) {
        // Remove active de todas as tabs e cards
        document.querySelectorAll('.tab-btn, .processo-card').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

        // Ativa a tab selecionada (suporta ambos os seletores)
        const btnAtivo = document.querySelector(`[data-tab="${tabId}"]`);
        const contentAtivo = document.getElementById(`tab-${tabId}`);

        if (btnAtivo) btnAtivo.classList.add('active');
        if (contentAtivo) contentAtivo.classList.add('active');

        this.tabAtiva = tabId;

        // Scroll suave para o conteúdo da tab
        if (contentAtivo) {
            contentAtivo.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    // ==================== SCANNER ====================
    setupScanner() {
        const scannerInput = document.getElementById('scannerInput');
        if (!scannerInput) return;

        // Enter para buscar
        scannerInput.addEventListener('keypress', async (e) => {
            if (e.key === 'Enter') {
                const brinco = scannerInput.value.trim();
                if (brinco.length >= 4) {
                    await this.buscarAnimal(brinco);
                }
            }
        });

        // Foco automático
        scannerInput.focus();
    }

    async buscarAnimal(brinco) {
        try {
            // Tenta buscar online primeiro
            if (this.isOnline) {
                const response = await fetch(`/api/curral/animal/${brinco}/`);
                if (response.ok) {
                    this.animalAtual = await response.json();
                    this.exibirAnimal(this.animalAtual);
                    return;
                }
            }

            // Se offline ou não encontrado, busca no IndexedDB
            if (window.offlineDB) {
                const animal = await window.offlineDB.buscarAnimal(brinco);
                if (animal) {
                    this.animalAtual = animal;
                    this.exibirAnimal(this.animalAtual);
                    return;
                }
            }

            // Animal não encontrado
            this.mostrarNotificacao('Animal não encontrado', 'Verifique o número do brinco.', 'error');
            
        } catch (error) {
            console.error('Erro ao buscar animal:', error);
            this.mostrarNotificacao('Erro', 'Não foi possível buscar o animal.', 'error');
        }
    }

    exibirAnimal(animal) {
        const animalCard = document.getElementById('animalCard');
        if (!animalCard) return;

        // Preenche informações
        document.getElementById('animalBrinco').textContent = animal.brinco || '—';
        document.getElementById('animalRaca').textContent = animal.raca || '—';
        document.getElementById('animalSexo').textContent = animal.sexo === 'M' ? 'Macho' : animal.sexo === 'F' ? 'Fêmea' : '—';
        document.getElementById('animalIdade').textContent = this.calcularIdade(animal.data_nascimento) || '—';
        document.getElementById('animalUltimoPeso').textContent = animal.ultimo_peso ? `${animal.ultimo_peso} kg` : '—';
        document.getElementById('animalLote').textContent = animal.lote || '—';
        document.getElementById('animalCategoria').textContent = animal.categoria || '—';

        // Exibe o card
        animalCard.style.display = 'block';
        animalCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Carrega dados adicionais
        this.carregarComparacaoLote(animal);
        this.carregarHistoricoPeso(animal);
        this.verificarAlertas(animal);
    }

    fecharAnimal() {
        const animalCard = document.getElementById('animalCard');
        if (animalCard) {
            animalCard.style.display = 'none';
        }
        this.animalAtual = null;
        
        // Limpa scanner
        const scannerInput = document.getElementById('scannerInput');
        if (scannerInput) {
            scannerInput.value = '';
            scannerInput.focus();
        }
    }

    calcularIdade(dataNascimento) {
        if (!dataNascimento) return null;
        
        const nascimento = new Date(dataNascimento);
        const hoje = new Date();
        const diff = hoje - nascimento;
        const anos = Math.floor(diff / (1000 * 60 * 60 * 24 * 365));
        const meses = Math.floor((diff % (1000 * 60 * 60 * 24 * 365)) / (1000 * 60 * 60 * 24 * 30));
        
        if (anos > 0) {
            return `${anos} ano${anos > 1 ? 's' : ''}${meses > 0 ? ` e ${meses} mês${meses > 1 ? 'es' : ''}` : ''}`;
        }
        return `${meses} mês${meses > 1 ? 'es' : ''}`;
    }

    // ==================== PESAGEM ====================
    setupPesagem() {
        const btnSimular = document.getElementById('btnSimularPeso');
        const btnManual = document.getElementById('btnPesoManual');
        const btnVoz = document.getElementById('btnPesoVoz');
        const btnLimpar = document.getElementById('btnLimparPeso');
        const btnSalvar = document.getElementById('btnSalvarPesagem');

        if (btnSimular) {
            btnSimular.addEventListener('click', () => this.simularPeso());
        }

        if (btnManual) {
            btnManual.addEventListener('click', () => this.ativarModoManual());
        }

        if (btnVoz) {
            btnVoz.addEventListener('click', () => this.ativarModoVoz());
        }

        if (btnLimpar) {
            btnLimpar.addEventListener('click', () => this.limparPeso());
        }

        if (btnSalvar) {
            btnSalvar.addEventListener('click', () => this.salvarPesagem());
        }

        // Listener para eventos de balança (se disponível)
        if (window.MONPEC_BALANCA) {
            // Escuta eventos de peso da balança
            if (typeof window.MONPEC_BALANCA.onPeso === 'function') {
                window.MONPEC_BALANCA.onPeso((peso) => {
                    if (peso && peso > 0) {
                        this.atualizarPeso(peso);
                        this.mostrarNotificacao('Peso recebido', `${peso.toFixed(1)} kg`, 'success');
                    }
                });
            }
            
            // Tenta ler peso periodicamente se estiver em modo balança
            setInterval(async () => {
                if (window.MONPEC_BALANCA && typeof window.MONPEC_BALANCA.lerPeso === 'function') {
                    try {
                        const peso = await window.MONPEC_BALANCA.lerPeso();
                        if (peso && peso > 0 && this.pesoAtual !== peso) {
                            this.atualizarPeso(peso);
                        }
                    } catch (error) {
                        // Silencioso - não mostra erro se a balança não estiver conectada
                    }
                }
            }, 2000); // Verifica a cada 2 segundos
        }

        // Listener para eventos customizados de peso (para integração com outras partes do sistema)
        window.addEventListener('pesoAtualizado', (event) => {
            if (event.detail && event.detail.peso) {
                this.atualizarPeso(event.detail.peso);
            }
        });
    }

    simularPeso() {
        const pesos = [185, 220, 275, 320, 195, 240, 285, 335];
        const pesoAleatorio = pesos[Math.floor(Math.random() * pesos.length)];
        this.atualizarPeso(pesoAleatorio);
    }

    atualizarPeso(peso) {
        // Garante que o peso seja um número válido
        const pesoNum = parseFloat(peso);
        if (isNaN(pesoNum) || pesoNum <= 0) {
            console.warn('Peso inválido:', peso);
            return;
        }
        
        this.pesoAtual = pesoNum;
        const pesoNumero = document.getElementById('pesoNumero');
        if (pesoNumero) {
            pesoNumero.textContent = pesoNum.toFixed(1);
        }

        // Atualiza informações de ganho
        const ultimoPeso = this.animalAtual?.ultimo_peso || this.animalAtual?.peso_atual;
        if (this.animalAtual && ultimoPeso) {
            const ganho = pesoNum - ultimoPeso;
            const ganhoUltima = document.getElementById('ganhoUltima');
            if (ganhoUltima) {
                ganhoUltima.textContent = `${ganho > 0 ? '+' : ''}${ganho.toFixed(1)} kg`;
            }

            // Calcula ganho diário (simulado - deve vir do backend)
            const diasDesdeUltima = 30; // TODO: calcular
            const ganhoDiario = ganho / diasDesdeUltima;
            const ganhoDiarioEl = document.getElementById('ganhoDiario');
            if (ganhoDiarioEl) {
                ganhoDiarioEl.textContent = `${ganhoDiario > 0 ? '+' : ''}${ganhoDiario.toFixed(2)} kg/dia`;
            }
            
            // Dias desde última pesagem
            const diasEl = document.getElementById('diasUltimaPesagem');
            if (diasEl) {
                diasEl.textContent = `${diasDesdeUltima} dias`;
            }

            // Classificação
            const aparte = this.classificarAparte(pesoNum);
            const aparteEl = document.getElementById('aparteClassificacao');
            if (aparteEl) {
                aparteEl.textContent = aparte.nome;
                aparteEl.className = `aparte-badge aparte-${aparte.cor}`;
            }
            
            // Atualiza indicadores
            this.atualizarIndicadoresPesagem(pesoNum, this.animalAtual);
        }
    }

    classificarAparte(peso) {
        if (peso >= 380) return { nome: 'Boiada', cor: 'success' };
        if (peso >= 300) return { nome: 'Cabeceira', cor: 'info' };
        if (peso >= 250) return { nome: 'Meio', cor: 'warning' };
        return { nome: 'Refugo', cor: 'error' };
    }

    ativarModoManual() {
        const peso = prompt('Digite o peso (kg):');
        if (peso) {
            const pesoNum = parseFloat(peso.replace(',', '.'));
            if (!isNaN(pesoNum) && pesoNum > 0) {
                this.atualizarPeso(pesoNum);
                this.mostrarNotificacao('Peso atualizado', `${pesoNum.toFixed(1)} kg`, 'success');
            } else {
                this.mostrarNotificacao('Erro', 'Peso inválido. Digite um número maior que zero.', 'error');
            }
        }
    }

    ativarModoVoz() {
        if (!this.recognition) {
            this.setupVoiceRecognition();
        }

        if (this.recognition) {
            this.recognition.start();
            this.mostrarNotificacao('Ouvindo...', 'Diga o peso em quilos', 'info');
        }
    }

    limparPeso() {
        this.pesoAtual = 0;
        const pesoNumero = document.getElementById('pesoNumero');
        if (pesoNumero) {
            pesoNumero.textContent = '0';
        }
    }

    async salvarPesagem() {
        if (!this.animalAtual) {
            this.mostrarNotificacao('Atenção', 'Identifique um animal primeiro.', 'warning');
            return;
        }

        // Obtém o peso atual do display (pode ter sido atualizado manualmente)
        const pesoNumero = document.getElementById('pesoNumero');
        let pesoValor = this.pesoAtual;
        
        if (pesoNumero) {
            const pesoTexto = pesoNumero.textContent.trim();
            const pesoParseado = parseFloat(pesoTexto.replace(/[^\d.,]/g, '').replace(',', '.'));
            if (!isNaN(pesoParseado) && pesoParseado > 0) {
                pesoValor = pesoParseado;
                this.pesoAtual = pesoValor;
            }
        }

        if (pesoValor <= 0) {
            this.mostrarNotificacao('Atenção', 'Informe o peso do animal.', 'warning');
            return;
        }

        // Obtém propriedade_id da URL
        const urlMatch = window.location.pathname.match(/propriedade\/(\d+)/);
        const propriedadeId = urlMatch ? urlMatch[1] : null;
        
        if (!propriedadeId) {
            this.mostrarNotificacao('Erro', 'Não foi possível identificar a propriedade.', 'error');
            return;
        }

        const pesagem = {
            animal_id: this.animalAtual.id,
            brinco: this.animalAtual.brinco || this.animalAtual.numero_brinco,
            peso: pesoValor
        };

        try {
            if (this.isOnline) {
                // Tenta salvar online usando a rota correta
                const response = await fetch(`/propriedade/${propriedadeId}/curral/api/pesagem/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(pesagem)
                });

                const responseData = await response.json();

                if (response.ok) {
                    this.mostrarNotificacao('Sucesso', 'Pesagem salva com sucesso!', 'success');
                    // Atualiza o animal atual com o novo peso
                    if (this.animalAtual) {
                        this.animalAtual.ultimo_peso = pesoValor;
                        this.animalAtual.peso_atual = pesoValor;
                    }
                    // Atualiza o display do último peso
                    const animalUltimoPeso = document.getElementById('animalUltimoPeso');
                    if (animalUltimoPeso) {
                        animalUltimoPeso.textContent = `${pesoValor.toFixed(1)} kg`;
                    }
                    this.limparPeso();
                    // Recarrega os dados do animal para atualizar informações
                    if (this.animalAtual && this.animalAtual.brinco) {
                        await this.buscarAnimal(this.animalAtual.brinco);
                    }
                    return;
                } else {
                    const mensagemErro = responseData.mensagem || 'Erro ao salvar pesagem.';
                    this.mostrarNotificacao('Erro', mensagemErro, 'error');
                    return;
                }
            }

            // Salva offline
            if (window.offlineDB) {
                await window.offlineDB.salvarPesagem({
                    ...pesagem,
                    propriedade_id: propriedadeId,
                    data: new Date().toISOString()
                });
                this.mostrarNotificacao('Salvo offline', 'A pesagem será sincronizada quando a conexão voltar.', 'info');
                this.limparPeso();
            } else {
                this.mostrarNotificacao('Erro', 'Sistema offline não disponível.', 'error');
            }

        } catch (error) {
            console.error('Erro ao salvar pesagem:', error);
            this.mostrarNotificacao('Erro', `Não foi possível salvar a pesagem: ${error.message}`, 'error');
        }
    }

    // ==================== FORMULÁRIOS ====================
    setupForms() {
        // Formulário de cadastro
        const formCadastro = document.getElementById('formCadastro');
        if (formCadastro) {
            formCadastro.addEventListener('submit', (e) => {
                e.preventDefault();
                this.salvarCadastro();
            });
        }

        // Formulário de sanidade
        const formSanidade = document.getElementById('formSanidade');
        if (formSanidade) {
            formSanidade.addEventListener('submit', (e) => {
                e.preventDefault();
                this.salvarSanidade();
            });
        }

        // Formulário reprodutivo
        const formReprodutivo = document.getElementById('formReprodutivo');
        if (formReprodutivo) {
            formReprodutivo.addEventListener('submit', (e) => {
                e.preventDefault();
                this.salvarReprodutivo();
            });
        }

        // Formulário movimentação
        const formMovimentacao = document.getElementById('formMovimentacao');
        if (formMovimentacao) {
            formMovimentacao.addEventListener('submit', (e) => {
                e.preventDefault();
                this.salvarMovimentacao();
            });
        }

        // Selectors de tipo
        document.querySelectorAll('.treatment-type-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.treatment-type-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        document.querySelectorAll('.procedure-type-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.procedure-type-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Mostra/esconde seções baseado no tipo
                const tipo = btn.getAttribute('data-type');
                document.getElementById('sectionIATF').style.display = tipo === 'iatf' ? 'block' : 'none';
                document.getElementById('sectionDiagnostico').style.display = tipo === 'diagnostico' ? 'block' : 'none';
            });
        });
    }

    async salvarCadastro() {
        const dados = {
            brinco: document.getElementById('cadastroBrinco').value,
            sisbov: document.getElementById('cadastroSisbov').value,
            numero_manejo: document.getElementById('cadastroNumeroManejo').value,
            raca: document.getElementById('cadastroRaca').value,
            sexo: document.getElementById('cadastroSexo').value,
            data_nascimento: document.getElementById('cadastroNascimento').value,
            peso_nascer: document.getElementById('cadastroPesoNascer').value,
            lote_id: document.getElementById('cadastroLote').value,
            pasto: document.getElementById('cadastroPasto').value,
            categoria_id: document.getElementById('cadastroCategoria').value
        };

        try {
            if (this.isOnline) {
                const response = await fetch('/api/curral/animal/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(dados)
                });

                if (response.ok) {
                    this.mostrarNotificacao('Sucesso', 'Animal cadastrado com sucesso!', 'success');
                    formCadastro.reset();
                    return;
                }
            }

            // Salva offline
            if (window.offlineDB) {
                await window.offlineDB.salvarAnimal(dados);
                this.mostrarNotificacao('Salvo offline', 'O cadastro será sincronizado quando a conexão voltar.', 'info');
                formCadastro.reset();
            }

        } catch (error) {
            console.error('Erro ao salvar cadastro:', error);
            this.mostrarNotificacao('Erro', 'Não foi possível salvar o cadastro.', 'error');
        }
    }

    async salvarSanidade() {
        const tipo = document.querySelector('.treatment-type-btn.active')?.getAttribute('data-type') || 'outro';
        const dados = {
            animal_id: this.animalAtual?.id,
            tipo: tipo,
            produto: document.getElementById('sanidadeProduto').value,
            dose: document.getElementById('sanidadeDose').value,
            lote: document.getElementById('sanidadeLote').value,
            data: document.getElementById('sanidadeData').value,
            responsavel: document.getElementById('sanidadeResponsavel').value,
            observacoes: document.getElementById('sanidadeObservacoes').value
        };

        try {
            if (this.isOnline) {
                const response = await fetch('/api/curral/sanidade/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(dados)
                });

                if (response.ok) {
                    this.mostrarNotificacao('Sucesso', 'Tratamento salvo com sucesso!', 'success');
                    document.getElementById('formSanidade').reset();
                    return;
                }
            }

            if (window.offlineDB) {
                await window.offlineDB.salvarSanidade(dados);
                this.mostrarNotificacao('Salvo offline', 'O tratamento será sincronizado quando a conexão voltar.', 'info');
                document.getElementById('formSanidade').reset();
            }

        } catch (error) {
            console.error('Erro ao salvar sanidade:', error);
            this.mostrarNotificacao('Erro', 'Não foi possível salvar o tratamento.', 'error');
        }
    }

    async salvarReprodutivo() {
        const tipo = document.querySelector('.procedure-type-btn.active')?.getAttribute('data-type') || 'iatf';
        const dados = {
            animal_id: this.animalAtual?.id,
            tipo: tipo,
            data_iatf: document.getElementById('iatfData')?.value,
            protocolo_id: document.getElementById('iatfProtocolo')?.value,
            touro_id: document.getElementById('iatfTouro')?.value,
            palheta: document.getElementById('iatfPalheta')?.value,
            inseminador_id: document.getElementById('iatfInseminador')?.value,
            data_diagnostico: document.getElementById('diagnosticoData')?.value,
            resultado: document.getElementById('diagnosticoResultado')?.value,
            metodo: document.getElementById('diagnosticoMetodo')?.value,
            responsavel: document.getElementById('diagnosticoResponsavel')?.value
        };

        try {
            if (this.isOnline) {
                const response = await fetch('/api/curral/reprodutivo/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(dados)
                });

                if (response.ok) {
                    this.mostrarNotificacao('Sucesso', 'Procedimento salvo com sucesso!', 'success');
                    document.getElementById('formReprodutivo').reset();
                    return;
                }
            }

            if (window.offlineDB) {
                await window.offlineDB.salvarReprodutivo(dados);
                this.mostrarNotificacao('Salvo offline', 'O procedimento será sincronizado quando a conexão voltar.', 'info');
                document.getElementById('formReprodutivo').reset();
            }

        } catch (error) {
            console.error('Erro ao salvar reprodutivo:', error);
            this.mostrarNotificacao('Erro', 'Não foi possível salvar o procedimento.', 'error');
        }
    }

    async salvarMovimentacao() {
        const dados = {
            animal_id: this.animalAtual?.id,
            tipo: document.getElementById('movimentacaoTipo').value,
            data: document.getElementById('movimentacaoData').value,
            lote_origem_id: document.getElementById('movimentacaoLoteOrigem').value,
            lote_destino_id: document.getElementById('movimentacaoLoteDestino').value,
            pasto_origem: document.getElementById('movimentacaoPastoOrigem').value,
            pasto_destino: document.getElementById('movimentacaoPastoDestino').value,
            motivo: document.getElementById('movimentacaoMotivo').value
        };

        try {
            if (this.isOnline) {
                const response = await fetch('/api/curral/movimentacao/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(dados)
                });

                if (response.ok) {
                    this.mostrarNotificacao('Sucesso', 'Movimentação salva com sucesso!', 'success');
                    document.getElementById('formMovimentacao').reset();
                    return;
                }
            }

            if (window.offlineDB) {
                await window.offlineDB.salvarMovimentacao(dados);
                this.mostrarNotificacao('Salvo offline', 'A movimentação será sincronizada quando a conexão voltar.', 'info');
                document.getElementById('formMovimentacao').reset();
            }

        } catch (error) {
            console.error('Erro ao salvar movimentação:', error);
            this.mostrarNotificacao('Erro', 'Não foi possível salvar a movimentação.', 'error');
        }
    }

    // ==================== VOZ ====================
    setupVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'pt-BR';

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.toLowerCase();
            const numeros = transcript.match(/\d+([.,]\d+)?/g);
            
            if (numeros && numeros.length > 0) {
                const peso = parseFloat(numeros[0].replace(',', '.'));
                if (!isNaN(peso) && peso > 0) {
                    this.atualizarPeso(peso);
                    this.mostrarNotificacao('Peso detectado', `${peso.toFixed(1)} kg`, 'success');
                }
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Erro no reconhecimento de voz:', event.error);
            this.mostrarNotificacao('Erro', 'Não foi possível reconhecer o peso por voz.', 'error');
        };
    }

    // ==================== CÂMERA ====================
    setupCameraScan() {
        const btnScanCamera = document.getElementById('btnScanCamera');
        if (btnScanCamera) {
            btnScanCamera.addEventListener('click', () => this.iniciarScanCamera());
        }
    }

    async iniciarScanCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'environment' } 
            });
            
            // TODO: Implementar leitura de código de barras
            this.mostrarNotificacao('Câmera ativada', 'Aponte para o código de barras do brinco.', 'info');
            
        } catch (error) {
            console.error('Erro ao acessar câmera:', error);
            this.mostrarNotificacao('Erro', 'Não foi possível acessar a câmera.', 'error');
        }
    }

    // ==================== OFFLINE/ONLINE ====================
    setupOfflineDetection() {
        this.atualizarStatusConexao();
    }

    handleOnline() {
        this.isOnline = true;
        this.atualizarStatusConexao();
        this.mostrarNotificacao('Online', 'Conexão restaurada. Sincronizando dados...', 'success');
        
        // Sincroniza automaticamente
        if (window.offlineSync) {
            window.offlineSync.forceSync();
        }
    }

    handleOffline() {
        this.isOnline = false;
        this.atualizarStatusConexao();
        this.mostrarNotificacao('Offline', 'Você está offline. Os dados serão salvos localmente.', 'info');
    }

    atualizarStatusConexao() {
        const statusIndicator = document.getElementById('statusIndicator');
        const statusIcon = document.getElementById('statusIcon');
        const statusText = document.getElementById('statusText');

        if (statusIndicator && statusIcon && statusText) {
            if (this.isOnline) {
                statusIndicator.classList.remove('offline');
                statusIcon.className = 'fas fa-wifi';
                statusText.textContent = 'Online';
            } else {
                statusIndicator.classList.add('offline');
                statusIcon.className = 'fas fa-wifi-slash';
                statusText.textContent = 'Offline';
            }
        }
    }

    async sincronizar() {
        const btnSync = document.getElementById('btnSync');
        if (btnSync) {
            btnSync.classList.add('syncing');
        }

        if (window.offlineSync) {
            await window.offlineSync.forceSync();
        }

        if (btnSync) {
            setTimeout(() => {
                btnSync.classList.remove('syncing');
            }, 1000);
        }
    }

    // ==================== UTILITÁRIOS ====================
    getCSRFToken() {
        const cookie = document.cookie.match(/csrftoken=([^;]+)/);
        return cookie ? cookie[1] : '';
    }

    mostrarNotificacao(title, message, type = 'info') {
        // Usa o sistema de notificações do offline-sync se disponível
        if (window.offlineSync) {
            window.offlineSync.showNotification(title, message, type);
        } else {
            // Fallback simples
            alert(`${title}: ${message}`);
        }
    }
    
    // ==================== MÉTRICAS EM TEMPO REAL ====================
    setupMetricas() {
        // Atualiza métricas a cada 30 segundos
        setInterval(() => this.carregarMetricas(), 30000);
    }
    
    async carregarMetricas() {
        try {
            if (this.isOnline) {
                const response = await fetch('/api/curral/metricas/');
                if (response.ok) {
                    const data = await response.json();
                    this.metricas = data;
                    this.atualizarMetricasUI();
                }
            }
        } catch (error) {
            console.error('Erro ao carregar métricas:', error);
        }
    }
    
    atualizarMetricasUI() {
        const animarValor = (elementId, valor, sufixo = '') => {
            const el = document.getElementById(elementId);
            if (!el) return;
            
            const valorAtual = parseFloat(el.textContent) || 0;
            const diff = valor - valorAtual;
            const steps = 20;
            let step = 0;
            
            const animacao = setInterval(() => {
                step++;
                const novoValor = valorAtual + (diff * (step / steps));
                el.textContent = sufixo ? `${novoValor.toFixed(1)}${sufixo}` : Math.round(novoValor);
                
                if (step >= steps) {
                    clearInterval(animacao);
                    el.textContent = sufixo ? `${valor.toFixed(1)}${sufixo}` : valor;
                }
            }, 30);
        };
        
        animarValor('metricAnimais', this.metricas.animais || 0);
        animarValor('metricPesagens', this.metricas.pesagens || 0);
        animarValor('metricTratamentos', this.metricas.tratamentos || 0);
        animarValor('metricGanhoMedio', this.metricas.ganhoMedio || 0, ' kg');
    }
    
    // ==================== SESSÃO ATIVA ====================
    setupSessaoAtiva() {
        const btnFechar = document.getElementById('btnFecharSessao');
        const btnVer = document.getElementById('btnVerSessao');
        const btnEncerrar = document.getElementById('btnEncerrarSessao');
        
        if (btnFechar) {
            btnFechar.addEventListener('click', () => {
                document.getElementById('sessaoAtivaCard').style.display = 'none';
            });
        }
        
        if (btnVer) {
            btnVer.addEventListener('click', () => {
                this.ativarTab('historico');
            });
        }
        
        if (btnEncerrar) {
            btnEncerrar.addEventListener('click', () => {
                this.encerrarSessao();
            });
        }
    }
    
    async carregarSessaoAtiva() {
        try {
            if (this.isOnline) {
                const response = await fetch('/api/curral/sessao/ativa/');
                if (response.ok) {
                    this.sessaoAtiva = await response.json();
                    this.atualizarSessaoUI();
                }
            }
        } catch (error) {
            console.error('Erro ao carregar sessão:', error);
        }
    }
    
    atualizarSessaoUI() {
        if (!this.sessaoAtiva) {
            document.getElementById('sessaoAtivaCard').style.display = 'none';
            return;
        }
        
        const card = document.getElementById('sessaoAtivaCard');
        if (card) card.style.display = 'block';
        
        const data = new Date(this.sessaoAtiva.data_inicio);
        document.getElementById('sessaoData').textContent = 
            data.toLocaleDateString('pt-BR') + ' ' + data.toLocaleTimeString('pt-BR');
        
        document.getElementById('sessaoEventos').textContent = this.sessaoAtiva.total_eventos || 0;
        document.getElementById('sessaoAnimais').textContent = this.sessaoAtiva.total_animais || 0;
        document.getElementById('sessaoPesagens').textContent = this.sessaoAtiva.total_pesagens || 0;
    }
    
    async encerrarSessao() {
        if (!confirm('Deseja encerrar a sessão atual?')) return;
        
        try {
            if (this.isOnline) {
                const response = await fetch(`/api/curral/sessao/${this.sessaoAtiva.id}/encerrar/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });
                
                if (response.ok) {
                    this.mostrarNotificacao('Sucesso', 'Sessão encerrada com sucesso!', 'success');
                    this.sessaoAtiva = null;
                    document.getElementById('sessaoAtivaCard').style.display = 'none';
                }
            }
        } catch (error) {
            console.error('Erro ao encerrar sessão:', error);
            this.mostrarNotificacao('Erro', 'Não foi possível encerrar a sessão.', 'error');
        }
    }
    
    // ==================== ALERTAS INTELIGENTES ====================
    setupAlertas() {
        // Verifica alertas a cada minuto
        setInterval(() => {
            if (this.animalAtual) {
                this.verificarAlertas(this.animalAtual);
            }
        }, 60000);
    }
    
    async verificarAlertas(animal) {
        try {
            if (this.isOnline && animal) {
                const response = await fetch(`/api/curral/animal/${animal.id}/alertas/`);
                if (response.ok) {
                    const alertas = await response.json();
                    this.exibirAlertas(alertas);
                }
            }
        } catch (error) {
            console.error('Erro ao verificar alertas:', error);
        }
    }
    
    exibirAlertas(alertas) {
        const container = document.getElementById('alertasContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        alertas.forEach(alerta => {
            const alertaCard = document.createElement('div');
            alertaCard.className = `alerta-card alerta-${alerta.tipo}`;
            alertaCard.innerHTML = `
                <div class="alerta-icon">
                    <i class="fas ${this.getAlertaIcon(alerta.tipo)}"></i>
                </div>
                <div class="alerta-content">
                    <div class="alerta-title">${alerta.titulo}</div>
                    <div class="alerta-message">${alerta.mensagem}</div>
                </div>
                <button class="alerta-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;
            container.appendChild(alertaCard);
        });
    }
    
    getAlertaIcon(tipo) {
        const icons = {
            warning: 'fa-exclamation-triangle',
            danger: 'fa-exclamation-circle',
            info: 'fa-info-circle',
            success: 'fa-check-circle'
        };
        return icons[tipo] || icons.info;
    }
    
    // ==================== AÇÕES RÁPIDAS ====================
    setupQuickActions() {
        const btnQuickPesagem = document.getElementById('btnQuickPesagem');
        const btnQuickSanidade = document.getElementById('btnQuickSanidade');
        const btnQuickHistorico = document.getElementById('btnQuickHistorico');
        
        if (btnQuickPesagem) {
            btnQuickPesagem.addEventListener('click', () => {
                this.ativarTab('pesagem');
            });
        }
        
        if (btnQuickSanidade) {
            btnQuickSanidade.addEventListener('click', () => {
                this.ativarTab('sanidade');
            });
        }
        
        if (btnQuickHistorico) {
            btnQuickHistorico.addEventListener('click', () => {
                this.ativarTab('historico');
            });
        }
    }
    
    // ==================== COMPARAÇÃO COM LOTE ====================
    async carregarComparacaoLote(animal) {
        try {
            if (this.isOnline && animal.lote_id) {
                const response = await fetch(`/api/curral/animal/${animal.id}/comparacao-lote/`);
                if (response.ok) {
                    const comparacao = await response.json();
                    this.exibirComparacao(comparacao);
                }
            }
        } catch (error) {
            console.error('Erro ao carregar comparação:', error);
        }
    }
    
    exibirComparacao(comparacao) {
        const comparisonDiv = document.getElementById('animalComparison');
        if (!comparisonDiv) return;
        
        comparisonDiv.style.display = 'block';
        
        // Peso vs Média
        const pesoPercent = (comparacao.peso_atual / comparacao.media_lote) * 100;
        const comparisonPeso = document.getElementById('comparisonPeso');
        const comparisonPesoValue = document.getElementById('comparisonPesoValue');
        
        if (comparisonPeso) {
            comparisonPeso.style.width = `${Math.min(pesoPercent, 100)}%`;
        }
        
        if (comparisonPesoValue) {
            const diff = comparacao.peso_atual - comparacao.media_lote;
            comparisonPesoValue.textContent = `${diff > 0 ? '+' : ''}${diff.toFixed(1)} kg`;
        }
        
        // Ganho vs Média
        const ganhoPercent = (comparacao.ganho_diario / comparacao.ganho_medio_lote) * 100;
        const comparisonGanho = document.getElementById('comparisonGanho');
        const comparisonGanhoValue = document.getElementById('comparisonGanhoValue');
        
        if (comparisonGanho) {
            comparisonGanho.style.width = `${Math.min(ganhoPercent, 100)}%`;
        }
        
        if (comparisonGanhoValue) {
            const diff = comparacao.ganho_diario - comparacao.ganho_medio_lote;
            comparisonGanhoValue.textContent = `${diff > 0 ? '+' : ''}${diff.toFixed(2)} kg/dia`;
        }
    }
    
    // ==================== HISTÓRICO VISUAL ====================
    setupHistorico() {
        const periodoSelect = document.getElementById('historicoPeriodo');
        if (periodoSelect) {
            periodoSelect.addEventListener('change', () => {
                if (this.animalAtual) {
                    this.carregarHistoricoPeso(this.animalAtual);
                }
            });
        }
    }
    
    async carregarHistoricoPeso(animal) {
        try {
            if (this.isOnline && animal.id) {
                const periodo = document.getElementById('historicoPeriodo')?.value || '30';
                const response = await fetch(`/api/curral/animal/${animal.id}/historico-peso/?periodo=${periodo}`);
                if (response.ok) {
                    const historico = await response.json();
                    this.criarGraficoPeso(historico);
                    this.criarGraficoGanho(historico);
                    this.criarTimeline(historico);
                }
            }
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
        }
    }
    
    criarGraficoPeso(historico) {
        const ctx = document.getElementById('pesoChart');
        if (!ctx) return;
        
        if (this.charts.peso) {
            this.charts.peso.destroy();
        }
        
        this.charts.peso = new Chart(ctx, {
            type: 'line',
            data: {
                labels: historico.datas || [],
                datasets: [{
                    label: 'Peso (kg)',
                    data: historico.pesos || [],
                    borderColor: '#2e7d32',
                    backgroundColor: 'rgba(46, 125, 50, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: false }
                }
            }
        });
    }
    
    criarGraficoGanho(historico) {
        const ctx = document.getElementById('historicoGanhoChart');
        if (!ctx) return;
        
        if (this.charts.ganho) {
            this.charts.ganho.destroy();
        }
        
        this.charts.ganho = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: historico.datas || [],
                datasets: [{
                    label: 'Ganho Diário (kg)',
                    data: historico.ganhos_diarios || [],
                    backgroundColor: '#4caf50'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
    
    criarTimeline(historico) {
        const timeline = document.getElementById('historicoTimeline');
        if (!timeline) return;
        
        timeline.innerHTML = '';
        
        historico.eventos?.forEach(evento => {
            const item = document.createElement('div');
            item.className = 'timeline-item';
            item.innerHTML = `
                <div class="timeline-icon">
                    <i class="fas ${this.getEventoIcon(evento.tipo)}"></i>
                </div>
                <div class="timeline-content">
                    <div class="timeline-title">${evento.titulo}</div>
                    <div class="timeline-date">${new Date(evento.data).toLocaleDateString('pt-BR')}</div>
                </div>
                <div class="timeline-value">${evento.valor || ''}</div>
            `;
            timeline.appendChild(item);
        });
    }
    
    getEventoIcon(tipo) {
        const icons = {
            pesagem: 'fa-weight',
            vacina: 'fa-syringe',
            tratamento: 'fa-pills',
            iatf: 'fa-baby-carriage',
            parto: 'fa-baby'
        };
        return icons[tipo] || 'fa-circle';
    }
    
    // ==================== INDICADORES DE PESAGEM ====================
    atualizarIndicadoresPesagem(peso, animal) {
        if (!animal) return;
        
        // Tendência
        const tendenciaEl = document.getElementById('indicadorTendencia');
        if (tendenciaEl && animal.ultimo_peso) {
            const tendencia = peso > animal.ultimo_peso ? '↗ Crescendo' : 
                            peso < animal.ultimo_peso ? '↘ Diminuindo' : '→ Estável';
            tendenciaEl.textContent = tendencia;
        }
        
        // Meta do Lote
        const metaEl = document.getElementById('indicadorMeta');
        if (metaEl && animal.meta_peso) {
            const percentual = (peso / animal.meta_peso) * 100;
            metaEl.textContent = `${percentual.toFixed(0)}%`;
        }
        
        // Performance
        const performanceEl = document.getElementById('indicadorPerformance');
        if (performanceEl && animal.ganho_medio_esperado) {
            const ganhoDiario = (peso - animal.ultimo_peso) / 30; // Simplificado
            const performance = (ganhoDiario / animal.ganho_medio_esperado) * 100;
            let classificacao = 'Excelente';
            if (performance < 80) classificacao = 'Boa';
            if (performance < 60) classificacao = 'Regular';
            if (performance < 40) classificacao = 'Baixa';
            performanceEl.textContent = classificacao;
        }
    }
}

// Inicializa quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.curralTelaUnica = new CurralTelaUnica();
    });
} else {
    window.curralTelaUnica = new CurralTelaUnica();
}

