#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico detalhado do servidor para identificar o problema exato
"""

import sys
import os
import time
import signal

def test_uvicorn_import():
    """Testa se uvicorn pode ser importado"""
    try:
        import uvicorn
        print("✅ Uvicorn importado com sucesso")
        print(f"   Versão: {uvicorn.__version__}")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar uvicorn: {e}")
        return False

def test_app_import():
    """Testa se a aplicação pode ser importada"""
    try:
        from backend.api.main import app
        print("✅ Aplicação importada com sucesso")
        print(f"   Rotas: {len(app.routes)}")
        return app
    except Exception as e:
        print(f"❌ Erro ao importar aplicação: {e}")
        return None

def run_server_with_timeout():
    """Executa servidor com timeout para diagnóstico"""
    try:
        import uvicorn
        from backend.api.main import app
        import threading
        import time
        
        print("🚀 Iniciando servidor com timeout de 10 segundos...")
        
        # Variável para controlar execução
        server_running = threading.Event()
        
        def run_server():
            try:
                uvicorn.run(
                    app,
                    host="127.0.0.1",
                    port=8002,
                    log_level="info",
                    access_log=False
                )
            except Exception as e:
                print(f"❌ Erro no servidor: {e}")
        
        # Executar servidor em thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Aguardar 10 segundos
        time.sleep(10)
        
        if server_thread.is_alive():
            print("✅ Servidor executou por 10 segundos sem problemas!")
            return True
        else:
            print("❌ Servidor parou prematuramente")
            return False
        
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {e}")
        return False

def main():
    """Executa diagnóstico completo"""
    print("=" * 50)
    print("DIAGNÓSTICO DO SERVIDOR BACKEND")
    print("=" * 50)
    
    print("\n1. Testando importação do uvicorn...")
    if not test_uvicorn_import():
        return
    
    print("\n2. Testando importação da aplicação...")
    app = test_app_import()
    if not app:
        return
    
    print("\n3. Testando execução do servidor...")
    if run_server_with_timeout():
        print("\n🎉 SERVIDOR FUNCIONA CORRETAMENTE!")
        print("   O problema pode ser específico do terminal do VS Code")
    else:
        print("\n❌ PROBLEMA IDENTIFICADO NO SERVIDOR")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()