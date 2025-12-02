"""
Inicializar Backend ERP Primotex - BACKEND ROBUSTO v2.0

🔄 MIGRADO EM: 17/11/2025
🎯 BACKEND: main_robust.py (com validação + retry)
📋 RECURSOS:
   - Validação pré-startup (8 checks)
   - Router isolation (1 falha ≠ crash total)
   - Health check real (SELECT 1)
   - Exception handlers globais
   - Graceful shutdown

Script alternativo usando uvicorn.run() diretamente
"""
import uvicorn
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("="*60)
    print("🚀 INICIANDO BACKEND ERP PRIMOTEX")
    print("="*60)
    print("📍 Host: 127.0.0.1")
    print("📍 Porta: 8002")
    print("📚 Docs: http://127.0.0.1:8002/docs")
    print("🏥 Health: http://127.0.0.1:8002/health")
    print("="*60)
    print("\n⏳ Aguarde a inicialização...\n")
    
    try:
        # MIGRAÇÃO BACKEND ROBUSTO - 17/11/2025
        # OLD: uvicorn.run("backend.api.main:app", ...)
        # NEW: Usando main_robust com validação pré-startup + retry
        uvicorn.run(
            "backend.api.main_robust:app",  # ← BACKEND ROBUSTO
            host="127.0.0.1",
            port=8002,
            reload=False,  # Desabilitar reload para evitar problemas
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n✅ Servidor encerrado pelo usuário")
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
