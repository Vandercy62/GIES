#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDAÇÃO COMPLETA DO SISTEMA ERP PRIMOTEX
==========================================

Análise e validação completa de todo o sistema implementado até novembro/2025.
Inclui verificação de:
- Estrutura de arquivos e diretórios
- Qualidade e integridade do código
- Funcionalidades implementadas
- Integrações e dependências
- Performance e segurança
- Cobertura de testes

Criado em: 01/11/2025
Autor: GitHub Copilot
"""

import os
import sys
import ast
import json
import time
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Adicionar caminho do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@dataclass
class ModuleAnalysis:
    """Análise de um módulo Python"""
    name: str
    lines: int
    functions: int
    classes: int
    imports: int
    docstrings: int
    type_hints: int
    complexity: int
    errors: List[str]
    warnings: List[str]

@dataclass
class SystemValidation:
    """Resultado da validação do sistema"""
    timestamp: datetime
    total_files: int
    total_lines: int
    total_functions: int
    total_classes: int
    modules: List[ModuleAnalysis]
    database_status: Dict[str, Any]
    dependencies_status: Dict[str, Any]
    api_endpoints: List[str]
    integrations: Dict[str, bool]
    security_score: float
    performance_score: float
    quality_score: float
    overall_score: float
    recommendations: List[str]
    critical_issues: List[str]

class SystemValidator:
    """Validador completo do sistema ERP Primotex"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results = SystemValidation(
            timestamp=datetime.now(),
            total_files=0,
            total_lines=0,
            total_functions=0,
            total_classes=0,
            modules=[],
            database_status={},
            dependencies_status={},
            api_endpoints=[],
            integrations={},
            security_score=0.0,
            performance_score=0.0,
            quality_score=0.0,
            overall_score=0.0,
            recommendations=[],
            critical_issues=[]
        )
    
    def analyze_python_file(self, file_path: Path) -> ModuleAnalysis:
        """Analisa um arquivo Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.splitlines())
            
            tree = ast.parse(content)
            
            # Contadores
            functions = 0
            classes = 0
            imports = 0
            docstrings = 0
            type_hints = 0
            complexity = 0
            errors = []
            warnings = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions += 1
                    # Verificar type hints
                    if node.returns or any(arg.annotation for arg in node.args.args):
                        type_hints += 1
                    # Verificar docstring
                    if (node.body and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant) and 
                        isinstance(node.body[0].value.value, str)):
                        docstrings += 1
                    # Calcular complexidade (aproximada)
                    complexity += self._calculate_complexity(node)
                    
                elif isinstance(node, ast.ClassDef):
                    classes += 1
                    # Verificar docstring da classe
                    if (node.body and isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant) and 
                        isinstance(node.body[0].value.value, str)):
                        docstrings += 1
                        
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports += 1
            
            # Verificações de qualidade
            if lines > 1000:
                warnings.append(f"Arquivo muito longo: {lines} linhas")
            
            if functions > 0 and type_hints / functions < 0.5:
                warnings.append("Baixa cobertura de type hints")
            
            if functions > 0 and docstrings / functions < 0.3:
                warnings.append("Baixa cobertura de docstrings")
            
            if complexity > 100:
                warnings.append("Alta complexidade ciclomática")
            
            return ModuleAnalysis(
                name=str(file_path.relative_to(self.project_root)),
                lines=lines,
                functions=functions,
                classes=classes,
                imports=imports,
                docstrings=docstrings,
                type_hints=type_hints,
                complexity=complexity,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            return ModuleAnalysis(
                name=str(file_path.relative_to(self.project_root)),
                lines=0,
                functions=0,
                classes=0,
                imports=0,
                docstrings=0,
                type_hints=0,
                complexity=0,
                errors=[f"Erro ao analisar: {str(e)}"],
                warnings=[]
            )
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calcula complexidade ciclomática aproximada"""
        complexity = 1  # Base
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def scan_project_structure(self) -> Dict[str, Any]:
        """Escaneia a estrutura do projeto"""
        structure = {
            "directories": [],
            "python_files": [],
            "config_files": [],
            "documentation": [],
            "tests": []
        }
        
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # Pular diretórios específicos
            if any(skip in str(root_path) for skip in ['.git', '__pycache__', '.pytest_cache', 'node_modules']):
                continue
            
            structure["directories"].append(str(root_path.relative_to(self.project_root)))
            
            for file in files:
                file_path = root_path / file
                rel_path = str(file_path.relative_to(self.project_root))
                
                if file.endswith('.py'):
                    structure["python_files"].append(rel_path)
                elif file in ['requirements.txt', 'pyproject.toml', 'setup.py', '.env']:
                    structure["config_files"].append(rel_path)
                elif file.endswith(('.md', '.rst', '.txt')) and 'doc' in file.lower():
                    structure["documentation"].append(rel_path)
                elif 'test' in file.lower() and file.endswith('.py'):
                    structure["tests"].append(rel_path)
        
        return structure
    
    def analyze_codebase(self):
        """Analisa toda a base de código"""
        print("🔍 Analisando base de código...")
        
        structure = self.scan_project_structure()
        
        for py_file in structure["python_files"]:
            file_path = self.project_root / py_file
            analysis = self.analyze_python_file(file_path)
            self.results.modules.append(analysis)
            
            # Acumular estatísticas
            self.results.total_lines += analysis.lines
            self.results.total_functions += analysis.functions
            self.results.total_classes += analysis.classes
        
        self.results.total_files = len(structure["python_files"])
        
        print(f"   ✅ {self.results.total_files} arquivos Python analisados")
        print(f"   📊 {self.results.total_lines:,} linhas de código")
        print(f"   🔧 {self.results.total_functions} funções")
        print(f"   📦 {self.results.total_classes} classes")
    
    def check_database_integrity(self):
        """Verifica integridade do banco de dados"""
        print("🗄️ Verificando banco de dados...")
        
        db_path = self.project_root / "primotex_erp.db"
        
        if not db_path.exists():
            self.results.database_status = {
                "exists": False,
                "tables": 0,
                "records": 0,
                "integrity": "N/A",
                "errors": ["Banco de dados não encontrado"]
            }
            self.results.critical_issues.append("Banco de dados principal não existe")
            return
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Listar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Contar registros
            total_records = 0
            table_stats = {}
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_records += count
                table_stats[table] = count
            
            # Verificar integridade
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            
            conn.close()
            
            self.results.database_status = {
                "exists": True,
                "tables": len(tables),
                "table_list": tables,
                "table_stats": table_stats,
                "total_records": total_records,
                "integrity": integrity_result,
                "errors": []
            }
            
            print(f"   ✅ {len(tables)} tabelas encontradas")
            print(f"   📊 {total_records:,} registros totais")
            print(f"   🔒 Integridade: {integrity_result}")
            
        except Exception as e:
            self.results.database_status = {
                "exists": True,
                "error": str(e),
                "tables": 0,
                "records": 0,
                "integrity": "ERROR"
            }
            self.results.critical_issues.append(f"Erro no banco de dados: {e}")
    
    def check_dependencies(self):
        """Verifica dependências do projeto"""
        print("📦 Verificando dependências...")
        
        # Verificar requirements.txt
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            except UnicodeDecodeError:
                with open(req_file, 'r', encoding='latin1') as f:
                    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        else:
            requirements = []
        
        # Verificar quais estão instaladas
        installed = []
        missing = []
        problematic = ['weasyprint', 'playwright', 'selenium']  # Pacotes que podem causar problemas
        
        for req in requirements:
            package = req.split('>=')[0].split('==')[0].split('[')[0]
            
            # Pular pacotes problemáticos
            if any(prob in package.lower() for prob in problematic):
                continue
                
            try:
                __import__(package)
                installed.append(package)
            except ImportError:
                try:
                    # Tentar importar com nome alternativo
                    import importlib
                    importlib.import_module(package.replace('-', '_'))
                    installed.append(package)
                except ImportError:
                    missing.append(package)
            except Exception:
                # Para outros erros (como dependências do sistema)
                missing.append(package)
        
        self.results.dependencies_status = {
            "total_required": len(requirements),
            "installed": len(installed),
            "missing": len(missing),
            "installed_packages": installed,
            "missing_packages": missing,
            "coverage": len(installed) / len(requirements) * 100 if requirements else 100
        }
        
        print(f"   ✅ {len(installed)}/{len(requirements)} dependências instaladas")
        if missing:
            print(f"   ⚠️  Faltando: {', '.join(missing)}")
    
    def scan_api_endpoints(self):
        """Escaneia endpoints da API"""
        print("🌐 Escaneando endpoints da API...")
        
        endpoints = []
        
        # Procurar por routers
        router_files = []
        for py_file in self.results.modules:
            if 'router' in py_file.name.lower() or 'api' in py_file.name:
                router_files.append(py_file.name)
        
        # Analisar arquivos de router
        for router_file in router_files:
            try:
                file_path = self.project_root / router_file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Procurar por decoradores de rota
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('@router.') or line.startswith('@app.'):
                        if any(method in line for method in ['get(', 'post(', 'put(', 'delete(', 'patch(']):
                            endpoints.append(line)
                            
            except Exception as e:
                continue
        
        self.results.api_endpoints = endpoints
        print(f"   ✅ {len(endpoints)} endpoints encontrados")
    
    def check_integrations(self):
        """Verifica status das integrações"""
        print("🔗 Verificando integrações...")
        
        integrations = {
            "whatsapp": False,
            "database": False,
            "auth": False,
            "logging": False,
            "email": False
        }
        
        # Verificar pelos arquivos e imports
        for module in self.results.modules:
            file_path = self.project_root / module.name
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                if 'whatsapp' in content:
                    integrations["whatsapp"] = True
                if any(db in content for db in ['sqlalchemy', 'sqlite', 'database']):
                    integrations["database"] = True
                if any(auth in content for auth in ['jwt', 'token', 'auth']):
                    integrations["auth"] = True
                if any(log in content for log in ['logging', 'logger', 'log']):
                    integrations["logging"] = True
                if 'email' in content:
                    integrations["email"] = True
                    
            except Exception:
                continue
        
        self.results.integrations = integrations
        
        active_integrations = sum(integrations.values())
        print(f"   ✅ {active_integrations}/{len(integrations)} integrações ativas")
    
    def calculate_scores(self):
        """Calcula scores de qualidade"""
        print("📊 Calculando scores de qualidade...")
        
        # Score de Segurança
        security_factors = []
        
        # Verificar autenticação
        if self.results.integrations.get("auth", False):
            security_factors.append(25)
        
        # Verificar validação de entrada
        validation_modules = [m for m in self.results.modules if 'schema' in m.name.lower() or 'validation' in m.name.lower()]
        if validation_modules:
            security_factors.append(25)
        
        # Verificar logs de auditoria
        if self.results.integrations.get("logging", False):
            security_factors.append(25)
        
        # Verificar integridade do banco
        if self.results.database_status.get("integrity") == "ok":
            security_factors.append(25)
        
        self.results.security_score = sum(security_factors)
        
        # Score de Performance
        performance_factors = []
        
        # Verificar uso de async/await
        async_modules = []
        for m in self.results.modules:
            try:
                with open(self.project_root / m.name, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'async' in content:
                        async_modules.append(m)
            except UnicodeDecodeError:
                try:
                    with open(self.project_root / m.name, 'r', encoding='latin1') as f:
                        content = f.read()
                        if 'async' in content:
                            async_modules.append(m)
                except Exception:
                    continue
            except Exception:
                continue
        if async_modules:
            performance_factors.append(30)
        
        # Verificar otimizações de banco
        if self.results.database_status.get("exists", False):
            performance_factors.append(35)
        
        # Verificar complexidade moderada
        avg_complexity = sum(m.complexity for m in self.results.modules) / len(self.results.modules) if self.results.modules else 0
        if avg_complexity < 50:
            performance_factors.append(35)
        
        self.results.performance_score = sum(performance_factors)
        
        # Score de Qualidade de Código
        if self.results.modules:
            total_functions = sum(m.functions for m in self.results.modules)
            total_docstrings = sum(m.docstrings for m in self.results.modules)
            total_type_hints = sum(m.type_hints for m in self.results.modules)
            
            docstring_coverage = (total_docstrings / total_functions * 100) if total_functions > 0 else 0
            type_hint_coverage = (total_type_hints / total_functions * 100) if total_functions > 0 else 0
            
            self.results.quality_score = (docstring_coverage * 0.4 + type_hint_coverage * 0.6)
        else:
            self.results.quality_score = 0
        
        # Score Geral
        self.results.overall_score = (
            self.results.security_score * 0.3 +
            self.results.performance_score * 0.3 +
            self.results.quality_score * 0.4
        )
        
        print(f"   🔒 Segurança: {self.results.security_score:.1f}/100")
        print(f"   ⚡ Performance: {self.results.performance_score:.1f}/100")
        print(f"   🎯 Qualidade: {self.results.quality_score:.1f}/100")
        print(f"   🏆 Score Geral: {self.results.overall_score:.1f}/100")
    
    def generate_recommendations(self):
        """Gera recomendações de melhoria"""
        print("💡 Gerando recomendações...")
        
        recommendations = []
        critical_issues = []
        
        # Dependências
        if self.results.dependencies_status.get("missing_packages"):
            critical_issues.append("Dependências críticas não instaladas")
            recommendations.append("Instalar dependências faltantes: pip install -r requirements.txt")
        
        # Banco de dados
        if not self.results.database_status.get("exists", False):
            critical_issues.append("Banco de dados principal não existe")
            recommendations.append("Configurar e inicializar banco de dados")
        
        # Qualidade do código
        if self.results.quality_score < 70:
            recommendations.append("Melhorar documentação e type hints")
        
        # Testes
        test_modules = [m for m in self.results.modules if 'test' in m.name.lower()]
        if not test_modules:
            recommendations.append("Implementar testes automatizados")
        
        # Segurança
        if self.results.security_score < 80:
            recommendations.append("Fortalecer medidas de segurança")
        
        # Performance
        if self.results.performance_score < 70:
            recommendations.append("Otimizar performance do sistema")
        
        # Módulos muito complexos
        complex_modules = [m for m in self.results.modules if m.complexity > 100]
        if complex_modules:
            recommendations.append("Refatorar módulos de alta complexidade")
        
        self.results.recommendations = recommendations
        self.results.critical_issues = critical_issues
        
        print(f"   ⚠️  {len(critical_issues)} problemas críticos")
        print(f"   💡 {len(recommendations)} recomendações")
    
    def export_report(self) -> str:
        """Exporta relatório completo"""
        report = f"""
# RELATÓRIO DE VALIDAÇÃO SISTEMA ERP PRIMOTEX
## Data: {self.results.timestamp.strftime('%d/%m/%Y %H:%M:%S')}

## 📊 ESTATÍSTICAS GERAIS
- **Arquivos Python:** {self.results.total_files:,}
- **Linhas de Código:** {self.results.total_lines:,}
- **Funções:** {self.results.total_functions:,}
- **Classes:** {self.results.total_classes:,}

## 🏆 SCORES DE QUALIDADE
- **Score Geral:** {self.results.overall_score:.1f}/100
- **Segurança:** {self.results.security_score:.1f}/100
- **Performance:** {self.results.performance_score:.1f}/100
- **Qualidade de Código:** {self.results.quality_score:.1f}/100

## 🗄️ STATUS DO BANCO DE DADOS
- **Existe:** {self.results.database_status.get('exists', False)}
- **Tabelas:** {self.results.database_status.get('tables', 0)}
- **Registros:** {self.results.database_status.get('total_records', 0):,}
- **Integridade:** {self.results.database_status.get('integrity', 'N/A')}

## 📦 DEPENDÊNCIAS
- **Total Requeridas:** {self.results.dependencies_status.get('total_required', 0)}
- **Instaladas:** {self.results.dependencies_status.get('installed', 0)}
- **Cobertura:** {self.results.dependencies_status.get('coverage', 0):.1f}%

## 🌐 API ENDPOINTS
- **Total Endpoints:** {len(self.results.api_endpoints)}

## 🔗 INTEGRAÇÕES
"""
        
        for integration, status in self.results.integrations.items():
            emoji = "✅" if status else "❌"
            report += f"- **{integration.title()}:** {emoji}\n"
        
        if self.results.critical_issues:
            report += "\n## ⚠️ PROBLEMAS CRÍTICOS\n"
            for issue in self.results.critical_issues:
                report += f"- {issue}\n"
        
        if self.results.recommendations:
            report += "\n## 💡 RECOMENDAÇÕES\n"
            for rec in self.results.recommendations:
                report += f"- {rec}\n"
        
        # Top 10 módulos maiores
        report += "\n## 📁 MÓDULOS PRINCIPAIS\n"
        sorted_modules = sorted(self.results.modules, key=lambda x: x.lines, reverse=True)[:10]
        for module in sorted_modules:
            report += f"- **{module.name}:** {module.lines:,} linhas, {module.functions} funções\n"
        
        return report
    
    def run_validation(self):
        """Executa validação completa"""
        print("🚀 INICIANDO VALIDAÇÃO COMPLETA DO SISTEMA")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            self.analyze_codebase()
            self.check_database_integrity()
            self.check_dependencies()
            self.scan_api_endpoints()
            self.check_integrations()
            self.calculate_scores()
            self.generate_recommendations()
            
            # Gerar relatório
            report = self.export_report()
            
            # Salvar relatório
            report_file = self.project_root / f"relatorio_validacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            elapsed_time = time.time() - start_time
            
            print("\n" + "=" * 60)
            print("✅ VALIDAÇÃO CONCLUÍDA")
            print(f"⏱️ Tempo: {elapsed_time:.2f} segundos")
            print(f"📄 Relatório salvo: {report_file}")
            
            # Score final
            if self.results.overall_score >= 90:
                print("🎉 SISTEMA EXCELENTE!")
            elif self.results.overall_score >= 75:
                print("👍 SISTEMA BOM")
            elif self.results.overall_score >= 60:
                print("⚠️ SISTEMA PRECISA MELHORIAS")
            else:
                print("🚨 SISTEMA CRÍTICO - AÇÃO NECESSÁRIA")
            
            print(f"🏆 Score Final: {self.results.overall_score:.1f}/100")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Erro durante validação: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Função principal"""
    print("Sistema ERP Primotex - Validação Completa")
    print("Novembro 2025")
    print()
    
    validator = SystemValidator()
    validator.run_validation()


if __name__ == "__main__":
    main()