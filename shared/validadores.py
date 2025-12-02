"""
SISTEMA ERP PRIMOTEX - VALIDADORES
==================================

Funções de validação para dados brasileiros.
Inclui validação de CPF, CNPJ, email, telefone, etc.

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 100
"""

import re
from typing import Tuple

# Constantes de mensagens de erro
MENSAGEM_CPF_INVALIDO = "CPF inválido"
MENSAGEM_CNPJ_INVALIDO = "CNPJ inválido"


def validar_cpf(cpf: str) -> Tuple[bool, str]:
    """
    Valida CPF brasileiro.

    Args:
        cpf: CPF com ou sem formatação

    Returns:
        (True/False, mensagem)
    """
    # Remove caracteres não numéricos
    cpf_numeros = re.sub(r'\D', '', cpf)

    # Verifica tamanho
    if len(cpf_numeros) != 11:
        return False, "CPF deve ter 11 dígitos"

    # Verifica se todos os dígitos são iguais
    if cpf_numeros == cpf_numeros[0] * 11:
        return False, MENSAGEM_CPF_INVALIDO

    # Calcula primeiro dígito verificador
    soma = sum(int(cpf_numeros[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cpf_numeros[9]) != digito1:
        return False, MENSAGEM_CPF_INVALIDO

    # Calcula segundo dígito verificador
    soma = sum(int(cpf_numeros[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cpf_numeros[10]) != digito2:
        return False, MENSAGEM_CPF_INVALIDO

    return True, "CPF válido"


def validar_cnpj(cnpj: str) -> Tuple[bool, str]:
    """
    Valida CNPJ brasileiro.

    Args:
        cnpj: CNPJ com ou sem formatação

    Returns:
        (True/False, mensagem)
    """
    # Remove caracteres não numéricos
    cnpj_numeros = re.sub(r'\D', '', cnpj)

    # Verifica tamanho
    if len(cnpj_numeros) != 14:
        return False, "CNPJ deve ter 14 dígitos"

    # Verifica se todos os dígitos são iguais
    if cnpj_numeros == cnpj_numeros[0] * 14:
        return False, MENSAGEM_CNPJ_INVALIDO

    # Calcula primeiro dígito verificador
    multiplicadores = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj_numeros[i]) * multiplicadores[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cnpj_numeros[12]) != digito1:
        return False, MENSAGEM_CNPJ_INVALIDO

    # Calcula segundo dígito verificador
    multiplicadores = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj_numeros[i]) * multiplicadores[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cnpj_numeros[13]) != digito2:
        return False, MENSAGEM_CNPJ_INVALIDO

    return True, "CNPJ válido"


def validar_email(email: str) -> Tuple[bool, str]:
    """
    Valida formato de email.

    Args:
        email: Email para validar

    Returns:
        (True/False, mensagem)
    """
    if not email:
        return True, ""  # Email é opcional

    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(padrao, email):
        return True, "Email válido"
    return False, "Email inválido"


def validar_telefone(telefone: str) -> Tuple[bool, str]:
    """
    Valida formato de telefone brasileiro.

    Args:
        telefone: Telefone para validar

    Returns:
        (True/False, mensagem)
    """
    if not telefone:
        return True, ""  # Telefone é opcional

    # Remove caracteres não numéricos
    numeros = re.sub(r'\D', '', telefone)

    # Verifica tamanho (10 ou 11 dígitos)
    if len(numeros) not in [10, 11]:
        return False, "Telefone deve ter 10 ou 11 dígitos"

    return True, "Telefone válido"


def validar_cep(cep: str) -> Tuple[bool, str]:
    """
    Valida formato de CEP brasileiro.

    Args:
        cep: CEP para validar

    Returns:
        (True/False, mensagem)
    """
    if not cep:
        return True, ""  # CEP é opcional

    # Remove caracteres não numéricos
    numeros = re.sub(r'\D', '', cep)

    # Verifica tamanho
    if len(numeros) != 8:
        return False, "CEP deve ter 8 dígitos"

    return True, "CEP válido"
