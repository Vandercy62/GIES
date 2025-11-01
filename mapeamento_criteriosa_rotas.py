#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAPEAMENTO CRITERIOSA DAS ROTAS - PASSO 3
==========================================

Análise detalhada de todas as 87 rotas disponíveis no sistema.
Validação criteriosa de cada módulo e endpoint.

Data: 01/11/2025
Status: Mapeamento de Rotas
"""

import requests
import json
from datetime import datetime


def buscar_openapi_spec():
    """Buscar especificação OpenAPI completa"""
    print("📋 BUSCANDO ESPECIFICAÇÃO OPENAPI")
    print("=" * 50)
    
    try:
        response = requests.get(
            "http://127.0.0.1:8002/openapi.json",
            timeout=10
        )
        
        if response.status_code == 200:
            spec = response.json()
            print(f"✅ OpenAPI carregado")
            print(f"   📊 Título: {spec.get('info', {}).get('title', 'N/A')}")
            print(f"   🔢 Versão: {spec.get('info', {}).get('version', 'N/A')}")
            print(f"   📖 Descrição: {spec.get('info', {}).get('description', 'N/A')[:100]}...")
            
            return spec
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None


def analisar_rotas_por_modulo(openapi_spec):
    """Analisar e categorizar rotas por módulo"""
    print("\n🗂️ ANÁLISE DE ROTAS POR MÓDULO")
    print("=" * 60)
    
    if not openapi_spec or "paths" not in openapi_spec:
        print("❌ Especificação inválida")
        return {}
    
    paths = openapi_spec["paths"]
    modulos = {}
    
    # Categorizar rotas por módulo
    for path, methods in paths.items():
        for method, details in methods.items():
            tags = details.get("tags", ["Outros"])
            tag = tags[0] if tags else "Outros"
            
            if tag not in modulos:
                modulos[tag] = []
            
            modulos[tag].append({
                "path": path,
                "method": method.upper(),
                "summary": details.get("summary", ""),
                "description": details.get("description", ""),
                "parameters": details.get("parameters", []),
                "responses": list(details.get("responses", {}).keys())
            })
    
    # Relatório detalhado por módulo
    total_rotas = 0
    for modulo, rotas in sorted(modulos.items()):
        count = len(rotas)
        total_rotas += count
        
        print(f"\n📁 {modulo}: {count} rotas")
        print("-" * 40)
        
        for i, rota in enumerate(rotas, 1):
            status_codes = ", ".join(rota["responses"])
            print(f"   {i:2d}. {rota['method']:6s} {rota['path']}")
            print(f"       📝 {rota['summary'][:60]}...")
            print(f"       📊 Respostas: {status_codes}")
            
            if rota["parameters"]:
                params = [p.get("name", "N/A") for p in rota["parameters"]]
                print(f"       🔧 Parâmetros: {', '.join(params[:3])}...")
    
    print(f"\n📊 TOTAL GERAL: {total_rotas} rotas em {len(modulos)} módulos")
    return modulos


def testar_endpoints_criticos(token):
    """Testar endpoints críticos com token válido"""
    print(f"\n🔍 TESTANDO ENDPOINTS CRÍTICOS")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints_teste = [
        {
            "url": "http://127.0.0.1:8002/api/v1/auth/me",
            "method": "GET",
            "description": "Perfil do usuário"
        },
        {
            "url": "http://127.0.0.1:8002/api/v1/clientes",
            "method": "GET",
            "description": "Lista de clientes"
        },
        {
            "url": "http://127.0.0.1:8002/api/v1/auth/profiles",
            "method": "GET",
            "description": "Perfis disponíveis"
        },
        {
            "url": "http://127.0.0.1:8002/api/v1/ordem-servico",
            "method": "GET",
            "description": "Ordens de serviço"
        },
        {
            "url": "http://127.0.0.1:8002/api/v1/financeiro/categorias",
            "method": "GET",
            "description": "Categorias financeiras"
        }
    ]
    
    resultados = []
    
    for endpoint in endpoints_teste:
        print(f"\n🎯 Testando: {endpoint['description']}")
        print(f"   📡 {endpoint['method']} {endpoint['url']}")
        
        try:
            if endpoint["method"] == "GET":
                response = requests.get(endpoint["url"], headers=headers, timeout=10)
            else:
                response = requests.post(endpoint["url"], headers=headers, timeout=10)
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   📋 Dados: Lista com {len(data)} itens")
                    elif isinstance(data, dict):
                        print(f"   📋 Dados: Objeto com {len(data)} campos")
                    else:
                        print(f"   📋 Dados: {type(data).__name__}")
                    print(f"   ✅ Sucesso!")
                except:
                    print(f"   📋 Dados: Resposta não-JSON")
                    print(f"   ✅ Sucesso!")
            else:
                error_msg = response.text[:100] if response.text else "Sem detalhes"
                print(f"   ❌ Erro: {error_msg}")
            
            resultados.append({
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": response.status_code == 200
            })
            
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            resultados.append({
                "endpoint": endpoint,
                "status_code": None,
                "success": False,
                "error": str(e)
            })
    
    # Resumo dos testes
    sucessos = sum(1 for r in resultados if r["success"])
    print(f"\n📈 RESUMO DOS TESTES:")
    print(f"   Total testado: {len(endpoints_teste)}")
    print(f"   Sucessos: {sucessos}")
    print(f"   Falhas: {len(endpoints_teste) - sucessos}")
    
    return resultados


def main():
    """Função principal de mapeamento"""
    print("🗺️ MAPEAMENTO CRITERIOSA DAS ROTAS")
    print("🎯 Análise detalhada de todos os 87 endpoints")
    print("=" * 70)
    
    # 1. Buscar especificação OpenAPI
    openapi_spec = buscar_openapi_spec()
    
    if not openapi_spec:
        print("❌ Não foi possível carregar especificação")
        return
    
    # 2. Analisar rotas por módulo
    modulos = analisar_rotas_por_modulo(openapi_spec)
    
    # 3. Obter token para testes
    print(f"\n🔐 OBTENDO TOKEN PARA TESTES")
    print("-" * 40)
    
    try:
        login_response = requests.post(
            "http://127.0.0.1:8002/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print(f"✅ Token obtido: {token[:30]}...")
            
            # 4. Testar endpoints críticos
            resultados_teste = testar_endpoints_criticos(token)
        else:
            print(f"❌ Falha no login: {login_response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Erro ao obter token: {e}")
        return
    
    # 5. Relatório final
    print(f"\n📊 RELATÓRIO FINAL DE MAPEAMENTO")
    print("=" * 60)
    
    print(f"\n🗂️ MÓDULOS IDENTIFICADOS:")
    for modulo, rotas in sorted(modulos.items()):
        status = "🟢" if modulo in ["Autenticação", "Clientes"] else "🟡"
        print(f"   {status} {modulo}: {len(rotas)} rotas")
    
    print(f"\n🔍 ENDPOINTS TESTADOS:")
    for resultado in resultados_teste:
        endpoint = resultado["endpoint"]
        status = "✅" if resultado["success"] else "❌"
        print(f"   {status} {endpoint['description']}: {resultado.get('status_code', 'N/A')}")
    
    print(f"\n✅ MAPEAMENTO CONCLUÍDO COM CRITÉRIO")
    print(f"🎯 Sistema com {sum(len(rotas) for rotas in modulos.values())} rotas mapeadas")
    print("=" * 70)


if __name__ == "__main__":
    main()