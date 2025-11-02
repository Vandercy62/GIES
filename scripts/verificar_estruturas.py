"""
VERIFICADOR DE ESTRUTURAS DE TABELAS
====================================

Script para verificar as colunas existentes nas tabelas do banco
e ajustar o importador conforme necessário.
"""

import sqlite3

DB_PATH = "C:\\GIES\\primotex_erp.db"

def verificar_estruturas():
    """Verificar estruturas das tabelas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tabelas = ['fornecedores', 'colaboradores', 'produtos']
    
    print("🔍 VERIFICANDO ESTRUTURAS DAS TABELAS")
    print("=" * 50)
    
    for tabela in tabelas:
        try:
            cursor.execute(f"PRAGMA table_info({tabela})")
            colunas = cursor.fetchall()
            
            print(f"\n📊 Tabela: {tabela}")
            print("-" * 30)
            
            if colunas:
                for coluna in colunas:
                    nome = coluna[1]
                    tipo = coluna[2]
                    print(f"   {nome} ({tipo})")
            else:
                print(f"   ❌ Tabela {tabela} não existe!")
                
        except Exception as e:
            print(f"   ❌ Erro ao verificar {tabela}: {e}")
    
    conn.close()

if __name__ == "__main__":
    verificar_estruturas()