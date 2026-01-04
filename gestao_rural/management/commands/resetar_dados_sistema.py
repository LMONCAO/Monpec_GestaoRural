# -*- coding: utf-8 -*-
"""
Comando para resetar completamente todos os dados do sistema
Mantém apenas usuários admin e estruturas básicas do sistema

Uso:
    python manage.py resetar_dados_sistema
    python manage.py resetar_dados_sistema --confirmar
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q

# Importar todos os modelos
from gestao_rural.models import (
    ProdutorRural, Propriedade, DocumentoPropriedade,
    CategoriaAnimal, InventarioRebanho, PlanejamentoAnual,
    AtividadePlanejada, MetaComercialPlanejada, MetaFinanceiraPlanejada,
    IndicadorPlanejado, CenarioPlanejamento, PoliticaVendasCategoria,
    ParametrosProjecaoRebanho, ParametrosVendaPorCategoria,
    MovimentacaoProjetada, VendaProjetada, RegraPromocaoCategoria,
    TransferenciaPropriedade, ConfiguracaoVenda, CustoFixo, CustoVariavel,
    CategoriaImobilizado, BemImobilizado, TipoFinanciamento, Financiamento,
    IndicadorFinanceiro, FluxoCaixa, SCRBancoCentral, DividaBanco,
    ContratoDivida, AmortizacaoContrato, ProjetoBancario, DocumentoProjeto,
    AnimalIndividual, MovimentacaoIndividual, AnimalPesagem,
    AnimalVacinaAplicada, AnimalTratamento, AnimalReproducaoEvento,
    AnimalHistoricoEvento, AnimalDocumento, BrincoAnimal,
    CurralSessao, CurralLote, CurralEvento, MensagemWhatsApp,
    PrecoCEPEA, PreferenciaModulosUsuario, AssinaturaCliente,
    TenantWorkspace, TenantUsuario
)

# Importar modelos de outros módulos
try:
    from gestao_rural.models_cadastros import (
        UnidadeMedida, Cliente, Frigorifico, Fornecedor,
        CentroCusto, PlanoConta
    )
except ImportError:
    UnidadeMedida = Cliente = Frigorifico = Fornecedor = None
    CentroCusto = PlanoConta = None

try:
    from gestao_rural.models_compras import (
        FornecedorCompras, CategoriaInsumo, Insumo,
        EstoqueInsumo, OrdemCompra, ItemOrdemCompra, MovimentacaoEstoque
    )
except ImportError:
    FornecedorCompras = CategoriaInsumo = Insumo = None
    EstoqueInsumo = OrdemCompra = ItemOrdemCompra = MovimentacaoEstoque = None

try:
    from gestao_rural.models_funcionarios import (
        Funcionario, PontoFuncionario, FolhaPagamento,
        Holerite, DescontoFuncionario
    )
except ImportError:
    Funcionario = PontoFuncionario = FolhaPagamento = None
    Holerite = DescontoFuncionario = None

try:
    from gestao_rural.models_financeiro import (
        ContaBancaria, CategoriaFinanceira, LancamentoFinanceiro,
        ParcelaLancamento, TransferenciaConta, SaldoConta
    )
except ImportError:
    ContaBancaria = CategoriaFinanceira = LancamentoFinanceiro = None
    ParcelaLancamento = TransferenciaConta = SaldoConta = None

try:
    from gestao_rural.models_compras_financeiro import (
        Fornecedor as FornecedorCF, CategoriaProduto, Produto,
        NotaFiscal, ItemNotaFiscal, NumeroSequencialNFE,
        OrdemCompra as OrdemCompraCF, ItemOrdemCompra as ItemOrdemCompraCF,
        ContaPagar, ContaReceber, RequisicaoCompra, ItemRequisicaoCompra,
        AprovacaoRequisicaoCompra, CotacaoFornecedor, ItemCotacaoFornecedor,
        RecebimentoCompra, ItemRecebimentoCompra, SetorPropriedade,
        ConviteCotacaoFornecedor, OrcamentoCompraMensal, AjusteOrcamentoCompra,
        AutorizacaoExcedenteOrcamento, EventoFluxoCompra
    )
except ImportError:
    FornecedorCF = CategoriaProduto = Produto = None
    NotaFiscal = ItemNotaFiscal = NumeroSequencialNFE = None
    OrdemCompraCF = ItemOrdemCompraCF = ContaPagar = ContaReceber = None
    RequisicaoCompra = ItemRequisicaoCompra = AprovacaoRequisicaoCompra = None
    CotacaoFornecedor = ItemCotacaoFornecedor = RecebimentoCompra = None
    ItemRecebimentoCompra = SetorPropriedade = ConviteCotacaoFornecedor = None
    OrcamentoCompraMensal = AjusteOrcamentoCompra = None
    AutorizacaoExcedenteOrcamento = EventoFluxoCompra = None

try:
    from gestao_rural.models_auditoria import (
        LogAuditoria, VerificacaoEmail, SessaoSegura, UsuarioAtivo
    )
except ImportError:
    LogAuditoria = VerificacaoEmail = SessaoSegura = UsuarioAtivo = None

try:
    from gestao_rural.models_marketing import (
        TemplatePost, PostGerado, LeadInteressado, CampanhaMarketing,
        ConfiguracaoMarketing
    )
except ImportError:
    TemplatePost = PostGerado = LeadInteressado = None
    CampanhaMarketing = ConfiguracaoMarketing = None

try:
    from gestao_rural.models_reproducao import (
        Touro, EstacaoMonta, IATF, MontaNatural, Nascimento,
        CalendarioReprodutivo
    )
except ImportError:
    Touro = EstacaoMonta = IATF = MontaNatural = None
    Nascimento = CalendarioReprodutivo = None

try:
    from gestao_rural.models_operacional import (
        TanqueCombustivel, AbastecimentoCombustivel, ConsumoCombustivel,
        EstoqueSuplementacao, CompraSuplementacao, DistribuicaoSuplementacao,
        Empreiteiro, ServicoEmpreiteiro, TipoEquipamento, Equipamento,
        ManutencaoEquipamento
    )
except ImportError:
    TanqueCombustivel = AbastecimentoCombustivel = ConsumoCombustivel = None
    EstoqueSuplementacao = CompraSuplementacao = DistribuicaoSuplementacao = None
    Empreiteiro = ServicoEmpreiteiro = TipoEquipamento = None
    Equipamento = ManutencaoEquipamento = None

try:
    from gestao_rural.models_patrimonio import (
        TipoBem, BemPatrimonial
    )
except ImportError:
    TipoBem = BemPatrimonial = None

try:
    from gestao_rural.models_projetos import (
        Projeto, EtapaProjeto
    )
except ImportError:
    Projeto = EtapaProjeto = None

try:
    from gestao_rural.models_relatorios_customizados import (
        RelatorioCustomizado, TemplateRelatorio
    )
except ImportError:
    RelatorioCustomizado = TemplateRelatorio = None

try:
    from gestao_rural.models_manejo import (
        ManejoTipo, Manejo, ManejoHistorico, ManejoChecklistItem,
        ManejoChecklistExecucao
    )
except ImportError:
    ManejoTipo = Manejo = ManejoHistorico = None
    ManejoChecklistItem = ManejoChecklistExecucao = None

try:
    from gestao_rural.models_iatf_completo import (
        ProtocoloIATF, TouroSemen, LoteSemen, LoteIATF, EtapaLoteIATF,
        IATFIndividual, AplicacaoMedicamentoIATF, CalendarioIATF
    )
except ImportError:
    ProtocoloIATF = TouroSemen = LoteSemen = LoteIATF = None
    EtapaLoteIATF = IATFIndividual = AplicacaoMedicamentoIATF = None
    CalendarioIATF = None

try:
    from gestao_rural.models_controles_operacionais import (
        TipoDistribuicao, DistribuicaoPasto, Cocho, ControleCocho,
        ArquivoKML, Pastagem, RotacaoPastagem, MonitoramentoPastagem
    )
except ImportError:
    TipoDistribuicao = DistribuicaoPasto = Cocho = ControleCocho = None
    ArquivoKML = Pastagem = RotacaoPastagem = MonitoramentoPastagem = None


class Command(BaseCommand):
    help = 'Reseta completamente todos os dados do sistema, mantendo apenas usuários admin e estruturas básicas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a exclusão sem perguntar'
        )
        parser.add_argument(
            '--manter-usuarios',
            action='store_true',
            help='Mantém todos os usuários (não exclui usuários não-admin)'
        )

    def handle(self, *args, **options):
        confirmar = options['confirmar']
        manter_usuarios = options['manter_usuarios']
        
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('⚠️  ATENÇÃO: RESET COMPLETO DO SISTEMA'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write('')
        self.stdout.write('Este comando irá excluir:')
        self.stdout.write('  ❌ Todas as fazendas (propriedades)')
        self.stdout.write('  ❌ Todos os produtores rurais')
        self.stdout.write('  ❌ Todos os animais e movimentações')
        self.stdout.write('  ❌ Todas as vendas e compras')
        self.stdout.write('  ❌ Todos os funcionários e folhas de pagamento')
        self.stdout.write('  ❌ Todos os dados financeiros')
        self.stdout.write('  ❌ Todas as assinaturas e tenants')
        self.stdout.write('  ❌ Todos os planejamentos e projeções')
        self.stdout.write('')
        self.stdout.write('Será mantido:')
        self.stdout.write('  ✅ Usuários admin e estruturas básicas')
        self.stdout.write('  ✅ Planos de assinatura (configurações)')
        self.stdout.write('  ✅ Categorias padrão do sistema')
        self.stdout.write('')
        
        if not confirmar:
            resposta = input('\nTem CERTEZA ABSOLUTA que deseja continuar? Digite "RESETAR" para confirmar: ')
            if resposta != 'RESETAR':
                self.stdout.write(self.style.WARNING('Operação cancelada.'))
                return
        
        try:
            with transaction.atomic():
                self.stdout.write('\n🔄 Iniciando reset do sistema...\n')
                
                # 1. Excluir dados relacionados a animais individuais
                self._excluir_modelo(AnimalDocumento, 'Documentos de Animais')
                self._excluir_modelo(AnimalHistoricoEvento, 'Histórico de Eventos de Animais')
                self._excluir_modelo(AnimalReproducaoEvento, 'Eventos de Reprodução')
                self._excluir_modelo(AnimalTratamento, 'Tratamentos de Animais')
                self._excluir_modelo(AnimalVacinaAplicada, 'Vacinas Aplicadas')
                self._excluir_modelo(AnimalPesagem, 'Pesagens de Animais')
                self._excluir_modelo(MovimentacaoIndividual, 'Movimentações Individuais')
                self._excluir_modelo(AnimalIndividual, 'Animais Individuais')
                self._excluir_modelo(BrincoAnimal, 'Brinco de Animais')
                
                # 2. Excluir dados de curral
                self._excluir_modelo(CurralEvento, 'Eventos de Curral')
                self._excluir_modelo(CurralLote, 'Lotes de Curral')
                self._excluir_modelo(CurralSessao, 'Sessões de Curral')
                
                # 3. Excluir dados de IATF completo
                if AplicacaoMedicamentoIATF:
                    self._excluir_modelo(AplicacaoMedicamentoIATF, 'Aplicações de Medicamentos IATF')
                if IATFIndividual:
                    self._excluir_modelo(IATFIndividual, 'IATF Individual')
                if EtapaLoteIATF:
                    self._excluir_modelo(EtapaLoteIATF, 'Etapas de Lote IATF')
                if LoteIATF:
                    self._excluir_modelo(LoteIATF, 'Lotes IATF')
                if LoteSemen:
                    self._excluir_modelo(LoteSemen, 'Lotes de Sêmen')
                if TouroSemen:
                    self._excluir_modelo(TouroSemen, 'Touros de Sêmen')
                if ProtocoloIATF:
                    self._excluir_modelo(ProtocoloIATF, 'Protocolos IATF')
                if CalendarioIATF:
                    self._excluir_modelo(CalendarioIATF, 'Calendários IATF')
                
                # 4. Excluir dados de reprodução
                if CalendarioReprodutivo:
                    self._excluir_modelo(CalendarioReprodutivo, 'Calendários Reprodutivos')
                if Nascimento:
                    self._excluir_modelo(Nascimento, 'Nascimentos')
                if MontaNatural:
                    self._excluir_modelo(MontaNatural, 'Montas Naturais')
                if IATF:
                    self._excluir_modelo(IATF, 'IATF')
                if EstacaoMonta:
                    self._excluir_modelo(EstacaoMonta, 'Estações de Monta')
                if Touro:
                    self._excluir_modelo(Touro, 'Touros')
                
                # 5. Excluir dados de manejo
                if ManejoChecklistExecucao:
                    self._excluir_modelo(ManejoChecklistExecucao, 'Execuções de Checklist de Manejo')
                if ManejoChecklistItem:
                    self._excluir_modelo(ManejoChecklistItem, 'Itens de Checklist de Manejo')
                if ManejoHistorico:
                    self._excluir_modelo(ManejoHistorico, 'Históricos de Manejo')
                if Manejo:
                    self._excluir_modelo(Manejo, 'Manejos')
                if ManejoTipo:
                    self._excluir_modelo(ManejoTipo, 'Tipos de Manejo')
                
                # 6. Excluir dados de controles operacionais
                if MonitoramentoPastagem:
                    self._excluir_modelo(MonitoramentoPastagem, 'Monitoramentos de Pastagem')
                if RotacaoPastagem:
                    self._excluir_modelo(RotacaoPastagem, 'Rotações de Pastagem')
                if Pastagem:
                    self._excluir_modelo(Pastagem, 'Pastagens')
                if ArquivoKML:
                    self._excluir_modelo(ArquivoKML, 'Arquivos KML')
                if ControleCocho:
                    self._excluir_modelo(ControleCocho, 'Controles de Cocho')
                if Cocho:
                    self._excluir_modelo(Cocho, 'Cochos')
                if DistribuicaoPasto:
                    self._excluir_modelo(DistribuicaoPasto, 'Distribuições de Pasto')
                if TipoDistribuicao:
                    self._excluir_modelo(TipoDistribuicao, 'Tipos de Distribuição')
                
                # 7. Excluir dados operacionais
                if ManutencaoEquipamento:
                    self._excluir_modelo(ManutencaoEquipamento, 'Manutenções de Equipamentos')
                if Equipamento:
                    self._excluir_modelo(Equipamento, 'Equipamentos')
                if TipoEquipamento:
                    self._excluir_modelo(TipoEquipamento, 'Tipos de Equipamento')
                if ServicoEmpreiteiro:
                    self._excluir_modelo(ServicoEmpreiteiro, 'Serviços de Empreiteiros')
                if Empreiteiro:
                    self._excluir_modelo(Empreiteiro, 'Empreiteiros')
                if DistribuicaoSuplementacao:
                    self._excluir_modelo(DistribuicaoSuplementacao, 'Distribuições de Suplementação')
                if CompraSuplementacao:
                    self._excluir_modelo(CompraSuplementacao, 'Compras de Suplementação')
                if EstoqueSuplementacao:
                    self._excluir_modelo(EstoqueSuplementacao, 'Estoques de Suplementação')
                if ConsumoCombustivel:
                    self._excluir_modelo(ConsumoCombustivel, 'Consumos de Combustível')
                if AbastecimentoCombustivel:
                    self._excluir_modelo(AbastecimentoCombustivel, 'Abastecimentos de Combustível')
                if TanqueCombustivel:
                    self._excluir_modelo(TanqueCombustivel, 'Tanques de Combustível')
                
                # 8. Excluir dados de patrimônio
                if BemPatrimonial:
                    self._excluir_modelo(BemPatrimonial, 'Bens Patrimoniais')
                if TipoBem:
                    self._excluir_modelo(TipoBem, 'Tipos de Bens')
                
                # 9. Excluir dados de projetos
                if EtapaProjeto:
                    self._excluir_modelo(EtapaProjeto, 'Etapas de Projetos')
                if Projeto:
                    self._excluir_modelo(Projeto, 'Projetos')
                
                # 10. Excluir dados de relatórios customizados
                if RelatorioCustomizado:
                    self._excluir_modelo(RelatorioCustomizado, 'Relatórios Customizados')
                if TemplateRelatorio:
                    self._excluir_modelo(TemplateRelatorio, 'Templates de Relatórios')
                
                # 11. Excluir dados de marketing
                if ConfiguracaoMarketing:
                    self._excluir_modelo(ConfiguracaoMarketing, 'Configurações de Marketing')
                if CampanhaMarketing:
                    self._excluir_modelo(CampanhaMarketing, 'Campanhas de Marketing')
                if LeadInteressado:
                    self._excluir_modelo(LeadInteressado, 'Leads Interessados')
                if PostGerado:
                    self._excluir_modelo(PostGerado, 'Posts Gerados')
                if TemplatePost:
                    self._excluir_modelo(TemplatePost, 'Templates de Posts')
                
                # 12. Excluir dados de auditoria
                if UsuarioAtivo:
                    self._excluir_modelo(UsuarioAtivo, 'Usuários Ativos')
                if SessaoSegura:
                    self._excluir_modelo(SessaoSegura, 'Sessões Seguras')
                if VerificacaoEmail:
                    self._excluir_modelo(VerificacaoEmail, 'Verificações de Email')
                if LogAuditoria:
                    self._excluir_modelo(LogAuditoria, 'Logs de Auditoria')
                
                # 13. Excluir dados de compras e financeiro (models_compras_financeiro)
                if EventoFluxoCompra:
                    self._excluir_modelo(EventoFluxoCompra, 'Eventos de Fluxo de Compra')
                if AutorizacaoExcedenteOrcamento:
                    self._excluir_modelo(AutorizacaoExcedenteOrcamento, 'Autorizações de Excedente de Orçamento')
                if AjusteOrcamentoCompra:
                    self._excluir_modelo(AjusteOrcamentoCompra, 'Ajustes de Orçamento de Compra')
                if OrcamentoCompraMensal:
                    self._excluir_modelo(OrcamentoCompraMensal, 'Orçamentos de Compra Mensais')
                if ConviteCotacaoFornecedor:
                    self._excluir_modelo(ConviteCotacaoFornecedor, 'Convites de Cotação para Fornecedores')
                if SetorPropriedade:
                    self._excluir_modelo(SetorPropriedade, 'Setores de Propriedade')
                if ItemRecebimentoCompra:
                    self._excluir_modelo(ItemRecebimentoCompra, 'Itens de Recebimento de Compra')
                if RecebimentoCompra:
                    self._excluir_modelo(RecebimentoCompra, 'Recebimentos de Compra')
                if ItemCotacaoFornecedor:
                    self._excluir_modelo(ItemCotacaoFornecedor, 'Itens de Cotação de Fornecedor')
                if CotacaoFornecedor:
                    self._excluir_modelo(CotacaoFornecedor, 'Cotações de Fornecedores')
                if AprovacaoRequisicaoCompra:
                    self._excluir_modelo(AprovacaoRequisicaoCompra, 'Aprovações de Requisição de Compra')
                if ItemRequisicaoCompra:
                    self._excluir_modelo(ItemRequisicaoCompra, 'Itens de Requisição de Compra')
                if RequisicaoCompra:
                    self._excluir_modelo(RequisicaoCompra, 'Requisições de Compra')
                if ContaReceber:
                    self._excluir_modelo(ContaReceber, 'Contas a Receber')
                if ContaPagar:
                    self._excluir_modelo(ContaPagar, 'Contas a Pagar')
                if ItemOrdemCompraCF:
                    self._excluir_modelo(ItemOrdemCompraCF, 'Itens de Ordem de Compra (CF)')
                if OrdemCompraCF:
                    self._excluir_modelo(OrdemCompraCF, 'Ordens de Compra (CF)')
                if NumeroSequencialNFE:
                    self._excluir_modelo(NumeroSequencialNFE, 'Números Sequenciais NFE')
                if ItemNotaFiscal:
                    self._excluir_modelo(ItemNotaFiscal, 'Itens de Nota Fiscal')
                if NotaFiscal:
                    self._excluir_modelo(NotaFiscal, 'Notas Fiscais')
                if Produto:
                    self._excluir_modelo(Produto, 'Produtos')
                if CategoriaProduto:
                    self._excluir_modelo(CategoriaProduto, 'Categorias de Produtos')
                if FornecedorCF:
                    self._excluir_modelo(FornecedorCF, 'Fornecedores (CF)')
                
                # 14. Excluir dados de compras (models_compras)
                if ItemOrdemCompra:
                    self._excluir_modelo(ItemOrdemCompra, 'Itens de Ordem de Compra')
                if OrdemCompra:
                    self._excluir_modelo(OrdemCompra, 'Ordens de Compra')
                if MovimentacaoEstoque:
                    self._excluir_modelo(MovimentacaoEstoque, 'Movimentações de Estoque')
                if EstoqueInsumo:
                    self._excluir_modelo(EstoqueInsumo, 'Estoque de Insumos')
                if Insumo:
                    self._excluir_modelo(Insumo, 'Insumos')
                if CategoriaInsumo:
                    self._excluir_modelo(CategoriaInsumo, 'Categorias de Insumos')
                if FornecedorCompras:
                    self._excluir_modelo(FornecedorCompras, 'Fornecedores de Compras')
                
                # 15. Excluir dados de funcionários
                if DescontoFuncionario:
                    self._excluir_modelo(DescontoFuncionario, 'Descontos de Funcionários')
                if Holerite:
                    self._excluir_modelo(Holerite, 'Holerites')
                if FolhaPagamento:
                    self._excluir_modelo(FolhaPagamento, 'Folhas de Pagamento')
                if PontoFuncionario:
                    self._excluir_modelo(PontoFuncionario, 'Pontos de Funcionários')
                if Funcionario:
                    self._excluir_modelo(Funcionario, 'Funcionários')
                
                # 16. Excluir dados financeiros
                if SaldoConta:
                    self._excluir_modelo(SaldoConta, 'Saldos de Contas')
                if TransferenciaConta:
                    self._excluir_modelo(TransferenciaConta, 'Transferências entre Contas')
                if ParcelaLancamento:
                    self._excluir_modelo(ParcelaLancamento, 'Parcelas de Lançamentos')
                if LancamentoFinanceiro:
                    self._excluir_modelo(LancamentoFinanceiro, 'Lançamentos Financeiros')
                if ContaBancaria:
                    self._excluir_modelo(ContaBancaria, 'Contas Bancárias')
                if CategoriaFinanceira:
                    self._excluir_modelo(CategoriaFinanceira, 'Categorias Financeiras')
                
                # 17. Excluir dados de projetos bancários
                self._excluir_modelo(DocumentoProjeto, 'Documentos de Projetos')
                self._excluir_modelo(ProjetoBancario, 'Projetos Bancários')
                self._excluir_modelo(AmortizacaoContrato, 'Amortizações de Contratos')
                self._excluir_modelo(ContratoDivida, 'Contratos de Dívidas')
                self._excluir_modelo(DividaBanco, 'Dívidas de Bancos')
                self._excluir_modelo(SCRBancoCentral, 'SCR Banco Central')
                self._excluir_modelo(FluxoCaixa, 'Fluxos de Caixa')
                self._excluir_modelo(IndicadorFinanceiro, 'Indicadores Financeiros')
                self._excluir_modelo(Financiamento, 'Financiamentos')
                self._excluir_modelo(TipoFinanciamento, 'Tipos de Financiamento')
                self._excluir_modelo(BemImobilizado, 'Bens Imobilizados')
                self._excluir_modelo(CategoriaImobilizado, 'Categorias de Imobilizados')
                self._excluir_modelo(CustoVariavel, 'Custos Variáveis')
                self._excluir_modelo(CustoFixo, 'Custos Fixos')
                
                # 18. Excluir dados de planejamento e projeções
                self._excluir_modelo(ConfiguracaoVenda, 'Configurações de Venda')
                self._excluir_modelo(TransferenciaPropriedade, 'Transferências de Propriedade')
                self._excluir_modelo(RegraPromocaoCategoria, 'Regras de Promoção')
                self._excluir_modelo(VendaProjetada, 'Vendas Projetadas')
                self._excluir_modelo(MovimentacaoProjetada, 'Movimentações Projetadas')
                self._excluir_modelo(ParametrosVendaPorCategoria, 'Parâmetros de Venda por Categoria')
                self._excluir_modelo(ParametrosProjecaoRebanho, 'Parâmetros de Projeção de Rebanho')
                self._excluir_modelo(PoliticaVendasCategoria, 'Políticas de Vendas por Categoria')
                self._excluir_modelo(CenarioPlanejamento, 'Cenários de Planejamento')
                self._excluir_modelo(IndicadorPlanejado, 'Indicadores Planejados')
                self._excluir_modelo(MetaFinanceiraPlanejada, 'Metas Financeiras Planejadas')
                self._excluir_modelo(MetaComercialPlanejada, 'Metas Comerciais Planejadas')
                self._excluir_modelo(AtividadePlanejada, 'Atividades Planejadas')
                self._excluir_modelo(PlanejamentoAnual, 'Planejamentos Anuais')
                self._excluir_modelo(InventarioRebanho, 'Inventários de Rebanho')
                
                # 19. Excluir cadastros relacionados a propriedades
                if Cliente:
                    self._excluir_modelo(Cliente, 'Clientes')
                if Frigorifico:
                    self._excluir_modelo(Frigorifico, 'Frigoríficos')
                if Fornecedor:
                    self._excluir_modelo(Fornecedor, 'Fornecedores')
                if CentroCusto:
                    self._excluir_modelo(CentroCusto, 'Centros de Custo')
                if PlanoConta:
                    self._excluir_modelo(PlanoConta, 'Planos de Conta')
                
                # 20. Excluir propriedades e documentos
                self._excluir_modelo(DocumentoPropriedade, 'Documentos de Propriedades')
                self._excluir_modelo(Propriedade, 'Propriedades (Fazendas)')
                
                # 21. Excluir categorias de animais (exceto as padrão do sistema)
                # Manter apenas categorias que não estão vinculadas a propriedades
                categorias_excluidas = CategoriaAnimal.objects.filter(
                    propriedade__isnull=False
                ).count()
                CategoriaAnimal.objects.filter(propriedade__isnull=False).delete()
                if categorias_excluidas > 0:
                    self.stdout.write(f'  ✅ {categorias_excluidas} categorias de animais excluídas')
                
                # 22. Excluir produtores rurais
                self._excluir_modelo(ProdutorRural, 'Produtores Rurais')
                
                # 23. Excluir assinaturas e tenants
                self._excluir_modelo(TenantWorkspace, 'Workspaces de Tenants')
                self._excluir_modelo(TenantUsuario, 'Usuários de Tenants')
                self._excluir_modelo(AssinaturaCliente, 'Assinaturas de Clientes')
                
                # 24. Excluir outros dados
                self._excluir_modelo(MensagemWhatsApp, 'Mensagens WhatsApp')
                self._excluir_modelo(PreferenciaModulosUsuario, 'Preferências de Módulos')
                
                # 25. Excluir usuários (exceto admin e superusers, se não for para manter)
                if not manter_usuarios:
                    usuarios_excluidos = User.objects.filter(
                        Q(is_superuser=False) & Q(is_staff=False)
                    ).count()
                    User.objects.filter(
                        Q(is_superuser=False) & Q(is_staff=False)
                    ).delete()
                    if usuarios_excluidos > 0:
                        self.stdout.write(f'  ✅ {usuarios_excluidos} usuários não-admin excluídos')
                
                # 26. Limpar dados de PrecoCEPEA (manter estrutura, limpar histórico)
                precos_excluidos = PrecoCEPEA.objects.count()
                PrecoCEPEA.objects.all().delete()
                if precos_excluidos > 0:
                    self.stdout.write(f'  ✅ {precos_excluidos} preços CEPEA excluídos')
                
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('=' * 70))
                self.stdout.write(self.style.SUCCESS('✅ RESET DO SISTEMA CONCLUÍDO COM SUCESSO!'))
                self.stdout.write(self.style.SUCCESS('=' * 70))
                self.stdout.write('')
                self.stdout.write('O sistema foi completamente resetado.')
                self.stdout.write('Todos os dados foram excluídos, mantendo apenas:')
                self.stdout.write('  • Usuários admin e superusers')
                self.stdout.write('  • Planos de assinatura (configurações)')
                self.stdout.write('  • Categorias padrão do sistema')
                self.stdout.write('')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao resetar sistema: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise
    
    def _excluir_modelo(self, modelo, nome_descritivo):
        """Exclui todos os registros de um modelo"""
        if modelo is None:
            return
        
        try:
            count = modelo.objects.count()
            if count > 0:
                modelo.objects.all().delete()
                self.stdout.write(f'  ✅ {count} {nome_descritivo} excluído(s)')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  Erro ao excluir {nome_descritivo}: {e}')
            )


