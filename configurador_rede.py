#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURADOR AUTOMÁTICO DE REDE - ERP PRIMOTEX
Detecta automaticamente a melhor configuração para sua situação
"""

import socket
import subprocess
import sys
import platform
import os
from datetime import datetime

def obter_ip_local():
    """Obtém o IP local da máquina"""
    try:
        # Conecta a um servidor externo para descobrir IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except Exception:
        return "127.0.0.1"

def verificar_porta_disponivel(porta=8002):
    """Verifica se a porta está disponível"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        resultado = sock.connect_ex(('127.0.0.1', porta))
        sock.close()
        return resultado != 0  # True se porta disponível
    except Exception:
        return False

def detectar_sistema():
    """Detecta informações do sistema"""
    return {
        "os": platform.system(),
        "versao": platform.version(),
        "arquitetura": platform.architecture()[0],
        "processador": platform.processor(),
        "nome_maquina": platform.node()
    }

def verificar_python():
    """Verifica versão do Python"""
    versao = sys.version_info
    return f"{versao.major}.{versao.minor}.{versao.micro}"

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    dependencias = {
        "fastapi": False,
        "uvicorn": False,
        "sqlalchemy": False,
        "tkinter": False
    }
    
    for dep in dependencias.keys():
        try:
            if dep == "tkinter":
                import tkinter
            else:
                __import__(dep)
            dependencias[dep] = True
        except ImportError:
            dependencias[dep] = False
    
    return dependencias

def criar_script_inicializacao(tipo_uso, ip_local, porta):
    """Cria script de inicialização personalizado"""
    
    if tipo_uso == "local":
        script_content = f"""@echo off
echo ========================================
echo   INICIANDO ERP PRIMOTEX - LOCAL
echo ========================================
echo Servidor: http://127.0.0.1:{porta}
echo Data/Hora: %date% %time%
echo.

cd /d C:\\GIES
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port {porta}

pause
"""
        nome_arquivo = "iniciar_local.bat"
    
    elif tipo_uso == "rede":
        script_content = f"""@echo off
echo ========================================
echo   INICIANDO ERP PRIMOTEX - REDE
echo ========================================
echo Servidor: http://{ip_local}:{porta}
echo Acesso local: http://127.0.0.1:{porta}
echo Data/Hora: %date% %time%
echo.
echo IMPORTANTE: Configure o firewall para permitir porta {porta}
echo.

cd /d C:\\GIES
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port {porta}

pause
"""
        nome_arquivo = "iniciar_rede.bat"
    
    elif tipo_uso == "recepcao":
        script_content = f"""@echo off
echo ========================================
echo   ERP PRIMOTEX - SISTEMA RECEPÇÃO
echo ========================================
echo Modo: Offline (sem servidor)
echo Data/Hora: %date% %time%
echo.

cd /d C:\\GIES
python sistema_recepcao_simples.py

pause
"""
        nome_arquivo = "iniciar_recepcao.bat"
    
    # Salvar arquivo
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    return nome_arquivo

def configurar_firewall_windows(porta):
    """Configura firewall do Windows"""
    try:
        # Comando para adicionar regra no firewall
        cmd = f'netsh advfirewall firewall add rule name="ERP Primotex" dir=in action=allow protocol=TCP localport={porta}'
        resultado = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return resultado.returncode == 0
    except Exception:
        return False

def main():
    print("=" * 60)
    print("    CONFIGURADOR AUTOMÁTICO - ERP PRIMOTEX")
    print("=" * 60)
    print()
    
    # 1. Detectar sistema
    print("🔍 DETECTANDO SISTEMA...")
    sistema = detectar_sistema()
    ip_local = obter_ip_local()
    python_version = verificar_python()
    
    print(f"   Sistema: {sistema['os']}")
    print(f"   IP Local: {ip_local}")
    print(f"   Python: {python_version}")
    print(f"   Máquina: {sistema['nome_maquina']}")
    print()
    
    # 2. Verificar dependências
    print("📦 VERIFICANDO DEPENDÊNCIAS...")
    deps = verificar_dependencias()
    deps_ok = all(deps.values())
    
    for dep, status in deps.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {dep}")
    
    if not deps_ok:
        print("\n⚠️  AVISO: Algumas dependências estão faltando!")
        print("   Execute: pip install fastapi uvicorn sqlalchemy")
        print()
    
    # 3. Verificar porta
    porta = 8002
    porta_livre = verificar_porta_disponivel(porta)
    if not porta_livre:
        print(f"⚠️  Porta {porta} em uso. Tentando porta 8003...")
        porta = 8003
        porta_livre = verificar_porta_disponivel(porta)
    
    print(f"🌐 PORTA DISPONÍVEL: {porta}")
    print()
    
    # 4. Menu de opções
    print("=" * 60)
    print("    COMO VOCÊ QUER USAR O SISTEMA?")
    print("=" * 60)
    print("1. 🏢 RECEPÇÃO HÍBRIDA - Interface gráfica (online/offline)")
    print("2. 🖥️  LOCAL - Servidor no mesmo computador")
    print("3. 🌐 REDE - Servidor para múltiplos computadores")
    print("4. ☁️  NUVEM - Configuração para servidor remoto")
    print("5. 📱 RECEPÇÃO SIMPLES - Terminal básico (offline)")
    print("0. ❌ Sair")
    print()
    
    while True:
        escolha = input("Digite sua opção (0-5): ").strip()
        
        if escolha == "0":
            print("👋 Saindo...")
            sys.exit(0)
        
        elif escolha == "1":
            print("\n🏢 CONFIGURANDO RECEPÇÃO HÍBRIDA...")
            print("✅ Sistema pronto para usar!")
            print("\n📋 INSTRUÇÕES:")
            print("   1. Execute: python sistema_recepcao_completo.py")
            print("   2. Interface gráfica com abas de Clientes e Agendamentos")
            print("   3. Funciona online (servidor) ou offline (arquivos locais)")
            print("   4. Conecta automaticamente se servidor disponível")
            break
        
        elif escolha == "2":
            print("\n🖥️ CONFIGURANDO SERVIDOR LOCAL...")
            script = criar_script_inicializacao("local", ip_local, porta)
            print(f"✅ Criado: {script}")
            print("\n📋 INSTRUÇÕES:")
            print(f"   1. Execute: {script}")
            print(f"   2. Acesse: http://127.0.0.1:{porta}/docs")
            print("   3. Login desktop: admin/admin123")
            break
        
        elif escolha == "3":
            print("\n🌐 CONFIGURANDO SERVIDOR DE REDE...")
            script = criar_script_inicializacao("rede", ip_local, porta)
            
            # Tentar configurar firewall
            if sistema['os'] == "Windows":
                print("🔧 Configurando firewall...")
                fw_ok = configurar_firewall_windows(porta)
                if fw_ok:
                    print("✅ Firewall configurado")
                else:
                    print("⚠️  Configure manualmente o firewall")
            
            print(f"✅ Criado: {script}")
            print("\n📋 INSTRUÇÕES:")
            print(f"   1. Execute: {script}")
            print(f"   2. Outros computadores acessam: http://{ip_local}:{porta}")
            print("   3. Configure clientes com IP do servidor")
            print("\n🔗 LINKS DE ACESSO:")
            print(f"   • API: http://{ip_local}:{porta}/docs")
            print(f"   • Health: http://{ip_local}:{porta}/health")
            break
        
        elif escolha == "4":
            print("\n☁️ CONFIGURAÇÃO PARA NUVEM...")
            print("\n📋 INSTRUÇÕES PARA SERVIDOR REMOTO:")
            print("   1. Instale Python 3.7+ no servidor")
            print("   2. Clone o repositório")
            print("   3. Execute: pip install -r requirements.txt")
            print("   4. Comando: python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 80")
            print("   5. Configure DNS e SSL")
            print("\n🔒 SEGURANÇA:")
            print("   • Altere senha padrão admin/admin123")
            print("   • Configure firewall (apenas portas 80, 443, 22)")
            print("   • Use HTTPS em produção")
            break
        
        elif escolha == "5":
            print("\n📱 CONFIGURANDO SISTEMA DE RECEPÇÃO SIMPLES...")
            script = criar_script_inicializacao("recepcao", ip_local, porta)
            print(f"✅ Criado: {script}")
            print("\n📋 INSTRUÇÕES:")
            print("   1. Execute: iniciar_recepcao.bat")
            print("   2. Use o menu para cadastrar clientes e agendar")
            print("   3. Dados salvos em: dados_recepcao/")
            break
        
        else:
            print("❌ Opção inválida! Digite 0-5")
    
    print("\n" + "=" * 60)
    print("    CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("📞 Suporte: Verifique o arquivo GUIA_COMPLETO_USO_SISTEMA.md")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Configuração cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("📞 Verifique o arquivo GUIA_COMPLETO_USO_SISTEMA.md")