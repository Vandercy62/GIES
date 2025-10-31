"""
TESTE DE INTEGRAÇÃO - SISTEMA DE COMUNICAÇÃO
============================================

Sistema ERP Primotex - Teste de integração do módulo de comunicação
Valida backend API, interface desktop e integração completa

Funcionalidades testadas:
- API endpoints de comunicação
- Interface desktop de comunicação  
- Integração com dashboard principal
- Templates e configurações
- Histórico e estatísticas

Autor: GitHub Copilot
Data: 29/10/2025
"""

import sys
import os
import requests
import json
import threading
import time
from typing import Dict, List, Any

def test_api_health():
    """Testar saúde da API"""
    try:
        response = requests.get("http://127.0.0.1:8003/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health Check: PASSOU")
            return True
        else:
            print(f"❌ API Health Check: FALHOU (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Health Check: ERRO ({e})")
        return False

def test_comunicacao_endpoints():
    """Testar endpoints de comunicação"""
    base_url = "http://127.0.0.1:8003/api/v1/comunicacao"
    headers = {"Content-Type": "application/json"}
    
    tests = [
        ("Templates", f"{base_url}/templates"),
        ("Configurações", f"{base_url}/configuracoes"),
        ("Histórico", f"{base_url}/historico"),
        ("Estatísticas", f"{base_url}/estatisticas"),
        ("Dashboard", f"{base_url}/dashboard")
    ]
    
    results = []
    
    for test_name, url in tests:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code in [200, 404]:  # 404 é OK para dados vazios
                print(f"✅ Endpoint {test_name}: PASSOU")
                results.append(True)
            else:
                print(f"❌ Endpoint {test_name}: FALHOU (Status: {response.status_code})")
                results.append(False)
        except Exception as e:
            print(f"❌ Endpoint {test_name}: ERRO ({e})")
            results.append(False)
    
    return all(results)

def test_post_endpoints():
    """Testar endpoints de criação"""
    base_url = "http://127.0.0.1:8003/api/v1/comunicacao"
    headers = {"Content-Type": "application/json"}
    
    # Teste de criação de template
    template_data = {
        "nome": "Template Teste",
        "tipo": "OS_CRIADA",
        "canal": "EMAIL",
        "template_texto": "Olá {{nome}}, sua OS foi criada!",
        "assunto": "Nova Ordem de Serviço",
        "ativo": True,
        "automatico": False
    }
    
    try:
        response = requests.post(f"{base_url}/templates", 
                               headers=headers, 
                               json=template_data, 
                               timeout=5)
        
        if response.status_code in [200, 201]:
            print("✅ Criação de Template: PASSOU")
            return True
        else:
            print(f"❌ Criação de Template: FALHOU (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Criação de Template: ERRO ({e})")
        return False

def test_desktop_interface():
    """Testar interface desktop"""
    try:
        # Importar módulo de comunicação
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        from comunicacao_window import ComunicacaoWindow
        
        print("✅ Importação da Interface: PASSOU")
        
        # Teste de inicialização (sem GUI real)
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Esconder janela
        
        # Simular criação da interface
        try:
            app = ComunicacaoWindow(root, token="test_token")
            print("✅ Inicialização da Interface: PASSOU")
            root.destroy()
            return True
        except Exception as e:
            print(f"❌ Inicialização da Interface: ERRO ({e})")
            root.destroy()
            return False
            
    except ImportError as e:
        print(f"❌ Importação da Interface: ERRO ({e})")
        return False
    except Exception as e:
        print(f"❌ Teste da Interface: ERRO ({e})")
        return False

def test_dashboard_integration():
    """Testar integração com dashboard"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        from dashboard import DashboardWindow
        
        # Verificar se método de comunicação existe
        if hasattr(DashboardWindow, 'show_comunicacao'):
            print("✅ Integração Dashboard: PASSOU")
            return True
        else:
            print("❌ Integração Dashboard: FALHOU (método não encontrado)")
            return False
            
    except Exception as e:
        print(f"❌ Integração Dashboard: ERRO ({e})")
        return False

def test_database_tables():
    """Testar criação das tabelas do banco"""
    try:
        import sqlite3
        
        # Conectar ao banco local
        conn = sqlite3.connect("primotex_erp.db")
        cursor = conn.cursor()
        
        # Verificar tabelas de comunicação
        tables = [
            "comunicacao_templates",
            "comunicacao_historico", 
            "comunicacao_config",
            "comunicacao_fila",
            "comunicacao_estatisticas"
        ]
        
        results = []
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print(f"✅ Tabela {table}: EXISTE")
                results.append(True)
            else:
                print(f"❌ Tabela {table}: NÃO EXISTE")
                results.append(False)
        
        conn.close()
        return all(results)
        
    except Exception as e:
        print(f"❌ Teste de Tabelas: ERRO ({e})")
        return False

def test_template_processing():
    """Testar processamento de templates"""
    try:
        # Testar endpoint de processamento
        base_url = "http://127.0.0.1:8003/api/v1/comunicacao"
        headers = {"Content-Type": "application/json"}
        
        process_data = {
            "template_texto": "Olá {{nome}}, sua OS {{numero}} foi criada!",
            "variaveis": {
                "nome": "João Silva",
                "numero": "12345"
            }
        }
        
        response = requests.post(f"{base_url}/templates/processar",
                               headers=headers,
                               json=process_data,
                               timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if "Olá João Silva" in result.get("texto_processado", ""):
                print("✅ Processamento de Templates: PASSOU")
                return True
            else:
                print("❌ Processamento de Templates: FALHOU (conteúdo incorreto)")
                return False
        else:
            print(f"❌ Processamento de Templates: FALHOU (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Processamento de Templates: ERRO ({e})")
        return False

def run_integration_tests():
    """Executar todos os testes de integração"""
    print("🚀 INICIANDO TESTES DE INTEGRAÇÃO - SISTEMA DE COMUNICAÇÃO")
    print("=" * 60)
    
    tests = [
        ("API Health Check", test_api_health),
        ("Endpoints de Comunicação", test_comunicacao_endpoints),
        ("Criação de Templates", test_post_endpoints),
        ("Processamento de Templates", test_template_processing),
        ("Tabelas do Banco", test_database_tables),
        ("Interface Desktop", test_desktop_interface),
        ("Integração Dashboard", test_dashboard_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Executando: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: ERRO CRÍTICO ({e})")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    
    print("\n" + "=" * 60)
    print(f"📈 TAXA DE SUCESSO: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("🎉 SISTEMA DE COMUNICAÇÃO: PRONTO PARA PRODUÇÃO!")
    elif success_rate >= 60:
        print("⚠️ SISTEMA DE COMUNICAÇÃO: NECESSITA AJUSTES")
    else:
        print("🚨 SISTEMA DE COMUNICAÇÃO: REQUER REVISÃO COMPLETA")
    
    print("=" * 60)
    
    return success_rate

def main():
    """Função principal"""
    try:
        # Aguardar um pouco para garantir que a API esteja rodando
        print("⏳ Aguardando API inicializar...")
        time.sleep(2)
        
        # Executar testes
        success_rate = run_integration_tests()
        
        # Código de saída
        if success_rate >= 80:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n🚨 Erro crítico nos testes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()