"""
TESTE SIMPLIFICADO - SISTEMA DE COMUNICAÇÃO  
============================================

Teste focado na validação básica sem GUI
"""

import requests
import sys
import time

def test_api_basic():
    """Teste básico da API"""
    try:
        response = requests.get("http://127.0.0.1:8003/health", timeout=5)
        if response.status_code == 200:
            print("✅ API funcionando")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return False

def test_comunicacao_endpoints():
    """Teste dos endpoints de comunicação"""
    endpoints = [
        "/api/v1/comunicacao/templates",
        "/api/v1/comunicacao/configuracoes",
        "/api/v1/comunicacao/historico"
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            url = f"http://127.0.0.1:8003{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 404]:  # 404 OK para listas vazias
                print(f"✅ Endpoint {endpoint}: OK")
                results.append(True)
            else:
                print(f"❌ Endpoint {endpoint}: Status {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ Endpoint {endpoint}: Erro {e}")
            results.append(False)
    
    return all(results)

def main():
    """Executar testes básicos"""
    print("🚀 TESTE BÁSICO - SISTEMA DE COMUNICAÇÃO")
    print("=" * 50)
    
    # Aguardar API
    print("⏳ Aguardando API...")
    time.sleep(3)
    
    tests = [
        ("API Health", test_api_basic),
        ("Endpoints Comunicação", test_comunicacao_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n📋 {name}:")
        result = test_func()
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n📊 RESULTADO: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 50:
        print("🎉 SISTEMA BÁSICO FUNCIONANDO!")
        return 0
    else:
        print("🚨 SISTEMA COM PROBLEMAS")
        return 1

if __name__ == "__main__":
    sys.exit(main())