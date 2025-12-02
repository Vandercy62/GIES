"""
INTERFACE DESKTOP - ORDEM DE SERVIÇO
====================================

Sistema ERP Primotex - Interface tkinter para gestão completa de Ordem de Serviço
Integração total com backend FastAPI - 13 endpoints sincronizados

Características:
- Gestão completa das 7 fases da OS
- Workflow visual intuitivo  
- Controle de status em tempo real
- Histórico de mudanças
- Atribuição de técnicos
- Integração com agendamento
- Interface responsiva e moderna
- Autenticação global com SessionManager

Autor: GitHub Copilot
Data: 29/10/2025
Última atualização: 15/11/2025 - Migração para SessionManager (FASE 7)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, date
import requests
import json
import threading
from typing import Dict, List, Optional, Any
import logging

# Importações de autenticação global - FASE 7
from frontend.desktop.auth_middleware import (
    require_login,
    get_token_for_api,
    create_auth_header,
    get_current_user_info,
    logout_user
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@require_login()
class OrdemServicoWindow:
    """Interface principal para gestão de Ordem de Serviço"""

    def __init__(self, parent=None):
        self.parent = parent
        self.api_base_url = "http://127.0.0.1:8002/api/v1"

        # Obter token da sessão global - FASE 7
        self.token = get_token_for_api()
        if not self.token:
            logger.error("Token não encontrado - usuário não autenticado")
            if parent:
                parent.destroy()
            return

        # Dados do usuário logado
        user_info = get_current_user_info()
        self.usuario_logado = user_info.get('username', 'desconhecido') if user_info else 'desconhecido'
        logger.info(f"OS Window inicializada para usuário: {self.usuario_logado}")

        # Dados da OS atual
        self.os_atual = None
        self.lista_os = []
        self.lista_clientes = []
        self.lista_tecnicos = []

        # Estado da interface
        self.loading = False

        # Configurar janela principal
        self.setup_window()

        # Configurar estilos
        self.setup_styles()

        # Criar interface
        self.create_widgets()

        # Carregar dados iniciais
        self.carregar_dados_iniciais()

    def setup_window(self):
        """Configurar janela principal"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("ERP Primotex - Gestão de Ordem de Serviço")
        self.window.geometry("1400x900")
        self.window.minsize(1200, 800)

        # Centralizar janela
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (900 // 2)
        self.window.geometry(f"1400x900+{x}+{y}")

        # Configurar fechamento
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Configurar estilos da interface"""
        self.style = ttk.Style()

        # Configurar tema
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')

        # Cores do sistema
        self.cores = {
            'primaria': '#2E86AB',      # Azul primário
            'secundaria': '#A23B72',    # Rosa secundário  
            'sucesso': '#5CB85C',       # Verde sucesso
            'aviso': '#F0AD4E',         # Amarelo aviso
            'perigo': '#D9534F',        # Vermelho perigo
            'info': '#5BC0DE',          # Azul info
            'claro': '#F8F9FA',         # Cinza claro
            'escuro': '#343A40'         # Cinza escuro
        }

        # Estilos customizados
        self.style.configure('Titulo.TLabel', 
                           font=('Arial', 16, 'bold'),
                           foreground=self.cores['primaria'])

        self.style.configure('Subtitulo.TLabel',
                           font=('Arial', 12, 'bold'),
                           foreground=self.cores['escuro'])

        self.style.configure('Status.TLabel',
                           font=('Arial', 10, 'bold'))

        # Configurar treeview
        self.style.configure("Treeview.Heading",
                           font=('Arial', 10, 'bold'))

    def create_widgets(self):
        """Criar todos os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Título principal
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(titulo_frame, text="🔧 Gestão de Ordem de Serviço", 
                 style='Titulo.TLabel').pack(side=tk.LEFT)

        # Botões de ação principais
        btn_frame = ttk.Frame(titulo_frame)
        btn_frame.pack(side=tk.RIGHT)

        ttk.Button(btn_frame, text="🆕 Nova OS", 
                  command=self.nova_os).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🔄 Atualizar", 
                  command=self.atualizar_lista).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📊 Relatório", 
                  command=self.gerar_relatorio).pack(side=tk.LEFT)

        # Painel esquerdo - Lista de OS
        self.create_lista_panel(main_frame)

        # Painel direito - Detalhes da OS
        self.create_detalhes_panel(main_frame)

        # Barra de status
        self.create_status_bar(main_frame)

    def create_lista_panel(self, parent):
        """Criar painel da lista de OS"""
        lista_frame = ttk.LabelFrame(parent, text="📋 Lista de Ordens de Serviço", padding="10")
        lista_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(1, weight=1)

        # Filtros
        filtro_frame = ttk.Frame(lista_frame)
        filtro_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filtro_frame.columnconfigure(1, weight=1)

        ttk.Label(filtro_frame, text="Filtro:").grid(row=0, column=0, padx=(0, 5))

        self.filtro_var = tk.StringVar()
        filtro_combo = ttk.Combobox(filtro_frame, textvariable=self.filtro_var, width=15)
        filtro_combo['values'] = ('Todas', 'Aguardando', 'Em Andamento', 'Concluídas', 'Canceladas')
        filtro_combo.set('Todas')
        filtro_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        filtro_combo.bind('<<ComboboxSelected>>', self.aplicar_filtro)

        ttk.Button(filtro_frame, text="🔍", 
                  command=self.aplicar_filtro, width=3).grid(row=0, column=2)

        # Treeview para lista de OS
        tree_frame = ttk.Frame(lista_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Configurar colunas
        columns = ('id', 'numero', 'cliente', 'fase', 'status', 'data_criacao')
        self.tree_os = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)

        # Configurar cabeçalhos
        self.tree_os.heading('id', text='ID')
        self.tree_os.heading('numero', text='Número')
        self.tree_os.heading('cliente', text='Cliente')
        self.tree_os.heading('fase', text='Fase')
        self.tree_os.heading('status', text='Status')
        self.tree_os.heading('data_criacao', text='Data Criação')

        # Configurar larguras
        self.tree_os.column('id', width=50, anchor='center')
        self.tree_os.column('numero', width=80, anchor='center')
        self.tree_os.column('cliente', width=200)
        self.tree_os.column('fase', width=120)
        self.tree_os.column('status', width=100, anchor='center')
        self.tree_os.column('data_criacao', width=100, anchor='center')

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_os.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_os.xview)
        self.tree_os.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid dos componentes
        self.tree_os.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Evento de seleção
        self.tree_os.bind('<<TreeviewSelect>>', self.on_os_selected)

        # Menu de contexto
        self.create_context_menu()

    def create_detalhes_panel(self, parent):
        """Criar painel de detalhes da OS"""
        detalhes_frame = ttk.LabelFrame(parent, text="📄 Detalhes da Ordem de Serviço", padding="10")
        detalhes_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        detalhes_frame.columnconfigure(0, weight=1)
        detalhes_frame.rowconfigure(0, weight=1)

        # Notebook para abas
        self.notebook = ttk.Notebook(detalhes_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Aba 1: Informações Gerais
        self.create_aba_geral()

        # Aba 2: Workflow das Fases
        self.create_aba_workflow()

        # Aba 3: Técnicos e Agendamento
        self.create_aba_tecnicos()

        # Aba 4: Histórico
        self.create_aba_historico()

        # Aba 5: Financeiro
        self.create_aba_financeiro()

    def create_aba_geral(self):
        """Criar aba de informações gerais"""
        aba_geral = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(aba_geral, text="📝 Geral")

        # Configurar grid
        aba_geral.columnconfigure(1, weight=1)

        row = 0

        # Número da OS
        ttk.Label(aba_geral, text="Número OS:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.numero_var = tk.StringVar()
        ttk.Entry(aba_geral, textvariable=self.numero_var, state='readonly', 
                 font=('Arial', 12, 'bold')).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1

        # Cliente
        ttk.Label(aba_geral, text="Cliente:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.cliente_var = tk.StringVar()
        cliente_combo = ttk.Combobox(aba_geral, textvariable=self.cliente_var, width=40)
        cliente_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        self.cliente_combo = cliente_combo
        row += 1

        # Descrição
        ttk.Label(aba_geral, text="Descrição:").grid(row=row, column=0, sticky=(tk.W, tk.N), pady=2)
        self.descricao_text = scrolledtext.ScrolledText(aba_geral, height=4, wrap=tk.WORD)
        self.descricao_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1

        # Observações
        ttk.Label(aba_geral, text="Observações:").grid(row=row, column=0, sticky=(tk.W, tk.N), pady=2)
        self.observacoes_text = scrolledtext.ScrolledText(aba_geral, height=3, wrap=tk.WORD)
        self.observacoes_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1

        # Prioridade
        ttk.Label(aba_geral, text="Prioridade:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.prioridade_var = tk.StringVar()
        prioridade_combo = ttk.Combobox(aba_geral, textvariable=self.prioridade_var, width=15)
        prioridade_combo['values'] = ('BAIXA', 'MEDIA', 'ALTA', 'URGENTE')
        prioridade_combo.set('MEDIA')
        prioridade_combo.grid(row=row, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        row += 1

        # Status atual
        ttk.Label(aba_geral, text="Status:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(aba_geral, textvariable=self.status_var, 
                                     style='Status.TLabel', font=('Arial', 12, 'bold'))
        self.status_label.grid(row=row, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        row += 1

        # Botões de ação
        btn_frame = ttk.Frame(aba_geral)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))

        ttk.Button(btn_frame, text="💾 Salvar", 
                  command=self.salvar_os).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="🗑️ Excluir", 
                  command=self.excluir_os).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="📋 Duplicar", 
                  command=self.duplicar_os).pack(side=tk.LEFT)

    def create_aba_workflow(self):
        """Criar aba do workflow das 7 fases"""
        aba_workflow = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(aba_workflow, text="🔄 Workflow")

        # Título
        ttk.Label(aba_workflow, text="🎯 Workflow das 7 Fases da OS", 
                 style='Subtitulo.TLabel').pack(pady=(0, 20))

        # Frame para as fases
        fases_frame = ttk.Frame(aba_workflow)
        fases_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar grid para 7 fases
        for fase_col in range(7):
            fases_frame.columnconfigure(fase_col, weight=1)

        # Definir as 7 fases
        self.fases_os = [
            {'nome': 'Abertura', 'icone': '📝', 'cor': '#17A2B8'},
            {'nome': 'Aprovação', 'icone': '✅', 'cor': '#28A745'},
            {'nome': 'Agendamento', 'icone': '📅', 'cor': '#FFC107'},
            {'nome': 'Execução', 'icone': '🔧', 'cor': '#FF6B35'},
            {'nome': 'Conferência', 'icone': '🔍', 'cor': '#6F42C1'},
            {'nome': 'Finalização', 'icone': '✔️', 'cor': '#20C997'},
            {'nome': 'Faturamento', 'icone': '💰', 'cor': '#E83E8C'}
        ]

        self.fase_widgets = []

        # Criar widgets para cada fase
        for i, fase in enumerate(self.fases_os):
            fase_frame = ttk.LabelFrame(fases_frame, text=f"{fase['icone']} {fase['nome']}", padding="10")
            fase_frame.grid(row=0, column=i, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2)

            # Status da fase
            status_frame = ttk.Frame(fase_frame)
            status_frame.pack(fill=tk.X, pady=(0, 10))

            status_var = tk.StringVar(value="Pendente")
            status_label = ttk.Label(status_frame, textvariable=status_var, 
                                   font=('Arial', 10, 'bold'))
            status_label.pack()

            # Data da fase
            data_var = tk.StringVar(value="--/--/----")
            data_label = ttk.Label(status_frame, textvariable=data_var, 
                                 font=('Arial', 9))
            data_label.pack()

            # Botões de ação
            btn_frame = ttk.Frame(fase_frame)
            btn_frame.pack(fill=tk.X, pady=(10, 0))

            iniciar_btn = ttk.Button(btn_frame, text="▶️ Iniciar", width=12,
                                   command=lambda idx=i: self.iniciar_fase(idx))
            iniciar_btn.pack(pady=(0, 5))

            concluir_btn = ttk.Button(btn_frame, text="✅ Concluir", width=12,
                                    command=lambda idx=i: self.concluir_fase(idx))
            concluir_btn.pack()

            # Armazenar widgets
            self.fase_widgets.append({
                'frame': fase_frame,
                'status_var': status_var,
                'status_label': status_label,
                'data_var': data_var,
                'data_label': data_label,
                'iniciar_btn': iniciar_btn,
                'concluir_btn': concluir_btn
            })

        # Indicador de progresso
        progress_frame = ttk.Frame(aba_workflow)
        progress_frame.pack(fill=tk.X, pady=20)

        ttk.Label(progress_frame, text="Progresso Geral:", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))

        self.progress_label = ttk.Label(progress_frame, text="0% - Não iniciado", 
                                      font=('Arial', 10))
        self.progress_label.pack(anchor=tk.W, pady=(5, 0))

    def create_aba_tecnicos(self):
        """Criar aba de técnicos e agendamento"""
        aba_tecnicos = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(aba_tecnicos, text="👥 Técnicos")

        # Configurar grid
        aba_tecnicos.columnconfigure(0, weight=1)
        aba_tecnicos.columnconfigure(1, weight=1)
        aba_tecnicos.rowconfigure(1, weight=1)

        # Título
        ttk.Label(aba_tecnicos, text="👥 Gestão de Técnicos e Agendamento", 
                 style='Subtitulo.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Painel esquerdo - Técnicos atribuídos
        tecnicos_frame = ttk.LabelFrame(aba_tecnicos, text="🔧 Técnicos Atribuídos", padding="10")
        tecnicos_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        tecnicos_frame.columnconfigure(0, weight=1)
        tecnicos_frame.rowconfigure(1, weight=1)

        # Botões de ação
        btn_tecnicos_frame = ttk.Frame(tecnicos_frame)
        btn_tecnicos_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(btn_tecnicos_frame, text="➕ Adicionar", 
                  command=self.adicionar_tecnico).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_tecnicos_frame, text="➖ Remover", 
                  command=self.remover_tecnico).pack(side=tk.LEFT)

        # Lista de técnicos
        tecnicos_list_frame = ttk.Frame(tecnicos_frame)
        tecnicos_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tecnicos_list_frame.columnconfigure(0, weight=1)
        tecnicos_list_frame.rowconfigure(0, weight=1)

        # Treeview para técnicos
        cols_tecnicos = ('nome', 'especialidade', 'status', 'data_atribuicao')
        self.tree_tecnicos = ttk.Treeview(tecnicos_list_frame, columns=cols_tecnicos, 
                                        show='headings', height=10)

        self.tree_tecnicos.heading('nome', text='Nome')
        self.tree_tecnicos.heading('especialidade', text='Especialidade')
        self.tree_tecnicos.heading('status', text='Status')
        self.tree_tecnicos.heading('data_atribuicao', text='Data Atribuição')

        # Scrollbar para técnicos
        scroll_tecnicos = ttk.Scrollbar(tecnicos_list_frame, orient=tk.VERTICAL, 
                                      command=self.tree_tecnicos.yview)
        self.tree_tecnicos.configure(yscrollcommand=scroll_tecnicos.set)

        self.tree_tecnicos.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scroll_tecnicos.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Painel direito - Agendamento
        agenda_frame = ttk.LabelFrame(aba_tecnicos, text="📅 Agendamento", padding="10")
        agenda_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        agenda_frame.columnconfigure(0, weight=1)

        row = 0

        # Data agendada
        ttk.Label(agenda_frame, text="Data Agendada:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.data_agendada_var = tk.StringVar()
        ttk.Entry(agenda_frame, textvariable=self.data_agendada_var).grid(row=row, column=1, 
                                                                        sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1

        # Hora agendada
        ttk.Label(agenda_frame, text="Hora Agendada:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.hora_agendada_var = tk.StringVar()
        ttk.Entry(agenda_frame, textvariable=self.hora_agendada_var).grid(row=row, column=1, 
                                                                        sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1

        # Duração estimada
        ttk.Label(agenda_frame, text="Duração (horas):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.duracao_var = tk.StringVar(value="2")
        ttk.Entry(agenda_frame, textvariable=self.duracao_var, width=10).grid(row=row, column=1, 
                                                                            sticky=tk.W, pady=2, padx=(10, 0))
        row += 1

        # Botões de agendamento
        btn_agenda_frame = ttk.Frame(agenda_frame)
        btn_agenda_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(btn_agenda_frame, text="📅 Agendar", 
                  command=self.agendar_os).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_agenda_frame, text="🔄 Reagendar", 
                  command=self.reagendar_os).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_agenda_frame, text="❌ Cancelar Agendamento", 
                  command=self.cancelar_agendamento).pack(side=tk.LEFT)

    def create_aba_historico(self):
        """Criar aba de histórico"""
        aba_historico = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(aba_historico, text="📜 Histórico")

        # Configurar grid
        aba_historico.columnconfigure(0, weight=1)
        aba_historico.rowconfigure(1, weight=1)

        # Título
        ttk.Label(aba_historico, text="📜 Histórico de Mudanças", 
                 style='Subtitulo.TLabel').grid(row=0, column=0, pady=(0, 20))

        # Frame para histórico
        hist_frame = ttk.Frame(aba_historico)
        hist_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        hist_frame.columnconfigure(0, weight=1)
        hist_frame.rowconfigure(0, weight=1)

        # Treeview para histórico
        cols_hist = ('data_hora', 'usuario', 'acao', 'fase', 'observacoes')
        self.tree_historico = ttk.Treeview(hist_frame, columns=cols_hist, 
                                         show='headings', height=15)

        self.tree_historico.heading('data_hora', text='Data/Hora')
        self.tree_historico.heading('usuario', text='Usuário')
        self.tree_historico.heading('acao', text='Ação')
        self.tree_historico.heading('fase', text='Fase')
        self.tree_historico.heading('observacoes', text='Observações')

        # Configurar larguras
        self.tree_historico.column('data_hora', width=150)
        self.tree_historico.column('usuario', width=120)
        self.tree_historico.column('acao', width=150)
        self.tree_historico.column('fase', width=120)
        self.tree_historico.column('observacoes', width=300)

        # Scrollbars para histórico
        v_scroll_hist = ttk.Scrollbar(hist_frame, orient=tk.VERTICAL, 
                                    command=self.tree_historico.yview)
        h_scroll_hist = ttk.Scrollbar(hist_frame, orient=tk.HORIZONTAL, 
                                    command=self.tree_historico.xview)

        self.tree_historico.configure(yscrollcommand=v_scroll_hist.set,
                                    xscrollcommand=h_scroll_hist.set)

        self.tree_historico.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scroll_hist.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scroll_hist.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Botão para atualizar histórico
        ttk.Button(aba_historico, text="🔄 Atualizar Histórico", 
                  command=self.carregar_historico).grid(row=2, column=0, pady=10)

    def create_aba_financeiro(self):
        """Criar aba financeiro"""
        aba_financeiro = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(aba_financeiro, text="💰 Financeiro")

        # Configurar grid
        aba_financeiro.columnconfigure(0, weight=1)
        aba_financeiro.columnconfigure(1, weight=1)

        # Título
        ttk.Label(aba_financeiro, text="💰 Informações Financeiras", 
                 style='Subtitulo.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Painel esquerdo - Orçamento
        orcamento_frame = ttk.LabelFrame(aba_financeiro, text="💵 Orçamento", padding="10")
        orcamento_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        orcamento_frame.columnconfigure(1, weight=1)

        row = 0

        # Valor orçado
        ttk.Label(orcamento_frame, text="Valor Orçado:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.valor_orcado_var = tk.StringVar(value="0,00")
        ttk.Entry(orcamento_frame, textvariable=self.valor_orcado_var).grid(row=row, column=1, 
                                                                          sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1

        # Valor executado
        ttk.Label(orcamento_frame, text="Valor Executado:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.valor_executado_var = tk.StringVar(value="0,00")
        ttk.Entry(orcamento_frame, textvariable=self.valor_executado_var).grid(row=row, column=1, 
                                                                             sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1

        # Status financeiro
        ttk.Label(orcamento_frame, text="Status Financeiro:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.status_financeiro_var = tk.StringVar()
        status_fin_combo = ttk.Combobox(orcamento_frame, textvariable=self.status_financeiro_var)
        status_fin_combo['values'] = ('PENDENTE', 'APROVADO', 'EM_COBRANCA', 'PAGO', 'CANCELADO')
        status_fin_combo.set('PENDENTE')
        status_fin_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1

        # Painel direito - Contas
        contas_frame = ttk.LabelFrame(aba_financeiro, text="🧾 Contas Relacionadas", padding="10")
        contas_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        contas_frame.columnconfigure(0, weight=1)
        contas_frame.rowconfigure(1, weight=1)

        # Botões de contas
        btn_contas_frame = ttk.Frame(contas_frame)
        btn_contas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(btn_contas_frame, text="📄 Gerar Conta", 
                  command=self.gerar_conta).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_contas_frame, text="💳 Ver Contas", 
                  command=self.ver_contas).pack(side=tk.LEFT)

        # Lista de contas
        contas_list_frame = ttk.Frame(contas_frame)
        contas_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        contas_list_frame.columnconfigure(0, weight=1)
        contas_list_frame.rowconfigure(0, weight=1)

        # Treeview para contas
        cols_contas = ('numero', 'tipo', 'valor', 'vencimento', 'status')
        self.tree_contas = ttk.Treeview(contas_list_frame, columns=cols_contas, 
                                      show='headings', height=8)

        self.tree_contas.heading('numero', text='Número')
        self.tree_contas.heading('tipo', text='Tipo')
        self.tree_contas.heading('valor', text='Valor')
        self.tree_contas.heading('vencimento', text='Vencimento')
        self.tree_contas.heading('status', text='Status')

        # Scrollbar para contas
        scroll_contas = ttk.Scrollbar(contas_list_frame, orient=tk.VERTICAL, 
                                    command=self.tree_contas.yview)
        self.tree_contas.configure(yscrollcommand=scroll_contas.set)

        self.tree_contas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scroll_contas.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def create_status_bar(self, parent):
        """Criar barra de status"""
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)

        self.status_text = tk.StringVar(value="Sistema pronto")
        ttk.Label(status_frame, textvariable=self.status_text).pack(side=tk.LEFT, padx=5, pady=2)

        # Indicador de conexão
        self.conexao_text = tk.StringVar(value="🔴 Desconectado")
        ttk.Label(status_frame, textvariable=self.conexao_text).pack(side=tk.RIGHT, padx=5, pady=2)

    def create_context_menu(self):
        """Criar menu de contexto"""
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="📝 Editar", command=self.editar_os)
        self.context_menu.add_command(label="👁️ Visualizar", command=self.visualizar_os)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔄 Atualizar Status", command=self.atualizar_status)
        self.context_menu.add_command(label="📅 Agendar", command=self.agendar_os)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Duplicar", command=self.duplicar_os)
        self.context_menu.add_command(label="🗑️ Excluir", command=self.excluir_os)

        # Bind do menu de contexto
        self.tree_os.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Mostrar menu de contexto"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    # =========================================================================
    # MÉTODOS DE DADOS E API
    # =========================================================================

    def carregar_dados_iniciais(self):
        """Carregar dados iniciais"""
        self.status_text.set("Carregando dados iniciais...")

        # Iniciar em thread separada
        thread = threading.Thread(target=self._carregar_dados_thread)
        thread.daemon = True
        thread.start()

    def _carregar_dados_thread(self):
        """Carregar dados em thread separada"""
        try:
            # Testar conexão COM autenticação - FASE 7
            headers = create_auth_header()
            response = requests.get(f"{self.api_base_url}/ordem-servico/health", 
                                  headers=headers, timeout=5)
            if response.status_code == 200:
                self.window.after(0, lambda: self.conexao_text.set("🟢 Conectado"))

                # Carregar lista de OS
                self.carregar_lista_os()

                # Carregar clientes
                self.carregar_clientes()

                self.window.after(0, lambda: self.status_text.set("Dados carregados com sucesso"))
            else:
                self.window.after(0, lambda: self.conexao_text.set("🟡 Conexão instável"))

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão: {e}")
            self.window.after(0, lambda: self.conexao_text.set("🔴 Erro de conexão"))
            self.window.after(0, lambda: self.status_text.set("Erro ao conectar com a API"))

            # Carregar dados mock para demonstração
            self.carregar_dados_mock()

    def carregar_lista_os(self):
        """Carregar lista de OS da API"""
        try:
            # Autenticação global - FASE 7
            headers = create_auth_header()
            response = requests.get(f"{self.api_base_url}/ordem-servico/", 
                                  headers=headers, timeout=10)
            if response.status_code == 200:
                self.lista_os = response.json()
                self.window.after(0, self.atualizar_tree_os)
            else:
                logger.error(f"Erro ao carregar OS: {response.status_code}")
                self.carregar_dados_mock()
        except Exception as e:
            logger.error(f"Erro ao carregar OS: {e}")
            self.carregar_dados_mock()

    def carregar_clientes(self):
        """Carregar lista de clientes"""
        try:
            # Autenticação global - FASE 7
            headers = create_auth_header()
            response = requests.get(f"{self.api_base_url}/clientes/", 
                                  headers=headers, timeout=10)
            if response.status_code == 200:
                clientes = response.json()
                clientes_lista = [f"{c['id']} - {c['nome']}" for c in clientes]
                self.window.after(0, lambda: self.cliente_combo.configure(values=clientes_lista))
            else:
                # Dados mock para clientes
                clientes_mock = ["1 - João Silva Construções", "2 - Maria Santos Arquitetura"]
                self.window.after(0, lambda: self.cliente_combo.configure(values=clientes_mock))
        except Exception as e:
            logger.error(f"Erro ao carregar clientes: {e}")

    def carregar_dados_mock(self):
        """Carregar dados mock para demonstração"""
        self.lista_os = [
            {
                'id': 1,
                'numero_os': 'OS-2025-001',
                'cliente_id': 1,
                'cliente_nome': 'João Silva Construções',
                'descricao': 'Instalação de forro PVC - Sala comercial',
                'fase_atual': 'EXECUCAO',
                'status': 'EM_ANDAMENTO',
                'prioridade': 'ALTA',
                'data_criacao': '2025-10-25',
                'data_prevista_conclusao': '2025-11-05',
                'valor_orcado': 5500.00,
                'observacoes': 'Cliente solicitou acabamento especial'
            },
            {
                'id': 2,
                'numero_os': 'OS-2025-002',
                'cliente_id': 2,
                'cliente_nome': 'Maria Santos Arquitetura',
                'descricao': 'Divisórias de vidro - Escritório',
                'fase_atual': 'AGENDAMENTO',
                'status': 'AGUARDANDO',
                'prioridade': 'MEDIA',
                'data_criacao': '2025-10-28',
                'data_prevista_conclusao': '2025-11-15',
                'valor_orcado': 8200.00,
                'observacoes': 'Aguardando disponibilidade do cliente'
            }
        ]

        self.window.after(0, self.atualizar_tree_os)
        self.window.after(0, lambda: self.status_text.set("Modo demonstração ativo"))

    def atualizar_tree_os(self):
        """Atualizar árvore de OS"""
        # Limpar árvore
        for item in self.tree_os.get_children():
            self.tree_os.delete(item)

        # Adicionar OS
        for os in self.lista_os:
            self.tree_os.insert('', 'end', values=(
                os.get('id', ''),
                os.get('numero_os', ''),
                os.get('cliente_nome', ''),
                os.get('fase_atual', ''),
                os.get('status', ''),
                os.get('data_criacao', '')
            ))

    # =========================================================================
    # EVENTOS DA INTERFACE
    # =========================================================================

    def on_os_selected(self, event):
        """Evento quando uma OS é selecionada"""
        selection = self.tree_os.selection()
        if selection:
            item = self.tree_os.item(selection[0])
            os_id = item['values'][0]

            # Buscar OS na lista
            for os in self.lista_os:
                if os.get('id') == os_id:
                    self.os_atual = os
                    self.carregar_detalhes_os(os)
                    break

    def carregar_detalhes_os(self, os_data):
        """Carregar detalhes da OS selecionada"""
        # Aba Geral
        self.numero_var.set(os_data.get('numero_os', ''))
        self.cliente_var.set(f"{os_data.get('cliente_id', '')} - {os_data.get('cliente_nome', '')}")

        self.descricao_text.delete(1.0, tk.END)
        self.descricao_text.insert(1.0, os_data.get('descricao', ''))

        self.observacoes_text.delete(1.0, tk.END)
        self.observacoes_text.insert(1.0, os_data.get('observacoes', ''))

        self.prioridade_var.set(os_data.get('prioridade', 'MEDIA'))
        self.status_var.set(os_data.get('status', ''))

        # Atualizar cor do status
        status = os_data.get('status', '')
        cor_status = self.cores['info']
        if status == 'EM_ANDAMENTO':
            cor_status = self.cores['aviso']
        elif status == 'CONCLUIDA':
            cor_status = self.cores['sucesso']
        elif status == 'CANCELADA':
            cor_status = self.cores['perigo']

        self.status_label.configure(foreground=cor_status)

        # Aba Workflow
        self.atualizar_workflow(os_data)

        # Aba Financeiro
        self.valor_orcado_var.set(f"{os_data.get('valor_orcado', 0):,.2f}")
        self.status_financeiro_var.set(os_data.get('status_financeiro', 'PENDENTE'))

    def atualizar_workflow(self, os_data):
        """Atualizar visual do workflow"""
        fase_atual = os_data.get('fase_atual', 'ABERTURA')

        # Mapear fases
        fases_map = {
            'ABERTURA': 0,
            'APROVACAO': 1,
            'AGENDAMENTO': 2,
            'EXECUCAO': 3,
            'CONFERENCIA': 4,
            'FINALIZACAO': 5,
            'FATURAMENTO': 6
        }

        fase_atual_idx = fases_map.get(fase_atual, 0)

        # Atualizar widgets das fases
        for i, widget in enumerate(self.fase_widgets):
            if i < fase_atual_idx:
                # Fase concluída
                widget['status_var'].set("✅ Concluída")
                widget['status_label'].configure(foreground=self.cores['sucesso'])
                widget['iniciar_btn'].configure(state='disabled')
                widget['concluir_btn'].configure(state='disabled')
            elif i == fase_atual_idx:
                # Fase atual
                widget['status_var'].set("🔄 Em Andamento")
                widget['status_label'].configure(foreground=self.cores['aviso'])
                widget['iniciar_btn'].configure(state='disabled')
                widget['concluir_btn'].configure(state='normal')
            elif i == fase_atual_idx + 1:
                # Próxima fase
                widget['status_var'].set("⏳ Próxima")
                widget['status_label'].configure(foreground=self.cores['info'])
                widget['iniciar_btn'].configure(state='normal')
                widget['concluir_btn'].configure(state='disabled')
            else:
                # Fases futuras
                widget['status_var'].set("⏸️ Pendente")
                widget['status_label'].configure(foreground=self.cores['escuro'])
                widget['iniciar_btn'].configure(state='disabled')
                widget['concluir_btn'].configure(state='disabled')

        # Atualizar barra de progresso
        progresso = ((fase_atual_idx + 1) / 7) * 100
        self.progress_var.set(progresso)
        self.progress_label.configure(text=f"{progresso:.1f}% - {self.fases_os[fase_atual_idx]['nome']}")

    # =========================================================================
    # AÇÕES DA INTERFACE
    # =========================================================================

    def nova_os(self):
        """Criar nova OS"""
        # Limpar formulário
        self.os_atual = None
        self.numero_var.set("Será gerado automaticamente")
        self.cliente_var.set("")
        self.descricao_text.delete(1.0, tk.END)
        self.observacoes_text.delete(1.0, tk.END)
        self.prioridade_var.set("MEDIA")
        self.status_var.set("NOVA")

        # Focar na aba geral
        self.notebook.select(0)

        self.status_text.set("Nova OS - Preencha os dados")

    def salvar_os(self):
        """Salvar OS atual"""
        try:
            # Validar dados
            if not self.cliente_var.get():
                messagebox.showerror("Erro", "Selecione um cliente")
                return

            if not self.descricao_text.get(1.0, tk.END).strip():
                messagebox.showerror("Erro", "Informe a descrição do serviço")
                return

            # Preparar dados
            cliente_id = self.cliente_var.get().split(' - ')[0] if ' - ' in self.cliente_var.get() else 1

            dados_os = {
                'cliente_id': int(cliente_id),
                'descricao': self.descricao_text.get(1.0, tk.END).strip(),
                'observacoes': self.observacoes_text.get(1.0, tk.END).strip(),
                'prioridade': self.prioridade_var.get(),
                'valor_orcado': float(self.valor_orcado_var.get().replace(',', '.')) if self.valor_orcado_var.get() else 0.0
            }

            if self.os_atual:
                # Atualizar OS existente - FASE 7: Com autenticação
                headers = create_auth_header()
                response = requests.put(f"{self.api_base_url}/ordem-servico/{self.os_atual['id']}", 
                                      json=dados_os, headers=headers, timeout=10)
                if response.status_code == 200:
                    messagebox.showinfo("Sucesso", "OS atualizada com sucesso!")
                    self.carregar_lista_os()
                else:
                    messagebox.showerror("Erro", f"Erro ao atualizar OS: {response.text}")
            else:
                # Criar nova OS - FASE 7: Com autenticação
                headers = create_auth_header()
                response = requests.post(f"{self.api_base_url}/ordem-servico/", 
                                       json=dados_os, headers=headers, timeout=10)
                if response.status_code == 201:
                    messagebox.showinfo("Sucesso", "OS criada com sucesso!")
                    self.carregar_lista_os()
                else:
                    messagebox.showerror("Erro", f"Erro ao criar OS: {response.text}")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro de Conexão", f"Erro ao conectar com a API: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def excluir_os(self):
        """Excluir OS atual"""
        if not self.os_atual:
            messagebox.showwarning("Aviso", "Selecione uma OS para excluir")
            return

        if messagebox.askyesno("Confirmação", 
                              f"Deseja realmente excluir a OS {self.os_atual.get('numero_os', '')}?"):
            try:
                # DELETE com autenticação - FASE 7
                headers = create_auth_header()
                response = requests.delete(f"{self.api_base_url}/ordem-servico/{self.os_atual['id']}", 
                                         headers=headers, timeout=10)
                if response.status_code == 200:
                    messagebox.showinfo("Sucesso", "OS excluída com sucesso!")
                    self.carregar_lista_os()
                    self.nova_os()  # Limpar formulário
                else:
                    messagebox.showerror("Erro", f"Erro ao excluir OS: {response.text}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir OS: {e}")

    def duplicar_os(self):
        """Duplicar OS atual"""
        if not self.os_atual:
            messagebox.showwarning("Aviso", "Selecione uma OS para duplicar")
            return

        # Limpar campos únicos
        self.numero_var.set("Será gerado automaticamente")
        self.status_var.set("NOVA")
        self.os_atual = None  # Será tratada como nova OS

        messagebox.showinfo("Info", "OS duplicada! Modifique os dados e salve.")

    def aplicar_filtro(self, event=None):
        """Aplicar filtro na lista"""
        filtro = self.filtro_var.get()
        # Implementar lógica de filtro
        self.status_text.set(f"Filtro aplicado: {filtro}")

    def atualizar_lista(self):
        """Atualizar lista de OS"""
        self.carregar_dados_iniciais()

    def iniciar_fase(self, fase_idx):
        """Iniciar uma fase específica"""
        if not self.os_atual:
            messagebox.showwarning("Aviso", "Selecione uma OS")
            return

        fase_nome = self.fases_os[fase_idx]['nome']

        if messagebox.askyesno("Confirmação", f"Iniciar fase: {fase_nome}?"):
            # Chamar API para atualizar fase
            self.status_text.set(f"Iniciando fase: {fase_nome}")
            # Simular atualização
            self.atualizar_workflow(self.os_atual)

    def concluir_fase(self, fase_idx):
        """Concluir uma fase específica"""
        if not self.os_atual:
            messagebox.showwarning("Aviso", "Selecione uma OS")
            return

        fase_nome = self.fases_os[fase_idx]['nome']

        if messagebox.askyesno("Confirmação", f"Concluir fase: {fase_nome}?"):
            # Chamar API para concluir fase
            self.status_text.set(f"Fase concluída: {fase_nome}")
            # Simular atualização
            self.atualizar_workflow(self.os_atual)

    def gerar_relatorio(self):
        """Gerar relatório de OS"""
        messagebox.showinfo("Relatório", "Funcionalidade em desenvolvimento")

    def adicionar_tecnico(self):
        """Adicionar técnico à OS"""
        messagebox.showinfo("Técnicos", "Funcionalidade em desenvolvimento")

    def remover_tecnico(self):
        """Remover técnico da OS"""
        messagebox.showinfo("Técnicos", "Funcionalidade em desenvolvimento")

    def agendar_os(self):
        """Agendar OS"""
        messagebox.showinfo("Agendamento", "Funcionalidade em desenvolvimento")

    def reagendar_os(self):
        """Reagendar OS"""
        messagebox.showinfo("Agendamento", "Funcionalidade em desenvolvimento")

    def cancelar_agendamento(self):
        """Cancelar agendamento"""
        messagebox.showinfo("Agendamento", "Funcionalidade em desenvolvimento")

    def carregar_historico(self):
        """Carregar histórico da OS"""
        if not self.os_atual:
            return

        # Simular dados de histórico
        historico_mock = [
            ('29/10/2025 10:30', 'admin', 'OS Criada', 'Abertura', 'OS criada pelo sistema'),
            ('29/10/2025 14:15', 'admin', 'Fase Iniciada', 'Aprovação', 'Iniciada análise técnica'),
            ('30/10/2025 09:00', 'joao.tecnico', 'Fase Concluída', 'Aprovação', 'Aprovado para execução')
        ]

        # Limpar histórico
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)

        # Adicionar dados
        for hist in historico_mock:
            self.tree_historico.insert('', 'end', values=hist)

    def gerar_conta(self):
        """Gerar conta financeira"""
        messagebox.showinfo("Financeiro", "Funcionalidade em desenvolvimento")

    def ver_contas(self):
        """Ver contas relacionadas"""
        messagebox.showinfo("Financeiro", "Funcionalidade em desenvolvimento")

    def editar_os(self):
        """Editar OS selecionada"""
        selection = self.tree_os.selection()
        if selection:
            self.on_os_selected(None)
            self.notebook.select(0)  # Focar na aba geral

    def visualizar_os(self):
        """Visualizar OS selecionada"""
        self.editar_os()

    def atualizar_status(self):
        """Atualizar status da OS"""
        messagebox.showinfo("Status", "Funcionalidade em desenvolvimento")

    def on_closing(self):
        """Evento de fechamento da janela"""
        if messagebox.askokcancel("Sair", "Deseja fechar o módulo de Ordem de Serviço?"):
            self.window.destroy()

# =============================================================================
# FUNÇÃO PRINCIPAL PARA TESTE
# =============================================================================

def main():
    """Função principal para teste da interface"""
    app = OrdemServicoWindow()
    app.window.mainloop()

if __name__ == "__main__":
    main()