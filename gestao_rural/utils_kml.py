# -*- coding: utf-8 -*-
"""
Utilitários para processamento de arquivos KML
Extrai polígonos de pastagens/piquetes do KML do Google Earth
"""

import xml.etree.ElementTree as ET
from decimal import Decimal
from typing import List, Dict, Tuple, Optional
import math


def parse_kml_file(kml_file) -> Dict:
    """
    Parse de arquivo KML e extrai informações
    
    Args:
        kml_file: Arquivo KML (file object)
    
    Returns:
        Dict com informações extraídas:
        {
            'nome': str,
            'pastagens': [
                {
                    'nome': str,
                    'coordenadas': str,  # "lat1,lon1 lat2,lon2 ..."
                    'area_ha': Decimal,
                    'descricao': str,
                }
            ]
        }
    """
    try:
        tree = ET.parse(kml_file)
        root = tree.getroot()
        
        # Namespace do KML
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        resultado = {
            'nome': '',
            'pastagens': []
        }
        
        # Extrair nome do documento/folder
        doc_name = root.find('.//kml:name', ns)
        if doc_name is not None:
            resultado['nome'] = doc_name.text or 'Fazenda'
        
        # Buscar todos os Placemarks (polígonos)
        placemarks = root.findall('.//kml:Placemark', ns)
        
        for placemark in placemarks:
            nome_elem = placemark.find('kml:name', ns)
            nome = nome_elem.text if nome_elem is not None else 'Piquete Sem Nome'
            
            # Buscar coordenadas do polígono
            coordenadas = None
            polygon = placemark.find('.//kml:Polygon', ns)
            
            if polygon is not None:
                outer_boundary = polygon.find('.//kml:outerBoundaryIs', ns)
                if outer_boundary is not None:
                    linear_ring = outer_boundary.find('.//kml:LinearRing', ns)
                    if linear_ring is not None:
                        coords_elem = linear_ring.find('kml:coordinates', ns)
                        if coords_elem is not None:
                            coordenadas = coords_elem.text.strip()
            
            # Buscar descrição
            desc_elem = placemark.find('kml:description', ns)
            descricao = desc_elem.text if desc_elem is not None else ''
            
            if coordenadas:
                # Calcular área
                area_ha = calcular_area_poligono_kml(coordenadas)
                
                resultado['pastagens'].append({
                    'nome': nome,
                    'coordenadas': coordenadas,
                    'area_ha': area_ha,
                    'descricao': descricao,
                })
        
        return resultado
    
    except Exception as e:
        raise Exception(f"Erro ao processar arquivo KML: {str(e)}")


def calcular_area_poligono_kml(coordenadas: str) -> Decimal:
    """
    Calcula área de um polígono KML em hectares
    
    Args:
        coordenadas: String com coordenadas no formato "lon1,lat1,alt1 lon2,lat2,alt2 ..."
    
    Returns:
        Área em hectares (Decimal)
    """
    try:
        # Parse das coordenadas
        pontos = []
        for coord in coordenadas.strip().split():
            partes = coord.split(',')
            if len(partes) >= 2:
                lon = float(partes[0])
                lat = float(partes[1])
                pontos.append((lat, lon))
        
        if len(pontos) < 3:
            return Decimal('0.00')
        
        # Fórmula de Shoelace para área de polígono esférico
        # Usando fórmula simplificada para pequenas áreas
        area_m2 = 0.0
        
        # Converter para radianos
        pontos_rad = []
        for lat, lon in pontos:
            pontos_rad.append((math.radians(lat), math.radians(lon)))
        
        # Fórmula de área de polígono esférico (aproximação)
        raio_terra = 6371000  # Raio da Terra em metros
        
        for i in range(len(pontos_rad)):
            j = (i + 1) % len(pontos_rad)
            lat1, lon1 = pontos_rad[i]
            lat2, lon2 = pontos_rad[j]
            
            area_m2 += (lon2 - lon1) * (
                2 + math.sin(lat1) + math.sin(lat2)
            )
        
        area_m2 = abs(area_m2) * (raio_terra ** 2) / 2
        
        # Converter para hectares
        area_ha = area_m2 / 10000
        
        return Decimal(str(round(area_ha, 4)))
    
    except Exception as e:
        print(f"Erro ao calcular área: {e}")
        return Decimal('0.00')


def extrair_coordenadas_centro(pastagem_data: Dict) -> Optional[Tuple[float, float]]:
    """
    Extrai coordenadas do centro do polígono
    
    Args:
        pastagem_data: Dict com dados da pastagem (incluindo 'coordenadas')
    
    Returns:
        Tupla (latitude, longitude) do centro ou None
    """
    try:
        coordenadas = pastagem_data.get('coordenadas', '')
        if not coordenadas:
            return None
        
        pontos = []
        for coord in coordenadas.strip().split():
            partes = coord.split(',')
            if len(partes) >= 2:
                lon = float(partes[0])
                lat = float(partes[1])
                pontos.append((lat, lon))
        
        if not pontos:
            return None
        
        # Calcular centro (média das coordenadas)
        lat_medio = sum(p[0] for p in pontos) / len(pontos)
        lon_medio = sum(p[1] for p in pontos) / len(pontos)
        
        return (lat_medio, lon_medio)
    
    except (ValueError, TypeError, IndexError, AttributeError) as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Erro ao calcular centro do polígono: {e}")
        return None


def validar_kml(kml_file) -> Tuple[bool, str]:
    """
    Valida se arquivo é um KML válido
    
    Args:
        kml_file: Arquivo KML
    
    Returns:
        Tupla (é_válido, mensagem)
    """
    try:
        tree = ET.parse(kml_file)
        root = tree.getroot()
        
        # Verificar se tem elementos KML
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        placemarks = root.findall('.//kml:Placemark', ns)
        
        if len(placemarks) == 0:
            return (False, "Arquivo KML não contém polígonos (Placemarks)")
        
        # Verificar se tem coordenadas
        tem_coordenadas = False
        for placemark in placemarks:
            polygon = placemark.find('.//kml:Polygon', ns)
            if polygon is not None:
                coords = polygon.find('.//kml:coordinates', ns)
                if coords is not None and coords.text:
                    tem_coordenadas = True
                    break
        
        if not tem_coordenadas:
            return (False, "Nenhum polígono com coordenadas encontrado")
        
        return (True, f"Arquivo válido com {len(placemarks)} polígono(s)")
    
    except ET.ParseError:
        return (False, "Arquivo não é um XML válido")
    except Exception as e:
        return (False, f"Erro ao validar arquivo: {str(e)}")


