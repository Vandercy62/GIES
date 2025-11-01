"""
SISTEMA ERP PRIMOTEX - DASHBOARD INTEGRADO
==========================================

Dashboard principal consolidado com métricas de todos os módulos:
- Ordem de Serviço: workflow, estatísticas, alertas
- Agendamento: calendário, disponibilidade, próximos eventos  
- Financeiro: fluxo de caixa, contas pendentes, receitas
- Comunicação: templates, histórico, estatísticas de envio
- Clientes/Produtos: métricas básicas e alertas

Interface executiva com KPIs em tempo real e alertas automáticos.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, Canvas
import threading
import requests
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
import json
import time
import sys
import os

# Adicionar diretório raiz ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Constantes da UI centralizadas
try:
    from ui_constants import (
        COLORS, FONT_STYLES, MODULE_TITLES, ACTION_MESSAGES, 
        PERFORMANCE
    )
except ImportError:
    # Fallback se ui_constants não estiver disponível
    COLORS = {
        'primary': '#2c3e50',
        'secondary': '#3498db',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'light': '#ecf0f1',
        'dark': '#34495e'
    }
    FONT_STYLES = {'default': ('Segoe UI', 10)}
    MODULE_TITLES = {}
    ACTION_MESSAGES = {}
    PERFORMANCE = {}

# Sistemas de performance (opcionais)
try:
    from shared.cache_system import erp_cache
    from shared.lazy_loading import erp_loader
    PERFORMANCE_ENABLED = True
except ImportError:
    erp_cache = None
    erp_loader = None
    PERFORMANCE_ENABLED = False

# Constantes locais para evitar dependências externas
API_BASE_URL = "http://127.0.0.1:8002"

# Configurações padrão se PERFORMANCE não estiver disponível
try:
    API_TIMEOUT = PERFORMANCE['api_timeout']
    CACHE_TIMEOUT_CONFIG = PERFORMANCE['cache_timeout']
    REFRESH_INTERVAL_CONFIG = PERFORMANCE['refresh_interval']
except (NameError, KeyError):
    API_TIMEOUT = 10
    CACHE_TIMEOUT_CONFIG = 30
    REFRESH_INTERVAL_CONFIG = 5000

# =======================================
# CONFIGURAÇÕES
# =======================================

# Cache de dados (atualizado a cada 30 segundos)
CACHE_TIMEOUT = 30  # segundos
REFRESH_INTERVAL = 5000  # millisegundos para auto-refresh

# Cores do dashboard
COLORS = {
    'primary': '#2c3e50',
    'success': '#27ae60', 
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#3498db',
    'light': '#ecf0f1',
    'dark': '#34495e',
    'background': '#f8f9fa'
}

# =======================================
# CLASSE DO DASHBOARD
# =======================================

class DashboardWindow:
    """Dashboard integrado com métricas de todos os módulos"""
    
    def __init__(self, user_data: Dict[str, Any]):
        self.user_data = user_data
        self.token = user_data.get("access_token")
        self.user_info = user_data.get("user", {})
        
        # Cache de dados
        self.metrics_cache = {}
        self.last_update = {}
        self.alerts = []
        
        # Configurações de API
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.load_dashboard_data()
        self.start_auto_refresh()
    
    def setup_window(self):
        """Configurar janela principal"""
        
        self.root.title("Sistema ERP Primotex - Dashboard")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Maximizar no Windows
        
        # Configurar cor de fundo
        self.root.configure(bg='#f8f9fa')
        
        # Configurar protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Criar widgets do dashboard"""

        # === BARRA SUPERIOR ===
        self.create_top_bar()
        
        # === SISTEMA DE NAVEGAÇÃO ===
        self.create_navigation_system()
        
        # === CONTAINER PRINCIPAL ===
        main_container = tk.Frame(self.root, bg='#f8f9fa')
        main_container.pack(fill='both', expand=True, padx=10, pady=5)

        # === MENU LATERAL ===
        self.create_sidebar(main_container)

        # === ÁREA DE CONTEÚDO ===
        self.create_content_area(main_container)
    
    def create_navigation_system(self):
        """Criar sistema de navegação integrado"""
        try:
            from navigation_system import NavigationSystem, QuickSearchWidget
            
            # Criar sistema de navegação
            self.nav_system = NavigationSystem(self.root)
            
            # Criar busca rápida
            self.search_widget = QuickSearchWidget(self.root, {})
            
            # Registrar callbacks de navegação
            self.register_navigation_callbacks()
            
        except Exception as e:
            print(f"Erro ao criar sistema de navegação: {str(e)}")
    
    def register_navigation_callbacks(self):
        """Registrar callbacks para navegação"""
        
        # Registrar módulos no sistema de navegação
        callbacks = {
            'dashboard': self.show_dashboard,
            'clientes': self.show_clients,
            'produtos': self.show_products,
            'estoque': self.show_estoque,
            'codigo_barras': self.show_codigo_barras,
            'relatorios': self.show_reports,
            'financeiro': self.show_financial,
            'orders': self.show_orders,
            'configuracoes': self.show_settings
        }
        
        for module_id, callback in callbacks.items():
            if hasattr(self, 'nav_system'):
                self.nav_system.register_callback(module_id, callback)

    def create_top_bar(self):
        """Criar barra superior com informações do usuário"""
        
        top_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)
        
        # Container interno
        container = tk.Frame(top_frame, bg='#2c3e50')
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Logo e título (esquerda)
        left_frame = tk.Frame(container, bg='#2c3e50')
        left_frame.pack(side='left', fill='y')
        
        logo_label = tk.Label(
            left_frame,
            text="🏢 Sistema ERP Primotex",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        logo_label.pack(side='left', pady=5)
        
        # Informações do usuário (direita)
        right_frame = tk.Frame(container, bg='#2c3e50')
        right_frame.pack(side='right', fill='y')
        
        # Data/hora atual
        self.datetime_label = tk.Label(
            right_frame,
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        self.datetime_label.pack(side='right', padx=(0, 20))
        self.update_datetime()
        
        # Informações do usuário
        user_info = f"👤 {self.user_info.get('nome_completo', 'Usuário')} ({self.user_info.get('perfil', 'N/A')})"
        user_label = tk.Label(
            right_frame,
            text=user_info,
            font=('Arial', 11),
            bg='#2c3e50',
            fg='white'
        )
        user_label.pack(side='right', padx=(0, 20), pady=5)
        
        # Botão logout
        logout_btn = tk.Button(
            right_frame,
            text="🚪 Sair",
            font=('Arial', 9),
            bg='#e74c3c',
            fg='white',
            border=0,
            padx=10,
            pady=2,
            command=self.logout
        )
        logout_btn.pack(side='right', padx=(0, 10))
    
    def create_sidebar(self, parent):
        """Criar menu lateral"""
        
        sidebar = tk.Frame(parent, bg='#34495e', width=250)
        sidebar.pack(side='left', fill='y', padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Título do menu
        menu_title = tk.Label(
            sidebar,
            text="📋 MÓDULOS DO SISTEMA",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white',
            pady=15
        )
        menu_title.pack(fill='x')
        
        # Botões do menu
        self.create_menu_buttons(sidebar)
    
    def create_menu_buttons(self, parent):
        """Criar botões do menu lateral"""
        
        buttons = [
            ("📊 Dashboard", self.show_dashboard, "#3498db"),
            ("👥 Clientes", self.show_clients, "#2ecc71"),
            ("📦 Produtos", self.show_products, "#f39c12"),
            ("📦 Estoque", self.show_estoque, "#e67e22"),
            ("🏷️ Códigos de Barras", self.show_codigo_barras, "#8e44ad"),
            (MODULE_TITLES['ordem_servico'], self.show_orders, "#9b59b6"),
            (MODULE_TITLES['financeiro'], self.show_financial, "#e67e22"),
            (MODULE_TITLES['comunicacao'], self.show_comunicacao, "#25d366"),
            ("📈 Relatórios", self.show_reports, "#1abc9c"),
            ("⚙️ Configurações", self.show_settings, "#95a5a6"),
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                parent,
                text=text,
                font=('Arial', 11),
                bg=color,
                fg='white',
                border=0,
                pady=12,
                command=command,
                relief='flat',
                cursor='hand2'
            )
            btn.pack(fill='x', padx=10, pady=2)
            
            # Efeito hover
            def on_enter(e, button=btn, original_color=color):
                button.config(bg=self.darken_color(original_color))
            
            def on_leave(e, button=btn, original_color=color):
                button.config(bg=original_color)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    
    def create_content_area(self, parent):
        """Criar área de conteúdo principal"""
        
        # Container de conteúdo
        self.content_frame = tk.Frame(parent, bg='white', relief='raised', bd=1)
        self.content_frame.pack(side='right', fill='both', expand=True)
        
        # Mostrar dashboard inicial
        self.show_dashboard()
    
    def show_dashboard(self):
        """Mostrar dashboard integrado"""
        
        self.clear_content()
        
        # Scrollable frame principal
        canvas = Canvas(self.content_frame, bg=COLORS['background'])
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === SEÇÃO 1: HEADER COM ALERTAS ===
        self.create_header_section(scrollable_frame)
        
        # === SEÇÃO 2: KPIs PRINCIPAIS (5 colunas) ===
        self.create_kpi_section(scrollable_frame)
        
        # === SEÇÃO 3: MÓDULOS DETALHADOS (2x2 grid) ===
        self.create_modules_section(scrollable_frame)
        
        # === SEÇÃO 4: GRÁFICOS E TENDÊNCIAS ===
        self.create_charts_section(scrollable_frame)
        
        # === SEÇÃO 5: AÇÕES RÁPIDAS ===
        self.create_quick_actions_section(scrollable_frame)
    
    def create_header_section(self, parent):
        """Criar header com título e alertas"""
        
        header_frame = tk.Frame(parent, bg=COLORS['background'])
        header_frame.pack(fill='x', padx=20, pady=10)
        
        # Título principal
        title_frame = tk.Frame(header_frame, bg=COLORS['background'])
        title_frame.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            title_frame,
            text="📊 Dashboard Executivo - Sistema ERP Primotex",
            font=FONT_STYLES['title'],
            bg=COLORS['background'],
            fg=COLORS['primary']
        )
        title.pack(side='left')
        
        # Data/hora atual
        now = datetime.now()
        timestamp = tk.Label(
            title_frame,
            text=f"Atualizado: {now.strftime('%d/%m/%Y %H:%M')}",
            font=FONT_STYLES['medium'],
            bg=COLORS['background'],
            fg=COLORS['dark']
        )
        timestamp.pack(side='right')
        
        # Barra de alertas
        self.alerts_frame = tk.Frame(header_frame, bg=COLORS['background'])
        self.alerts_frame.pack(fill='x')
        
        self.update_alerts_display()
    
    def update_alerts_display(self):
        """Atualizar exibição de alertas"""
        
        # Limpar alertas existentes
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()
        
        if not self.alerts:
            no_alerts = tk.Label(
                self.alerts_frame,
                text="✅ Nenhum alerta crítico no momento",
                font=('Segoe UI', 10),
                bg=COLORS['success'],
                fg='white',
                relief='flat',
                padx=10,
                pady=5
            )
            no_alerts.pack(side='left', padx=5)
        else:
            for alert in self.alerts[:3]:  # Mostrar máximo 3 alertas
                alert_label = tk.Label(
                    self.alerts_frame,
                    text=f"⚠️ {alert['message']}",
                    font=('Segoe UI', 10),
                    bg=COLORS[alert.get('type', 'warning')],
                    fg='white',
                    relief='flat',
                    padx=10,
                    pady=5
                )
                alert_label.pack(side='left', padx=5)
        """Criar cards com métricas principais"""
        
    def create_kpi_section(self, parent):
        """Criar seção de KPIs principais"""
        
        kpi_frame = tk.Frame(parent, bg=COLORS['background'])
        kpi_frame.pack(fill='x', padx=20, pady=10)
        
        # Título da seção
        section_title = tk.Label(
            kpi_frame,
            text="📈 Indicadores Principais",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['primary']
        )
        section_title.pack(anchor='w', pady=(0, 10))
        
        # Frame para os cards
        cards_frame = tk.Frame(kpi_frame, bg=COLORS['background'])
        cards_frame.pack(fill='x')
        
        # KPIs principais (dados do cache)
        kpis = [
            {
                'title': '👥 Clientes',
                'value': self.get_cached_value('clientes', 'total', '0'),
                'subtitle': 'Total cadastrados',
                'color': COLORS['info'],
                'trend': self.get_cached_value('clientes', 'trend', '0%')
            },
            {
                'title': '📋 Ordens Serviço',
                'value': self.get_cached_value('os', 'abertas', '0'),
                'subtitle': 'Abertas/Execução',
                'color': COLORS['warning'],
                'trend': self.get_cached_value('os', 'trend', '0%')
            },
            {
                'title': '📅 Agendamentos',
                'value': self.get_cached_value('agendamento', 'hoje', '0'),
                'subtitle': 'Hoje',
                'color': COLORS['success'],
                'trend': self.get_cached_value('agendamento', 'trend', '0%')
            },
            {
                'title': '💰 Financeiro',
                'value': self.get_cached_value('financeiro', 'saldo', 'R$ 0'),
                'subtitle': 'Saldo atual',
                'color': COLORS['primary'],
                'trend': self.get_cached_value('financeiro', 'trend', '0%')
            },
            {
                'title': '⚡ Performance',
                'value': self.get_performance_metrics(),
                'subtitle': 'Cache Hit Ratio',
                'color': '#9b59b6',  # Roxo para performance
                'trend': self.get_performance_trend()
            }
        ]
        
        for i, kpi in enumerate(kpis):
            card = self.create_kpi_card(cards_frame, kpi)
            card.grid(row=0, column=i, padx=8, pady=5, sticky='ew')
        
        # Configurar colunas para distribuição igual
        for col_index in range(len(kpis)):
            cards_frame.grid_columnconfigure(col_index, weight=1)
    
    def create_kpi_card(self, parent, kpi_data: Dict[str, str]):
        """Criar card de KPI moderno"""
        
        card = tk.Frame(parent, bg='white', relief='raised', bd=1)
        
        # Container interno com padding
        inner = tk.Frame(card, bg='white')
        inner.pack(fill='both', expand=True, padx=15, pady=12)
        
        # Título do KPI
        title_label = tk.Label(
            inner,
            text=kpi_data['title'],
            font=('Segoe UI', 11, 'bold'),
            bg='white',
            fg=COLORS['dark']
        )
        title_label.pack(anchor='w')
        
        # Valor principal (grande)
        value_label = tk.Label(
            inner,
            text=kpi_data['value'],
            font=('Segoe UI', 18, 'bold'),
            bg='white',
            fg=kpi_data['color']
        )
        value_label.pack(anchor='w', pady=(5, 0))
        
        # Subtitle e trend em linha
        bottom_frame = tk.Frame(inner, bg='white')
        bottom_frame.pack(fill='x', pady=(5, 0))
        
        subtitle_label = tk.Label(
            bottom_frame,
            text=kpi_data['subtitle'],
            font=('Segoe UI', 9),
            bg='white',
            fg=COLORS['dark']
        )
        subtitle_label.pack(side='left')
        
        # Trend (se positivo = verde, negativo = vermelho)
        trend_text = kpi_data['trend']
        
        # Determinar cor da tendência de forma mais legível
        if '+' in trend_text:
            trend_color = COLORS['success']
        elif '-' in trend_text:
            trend_color = COLORS['danger']
        else:
            trend_color = COLORS['dark']
        
        trend_label = tk.Label(
            bottom_frame,
            text=trend_text,
            font=('Segoe UI', 9, 'bold'),
            bg='white',
            fg=trend_color
        )
        trend_label.pack(side='right')
        
        return card
    
    def get_cached_value(self, module: str, metric: str, default: str = '0') -> str:
        """Obter valor do cache ou padrão"""
        try:
            return self.metrics_cache.get(module, {}).get(metric, default)
        except Exception:
            return default
    
    def get_performance_metrics(self) -> str:
        """Obter métricas de performance do sistema"""
        try:
            health = erp_cache.get_cache_health()
            hit_ratio = health.get('hit_ratio', 0)
            return f"{hit_ratio:.0f}%"
        except Exception:
            return "N/A"
    
    def get_performance_trend(self) -> str:
        """Obter tendência de performance"""
        try:
            health = erp_cache.get_cache_health()
            hit_ratio = health.get('hit_ratio', 0)
            
            if hit_ratio >= 80:
                return "🚀 Excelente"
            elif hit_ratio >= 60:
                return "✅ Bom"
            elif hit_ratio >= 40:
                return "⚠️ Regular"
            else:
                return "🔧 Otimizar"
        except Exception:
            return "➖"
    
    def create_modules_section(self, parent):
        """Criar seção de módulos detalhados (2x2 grid)"""
        
        modules_frame = tk.Frame(parent, bg=COLORS['background'])
        modules_frame.pack(fill='x', padx=20, pady=20)
        
        # Título da seção
        section_title = tk.Label(
            modules_frame,
            text="🏢 Módulos do Sistema",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['primary']
        )
        section_title.pack(anchor='w', pady=(0, 15))
        
        # Grid 2x2 dos módulos
        grid_frame = tk.Frame(modules_frame, bg=COLORS['background'])
        grid_frame.pack(fill='x')
        
        # Configurar grid
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        
        # Módulo 1: Ordem de Serviço (0,0)
        self.create_os_module_card(grid_frame).grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        
        # Módulo 2: Agendamento (0,1)
        self.create_agendamento_module_card(grid_frame).grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        
        # Módulo 3: Financeiro (1,0)
        self.create_financeiro_module_card(grid_frame).grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        
        # Módulo 4: Comunicação (1,1)
        self.create_comunicacao_module_card(grid_frame).grid(row=1, column=1, padx=10, pady=10, sticky='ew')
    
    def create_os_module_card(self, parent):
        """Card detalhado do módulo Ordem de Serviço"""
        
        card = tk.Frame(parent, bg='white', relief='raised', bd=1)
        inner = tk.Frame(card, bg='white')
        inner.pack(fill='both', expand=True, padx=15, pady=12)
        
        # Header do módulo
        header = tk.Frame(inner, bg='white')
        header.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(header, text="📋 Ordem de Serviço", font=('Segoe UI', 12, 'bold'), bg='white', fg=COLORS['primary'])
        title.pack(side='left')
        
        btn_abrir = tk.Button(header, text="Abrir", font=('Segoe UI', 9), bg=COLORS['primary'], fg='white',
                             command=self.open_ordem_servico, relief='flat', padx=15)
        btn_abrir.pack(side='right')
        
        # Métricas do módulo
        metrics = [
            ("Abertas:", self.get_cached_value('os', 'abertas', '0')),
            ("Em execução:", self.get_cached_value('os', 'execucao', '0')),
            ("Atrasadas:", self.get_cached_value('os', 'atrasadas', '0')),
            ("Concluídas hoje:", self.get_cached_value('os', 'concluidas_hoje', '0'))
        ]
        
        for label, value in metrics:
            row = tk.Frame(inner, bg='white')
            row.pack(fill='x', pady=2)
            
            tk.Label(row, text=label, font=('Segoe UI', 9), bg='white', fg=COLORS['dark']).pack(side='left')
            tk.Label(row, text=value, font=('Segoe UI', 9, 'bold'), bg='white', fg=COLORS['info']).pack(side='right')
        
        return card
    
    def create_agendamento_module_card(self, parent):
        """Card detalhado do módulo Agendamento"""
        
        card = tk.Frame(parent, bg='white', relief='raised', bd=1)
        inner = tk.Frame(card, bg='white')
        inner.pack(fill='both', expand=True, padx=15, pady=12)
        
        # Header
        header = tk.Frame(inner, bg='white')
        header.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(header, text="📅 Agendamento", font=('Segoe UI', 12, 'bold'), bg='white', fg=COLORS['success'])
        title.pack(side='left')
        
        btn_abrir = tk.Button(header, text="Abrir", font=('Segoe UI', 9), bg=COLORS['success'], fg='white',
                             command=self.open_agendamento, relief='flat', padx=15)
        btn_abrir.pack(side='right')
        
        # Métricas
        metrics = [
            ("Hoje:", self.get_cached_value('agendamento', 'hoje', '0')),
            ("Esta semana:", self.get_cached_value('agendamento', 'semana', '0')),
            ("Próximo:", self.get_cached_value('agendamento', 'proximo', 'N/A')),
            ("Disponibilidade:", self.get_cached_value('agendamento', 'disponibilidade', 'N/A'))
        ]
        
        for label, value in metrics:
            row = tk.Frame(inner, bg='white')
            row.pack(fill='x', pady=2)
            
            tk.Label(row, text=label, font=('Segoe UI', 9), bg='white', fg=COLORS['dark']).pack(side='left')
            tk.Label(row, text=value, font=('Segoe UI', 9, 'bold'), bg='white', fg=COLORS['success']).pack(side='right')
        
        return card
    
    def create_financeiro_module_card(self, parent):
        """Card detalhado do módulo Financeiro"""
        
        card = tk.Frame(parent, bg='white', relief='raised', bd=1)
        inner = tk.Frame(card, bg='white')
        inner.pack(fill='both', expand=True, padx=15, pady=12)
        
        # Header
        header = tk.Frame(inner, bg='white')
        header.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(header, text="💰 Financeiro", font=('Segoe UI', 12, 'bold'), bg='white', fg=COLORS['primary'])
        title.pack(side='left')
        
        btn_abrir = tk.Button(header, text="Abrir", font=('Segoe UI', 9), bg=COLORS['primary'], fg='white',
                             command=self.open_financeiro, relief='flat', padx=15)
        btn_abrir.pack(side='right')
        
        # Métricas
        metrics = [
            ("Saldo atual:", self.get_cached_value('financeiro', 'saldo', 'R$ 0')),
            ("A receber:", self.get_cached_value('financeiro', 'receber', 'R$ 0')),
            ("A pagar:", self.get_cached_value('financeiro', 'pagar', 'R$ 0')),
            ("Vencidas:", self.get_cached_value('financeiro', 'vencidas', '0'))
        ]
        
        for label, value in metrics:
            row = tk.Frame(inner, bg='white')
            row.pack(fill='x', pady=2)
            
            tk.Label(row, text=label, font=('Segoe UI', 9), bg='white', fg=COLORS['dark']).pack(side='left')
            tk.Label(row, text=value, font=('Segoe UI', 9, 'bold'), bg='white', fg=COLORS['primary']).pack(side='right')
        
        return card
    
    def create_comunicacao_module_card(self, parent):
        """Card detalhado do módulo Comunicação"""
        
        card = tk.Frame(parent, bg='white', relief='raised', bd=1)
        inner = tk.Frame(card, bg='white')
        inner.pack(fill='both', expand=True, padx=15, pady=12)
        
        # Header
        header = tk.Frame(inner, bg='white')
        header.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(header, text="📱 Comunicação", font=('Segoe UI', 12, 'bold'), bg='white', fg=COLORS['info'])
        title.pack(side='left')
        
        btn_abrir = tk.Button(header, text="Abrir", font=('Segoe UI', 9), bg=COLORS['info'], fg='white',
                             command=self.open_comunicacao, relief='flat', padx=15)
        btn_abrir.pack(side='right')
        
        # Métricas
        metrics = [
            ("Enviadas hoje:", self.get_cached_value('comunicacao', 'enviadas', '0')),
            ("Templates:", self.get_cached_value('comunicacao', 'templates', '0')),
            ("WhatsApp:", self.get_cached_value('comunicacao', 'whatsapp', '0')),
            ("Taxa sucesso:", self.get_cached_value('comunicacao', 'taxa_sucesso', '0%'))
        ]
        
        for label, value in metrics:
            row = tk.Frame(inner, bg='white')
            row.pack(fill='x', pady=2)
            
            tk.Label(row, text=label, font=('Segoe UI', 9), bg='white', fg=COLORS['dark']).pack(side='left')
            tk.Label(row, text=value, font=('Segoe UI', 9, 'bold'), bg='white', fg=COLORS['info']).pack(side='right')
        
        return card
    
    def create_charts_section(self, parent):
        """Criar seção de gráficos e tendências"""
        
        charts_frame = tk.Frame(parent, bg=COLORS['background'])
        charts_frame.pack(fill='x', padx=20, pady=20)
        
        # Título da seção
        section_title = tk.Label(
            charts_frame,
            text="📊 Tendências e Análises",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['primary']
        )
        section_title.pack(anchor='w', pady=(0, 15))
        
        # Container dos gráficos (2 colunas)
        graphs_container = tk.Frame(charts_frame, bg=COLORS['background'])
        graphs_container.pack(fill='x')
        
        # Configurar colunas
        graphs_container.grid_columnconfigure(0, weight=1)
        graphs_container.grid_columnconfigure(1, weight=1)
        
        # Gráfico 1: Atividades dos últimos 7 dias
        self.create_activity_chart(graphs_container).grid(row=0, column=0, padx=(0, 10), pady=5, sticky='ew')
        
        # Gráfico 2: Status financeiro
        self.create_financial_chart(graphs_container).grid(row=0, column=1, padx=(10, 0), pady=5, sticky='ew')
    
    def create_activity_chart(self, parent):
        """Criar gráfico de atividades dos últimos 7 dias"""
        
        chart_frame = tk.Frame(parent, bg='white', relief='raised', bd=1)
        inner = tk.Frame(chart_frame, bg='white')
        inner.pack(fill='both', expand=True, padx=15, pady=12)
        
        # Título
        title = tk.Label(inner, text="📈 Atividades - Últimos 7 dias", 
                        font=('Segoe UI', 11, 'bold'), bg='white', fg=COLORS['primary'])
        title.pack(anchor='w', pady=(0, 10))
        
        # Simulação de gráfico com barras textuais
        days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        values = [12, 8, 15, 20, 18, 5, 3]  # Dados simulados
        
        for day, value in zip(days, values):
            row = tk.Frame(inner, bg='white')
            row.pack(fill='x', pady=1)
            
            tk.Label(row, text=day, font=('Segoe UI', 9), bg='white', fg=COLORS['dark'], width=4).pack(side='left')
            
            # Barra visual
            bar_length = int(value * 8)  # Escala visual
            bar_text = "█" * bar_length
            tk.Label(row, text=bar_text, font=('Segoe UI', 9), bg='white', fg=COLORS['info']).pack(side='left', padx=(5, 0))
            
            tk.Label(row, text=str(value), font=('Segoe UI', 9, 'bold'), bg='white', fg=COLORS['dark']).pack(side='right')
        
        return chart_frame
    
    def create_financial_chart(self, parent):
        """Criar gráfico de status financeiro"""
        
        chart_frame = tk.Frame(parent, bg='white', relief='raised', bd=1)
        inner = tk.Frame(chart_frame, bg='white')
        inner.pack(fill='both', expand=True, padx=15, pady=12)
        
        # Título
        title = tk.Label(inner, text="� Status Financeiro", 
                        font=('Segoe UI', 11, 'bold'), bg='white', fg=COLORS['primary'])
        title.pack(anchor='w', pady=(0, 10))
        
        # Métricas financeiras
        financial_data = [
            ("Receitas", self.get_cached_value('financeiro', 'receitas', 'R$ 0'), COLORS['success']),
            ("Despesas", self.get_cached_value('financeiro', 'despesas', 'R$ 0'), COLORS['danger']),
            ("A Receber", self.get_cached_value('financeiro', 'receber', 'R$ 0'), COLORS['warning']),
            ("A Pagar", self.get_cached_value('financeiro', 'pagar', 'R$ 0'), COLORS['info'])
        ]
        
        for label, value, color in financial_data:
            row = tk.Frame(inner, bg='white')
            row.pack(fill='x', pady=3)
            
            tk.Label(row, text=f"● {label}:", font=('Segoe UI', 9), 
                    bg='white', fg=color).pack(side='left')
            tk.Label(row, text=value, font=('Segoe UI', 9, 'bold'), 
                    bg='white', fg=COLORS['dark']).pack(side='right')
        
        return chart_frame
    
    def create_quick_actions_section(self, parent):
        """Criar seção de ações rápidas"""
        
        actions_frame = tk.Frame(parent, bg=COLORS['background'])
        actions_frame.pack(fill='x', padx=20, pady=(20, 40))
        
        # Título da seção
        section_title = tk.Label(
            actions_frame,
            text="⚡ Ações Rápidas",
            font=('Segoe UI', 14, 'bold'),
            bg=COLORS['background'],
            fg=COLORS['primary']
        )
        section_title.pack(anchor='w', pady=(0, 15))
        
        # Container dos botões
        buttons_frame = tk.Frame(actions_frame, bg=COLORS['background'])
        buttons_frame.pack(fill='x')
        
        # Ações rápidas
        actions = [
            ("➕ Nova OS", self.quick_new_os, COLORS['warning']),
            ("📅 Agendar", self.quick_schedule, COLORS['success']),
            ("💰 Lançamento", self.quick_financial, COLORS['primary']),
            ("📱 Enviar Msg", self.quick_message, COLORS['info']),
            ("📋 Relatório", self.quick_report, COLORS['dark'])
        ]
        
        for i, (text, command, color) in enumerate(actions):
            btn = tk.Button(
                buttons_frame,
                text=text,
                font=('Segoe UI', 10, 'bold'),
                bg=color,
                fg='white',
                relief='flat',
                padx=20,
                pady=8,
                command=command
            )
            btn.grid(row=0, column=i, padx=8, pady=5, sticky='ew')
        
        # Configurar colunas
        for i in range(len(actions)):
            buttons_frame.grid_columnconfigure(i, weight=1)
    
    # =======================================
    # MÉTODOS DE COLETA DE DADOS
    # =======================================
    
    def load_dashboard_data(self):
        """Carregar dados do dashboard em thread separada"""
        def fetch_data():
            try:
                self.fetch_all_metrics()
                self.root.after(0, self.refresh_dashboard_display)
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")
        
        thread = threading.Thread(target=fetch_data, daemon=True)
        thread.start()
    
    def fetch_all_metrics(self):
        """Buscar métricas de todos os módulos"""
        
        # Buscar métricas de cada módulo
        self.fetch_clientes_metrics()
        self.fetch_os_metrics()
        self.fetch_agendamento_metrics()
        self.fetch_financeiro_metrics()
        self.fetch_comunicacao_metrics()
        
        # Atualizar alertas
        self.update_alerts()
    
    def fetch_clientes_metrics(self):
        """Buscar métricas de clientes com cache"""
        try:
            # Tentar cache primeiro
            cached_data = erp_cache.get_clientes()
            if cached_data:
                self.metrics_cache['clientes'] = {
                    'total': str(len(cached_data)),
                    'trend': '+2%'  # Simulado
                }
                return
            
            # Buscar da API se não há cache
            response = requests.get(
                f"{API_BASE_URL}/api/v1/clientes",
                headers=self.headers,
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                clientes = data.get('clientes', [])
                
                # Armazenar no cache
                erp_cache.set_clientes(clientes)
                
                self.metrics_cache['clientes'] = {
                    'total': str(len(clientes)),
                    'trend': '+2%'  # Simulado
                }
        except Exception as e:
            print(f"Erro ao buscar clientes: {e}")
            self.metrics_cache['clientes'] = {'total': '0', 'trend': '0%'}
    
    def fetch_os_metrics(self):
        """Buscar métricas de Ordem de Serviço"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/ordem-servico/dashboard/estatisticas",
                headers=self.headers,
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                self.metrics_cache['os'] = {
                    'abertas': str(data.get('por_status', {}).get('aberta', 0)),
                    'execucao': str(data.get('por_status', {}).get('em_execucao', 0)),
                    'atrasadas': str(data.get('atrasadas', 0)),
                    'concluidas_hoje': str(data.get('concluidas_hoje', 0)),
                    'trend': '+5%'
                }
        except Exception as e:
            print(f"Erro ao buscar OS: {e}")
            self.metrics_cache['os'] = {
                'abertas': '0', 'execucao': '0', 'atrasadas': '0', 
                'concluidas_hoje': '0', 'trend': '0%'
            }
    
    def fetch_agendamento_metrics(self):
        """Buscar métricas de Agendamento"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/agendamento/estatisticas/",
                headers=self.headers,
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                self.metrics_cache['agendamento'] = {
                    'hoje': str(data.get('total_hoje', 0)),
                    'semana': str(data.get('total_semana', 0)),
                    'proximo': data.get('proximo_agendamento', 'N/A'),
                    'disponibilidade': '80%',  # Simulado
                    'trend': '+3%'
                }
        except Exception as e:
            print(f"Erro ao buscar agendamento: {e}")
            self.metrics_cache['agendamento'] = {
                'hoje': '0', 'semana': '0', 'proximo': 'N/A',
                'disponibilidade': 'N/A', 'trend': '0%'
            }
    
    def fetch_financeiro_metrics(self):
        """Buscar métricas Financeiras"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/financeiro/dashboard/resumo",
                headers=self.headers,
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                self.metrics_cache['financeiro'] = {
                    'saldo': f"R$ {data.get('saldo_atual', 0):,.2f}",
                    'receber': f"R$ {data.get('total_receber', 0):,.2f}",
                    'pagar': f"R$ {data.get('total_pagar', 0):,.2f}",
                    'vencidas': str(data.get('contas_vencidas', 0)),
                    'receitas': f"R$ {data.get('receitas_mes', 0):,.2f}",
                    'despesas': f"R$ {data.get('despesas_mes', 0):,.2f}",
                    'trend': '+8%'
                }
        except Exception as e:
            print(f"Erro ao buscar financeiro: {e}")
            self.metrics_cache['financeiro'] = {
                'saldo': 'R$ 0', 'receber': 'R$ 0', 'pagar': 'R$ 0',
                'vencidas': '0', 'receitas': 'R$ 0', 'despesas': 'R$ 0',
                'trend': '0%'
            }
    
    def fetch_comunicacao_metrics(self):
        """Buscar métricas de Comunicação"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/comunicacao/dashboard",
                headers=self.headers,
                timeout=API_TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                self.metrics_cache['comunicacao'] = {
                    'enviadas': str(data.get('comunicacoes_hoje', 0)),
                    'templates': str(data.get('total_templates', 0)),
                    'whatsapp': str(data.get('whatsapp_enviados', 0)),
                    'taxa_sucesso': f"{data.get('taxa_sucesso', 0)}%",
                    'trend': '+12%'
                }
        except Exception as e:
            print(f"Erro ao buscar comunicação: {e}")
            self.metrics_cache['comunicacao'] = {
                'enviadas': '0', 'templates': '0', 'whatsapp': '0',
                'taxa_sucesso': '0%', 'trend': '0%'
            }
    
    def update_alerts(self):
        """Atualizar lista de alertas críticos"""
        self.alerts = []
        
        # Verificar OS atrasadas
        os_atrasadas = int(self.get_cached_value('os', 'atrasadas', '0'))
        if os_atrasadas > 0:
            self.alerts.append({
                'message': f"{os_atrasadas} Ordens de Serviço atrasadas",
                'type': 'danger'
            })
        
        # Verificar contas vencidas
        contas_vencidas = int(self.get_cached_value('financeiro', 'vencidas', '0'))
        if contas_vencidas > 0:
            self.alerts.append({
                'message': f"{contas_vencidas} contas financeiras vencidas",
                'type': 'warning'
            })
        
        # Verificar estoque baixo (simulado)
        if int(self.get_cached_value('estoque', 'baixo', '0')) > 0:
            self.alerts.append({
                'message': "Produtos com estoque baixo detectados",
                'type': 'warning'
            })
    
    def refresh_dashboard_display(self):
        """Atualizar exibição do dashboard com novos dados"""
        # Recriar o dashboard com dados atualizados
        self.show_dashboard()
    
    def start_auto_refresh(self):
        """Iniciar atualização automática do dashboard"""
        def auto_refresh():
            self.load_dashboard_data()
            self.root.after(REFRESH_INTERVAL, auto_refresh)
        
        # Primeira atualização após 5 segundos
        self.root.after(5000, auto_refresh)
    
    # =======================================
    # MÉTODOS DE NAVEGAÇÃO
    # =======================================
    
    def open_ordem_servico(self):
        """Abrir módulo Ordem de Serviço"""
        try:
            from ordem_servico_window import OrdemServicoWindow
            os_window = OrdemServicoWindow(self.root, self.token)
            os_window.run()
        except ImportError:
            messagebox.showinfo("Info", "Módulo Ordem de Serviço será aberto")
    
    def open_agendamento(self):
        """Abrir módulo Agendamento"""
        try:
            from agendamento_window import AgendamentoWindow
            agend_window = AgendamentoWindow(self.root)
            agend_window.run()
        except ImportError:
            messagebox.showinfo("Info", "Módulo Agendamento será aberto")
    
    def open_financeiro(self):
        """Abrir módulo Financeiro"""
        try:
            from financeiro_window import FinanceiroWindow
            fin_window = FinanceiroWindow(self.root, self.token)
            fin_window.run()
        except ImportError:
            messagebox.showinfo("Info", "Módulo Financeiro será aberto")
    
    def open_comunicacao(self):
        """Abrir módulo Comunicação"""
        try:
            from comunicacao_window import ComunicacaoWindow
            com_window = ComunicacaoWindow(self.root, self.token)
            com_window.run()
        except ImportError:
            messagebox.showinfo("Info", "Módulo Comunicação será aberto")
    
    # =======================================
    # AÇÕES RÁPIDAS
    # =======================================
    
    def quick_new_os(self):
        """Ação rápida: Nova OS"""
        messagebox.showinfo(ACTION_MESSAGES['title'], ACTION_MESSAGES['nova_os'])
    
    def quick_schedule(self):
        """Ação rápida: Agendar"""
        messagebox.showinfo(ACTION_MESSAGES['title'], ACTION_MESSAGES['novo_agendamento'])
    
    def quick_financial(self):
        """Ação rápida: Lançamento financeiro"""
        messagebox.showinfo(ACTION_MESSAGES['title'], "Funcionalidade: Novo Lançamento Financeiro")
    
    def quick_message(self):
        """Ação rápida: Enviar mensagem"""
        messagebox.showinfo(ACTION_MESSAGES['title'], "Funcionalidade: Enviar Comunicação")
    
    def quick_report(self):
        """Ação rápida: Gerar relatório"""
        messagebox.showinfo(ACTION_MESSAGES['title'], "Funcionalidade: Gerar Relatório")
    
    # =======================================
    # MÉTODOS AUXILIARES
    # =======================================
    
    def clear_content(self):
        """Limpar área de conteúdo"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_datetime(self):
        """Atualizar data/hora na barra superior"""
        
        now = datetime.now()
        datetime_str = now.strftime("%d/%m/%Y - %H:%M:%S")
        if hasattr(self, 'datetime_label'):
            self.datetime_label.config(text=datetime_str)
        
        # Agendar próxima atualização
        self.root.after(1000, self.update_datetime)
    
    def darken_color(self, color):
        """Escurecer cor para efeito hover"""
        # Simples mapeamento de cores para versões mais escuras
        color_map = {
            "#3498db": "#2980b9",
            "#2ecc71": "#27ae60",
            "#f39c12": "#e67e22",
            "#9b59b6": "#8e44ad",
            "#e67e22": "#d35400",
            "#1abc9c": "#16a085",
            "#95a5a6": "#7f8c8d",
            "#25d366": "#128c7e",
        }
        return color_map.get(color, color)
    
    # === MÉTODOS DE NAVEGAÇÃO ===
    
    def show_clients(self):
        """Mostrar módulo de clientes"""
        
        # Registrar navegação
        if hasattr(self, 'nav_system'):
            self.nav_system.navigate_to('clientes', 'Clientes', {}, self.show_clients)
        
        try:
            # Usar lazy loading para carregar o módulo
            def create_clientes_module():
                from clientes_window import ClientesWindow
                return ClientesWindow
            
            # Registrar factory se não existe
            if not erp_loader.is_registered('clientes'):
                erp_loader.register_factory('clientes', create_clientes_module)
            
            # Carregar módulo lazy
            clientes_class = erp_loader.get_module('clientes')
            clientes_class(self.user_data, self.root)
            
        except ImportError as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao carregar módulo de clientes: {e}"
            )
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir clientes:\n{str(e)}"
            )
    
    def show_products(self):
        """Abrir janela de gerenciamento de produtos com lazy loading"""
        try:
            # Usar lazy loading para carregar o módulo
            def create_produtos_module():
                from produtos_window import ProdutosWindow
                return ProdutosWindow
            
            # Registrar factory se não existe
            if not erp_loader.is_registered('produtos'):
                erp_loader.register_factory('produtos', create_produtos_module)
            
            # Carregar módulo lazy
            produtos_class = erp_loader.get_module('produtos')
            produtos_class(self.user_data, self.root)
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir módulo de produtos:\n{str(e)}"
            )
    
    def show_estoque(self):
        """Abrir janela de controle de estoque"""
        try:
            from estoque_window import EstoqueWindow
            EstoqueWindow(self.user_data, self.root)
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir controle de estoque:\n{str(e)}"
            )
    
    def show_codigo_barras(self):
        """Mostrar gerador de códigos de barras"""
        try:
            from codigo_barras_window import CodigoBarrasWindow
            CodigoBarrasWindow(self.user_data, self.root)
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir gerador de códigos de barras:\n{str(e)}"
            )
    
    def show_orders(self):
        """Mostrar módulo de OS"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="📋 Ordem de Serviço",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title.pack(pady=20)
        
        info_label = tk.Label(
            self.content_frame,
            text="🚧 Módulo planejado para Fase 3",
            font=('Arial', 14),
            bg='white',
            fg='#7f8c8d'
        )
        info_label.pack(pady=10)
    
    def show_financial(self):
        """Mostrar módulo financeiro"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="💰 Módulo Financeiro",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title.pack(pady=20)
        
        info_label = tk.Label(
            self.content_frame,
            text="🚧 Módulo planejado para Fase 4",
            font=('Arial', 14),
            bg='white',
            fg='#7f8c8d'
        )
        info_label.pack(pady=10)
    
    def show_comunicacao(self):
        """Mostrar sistema de comunicação"""
        try:
            from comunicacao_window import ComunicacaoWindow
            ComunicacaoWindow(self.root, self.token)
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir sistema de comunicação:\n{str(e)}"
            )
    
    def show_reports(self):
        """Mostrar módulo de relatórios"""
        try:
            from relatorios_window import RelatoriosWindow
            RelatoriosWindow(self.user_data, self.root)
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir gerador de relatórios:\n{str(e)}"
            )
    
    def show_settings(self):
        """Mostrar configurações"""
        self.clear_content()
        
        title = tk.Label(
            self.content_frame,
            text="⚙️ Configurações",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title.pack(pady=20)
        
        info_label = tk.Label(
            self.content_frame,
            text="🚧 Painel de configurações em desenvolvimento",
            font=('Arial', 14),
            bg='white',
            fg='#7f8c8d'
        )
        info_label.pack(pady=10)
    
    def logout(self):
        """Fazer logout do sistema"""
        
        result = messagebox.askyesno(
            "Confirmar Logout",
            "Deseja realmente sair do sistema?"
        )
        
        if result:
            self.root.quit()
    
    def on_closing(self):
        """Tratar fechamento da janela"""
        
        result = messagebox.askyesno(
            "Fechar Sistema",
            "Deseja realmente fechar o sistema?"
        )
        
        if result:
            self.root.quit()
    
    def run(self):
        """Executar o dashboard"""
        
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
# APLICAÇÃO PRINCIPAL INTEGRADA
# =======================================

def main():
    """Função principal que integra login + dashboard"""
    
    from login_tkinter import LoginWindow
    
    print("=" * 50)
    print("SISTEMA ERP PRIMOTEX - APLICAÇÃO COMPLETA")
    print("=" * 50)
    
    # 1. Tela de Login
    print("🔐 Iniciando tela de login...")
    login_window = LoginWindow()
    user_data = login_window.run()
    
    if not user_data:
        print("❌ Login cancelado")
        return
    
    # 2. Dashboard Principal
    print("📊 Iniciando dashboard...")
    dashboard = DashboardWindow(user_data)
    dashboard.run()
    
    print("👋 Sistema encerrado")

if __name__ == "__main__":
    main()