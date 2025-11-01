"""
SISTEMA ERP PRIMOTEX - TESTE FINAL DA FASE 1
===========================================

Script completo para testar todas as funcionalidades da Fase 1.
Validação de banco de dados, autenticação e APIs.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import requests
import json
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8002"

def test_health_check():
    """Testar endpoint de saúde"""
    print("📊 Testando health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   📊 Database: {data.get('database')}")
            return True
        else:
            print(f"   ❌ Erro: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return False

def test_login():
    """Testar login e obter token"""
    print("🔐 Testando login...")
    
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user", {})
            
            print(f"   ✅ Login realizado com sucesso!")
            print(f"   👤 Usuário: {user.get('username')}")
            print(f"   📧 Email: {user.get('email')}")
            print(f"   🔑 Token: {token[:30]}...")
            
            return token
        else:
            print(f"   ❌ Erro no login: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return None

def test_protected_endpoint(token):
    """Testar endpoint protegido"""
    print("🔒 Testando endpoint protegido...")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Perfil obtido com sucesso!")
            print(f"   👤 Nome: {data.get('nome_completo')}")
            print(f"   🎭 Perfil: {data.get('perfil')}")
            return True
        else:
            print(f"   ❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return False

def test_database_models():
    """Testar modelos do banco de dados"""
    print("🗃️ Testando modelos do banco...")
    
    try:
        from backend.models import ALL_MODELS, validate_models
        
        models_info = validate_models()
        
        print(f"   ✅ {len(ALL_MODELS)} modelos carregados:")
        
        for model_name, info in models_info.items():
            print(f"      📋 {model_name}: {info['columns']} colunas")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao testar modelos: {e}")
        return False

def test_client_endpoints(token):
    """Testar endpoints de clientes"""
    print("👥 Testando endpoints de clientes...")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Testar listagem de clientes
        response = requests.get(
            f"{BASE_URL}/api/v1/clientes",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "total" in data and "clientes" in data:
                total = data["total"]
                clientes = data["clientes"]
                print(f"   ✅ Listagem funcionando: {total} clientes")
                print(f"   📊 Paginação: {len(clientes)} registros retornados")
                return True
            else:
                print(f"   ❌ Resposta inesperada: {data}")
                return False
        else:
            print(f"   ❌ Erro na listagem: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return False

def test_api_documentation():
    """Testar documentação da API"""
    print("📚 Testando documentação da API...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        
        if response.status_code == 200:
            print("   ✅ Documentação Swagger acessível")
            return True
        else:
            print(f"   ❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return False

def main():
    """Função principal de teste"""
    print("=" * 60)
    print("🧪 SISTEMA ERP PRIMOTEX - TESTE FINAL DA FASE 1")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 6
    
    # 1. Teste de saúde
    if test_health_check():
        tests_passed += 1
    
    # 2. Teste de modelos
    if test_database_models():
        tests_passed += 1
    
    # 3. Teste de login
    token = test_login()
    if token:
        tests_passed += 1
        
        # 4. Teste de endpoint protegido
        if test_protected_endpoint(token):
            tests_passed += 1
            
        # 5. Teste de clientes
        if test_client_endpoints(token):
            tests_passed += 1
    else:
        print("   ⚠️ Pulando testes que requerem autenticação")
    
    # 6. Teste de documentação
    if test_api_documentation():
        tests_passed += 1
    
    # Resultado final
    print("\n" + "=" * 60)
    print(f"📊 RESULTADO FINAL: {tests_passed}/{total_tests} testes passaram")
    
    if tests_passed == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ FASE 1 - FUNDAÇÃO CONCLUÍDA COM SUCESSO!")
        
        print("\n🔧 Funcionalidades implementadas:")
        print("   • Banco de dados SQLAlchemy + SQLite")
        print("   • Sistema de autenticação JWT")
        print("   • APIs REST com FastAPI")
        print("   • Modelos de dados completos")
        print("   • Documentação automática")
        print("   • Validação e serialização")
        print("   • Sistema de permissões")
        print("   • Endpoints de administração")
        
        print("\n🚀 Próximas etapas (Fase 2):")
        print("   • Interface desktop PyQt6")
        print("   • Módulo de produtos completo")
        print("   • Sistema de estoque")
        print("   • Geração de códigos de barras")
        print("   • Relatórios básicos")
        
        return True
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("⚠️ Revisar implementação antes de prosseguir")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)