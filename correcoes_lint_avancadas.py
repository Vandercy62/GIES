#!/usr/bin/env python3
"""
Script para correções avançadas de lint
FASE 102B - Limpeza de código sem quebrar funcionalidade
"""

import re
from pathlib import Path


def limpar_espacos_em_branco(arquivo: Path) -> int:
    """Remove espaços em branco de linhas vazias"""
    with open(arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    linhas_corrigidas = 0
    novas_linhas = []
    
    for linha in linhas:
        # Se a linha tem apenas espaços, substituir por linha vazia
        if linha.strip() == '' and linha != '\n':
            novas_linhas.append('\n')
            linhas_corrigidas += 1
        else:
            novas_linhas.append(linha)
    
    if linhas_corrigidas > 0:
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.writelines(novas_linhas)
    
    return linhas_corrigidas


def quebrar_linhas_longas_colaborador_router():
    """Quebra linhas longas específicas do colaborador_router.py"""
    arquivo = Path('backend/api/routers/colaborador_router.py')
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Correção 1: Linha 137 - query.filter
    conteudo = conteudo.replace(
        '                query = query.filter(\n'
        '                    Colaborador.superior_direto_id.isnot(None)',
        '                query = query.filter(\n'
        '                    Colaborador.superior_direto_id.isnot(None)\n'
        '                )'
    )
    
    # Correção 2: Linha 212 - status_code muito longo
    conteudo = re.sub(
        r'raise HTTPException\(\s*status_code=status\.HTTP_400_BAD_REQUEST,\s*detail="CPF já cadastrado"\s*\)',
        'raise HTTPException(\n'
        '            status_code=status.HTTP_400_BAD_REQUEST,\n'
        '            detail="CPF já cadastrado"\n'
        '        )',
        conteudo
    )
    
    # Correção 3: Linha 219 - .first() muito longo
    conteudo = re.sub(
        r'usuario_existente = db\.query\(Colaborador\)\.filter\(\s*Colaborador\.usuario == colaborador_data\.usuario\s*\)\.first\(\)',
        'usuario_existente = db.query(Colaborador).filter(\n'
        '        Colaborador.usuario == colaborador_data.usuario\n'
        '    ).first()',
        conteudo
    )
    
    # Correção 4: Linha 227 - Cargo filter muito longo
    conteudo = re.sub(
        r'cargo = db\.query\(Cargo\)\.filter\(\s*Cargo\.id == colaborador_data\.cargo_id\s*\)\.first\(\)',
        'cargo = db.query(Cargo).filter(\n'
        '        Cargo.id == colaborador_data.cargo_id\n'
        '    ).first()',
        conteudo
    )
    
    # Correção 5: Linha 289 - return statement longo
    conteudo = re.sub(
        r'return colaborador\s*# Retorna com relacionamentos carregados',
        'return colaborador  # Retorna com relacionamentos',
        conteudo
    )
    
    # Correção 6: Linha 301-302 - query muito longo
    conteudo = re.sub(
        r'colaborador = db\.query\(Colaborador\)\.filter\(\s*Colaborador\.id == colaborador_id\s*\)\.first\(\)',
        'colaborador = db.query(Colaborador).filter(\n'
        '        Colaborador.id == colaborador_id\n'
        '    ).first()',
        conteudo
    )
    
    # Correção 7: Linha 309 - if 'cargo_id' muito longo
    conteudo = re.sub(
        r"if 'cargo_id' in update_data and update_data\['cargo_id'\] != colaborador\.cargo_id:",
        "if ('cargo_id' in update_data and\n"
        "            update_data['cargo_id'] != colaborador.cargo_id):",
        conteudo
    )
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"✅ Linhas longas quebradas em {arquivo.name}")


def processar_todos_arquivos():
    """Processa todos os arquivos Python do projeto"""
    pastas = [
        Path('backend/api/routers'),
        Path('backend/schemas'),
        Path('backend/services'),
        Path('frontend/desktop'),
        Path('shared')
    ]
    
    total_correcoes = 0
    arquivos_corrigidos = []
    
    for pasta in pastas:
        if not pasta.exists():
            continue
            
        for arquivo in pasta.glob('*.py'):
            if arquivo.name.startswith('test_'):
                continue  # Pula testes
                
            correcoes = limpar_espacos_em_branco(arquivo)
            if correcoes > 0:
                total_correcoes += correcoes
                arquivos_corrigidos.append(f"{arquivo} ({correcoes} linhas)")
    
    return total_correcoes, arquivos_corrigidos


def main():
    print("=" * 60)
    print("FASE 102B - CORREÇÕES AVANÇADAS DE LINT")
    print("=" * 60)
    print()
    
    # Etapa 1: Limpar espaços em branco
    print("📁 Limpando espaços em branco de linhas vazias...")
    total, arquivos = processar_todos_arquivos()
    
    if arquivos:
        print(f"\n✅ {total} linhas corrigidas em {len(arquivos)} arquivos:")
        for arq in arquivos[:10]:  # Mostra até 10
            print(f"   - {arq}")
        if len(arquivos) > 10:
            print(f"   ... e mais {len(arquivos) - 10} arquivos")
    else:
        print("✅ Nenhuma correção necessária")
    
    print()
    
    # Etapa 2: Quebrar linhas longas específicas
    print("📁 Quebrando linhas longas em colaborador_router.py...")
    quebrar_linhas_longas_colaborador_router()
    
    print()
    print("=" * 60)
    print("✅ TODAS AS CORREÇÕES AVANÇADAS CONCLUÍDAS!")
    print("=" * 60)


if __name__ == '__main__':
    main()
