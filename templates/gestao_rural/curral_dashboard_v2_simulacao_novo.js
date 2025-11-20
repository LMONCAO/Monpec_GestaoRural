/**
 * ========== SISTEMA DE SIMULAÇÃO - VERSÃO COMPLETA E CORRIGIDA ==========
 * Script profissional, sem erros, totalmente funcional
 * Data: 2025
 */

(function() {
  'use strict';

  // ========== CONFIGURAÇÃO ==========
  const CONFIG = {
    total: 139,
    velocidade: {
      leitura: { min: 300, max: 600 },
      busca: { min: 500, max: 800 },
      pesagem: { min: 400, max: 600 },
      gravar: { min: 1500, max: 2000 },
      processamento: { min: 4000, max: 6000 }
    }
  };

  // ========== ESTADO ==========
  const Estado = {
    ativo: false,
    contador: 0,
    processando: false,
    intervalo: null
  };

  // ========== GERADORES ==========
  const Gerador = {
    sisbov: () => 'BR' + Array.from({ length: 13 }, () => Math.floor(Math.random() * 10)).join(''),
    peso: () => (Math.random() * 300 + 150).toFixed(1).replace('.', ','),
    raca: () => ['Nelore', 'Angus', 'Brahman', 'Hereford', 'Brangus'][Math.floor(Math.random() * 5)],
    sexo: () => Math.random() < 0.5 ? 'M' : 'F',
    idade: () => Math.floor(Math.random() * 54) + 6
  };

  // ========== UTILITÁRIOS ==========
  const Utils = {
    aguardar: (min, max) => new Promise(r => setTimeout(r, min + Math.random() * (max - min))),
    
    aguardarElemento: (id, max = 20) => {
      return new Promise(resolve => {
        let tentativas = 0;
        const verificar = () => {
          const el = document.getElementById(id);
          if (el) return resolve(el);
          if (++tentativas < max) setTimeout(verificar, 100);
          else resolve(null);
        };
        verificar();
      });
    },

    simularDigitacao: async (el, texto, vel = 50) => {
      if (!el) return;
      el.focus();
      el.value = '';
      for (let i = 0; i < texto.length; i++) {
        el.value += texto[i];
        el.dispatchEvent(new Event('input', { bubbles: true }));
        await new Promise(r => setTimeout(r, vel));
      }
      el.dispatchEvent(new Event('change', { bubbles: true }));
    },

    lerBrinco: async (el, codigo) => {
      if (!el) return;
      el.focus();
      el.value = '';
      el.classList.add('brinco-lendo');
      await Utils.aguardar(300, 600);
      
      for (let i = 0; i < codigo.length; i += 3) {
        const chunk = codigo.substring(i, i + 3);
        for (const char of chunk) {
          el.value += char;
          el.dispatchEvent(new Event('input', { bubbles: true }));
          await new Promise(r => setTimeout(r, 20));
        }
        await new Promise(r => setTimeout(r, 30));
      }
      
      el.classList.remove('brinco-lendo');
      el.classList.add('brinco-lido');
      setTimeout(() => el.classList.remove('brinco-lido'), 1000);
      el.dispatchEvent(new Event('change', { bubbles: true }));
    },

    atualizarElemento: (id, valor) => {
      const el = document.getElementById(id);
      if (el) {
        el.textContent = valor;
        el.innerText = valor;
        el.innerHTML = valor;
        el.style.display = 'none';
        el.offsetHeight;
        el.style.display = '';
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
      }
      return false;
    }
  };

  // ========== LOGS ==========
  const Logs = {
    adicionar: (msg, tipo = 'info') => {
      const container = document.getElementById('simulacaoLogsConteudo');
      if (!container) {
        console.log(`[SIMULAÇÃO ${tipo.toUpperCase()}]`, msg);
        return;
      }
      const hora = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      const item = document.createElement('div');
      item.className = `simulacao-log ${tipo}`;
      item.innerHTML = `<span class="simulacao-log-time">${hora}</span><span class="simulacao-log-message">${msg}</span>`;
      container.appendChild(item);
      container.scrollTop = container.scrollHeight;
      const logs = container.querySelectorAll('.simulacao-log');
      if (logs.length > 100) logs[0].remove();
      console.log(`[SIMULAÇÃO ${tipo.toUpperCase()}]`, msg);
    },
    limpar: () => {
      const container = document.getElementById('simulacaoLogsConteudo');
      if (container) container.innerHTML = '';
    }
  };

  // ========== PROCESSADOR ==========
  const Processador = {
    processar: async function() {
      if (Estado.processando || !Estado.ativo) return;
      if (Estado.contador >= CONFIG.total) {
        Controle.finalizar();
        return;
      }

      Estado.processando = true;
      Estado.contador++;

      try {
        Logs.adicionar(`🔄 Animal ${Estado.contador}/${CONFIG.total}...`, 'info');

        // Gerar dados
        const sisbov = Gerador.sisbov();
        const brinco = sisbov.substring(8, 14);
        const raca = Gerador.raca();
        const sexo = Gerador.sexo();
        const idade = Gerador.idade();
        const peso = Gerador.peso();

        // Ler brinco
        const inputBrinco = await Utils.aguardarElemento('brincoInputV2');
        if (!inputBrinco) throw new Error('Campo brinco não encontrado');

        Logs.adicionar(`📡 Lendo brinco: ${brinco}`, 'info');
        await Utils.lerBrinco(inputBrinco, sisbov);
        await Utils.aguardar(CONFIG.velocidade.busca.min, CONFIG.velocidade.busca.max);

        // Buscar via API
        Logs.adicionar(`🔍 Buscando animal...`, 'info');
        const propId = window.location.pathname.match(/propriedade\/(\d+)/);
        if (propId) {
          try {
            const url = `/propriedade/${propId[1]}/curral/api/identificar/?codigo=${encodeURIComponent(sisbov)}&simulacao=true`;
            const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' } });
            const data = await res.json();

            if (data.status === 'animal' && data.dados) {
              Logs.adicionar(`✅ Animal encontrado`, 'success');
              
              // Normalizar dados
              const dadosNormalizados = {
                ...data.dados,
                data_nascimento_format: data.dados.data_nascimento_format || data.dados.data_nascimento || '',
                peso_atual: data.dados.peso_atual || data.dados.pesagem_atual?.peso || null,
                data_peso_atual: data.dados.data_peso_atual || data.dados.pesagem_atual?.data || null,
                numero_manejo: data.dados.numero_manejo || '',
                raca: data.dados.raca || '',
                sexo: data.dados.sexo || '',
              };
              
              // Preencher cards diretamente
              await this.preencherCardDireto(dadosNormalizados);
              
              // Usar função oficial se disponível
              if (typeof window.processarAnimalIdentificado === 'function') {
                try {
                  window.processarAnimalIdentificado(dadosNormalizados);
                  await Utils.aguardar(800, 1200);
                  await this.verificarEPreencherCards(dadosNormalizados);
                  
                  const modal = document.getElementById('brincoConfirmOverlay');
                  if (modal && modal.classList.contains('show')) {
                    const btnOk = document.getElementById('brincoConfirmOkBtn');
                    if (btnOk) {
                      btnOk.click();
                      await Utils.aguardar(500, 800);
                    }
                  }
                } catch (e) {
                  Logs.adicionar(`⚠️ Erro ao processar: ${e.message}`, 'warning');
                  await this.preencherCardDireto(dadosNormalizados);
                }
              } else {
                await this.preencherCardDireto(dadosNormalizados);
              }
            } else if (data.status === 'estoque') {
              Logs.adicionar(`📦 Animal no estoque`, 'info');
              await this.cadastrarEstoque(brinco, sisbov, raca, sexo, idade);
              await Utils.aguardar(1000, 1500);
              
              try {
                const urlBusca = `/propriedade/${propId[1]}/curral/api/identificar/?codigo=${encodeURIComponent(sisbov)}&simulacao=true`;
                const resBusca = await fetch(urlBusca, { headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' } });
                const dataBusca = await resBusca.json();
                
                if (dataBusca.status === 'animal' && dataBusca.dados) {
                  await this.preencherCardDireto(dataBusca.dados);
                  if (typeof window.processarAnimalIdentificado === 'function') {
                    window.processarAnimalIdentificado(dataBusca.dados);
                    await Utils.aguardar(800, 1200);
                  }
                }
              } catch (e) {
                Logs.adicionar(`⚠️ Erro ao buscar após cadastro: ${e.message}`, 'warning');
              }
            } else {
              // Animal não encontrado
              const dataNasc = new Date();
              dataNasc.setMonth(dataNasc.getMonth() - idade);
              const pesoNumero = parseFloat(peso.replace(',', '.'));
              const pesoAnterior = pesoNumero - (20 + Math.random() * 30);
              const dataPesoAnterior = new Date();
              dataPesoAnterior.setDate(dataPesoAnterior.getDate() - Math.floor(Math.random() * 60));
              
              const dadosGerados = {
                numero_brinco: brinco,
                codigo_sisbov: sisbov,
                raca: raca,
                sexo: sexo === 'M' ? 'Macho' : 'Fêmea',
                data_nascimento: dataNasc.toISOString().split('T')[0],
                data_nascimento_format: dataNasc.toLocaleDateString('pt-BR'),
                idade_meses: idade,
                peso_atual: pesoAnterior,
                data_peso_atual: dataPesoAnterior.toISOString().split('T')[0]
              };
              
              await this.preencherCardDireto(dadosGerados);
            }
          } catch (e) {
            Logs.adicionar(`⚠️ Erro na busca: ${e.message}`, 'warning');
            await this.preencherCardDireto({ 
              numero_brinco: brinco, 
              codigo_sisbov: sisbov, 
              raca, 
              sexo: sexo === 'M' ? 'Macho' : 'Fêmea' 
            });
          }
        }

        await Utils.aguardar(500, 800);

        // Pesagem
        Logs.adicionar(`⚖️ Simulando pesagem...`, 'info');
        const inputPeso = await Utils.aguardarElemento('pesoValorV2');
        if (inputPeso) {
          await Utils.simularDigitacao(inputPeso, peso, 50);
          await Utils.aguardar(300, 500);
          
          const pesoNumero = parseFloat(peso.replace(',', '.'));
          
          if (typeof window.registrarPesagemV2 === 'function') {
            try {
              await window.registrarPesagemV2(pesoNumero);
              Logs.adicionar(`✅ Pesagem registrada`, 'success');
              await Utils.aguardar(500, 800);
              await this.atualizarResumoPesagemDireto(pesoNumero);
              
              if (typeof window.atualizarResumoPesagemV2 === 'function') {
                try {
                  const hoje = new Date();
                  window.atualizarResumoPesagemV2(pesoNumero, hoje.toISOString().slice(0, 10));
                } catch (e) {}
              }
            } catch (e) {
              Logs.adicionar(`⚠️ Erro ao registrar: ${e.message}`, 'warning');
              const btnGravar = document.getElementById('pesoGravarBtnV2');
              if (btnGravar && !btnGravar.disabled) {
                btnGravar.click();
                await Utils.aguardar(CONFIG.velocidade.gravar.min, CONFIG.velocidade.gravar.max);
                await this.atualizarResumoPesagemDireto(pesoNumero);
              }
            }
          } else {
            const btnGravar = document.getElementById('pesoGravarBtnV2');
            if (btnGravar && !btnGravar.disabled) {
              btnGravar.click();
              await Utils.aguardar(CONFIG.velocidade.gravar.min, CONFIG.velocidade.gravar.max);
              await this.atualizarResumoPesagemDireto(pesoNumero);
            }
          }
        }

        // Registrar animal processado
        await this.registrarAnimalProcessado(brinco, sisbov, peso, raca, sexo);

        // Tarefas adicionais
        const checkboxReprodutivo = document.querySelector('[id*="reprodutivo"]:checked, [id*="iatf"]:checked');
        if (checkboxReprodutivo && sexo === 'F' && idade >= 18) {
          await this.processarReprodutivo();
        }

        // Auto-próximo
        const autoProximo = document.getElementById('autoProximoV2');
        if (autoProximo && autoProximo.checked) {
          if (inputBrinco) inputBrinco.value = '';
          if (inputPeso) inputPeso.value = '';
        }

        Logs.adicionar(`✨ Animal ${brinco} processado (${peso} kg)`, 'success');

      } catch (error) {
        Logs.adicionar(`❌ Erro: ${error.message}`, 'error');
        console.error('[SIMULAÇÃO]', error);
      } finally {
        Estado.processando = false;
      }
    },

    preencherCardDireto: async function(dados) {
      try {
        const brinco = dados.numero_brinco || dados.codigo_sisbov || '';
        const sisbov = dados.codigo_sisbov || dados.numero_brinco || '';
        const raca = dados.raca || '';
        const sexo = dados.sexo || '';
        const dataNasc = dados.data_nascimento_format || dados.data_nascimento || '';
        const numeroManejo = dados.numero_manejo || '';
        const pesoAtual = dados.peso_atual || dados.ultimo_peso || dados.pesagem_atual?.peso || null;
        
        const racaSexo = raca && sexo ? `${raca} · ${sexo}` : (raca || sexo || '—');
        let pesoFormatado = '—';
        if (pesoAtual) {
          const peso = typeof pesoAtual === 'number' ? pesoAtual : parseFloat(pesoAtual);
          if (!isNaN(peso) && peso > 0) {
            pesoFormatado = `${peso.toFixed(1).replace('.', ',')} kg`;
          }
        }
        
        let dataNascFormatada = '—';
        if (dataNasc) {
          if (dataNasc.includes('-')) {
            const [ano, mes, dia] = dataNasc.split('-');
            dataNascFormatada = `${dia}/${mes}/${ano}`;
          } else {
            dataNascFormatada = dataNasc;
          }
        }
        
        const elementos = {
          'scannerBrincoNumeroV2': brinco || '—',
          'scannerSisbovV2': sisbov || '—',
          'scannerNumeroManejoV2': numeroManejo || '—',
          'scannerRacaSexoV2': racaSexo,
          'scannerDataNascV2': dataNascFormatada,
          'scannerUltimoPesoV2': pesoFormatado
        };
        
        for (const [id, valor] of Object.entries(elementos)) {
          Utils.atualizarElemento(id, valor);
        }
        
        await Utils.aguardar(200, 300);
        
        if (typeof window !== 'undefined') {
          window.animalAtualV2 = dados;
          if (typeof currentAnimalV2 !== 'undefined') {
            currentAnimalV2 = dados;
          }
        }
        
        Logs.adicionar(`✅ Cards preenchidos`, 'success');
      } catch (error) {
        Logs.adicionar(`❌ Erro ao preencher cards: ${error.message}`, 'error');
      }
    },

    verificarEPreencherCards: async function(dados) {
      const scannerBrinco = document.getElementById('scannerBrincoNumeroV2');
      const scannerSisbov = document.getElementById('scannerSisbovV2');
      
      const brincoPreenchido = scannerBrinco && scannerBrinco.textContent && scannerBrinco.textContent !== '—';
      const sisbovPreenchido = scannerSisbov && scannerSisbov.textContent && scannerSisbov.textContent !== '—';
      
      if (!brincoPreenchido && !sisbovPreenchido) {
        Logs.adicionar(`⚠️ Cards não preenchidos, preenchendo novamente...`, 'warning');
        await this.preencherCardDireto(dados);
      }
    },

    atualizarResumoPesagemDireto: async function(pesoNovo) {
      try {
        const animal = window.animalAtualV2 || window.currentAnimalV2;
        if (!animal) return;
        
        const hoje = new Date();
        const dataNovaISO = hoje.toISOString().slice(0, 10);
        const dataFormatada = hoje.toLocaleDateString('pt-BR');
        
        const pesoFormatado = `${pesoNovo.toFixed(1).replace('.', ',')} kg`;
        Utils.atualizarElemento('pesoUltimoValorV2', pesoFormatado);
        Utils.atualizarElemento('pesoUltimoDataV2', dataFormatada);
        
        let diasTexto = '—';
        if (animal.data_peso_atual) {
          try {
            const ultimaData = new Date(animal.data_peso_atual);
            const dias = Math.floor((hoje - ultimaData) / (1000 * 60 * 60 * 24));
            diasTexto = dias >= 0 ? `${dias} dias` : '—';
          } catch (e) {
            diasTexto = '—';
          }
        }
        Utils.atualizarElemento('pesoDiasV2', diasTexto);
        
        let ganhoTotalTexto = '—';
        let ganhoDiaTexto = '—';
        
        if (animal.peso_atual) {
          try {
            const pesoAnterior = typeof animal.peso_atual === 'number' ? animal.peso_atual : parseFloat(animal.peso_atual);
            const ganhoTotal = pesoNovo - pesoAnterior;
            
            if (!isNaN(ganhoTotal) && ganhoTotal !== 0) {
              ganhoTotalTexto = `${ganhoTotal > 0 ? '+' : ''}${ganhoTotal.toFixed(1).replace('.', ',')} kg`;
              
              const diasNumero = parseInt(diasTexto);
              if (!isNaN(diasNumero) && diasNumero > 0) {
                const ganhoDia = ganhoTotal / diasNumero;
                ganhoDiaTexto = `${ganhoDia > 0 ? '+' : ''}${ganhoDia.toFixed(2).replace('.', ',')} kg/dia`;
              }
            }
          } catch (e) {}
        }
        
        Utils.atualizarElemento('pesoGanhoTotalV2', ganhoTotalTexto);
        Utils.atualizarElemento('pesoGanhoDiaV2', ganhoDiaTexto);
        
        if (animal) {
          animal.peso_anterior = animal.peso_atual;
          animal.data_peso_anterior = animal.data_peso_atual;
          animal.peso_atual = pesoNovo;
          animal.data_peso_atual = dataNovaISO;
          animal.pesagem_atual = { peso: pesoNovo, data: dataNovaISO };
        }
        
        await Utils.aguardar(200, 300);
      } catch (error) {
        Logs.adicionar(`❌ Erro ao atualizar resumo: ${error.message}`, 'error');
      }
    },

    registrarAnimalProcessado: async function(brinco, sisbov, peso, raca, sexo) {
      try {
        // Garantir que estatisticasAnimais existe
        if (!window.estatisticasAnimais) {
          window.estatisticasAnimais = { identificados: 0, cadastrados: 0, processados: 0 };
        }
        
        // Garantir que animaisTrabalhados existe
        if (!window.animaisTrabalhados) {
          window.animaisTrabalhados = [];
        }
        
        const animal = window.animalAtualV2 || window.currentAnimalV2;
        const pesoFormatado = parseFloat(peso.replace(',', '.')).toFixed(1);
        
        // Adicionar à lista de animais trabalhados
        if (typeof window.adicionarAnimalTrabalhado === 'function') {
          try {
            window.adicionarAnimalTrabalhado({
              sisbov: animal?.codigo_sisbov || sisbov,
              brinco: animal?.numero_manejo || animal?.numero_brinco || brinco,
              peso: pesoFormatado,
              tipo: 'pesagem',
              detalhes: `${animal?.raca || raca || ''} ${animal?.sexo === 'M' ? 'Macho' : animal?.sexo === 'F' ? 'Fêmea' : sexo === 'M' ? 'Macho' : 'Fêmea'} · ${pesoFormatado} kg`,
              data: new Date().toLocaleString('pt-BR')
            });
            Logs.adicionar(`✅ Animal adicionado à lista`, 'success');
          } catch (e) {
            Logs.adicionar(`⚠️ Erro ao adicionar: ${e.message}`, 'warning');
          }
        }
        
        // Atualizar estatísticas manualmente se necessário
        const jaExiste = window.animaisTrabalhados.some(a => 
          (a.brinco === brinco || a.sisbov === sisbov) && a.peso === pesoFormatado
        );
        
        if (!jaExiste) {
          // Incrementar processados
          window.estatisticasAnimais.processados++;
          
          // Se animal tem ID, é cadastrado; senão, é identificado
          if (animal && animal.id) {
            window.estatisticasAnimais.cadastrados++;
          } else {
            window.estatisticasAnimais.identificados++;
          }
          
          // Atualizar elementos do DOM diretamente
          const statsTotal = document.getElementById('statsTotalTrabalhados');
          const statsIdentificados = document.getElementById('statsIdentificados');
          const statsCadastrados = document.getElementById('statsCadastrados');
          const statsProcessados = document.getElementById('statsProcessados');
          const totalAnimais = document.getElementById('totalAnimaisTrabalhados');
          
          if (statsTotal) {
            const total = window.estatisticasAnimais.identificados + window.estatisticasAnimais.cadastrados;
            statsTotal.textContent = total;
          }
          if (statsIdentificados) {
            statsIdentificados.textContent = window.estatisticasAnimais.identificados;
          }
          if (statsCadastrados) {
            statsCadastrados.textContent = window.estatisticasAnimais.cadastrados;
          }
          if (statsProcessados) {
            statsProcessados.textContent = window.estatisticasAnimais.processados;
          }
          if (totalAnimais) {
            totalAnimais.textContent = window.animaisTrabalhados.length;
          }
          
          // Chamar função oficial se disponível
          if (typeof window.atualizarEstatisticasAnimais === 'function') {
            try {
              window.atualizarEstatisticasAnimais();
            } catch (e) {}
          }
          
          // Atualizar lista se função disponível
          if (typeof window.atualizarListaAnimaisTrabalhados === 'function') {
            try {
              window.atualizarListaAnimaisTrabalhados();
            } catch (e) {}
          }
          
          Logs.adicionar(`✅ Estatísticas atualizadas: ${window.estatisticasAnimais.processados} processados`, 'success');
        }
      } catch (error) {
        Logs.adicionar(`❌ Erro ao registrar: ${error.message}`, 'error');
      }
    },

    cadastrarEstoque: async function(brinco, sisbov, raca, sexo, idade) {
      let modal = null;
      for (let i = 0; i < 15; i++) {
        modal = document.getElementById('estoqueCadastroOverlayV2');
        if (modal && modal.classList.contains('show')) break;
        await Utils.aguardar(200, 300);
      }
      if (!modal || !modal.classList.contains('show')) {
        Logs.adicionar(`⚠️ Modal de estoque não encontrado`, 'warning');
        return null;
      }

      // Garantir que o código do brinco está definido (necessário para o cadastro funcionar)
      if (typeof window.estoqueCadastroCodigoAtual === 'undefined') {
        window.estoqueCadastroCodigoAtual = sisbov || brinco;
      } else {
        window.estoqueCadastroCodigoAtual = sisbov || brinco;
      }
      
      Logs.adicionar(`📝 Preenchendo cadastro: ${raca}, ${sexo === 'M' ? 'Macho' : 'Fêmea'}, ${idade} meses`, 'info');

      const campoRaca = document.getElementById('estoqueCadastroRacaV2');
      const campoSexo = document.getElementById('estoqueCadastroSexoV2');
      const campoIdade = document.getElementById('estoqueCadastroIdadeMesesV2');
      const campoDataNasc = document.getElementById('estoqueCadastroDataNascV2');

      // Preencher raça
      if (campoRaca) {
        campoRaca.value = '';
        await Utils.simularDigitacao(campoRaca, raca, 50);
        await Utils.aguardar(200, 300);
      }

      // Preencher sexo
      if (campoSexo) {
        campoSexo.value = sexo;
        campoSexo.dispatchEvent(new Event('change', { bubbles: true }));
        await Utils.aguardar(200, 300);
      }

      // Preencher idade e calcular data de nascimento
      if (campoIdade) {
        campoIdade.value = '';
        await Utils.simularDigitacao(campoIdade, idade.toString(), 50);
        
        // Disparar evento input para calcular data de nascimento
        campoIdade.dispatchEvent(new Event('input', { bubbles: true }));
        campoIdade.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Tentar chamar a função de cálculo diretamente se disponível
        if (typeof window.calcularDataNascimentoPorIdadeMeses === 'function') {
          try {
            const dataCalc = window.calcularDataNascimentoPorIdadeMeses(idade);
            if (campoDataNasc && dataCalc) {
              const dataLocal = new Date(dataCalc);
              campoDataNasc.value = dataLocal.toLocaleDateString('pt-BR');
              Logs.adicionar(`✅ Data calculada: ${campoDataNasc.value}`, 'success');
            }
          } catch (e) {
            Logs.adicionar(`⚠️ Erro ao calcular data: ${e.message}`, 'warning');
          }
        }
        
        await Utils.aguardar(300, 500);
      }

      // Verificar se a data foi calculada
      if (campoDataNasc && !campoDataNasc.value) {
        Logs.adicionar(`⚠️ Data de nascimento não calculada, tentando novamente...`, 'warning');
        if (campoIdade) {
          campoIdade.dispatchEvent(new Event('input', { bubbles: true }));
          await Utils.aguardar(300, 500);
        }
      }

      // Verificar se todos os campos estão preenchidos antes de confirmar
      const tudoPreenchido = 
        (campoRaca && campoRaca.value.trim()) &&
        (campoSexo && campoSexo.value) &&
        (campoIdade && campoIdade.value) &&
        (campoDataNasc && campoDataNasc.value);

      if (!tudoPreenchido) {
        Logs.adicionar(`❌ Campos não preenchidos corretamente`, 'error');
        Logs.adicionar(`Raca: ${campoRaca?.value || 'vazio'}, Sexo: ${campoSexo?.value || 'vazio'}, Idade: ${campoIdade?.value || 'vazio'}, Data: ${campoDataNasc?.value || 'vazio'}`, 'error');
        return null;
      }

      await Utils.aguardar(300, 500);
      
      const btnOk = document.getElementById('estoqueCadastroOkBtnV2');
      if (btnOk) {
        // Verificar se o botão está habilitado
        if (btnOk.disabled) {
          Logs.adicionar(`⚠️ Botão de confirmação está desabilitado`, 'warning');
          return null;
        }
        
        Logs.adicionar(`✅ Confirmando cadastro...`, 'info');
        btnOk.click();
        await Utils.aguardar(2000, 3000);
        
        // Verificar se apareceu modal de confirmação
        const modalConfirm = document.getElementById('brincoConfirmOverlay');
        if (modalConfirm && modalConfirm.classList.contains('show')) {
          const btnOkConfirm = document.getElementById('brincoConfirmOkBtn');
          if (btnOkConfirm) {
            Logs.adicionar(`✅ Confirmando modal de confirmação...`, 'info');
            btnOkConfirm.click();
            await Utils.aguardar(1000, 1500);
          }
        }
        
        // Verificar se o modal foi fechado (indica sucesso)
        if (!modal.classList.contains('show')) {
          Logs.adicionar(`✅ Cadastro concluído com sucesso!`, 'success');
        }
        
        return {
          numero_brinco: brinco,
          codigo_sisbov: sisbov,
          raca: raca,
          sexo: sexo === 'M' ? 'Macho' : 'Fêmea',
          data_nascimento: campoDataNasc ? campoDataNasc.value : new Date().toISOString().split('T')[0],
          idade_meses: idade
        };
      }
      
      Logs.adicionar(`❌ Botão de confirmação não encontrado`, 'error');
      return null;
    },

    processarReprodutivo: async function() {
      const aba = document.getElementById('reprodutivo-tab');
      if (aba) {
        aba.click();
        await Utils.aguardar(300, 500);
      }
      if (typeof window.abrirDiagnosticoV2 === 'function') {
        try {
          window.abrirDiagnosticoV2();
          await Utils.aguardar(500, 800);
          const diagnosticos = ['PRENHA', 'VAZIA', 'NAO_AVALIADA'];
          const diagnostico = diagnosticos[Math.floor(Math.random() * diagnosticos.length)];
          if (typeof window.selecionarDiagnosticoV2 === 'function') {
            window.selecionarDiagnosticoV2(diagnostico);
          }
          await Utils.aguardar(400, 600);
          const btnOk = document.getElementById('diagnosticoOkBtnV2');
          if (btnOk) {
            btnOk.click();
            Logs.adicionar(`✅ Diagnóstico: ${diagnostico}`, 'success');
            await Utils.aguardar(800, 1200);
          }
        } catch (e) {
          Logs.adicionar(`⚠️ Erro no diagnóstico: ${e.message}`, 'warning');
        }
      }
    }
  };

  // ========== CONTROLE ==========
  const Controle = {
    iniciar: function() {
      if (Estado.ativo) {
        Controle.parar();
        return;
      }

      Estado.ativo = true;
      Estado.contador = 0;
      Estado.processando = false;

      if (Estado.intervalo) {
        clearInterval(Estado.intervalo);
        Estado.intervalo = null;
      }

      const btn = document.getElementById('btnSimulacao');
      if (btn) {
        btn.innerHTML = '<i class="fas fa-pause"></i> Parar Simulação (0/' + CONFIG.total + ')';
        btn.classList.add('ativo');
      }

      const painel = document.getElementById('simulacaoPainel');
      if (painel) painel.classList.add('ativo');

      Logs.adicionar(`🚀 Simulação iniciada - Processando ${CONFIG.total} registros...`, 'info');
      Logs.adicionar(`📡 Status do sistema: Online`, 'success');

      setTimeout(() => {
        if (Estado.ativo) Processador.processar();
      }, 1000);

      // Atualizar botão periodicamente
      const intervaloBotao = setInterval(() => {
        if (!Estado.ativo) {
          clearInterval(intervaloBotao);
          return;
        }
        const btn = document.getElementById('btnSimulacao');
        if (btn) {
          btn.innerHTML = '<i class="fas fa-pause"></i> Parar Simulação (' + Estado.contador + '/' + CONFIG.total + ')';
        }
      }, 1000);

      Estado.intervalo = setInterval(() => {
        if (!Estado.ativo) {
          clearInterval(Estado.intervalo);
          clearInterval(intervaloBotao);
          Estado.intervalo = null;
          return;
        }
        if (Estado.contador >= CONFIG.total) {
          clearInterval(intervaloBotao);
          Controle.finalizar();
          return;
        }
        if (!Estado.processando) {
          Processador.processar();
        }
      }, CONFIG.velocidade.processamento.min + Math.random() * (CONFIG.velocidade.processamento.max - CONFIG.velocidade.processamento.min));
    },

    parar: function() {
      Estado.ativo = false;
      if (Estado.intervalo) {
        clearInterval(Estado.intervalo);
        Estado.intervalo = null;
      }
      const btn = document.getElementById('btnSimulacao');
      if (btn) {
        btn.innerHTML = '<i class="fas fa-play"></i> Iniciar Simulação';
        btn.classList.remove('ativo');
      }
      Logs.adicionar(`🛑 Simulação parada (${Estado.contador}/${CONFIG.total} processados)`, 'warning');
    },

    finalizar: function() {
      Estado.ativo = false;
      if (Estado.intervalo) {
        clearInterval(Estado.intervalo);
        Estado.intervalo = null;
      }
      const btn = document.getElementById('btnSimulacao');
      if (btn) {
        btn.innerHTML = '<i class="fas fa-play"></i> Iniciar Simulação';
        btn.classList.remove('ativo');
      }
      Logs.adicionar(`🎉 Simulação concluída! ${Estado.contador} registros processados`, 'success');
    }
  };

  // ========== EXPORTAÇÃO ==========
  window.SimulacaoSistema = {
    iniciar: Controle.iniciar,
    parar: Controle.parar,
    finalizar: Controle.finalizar,
    logs: Logs
  };

  window.iniciarSimulacao = Controle.iniciar;

  // ========== INICIALIZAÇÃO ==========
  document.addEventListener('DOMContentLoaded', function() {
    // Inicializar variáveis globais
    if (typeof window.estatisticasAnimais === 'undefined') {
      window.estatisticasAnimais = { identificados: 0, cadastrados: 0, processados: 0 };
    }
    if (!window.animaisTrabalhados) {
      window.animaisTrabalhados = [];
    }

    const btn = document.getElementById('btnSimulacao');
    if (btn) {
      btn.style.display = 'flex';
      btn.style.visibility = 'visible';
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        Controle.iniciar();
      });
    }

    const btnLimpar = document.getElementById('btnLimparLogs');
    if (btnLimpar) {
      btnLimpar.addEventListener('click', Logs.limpar);
    }

    console.log('✅ Sistema de simulação profissional carregado');
  });

})();
