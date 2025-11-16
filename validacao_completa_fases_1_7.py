#!/usr/bin/env python3
"""
Validação Completa e Mapeamento de Relacionamentos - FASES 1-7
Sistema ERP Primotex
Data: 15/11/2025

OBJETIVO:
1. Validar sincronização entre tabelas
2. Mapear TODAS as Foreign Keys
3. Validar relacionamentos bidirecionais
4. Identificar problemas de integridade
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set

# =============================================================================
# ESTRUTURA DE DADOS
# =============================================================================

class ForeignKey:
    """Representa uma Foreign Key"""
    def __init__(self, source_table: str, source_column: str, 
                 target_table: str, target_column: str, file: str):
        self.source_table = source_table
        self.source_column = source_column
        self.target_table = target_table
        self.target_column = target_column
        self.file = file
    
    def __repr__(self):
        return f"{self.source_table}.{self.source_column} → {self.target_table}.{self.target_column}"

class Relationship:
    """Representa um relationship SQLAlchemy"""
    def __init__(self, source_model: str, attribute: str, 
                 target_model: str, back_populates: str, file: str):
        self.source_model = source_model
        self.attribute = attribute
        self.target_model = target_model
        self.back_populates = back_populates
        self.file = file
    
    def __repr__(self):
        return f"{self.source_model}.{self.attribute} ↔ {self.target_model}.{self.back_populates}"

# =============================================================================
# ANÁLISE DE MODELS
# =============================================================================

def extract_table_name(file_path: Path) -> str:
    """Extrai o nome da tabela do arquivo model"""
    content = file_path.read_text(encoding='utf-8')
    
    # Procurar __tablename__
    match = re.search(r'__tablename__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    
    # Fallback: usar nome do arquivo
    return file_path.stem.replace('_model', '')

def extract_foreign_keys(file_path: Path) -> List[ForeignKey]:
    """Extrai todas as Foreign Keys de um model"""
    content = file_path.read_text(encoding='utf-8')
    fks = []
    
    table_name = extract_table_name(file_path)
    
    # Pattern: Column(..., ForeignKey("table.column"))
    pattern = r'(\w+)\s*=\s*Column\([^)]*ForeignKey\(["\']([^"\']+)["\']\)'
    
    for match in re.finditer(pattern, content):
        source_column = match.group(1)
        fk_reference = match.group(2)
        
        if '.' in fk_reference:
            target_table, target_column = fk_reference.split('.', 1)
            
            fk = ForeignKey(
                source_table=table_name,
                source_column=source_column,
                target_table=target_table,
                target_column=target_column,
                file=file_path.name
            )
            fks.append(fk)
    
    return fks

def extract_relationships(file_path: Path) -> List[Relationship]:
    """Extrai todos os relationships de um model"""
    content = file_path.read_text(encoding='utf-8')
    rels = []
    
    # Extrair nome do model (class name)
    class_match = re.search(r'class\s+(\w+)\(Base\):', content)
    if not class_match:
        return []
    
    source_model = class_match.group(1)
    
    # Pattern: attribute = relationship("TargetModel", back_populates="attr")
    pattern = r'(\w+)\s*=\s*relationship\(["\']([^"\']+)["\'][^)]*back_populates=["\']([^"\']+)["\']'
    
    for match in re.finditer(pattern, content):
        attribute = match.group(1)
        target_model = match.group(2)
        back_populates = match.group(3)
        
        rel = Relationship(
            source_model=source_model,
            attribute=attribute,
            target_model=target_model,
            back_populates=back_populates,
            file=file_path.name
        )
        rels.append(rel)
    
    return rels

# =============================================================================
# VALIDAÇÃO DE SINCRONIZAÇÃO
# =============================================================================

def validate_foreign_keys(all_fks: List[ForeignKey]) -> List[str]:
    """Valida se todas as FKs apontam para tabelas existentes"""
    issues = []
    
    # Coletar todas as tabelas existentes
    existing_tables = {fk.source_table for fk in all_fks}
    existing_tables.update({fk.target_table for fk in all_fks})
    
    # Adicionar tabelas conhecidas
    known_tables = {
        'users', 'clientes', 'produtos', 'ordens_servico', 'fases_os',
        'agendamentos', 'contas_receber', 'contas_pagar', 'fluxo_caixa',
        'comunicacao_templates', 'comunicacao_historico', 'colaboradores',
        'departamentos', 'cargos', 'fornecedores', 'categorias_produto',
        'movimentacoes_estoque', 'inventarios'
    }
    existing_tables.update(known_tables)
    
    # Validar cada FK
    for fk in all_fks:
        if fk.target_table not in existing_tables:
            issues.append(
                f"⚠️ FK órfã: {fk} (tabela '{fk.target_table}' não encontrada) [{fk.file}]"
            )
    
    return issues

def validate_relationships(all_rels: List[Relationship]) -> List[str]:
    """Valida se relationships são bidirecionais"""
    issues = []
    
    # Criar mapa de relationships
    rel_map = {}
    for rel in all_rels:
        key = (rel.source_model, rel.attribute)
        rel_map[key] = rel
    
    # Validar bidirecionalidade
    for rel in all_rels:
        # Procurar relationship reverso
        reverse_key = (rel.target_model, rel.back_populates)
        
        if reverse_key not in rel_map:
            issues.append(
                f"⚠️ Relationship unidirecional: {rel} "
                f"(falta {rel.target_model}.{rel.back_populates}) [{rel.file}]"
            )
        else:
            # Verificar se o reverso aponta de volta
            reverse_rel = rel_map[reverse_key]
            if reverse_rel.target_model != rel.source_model or \
               reverse_rel.back_populates != rel.attribute:
                issues.append(
                    f"⚠️ Relationship inconsistente: {rel} vs {reverse_rel}"
                )
    
    return issues

# =============================================================================
# ANÁLISE COMPLETA
# =============================================================================

def analyze_all_models() -> Tuple[List[ForeignKey], List[Relationship]]:
    """Analisa todos os models do sistema"""
    models_dir = Path("backend/models")
    
    all_fks = []
    all_rels = []
    
    print("📁 Analisando models...")
    for model_file in models_dir.glob("*.py"):
        if model_file.name.startswith('__'):
            continue
        
        print(f"  📄 {model_file.name}")
        
        # Extrair FKs
        fks = extract_foreign_keys(model_file)
        all_fks.extend(fks)
        print(f"     - {len(fks)} Foreign Keys encontradas")
        
        # Extrair relationships
        rels = extract_relationships(model_file)
        all_rels.extend(rels)
        print(f"     - {len(rels)} Relationships encontrados")
    
    return all_fks, all_rels

def generate_dependency_graph(all_fks: List[ForeignKey]) -> Dict[str, Set[str]]:
    """Gera grafo de dependências entre tabelas"""
    graph = {}
    
    for fk in all_fks:
        if fk.source_table not in graph:
            graph[fk.source_table] = set()
        graph[fk.source_table].add(fk.target_table)
    
    return graph

def detect_circular_dependencies(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """Detecta dependências circulares"""
    cycles = []
    
    def dfs(node, path, visited):
        if node in path:
            # Encontrou ciclo
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return
        
        if node in visited:
            return
        
        visited.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            dfs(neighbor, path, visited)
        
        path.pop()
    
    visited = set()
    for node in graph:
        dfs(node, [], visited)
    
    return cycles

# =============================================================================
# RELATÓRIO
# =============================================================================

def generate_report(all_fks: List[ForeignKey], all_rels: List[Relationship]):
    """Gera relatório completo de validação"""
    
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO DE VALIDAÇÃO - FASES 1-7")
    print("=" * 80)
    print()
    
    # Estatísticas gerais
    print("📈 ESTATÍSTICAS GERAIS")
    print("-" * 80)
    print(f"Total de Foreign Keys: {len(all_fks)}")
    print(f"Total de Relationships: {len(all_rels)}")
    print()
    
    # Listar todas as FKs por tabela
    print("🔗 FOREIGN KEYS POR TABELA")
    print("-" * 80)
    
    fks_by_table = {}
    for fk in all_fks:
        if fk.source_table not in fks_by_table:
            fks_by_table[fk.source_table] = []
        fks_by_table[fk.source_table].append(fk)
    
    for table in sorted(fks_by_table.keys()):
        print(f"\n📋 {table.upper()}")
        for fk in fks_by_table[table]:
            print(f"   {fk.source_column} → {fk.target_table}.{fk.target_column}")
    
    print()
    
    # Listar relationships
    print("🔄 RELATIONSHIPS POR MODEL")
    print("-" * 80)
    
    rels_by_model = {}
    for rel in all_rels:
        if rel.source_model not in rels_by_model:
            rels_by_model[rel.source_model] = []
        rels_by_model[rel.source_model].append(rel)
    
    for model in sorted(rels_by_model.keys()):
        print(f"\n📋 {model}")
        for rel in rels_by_model[model]:
            print(f"   {rel.attribute} ↔ {rel.target_model}.{rel.back_populates}")
    
    print()
    
    # Validações
    print("🔍 VALIDAÇÕES")
    print("-" * 80)
    
    fk_issues = validate_foreign_keys(all_fks)
    rel_issues = validate_relationships(all_rels)
    
    if not fk_issues and not rel_issues:
        print("✅ Nenhum problema encontrado!")
    else:
        if fk_issues:
            print("\n⚠️ PROBLEMAS EM FOREIGN KEYS:")
            for issue in fk_issues:
                print(f"   {issue}")
        
        if rel_issues:
            print("\n⚠️ PROBLEMAS EM RELATIONSHIPS:")
            for issue in rel_issues:
                print(f"   {issue}")
    
    print()
    
    # Grafo de dependências
    print("📊 GRAFO DE DEPENDÊNCIAS")
    print("-" * 80)
    
    graph = generate_dependency_graph(all_fks)
    for table in sorted(graph.keys()):
        deps = ', '.join(sorted(graph[table]))
        print(f"{table} → {deps}")
    
    print()
    
    # Dependências circulares
    print("🔄 ANÁLISE DE DEPENDÊNCIAS CIRCULARES")
    print("-" * 80)
    
    cycles = detect_circular_dependencies(graph)
    if not cycles:
        print("✅ Nenhuma dependência circular detectada!")
    else:
        print(f"⚠️ {len(cycles)} ciclos detectados:")
        for i, cycle in enumerate(cycles, 1):
            print(f"   Ciclo {i}: {' → '.join(cycle)}")
    
    print()
    print("=" * 80)
    print("✅ VALIDAÇÃO CONCLUÍDA!")
    print("=" * 80)

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Executa validação completa"""
    print("=" * 80)
    print("🔍 VALIDAÇÃO COMPLETA - SISTEMA ERP PRIMOTEX")
    print("FASES 1-7: Mapeamento de Relacionamentos")
    print("=" * 80)
    print()
    
    # Analisar models
    all_fks, all_rels = analyze_all_models()
    
    # Gerar relatório
    generate_report(all_fks, all_rels)

if __name__ == "__main__":
    main()
