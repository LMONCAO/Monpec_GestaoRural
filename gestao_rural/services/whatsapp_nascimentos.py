# -*- coding: utf-8 -*-
"""
Serviço para processar mensagens de áudio do WhatsApp e extrair informações
sobre nascimentos de bezerros
"""

import re
from datetime import datetime, date, time
from typing import Dict, Optional, Tuple
from decimal import Decimal, InvalidOperation

from django.utils import timezone
from gestao_rural.models import MensagemWhatsApp, Propriedade, AnimalIndividual
from gestao_rural.models_reproducao import Nascimento


class ProcessadorAudioNascimento:
    """Processa áudio transcrito e extrai informações estruturadas sobre nascimento"""
    
    def __init__(self):
        self.padroes = {
            'brinco_mae': [
                r'brinco\s+(?:da\s+)?(?:mãe|mae|vaca)\s*:?\s*(\d+)',
                r'mãe\s+(?:com\s+)?brinco\s*:?\s*(\d+)',
                r'vaca\s+(?:número|num|#)\s*:?\s*(\d+)',
                r'brinco\s*:?\s*(\d{4,})',  # Brinco genérico (4+ dígitos)
            ],
            'brinco_bezerro': [
                r'brinco\s+(?:do\s+)?(?:bezerro|bezerra|bezerr[oa])\s*:?\s*(\d+)',
                r'bezerro\s+(?:número|num|#)\s*:?\s*(\d+)',
                r'novo\s+brinco\s*:?\s*(\d+)',
                r'identificar\s+(?:com\s+)?brinco\s*:?\s*(\d+)',
            ],
            'sexo': [
                r'(?:sexo|é|eh)\s*(?:um|uma)?\s*(macho|fêmea|femea|m|f)',
                r'(macho|fêmea|femea)',
                r'é\s+(?:um|uma)\s*(macho|fêmea|femea)',
            ],
            'peso': [
                r'peso\s*:?\s*(\d+[.,]?\d*)\s*(?:kg|quilos|kilos)',
                r'(\d+[.,]?\d*)\s*(?:kg|quilos|kilos)',
                r'pesou\s+(\d+[.,]?\d*)',
            ],
            'data': [
                r'nasceu\s+(?:em|no|dia|hoje|ontem)?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
                r'data\s*:?\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
            ],
            'hora': [
                r'às?\s*(\d{1,2})[:h](\d{2})',
                r'hora\s*:?\s*(\d{1,2})[:h](\d{2})',
            ],
            'tipo_parto': [
                r'(?:parto|nascimento)\s+(normal|cesárea|cesarea|cesariana|difícil|dificil)',
                r'(normal|cesárea|cesarea|cesariana|difícil|dificil)',
            ],
            'raca': [
                r'raça\s*:?\s*([a-záàâãéêíóôõúç\s]+)',
                r'raça\s+([a-záàâãéêíóôõúç\s]+)',
                r'(?:é|eh)\s+(?:da\s+)?raça\s+([a-záàâãéêíóôõúç\s]+)',
                r'(nelore|angus|hereford|brahman|simental|gir|guzerá|guzera|canchim|senepol|brangus|tabapuã|tabapua)',
            ],
            'cor': [
                r'cor\s*:?\s*([a-záàâãéêíóôõúç\s]+)',
                r'cor\s+([a-záàâãéêíóôõúç\s]+)',
                r'(?:é|eh)\s+(?:de\s+)?cor\s+([a-záàâãéêíóôõúç\s]+)',
                r'(branco|preto|vermelho|amarelo|marrom|cinza|pardo|amarelado|vermelhado)',
            ],
            'invernada': [
                r'invernada\s*:?\s*([a-záàâãéêíóôõúç\d\s]+)',
                r'invernada\s+([a-záàâãéêíóôõúç\d\s]+)',
                r'(?:na|da)\s+invernada\s+([a-záàâãéêíóôõúç\d\s]+)',
                r'pasto\s+([a-záàâãéêíóôõúç\d\s]+)',
            ],
        }
    
    def processar_texto(self, texto: str) -> Dict:
        """
        Processa texto transcrito e extrai informações estruturadas
        
        Retorna dicionário com:
        - brinco_mae: número do brinco da mãe
        - brinco_bezerro: número do brinco do bezerro
        - sexo: 'M' ou 'F'
        - peso: Decimal
        - data_nascimento: date
        - hora_nascimento: time (opcional)
        - tipo_parto: str
        - observacoes: str
        """
        texto_lower = texto.lower()
        dados = {
            'brinco_mae': None,
            'brinco_bezerro': None,
            'sexo': None,
            'peso': None,
            'data_nascimento': None,
            'hora_nascimento': None,
            'tipo_parto': 'NORMAL',
            'raca': None,
            'cor': None,
            'invernada': None,
            'observacoes': texto,
        }
        
        # Extrair brinco da mãe
        for padrao in self.padroes['brinco_mae']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                dados['brinco_mae'] = match.group(1).strip()
                break
        
        # Extrair brinco do bezerro
        for padrao in self.padroes['brinco_bezerro']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                dados['brinco_bezerro'] = match.group(1).strip()
                break
        
        # Extrair sexo
        for padrao in self.padroes['sexo']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                sexo_texto = match.group(1).lower()
                if sexo_texto in ['m', 'macho']:
                    dados['sexo'] = 'M'
                elif sexo_texto in ['f', 'fêmea', 'femea']:
                    dados['sexo'] = 'F'
                if dados['sexo']:
                    break
        
        # Extrair peso
        for padrao in self.padroes['peso']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                peso_str = match.group(1).replace(',', '.')
                try:
                    dados['peso'] = Decimal(peso_str)
                except (InvalidOperation, ValueError):
                    pass
                if dados['peso']:
                    break
        
        # Extrair data
        hoje = date.today()
        for padrao in self.padroes['data']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                try:
                    dia = int(match.group(1))
                    mes = int(match.group(2))
                    ano_str = match.group(3)
                    if len(ano_str) == 2:
                        ano = 2000 + int(ano_str)
                    else:
                        ano = int(ano_str)
                    dados['data_nascimento'] = date(ano, mes, dia)
                except (ValueError, IndexError):
                    pass
                if dados['data_nascimento']:
                    break
        
        # Se não encontrou data, assume hoje
        if not dados['data_nascimento']:
            if 'hoje' in texto_lower:
                dados['data_nascimento'] = hoje
            elif 'ontem' in texto_lower:
                from datetime import timedelta
                dados['data_nascimento'] = hoje - timedelta(days=1)
            else:
                dados['data_nascimento'] = hoje
        
        # Extrair hora (se não informada, usa hora atual automaticamente)
        hora_encontrada = False
        for padrao in self.padroes['hora']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                try:
                    hora = int(match.group(1))
                    minuto = int(match.group(2))
                    dados['hora_nascimento'] = time(hora, minuto)
                    hora_encontrada = True
                except (ValueError, IndexError):
                    pass
                if dados['hora_nascimento']:
                    break
        
        # Se não encontrou hora, usa hora atual automaticamente
        if not hora_encontrada:
            from datetime import datetime
            agora = datetime.now()
            dados['hora_nascimento'] = agora.time().replace(second=0, microsecond=0)
        
        # Extrair tipo de parto
        for padrao in self.padroes['tipo_parto']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                tipo_texto = match.group(1).lower()
                if 'cesar' in tipo_texto:
                    dados['tipo_parto'] = 'CESAREA'
                elif 'dificil' in tipo_texto or 'difícil' in tipo_texto:
                    dados['tipo_parto'] = 'DIFICIL'
                else:
                    dados['tipo_parto'] = 'NORMAL'
                break
        
        # Extrair raça
        for padrao in self.padroes['raca']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                raca_texto = match.group(1).strip()
                # Normalizar raça
                raca_texto = raca_texto.lower()
                if 'nelore' in raca_texto:
                    dados['raca'] = 'Nelore'
                elif 'angus' in raca_texto:
                    dados['raca'] = 'Angus'
                elif 'hereford' in raca_texto:
                    dados['raca'] = 'Hereford'
                elif 'brahman' in raca_texto:
                    dados['raca'] = 'Brahman'
                elif 'simental' in raca_texto:
                    dados['raca'] = 'Simental'
                elif 'gir' in raca_texto:
                    dados['raca'] = 'Gir'
                elif 'guzer' in raca_texto:
                    dados['raca'] = 'Guzerá'
                elif 'canchim' in raca_texto:
                    dados['raca'] = 'Canchim'
                elif 'senepol' in raca_texto:
                    dados['raca'] = 'Senepol'
                elif 'brangus' in raca_texto:
                    dados['raca'] = 'Brangus'
                elif 'tabapu' in raca_texto:
                    dados['raca'] = 'Tabapuã'
                else:
                    dados['raca'] = raca_texto.title()  # Capitalizar primeira letra
                break
        
        # Extrair cor
        for padrao in self.padroes['cor']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                cor_texto = match.group(1).strip()
                dados['cor'] = cor_texto.title()  # Capitalizar primeira letra
                break
        
        # Extrair invernada
        for padrao in self.padroes['invernada']:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                invernada_texto = match.group(1).strip()
                dados['invernada'] = invernada_texto.title()  # Capitalizar primeira letra
                break
        
        return dados
    
    def validar_dados(self, dados: Dict, propriedade) -> Tuple[bool, Optional[str]]:
        """Valida se os dados extraídos são suficientes para registrar nascimento"""
        erros = []
        
        if not dados.get('brinco_mae'):
            erros.append("Brinco da mãe não identificado")
        
        if not dados.get('sexo'):
            erros.append("Sexo do bezerro não identificado")
        
        if not dados.get('data_nascimento'):
            erros.append("Data de nascimento não identificada")
        
        # Verificar se a mãe existe
        if dados.get('brinco_mae') and propriedade:
            try:
                mae = AnimalIndividual.objects.filter(
                    propriedade=propriedade,
                    numero_brinco=dados['brinco_mae']
                ).first()
                if not mae:
                    erros.append(f"Vaca com brinco {dados['brinco_mae']} não encontrada na propriedade")
            except Exception as e:
                erros.append(f"Erro ao buscar mãe: {str(e)}")
        
        if erros:
            return False, "; ".join(erros)
        
        return True, None
    
    def registrar_nascimento(self, mensagem: MensagemWhatsApp, dados: Dict) -> Optional[Nascimento]:
        """
        Registra o nascimento no sistema baseado nos dados extraídos
        
        Retorna o objeto Nascimento criado ou None em caso de erro
        """
        
        if not mensagem.propriedade:
            return None
        
        try:
            # Buscar a mãe
            mae = AnimalIndividual.objects.filter(
                propriedade=mensagem.propriedade,
                numero_brinco=dados['brinco_mae']
            ).first()
            
            if not mae:
                raise ValueError(f"Vaca com brinco {dados['brinco_mae']} não encontrada")
            
            # Criar registro de nascimento
            # Organizar observações na ordem especificada
            observacoes_partes = []
            
            # 1. Brinco do bezerro
            if dados.get('brinco_bezerro'):
                observacoes_partes.append(f"Brinco do bezerro: {dados['brinco_bezerro']}")
            
            # 2. Brinco da mãe
            if dados.get('brinco_mae'):
                observacoes_partes.append(f"Brinco da mãe: {dados['brinco_mae']}")
            
            # 3. Sexo
            if dados.get('sexo'):
                sexo_display = 'Macho' if dados['sexo'] == 'M' else 'Fêmea'
                observacoes_partes.append(f"Sexo: {sexo_display}")
            
            # 4. Raça
            if dados.get('raca'):
                observacoes_partes.append(f"Raça: {dados['raca']}")
            
            # 5. Cor
            if dados.get('cor'):
                observacoes_partes.append(f"Cor: {dados['cor']}")
            
            # 6. Peso
            if dados.get('peso'):
                observacoes_partes.append(f"Peso: {dados['peso']} kg")
            
            # 7. Invernada
            if dados.get('invernada'):
                observacoes_partes.append(f"Invernada: {dados['invernada']}")
            
            # 8. Hora (sempre mostrar, automática se não informada)
            hora_para_obs = dados.get('hora_nascimento')
            if not hora_para_obs:
                # Se não foi informada, usar hora atual
                from datetime import datetime
                hora_para_obs = datetime.now().time().replace(second=0, microsecond=0)
                # Atualizar dados para usar hora atual
                dados['hora_nascimento'] = hora_para_obs
                observacoes_partes.append(f"Hora: {hora_para_obs.strftime('%H:%M')} (Automática)")
            else:
                observacoes_partes.append(f"Hora: {hora_para_obs.strftime('%H:%M')}")
            
            # 9. Observação original (se houver informações adicionais no texto)
            texto_original = dados.get('observacoes', '')
            # Remover informações já extraídas do texto original para evitar duplicação
            texto_limpo = texto_original
            if dados.get('brinco_bezerro'):
                texto_limpo = re.sub(rf'\b(?:brinco\s+(?:do\s+)?(?:bezerro|bezerra|bezerr[oa])\s*:?\s*)?{dados["brinco_bezerro"]}\b', '', texto_limpo, flags=re.IGNORECASE)
            if dados.get('brinco_mae'):
                texto_limpo = re.sub(rf'\b(?:brinco\s+(?:da\s+)?(?:mãe|mae|vaca)\s*:?\s*)?{dados["brinco_mae"]}\b', '', texto_limpo, flags=re.IGNORECASE)
            if dados.get('sexo'):
                texto_limpo = re.sub(r'\b(?:sexo|é|eh)\s*(?:um|uma)?\s*(?:macho|fêmea|femea|m|f)\b', '', texto_limpo, flags=re.IGNORECASE)
            if dados.get('peso'):
                texto_limpo = re.sub(rf'\b(?:peso\s*:?\s*)?{dados["peso"]}\s*(?:kg|quilos|kilos)\b', '', texto_limpo, flags=re.IGNORECASE)
            if dados.get('raca'):
                texto_limpo = re.sub(rf'\b(?:raça\s*:?\s*)?{dados["raca"]}\b', '', texto_limpo, flags=re.IGNORECASE)
            if dados.get('cor'):
                texto_limpo = re.sub(rf'\b(?:cor\s*:?\s*)?{dados["cor"]}\b', '', texto_limpo, flags=re.IGNORECASE)
            if dados.get('invernada'):
                texto_limpo = re.sub(rf'\b(?:invernada\s*:?\s*)?{dados["invernada"]}\b', '', texto_limpo, flags=re.IGNORECASE)
            
            # Limpar texto de palavras comuns e espaços extras
            texto_limpo = re.sub(r'\b(?:olá|acabei|registrar|nascimento|vaca|teve|bezerro|nasceu|hoje|ontem|dia|parto|normal|cesariana|difícil|dificil)\b', '', texto_limpo, flags=re.IGNORECASE)
            texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
            
            # Se sobrar algo significativo no texto, adicionar como observação
            if texto_limpo and len(texto_limpo) > 10:
                observacoes_partes.append(f"Observação: {texto_limpo}")
            
            # Juntar todas as partes
            observacoes_texto = ', '.join(observacoes_partes)
            
            nascimento = Nascimento.objects.create(
                propriedade=mensagem.propriedade,
                mae=mae,
                data_nascimento=dados['data_nascimento'],
                hora_nascimento=dados.get('hora_nascimento'),  # Já vem com hora atual se não informada
                tipo_parto=dados.get('tipo_parto', 'NORMAL'),
                numero_brinco_bezerro=dados.get('brinco_bezerro'),
                sexo=dados['sexo'],
                peso_nascimento=dados.get('peso'),
                observacoes=observacoes_texto.strip(),
                responsavel=None,  # Pode ser associado ao usuário se houver autenticação
            )
            
            # Se houver brinco do bezerro, criar ou atualizar AnimalIndividual
            if dados.get('brinco_bezerro'):
                from gestao_rural.models import CategoriaAnimal
                
                # Determinar categoria baseada no sexo
                if dados['sexo'] == 'M':
                    categoria_nome = 'Bezerros (0-12m)'
                else:
                    categoria_nome = 'Bezerras (0-12m)'
                
                try:
                    categoria = CategoriaAnimal.objects.get(nome=categoria_nome)
                except CategoriaAnimal.DoesNotExist:
                    # Usar primeira categoria disponível se não encontrar
                    categoria = CategoriaAnimal.objects.filter(
                        propriedade=mensagem.propriedade
                    ).first()
                
                if categoria:
                    # Criar ou atualizar animal individual
                    animal_bezerro, created = AnimalIndividual.objects.get_or_create(
                        numero_brinco=dados['brinco_bezerro'],
                        defaults={
                            'propriedade': mensagem.propriedade,
                            'categoria': categoria,
                            'sexo': dados['sexo'],
                            'data_nascimento': dados['data_nascimento'],
                            'raca': dados.get('raca'),
                            'mae': mae,
                            'status': 'ATIVO',
                            'tipo_origem': 'NASCIMENTO',
                        }
                    )
                    
                    # Atualizar campos se animal já existia
                    if not created:
                        animal_bezerro.raca = dados.get('raca') or animal_bezerro.raca
                        animal_bezerro.data_nascimento = dados['data_nascimento']
                        animal_bezerro.mae = mae
                        animal_bezerro.peso_atual_kg = dados.get('peso')
                        if dados.get('cor'):
                            # Adicionar cor nas observações se não houver campo específico
                            obs_atual = animal_bezerro.observacoes or ''
                            if 'Cor:' not in obs_atual:
                                animal_bezerro.observacoes = f"{obs_atual}\nCor: {dados['cor']}".strip()
                        if dados.get('invernada'):
                            obs_atual = animal_bezerro.observacoes or ''
                            if 'Invernada:' not in obs_atual:
                                animal_bezerro.observacoes = f"{obs_atual}\nInvernada: {dados['invernada']}".strip()
                        animal_bezerro.save()
                    
                    # Associar animal ao nascimento
                    nascimento.animal_individual = animal_bezerro
                    nascimento.save()
            
            return nascimento
            
        except Exception as e:
            raise ValueError(f"Erro ao registrar nascimento: {str(e)}")

