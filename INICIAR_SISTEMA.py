"""
LAUNCHER - ERP PRIMOTEX DESKTOP
================================

Inicia o sistema ERP Primotex com verificação de backend.

Uso:
    python INICIAR_SISTEMA.py
    
    ou duplo clique em: INICIAR_SISTEMA.bat
"""

import sys
import time
import requests
from pathlib import Path

# Adicionar ao path
sys.path.insert(0, str(Path(__file__).parent))

from frontend.desktop.login_tkinter import LoginWindow


def verificar_backend(max_tentativas=5):
    """Verifica se backend está rodando"""
    
    api_url = "http://127.0.0.1:8002/health"
    
    print("\n🔍 Verificando backend...")
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            response = requests.get(api_url, timeout=2)
            if response.status_code == 200:
                print(f"✅ Backend online (tentativa {tentativa}/{max_tentativas})")
                return True
        except requests.exceptions.RequestException:
            if tentativa < max_tentativas:
                print(f"⏳ Tentativa {tentativa}/{max_tentativas} - Aguardando backend...")
                time.sleep(2)
            else:
                print(f"❌ Backend não respondeu após {max_tentativas} tentativas")
    
    return False


def main():
    """Função principal"""
    
    print("=" * 70)
    print("🏢 ERP PRIMOTEX - SISTEMA DE GESTÃO EMPRESARIAL")
    print("=" * 70)
    print("\n📦 Versão: 9.0 - PRODUCTION READY")
    print("🔐 Autenticação: SessionManager Global")
    print("💻 Interface: tkinter Desktop")
    print("🌐 API: FastAPI + SQLAlchemy")
    
    # Verificar backend
    if not verificar_backend():
        print("\n" + "=" * 70)
        print("⚠️  ATENÇÃO: Backend não está respondendo!")
        print("=" * 70)
        print("\n📋 Para iniciar o backend, execute em outro terminal:")
        print("   cd C:\\GIES")
        print("   .venv\\Scripts\\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002")
        print("\nOu clique duplo em: INICIAR_BACKEND.bat")
        print("=" * 70)
        
        resposta = input("\n❓ Deseja continuar mesmo assim? (s/N): ").lower()
        if resposta != 's':
            print("\n👋 Encerrando...")
            return 1
    
    print("\n" + "=" * 70)
    print("🚀 INICIANDO SISTEMA...")
    print("=" * 70)
    print("\n📋 Módulos disponíveis:")
    print("   ✅ Login e autenticação global")
    print("   ✅ Dashboard principal")
    print("   ✅ Gestão de clientes")
    print("   ✅ Gestão de produtos (NOVO!)")
    print("   ✅ Controle de estoque")
    print("   ✅ Ordens de serviço (7 fases)")
    print("   ✅ Sistema financeiro")
    print("   ✅ Agendamento")
    print("   ✅ Relatórios PDF")
    print("   ✅ Códigos de barras")
    print("   ✅ Colaboradores e fornecedores")
    
    print("\n🔑 Credenciais padrão:")
    print("   Usuário: admin")
    print("   Senha: admin123")
    
    print("\n⏳ Abrindo tela de login...")
    print("=" * 70 + "\n")
    
    try:
        # LoginWindow cria sua própria janela root
        # skip_restore=False = auto-login se sessão válida
        login_window = LoginWindow(skip_restore=False)
        
        # Executar mainloop e verificar se deve abrir dashboard
        login_window.run()
        
        print("\n✅ Sistema encerrado com sucesso!")
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO ao iniciar sistema: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
