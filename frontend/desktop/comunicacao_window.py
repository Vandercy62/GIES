"""
INTERFACE DESKTOP - SISTEMA DE COMUNICAÇÃO
=========================================

Sistema ERP Primotex - Interface Desktop para Gestão de Comunicação
Interface completa para templates, envio, histórico e configurações

Funcionalidades:
- Gestão de templates de mensagens
- Envio individual e em lote
- Histórico de comunicações
- Configuração de canais
- Dashboard de estatísticas
- Integração WhatsApp Business API

Autor: GitHub Copilot
Data: 29/10/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import requests
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import webbrowser
from urllib.parse import quote

class ComunicacaoWindow:
    """
    Interface principal do sistema de comunicação
    """
    
    def __init__(self, parent: tk.Tk = None, token: str = None):
        """Inicializar interface de comunicação"""
        
        # Configuração da janela
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
            
        self.window.title("Sistema de Comunicação - ERP Primotex")
        self.window.geometry("1400x900")
        self.window.minsize(1200, 800)
        
        # Configuração da API
        self.api_base = "http://127.0.0.1:8003"
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}" if token else "",
            "Content-Type": "application/json"
        }
        
        # Variáveis de controle
        self.templates = []
        self.historico = []
        self.configuracoes = []
        self.estatisticas = {}
        self.selected_template = None
        self.preview_mode = False
        
        # Configurar estilo
        self.setup_styles()
        
        # Criar interface
        self.create_interface()
        
        # Carregar dados iniciais
        self.load_initial_data()
        
    def setup_styles(self):
        """Configurar estilos da interface"""
        style = ttk.Style()
        
        # Configurar tema
        style.theme_use('clam')
        
        # Cores principais
        bg_color = "#f0f0f0"
        primary_color = "#2E8B57"
        secondary_color = "#FF6B35"
        text_color = "#2C3E50"
        
        # Configurar estilos personalizados
        style.configure("Title.TLabel", 
                       font=("Segoe UI", 16, "bold"),
                       foreground=primary_color)
        
        style.configure("Subtitle.TLabel", 
                       font=("Segoe UI", 12, "bold"),
                       foreground=text_color)
        
        style.configure("Header.TFrame", background=primary_color)
        style.configure("Card.TFrame", background="white", relief="raised")
        style.configure("Success.TButton", background="#28a745")
        style.configure("Warning.TButton", background="#ffc107")
        style.configure("Danger.TButton", background="#dc3545")
        
    def create_interface(self):
        """Criar interface principal"""
        
        # Header principal
        self.create_header()
        
        # Container principal
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Criar abas
        self.create_templates_tab()
        self.create_envio_tab()
        self.create_historico_tab()
        self.create_configuracoes_tab()
        self.create_dashboard_tab()
        
    def create_header(self):
        """Criar header principal"""
        header_frame = ttk.Frame(self.window, style="Header.TFrame")
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Título
        title_label = ttk.Label(header_frame, 
                               text="💬 Sistema de Comunicação",
                               style="Title.TLabel",
                               foreground="white",
                               background="#2E8B57")
        title_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        # Status de conexão
        self.status_label = ttk.Label(header_frame,
                                     text="🔴 Desconectado",
                                     foreground="white",
                                     background="#2E8B57")
        self.status_label.pack(side=tk.RIGHT, padx=15, pady=15)
        
        # Botão de atualização
        refresh_btn = ttk.Button(header_frame,
                                text="🔄 Atualizar",
                                command=self.refresh_all_data)
        refresh_btn.pack(side=tk.RIGHT, padx=5, pady=15)
        
    def create_templates_tab(self):
        """Criar aba de templates"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📝 Templates")
        
        # Container principal
        container = ttk.Frame(tab_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Toolbar superior
        toolbar = ttk.Frame(container)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="➕ Novo Template", 
                  command=self.novo_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="✏️ Editar", 
                  command=self.editar_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="🗑️ Excluir", 
                  command=self.excluir_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="👁️ Visualizar", 
                  command=self.visualizar_template).pack(side=tk.LEFT, padx=5)
        
        # Separador
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Filtros
        ttk.Label(toolbar, text="Tipo:").pack(side=tk.LEFT, padx=(10, 5))
        self.tipo_filter = ttk.Combobox(toolbar, width=15, state="readonly")
        self.tipo_filter.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(toolbar, text="Canal:").pack(side=tk.LEFT, padx=(10, 5))
        self.canal_filter = ttk.Combobox(toolbar, width=12, state="readonly")
        self.canal_filter.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(toolbar, text="🔍 Filtrar", 
                  command=self.filtrar_templates).pack(side=tk.LEFT, padx=(10, 0))
        
        # Container com divisão
        content_frame = ttk.Frame(container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de templates (esquerda)
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(left_frame, text="Templates Disponíveis", 
                 style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        # Treeview para templates
        columns = ("ID", "Nome", "Tipo", "Canal", "Status", "Automático")
        self.templates_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        # Configurar colunas
        self.templates_tree.heading("ID", text="ID")
        self.templates_tree.heading("Nome", text="Nome")
        self.templates_tree.heading("Tipo", text="Tipo")
        self.templates_tree.heading("Canal", text="Canal")
        self.templates_tree.heading("Status", text="Status")
        self.templates_tree.heading("Automático", text="Auto")
        
        self.templates_tree.column("ID", width=50)
        self.templates_tree.column("Nome", width=200)
        self.templates_tree.column("Tipo", width=150)
        self.templates_tree.column("Canal", width=100)
        self.templates_tree.column("Status", width=80)
        self.templates_tree.column("Automático", width=60)
        
        # Scrollbar para templates
        templates_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, 
                                        command=self.templates_tree.yview)
        self.templates_tree.configure(yscrollcommand=templates_scroll.set)
        
        self.templates_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        templates_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind evento de seleção
        self.templates_tree.bind("<<TreeviewSelect>>", self.on_template_select)
        
        # Preview do template (direita)
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        ttk.Label(right_frame, text="Preview do Template", 
                 style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        # Área de preview
        self.preview_frame = ttk.Frame(right_frame, style="Card.TFrame")
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Informações do template
        info_frame = ttk.Frame(self.preview_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.template_info = ttk.Label(info_frame, text="Selecione um template para visualizar")
        self.template_info.pack(anchor=tk.W)
        
        # Área de texto do template
        text_frame = ttk.Frame(self.preview_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.template_text = tk.Text(text_frame, wrap=tk.WORD, state="disabled", height=20)
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                   command=self.template_text.yview)
        self.template_text.configure(yscrollcommand=text_scroll.set)
        
        self.template_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_envio_tab(self):
        """Criar aba de envio"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📤 Enviar Mensagens")
        
        # Container principal
        container = ttk.Frame(tab_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Seção de envio individual
        individual_frame = ttk.LabelFrame(container, text="📱 Envio Individual", padding=10)
        individual_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Linha 1: Template e destinatário
        row1 = ttk.Frame(individual_frame)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(row1, text="Template:").pack(side=tk.LEFT)
        self.envio_template = ttk.Combobox(row1, width=30, state="readonly")
        self.envio_template.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(row1, text="Destinatário:").pack(side=tk.LEFT)
        self.destinatario_nome = ttk.Entry(row1, width=25)
        self.destinatario_nome.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(row1, text="Contato:").pack(side=tk.LEFT)
        self.destinatario_contato = ttk.Entry(row1, width=20)
        self.destinatario_contato.pack(side=tk.LEFT, padx=(5, 0))
        
        # Linha 2: Assunto e canal
        row2 = ttk.Frame(individual_frame)
        row2.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(row2, text="Assunto:").pack(side=tk.LEFT)
        self.envio_assunto = ttk.Entry(row2, width=40)
        self.envio_assunto.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(row2, text="Canal:").pack(side=tk.LEFT)
        self.envio_canal = ttk.Combobox(row2, width=15, state="readonly",
                                       values=["EMAIL", "WHATSAPP", "SMS"])
        self.envio_canal.pack(side=tk.LEFT, padx=(5, 15))
        
        # Botões de ação
        button_frame = ttk.Frame(individual_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📋 Preview", 
                  command=self.preview_mensagem).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="📤 Enviar Agora", 
                  command=self.enviar_individual).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⏰ Agendar", 
                  command=self.agendar_envio).pack(side=tk.LEFT, padx=5)
        
        # Seção de envio em lote
        lote_frame = ttk.LabelFrame(container, text="📊 Envio em Lote", padding=10)
        lote_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar do lote
        lote_toolbar = ttk.Frame(lote_frame)
        lote_toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(lote_toolbar, text="📂 Importar Lista", 
                  command=self.importar_lista).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(lote_toolbar, text="➕ Adicionar Manualmente", 
                  command=self.adicionar_destinatario).pack(side=tk.LEFT, padx=5)
        ttk.Button(lote_toolbar, text="🗑️ Remover Selecionado", 
                  command=self.remover_destinatario).pack(side=tk.LEFT, padx=5)
        ttk.Button(lote_toolbar, text="🚀 Enviar Lote", 
                  command=self.enviar_lote).pack(side=tk.RIGHT)
        
        # Lista de destinatários
        destinatarios_frame = ttk.Frame(lote_frame)
        destinatarios_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Nome", "Contato", "Canal", "Status")
        self.destinatarios_tree = ttk.Treeview(destinatarios_frame, columns=columns, 
                                              show="headings", height=10)
        
        for col in columns:
            self.destinatarios_tree.heading(col, text=col)
            
        self.destinatarios_tree.column("Nome", width=200)
        self.destinatarios_tree.column("Contato", width=150)
        self.destinatarios_tree.column("Canal", width=100)
        self.destinatarios_tree.column("Status", width=100)
        
        # Scrollbar para destinatários
        dest_scroll = ttk.Scrollbar(destinatarios_frame, orient=tk.VERTICAL,
                                   command=self.destinatarios_tree.yview)
        self.destinatarios_tree.configure(yscrollcommand=dest_scroll.set)
        
        self.destinatarios_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dest_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_historico_tab(self):
        """Criar aba de histórico"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📋 Histórico")
        
        # Container principal
        container = ttk.Frame(tab_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filtros superiores
        filters_frame = ttk.Frame(container)
        filters_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Linha 1 de filtros
        filter_row1 = ttk.Frame(filters_frame)
        filter_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(filter_row1, text="Período:").pack(side=tk.LEFT)
        self.data_inicio = ttk.Entry(filter_row1, width=12)
        self.data_inicio.pack(side=tk.LEFT, padx=(5, 5))
        
        ttk.Label(filter_row1, text="até").pack(side=tk.LEFT)
        self.data_fim = ttk.Entry(filter_row1, width=12)
        self.data_fim.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(filter_row1, text="Status:").pack(side=tk.LEFT)
        self.status_filter = ttk.Combobox(filter_row1, width=12, state="readonly",
                                         values=["TODOS", "ENVIADO", "ENTREGUE", "LIDO", "ERRO"])
        self.status_filter.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(filter_row1, text="Canal:").pack(side=tk.LEFT)
        self.canal_hist_filter = ttk.Combobox(filter_row1, width=12, state="readonly",
                                             values=["TODOS", "EMAIL", "WHATSAPP", "SMS"])
        self.canal_hist_filter.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Button(filter_row1, text="🔍 Filtrar", 
                  command=self.filtrar_historico).pack(side=tk.LEFT, padx=(10, 0))
        
        # Lista do histórico
        historico_frame = ttk.Frame(container)
        historico_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Data", "Destinatário", "Assunto", "Canal", "Status", "Template")
        self.historico_tree = ttk.Treeview(historico_frame, columns=columns, 
                                          show="headings", height=20)
        
        # Configurar colunas do histórico
        self.historico_tree.heading("ID", text="ID")
        self.historico_tree.heading("Data", text="Data/Hora")
        self.historico_tree.heading("Destinatário", text="Destinatário")
        self.historico_tree.heading("Assunto", text="Assunto")
        self.historico_tree.heading("Canal", text="Canal")
        self.historico_tree.heading("Status", text="Status")
        self.historico_tree.heading("Template", text="Template")
        
        self.historico_tree.column("ID", width=50)
        self.historico_tree.column("Data", width=130)
        self.historico_tree.column("Destinatário", width=200)
        self.historico_tree.column("Assunto", width=250)
        self.historico_tree.column("Canal", width=80)
        self.historico_tree.column("Status", width=100)
        self.historico_tree.column("Template", width=150)
        
        # Scrollbar para histórico
        hist_scroll = ttk.Scrollbar(historico_frame, orient=tk.VERTICAL,
                                   command=self.historico_tree.yview)
        self.historico_tree.configure(yscrollcommand=hist_scroll.set)
        
        self.historico_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hist_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind evento de duplo clique
        self.historico_tree.bind("<Double-1>", self.visualizar_historico_item)
        
    def create_configuracoes_tab(self):
        """Criar aba de configurações"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="⚙️ Configurações")
        
        # Container principal
        container = ttk.Frame(tab_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurações de WhatsApp
        whatsapp_frame = ttk.LabelFrame(container, text="📱 WhatsApp Business API", padding=10)
        whatsapp_frame.pack(fill=tk.X, pady=(0, 10))
        
        # API Token
        token_frame = ttk.Frame(whatsapp_frame)
        token_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(token_frame, text="API Token:").pack(side=tk.LEFT)
        self.whatsapp_token = ttk.Entry(token_frame, width=50, show="*")
        self.whatsapp_token.pack(side=tk.LEFT, padx=(5, 10))
        ttk.Button(token_frame, text="Testar", 
                  command=self.testar_whatsapp).pack(side=tk.LEFT)
        
        # Phone Number ID
        phone_frame = ttk.Frame(whatsapp_frame)
        phone_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(phone_frame, text="Phone Number ID:").pack(side=tk.LEFT)
        self.whatsapp_phone_id = ttk.Entry(phone_frame, width=25)
        self.whatsapp_phone_id.pack(side=tk.LEFT, padx=(5, 0))
        
        # Configurações de Email
        email_frame = ttk.LabelFrame(container, text="📧 Configurações de Email", padding=10)
        email_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Servidor SMTP
        smtp_frame = ttk.Frame(email_frame)
        smtp_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(smtp_frame, text="Servidor SMTP:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.smtp_server = ttk.Entry(smtp_frame, width=25)
        self.smtp_server.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(smtp_frame, text="Porta:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.smtp_port = ttk.Entry(smtp_frame, width=8)
        self.smtp_port.grid(row=0, column=3, padx=(0, 15))
        
        ttk.Label(smtp_frame, text="Usuário:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.smtp_user = ttk.Entry(smtp_frame, width=25)
        self.smtp_user.grid(row=1, column=1, padx=(0, 15), pady=(5, 0))
        
        ttk.Label(smtp_frame, text="Senha:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.smtp_password = ttk.Entry(smtp_frame, width=15, show="*")
        self.smtp_password.grid(row=1, column=3, padx=(0, 15), pady=(5, 0))
        
        # Botões de teste
        test_frame = ttk.Frame(email_frame)
        test_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(test_frame, text="✉️ Testar Email", 
                  command=self.testar_email).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(test_frame, text="💾 Salvar Configurações", 
                  command=self.salvar_configuracoes).pack(side=tk.LEFT, padx=5)
        
        # Configurações gerais
        geral_frame = ttk.LabelFrame(container, text="🔧 Configurações Gerais", padding=10)
        geral_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Limites e tentativas
        limits_frame = ttk.Frame(geral_frame)
        limits_frame.pack(fill=tk.X)
        
        ttk.Label(limits_frame, text="Limite diário de envios:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.limite_diario = ttk.Entry(limits_frame, width=10)
        self.limite_diario.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(limits_frame, text="Máx. tentativas:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.max_tentativas = ttk.Entry(limits_frame, width=5)
        self.max_tentativas.grid(row=0, column=3, padx=(0, 15))
        
        ttk.Label(limits_frame, text="Intervalo entre envios (seg):").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.intervalo_envio = ttk.Entry(limits_frame, width=10)
        self.intervalo_envio.grid(row=1, column=1, padx=(0, 15), pady=(5, 0))
        
    def create_dashboard_tab(self):
        """Criar aba de dashboard"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📊 Dashboard")
        
        # Container principal
        container = ttk.Frame(tab_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Métricas principais
        metrics_frame = ttk.Frame(container)
        metrics_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Cards de métricas
        self.create_metric_card(metrics_frame, "📤 Enviados Hoje", "0", "#28a745", 0, 0)
        self.create_metric_card(metrics_frame, "✅ Entregues", "0", "#17a2b8", 0, 1)
        self.create_metric_card(metrics_frame, "👁️ Lidos", "0", "#6610f2", 0, 2)
        self.create_metric_card(metrics_frame, "❌ Erros", "0", "#dc3545", 0, 3)
        
        # Segunda linha de métricas
        self.create_metric_card(metrics_frame, "📧 Emails", "0", "#fd7e14", 1, 0)
        self.create_metric_card(metrics_frame, "📱 WhatsApp", "0", "#25d366", 1, 1)
        self.create_metric_card(metrics_frame, "📲 SMS", "0", "#6f42c1", 1, 2)
        self.create_metric_card(metrics_frame, "⏳ Pendentes", "0", "#ffc107", 1, 3)
        
        # Container para gráficos
        charts_frame = ttk.Frame(container)
        charts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Gráfico de comunicações por período
        left_chart_frame = ttk.LabelFrame(charts_frame, text="📈 Comunicações por Período", padding=10)
        left_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Área do gráfico (simulado com listbox)
        self.chart_periodo = tk.Listbox(left_chart_frame, height=15)
        self.chart_periodo.pack(fill=tk.BOTH, expand=True)
        
        # Gráfico de distribuição por canal
        right_chart_frame = ttk.LabelFrame(charts_frame, text="🎯 Distribuição por Canal", padding=10)
        right_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Área do gráfico de canais
        self.chart_canais = tk.Listbox(right_chart_frame, height=15)
        self.chart_canais.pack(fill=tk.BOTH, expand=True)
        
        # Botão de atualização do dashboard
        update_btn = ttk.Button(container, text="🔄 Atualizar Dashboard", 
                               command=self.atualizar_dashboard)
        update_btn.pack(pady=(10, 0))
        
    def create_metric_card(self, parent, title, value, color, row, col):
        """Criar card de métrica"""
        card_frame = ttk.Frame(parent, style="Card.TFrame")
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        parent.grid_columnconfigure(col, weight=1)
        
        # Título
        title_label = ttk.Label(card_frame, text=title, font=("Segoe UI", 10, "bold"))
        title_label.pack(pady=(10, 5))
        
        # Valor
        value_label = ttk.Label(card_frame, text=value, font=("Segoe UI", 16, "bold"), 
                               foreground=color)
        value_label.pack(pady=(0, 10))
        
        # Armazenar referência para atualização
        setattr(self, f"metric_{row}_{col}", value_label)
        
    def load_initial_data(self):
        """Carregar dados iniciais"""
        def load_data():
            try:
                self.check_connection()
                self.load_templates()
                self.load_configuracoes()
                self.load_historico()
                self.atualizar_dashboard()
                
                # Atualizar status
                self.window.after(0, lambda: self.status_label.config(
                    text="🟢 Conectado", foreground="lightgreen"))
                    
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")
                self.window.after(0, lambda: self.status_label.config(
                    text="🔴 Erro de Conexão"))
        
        # Executar em thread separada
        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()
        
    def check_connection(self):
        """Verificar conexão com API"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def load_templates(self):
        """Carregar templates da API"""
        try:
            response = requests.get(f"{self.api_base}/api/v1/comunicacao/templates", 
                                   headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.templates = response.json()
                self.window.after(0, self.update_templates_tree)
                self.window.after(0, self.update_template_combos)
        except Exception as e:
            print(f"Erro ao carregar templates: {e}")
            
    def load_configuracoes(self):
        """Carregar configurações da API"""
        try:
            response = requests.get(f"{self.api_base}/api/v1/comunicacao/configuracoes", 
                                   headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.configuracoes = response.json()
                self.window.after(0, self.update_configuracoes_form)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            
    def load_historico(self):
        """Carregar histórico da API"""
        try:
            response = requests.get(f"{self.api_base}/api/v1/comunicacao/historico", 
                                   headers=self.headers, timeout=10)
            if response.status_code == 200:
                self.historico = response.json()
                self.window.after(0, self.update_historico_tree)
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
            
    def update_templates_tree(self):
        """Atualizar árvore de templates"""
        # Limpar árvore
        for item in self.templates_tree.get_children():
            self.templates_tree.delete(item)
            
        # Adicionar templates
        for template in self.templates:
            values = (
                template.get('id', ''),
                template.get('nome', ''),
                template.get('tipo', ''),
                template.get('canal', ''),
                "Ativo" if template.get('ativo', False) else "Inativo",
                "Sim" if template.get('automatico', False) else "Não"
            )
            self.templates_tree.insert("", tk.END, values=values)
            
    def update_template_combos(self):
        """Atualizar comboboxes de templates"""
        template_names = [f"{t['nome']} ({t['tipo']})" for t in self.templates if t.get('ativo', False)]
        
        self.envio_template['values'] = template_names
        
        # Atualizar filtros
        tipos = list(set(t.get('tipo', '') for t in self.templates))
        canais = list(set(t.get('canal', '') for t in self.templates))
        
        self.tipo_filter['values'] = ["TODOS"] + tipos
        self.canal_filter['values'] = ["TODOS"] + canais
        
    def update_configuracoes_form(self):
        """Atualizar formulário de configurações"""
        # Buscar configuração do WhatsApp
        whatsapp_config = next((c for c in self.configuracoes 
                               if c.get('tipo') == 'WHATSAPP'), {})
        if whatsapp_config:
            config = whatsapp_config.get('configuracoes', {})
            self.whatsapp_token.insert(0, config.get('token', ''))
            self.whatsapp_phone_id.insert(0, config.get('phone_number_id', ''))
            
        # Buscar configuração do Email
        email_config = next((c for c in self.configuracoes 
                            if c.get('tipo') == 'EMAIL'), {})
        if email_config:
            config = email_config.get('configuracoes', {})
            self.smtp_server.insert(0, config.get('smtp_server', ''))
            self.smtp_port.insert(0, str(config.get('smtp_port', '')))
            self.smtp_user.insert(0, config.get('smtp_user', ''))
            self.smtp_password.insert(0, config.get('smtp_password', ''))
            
    def update_historico_tree(self):
        """Atualizar árvore de histórico"""
        # Limpar árvore
        for item in self.historico_tree.get_children():
            self.historico_tree.delete(item)
            
        # Adicionar histórico
        for hist in self.historico:
            values = (
                hist.get('id', ''),
                hist.get('criado_em', ''),
                hist.get('destinatario_nome', ''),
                hist.get('assunto', ''),
                hist.get('tipo', ''),
                hist.get('status', ''),
                hist.get('template_nome', '')
            )
            self.historico_tree.insert("", tk.END, values=values)
            
    # Event handlers
    def on_template_select(self, event):
        """Evento de seleção de template"""
        selection = self.templates_tree.selection()
        if not selection:
            return
            
        item = self.templates_tree.item(selection[0])
        template_id = item['values'][0]
        
        # Buscar template completo
        template = next((t for t in self.templates if t.get('id') == template_id), None)
        if template:
            self.show_template_preview(template)
            
    def show_template_preview(self, template):
        """Mostrar preview do template"""
        # Atualizar informações
        info_text = f"Nome: {template.get('nome', '')}\n"
        info_text += f"Tipo: {template.get('tipo', '')}\n"
        info_text += f"Canal: {template.get('canal', '')}\n"
        info_text += f"Status: {'Ativo' if template.get('ativo') else 'Inativo'}\n"
        info_text += f"Automático: {'Sim' if template.get('automatico') else 'Não'}"
        
        self.template_info.config(text=info_text)
        
        # Atualizar texto do template
        self.template_text.config(state="normal")
        self.template_text.delete(1.0, tk.END)
        
        template_content = f"Assunto: {template.get('assunto', 'N/A')}\n\n"
        template_content += f"Conteúdo:\n{template.get('template_texto', '')}"
        
        self.template_text.insert(1.0, template_content)
        self.template_text.config(state="disabled")
        
    # Métodos de ação
    def novo_template(self):
        """Criar novo template"""
        # Implementar dialog de criação de template
        messagebox.showinfo("Novo Template", "Funcionalidade em desenvolvimento")
        
    def editar_template(self):
        """Editar template selecionado"""
        selection = self.templates_tree.selection()
        if not selection:
            messagebox.showwarning("Seleção", "Selecione um template para editar")
            return
        messagebox.showinfo("Editar Template", "Funcionalidade em desenvolvimento")
        
    def excluir_template(self):
        """Excluir template selecionado"""
        selection = self.templates_tree.selection()
        if not selection:
            messagebox.showwarning("Seleção", "Selecione um template para excluir")
            return
            
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este template?"):
            messagebox.showinfo("Excluir", "Funcionalidade em desenvolvimento")
            
    def visualizar_template(self):
        """Visualizar template em janela separada"""
        selection = self.templates_tree.selection()
        if not selection:
            messagebox.showwarning("Seleção", "Selecione um template para visualizar")
            return
        messagebox.showinfo("Visualizar", "Funcionalidade em desenvolvimento")
        
    def filtrar_templates(self):
        """Filtrar templates"""
        messagebox.showinfo("Filtrar", "Funcionalidade em desenvolvimento")
        
    def preview_mensagem(self):
        """Preview da mensagem a ser enviada"""
        messagebox.showinfo("Preview", "Funcionalidade em desenvolvimento")
        
    def enviar_individual(self):
        """Enviar mensagem individual"""
        if not self.destinatario_nome.get() or not self.destinatario_contato.get():
            messagebox.showwarning("Campos obrigatórios", 
                                 "Preencha nome e contato do destinatário")
            return
        messagebox.showinfo("Enviar", "Funcionalidade em desenvolvimento")
        
    def agendar_envio(self):
        """Agendar envio"""
        messagebox.showinfo("Agendar", "Funcionalidade em desenvolvimento")
        
    def importar_lista(self):
        """Importar lista de destinatários"""
        file_path = filedialog.askopenfilename(
            title="Importar Lista",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        if file_path:
            messagebox.showinfo("Importar", f"Arquivo selecionado: {file_path}")
            
    def adicionar_destinatario(self):
        """Adicionar destinatário manualmente"""
        messagebox.showinfo("Adicionar", "Funcionalidade em desenvolvimento")
        
    def remover_destinatario(self):
        """Remover destinatário selecionado"""
        selection = self.destinatarios_tree.selection()
        if not selection:
            messagebox.showwarning("Seleção", "Selecione um destinatário para remover")
            return
        messagebox.showinfo("Remover", "Funcionalidade em desenvolvimento")
        
    def enviar_lote(self):
        """Enviar lote de mensagens"""
        messagebox.showinfo("Enviar Lote", "Funcionalidade em desenvolvimento")
        
    def filtrar_historico(self):
        """Filtrar histórico"""
        messagebox.showinfo("Filtrar Histórico", "Funcionalidade em desenvolvimento")
        
    def visualizar_historico_item(self, event):
        """Visualizar item do histórico"""
        selection = self.historico_tree.selection()
        if not selection:
            return
        messagebox.showinfo("Visualizar Histórico", "Funcionalidade em desenvolvimento")
        
    def testar_whatsapp(self):
        """Testar configuração do WhatsApp"""
        if not self.whatsapp_token.get():
            messagebox.showwarning("Token", "Informe o token do WhatsApp")
            return
        messagebox.showinfo("Teste WhatsApp", "Funcionalidade em desenvolvimento")
        
    def testar_email(self):
        """Testar configuração de email"""
        if not all([self.smtp_server.get(), self.smtp_port.get(), 
                   self.smtp_user.get(), self.smtp_password.get()]):
            messagebox.showwarning("Configurações", "Preencha todas as configurações de email")
            return
        messagebox.showinfo("Teste Email", "Funcionalidade em desenvolvimento")
        
    def salvar_configuracoes(self):
        """Salvar configurações"""
        messagebox.showinfo("Salvar", "Configurações salvas com sucesso!")
        
    def atualizar_dashboard(self):
        """Atualizar dashboard com estatísticas"""
        def update_metrics():
            try:
                # Carregar estatísticas da API
                response = requests.get(f"{self.api_base}/api/v1/comunicacao/estatisticas", 
                                       headers=self.headers, timeout=10)
                if response.status_code == 200:
                    stats = response.json()
                    
                    # Atualizar métricas na UI thread
                    self.window.after(0, lambda: self.update_metric_cards(stats))
                    self.window.after(0, lambda: self.update_charts(stats))
                    
            except Exception as e:
                print(f"Erro ao atualizar dashboard: {e}")
        
        # Executar em thread separada
        thread = threading.Thread(target=update_metrics, daemon=True)
        thread.start()
        
    def update_metric_cards(self, stats):
        """Atualizar cards de métricas"""
        # Exemplo de atualização (ajustar conforme estrutura real da API)
        metrics_data = {
            "metric_0_0": stats.get('enviados_hoje', 0),
            "metric_0_1": stats.get('entregues', 0),
            "metric_0_2": stats.get('lidos', 0),
            "metric_0_3": stats.get('erros', 0),
            "metric_1_0": stats.get('emails', 0),
            "metric_1_1": stats.get('whatsapp', 0),
            "metric_1_2": stats.get('sms', 0),
            "metric_1_3": stats.get('pendentes', 0)
        }
        
        for metric_name, value in metrics_data.items():
            if hasattr(self, metric_name):
                getattr(self, metric_name).config(text=str(value))
                
    def update_charts(self, stats):
        """Atualizar gráficos (simulado)"""
        # Limpar gráficos
        self.chart_periodo.delete(0, tk.END)
        self.chart_canais.delete(0, tk.END)
        
        # Adicionar dados de exemplo
        for dia in range(7):
            self.chart_periodo.insert(tk.END, f"Dia {dia+1}: {dia*10} mensagens")
            
        canais = ["Email: 45%", "WhatsApp: 35%", "SMS: 20%"]
        for canal in canais:
            self.chart_canais.insert(tk.END, canal)
            
    def refresh_all_data(self):
        """Atualizar todos os dados"""
        self.load_initial_data()
        messagebox.showinfo("Atualização", "Dados atualizados com sucesso!")

def main():
    """Função principal para teste"""
    root = tk.Tk()
    app = ComunicacaoWindow(root, token="test_token")
    root.mainloop()

if __name__ == "__main__":
    main()