#!/usr/bin/env python3
"""
Conversão automática de Pydantic v2 para v1
"""

import os
import re

def converter_arquivo(caminho_arquivo):
    """Converte um arquivo de Pydantic v2 para v1"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        conteudo_original = conteudo
        
        # Substituições necessárias
        conversoes = [
            # Imports
            (r'from pydantic import.*field_validator.*model_validator.*', 
             'from pydantic import BaseModel, Field, validator'),
            
            # field_validator para validator
            (r'@field_validator\((.*?)\)', r'@validator(\1)'),
            
            # model_validator para root_validator  
            (r'@model_validator\(mode=[\'"]before[\'"]?\)', '@root_validator(pre=True)'),
            (r'@model_validator\(mode=[\'"]after[\'"]?\)', '@root_validator(pre=False)'),
            (r'@model_validator\((.*?)\)', r'@root_validator(\1)'),
            
            # Função cls parameter
            (r'def (.*?)\(cls, v\):', r'def \1(cls, v):'),
            (r'def (.*?)\(cls, values\):', r'def \1(cls, values):'),
        ]
        
        for padrao, substituicao in conversoes:
            conteudo = re.sub(padrao, substituicao, conteudo, flags=re.MULTILINE)
        
        # Salvar apenas se houve mudanças
        if conteudo != conteudo_original:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print(f"✅ Convertido: {caminho_arquivo}")
            return True
        else:
            print(f"⏭️ Inalterado: {caminho_arquivo}")
            return False
            
    except Exception as e:
        print(f"❌ Erro em {caminho_arquivo}: {e}")
        return False

def main():
    """Converte todos os arquivos schemas"""
    print("🔄 CONVERSÃO PYDANTIC v2 → v1")
    print("=" * 40)
    
    # Arquivos a converter
    arquivos = [
        'backend/schemas/ordem_servico_schemas.py',
        'backend/schemas/financeiro_schemas.py', 
        'backend/schemas/agendamento_schemas.py'
    ]
    
    convertidos = 0
    
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            if converter_arquivo(arquivo):
                convertidos += 1
        else:
            print(f"⚠️ Não encontrado: {arquivo}")
    
    print("=" * 40)
    print(f"✅ Convertidos: {convertidos} arquivos")
    print("🎯 Execute agora: python configurador_rede.py")
    
if __name__ == "__main__":
    main()