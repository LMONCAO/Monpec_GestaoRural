# -*- coding: utf-8 -*-
"""
Módulo de Integração com APIs Externas
- MAPA (Ministério da Agricultura)
- Embrapa (AgroAPI)
- CNA (Confederação da Agricultura)
"""

from .api_bovtrace import BovTraceAPI
from .api_agrofit import AgrofitAPI
from .api_infodap import InfoDAPAPI

__all__ = [
    'BovTraceAPI',
    'AgrofitAPI',
    'InfoDAPAPI',
]


