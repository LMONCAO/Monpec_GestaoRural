/**
 * PWA Install Prompt
 * MONPEC Curral Inteligente
 * Gerencia a instalação do app como PWA
 */

class PWAInstallManager {
    constructor() {
        this.deferredPrompt = null;
        this.isInstalled = this.checkIfInstalled();
        this.init();
    }

    init() {
        // Detecta se já está instalado
        if (this.isInstalled) {
            this.hideInstallPrompt();
            return;
        }

        // Escuta o evento beforeinstallprompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallPrompt();
        });

        // Detecta se foi instalado
        window.addEventListener('appinstalled', () => {
            console.log('PWA instalado com sucesso!');
            this.isInstalled = true;
            this.hideInstallPrompt();
            this.showInstallSuccess();
        });

        // Verifica se está em modo standalone (já instalado)
        if (window.matchMedia('(display-mode: standalone)').matches) {
            this.isInstalled = true;
            this.hideInstallPrompt();
        }

        // Mostra instruções de instalação manual se necessário
        this.checkManualInstall();
    }

    checkIfInstalled() {
        // Verifica se está rodando como PWA instalado
        if (window.matchMedia('(display-mode: standalone)').matches) {
            return true;
        }

        // Verifica se está em modo fullscreen (iOS)
        if (window.navigator.standalone === true) {
            return true;
        }

        // Verifica localStorage
        if (localStorage.getItem('pwa_installed') === 'true') {
            return true;
        }

        return false;
    }

    showInstallPrompt() {
        // Remove prompt anterior se existir
        const existing = document.getElementById('pwaInstallPrompt');
        if (existing) {
            existing.remove();
        }

        // Cria o prompt
        const prompt = document.createElement('div');
        prompt.id = 'pwaInstallPrompt';
        prompt.className = 'pwa-install-prompt';
        prompt.innerHTML = `
            <div class="pwa-install-content">
                <div class="pwa-install-icon">
                    <i class="fas fa-mobile-alt"></i>
                </div>
                <div class="pwa-install-text">
                    <div class="pwa-install-title">Instalar MONPEC Curral</div>
                    <div class="pwa-install-message">Instale o app para acesso rápido e uso offline</div>
                </div>
                <div class="pwa-install-actions">
                    <button class="pwa-install-btn" id="pwaInstallBtn">
                        <i class="fas fa-download"></i> Instalar
                    </button>
                    <button class="pwa-install-close" id="pwaInstallClose">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(prompt);

        // Event listeners
        const installBtn = document.getElementById('pwaInstallBtn');
        const closeBtn = document.getElementById('pwaInstallClose');

        if (installBtn) {
            installBtn.addEventListener('click', () => this.installApp());
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hideInstallPrompt());
        }

        // Atualiza botão no header
        this.updateHeaderButton();

        // Auto-hide após 10 segundos
        setTimeout(() => {
            if (prompt.parentElement) {
                this.hideInstallPrompt();
            }
        }, 10000);
    }

    async installApp() {
        if (!this.deferredPrompt) {
            // Se não há prompt nativo, mostra instruções manuais
            this.showManualInstallInstructions();
            return;
        }

        // Mostra o prompt de instalação nativo
        this.deferredPrompt.prompt();

        // Aguarda a resposta do usuário
        const { outcome } = await this.deferredPrompt.userChoice;

        if (outcome === 'accepted') {
            console.log('Usuário aceitou instalar o PWA');
            localStorage.setItem('pwa_installed', 'true');
        } else {
            console.log('Usuário recusou instalar o PWA');
        }

        // Limpa o prompt
        this.deferredPrompt = null;
        this.hideInstallPrompt();
    }

    hideInstallPrompt() {
        const prompt = document.getElementById('pwaInstallPrompt');
        if (prompt) {
            prompt.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => {
                if (prompt.parentElement) {
                    prompt.remove();
                }
            }, 300);
        }
    }

    showInstallSuccess() {
        const notification = document.createElement('div');
        notification.className = 'pwa-install-success';
        notification.innerHTML = `
            <div class="pwa-install-success-content">
                <i class="fas fa-check-circle"></i>
                <span>App instalado com sucesso!</span>
            </div>
        `;

        document.body.appendChild(notification);

        // Atualiza botão no header
        this.updateHeaderButton();

        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }

    updateHeaderButton() {
        const btnInstall = document.getElementById('btnInstallApp');
        if (btnInstall) {
            if (this.isInstalled) {
                btnInstall.style.display = 'none';
            } else if (this.deferredPrompt) {
                btnInstall.style.display = 'flex';
                btnInstall.addEventListener('click', () => this.installApp());
            } else {
                btnInstall.style.display = 'flex';
                btnInstall.addEventListener('click', () => this.showManualInstallInstructions());
            }
        }
    }

    checkManualInstall() {
        // Detecta o navegador e sistema operacional
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        const isAndroid = /Android/.test(navigator.userAgent);
        const isChrome = /Chrome/.test(navigator.userAgent);
        const isSafari = /Safari/.test(navigator.userAgent) && !isChrome;
        const isEdge = /Edge/.test(navigator.userAgent);
        const isFirefox = /Firefox/.test(navigator.userAgent);

        // Se não há prompt nativo e não está instalado, mostra instruções
        if (!this.deferredPrompt && !this.isInstalled) {
            // Aguarda um pouco antes de mostrar (para não ser intrusivo)
            setTimeout(() => {
                if (!this.deferredPrompt && !this.isInstalled) {
                    this.showManualInstallInstructions(isIOS, isAndroid, isChrome, isSafari);
                }
            }, 5000);
        }
    }

    showManualInstallInstructions(isIOS, isAndroid, isChrome, isSafari) {
        // Remove instruções anteriores
        const existing = document.getElementById('pwaManualInstall');
        if (existing) {
            existing.remove();
        }

        let instructions = '';

        if (isIOS && isSafari) {
            instructions = `
                <div class="manual-install-steps">
                    <h3><i class="fab fa-apple"></i> Instalar no iOS</h3>
                    <ol>
                        <li>Toque no botão <strong>Compartilhar</strong> <i class="fas fa-share"></i> na parte inferior</li>
                        <li>Role para baixo e toque em <strong>"Adicionar à Tela de Início"</strong></li>
                        <li>Toque em <strong>"Adicionar"</strong> no canto superior direito</li>
                    </ol>
                </div>
            `;
        } else if (isAndroid && isChrome) {
            instructions = `
                <div class="manual-install-steps">
                    <h3><i class="fab fa-android"></i> Instalar no Android</h3>
                    <ol>
                        <li>Toque no menu <i class="fas fa-ellipsis-vertical"></i> no canto superior direito</li>
                        <li>Selecione <strong>"Adicionar à tela inicial"</strong> ou <strong>"Instalar app"</strong></li>
                        <li>Toque em <strong>"Instalar"</strong> ou <strong>"Adicionar"</strong></li>
                    </ol>
                </div>
            `;
        } else if (isChrome || isEdge) {
            instructions = `
                <div class="manual-install-steps">
                    <h3><i class="fab fa-chrome"></i> Instalar no Navegador</h3>
                    <ol>
                        <li>Procure pelo ícone de instalação <i class="fas fa-plus-square"></i> na barra de endereços</li>
                        <li>Ou use o menu do navegador → <strong>"Instalar MONPEC Curral"</strong></li>
                        <li>Clique em <strong>"Instalar"</strong> quando o prompt aparecer</li>
                    </ol>
                </div>
            `;
        } else {
            instructions = `
                <div class="manual-install-steps">
                    <h3>Instalar o App</h3>
                    <p>Procure pela opção de instalação no menu do seu navegador ou siga as instruções específicas do seu dispositivo.</p>
                </div>
            `;
        }

        const manualInstall = document.createElement('div');
        manualInstall.id = 'pwaManualInstall';
        manualInstall.className = 'pwa-manual-install';
        manualInstall.innerHTML = `
            <div class="manual-install-header">
                <h3><i class="fas fa-info-circle"></i> Como Instalar</h3>
                <button class="manual-install-close" id="manualInstallClose">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="manual-install-body">
                ${instructions}
                <div class="manual-install-benefits">
                    <h4>Benefícios de instalar:</h4>
                    <ul>
                        <li><i class="fas fa-check"></i> Acesso rápido direto da tela inicial</li>
                        <li><i class="fas fa-check"></i> Funciona offline</li>
                        <li><i class="fas fa-check"></i> Experiência como app nativo</li>
                        <li><i class="fas fa-check"></i> Notificações e atualizações automáticas</li>
                    </ul>
                </div>
            </div>
        `;

        document.body.appendChild(manualInstall);

        // Fecha ao clicar no X
        const closeBtn = document.getElementById('manualInstallClose');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                if (manualInstall.parentElement) {
                    manualInstall.remove();
                }
            });
        }

        // Fecha ao clicar fora
        manualInstall.addEventListener('click', (e) => {
            if (e.target === manualInstall) {
                manualInstall.remove();
            }
        });
    }
}

// Inicializa quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.pwaInstallManager = new PWAInstallManager();
    });
} else {
    window.pwaInstallManager = new PWAInstallManager();
}

