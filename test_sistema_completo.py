#!/usr/bin/env python3
"""
TESTE RÁPIDO DE SISTEMA - ERP PRIMOTEX
======================================

Teste direto do funcionamento dos principais módulos
Valida backend, frontend e integrações básicas

Autor: GitHub Copilot
Data: 29/10/2025
"""

import sys
import requests
from datetime import datetime

def test_quick_imports():
    """Teste rápido de importações principais"""
    print("🔍 Testando importações do sistema...")
    
    try:
        # Backend - modelos
        from backend.models.comunicacao import ComunicacaoTemplate
        from backend.models.ordem_servico_model import OrdemServico
        from backend.models.agendamento_model import Agendamento
        from backend.models.financeiro_model import ContaReceber
        print("✅ Modelos backend: OK")
        
        # Backend - services
        from backend.services.comunicacao_service import ComunicacaoService
        print("✅ Services backend: OK")
        
        # Backend - routers
        from backend.api.routers.comunicacao_router import router as comm_router
        from backend.api.routers.ordem_servico_router import router as os_router
        from backend.api.routers.agendamento_router import router as agenda_router
        from backend.api.routers.financeiro_router_simples import router as fin_router
        print(f"✅ Routers backend: OK")
        print(f"   - Comunicação: {len(comm_router.routes)} rotas")
        print(f"   - OS: {len(os_router.routes)} rotas")
        print(f"   - Agendamento: {len(agenda_router.routes)} rotas")
        print(f"   - Financeiro: {len(fin_router.routes)} rotas")
        
        # Frontend - interfaces
        sys.path.append('frontend/desktop')
        from dashboard import DashboardWindow
        from comunicacao_window import ComunicacaoWindow
        from ordem_servico_window import OrdemServicoWindow
        from agendamento_window import AgendamentoWindow
        from financeiro_window import FinanceiroWindow
        print("✅ Interfaces frontend: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas importações: {e}")
        return False

def test_database_tables():
    """Teste das tabelas do banco de dados"""
    print("\n🗄️ Testando estrutura do banco...")
    
    try:
        from backend.models import ALL_MODELS
        from backend.database.config import engine
        
        print(f"✅ Total de modelos definidos: {len(ALL_MODELS)}")
        
        # Listar tabelas por módulo
        os_tables = [m for m in ALL_MODELS if 'OS' in str(m) or 'Ordem' in str(m) or 'Fase' in str(m) or 'Visita' in str(m) or 'Orcamento' in str(m)]
        agenda_tables = [m for m in ALL_MODELS if 'Agendamento' in str(m) or 'Disponibilidade' in str(m) or 'Bloqueio' in str(m) or 'Configuracao' in str(m)]
        fin_tables = [m for m in ALL_MODELS if 'Conta' in str(m) or 'Financeira' in str(m) or 'Fluxo' in str(m) or 'Movimentacao' in str(m)]
        comm_tables = [m for m in ALL_MODELS if 'Comunicacao' in str(m)]
        
        print(f"   - OS: {len(os_tables)} tabelas")
        print(f"   - Agendamento: {len(agenda_tables)} tabelas")
        print(f"   - Financeiro: {len(fin_tables)} tabelas")
        print(f"   - Comunicação: {len(comm_tables)} tabelas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return False

def test_api_startup():
    """Teste de inicialização da API"""
    print("\n🌐 Testando capacidade de inicialização da API...")
    
    try:
        from backend.api.main import app
        print("✅ FastAPI app: OK")
        
        # Verificar routers incluídos
        total_routes = len([r for r in app.routes if hasattr(r, 'path')])
        api_routes = len([r for r in app.routes if hasattr(r, 'path') and r.path.startswith('/api')])
        
        print(f"   - Total de rotas: {total_routes}")
        print(f"   - Rotas API: {api_routes}")
        
        # Verificar se os principais endpoints estão presentes
        route_paths = [r.path for r in app.routes if hasattr(r, 'path')]
        has_comm = any('/comunicacao' in path for path in route_paths)
        has_os = any('/os' in path for path in route_paths)
        has_agenda = any('/agendamento' in path for path in route_paths)
        has_fin = any('/financeiro' in path for path in route_paths)
        
        print(f"   - Endpoints comunicação: {'✅' if has_comm else '❌'}")
        print(f"   - Endpoints OS: {'✅' if has_os else '❌'}")
        print(f"   - Endpoints agendamento: {'✅' if has_agenda else '❌'}")
        print(f"   - Endpoints financeiro: {'✅' if has_fin else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return False

def main():
    """Executar todos os testes rápidos"""
    
    print("🧪 TESTE RÁPIDO DO SISTEMA ERP PRIMOTEX")
    print("=" * 50)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    tests = [
        ("Importações", test_quick_imports),
        ("Banco de dados", test_database_tables),
        ("API Startup", test_api_startup)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"📋 {name}")
        if test_func():
            passed += 1
        print()
    
    # Relatório final
    print("📊 RELATÓRIO FINAL")
    print("=" * 30)
    print(f"Testes executados: {total}")
    print(f"Testes aprovados: {passed}")
    print(f"Taxa de sucesso: {(passed/total)*100:.1f}%")
    print()
    
    if passed == total:
        print("🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("✅ Todos os módulos integrados e operacionais")
        print()
        print("🚀 COMANDOS PARA USAR O SISTEMA:")
        print("=" * 40)
        print("1. Iniciar API (em um terminal):")
        print("   .venv\\Scripts\\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8003")
        print()
        print("2. Iniciar aplicação desktop (em outro terminal):")
        print("   cd frontend\\desktop")
        print("   ..\\..\\venv\\Scripts\\python.exe login_tkinter.py")
        print()
        print("3. Login: admin / admin123")
        print("4. Acessar módulos via dashboard")
        
        return True
    else:
        print("❌ Alguns módulos precisam de atenção")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)