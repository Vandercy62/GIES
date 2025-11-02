#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE RECEPÇÃO SIMPLES - ERP PRIMOTEX
Sistema básico de terminal para recepção (offline)
"""

import json
import os
from datetime import datetime
from pathlib import Path

class SistemaRecepcaoSimples:
    def __init__(self):
        # Criar pasta de dados
        self.dados_folder = Path("dados_recepcao")
        self.dados_folder.mkdir(exist_ok=True)
        
        # Arquivos de dados
        self.clientes_file = self.dados_folder / "clientes.json"
        self.agendamentos_file = self.dados_folder / "agendamentos.json"
        
        # Carregar dados
        self.clientes = self.carregar_clientes()
        self.agendamentos = self.carregar_agendamentos()
        
    def carregar_clientes(self):
        """Carrega lista de clientes do arquivo"""
        if self.clientes_file.exists():
            try:
                with open(self.clientes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def carregar_agendamentos(self):
        """Carrega lista de agendamentos do arquivo"""
        if self.agendamentos_file.exists():
            try:
                with open(self.agendamentos_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def salvar_clientes(self):
        """Salva lista de clientes no arquivo"""
        with open(self.clientes_file, 'w', encoding='utf-8') as f:
            json.dump(self.clientes, f, ensure_ascii=False, indent=2)
    
    def salvar_agendamentos(self):
        """Salva lista de agendamentos no arquivo"""
        with open(self.agendamentos_file, 'w', encoding='utf-8') as f:
            json.dump(self.agendamentos, f, ensure_ascii=False, indent=2)
    
    def buscar_cliente(self):
        """Busca cliente por nome, telefone ou CPF"""
        if not self.clientes:
            print("❌ Nenhum cliente cadastrado ainda.")
            return
        
        termo = input("🔍 Digite nome, telefone ou CPF: ").strip().lower()
        
        encontrados = []
        for cliente in self.clientes:
            if (termo in cliente['nome'].lower() or 
                termo in cliente['telefone'] or 
                termo in cliente.get('cpf', '').lower()):
                encontrados.append(cliente)
        
        if encontrados:
            print(f"\n✅ {len(encontrados)} cliente(s) encontrado(s):")
            for i, cliente in enumerate(encontrados, 1):
                print(f"\n{i}. {cliente['nome']}")
                print(f"   📞 {cliente['telefone']}")
                if cliente.get('cpf'):
                    print(f"   🆔 {cliente['cpf']}")
                if cliente.get('endereco'):
                    print(f"   🏠 {cliente['endereco']}")
        else:
            print("❌ Nenhum cliente encontrado.")
    
    def cadastrar_cliente(self):
        """Cadastra novo cliente"""
        print("\n📝 CADASTRO DE NOVO CLIENTE")
        print("-" * 30)
        
        nome = input("Nome completo: ").strip()
        if not nome:
            print("❌ Nome é obrigatório!")
            return
        
        telefone = input("Telefone: ").strip()
        if not telefone:
            print("❌ Telefone é obrigatório!")
            return
        
        cpf = input("CPF/CNPJ (opcional): ").strip()
        endereco = input("Endereço (opcional): ").strip()
        email = input("Email (opcional): ").strip()
        
        cliente = {
            "id": len(self.clientes) + 1,
            "nome": nome,
            "telefone": telefone,
            "cpf": cpf,
            "endereco": endereco,
            "email": email,
            "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        self.clientes.append(cliente)
        self.salvar_clientes()
        
        print(f"✅ Cliente '{nome}' cadastrado com sucesso!")
    
    def agendar_visita(self):
        """Agenda uma visita técnica"""
        if not self.clientes:
            print("❌ Cadastre um cliente primeiro!")
            return
        
        print("\n📅 AGENDAR VISITA TÉCNICA")
        print("-" * 30)
        
        # Escolher cliente
        cliente_nome = input("Nome do cliente: ").strip()
        cliente_encontrado = None
        
        for cliente in self.clientes:
            if cliente_nome.lower() in cliente['nome'].lower():
                cliente_encontrado = cliente
                break
        
        if not cliente_encontrado:
            print("❌ Cliente não encontrado. Cadastre primeiro.")
            return
        
        # Dados do agendamento
        data = input("Data da visita (DD/MM/AAAA): ").strip()
        if not data:
            data = datetime.now().strftime("%d/%m/%Y")
        
        hora = input("Horário (HH:MM): ").strip()
        if not hora:
            hora = "14:00"
        
        servico = input("Tipo de serviço (Forro/Divisória/Orçamento): ").strip()
        if not servico:
            servico = "Visita técnica"
        
        observacoes = input("Observações (opcional): ").strip()
        
        agendamento = {
            "id": len(self.agendamentos) + 1,
            "cliente_id": cliente_encontrado['id'],
            "cliente_nome": cliente_encontrado['nome'],
            "cliente_telefone": cliente_encontrado['telefone'],
            "data": data,
            "hora": hora,
            "servico": servico,
            "observacoes": observacoes,
            "status": "Agendado",
            "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        self.agendamentos.append(agendamento)
        self.salvar_agendamentos()
        
        print(f"✅ Visita agendada para {cliente_encontrado['nome']} em {data} às {hora}")
    
    def ver_agendamentos_hoje(self):
        """Mostra agendamentos de hoje"""
        hoje = datetime.now().strftime("%d/%m/%Y")
        agendamentos_hoje = [a for a in self.agendamentos if a['data'] == hoje]
        
        if agendamentos_hoje:
            print(f"\n📅 AGENDAMENTOS DE HOJE ({hoje}):")
            print("=" * 50)
            for agenda in agendamentos_hoje:
                print(f"🕐 {agenda['hora']} - {agenda['cliente_nome']}")
                print(f"   📞 {agenda['cliente_telefone']}")
                print(f"   🔧 {agenda['servico']}")
                if agenda['observacoes']:
                    print(f"   📝 {agenda['observacoes']}")
                print(f"   ⭐ Status: {agenda['status']}")
                print("-" * 30)
        else:
            print(f"📅 Nenhum agendamento para hoje ({hoje})")
    
    def registrar_visita_realizada(self):
        """Marca visita como realizada"""
        if not self.agendamentos:
            print("❌ Nenhum agendamento encontrado.")
            return
        
        print("\n✅ REGISTRAR VISITA REALIZADA")
        print("-" * 35)
        
        # Mostrar agendamentos pendentes
        pendentes = [a for a in self.agendamentos if a['status'] == 'Agendado']
        
        if not pendentes:
            print("✅ Todas as visitas já foram registradas!")
            return
        
        print("Agendamentos pendentes:")
        for i, agenda in enumerate(pendentes, 1):
            print(f"{i}. {agenda['data']} {agenda['hora']} - {agenda['cliente_nome']}")
        
        try:
            escolha = int(input("Escolha o número da visita realizada: ")) - 1
            if 0 <= escolha < len(pendentes):
                agendamento = pendentes[escolha]
                
                # Encontrar no array principal e atualizar
                for i, a in enumerate(self.agendamentos):
                    if a['id'] == agendamento['id']:
                        self.agendamentos[i]['status'] = 'Realizada'
                        self.agendamentos[i]['data_realizacao'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                        break
                
                self.salvar_agendamentos()
                print(f"✅ Visita de {agendamento['cliente_nome']} marcada como realizada!")
            else:
                print("❌ Opção inválida!")
        except ValueError:
            print("❌ Digite um número válido!")
    
    def agenda_semana(self):
        """Mostra agenda da semana"""
        print("\n📊 AGENDA DA SEMANA")
        print("=" * 40)
        
        if not self.agendamentos:
            print("📅 Nenhum agendamento cadastrado.")
            return
        
        # Agrupar por data
        agenda_por_data = {}
        for agenda in self.agendamentos:
            data = agenda['data']
            if data not in agenda_por_data:
                agenda_por_data[data] = []
            agenda_por_data[data].append(agenda)
        
        # Mostrar ordenado por data
        for data in sorted(agenda_por_data.keys()):
            print(f"\n📅 {data}:")
            agendas_dia = sorted(agenda_por_data[data], key=lambda x: x['hora'])
            for agenda in agendas_dia:
                status_icon = "✅" if agenda['status'] == 'Realizada' else "🕐"
                print(f"   {status_icon} {agenda['hora']} - {agenda['cliente_nome']} ({agenda['servico']})")
    
    def menu_principal(self):
        """Exibe menu principal"""
        while True:
            print("\n" + "=" * 50)
            print("    SISTEMA ERP PRIMOTEX - RECEPÇÃO")
            print("=" * 50)
            print("1. 🔍 Buscar Cliente")
            print("2. 👤 Cadastrar Novo Cliente")
            print("3. 📅 Agendar Visita Técnica")
            print("4. 📋 Ver Agendamentos de Hoje")
            print("5. ✅ Registrar Visita Realizada")
            print("6. 📊 Agenda da Semana")
            print("0. ❌ Sair")
            print("=" * 50)
            
            opcao = input("Digite sua opção: ").strip()
            
            if opcao == "1":
                self.buscar_cliente()
            elif opcao == "2":
                self.cadastrar_cliente()
            elif opcao == "3":
                self.agendar_visita()
            elif opcao == "4":
                self.ver_agendamentos_hoje()
            elif opcao == "5":
                self.registrar_visita_realizada()
            elif opcao == "6":
                self.agenda_semana()
            elif opcao == "0":
                print("\n👋 Obrigado por usar o Sistema ERP Primotex!")
                print(f"📁 Dados salvos em: {self.dados_folder.absolute()}")
                break
            else:
                print("❌ Opção inválida! Digite um número de 0 a 6.")
            
            input("\nPressione Enter para continuar...")

def main():
    """Função principal"""
    try:
        sistema = SistemaRecepcaoSimples()
        sistema.menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()