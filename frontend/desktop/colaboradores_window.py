#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA ERP PRIMOTEX - INTERFACE DE COLABORADORES
=================================================

Interface tkinter para gestão completa de colaboradores/funcionários.
Implementa CRUD completo com validação e integração com API.

FUNCIONALIDADES:
- Listagem de colaboradores com filtros
- Cadastro de novos colaboradores
- Edição de colaboradores existentes
- Validação de CPF e documentos
- Gestão de cargos e departamentos
- Controle de salários e benefícios
- Histórico profissional

Autor: GitHub Copilot
Data: 01/11/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import re
from datetime import datetime, date

# Configuração da API
API_BASE_URL = "http://127.0.0.1:8002"


class ColaboradoresWindow:
    """Interface principal de colaboradores"""

    def __init__(self, parent=None, api_token=None):
        self.parent = parent
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}" if api_token else "",
            "Content-Type": "application/json"
        }

        # Dados
        self.colaboradores = []
        self.departamentos = []
        self.cargos = []
        self.colaborador_selecionado = None

        # Criar janela
        self.setup_window()
        self.create_widgets()
        self.carregar_dados_iniciais()

    def setup_window(self):
        """Configurar janela principal"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Sistema ERP Primotex - Gestão de Colaboradores")
        self.window.geometry("1400x800")
        self.window.minsize(1200, 700)

        # Centralizar janela
        if self.parent:
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
            text="👥 GESTÃO DE COLABORADORES",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")

        # Criar abas
        self.create_lista_tab()
        self.create_cadastro_tab()
        self.create_departamentos_tab()
        self.create_cargos_tab()
        self.create_estatisticas_tab()

    def create_lista_tab(self):
        """Criar aba de listagem"""

        # Frame da aba
        lista_frame = ttk.Frame(self.notebook)
        self.notebook.add(lista_frame, text="📋 Lista de Colaboradores")

        lista_frame.grid_rowconfigure(2, weight=1)
        lista_frame.grid_columnconfigure(0, weight=1)

        # Frame de filtros
        filtros_frame = ttk.LabelFrame(lista_frame, text="🔍 Filtros de Busca")
        filtros_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        filtros_frame.grid_columnconfigure(1, weight=1)

        # Filtro de busca
        ttk.Label(filtros_frame, text="Buscar:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.busca_var = tk.StringVar()
        busca_entry = ttk.Entry(filtros_frame, textvariable=self.busca_var, width=40)
        busca_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        busca_entry.bind('<KeyRelease>', self.filtrar_colaboradores)

        # Filtro por departamento
        ttk.Label(filtros_frame, text="Departamento:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.departamento_var = tk.StringVar()
        self.departamento_combo = ttk.Combobox(filtros_frame, textvariable=self.departamento_var, width=20)
        self.departamento_combo.grid(row=0, column=3, padx=5, pady=5)
        self.departamento_combo.bind('<<ComboboxSelected>>', self.filtrar_colaboradores)

        # Filtro por status
        ttk.Label(filtros_frame, text="Status:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(filtros_frame, textvariable=self.status_var, width=15)
        status_combo['values'] = ("Todos", "ATIVO", "INATIVO", "LICENCA", "FERIAS")
        status_combo.current(0)
        status_combo.grid(row=0, column=5, padx=5, pady=5)
        status_combo.bind('<<ComboboxSelected>>', self.filtrar_colaboradores)

        # Botões de ação
        botoes_frame = ttk.Frame(lista_frame)
        botoes_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        ttk.Button(
            botoes_frame,
            text="➕ Novo Colaborador",
            command=self.ir_para_cadastro
        ).pack(side="left", padx=5)

        ttk.Button(
            botoes_frame,
            text="✏️ Editar",
            command=self.editar_colaborador
        ).pack(side="left", padx=5)

        ttk.Button(
            botoes_frame,
            text="🔄 Atualizar",
            command=self.carregar_colaboradores
        ).pack(side="left", padx=5)

        ttk.Button(
            botoes_frame,
            text="📊 Relatório",
            command=self.gerar_relatorio
        ).pack(side="right", padx=5)

        # Treeview para lista
        self.create_treeview(lista_frame)

    def create_treeview(self, parent):
        """Criar treeview para listagem"""

        # Frame do treeview
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Colunas do treeview
        columns = (
            "matricula", "nome", "cp", "departamento", 
            "cargo", "admissao", "salario", "status"
        )

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        # Configurar cabeçalhos
        headers = {
            "matricula": ("Matrícula", 80),
            "nome": ("Nome Completo", 200),
            "cp": ("CPF", 120),
            "departamento": ("Departamento", 150),
            "cargo": ("Cargo", 150),
            "admissao": ("Admissão", 100),
            "salario": ("Salário", 100),
            "status": ("Status", 80)
        }

        for col, (text, width) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, minwidth=50)

        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Grid do treeview e scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        # Eventos
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)

    def create_cadastro_tab(self):
        """Criar aba de cadastro/edição"""

        # Frame da aba
        cadastro_frame = ttk.Frame(self.notebook)
        self.notebook.add(cadastro_frame, text="📝 Cadastro/Edição")

        # Criar scrollable frame
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
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        cadastro_frame.grid_rowconfigure(0, weight=1)
        cadastro_frame.grid_columnconfigure(0, weight=1)

        # Criar formulário
        self.create_form(scrollable_frame)

    def create_form(self, parent):
        """Criar formulário de cadastro"""

        # Variáveis do formulário
        self.form_vars = {}

        # Seção: Dados Pessoais
        pessoais_frame = ttk.LabelFrame(parent, text="👤 Dados Pessoais")
        pessoais_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        pessoais_frame.grid_columnconfigure(1, weight=1)
        pessoais_frame.grid_columnconfigure(3, weight=1)

        # Nome completo
        ttk.Label(pessoais_frame, text="Nome Completo:*").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.form_vars['nome_completo'] = tk.StringVar()
        ttk.Entry(pessoais_frame, textvariable=self.form_vars['nome_completo'], width=40).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew"
        )

        # CPF
        ttk.Label(pessoais_frame, text="CPF:*").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.form_vars['cp'] = tk.StringVar()
        cpf_entry = ttk.Entry(pessoais_frame, textvariable=self.form_vars['cp'], width=20)
        cpf_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        cpf_entry.bind('<KeyRelease>', self.formatar_cpf)

        # RG
        ttk.Label(pessoais_frame, text="RG:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.form_vars['rg'] = tk.StringVar()
        ttk.Entry(pessoais_frame, textvariable=self.form_vars['rg'], width=20).grid(
            row=1, column=1, padx=5, pady=5, sticky="w"
        )

        # Data de nascimento
        ttk.Label(pessoais_frame, text="Data Nascimento:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.form_vars['data_nascimento'] = tk.StringVar()
        ttk.Entry(pessoais_frame, textvariable=self.form_vars['data_nascimento'], width=15).grid(
            row=1, column=3, padx=5, pady=5, sticky="w"
        )

        # Estado civil
        ttk.Label(pessoais_frame, text="Estado Civil:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.form_vars['estado_civil'] = tk.StringVar()
        estado_combo = ttk.Combobox(pessoais_frame, textvariable=self.form_vars['estado_civil'], width=15)
        estado_combo['values'] = ("Solteiro", "Casado", "Divorciado", "Viúvo", "União Estável")
        estado_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Seção: Contato
        contato_frame = ttk.LabelFrame(parent, text="📞 Contato")
        contato_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        contato_frame.grid_columnconfigure(1, weight=1)
        contato_frame.grid_columnconfigure(3, weight=1)

        # Email pessoal
        ttk.Label(contato_frame, text="Email Pessoal:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.form_vars['email_pessoal'] = tk.StringVar()
        ttk.Entry(contato_frame, textvariable=self.form_vars['email_pessoal'], width=30).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew"
        )

        # Telefone
        ttk.Label(contato_frame, text="Telefone:*").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.form_vars['telefone'] = tk.StringVar()
        telefone_entry = ttk.Entry(contato_frame, textvariable=self.form_vars['telefone'], width=20)
        telefone_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        telefone_entry.bind('<KeyRelease>', self.formatar_telefone)

        # Seção: Dados Profissionais
        profissional_frame = ttk.LabelFrame(parent, text="💼 Dados Profissionais")
        profissional_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        profissional_frame.grid_columnconfigure(1, weight=1)
        profissional_frame.grid_columnconfigure(3, weight=1)

        # Matrícula
        ttk.Label(profissional_frame, text="Matrícula:*").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.form_vars['matricula'] = tk.StringVar()
        ttk.Entry(profissional_frame, textvariable=self.form_vars['matricula'], width=15).grid(
            row=0, column=1, padx=5, pady=5, sticky="w"
        )

        # Data de admissão
        ttk.Label(profissional_frame, text="Data Admissão:*").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.form_vars['data_admissao'] = tk.StringVar()
        ttk.Entry(profissional_frame, textvariable=self.form_vars['data_admissao'], width=15).grid(
            row=0, column=3, padx=5, pady=5, sticky="w"
        )

        # Departamento
        ttk.Label(profissional_frame, text="Departamento:*").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.form_vars['departamento_id'] = tk.StringVar()
        self.departamento_combo_form = ttk.Combobox(profissional_frame, textvariable=self.form_vars['departamento_id'], width=25)
        self.departamento_combo_form.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Cargo
        ttk.Label(profissional_frame, text="Cargo:*").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.form_vars['cargo_id'] = tk.StringVar()
        self.cargo_combo_form = ttk.Combobox(profissional_frame, textvariable=self.form_vars['cargo_id'], width=25)
        self.cargo_combo_form.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # Tipo de contrato
        ttk.Label(profissional_frame, text="Tipo Contrato:*").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.form_vars['tipo_contrato'] = tk.StringVar()
        contrato_combo = ttk.Combobox(profissional_frame, textvariable=self.form_vars['tipo_contrato'], width=20)
        contrato_combo['values'] = ("CLT", "Pessoa Jurídica", "Estagiário", "Temporário")
        contrato_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Salário
        ttk.Label(profissional_frame, text="Salário:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.form_vars['salario'] = tk.StringVar()
        ttk.Entry(profissional_frame, textvariable=self.form_vars['salario'], width=15).grid(
            row=2, column=3, padx=5, pady=5, sticky="w"
        )

        # Seção: Endereço
        endereco_frame = ttk.LabelFrame(parent, text="🏠 Endereço")
        endereco_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        endereco_frame.grid_columnconfigure(1, weight=1)
        endereco_frame.grid_columnconfigure(3, weight=1)

        # CEP
        ttk.Label(endereco_frame, text="CEP:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.form_vars['cep'] = tk.StringVar()
        cep_entry = ttk.Entry(endereco_frame, textvariable=self.form_vars['cep'], width=15)
        cep_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        cep_entry.bind('<KeyRelease>', self.formatar_cep)

        # Logradouro
        ttk.Label(endereco_frame, text="Logradouro:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.form_vars['logradouro'] = tk.StringVar()
        ttk.Entry(endereco_frame, textvariable=self.form_vars['logradouro'], width=40).grid(
            row=0, column=3, padx=5, pady=5, sticky="ew"
        )

        # Número e complemento
        ttk.Label(endereco_frame, text="Número:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.form_vars['numero'] = tk.StringVar()
        ttk.Entry(endereco_frame, textvariable=self.form_vars['numero'], width=10).grid(
            row=1, column=1, padx=5, pady=5, sticky="w"
        )

        ttk.Label(endereco_frame, text="Complemento:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.form_vars['complemento'] = tk.StringVar()
        ttk.Entry(endereco_frame, textvariable=self.form_vars['complemento'], width=30).grid(
            row=1, column=3, padx=5, pady=5, sticky="ew"
        )

        # Bairro e cidade
        ttk.Label(endereco_frame, text="Bairro:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.form_vars['bairro'] = tk.StringVar()
        ttk.Entry(endereco_frame, textvariable=self.form_vars['bairro'], width=25).grid(
            row=2, column=1, padx=5, pady=5, sticky="ew"
        )

        ttk.Label(endereco_frame, text="Cidade:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.form_vars['cidade'] = tk.StringVar()
        ttk.Entry(endereco_frame, textvariable=self.form_vars['cidade'], width=25).grid(
            row=2, column=3, padx=5, pady=5, sticky="ew"
        )

        # UF
        ttk.Label(endereco_frame, text="UF:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.form_vars['u'] = tk.StringVar()
        uf_combo = ttk.Combobox(endereco_frame, textvariable=self.form_vars['u'], width=5)
        uf_combo['values'] = ("SP", "RJ", "MG", "RS", "PR", "SC", "BA", "GO", "PE", "CE")  # Lista simplificada
        uf_combo.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Botões de ação
        botoes_frame = ttk.Frame(parent)
        botoes_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=20)

        ttk.Button(
            botoes_frame,
            text="💾 Salvar",
            command=self.salvar_colaborador
        ).pack(side="left", padx=5)

        ttk.Button(
            botoes_frame,
            text="🔄 Limpar",
            command=self.limpar_formulario
        ).pack(side="left", padx=5)

        ttk.Button(
            botoes_frame,
            text="❌ Cancelar",
            command=self.cancelar_edicao
        ).pack(side="left", padx=5)

    def create_departamentos_tab(self):
        """Criar aba de departamentos"""

        dept_frame = ttk.Frame(self.notebook)
        self.notebook.add(dept_frame, text="🏢 Departamentos")

        # Título
        ttk.Label(dept_frame, text="Gestão de Departamentos", font=("Arial", 14, "bold")).pack(pady=10)

        # Frame de cadastro
        cadastro_dept_frame = ttk.LabelFrame(dept_frame, text="Novo Departamento")
        cadastro_dept_frame.pack(fill="x", padx=10, pady=5)

        # Campos do departamento
        campos_frame = ttk.Frame(cadastro_dept_frame)
        campos_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(campos_frame, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.dept_nome_var = tk.StringVar()
        ttk.Entry(campos_frame, textvariable=self.dept_nome_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(campos_frame, text="Descrição:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.dept_descricao_var = tk.StringVar()
        ttk.Entry(campos_frame, textvariable=self.dept_descricao_var, width=40).grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(campos_frame, text="Salvar Departamento", command=self.salvar_departamento).grid(
            row=0, column=4, padx=10, pady=5
        )

        # Lista de departamentos
        lista_dept_frame = ttk.LabelFrame(dept_frame, text="Departamentos Cadastrados")
        lista_dept_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Treeview departamentos
        dept_columns = ("id", "nome", "descricao", "colaboradores")
        self.dept_tree = ttk.Treeview(lista_dept_frame, columns=dept_columns, show="headings", height=10)

        self.dept_tree.heading("id", text="ID")
        self.dept_tree.heading("nome", text="Nome")
        self.dept_tree.heading("descricao", text="Descrição")
        self.dept_tree.heading("colaboradores", text="Colaboradores")

        self.dept_tree.column("id", width=50)
        self.dept_tree.column("nome", width=200)
        self.dept_tree.column("descricao", width=300)
        self.dept_tree.column("colaboradores", width=100)

        self.dept_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def create_cargos_tab(self):
        """Criar aba de cargos"""

        cargo_frame = ttk.Frame(self.notebook)
        self.notebook.add(cargo_frame, text="💼 Cargos")

        # Título
        ttk.Label(cargo_frame, text="Gestão de Cargos", font=("Arial", 14, "bold")).pack(pady=10)

        # Frame de cadastro
        cadastro_cargo_frame = ttk.LabelFrame(cargo_frame, text="Novo Cargo")
        cadastro_cargo_frame.pack(fill="x", padx=10, pady=5)

        # Campos do cargo
        campos_frame = ttk.Frame(cadastro_cargo_frame)
        campos_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(campos_frame, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cargo_nome_var = tk.StringVar()
        ttk.Entry(campos_frame, textvariable=self.cargo_nome_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(campos_frame, text="Descrição:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.cargo_descricao_var = tk.StringVar()
        ttk.Entry(campos_frame, textvariable=self.cargo_descricao_var, width=40).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(campos_frame, text="Salário Base:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.cargo_salario_var = tk.StringVar()
        ttk.Entry(campos_frame, textvariable=self.cargo_salario_var, width=15).grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(campos_frame, text="Salvar Cargo", command=self.salvar_cargo).grid(
            row=1, column=4, padx=10, pady=5
        )

        # Lista de cargos
        lista_cargo_frame = ttk.LabelFrame(cargo_frame, text="Cargos Cadastrados")
        lista_cargo_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Treeview cargos
        cargo_columns = ("id", "nome", "descricao", "salario_base", "colaboradores")
        self.cargo_tree = ttk.Treeview(lista_cargo_frame, columns=cargo_columns, show="headings", height=10)

        self.cargo_tree.heading("id", text="ID")
        self.cargo_tree.heading("nome", text="Nome")
        self.cargo_tree.heading("descricao", text="Descrição")
        self.cargo_tree.heading("salario_base", text="Salário Base")
        self.cargo_tree.heading("colaboradores", text="Colaboradores")

        self.cargo_tree.column("id", width=50)
        self.cargo_tree.column("nome", width=200)
        self.cargo_tree.column("descricao", width=300)
        self.cargo_tree.column("salario_base", width=100)
        self.cargo_tree.column("colaboradores", width=100)

        self.cargo_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def create_estatisticas_tab(self):
        """Criar aba de estatísticas"""

        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Estatísticas")

        # Título
        ttk.Label(stats_frame, text="Estatísticas de Colaboradores", font=("Arial", 14, "bold")).pack(pady=10)

        # Frame dos cards
        cards_frame = ttk.Frame(stats_frame)
        cards_frame.pack(fill="x", padx=20, pady=10)

        # Cards de estatísticas
        self.create_stat_card(cards_frame, "Total Colaboradores", "0", 0, 0)
        self.create_stat_card(cards_frame, "Ativos", "0", 0, 1)
        self.create_stat_card(cards_frame, "Inativos", "0", 0, 2)
        self.create_stat_card(cards_frame, "Departamentos", "0", 1, 0)
        self.create_stat_card(cards_frame, "Cargos", "0", 1, 1)
        self.create_stat_card(cards_frame, "Folha Salarial", "R$ 0,00", 1, 2)

        # Atualizar estatísticas
        threading.Thread(target=self.carregar_estatisticas, daemon=True).start()

    def create_stat_card(self, parent, titulo, valor, row, col):
        """Criar card de estatística"""

        card_frame = ttk.LabelFrame(parent, text=titulo)
        card_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        valor_label = ttk.Label(card_frame, text=valor, font=("Arial", 16, "bold"))
        valor_label.pack(pady=10)

        # Armazenar referência para atualização
        setattr(self, f"stat_{titulo.lower().replace(' ', '_')}", valor_label)

    # =======================================
    # MÉTODOS DE DADOS
    # =======================================

    def carregar_dados_iniciais(self):
        """Carregar dados iniciais em thread separada"""
        threading.Thread(target=self._carregar_dados_iniciais, daemon=True).start()

    def _carregar_dados_iniciais(self):
        """Carregar dados iniciais (executa em thread)"""
        try:
            self.carregar_colaboradores()
            self.carregar_departamentos()
            self.carregar_cargos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")

    def carregar_colaboradores(self):
        """Carregar lista de colaboradores"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/colaboradores",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                self.colaboradores = response.json().get('colaboradores', [])
                self.window.after(0, self.atualizar_lista_colaboradores)
            else:
                self.window.after(0, lambda: messagebox.showerror("Erro", "Erro ao carregar colaboradores"))

        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Erro", f"Erro de conexão: {e}"))

    def carregar_departamentos(self):
        """Carregar lista de departamentos"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/colaboradores/departamentos",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                self.departamentos = response.json()
                self.window.after(0, self.atualizar_combos_departamentos)

        except Exception as e:
            print(f"Erro ao carregar departamentos: {e}")

    def carregar_cargos(self):
        """Carregar lista de cargos"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/colaboradores/cargos",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                self.cargos = response.json()
                self.window.after(0, self.atualizar_combos_cargos)

        except Exception as e:
            print(f"Erro ao carregar cargos: {e}")

    def carregar_estatisticas(self):
        """Carregar estatísticas"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/colaboradores/estatisticas",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                stats = response.json()
                self.window.after(0, lambda: self.atualizar_estatisticas(stats))

        except Exception as e:
            print(f"Erro ao carregar estatísticas: {e}")

    # =======================================
    # MÉTODOS DE INTERFACE
    # =======================================

    def atualizar_lista_colaboradores(self):
        """Atualizar lista de colaboradores no treeview"""

        # Limpar lista atual
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Adicionar colaboradores
        for colaborador in self.colaboradores:
            departamento_nome = next(
                (d['nome'] for d in self.departamentos if d['id'] == colaborador.get('departamento_id')),
                'N/A'
            )
            cargo_nome = next(
                (c['nome'] for c in self.cargos if c['id'] == colaborador.get('cargo_id')),
                'N/A'
            )

            salario = f"R$ {colaborador.get('salario', 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

            self.tree.insert('', 'end', values=(
                colaborador.get('matricula', ''),
                colaborador.get('nome_completo', ''),
                colaborador.get('cp', ''),
                departamento_nome,
                cargo_nome,
                colaborador.get('data_admissao', ''),
                salario,
                colaborador.get('status', '')
            ))

    def atualizar_combos_departamentos(self):
        """Atualizar comboboxes de departamentos"""

        valores = [f"{d['id']} - {d['nome']}" for d in self.departamentos]

        self.departamento_combo['values'] = ["Todos"] + [d['nome'] for d in self.departamentos]
        self.departamento_combo_form['values'] = valores

        # Atualizar treeview de departamentos
        for item in self.dept_tree.get_children():
            self.dept_tree.delete(item)

        for dept in self.departamentos:
            self.dept_tree.insert('', 'end', values=(
                dept['id'],
                dept['nome'],
                dept.get('descricao', ''),
                dept.get('total_colaboradores', 0)
            ))

    def atualizar_combos_cargos(self):
        """Atualizar comboboxes de cargos"""

        valores = [f"{c['id']} - {c['nome']}" for c in self.cargos]
        self.cargo_combo_form['values'] = valores

        # Atualizar treeview de cargos
        for item in self.cargo_tree.get_children():
            self.cargo_tree.delete(item)

        for cargo in self.cargos:
            salario = f"R$ {cargo.get('salario_base', 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

            self.cargo_tree.insert('', 'end', values=(
                cargo['id'],
                cargo['nome'],
                cargo.get('descricao', ''),
                salario,
                cargo.get('total_colaboradores', 0)
            ))

    def atualizar_estatisticas(self, stats):
        """Atualizar cards de estatísticas"""

        if hasattr(self, 'stat_total_colaboradores'):
            self.stat_total_colaboradores.config(text=str(stats.get('total_colaboradores', 0)))

        if hasattr(self, 'stat_ativos'):
            self.stat_ativos.config(text=str(stats.get('colaboradores_ativos', 0)))

        if hasattr(self, 'stat_inativos'):
            self.stat_inativos.config(text=str(stats.get('colaboradores_inativos', 0)))

        if hasattr(self, 'stat_departamentos'):
            self.stat_departamentos.config(text=str(stats.get('total_departamentos', 0)))

        if hasattr(self, 'stat_cargos'):
            self.stat_cargos.config(text=str(stats.get('total_cargos', 0)))

        if hasattr(self, 'stat_folha_salarial'):
            folha = stats.get('folha_salarial_total', 0)
            folha_formatada = f"R$ {folha:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            self.stat_folha_salarial.config(text=folha_formatada)

    # =======================================
    # MÉTODOS DE AÇÃO
    # =======================================

    def filtrar_colaboradores(self, event=None):
        """Filtrar colaboradores conforme critérios"""

        busca = self.busca_var.get().lower()
        departamento = self.departamento_var.get()
        status = self.status_var.get()

        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filtrar colaboradores
        for colaborador in self.colaboradores:
            # Filtro de busca
            if busca and busca not in colaborador.get('nome_completo', '').lower() and \
               busca not in colaborador.get('matricula', '').lower() and \
               busca not in colaborador.get('cp', '').lower():
                continue

            # Filtro de departamento
            if departamento and departamento != "Todos":
                dept_nome = next(
                    (d['nome'] for d in self.departamentos if d['id'] == colaborador.get('departamento_id')),
                    ''
                )
                if departamento != dept_nome:
                    continue

            # Filtro de status
            if status and status != "Todos" and status != colaborador.get('status'):
                continue

            # Adicionar ao treeview
            departamento_nome = next(
                (d['nome'] for d in self.departamentos if d['id'] == colaborador.get('departamento_id')),
                'N/A'
            )
            cargo_nome = next(
                (c['nome'] for c in self.cargos if c['id'] == colaborador.get('cargo_id')),
                'N/A'
            )

            salario = f"R$ {colaborador.get('salario', 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

            self.tree.insert('', 'end', values=(
                colaborador.get('matricula', ''),
                colaborador.get('nome_completo', ''),
                colaborador.get('cp', ''),
                departamento_nome,
                cargo_nome,
                colaborador.get('data_admissao', ''),
                salario,
                colaborador.get('status', '')
            ))

    def ir_para_cadastro(self):
        """Ir para aba de cadastro"""
        self.notebook.select(1)  # Aba de cadastro
        self.limpar_formulario()

    def editar_colaborador(self):
        """Editar colaborador selecionado"""

        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um colaborador para editar")
            return

        item = self.tree.item(selection[0])
        matricula = item['values'][0]

        # Buscar colaborador
        colaborador = next((c for c in self.colaboradores if c.get('matricula') == matricula), None)
        if not colaborador:
            messagebox.showerror("Erro", "Colaborador não encontrado")
            return

        # Ir para aba de cadastro e preencher formulário
        self.notebook.select(1)
        self.preencher_formulario(colaborador)

    def preencher_formulario(self, colaborador):
        """Preencher formulário com dados do colaborador"""

        # Limpar formulário
        self.limpar_formulario()

        # Preencher campos
        for campo, valor in colaborador.items():
            if campo in self.form_vars and valor is not None:
                if campo in ['departamento_id', 'cargo_id']:
                    # Para comboboxes de relacionamento
                    if campo == 'departamento_id':
                        item = next((d for d in self.departamentos if d['id'] == valor), None)
                        if item:
                            self.form_vars[campo].set(f"{item['id']} - {item['nome']}")
                    elif campo == 'cargo_id':
                        item = next((c for c in self.cargos if c['id'] == valor), None)
                        if item:
                            self.form_vars[campo].set(f"{item['id']} - {item['nome']}")
                else:
                    self.form_vars[campo].set(str(valor))

        # Armazenar colaborador sendo editado
        self.colaborador_selecionado = colaborador

    def salvar_colaborador(self):
        """Salvar colaborador (novo ou editado)"""

        # Validar campos obrigatórios
        if not self.validar_formulario():
            return

        # Preparar dados
        dados = self.preparar_dados_formulario()

        # Executar em thread
        threading.Thread(
            target=self._salvar_colaborador,
            args=(dados,),
            daemon=True
        ).start()

    def _salvar_colaborador(self, dados):
        """Salvar colaborador (executa em thread)"""

        try:
            if self.colaborador_selecionado:
                # Editar colaborador existente
                response = requests.put(
                    f"{API_BASE_URL}/api/v1/colaboradores/{self.colaborador_selecionado['id']}",
                    json=dados,
                    headers=self.headers,
                    timeout=10
                )
            else:
                # Criar novo colaborador
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/colaboradores",
                    json=dados,
                    headers=self.headers,
                    timeout=10
                )

            if response.status_code in [200, 201]:
                self.window.after(0, lambda: messagebox.showinfo("Sucesso", "Colaborador salvo com sucesso!"))
                self.window.after(0, self.limpar_formulario)
                self.window.after(0, lambda: self.notebook.select(0))  # Voltar para lista
                self.carregar_colaboradores()
            else:
                erro = response.json().get('detail', 'Erro desconhecido')
                self.window.after(0, lambda: messagebox.showerror("Erro", f"Erro ao salvar: {erro}"))

        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Erro", f"Erro de conexão: {e}"))

    def salvar_departamento(self):
        """Salvar novo departamento"""

        nome = self.dept_nome_var.get().strip()
        descricao = self.dept_descricao_var.get().strip()

        if not nome:
            messagebox.showwarning("Aviso", "Nome do departamento é obrigatório")
            return

        dados = {
            "nome": nome,
            "descricao": descricao,
            "ativo": True
        }

        threading.Thread(
            target=self._salvar_departamento,
            args=(dados,),
            daemon=True
        ).start()

    def _salvar_departamento(self, dados):
        """Salvar departamento (executa em thread)"""

        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/colaboradores/departamentos",
                json=dados,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 201:
                self.window.after(0, lambda: messagebox.showinfo("Sucesso", "Departamento criado com sucesso!"))
                self.window.after(0, lambda: self.dept_nome_var.set(""))
                self.window.after(0, lambda: self.dept_descricao_var.set(""))
                self.carregar_departamentos()
            else:
                erro = response.json().get('detail', 'Erro desconhecido')
                self.window.after(0, lambda: messagebox.showerror("Erro", f"Erro ao salvar: {erro}"))

        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Erro", f"Erro de conexão: {e}"))

    def salvar_cargo(self):
        """Salvar novo cargo"""

        nome = self.cargo_nome_var.get().strip()
        descricao = self.cargo_descricao_var.get().strip()
        salario = self.cargo_salario_var.get().strip()

        if not nome:
            messagebox.showwarning("Aviso", "Nome do cargo é obrigatório")
            return

        try:
            salario_valor = float(salario.replace(',', '.')) if salario else 0.0
        except ValueError:
            messagebox.showerror("Erro", "Salário deve ser um número válido")
            return

        dados = {
            "nome": nome,
            "descricao": descricao,
            "salario_base": salario_valor,
            "ativo": True
        }

        threading.Thread(
            target=self._salvar_cargo,
            args=(dados,),
            daemon=True
        ).start()

    def _salvar_cargo(self, dados):
        """Salvar cargo (executa em thread)"""

        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/colaboradores/cargos",
                json=dados,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 201:
                self.window.after(0, lambda: messagebox.showinfo("Sucesso", "Cargo criado com sucesso!"))
                self.window.after(0, lambda: self.cargo_nome_var.set(""))
                self.window.after(0, lambda: self.cargo_descricao_var.set(""))
                self.window.after(0, lambda: self.cargo_salario_var.set(""))
                self.carregar_cargos()
            else:
                erro = response.json().get('detail', 'Erro desconhecido')
                self.window.after(0, lambda: messagebox.showerror("Erro", f"Erro ao salvar: {erro}"))

        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Erro", f"Erro de conexão: {e}"))

    def gerar_relatorio(self):
        """Gerar relatório de colaboradores"""
        messagebox.showinfo("Em Desenvolvimento", "Funcionalidade de relatórios será implementada em breve")

    # =======================================
    # MÉTODOS DE VALIDAÇÃO E FORMATAÇÃO
    # =======================================

    def validar_formulario(self):
        """Validar campos obrigatórios do formulário"""

        campos_obrigatorios = [
            ('nome_completo', 'Nome Completo'),
            ('cp', 'CPF'),
            ('telefone', 'Telefone'),
            ('matricula', 'Matrícula'),
            ('data_admissao', 'Data de Admissão'),
            ('departamento_id', 'Departamento'),
            ('cargo_id', 'Cargo'),
            ('tipo_contrato', 'Tipo de Contrato')
        ]

        for campo, nome in campos_obrigatorios:
            if not self.form_vars[campo].get().strip():
                messagebox.showerror("Erro", f"Campo '{nome}' é obrigatório")
                return False

        # Validar CPF
        if not self.validar_cpf(self.form_vars['cp'].get()):
            messagebox.showerror("Erro", "CPF inválido")
            return False

        return True

    def validar_cpf(self, cpf):
        """Validar CPF"""
        # Remove formatação
        cpf = re.sub(r'[^0-9]', '', cpf)

        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        # Validar dígitos verificadores
        def calcular_digito(cpf, peso):
            soma = sum(int(cpf[i]) * peso[i] for i in range(len(peso)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto

        peso1 = list(range(10, 1, -1))
        peso2 = list(range(11, 1, -1))

        digito1 = calcular_digito(cpf, peso1)
        digito2 = calcular_digito(cpf, peso2)

        return cpf[-2:] == f"{digito1}{digito2}"

    def formatar_cpf(self, event=None):
        """Formatar CPF automaticamente"""
        widget = event.widget
        valor = widget.get()

        # Remove caracteres não numéricos
        numeros = re.sub(r'[^0-9]', '', valor)

        # Aplica máscara
        if len(numeros) <= 11:
            if len(numeros) > 9:
                formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
            elif len(numeros) > 6:
                formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:]}"
            elif len(numeros) > 3:
                formatado = f"{numeros[:3]}.{numeros[3:]}"
            else:
                formatado = numeros

            widget.delete(0, tk.END)
            widget.insert(0, formatado)

    def formatar_telefone(self, event=None):
        """Formatar telefone automaticamente"""
        widget = event.widget
        valor = widget.get()

        # Remove caracteres não numéricos
        numeros = re.sub(r'[^0-9]', '', valor)

        # Aplica máscara
        if len(numeros) <= 11:
            if len(numeros) > 7:
                if len(numeros) == 11:  # Celular
                    formatado = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
                else:  # Fixo
                    formatado = f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
            elif len(numeros) > 2:
                formatado = f"({numeros[:2]}) {numeros[2:]}"
            else:
                formatado = numeros

            widget.delete(0, tk.END)
            widget.insert(0, formatado)

    def formatar_cep(self, event=None):
        """Formatar CEP automaticamente"""
        widget = event.widget
        valor = widget.get()

        # Remove caracteres não numéricos
        numeros = re.sub(r'[^0-9]', '', valor)

        # Aplica máscara
        if len(numeros) <= 8:
            if len(numeros) > 5:
                formatado = f"{numeros[:5]}-{numeros[5:]}"
            else:
                formatado = numeros

            widget.delete(0, tk.END)
            widget.insert(0, formatado)

    def preparar_dados_formulario(self):
        """Preparar dados do formulário para envio"""

        dados = {}

        # Campos diretos
        campos_diretos = [
            'nome_completo', 'cp', 'rg', 'data_nascimento', 'estado_civil',
            'email_pessoal', 'telefone', 'matricula', 'data_admissao',
            'tipo_contrato', 'cep', 'logradouro', 'numero', 'complemento',
            'bairro', 'cidade', 'u'
        ]

        for campo in campos_diretos:
            valor = self.form_vars[campo].get().strip()
            if valor:
                dados[campo] = valor

        # Salário
        salario = self.form_vars['salario'].get().strip()
        if salario:
            try:
                dados['salario'] = float(salario.replace(',', '.'))
            except ValueError:
                pass

        # Departamento ID
        dept_value = self.form_vars['departamento_id'].get()
        if dept_value and ' - ' in dept_value:
            dados['departamento_id'] = int(dept_value.split(' - ')[0])

        # Cargo ID
        cargo_value = self.form_vars['cargo_id'].get()
        if cargo_value and ' - ' in cargo_value:
            dados['cargo_id'] = int(cargo_value.split(' - ')[0])

        # Status padrão
        dados['status'] = 'ATIVO'
        dados['ativo'] = True

        return dados

    def limpar_formulario(self):
        """Limpar todos os campos do formulário"""

        for var in self.form_vars.values():
            var.set("")

        self.colaborador_selecionado = None

    def cancelar_edicao(self):
        """Cancelar edição e voltar para lista"""

        self.limpar_formulario()
        self.notebook.select(0)  # Voltar para aba de lista

    # =======================================
    # EVENTOS
    # =======================================

    def on_item_select(self, event):
        """Evento de seleção de item"""
        pass

    def on_item_double_click(self, event):
        """Evento de duplo clique no item"""
        self.editar_colaborador()


# =======================================
# FUNÇÃO PARA TESTE
# =======================================

def main():
    """Função principal para teste"""

    # Criar janela principal
    root = tk.Tk()
    root.withdraw()  # Ocultar janela principal

    # Criar interface de colaboradores
    app = ColaboradoresWindow()

    # Iniciar loop principal
    root.mainloop()


if __name__ == "__main__":
    main()