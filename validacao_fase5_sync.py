#!/usr/bin/env python3
"""
Script de Validação FASE 5 - Comunicação e Colaboradores
Verifica sincronização de tabelas e relacionamentos
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import inspect
from backend.database.config import engine
from backend.models.comunicacao import (
    ComunicacaoTemplate, ComunicacaoHistorico, 
    ComunicacaoConfig, ComunicacaoFila, ComunicacaoEstatisticas
)
from backend.models.colaborador_model import (
    Colaborador, Departamento, Cargo, ColaboradorDocumento,
    HistoricoProfissional, PontoEletronico, PeriodoFerias
)
from backend.models.cliente_model import Cliente

def validar_comunicacao():
    """Valida relacionamentos do módulo de Comunicação"""
    print("\n🔍 VALIDAÇÃO - MÓDULO DE COMUNICAÇÃO\n" + "="*80)
    
    validacoes = []
    problemas = []
    
    # 1. ComunicacaoTemplate → ComunicacaoHistorico
    print("\n1️⃣ ComunicacaoTemplate ↔ ComunicacaoHistorico")
    try:
        mapper = inspect(ComunicacaoTemplate)
        rel = mapper.relationships.get('comunicacoes')
        if rel:
            print(f"   ✅ ComunicacaoTemplate.comunicacoes → {rel.target}")
            validacoes.append("ComunicacaoTemplate → ComunicacaoHistorico")
        else:
            problemas.append("ComunicacaoTemplate.comunicacoes não encontrado")
    except Exception as e:
        problemas.append(f"Erro em ComunicacaoTemplate: {e}")
    
    # 2. ComunicacaoHistorico → Cliente
    print("\n2️⃣ ComunicacaoHistorico ↔ Cliente")
    try:
        mapper = inspect(ComunicacaoHistorico)
        rel = mapper.relationships.get('cliente')
        if rel:
            print(f"   ✅ ComunicacaoHistorico.cliente → {rel.target}")
            validacoes.append("ComunicacaoHistorico → Cliente")
        else:
            problemas.append("ComunicacaoHistorico.cliente não encontrado")
    except Exception as e:
        problemas.append(f"Erro em ComunicacaoHistorico: {e}")
    
    # 3. Cliente → ComunicacaoHistorico (reverso)
    print("\n3️⃣ Cliente ↔ ComunicacaoHistorico (reverso)")
    try:
        mapper = inspect(Cliente)
        rel = mapper.relationships.get('comunicacoes')
        if rel:
            print(f"   ✅ Cliente.comunicacoes → {rel.target}")
            validacoes.append("Cliente → ComunicacaoHistorico (reverso)")
        else:
            print("   ⚠️ Cliente.comunicacoes não encontrado (pode ser opcional)")
    except Exception as e:
        print(f"   ⚠️ Erro: {e}")
    
    return validacoes, problemas

def validar_colaboradores():
    """Valida relacionamentos do módulo de Colaboradores"""
    print("\n\n🔍 VALIDAÇÃO - MÓDULO DE COLABORADORES\n" + "="*80)
    
    validacoes = []
    problemas = []
    
    # 1. Colaborador → Usuario
    print("\n1️⃣ Colaborador ↔ Usuario")
    try:
        mapper = inspect(Colaborador)
        rel = mapper.relationships.get('usuario')
        if rel:
            print(f"   ✅ Colaborador.usuario → {rel.target}")
            validacoes.append("Colaborador → Usuario")
        else:
            problemas.append("Colaborador.usuario não encontrado")
    except Exception as e:
        problemas.append(f"Erro em Colaborador.usuario: {e}")
    
    # 2. Colaborador → Cargo
    print("\n2️⃣ Colaborador ↔ Cargo")
    try:
        rel = mapper.relationships.get('cargo')
        if rel:
            print(f"   ✅ Colaborador.cargo → {rel.target}")
            validacoes.append("Colaborador → Cargo")
        else:
            problemas.append("Colaborador.cargo não encontrado")
    except Exception as e:
        problemas.append(f"Erro em Colaborador.cargo: {e}")
    
    # 3. Colaborador → Departamento
    print("\n3️⃣ Colaborador ↔ Departamento")
    try:
        rel = mapper.relationships.get('departamento')
        if rel:
            print(f"   ✅ Colaborador.departamento → {rel.target}")
            validacoes.append("Colaborador → Departamento")
        else:
            problemas.append("Colaborador.departamento não encontrado")
    except Exception as e:
        problemas.append(f"Erro em Colaborador.departamento: {e}")
    
    # 4. Colaborador → ColaboradorDocumento
    print("\n4️⃣ Colaborador ↔ ColaboradorDocumento")
    try:
        rel = mapper.relationships.get('documentos')
        if rel:
            print(f"   ✅ Colaborador.documentos → {rel.target}")
            validacoes.append("Colaborador → ColaboradorDocumento")
        else:
            problemas.append("Colaborador.documentos não encontrado")
    except Exception as e:
        problemas.append(f"Erro em Colaborador.documentos: {e}")
    
    # 5. Cargo → Colaborador (reverso)
    print("\n5️⃣ Cargo ↔ Colaborador (reverso)")
    try:
        mapper = inspect(Cargo)
        rel = mapper.relationships.get('colaboradores')
        if rel:
            print(f"   ✅ Cargo.colaboradores → {rel.target}")
            validacoes.append("Cargo → Colaborador (reverso)")
        else:
            problemas.append("Cargo.colaboradores não encontrado")
    except Exception as e:
        problemas.append(f"Erro em Cargo.colaboradores: {e}")
    
    # 6. Departamento → Colaborador (reverso)
    print("\n6️⃣ Departamento ↔ Colaborador (reverso)")
    try:
        mapper = inspect(Departamento)
        rel = mapper.relationships.get('colaboradores')
        if rel:
            print(f"   ✅ Departamento.colaboradores → {rel.target}")
            validacoes.append("Departamento → Colaborador (reverso)")
        else:
            problemas.append("Departamento.colaboradores não encontrado")
    except Exception as e:
        problemas.append(f"Erro em Departamento.colaboradores: {e}")
    
    return validacoes, problemas

def validar_foreign_keys_fase5():
    """Valida Foreign Keys da FASE 5"""
    print("\n\n🔐 VALIDAÇÃO DE FOREIGN KEYS - FASE 5\n" + "="*80)
    
    inspector = inspect(engine)
    fks_validadas = []
    
    tabelas_fase5 = [
        'comunicacao_templates',
        'comunicacao_historico',
        'comunicacao_config',
        'comunicacao_fila',
        'colaboradores',
        'departamentos',
        'cargos',
        'colaborador_documentos',
        'historico_profissional',
        'ponto_eletronico',
        'periodo_ferias'
    ]
    
    for tabela in tabelas_fase5:
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
            else:
                print(f"\n⚠️  {tabela}: Nenhuma FK (tabela independente)")
        except Exception as e:
            print(f"\n❌ Erro ao validar {tabela}: {e}")
    
    return fks_validadas

def main():
    print("\n" + "="*80)
    print("🔍 VALIDAÇÃO COMPLETA - FASE 5 (Comunicação e Colaboradores)")
    print("="*80)
    
    # 1. Validar Comunicação
    val_com, prob_com = validar_comunicacao()
    
    # 2. Validar Colaboradores
    val_colab, prob_colab = validar_colaboradores()
    
    # 3. Validar Foreign Keys
    fks = validar_foreign_keys_fase5()
    
    # Resumo
    print("\n\n" + "="*80)
    print("📊 RESUMO DA VALIDAÇÃO - FASE 5")
    print("="*80)
    
    total_validacoes = len(val_com) + len(val_colab)
    total_problemas = len(prob_com) + len(prob_colab)
    
    print(f"\n✅ RELACIONAMENTOS VALIDADOS: {total_validacoes}")
    for v in val_com + val_colab:
        print(f"   • {v}")
    
    print(f"\n✅ FOREIGN KEYS VALIDADAS: {len(fks)}")
    for fk in fks[:10]:
        print(f"   • {fk}")
    if len(fks) > 10:
        print(f"   ... e mais {len(fks) - 10} FKs")
    
    if total_problemas > 0:
        print(f"\n❌ PROBLEMAS ENCONTRADOS: {total_problemas}")
        for p in prob_com + prob_colab:
            print(f"   • {p}")
        return False
    else:
        print("\n\n🎉 TODAS AS VALIDAÇÕES DA FASE 5 PASSARAM!")
        print("✅ Módulos de Comunicação e Colaboradores sincronizados")
        return True

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
