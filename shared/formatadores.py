"""
SISTEMA ERP PRIMOTEX - FORMATADORES
===================================

Funções para formatação de dados brasileiros.
Inclui máscaras para CPF, CNPJ, telefone, CEP, etc.

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 100
"""

import re


def formatar_cpf(cpf: str) -> str:
    """
    Formata CPF: 123.456.789-01
    """
    numeros = re.sub(r'\D', '', cpf)
    if len(numeros) != 11:
        return cpf
    return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"


def formatar_cnpj(cnpj: str) -> str:
    """
    Formata CNPJ: 12.345.678/0001-90
    """
    numeros = re.sub(r'\D', '', cnpj)
    if len(numeros) != 14:
        return cnpj
    return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"


def formatar_telefone(telefone: str) -> str:
    """
    Formata telefone: (11) 99999-9999 ou (11) 3000-0000
    """
    numeros = re.sub(r'\D', '', telefone)

    if len(numeros) == 11:
        # Celular com 9 dígitos
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        # Fixo com 8 dígitos
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"

    return telefone


def formatar_cep(cep: str) -> str:
    """
    Formata CEP: 12345-678
    """
    numeros = re.sub(r'\D', '', cep)
    if len(numeros) != 8:
        return cep
    return f"{numeros[:5]}-{numeros[5:]}"


def formatar_moeda(valor: float) -> str:
    """
    Formata valor monetário: R$ 1.234,56
    """
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def remover_formatacao(texto: str) -> str:
    """
    Remove toda formatação, deixando apenas números
    """
    return re.sub(r'\D', '', texto)
