#!/usr/bin/env python3
"""
Correções finais de lint - colaborador_router.py
FASE 102B - Limpeza final
"""

import re
from pathlib import Path


def corrigir_comparacoes_booleanas(conteudo: str) -> str:
    """Corrige comparações == True/False"""
    # == True -> is True
    conteudo = re.sub(
        r'\.ativo == True\)',
        '.ativo.is_(True))',
        conteudo
    )

    # == False -> is False (ou is_(False) no SQLAlchemy)
    conteudo = re.sub(
        r'\.ativo == False\)',
        '.ativo.is_(False))',
        conteudo
    )

    return conteudo


def corrigir_linhas_longas(conteudo: str) -> str:
    """Quebra linhas longas específicas"""

    # Linha 385 - nova_observacao muito longa
    conteudo = re.sub(
        r'nova_observacao = f"\\n\[\{datetime\.now\(\)\.strftime\(\'%d/%m/%Y %H:%M\'\)\}\] Status alterado de \{status_anterior\.value\} para \{novo_status\.value\}\. Motivo: \{motivo\}"',
        'nova_observacao = (\n'
        '            f"\\n[{datetime.now().strftime(\'%d/%m/%Y %H:%M\')}] "\n'
        '            f"Status alterado de {status_anterior.value} para "\n'
        '            f"{novo_status.value}. Motivo: {motivo}"\n'
        '        )',
        conteudo,
        flags=re.MULTILINE
    )

    # Linha 390 - return statement longo
    conteudo = re.sub(
        r'return \{"message": f"Status alterado para \{novo_status\.value\}", "status_anterior": status_anterior\.value\}',
        'return {\n'
        '            "message": f"Status alterado para {novo_status.value}",\n'
        '            "status_anterior": status_anterior.value\n'
        '        }',
        conteudo
    )

    # Linha 434 - nova_observacao inativado
    conteudo = re.sub(
        r'nova_observacao = f"\\n\[\{datetime\.now\(\)\.strftime\(\'%d/%m/%Y %H:%M\'\)\}\] Colaborador inativado\. Motivo: \{motivo\}"',
        'nova_observacao = (\n'
        '            f"\\n[{datetime.now().strftime(\'%d/%m/%Y %H:%M\')}] "\n'
        '            f"Colaborador inativado. Motivo: {motivo}"\n'
        '        )',
        conteudo
    )

    # Linha 481 - total_ativos
    conteudo = re.sub(
        r'total_ativos = db\.query\(Colaborador\)\.filter\(Colaborador\.ativo\.is_\(True\)\)\.count\(\)',
        'total_ativos = (\n'
        '            db.query(Colaborador)\n'
        '            .filter(Colaborador.ativo.is_(True))\n'
        '            .count()\n'
        '        )',
        conteudo
    )

    # Linha 482 - total_inativos
    conteudo = re.sub(
        r'total_inativos = db\.query\(Colaborador\)\.filter\(Colaborador\.ativo\.is_\(False\)\)\.count\(\)',
        'total_inativos = (\n'
        '            db.query(Colaborador)\n'
        '            .filter(Colaborador.ativo.is_(False))\n'
        '            .count()\n'
        '        )',
        conteudo
    )

    # Linha 483 - total_em_ferias
    conteudo = re.sub(
        r'total_em_ferias = db\.query\(Colaborador\)\.filter\(Colaborador\.status == StatusColaborador\.FERIAS\)\.count\(\)',
        'total_em_ferias = (\n'
        '            db.query(Colaborador)\n'
        '            .filter(Colaborador.status == StatusColaborador.FERIAS)\n'
        '            .count()\n'
        '        )',
        conteudo
    )

    # Linha 484 - total_afastados
    conteudo = re.sub(
        r'total_afastados = db\.query\(Colaborador\)\.filter\(Colaborador\.status == StatusColaborador\.AFASTADO\)\.count\(\)',
        'total_afastados = (\n'
        '            db.query(Colaborador)\n'
        '            .filter(Colaborador.status == StatusColaborador.AFASTADO)\n'
        '            .count()\n'
        '        )',
        conteudo
    )

    # Linha 521 - colaboradores_ativos
    conteudo = re.sub(
        r'colaboradores_ativos = db\.query\(Colaborador\)\.filter\(Colaborador\.ativo\.is_\(True\)\)\.all\(\)',
        'colaboradores_ativos = (\n'
        '            db.query(Colaborador)\n'
        '            .filter(Colaborador.ativo.is_(True))\n'
        '            .all()\n'
        '        )',
        conteudo
    )

    # Linha 525 - list comprehension idades
    conteudo = re.sub(
        r'idades = \[c\.idade for c in colaboradores_ativos if c\.idade and c\.idade > 0\]',
        'idades = [\n'
        '                    c.idade for c in colaboradores_ativos\n'
        '                    if c.idade and c.idade > 0\n'
        '                ]',
        conteudo
    )

    # Linha 532 - list comprehension tempos_empresa
    conteudo = re.sub(
        r'tempos_empresa = \[c\.tempo_empresa for c in colaboradores_ativos if c\.tempo_empresa and c\.tempo_empresa > 0\]',
        'tempos_empresa = [\n'
        '                    c.tempo_empresa for c in colaboradores_ativos\n'
        '                    if c.tempo_empresa and c.tempo_empresa > 0\n'
        '                ]',
        conteudo
    )

    # Linha 533 - tempo_empresa_medio
    conteudo = re.sub(
        r'tempo_empresa_medio = sum\(tempos_empresa\) / len\(tempos_empresa\) if tempos_empresa else 0',
        'tempo_empresa_medio = (\n'
        '                    sum(tempos_empresa) / len(tempos_empresa)\n'
        '                    if tempos_empresa else 0\n'
        '                )',
        conteudo
    )

    # Linha 539 - list comprehension salarios
    conteudo = re.sub(
        r'salarios = \[float\(c\.salario_atual\) for c in colaboradores_ativos if c\.salario_atual is not None and c\.salario_atual > 0\]',
        'salarios = [\n'
        '                    float(c.salario_atual)\n'
        '                    for c in colaboradores_ativos\n'
        '                    if (c.salario_atual is not None and\n'
        '                        c.salario_atual > 0)\n'
        '                ]',
        conteudo
    )

    # Linha 540 - salario_medio
    conteudo = re.sub(
        r'salario_medio = sum\(salarios\) / len\(salarios\) if salarios else 0',
        'salario_medio = (\n'
        '                    sum(salarios) / len(salarios)\n'
        '                    if salarios else 0\n'
        '                )',
        conteudo
    )

    # Linha 587 - tempo_empresa_medio conversão
    conteudo = re.sub(
        r'tempo_empresa_medio=tempo_empresa_medio / 365 if tempo_empresa_medio else 0,  # Converter para anos',
        'tempo_empresa_medio=(\n'
        '                tempo_empresa_medio / 365\n'
        '                if tempo_empresa_medio else 0\n'
        '            ),  # Converter para anos',
        conteudo
    )

    return conteudo


def main():
    print("=" * 60)
    print("FASE 102B - CORREÇÕES FINAIS DE LINT")
    print("=" * 60)
    print()

    arquivo = Path('backend/api/routers/colaborador_router.py')

    print(f"📁 Processando {arquivo.name}...")

    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Aplicar correções
    print("  ✅ Corrigindo comparações booleanas...")
    conteudo = corrigir_comparacoes_booleanas(conteudo)

    print("  ✅ Quebrando linhas longas...")
    conteudo = corrigir_linhas_longas(conteudo)

    # Salvar
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo)

    print()
    print("=" * 60)
    print("✅ CORREÇÕES FINAIS CONCLUÍDAS!")
    print("=" * 60)


if __name__ == '__main__':
    main()
