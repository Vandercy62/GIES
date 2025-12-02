"""
SISTEMA ERP PRIMOTEX - COMPONENTES DO WIZARD DE COLABORADORES
=============================================================

Módulo contendo os componentes (abas) do wizard de colaboradores.

COMPONENTES:
- aba_lista.py - Lista de colaboradores com busca
- aba_dados_pessoais.py - Dados pessoais (CPF, RG, endereço, foto)
- aba_dados_profissionais.py - Cargo, salário, contrato
- aba_documentos.py - Documentos com sistema de alertas ⭐⭐⭐
- aba_observacoes.py - Observações, férias, avaliações

Autor: GitHub Copilot
Data: 17/11/2025 - FASE 103
"""

from .aba_lista import AbaLista
from .aba_dados_pessoais import AbaDadosPessoais
from .aba_dados_profissionais import AbaDadosProfissionais
from .aba_documentos import AbaDocumentos
from .aba_observacoes import AbaObservacoes

__all__ = [
    'AbaLista',
    'AbaDadosPessoais',
    'AbaDadosProfissionais',
    'AbaDocumentos',
    'AbaObservacoes'
]
