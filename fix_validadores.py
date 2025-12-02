#!/usr/bin/env python3
"""Corrigir strings duplicadas em validadores.py"""

from pathlib import Path

arquivo = Path('shared/validadores.py')
conteudo = arquivo.read_text(encoding='utf-8')

# Substituir CPF inválido
conteudo = conteudo.replace(
    'return False, "CPF inválido"',
    'return False, MENSAGEM_CPF_INVALIDO'
)

# Substituir CNPJ inválido
conteudo = conteudo.replace(
    'return False, "CNPJ inválido"',
    'return False, MENSAGEM_CNPJ_INVALIDO'
)

arquivo.write_text(conteudo, encoding='utf-8')
print('✅ Constantes aplicadas em validadores.py')
