#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANÁLISE ESPECÍFICA SISTEMA ERP PRIMOTEX
=======================================

Análise focada apenas no código do projeto Primotex,
excluindo bibliotecas e dependências externas.

Criado em: 01/11/2025
Autor: GitHub Copilot
"""

import os
import sys
import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ProjectModule:
    """Módulo do projeto Primotex"""
    name: str
    path: str
    lines: int
    functions: int
    classes: int
    imports: int
    complexity: int
    type_hints: int
    docstrings: int
    category: str  # backend, frontend, shared, tests
    status: str    # complete, partial, missing

class PrimotexAnalyzer:
    """Analisador específico do Sistema Primotex"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.modules = []
        self.project_stats = {
            "backend": {"files": 0, "lines": 0, "functions": 0, "classes": 0},
            "frontend": {"files": 0, "lines": 0, "functions": 0, "classes": 0},
            "shared": {"files": 0, "lines": 0, "functions": 0, "classes": 0},
            "tests": {"files": 0, "lines": 0, "functions": 0, "classes": 0}
        }
        
        # Exclusões de análise
        self.excluded_paths = [
            '.venv', '.venv311', '.venv_new', '__pycache__', 
            '.git', '.pytest_cache', 'node_modules',
            'migrations/versions'  # Arquivos de migração auto-gerados
        ]
    
    def should_exclude_path(self, path: Path) -> bool:
        """Verifica se o caminho deve ser excluído"""
        path_str = str(path)
        return any(excluded in path_str for excluded in self.excluded_paths)
    
    def categorize_module(self, file_path: Path) -> str:
        """Categoriza o módulo do projeto"""
        path_str = str(file_path)
        
        if 'backend' in path_str:
            return 'backend'
        elif 'frontend' in path_str:
            return 'frontend'
        elif 'shared' in path_str:
            return 'shared'
        elif 'test' in path_str.lower():
            return 'tests'
        else:
            return 'root'
    
    def analyze_python_file(self, file_path: Path) -> ProjectModule:
        """Analisa um arquivo Python do projeto"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = len([line for line in content.splitlines() if line.strip()])
            tree = ast.parse(content)
            
            functions = 0
            classes = 0
            imports = 0
            type_hints = 0
            docstrings = 0
            complexity = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions += 1
                    if node.returns or any(arg.annotation for arg in node.args.args):
                        type_hints += 1
                    if (node.body and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant)):
                        docstrings += 1
                    complexity += self._calculate_complexity(node)
                    
                elif isinstance(node, ast.ClassDef):
                    classes += 1
                    if (node.body and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant)):
                        docstrings += 1
                        
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports += 1
            
            category = self.categorize_module(file_path)
            
            # Determinar status baseado no conteúdo
            status = "complete"
            if lines < 10:
                status = "minimal"
            elif "TODO" in content or "FIXME" in content:
                status = "partial"
            elif "pass" in content and functions == 0:
                status = "stub"
            
            return ProjectModule(
                name=file_path.name,
                path=str(file_path.relative_to(self.project_root)),
                lines=lines,
                functions=functions,
                classes=classes,
                imports=imports,
                complexity=complexity,
                type_hints=type_hints,
                docstrings=docstrings,
                category=category,
                status=status
            )
            
        except Exception as e:
            return ProjectModule(
                name=file_path.name,
                path=str(file_path.relative_to(self.project_root)),
                lines=0, functions=0, classes=0, imports=0,
                complexity=0, type_hints=0, docstrings=0,
                category="error", status=f"error: {e}"
            )
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calcula complexidade ciclomática"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
        return complexity
    
    def scan_project(self):
        """Escaneia todo o projeto"""
        print("🔍 Analisando código do projeto Primotex...")
        
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # Pular diretórios excluídos
            if self.should_exclude_path(root_path):
                continue
            
            for file in files:
                if file.endswith('.py'):
                    file_path = root_path / file
                    
                    if self.should_exclude_path(file_path):
                        continue
                    
                    module = self.analyze_python_file(file_path)
                    self.modules.append(module)
                    
                    # Acumular estatísticas
                    category = module.category
                    if category in self.project_stats:
                        self.project_stats[category]["files"] += 1
                        self.project_stats[category]["lines"] += module.lines
                        self.project_stats[category]["functions"] += module.functions
                        self.project_stats[category]["classes"] += module.classes
        
        print(f"   ✅ {len(self.modules)} arquivos do projeto analisados")
    
    def analyze_features(self) -> Dict[str, Any]:
        """Analisa features implementadas"""
        features = {
            "authentication": False,
            "cliente_crud": False,
            "produto_crud": False,
            "estoque_management": False,
            "ordem_servico": False,
            "agendamento": False,
            "financeiro": False,
            "relatorios": False,
            "comunicacao": False,
            "codigo_barras": False,
            "dashboard": False
        }
        
        # Verificar por nomes de arquivos e conteúdo
        for module in self.modules:
            name_lower = module.name.lower()
            path_lower = module.path.lower()
            
            if 'auth' in name_lower or 'login' in name_lower:
                features["authentication"] = True
            if 'cliente' in name_lower:
                features["cliente_crud"] = True
            if 'produto' in name_lower:
                features["produto_crud"] = True
            if 'estoque' in name_lower:
                features["estoque_management"] = True
            if 'ordem' in name_lower or 'os_' in name_lower:
                features["ordem_servico"] = True
            if 'agendamento' in name_lower:
                features["agendamento"] = True
            if 'financeiro' in name_lower:
                features["financeiro"] = True
            if 'relatorio' in name_lower:
                features["relatorios"] = True
            if 'comunicacao' in name_lower or 'whatsapp' in name_lower:
                features["comunicacao"] = True
            if 'codigo' in name_lower or 'barras' in name_lower:
                features["codigo_barras"] = True
            if 'dashboard' in name_lower:
                features["dashboard"] = True
        
        return features
    
    def analyze_phase_completion(self) -> Dict[str, Dict]:
        """Analisa completude das fases do projeto"""
        phases = {
            "Fase 1 - Fundação": {
                "backend_base": any('main.py' in m.path for m in self.modules),
                "models": any('models' in m.path for m in self.modules),
                "database": any('database' in m.path for m in self.modules),
                "auth": any('auth' in m.path for m in self.modules),
                "completion": 0
            },
            "Fase 2 - Interface Desktop": {
                "desktop_app": any('desktop' in m.path for m in self.modules),
                "clientes_window": any('clientes_window' in m.name for m in self.modules),
                "produtos_window": any('produtos_window' in m.name for m in self.modules),
                "estoque_window": any('estoque_window' in m.name for m in self.modules),
                "relatorios": any('relatorio' in m.name for m in self.modules),
                "completion": 0
            },
            "Fase 3 - OS e Agendamento": {
                "ordem_servico_model": any('ordem_servico' in m.name for m in self.modules),
                "ordem_servico_service": any('ordem_servico_service' in m.name for m in self.modules),
                "ordem_servico_schemas": any('ordem_servico_schema' in m.name for m in self.modules),
                "agendamento": any('agendamento' in m.name for m in self.modules),
                "completion": 0
            }
        }
        
        # Calcular completude de cada fase
        for phase_name, phase_data in phases.items():
            items = [k for k in phase_data.keys() if k != 'completion']
            completed = sum(1 for item in items if phase_data[item])
            phase_data['completion'] = (completed / len(items)) * 100
        
        return phases
    
    def generate_quality_metrics(self) -> Dict[str, float]:
        """Gera métricas de qualidade do código"""
        if not self.modules:
            return {}
        
        total_functions = sum(m.functions for m in self.modules)
        total_docstrings = sum(m.docstrings for m in self.modules)
        total_type_hints = sum(m.type_hints for m in self.modules)
        total_lines = sum(m.lines for m in self.modules)
        
        return {
            "docstring_coverage": (total_docstrings / total_functions * 100) if total_functions > 0 else 0,
            "type_hint_coverage": (total_type_hints / total_functions * 100) if total_functions > 0 else 0,
            "avg_function_length": (total_lines / total_functions) if total_functions > 0 else 0,
            "avg_complexity": sum(m.complexity for m in self.modules) / len(self.modules),
            "code_density": total_lines / len(self.modules)
        }
    
    def generate_report(self) -> str:
        """Gera relatório detalhado"""
        features = self.analyze_features()
        phases = self.analyze_phase_completion()
        quality = self.generate_quality_metrics()
        
        # Estatísticas totais
        total_files = len(self.modules)
        total_lines = sum(m.lines for m in self.modules)
        total_functions = sum(m.functions for m in self.modules)
        total_classes = sum(m.classes for m in self.modules)
        
        # Features implementadas
        implemented_features = sum(1 for f in features.values() if f)
        feature_completion = (implemented_features / len(features)) * 100
        
        report = f"""
# ANÁLISE ESPECÍFICA SISTEMA ERP PRIMOTEX
## Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## 📊 ESTATÍSTICAS DO PROJETO
- **Arquivos Python do Projeto:** {total_files:,}
- **Linhas de Código:** {total_lines:,}
- **Funções:** {total_functions:,}
- **Classes:** {total_classes:,}

## 📂 DISTRIBUIÇÃO POR CATEGORIA
"""
        
        for category, stats in self.project_stats.items():
            if stats["files"] > 0:
                report += f"- **{category.title()}:** {stats['files']} arquivos, {stats['lines']:,} linhas\n"
        
        report += f"""
## 🎯 FEATURES IMPLEMENTADAS ({feature_completion:.1f}% completo)
"""
        
        for feature, implemented in features.items():
            emoji = "✅" if implemented else "❌"
            report += f"- **{feature.replace('_', ' ').title()}:** {emoji}\n"
        
        report += "\n## 📋 COMPLETUDE DAS FASES\n"
        
        for phase_name, phase_data in phases.items():
            completion = phase_data['completion']
            emoji = "✅" if completion >= 90 else "🔄" if completion >= 50 else "❌"
            report += f"- **{phase_name}:** {emoji} {completion:.1f}%\n"
            
            for item, status in phase_data.items():
                if item != 'completion':
                    emoji = "✅" if status else "❌"
                    report += f"  - {item.replace('_', ' ').title()}: {emoji}\n"
        
        report += f"""
## 📈 MÉTRICAS DE QUALIDADE
- **Cobertura de Docstrings:** {quality.get('docstring_coverage', 0):.1f}%
- **Cobertura de Type Hints:** {quality.get('type_hint_coverage', 0):.1f}%
- **Complexidade Média:** {quality.get('avg_complexity', 0):.1f}
- **Densidade de Código:** {quality.get('code_density', 0):.1f} linhas/arquivo

## 📁 MÓDULOS PRINCIPAIS DO PROJETO
"""
        
        # Top 15 módulos do projeto por linhas
        project_modules = [m for m in self.modules if m.lines > 0]
        sorted_modules = sorted(project_modules, key=lambda x: x.lines, reverse=True)[:15]
        
        for module in sorted_modules:
            report += f"- **{module.path}:** {module.lines:,} linhas, {module.functions} funções, {module.classes} classes\n"
        
        # Módulos por categoria
        for category in ['backend', 'frontend', 'shared', 'tests']:
            category_modules = [m for m in self.modules if m.category == category and m.lines > 0]
            if category_modules:
                report += f"\n### {category.title()} - Top 5\n"
                sorted_cat = sorted(category_modules, key=lambda x: x.lines, reverse=True)[:5]
                for module in sorted_cat:
                    report += f"- **{module.name}:** {module.lines:,} linhas, {module.functions} funções\n"
        
        return report
    
    def run_analysis(self):
        """Executa análise completa"""
        print("🚀 ANÁLISE ESPECÍFICA SISTEMA PRIMOTEX")
        print("=" * 50)
        
        self.scan_project()
        
        report = self.generate_report()
        
        # Salvar relatório
        report_file = self.project_root / f"analise_primotex_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Relatório detalhado salvo: {report_file}")
        
        # Resumo na tela
        total_lines = sum(m.lines for m in self.modules)
        features = self.analyze_features()
        implemented_features = sum(1 for f in features.values() if f)
        
        print(f"\n📊 RESUMO:")
        print(f"   📁 {len(self.modules)} arquivos do projeto")
        print(f"   📝 {total_lines:,} linhas de código")
        print(f"   🎯 {implemented_features}/{len(features)} features implementadas")
        
        print("\n✅ ANÁLISE CONCLUÍDA!")
        print("=" * 50)


def main():
    """Função principal"""
    analyzer = PrimotexAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()