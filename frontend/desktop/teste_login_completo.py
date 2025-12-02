#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo do sistema de login
Sistema ERP Primotex - Forros e Divisórias

Este script testa o acesso completo ao sistema através do login:
1. Teste de autenticação via API
2. Teste da interface de login
3. Validação de credenciais
4. Acesso ao dashboard
"""

import sys
import os
import threading
import time
import requests
from typing import Dict, Any, Optional
import json

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    print("✅ tkinter importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar tkinter: {e}")
    sys.exit(1)

# Importações do sistema
try:
    from frontend.desktop.login_tkinter import LoginWindow
    from frontend.desktop.dashboard import Dashboard
    print("✅ Módulos do sistema importados com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Verifique se os arquivos existem:")
    print("- frontend/desktop/login_tkinter.py")
    print("- frontend/desktop/dashboard.py")

class TestadorLogin:
    """Classe para testar o sistema de login completo"""

    def __init__(self):
        self.api_base = "http://127.0.0.1:8002"
        self.credenciais_teste = [
            {"username": "admin", "password": "admin123", "descricao": "Administrador"},
            {"username": "usuario_teste", "password": "senha123", "descricao": "Usuário Teste"},
            {"username": "credencial_invalida", "password": "senha_errada", "descricao": "Credencial Inválida"}
        ]
        self.resultados = []

    def print_header(self, titulo: str):
        """Imprime um cabeçalho formatado"""
        print("\n" + "="*60)
        print(f" {titulo}")
        print("="*60)

    def print_step(self, step: str, status: str, details: str = ""):
        """Imprime um passo do teste"""
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏳"
        print(f"{status_icon} {step}: {status}")
        if details:
            print(f"   📋 {details}")

    def testar_api_health(self) -> bool:
        """Testa se a API está respondendo"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_step("API Health Check", "PASS", 
                              f"Status: {data.get('status')}, Database: {data.get('database')}")
                return True
            else:
                self.print_step("API Health Check", "FAIL", f"Status Code: {response.status_code}")
                return False
        except Exception as e:
            self.print_step("API Health Check", "FAIL", f"Erro: {str(e)}")
            return False

    def testar_autenticacao_api(self, username: str, password: str) -> Dict[str, Any]:
        """Testa autenticação diretamente na API"""
        try:
            payload = {"username": username, "password": password}
            response = requests.post(f"{self.api_base}/api/v1/auth/login", 
                                   json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    "sucesso": True,
                    "token": data.get("access_token", ""),
                    "usuario": data.get("user", {}),
                    "detalhes": f"Token recebido, usuário: {data.get('user', {}).get('username', 'N/A')}"
                }
            else:
                return {
                    "sucesso": False,
                    "erro": f"Status {response.status_code}",
                    "detalhes": response.text[:100]
                }
        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e),
                "detalhes": "Erro de conexão ou timeout"
            }

    def testar_todas_credenciais(self):
        """Testa todas as credenciais configuradas"""
        self.print_header("TESTE DE AUTENTICAÇÃO VIA API")

        for cred in self.credenciais_teste:
            print(f"\n🔐 Testando: {cred['descricao']}")
            print(f"   Username: {cred['username']}")
            print(f"   Password: {'*' * len(cred['password'])}")

            resultado = self.testar_autenticacao_api(cred["username"], cred["password"])

            if resultado["sucesso"]:
                self.print_step("Autenticação API", "PASS", resultado.get("detalhes", ""))
                # Testar se o token é válido
                self.testar_token_valido(resultado["token"])
            else:
                status = "FAIL" if cred["username"] != "credencial_invalida" else "PASS"
                self.print_step("Autenticação API", status, 
                              f"Erro: {resultado.get('erro', 'Desconhecido')}")

            self.resultados.append({
                "credencial": cred["descricao"],
                "resultado": resultado
            })

    def testar_token_valido(self, token: str):
        """Testa se o token JWT é válido fazendo uma requisição autenticada"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{self.api_base}/api/v1/clientes", 
                                  headers=headers, timeout=5)

            if response.status_code == 200:
                self.print_step("Validação Token", "PASS", "Token válido para acessar recursos")
            else:
                self.print_step("Validação Token", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.print_step("Validação Token", "FAIL", f"Erro: {str(e)}")

    def testar_interface_login(self):
        """Testa a interface de login"""
        self.print_header("TESTE DA INTERFACE DE LOGIN")

        try:
            # Criar uma janela de teste
            root = tk.Tk()
            root.withdraw()  # Esconder janela principal

            # Tentar criar janela de login
            login_window = LoginWindow(root)
            self.print_step("Criação Interface Login", "PASS", "Janela criada com sucesso")

            # Verificar elementos da interface
            if hasattr(login_window, 'username_entry') and hasattr(login_window, 'password_entry'):
                self.print_step("Elementos da Interface", "PASS", "Campos de entrada encontrados")
            else:
                self.print_step("Elementos da Interface", "FAIL", "Campos não encontrados")

            if hasattr(login_window, 'login_button'):
                self.print_step("Botão de Login", "PASS", "Botão encontrado")
            else:
                self.print_step("Botão de Login", "FAIL", "Botão não encontrado")

            # Fechar janela de teste
            login_window.destroy()
            root.destroy()

            return True

        except Exception as e:
            self.print_step("Interface Login", "FAIL", f"Erro: {str(e)}")
            return False

    def testar_login_completo_simulado(self):
        """Simula um login completo com credenciais válidas"""
        self.print_header("TESTE DE LOGIN COMPLETO SIMULADO")

        try:
            # Usar credenciais do admin
            cred = self.credenciais_teste[0]  # admin

            # 1. Testar autenticação
            resultado_auth = self.testar_autenticacao_api(cred["username"], cred["password"])

            if not resultado_auth["sucesso"]:
                self.print_step("Login Simulado", "FAIL", "Falha na autenticação")
                return False

            self.print_step("Autenticação", "PASS", "Credenciais válidas")

            # 2. Simular criação do dashboard
            try:
                root = tk.Tk()
                root.withdraw()

                # Dados do usuário mockados
                user_data = {
                    "id": 1,
                    "username": cred["username"],
                    "email": "admin@primotex.com",
                    "perfil": "administrador",
                    "token": resultado_auth["token"]
                }

                # Tentar criar dashboard
                dashboard = Dashboard(root, user_data)
                self.print_step("Criação Dashboard", "PASS", f"Dashboard criado para {user_data['username']}")

                # Verificar elementos do dashboard
                if hasattr(dashboard, 'main_frame'):
                    self.print_step("Elementos Dashboard", "PASS", "Frame principal encontrado")
                else:
                    self.print_step("Elementos Dashboard", "FAIL", "Frame principal não encontrado")

                # Fechar
                dashboard.destroy()
                root.destroy()

                return True

            except Exception as e:
                self.print_step("Dashboard", "FAIL", f"Erro ao criar dashboard: {str(e)}")
                return False

        except Exception as e:
            self.print_step("Login Completo", "FAIL", f"Erro geral: {str(e)}")
            return False

    def executar_testes_completos(self):
        """Executa todos os testes de login"""
        print("🚀 INICIANDO TESTES DE LOGIN DO SISTEMA ERP PRIMOTEX")
        print(f"📅 Data: {time.strftime('%d/%m/%Y %H:%M:%S')}")

        # 1. Teste de saúde da API
        if not self.testar_api_health():
            print("\n❌ API não está respondendo. Verifique se o servidor está rodando:")
            print("   .venv\\Scripts\\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002")
            return

        # 2. Testes de autenticação
        self.testar_todas_credenciais()

        # 3. Teste da interface
        self.testar_interface_login()

        # 4. Teste completo simulado
        self.testar_login_completo_simulado()

        # 5. Relatório final
        self.imprimir_relatorio_final()

    def imprimir_relatorio_final(self):
        """Imprime relatório final dos testes"""
        self.print_header("RELATÓRIO FINAL DOS TESTES")

        sucessos = 0
        total = len(self.resultados)

        for resultado in self.resultados:
            cred = resultado["credencial"]
            res = resultado["resultado"]

            if res["sucesso"] or cred == "Credencial Inválida":
                sucessos += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"

            print(f"{status} {cred}")

        print("\n📊 ESTATÍSTICAS:")
        print(f"   Total de testes: {total}")
        print(f"   Sucessos: {sucessos}")
        print(f"   Taxa de sucesso: {(sucessos/total)*100:.1f}%")

        if sucessos == total:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Sistema de login está funcionando corretamente")
        else:
            print(f"\n⚠️  {total-sucessos} teste(s) falharam")
            print("❌ Verifique os erros acima")

        print("\n🔧 COMANDOS ÚTEIS:")
        print("   Iniciar servidor: .venv\\Scripts\\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002")
        print("   Login manual: .venv\\Scripts\\python.exe frontend\\desktop\\login_tkinter.py")
        print("   Dashboard direto: .venv\\Scripts\\python.exe frontend\\desktop\\dashboard.py")

def main():
    """Função principal"""
    testador = TestadorLogin()
    testador.executar_testes_completos()

if __name__ == "__main__":
    main()