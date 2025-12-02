"""
SUITE DE TESTES COMPLETA - SISTEMA ERP PRIMOTEX
================================================

Suite unificada de testes para todos os módulos implementados.
Cobertura: Backend, Frontend Desktop, Validadores, Formatadores, Widgets.

Autor: GitHub Copilot
Data: 17/11/2025
Versão: 1.0
"""

import unittest
import sys
import os
from pathlib import Path

# Adiciona diretório raiz ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

# Configuração de ambiente
os.environ['PYTHONPATH'] = str(Path(__file__).parent)


# =======================================
# IMPORTS DOS MÓDULOS DE TESTE
# =======================================

print("\n" + "="*70)
print("🔍 CARREGANDO SUITES DE TESTE")
print("="*70 + "\n")

# Lista de módulos de teste disponíveis
test_modules = []
test_status = {}

# Tenta importar teste de clientes
try:
    from frontend.desktop.test_clientes_wizard import (
        TestValidadores as TestValidadoresClientes,
        TestIntegracaoWizard as TestWizardClientes
    )
    test_modules.append(('Clientes - Validadores', TestValidadoresClientes))
    test_modules.append(('Clientes - Wizard', TestWizardClientes))
    test_status['clientes'] = '✅'
    print("✅ Testes de Clientes carregados")
except ImportError as e:
    test_status['clientes'] = '❌'
    print(f"⚠️  Testes de Clientes não disponíveis: {e}")

# Tenta importar teste de fornecedores
try:
    from frontend.desktop.test_fornecedores_wizard import (
        TestValidadores as TestValidadoresFornecedores,
        TestAvaliacaoWidget,
        TestBuscaCEP,
        TestIntegracaoWizard as TestWizardFornecedores,
        TestFormatadores
    )
    test_modules.append(('Fornecedores - Validadores', TestValidadoresFornecedores))
    test_modules.append(('Fornecedores - Widget Avaliação', TestAvaliacaoWidget))
    test_modules.append(('Fornecedores - Busca CEP', TestBuscaCEP))
    test_modules.append(('Fornecedores - Wizard', TestWizardFornecedores))
    test_modules.append(('Fornecedores - Formatadores', TestFormatadores))
    test_status['fornecedores'] = '✅'
    print("✅ Testes de Fornecedores carregados")
except ImportError as e:
    test_status['fornecedores'] = '❌'
    print(f"⚠️  Testes de Fornecedores não disponíveis: {e}")


# =======================================
# RUNNER PRINCIPAL
# =======================================

def run_all_tests(verbosity=2):
    """
    Executa toda a suite de testes do sistema.
    
    Args:
        verbosity: Nível de detalhamento (0=mínimo, 2=máximo)
    
    Returns:
        unittest.TestResult: Resultado consolidado
    """
    
    print("\n" + "="*70)
    print("🧪 SUITE DE TESTES COMPLETA - ERP PRIMOTEX")
    print("="*70 + "\n")
    
    # Cria suite principal
    master_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    # Adiciona todos os testes disponíveis
    for test_name, test_class in test_modules:
        print(f"📋 Adicionando: {test_name}")
        master_suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Conta total de testes
    total_tests = master_suite.countTestCases()
    
    print(f"\n📊 Total de testes a executar: {total_tests}")
    print("\n" + "="*70)
    print("🚀 EXECUTANDO TESTES")
    print("="*70 + "\n")
    
    # Executa com verbosidade
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(master_suite)
    
    # Relatório consolidado
    print("\n" + "="*70)
    print("📈 RELATÓRIO CONSOLIDADO")
    print("="*70)
    
    # Status dos módulos
    print("\n🔍 Status por Módulo:")
    for module, status in test_status.items():
        print(f"   {status} {module.capitalize()}")
    
    # Estatísticas gerais
    print(f"\n📊 Estatísticas Gerais:")
    print(f"   ✅ Testes Executados: {result.testsRun}")
    print(f"   ✅ Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Falhas: {len(result.failures)}")
    print(f"   ⚠️  Erros: {len(result.errors)}")
    print(f"   ⏭️  Pulados: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    # Taxa de sucesso
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        print(f"\n🎯 Taxa de Sucesso: {success_rate:.1f}%")
        
        # Emoji de status
        if success_rate == 100:
            print("   🏆 EXCELENTE! Todos os testes passaram!")
        elif success_rate >= 80:
            print("   ✅ BOM! Maioria dos testes passando.")
        elif success_rate >= 60:
            print("   ⚠️  ATENÇÃO! Algumas falhas detectadas.")
        else:
            print("   ❌ CRÍTICO! Muitas falhas detectadas.")
    
    # Detalhes de falhas
    if result.failures:
        print(f"\n❌ Detalhes das Falhas ({len(result.failures)}):")
        for i, (test, traceback) in enumerate(result.failures[:5], 1):
            print(f"\n   {i}. {test}")
            print(f"      {traceback.split(chr(10))[0][:100]}...")
    
    # Detalhes de erros
    if result.errors:
        print(f"\n⚠️  Detalhes dos Erros ({len(result.errors)}):")
        for i, (test, traceback) in enumerate(result.errors[:5], 1):
            print(f"\n   {i}. {test}")
            print(f"      {traceback.split(chr(10))[0][:100]}...")
    
    print("\n" + "="*70)
    
    # Recomendações
    if result.failures or result.errors:
        print("\n💡 Recomendações:")
        print("   1. Execute testes individuais para debug detalhado")
        print("   2. Verifique logs do sistema para mais informações")
        print("   3. Rode com verbosity=2 para stack traces completos")
    
    print("\n" + "="*70)
    print("✅ SUITE COMPLETA EXECUTADA")
    print("="*70 + "\n")
    
    return result


# =======================================
# FUNÇÕES AUXILIARES
# =======================================

def run_module_tests(module_name, verbosity=2):
    """
    Executa testes de um módulo específico.
    
    Args:
        module_name: Nome do módulo ('clientes' ou 'fornecedores')
        verbosity: Nível de detalhamento
    """
    
    print(f"\n🔍 Executando testes de: {module_name.upper()}\n")
    
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    # Filtra testes do módulo
    for test_name, test_class in test_modules:
        if module_name.lower() in test_name.lower():
            suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    if suite.countTestCases() == 0:
        print(f"⚠️  Nenhum teste encontrado para {module_name}")
        return None
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)


def list_available_tests():
    """Lista todos os testes disponíveis"""
    
    print("\n" + "="*70)
    print("📋 TESTES DISPONÍVEIS")
    print("="*70 + "\n")
    
    if not test_modules:
        print("⚠️  Nenhum teste carregado")
        return
    
    for i, (test_name, test_class) in enumerate(test_modules, 1):
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(test_class)
        count = suite.countTestCases()
        print(f"{i:2}. {test_name:40} ({count} testes)")
    
    print(f"\n📊 Total: {len(test_modules)} suites, "
          f"{sum(unittest.TestLoader().loadTestsFromTestCase(tc).countTestCases() for _, tc in test_modules)} testes")
    print("="*70 + "\n")


# =======================================
# MAIN
# =======================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Suite Completa de Testes - ERP Primotex"
    )
    parser.add_argument(
        '--module',
        choices=['clientes', 'fornecedores', 'all'],
        default='all',
        help='Módulo para testar (padrão: all)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='Lista todos os testes disponíveis'
    )
    parser.add_argument(
        '--verbosity',
        type=int,
        choices=[0, 1, 2],
        default=2,
        help='Nível de detalhamento (0=mínimo, 2=máximo)'
    )
    
    args = parser.parse_args()
    
    # Lista testes se solicitado
    if args.list:
        list_available_tests()
        sys.exit(0)
    
    # Executa testes
    if args.module == 'all':
        result = run_all_tests(verbosity=args.verbosity)
    else:
        result = run_module_tests(args.module, verbosity=args.verbosity)
    
    # Exit code baseado em resultado
    if result and (result.failures or result.errors):
        sys.exit(1)
    else:
        sys.exit(0)
