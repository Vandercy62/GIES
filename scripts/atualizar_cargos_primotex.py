"""
ATUALIZAR CARGOS PRIMOTEX
========================

Script para atualizar os cargos conforme especificação da empresa
"""

import sqlite3
from datetime import datetime

DB_PATH = "C:\\GIES\\primotex_erp.db"


def atualizar_cargos_primotex():
    """Atualizar cargos para os específicos da Primotex"""
    
    print("🔧 ATUALIZANDO CARGOS PRIMOTEX")
    print("=" * 40)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Limpar cargos existentes
        print("🗑️  Removendo cargos antigos...")
        cursor.execute("DELETE FROM cargos;")
        
        # Criar novos cargos específicos da Primotex
        print("✨ Criando cargos da Primotex...")
        
        cargos_primotex = [
            ("Gerente", "Gerente Geral da Empresa", 8000.00, 12000.00),
            ("Orçamentista", "Responsável por Orçamentos", 4000.00, 6000.00),
            ("Financeiro", "Responsável Financeiro", 3500.00, 5500.00),
            ("Montador", "Montador de Forros e Divisórias", 2500.00, 4000.00),
            ("Motorista", "Motorista para Entregas", 2200.00, 3500.00),
            ("Ajudante", "Ajudante Geral", 1500.00, 2500.00),
            ("Atendente", "Atendente ao Cliente", 1800.00, 3000.00),
            ("Proprietário", "Proprietário da Empresa", 15000.00, 30000.00)
        ]
        
        for nome, descricao, salario_min, salario_max in cargos_primotex:
            cursor.execute("""
                INSERT INTO cargos (nome, descricao, salario_minimo, salario_maximo, 
                                  ativo, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, descricao, salario_min, salario_max, True, 
                  datetime.now().isoformat()))
            
            cargo_id = cursor.lastrowid
            print(f"   ✅ ID {cargo_id}: {nome}")
        
        conn.commit()
        
        # Verificar cargos criados
        print(f"\n📝 Cargos atualizados:")
        cursor.execute("SELECT id, nome FROM cargos ORDER BY id;")
        cargos = cursor.fetchall()
        
        for cargo_id, nome in cargos:
            print(f"   ID {cargo_id}: {nome}")
        
        print(f"\n✅ Total de cargos: {len(cargos)}")
        print("🎯 Cargos da Primotex configurados com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar cargos: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def main():
    """Executar atualização"""
    sucesso = atualizar_cargos_primotex()
    
    if sucesso:
        print(f"\n🚀 SISTEMA PRONTO!")
        print("💡 Agora você pode importar colaboradores com os cargos corretos!")
    else:
        print(f"\n❌ Falha na atualização dos cargos")


if __name__ == "__main__":
    main()