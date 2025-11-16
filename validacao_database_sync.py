#!/usr/bin/env python3
"""
Script de Validação de Sincronização de Tabelas - FASE 1-4
Verifica integridade referencial e relacionamentos entre todas as tabelas
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import inspect, MetaData
from sqlalchemy.orm import Session
from backend.database.config import engine, Base
from backend.models.cliente_model import Cliente
from backend.models.produto_model import Produto
from backend.models.ordem_servico_model import OrdemServico, FaseOS, VisitaTecnica, Orcamento
from backend.models.financeiro_model import ContaReceber, ContaPagar, MovimentacaoFinanceira, CategoriaFinanceira
from backend.models.agendamento_model import Agendamento
from backend.models.fornecedor_model import Fornecedor

def validar_relationships():
    """Valida todos os relationships entre modelos"""
    print("\n🔍 VALIDAÇÃO DE RELACIONAMENTOS ENTRE TABELAS\n")
    print("="*80)
    
    problemas = []
    validacoes = []
    
    # 1. Cliente → OrdemServico
    print("\n1️⃣ Cliente ↔ OrdemServico")
    try:
        mapper = inspect(Cliente)
        rel = mapper.relationships.get('ordens_servico')
        if rel:
            print(f"   ✅ Cliente.ordens_servico → {rel.target}")
            validacoes.append("Cliente → OrdemServico")
        else:
            problemas.append("Cliente.ordens_servico não encontrado")
    except Exception as e:
        problemas.append(f"Erro em Cliente.ordens_servico: {e}")
    
    # 2. Cliente → ContaReceber
    print("\n2️⃣ Cliente ↔ ContaReceber")
    try:
        rel = mapper.relationships.get('contas_receber')
        if rel:
            print(f"   ✅ Cliente.contas_receber → {rel.target}")
            validacoes.append("Cliente → ContaReceber")
        else:
            problemas.append("Cliente.contas_receber não encontrado")
    except Exception as e:
        problemas.append(f"Erro em Cliente.contas_receber: {e}")
    
    # 3. Cliente → Agendamento
    print("\n3️⃣ Cliente ↔ Agendamento")
    try:
        rel = mapper.relationships.get('agendamentos')
        if rel:
            print(f"   ✅ Cliente.agendamentos → {rel.target}")
            validacoes.append("Cliente → Agendamento")
        else:
            problemas.append("Cliente.agendamentos não encontrado")
    except Exception as e:
        problemas.append(f"Erro em Cliente.agendamentos: {e}")
    
    # 4. OrdemServico → FaseOS
    print("\n4️⃣ OrdemServico ↔ FaseOS")
    try:
        mapper_os = inspect(OrdemServico)
        rel = mapper_os.relationships.get('fases')
        if rel:
            print(f"   ✅ OrdemServico.fases → {rel.target}")
            print(f"   ⚙️ Cascade: {rel.cascade}")
            validacoes.append("OrdemServico → FaseOS (cascade)")
        else:
            problemas.append("OrdemServico.fases não encontrado")
    except Exception as e:
        problemas.append(f"Erro em OrdemServico.fases: {e}")
    
    # 5. OrdemServico → ContaReceber
    print("\n5️⃣ OrdemServico ↔ ContaReceber")
    try:
        rel = mapper_os.relationships.get('contas_receber')
        if rel:
            print(f"   ✅ OrdemServico.contas_receber → {rel.target}")
            print(f"   ⚙️ Cascade: {rel.cascade}")
            validacoes.append("OrdemServico → ContaReceber (cascade)")
        else:
            problemas.append("OrdemServico.contas_receber não encontrado")
    except Exception as e:
        problemas.append(f"Erro em OrdemServico.contas_receber: {e}")
    
    # 6. OrdemServico → Agendamento
    print("\n6️⃣ OrdemServico ↔ Agendamento")
    try:
        rel = mapper_os.relationships.get('agendamentos')
        if rel:
            print(f"   ✅ OrdemServico.agendamentos → {rel.target}")
            print(f"   ⚙️ Cascade: {rel.cascade}")
            validacoes.append("OrdemServico → Agendamento (cascade)")
        else:
            problemas.append("OrdemServico.agendamentos não encontrado")
    except Exception as e:
        problemas.append(f"Erro em OrdemServico.agendamentos: {e}")
    
    # 7. ContaReceber → MovimentacaoFinanceira
    print("\n7️⃣ ContaReceber ↔ MovimentacaoFinanceira")
    try:
        mapper_cr = inspect(ContaReceber)
        rel = mapper_cr.relationships.get('movimentacoes')
        if rel:
            print(f"   ✅ ContaReceber.movimentacoes → {rel.target}")
            print(f"   ⚙️ Cascade: {rel.cascade}")
            validacoes.append("ContaReceber → MovimentacaoFinanceira (cascade)")
        else:
            problemas.append("ContaReceber.movimentacoes não encontrado")
    except Exception as e:
        problemas.append(f"Erro em ContaReceber.movimentacoes: {e}")
    
    # 8. ContaPagar → MovimentacaoFinanceira
    print("\n8️⃣ ContaPagar ↔ MovimentacaoFinanceira")
    try:
        mapper_cp = inspect(ContaPagar)
        rel = mapper_cp.relationships.get('movimentacoes')
        if rel:
            print(f"   ✅ ContaPagar.movimentacoes → {rel.target}")
            print(f"   ⚙️ Cascade: {rel.cascade}")
            validacoes.append("ContaPagar → MovimentacaoFinanceira (cascade)")
        else:
            problemas.append("ContaPagar.movimentacoes não encontrado")
    except Exception as e:
        problemas.append(f"Erro em ContaPagar.movimentacoes: {e}")
    
    # 9. Agendamento → OrdemServico (opcional)
    print("\n9️⃣ Agendamento ↔ OrdemServico (opcional)")
    try:
        mapper_ag = inspect(Agendamento)
        rel = mapper_ag.relationships.get('ordem_servico')
        if rel:
            print(f"   ✅ Agendamento.ordem_servico → {rel.target}")
            validacoes.append("Agendamento → OrdemServico (opcional)")
        else:
            problemas.append("Agendamento.ordem_servico não encontrado")
    except Exception as e:
        problemas.append(f"Erro em Agendamento.ordem_servico: {e}")
    
    return validacoes, problemas

def validar_foreign_keys():
    """Valida todas as Foreign Keys no banco"""
    print("\n\n🔐 VALIDAÇÃO DE FOREIGN KEYS\n")
    print("="*80)
    
    inspector = inspect(engine)
    tabelas_validadas = []
    fks_validadas = []
    problemas_fk = []
    
    # Tabelas críticas para validar
    tabelas_criticas = [
        'clientes',
        'ordens_servico',
        'fases_os',
        'contas_receber',
        'contas_pagar',
        'movimentacoes_financeiras',
        'agendamentos',
        'produtos',
        'fornecedores'
    ]
    
    for tabela in tabelas_criticas:
        try:
            fks = inspector.get_foreign_keys(tabela)
            if fks:
                print(f"\n📋 {tabela}:")
                for fk in fks:
                    col = fk['constrained_columns'][0]
                    ref_table = fk['referred_table']
                    ref_col = fk['referred_columns'][0]
                    print(f"   ✅ {col} → {ref_table}.{ref_col}")
                    fks_validadas.append(f"{tabela}.{col} → {ref_table}.{ref_col}")
                tabelas_validadas.append(tabela)
            else:
                print(f"\n⚠️  {tabela}: Nenhuma FK encontrada")
        except Exception as e:
            problemas_fk.append(f"Erro ao validar {tabela}: {e}")
    
    return tabelas_validadas, fks_validadas, problemas_fk

def validar_indices():
    """Valida índices das tabelas"""
    print("\n\n📊 VALIDAÇÃO DE ÍNDICES\n")
    print("="*80)
    
    inspector = inspect(engine)
    indices_validados = []
    
    tabelas_criticas = ['clientes', 'ordens_servico', 'contas_receber', 'contas_pagar']
    
    for tabela in tabelas_criticas:
        try:
            indices = inspector.get_indexes(tabela)
            if indices:
                print(f"\n📌 {tabela}:")
                for idx in indices:
                    print(f"   ✅ {idx['name']}: {idx['column_names']}")
                    indices_validados.append(f"{tabela}.{idx['name']}")
        except Exception as e:
            print(f"   ⚠️ Erro: {e}")
    
    return indices_validados

def main():
    print("\n" + "="*80)
    print("🔍 VALIDAÇÃO COMPLETA DE SINCRONIZAÇÃO DE TABELAS - FASES 1-4")
    print("="*80)
    
    # 1. Validar relacionamentos
    validacoes_rel, problemas_rel = validar_relationships()
    
    # 2. Validar Foreign Keys
    tabelas_val, fks_val, problemas_fk = validar_foreign_keys()
    
    # 3. Validar índices
    indices_val = validar_indices()
    
    # Resumo final
    print("\n\n" + "="*80)
    print("📊 RESUMO DA VALIDAÇÃO")
    print("="*80)
    
    print(f"\n✅ RELACIONAMENTOS VALIDADOS: {len(validacoes_rel)}")
    for v in validacoes_rel:
        print(f"   • {v}")
    
    print(f"\n✅ TABELAS COM FK VALIDADAS: {len(tabelas_val)}")
    for t in tabelas_val:
        print(f"   • {t}")
    
    print(f"\n✅ FOREIGN KEYS VALIDADAS: {len(fks_val)}")
    for fk in fks_val[:10]:  # Mostrar apenas primeiras 10
        print(f"   • {fk}")
    if len(fks_val) > 10:
        print(f"   ... e mais {len(fks_val) - 10} FKs")
    
    print(f"\n✅ ÍNDICES VALIDADOS: {len(indices_val)}")
    
    # Problemas encontrados
    if problemas_rel or problemas_fk:
        print(f"\n❌ PROBLEMAS ENCONTRADOS:")
        for p in problemas_rel + problemas_fk:
            print(f"   • {p}")
        return False
    else:
        print("\n\n🎉 TODAS AS VALIDAÇÕES PASSARAM!")
        print("✅ Sistema pronto para testes de integração")
        return True

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
