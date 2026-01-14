# -*- coding: utf-8 -*-
"""
Módulo de Integração com APIs Externas
- MAPA (Ministério da Agricultura)
- Embrapa (AgroAPI)
- CNA (Confederação da Agricultura)
- IMEA (Instituto Mato-grossense de Economia Agropecuária)
- Scot Consultoria
"""

from .api_bovtrace import BovTraceAPI
from .api_agrofit import AgrofitAPI
from .api_infodap import InfoDAPAPI
from .api_cepea import CEPEAService
from .api_imea import IMEAService
from .api_scot_consultoria import ScotConsultoriaService

__all__ = [
    'BovTraceAPI',
    'AgrofitAPI',
    'InfoDAPAPI',
    'CEPEAService',
    'IMEAService',
    'ScotConsultoriaService',
]


