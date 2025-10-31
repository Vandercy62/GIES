#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simples de Login - Sistema ERP Primotex
============================================

Teste rápido do sistema de login com interface real.
"""

import sys
import os
import time
import requests

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def testar_api():
    """Testa conexão com a API"""
    print("🔧 Testando conexão com API...")
    try:
        response = requests.get("http://127.0.0.1:8002/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API respondendo: {data.get('status')}")
            print(f"📊 Database: {data.get('database')}")
            return True
        else:
            print(f"❌ API retornou status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def testar_autenticacao():
    """Testa autenticação"""
    print("\n🔐 Testando autenticação...")
    
    # Credenciais do admin
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8002/api/v1/auth/login",
            json=credentials,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login bem-sucedido!")
            print(f"👤 Usuário: {data.get('user', {}).get('username')}")
            print(f"🎫 Token: {data.get('access_token', '')[:50]}...")
            print(f"🔒 Perfil: {data.get('user', {}).get('perfil', 'N/A')}")
            return True, data
        else:
            print(f"❌ Falha no login: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Erro durante login: {e}")
        return False, None

def testar_acesso_recursos(token):
    """Testa acesso a recursos protegidos"""
    print("\n🛡️  Testando acesso a recursos protegidos...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Testar diferentes endpoints
    endpoints = [
        ("/api/v1/clientes", "Clientes"),
        ("/api/v1/produtos", "Produtos"),
        ("/api/v1/estoque", "Estoque")
    ]
    
    sucessos = 0
    for endpoint, nome in endpoints:
        try:
            response = requests.get(f"http://127.0.0.1:8002{endpoint}", 
                                  headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ {nome}: Acesso autorizado")
                sucessos += 1
            else:
                print(f"❌ {nome}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {nome}: Erro {e}")
    
    print(f"\n📈 Recursos acessíveis: {sucessos}/{len(endpoints)}")
    return sucessos == len(endpoints)

def main():
    """Função principal do teste"""
    print("🚀 TESTE DE ACESSO AO SISTEMA ERP PRIMOTEX")
    print("=" * 50)
    print(f"📅 Data: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # 1. Testar API
    if not testar_api():
        print("\n❌ FALHA: API não está respondendo")
        print("\n💡 Para iniciar o servidor:")
        print("   .venv\\Scripts\\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002")
        return
    
    # 2. Testar autenticação
    sucesso_login, dados_usuario = testar_autenticacao()
    if not sucesso_login:
        print("\n❌ FALHA: Não foi possível fazer login")
        return
    
    # 3. Testar acesso a recursos
    token = dados_usuario.get("access_token")
    if testar_acesso_recursos(token):
        print("\n🎉 SUCESSO: Todos os testes passaram!")
        print("✅ Sistema de login está funcionando perfeitamente")
    else:
        print("\n⚠️  PARCIAL: Login OK, mas alguns recursos inacessíveis")
    
    # 4. Instruções para teste manual
    print("\n" + "=" * 50)
    print("🖥️  TESTE MANUAL RECOMENDADO:")
    print("   python frontend\\desktop\\login_tkinter.py")
    print("\n🔑 CREDENCIAIS DE TESTE:")
    print("   Usuário: admin")
    print("   Senha: admin123")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("   1. Execute o login manual acima")
    print("   2. Verifique se a interface abre corretamente")
    print("   3. Teste a navegação no dashboard")

if __name__ == "__main__":
    main()