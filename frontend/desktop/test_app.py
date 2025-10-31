"""
TESTE DIRETO DA APLICAÇÃO DESKTOP
==================================

Script para testar diretamente o sistema login + dashboard
sem verificar servidor (assumindo que já está rodando).
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def main():
    """Testar aplicação diretamente"""
    
    print("=" * 60)
    print("🏢 TESTE - SISTEMA ERP PRIMOTEX FASE 2")
    print("=" * 60)
    
    try:
        from login_tkinter import LoginWindow
        from dashboard import DashboardWindow
        
        # 1. Login
        print("\n🔐 Iniciando tela de login...")
        login_window = LoginWindow()
        user_data = login_window.run()
        
        if not user_data:
            print("❌ Login cancelado")
            return
        
        print(f"✅ Login realizado: {user_data.get('user', {}).get('username')}")
        
        # 2. Dashboard
        print("\n📊 Iniciando dashboard...")
        dashboard = DashboardWindow(user_data)
        dashboard.run()
        
        print("\n👋 Aplicação encerrada")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()