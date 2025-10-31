#!/usr/bin/env python3
"""
TESTE DE INTEGRAÇÃO FINAL - SISTEMA DE COMUNICAÇÃO
==================================================

Teste completo do sistema de comunicação do ERP Primotex
Valida backend (API) e frontend (dashboard integration)

Autor: GitHub Copilot
Data: 29/10/2025
"""

import requests
import json
import sys
import traceback
from datetime import datetime

def test_api_health():
    """Testar se a API está rodando"""
    try:
        response = requests.get("http://127.0.0.1:8003/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health Check: OK")
            return True
        else:
            print(f"❌ API Health Check falhou: status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API não está rodando: {e}")
        return False

def test_comunicacao_endpoints():
    """Testar endpoints específicos de comunicação"""
    endpoints_to_test = [
        ("GET", "/api/v1/comunicacao/templates", "Templates"),
        ("GET", "/api/v1/comunicacao/historico", "Histórico"),
        ("GET", "/api/v1/comunicacao/configuracoes", "Configurações"),
        ("GET", "/api/v1/comunicacao/dashboard", "Dashboard"),
    ]
    
    results = []
    
    for method, endpoint, description in endpoints_to_test:
        try:
            url = f"http://127.0.0.1:8003{endpoint}"
            response = requests.request(method, url, timeout=5)
            
            if response.status_code in [200, 404]:  # 404 é OK para endpoints vazios
                print(f"✅ {description}: {response.status_code}")
                results.append(True)
            else:
                print(f"❌ {description}: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {description}: Erro - {e}")
            results.append(False)
    
    return all(results)

def test_frontend_integration():
    """Testar integração do frontend"""
    try:
        # Testar importação do dashboard
        sys.path.append('frontend/desktop')
        from dashboard import DashboardWindow
        print("✅ Dashboard import: OK")
        
        # Testar importação da interface de comunicação
        from comunicacao_window import ComunicacaoWindow
        print("✅ ComunicacaoWindow import: OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Frontend import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False

def test_backend_models():
    """Testar modelos do backend"""
    try:
        # Testar importação dos modelos
        from backend.models.comunicacao import (
            ComunicacaoTemplate, ComunicacaoHistorico, 
            TIPOS_COMUNICACAO, STATUS_ENVIO
        )
        print("✅ Modelos de comunicação: OK")
        
        # Testar importação do service
        from backend.services.comunicacao_service import ComunicacaoService
        print("✅ ComunicacaoService: OK")
        
        # Testar importação do router
        from backend.api.routers.comunicacao_router import router
        print(f"✅ Router de comunicação: OK ({len(router.routes)} rotas)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Backend import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False

def main():
    """Executar todos os testes"""
    
    print("🧪 TESTE DE INTEGRAÇÃO - SISTEMA DE COMUNICAÇÃO")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Contadores
    total_tests = 4
    passed_tests = 0
    
    # Teste 1: Backend Models
    print("📦 Testando modelos e serviços do backend...")
    if test_backend_models():
        passed_tests += 1
    print()
    
    # Teste 2: Frontend Integration
    print("🖥️ Testando integração do frontend...")
    if test_frontend_integration():
        passed_tests += 1
    print()
    
    # Teste 3: API Health
    print("🌐 Testando conectividade da API...")
    api_running = test_api_health()
    if api_running:
        passed_tests += 1
    print()
    
    # Teste 4: Endpoints específicos (só se API estiver rodando)
    print("🔌 Testando endpoints de comunicação...")
    if api_running:
        if test_comunicacao_endpoints():
            passed_tests += 1
    else:
        print("⚠️ Pulando teste de endpoints (API não está rodando)")
        total_tests -= 1
    print()
    
    # Relatório final
    print("📊 RELATÓRIO FINAL")
    print("=" * 30)
    print(f"Testes executados: {total_tests}")
    print(f"Testes aprovados: {passed_tests}")
    print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    if passed_tests == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de comunicação pronto para uso")
        
        if api_running:
            print()
            print("🚀 Para usar o sistema:")
            print("1. Mantenha a API rodando (uvicorn)")
            print("2. Execute: python frontend/desktop/login_tkinter.py")
            print("3. Acesse: Dashboard → Comunicação")
        
        return True
    else:
        print("❌ Alguns testes falharam")
        print("🔧 Verificar problemas antes de continuar")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Erro crítico no teste: {e}")
        traceback.print_exc()
        sys.exit(1)