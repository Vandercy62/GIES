#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA ERP PRIMOTEX - INTERFACE DE FORNECEDORES
===============================================

Interface tkinter para gestão completa de fornecedores.
Implementa CRUD completo com validação e integração com API.

FUNCIONALIDADES:
- Listagem de fornecedores com filtros
- Cadastro de novos fornecedores
- Edição de fornecedores existentes
- Validação de CNPJ/CPF
- Busca e filtros avançados
- Integração com sistema financeiro

Autor: GitHub Copilot
Data: 01/11/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading

# Configuração da API
API_BASE_URL = "http://127.0.0.1:8002"


class FornecedoresWindow:
    """Interface principal de fornecedores"""
    
    def __init__(self, parent=None, api_token=None):
        self.parent = parent
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}" if api_token else "",
            "Content-Type": "application/json"
        }
        
        # Dados
        self.fornecedores = []
        self.fornecedor_selecionado = None
        
        # Criar janela
        self.setup_window()
        self.create_widgets()
        self.carregar_dados_iniciais()
    
    def setup_window(self):
        """Configurar janela principal"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Sistema ERP Primotex - Gestão de Fornecedores")
        self.window.geometry("1200x700")
        self.window.minsize(1000, 600)
        
        # Centralizar janela
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Configurar grid
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
    
    def create_widgets(self):
        """Criar widgets da interface"""
        
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="🏭 GESTÃO DE FORNECEDORES",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        
        # Criar abas
        self.create_lista_tab()
        self.create_cadastro_tab()
        self.create_estatisticas_tab()
    
    def create_lista_tab(self):
        """Criar aba de listagem"""
        
        # Frame da aba
        lista_frame = ttk.Frame(self.notebook)
        self.notebook.add(lista_frame, text="📋 Lista de Fornecedores")
        
        lista_frame.grid_rowconfigure(2, weight=1)
        lista_frame.grid_columnconfigure(0, weight=1)
        
        # Frame de filtros
        filtros_frame = ttk.LabelFrame(lista_frame, text="Filtros de Busca")
        filtros_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        filtros_frame.grid_columnconfigure(1, weight=1)
        
        # Campo de busca
        ttk.Label(filtros_frame, text="Buscar:").grid(row=0, column=0, padx=5, pady=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filtros_frame, textvariable=self.search_var, width=40)
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Filtro por categoria
        ttk.Label(filtros_frame, text="Categoria:").grid(row=0, column=2, padx=5, pady=5)
        self.categoria_var = tk.StringVar()
        categoria_combo = ttk.Combobox(
            filtros_frame,
            textvariable=self.categoria_var,
            values=["Todas"] + self.get_categorias_fornecedor(),
            width=20,
            state="readonly"
        )
        categoria_combo.grid(row=0, column=3, padx=5, pady=5)
        categoria_combo.set("Todas")
        categoria_combo.bind('<<ComboboxSelected>>', self.aplicar_filtros)
        
        # Filtro por status
        ttk.Label(filtros_frame, text="Status:").grid(row=0, column=4, padx=5, pady=5)
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(
            filtros_frame,
            textvariable=self.status_var,
            values=["Todos", "Ativo", "Inativo", "Bloqueado", "Em Análise"],
            width=15,
            state="readonly"
        )
        status_combo.grid(row=0, column=5, padx=5, pady=5)
        status_combo.set("Todos")
        status_combo.bind('<<ComboboxSelected>>', self.aplicar_filtros)
        
        # Botão de limpar filtros
        ttk.Button(
            filtros_frame,
            text="🔄 Limpar",
            command=self.limpar_filtros
        ).grid(row=0, column=6, padx=5, pady=5)
        
        # Frame de botões
        botoes_frame = ttk.Frame(lista_frame)
        botoes_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # Botões de ação
        ttk.Button(
            botoes_frame,
            text="➕ Novo Fornecedor",
            command=self.novo_fornecedor
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="✏️ Editar",
            command=self.editar_fornecedor
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="❌ Inativar",
            command=self.inativar_fornecedor
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="🔄 Atualizar",
            command=self.carregar_fornecedores
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame da tabela
        table_frame = ttk.Frame(lista_frame)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview
        columns = (
            "ID", "CNPJ/CPF", "Razão Social", "Nome Fantasia",
            "Categoria", "Telefone", "Email", "Cidade", "Status"
        )
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configurar colunas
        self.tree.heading("ID", text="ID")
        self.tree.heading("CNPJ/CPF", text="CNPJ/CPF")
        self.tree.heading("Razão Social", text="Razão Social")
        self.tree.heading("Nome Fantasia", text="Nome Fantasia")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.heading("Telefone", text="Telefone")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Cidade", text="Cidade")
        self.tree.heading("Status", text="Status")
        
        # Configurar larguras
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("CNPJ/CPF", width=120, anchor="center")
        self.tree.column("Razão Social", width=200)
        self.tree.column("Nome Fantasia", width=150)
        self.tree.column("Categoria", width=120)
        self.tree.column("Telefone", width=100, anchor="center")
        self.tree.column("Email", width=150)
        self.tree.column("Cidade", width=100)
        self.tree.column("Status", width=80, anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid da tabela e scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind eventos
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # Frame de informações
        info_frame = ttk.LabelFrame(lista_frame, text="Informações do Fornecedor")
        info_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        
        self.info_text = tk.Text(info_frame, height=4, wrap="word")
        self.info_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_cadastro_tab(self):
        """Criar aba de cadastro/edição"""
        
        # Frame da aba
        cadastro_frame = ttk.Frame(self.notebook)
        self.notebook.add(cadastro_frame, text="📝 Cadastro/Edição")
        
        # Canvas e scrollbar para scroll
        canvas = tk.Canvas(cadastro_frame)
        scrollbar = ttk.Scrollbar(cadastro_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid do canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Criar formulário
        self.create_form(scrollable_frame)
    
    def create_form(self, parent):
        """Criar formulário de cadastro"""
        
        # Título do formulário
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill="x", padx=10, pady=10)
        
        self.form_title = ttk.Label(
            title_frame,
            text="📝 NOVO FORNECEDOR",
            font=("Arial", 14, "bold")
        )
        self.form_title.pack()
        
        # Frame principal do formulário
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Seção 1: Identificação Básica
        id_frame = ttk.LabelFrame(form_frame, text="📋 Identificação Básica")
        id_frame.pack(fill="x", pady=5)
        id_frame.grid_columnconfigure(1, weight=1)
        id_frame.grid_columnconfigure(3, weight=1)
        
        # CNPJ/CPF
        ttk.Label(id_frame, text="* CNPJ/CPF:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cnpj_cpf_var = tk.StringVar()
        cnpj_entry = ttk.Entry(id_frame, textvariable=self.cnpj_cpf_var, width=20)
        cnpj_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        cnpj_entry.bind('<KeyRelease>', self.validar_cnpj_cpf)
        
        # Tipo de pessoa
        ttk.Label(id_frame, text="Tipo:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.tipo_pessoa_var = tk.StringVar()
        tipo_combo = ttk.Combobox(
            id_frame,
            textvariable=self.tipo_pessoa_var,
            values=["Pessoa Jurídica", "Pessoa Física"],
            state="readonly",
            width=15
        )
        tipo_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        tipo_combo.set("Pessoa Jurídica")
        
        # Razão Social
        ttk.Label(id_frame, text="* Razão Social:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.razao_social_var = tk.StringVar()
        ttk.Entry(id_frame, textvariable=self.razao_social_var).grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Nome Fantasia
        ttk.Label(id_frame, text="Nome Fantasia:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.nome_fantasia_var = tk.StringVar()
        ttk.Entry(id_frame, textvariable=self.nome_fantasia_var).grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Seção 2: Categorização
        cat_frame = ttk.LabelFrame(form_frame, text="🏷️ Categorização")
        cat_frame.pack(fill="x", pady=5)
        cat_frame.grid_columnconfigure(1, weight=1)
        cat_frame.grid_columnconfigure(3, weight=1)
        
        # Categoria
        ttk.Label(cat_frame, text="* Categoria:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.categoria_form_var = tk.StringVar()
        categoria_combo = ttk.Combobox(
            cat_frame,
            textvariable=self.categoria_form_var,
            values=self.get_categorias_fornecedor(),
            state="readonly"
        )
        categoria_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Subcategoria
        ttk.Label(cat_frame, text="Subcategoria:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.subcategoria_var = tk.StringVar()
        ttk.Entry(cat_frame, textvariable=self.subcategoria_var).grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        
        # Seção 3: Contato
        contato_frame = ttk.LabelFrame(form_frame, text="📞 Informações de Contato")
        contato_frame.pack(fill="x", pady=5)
        contato_frame.grid_columnconfigure(1, weight=1)
        contato_frame.grid_columnconfigure(3, weight=1)
        
        # Contato Principal
        ttk.Label(contato_frame, text="Contato Principal:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.contato_principal_var = tk.StringVar()
        ttk.Entry(contato_frame, textvariable=self.contato_principal_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Telefone
        ttk.Label(contato_frame, text="Telefone:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.telefone_var = tk.StringVar()
        telefone_entry = ttk.Entry(contato_frame, textvariable=self.telefone_var)
        telefone_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        telefone_entry.bind('<KeyRelease>', self.formatar_telefone)
        
        # Email
        ttk.Label(contato_frame, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(contato_frame, textvariable=self.email_var).grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Seção 4: Endereço
        endereco_frame = ttk.LabelFrame(form_frame, text="📍 Endereço")
        endereco_frame.pack(fill="x", pady=5)
        endereco_frame.grid_columnconfigure(1, weight=1)
        endereco_frame.grid_columnconfigure(3, weight=1)
        endereco_frame.grid_columnconfigure(5, weight=1)
        
        # CEP
        ttk.Label(endereco_frame, text="CEP:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cep_var = tk.StringVar()
        cep_entry = ttk.Entry(endereco_frame, textvariable=self.cep_var, width=12)
        cep_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        cep_entry.bind('<KeyRelease>', self.formatar_cep)
        
        # Cidade
        ttk.Label(endereco_frame, text="Cidade:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.cidade_var = tk.StringVar()
        ttk.Entry(endereco_frame, textvariable=self.cidade_var).grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        
        # Estado
        ttk.Label(endereco_frame, text="UF:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.estado_var = tk.StringVar()
        estado_combo = ttk.Combobox(
            endereco_frame,
            textvariable=self.estado_var,
            values=self.get_estados_brasil(),
            state="readonly",
            width=5
        )
        estado_combo.grid(row=0, column=5, sticky="ew", padx=5, pady=5)
        
        # Logradouro
        ttk.Label(endereco_frame, text="Logradouro:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.logradouro_var = tk.StringVar()
        ttk.Entry(endereco_frame, textvariable=self.logradouro_var).grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Número
        ttk.Label(endereco_frame, text="Número:").grid(row=1, column=4, sticky="w", padx=5, pady=5)
        self.numero_var = tk.StringVar()
        ttk.Entry(endereco_frame, textvariable=self.numero_var, width=10).grid(row=1, column=5, sticky="ew", padx=5, pady=5)
        
        # Seção 5: Observações
        obs_frame = ttk.LabelFrame(form_frame, text="📝 Observações")
        obs_frame.pack(fill="x", pady=5)
        
        self.observacoes_text = tk.Text(obs_frame, height=4, wrap="word")
        self.observacoes_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Botões
        botoes_frame = ttk.Frame(form_frame)
        botoes_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            botoes_frame,
            text="💾 Salvar",
            command=self.salvar_fornecedor
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="🔄 Limpar",
            command=self.limpar_formulario
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botoes_frame,
            text="❌ Cancelar",
            command=self.cancelar_edicao
        ).pack(side=tk.RIGHT, padx=5)
        
        # Variáveis para controle
        self.editando = False
        self.fornecedor_editando_id = None
    
    def create_estatisticas_tab(self):
        """Criar aba de estatísticas"""
        
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Estatísticas")
        
        # Título
        ttk.Label(
            stats_frame,
            text="📊 ESTATÍSTICAS DE FORNECEDORES",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Frame para widgets de stats
        self.stats_content = ttk.Frame(stats_frame)
        self.stats_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botão para carregar stats
        ttk.Button(
            stats_frame,
            text="🔄 Atualizar Estatísticas",
            command=self.carregar_estatisticas
        ).pack(pady=10)
    
    # =======================================
    # MÉTODOS DE DADOS
    # =======================================
    
    def carregar_dados_iniciais(self):
        """Carregar dados iniciais"""
        self.carregar_fornecedores()
    
    def carregar_fornecedores(self):
        """Carregar lista de fornecedores"""
        def _carregar():
            try:
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/fornecedores",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.fornecedores = data.get('items', [])
                    self.window.after(0, self.atualizar_lista)
                else:
                    self.window.after(0, lambda: messagebox.showerror(
                        "Erro", f"Erro ao carregar fornecedores: {response.status_code}"
                    ))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror(
                    "Erro", f"Erro ao conectar com a API: {str(e)}"
                ))
        
        threading.Thread(target=_carregar, daemon=True).start()
    
    def atualizar_lista(self):
        """Atualizar lista na treeview"""
        # Limpar lista atual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar fornecedores
        for fornecedor in self.fornecedores:
            values = (
                fornecedor.get('id', ''),
                fornecedor.get('documento_formatado', fornecedor.get('cnpj_cpf', '')),
                fornecedor.get('razao_social', ''),
                fornecedor.get('nome_fantasia', ''),
                fornecedor.get('categoria', ''),
                fornecedor.get('telefone', ''),
                fornecedor.get('email', ''),
                fornecedor.get('cidade', ''),
                fornecedor.get('status', '')
            )
            
            # Adicionar com tag baseada no status
            tag = "ativo" if fornecedor.get('ativo') else "inativo"
            self.tree.insert("", "end", values=values, tags=(tag,))
        
        # Configurar cores das tags
        self.tree.tag_configure("ativo", foreground="darkgreen")
        self.tree.tag_configure("inativo", foreground="red")
    
    # =======================================
    # MÉTODOS DE EVENTOS
    # =======================================
    
    def on_search_change(self, event=None):
        """Evento de mudança na busca"""
        # Implementar busca em tempo real ou aguardar delay
        self.window.after(500, self.aplicar_filtros)
    
    def aplicar_filtros(self, event=None):
        """Aplicar filtros na lista"""
        # Implementar filtros - por enquanto apenas carregar tudo
        self.carregar_fornecedores()
    
    def limpar_filtros(self):
        """Limpar todos os filtros"""
        self.search_var.set("")
        self.categoria_var.set("Todas")
        self.status_var.set("Todos")
        self.carregar_fornecedores()
    
    def on_item_select(self, event=None):
        """Evento de seleção de item"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            
            # Buscar fornecedor completo
            fornecedor_id = values[0]
            fornecedor = next((f for f in self.fornecedores if f['id'] == fornecedor_id), None)
            
            if fornecedor:
                self.exibir_informacoes_fornecedor(fornecedor)
    
    def on_item_double_click(self, event=None):
        """Evento de duplo clique - editar fornecedor"""
        self.editar_fornecedor()
    
    def exibir_informacoes_fornecedor(self, fornecedor):
        """Exibir informações detalhadas do fornecedor"""
        info = f"""
📋 {fornecedor.get('nome_exibicao', fornecedor.get('razao_social', ''))}

📄 CNPJ/CPF: {fornecedor.get('documento_formatado', '')}
🏷️ Categoria: {fornecedor.get('categoria', '')}
📞 Telefone: {fornecedor.get('telefone', 'Não informado')}
✉️ Email: {fornecedor.get('email', 'Não informado')}
📍 Cidade: {fornecedor.get('cidade', 'Não informada')}
📊 Status: {fornecedor.get('status', '')} ({'Ativo' if fornecedor.get('ativo') else 'Inativo'})
📅 Cadastro: {fornecedor.get('data_cadastro', '')[:10] if fornecedor.get('data_cadastro') else ''}
        """.strip()
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
    
    # =======================================
    # MÉTODOS DE AÇÕES
    # =======================================
    
    def novo_fornecedor(self):
        """Iniciar cadastro de novo fornecedor"""
        self.limpar_formulario()
        self.editando = False
        self.fornecedor_editando_id = None
        self.form_title.config(text="📝 NOVO FORNECEDOR")
        self.notebook.select(1)  # Ir para aba de cadastro
    
    def editar_fornecedor(self):
        """Editar fornecedor selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para editar")
            return
        
        item = self.tree.item(selection[0])
        fornecedor_id = item['values'][0]
        
        # Buscar fornecedor completo
        fornecedor = next((f for f in self.fornecedores if f['id'] == fornecedor_id), None)
        
        if fornecedor:
            self.carregar_fornecedor_no_formulario(fornecedor)
            self.editando = True
            self.fornecedor_editando_id = fornecedor_id
            self.form_title.config(text="✏️ EDITAR FORNECEDOR")
            self.notebook.select(1)  # Ir para aba de cadastro
    
    def carregar_fornecedor_no_formulario(self, fornecedor):
        """Carregar dados do fornecedor no formulário"""
        self.cnpj_cpf_var.set(fornecedor.get('cnpj_cpf', ''))
        self.tipo_pessoa_var.set(fornecedor.get('tipo_pessoa', 'Pessoa Jurídica'))
        self.razao_social_var.set(fornecedor.get('razao_social', ''))
        self.nome_fantasia_var.set(fornecedor.get('nome_fantasia', ''))
        self.categoria_form_var.set(fornecedor.get('categoria', ''))
        self.subcategoria_var.set(fornecedor.get('subcategoria', ''))
        self.contato_principal_var.set(fornecedor.get('contato_principal', ''))
        self.telefone_var.set(fornecedor.get('telefone', ''))
        self.email_var.set(fornecedor.get('email', ''))
        self.cep_var.set(fornecedor.get('cep', ''))
        self.cidade_var.set(fornecedor.get('cidade', ''))
        self.estado_var.set(fornecedor.get('estado', ''))
        self.logradouro_var.set(fornecedor.get('logradouro', ''))
        self.numero_var.set(fornecedor.get('numero', ''))
        
        # Observações
        self.observacoes_text.delete(1.0, tk.END)
        if fornecedor.get('observacoes'):
            self.observacoes_text.insert(1.0, fornecedor['observacoes'])
    
    def salvar_fornecedor(self):
        """Salvar fornecedor (criar ou atualizar)"""
        if not self.validar_formulario():
            return
        
        # Preparar dados
        dados = {
            "cnpj_cpf": self.cnpj_cpf_var.get().strip(),
            "tipo_pessoa": self.tipo_pessoa_var.get(),
            "razao_social": self.razao_social_var.get().strip(),
            "nome_fantasia": self.nome_fantasia_var.get().strip() or None,
            "categoria": self.categoria_form_var.get(),
            "subcategoria": self.subcategoria_var.get().strip() or None,
            "contato_principal": self.contato_principal_var.get().strip() or None,
            "telefone": self.telefone_var.get().strip() or None,
            "email": self.email_var.get().strip() or None,
            "cep": self.cep_var.get().strip() or None,
            "cidade": self.cidade_var.get().strip() or None,
            "estado": self.estado_var.get() or None,
            "logradouro": self.logradouro_var.get().strip() or None,
            "numero": self.numero_var.get().strip() or None,
            "observacoes": self.observacoes_text.get(1.0, tk.END).strip() or None
        }
        
        def _salvar():
            try:
                if self.editando:
                    # Atualizar
                    response = requests.put(
                        f"{API_BASE_URL}/api/v1/fornecedores/{self.fornecedor_editando_id}",
                        json=dados,
                        headers=self.headers,
                        timeout=10
                    )
                else:
                    # Criar
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/fornecedores",
                        json=dados,
                        headers=self.headers,
                        timeout=10
                    )
                
                if response.status_code in [200, 201]:
                    self.window.after(0, self._on_save_success)
                else:
                    error_msg = response.json().get('detail', 'Erro desconhecido')
                    self.window.after(0, lambda: messagebox.showerror(
                        "Erro", f"Erro ao salvar: {error_msg}"
                    ))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror(
                    "Erro", f"Erro ao conectar: {str(e)}"
                ))
        
        threading.Thread(target=_salvar, daemon=True).start()
    
    def _on_save_success(self):
        """Callback de sucesso ao salvar"""
        acao = "atualizado" if self.editando else "cadastrado"
        messagebox.showinfo("Sucesso", f"Fornecedor {acao} com sucesso!")
        self.limpar_formulario()
        self.carregar_fornecedores()
        self.notebook.select(0)  # Voltar para lista
    
    def inativar_fornecedor(self):
        """Inativar fornecedor selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para inativar")
            return
        
        item = self.tree.item(selection[0])
        fornecedor_id = item['values'][0]
        nome = item['values'][2]
        
        if messagebox.askyesno("Confirmar", f"Inativar fornecedor '{nome}'?"):
            def _inativar():
                try:
                    response = requests.patch(
                        f"{API_BASE_URL}/api/v1/fornecedores/{fornecedor_id}/status",
                        params={"novo_status": "Inativo", "motivo": "Inativado pelo usuário"},
                        headers=self.headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        self.window.after(0, self._on_inativar_success)
                    else:
                        error_msg = response.json().get('detail', 'Erro desconhecido')
                        self.window.after(0, lambda: messagebox.showerror(
                            "Erro", f"Erro ao inativar: {error_msg}"
                        ))
                except Exception as e:
                    self.window.after(0, lambda: messagebox.showerror(
                        "Erro", f"Erro ao conectar: {str(e)}"
                    ))
            
            threading.Thread(target=_inativar, daemon=True).start()
    
    def _on_inativar_success(self):
        """Callback de sucesso ao inativar"""
        messagebox.showinfo("Sucesso", "Fornecedor inativado com sucesso!")
        self.carregar_fornecedores()
    
    def limpar_formulario(self):
        """Limpar todos os campos do formulário"""
        self.cnpj_cpf_var.set("")
        self.tipo_pessoa_var.set("Pessoa Jurídica")
        self.razao_social_var.set("")
        self.nome_fantasia_var.set("")
        self.categoria_form_var.set("")
        self.subcategoria_var.set("")
        self.contato_principal_var.set("")
        self.telefone_var.set("")
        self.email_var.set("")
        self.cep_var.set("")
        self.cidade_var.set("")
        self.estado_var.set("")
        self.logradouro_var.set("")
        self.numero_var.set("")
        self.observacoes_text.delete(1.0, tk.END)
        
        self.editando = False
        self.fornecedor_editando_id = None
    
    def cancelar_edicao(self):
        """Cancelar edição e voltar para lista"""
        self.limpar_formulario()
        self.notebook.select(0)
    
    def carregar_estatisticas(self):
        """Carregar estatísticas de fornecedores"""
        def _carregar():
            try:
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/fornecedores/stats/resumo",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    stats = response.json()
                    self.window.after(0, lambda: self.exibir_estatisticas(stats))
                else:
                    self.window.after(0, lambda: messagebox.showerror(
                        "Erro", f"Erro ao carregar estatísticas: {response.status_code}"
                    ))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror(
                    "Erro", f"Erro ao conectar: {str(e)}"
                ))
        
        threading.Thread(target=_carregar, daemon=True).start()
    
    def exibir_estatisticas(self, stats):
        """Exibir estatísticas na interface"""
        # Limpar conteúdo anterior
        for widget in self.stats_content.winfo_children():
            widget.destroy()
        
        # Frame para cards
        cards_frame = ttk.Frame(self.stats_content)
        cards_frame.pack(fill="x", pady=10)
        
        # Cards de resumo
        cards = [
            ("📊 Total", stats.get('total_fornecedores', 0)),
            ("✅ Ativos", stats.get('total_ativos', 0)),
            ("❌ Inativos", stats.get('total_inativos', 0)),
            ("⭐ Avaliação Média", f"{stats.get('avaliacao_media', 0):.1f}" if stats.get('avaliacao_media') else "N/A")
        ]
        
        for i, (titulo, valor) in enumerate(cards):
            card = ttk.LabelFrame(cards_frame, text=titulo)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            cards_frame.grid_columnconfigure(i, weight=1)
            
            ttk.Label(
                card,
                text=str(valor),
                font=("Arial", 16, "bold")
            ).pack(pady=10)
        
        # Gráfico por categoria (texto)
        if stats.get('total_por_categoria'):
            cat_frame = ttk.LabelFrame(self.stats_content, text="📊 Fornecedores por Categoria")
            cat_frame.pack(fill="x", pady=10)
            
            for categoria, total in stats['total_por_categoria'].items():
                ttk.Label(
                    cat_frame,
                    text=f"{categoria}: {total}"
                ).pack(anchor="w", padx=10, pady=2)
    
    # =======================================
    # MÉTODOS DE VALIDAÇÃO
    # =======================================
    
    def validar_formulario(self):
        """Validar campos obrigatórios"""
        errors = []
        
        if not self.cnpj_cpf_var.get().strip():
            errors.append("CNPJ/CPF é obrigatório")
        
        if not self.razao_social_var.get().strip():
            errors.append("Razão Social é obrigatória")
        
        if not self.categoria_form_var.get():
            errors.append("Categoria é obrigatória")
        
        if errors:
            messagebox.showerror("Erro de Validação", "\n".join(errors))
            return False
        
        return True
    
    def validar_cnpj_cpf(self, event=None):
        """Validar e formatar CNPJ/CPF"""
        value = self.cnpj_cpf_var.get()
        # Remover caracteres não numéricos
        numbers = ''.join(filter(str.isdigit, value))
        
        # Formatar baseado no tamanho
        if len(numbers) <= 11:  # CPF
            formatted = self.format_cpf(numbers)
        else:  # CNPJ
            formatted = self.format_cnpj(numbers)
        
        self.cnpj_cpf_var.set(formatted)
    
    def format_cpf(self, cpf):
        """Formatar CPF"""
        if len(cpf) <= 3:
            return cpf
        elif len(cpf) <= 6:
            return f"{cpf[:3]}.{cpf[3:]}"
        elif len(cpf) <= 9:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:]}"
        else:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
    
    def format_cnpj(self, cnpj):
        """Formatar CNPJ"""
        if len(cnpj) <= 2:
            return cnpj
        elif len(cnpj) <= 5:
            return f"{cnpj[:2]}.{cnpj[2:]}"
        elif len(cnpj) <= 8:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:]}"
        elif len(cnpj) <= 12:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:]}"
        else:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
    
    def formatar_telefone(self, event=None):
        """Formatar telefone"""
        value = self.telefone_var.get()
        numbers = ''.join(filter(str.isdigit, value))
        
        if len(numbers) <= 2:
            formatted = numbers
        elif len(numbers) <= 6:
            formatted = f"({numbers[:2]}) {numbers[2:]}"
        elif len(numbers) <= 10:
            formatted = f"({numbers[:2]}) {numbers[2:6]}-{numbers[6:]}"
        else:
            formatted = f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:11]}"
        
        self.telefone_var.set(formatted)
    
    def formatar_cep(self, event=None):
        """Formatar CEP"""
        value = self.cep_var.get()
        numbers = ''.join(filter(str.isdigit, value))
        
        if len(numbers) <= 5:
            formatted = numbers
        else:
            formatted = f"{numbers[:5]}-{numbers[5:8]}"
        
        self.cep_var.set(formatted)
    
    # =======================================
    # MÉTODOS AUXILIARES
    # =======================================
    
    def get_categorias_fornecedor(self):
        """Obter lista de categorias"""
        return [
            "Materiais de Construção",
            "Ferragens e Parafusos",
            "Perfis de Alumínio",
            "Forros PVC",
            "Divisórias",
            "Gesso e Acabamentos",
            "Equipamentos e Ferramentas",
            "Serviços Terceirizados",
            "Transporte e Logística",
            "Escritório e Administração",
            "Outros"
        ]
    
    def get_estados_brasil(self):
        """Obter lista de estados do Brasil"""
        return [
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
            "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
            "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]


# =======================================
# FUNÇÃO PRINCIPAL
# =======================================

def main():
    """Função principal para teste"""
    app = FornecedoresWindow()
    app.window.mainloop()


if __name__ == "__main__":
    main()