"""
SISTEMA ERP PRIMOTEX - INTERFACE DE CLIENTES
============================================

Interface completa para gerenciamento de clientes com CRUD.
Integração com API backend para persistência de dados.

Autor: GitHub Copilot
Data: 29/10/2025
"""

# Constantes da UI centralizadas
from frontend.desktop.ui_constants import KEYBOARD_EVENTS, PERSON_TYPES

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from typing import Dict, Any, Optional, List
import re

# Importar middleware de autenticação
from frontend.desktop.auth_middleware import (
    require_login,
    get_token_for_api,
    create_auth_header,
    get_current_user_info
)

# =======================================
# CONFIGURAÇÕES
# =======================================

API_BASE_URL = "http://127.0.0.1:8002"

# =======================================
# CLASSE INTERFACE DE CLIENTES
# =======================================

@require_login()
class ClientesWindow:
    """Interface de gerenciamento de clientes"""
    
    def __init__(self, parent_window=None):
        # NÃO recebe mais user_data - usa SessionManager
        self.token = get_token_for_api()
        self.user_data = get_current_user_info()
        self.parent_window = parent_window
        
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.clientes_data = []
        self.cliente_selecionado = None
        
        self.setup_window()
        self.create_widgets()
        self.carregar_clientes()
    
    def setup_window(self):
        """Configurar janela"""
        
        self.root.title("Sistema ERP Primotex - Gerenciamento de Clientes")
        self.root.geometry("1400x900")
        
        if not self.parent_window:
            self.root.state('zoomed')  # Maximizar se for janela principal
        
        self.root.configure(bg='#f8f9fa')
        
        # Configurar protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Criar widgets da interface"""
        
        # === BARRA SUPERIOR ===
        self.create_top_bar()
        
        # === CONTAINER PRINCIPAL ===
        main_container = tk.Frame(self.root, bg='#f8f9fa')
        main_container.pack(fill='both', expand=True, padx=15, pady=10)
        
        # === BARRA DE FERRAMENTAS ===
        self.create_toolbar(main_container)
        
        # === ÁREA PRINCIPAL ===
        content_frame = tk.Frame(main_container, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True, pady=10)
        
        # === ÁREA DE LISTAGEM (ESQUERDA) ===
        self.create_list_area(content_frame)
        
        # === ÁREA DE FORMULÁRIO (DIREITA) ===
        self.create_form_area(content_frame)
    
    def create_top_bar(self):
        """Criar barra superior"""
        
        top_frame = tk.Frame(self.root, bg='#2c3e50', height=50)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)
        
        # Container interno
        container = tk.Frame(top_frame, bg='#2c3e50')
        container.pack(fill='both', expand=True, padx=20, pady=8)
        
        # Título
        title_label = tk.Label(
            container,
            text="👥 Gerenciamento de Clientes",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(side='left', pady=5)
        
        # Informações do usuário (direita)
        user_info = f"📱 Usuário: {self.user_data.get('user', {}).get('username', 'N/A')}"
        user_label = tk.Label(
            container,
            text=user_info,
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        user_label.pack(side='right', pady=5)
    
    def create_toolbar(self, parent):
        """Criar barra de ferramentas"""
        
        toolbar = tk.Frame(parent, bg='#ecf0f1', relief='raised', bd=1)
        toolbar.pack(fill='x', pady=(0, 10))
        
        # Container interno
        toolbar_content = tk.Frame(toolbar, bg='#ecf0f1')
        toolbar_content.pack(fill='x', padx=10, pady=8)
        
        # Botões da esquerda
        left_frame = tk.Frame(toolbar_content, bg='#ecf0f1')
        left_frame.pack(side='left')
        
        # Botão Novo
        self.btn_novo = tk.Button(
            left_frame,
            text="➕ Novo Cliente",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.novo_cliente
        )
        self.btn_novo.pack(side='left', padx=(0, 10))
        
        # Botão Editar
        self.btn_editar = tk.Button(
            left_frame,
            text="✏️ Editar",
            font=('Arial', 10),
            bg='#f39c12',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            state='disabled',
            command=self.editar_cliente
        )
        self.btn_editar.pack(side='left', padx=(0, 10))
        
        # Botão Excluir
        self.btn_excluir = tk.Button(
            left_frame,
            text="🗑️ Excluir",
            font=('Arial', 10),
            bg='#e74c3c',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            state='disabled',
            command=self.excluir_cliente
        )
        self.btn_excluir.pack(side='left', padx=(0, 10))
        
        # Separador
        separator = tk.Frame(left_frame, bg='#bdc3c7', width=2, height=30)
        separator.pack(side='left', padx=15)
        
        # Botão Atualizar
        self.btn_atualizar = tk.Button(
            left_frame,
            text="🔄 Atualizar",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.carregar_clientes
        )
        self.btn_atualizar.pack(side='left')
        
        # Campo de busca (direita)
        right_frame = tk.Frame(toolbar_content, bg='#ecf0f1')
        right_frame.pack(side='right')
        
        tk.Label(
            right_frame,
            text="🔍 Buscar:",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(side='left', padx=(0, 5))
        
        self.entry_busca = tk.Entry(
            right_frame,
            font=('Arial', 10),
            width=25,
            bg='white',
            relief='flat',
            bd=5
        )
        self.entry_busca.pack(side='left', padx=(0, 10))
        self.entry_busca.bind(KEYBOARD_EVENTS['key_release'], self.filtrar_clientes)
        
        btn_buscar = tk.Button(
            right_frame,
            text="Buscar",
            font=('Arial', 9),
            bg='#95a5a6',
            fg='white',
            padx=10,
            pady=3,
            border=0,
            command=self.filtrar_clientes
        )
        btn_buscar.pack(side='left')
    
    def create_list_area(self, parent):
        """Criar área de listagem de clientes"""
        
        # Frame da listagem
        list_frame = tk.LabelFrame(
            parent,
            text="📋 Lista de Clientes",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            relief='raised',
            bd=1
        )
        list_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Configurar Treeview
        columns = ('id', 'nome', 'tipo', 'documento', 'telefone', 'email', 'status')
        
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=20
        )
        
        # Configurar cabeçalhos
        self.tree.heading('id', text='ID')
        self.tree.heading('nome', text='Nome/Razão Social')
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('documento', text='CPF/CNPJ')
        self.tree.heading('telefone', text='Telefone')
        self.tree.heading('email', text='Email')
        self.tree.heading('status', text='Status')
        
        # Configurar larguras das colunas
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('nome', width=250, anchor='w')
        self.tree.column('tipo', width=80, anchor='center')
        self.tree.column('documento', width=150, anchor='center')
        self.tree.column('telefone', width=120, anchor='center')
        self.tree.column('email', width=200, anchor='w')
        self.tree.column('status', width=80, anchor='center')
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack scrollbars e treeview
        self.tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        v_scroll.pack(side='right', fill='y', pady=10)
        h_scroll.pack(side='bottom', fill='x', padx=(10, 0))
        
        # Bind eventos
        self.tree.bind('<<TreeviewSelect>>', self.on_cliente_selecionado)
        self.tree.bind('<Double-1>', self.editar_cliente)
        
        # Contador de registros
        self.label_contador = tk.Label(
            list_frame,
            text="Total: 0 clientes",
            font=('Arial', 9),
            bg='white',
            fg='#7f8c8d'
        )
        self.label_contador.pack(side='bottom', pady=(0, 10))
    
    def create_form_area(self, parent):
        """Criar área do formulário"""
        
        # Frame do formulário
        form_frame = tk.LabelFrame(
            parent,
            text="📝 Dados do Cliente",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            relief='raised',
            bd=1,
            width=400
        )
        form_frame.pack(side='right', fill='y')
        form_frame.pack_propagate(False)
        
        # Scroll area para o formulário
        canvas = tk.Canvas(form_frame, bg='white')
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        self.form_content = tk.Frame(canvas, bg='white')
        
        self.form_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.form_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Campos do formulário
        self.create_form_fields()
        
        # Botões do formulário
        self.create_form_buttons()
    
    def create_form_fields(self):
        """Criar campos do formulário"""
        
        # ID (oculto para edição)
        self.var_id = tk.StringVar()
        
        # Tipo de cliente
        tk.Label(
            self.form_content,
            text="Tipo de Cliente *",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(10, 2))
        
        self.var_tipo = tk.StringVar(value=PERSON_TYPES['fisica'])
        tipo_frame = tk.Frame(self.form_content, bg='white')
        tipo_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Radiobutton(
            tipo_frame,
            text="Pessoa Física",
            variable=self.var_tipo,
            value="Física",
            font=('Arial', 9),
            bg='white',
            command=self.on_tipo_changed
        ).pack(side='left', padx=(0, 20))
        
        tk.Radiobutton(
            tipo_frame,
            text="Pessoa Jurídica",
            variable=self.var_tipo,
            value="Jurídica",
            font=('Arial', 9),
            bg='white',
            command=self.on_tipo_changed
        ).pack(side='left')
        
        # Nome/Razão Social
        self.label_nome = tk.Label(
            self.form_content,
            text="Nome Completo *",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        self.label_nome.pack(anchor='w', padx=10, pady=(10, 2))
        
        self.var_nome = tk.StringVar()
        self.entry_nome = tk.Entry(
            self.form_content,
            textvariable=self.var_nome,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=5
        )
        self.entry_nome.pack(fill='x', padx=10, pady=(0, 10))
        
        # CPF/CNPJ
        self.label_documento = tk.Label(
            self.form_content,
            text="CPF *",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        self.label_documento.pack(anchor='w', padx=10, pady=(0, 2))
        
        self.var_documento = tk.StringVar()
        self.entry_documento = tk.Entry(
            self.form_content,
            textvariable=self.var_documento,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=5
        )
        self.entry_documento.pack(fill='x', padx=10, pady=(0, 10))
        self.entry_documento.bind('<KeyRelease>', self.format_documento)
        
        # Email
        tk.Label(
            self.form_content,
            text="Email *",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(0, 2))
        
        self.var_email = tk.StringVar()
        self.entry_email = tk.Entry(
            self.form_content,
            textvariable=self.var_email,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=5
        )
        self.entry_email.pack(fill='x', padx=10, pady=(0, 10))
        
        # Telefone
        tk.Label(
            self.form_content,
            text="Telefone *",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(0, 2))
        
        self.var_telefone = tk.StringVar()
        self.entry_telefone = tk.Entry(
            self.form_content,
            textvariable=self.var_telefone,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=5
        )
        self.entry_telefone.pack(fill='x', padx=10, pady=(0, 10))
        self.entry_telefone.bind('<KeyRelease>', self.format_telefone)
        
        # Endereço
        tk.Label(
            self.form_content,
            text="Endereço",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(10, 2))
        
        self.var_endereco = tk.StringVar()
        self.entry_endereco = tk.Entry(
            self.form_content,
            textvariable=self.var_endereco,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=5
        )
        self.entry_endereco.pack(fill='x', padx=10, pady=(0, 10))
        
        # Cidade
        tk.Label(
            self.form_content,
            text="Cidade",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(0, 2))
        
        self.var_cidade = tk.StringVar()
        self.entry_cidade = tk.Entry(
            self.form_content,
            textvariable=self.var_cidade,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=5
        )
        self.entry_cidade.pack(fill='x', padx=10, pady=(0, 10))
        
        # CEP
        tk.Label(
            self.form_content,
            text="CEP",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(0, 2))
        
        self.var_cep = tk.StringVar()
        self.entry_cep = tk.Entry(
            self.form_content,
            textvariable=self.var_cep,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=5
        )
        self.entry_cep.pack(fill='x', padx=10, pady=(0, 10))
        self.entry_cep.bind('<KeyRelease>', self.format_cep)
        
        # Status
        tk.Label(
            self.form_content,
            text="Status",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(10, 2))
        
        self.var_status = tk.StringVar(value="Ativo")
        status_combo = ttk.Combobox(
            self.form_content,
            textvariable=self.var_status,
            values=["Ativo", "Inativo"],
            state="readonly",
            font=('Arial', 10)
        )
        status_combo.pack(fill='x', padx=10, pady=(0, 10))
        
        # Observações
        tk.Label(
            self.form_content,
            text="Observações",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(10, 2))
        
        self.text_observacoes = tk.Text(
            self.form_content,
            font=('Arial', 9),
            bg='#f8f9fa',
            relief='flat',
            bd=5,
            height=4,
            wrap='word'
        )
        self.text_observacoes.pack(fill='x', padx=10, pady=(0, 20))
    
    def create_form_buttons(self):
        """Criar botões do formulário"""
        
        buttons_frame = tk.Frame(self.form_content, bg='white')
        buttons_frame.pack(fill='x', padx=10, pady=(10, 20))
        
        # Botão Salvar
        self.btn_salvar = tk.Button(
            buttons_frame,
            text="💾 Salvar",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8,
            border=0,
            command=self.salvar_cliente
        )
        self.btn_salvar.pack(side='left', padx=(0, 10))
        
        # Botão Cancelar
        self.btn_cancelar = tk.Button(
            buttons_frame,
            text="❌ Cancelar",
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=8,
            border=0,
            command=self.cancelar_edicao
        )
        self.btn_cancelar.pack(side='left')
        
        # Botão Limpar
        self.btn_limpar = tk.Button(
            buttons_frame,
            text="🧹 Limpar",
            font=('Arial', 10),
            bg='#f39c12',
            fg='white',
            padx=20,
            pady=8,
            border=0,
            command=self.limpar_formulario
        )
        self.btn_limpar.pack(side='right')
    
    # =======================================
    # MÉTODOS DE CONTROLE
    # =======================================
    
    def on_tipo_changed(self):
        """Callback quando tipo de cliente muda"""
        
        if self.var_tipo.get() == "Física":
            self.label_nome.config(text="Nome Completo *")
            self.label_documento.config(text="CPF *")
        else:
            self.label_nome.config(text="Razão Social *")
            self.label_documento.config(text="CNPJ *")
        
        # Limpar documento ao mudar tipo
        self.var_documento.set("")
    
    def formatar_cpf(self, documento: str) -> str:
        """Formatar CPF: 000.000.000-00"""
        if len(documento) <= 11:
            if len(documento) > 3:
                documento = f"{documento[:3]}.{documento[3:]}"
            if len(documento) > 7:
                documento = f"{documento[:7]}.{documento[7:]}"
            if len(documento) > 11:
                documento = f"{documento[:11]}-{documento[11:]}"
        return documento
    
    def formatar_cnpj(self, documento: str) -> str:
        """Formatar CNPJ: 00.000.000/0000-00"""
        if len(documento) <= 14:
            if len(documento) > 2:
                documento = f"{documento[:2]}.{documento[2:]}"
            if len(documento) > 6:
                documento = f"{documento[:6]}.{documento[6:]}"
            if len(documento) > 10:
                documento = f"{documento[:10]}/{documento[10:]}"
            if len(documento) > 15:
                documento = f"{documento[:15]}-{documento[15:]}"
        return documento
    
    def format_documento(self, event=None):
        """Formatar CPF/CNPJ baseado no tipo de pessoa"""
        
        documento = re.sub(r'\D', '', self.var_documento.get())
        
        if self.var_tipo.get() == "Física":
            documento = self.formatar_cpf(documento)
        else:
            documento = self.formatar_cnpj(documento)
        
        self.var_documento.set(documento)
    
    def format_telefone(self, event=None):
        """Formatar telefone"""
        
        telefone = re.sub(r'\D', '', self.var_telefone.get())
        
        if len(telefone) <= 11:
            if len(telefone) > 2:
                telefone = f"({telefone[:2]}) {telefone[2:]}"
            if len(telefone) > 10:
                if len(telefone) == 15:  # (00) 00000-0000
                    telefone = f"{telefone[:10]}-{telefone[10:]}"
                elif len(telefone) == 14:  # (00) 0000-0000
                    telefone = f"{telefone[:9]}-{telefone[9:]}"
        
        self.var_telefone.set(telefone)
    
    def format_cep(self, event=None):
        """Formatar CEP"""
        
        cep = re.sub(r'\D', '', self.var_cep.get())
        
        if len(cep) <= 8:
            if len(cep) > 5:
                cep = f"{cep[:5]}-{cep[5:]}"
        
        self.var_cep.set(cep)
    
    def on_cliente_selecionado(self, event=None):
        """Callback quando cliente é selecionado na lista"""
        
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            cliente_id = item['values'][0]
            
            # Encontrar cliente nos dados
            self.cliente_selecionado = None
            for cliente in self.clientes_data:
                if cliente.get('id') == cliente_id:
                    self.cliente_selecionado = cliente
                    break
            
            # Habilitar botões
            self.btn_editar.config(state='normal')
            self.btn_excluir.config(state='normal')
        else:
            self.cliente_selecionado = None
            self.btn_editar.config(state='disabled')
            self.btn_excluir.config(state='disabled')
    
    def filtrar_clientes(self, event=None):
        """Filtrar clientes na lista"""
        
        termo = self.entry_busca.get().lower()
        
        # Limpar lista
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrar e popular lista
        clientes_filtrados = []
        for cliente in self.clientes_data:
            if (termo in cliente.get('nome', '').lower() or
                termo in cliente.get('email', '').lower() or
                termo in cliente.get('cpf_cnpj', '').lower() or
                termo in cliente.get('telefone', '').lower()):
                clientes_filtrados.append(cliente)
        
        self.popular_lista(clientes_filtrados)
    
    def popular_lista(self, clientes_list=None):
        """Popular lista de clientes"""
        
        if clientes_list is None:
            clientes_list = self.clientes_data
        
        # Limpar lista atual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar clientes
        for cliente in clientes_list:
            self.tree.insert('', 'end', values=(
                cliente.get('id', ''),
                cliente.get('nome', ''),
                cliente.get('tipo_pessoa', ''),
                cliente.get('cpf_cnpj', ''),
                cliente.get('telefone', ''),
                cliente.get('email', ''),
                cliente.get('status', '')
            ))
        
        # Atualizar contador
        total = len(clientes_list)
        self.label_contador.config(text=f"Total: {total} clientes")
    
    # =======================================
    # MÉTODOS DE API
    # =======================================
    
    def carregar_clientes(self):
        """Carregar lista de clientes da API"""
        
        def load_data():
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/clientes",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.clientes_data = response.json()
                    
                    # Atualizar interface na thread principal
                    self.root.after(0, lambda: self.popular_lista())
                    
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao carregar clientes: {response.status_code}"
                    ))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro de conexão: {str(e)}"
                ))
        
        # Executar em thread separada
        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()
    
    def salvar_cliente(self):
        """Salvar cliente (criar ou atualizar)"""
        
        # Validar campos obrigatórios
        if not self.validar_formulario():
            return
        
        # Preparar dados
        dados_cliente = {
            "nome": self.var_nome.get().strip(),
            "tipo_pessoa": self.var_tipo.get(),
            "cpf_cnpj": re.sub(r'\D', '', self.var_documento.get()),
            "email": self.var_email.get().strip(),
            "telefone": re.sub(r'\D', '', self.var_telefone.get()),
            "endereco": self.var_endereco.get().strip(),
            "cidade": self.var_cidade.get().strip(),
            "cep": re.sub(r'\D', '', self.var_cep.get()),
            "status": self.var_status.get(),
            "observacoes": self.text_observacoes.get("1.0", tk.END).strip()
        }
        
        def save_data():
            try:
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                
                cliente_id = self.var_id.get()
                
                if cliente_id:
                    # Atualizar cliente existente
                    response = requests.put(
                        f"{API_BASE_URL}/api/v1/clientes/{cliente_id}",
                        json=dados_cliente,
                        headers=headers,
                        timeout=10
                    )
                else:
                    # Criar novo cliente
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/clientes",
                        json=dados_cliente,
                        headers=headers,
                        timeout=10
                    )
                
                if response.status_code in [200, 201]:
                    self.root.after(0, lambda: [
                        messagebox.showinfo("Sucesso", "Cliente salvo com sucesso!"),
                        self.limpar_formulario(),
                        self.carregar_clientes()
                    ])
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao salvar cliente: {response.status_code}\n{response.text}"
                    ))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro de conexão: {str(e)}"
                ))
        
        # Executar em thread separada
        thread = threading.Thread(target=save_data, daemon=True)
        thread.start()
    
    def validar_formulario(self):
        """Validar campos do formulário"""
        
        # Campos obrigatórios
        if not self.var_nome.get().strip():
            messagebox.showerror("Erro", "Nome é obrigatório!")
            self.entry_nome.focus()
            return False
        
        if not self.var_documento.get().strip():
            messagebox.showerror("Erro", "CPF/CNPJ é obrigatório!")
            self.entry_documento.focus()
            return False
        
        if not self.var_email.get().strip():
            messagebox.showerror("Erro", "Email é obrigatório!")
            self.entry_email.focus()
            return False
        
        if not self.var_telefone.get().strip():
            messagebox.showerror("Erro", "Telefone é obrigatório!")
            self.entry_telefone.focus()
            return False
        
        # Validar email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.var_email.get().strip()):
            messagebox.showerror("Erro", "Email inválido!")
            self.entry_email.focus()
            return False
        
        return True
    
    # =======================================
    # MÉTODOS DE AÇÃO
    # =======================================
    
    def novo_cliente(self):
        """Preparar formulário para novo cliente"""
        
        self.limpar_formulario()
        self.entry_nome.focus()
    
    def editar_cliente(self, event=None):
        """Editar cliente selecionado"""
        
        if not self.cliente_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar!")
            return
        
        # Preencher formulário com dados do cliente
        cliente = self.cliente_selecionado
        
        self.var_id.set(str(cliente.get('id', '')))
        self.var_nome.set(cliente.get('nome', ''))
        self.var_tipo.set(cliente.get('tipo_pessoa', 'Física'))
        self.var_documento.set(cliente.get('cpf_cnpj', ''))
        self.var_email.set(cliente.get('email', ''))
        self.var_telefone.set(cliente.get('telefone', ''))
        self.var_endereco.set(cliente.get('endereco', ''))
        self.var_cidade.set(cliente.get('cidade', ''))
        self.var_cep.set(cliente.get('cep', ''))
        self.var_status.set(cliente.get('status', 'Ativo'))
        
        self.text_observacoes.delete("1.0", tk.END)
        self.text_observacoes.insert("1.0", cliente.get('observacoes', ''))
        
        # Atualizar labels conforme tipo
        self.on_tipo_changed()
        
        # Focar no primeiro campo
        self.entry_nome.focus()
    
    def excluir_cliente(self):
        """Excluir cliente selecionado"""
        
        if not self.cliente_selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir!")
            return
        
        # Confirmar exclusão
        nome = self.cliente_selecionado.get('nome', '')
        resultado = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o cliente:\n\n{nome}\n\nEsta ação não pode ser desfeita!"
        )
        
        if not resultado:
            return
        
        def delete_data():
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                cliente_id = self.cliente_selecionado.get('id')
                
                response = requests.delete(
                    f"{API_BASE_URL}/api/v1/clientes/{cliente_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.root.after(0, lambda: [
                        messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!"),
                        self.limpar_formulario(),
                        self.carregar_clientes()
                    ])
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao excluir cliente: {response.status_code}"
                    ))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro de conexão: {str(e)}"
                ))
        
        # Executar em thread separada
        thread = threading.Thread(target=delete_data, daemon=True)
        thread.start()
    
    def cancelar_edicao(self):
        """Cancelar edição atual"""
        
        self.limpar_formulario()
    
    def limpar_formulario(self):
        """Limpar todos os campos do formulário"""
        
        self.var_id.set("")
        self.var_nome.set("")
        self.var_tipo.set("Física")
        self.var_documento.set("")
        self.var_email.set("")
        self.var_telefone.set("")
        self.var_endereco.set("")
        self.var_cidade.set("")
        self.var_cep.set("")
        self.var_status.set("Ativo")
        
        self.text_observacoes.delete("1.0", tk.END)
        
        # Atualizar labels
        self.on_tipo_changed()
        
        # Desselecionar na lista
        self.tree.selection_remove(self.tree.selection())
        self.cliente_selecionado = None
        
        # Desabilitar botões
        self.btn_editar.config(state='disabled')
        self.btn_excluir.config(state='disabled')
    
    def on_closing(self):
        """Tratar fechamento da janela"""
        
        if messagebox.askyesno("Fechar", "Deseja fechar o gerenciamento de clientes?"):
            self.root.destroy()
    
    def run(self):
        """Executar a interface"""
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            try:
                self.root.destroy()
            except Exception:
                pass

# =======================================
# FUNÇÃO PRINCIPAL
# =======================================

def main():
    """Teste da interface de clientes"""
    
    # Dados de usuário mock para teste
    user_data = {
        "access_token": "mock_token",
        "user": {
            "username": "admin",
            "nome_completo": "Administrador"
        }
    }
    
    app = ClientesWindow(user_data)
    app.run()

if __name__ == "__main__":
    main()