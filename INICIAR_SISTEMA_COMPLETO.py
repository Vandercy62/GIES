#!/usr/bin/env python3
"""
LAUNCHER COMPLETO DO SISTEMA ERP PRIMOTEX
========================================

Inicia o sistema completo:
1. Backend API (porta 8002)
2. Interface Web (porta 8003)
3. Monitoramento automático

Autor: GitHub Copilot
Data: 02/12/2025
"""

import subprocess
import time
import sys
import os
import requests
import threading
from datetime import datetime

def print_status(message, status="INFO"):
    """Print com timestamp e status"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def check_port(port):
    """Verificar se uma porta está sendo usada"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('localhost', port))
        return result == 0

def kill_port_process(port):
    """Matar processo que está usando uma porta"""
    try:
        if os.name == 'nt':  # Windows
            cmd = f'netstat -ano | findstr :{port}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if f':{port}' in line and 'LISTENING' in line:
                        pid = line.split()[-1]
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                        print_status(f"Processo na porta {port} encerrado (PID: {pid})", "INFO")
                        time.sleep(2)
                        break
    except Exception as e:
        print_status(f"Erro ao encerrar processo na porta {port}: {e}", "ERROR")

def start_backend():
    """Iniciar o backend da API"""
    print_status("Iniciando backend API...", "INFO")
    
    # Verificar e matar processo na porta 8002 se existir
    if check_port(8002):
        print_status("Porta 8002 em uso - encerrando processo...", "WARNING")
        kill_port_process(8002)
    
    # Iniciar o backend
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.api.main:app",
        "--host", "127.0.0.1",
        "--port", "8002",
        "--log-level", "info"
    ]
    
    try:
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print_status("Backend iniciado, aguardando inicialização...", "INFO")
        
        # Aguardar backend estar pronto
        for i in range(30):  # 30 segundos timeout
            try:
                response = requests.get("http://127.0.0.1:8002/health", timeout=2)
                if response.status_code == 200:
                    print_status("Backend API iniciado com sucesso!", "SUCCESS")
                    return backend_process
            except:
                pass
            time.sleep(1)
            
        print_status("Timeout ao aguardar backend", "ERROR")
        return None
        
    except Exception as e:
        print_status(f"Erro ao iniciar backend: {e}", "ERROR")
        return None

def start_web_interface():
    """Iniciar a interface web"""
    print_status("Iniciando interface web...", "INFO")
    
    # Verificar e matar processo na porta 8003 se existir
    if check_port(8003):
        print_status("Porta 8003 em uso - encerrando processo...", "WARNING")
        kill_port_process(8003)
    
    # Iniciar interface web
    web_cmd = [sys.executable, "web_interface.py"]
    
    try:
        web_process = subprocess.Popen(
            web_cmd,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print_status("Interface web iniciada, aguardando inicialização...", "INFO")
        
        # Aguardar interface web estar pronta
        for i in range(15):  # 15 segundos timeout
            try:
                response = requests.get("http://localhost:8003", timeout=2)
                if response.status_code in [200, 302]:  # 302 = redirect para login
                    print_status("Interface web iniciada com sucesso!", "SUCCESS")
                    return web_process
            except:
                pass
            time.sleep(1)
            
        print_status("Timeout ao aguardar interface web", "ERROR")
        return None
        
    except Exception as e:
        print_status(f"Erro ao iniciar interface web: {e}", "ERROR")
        return None

def monitor_processes(backend_process, web_process):
    """Monitorar os processos em execução"""
    print_status("Iniciando monitoramento dos processos...", "INFO")
    
    while True:
        try:
            # Verificar backend
            if backend_process and backend_process.poll() is not None:
                print_status("Backend parou inesperadamente!", "ERROR")
                break
                
            # Verificar interface web
            if web_process and web_process.poll() is not None:
                print_status("Interface web parou inesperadamente!", "ERROR")
                break
                
            # Verificar conectividade
            try:
                requests.get("http://127.0.0.1:8002/health", timeout=2)
                requests.get("http://localhost:8003", timeout=2)
            except:
                print_status("Perda de conectividade detectada", "WARNING")
                
            time.sleep(10)  # Verificar a cada 10 segundos
            
        except KeyboardInterrupt:
            print_status("Interrompido pelo usuário", "INFO")
            break
        except Exception as e:
            print_status(f"Erro no monitoramento: {e}", "ERROR")
            time.sleep(5)

def main():
    """Função principal"""
    print("=" * 60)
    print("  ERP PRIMOTEX - SISTEMA COMPLETO")
    print("=" * 60)
    print()
    
    backend_process = None
    web_process = None
    
    try:
        # 1. Iniciar backend
        backend_process = start_backend()
        if not backend_process:
            print_status("Falha ao iniciar backend - abortando", "ERROR")
            return
            
        # 2. Iniciar interface web
        web_process = start_web_interface()
        if not web_process:
            print_status("Falha ao iniciar interface web - abortando", "ERROR")
            return
            
        # 3. Sistema iniciado com sucesso
        print()
        print("=" * 60)
        print("  ✅ SISTEMA INICIADO COM SUCESSO!")
        print("=" * 60)
        print()
        print("🌐 Interface Web: http://localhost:8003")
        print("🔧 API Backend:   http://localhost:8002")
        print("📚 Documentação:  http://localhost:8002/docs")
        print()
        print("👤 Login padrão:  admin / admin123")
        print()
        print("💡 Dicas:")
        print("   - Abra o navegador em http://localhost:8003")
        print("   - Use Ctrl+C para parar o sistema")
        print("   - Logs aparecem em tempo real na interface web")
        print()
        print("=" * 60)
        
        # 4. Monitorar processos
        monitor_processes(backend_process, web_process)
        
    except KeyboardInterrupt:
        print_status("\nParando sistema...", "INFO")
        
    finally:
        # Encerrar processos
        if backend_process:
            backend_process.terminate()
            print_status("Backend encerrado", "INFO")
            
        if web_process:
            web_process.terminate()
            print_status("Interface web encerrada", "INFO")
            
        print_status("Sistema encerrado", "INFO")

if __name__ == "__main__":
    main()