# -*- coding: utf-8 -*-
"""
Comando para sincronizar automaticamente Notas Fiscais Eletrônicas recebidas
(emitidas para o CPF/CNPJ da propriedade)
"""

from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.conf import settings

from gestao_rural.models import Propriedade
from gestao_rural.services_nfe_consulta import (
    consultar_nfe_recebidas,
    baixar_xml_nfe,
    baixar_pdf_nfe,
    importar_nfe_do_xml
)
from gestao_rural.models_compras_financeiro import NotaFiscal
from gestao_rural.views_compras import gerar_conta_pagar_para_ordem
from gestao_rural.models_compras_financeiro import OrdemCompra


class Command(BaseCommand):
    help = 'Sincroniza NFe recebidas automaticamente para todas as propriedades configuradas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--propriedade-id',
            type=int,
            help='ID da propriedade específica (se não informado, sincroniza todas)',
        )
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Número de dias para buscar NFe (padrão: 30)',
        )
        parser.add_argument(
            '--limite',
            type=int,
            default=100,
            help='Número máximo de notas a buscar por propriedade (padrão: 100)',
        )
        parser.add_argument(
            '--baixar-pdf',
            action='store_true',
            help='Baixar PDF (DANFE) das notas encontradas',
        )

    def handle(self, *args, **options):
        propriedade_id = options.get('propriedade_id')
        dias = options.get('dias', 30)
        limite = options.get('limite', 100)
        baixar_pdf = options.get('baixar_pdf', False)
        
        # Verificar configuração da API
        api_nfe = getattr(settings, 'API_NFE', None)
        if not api_nfe:
            self.stdout.write(
                self.style.ERROR('API de NF-e não configurada. Configure API_NFE nas settings.')
            )
            return
        
        # Buscar propriedades
        if propriedade_id:
            try:
                propriedades = [Propriedade.objects.get(id=propriedade_id)]
            except Propriedade.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Propriedade com ID {propriedade_id} não encontrada.')
                )
                return
        else:
            # Buscar todas as propriedades que têm CPF/CNPJ configurado
            propriedades = Propriedade.objects.exclude(
                produtor__cpf_cnpj__isnull=True
            ).exclude(
                produtor__cpf_cnpj=''
            )
        
        if not propriedades:
            self.stdout.write(
                self.style.WARNING('Nenhuma propriedade encontrada com CPF/CNPJ configurado.')
            )
            return
        
        total_propriedades = len(propriedades)
        self.stdout.write(
            self.style.SUCCESS(f'Iniciando sincronização para {total_propriedades} propriedade(s)...')
        )
        
        # Definir período
        data_fim = date.today()
        data_inicio = data_fim - timedelta(days=dias)
        
        total_notas_encontradas = 0
        total_notas_importadas = 0
        total_erros = 0
        
        for propriedade in propriedades:
            self.stdout.write(f'\n{"="*60}')
            self.stdout.write(f'Propriedade: {propriedade.nome_propriedade}')
            self.stdout.write(f'CPF/CNPJ: {propriedade.produtor.cpf_cnpj}')
            self.stdout.write(f'Período: {data_inicio} a {data_fim}')
            self.stdout.write(f'{"="*60}')
            
            try:
                # Consultar NFe recebidas
                resultado = consultar_nfe_recebidas(
                    propriedade=propriedade,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    limite=limite
                )
                
                if not resultado['sucesso']:
                    self.stdout.write(
                        self.style.WARNING(f'Erro ao consultar: {resultado.get("erro", "Erro desconhecido")}')
                    )
                    total_erros += 1
                    continue
                
                notas_encontradas = resultado.get('notas', [])
                total_encontrado = resultado.get('total_encontrado', 0)
                total_notas_encontradas += total_encontrado
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {total_encontrado} nota(s) encontrada(s)')
                )
                
                if not notas_encontradas:
                    self.stdout.write('  Nenhuma nota nova para importar.')
                    continue
                
                # Processar cada nota
                notas_importadas_propriedade = 0
                for nota_data in notas_encontradas:
                    chave_acesso = nota_data.get('chave_acesso', '')
                    
                    if not chave_acesso:
                        self.stdout.write(
                            self.style.WARNING('  ⚠ Nota sem chave de acesso, pulando...')
                        )
                        continue
                    
                    # Verificar se já existe
                    if NotaFiscal.objects.filter(chave_acesso=chave_acesso).exists():
                        self.stdout.write(f'  ⊗ Nota {chave_acesso[:20]}... já existe, pulando...')
                        continue
                    
                    try:
                        with transaction.atomic():
                            # Baixar XML
                            api_config = getattr(settings, 'API_NFE', {})
                            resultado_xml = baixar_xml_nfe(chave_acesso, api_config)
                            
                            if not resultado_xml['sucesso']:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'  ⚠ Erro ao baixar XML da nota {chave_acesso[:20]}...: '
                                        f'{resultado_xml.get("erro", "Erro desconhecido")}'
                                    )
                                )
                                continue
                            
                            xml_content = resultado_xml.get('xml')
                            if not xml_content:
                                self.stdout.write(
                                    self.style.WARNING(f'  ⚠ XML vazio para nota {chave_acesso[:20]}...')
                                )
                                continue
                            
                            # Importar NFe do XML
                            resultado_importacao = importar_nfe_do_xml(
                                xml_content=xml_content,
                                propriedade=propriedade,
                                usuario=None  # Importação automática
                            )
                            
                            if not resultado_importacao['sucesso']:
                                self.stdout.write(
                                    self.style.ERROR(
                                        f'  ✗ Erro ao importar nota {chave_acesso[:20]}...: '
                                        f'{resultado_importacao.get("erro", "Erro desconhecido")}'
                                    )
                                )
                                continue
                            
                            nota_fiscal = resultado_importacao['nota_fiscal']
                            
                            # Baixar PDF se solicitado
                            if baixar_pdf:
                                resultado_pdf = baixar_pdf_nfe(chave_acesso, api_config)
                                if resultado_pdf['sucesso']:
                                    from django.core.files.base import ContentFile
                                    nota_fiscal.arquivo_pdf.save(
                                        f'nfe_{chave_acesso}.pdf',
                                        ContentFile(resultado_pdf['pdf']),
                                        save=True
                                    )
                            
                            # Tentar vincular a ordem de compra
                            self._vincular_ordem_compra(nota_fiscal, propriedade)
                            
                            notas_importadas_propriedade += 1
                            total_notas_importadas += 1
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  ✓ Nota {nota_fiscal.numero}/{nota_fiscal.serie} '
                                    f'importada (R$ {nota_fiscal.valor_total:.2f})'
                                )
                            )
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'  ✗ Erro ao processar nota: {str(e)}')
                        )
                        total_erros += 1
                        continue
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✓ {notas_importadas_propriedade} nota(s) importada(s) para esta propriedade'
                    )
                )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'\n✗ Erro ao processar propriedade: {str(e)}')
                )
                total_erros += 1
                continue
        
        # Resumo final
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(self.style.SUCCESS('RESUMO DA SINCRONIZAÇÃO'))
        self.stdout.write(f'{"="*60}')
        self.stdout.write(f'Propriedades processadas: {total_propriedades}')
        self.stdout.write(f'Notas encontradas: {total_notas_encontradas}')
        self.stdout.write(f'Notas importadas: {total_notas_importadas}')
        self.stdout.write(f'Erros: {total_erros}')
        self.stdout.write(f'{"="*60}\n')
    
    def _vincular_ordem_compra(self, nota_fiscal, propriedade):
        """
        Tenta vincular a nota fiscal a uma ordem de compra existente
        """
        try:
            # Buscar ordens de compra do mesmo fornecedor sem nota fiscal
            ordens_possiveis = OrdemCompra.objects.filter(
                propriedade=propriedade,
                fornecedor=nota_fiscal.fornecedor,
                nota_fiscal__isnull=True,
                status__in=['ENVIADA', 'APROVADA', 'RECEBIDA']
            ).order_by('-data_emissao')
            
            from decimal import Decimal
            tolerancia_minima = Decimal('1.00')
            tolerancia_percentual = Decimal('0.05')
            
            for ordem_candidata in ordens_possiveis:
                if ordem_candidata.valor_total:
                    diferenca = abs(ordem_candidata.valor_total - nota_fiscal.valor_total)
                    tolerancia = max(tolerancia_minima, ordem_candidata.valor_total * tolerancia_percentual)
                    
                    if diferenca <= tolerancia:
                        # Vincular
                        ordem_candidata.nota_fiscal = nota_fiscal
                        ordem_candidata.status = 'RECEBIDA'
                        ordem_candidata.data_recebimento = nota_fiscal.data_emissao
                        ordem_candidata.save(update_fields=['nota_fiscal', 'status', 'data_recebimento'])
                        
                        # Gerar conta a pagar
                        conta_pagar, _ = gerar_conta_pagar_para_ordem(ordem_candidata)
                        conta_pagar.nota_fiscal = nota_fiscal
                        conta_pagar.valor = nota_fiscal.valor_total
                        conta_pagar.save(update_fields=['nota_fiscal', 'valor'])
                        
                        return True
            
            return False
        except Exception as e:
            # Não falhar a importação se houver erro na vinculação
            return False

