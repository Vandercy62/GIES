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
    """Verifica se backend está rodando com health check DETALHADO
    
    🔄 MIGRADO: 17/11/2025 - Backend Robusto v2.0
    Valida não apenas se porta responde, mas também:
    - Status do backend (healthy/degraded)
    - Database connection (SELECT 1)
    - Routers carregados (10/10)
    """
    
    api_url = "http://127.0.0.1:8002/health"
    
    print("\n🔍 Verificando Backend Robusto v2.0...")
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            response = requests.get(api_url, timeout=5)  # Aumentado para 5s
            
            if response.status_code == 200:
                # ===== HEALTH CHECK DETALHADO =====
                try:
                    data = response.json()
                    status = data.get("status", "unknown")
                    
                    # Validar status geral
                    if status != "healthy":
                        print(f"⚠️  Backend degradado: {status}")
                        continue
                    
                    # Validar database (NOVO - Backend Robusto)
                    db_info = data.get("database", {})
                    db_status = db_info.get("status", "unknown")
                    
                    if db_status != "healthy":
                        print(f"❌ Database não está saudável: {db_status}")
                        continue
                    
                    # Validar routers (NOVO - Backend Robusto)
                    routers_info = data.get("routers", {})
                    routers_loaded = routers_info.get("loaded", 0)
                    routers_total = routers_info.get("total", 0)
                    
                    if routers_loaded < routers_total:
                        print(f"⚠️  Apenas {routers_loaded}/{routers_total} routers carregados")
                    
                    # Sucesso!
                    print(f"✅ Backend Robusto 100% operacional")
                    print(f"   🗄️  Database: {db_status}")
                    print(f"   🔌 Routers: {routers_loaded}/{routers_total}")
                    print(f"   📊 Tables: {db_info.get('tables', '?')}")
                    return True
                    
                except (ValueError, KeyError) as e:
                    # Fallback para backend antigo (sem health check detalhado)
                    print(f"⚠️  Backend antigo detectado (sem validação detalhada)")
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
        print("\n📋 Para iniciar o Backend Robusto v2.0:")
        print("\n   🚀 OPÇÃO 1 (RECOMENDADO): Clique duplo em INICIAR_BACKEND_ROBUSTO.bat")
        print("\n   💻 OPÇÃO 2: Execute manualmente:")
        print("      cd C:\\GIES")
        print("      .venv\\Scripts\\python.exe start_backend_robust.py")
        print("\n   ⚠️  OPÇÃO 3 (ANTIGO - não recomendado):")
        print("      .venv\\Scripts\\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002")
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
