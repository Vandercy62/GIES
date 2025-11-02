"""
VERIFICAR COLUNAS DO CSV COLABORADORES
=====================================

Script para verificar as colunas exatas do arquivo CSV
"""

import csv
import os

def verificar_colunas_csv():
    """Verificar colunas disponíveis no CSV"""
    
    arquivo_csv = r"C:\Users\Vanderci\OneDrive\Documentos\Banco de dados\COLABORADORES.csv"
    
    if not os.path.exists(arquivo_csv):
        print(f"❌ Arquivo não encontrado: {arquivo_csv}")
        return
    
    print("📋 COLUNAS DISPONÍVEIS NO CSV COLABORADORES:")
    print("=" * 50)
    
    with open(arquivo_csv, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        # Mostrar colunas
        colunas = reader.fieldnames
        for i, coluna in enumerate(colunas, 1):
            print(f"   {i:2d}. '{coluna}'")
        
        print(f"\n📊 Total de colunas: {len(colunas)}")
        
        # Mostrar primeira linha de dados
        primeira_linha = next(reader)
        print(f"\n📄 PRIMEIRA LINHA DE DADOS:")
        print("-" * 50)
        for coluna, valor in primeira_linha.items():
            valor_truncado = valor[:50] + "..." if len(valor) > 50 else valor
            print(f"   {coluna}: {valor_truncado}")

if __name__ == "__main__":
    verificar_colunas_csv()