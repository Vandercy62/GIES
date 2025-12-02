#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA ERP PRIMOTEX - WIZARD DE COLABORADORES
==============================================

Interface tkinter para gestão completa de colaboradores/funcionários.
Implementa wizard com 4 abas seguindo padrão do sistema.

ABAS DO WIZARD:
1. 📋 Dados Pessoais - Nome, CPF, RG, nascimento, endereço
2. 💼 Dados Profissionais - Matrícula, cargo, departamento, salário
3. 📄 Documentos - Upload documentos + sistema de alertas vencimento ⭐
4. 📊 Estatísticas - Resumo, tempo empresa, histórico

FUNCIONALIDADES CRÍTICAS:
- Sistema de alertas documentos (4 cores: 🟢>30d 🟡15-30d 🟠1-14d 🔴vencido)
- Captura foto 3x4 (upload OU webcam)
- Validação CPF, telefone, CEP
- Integração completa com API

Autor: GitHub Copilot
Data: 17/11/2025 - FASE 102
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import threading
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Any
import base64
import io
from PIL import Image, ImageTk

# Imports do projeto
from frontend.desktop.auth_middleware import (
    require_login,
    get_token_for_api,
    create_auth_header,
    get_current_user_info
)
from frontend.desktop.foto_dialog import FotoDialog

# Configuração da API
API_BASE_URL = "http://127.0.0.1:8002"


@require_login()
class ColaboradoresWizard:
    """
    Wizard completo de colaboradores com 4 abas.

    Segue padrão fornecedores_wizard.py e clientes_wizard.py.
    """

    def __init__(self, parent=None):
        """
        Inicializar wizard de colaboradores.

        Args:
            parent: Janela pai (opcional)
        """
        self.parent = parent
        self.token = get_token_for_api()
        self.headers = create_auth_header()
        self.current_user = get_current_user_info()

        # Dados
        self.colaboradores = []
        self.colaborador_selecionado = None
        self.modo_edicao = False

        # Dados auxiliares (cargos, departamentos)
        self.cargos_list = []
        self.departamentos_list = []

        # Foto 3x4
        self.foto_base64 = None
        self.foto_preview_label = None
        self.foto_photo_tk = None

        # Configurar janela
        self.setup_window()
        self.create_widgets()
        self.carregar_dados_iniciais()

    def setup_window(self):
        """Configurar janela principal"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Sistema ERP Primotex - Gestão de Colaboradores")
        self.window.geometry("1400x800")
        self.window.minsize(1200, 700)

        # Centralizar
        if self.parent:
            self.window.transient(self.parent)
            self.window.grab_set()

        # Grid config
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Protocolo de fechamento
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Criar todos os widgets da interface"""

        # Frame principal
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Cabeçalho
        self.create_header(main_frame)

        # Notebook principal (4 abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        # Criar abas
        self.create_aba_listagem()
        self.create_aba_dados_pessoais()
        self.create_aba_dados_profissionais()
        self.create_aba_documentos()
        self.create_aba_estatisticas()

        # Rodapé com botões
        self.create_footer(main_frame)

    def create_header(self, parent):
        """Criar cabeçalho com título e informações"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)

        # Título
        title_label = ttk.Label(
            header_frame,
            text="👥 GESTÃO DE COLABORADORES",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=(0, 20))

        # Info usuário logado
        user_label = ttk.Label(
            header_frame,
            text=f"Usuário: {self.current_user.get('username', 'N/A')} | Perfil: {self.current_user.get('perfil', 'N/A')}",
            font=("Arial", 9)
        )
        user_label.grid(row=0, column=1, sticky="e")

        # Separador
        ttk.Separator(parent, orient="horizontal").grid(
            row=1, column=0, sticky="ew", pady=5
        )

    def create_aba_listagem(self):
        """
        ABA 1: LISTAGEM DE COLABORADORES

        TreeView com filtros por departamento, cargo, status.
        Duplo-clique abre edição.
        """
        lista_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(lista_frame, text="📋 Lista de Colaboradores")

        lista_frame.grid_rowconfigure(2, weight=1)
        lista_frame.grid_columnconfigure(0, weight=1)

        # Filtros
        filtros_frame = ttk.LabelFrame(lista_frame, text="Filtros", padding=10)
        filtros_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Campo de busca
        ttk.Label(filtros_frame, text="Buscar:").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filtros_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky="w", padx=5)

        # Botão buscar
        ttk.Button(
            filtros_frame,
            text="🔍 Buscar",
            command=self.filtrar_colaboradores
        ).grid(row=0, column=2, padx=5)

        # Botão limpar
        ttk.Button(
            filtros_frame,
            text="🔄 Limpar",
            command=self.limpar_filtros
        ).grid(row=0, column=3, padx=5)

        # Estatísticas rápidas
        self.stats_label = ttk.Label(
            lista_frame,
            text="Total: 0 colaboradores | Ativos: 0 | Inativos: 0",
            font=("Arial", 9, "bold")
        )
        self.stats_label.grid(row=1, column=0, sticky="w", pady=5)

        # TreeView
        tree_frame = ttk.Frame(lista_frame)
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")

        # TreeView
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("id", "matricula", "nome", "cp", "cargo", "departamento", "status", "admissao"),
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )

        # Configurar colunas
        self.tree.heading("id", text="ID")
        self.tree.heading("matricula", text="Matrícula")
        self.tree.heading("nome", text="Nome Completo")
        self.tree.heading("cp", text="CPF")
        self.tree.heading("cargo", text="Cargo")
        self.tree.heading("departamento", text="Departamento")
        self.tree.heading("status", text="Status")
        self.tree.heading("admissao", text="Admissão")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("matricula", width=100, anchor="center")
        self.tree.column("nome", width=250)
        self.tree.column("cp", width=120, anchor="center")
        self.tree.column("cargo", width=150)
        self.tree.column("departamento", width=150)
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("admissao", width=100, anchor="center")

        # Layout scrollbars
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")

        # Eventos
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # Botões de ação
        actions_frame = ttk.Frame(lista_frame)
        actions_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        ttk.Button(
            actions_frame,
            text="➕ Novo Colaborador",
            command=self.novo_colaborador
        ).pack(side="left", padx=5)

        ttk.Button(
            actions_frame,
            text="✏️ Editar Selecionado",
            command=self.editar_colaborador
        ).pack(side="left", padx=5)

        ttk.Button(
            actions_frame,
            text="🗑️ Inativar Selecionado",
            command=self.inativar_colaborador
        ).pack(side="left", padx=5)

        ttk.Button(
            actions_frame,
            text="🔄 Atualizar Lista",
            command=self.atualizar_lista
        ).pack(side="left", padx=5)

    def create_aba_dados_pessoais(self):
        """
        ABA 2: DADOS PESSOAIS

        Formulário completo com validações CPF/CEP/Telefone.
        Campos: nome, CPF, RG, nascimento, estado civil, endereço completo.
        """
        dados_pessoais_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(dados_pessoais_frame, text="👤 Dados Pessoais")

        # Configurar scroll
        canvas = tk.Canvas(dados_pessoais_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            dados_pessoais_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Variáveis do formulário
        self.nome_completo_var = tk.StringVar()
        self.nome_social_var = tk.StringVar()
        self.cpf_var = tk.StringVar()
        self.rg_var = tk.StringVar()
        self.data_nascimento_var = tk.StringVar()
        self.estado_civil_var = tk.StringVar()
        self.sexo_var = tk.StringVar()
        self.nacionalidade_var = tk.StringVar(value="Brasileira")
        self.naturalidade_var = tk.StringVar()

        # Contato
        self.telefone_principal_var = tk.StringVar()
        self.telefone_secundario_var = tk.StringVar()
        self.email_pessoal_var = tk.StringVar()
        self.email_corporativo_var = tk.StringVar()

        # Endereço
        self.cep_var = tk.StringVar()
        self.logradouro_var = tk.StringVar()
        self.numero_var = tk.StringVar()
        self.complemento_var = tk.StringVar()
        self.bairro_var = tk.StringVar()
        self.cidade_var = tk.StringVar()
        self.estado_var = tk.StringVar()

        row = 0

        # === SEÇÃO 0: FOTO 3x4 ===
        foto_frame = ttk.Frame(scrollable_frame, relief="solid", borderwidth=1)
        foto_frame.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 15))

        # Preview da foto
        self.foto_preview_label = tk.Label(
            foto_frame, text="SEM\nFOTO", font=("Segoe UI", 9),
            width=12, height=6, bg="#f0f0f0", fg="#999"
        )
        self.foto_preview_label.pack(padx=5, pady=5)

        # Botão capturar/carregar
        btn_foto = ttk.Button(
            foto_frame, text="📸 Foto 3x4",
            command=self.abrir_dialog_foto, width=14
        )
        btn_foto.pack(pady=(0, 5))

        row += 1

        # === SEÇÃO 1: DADOS BÁSICOS ===
        secao1_label = ttk.Label(
            scrollable_frame,
            text="📋 DADOS BÁSICOS",
            font=("Arial", 11, "bold")
        )
        secao1_label.grid(row=row, column=0, columnspan=4, sticky="w", pady=(0, 10))
        row += 1

        # Nome completo (obrigatório)
        ttk.Label(scrollable_frame, text="Nome Completo: *").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        nome_entry = ttk.Entry(
            scrollable_frame, textvariable=self.nome_completo_var, width=40
        )
        nome_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        # Nome social (opcional)
        ttk.Label(scrollable_frame, text="Nome Social:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        nome_social_entry = ttk.Entry(
            scrollable_frame, textvariable=self.nome_social_var, width=40
        )
        nome_social_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        # CPF (obrigatório com validação)
        ttk.Label(scrollable_frame, text="CPF: *").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        cpf_frame = ttk.Frame(scrollable_frame)
        cpf_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        cpf_entry = ttk.Entry(cpf_frame, textvariable=self.cpf_var, width=20)
        cpf_entry.pack(side="left", padx=(0, 5))

        self.cpf_status_label = ttk.Label(cpf_frame, text="", foreground="gray")
        self.cpf_status_label.pack(side="left")

        # Bind validação CPF
        self.cpf_var.trace("w", self.validar_cpf_real_time)
        row += 1

        # RG
        ttk.Label(scrollable_frame, text="RG:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(scrollable_frame, textvariable=self.rg_var, width=20).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )
        row += 1

        # Data de nascimento
        ttk.Label(scrollable_frame, text="Data de Nascimento:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            scrollable_frame, textvariable=self.data_nascimento_var, width=15
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(scrollable_frame, text="(DD/MM/AAAA)", font=("Arial", 8)).grid(
            row=row, column=1, sticky="w", padx=(120, 0), pady=5
        )
        row += 1

        # Estado civil
        ttk.Label(scrollable_frame, text="Estado Civil:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        estado_civil_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.estado_civil_var,
            values=["Solteiro(a)", "Casado(a)", "Divorciado(a)", 
                    "Viúvo(a)", "União Estável"],
            state="readonly",
            width=18
        )
        estado_civil_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1

        # Sexo
        ttk.Label(scrollable_frame, text="Sexo:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        sexo_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.sexo_var,
            values=["Masculino", "Feminino", "Outro", "Prefiro não informar"],
            state="readonly",
            width=18
        )
        sexo_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1

        # Nacionalidade e Naturalidade
        ttk.Label(scrollable_frame, text="Nacionalidade:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(scrollable_frame, textvariable=self.nacionalidade_var, width=20).grid(
            row=row, column=1, sticky="w", padx=5, pady=5
        )
        row += 1

        ttk.Label(scrollable_frame, text="Naturalidade:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(scrollable_frame, textvariable=self.naturalidade_var, width=30).grid(
            row=row, column=1, sticky="ew", padx=5, pady=5
        )
        row += 1

        # Separador
        ttk.Separator(scrollable_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=4, sticky="ew", pady=15
        )
        row += 1

        # === SEÇÃO 2: CONTATO ===
        secao2_label = ttk.Label(
            scrollable_frame,
            text="📞 CONTATO",
            font=("Arial", 11, "bold")
        )
        secao2_label.grid(row=row, column=0, columnspan=4, sticky="w", pady=(0, 10))
        row += 1

        # Telefone principal (obrigatório)
        ttk.Label(scrollable_frame, text="Telefone Principal: *").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        tel_frame = ttk.Frame(scrollable_frame)
        tel_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        tel_entry = ttk.Entry(tel_frame, textvariable=self.telefone_principal_var, width=20)
        tel_entry.pack(side="left", padx=(0, 5))

        self.tel_status_label = ttk.Label(tel_frame, text="", foreground="gray")
        self.tel_status_label.pack(side="left")

        # Bind validação telefone
        self.telefone_principal_var.trace("w", self.validar_telefone_real_time)
        row += 1

        # Telefone secundário
        ttk.Label(scrollable_frame, text="Telefone Secundário:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            scrollable_frame, textvariable=self.telefone_secundario_var, width=20
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1

        # Email pessoal
        ttk.Label(scrollable_frame, text="Email Pessoal:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            scrollable_frame, textvariable=self.email_pessoal_var, width=40
        ).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        # Email corporativo
        ttk.Label(scrollable_frame, text="Email Corporativo:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            scrollable_frame, textvariable=self.email_corporativo_var, width=40
        ).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1

        # Separador
        ttk.Separator(scrollable_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=4, sticky="ew", pady=15
        )
        row += 1

        # === SEÇÃO 3: ENDEREÇO ===
        secao3_label = ttk.Label(
            scrollable_frame,
            text="🏠 ENDEREÇO",
            font=("Arial", 11, "bold")
        )
        secao3_label.grid(row=row, column=0, columnspan=4, sticky="w", pady=(0, 10))
        row += 1

        # CEP com busca automática
        ttk.Label(scrollable_frame, text="CEP:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        cep_frame = ttk.Frame(scrollable_frame)
        cep_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        cep_entry = ttk.Entry(cep_frame, textvariable=self.cep_var, width=15)
        cep_entry.pack(side="left", padx=(0, 5))

        ttk.Button(
            cep_frame,
            text="🔍 Buscar",
            command=self.buscar_cep,
            width=10
        ).pack(side="left")

        self.cep_status_label = ttk.Label(cep_frame, text="", foreground="gray")
        self.cep_status_label.pack(side="left", padx=5)
        row += 1

        # Logradouro
        ttk.Label(scrollable_frame, text="Logradouro:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(scrollable_frame, textvariable=self.logradouro_var, width=40).grid(
            row=row, column=1, sticky="ew", padx=5, pady=5
        )
        row += 1

        # Número e Complemento
        ttk.Label(scrollable_frame, text="Número:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        numero_compl_frame = ttk.Frame(scrollable_frame)
        numero_compl_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        ttk.Entry(numero_compl_frame, textvariable=self.numero_var, width=10).pack(
            side="left", padx=(0, 10)
        )
        ttk.Label(numero_compl_frame, text="Complemento:").pack(side="left", padx=(0, 5))
        ttk.Entry(numero_compl_frame, textvariable=self.complemento_var, width=20).pack(
            side="left"
        )
        row += 1

        # Bairro
        ttk.Label(scrollable_frame, text="Bairro:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(scrollable_frame, textvariable=self.bairro_var, width=30).grid(
            row=row, column=1, sticky="ew", padx=5, pady=5
        )
        row += 1

        # Cidade e Estado
        ttk.Label(scrollable_frame, text="Cidade:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        cidade_estado_frame = ttk.Frame(scrollable_frame)
        cidade_estado_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        ttk.Entry(
            cidade_estado_frame, textvariable=self.cidade_var, width=25
        ).pack(side="left", padx=(0, 10))

        ttk.Label(cidade_estado_frame, text="UF:").pack(side="left", padx=(0, 5))

        estado_combo = ttk.Combobox(
            cidade_estado_frame,
            textvariable=self.estado_var,
            values=[
                "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
                "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
                "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
            ],
            state="readonly",
            width=5
        )
        estado_combo.pack(side="left")
        row += 1

        # Configurar grid
        scrollable_frame.grid_columnconfigure(1, weight=1)

    def create_aba_dados_profissionais(self):
        """
        ABA 2: DADOS PROFISSIONAIS

        Formulário completo com campos obrigatórios para criação de colaborador.
        TAREFA 4 - Implementado em 17/11/2025
        """
        dados_prof_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(dados_prof_frame, text="💼 Dados Profissionais")

        # Configurar scroll
        canvas = tk.Canvas(dados_prof_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            dados_prof_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Variáveis do formulário
        self.matricula_var = tk.StringVar()
        self.user_id_var = tk.StringVar()
        self.cargo_id_var = tk.StringVar()
        self.departamento_id_var = tk.StringVar()
        self.superior_id_var = tk.StringVar()
        self.tipo_contrato_var = tk.StringVar()
        self.data_admissao_var = tk.StringVar()
        self.salario_base_var = tk.StringVar()
        self.carga_horaria_semanal_var = tk.StringVar(value="44")
        self.horario_entrada_var = tk.StringVar(value="08:00")
        self.horario_saida_var = tk.StringVar(value="17:00")
        self.horario_almoco_inicio_var = tk.StringVar(value="12:00")
        self.horario_almoco_fim_var = tk.StringVar(value="13:00")
        self.vale_transporte_var = tk.BooleanVar(value=False)
        self.vale_refeicao_var = tk.BooleanVar(value=False)
        self.plano_saude_var = tk.BooleanVar(value=False)

        row = 0

        # === SEÇÃO 1: IDENTIFICAÇÃO ===
        secao1_label = ttk.Label(
            scrollable_frame,
            text="🆔 IDENTIFICAÇÃO",
            font=("Arial", 11, "bold")
        )
        secao1_label.grid(
            row=row, column=0, columnspan=4, sticky="w", pady=(0, 10)
        )
        row += 1

        # Matrícula (obrigatório, único)
        ttk.Label(scrollable_frame, text="Matrícula: *").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        matricula_entry = ttk.Entry(
            scrollable_frame, textvariable=self.matricula_var, width=20
        )
        matricula_entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(
            scrollable_frame, text="(Código único do colaborador)",
            font=("Arial", 8), foreground="gray"
        ).grid(row=row, column=2, sticky="w", padx=5, pady=5)
        row += 1

        # User ID (obrigatório para login)
        ttk.Label(scrollable_frame, text="User ID: *").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        user_id_entry = ttk.Entry(
            scrollable_frame, textvariable=self.user_id_var, width=20
        )
        user_id_entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(
            scrollable_frame, text="(ID do usuário para login no sistema)",
            font=("Arial", 8), foreground="gray"
        ).grid(row=row, column=2, sticky="w", padx=5, pady=5)
        row += 1

        # === SEÇÃO 2: HIERARQUIA ===
        secao2_label = ttk.Label(
            scrollable_frame,
            text="🏢 HIERARQUIA",
            font=("Arial", 11, "bold")
        )
        secao2_label.grid(
            row=row, column=0, columnspan=4, sticky="w", pady=(15, 10)
        )
        row += 1

        # Cargo (obrigatório)
        ttk.Label(scrollable_frame, text="Cargo: *").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        self.cargo_combo = ttk.Combobox(
            scrollable_frame, textvariable=self.cargo_id_var, width=30
        )
        self.cargo_combo.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        btn_novo_cargo = ttk.Button(
            scrollable_frame, text="➕ Novo", width=8,
            command=self.criar_cargo
        )
        btn_novo_cargo.grid(row=row, column=2, sticky="w", padx=5, pady=5)
        row += 1

        # Departamento (obrigatório)
        ttk.Label(scrollable_frame, text="Departamento: *").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        self.departamento_combo = ttk.Combobox(
            scrollable_frame, textvariable=self.departamento_id_var, width=30
        )
        self.departamento_combo.grid(
            row=row, column=1, sticky="ew", padx=5, pady=5
        )

        btn_novo_depto = ttk.Button(
            scrollable_frame, text="➕ Novo", width=8,
            command=self.criar_departamento
        )
        btn_novo_depto.grid(row=row, column=2, sticky="w", padx=5, pady=5)
        row += 1

        # Superior Direto (opcional)
        ttk.Label(scrollable_frame, text="Superior Direto:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        self.superior_combo = ttk.Combobox(
            scrollable_frame, textvariable=self.superior_id_var, width=30
        )
        self.superior_combo.grid(
            row=row, column=1, sticky="ew", padx=5, pady=5
        )
        row += 1

        # === SEÇÃO 3: CONTRATO ===
        secao3_label = ttk.Label(
            scrollable_frame,
            text="📄 CONTRATO",
            font=("Arial", 11, "bold")
        )
        secao3_label.grid(
            row=row, column=0, columnspan=4, sticky="w", pady=(15, 10)
        )
        row += 1

        # Tipo de Contrato (obrigatório)
        ttk.Label(scrollable_frame, text="Tipo Contrato: *").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        tipo_contrato_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.tipo_contrato_var,
            values=["CLT", "PJ", "Estágio", "Temporário", "Terceirizado"],
            state="readonly",
            width=18
        )
        tipo_contrato_combo.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1

        # Data de Admissão (obrigatório)
        ttk.Label(scrollable_frame, text="Data Admissão: *").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        ttk.Entry(
            scrollable_frame, textvariable=self.data_admissao_var, width=15
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(
            scrollable_frame, text="(DD/MM/AAAA)", font=("Arial", 8)
        ).grid(row=row, column=1, sticky="w", padx=(120, 0), pady=5)
        row += 1

        # Salário Base (obrigatório)
        ttk.Label(scrollable_frame, text="Salário Base: *").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        salario_frame = ttk.Frame(scrollable_frame)
        salario_frame.grid(row=row, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(salario_frame, text="R$").pack(side="left", padx=(0, 5))
        ttk.Entry(
            salario_frame, textvariable=self.salario_base_var, width=15
        ).pack(side="left")
        row += 1

        # === SEÇÃO 4: JORNADA DE TRABALHO ===
        secao4_label = ttk.Label(
            scrollable_frame,
            text="⏰ JORNADA DE TRABALHO",
            font=("Arial", 11, "bold")
        )
        secao4_label.grid(
            row=row, column=0, columnspan=4, sticky="w", pady=(15, 10)
        )
        row += 1

        # Carga Horária Semanal
        ttk.Label(scrollable_frame, text="Carga Horária Semanal:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        carga_frame = ttk.Frame(scrollable_frame)
        carga_frame.grid(row=row, column=1, sticky="w", padx=5, pady=5)

        ttk.Entry(
            carga_frame, textvariable=self.carga_horaria_semanal_var, width=8
        ).pack(side="left", padx=(0, 5))
        ttk.Label(carga_frame, text="horas/semana").pack(side="left")
        row += 1

        # Horários
        ttk.Label(scrollable_frame, text="Horário Entrada:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        horarios_frame = ttk.Frame(scrollable_frame)
        horarios_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        ttk.Entry(
            horarios_frame, textvariable=self.horario_entrada_var, width=8
        ).pack(side="left", padx=(0, 15))

        ttk.Label(horarios_frame, text="Saída:").pack(side="left", padx=(0, 5))
        ttk.Entry(
            horarios_frame, textvariable=self.horario_saida_var, width=8
        ).pack(side="left")
        row += 1

        # Horário Almoço
        ttk.Label(scrollable_frame, text="Horário Almoço:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5
        )
        almoco_frame = ttk.Frame(scrollable_frame)
        almoco_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(almoco_frame, text="Início:").pack(side="left", padx=(0, 5))
        ttk.Entry(
            almoco_frame, textvariable=self.horario_almoco_inicio_var, width=8
        ).pack(side="left", padx=(0, 15))

        ttk.Label(almoco_frame, text="Fim:").pack(side="left", padx=(0, 5))
        ttk.Entry(
            almoco_frame, textvariable=self.horario_almoco_fim_var, width=8
        ).pack(side="left")
        row += 1

        # === SEÇÃO 5: BENEFÍCIOS ===
        secao5_label = ttk.Label(
            scrollable_frame,
            text="🎁 BENEFÍCIOS",
            font=("Arial", 11, "bold")
        )
        secao5_label.grid(
            row=row, column=0, columnspan=4, sticky="w", pady=(15, 10)
        )
        row += 1

        # Checkboxes de benefícios
        beneficios_frame = ttk.Frame(scrollable_frame)
        beneficios_frame.grid(
            row=row, column=0, columnspan=4, sticky="w", padx=5, pady=5
        )

        ttk.Checkbutton(
            beneficios_frame, text="Vale Transporte",
            variable=self.vale_transporte_var
        ).pack(side="left", padx=(0, 15))

        ttk.Checkbutton(
            beneficios_frame, text="Vale Refeição",
            variable=self.vale_refeicao_var
        ).pack(side="left", padx=(0, 15))

        ttk.Checkbutton(
            beneficios_frame, text="Plano de Saúde",
            variable=self.plano_saude_var
        ).pack(side="left")
        row += 1

        # Nota informativa
        nota_label = ttk.Label(
            scrollable_frame,
            text="💡 Os campos marcados com * são obrigatórios",
            font=("Arial", 9), foreground="gray"
        )
        nota_label.grid(
            row=row, column=0, columnspan=4, sticky="w", padx=5, pady=(15, 5)
        )

        # Configurar grid
        scrollable_frame.grid_columnconfigure(1, weight=1)

    def create_aba_documentos(self):
        """
        ABA 4: DOCUMENTOS ⭐ (CRÍTICA) - TAREFA 5

        TreeView documentos + sistema de alertas 4 cores.
        Implementação completa com upload, download e exclusão.
        """
        documentos_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(documentos_frame, text="📄 Documentos ⭐")

        # Frame superior - Botões
        btn_frame = ttk.Frame(documentos_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            btn_frame,
            text="➕ Adicionar Documento",
            command=self._adicionar_documento
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="👁️ Visualizar",
            command=self._visualizar_documento
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="📥 Download",
            command=self._download_documento
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="🗑️ Excluir",
            command=self._excluir_documento
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="🔄 Atualizar",
            command=self._carregar_documentos
        ).pack(side=tk.LEFT, padx=5)

        # Label de estatísticas
        self.stats_label = ttk.Label(
            btn_frame,
            text="Total: 0 | 🔴 Vencidos: 0 | 🟡 Vencendo: 0 | 🟢 OK: 0",
            font=("Arial", 9, "bold")
        )
        self.stats_label.pack(side=tk.RIGHT, padx=10)

        # TreeView de documentos
        tree_frame = ttk.Frame(documentos_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # TreeView
        self.documentos_tree = ttk.Treeview(
            tree_frame,
            columns=("id", "tipo", "nome", "validade", "dias", "status"),
            show="tree headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )

        tree_scroll_y.config(command=self.documentos_tree.yview)
        tree_scroll_x.config(command=self.documentos_tree.xview)

        # Colunas
        self.documentos_tree.heading("#0", text="Status")
        self.documentos_tree.heading("id", text="ID")
        self.documentos_tree.heading("tipo", text="Tipo Documento")
        self.documentos_tree.heading("nome", text="Nome Arquivo")
        self.documentos_tree.heading("validade", text="Validade")
        self.documentos_tree.heading("dias", text="Dias Restantes")
        self.documentos_tree.heading("status", text="Situação")

        # Larguras
        self.documentos_tree.column("#0", width=80, minwidth=80)
        self.documentos_tree.column("id", width=50, minwidth=50)
        self.documentos_tree.column("tipo", width=150, minwidth=150)
        self.documentos_tree.column("nome", width=250, minwidth=200)
        self.documentos_tree.column("validade", width=100, minwidth=100)
        self.documentos_tree.column("dias", width=120, minwidth=100)
        self.documentos_tree.column("status", width=120, minwidth=100)

        self.documentos_tree.pack(fill=tk.BOTH, expand=True)

        # Tags de cores para alertas
        self.documentos_tree.tag_configure("verde", background="#90EE90")     # Verde claro
        self.documentos_tree.tag_configure("amarelo", background="#FFFFE0")   # Amarelo claro
        self.documentos_tree.tag_configure("laranja", background="#FFD580")   # Laranja claro
        self.documentos_tree.tag_configure("vermelho", background="#FFB6C1")  # Vermelho claro
        self.documentos_tree.tag_configure("neutro", background="#E0E0E0")    # Cinza claro

        # Legenda de cores
        legenda_frame = ttk.LabelFrame(documentos_frame, text="📊 Legenda de Alertas", padding=10)
        legenda_frame.pack(fill=tk.X, pady=(10, 0))

        legenda_texto = (
            "🟢 Verde: > 30 dias para vencer  |  "
            "🟡 Amarelo: 15-30 dias  |  "
            "🟠 Laranja: 1-14 dias  |  "
            "🔴 Vermelho: VENCIDO  |  "
            "⚪ Neutro: Sem validade"
        )
        ttk.Label(legenda_frame, text=legenda_texto).pack()

    def _calcular_cor_alerta(self, data_validade_str: str) -> tuple:
        """
        Calcular cor de alerta baseado na data de validade.

        Args:
            data_validade_str: Data em formato string "YYYY-MM-DD"

        Returns:
            tuple: (tag_cor, emoji, texto_status, dias_restantes)
        """
        if not data_validade_str:
            return ("neutro", "⚪", "Sem validade", None)

        try:
            data_val = datetime.strptime(data_validade_str, "%Y-%m-%d").date()
            hoje = date.today()
            dias_restantes = (data_val - hoje).days

            if dias_restantes < 0:
                return ("vermelho", "🔴", f"VENCIDO ({abs(dias_restantes)}d)", dias_restantes)
            elif dias_restantes <= 14:
                return ("laranja", "🟠", f"Vence em {dias_restantes}d", dias_restantes)
            elif dias_restantes <= 30:
                return ("amarelo", "🟡", f"Vence em {dias_restantes}d", dias_restantes)
            else:
                return ("verde", "🟢", f"OK ({dias_restantes}d)", dias_restantes)

        except Exception as e:
            print(f"Erro ao calcular alerta: {e}")
            return ("neutro", "⚪", "Erro", None)

    def _carregar_documentos(self):
        """Carregar documentos do colaborador via API"""
        if not self.colaborador_selecionado:
            messagebox.showwarning(
                "Aviso",
                "Selecione um colaborador primeiro"
            )
            return

        # Executar em thread separada
        thread = threading.Thread(
            target=self._carregar_documentos_thread,
            daemon=True
        )
        thread.start()

    def _carregar_documentos_thread(self):
        """Thread para carregar documentos"""
        try:
            colaborador_id = self.colaborador_selecionado["id"]

            response = requests.get(
                f"{API_BASE_URL}/colaboradores/{colaborador_id}/documentos",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.window.after(0, self._on_documentos_carregados, data)
            else:
                erro = response.json().get("detail", "Erro ao carregar documentos")
                self.window.after(0, self._on_documentos_erro, erro)

        except requests.Timeout:
            self.window.after(0, self._on_documentos_erro, "Timeout ao carregar documentos")
        except Exception as e:
            self.window.after(0, self._on_documentos_erro, str(e))

    def _on_documentos_carregados(self, data: Dict):
        """Callback após carregar documentos"""
        # Limpar tree
        for item in self.documentos_tree.get_children():
            self.documentos_tree.delete(item)

        # Preencher tree
        for doc in data.get("items", []):
            tag_cor, emoji, status_texto, dias = self._calcular_cor_alerta(
                doc.get("data_validade")
            )

            # Formatar validade
            validade_fmt = "Sem validade"
            if doc.get("data_validade"):
                try:
                    data_val = datetime.strptime(doc["data_validade"], "%Y-%m-%d")
                    validade_fmt = data_val.strftime("%d/%m/%Y")
                except:
                    pass

            # Inserir no tree
            self.documentos_tree.insert(
                "",
                tk.END,
                text=emoji,
                values=(
                    doc["id"],
                    doc["tipo_documento"],
                    doc["nome_arquivo"],
                    validade_fmt,
                    dias if dias is not None else "N/A",
                    status_texto
                ),
                tags=(tag_cor,)
            )

        # Atualizar estatísticas
        total = data.get("total", 0)
        vencidos = data.get("total_vencidos", 0)
        vencendo = data.get("total_vencendo", 0)
        ok = data.get("total_ok", 0)

        self.stats_label.config(
            text=f"Total: {total} | 🔴 Vencidos: {vencidos} | 🟡 Vencendo: {vencendo} | 🟢 OK: {ok}"
        )

    def _on_documentos_erro(self, mensagem: str):
        """Callback em caso de erro ao carregar documentos"""
        messagebox.showerror("Erro", f"Erro ao carregar documentos:\n{mensagem}")

    def _adicionar_documento(self):
        """Abrir dialog para adicionar documento"""
        if not self.colaborador_selecionado:
            messagebox.showwarning(
                "Aviso",
                "Selecione um colaborador primeiro"
            )
            return

        # Criar dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("Adicionar Documento")
        dialog.geometry("500x450")
        dialog.transient(self.window)
        dialog.grab_set()

        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (450 // 2)
        dialog.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tipo de documento
        ttk.Label(main_frame, text="Tipo de Documento:").grid(row=0, column=0, sticky=tk.W, pady=5)
        tipo_var = tk.StringVar()
        tipo_combo = ttk.Combobox(
            main_frame,
            textvariable=tipo_var,
            values=[
                "RG", "CPF", "CNH", "Título de Eleitor", "Carteira de Trabalho",
                "PIS/PASEP", "Certificado", "Diploma", "Certificado de Curso",
                "Contrato", "Exame Médico", "Comprovante de Residência"
            ],
            state="readonly"
        )
        tipo_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        tipo_combo.set("RG")

        # Nome do arquivo
        ttk.Label(main_frame, text="Nome do Arquivo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        nome_var = tk.StringVar()
        nome_entry = ttk.Entry(main_frame, textvariable=nome_var, width=40)
        nome_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Arquivo
        ttk.Label(main_frame, text="Arquivo:").grid(row=2, column=0, sticky=tk.W, pady=5)
        arquivo_frame = ttk.Frame(main_frame)
        arquivo_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        arquivo_path_var = tk.StringVar()
        arquivo_entry = ttk.Entry(arquivo_frame, textvariable=arquivo_path_var, state="readonly")
        arquivo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.arquivo_base64 = None

        def selecionar_arquivo():
            filename = filedialog.askopenfilename(
                title="Selecionar Arquivo",
                filetypes=[
                    ("PDF", "*.pd"),
                    ("Imagens", "*.png *.jpg *.jpeg *.bmp *.gi"),
                    ("Todos os arquivos", "*.*")
                ]
            )

            if filename:
                arquivo_path_var.set(filename)
                # Preencher nome automaticamente se vazio
                if not nome_var.get():
                    import os
                    nome_var.set(os.path.basename(filename))

                # Ler arquivo e converter para Base64
                try:
                    with open(filename, "rb") as f:
                        arquivo_bytes = f.read()
                        self.arquivo_base64 = base64.b64encode(arquivo_bytes).decode('utf-8')
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao ler arquivo:\n{e}")
                    arquivo_path_var.set("")
                    self.arquivo_base64 = None

        ttk.Button(
            arquivo_frame,
            text="Selecionar...",
            command=selecionar_arquivo
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Data de validade
        ttk.Label(main_frame, text="Data de Validade:").grid(row=3, column=0, sticky=tk.W, pady=5)
        validade_var = tk.StringVar()
        validade_entry = ttk.Entry(main_frame, textvariable=validade_var, width=40)
        validade_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(main_frame, text="(Formato: DD/MM/AAAA - Opcional)", font=("Arial", 8)).grid(
            row=4, column=1, sticky=tk.W
        )

        # Descrição
        ttk.Label(main_frame, text="Descrição:").grid(row=5, column=0, sticky=tk.W, pady=5)
        descricao_text = tk.Text(main_frame, height=5, width=40)
        descricao_text.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)

        def salvar():
            # Validações
            if not tipo_var.get():
                messagebox.showwarning("Aviso", "Selecione o tipo de documento")
                return

            if not nome_var.get():
                messagebox.showwarning("Aviso", "Informe o nome do arquivo")
                return

            if not self.arquivo_base64:
                messagebox.showwarning("Aviso", "Selecione um arquivo")
                return

            # Converter data de validade
            data_validade = None
            if validade_var.get():
                try:
                    data_obj = datetime.strptime(validade_var.get(), "%d/%m/%Y")
                    data_validade = data_obj.strftime("%Y-%m-%d")
                except:
                    messagebox.showwarning(
                        "Aviso",
                        "Data de validade inválida. Use o formato DD/MM/AAAA"
                    )
                    return

            # Montar dados
            dados = {
                "tipo_documento": tipo_var.get(),
                "nome_arquivo": nome_var.get(),
                "arquivo_base64": self.arquivo_base64,
                "descricao": descricao_text.get("1.0", tk.END).strip() or None,
                "data_validade": data_validade
            }

            dialog.destroy()

            # Upload em thread
            thread = threading.Thread(
                target=self._upload_documento_thread,
                args=(dados,),
                daemon=True
            )
            thread.start()

        ttk.Button(btn_frame, text="💾 Salvar", command=salvar, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cancelar", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)

        main_frame.columnconfigure(1, weight=1)

    def _upload_documento_thread(self, dados: Dict):
        """Thread para upload de documento"""
        try:
            colaborador_id = self.colaborador_selecionado["id"]

            response = requests.post(
                f"{API_BASE_URL}/colaboradores/{colaborador_id}/documentos",
                json=dados,
                headers=self.headers,
                timeout=30  # Upload pode demorar mais
            )

            if response.status_code == 201:
                self.window.after(0, self._on_upload_sucesso)
            else:
                erro = response.json().get("detail", "Erro ao fazer upload")
                self.window.after(0, self._on_upload_erro, erro)

        except requests.Timeout:
            self.window.after(0, self._on_upload_erro, "Timeout ao fazer upload")
        except Exception as e:
            self.window.after(0, self._on_upload_erro, str(e))

    def _on_upload_sucesso(self):
        """Callback após upload com sucesso"""
        messagebox.showinfo("Sucesso", "Documento adicionado com sucesso!")
        self._carregar_documentos()

    def _on_upload_erro(self, mensagem: str):
        """Callback em caso de erro no upload"""
        messagebox.showerror("Erro", f"Erro ao adicionar documento:\n{mensagem}")

    def _visualizar_documento(self):
        """Abrir documento no sistema operacional"""
        selecionado = self.documentos_tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um documento")
            return

        # Fazer download e abrir
        self._download_documento(abrir=True)

    def _download_documento(self, abrir=False):
        """Fazer download de documento"""
        selecionado = self.documentos_tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um documento")
            return

        item = self.documentos_tree.item(selecionado[0])
        documento_id = item["values"][0]
        nome_arquivo = item["values"][2]

        # Executar em thread
        thread = threading.Thread(
            target=self._download_documento_thread,
            args=(documento_id, nome_arquivo, abrir),
            daemon=True
        )
        thread.start()

    def _download_documento_thread(self, documento_id: int, nome_arquivo: str, abrir: bool):
        """Thread para download de documento"""
        try:
            colaborador_id = self.colaborador_selecionado["id"]

            response = requests.get(
                f"{API_BASE_URL}/colaboradores/{colaborador_id}/documentos/{documento_id}/download",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                # Salvar arquivo temporário ou na pasta Downloads
                import tempfile
                import os
                import subprocess
                import platform

                if abrir:
                    # Salvar em temp e abrir
                    temp_dir = tempfile.gettempdir()
                    filepath = os.path.join(temp_dir, nome_arquivo)
                else:
                    # Perguntar onde salvar
                    filepath = filedialog.asksaveasfilename(
                        defaultextension="",
                        initialfile=nome_arquivo,
                        filetypes=[("Todos os arquivos", "*.*")]
                    )

                    if not filepath:
                        return

                # Salvar arquivo
                with open(filepath, "wb") as f:
                    f.write(response.content)

                if abrir:
                    # Abrir arquivo no programa padrão
                    if platform.system() == "Windows":
                        os.startfile(filepath)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", filepath])
                    else:  # Linux
                        subprocess.run(["xdg-open", filepath])

                    self.window.after(0, lambda: messagebox.showinfo(
                        "Sucesso",
                        f"Documento aberto em:\n{filepath}"
                    ))
                else:
                    self.window.after(0, lambda: messagebox.showinfo(
                        "Sucesso",
                        f"Documento salvo em:\n{filepath}"
                    ))
            else:
                erro = response.json().get("detail", "Erro ao baixar documento")
                self.window.after(0, self._on_download_erro, erro)

        except Exception as e:
            self.window.after(0, self._on_download_erro, str(e))

    def _on_download_erro(self, mensagem: str):
        """Callback em caso de erro no download"""
        messagebox.showerror("Erro", f"Erro ao baixar documento:\n{mensagem}")

    def _excluir_documento(self):
        """Excluir documento selecionado"""
        selecionado = self.documentos_tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um documento")
            return

        item = self.documentos_tree.item(selecionado[0])
        documento_id = item["values"][0]
        nome_arquivo = item["values"][2]

        # Confirmar exclusão
        if not messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o documento?\n\n{nome_arquivo}"
        ):
            return

        # Executar em thread
        thread = threading.Thread(
            target=self._excluir_documento_thread,
            args=(documento_id,),
            daemon=True
        )
        thread.start()

    def _excluir_documento_thread(self, documento_id: int):
        """Thread para excluir documento"""
        try:
            colaborador_id = self.colaborador_selecionado["id"]

            response = requests.delete(
                f"{API_BASE_URL}/colaboradores/{colaborador_id}/documentos/{documento_id}",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                self.window.after(0, self._on_exclusao_sucesso)
            else:
                erro = response.json().get("detail", "Erro ao excluir documento")
                self.window.after(0, self._on_exclusao_erro, erro)

        except Exception as e:
            self.window.after(0, self._on_exclusao_erro, str(e))

    def _on_exclusao_sucesso(self):
        """Callback após exclusão com sucesso"""
        messagebox.showinfo("Sucesso", "Documento excluído com sucesso!")
        self._carregar_documentos()

    def _on_exclusao_erro(self, mensagem: str):
        """Callback em caso de erro na exclusão"""
        messagebox.showerror("Erro", f"Erro ao excluir documento:\n{mensagem}")


    def create_aba_estatisticas(self):
        """
        ABA 5: ESTATÍSTICAS

        Resumo: tempo empresa, idade, salário total, histórico.
        TODO: Implementar na TAREFA 6
        """
        stats_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(stats_frame, text="📊 Estatísticas")

        # Label placeholder
        placeholder_label = ttk.Label(
            stats_frame,
            text="📝 Painel de Estatísticas será implementado na TAREFA 6\n\n"
                 "Informações exibidas:\n"
                 "• Tempo de empresa (anos, meses, dias)\n"
                 "• Idade atual\n"
                 "• Salário total (salário + benefícios)\n"
                 "• Histórico de mudanças de cargo/departamento\n"
                 "• Avaliações de desempenho\n"
                 "• Férias (programadas, gozadas, saldo)\n"
                 "• Gráficos de desempenho",
            justify="left",
            font=("Arial", 10)
        )
        placeholder_label.pack(pady=20)

    def create_footer(self, parent):
        """Criar rodapé com botões de ação"""
        footer_frame = ttk.Frame(parent)
        footer_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        # Separador
        ttk.Separator(parent, orient="horizontal").grid(
            row=3, column=0, sticky="ew", pady=5
        )

        # Botões
        ttk.Button(
            footer_frame,
            text="💾 Salvar",
            command=self.salvar_colaborador,
            width=15
        ).pack(side="left", padx=5)

        ttk.Button(
            footer_frame,
            text="🔄 Limpar",
            command=self.limpar_formulario,
            width=15
        ).pack(side="left", padx=5)

        ttk.Button(
            footer_frame,
            text="❌ Fechar",
            command=self.on_closing,
            width=15
        ).pack(side="right", padx=5)

    # ==========================================
    # MÉTODOS DE CARREGAMENTO DE DADOS
    # ==========================================

    def carregar_dados_iniciais(self):
        """Carregar dados iniciais em background"""
        threading.Thread(
            target=self._carregar_dados_thread,
            daemon=True
        ).start()

    def _carregar_dados_thread(self):
        """Thread para carregar colaboradores, cargos e departamentos"""
        try:
            # Carregar colaboradores
            response = requests.get(
                f"{API_BASE_URL}/colaboradores/",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.colaboradores = data.get("items", [])
                self.window.after(0, self.atualizar_tree)
                self.window.after(0, self.atualizar_estatisticas)

            # Carregar cargos
            # URL corrigida - router tem prefix="/colaboradores"
            # f"{API_BASE_URL}/cargos/",  # ANTIGA - causava 404
            response_cargos = requests.get(
                f"{API_BASE_URL}/colaboradores/cargos/",  # CORRETA
                headers=self.headers,
                timeout=10
            )
            if response_cargos.status_code == 200:
                self.cargos_list = response_cargos.json()
                # Popular combobox de cargos
                self.window.after(0, self._popular_combo_cargos)

            # Carregar departamentos
            # URL corrigida - router tem prefix="/colaboradores"
            # f"{API_BASE_URL}/departamentos/",  # ANTIGA - causava 404
            response_dept = requests.get(
                f"{API_BASE_URL}/colaboradores/departamentos/",  # CORRETA
                headers=self.headers,
                timeout=10
            )
            if response_dept.status_code == 200:
                self.departamentos_list = response_dept.json()
                # Popular combobox de departamentos
                self.window.after(0, self._popular_combo_departamentos)

            # Popular combobox de superiores (após carregar colaboradores)
            self.window.after(0, self._popular_combo_superiores)

        except requests.exceptions.RequestException as e:
            self.window.after(0, lambda: messagebox.showerror(
                "Erro",
                f"Erro ao carregar dados: {str(e)}"
            ))

    def atualizar_tree(self):
        """Atualizar TreeView com colaboradores"""
        # Limpar tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Inserir colaboradores
        for colab in self.colaboradores:
            self.tree.insert("", "end", values=(
                colab.get("id", ""),
                colab.get("matricula", ""),
                colab.get("nome_completo", ""),
                colab.get("cpf_formatado", colab.get("cp", "")),
                colab.get("cargo", {}).get("nome", "N/A") if colab.get("cargo") else "N/A",
                colab.get("departamento", {}).get("nome", "N/A") if colab.get("departamento") else "N/A",
                colab.get("status", ""),
                colab.get("data_admissao", "")
            ))

    def atualizar_estatisticas(self):
        """Atualizar label de estatísticas"""
        total = len(self.colaboradores)
        ativos = sum(1 for c in self.colaboradores if c.get("ativo", False))
        inativos = total - ativos

        self.stats_label.config(
            text=f"Total: {total} colaboradores | Ativos: {ativos} | Inativos: {inativos}"
        )

    def _popular_combo_cargos(self):
        """Popular combobox de cargos com dados da API"""
        if not self.cargos_list:
            return

        # Formatar valores: "ID: Nome"
        valores = [
            f"{cargo['id']}: {cargo['nome']}"
            for cargo in self.cargos_list
        ]

        self.cargo_combo['values'] = valores

    def _popular_combo_departamentos(self):
        """Popular combobox de departamentos com dados da API"""
        if not self.departamentos_list:
            return

        # Formatar valores: "ID: Nome"
        valores = [
            f"{depto['id']}: {depto['nome']}"
            for depto in self.departamentos_list
        ]

        self.departamento_combo['values'] = valores

    def _popular_combo_superiores(self):
        """Popular combobox de superiores com colaboradores ativos"""
        if not self.colaboradores:
            return

        # Filtrar apenas colaboradores ativos
        ativos = [
            c for c in self.colaboradores
            if c.get("ativo", False)
        ]

        # Formatar valores: "ID: Nome (Cargo)"
        valores = [
            f"{colab['id']}: {colab['nome_completo']}"
            for colab in ativos
        ]

        self.superior_combo['values'] = valores

    # ==========================================
    # MÉTODOS DE AÇÃO
    # ==========================================

    def filtrar_colaboradores(self):
        """Filtrar colaboradores por busca"""
        search_term = self.search_var.get().lower()

        if not search_term:
            self.atualizar_tree()
            return

        # Filtrar
        filtered = [
            c for c in self.colaboradores
            if search_term in c.get("nome_completo", "").lower()
            or search_term in c.get("matricula", "").lower()
            or search_term in c.get("cp", "").lower()
        ]

        # Atualizar tree com filtrados
        for item in self.tree.get_children():
            self.tree.delete(item)

        for colab in filtered:
            self.tree.insert("", "end", values=(
                colab.get("id", ""),
                colab.get("matricula", ""),
                colab.get("nome_completo", ""),
                colab.get("cpf_formatado", colab.get("cp", "")),
                colab.get("cargo", {}).get("nome", "N/A") if colab.get("cargo") else "N/A",
                colab.get("departamento", {}).get("nome", "N/A") if colab.get("departamento") else "N/A",
                colab.get("status", ""),
                colab.get("data_admissao", "")
            ))

    def limpar_filtros(self):
        """Limpar filtros e recarregar lista completa"""
        self.search_var.set("")
        self.atualizar_tree()

    def on_tree_double_click(self, event):
        """Evento de duplo-clique no TreeView"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            colab_id = item["values"][0]

            # Encontrar colaborador
            colaborador = next(
                (c for c in self.colaboradores if c.get("id") == colab_id),
                None
            )

            if colaborador:
                self.editar_colaborador_obj(colaborador)

    def novo_colaborador(self):
        """Criar novo colaborador"""
        self.modo_edicao = False
        self.colaborador_selecionado = None
        self.limpar_formulario()
        self.notebook.select(1)  # Ir para aba Dados Pessoais
        messagebox.showinfo(
            "Novo Colaborador",
            "Preencha os dados nas abas e clique em Salvar."
        )

    def editar_colaborador(self):
        """Editar colaborador selecionado no TreeView"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um colaborador para editar.")
            return

        item = self.tree.item(selection[0])
        colab_id = item["values"][0]

        colaborador = next(
            (c for c in self.colaboradores if c.get("id") == colab_id),
            None
        )

        if colaborador:
            self.editar_colaborador_obj(colaborador)

    def editar_colaborador_obj(self, colaborador: Dict):
        """Editar objeto colaborador"""
        self.modo_edicao = True
        self.colaborador_selecionado = colaborador

        # Preencher formulário com dados do colaborador
        self.preencher_formulario_edicao(colaborador)

        self.notebook.select(1)  # Ir para aba Dados Pessoais
        messagebox.showinfo(
            "Edição",
            f"Editando: {colaborador.get('nome_completo', 'N/A')}\n\n"
            "Preencha ou altere os dados e clique em Salvar."
        )

    def inativar_colaborador(self):
        """Inativar colaborador selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um colaborador para inativar.")
            return

        item = self.tree.item(selection[0])
        colab_id = item["values"][0]
        colab_nome = item["values"][2]

        if not messagebox.askyesno(
            "Confirmar Inativação",
            f"Deseja inativar o colaborador:\n{colab_nome}?"
        ):
            return

        threading.Thread(
            target=self._inativar_colaborador_thread,
            args=(colab_id,),
            daemon=True
        ).start()

    def _inativar_colaborador_thread(self, colab_id: int):
        """Thread para inativar colaborador"""
        try:
            response = requests.delete(
                f"{API_BASE_URL}/colaboradores/{colab_id}",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                self.window.after(0, lambda: messagebox.showinfo(
                    "Sucesso",
                    "Colaborador inativado com sucesso!"
                ))
                self.window.after(0, self.atualizar_lista)
            else:
                self.window.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro ao inativar: {response.text}"
                ))

        except requests.exceptions.RequestException as e:
            self.window.after(0, lambda: messagebox.showerror(
                "Erro",
                f"Erro na requisição: {str(e)}"
            ))

    def atualizar_lista(self):
        """Recarregar lista de colaboradores"""
        self.carregar_dados_iniciais()

    def salvar_colaborador(self):
        """Salvar colaborador (criar ou atualizar)"""
        # Validar campos obrigatórios da aba Dados Pessoais
        if not self.nome_completo_var.get().strip():
            messagebox.showwarning(
                "Campo Obrigatório",
                "Nome completo é obrigatório!"
            )
            self.notebook.select(1)  # Ir para aba Dados Pessoais
            return

        if not self.cpf_var.get().strip():
            messagebox.showwarning(
                "Campo Obrigatório",
                "CPF é obrigatório!"
            )
            self.notebook.select(1)
            return

        # Validar CPF
        cpf_limpo = ''.join(filter(str.isdigit, self.cpf_var.get()))
        if not self._validar_cpf_algoritmo(cpf_limpo):
            messagebox.showerror(
                "CPF Inválido",
                "O CPF informado é inválido! Corrija antes de salvar."
            )
            self.notebook.select(1)
            return

        # Validar telefone principal
        if self.telefone_principal_var.get():
            tel_limpo = ''.join(
                filter(str.isdigit, self.telefone_principal_var.get())
            )
            if len(tel_limpo) not in [10, 11]:
                messagebox.showwarning(
                    "Telefone Inválido",
                    "Telefone principal deve ter 10 ou 11 dígitos."
                )
                self.notebook.select(1)
                return

        # Validar campos obrigatórios da Aba Dados Profissionais
        campos_obrigatorios = {
            "Matrícula": self.matricula_var.get().strip(),
            "Usuário do Sistema": self.user_id_var.get().strip(),
            "Cargo": self.cargo_id_var.get(),
            "Departamento": self.departamento_id_var.get(),
            "Tipo de Contrato": self.tipo_contrato_var.get(),
            "Data de Admissão": self.data_admissao_var.get().strip(),
            "Salário Base": self.salario_base_var.get().strip(),
        }

        campos_vazios = [
            nome for nome, valor in campos_obrigatorios.items() if not valor
        ]

        if campos_vazios:
            messagebox.showwarning(
                "Dados Profissionais Incompletos",
                "Preencha os campos obrigatórios:\n\n"
                + "\n".join(f"• {campo}" for campo in campos_vazios)
            )
            self.notebook.select(2)  # Ir para aba Dados Profissionais
            return

        # Coletar dados do formulário
        dados = self._coletar_dados_formulario()

        # Salvar via API
        if self.modo_edicao and self.colaborador_selecionado:
            self._atualizar_colaborador(dados)
        else:
            self._criar_colaborador(dados)

    def _coletar_dados_formulario(self) -> Dict:
        """
        Coletar dados de todas as abas do formulário.

        Returns:
            Dicionário com dados para envio à API
        """
        # Limpar CPF e telefones (apenas dígitos)
        cpf_limpo = ''.join(filter(str.isdigit, self.cpf_var.get()))
        tel_principal = ''.join(
            filter(str.isdigit, self.telefone_principal_var.get())
        )
        tel_secundario = ''.join(
            filter(str.isdigit, self.telefone_secundario_var.get())
        ) if self.telefone_secundario_var.get() else None

        # Limpar CEP
        cep_limpo = ''.join(filter(str.isdigit, self.cep_var.get()))

        dados = {
            # Dados pessoais
            "nome_completo": self.nome_completo_var.get().strip(),
            "nome_social": self.nome_social_var.get().strip() or None,
            "cp": cpf_limpo,
            "rg": self.rg_var.get().strip() or None,
            "data_nascimento": self.data_nascimento_var.get().strip() or None,
            "estado_civil": self.estado_civil_var.get() or None,
            "sexo": self.sexo_var.get() or None,
            "nacionalidade": self.nacionalidade_var.get().strip() or "Brasileira",
            "naturalidade": self.naturalidade_var.get().strip() or None,

            # Contato
            "telefone_principal": tel_principal or None,
            "telefone_secundario": tel_secundario,
            "email_pessoal": self.email_pessoal_var.get().strip() or None,
            "email_corporativo": self.email_corporativo_var.get().strip() or None,

            # Endereço
            "cep": cep_limpo or None,
            "logradouro": self.logradouro_var.get().strip() or None,
            "numero": self.numero_var.get().strip() or None,
            "complemento": self.complemento_var.get().strip() or None,
            "bairro": self.bairro_var.get().strip() or None,
            "cidade": self.cidade_var.get().strip() or None,
            "estado": self.estado_var.get() or None,

            # Foto 3x4
            "foto_base64": self.foto_base64,

            # Dados Profissionais
            "matricula": self.matricula_var.get().strip(),
            "user_id": int(self.user_id_var.get()) if self.user_id_var.get().strip() else None,
            "cargo_id": int(self.cargo_id_var.get()) if self.cargo_id_var.get() else None,
            "departamento_id": int(self.departamento_id_var.get()) if self.departamento_id_var.get() else None,
            "superior_direto_id": int(self.superior_id_var.get()) if self.superior_id_var.get() else None,
            "tipo_contrato": self.tipo_contrato_var.get() or None,
            "data_admissao": self.data_admissao_var.get().strip() or None,
            "salario_base": float(self.salario_base_var.get().replace(",", ".")) if self.salario_base_var.get().strip() else None,
            "carga_horaria_semanal": int(self.carga_horaria_semanal_var.get()) if self.carga_horaria_semanal_var.get().strip() else 44,
            "horario_entrada": self.horario_entrada_var.get().strip() or None,
            "horario_saida": self.horario_saida_var.get().strip() or None,
            "horario_almoco_inicio": self.horario_almoco_inicio_var.get().strip() or None,
            "horario_almoco_fim": self.horario_almoco_fim_var.get().strip() or None,
            "vale_transporte": self.vale_transporte_var.get(),
            "vale_refeicao": self.vale_refeicao_var.get(),
            "plano_saude": self.plano_saude_var.get(),
        }

        return dados

    def _criar_colaborador(self, dados: Dict):
        """
        Criar novo colaborador via API em thread separada.

        Args:
            dados: Dicionário com dados do colaborador validados
        """
        # Desabilitar botões durante salvamento
        self.salvar_btn.config(state="disabled")
        self.cancelar_btn.config(state="disabled")

        # Criar thread para não bloquear UI
        threading.Thread(
            target=self._criar_colaborador_thread,
            args=(dados,),
            daemon=True
        ).start()

    def _criar_colaborador_thread(self, dados: Dict):
        """Thread para criar colaborador via POST /colaboradores/"""
        try:
            # Extrair IDs dos combos (formato "ID: Nome")
            if dados.get("cargo_id") and isinstance(dados["cargo_id"], str):
                dados["cargo_id"] = int(dados["cargo_id"].split(':')[0])

            if dados.get("departamento_id") and isinstance(dados["departamento_id"], str):
                dados["departamento_id"] = int(dados["departamento_id"].split(':')[0])

            if dados.get("superior_direto_id") and isinstance(dados["superior_direto_id"], str):
                dados["superior_direto_id"] = int(dados["superior_direto_id"].split(':')[0])

            # Fazer POST para criar colaborador
            response = requests.post(
                f"{API_BASE_URL}/colaboradores/",
                json=dados,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 201:
                # Sucesso!
                colaborador_criado = response.json()

                # Atualizar lista de colaboradores
                self.colaboradores.append(colaborador_criado)

                # Atualizar UI na thread principal
                self.window.after(0, lambda: self._on_criar_sucesso(colaborador_criado))
            else:
                # Erro da API
                error_detail = response.json().get("detail", "Erro desconhecido")
                self.window.after(0, lambda: self._on_criar_erro(error_detail))

        except requests.exceptions.Timeout:
            self.window.after(0, lambda: self._on_criar_erro(
                "Timeout: Servidor demorou muito para responder"
            ))
        except requests.exceptions.ConnectionError:
            self.window.after(0, lambda: self._on_criar_erro(
                "Erro de conexão: Verifique se o backend está rodando"
            ))
        except Exception as e:
            self.window.after(0, lambda: self._on_criar_erro(f"Erro: {str(e)}"))

    def _on_criar_sucesso(self, colaborador: Dict):
        """Callback após criar colaborador com sucesso"""
        # Reabilitar botões
        self.salvar_btn.config(state="normal")
        self.cancelar_btn.config(state="normal")

        # Atualizar tree
        self.atualizar_tree()
        self.atualizar_estatisticas()

        # Atualizar combo de superiores (novo colaborador pode ser superior)
        self._popular_combo_superiores()

        # Limpar formulário
        self.limpar_formulario()

        # Mensagem de sucesso
        messagebox.showinfo(
            "Sucesso! ✅",
            "Colaborador criado com sucesso!\n\n"
            f"Matrícula: {colaborador.get('matricula')}\n"
            f"Nome: {colaborador.get('nome_completo')}\n\n"
            f"ID: {colaborador.get('id')}"
        )

        # Voltar para aba de listagem
        self.notebook.select(0)

    def _on_criar_erro(self, mensagem: str):
        """Callback após erro ao criar colaborador"""
        # Reabilitar botões
        self.salvar_btn.config(state="normal")
        self.cancelar_btn.config(state="normal")

        # Mensagem de erro
        messagebox.showerror(
            "Erro ao Criar Colaborador ❌",
            "Não foi possível criar o colaborador.\n\n"
            f"Detalhes: {mensagem}\n\n"
            "Verifique os dados e tente novamente."
        )

    def _atualizar_colaborador(self, dados: Dict):
        """
        Atualizar colaborador existente via API em thread separada.

        Args:
            dados: Dicionário com dados do colaborador validados
        """
        if not self.colaborador_selecionado:
            messagebox.showerror("Erro", "Nenhum colaborador selecionado!")
            return

        colaborador_id = self.colaborador_selecionado.get("id")

        # Desabilitar botões durante salvamento
        self.salvar_btn.config(state="disabled")
        self.cancelar_btn.config(state="disabled")

        # Criar thread para não bloquear UI
        threading.Thread(
            target=self._atualizar_colaborador_thread,
            args=(colaborador_id, dados),
            daemon=True
        ).start()

    def _atualizar_colaborador_thread(self, colaborador_id: int, dados: Dict):
        """Thread para atualizar colaborador via PUT /colaboradores/{id}"""
        try:
            # Extrair IDs dos combos (formato "ID: Nome")
            if dados.get("cargo_id") and isinstance(dados["cargo_id"], str):
                dados["cargo_id"] = int(dados["cargo_id"].split(':')[0])

            if dados.get("departamento_id") and isinstance(dados["departamento_id"], str):
                dados["departamento_id"] = int(dados["departamento_id"].split(':')[0])

            if dados.get("superior_direto_id") and isinstance(dados["superior_direto_id"], str):
                dados["superior_direto_id"] = int(dados["superior_direto_id"].split(':')[0])

            # Fazer PUT para atualizar colaborador
            response = requests.put(
                f"{API_BASE_URL}/colaboradores/{colaborador_id}",
                json=dados,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                # Sucesso!
                colaborador_atualizado = response.json()

                # Atualizar na lista local
                for i, colab in enumerate(self.colaboradores):
                    if colab.get("id") == colaborador_id:
                        self.colaboradores[i] = colaborador_atualizado
                        break

                # Atualizar UI na thread principal
                self.window.after(
                    0, lambda: self._on_atualizar_sucesso(colaborador_atualizado)
                )
            else:
                # Erro da API
                error_detail = response.json().get("detail", "Erro desconhecido")
                self.window.after(0, lambda: self._on_atualizar_erro(error_detail))

        except requests.exceptions.Timeout:
            self.window.after(0, lambda: self._on_atualizar_erro(
                "Timeout: Servidor demorou muito para responder"
            ))
        except requests.exceptions.ConnectionError:
            self.window.after(0, lambda: self._on_atualizar_erro(
                "Erro de conexão: Verifique se o backend está rodando"
            ))
        except Exception as e:
            self.window.after(0, lambda: self._on_atualizar_erro(f"Erro: {str(e)}"))

    def _on_atualizar_sucesso(self, colaborador: Dict):
        """Callback após atualizar colaborador com sucesso"""
        # Reabilitar botões
        self.salvar_btn.config(state="normal")
        self.cancelar_btn.config(state="normal")

        # Atualizar tree
        self.atualizar_tree()
        self.atualizar_estatisticas()

        # Atualizar combo de superiores
        self._popular_combo_superiores()

        # Limpar formulário e sair do modo edição
        self.limpar_formulario()
        self.modo_edicao = False
        self.colaborador_selecionado = None

        # Mensagem de sucesso
        messagebox.showinfo(
            "Sucesso! ✅",
            "Colaborador atualizado com sucesso!\n\n"
            f"Matrícula: {colaborador.get('matricula')}\n"
            f"Nome: {colaborador.get('nome_completo')}"
        )

        # Voltar para aba de listagem
        self.notebook.select(0)

    def _on_atualizar_erro(self, mensagem: str):
        """Callback após erro ao atualizar colaborador"""
        # Reabilitar botões
        self.salvar_btn.config(state="normal")
        self.cancelar_btn.config(state="normal")

        # Mensagem de erro
        messagebox.showerror(
            "Erro ao Atualizar Colaborador ❌",
            "Não foi possível atualizar o colaborador.\n\n"
            f"Detalhes: {mensagem}\n\n"
            "Verifique os dados e tente novamente."
        )

    def preencher_formulario_edicao(self, colaborador: Dict):
        """
        Preencher formulário com dados do colaborador para edição.

        Args:
            colaborador: Dicionário com dados do colaborador da API
        """
        # Limpar formulário primeiro
        self.limpar_formulario()

        # Preencher aba Dados Pessoais
        self.nome_completo_var.set(colaborador.get("nome_completo", ""))
        self.nome_social_var.set(colaborador.get("nome_social", ""))
        self.cpf_var.set(colaborador.get("cpf_formatado", colaborador.get("cp", "")))
        self.rg_var.set(colaborador.get("rg", ""))
        self.data_nascimento_var.set(colaborador.get("data_nascimento", ""))
        self.estado_civil_var.set(colaborador.get("estado_civil", ""))
        self.sexo_var.set(colaborador.get("sexo", ""))
        self.nacionalidade_var.set(
            colaborador.get("nacionalidade", "Brasileira")
        )
        self.naturalidade_var.set(colaborador.get("naturalidade", ""))

        # Contato
        self.telefone_principal_var.set(
            colaborador.get("telefone_formatado", colaborador.get("telefone_principal", ""))
        )
        self.telefone_secundario_var.set(
            colaborador.get("telefone_secundario", "")
        )
        self.email_pessoal_var.set(colaborador.get("email_pessoal", ""))
        self.email_corporativo_var.set(colaborador.get("email_corporativo", ""))

        # Endereço
        cep = colaborador.get("cep", "")
        if cep and len(cep) == 8:
            self.cep_var.set(f"{cep[:5]}-{cep[5:]}")
        else:
            self.cep_var.set(cep)

        self.logradouro_var.set(colaborador.get("logradouro", ""))
        self.numero_var.set(colaborador.get("numero", ""))
        self.complemento_var.set(colaborador.get("complemento", ""))
        self.bairro_var.set(colaborador.get("bairro", ""))
        self.cidade_var.set(colaborador.get("cidade", ""))
        self.estado_var.set(colaborador.get("estado", ""))

        # Foto 3x4
        foto_base64 = colaborador.get("foto_base64")
        if foto_base64 and self.foto_preview_label:
            try:
                # Decodificar base64
                img_data = base64.b64decode(foto_base64)
                img = Image.open(io.BytesIO(img_data))

                # Thumbnail para preview
                img.thumbnail((120, 160), Image.Resampling.LANCZOS)

                # Converter para PhotoImage
                photo_tk = ImageTk.PhotoImage(img)

                # Atualizar preview
                self.foto_preview_label.config(
                    image=photo_tk, text="", bg="white"
                )
                self.foto_photo_tk = photo_tk
                self.foto_base64 = foto_base64
            except Exception as e:
                print(f"Erro ao carregar foto: {e}")

        # Dados Profissionais
        self.matricula_var.set(colaborador.get("matricula", ""))
        user_id = colaborador.get("user_id")
        self.user_id_var.set(str(user_id) if user_id else "")

        # Cargo - buscar nome para formar "ID: Nome"
        cargo_id = colaborador.get("cargo_id")
        if cargo_id:
            cargo_obj = colaborador.get("cargo")
            if cargo_obj:
                self.cargo_id_var.set(f"{cargo_id}: {cargo_obj.get('nome', '')}")
            else:
                self.cargo_id_var.set(str(cargo_id))
        else:
            self.cargo_id_var.set("")

        # Departamento - buscar nome para formar "ID: Nome"
        departamento_id = colaborador.get("departamento_id")
        if departamento_id:
            depto_obj = colaborador.get("departamento")
            if depto_obj:
                self.departamento_id_var.set(
                    f"{departamento_id}: {depto_obj.get('nome', '')}"
                )
            else:
                self.departamento_id_var.set(str(departamento_id))
        else:
            self.departamento_id_var.set("")

        # Superior - buscar nome para formar "ID: Nome"
        superior_id = colaborador.get("superior_direto_id")
        if superior_id:
            # Buscar colaborador na lista
            superior = next(
                (c for c in self.colaboradores if c.get("id") == superior_id),
                None
            )
            if superior:
                self.superior_id_var.set(
                    f"{superior_id}: {superior.get('nome_completo', '')}"
                )
            else:
                self.superior_id_var.set(str(superior_id))
        else:
            self.superior_id_var.set("")

        self.tipo_contrato_var.set(colaborador.get("tipo_contrato", ""))
        self.data_admissao_var.set(colaborador.get("data_admissao", ""))

        salario = colaborador.get("salario_base")
        self.salario_base_var.set(str(salario) if salario else "")

        carga = colaborador.get("carga_horaria_semanal", 44)
        self.carga_horaria_semanal_var.set(str(carga))

        self.horario_entrada_var.set(colaborador.get("horario_entrada", ""))
        self.horario_saida_var.set(colaborador.get("horario_saida", ""))
        self.horario_almoco_inicio_var.set(
            colaborador.get("horario_almoco_inicio", "")
        )
        self.horario_almoco_fim_var.set(
            colaborador.get("horario_almoco_fim", "")
        )

        self.vale_transporte_var.set(colaborador.get("vale_transporte", False))
        self.vale_refeicao_var.set(colaborador.get("vale_refeicao", False))
        self.plano_saude_var.set(colaborador.get("plano_saude", False))

    def limpar_formulario(self):
        """Limpar todos os campos do formulário"""
        # Aba Dados Pessoais
        self.nome_completo_var.set("")
        self.nome_social_var.set("")
        self.cpf_var.set("")
        self.rg_var.set("")
        self.data_nascimento_var.set("")
        self.estado_civil_var.set("")
        self.sexo_var.set("")
        self.nacionalidade_var.set("Brasileira")
        self.naturalidade_var.set("")

        # Contato
        self.telefone_principal_var.set("")
        self.telefone_secundario_var.set("")
        self.email_pessoal_var.set("")
        self.email_corporativo_var.set("")

        # Endereço
        self.cep_var.set("")
        self.logradouro_var.set("")
        self.numero_var.set("")
        self.complemento_var.set("")
        self.bairro_var.set("")
        self.cidade_var.set("")
        self.estado_var.set("")

        # Limpar foto
        self.foto_base64 = None
        if self.foto_preview_label:
            self.foto_preview_label.config(
                image="", text="SEM\nFOTO", bg="#f0f0f0"
            )
        self.foto_photo_tk = None

        # Limpar status labels
        self.cpf_status_label.config(text="", foreground="gray")
        self.tel_status_label.config(text="", foreground="gray")
        self.cep_status_label.config(text="", foreground="gray")

        # Dados Profissionais
        self.matricula_var.set("")
        self.user_id_var.set("")
        self.cargo_id_var.set("")
        self.departamento_id_var.set("")
        self.superior_id_var.set("")
        self.tipo_contrato_var.set("")
        self.data_admissao_var.set("")
        self.salario_base_var.set("")
        self.carga_horaria_semanal_var.set("44")
        self.horario_entrada_var.set("08:00")
        self.horario_saida_var.set("17:00")
        self.horario_almoco_inicio_var.set("12:00")
        self.horario_almoco_fim_var.set("13:00")
        self.vale_transporte_var.set(False)
        self.vale_refeicao_var.set(False)
        self.plano_saude_var.set(False)

        # Reset variáveis de controle
        self.colaborador_selecionado = None
        self.modo_edicao = False

    def criar_cargo(self):
        """Dialog para criar novo cargo"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Criar Novo Cargo")
        dialog.geometry("400x200")
        dialog.transient(self.window)
        dialog.grab_set()

        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 100
        dialog.geometry(f"400x200+{x}+{y}")

        # Campos
        ttk.Label(dialog, text="Nome do Cargo:").pack(pady=(20, 5))
        nome_var = tk.StringVar()
        nome_entry = ttk.Entry(dialog, textvariable=nome_var, width=30)
        nome_entry.pack(pady=5)

        ttk.Label(dialog, text="Descrição:").pack(pady=(10, 5))
        descricao_var = tk.StringVar()
        descricao_entry = ttk.Entry(dialog, textvariable=descricao_var, width=30)
        descricao_entry.pack(pady=5)

        def salvar():
            nome = nome_var.get().strip()
            if not nome:
                messagebox.showwarning("Atenção", "Nome do cargo é obrigatório!")
                return

            # Desabilitar campos durante salvamento
            nome_entry.config(state="disabled")
            descricao_entry.config(state="disabled")
            salvar_btn.config(state="disabled")

            # Dados para API
            dados = {
                "nome": nome,
                "descricao": descricao_var.get().strip() or None
            }

            # Iniciar thread para salvar
            threading.Thread(
                target=self._criar_cargo_thread,
                args=(dados, dialog, nome_entry, descricao_entry, salvar_btn),
                daemon=True
            ).start()

        salvar_btn = ttk.Button(dialog, text="Salvar", command=salvar)
        salvar_btn.pack(pady=15)

    def _criar_cargo_thread(self, dados: Dict, dialog, nome_entry, descricao_entry, salvar_btn):
        """Thread para criar cargo via API"""
        try:
            # URL corrigida - router tem prefix="/colaboradores"
            # f"{API_BASE_URL}/cargos/",  # ANTIGA - causava 404
            response = requests.post(
                f"{API_BASE_URL}/colaboradores/cargos/",  # CORRETA
                json=dados,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 201:
                cargo_criado = response.json()
                self.window.after(0, lambda: self._on_criar_cargo_sucesso(cargo_criado, dialog))
            else:
                error_detail = response.json().get("detail", "Erro desconhecido")
                self.window.after(0, lambda: self._on_criar_cargo_erro(
                    error_detail, dialog, nome_entry, descricao_entry, salvar_btn
                ))

        except requests.exceptions.Timeout:
            self.window.after(0, lambda: self._on_criar_cargo_erro(
                "Timeout: Servidor demorou muito para responder",
                dialog, nome_entry, descricao_entry, salvar_btn
            ))
        except requests.exceptions.ConnectionError:
            self.window.after(0, lambda: self._on_criar_cargo_erro(
                "Erro de conexão: Verifique se o servidor está rodando",
                dialog, nome_entry, descricao_entry, salvar_btn
            ))
        except Exception as e:
            self.window.after(0, lambda: self._on_criar_cargo_erro(
                f"Erro inesperado: {str(e)}",
                dialog, nome_entry, descricao_entry, salvar_btn
            ))

    def _on_criar_cargo_sucesso(self, cargo: Dict, dialog):
        """Callback de sucesso ao criar cargo"""
        # Recarregar lista de cargos
        threading.Thread(target=self._carregar_cargos_thread, daemon=True).start()

        # Fechar dialog
        dialog.destroy()

        # Mensagem de sucesso
        messagebox.showinfo(
            "Sucesso",
            "Cargo criado com sucesso!\n\n"
            f"Nome: {cargo.get('nome')}\n"
            f"ID: {cargo.get('id')}"
        )

    def _on_criar_cargo_erro(self, mensagem: str, dialog, nome_entry, descricao_entry, salvar_btn):
        """Callback de erro ao criar cargo"""
        # Reabilitar campos
        nome_entry.config(state="normal")
        descricao_entry.config(state="normal")
        salvar_btn.config(state="normal")

        # Mensagem de erro
        messagebox.showerror("Erro ao Criar Cargo", mensagem)

    def criar_departamento(self):
        """Dialog para criar novo departamento"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Criar Novo Departamento")
        dialog.geometry("400x200")
        dialog.transient(self.window)
        dialog.grab_set()

        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 100
        dialog.geometry(f"400x200+{x}+{y}")

        # Campos
        ttk.Label(dialog, text="Nome do Departamento:").pack(pady=(20, 5))
        nome_var = tk.StringVar()
        nome_entry = ttk.Entry(dialog, textvariable=nome_var, width=30)
        nome_entry.pack(pady=5)

        ttk.Label(dialog, text="Descrição:").pack(pady=(10, 5))
        descricao_var = tk.StringVar()
        descricao_entry = ttk.Entry(dialog, textvariable=descricao_var, width=30)
        descricao_entry.pack(pady=5)

        def salvar():
            nome = nome_var.get().strip()
            if not nome:
                messagebox.showwarning(
                    "Atenção", "Nome do departamento é obrigatório!"
                )
                return

            # Desabilitar campos durante salvamento
            nome_entry.config(state="disabled")
            descricao_entry.config(state="disabled")
            salvar_btn.config(state="disabled")

            # Dados para API
            dados = {
                "nome": nome,
                "descricao": descricao_var.get().strip() or None
            }

            # Iniciar thread para salvar
            threading.Thread(
                target=self._criar_departamento_thread,
                args=(dados, dialog, nome_entry, descricao_entry, salvar_btn),
                daemon=True
            ).start()

        salvar_btn = ttk.Button(dialog, text="Salvar", command=salvar)
        salvar_btn.pack(pady=15)

    def _criar_departamento_thread(self, dados: Dict, dialog, nome_entry, descricao_entry, salvar_btn):
        """Thread para criar departamento via API"""
        try:
            # URL corrigida - router tem prefix="/colaboradores"
            # f"{API_BASE_URL}/departamentos/",  # ANTIGA - causava 404
            response = requests.post(
                f"{API_BASE_URL}/colaboradores/departamentos/",  # CORRETA
                json=dados,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 201:
                departamento_criado = response.json()
                self.window.after(0, lambda: self._on_criar_departamento_sucesso(departamento_criado, dialog))
            else:
                error_detail = response.json().get("detail", "Erro desconhecido")
                self.window.after(0, lambda: self._on_criar_departamento_erro(
                    error_detail, dialog, nome_entry, descricao_entry, salvar_btn
                ))

        except requests.exceptions.Timeout:
            self.window.after(0, lambda: self._on_criar_departamento_erro(
                "Timeout: Servidor demorou muito para responder",
                dialog, nome_entry, descricao_entry, salvar_btn
            ))
        except requests.exceptions.ConnectionError:
            self.window.after(0, lambda: self._on_criar_departamento_erro(
                "Erro de conexão: Verifique se o servidor está rodando",
                dialog, nome_entry, descricao_entry, salvar_btn
            ))
        except Exception as e:
            self.window.after(0, lambda: self._on_criar_departamento_erro(
                f"Erro inesperado: {str(e)}",
                dialog, nome_entry, descricao_entry, salvar_btn
            ))

    def _on_criar_departamento_sucesso(self, departamento: Dict, dialog):
        """Callback de sucesso ao criar departamento"""
        # Recarregar lista de departamentos
        threading.Thread(target=self._carregar_departamentos_thread, daemon=True).start()

        # Fechar dialog
        dialog.destroy()

        # Mensagem de sucesso
        messagebox.showinfo(
            "Sucesso",
            "Departamento criado com sucesso!\n\n"
            f"Nome: {departamento.get('nome')}\n"
            f"ID: {departamento.get('id')}"
        )

    def _on_criar_departamento_erro(self, mensagem: str, dialog, nome_entry, descricao_entry, salvar_btn):
        """Callback de erro ao criar departamento"""
        # Reabilitar campos
        nome_entry.config(state="normal")
        descricao_entry.config(state="normal")
        salvar_btn.config(state="normal")

        # Mensagem de erro
        messagebox.showerror("Erro ao Criar Departamento", mensagem)

    def on_closing(self):
        """Evento ao fechar janela"""
        if messagebox.askokcancel("Sair", "Deseja fechar a janela de colaboradores?"):
            self.window.destroy()

    # ==========================================
    # MÉTODOS DE VALIDAÇÃO - ABA DADOS PESSOAIS
    # ==========================================

    def validar_cpf_real_time(self, *args):
        """Validar CPF em tempo real"""
        cpf = self.cpf_var.get()

        if not cpf:
            self.cpf_status_label.config(text="", foreground="gray")
            return

        # Remover formatação
        cpf_limpo = ''.join(filter(str.isdigit, cpf))

        if len(cpf_limpo) < 11:
            self.cpf_status_label.config(text="⏳ Digitando...", foreground="gray")
            return

        if len(cpf_limpo) > 11:
            self.cpf_status_label.config(text="❌ CPF inválido", foreground="red")
            return

        # Validar CPF
        if self._validar_cpf_algoritmo(cpf_limpo):
            self.cpf_status_label.config(text="✅ CPF válido", foreground="green")
            # Formatar CPF
            cpf_formatado = (
                f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
            )
            if self.cpf_var.get() != cpf_formatado:
                self.cpf_var.set(cpf_formatado)
        else:
            self.cpf_status_label.config(text="❌ CPF inválido", foreground="red")

    def _validar_cpf_algoritmo(self, cpf: str) -> bool:
        """
        Validar CPF usando algoritmo oficial.

        Args:
            cpf: CPF apenas dígitos (11 caracteres)

        Returns:
            True se CPF válido, False caso contrário
        """
        if len(cpf) != 11:
            return False

        # Verificar se não é sequência repetida
        if cpf == cpf[0] * 11:
            return False

        # Validar dígitos verificadores
        def calcular_digito(cpf_parcial):
            soma = sum(
                int(cpf_parcial[i]) * (len(cpf_parcial) + 1 - i)
                for i in range(len(cpf_parcial))
            )
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)

        if cpf[9] != calcular_digito(cpf[:9]):
            return False

        if cpf[10] != calcular_digito(cpf[:10]):
            return False

        return True

    def validar_telefone_real_time(self, *args):
        """Validar telefone em tempo real"""
        telefone = self.telefone_principal_var.get()

        if not telefone:
            self.tel_status_label.config(text="", foreground="gray")
            return

        # Remover formatação
        tel_limpo = ''.join(filter(str.isdigit, telefone))

        if len(tel_limpo) < 10:
            self.tel_status_label.config(
                text="⏳ Digitando...", foreground="gray"
            )
            return

        if len(tel_limpo) in [10, 11]:
            self.tel_status_label.config(
                text="✅ Telefone válido", foreground="green"
            )
            # Formatar telefone
            if len(tel_limpo) == 11:
                tel_formatado = (
                    f"({tel_limpo[:2]}) {tel_limpo[2:7]}-{tel_limpo[7:]}"
                )
            else:
                tel_formatado = (
                    f"({tel_limpo[:2]}) {tel_limpo[2:6]}-{tel_limpo[6:]}"
                )

            if self.telefone_principal_var.get() != tel_formatado:
                self.telefone_principal_var.set(tel_formatado)
        else:
            self.tel_status_label.config(
                text="❌ Telefone inválido", foreground="red"
            )

    def buscar_cep(self):
        """Buscar endereço por CEP usando API ViaCEP"""
        cep = self.cep_var.get()
        cep_limpo = ''.join(filter(str.isdigit, cep))

        if len(cep_limpo) != 8:
            messagebox.showwarning(
                "CEP Inválido",
                "Digite um CEP válido com 8 dígitos."
            )
            return

        self.cep_status_label.config(text="🔄 Buscando...", foreground="blue")

        # Thread para buscar CEP
        threading.Thread(
            target=self._buscar_cep_thread,
            args=(cep_limpo,),
            daemon=True
        ).start()

    def _buscar_cep_thread(self, cep: str):
        """Thread para buscar CEP na API ViaCEP"""
        try:
            response = requests.get(
                f"https://viacep.com.br/ws/{cep}/json/",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                if "erro" in data:
                    self.window.after(0, lambda: self.cep_status_label.config(
                        text="❌ CEP não encontrado", foreground="red"
                    ))
                    return

                # Preencher campos
                self.window.after(0, lambda: self._preencher_endereco(data))
                self.window.after(0, lambda: self.cep_status_label.config(
                    text="✅ CEP encontrado", foreground="green"
                ))
            else:
                self.window.after(0, lambda: self.cep_status_label.config(
                    text="❌ Erro ao buscar", foreground="red"
                ))

        except requests.exceptions.RequestException:
            self.window.after(0, lambda: self.cep_status_label.config(
                text="❌ Erro de conexão", foreground="red"
            ))

    def _preencher_endereco(self, data: Dict):
        """Preencher campos de endereço com dados do CEP"""
        self.logradouro_var.set(data.get("logradouro", ""))
        self.bairro_var.set(data.get("bairro", ""))
        self.cidade_var.set(data.get("localidade", ""))
        self.estado_var.set(data.get("u", ""))

        # Formatar CEP
        cep = data.get("cep", "").replace("-", "")
        if len(cep) == 8:
            self.cep_var.set(f"{cep[:5]}-{cep[5:]}")

    def abrir_dialog_foto(self):
        """Abrir dialog para captura/upload de foto 3x4"""
        try:
            # Criar e abrir dialog
            dialog = FotoDialog(self.window)
            self.window.wait_window(dialog.dialog)

            # Verificar se foto foi capturada
            foto_base64 = dialog.get_foto_base64()
            foto_image = dialog.get_foto_image()

            if foto_base64 and foto_image:
                # Salvar base64
                self.foto_base64 = foto_base64

                # Atualizar preview
                try:
                    if self.foto_preview_label:
                        # Criar thumbnail para preview
                        img_preview = foto_image.copy()
                        img_preview.thumbnail((120, 160), Image.Resampling.LANCZOS)

                        # Converter para PhotoImage
                        photo_tk = ImageTk.PhotoImage(img_preview)

                        # Atualizar label
                        self.foto_preview_label.config(
                            image=photo_tk, text="", bg="white"
                        )

                        # Manter referência para evitar garbage collection
                        self.foto_photo_tk = photo_tk

                        messagebox.showinfo(
                            "✅ Sucesso",
                            "Foto adicionada!\n\nLembre-se de salvar o colaborador."
                        )
                except Exception as e:
                    messagebox.showwarning(
                        "⚠️ Aviso",
                        f"Foto salva, mas erro no preview:\n{str(e)}"
                    )

        except Exception as e:
            messagebox.showerror(
                "❌ Erro",
                f"Erro ao abrir dialog de foto:\n\n{str(e)}"
            )

    def run(self):
        """Iniciar loop principal (se for janela standalone)"""
        if not self.parent:
            self.window.mainloop()


# ==========================================
# TESTE STANDALONE
# ==========================================

if __name__ == "__main__":
    # Teste direto (requer login primeiro)
    print("⚠️ AVISO: Execute via dashboard_principal.py para autenticação automática.")
    print("Iniciando wizard de colaboradores em modo standalone...\n")

    app = ColaboradoresWizard()
    app.run()
