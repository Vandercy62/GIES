"""
TESTE COMPLETO - DASHBOARD + CLIENTES
=====================================

Teste da aplicação completa com dashboard e módulo de clientes.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def main():
    print("=" * 60)
    print("🏢 SISTEMA ERP PRIMOTEX - TESTE COMPLETO")
    print("=" * 60)
    
    try:
        # Dados de usuário mock
        user_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            "user": {
                "id": 1,
                "username": "admin",
                "nome_completo": "Administrador Sistema",
                "perfil": "Administrador"
            }
        }
        
        from dashboard import DashboardWindow
        
        print("📊 Iniciando dashboard principal...")
        dashboard = DashboardWindow(user_data)
        dashboard.run()
        
        print("👋 Aplicação encerrada")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()