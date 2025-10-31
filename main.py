"""
SISTEMA ERP PRIMOTEX - APLICAÇÃO PRINCIPAL
==========================================

Ponto de entrada principal do Sistema ERP Primotex.
Este arquivo inicializa tanto o backend FastAPI quanto o frontend PyQt6.

Autor: GitHub Copilot
Data: 29/10/2025
Empresa: Primotex - Forros e Divisórias Eireli
"""

import sys
import asyncio
import threading
from pathlib import Path

# Adicionar o diretório raiz ao path do Python
sys.path.append(str(Path(__file__).parent))

def start_backend():
    """Inicia o servidor FastAPI em thread separada"""
    import uvicorn
    from backend.api.main import app
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

def start_frontend():
    """Inicia a interface desktop PyQt6"""
    from PyQt6.QtWidgets import QApplication
    from frontend.desktop.main_window import MainWindow
    
    app = QApplication(sys.argv)
    app.setApplicationName("Primotex ERP")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Primotex - Forros e Divisórias Eireli")
    
    # Aplicar estilo moderno
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QMenuBar {
            background-color: #2c3e50;
            color: white;
            padding: 4px;
        }
        QMenuBar::item {
            padding: 4px 8px;
            background-color: transparent;
        }
        QMenuBar::item:selected {
            background-color: #34495e;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

def main():
    """Função principal - decide qual modo executar"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "backend":
            print("🚀 Iniciando apenas o backend FastAPI...")
            start_backend()
        elif mode == "frontend":
            print("🖥️ Iniciando apenas o frontend desktop...")
            start_frontend()
        elif mode == "api":
            print("📡 Modo API - Apenas servidor web...")
            start_backend()
        else:
            print("❌ Modo inválido. Use: backend, frontend ou api")
            return
    else:
        print("🌟 Iniciando Sistema ERP Primotex completo...")
        print("📡 Backend: http://127.0.0.1:8000")
        print("🖥️ Frontend: Desktop PyQt6")
        
        # Iniciar backend em thread separada
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Aguardar um momento para o backend inicializar
        import time
        time.sleep(2)
        
        # Iniciar frontend na thread principal
        start_frontend()

if __name__ == "__main__":
    main()