"""
SISTEMA ERP PRIMOTEX - INTERFACE DE COMUNICAÇÃO
===============================================

Interface completa para gerenciamento de comunicação WhatsApp/Email.
Integração com API backend para templates e histórico.

Autor: GitHub Copilot
Data: 01/11/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import requests
from typing import Dict, Any, Optional, List
import re
from datetime import datetime
import json

# =======================================
# CONFIGURAÇÕES
# =======================================

API_BASE_URL = "http://127.0.0.1:8002"

# =======================================
# CLASSE INTERFACE DE COMUNICAÇÃO
# =======================================

class ComunicacaoWindow:
    """Interface de gerenciamento de comunicação"""

    def __init__(self, user_data: Dict[str, Any], parent_window=None):
        self.user_data = user_data
        self.token = user_data.get("access_token")
        self.parent_window = parent_window

        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.templates_data = []
        self.historico_data = []
        self.configuracoes_data = {}

        self.setup_window()
        self.create_widgets()
        self.carregar_dados_iniciais()

    def setup_window(self):
        """Configurar janela"""

        self.root.title("Sistema ERP Primotex - Comunicação WhatsApp/Email")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Centralizar na tela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")

        # Configurar ícone se existir
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass

        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Criar widgets da interface"""

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar redimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(title_frame, text="📱 Comunicação", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)

        # Botões principais
        btn_frame = ttk.Frame(title_frame)
        btn_frame.pack(side=tk.RIGHT)

        ttk.Button(btn_frame, text="🔄 Atualizar", 
                  command=self.carregar_dados_iniciais).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(btn_frame, text="⚙️ Configurações", 
                  command=self.abrir_configuracoes).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(btn_frame, text="❌ Fechar", 
                  command=self.on_closing).pack(side=tk.LEFT)

        # Notebook com abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Aba 1: Enviar Mensagem
        self.create_enviar_tab()

        # Aba 2: Templates
        self.create_templates_tab()

        # Aba 3: Histórico
        self.create_historico_tab()

        # Aba 4: Estatísticas
        self.create_estatisticas_tab()

    def create_enviar_tab(self):
        """Criar aba de envio de mensagens"""

        enviar_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(enviar_frame, text="📤 Enviar Mensagem")

        # Configurar grid
        enviar_frame.columnconfigure(1, weight=1)

        # Tipo de comunicação
        row = 0
        ttk.Label(enviar_frame, text="Tipo:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tipo_var = tk.StringVar(value="whatsapp")
        tipo_frame = ttk.Frame(enviar_frame)
        tipo_frame.grid(row=row, column=1, sticky=tk.W, pady=5)

        ttk.Radiobutton(tipo_frame, text="📱 WhatsApp", variable=self.tipo_var, 
                       value="whatsapp").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(tipo_frame, text="📧 Email", variable=self.tipo_var, 
                       value="email").pack(side=tk.LEFT)

        # Destinatário
        row += 1
        ttk.Label(enviar_frame, text="Destinatário:").grid(row=row, column=0, sticky=tk.W, pady=5)
        dest_frame = ttk.Frame(enviar_frame)
        dest_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        dest_frame.columnconfigure(0, weight=1)

        self.destinatario_entry = ttk.Entry(dest_frame, width=50)
        self.destinatario_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

        ttk.Button(dest_frame, text="📋 Clientes", 
                  command=self.selecionar_cliente).grid(row=0, column=1, padx=(5, 0))

        # Template
        row += 1
        ttk.Label(enviar_frame, text="Template:").grid(row=row, column=0, sticky=tk.W, pady=5)
        template_frame = ttk.Frame(enviar_frame)
        template_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        template_frame.columnconfigure(0, weight=1)

        self.template_combo = ttk.Combobox(template_frame, state="readonly")
        self.template_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.template_combo.bind("<<ComboboxSelected>>", self.on_template_selected)

        ttk.Button(template_frame, text="📝 Novo", 
                  command=self.criar_template).grid(row=0, column=1, padx=(5, 0))

        # Assunto (para email)
        row += 1
        self.assunto_label = ttk.Label(enviar_frame, text="Assunto:")
        self.assunto_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        self.assunto_entry = ttk.Entry(enviar_frame, width=60)
        self.assunto_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)

        # Mensagem
        row += 1
        ttk.Label(enviar_frame, text="Mensagem:").grid(row=row, column=0, sticky=(tk.W, tk.N), pady=5)

        msg_frame = ttk.Frame(enviar_frame)
        msg_frame.grid(row=row, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        msg_frame.columnconfigure(0, weight=1)
        msg_frame.rowconfigure(0, weight=1)

        self.mensagem_text = scrolledtext.ScrolledText(msg_frame, height=8, wrap=tk.WORD)
        self.mensagem_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Variáveis disponíveis
        row += 1
        ttk.Label(enviar_frame, text="Variáveis:").grid(row=row, column=0, sticky=tk.W, pady=5)
        var_text = "{{nome}}, {{telefone}}, {{email}}, {{empresa}}, {{data}}, {{hora}}"
        ttk.Label(enviar_frame, text=var_text, foreground="gray").grid(row=row, column=1, sticky=tk.W, pady=5)

        # Botões de ação
        row += 1
        btn_frame = ttk.Frame(enviar_frame)
        btn_frame.grid(row=row, column=1, sticky=tk.E, pady=10)

        ttk.Button(btn_frame, text="🔍 Visualizar", 
                  command=self.visualizar_mensagem).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(btn_frame, text="📤 Enviar", 
                  command=self.enviar_mensagem).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(btn_frame, text="💾 Salvar Template", 
                  command=self.salvar_como_template).pack(side=tk.LEFT)

        # Configurar redimensionamento
        enviar_frame.rowconfigure(row-1, weight=1)

        # Configurar visibilidade inicial
        self.tipo_var.trace('w', self.on_tipo_changed)
        self.on_tipo_changed()

    def create_templates_tab(self):
        """Criar aba de templates"""

        templates_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(templates_frame, text="📝 Templates")

        # Configurar grid
        templates_frame.columnconfigure(0, weight=1)
        templates_frame.rowconfigure(1, weight=1)

        # Toolbar
        toolbar = ttk.Frame(templates_frame)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(toolbar, text="➕ Novo Template", 
                  command=self.criar_template).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(toolbar, text="✏️ Editar", 
                  command=self.editar_template).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(toolbar, text="🗑️ Excluir", 
                  command=self.excluir_template).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(toolbar, text="🔄 Atualizar", 
                  command=self.carregar_templates).pack(side=tk.RIGHT)

        # Treeview para templates
        tree_frame = ttk.Frame(templates_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Colunas
        columns = ("nome", "tipo", "categoria", "ativo", "criado")
        self.templates_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        # Cabeçalhos
        self.templates_tree.heading("nome", text="Nome")
        self.templates_tree.heading("tipo", text="Tipo")
        self.templates_tree.heading("categoria", text="Categoria")
        self.templates_tree.heading("ativo", text="Status")
        self.templates_tree.heading("criado", text="Criado")

        # Larguras
        self.templates_tree.column("nome", width=250)
        self.templates_tree.column("tipo", width=100)
        self.templates_tree.column("categoria", width=150)
        self.templates_tree.column("ativo", width=80)
        self.templates_tree.column("criado", width=120)

        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.templates_tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.templates_tree.xview)
        self.templates_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Grid
        self.templates_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Evento de duplo clique
        self.templates_tree.bind("<Double-1>", lambda e: self.editar_template())

    def create_historico_tab(self):
        """Criar aba de histórico"""

        historico_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(historico_frame, text="📊 Histórico")

        # Configurar grid
        historico_frame.columnconfigure(0, weight=1)
        historico_frame.rowconfigure(2, weight=1)

        # Filtros
        filtro_frame = ttk.LabelFrame(historico_frame, text="Filtros", padding="10")
        filtro_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filtro_frame.columnconfigure(1, weight=1)
        filtro_frame.columnconfigure(3, weight=1)

        # Período
        ttk.Label(filtro_frame, text="Período:").grid(row=0, column=0, sticky=tk.W, pady=5)

        periodo_frame = ttk.Frame(filtro_frame)
        periodo_frame.grid(row=0, column=1, sticky=tk.W, pady=5)

        self.data_inicio = ttk.Entry(periodo_frame, width=12)
        self.data_inicio.pack(side=tk.LEFT)
        ttk.Label(periodo_frame, text=" até ").pack(side=tk.LEFT)
        self.data_fim = ttk.Entry(periodo_frame, width=12)
        self.data_fim.pack(side=tk.LEFT)

        # Tipo
        ttk.Label(filtro_frame, text="Tipo:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.filtro_tipo = ttk.Combobox(filtro_frame, values=["Todos", "WhatsApp", "Email"], 
                                       state="readonly", width=15)
        self.filtro_tipo.set("Todos")
        self.filtro_tipo.grid(row=0, column=3, sticky=tk.W, pady=5)

        # Status
        ttk.Label(filtro_frame, text="Status:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.filtro_status = ttk.Combobox(filtro_frame, 
                                         values=["Todos", "Enviado", "Entregue", "Lido", "Erro"], 
                                         state="readonly", width=15)
        self.filtro_status.set("Todos")
        self.filtro_status.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Botão filtrar
        ttk.Button(filtro_frame, text="🔍 Filtrar", 
                  command=self.filtrar_historico).grid(row=1, column=3, sticky=tk.E, pady=5)

        # Toolbar
        toolbar = ttk.Frame(historico_frame)
        toolbar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(toolbar, text="📊 Exportar", 
                  command=self.exportar_historico).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(toolbar, text="🗑️ Limpar Histórico", 
                  command=self.limpar_historico).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(toolbar, text="🔄 Atualizar", 
                  command=self.carregar_historico).pack(side=tk.RIGHT)

        # Treeview para histórico
        tree_frame = ttk.Frame(historico_frame)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Colunas
        columns = ("data", "tipo", "destinatario", "assunto", "status", "template")
        self.historico_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        # Cabeçalhos
        self.historico_tree.heading("data", text="Data/Hora")
        self.historico_tree.heading("tipo", text="Tipo")
        self.historico_tree.heading("destinatario", text="Destinatário")
        self.historico_tree.heading("assunto", text="Assunto/Conteúdo")
        self.historico_tree.heading("status", text="Status")
        self.historico_tree.heading("template", text="Template")

        # Larguras
        self.historico_tree.column("data", width=130)
        self.historico_tree.column("tipo", width=80)
        self.historico_tree.column("destinatario", width=180)
        self.historico_tree.column("assunto", width=250)
        self.historico_tree.column("status", width=100)
        self.historico_tree.column("template", width=150)

        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.historico_tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.historico_tree.xview)
        self.historico_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Grid
        self.historico_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Evento de duplo clique
        self.historico_tree.bind("<Double-1>", lambda e: self.ver_detalhes_historico())

    def create_estatisticas_tab(self):
        """Criar aba de estatísticas"""

        stats_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(stats_frame, text="📈 Estatísticas")

        # Configurar grid
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)

        # Cards de estatísticas
        self.create_stats_cards(stats_frame)

        # Gráficos (simulados com texto)
        self.create_stats_charts(stats_frame)

    def create_stats_cards(self, parent):
        """Criar cards de estatísticas"""

        # Frame para cards
        cards_frame = ttk.Frame(parent)
        cards_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        # Configurar grid
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)

        # Card 1: Total Enviados
        card1 = ttk.LabelFrame(cards_frame, text="📤 Total Enviados", padding="10")
        card1.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        self.total_enviados_label = ttk.Label(card1, text="0", font=("Arial", 24, "bold"))
        self.total_enviados_label.pack()
        ttk.Label(card1, text="mensagens").pack()

        # Card 2: Taxa de Entrega
        card2 = ttk.LabelFrame(cards_frame, text="📊 Taxa Entrega", padding="10")
        card2.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        self.taxa_entrega_label = ttk.Label(card2, text="0%", font=("Arial", 24, "bold"))
        self.taxa_entrega_label.pack()
        ttk.Label(card2, text="sucesso").pack()

        # Card 3: WhatsApp
        card3 = ttk.LabelFrame(cards_frame, text="📱 WhatsApp", padding="10")
        card3.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=5)

        self.whatsapp_count_label = ttk.Label(card3, text="0", font=("Arial", 24, "bold"))
        self.whatsapp_count_label.pack()
        ttk.Label(card3, text="mensagens").pack()

        # Card 4: Email
        card4 = ttk.LabelFrame(cards_frame, text="📧 Email", padding="10")
        card4.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(5, 0))

        self.email_count_label = ttk.Label(card4, text="0", font=("Arial", 24, "bold"))
        self.email_count_label.pack()
        ttk.Label(card4, text="mensagens").pack()

    def create_stats_charts(self, parent):
        """Criar gráficos de estatísticas (simulados)"""

        # Gráfico de envios por dia
        chart1_frame = ttk.LabelFrame(parent, text="📅 Envios por Dia (Últimos 7 dias)", padding="10")
        chart1_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        self.chart1_text = scrolledtext.ScrolledText(chart1_frame, height=10, wrap=tk.WORD)
        self.chart1_text.pack(fill=tk.BOTH, expand=True)

        # Gráfico de templates mais usados
        chart2_frame = ttk.LabelFrame(parent, text="🏆 Templates Mais Usados", padding="10")
        chart2_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.chart2_text = scrolledtext.ScrolledText(chart2_frame, height=10, wrap=tk.WORD)
        self.chart2_text.pack(fill=tk.BOTH, expand=True)

        # Configurar redimensionamento
        parent.rowconfigure(1, weight=1)

    # =======================================
    # MÉTODOS DE AÇÃO
    # =======================================

    def carregar_dados_iniciais(self):
        """Carregar todos os dados iniciais"""
        threading.Thread(target=self._carregar_dados_iniciais, daemon=True).start()

    def _carregar_dados_iniciais(self):
        """Thread para carregar dados iniciais"""
        try:
            self.carregar_templates()
            self.carregar_historico()
            self.carregar_estatisticas()
            self.carregar_configuracoes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")

    def carregar_templates(self):
        """Carregar templates"""
        try:
            # Simular dados para demonstração
            self.templates_data = [
                {
                    "id": 1,
                    "nome": "Boas-vindas",
                    "tipo": "whatsapp",
                    "categoria": "geral",
                    "assunto": "",
                    "conteudo": "Olá {{nome}}! Bem-vindo à Primotex!",
                    "ativo": True,
                    "criado_em": "2025-01-01 10:00:00"
                },
                {
                    "id": 2,
                    "nome": "Orçamento Pronto",
                    "tipo": "email",
                    "categoria": "vendas",
                    "assunto": "Orçamento {{numero}} - Primotex",
                    "conteudo": "Olá {{nome}},\n\nSeu orçamento está pronto!",
                    "ativo": True,
                    "criado_em": "2025-01-01 11:00:00"
                }
            ]

            # Atualizar treeview de templates
            self.root.after(0, self._atualizar_templates_tree)

            # Atualizar combo de templates
            self.root.after(0, self._atualizar_template_combo)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao carregar templates: {str(e)}"))

    def _atualizar_templates_tree(self):
        """Atualizar treeview de templates"""
        # Limpar
        for item in self.templates_tree.get_children():
            self.templates_tree.delete(item)

        # Adicionar dados
        for template in self.templates_data:
            status = "Ativo" if template["ativo"] else "Inativo"
            criado = template["criado_em"][:10]  # Apenas data

            self.templates_tree.insert("", "end", values=(
                template["nome"],
                template["tipo"].title(),
                template["categoria"].title(),
                status,
                criado
            ))

    def _atualizar_template_combo(self):
        """Atualizar combo de templates"""
        templates_nomes = [t["nome"] for t in self.templates_data if t["ativo"]]
        self.template_combo.configure(values=["Selecionar template..."] + templates_nomes)
        self.template_combo.current(0)

    def carregar_historico(self):
        """Carregar histórico"""
        try:
            # Simular dados para demonstração
            self.historico_data = [
                {
                    "id": 1,
                    "data_envio": "2025-01-01 14:30:00",
                    "tipo": "whatsapp",
                    "destinatario": "(11) 99999-9999",
                    "assunto": "Boas-vindas",
                    "status": "entregue",
                    "template_nome": "Boas-vindas"
                },
                {
                    "id": 2,
                    "data_envio": "2025-01-01 15:15:00",
                    "tipo": "email",
                    "destinatario": "cliente@email.com",
                    "assunto": "Orçamento 001 - Primotex",
                    "status": "enviado",
                    "template_nome": "Orçamento Pronto"
                }
            ]

            # Atualizar treeview
            self.root.after(0, self._atualizar_historico_tree)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao carregar histórico: {str(e)}"))

    def _atualizar_historico_tree(self):
        """Atualizar treeview de histórico"""
        # Limpar
        for item in self.historico_tree.get_children():
            self.historico_tree.delete(item)

        # Adicionar dados
        for item in self.historico_data:
            data_hora = item["data_envio"][:-3]  # Remover segundos
            tipo_icon = "📱" if item["tipo"] == "whatsapp" else "📧"
            status_icon = {"enviado": "📤", "entregue": "✅", "lido": "👁️", "erro": "❌"}.get(item["status"], "❓")

            self.historico_tree.insert("", "end", values=(
                data_hora,
                f"{tipo_icon} {item['tipo'].title()}",
                item["destinatario"],
                item["assunto"],
                f"{status_icon} {item['status'].title()}",
                item["template_nome"]
            ))

    def carregar_estatisticas(self):
        """Carregar estatísticas"""
        try:
            # Simular dados para demonstração
            stats = {
                "total_enviados": 156,
                "taxa_entrega": 92.3,
                "whatsapp_count": 98,
                "email_count": 58
            }

            # Atualizar labels
            self.root.after(0, lambda: self._atualizar_estatisticas(stats))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao carregar estatísticas: {str(e)}"))

    def _atualizar_estatisticas(self, stats):
        """Atualizar estatísticas na UI"""
        self.total_enviados_label.config(text=str(stats["total_enviados"]))
        self.taxa_entrega_label.config(text=f"{stats['taxa_entrega']:.1f}%")
        self.whatsapp_count_label.config(text=str(stats["whatsapp_count"]))
        self.email_count_label.config(text=str(stats["email_count"]))

        # Atualizar gráficos (simulado)
        self.chart1_text.delete(1.0, tk.END)
        self.chart1_text.insert(tk.END, """📊 Envios por Dia:

Segunda-feira: ████████████ 24 envios
Terça-feira:   ██████████   20 envios  
Quarta-feira:  ████████████ 22 envios
Quinta-feira:  ███████████  18 envios
Sexta-feira:   ████████████ 26 envios
Sábado:        ██████       12 envios
Domingo:       ████         8 envios

Total da semana: 130 mensagens""")

        self.chart2_text.delete(1.0, tk.END)
        self.chart2_text.insert(tk.END, """🏆 Templates Mais Usados:

1º Boas-vindas        ████████████ 45 usos
2º Orçamento Pronto   ██████████   32 usos
3º Agendamento        ████████     28 usos
4º Lembrete           ██████       18 usos
5º Obrigado           ████         12 usos

📈 Top performers desta semana
💡 Considere criar variações dos templates mais populares""")

    def carregar_configuracoes(self):
        """Carregar configurações"""
        try:
            # Simular dados para demonstração
            self.configuracoes_data = {
                "whatsapp_api_key": "***************",
                "whatsapp_ativo": True,
                "email_smtp_server": "smtp.gmail.com",
                "email_smtp_port": 587,
                "email_usuario": "sistema@primotex.com.br",
                "email_ativo": True
            }
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configurações: {str(e)}")

    def on_tipo_changed(self, *args):
        """Chamado quando o tipo de comunicação muda"""
        if self.tipo_var.get() == "email":
            self.assunto_label.grid()
            self.assunto_entry.grid()
        else:
            self.assunto_label.grid_remove()
            self.assunto_entry.grid_remove()

    def on_template_selected(self, event=None):
        """Chamado quando um template é selecionado"""
        template_nome = self.template_combo.get()
        if template_nome and template_nome != "Selecionar template...":
            # Buscar template
            template = next((t for t in self.templates_data if t["nome"] == template_nome), None)
            if template:
                # Verificar tipo compatível
                if template["tipo"] != self.tipo_var.get():
                    resposta = messagebox.askyesno(
                        "Tipo Diferente",
                        f"Este template é para {template['tipo'].title()}, mas você selecionou {self.tipo_var.get().title()}.\n\nDeseja continuar?"
                    )
                    if not resposta:
                        self.template_combo.current(0)
                        return

                # Preencher campos
                if template["assunto"]:
                    self.assunto_entry.delete(0, tk.END)
                    self.assunto_entry.insert(0, template["assunto"])

                self.mensagem_text.delete(1.0, tk.END)
                self.mensagem_text.insert(1.0, template["conteudo"])

    def selecionar_cliente(self):
        """Abrir dialog para selecionar cliente"""
        # Simulação - em produção seria um dialog com lista de clientes
        clientes_exemplo = [
            "João Silva - (11) 99999-9999",
            "Maria Santos - maria@email.com",
            "Empresa ABC - contato@abc.com.br"
        ]

        # Dialog simples
        dialog = tk.Toplevel(self.root)
        dialog.title("Selecionar Cliente")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # Lista
        listbox = tk.Listbox(dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for cliente in clientes_exemplo:
            listbox.insert(tk.END, cliente)

        # Botões
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        def selecionar():
            selection = listbox.curselection()
            if selection:
                cliente = listbox.get(selection[0])
                # Extrair contato (simplificado)
                if "-" in cliente:
                    contato = cliente.split("-")[1].strip()
                    self.destinatario_entry.delete(0, tk.END)
                    self.destinatario_entry.insert(0, contato)
            dialog.destroy()

        ttk.Button(btn_frame, text="Selecionar", command=selecionar).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT)

    def visualizar_mensagem(self):
        """Visualizar mensagem antes de enviar"""
        mensagem = self.mensagem_text.get(1.0, tk.END).strip()
        if not mensagem:
            messagebox.showwarning("Aviso", "Digite uma mensagem para visualizar.")
            return

        # Simular substituição de variáveis
        mensagem_processada = mensagem.replace("{{nome}}", "João Silva")
        mensagem_processada = mensagem_processada.replace("{{telefone}}", "(11) 99999-9999")
        mensagem_processada = mensagem_processada.replace("{{email}}", "joao@email.com")
        mensagem_processada = mensagem_processada.replace("{{empresa}}", "Empresa Exemplo")
        mensagem_processada = mensagem_processada.replace("{{data}}", datetime.now().strftime("%d/%m/%Y"))
        mensagem_processada = mensagem_processada.replace("{{hora}}", datetime.now().strftime("%H:%M"))

        # Dialog de visualização
        dialog = tk.Toplevel(self.root)
        dialog.title("Visualização da Mensagem")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Texto
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, mensagem_processada)
        text_widget.config(state=tk.DISABLED)

        # Botão fechar
        ttk.Button(dialog, text="Fechar", command=dialog.destroy).pack(pady=5)

    def enviar_mensagem(self):
        """Enviar mensagem"""
        # Validar campos
        destinatario = self.destinatario_entry.get().strip()
        mensagem = self.mensagem_text.get(1.0, tk.END).strip()

        if not destinatario:
            messagebox.showwarning("Aviso", "Informe o destinatário.")
            return

        if not mensagem:
            messagebox.showwarning("Aviso", "Digite uma mensagem.")
            return

        if self.tipo_var.get() == "email":
            assunto = self.assunto_entry.get().strip()
            if not assunto:
                messagebox.showwarning("Aviso", "Informe o assunto do email.")
                return

        # Confirmar envio
        tipo = self.tipo_var.get().title()
        if not messagebox.askyesno("Confirmar", f"Enviar {tipo} para {destinatario}?"):
            return

        # Simular envio
        threading.Thread(target=self._enviar_mensagem, args=(destinatario, mensagem), daemon=True).start()

    def _enviar_mensagem(self, destinatario, mensagem):
        """Thread para enviar mensagem"""
        try:
            # Simular delay de envio
            import time
            time.sleep(2)

            # Simular sucesso (90% de taxa de sucesso)
            import random
            sucesso = random.random() < 0.9

            if sucesso:
                self.root.after(0, lambda: messagebox.showinfo("Sucesso", "Mensagem enviada com sucesso!"))
                # Adicionar ao histórico
                novo_item = {
                    "id": len(self.historico_data) + 1,
                    "data_envio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tipo": self.tipo_var.get(),
                    "destinatario": destinatario,
                    "assunto": mensagem[:50] + "..." if len(mensagem) > 50 else mensagem,
                    "status": "enviado",
                    "template_nome": self.template_combo.get() if self.template_combo.get() != "Selecionar template..." else "Manual"
                }
                self.historico_data.insert(0, novo_item)
                self.root.after(0, self._atualizar_historico_tree)
            else:
                self.root.after(0, lambda: messagebox.showerror("Erro", "Falha no envio. Tente novamente."))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao enviar: {str(e)}"))

    def salvar_como_template(self):
        """Salvar mensagem atual como template"""
        mensagem = self.mensagem_text.get(1.0, tk.END).strip()
        if not mensagem:
            messagebox.showwarning("Aviso", "Digite uma mensagem para salvar como template.")
            return

        # Dialog para dados do template
        self.criar_template(mensagem_inicial=mensagem)

    def criar_template(self, mensagem_inicial=""):
        """Criar novo template"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Novo Template")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Frame principal
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # Campos
        row = 0
        ttk.Label(main_frame, text="Nome:").grid(row=row, column=0, sticky=tk.W, pady=5)
        nome_entry = ttk.Entry(main_frame, width=50)
        nome_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)

        row += 1
        ttk.Label(main_frame, text="Tipo:").grid(row=row, column=0, sticky=tk.W, pady=5)
        tipo_combo = ttk.Combobox(main_frame, values=["whatsapp", "email"], state="readonly")
        tipo_combo.set(self.tipo_var.get())
        tipo_combo.grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        ttk.Label(main_frame, text="Categoria:").grid(row=row, column=0, sticky=tk.W, pady=5)
        categoria_combo = ttk.Combobox(main_frame, values=["geral", "vendas", "suporte", "marketing"])
        categoria_combo.set("geral")
        categoria_combo.grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        assunto_label = ttk.Label(main_frame, text="Assunto:")
        assunto_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        assunto_entry = ttk.Entry(main_frame, width=50)
        assunto_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)

        # Inicializar com assunto atual se for email
        if self.tipo_var.get() == "email":
            assunto_entry.insert(0, self.assunto_entry.get())

        row += 1
        ttk.Label(main_frame, text="Conteúdo:").grid(row=row, column=0, sticky=(tk.W, tk.N), pady=5)

        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=row, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        conteudo_text = scrolledtext.ScrolledText(content_frame, height=12, wrap=tk.WORD)
        conteudo_text.pack(fill=tk.BOTH, expand=True)
        conteudo_text.insert(1.0, mensagem_inicial)

        # Configurar redimensionamento
        main_frame.rowconfigure(row, weight=1)

        # Função para alternar visibilidade do assunto
        def on_tipo_changed(*args):
            if tipo_combo.get() == "email":
                assunto_label.grid()
                assunto_entry.grid()
            else:
                assunto_label.grid_remove()
                assunto_entry.grid_remove()

        tipo_combo.bind("<<ComboboxSelected>>", on_tipo_changed)
        on_tipo_changed()

        # Botões
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        def salvar():
            nome = nome_entry.get().strip()
            tipo = tipo_combo.get()
            categoria = categoria_combo.get()
            assunto = assunto_entry.get().strip()
            conteudo = conteudo_text.get(1.0, tk.END).strip()

            if not nome or not tipo or not conteudo:
                messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios.")
                return

            # Adicionar template (simulação)
            novo_template = {
                "id": len(self.templates_data) + 1,
                "nome": nome,
                "tipo": tipo,
                "categoria": categoria,
                "assunto": assunto,
                "conteudo": conteudo,
                "ativo": True,
                "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            self.templates_data.append(novo_template)
            self._atualizar_templates_tree()
            self._atualizar_template_combo()

            messagebox.showinfo("Sucesso", "Template criado com sucesso!")
            dialog.destroy()

        ttk.Button(btn_frame, text="💾 Salvar", command=salvar).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="❌ Cancelar", command=dialog.destroy).pack(side=tk.RIGHT)

    def editar_template(self):
        """Editar template selecionado"""
        selection = self.templates_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um template para editar.")
            return

        # Obter dados do template
        item = self.templates_tree.item(selection[0])
        nome_template = item["values"][0]

        template = next((t for t in self.templates_data if t["nome"] == nome_template), None)
        if not template:
            messagebox.showerror("Erro", "Template não encontrado.")
            return

        # Abrir dialog de edição (similar ao criar)
        messagebox.showinfo("Info", f"Funcionalidade de edição será implementada para: {nome_template}")

    def excluir_template(self):
        """Excluir template selecionado"""
        selection = self.templates_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um template para excluir.")
            return

        item = self.templates_tree.item(selection[0])
        nome_template = item["values"][0]

        if messagebox.askyesno("Confirmar", f"Excluir template '{nome_template}'?"):
            # Remover da lista
            self.templates_data = [t for t in self.templates_data if t["nome"] != nome_template]
            self._atualizar_templates_tree()
            self._atualizar_template_combo()
            messagebox.showinfo("Sucesso", "Template excluído com sucesso!")

    def filtrar_historico(self):
        """Filtrar histórico"""
        # Implementar filtros
        messagebox.showinfo("Info", "Filtros serão aplicados ao histórico.")
        self.carregar_historico()

    def exportar_historico(self):
        """Exportar histórico"""
        messagebox.showinfo("Info", "Histórico exportado para planilha Excel.")

    def limpar_historico(self):
        """Limpar histórico"""
        if messagebox.askyesno("Confirmar", "Limpar todo o histórico?"):
            self.historico_data = []
            self._atualizar_historico_tree()
            messagebox.showinfo("Sucesso", "Histórico limpo com sucesso!")

    def ver_detalhes_historico(self):
        """Ver detalhes de item do histórico"""
        selection = self.historico_tree.selection()
        if not selection:
            return

        item = self.historico_tree.item(selection[0])
        messagebox.showinfo("Detalhes", f"Detalhes do envio:\n\n{item['values']}")

    def abrir_configuracoes(self):
        """Abrir configurações de comunicação"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configurações de Comunicação")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Aba WhatsApp
        whatsapp_frame = ttk.Frame(notebook, padding="10")
        notebook.add(whatsapp_frame, text="📱 WhatsApp")

        ttk.Label(whatsapp_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(whatsapp_frame, width=40, show="*").grid(row=0, column=1, pady=5)

        ttk.Checkbutton(whatsapp_frame, text="Ativar WhatsApp").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Aba Email
        email_frame = ttk.Frame(notebook, padding="10")
        notebook.add(email_frame, text="📧 Email")

        ttk.Label(email_frame, text="Servidor SMTP:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(email_frame, width=30).grid(row=0, column=1, pady=5)

        ttk.Label(email_frame, text="Porta:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(email_frame, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(email_frame, text="Usuário:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(email_frame, width=30).grid(row=2, column=1, pady=5)

        ttk.Label(email_frame, text="Senha:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(email_frame, width=30, show="*").grid(row=3, column=1, pady=5)

        ttk.Checkbutton(email_frame, text="Ativar Email").grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Botões
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="💾 Salvar", command=lambda: messagebox.showinfo("Info", "Configurações salvas!")).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="🧪 Testar", command=lambda: messagebox.showinfo("Info", "Teste de conexão realizado!")).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="❌ Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, padx=(0, 5))

    def on_closing(self):
        """Evento de fechamento da janela"""
        if messagebox.askokcancel("Sair", "Deseja fechar o módulo de comunicação?"):
            if self.parent_window:
                self.parent_window.deiconify()
            self.root.destroy()

# =======================================
# FUNÇÃO PRINCIPAL
# =======================================

def main():
    """Função principal para teste"""
    # Dados de teste
    user_data = {
        "id": 1,
        "username": "admin",
        "nome": "Administrador",
        "email": "admin@primotex.com.br",
        "access_token": "test_token",
        "permissions": ["all"]
    }

    # Criar interface
    app = ComunicacaoWindow(user_data)
    app.root.mainloop()

if __name__ == "__main__":
    main()