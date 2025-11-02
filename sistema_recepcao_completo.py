#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE RECEPÇÃO PRIMOTEX - VERSÃO COMPLETA
Funciona tanto OFFLINE (sem internet) quanto ONLINE (com servidor)
"""

import json
import os
import sys
import requests
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import threading
from pathlib import Path

class SistemaRecepcaoCompleto:
    def __init__(self):
        # Configurações
        self.dados_folder = Path("dados_recepcao")
        self.dados_folder.mkdir(exist_ok=True)
        self.clientes_file = self.dados_folder / "clientes.json"
        self.agendamentos_file = self.dados_folder / "agendamentos.json"
        
        # URLs do servidor (configurável)
        self.servidor_urls = [
            "http://127.0.0.1:8002",
            "http://192.168.0.249:8002",
            "http://192.168.1.100:8002",
            "http://localhost:8002"
        ]
        self.servidor_ativo = None
        self.modo_online = False
        self.token_auth = None
        
        # Interface
        self.root = tk.Tk()
        self.setup_interface()
        
        # Verificar conectividade
        self.verificar_servidor()
        
    def setup_interface(self):
        """Configura a interface gráfica"""
        self.root.title("ERP PRIMOTEX - RECEPÇÃO")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status de conexão
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(self.status_frame, text="Verificando conexão...", 
                                     font=('Arial', 10, 'bold'))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.refresh_btn = ttk.Button(self.status_frame, text="🔄 Reconectar", 
                                     command=self.verificar_servidor)
        self.refresh_btn.grid(row=0, column=1, sticky=tk.E)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Aba Clientes
        self.aba_clientes = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_clientes, text="👥 Clientes")
        self.setup_aba_clientes()
        
        # Aba Agendamentos
        self.aba_agenda = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_agenda, text="📅 Agendamentos")
        self.setup_aba_agenda()
        
        # Configurar redimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def setup_aba_clientes(self):
        """Configura a aba de clientes"""
        # Frame de busca
        search_frame = ttk.Frame(self.aba_clientes)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="🔍 Buscar Cliente:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.buscar_clientes)
        
        ttk.Button(search_frame, text="🆕 Novo Cliente", 
                  command=self.novo_cliente).pack(side=tk.RIGHT, padx=5)
        
        # Lista de clientes
        self.tree_clientes = ttk.Treeview(self.aba_clientes, 
                                         columns=('Nome', 'Telefone', 'CPF', 'Origem'), 
                                         show='headings', height=15)
        
        self.tree_clientes.heading('Nome', text='Nome')
        self.tree_clientes.heading('Telefone', text='Telefone')
        self.tree_clientes.heading('CPF', text='CPF/CNPJ')
        self.tree_clientes.heading('Origem', text='Origem')
        
        self.tree_clientes.column('Nome', width=200)
        self.tree_clientes.column('Telefone', width=150)
        self.tree_clientes.column('CPF', width=150)
        self.tree_clientes.column('Origem', width=100)
        
        self.tree_clientes.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree_clientes.bind('<Double-1>', self.editar_cliente)
        
        self.carregar_clientes()
        
    def setup_aba_agenda(self):
        """Configura a aba de agendamentos"""
        # Frame de controles
        control_frame = ttk.Frame(self.aba_agenda)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="📅 Novo Agendamento", 
                  command=self.novo_agendamento).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📋 Hoje", 
                  command=self.mostrar_hoje).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📊 Esta Semana", 
                  command=self.mostrar_semana).pack(side=tk.LEFT, padx=5)
        
        # Lista de agendamentos
        self.tree_agenda = ttk.Treeview(self.aba_agenda, 
                                       columns=('Data', 'Hora', 'Cliente', 'Serviço', 'Status'), 
                                       show='headings', height=15)
        
        self.tree_agenda.heading('Data', text='Data')
        self.tree_agenda.heading('Hora', text='Hora')
        self.tree_agenda.heading('Cliente', text='Cliente')
        self.tree_agenda.heading('Serviço', text='Serviço')
        self.tree_agenda.heading('Status', text='Status')
        
        self.tree_agenda.column('Data', width=100)
        self.tree_agenda.column('Hora', width=80)
        self.tree_agenda.column('Cliente', width=200)
        self.tree_agenda.column('Serviço', width=200)
        self.tree_agenda.column('Status', width=100)
        
        self.tree_agenda.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree_agenda.bind('<Double-1>', self.editar_agendamento)
        
        self.carregar_agendamentos()
        
    def verificar_servidor(self):
        """Verifica se o servidor está disponível"""
        def check_async():
            self.modo_online = False
            self.servidor_ativo = None
            
            for url in self.servidor_urls:
                try:
                    response = requests.get(f"{url}/health", timeout=3)
                    if response.status_code == 200:
                        self.servidor_ativo = url
                        self.modo_online = True
                        # Tentar fazer login automático
                        self.fazer_login_automatico()
                        break
                except:
                    continue
            
            # Atualizar status na interface
            self.root.after(0, self.atualizar_status)
        
        threading.Thread(target=check_async, daemon=True).start()
        
    def fazer_login_automatico(self):
        """Tenta fazer login automático com credenciais padrão"""
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            response = requests.post(f"{self.servidor_ativo}/api/v1/auth/login", 
                                   json=login_data, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.token_auth = data.get("access_token")
        except:
            pass
            
    def atualizar_status(self):
        """Atualiza o status da conexão na interface"""
        if self.modo_online:
            self.status_label.config(text=f"🟢 ONLINE - Conectado ao servidor: {self.servidor_ativo}", 
                                   foreground='green')
            # Recarregar dados do servidor
            self.carregar_clientes()
            self.carregar_agendamentos()
        else:
            self.status_label.config(text="🔴 OFFLINE - Usando dados locais", 
                                   foreground='red')
            
    def get_headers(self):
        """Retorna headers para requisições autenticadas"""
        if self.token_auth:
            return {"Authorization": f"Bearer {self.token_auth}"}
        return {}
        
    def carregar_clientes(self):
        """Carrega clientes do servidor ou arquivo local"""
        self.tree_clientes.delete(*self.tree_clientes.get_children())
        
        if self.modo_online and self.token_auth:
            # Carregar do servidor
            try:
                response = requests.get(f"{self.servidor_ativo}/api/v1/clientes", 
                                      headers=self.get_headers(), timeout=5)
                if response.status_code == 200:
                    clientes = response.json()
                    for cliente in clientes:
                        self.tree_clientes.insert('', 'end', values=(
                            cliente.get('nome', ''),
                            cliente.get('telefone', ''),
                            cliente.get('cpf_cnpj', ''),
                            'Servidor'
                        ))
                    return
            except:
                pass
        
        # Carregar arquivo local
        if self.clientes_file.exists():
            try:
                with open(self.clientes_file, 'r', encoding='utf-8') as f:
                    clientes = json.load(f)
                    for cliente in clientes:
                        self.tree_clientes.insert('', 'end', values=(
                            cliente['nome'],
                            cliente['telefone'],
                            cliente.get('cpf', ''),
                            'Local'
                        ))
            except:
                pass
                
    def carregar_agendamentos(self):
        """Carrega agendamentos do servidor ou arquivo local"""
        self.tree_agenda.delete(*self.tree_agenda.get_children())
        
        if self.modo_online:
            # Tentar carregar do servidor (implementar quando API estiver pronta)
            pass
        
        # Carregar arquivo local
        if self.agendamentos_file.exists():
            try:
                with open(self.agendamentos_file, 'r', encoding='utf-8') as f:
                    agendamentos = json.load(f)
                    for agenda in agendamentos:
                        self.tree_agenda.insert('', 'end', values=(
                            agenda['data'],
                            agenda['hora'],
                            agenda['cliente'],
                            agenda['servico'],
                            agenda.get('status', 'Agendado')
                        ))
            except:
                pass
                
    def buscar_clientes(self, event=None):
        """Busca clientes conforme texto digitado"""
        termo = self.search_var.get().lower()
        
        # Limpar lista atual
        self.tree_clientes.delete(*self.tree_clientes.get_children())
        
        if self.modo_online and self.token_auth:
            # Buscar no servidor
            try:
                response = requests.get(f"{self.servidor_ativo}/api/v1/clientes", 
                                      headers=self.get_headers(), timeout=5)
                if response.status_code == 200:
                    clientes = response.json()
                    for cliente in clientes:
                        nome = cliente.get('nome', '').lower()
                        telefone = cliente.get('telefone', '').lower()
                        if termo in nome or termo in telefone:
                            self.tree_clientes.insert('', 'end', values=(
                                cliente.get('nome', ''),
                                cliente.get('telefone', ''),
                                cliente.get('cpf_cnpj', ''),
                                'Servidor'
                            ))
                    return
            except:
                pass
        
        # Buscar local
        if self.clientes_file.exists():
            try:
                with open(self.clientes_file, 'r', encoding='utf-8') as f:
                    clientes = json.load(f)
                    for cliente in clientes:
                        if (termo in cliente['nome'].lower() or 
                            termo in cliente['telefone'].lower()):
                            self.tree_clientes.insert('', 'end', values=(
                                cliente['nome'],
                                cliente['telefone'],
                                cliente.get('cpf', ''),
                                'Local'
                            ))
            except:
                pass
                
    def novo_cliente(self):
        """Abre janela para cadastrar novo cliente"""
        ClienteWindow(self, None)
        
    def editar_cliente(self, event):
        """Edita cliente selecionado"""
        selection = self.tree_clientes.selection()
        if selection:
            item = self.tree_clientes.item(selection[0])
            values = item['values']
            ClienteWindow(self, values)
            
    def novo_agendamento(self):
        """Abre janela para novo agendamento"""
        AgendamentoWindow(self, None)
        
    def editar_agendamento(self, event):
        """Edita agendamento selecionado"""
        selection = self.tree_agenda.selection()
        if selection:
            item = self.tree_agenda.item(selection[0])
            values = item['values']
            AgendamentoWindow(self, values)
            
    def mostrar_hoje(self):
        """Filtra agendamentos de hoje"""
        hoje = datetime.now().strftime('%d/%m/%Y')
        self.filtrar_agendamentos_por_data(hoje)
        
    def mostrar_semana(self):
        """Filtra agendamentos desta semana"""
        hoje = datetime.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        
        # Implementar filtro por período
        self.carregar_agendamentos()
        
    def filtrar_agendamentos_por_data(self, data_filtro):
        """Filtra agendamentos por data específica"""
        self.tree_agenda.delete(*self.tree_agenda.get_children())
        
        if self.agendamentos_file.exists():
            try:
                with open(self.agendamentos_file, 'r', encoding='utf-8') as f:
                    agendamentos = json.load(f)
                    for agenda in agendamentos:
                        if agenda['data'] == data_filtro:
                            self.tree_agenda.insert('', 'end', values=(
                                agenda['data'],
                                agenda['hora'],
                                agenda['cliente'],
                                agenda['servico'],
                                agenda.get('status', 'Agendado')
                            ))
            except:
                pass
                
    def salvar_cliente_local(self, cliente_data):
        """Salva cliente no arquivo local"""
        clientes = []
        if self.clientes_file.exists():
            try:
                with open(self.clientes_file, 'r', encoding='utf-8') as f:
                    clientes = json.load(f)
            except:
                pass
        
        clientes.append(cliente_data)
        
        with open(self.clientes_file, 'w', encoding='utf-8') as f:
            json.dump(clientes, f, ensure_ascii=False, indent=2)
            
    def salvar_agendamento_local(self, agenda_data):
        """Salva agendamento no arquivo local"""
        agendamentos = []
        if self.agendamentos_file.exists():
            try:
                with open(self.agendamentos_file, 'r', encoding='utf-8') as f:
                    agendamentos = json.load(f)
            except:
                pass
        
        agendamentos.append(agenda_data)
        
        with open(self.agendamentos_file, 'w', encoding='utf-8') as f:
            json.dump(agendamentos, f, ensure_ascii=False, indent=2)
            
    def run(self):
        """Inicia a aplicação"""
        self.root.mainloop()


class ClienteWindow:
    def __init__(self, parent, cliente_data):
        self.parent = parent
        self.cliente_data = cliente_data
        
        self.window = tk.Toplevel(parent.root)
        self.window.title("Cliente")
        self.window.geometry("400x300")
        self.window.transient(parent.root)
        self.window.grab_set()
        
        self.setup_form()
        
    def setup_form(self):
        """Configura o formulário de cliente"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Nome
        ttk.Label(main_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nome_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.nome_var, width=40).grid(row=0, column=1, pady=5)
        
        # Telefone
        ttk.Label(main_frame, text="Telefone:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.telefone_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.telefone_var, width=40).grid(row=1, column=1, pady=5)
        
        # CPF/CNPJ
        ttk.Label(main_frame, text="CPF/CNPJ:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.cpf_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.cpf_var, width=40).grid(row=2, column=1, pady=5)
        
        # Email
        ttk.Label(main_frame, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.email_var, width=40).grid(row=3, column=1, pady=5)
        
        # Endereço
        ttk.Label(main_frame, text="Endereço:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.endereco_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.endereco_var, width=40).grid(row=4, column=1, pady=5)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Salvar", command=self.salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Preencher dados se estiver editando
        if self.cliente_data:
            self.nome_var.set(self.cliente_data[0])
            self.telefone_var.set(self.cliente_data[1])
            self.cpf_var.set(self.cliente_data[2])
            
    def salvar(self):
        """Salva o cliente"""
        if not self.nome_var.get() or not self.telefone_var.get():
            messagebox.showerror("Erro", "Nome e telefone são obrigatórios!")
            return
            
        cliente_data = {
            "nome": self.nome_var.get(),
            "telefone": self.telefone_var.get(),
            "cpf_cnpj": self.cpf_var.get(),
            "email": self.email_var.get(),
            "endereco": self.endereco_var.get(),
            "data_cadastro": datetime.now().isoformat()
        }
        
        sucesso = False
        
        # Tentar salvar no servidor primeiro
        if self.parent.modo_online and self.parent.token_auth:
            try:
                response = requests.post(f"{self.parent.servidor_ativo}/api/v1/clientes", 
                                       json=cliente_data, 
                                       headers=self.parent.get_headers(), 
                                       timeout=5)
                if response.status_code == 200:
                    sucesso = True
                    messagebox.showinfo("Sucesso", "Cliente salvo no servidor!")
            except:
                pass
        
        # Se não conseguiu salvar no servidor, salvar localmente
        if not sucesso:
            self.parent.salvar_cliente_local(cliente_data)
            messagebox.showinfo("Sucesso", "Cliente salvo localmente!")
        
        # Recarregar lista
        self.parent.carregar_clientes()
        self.window.destroy()


class AgendamentoWindow:
    def __init__(self, parent, agenda_data):
        self.parent = parent
        self.agenda_data = agenda_data
        
        self.window = tk.Toplevel(parent.root)
        self.window.title("Agendamento")
        self.window.geometry("400x350")
        self.window.transient(parent.root)
        self.window.grab_set()
        
        self.setup_form()
        
    def setup_form(self):
        """Configura o formulário de agendamento"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cliente
        ttk.Label(main_frame, text="Cliente:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cliente_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.cliente_var, width=40).grid(row=0, column=1, pady=5)
        
        # Data
        ttk.Label(main_frame, text="Data (DD/MM/AAAA):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.data_var = tk.StringVar()
        data_entry = ttk.Entry(main_frame, textvariable=self.data_var, width=40)
        data_entry.grid(row=1, column=1, pady=5)
        # Preencher com data atual
        self.data_var.set(datetime.now().strftime('%d/%m/%Y'))
        
        # Hora
        ttk.Label(main_frame, text="Hora (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.hora_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.hora_var, width=40).grid(row=2, column=1, pady=5)
        
        # Serviço
        ttk.Label(main_frame, text="Serviço:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.servico_var = tk.StringVar()
        servico_combo = ttk.Combobox(main_frame, textvariable=self.servico_var, width=37)
        servico_combo['values'] = (
            'Instalação de Forro',
            'Instalação de Divisória',
            'Manutenção',
            'Orçamento',
            'Visita Técnica',
            'Outro'
        )
        servico_combo.grid(row=3, column=1, pady=5)
        
        # Observações
        ttk.Label(main_frame, text="Observações:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.obs_text = tk.Text(main_frame, width=30, height=4)
        self.obs_text.grid(row=4, column=1, pady=5)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Salvar", command=self.salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Preencher dados se estiver editando
        if self.agenda_data:
            self.data_var.set(self.agenda_data[0])
            self.hora_var.set(self.agenda_data[1])
            self.cliente_var.set(self.agenda_data[2])
            self.servico_var.set(self.agenda_data[3])
            
    def salvar(self):
        """Salva o agendamento"""
        if not all([self.cliente_var.get(), self.data_var.get(), 
                   self.hora_var.get(), self.servico_var.get()]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
            
        agenda_data = {
            "cliente": self.cliente_var.get(),
            "data": self.data_var.get(),
            "hora": self.hora_var.get(),
            "servico": self.servico_var.get(),
            "observacoes": self.obs_text.get("1.0", tk.END).strip(),
            "status": "Agendado",
            "data_criacao": datetime.now().isoformat()
        }
        
        # Salvar localmente (implementar API de agendamentos depois)
        self.parent.salvar_agendamento_local(agenda_data)
        messagebox.showinfo("Sucesso", "Agendamento salvo!")
        
        # Recarregar lista
        self.parent.carregar_agendamentos()
        self.window.destroy()


def main():
    """Função principal"""
    print("=" * 60)
    print("    SISTEMA DE RECEPÇÃO PRIMOTEX - VERSÃO COMPLETA")
    print("=" * 60)
    print("🔄 Verificando conexão com servidor...")
    print("📱 Modo híbrido: ONLINE (servidor) + OFFLINE (local)")
    print("=" * 60)
    
    try:
        app = SistemaRecepcaoCompleto()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        input("Pressione Enter para sair...")


if __name__ == "__main__":
    main()