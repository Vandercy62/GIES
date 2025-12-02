#!/usr/bin/env python3
"""
INICIALIZADOR WEB SIMPLES - ERP PRIMOTEX
========================================

Este script inicia:
1. Backend API (FastAPI) na porta 8002  
2. Interface Web (Flask) na porta 8003

Uso:
1. Executar este script
2. Aguardar mensagens de sucesso 
3. Acessar http://localhost:8003 no navegador
4. Login: admin / admin123
"""

import subprocess
import sys
import time
import requests
import os
import signal
from concurrent.futures import ThreadPoolExecutor

# Lista de processos para cleanup
processos = []

def cleanup_processos():
    """Finalizar todos os processos ao sair"""
    print("\n🔄 Finalizando processos...")
    for processo in processos:
        try:
            processo.terminate()
            processo.wait(timeout=5)
        except:
            try:
                processo.kill()
            except:
                pass

def signal_handler(sig, frame):
    """Handler para Ctrl+C"""
    print("\n⚠️ Interrompido pelo usuário")
    cleanup_processos()
    sys.exit(0)

def verificar_porta(porta, nome_servico):
    """Verificar se serviço está respondendo"""
    for tentativa in range(30):  # 30 segundos timeout
        try:
            if porta == 8002:
                response = requests.get(f"http://127.0.0.1:{porta}/health", timeout=2)
            else:
                response = requests.get(f"http://127.0.0.1:{porta}/", timeout=2)
            
            if response.status_code in [200, 302]:  # 200 OK ou 302 Redirect
                print(f"✅ {nome_servico} respondendo na porta {porta}")
                return True
        except:
            pass
        
        if tentativa < 29:
            print(f"⏳ Aguardando {nome_servico}... ({tentativa+1}/30)")
            time.sleep(1)
    
    return False

def iniciar_backend():
    """Iniciar o backend FastAPI"""
    print("🚀 Iniciando Backend API (FastAPI)...")
    
    cmd = [
        sys.executable,
        "-m", "uvicorn", 
        "backend.api.main:app",
        "--host", "127.0.0.1", 
        "--port", "8002",
        "--log-level", "info"
    ]
    
    try:
        processo = subprocess.Popen(
            cmd,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        processos.append(processo)
        
        # Verificar se iniciou corretamente
        if verificar_porta(8002, "Backend API"):
            return True
        else:
            print("❌ Backend falhou ao iniciar")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return False

def iniciar_web():
    """Iniciar a interface web Flask"""
    print("🌐 Iniciando Interface Web (Flask)...")
    
    cmd = [
        sys.executable,
        "web_interface_simples.py"
    ]
    
    try:
        processo = subprocess.Popen(
            cmd,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        processos.append(processo)
        
        # Verificar se iniciou corretamente
        if verificar_porta(8003, "Interface Web"):
            return True
        else:
            print("❌ Interface Web falhou ao iniciar")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao iniciar interface web: {e}")
        return False

def main():
    # Configurar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 50)
    print("🔧 ERP PRIMOTEX - INICIALIZADOR WEB SIMPLES")
    print("=" * 50)
    print()
    
    # Verificar se já existe algo rodando nas portas
    try:
        requests.get("http://127.0.0.1:8002/health", timeout=1)
        print("⚠️ Backend já está rodando na porta 8002")
    except:
        pass
    
    try:
        requests.get("http://127.0.0.1:8003/", timeout=1)
        print("⚠️ Interface Web já está rodando na porta 8003")
    except:
        pass
    
    # Usar ThreadPoolExecutor para iniciar ambos em paralelo
    with ThreadPoolExecutor(max_workers=2) as executor:
        print("\n📋 Iniciando serviços...")
        
        # Iniciar backend primeiro
        backend_future = executor.submit(iniciar_backend)
        
        # Aguardar backend antes de iniciar web
        if backend_future.result():
            # Iniciar interface web
            web_future = executor.submit(iniciar_web)
            
            if web_future.result():
                print("\n" + "=" * 50)
                print("✅ SISTEMA INICIADO COM SUCESSO!")
                print("=" * 50)
                print()
                print("🌐 Acesse: http://localhost:8003")
                print("🔑 Login: admin")
                print("🗝️  Senha: admin123")
                print("📚 API Docs: http://localhost:8002/docs")
                print()
                print("⚠️ Pressione Ctrl+C para parar o sistema")
                print("=" * 50)
                
                # Manter vivo
                try:
                    while True:
                        time.sleep(1)
                        # Verificar se processos ainda estão rodando
                        for processo in processos[:]:
                            if processo.poll() is not None:
                                print(f"⚠️ Um processo finalizou inesperadamente")
                                processos.remove(processo)
                        
                        # Se todos os processos morreram, sair
                        if not processos:
                            print("❌ Todos os processos finalizaram")
                            break
                            
                except KeyboardInterrupt:
                    print("\n⚠️ Interrompido pelo usuário")
                    
            else:
                print("❌ Falha ao iniciar Interface Web")
        else:
            print("❌ Falha ao iniciar Backend")
    
    cleanup_processos()
    print("🔄 Sistema finalizado")

if __name__ == "__main__":
    main()