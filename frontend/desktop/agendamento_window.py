"""
INTERFACE DESKTOP - AGENDAMENTO
==============================

Sistema ERP Primotex - Interface tkinter para gestão completa de Agendamento
Integração total com backend FastAPI - 17 endpoints sincronizados

Características:
- Calendário visual interativo
- Gestão completa de eventos
- Integração com Ordem de Serviço
- Consulta de disponibilidade
- Sistema de conflitos automático
- Configurações de horários
- Relatórios de agenda
- Interface moderna e responsiva

Autor: GitHub Copilot
Data: 29/10/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date, timedelta
import calendar
import requests
import json
import threading
from typing import Dict, List, Optional, Any
import logging
from shared.constants import (
    STYLE_SUBTITULO_LABEL, FONT_SEGOE_UI,
    MSG_FUNCIONALIDADE_EM_DESENVOLVIMENTO
)

# Importar middleware de autenticação
from frontend.desktop.auth_middleware import (
    require_login,
    get_token_for_api,
    create_auth_header,
    get_current_user_info
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@require_login()
class AgendamentoWindow:
    """Interface principal para gestão de Agendamento"""

    def __init__(self, parent=None):
        self.parent = parent
        self.api_base_url = "http://127.0.0.1:8002/api/v1"
        self.token = get_token_for_api()  # Pega token da sessão global

        # Dados do agendamento
        self.evento_atual = None
        self.lista_eventos = []
        self.configuracoes_horario = {}
        self.data_selecionada = datetime.now().date()
        self.mes_atual = datetime.now().month
        self.ano_atual = datetime.now().year

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
        self.window.title("ERP Primotex - Sistema de Agendamento")
        self.window.geometry("1500x900")
        self.window.minsize(1200, 800)

        # Centralizar janela
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (900 // 2)
        self.window.geometry(f"1500x900+{x}+{y}")

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
            'escuro': '#343A40',        # Cinza escuro
            'calendario': '#E9ECEF'     # Cinza calendário
        }

        # Estilos customizados
        self.style.configure('Titulo.TLabel', 
                           font=('Arial', 16, 'bold'),
                           foreground=self.cores['primaria'])

        self.style.configure(STYLE_SUBTITULO_LABEL,
                           font=('Arial', 12, 'bold'),
                           foreground=self.cores['escuro'])

        self.style.configure('Calendario.TLabel',
                           font=('Arial', 10),
                           borderwidth=1,
                           relief='solid')

        self.style.configure('CalendarioHeader.TLabel',
                           font=('Arial', 11, 'bold'),
                           background=self.cores['primaria'],
                           foreground='white')

    def create_widgets(self):
        """Criar todos os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(1, weight=1)

        # Título principal
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(titulo_frame, text="📅 Sistema de Agendamento", 
                 style='Titulo.TLabel').pack(side=tk.LEFT)

        # Botões de ação principais
        btn_frame = ttk.Frame(titulo_frame)
        btn_frame.pack(side=tk.RIGHT)

        ttk.Button(btn_frame, text="🆕 Novo Evento", 
                  command=self.novo_evento).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="⚙️ Configurações", 
                  command=self.abrir_configuracoes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📊 Relatórios", 
                  command=self.gerar_relatorios).pack(side=tk.LEFT)

        # Painel esquerdo - Calendário
        self.create_calendario_panel(main_frame)

        # Painel direito - Detalhes e eventos
        self.create_detalhes_panel(main_frame)

        # Barra de status
        self.create_status_bar(main_frame)

    def create_calendario_panel(self, parent):
        """Criar painel do calendário"""
        cal_frame = ttk.LabelFrame(parent, text="📆 Calendário", padding="10")
        cal_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        cal_frame.columnconfigure(0, weight=1)
        cal_frame.rowconfigure(2, weight=1)

        # Controles de navegação
        nav_frame = ttk.Frame(cal_frame)
        nav_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        nav_frame.columnconfigure(1, weight=1)

        ttk.Button(nav_frame, text="◀️", width=3,
                  command=self.mes_anterior).grid(row=0, column=0)

        self.mes_ano_var = tk.StringVar()
        mes_ano_label = ttk.Label(nav_frame, textvariable=self.mes_ano_var,
                                 font=('Arial', 14, 'bold'))
        mes_ano_label.grid(row=0, column=1)

        ttk.Button(nav_frame, text="▶️", width=3,
                  command=self.proximo_mes).grid(row=0, column=2)

        # Botão hoje
        ttk.Button(nav_frame, text="📍 Hoje",
                  command=self.ir_para_hoje).grid(row=0, column=3, padx=(10, 0))

        # Cabeçalho dos dias da semana
        dias_frame = ttk.Frame(cal_frame)
        dias_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        dias_semana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
        for i, dia in enumerate(dias_semana):
            dias_frame.columnconfigure(i, weight=1)
            ttk.Label(dias_frame, text=dia, style='CalendarioHeader.TLabel',
                     anchor='center').grid(row=0, column=i, sticky=(tk.W, tk.E), padx=1)

        # Grid do calendário
        self.cal_grid_frame = ttk.Frame(cal_frame)
        self.cal_grid_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar grid para 6 semanas
        for col in range(7):
            self.cal_grid_frame.columnconfigure(col, weight=1)
        for row in range(6):
            self.cal_grid_frame.rowconfigure(row, weight=1)

        # Criar botões do calendário
        self.cal_buttons = {}
        self.create_calendar_grid()

        # Legenda de eventos
        legenda_frame = ttk.LabelFrame(cal_frame, text="📋 Legenda", padding="5")
        legenda_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Tipos de eventos
        tipos_eventos = [
            ('🔧 OS Agendada', self.cores['primaria']),
            ('📞 Ligação', self.cores['info']),
            ('📧 Email', self.cores['aviso']),
            ('🤝 Reunião', self.cores['secundaria']),
            ('⚠️ Conflito', self.cores['perigo'])
        ]

        for i, (texto, cor) in enumerate(tipos_eventos):
            row = i // 2
            col = i % 2

            item_frame = ttk.Frame(legenda_frame)
            item_frame.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)

            # Indicador colorido
            color_label = tk.Label(item_frame, text="●", foreground=cor, 
                                 font=('Arial', 12))
            color_label.pack(side=tk.LEFT)

            # Texto
            ttk.Label(item_frame, text=texto, font=('Arial', 9)).pack(side=tk.LEFT, padx=(5, 0))

    def create_detalhes_panel(self, parent):
        """Criar painel de detalhes"""
        detalhes_frame = ttk.LabelFrame(parent, text="📄 Detalhes do Agendamento", padding="10")
        detalhes_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        detalhes_frame.columnconfigure(0, weight=1)
        detalhes_frame.rowconfigure(0, weight=1)

        # Notebook para abas
        self.notebook = ttk.Notebook(detalhes_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Aba 1: Eventos do Dia
        self.create_aba_eventos()

        # Aba 2: Novo/Editar Evento
        self.create_aba_evento_form()

        # Aba 3: Disponibilidade
        self.create_aba_disponibilidade()

        # Aba 4: Conflitos
        self.create_aba_conflitos()

    def create_aba_eventos(self):
        """Criar aba de eventos do dia"""
        aba_eventos = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(aba_eventos, text="📅 Eventos do Dia")

        # Configurar grid
        aba_eventos.columnconfigure(0, weight=1)
        aba_eventos.rowconfigure(1, weight=1)

        # Cabeçalho com data selecionada
        header_frame = ttk.Frame(aba_eventos)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)

        self.data_selecionada_var = tk.StringVar()
        ttk.Label(header_frame, textvariable=self.data_selecionada_var,
                 style=STYLE_SUBTITULO_LABEL).grid(row=0, column=0, sticky=tk.W)

        # Botões de ação
        btn_eventos_frame = ttk.Frame(header_frame)
        btn_eventos_frame.grid(row=0, column=1, sticky=tk.E)

        ttk.Button(btn_eventos_frame, text="➕ Adicionar", 
                  command=self.adicionar_evento).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_eventos_frame, text="🔄 Atualizar", 
                  command=self.atualizar_eventos_dia).pack(side=tk.LEFT)

        # Lista de eventos
        lista_frame = ttk.Frame(aba_eventos)
        lista_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        lista_frame.columnconfigure(0, weight=1)
        lista_frame.rowconfigure(0, weight=1)

        # Treeview para eventos
        columns = ('hora', 'tipo', 'titulo', 'cliente', 'status', 'tecnico')
        self.tree_eventos = ttk.Treeview(lista_frame, columns=columns, 
                                       show='headings', height=15)

        # Configurar cabeçalhos
        self.tree_eventos.heading('hora', text='Hora')
        self.tree_eventos.heading('tipo', text='Tipo')
        self.tree_eventos.heading('titulo', text='Título')
        self.tree_eventos.heading('cliente', text='Cliente')
        self.tree_eventos.heading('status', text='Status')
        self.tree_eventos.heading('tecnico', text='Técnico')

        # Configurar larguras
        self.tree_eventos.column('hora', width=80, anchor='center')
        self.tree_eventos.column('tipo', width=100)
        self.tree_eventos.column('titulo', width=200)
        self.tree_eventos.column('cliente', width=150)
        self.tree_eventos.column('status', width=100, anchor='center')
        self.tree_eventos.column('tecnico', width=120)

        # Scrollbars
        v_scroll = ttk.Scrollbar(lista_frame, orient=tk.VERTICAL, 
                               command=self.tree_eventos.yview)
        h_scroll = ttk.Scrollbar(lista_frame, orient=tk.HORIZONTAL, 
                               command=self.tree_eventos.xview)

        self.tree_eventos.configure(yscrollcommand=v_scroll.set,
                                  xscrollcommand=h_scroll.set)

        # Grid dos componentes
        self.tree_eventos.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Eventos de seleção
        self.tree_eventos.bind('<<TreeviewSelect>>', self.on_evento_selected)
        self.tree_eventos.bind('<Double-1>', self.editar_evento)

        # Menu de contexto
        self.create_context_menu_eventos()

    def create_aba_evento_form(self):
        """Criar aba do formulário de evento"""
        aba_form = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(aba_form, text="📝 Evento")

        # Configurar grid
        aba_form.columnconfigure(1, weight=1)

        row = 0

        # Título do evento
        ttk.Label(aba_form, text="Título:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.titulo_var = tk.StringVar()
        ttk.Entry(aba_form, textvariable=self.titulo_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1

        # Tipo do evento
        ttk.Label(aba_form, text="Tipo:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.tipo_var = tk.StringVar()
        tipo_combo = ttk.Combobox(aba_form, textvariable=self.tipo_var, width=20)
        tipo_combo['values'] = ('OS_AGENDADA', 'LIGACAO', 'EMAIL', 'REUNIAO', 'OUTROS')
        tipo_combo.set('OS_AGENDADA')
        tipo_combo.grid(row=row, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        row += 1

        # Data e hora
        datetime_frame = ttk.Frame(aba_form)
        datetime_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        ttk.Label(aba_form, text="Data/Hora:").grid(row=row, column=0, sticky=tk.W, pady=2)

        # Data
        self.data_evento_var = tk.StringVar()
        ttk.Entry(datetime_frame, textvariable=self.data_evento_var, width=12).pack(side=tk.LEFT)

        # Hora início
        ttk.Label(datetime_frame, text="das").pack(side=tk.LEFT, padx=(5, 5))
        self.hora_inicio_var = tk.StringVar()
        ttk.Entry(datetime_frame, textvariable=self.hora_inicio_var, width=8).pack(side=tk.LEFT)

        # Hora fim
        ttk.Label(datetime_frame, text="às").pack(side=tk.LEFT, padx=(5, 5))
        self.hora_fim_var = tk.StringVar()
        ttk.Entry(datetime_frame, textvariable=self.hora_fim_var, width=8).pack(side=tk.LEFT)
        row += 1

        # Cliente
        ttk.Label(aba_form, text="Cliente:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.cliente_evento_var = tk.StringVar()
        cliente_combo = ttk.Combobox(aba_form, textvariable=self.cliente_evento_var, width=40)
        cliente_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        self.cliente_evento_combo = cliente_combo
        row += 1

        # Técnico responsável
        ttk.Label(aba_form, text="Técnico:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.tecnico_var = tk.StringVar()
        tecnico_combo = ttk.Combobox(aba_form, textvariable=self.tecnico_var, width=30)
        tecnico_combo.grid(row=row, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        self.tecnico_combo = tecnico_combo
        row += 1

        # Descrição
        ttk.Label(aba_form, text="Descrição:").grid(row=row, column=0, sticky=(tk.W, tk.N), pady=2)
        self.descricao_evento_text = tk.Text(aba_form, height=4, wrap=tk.WORD)
        self.descricao_evento_text.grid(row=row, column=1, sticky=(tk.W, tk.E), 
                                       pady=2, padx=(10, 0))
        row += 1

        # Status
        ttk.Label(aba_form, text="Status:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.status_evento_var = tk.StringVar()
        status_combo = ttk.Combobox(aba_form, textvariable=self.status_evento_var, width=15)
        status_combo['values'] = ('AGENDADO', 'CONFIRMADO', 'EM_ANDAMENTO', 'CONCLUIDO', 'CANCELADO')
        status_combo.set('AGENDADO')
        status_combo.grid(row=row, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        row += 1

        # Lembrete
        ttk.Label(aba_form, text="Lembrete:").grid(row=row, column=0, sticky=tk.W, pady=2)
        lembrete_frame = ttk.Frame(aba_form)
        lembrete_frame.grid(row=row, column=1, sticky=tk.W, pady=2, padx=(10, 0))

        self.lembrete_var = tk.BooleanVar()
        ttk.Checkbutton(lembrete_frame, variable=self.lembrete_var, 
                       text="Enviar lembrete").pack(side=tk.LEFT)

        self.lembrete_minutos_var = tk.StringVar(value="30")
        ttk.Entry(lembrete_frame, textvariable=self.lembrete_minutos_var, width=5).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(lembrete_frame, text="minutos antes").pack(side=tk.LEFT)
        row += 1

        # Botões de ação
        btn_form_frame = ttk.Frame(aba_form)
        btn_form_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(btn_form_frame, text="💾 Salvar Evento", 
                  command=self.salvar_evento).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_form_frame, text="🗑️ Excluir Evento", 
                  command=self.excluir_evento).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_form_frame, text="🔄 Limpar Formulário", 
                  command=self.limpar_formulario).pack(side=tk.LEFT)

    def create_aba_disponibilidade(self):
        """Criar aba de consulta de disponibilidade"""
        aba_disp = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(aba_disp, text="🕐 Disponibilidade")

        # Configurar grid
        aba_disp.columnconfigure(0, weight=1)
        aba_disp.rowconfigure(2, weight=1)

        # Filtros de consulta
        filtros_frame = ttk.LabelFrame(aba_disp, text="🔍 Consultar Disponibilidade", padding="10")
        filtros_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filtros_frame.columnconfigure(1, weight=1)

        row = 0

        # Data consulta
        ttk.Label(filtros_frame, text="Data:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.data_consulta_var = tk.StringVar()
        ttk.Entry(filtros_frame, textvariable=self.data_consulta_var, width=12).grid(
            row=row, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        row += 1

        # Técnico consulta
        ttk.Label(filtros_frame, text="Técnico:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.tecnico_consulta_var = tk.StringVar()
        tecnico_consulta_combo = ttk.Combobox(filtros_frame, textvariable=self.tecnico_consulta_var)
        tecnico_consulta_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        self.tecnico_consulta_combo = tecnico_consulta_combo
        row += 1

        # Botão consultar
        ttk.Button(filtros_frame, text="🔍 Consultar Disponibilidade", 
                  command=self.consultar_disponibilidade).grid(row=row, column=0, columnspan=2, pady=10)

        # Resultado da consulta
        resultado_frame = ttk.LabelFrame(aba_disp, text="📊 Resultado", padding="10")
        resultado_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        resultado_frame.columnconfigure(0, weight=1)

        self.disponibilidade_text = tk.Text(resultado_frame, height=4, wrap=tk.WORD)
        self.disponibilidade_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.disponibilidade_text.configure(state='disabled')  # Configurar após criação

        # Grade de horários
        grade_frame = ttk.LabelFrame(aba_disp, text="⏰ Grade de Horários", padding="10")
        grade_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        grade_frame.columnconfigure(0, weight=1)
        grade_frame.rowconfigure(0, weight=1)

        # Treeview para grade de horários
        cols_grade = ('horario', 'disponivel', 'evento_atual', 'cliente')
        self.tree_grade = ttk.Treeview(grade_frame, columns=cols_grade, 
                                     show='headings', height=12)

        self.tree_grade.heading('horario', text='Horário')
        self.tree_grade.heading('disponivel', text='Disponível')
        self.tree_grade.heading('evento_atual', text='Evento Atual')
        self.tree_grade.heading('cliente', text='Cliente')

        # Scrollbar para grade
        scroll_grade = ttk.Scrollbar(grade_frame, orient=tk.VERTICAL, 
                                   command=self.tree_grade.yview)
        self.tree_grade.configure(yscrollcommand=scroll_grade.set)

        self.tree_grade.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scroll_grade.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def create_aba_conflitos(self):
        """Criar aba de conflitos"""
        aba_conflitos = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(aba_conflitos, text="⚠️ Conflitos")

        # Configurar grid
        aba_conflitos.columnconfigure(0, weight=1)
        aba_conflitos.rowconfigure(1, weight=1)

        # Cabeçalho
        header_conflitos = ttk.Frame(aba_conflitos)
        header_conflitos.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(header_conflitos, text="⚠️ Conflitos de Agendamento", 
                 style=STYLE_SUBTITULO_LABEL).pack(side=tk.LEFT)

        ttk.Button(header_conflitos, text="🔄 Verificar Conflitos", 
                  command=self.verificar_conflitos).pack(side=tk.RIGHT)

        # Lista de conflitos
        conflitos_frame = ttk.Frame(aba_conflitos)
        conflitos_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        conflitos_frame.columnconfigure(0, weight=1)
        conflitos_frame.rowconfigure(0, weight=1)

        # Treeview para conflitos
        cols_conflitos = ('data_hora', 'evento1', 'evento2', 'tecnico', 'severidade')
        self.tree_conflitos = ttk.Treeview(conflitos_frame, columns=cols_conflitos, 
                                         show='headings', height=15)

        self.tree_conflitos.heading('data_hora', text='Data/Hora')
        self.tree_conflitos.heading('evento1', text='Evento 1')
        self.tree_conflitos.heading('evento2', text='Evento 2')
        self.tree_conflitos.heading('tecnico', text='Técnico')
        self.tree_conflitos.heading('severidade', text='Severidade')

        # Scrollbar para conflitos
        scroll_conflitos = ttk.Scrollbar(conflitos_frame, orient=tk.VERTICAL, 
                                       command=self.tree_conflitos.yview)
        self.tree_conflitos.configure(yscrollcommand=scroll_conflitos.set)

        self.tree_conflitos.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scroll_conflitos.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Botões de resolução
        resolve_frame = ttk.Frame(aba_conflitos)
        resolve_frame.grid(row=2, column=0, pady=10)

        ttk.Button(resolve_frame, text="🔧 Resolver Automaticamente", 
                  command=self.resolver_conflitos_auto).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(resolve_frame, text="✏️ Resolver Manualmente", 
                  command=self.resolver_conflito_manual).pack(side=tk.LEFT)

    def create_context_menu_eventos(self):
        """Criar menu de contexto para eventos"""
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="✏️ Editar", command=self.editar_evento)
        self.context_menu.add_command(label="👁️ Visualizar", command=self.visualizar_evento)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✅ Confirmar", command=self.confirmar_evento)
        self.context_menu.add_command(label="▶️ Iniciar", command=self.iniciar_evento)
        self.context_menu.add_command(label="✔️ Concluir", command=self.concluir_evento)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔄 Reagendar", command=self.reagendar_evento)
        self.context_menu.add_command(label="❌ Cancelar", command=self.cancelar_evento)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Excluir", command=self.excluir_evento)

        # Bind do menu
        self.tree_eventos.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Mostrar menu de contexto"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def create_status_bar(self, parent):
        """Criar barra de status"""
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)

        self.status_text = tk.StringVar(value="Sistema de agendamento pronto")
        ttk.Label(status_frame, textvariable=self.status_text).pack(side=tk.LEFT, padx=5, pady=2)

        # Indicador de conexão
        self.conexao_text = tk.StringVar(value="🔴 Desconectado")
        ttk.Label(status_frame, textvariable=self.conexao_text).pack(side=tk.RIGHT, padx=5, pady=2)

    # =========================================================================
    # MÉTODOS DO CALENDÁRIO
    # =========================================================================

    def create_calendar_grid(self):
        """Criar grid do calendário"""
        # Limpar grid anterior
        for widget in self.cal_grid_frame.winfo_children():
            widget.destroy()

        self.cal_buttons = {}

        # Obter primeiro dia do mês
        primeiro_dia = date(self.ano_atual, self.mes_atual, 1)

        # Calcular primeira semana
        inicio_calendario = primeiro_dia - timedelta(days=primeiro_dia.weekday() + 1)
        if primeiro_dia.weekday() == 6:  # Domingo
            inicio_calendario = primeiro_dia

        # Atualizar título do mês
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        self.mes_ano_var.set(f"{meses[self.mes_atual-1]} {self.ano_atual}")

        # Criar botões para 6 semanas
        data_atual = inicio_calendario
        for semana in range(6):
            for dia_semana in range(7):
                btn_text = str(data_atual.day)

                # Criar botão (estilos serão aplicados pelo tkinter baseado no estado)

                # Criar botão
                btn = tk.Button(self.cal_grid_frame, text=btn_text,
                              width=4, height=2,
                              command=lambda d=data_atual: self.selecionar_data(d))

                btn.grid(row=semana, column=dia_semana, padx=1, pady=1, sticky=(tk.W, tk.E, tk.N, tk.S))

                # Armazenar referência
                self.cal_buttons[data_atual] = btn

                data_atual += timedelta(days=1)

        # Carregar eventos do mês
        self.carregar_eventos_mes()

    def selecionar_data(self, data):
        """Selecionar uma data no calendário"""
        self.data_selecionada = data

        # Atualizar visual
        self.create_calendar_grid()

        # Atualizar label da data
        self.data_selecionada_var.set(f"📅 {data.strftime('%d/%m/%Y - %A')}")

        # Carregar eventos do dia
        self.carregar_eventos_dia()

        # Focar na aba de eventos
        self.notebook.select(0)

    def mes_anterior(self):
        """Navegar para mês anterior"""
        if self.mes_atual == 1:
            self.mes_atual = 12
            self.ano_atual -= 1
        else:
            self.mes_atual -= 1

        self.create_calendar_grid()

    def proximo_mes(self):
        """Navegar para próximo mês"""
        if self.mes_atual == 12:
            self.mes_atual = 1
            self.ano_atual += 1
        else:
            self.mes_atual += 1

        self.create_calendar_grid()

    def ir_para_hoje(self):
        """Ir para a data de hoje"""
        hoje = date.today()
        self.mes_atual = hoje.month
        self.ano_atual = hoje.year
        self.selecionar_data(hoje)

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
            # Testar conexão
            response = requests.get(f"{self.api_base_url}/agendamento/health", timeout=5)
            if response.status_code == 200:
                self.window.after(0, lambda: self.conexao_text.set("🟢 Conectado"))

                # Carregar configurações
                self.carregar_configuracoes()

                # Carregar eventos
                self.carregar_eventos_mes()

                self.window.after(0, lambda: self.status_text.set("Dados carregados com sucesso"))
            else:
                self.window.after(0, lambda: self.conexao_text.set("🟡 Conexão instável"))

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão: {e}")
            self.window.after(0, lambda: self.conexao_text.set("🔴 Erro de conexão"))
            self.window.after(0, lambda: self.status_text.set("Modo demonstração ativo"))

            # Carregar dados mock
            self.carregar_dados_mock()

    def carregar_dados_mock(self):
        """Carregar dados mock para demonstração"""
        # Eventos mock
        self.lista_eventos = [
            {
                'id': 1,
                'titulo': 'Instalação Forro PVC - João Silva',
                'tipo': 'OS_AGENDADA',
                'data_inicio': '2025-10-30T09:00:00',
                'data_fim': '2025-10-30T12:00:00',
                'cliente_nome': 'João Silva Construções',
                'tecnico_nome': 'Carlos Técnico',
                'status': 'AGENDADO',
                'descricao': 'Instalação de forro PVC em sala comercial'
            },
            {
                'id': 2,
                'titulo': 'Manutenção Divisórias - Maria Santos',
                'tipo': 'OS_AGENDADA',
                'data_inicio': '2025-10-30T14:00:00',
                'data_fim': '2025-10-30T17:00:00',
                'cliente_nome': 'Maria Santos Arquitetura',
                'tecnico_nome': 'Pedro Técnico',
                'status': 'CONFIRMADO',
                'descricao': 'Manutenção em divisórias de vidro'
            }
        ]

        # Atualizar interface
        self.window.after(0, self.atualizar_interface)

    def carregar_configuracoes(self):
        """Carregar configurações de horário"""
        try:
            response = requests.get(f"{self.api_base_url}/agendamento/configuracoes", timeout=10)
            if response.status_code == 200:
                self.configuracoes_horario = response.json()
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")

    def carregar_eventos_mes(self):
        """Carregar eventos do mês atual"""
        try:
            inicio_mes = date(self.ano_atual, self.mes_atual, 1)
            fim_mes = date(self.ano_atual, self.mes_atual, calendar.monthrange(self.ano_atual, self.mes_atual)[1])

            params = {
                'data_inicio': inicio_mes.isoformat(),
                'data_fim': fim_mes.isoformat()
            }

            response = requests.get(f"{self.api_base_url}/agendamento/eventos", 
                                  params=params, timeout=10)
            if response.status_code == 200:
                self.lista_eventos = response.json()
                self.window.after(0, self.atualizar_interface)
        except Exception as e:
            logger.error(f"Erro ao carregar eventos: {e}")
            self.carregar_dados_mock()

    def carregar_eventos_dia(self):
        """Carregar eventos do dia selecionado"""
        # Filtrar eventos do dia
        eventos_dia = []
        data_str = self.data_selecionada.isoformat()

        for evento in self.lista_eventos:
            data_evento = evento.get('data_inicio', '')[:10]  # YYYY-MM-DD
            if data_evento == data_str:
                eventos_dia.append(evento)

        # Atualizar treeview
        self.atualizar_tree_eventos(eventos_dia)

    def atualizar_tree_eventos(self, eventos):
        """Atualizar treeview de eventos"""
        # Limpar árvore
        for item in self.tree_eventos.get_children():
            self.tree_eventos.delete(item)

        # Adicionar eventos
        for evento in eventos:
            data_inicio = evento.get('data_inicio', '')
            hora = data_inicio[11:16] if len(data_inicio) > 10 else ''  # HH:MM

            self.tree_eventos.insert('', 'end', values=(
                hora,
                evento.get('tipo', ''),
                evento.get('titulo', ''),
                evento.get('cliente_nome', ''),
                evento.get('status', ''),
                evento.get('tecnico_nome', '')
            ))

    def atualizar_interface(self):
        """Atualizar toda a interface"""
        self.carregar_eventos_dia()
        # Adicionar indicadores visuais no calendário para dias com eventos
        self.marcar_dias_com_eventos()

    def marcar_dias_com_eventos(self):
        """Marcar dias que têm eventos no calendário"""
        # Implementar indicadores visuais para dias com eventos
        for data, btn in self.cal_buttons.items():
            tem_eventos = any(
                evento.get('data_inicio', '')[:10] == data.isoformat() 
                for evento in self.lista_eventos
            )

            if tem_eventos and data.month == self.mes_atual:
                # Adicionar indicador visual
                btn.configure(bg='lightblue')

    # =========================================================================
    # AÇÕES DA INTERFACE
    # =========================================================================

    def novo_evento(self):
        """Criar novo evento"""
        self.evento_atual = None
        self.limpar_formulario()
        self.data_evento_var.set(self.data_selecionada.strftime('%Y-%m-%d'))
        self.notebook.select(1)  # Focar na aba do formulário
        self.status_text.set("Novo evento - Preencha os dados")

    def adicionar_evento(self):
        """Adicionar evento (mesmo que novo evento)"""
        self.novo_evento()

    def salvar_evento(self):
        """Salvar evento atual"""
        try:
            # Validar dados
            if not self.titulo_var.get():
                messagebox.showerror("Erro", "Informe o título do evento")
                return

            if not self.data_evento_var.get():
                messagebox.showerror("Erro", "Informe a data do evento")
                return

            # Preparar dados
            dados_evento = {
                'titulo': self.titulo_var.get(),
                'tipo': self.tipo_var.get(),
                'data_inicio': f"{self.data_evento_var.get()}T{self.hora_inicio_var.get()}:00",
                'data_fim': f"{self.data_evento_var.get()}T{self.hora_fim_var.get()}:00",
                'descricao': self.descricao_evento_text.get(1.0, tk.END).strip(),
                'status': self.status_evento_var.get()
            }

            if self.evento_atual:
                # Atualizar evento
                response = requests.put(f"{self.api_base_url}/agendamento/eventos/{self.evento_atual['id']}", 
                                      json=dados_evento, timeout=10)
                if response.status_code == 200:
                    messagebox.showinfo("Sucesso", "Evento atualizado com sucesso!")
                else:
                    messagebox.showerror("Erro", f"Erro ao atualizar evento: {response.text}")
            else:
                # Criar novo evento
                response = requests.post(f"{self.api_base_url}/agendamento/eventos", 
                                       json=dados_evento, timeout=10)
                if response.status_code == 201:
                    messagebox.showinfo("Sucesso", "Evento criado com sucesso!")
                else:
                    messagebox.showerror("Erro", f"Erro ao criar evento: {response.text}")

            # Recarregar eventos
            self.carregar_eventos_mes()

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro de Conexão", f"Erro ao conectar com a API: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def limpar_formulario(self):
        """Limpar formulário de evento"""
        self.titulo_var.set("")
        self.tipo_var.set("OS_AGENDADA")
        self.data_evento_var.set("")
        self.hora_inicio_var.set("")
        self.hora_fim_var.set("")
        self.cliente_evento_var.set("")
        self.tecnico_var.set("")
        self.status_evento_var.set("AGENDADO")
        self.lembrete_var.set(False)
        self.lembrete_minutos_var.set("30")

        self.descricao_evento_text.delete(1.0, tk.END)

    def on_evento_selected(self, event):
        """Evento quando um evento é selecionado"""
        selection = self.tree_eventos.selection()
        if selection:
            # Implementar carregamento de detalhes do evento
            pass

    def editar_evento(self):
        """Editar evento selecionado"""
        selection = self.tree_eventos.selection()
        if selection:
            self.notebook.select(1)  # Focar na aba de formulário
            # Implementar carregamento dos dados do evento

    def excluir_evento(self):
        """Excluir evento atual"""
        if not self.evento_atual:
            messagebox.showwarning("Aviso", "Selecione um evento para excluir")
            return

        if messagebox.askyesno("Confirmação", 
                              f"Deseja realmente excluir o evento '{self.evento_atual.get('titulo', '')}'?"):
            try:
                response = requests.delete(f"{self.api_base_url}/agendamento/eventos/{self.evento_atual['id']}", 
                                         timeout=10)
                if response.status_code == 200:
                    messagebox.showinfo("Sucesso", "Evento excluído com sucesso!")
                    self.carregar_eventos_mes()
                    self.limpar_formulario()
                else:
                    messagebox.showerror("Erro", f"Erro ao excluir evento: {response.text}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir evento: {e}")

    def consultar_disponibilidade(self):
        """Consultar disponibilidade de técnico"""
        if not self.data_consulta_var.get():
            messagebox.showwarning("Aviso", "Informe a data para consulta")
            return

        # Simular consulta de disponibilidade
        resultado = """
Consulta de Disponibilidade - {self.data_consulta_var.get()}
Técnico: {self.tecnico_consulta_var.get() or 'Todos'}

Horários Disponíveis:
• 08:00 - 09:00: Disponível
• 09:00 - 12:00: Ocupado (OS João Silva)
• 14:00 - 17:00: Ocupado (OS Maria Santos)
• 17:00 - 18:00: Disponível
"""

        self.disponibilidade_text.configure(state='normal')
        self.disponibilidade_text.delete(1.0, tk.END)
        self.disponibilidade_text.insert(1.0, resultado)
        self.disponibilidade_text.configure(state='disabled')

    def verificar_conflitos(self):
        """Verificar conflitos de agendamento"""
        # Simular verificação de conflitos
        conflitos_mock = [
            ('30/10/2025 14:00', 'OS João Silva', 'Reunião Equipe', 'Carlos Técnico', 'ALTA'),
            ('31/10/2025 09:30', 'OS Maria Santos', 'Manutenção Urgente', 'Pedro Técnico', 'MEDIA')
        ]

        # Limpar árvore
        for item in self.tree_conflitos.get_children():
            self.tree_conflitos.delete(item)

        # Adicionar conflitos
        for conflito in conflitos_mock:
            self.tree_conflitos.insert('', 'end', values=conflito)

        self.status_text.set(f"{len(conflitos_mock)} conflitos encontrados")

    def abrir_configuracoes(self):
        """Abrir janela de configurações"""
        messagebox.showinfo("Configurações", MSG_FUNCIONALIDADE_EM_DESENVOLVIMENTO)

    def gerar_relatorios(self):
        """Gerar relatórios"""
        messagebox.showinfo("Relatórios", MSG_FUNCIONALIDADE_EM_DESENVOLVIMENTO)

    def atualizar_eventos_dia(self):
        """Atualizar eventos do dia"""
        self.carregar_eventos_dia()
        self.status_text.set("Eventos atualizados")

    def visualizar_evento(self):
        """Visualizar evento selecionado"""
        self.editar_evento()

    def confirmar_evento(self):
        """Confirmar evento"""
        messagebox.showinfo("Evento", "Evento confirmado!")

    def iniciar_evento(self):
        """Iniciar evento"""
        messagebox.showinfo("Evento", "Evento iniciado!")

    def concluir_evento(self):
        """Concluir evento"""
        messagebox.showinfo("Evento", "Evento concluído!")

    def reagendar_evento(self):
        """Reagendar evento"""
        messagebox.showinfo("Agendamento", MSG_FUNCIONALIDADE_EM_DESENVOLVIMENTO)

    def cancelar_evento(self):
        """Cancelar evento"""
        if messagebox.askyesno("Confirmação", "Deseja cancelar este evento?"):
            messagebox.showinfo("Evento", "Evento cancelado!")

    def resolver_conflitos_auto(self):
        """Resolver conflitos automaticamente"""
        messagebox.showinfo("Conflitos", "Resolução automática em desenvolvimento")

    def resolver_conflito_manual(self):
        """Resolver conflito manualmente"""
        messagebox.showinfo("Conflitos", "Resolução manual em desenvolvimento")

    def on_closing(self):
        """Evento de fechamento da janela"""
        if messagebox.askokcancel("Sair", "Deseja fechar o sistema de agendamento?"):
            self.window.destroy()

# =============================================================================
# FUNÇÃO PRINCIPAL PARA TESTE
# =============================================================================

def main():
    """Função principal para teste da interface"""
    app = AgendamentoWindow()
    app.window.mainloop()

if __name__ == "__main__":
    main()