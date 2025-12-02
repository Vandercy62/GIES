"""
SISTEMA ERP PRIMOTEX - APLICAÇÃO PRINCIPAL
==========================================

Script principal que integra login e dashboard.
Aplica todas as funcionalidades da Fase 2.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import sys
import os
import threading
from pathlib import Path

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent))

def verificar_servidor():
    """Verificar se o servidor backend está rodando"""
    import requests

    try:
        response = requests.get("http://127.0.0.1:8002/api/v1/health", timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def iniciar_servidor():
    """Iniciar servidor backend se necessário"""
    import subprocess
    import time

    print("🚀 Iniciando servidor backend...")

    # Caminho para o backend
    backend_path = Path(__file__).parent.parent.parent / "backend"

    if not backend_path.exists():
        print("❌ Diretório backend não encontrado")
        return False

    try:
        # Iniciar uvicorn em processo separado
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.api.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8002",
            "--reload"
        ], cwd=str(backend_path.parent))

        # Aguardar inicialização
        print("⏳ Aguardando servidor inicializar...")
        for tentativa in range(10):
            time.sleep(1)
            if verificar_servidor():
                print("✅ Servidor backend online!")
                return True
            print(f"   Tentativa {tentativa+1}/10...")

        print("❌ Timeout ao iniciar servidor")
        return False

    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False

def exibir_cabecalho():
    """Exibe cabeçalho inicial da aplicação"""
    print("=" * 60)
    print("🏢 SISTEMA ERP PRIMOTEX - FASE 2")
    print("   Interface Desktop Integrada")
    print("=" * 60)

def verificar_e_iniciar_backend():
    """Verifica se backend está rodando e tenta iniciar se necessário"""
    print("\n🔍 Verificando servidor backend...")
    if not verificar_servidor():
        print("❌ Servidor não está rodando")
        if input("Deseja tentar iniciar automaticamente? (s/n): ").lower() == 's':
            if not iniciar_servidor():
                print("❌ Falha ao iniciar servidor. Execute manualmente:")
                print("   cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8002")
                return False
        else:
            print("❌ Sistema não pode funcionar sem o backend")
            return False
    else:
        print("✅ Servidor backend está online!")
    return True

def importar_modulos():
    """Importa módulos necessários da aplicação"""
    try:
        from login_tkinter import LoginWindow
        from dashboard import DashboardWindow
        return LoginWindow, DashboardWindow
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        return None, None

def executar_ciclo_login_dashboard():
    """Executa ciclo completo de login e dashboard"""
    login_window_class, dashboard_window_class = importar_modulos()

    if not login_window_class or not dashboard_window_class:
        return False

    # Login
    print("\n🔐 Iniciando tela de login...")
    login_window = login_window_class()
    user_data = login_window.run()

    if not user_data:
        print("👋 Login cancelado pelo usuário")
        return False

    print(f"✅ Login realizado: {user_data.get('user', {}).get('username')}")

    # Dashboard
    print("\n📊 Iniciando dashboard principal...")
    dashboard = dashboard_window_class(user_data)
    dashboard.run()

    # Perguntar se quer fazer novo login
    print("\n🔄 Dashboard fechado")
    return input("Deseja fazer novo login? (s/n): ").lower() == 's'

def main():
    """Função principal da aplicação"""

    exibir_cabecalho()

    # Verificar backend
    if not verificar_e_iniciar_backend():
        return

    # Executar sequência completa
    while True:
        try:
            continuar = executar_ciclo_login_dashboard()
            if not continuar:
                break

        except KeyboardInterrupt:
            print("\n⏹️ Aplicação interrompida pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro na aplicação: {e}")
            import traceback
            traceback.print_exc()
            break

    print("\n👋 Sistema ERP Primotex encerrado")
    print("   Obrigado por usar nosso sistema!")

if __name__ == "__main__":
    main()