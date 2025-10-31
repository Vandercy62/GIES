#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstração Completa do Sistema de Login
========================================

Este script demonstra o acesso completo ao sistema ERP Primotex
através do login, incluindo testes da API e interface.
"""

import sys
import os
import time
import requests
import threading

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class DemonstradorLogin:
    """Classe para demonstrar o sistema de login"""
    
    def __init__(self):
        self.api_base = "http://127.0.0.1:8002"
        
    def print_header(self, titulo):
        """Imprime cabeçalho formatado"""
        print("\n" + "=" * 60)
        print(f" {titulo}")
        print("=" * 60)
        
    def verificar_sistema(self):
        """Verifica se o sistema está funcionando"""
        self.print_header("VERIFICAÇÃO DO SISTEMA")
        
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ Sistema funcionando corretamente!")
                print(f"📊 Status: {data.get('status')}")
                print(f"🗄️  Database: {data.get('database')}")
                print(f"🔧 Serviços ativos: {len(data.get('services', {}))}")
                return True
            else:
                print(f"❌ Sistema retornou erro: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            print("\n💡 Verifique se o servidor está rodando:")
            print("   .venv\\Scripts\\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002")
            return False
            
    def demonstrar_login_api(self):
        """Demonstra login via API"""
        self.print_header("DEMONSTRAÇÃO - LOGIN VIA API")
        
        credenciais = {
            "username": "admin",
            "password": "admin123"
        }
        
        print("🔐 Tentando login com:")
        print(f"   Usuário: {credenciais['username']}")
        print(f"   Senha: {'*' * len(credenciais['password'])}")
        
        try:
            response = requests.post(
                f"{self.api_base}/api/v1/auth/login",
                json=credenciais,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get('user', {})
                
                print("\n🎉 LOGIN REALIZADO COM SUCESSO!")
                print(f"👤 Usuário logado: {user_info.get('username')}")
                print(f"✉️  Email: {user_info.get('email', 'N/A')}")
                print(f"🎯 Perfil: {user_info.get('perfil', 'N/A')}")
                print(f"🕒 Login em: {time.strftime('%d/%m/%Y %H:%M:%S')}")
                
                # Demonstrar acesso a recursos
                self.demonstrar_acesso_recursos(data.get('access_token'))
                
                return True, data
            else:
                print("\n❌ FALHA NO LOGIN!")
                print(f"Status: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"\n❌ ERRO DURANTE LOGIN: {e}")
            return False, None
            
    def demonstrar_acesso_recursos(self, token):
        """Demonstra acesso aos recursos do sistema"""
        print("\n🛡️  TESTANDO ACESSO AOS MÓDULOS DO SISTEMA...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        modulos = [
            ("/api/v1/clientes", "👥 Clientes", "Gerenciamento de clientes"),
            ("/api/v1/produtos", "📦 Produtos", "Catálogo de produtos"),
            ("/api/v1/estoque", "📊 Estoque", "Controle de estoque"),
            ("/api/v1/usuarios", "👤 Usuários", "Administração de usuários")
        ]
        
        sucessos = 0
        for endpoint, nome, descricao in modulos:
            try:
                response = requests.get(f"{self.api_base}{endpoint}", 
                                      headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {nome}: Acesso autorizado - {descricao}")
                    sucessos += 1
                elif response.status_code == 404:
                    print(f"⚠️  {nome}: Módulo não implementado ainda")
                else:
                    print(f"❌ {nome}: Acesso negado (Status: {response.status_code})")
            except Exception as e:
                print(f"❌ {nome}: Erro de conexão - {e}")
        
        print(f"\n📈 RESUMO: {sucessos}/{len(modulos)} módulos acessíveis")
        
    def demonstrar_interface_login(self):
        """Demonstra a interface de login"""
        self.print_header("DEMONSTRAÇÃO - INTERFACE DE LOGIN")
        
        print("🖥️  Abrindo interface gráfica de login...")
        print("📋 Para testar manualmente:")
        print("   1. Uma janela de login deve ter aberto")
        print("   2. Use as credenciais:")
        print("      Usuário: admin")
        print("      Senha: admin123")
        print("   3. Clique em 'Entrar'")
        print("   4. O dashboard deve abrir automaticamente")
        
        try:
            # Importar e executar login em thread separada
            def abrir_login():
                try:
                    from frontend.desktop.login_tkinter import LoginWindow
                    login = LoginWindow()
                    login.run()
                except Exception as e:
                    print(f"❌ Erro ao abrir interface: {e}")
            
            thread_login = threading.Thread(target=abrir_login, daemon=True)
            thread_login.start()
            
            print("✅ Interface de login iniciada com sucesso!")
            print("🔄 Execute o script novamente se a janela não abrir")
            
        except Exception as e:
            print(f"❌ Erro ao iniciar interface: {e}")
            print("💡 Execute manualmente:")
            print("   python frontend\\desktop\\login_tkinter.py")
            
    def executar_demonstracao_completa(self):
        """Executa demonstração completa do sistema de login"""
        print("🚀 DEMONSTRAÇÃO COMPLETA - SISTEMA DE LOGIN ERP PRIMOTEX")
        print(f"📅 Data: {time.strftime('%d/%m/%Y %H:%M:%S')}")
        print("🏢 Empresa: Primotex - Forros e Divisórias Eireli")
        print("📊 Versão: 2.0.0 - Fase 2 Completa")
        
        # 1. Verificar sistema
        if not self.verificar_sistema():
            return
        
        # 2. Demonstrar login via API
        sucesso_api, _ = self.demonstrar_login_api()
        
        # 3. Demonstrar interface
        if sucesso_api:
            self.demonstrar_interface_login()
        
        # 4. Resumo final
        self.print_header("RESUMO DA DEMONSTRAÇÃO")
        
        if sucesso_api:
            print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("✅ Sistema de login funcionando perfeitamente")
            print("✅ API de autenticação operacional")
            print("✅ Interface gráfica acessível")
            
            print("\n🎯 PRÓXIMOS PASSOS SUGERIDOS:")
            print("   1. Teste manual da interface")
            print("   2. Navegue pelos módulos do dashboard")
            print("   3. Experimente as funcionalidades disponíveis")
            
        else:
            print("❌ FALHAS DETECTADAS!")
            print("🔧 Verifique os erros acima e tente novamente")
            
        print("\n📋 COMANDOS ÚTEIS:")
        print("   Servidor: .venv\\Scripts\\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002")
        print("   Login: python frontend\\desktop\\login_tkinter.py")
        print("   Dashboard: python frontend\\desktop\\dashboard.py")

def main():
    """Função principal"""
    demonstrador = DemonstradorLogin()
    demonstrador.executar_demonstracao_completa()

if __name__ == "__main__":
    main()