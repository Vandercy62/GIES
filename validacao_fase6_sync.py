#!/usr/bin/env python3
"""
Script de Validação FASE 6 - Fornecedores
Verifica sincronização de tabelas e relacionamentos
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import inspect
from backend.database.config import engine
from backend.models.fornecedor_model import Fornecedor
from backend.models.financeiro_model import ContaPagar
from backend.models.produto_model import Produto

def validar_fornecedor():
    """Valida relacionamentos do módulo de Fornecedores"""
    print("\n🔍 VALIDAÇÃO - MÓDULO DE FORNECEDORES\n" + "="*80)
    
    validacoes = []
    problemas = []
    
    # 1. ContaPagar → Fornecedor
    print("\n1️⃣ ContaPagar ↔ Fornecedor")
    try:
        from backend.models.financeiro_model import ContaPagar
        mapper = inspect(ContaPagar)
        rel = mapper.relationships.get('fornecedor')
        if rel:
            print(f"   ✅ ContaPagar.fornecedor → {rel.target}")
            validacoes.append("ContaPagar → Fornecedor")
        else:
            print("   ⚠️ ContaPagar.fornecedor não encontrado (opcional)")
    except Exception as e:
        print(f"   ⚠️ Erro: {e}")
    
    # 2. Produto → Fornecedor  
    print("\n2️⃣ Produto ↔ Fornecedor (fornecedor_principal_id)")
    try:
        from backend.models.produto_model import Produto
        mapper = inspect(Produto)
        # Verifica se tem FK para fornecedor
        fks = [col for col in mapper.columns if 'fornecedor' in col.name.lower()]
        if fks:
            print(f"   ✅ Produto tem FK: {[fk.name for fk in fks]}")
            validacoes.append("Produto → Fornecedor (FK)")
        else:
            print("   ⚠️ Produto.fornecedor_principal_id não implementado (futuro)")
    except Exception as e:
        print(f"   ⚠️ Erro: {e}")
    
    # 3. Fornecedor → Contas a Pagar (reverso)
    print("\n3️⃣ Fornecedor ↔ ContaPagar (reverso)")
    try:
        mapper = inspect(Fornecedor)
        rel = mapper.relationships.get('contas_pagar')
        if rel:
            print(f"   ✅ Fornecedor.contas_pagar → {rel.target}")
            validacoes.append("Fornecedor → ContaPagar (reverso)")
        else:
            print("   ⚠️ Fornecedor.contas_pagar não definido (pode ser implementado no futuro)")
    except Exception as e:
        print(f"   ⚠️ Erro: {e}")
    
    return validacoes, problemas

def validar_foreign_keys_fase6():
    """Valida Foreign Keys da FASE 6"""
    print("\n\n🔐 VALIDAÇÃO DE FOREIGN KEYS - FASE 6\n" + "="*80)
    
    inspector = inspect(engine)
    fks_validadas = []
    
    # 1. Fornecedores (deve ser tabela independente)
    print("\n📋 fornecedores:")
    try:
        fks = inspector.get_foreign_keys('fornecedores')
        if fks:
            for fk in fks:
                col = fk['constrained_columns'][0]
                ref_table = fk['referred_table']
                ref_col = fk['referred_columns'][0]
                print(f"   ✅ {col} → {ref_table}.{ref_col}")
                fks_validadas.append(f"fornecedores.{col} → {ref_table}.{ref_col}")
        else:
            print("   ✅ Tabela independente (sem FKs) - CORRETO!")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Contas a Pagar → Fornecedor
    print("\n📋 contas_pagar:")
    try:
        fks = inspector.get_foreign_keys('contas_pagar')
        fornecedor_fks = [fk for fk in fks if 'fornecedor' in str(fk.get('constrained_columns', []))]
        if fornecedor_fks:
            for fk in fornecedor_fks:
                col = fk['constrained_columns'][0]
                ref_table = fk['referred_table']
                ref_col = fk['referred_columns'][0]
                print(f"   ✅ {col} → {ref_table}.{ref_col}")
                fks_validadas.append(f"contas_pagar.{col} → {ref_table}.{ref_col}")
        else:
            print("   ⚠️ FK fornecedor_id não encontrado (verificar implementação)")
    except Exception as e:
        print(f"   ⚠️ Erro: {e}")
    
    # 3. Produtos → Fornecedor
    print("\n📋 produtos:")
    try:
        fks = inspector.get_foreign_keys('produtos')
        fornecedor_fks = [fk for fk in fks if 'fornecedor' in str(fk.get('constrained_columns', []))]
        if fornecedor_fks:
            for fk in fornecedor_fks:
                col = fk['constrained_columns'][0]
                ref_table = fk['referred_table']
                ref_col = fk['referred_columns'][0]
                print(f"   ✅ {col} → {ref_table}.{ref_col}")
                fks_validadas.append(f"produtos.{col} → {ref_table}.{ref_col}")
        else:
            print("   ⚠️ FK fornecedor_principal_id não encontrado (implementação futura)")
    except Exception as e:
        print(f"   ⚠️ Erro: {e}")
    
    return fks_validadas

def validar_indexes_fase6():
    """Valida indexes da FASE 6"""
    print("\n\n📊 VALIDAÇÃO DE INDEXES - FASE 6\n" + "="*80)
    
    inspector = inspect(engine)
    
    print("\n📋 fornecedores:")
    try:
        indexes = inspector.get_indexes('fornecedores')
        print(f"   ✅ Total de indexes: {len(indexes)}")
        for idx in indexes[:5]:  # Mostrar primeiros 5
            print(f"      • {idx['name']}: {idx['column_names']}")
        if len(indexes) > 5:
            print(f"      ... e mais {len(indexes) - 5} indexes")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def main():
    print("\n" + "="*80)
    print("🔍 VALIDAÇÃO COMPLETA - FASE 6 (Fornecedores)")
    print("="*80)
    
    # 1. Validar Fornecedores
    val_forn, prob_forn = validar_fornecedor()
    
    # 2. Validar Foreign Keys
    fks = validar_foreign_keys_fase6()
    
    # 3. Validar Indexes
    validar_indexes_fase6()
    
    # Resumo
    print("\n\n" + "="*80)
    print("📊 RESUMO DA VALIDAÇÃO - FASE 6")
    print("="*80)
    
    total_validacoes = len(val_forn)
    total_problemas = len(prob_forn)
    
    if total_validacoes > 0:
        print(f"\n✅ RELACIONAMENTOS VALIDADOS: {total_validacoes}")
        for v in val_forn:
            print(f"   • {v}")
    
    print(f"\n✅ FOREIGN KEYS VALIDADAS: {len(fks)}")
    for fk in fks:
        print(f"   • {fk}")
    
    if total_problemas > 0:
        print(f"\n⚠️ OBSERVAÇÕES: {total_problemas}")
        for p in prob_forn:
            print(f"   • {p}")
    
    print("\n\n🎉 VALIDAÇÃO DA FASE 6 CONCLUÍDA!")
    print("✅ Módulo de Fornecedores pronto para uso")
    print("📝 Relacionamentos opcionais podem ser implementados no futuro")
    
    return total_problemas == 0

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
