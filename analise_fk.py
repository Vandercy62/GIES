#!/usr/bin/env python3
"""
ANÁLISE ESTRUTURA BANCO - Verifica FK entre tabelas
"""

import sqlite3

def main():
    print("🔍 ANALISANDO ESTRUTURA DO BANCO")
    print("=" * 50)
    
    conn = sqlite3.connect('primotex_erp.db')
    cursor = conn.cursor()
    
    # Schema da tabela departamentos
    print("\n📋 TABELA DEPARTAMENTOS:")
    cursor.execute("PRAGMA table_info(departamentos)")
    for row in cursor.fetchall():
        print(f"  {row}")
    
    # Schema da tabela colaboradores  
    print("\n👥 TABELA COLABORADORES:")
    cursor.execute("PRAGMA table_info(colaboradores)")
    for row in cursor.fetchall():
        print(f"  {row}")
    
    # FK constraints
    print("\n🔗 FOREIGN KEYS DEPARTAMENTOS:")
    cursor.execute("PRAGMA foreign_key_list(departamentos)")
    for row in cursor.fetchall():
        print(f"  {row}")
        
    print("\n🔗 FOREIGN KEYS COLABORADORES:")
    cursor.execute("PRAGMA foreign_key_list(colaboradores)")
    for row in cursor.fetchall():
        print(f"  {row}")
    
    conn.close()

if __name__ == "__main__":
    main()