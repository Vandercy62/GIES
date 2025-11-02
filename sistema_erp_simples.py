#!/usr/bin/env python3
"""
Sistema ERP Primotex - Versão Simplificada sem Problemas
"""

import json
import os
from datetime import datetime, timedelta
import subprocess
import sys

def criar_sistema_basico():
    """Cria um sistema básico funcional"""
    print("🚀 SISTEMA ERP PRIMOTEX - VERSÃO SIMPLIFICADA")
    print("=" * 50)
    
    # Dados de exemplo
    dados = {
        "clientes": [
            {
                "id": 1,
                "nome": "João Silva",
                "email": "joao@email.com",
                "telefone": "(11) 99999-9999",
                "endereco": "Rua A, 123"
            },
            {
                "id": 2,
                "nome": "Maria Santos",
                "email": "maria@email.com", 
                "telefone": "(11) 88888-8888",
                "endereco": "Av. B, 456"
            }
        ],
        "produtos": [
            {
                "id": 1,
                "nome": "Forro PVC Branco",
                "preco": 25.50,
                "estoque": 100,
                "categoria": "Forros"
            },
            {
                "id": 2,
                "nome": "Divisória Eucatex",
                "preco": 180.00,
                "estoque": 50,
                "categoria": "Divisórias"
            }
        ],
        "recepcao": [],
        "login": {
            "usuario": "admin",
            "senha": "admin123",
            "ultimo_acesso": datetime.now().isoformat()
        }
    }
    
    # Salvar dados
    with open('dados_erp.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    print("✅ Base de dados criada: dados_erp.json")
    return True

def menu_principal():
    """Menu principal do sistema"""
    while True:
        print("\n" + "=" * 50)
        print("🏢 ERP PRIMOTEX - SISTEMA SIMPLIFICADO")
        print("=" * 50)
        print("1. 📋 Ver Clientes")
        print("2. 📦 Ver Produtos") 
        print("3. 👥 Recepção de Visitas")
        print("4. 📊 Relatório Rápido")
        print("5. 🔧 Configurações")
        print("6. 🚪 Sair")
        print("=" * 50)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            mostrar_clientes()
        elif opcao == "2":
            mostrar_produtos()
        elif opcao == "3":
            recepcao_visitas()
        elif opcao == "4":
            relatorio_rapido()
        elif opcao == "5":
            configuracoes()
        elif opcao == "6":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")

def carregar_dados():
    """Carrega dados do arquivo JSON"""
    try:
        with open('dados_erp.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("📁 Criando base de dados...")
        criar_sistema_basico()
        return carregar_dados()

def salvar_dados(dados):
    """Salva dados no arquivo JSON"""
    with open('dados_erp.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def mostrar_clientes():
    """Mostra lista de clientes"""
    dados = carregar_dados()
    print("\n📋 CLIENTES CADASTRADOS")
    print("-" * 40)
    
    for cliente in dados['clientes']:
        print(f"ID: {cliente['id']}")
        print(f"Nome: {cliente['nome']}")
        print(f"Email: {cliente['email']}")
        print(f"Telefone: {cliente['telefone']}")
        print(f"Endereço: {cliente['endereco']}")
        print("-" * 40)
    
    input("\n📌 Pressione Enter para continuar...")

def mostrar_produtos():
    """Mostra lista de produtos"""
    dados = carregar_dados()
    print("\n📦 PRODUTOS CADASTRADOS")
    print("-" * 50)
    
    for produto in dados['produtos']:
        print(f"ID: {produto['id']}")
        print(f"Nome: {produto['nome']}")
        print(f"Preço: R$ {produto['preco']:.2f}")
        print(f"Estoque: {produto['estoque']} unidades")
        print(f"Categoria: {produto['categoria']}")
        print("-" * 50)
    
    input("\n📌 Pressione Enter para continuar...")

def recepcao_visitas():
    """Sistema de recepção"""
    dados = carregar_dados()
    print("\n👥 RECEPÇÃO DE VISITAS")
    print("-" * 30)
    
    nome = input("Nome do visitante: ").strip()
    empresa = input("Empresa: ").strip()
    motivo = input("Motivo da visita: ").strip()
    
    if nome:
        visita = {
            "id": len(dados['recepcao']) + 1,
            "nome": nome,
            "empresa": empresa,
            "motivo": motivo,
            "data_hora": datetime.now().isoformat(),
            "status": "Aguardando"
        }
        
        dados['recepcao'].append(visita)
        salvar_dados(dados)
        
        print(f"\n✅ Visita registrada!")
        print(f"ID: {visita['id']}")
        print(f"Visitante: {nome}")
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    input("\n📌 Pressione Enter para continuar...")

def relatorio_rapido():
    """Relatório rápido do sistema"""
    dados = carregar_dados()
    print("\n📊 RELATÓRIO RÁPIDO")
    print("=" * 30)
    
    total_clientes = len(dados['clientes'])
    total_produtos = len(dados['produtos'])
    total_visitas = len(dados['recepcao'])
    
    valor_estoque = sum(p['preco'] * p['estoque'] for p in dados['produtos'])
    
    print(f"👥 Total de Clientes: {total_clientes}")
    print(f"📦 Total de Produtos: {total_produtos}")
    print(f"🏢 Visitas Hoje: {total_visitas}")
    print(f"💰 Valor do Estoque: R$ {valor_estoque:.2f}")
    print("=" * 30)
    
    input("\n📌 Pressione Enter para continuar...")

def configuracoes():
    """Configurações do sistema"""
    print("\n🔧 CONFIGURAÇÕES")
    print("-" * 20)
    print("1. 🔄 Reiniciar Sistema")
    print("2. 📊 Iniciar Servidor Web")
    print("3. 🌐 Configurar Rede")
    print("4. 📱 Sistema Recepção GUI")
    print("5. ← Voltar")
    
    opcao = input("Escolha: ").strip()
    
    if opcao == "1":
        print("🔄 Reiniciando...")
        os.system('cls' if os.name == 'nt' else 'clear')
    elif opcao == "2":
        print("📊 Iniciando servidor...")
        try:
            subprocess.Popen([sys.executable, "sistema_recepcao_completo.py"])
            print("✅ Servidor iniciado!")
        except:
            print("❌ Erro ao iniciar servidor")
    elif opcao == "3":
        os.system(f'{sys.executable} configurador_rede.py')
    elif opcao == "4":
        try:
            subprocess.Popen([sys.executable, "sistema_recepcao_completo.py"])
            print("✅ Interface gráfica iniciada!")
        except:
            print("❌ Erro ao iniciar interface")

def main():
    """Função principal"""
    print("🔑 LOGIN ERP PRIMOTEX")
    print("=" * 25)
    
    usuario = input("Usuário: ").strip()
    senha = input("Senha: ").strip()
    
    if usuario == "admin" and senha == "admin123":
        print("✅ Login realizado com sucesso!")
        input("📌 Pressione Enter para continuar...")
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Criar dados se não existir
        if not os.path.exists('dados_erp.json'):
            criar_sistema_basico()
        
        menu_principal()
    else:
        print("❌ Credenciais inválidas!")
        print("💡 Use: admin / admin123")

if __name__ == "__main__":
    main()