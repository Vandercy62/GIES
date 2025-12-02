#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correções automáticas de lint para FASE 102B
Corrige strings duplicadas, linhas longas, f-strings desnecessárias
"""

import re
from pathlib import Path

def corrigir_colaborador_router():
    """Corrige backend/api/routers/colaborador_router.py"""
    arquivo = Path("backend/api/routers/colaborador_router.py")
    conteudo = arquivo.read_text(encoding='utf-8')
    
    # Substituir strings duplicadas pela constante
    conteudo = conteudo.replace(
        'detail="Colaborador não encontrado"',
        'detail=COLABORADOR_NAO_ENCONTRADO'
    )
    
    # Substituir formato de data duplicado
    conteudo = conteudo.replace(
        'strftime("%d/%m/%Y")',
        'strftime(FORMATO_DATA_BR)'
    )
    
    # Corrigir linhas longas - quebrar em múltiplas linhas
    correcoes_linhas = [
        # Linha 137
        (
            '                query = query.filter(Colaborador.superior_direto_id.isnot(None))',
            '                query = query.filter(\n'
            '                    Colaborador.superior_direto_id.isnot(None)\n'
            '                )'
        ),
        # Linha 193
        (
            '    if db.query(Colaborador).filter(Colaborador.matricula == colaborador_data.matricula).first():',
            '    colaborador_existente = db.query(Colaborador).filter(\n'
            '        Colaborador.matricula == colaborador_data.matricula\n'
            '    ).first()\n'
            '    if colaborador_existente:'
        ),
        # Linha 208
        (
            '    if db.query(Colaborador).filter(Colaborador.user_id == colaborador_data.user_id).first():',
            '    usuario_existente = db.query(Colaborador).filter(\n'
            '        Colaborador.user_id == colaborador_data.user_id\n'
            '    ).first()\n'
            '    if usuario_existente:'
        ),
        # Linha 215
        (
            '    cargo = db.query(Cargo).filter(Cargo.id == colaborador_data.cargo_id).first()',
            '    cargo = db.query(Cargo).filter(\n'
            '        Cargo.id == colaborador_data.cargo_id\n'
            '    ).first()'
        ),
        # Linha 223
        (
            '    departamento = db.query(Departamento).filter(Departamento.id == colaborador_data.departamento_id).first()',
            '    departamento = db.query(Departamento).filter(\n'
            '        Departamento.id == colaborador_data.departamento_id\n'
            '    ).first()'
        ),
        # Linha 285
        (
            '    colaborador = db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()',
            '    colaborador = db.query(Colaborador).filter(\n'
            '        Colaborador.id == colaborador_id\n'
            '    ).first()'
        ),
        # Linha 297
        (
            "    if 'cargo_id' in update_data and update_data['cargo_id'] != colaborador.cargo_id:",
            "    if ('cargo_id' in update_data and\n"
            "            update_data['cargo_id'] != colaborador.cargo_id):"
        ),
        # Linha 298
        (
            "        cargo = db.query(Cargo).filter(Cargo.id == update_data['cargo_id']).first()",
            "        cargo = db.query(Cargo).filter(\n"
            "            Cargo.id == update_data['cargo_id']\n"
            "        ).first()"
        ),
        # Linha 305
        (
            "    if 'departamento_id' in update_data and update_data['departamento_id'] != colaborador.departamento_id:",
            "    if ('departamento_id' in update_data and\n"
            "            update_data['departamento_id'] != colaborador.departamento_id):"
        ),
        # Linha 306
        (
            "        departamento = db.query(Departamento).filter(Departamento.id == update_data['departamento_id']).first()",
            "        departamento = db.query(Departamento).filter(\n"
            "            Departamento.id == update_data['departamento_id']\n"
            "        ).first()"
        ),
    ]
    
    for antigo, novo in correcoes_linhas:
        conteudo = conteudo.replace(antigo, novo)
    
    # Salvar arquivo corrigido
    arquivo.write_text(conteudo, encoding='utf-8')
    print(f"✅ {arquivo.name} corrigido!")
    
    return True


def corrigir_todos_routers():
    """Corrige todos os routers do backend"""
    routers_dir = Path("backend/api/routers")
    
    for arquivo in routers_dir.glob("*.py"):
        if arquivo.name == "__init__.py":
            continue
            
        print(f"\n🔍 Analisando {arquivo.name}...")
        conteudo = arquivo.read_text(encoding='utf-8')
        original = conteudo
        
        # Remover f-strings desnecessárias (sem variáveis)
        # Exemplo: f"texto fixo" -> "texto fixo"
        conteudo = re.sub(
            r'f"([^{}"]*)"',
            r'"\1"',
            conteudo
        )
        conteudo = re.sub(
            r"f'([^{}']*)'",
            r"'\1'",
            conteudo
        )
        
        # Salvar se houver mudanças
        if conteudo != original:
            arquivo.write_text(conteudo, encoding='utf-8')
            print(f"  ✅ F-strings desnecessárias removidas")
    
    print("\n✅ Todos os routers analisados!")


def corrigir_frontend_desktop():
    """Corrige arquivos do frontend desktop"""
    desktop_dir = Path("frontend/desktop")
    
    for arquivo in desktop_dir.glob("*.py"):
        if arquivo.name.startswith("test_"):
            continue
            
        print(f"\n🔍 Analisando {arquivo.name}...")
        conteudo = arquivo.read_text(encoding='utf-8')
        original = conteudo
        
        # Remover f-strings desnecessárias
        conteudo = re.sub(
            r'f"([^{}"]*)"',
            r'"\1"',
            conteudo
        )
        conteudo = re.sub(
            r"f'([^{}']*)'",
            r"'\1'",
            conteudo
        )
        
        # Salvar se houver mudanças
        if conteudo != original:
            arquivo.write_text(conteudo, encoding='utf-8')
            print(f"  ✅ F-strings desnecessárias removidas")
    
    print("\n✅ Todos os arquivos desktop analisados!")


if __name__ == "__main__":
    print("=" * 60)
    print("FASE 102B - CORREÇÕES AUTOMÁTICAS DE LINT")
    print("=" * 60)
    
    print("\n📁 Corrigindo colaborador_router.py...")
    corrigir_colaborador_router()
    
    print("\n📁 Corrigindo todos os routers...")
    corrigir_todos_routers()
    
    print("\n📁 Corrigindo frontend desktop...")
    corrigir_frontend_desktop()
    
    print("\n" + "=" * 60)
    print("✅ TODAS AS CORREÇÕES CONCLUÍDAS!")
    print("=" * 60)
