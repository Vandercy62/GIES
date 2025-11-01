#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRAÇÃO CORRETIVA - CAMPOS ATIVO
==================================

Adiciona o campo 'ativo' aos modelos financeiros
que estavam sendo usados no código mas não existiam.

Data: 01/11/2025
Status: Correção Crítica
"""

from sqlalchemy import text
from backend.database.config import SessionLocal


def aplicar_correcoes_banco():
    """Aplicar correções no banco de dados"""
    db = SessionLocal()
    
    try:
        print("🔧 APLICANDO CORREÇÕES NO BANCO DE DADOS")
        print("=" * 60)
        
        # 1. Adicionar campo 'ativo' em contas_receber
        print("\n📋 Adicionando campo 'ativo' em contas_receber...")
        try:
            db.execute(text("""
                ALTER TABLE contas_receber 
                ADD COLUMN ativo BOOLEAN DEFAULT TRUE NOT NULL
            """))
            print("✅ Campo 'ativo' adicionado em contas_receber")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️ Campo 'ativo' já existe em contas_receber")
            else:
                print(f"❌ Erro ao adicionar 'ativo' em contas_receber: {e}")
        
        # 2. Adicionar campo 'ativo' em contas_pagar
        print("\n📋 Adicionando campo 'ativo' em contas_pagar...")
        try:
            db.execute(text("""
                ALTER TABLE contas_pagar 
                ADD COLUMN ativo BOOLEAN DEFAULT TRUE NOT NULL
            """))
            print("✅ Campo 'ativo' adicionado em contas_pagar")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️ Campo 'ativo' já existe em contas_pagar")
            else:
                print(f"❌ Erro ao adicionar 'ativo' em contas_pagar: {e}")
        
        # 3. Renomear 'ativa' para 'ativo' em categorias_financeiras
        print("\n📋 Corrigindo campo 'ativa' -> 'ativo' em categorias_financeiras...")
        try:
            # Verificar se existe o campo 'ativa'
            result = db.execute(text("""
                PRAGMA table_info(categorias_financeiras)
            """)).fetchall()
            
            columns = [row[1] for row in result]
            
            if 'ativa' in columns and 'ativo' not in columns:
                # Renomear coluna
                db.execute(text("""
                    ALTER TABLE categorias_financeiras 
                    RENAME COLUMN ativa TO ativo
                """))
                print("✅ Campo 'ativa' renomeado para 'ativo' em categorias_financeiras")
            elif 'ativo' in columns:
                print("ℹ️ Campo 'ativo' já existe em categorias_financeiras")
            else:
                # Adicionar campo
                db.execute(text("""
                    ALTER TABLE categorias_financeiras 
                    ADD COLUMN ativo BOOLEAN DEFAULT TRUE NOT NULL
                """))
                print("✅ Campo 'ativo' adicionado em categorias_financeiras")
        
        except Exception as e:
            print(f"❌ Erro ao corrigir campo em categorias_financeiras: {e}")
        
        # 4. Atualizar todos os registros existentes para ativo=TRUE
        print("\n📋 Atualizando registros existentes...")
        try:
            # Contas receber
            result = db.execute(text("""
                UPDATE contas_receber SET ativo = TRUE WHERE ativo IS NULL
            """))
            print(f"✅ {result.rowcount} registros atualizados em contas_receber")
            
            # Contas pagar
            result = db.execute(text("""
                UPDATE contas_pagar SET ativo = TRUE WHERE ativo IS NULL
            """))
            print(f"✅ {result.rowcount} registros atualizados em contas_pagar")
            
            # Categorias
            result = db.execute(text("""
                UPDATE categorias_financeiras SET ativo = TRUE WHERE ativo IS NULL
            """))
            print(f"✅ {result.rowcount} registros atualizados em categorias_financeiras")
            
        except Exception as e:
            print(f"⚠️ Erro ao atualizar registros: {e}")
        
        # Fazer commit das alterações
        db.commit()
        
        print(f"\n🎉 CORREÇÕES APLICADAS COM SUCESSO!")
        print(f"✅ Banco de dados atualizado")
        
    except Exception as e:
        print(f"❌ Erro geral na migração: {e}")
        db.rollback()
        
    finally:
        db.close()


def verificar_correcoes():
    """Verificar se as correções foram aplicadas"""
    db = SessionLocal()
    
    try:
        print(f"\n🔍 VERIFICANDO CORREÇÕES APLICADAS")
        print("=" * 50)
        
        # Verificar estrutura das tabelas
        tabelas = ["contas_receber", "contas_pagar", "categorias_financeiras"]
        
        for tabela in tabelas:
            print(f"\n📋 Estrutura da tabela {tabela}:")
            
            result = db.execute(text(f"""
                PRAGMA table_info({tabela})
            """)).fetchall()
            
            columns = [row[1] for row in result]
            
            if 'ativo' in columns:
                print(f"   ✅ Campo 'ativo' encontrado")
                
                # Contar registros ativos
                count_result = db.execute(text(f"""
                    SELECT COUNT(*) FROM {tabela} WHERE ativo = TRUE
                """)).scalar()
                
                print(f"   📊 {count_result} registros ativos")
            else:
                print(f"   ❌ Campo 'ativo' NÃO encontrado")
        
        print(f"\n✅ VERIFICAÇÃO CONCLUÍDA")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("🔧 MIGRAÇÃO CORRETIVA - CAMPOS ATIVO")
    print("🎯 Corrigindo modelos financeiros")
    print("=" * 70)
    
    aplicar_correcoes_banco()
    verificar_correcoes()
    
    print("\n" + "=" * 70)
    print("✅ MIGRAÇÃO CONCLUÍDA")
    print("=" * 70)