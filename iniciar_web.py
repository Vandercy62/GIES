#!/usr/bin/env python3
"""
INICIALIZADOR SISTEMA ERP PRIMOTEX - VERSÃO SIMPLES
===================================================

Inicia backend e web interface de forma simples e estável.
"""

import subprocess
import time
import sys
import os

def main():
    """Função principal"""
    print("🚀 INICIANDO ERP PRIMOTEX - VERSÃO WEB")
    print("=" * 50)
    
    # 1. Iniciar Backend
    print("📡 Iniciando backend API (porta 8002)...")
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.api.main:app",
        "--host", "127.0.0.1",
        "--port", "8002"
    ]
    
    backend_process = subprocess.Popen(backend_cmd, cwd=os.getcwd())
    time.sleep(3)  # Aguardar 3 segundos
    
    # 2. Iniciar Interface Web
    print("🌐 Iniciando interface web (porta 8003)...")
    web_cmd = [sys.executable, "web_interface.py"]
    
    web_process = subprocess.Popen(web_cmd, cwd=os.getcwd())
    time.sleep(2)  # Aguardar 2 segundos
    
    print("\n✅ SISTEMA INICIADO COM SUCESSO!")
    print("=" * 50)
    print("🌐 Acesse: http://localhost:8003")
    print("🔧 API: http://localhost:8002")
    print("👤 Login: admin / admin123")
    print("\n💡 Pressione Ctrl+C para parar")
    print("=" * 50)
    
    try:
        # Aguardar até interrupção
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Parando sistema...")
        backend_process.terminate()
        web_process.terminate()
        print("✅ Sistema encerrado")

if __name__ == "__main__":
    main()