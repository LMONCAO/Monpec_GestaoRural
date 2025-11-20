# -*- coding: utf-8 -*-
"""
Serviço para processar mensagens de áudio do WhatsApp e extrair informações
sobre distribuição de suplementação
"""

import re
from datetime import datetime, date
from typing import Dict, Optional, Tuple
from decimal import Decimal, InvalidOperation

from django.utils import timezone
from django.contrib.auth.models import User
from gestao_rural.models import MensagemWhatsApp, Propriedade
from gestao_rural.models_operacional import DistribuicaoSuplementacao, EstoqueSuplementacao


class ProcessadorAudioSuplementacao:
    """Processa áudio transcrito e extrai informações estruturadas sobre distribuição de suplementação"""
    
    def __init__(self):
        self.padroes = {
            'tipo_suplementacao': [
                r'tipo\s+(?:de\s+)?suplement(?:a|o|ação|ação)\s*:?\s*([a-záàâãéêíóôõúç\s]+)',
                r'suplement(?:a|o|ação|ação)\s*:?\s*([a-záàâãéêíóôõúç\s]+)',
                r'(?:distribuí|distribuir|distribuindo)\s+(?:o\s+)?([a-záàâãéêíóôõúç\s]+?)(?:\s+(?:na|para|em))',
                r'(sal\s+mineral|ração|suplemento\s+proteico|ração|sal|mineral|proteinado)',
            ],
            'nome_produto': [
                r'(?:produto|nome\s+do\s+produto|marca)\s*:?\s*([a-záàâãéêíóôõúç\d\s\-]+?)(?:\s*,\s*(?:quantidade|invernada|na|para|em)|$)',
                r'tipo\s+(?:de\s+)?suplement(?:a|o|ação|ação)\s+[^,]+,\s*produto\s+([a-záàâãéêíóôõúç\d\s\-]+?)(?:\s*,\s*(?:quantidade|invernada|na|para|em)|$)',
                r'(?:produto|marca)\s+([a-záàâãéêíóôõúç\d\s\-]+?)(?:\s*,\s*(?:quantidade|invernada|na|para|em)|$)',
            ],
            'quantidade': [
                r'quantidade\s*:?\s*(\d+[.,]?\d*)\s*(?:saco|sacos|sc|scs)',
                r'(\d+[.,]?\d*)\s*(?:saco|sacos|sc|scs)',
                r'distribuí\s+(\d+[.,]?\d*)\s*(?:saco|sacos|sc|scs)',
                r'(\d+[.,]?\d*)\s*(?:saco|sacos)',
                r'quantidade\s*:?\s*(\d+[.,]?\d*)\s*(?:kg|quilos|kilos|gramas|g)',
                r'(\d+[.,]?\d*)\s*(?:kg|quilos|kilos|gramas|g)',
                r'distribuí\s+(\d+[.,]?\d*)',
                r'(\d+[.,]?\d*)\s*(?:kg|quilos)',
            ],
            'invernada': [
                r'invernada\s*:?\s*([a-záàâãéêíóôõúç\d\s]+)',
                r'invernada\s+([a-záàâãéêíóôõúç\d\s]+)',
                r'(?:na|da)\s+invernada\s+([a-záàâãéêíóôõúç\d\s]+)',
                r'pasto\s+([a-záàâãéêíóôõúç\d\s]+)',
                r'piquete\s+([a-záàâãéêíóôõúç\d\s]+)',
            ],
            'data': [
                r'hoje|agora',
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
                r'data\s*:?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            ],
        }
    
    def processar_texto(self, texto: str) -> Dict:
        """
        Processa texto transcrito e extrai informações estruturadas
        
        Retorna dicionário com:
        - tipo_suplementacao: str
        - quantidade: Decimal
        - invernada: str
        - data: date
        - observacoes: str
        """
        texto_lower = texto.lower()
        dados = {
            'tipo_suplementacao': None,
            'nome_produto': None,
            'quantidade': None,
            'invernada': None,
            'data': None,
            'observacoes': texto,
        }
        
        # Extrair tipo de suplementação
        for padrao in self.padroes['tipo_suplementacao']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                tipo_texto = match.group(1).strip()
                # Normalizar tipos comuns
                tipo_texto = tipo_texto.lower()
                if 'sal' in tipo_texto and 'mineral' in tipo_texto:
                    dados['tipo_suplementacao'] = 'Sal Mineral'
                elif 'ração' in tipo_texto:
                    dados['tipo_suplementacao'] = 'Ração'
                elif 'proteico' in tipo_texto or 'proteinado' in tipo_texto:
                    dados['tipo_suplementacao'] = 'Suplemento Proteico'
                elif 'sal' in tipo_texto:
                    dados['tipo_suplementacao'] = 'Sal'
                elif 'mineral' in tipo_texto:
                    dados['tipo_suplementacao'] = 'Mineral'
                else:
                    dados['tipo_suplementacao'] = tipo_texto.title()  # Capitalizar primeira letra
                break
        
        # Extrair nome do produto (após tipo de suplementação)
        for padrao in self.padroes['nome_produto']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                nome_produto = match.group(1).strip()
                # Limpar o nome do produto (remover palavras comuns que podem ter sido capturadas)
                nome_produto = re.sub(r'\b(?:tipo|de|suplementação|suplemento|produto|nome|marca)\b', '', nome_produto, flags=re.IGNORECASE)
                nome_produto = re.sub(r'\s+', ' ', nome_produto).strip()
                if nome_produto and len(nome_produto) > 2:
                    dados['nome_produto'] = nome_produto.title()  # Capitalizar primeira letra
                    break
        
        # Extrair quantidade (prioridade para sacos)
        for i, padrao in enumerate(self.padroes['quantidade']):
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                quantidade_str = match.group(1).replace(',', '.')
                try:
                    quantidade = Decimal(quantidade_str)
                    # Verificar se é em sacos (primeiros 4 padrões são para sacos)
                    if i < 4:  # Primeiros 4 padrões são para sacos
                        dados['quantidade_sacos'] = quantidade
                    else:
                        # Se mencionou gramas, converter para kg
                        if 'grama' in texto_lower or 'g ' in texto_lower:
                            quantidade = quantidade / 1000
                        dados['quantidade'] = quantidade
                        dados['quantidade_original'] = quantidade_str
                except (InvalidOperation, ValueError):
                    pass
                if dados.get('quantidade') or dados.get('quantidade_sacos'):
                    break
        
        # Extrair invernada
        for padrao in self.padroes['invernada']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                invernada_texto = match.group(1).strip()
                dados['invernada'] = invernada_texto.title()  # Capitalizar primeira letra
                break
        
        # Extrair data (usa hoje se não informada)
        hoje = date.today()
        for padrao in self.padroes['data']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                if 'hoje' in texto_lower or 'agora' in texto_lower:
                    dados['data'] = hoje
                    break
                try:
                    dia = int(match.group(1))
                    mes = int(match.group(2))
                    ano_str = match.group(3)
                    if len(ano_str) == 2:
                        ano = 2000 + int(ano_str)
                    else:
                        ano = int(ano_str)
                    dados['data'] = date(ano, mes, dia)
                except (ValueError, IndexError):
                    pass
                if dados['data']:
                    break
        
        # Se não encontrou data, assume hoje
        if not dados['data']:
            dados['data'] = hoje
        
        return dados
    
    def _extrair_fator_conversao_saco(self, estoque: EstoqueSuplementacao) -> Decimal:
        """
        Extrai o fator de conversão de sacos para a unidade do estoque
        Procura nas observações padrões como "50 kg por saco", "1 saco = 50kg", etc.
        Se não encontrar, usa padrão comum: 50 kg por saco
        """
        if not estoque.observacoes:
            return Decimal('50')  # Padrão: 50 kg por saco
        
        texto_obs = estoque.observacoes.lower()
        
        # Padrões para encontrar conversão
        padroes = [
            r'(\d+[.,]?\d*)\s*(?:kg|quilos|kilos)\s*(?:por|/\s*)?\s*(?:saco|sc)',
            r'(?:saco|sc)\s*(?:=|equivale|tem)\s*(\d+[.,]?\d*)\s*(?:kg|quilos|kilos)',
            r'(\d+[.,]?\d*)\s*(?:kg|quilos|kilos)\s*(?:por|/\s*)?\s*(?:saco|sc)',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto_obs, re.IGNORECASE)
            if match:
                try:
                    fator = Decimal(match.group(1).replace(',', '.'))
                    return fator
                except (InvalidOperation, ValueError):
                    continue
        
        # Padrão comum se não encontrar
        return Decimal('50')  # 50 kg por saco
    
    def validar_dados(self, dados: Dict, propriedade) -> Tuple[bool, Optional[str]]:
        """Valida se os dados extraídos são suficientes para registrar distribuição"""
        erros = []
        
        if not dados.get('tipo_suplementacao'):
            erros.append("Tipo de suplementação não identificado")
        
        if not dados.get('quantidade') and not dados.get('quantidade_sacos'):
            erros.append("Quantidade não identificada")
        
        if not dados.get('invernada'):
            erros.append("Invernada não identificada")
        
        # Verificar se existe estoque do tipo de suplementação e converter se necessário
        if dados.get('tipo_suplementacao') and propriedade:
            try:
                estoque = EstoqueSuplementacao.objects.filter(
                    propriedade=propriedade,
                    tipo_suplemento__icontains=dados['tipo_suplementacao']
                ).first()
                if not estoque:
                    erros.append(f"Estoque de {dados['tipo_suplementacao']} não encontrado. Crie o estoque primeiro.")
                else:
                    # Se quantidade foi informada em sacos, converter
                    if dados.get('quantidade_sacos'):
                        fator_conversao = self._extrair_fator_conversao_saco(estoque)
                        quantidade_kg = dados['quantidade_sacos'] * fator_conversao
                        dados['quantidade'] = quantidade_kg
                        dados['quantidade_original_sacos'] = dados['quantidade_sacos']
                        dados['fator_conversao'] = fator_conversao
                    
                    # Validar estoque disponível
                    quantidade_final = dados.get('quantidade', 0)
                    if estoque.quantidade_atual < quantidade_final:
                        erros.append(f"Estoque insuficiente! Disponível: {estoque.quantidade_atual} {estoque.unidade_medida}")
            except Exception as e:
                erros.append(f"Erro ao buscar estoque: {str(e)}")
        
        if erros:
            return False, "; ".join(erros)
        
        return True, None
    
    def registrar_distribuicao(self, mensagem: MensagemWhatsApp, dados: Dict) -> Optional[DistribuicaoSuplementacao]:
        """
        Registra a distribuição no sistema baseado nos dados extraídos
        
        Retorna o objeto DistribuicaoSuplementacao criado ou None em caso de erro
        """
        
        if not mensagem.propriedade:
            return None
        
        try:
            # Buscar o estoque
            estoque = EstoqueSuplementacao.objects.filter(
                propriedade=mensagem.propriedade,
                tipo_suplemento__icontains=dados['tipo_suplementacao']
            ).first()
            
            if not estoque:
                raise ValueError(f"Estoque de {dados['tipo_suplementacao']} não encontrado")
            
            # Verificar estoque disponível
            if estoque.quantidade_atual < dados['quantidade']:
                raise ValueError(f"Estoque insuficiente! Disponível: {estoque.quantidade_atual} {estoque.unidade_medida}")
            
            # Organizar observações na ordem especificada
            observacoes_partes = []
            
            # 1. Tipo de suplementação
            observacoes_partes.append(f"Tipo de suplementação: {dados['tipo_suplementacao']}")
            
            # 2. Nome do produto (se informado)
            if dados.get('nome_produto'):
                observacoes_partes.append(f"Produto: {dados['nome_produto']}")
            
            # 3. Quantidade
            if dados.get('quantidade_original_sacos'):
                # Se foi informado em sacos, mostrar ambos
                observacoes_partes.append(f"Quantidade: {dados['quantidade_original_sacos']} sacos ({dados['quantidade']} {estoque.unidade_medida})")
            else:
                observacoes_partes.append(f"Quantidade: {dados['quantidade']} {estoque.unidade_medida}")
            
            # 4. Invernada
            observacoes_partes.append(f"Invernada: {dados['invernada']}")
            
            # 5. Data
            observacoes_partes.append(f"Data: {dados['data'].strftime('%d/%m/%Y')}")
            
            # 6. Observação original (se houver informações adicionais)
            texto_original = dados.get('observacoes', '')
            texto_limpo = texto_original
            
            # Remover informações já extraídas
            if dados.get('tipo_suplementacao'):
                texto_limpo = re.sub(rf'\b(?:tipo\s+(?:de\s+)?suplement(?:a|o|ação|ação)\s*:?\s*)?{dados["tipo_suplementacao"]}\b', '', texto_limpo, flags=re.IGNORECASE)
            if dados.get('nome_produto'):
                texto_limpo = re.sub(rf'\b(?:produto|nome\s+do\s+produto|marca)\s*:?\s*{dados["nome_produto"]}\b', '', texto_limpo, flags=re.IGNORECASE)
            if dados.get('quantidade'):
                texto_limpo = re.sub(rf'\b(?:quantidade\s*:?\s*)?{dados["quantidade"]}\s*(?:kg|quilos|kilos|gramas|g)\b', '', texto_limpo, flags=re.IGNORECASE)
            if dados.get('invernada'):
                texto_limpo = re.sub(rf'\b(?:invernada\s*:?\s*)?{dados["invernada"]}\b', '', texto_limpo, flags=re.IGNORECASE)
            
            # Limpar texto de palavras comuns
            texto_limpo = re.sub(r'\b(?:distribuí|distribuir|distribuindo|hoje|agora|registrar|distribuição)\b', '', texto_limpo, flags=re.IGNORECASE)
            texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
            
            # Se sobrar algo significativo, adicionar como observação
            if texto_limpo and len(texto_limpo) > 10:
                observacoes_partes.append(f"Observação: {texto_limpo}")
            
            # Juntar todas as partes
            observacoes_texto = ', '.join(observacoes_partes)
            
            # Criar registro de distribuição
            # O modelo DistribuicaoSuplementacao não tem campo propriedade diretamente,
            # ele herda através do estoque
            distribuicao = DistribuicaoSuplementacao.objects.create(
                estoque=estoque,
                data=dados['data'],
                pastagem=dados['invernada'],
                quantidade=dados['quantidade'],
                numero_animais=0,  # Pode ser informado depois
                valor_unitario=estoque.valor_unitario_medio or Decimal('0'),
                observacoes=observacoes_texto.strip(),
                responsavel=None,  # Pode ser associado ao usuário se houver autenticação
            )
            
            return distribuicao
            
        except Exception as e:
            raise ValueError(f"Erro ao registrar distribuição: {str(e)}")

