"""
VERIFICAR CARGOS E CORRIGIR COLABORADORES
=======================================

Script para criar cargos padrão e importar colaboradores
"""

import sqlite3
from datetime import datetime

DB_PATH = "C:\\GIES\\primotex_erp.db"

def verificar_e_criar_cargos():
    """Verificar tabela cargos e criar registros padrão"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar estrutura da tabela cargos
    print("📋 Estrutura da tabela CARGOS:")
    cursor.execute("PRAGMA table_info(cargos);")
    colunas = cursor.fetchall()
    for col in colunas:
        print(f"   {col[1]} ({col[2]}) - NOT NULL: {col[3]}")
    
    # Verificar se existem cargos
    cursor.execute("SELECT COUNT(*) FROM cargos;")
    total_cargos = cursor.fetchone()[0]
    print(f"\n📊 Total de cargos existentes: {total_cargos}")
    
    if total_cargos == 0:
        print("🔧 Criando cargos padrão...")
        
        cargos_padrao = [
            ("Gerente", "Gerente Geral", 8000.00, 8000.00),
            ("Supervisor", "Supervisor de Equipe", 5000.00, 6000.00),
            ("Técnico", "Técnico Especializado", 3000.00, 4500.00),
            ("Operador", "Operador de Produção", 2000.00, 3000.00),
            ("Assistente", "Assistente Administrativo", 1500.00, 2500.00),
            ("Auxiliar", "Auxiliar Geral", 1200.00, 2000.00)
        ]
        
        for nome, descricao, salario_min, salario_max in cargos_padrao:
            cursor.execute("""
                INSERT INTO cargos (nome, descricao, salario_minimo, salario_maximo, data_criacao)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, descricao, salario_min, salario_max, datetime.now().isoformat()))
            print(f"   ✅ Cargo criado: {nome}")
    
    # Listar cargos disponíveis
    cursor.execute("SELECT id, nome FROM cargos ORDER BY id;")
    cargos = cursor.fetchall()
    print(f"\n📝 Cargos disponíveis:")
    for cargo_id, nome in cargos:
        print(f"   ID {cargo_id}: {nome}")
    
    conn.commit()
    conn.close()
    
    return cargos

def main():
    print("🔍 VERIFICANDO SISTEMA DE CARGOS")
    print("=" * 40)
    
    cargos = verificar_e_criar_cargos()
    
    print(f"\n✅ Sistema verificado - {len(cargos)} cargos disponíveis")
    print("💡 Agora podemos importar colaboradores com cargo_id padrão!")

if __name__ == "__main__":
    main()