"""
SISTEMA ERP PRIMOTEX - DASHBOARD DE ORDENS DE SERVIÇO
=====================================================

Interface completa para gerenciamento de Ordens de Serviço (OS) com workflow de 7 fases.
Integração com API backend para persistência e controle de status.

Autor: GitHub Copilot
Data: 15/11/2025
Versão: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

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

# CORES DO SISTEMA
COLORS = {
    "primary": "#2c3e50",
    "success": "#27ae60",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#3498db",
    "light": "#ecf0f1",
    "dark": "#34495e",
    "white": "#ffffff"
}

# STATUS DE OS (7 FASES DO WORKFLOW)
STATUS_OS = {
    "solicitacao": {"label": "1. Solicitação", "color": COLORS["info"]},
    "analise": {"label": "2. Análise Técnica", "color": COLORS["warning"]},
    "orcamento": {"label": "3. Orçamento", "color": "#9b59b6"},
    "aprovacao": {"label": "4. Aprovação", "color": "#e67e22"},
    "execucao": {"label": "5. Execução", "color": COLORS["primary"]},
    "finalizacao": {"label": "6. Finalização", "color": "#16a085"},
    "concluido": {"label": "7. Concluído", "color": COLORS["success"]}
}

# PRIORIDADES DE OS
PRIORIDADES = {
    "baixa": {"label": "Baixa", "color": "#95a5a6"},
    "normal": {"label": "Normal", "color": COLORS["info"]},
    "alta": {"label": "Alta", "color": COLORS["warning"]},
    "urgente": {"label": "Urgente", "color": COLORS["danger"]}
}

# =======================================
# CLASSE DASHBOARD DE OS
# =======================================

@require_login()
class OSDashboard:
    """Dashboard completo de Ordens de Serviço"""

    def __init__(self, parent_window=None):
        # NÃO recebe mais user_data - usa SessionManager
        self.token = get_token_for_api()
        self.user_data = get_current_user_info()
        self.parent_window = parent_window

        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.os_data = []
        self.selected_os = None
        self.filtro_status = "todos"
        self.filtro_prioridade = "todos"

        self.setup_window()
        self.create_widgets()
        self.load_os_list()

    def setup_window(self):
        """Configuração inicial da janela"""
        self.root.title("Dashboard de Ordens de Serviço - ERP Primotex")
        self.root.geometry("1400x800")

        # Centralizar janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1400x800+{x}+{y}")

        self.root.configure(bg=COLORS["light"])

    def create_widgets(self):
        """Criar todos os widgets da interface"""
        # ===== CABEÇALHO =====
        header_frame = tk.Frame(self.root, bg=COLORS["primary"], height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Título
        title_label = tk.Label(
            header_frame,
            text="🏗️ Dashboard de Ordens de Serviço",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        )
        title_label.pack(side="left", padx=20, pady=20)

        # Informações do usuário
        user_info = f"👤 {self.user_data.get('username', 'Usuário')} | {self.user_data.get('permission_level', 'N/A').title()}"
        user_label = tk.Label(
            header_frame,
            text=user_info,
            font=("Segoe UI", 10),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        )
        user_label.pack(side="right", padx=20, pady=20)

        # ===== ÁREA PRINCIPAL =====
        main_frame = tk.Frame(self.root, bg=COLORS["light"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== PAINEL ESQUERDO (LISTA DE OS) =====
        left_panel = tk.Frame(main_frame, bg=COLORS["white"], relief="solid", borderwidth=1)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Barra de ferramentas (filtros e ações)
        toolbar_frame = tk.Frame(left_panel, bg=COLORS["white"])
        toolbar_frame.pack(fill="x", padx=10, pady=10)

        # Botão Nova OS
        btn_nova = tk.Button(
            toolbar_frame,
            text="➕ Nova OS",
            command=self.show_nova_os_dialog,
            bg=COLORS["success"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8
        )
        btn_nova.pack(side="left", padx=(0, 10))

        # Botão Atualizar
        btn_refresh = tk.Button(
            toolbar_frame,
            text="🔄 Atualizar",
            command=self.load_os_list,
            bg=COLORS["info"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8
        )
        btn_refresh.pack(side="left", padx=(0, 10))

        # Filtro por Status
        tk.Label(
            toolbar_frame,
            text="Status:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).pack(side="left", padx=(20, 5))

        self.status_filter_var = tk.StringVar(value="todos")
        status_combo = ttk.Combobox(
            toolbar_frame,
            textvariable=self.status_filter_var,
            values=["todos"] + [STATUS_OS[k]["label"] for k in STATUS_OS.keys()],
            state="readonly",
            width=20,
            font=("Segoe UI", 9)
        )
        status_combo.pack(side="left", padx=(0, 10))
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Filtro por Prioridade
        tk.Label(
            toolbar_frame,
            text="Prioridade:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).pack(side="left", padx=(10, 5))

        self.prioridade_filter_var = tk.StringVar(value="todos")
        prioridade_combo = ttk.Combobox(
            toolbar_frame,
            textvariable=self.prioridade_filter_var,
            values=["todos"] + [PRIORIDADES[k]["label"] for k in PRIORIDADES.keys()],
            state="readonly",
            width=15,
            font=("Segoe UI", 9)
        )
        prioridade_combo.pack(side="left")
        prioridade_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Tabela de OS
        tree_frame = tk.Frame(left_panel, bg=COLORS["white"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y")

        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("os", "cliente", "titulo", "status", "prioridade", "data", "valor"),
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=20
        )

        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        # Configurar colunas
        self.tree.heading("os", text="OS Nº")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("titulo", text="Título")
        self.tree.heading("status", text="Status")
        self.tree.heading("prioridade", text="Prioridade")
        self.tree.heading("data", text="Data")
        self.tree.heading("valor", text="Valor Total")

        self.tree.column("os", width=80, anchor="center")
        self.tree.column("cliente", width=180)
        self.tree.column("titulo", width=250)
        self.tree.column("status", width=150, anchor="center")
        self.tree.column("prioridade", width=100, anchor="center")
        self.tree.column("data", width=100, anchor="center")
        self.tree.column("valor", width=100, anchor="e")

        self.tree.pack(fill="both", expand=True)

        # Evento de seleção
        self.tree.bind("<<TreeviewSelect>>", self.on_os_selected)

        # ===== PAINEL DIREITO (DETALHES DA OS) =====
        right_panel = tk.Frame(main_frame, bg=COLORS["white"], relief="solid", borderwidth=1, width=500)
        right_panel.pack(side="right", fill="both", padx=(5, 0))
        right_panel.pack_propagate(False)

        # Título do painel
        details_title = tk.Label(
            right_panel,
            text="📋 Detalhes da Ordem de Serviço",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["white"],
            fg=COLORS["primary"]
        )
        details_title.pack(pady=(15, 10))

        # Frame de detalhes com scroll
        details_scroll = ttk.Scrollbar(right_panel, orient="vertical")
        details_scroll.pack(side="right", fill="y", padx=(0, 10))

        self.details_canvas = tk.Canvas(
            right_panel,
            bg=COLORS["white"],
            yscrollcommand=details_scroll.set,
            highlightthickness=0
        )
        self.details_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))

        details_scroll.config(command=self.details_canvas.yview)

        # Frame interno do canvas
        self.details_frame = tk.Frame(self.details_canvas, bg=COLORS["white"])
        self.details_canvas_window = self.details_canvas.create_window(
            (0, 0),
            window=self.details_frame,
            anchor="nw"
        )

        # Configurar scroll
        self.details_frame.bind("<Configure>", self.on_details_configure)
        self.details_canvas.bind("<Configure>", self.on_canvas_configure)

        # Placeholder inicial
        self.show_empty_details()

    def on_details_configure(self, event):
        """Atualizar scroll region quando details_frame mudar"""
        self.details_canvas.configure(scrollregion=self.details_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Ajustar largura do frame interno ao canvas"""
        self.details_canvas.itemconfig(
            self.details_canvas_window,
            width=event.width
        )

    def show_empty_details(self):
        """Mostrar mensagem quando nenhuma OS está selecionada"""
        # Limpar frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        empty_label = tk.Label(
            self.details_frame,
            text="👈 Selecione uma OS\npara ver os detalhes",
            font=("Segoe UI", 12),
            bg=COLORS["white"],
            fg="#7f8c8d",
            justify="center"
        )
        empty_label.pack(pady=100)

    def show_os_details(self, os: Dict[str, Any]):
        """Mostrar detalhes completos da OS selecionada"""
        # Limpar frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # ===== INFORMAÇÕES BÁSICAS =====
        info_frame = tk.LabelFrame(
            self.details_frame,
            text="📌 Informações Básicas",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["white"],
            fg=COLORS["primary"],
            padx=10,
            pady=10
        )
        info_frame.pack(fill="x", padx=5, pady=(0, 10))

        # Número da OS
        self.create_detail_field(info_frame, "OS Nº:", os.get("numero_os", "N/A"), bold=True)

        # Cliente
        self.create_detail_field(info_frame, "Cliente:", os.get("cliente_nome", "N/A"))

        # Título
        self.create_detail_field(info_frame, "Título:", os.get("titulo", "N/A"))

        # Status com cor
        status_key = os.get("status", "solicitacao")
        status_info = STATUS_OS.get(status_key, STATUS_OS["solicitacao"])
        self.create_detail_field_colored(
            info_frame,
            "Status:",
            status_info["label"],
            status_info["color"]
        )

        # Prioridade com cor
        prioridade_key = os.get("prioridade", "normal")
        prioridade_info = PRIORIDADES.get(prioridade_key, PRIORIDADES["normal"])
        self.create_detail_field_colored(
            info_frame,
            "Prioridade:",
            prioridade_info["label"],
            prioridade_info["color"]
        )

        # ===== DATAS E PRAZOS =====
        dates_frame = tk.LabelFrame(
            self.details_frame,
            text="📅 Datas e Prazos",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["white"],
            fg=COLORS["primary"],
            padx=10,
            pady=10
        )
        dates_frame.pack(fill="x", padx=5, pady=(0, 10))

        # Data de Solicitação
        data_solicitacao = os.get("data_solicitacao", "N/A")
        if data_solicitacao != "N/A":
            try:
                dt = datetime.fromisoformat(data_solicitacao.replace("Z", "+00:00"))
                data_solicitacao = dt.strftime("%d/%m/%Y %H:%M")
            except:
                pass
        self.create_detail_field(dates_frame, "Solicitação:", data_solicitacao)

        # Data Prazo
        data_prazo = os.get("data_prazo", "N/A")
        if data_prazo != "N/A":
            try:
                dt = datetime.fromisoformat(data_prazo.replace("Z", "+00:00"))
                data_prazo = dt.strftime("%d/%m/%Y")
            except:
                pass
        self.create_detail_field(dates_frame, "Prazo:", data_prazo)

        # ===== DESCRIÇÃO =====
        desc_frame = tk.LabelFrame(
            self.details_frame,
            text="📝 Descrição",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["white"],
            fg=COLORS["primary"],
            padx=10,
            pady=10
        )
        desc_frame.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        desc_text = scrolledtext.ScrolledText(
            desc_frame,
            height=6,
            font=("Segoe UI", 9),
            wrap="word",
            bg="#f8f9fa",
            relief="flat"
        )
        desc_text.pack(fill="both", expand=True)
        desc_text.insert("1.0", os.get("descricao", "Sem descrição"))
        desc_text.config(state="disabled")

        # ===== ENDEREÇO DO SERVIÇO =====
        if os.get("endereco_servico"):
            endereco_frame = tk.LabelFrame(
                self.details_frame,
                text="📍 Endereço do Serviço",
                font=("Segoe UI", 11, "bold"),
                bg=COLORS["white"],
                fg=COLORS["primary"],
                padx=10,
                pady=10
            )
            endereco_frame.pack(fill="x", padx=5, pady=(0, 10))

            endereco_label = tk.Label(
                endereco_frame,
                text=os.get("endereco_servico", ""),
                font=("Segoe UI", 9),
                bg=COLORS["white"],
                fg=COLORS["dark"],
                justify="left",
                wraplength=400
            )
            endereco_label.pack(anchor="w")

        # ===== FINANCEIRO =====
        financeiro_frame = tk.LabelFrame(
            self.details_frame,
            text="💰 Financeiro",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["white"],
            fg=COLORS["primary"],
            padx=10,
            pady=10
        )
        financeiro_frame.pack(fill="x", padx=5, pady=(0, 10))

        valor_total = os.get("valor_total", 0)
        try:
            valor_formatado = f"R$ {float(valor_total):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            valor_formatado = "R$ 0,00"

        self.create_detail_field(financeiro_frame, "Valor Total:", valor_formatado, bold=True)

        # ===== OBSERVAÇÕES =====
        if os.get("observacoes"):
            obs_frame = tk.LabelFrame(
                self.details_frame,
                text="💬 Observações",
                font=("Segoe UI", 11, "bold"),
                bg=COLORS["white"],
                fg=COLORS["primary"],
                padx=10,
                pady=10
            )
            obs_frame.pack(fill="both", expand=True, padx=5, pady=(0, 10))

            obs_text = scrolledtext.ScrolledText(
                obs_frame,
                height=4,
                font=("Segoe UI", 9),
                wrap="word",
                bg="#f8f9fa",
                relief="flat"
            )
            obs_text.pack(fill="both", expand=True)
            obs_text.insert("1.0", os.get("observacoes", ""))
            obs_text.config(state="disabled")

        # ===== AÇÕES =====
        actions_frame = tk.Frame(self.details_frame, bg=COLORS["white"])
        actions_frame.pack(fill="x", padx=5, pady=(10, 5))

        # Botão Editar
        btn_edit = tk.Button(
            actions_frame,
            text="✏️ Editar OS",
            command=lambda: self.edit_os(os["id"]),
            bg=COLORS["info"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        btn_edit.pack(side="left", padx=(0, 10), fill="x", expand=True)

        # Botão Alterar Status
        btn_status = tk.Button(
            actions_frame,
            text="🔄 Alterar Status",
            command=lambda: self.change_status(os),
            bg=COLORS["warning"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        btn_status.pack(side="left", fill="x", expand=True)
        
        # Segunda linha de ações
        actions_frame2 = tk.Frame(self.details_frame, bg=COLORS["white"])
        actions_frame2.pack(fill="x", padx=5, pady=(5, 0))
        
        # Botão Criar Croqui
        btn_croqui = tk.Button(
            actions_frame2,
            text="🎨 Criar Croqui Técnico",
            command=lambda: self.abrir_canvas_croqui(os["id"]),
            bg="#17a2b8",
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        btn_croqui.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Label informativa
        tk.Label(
            actions_frame2,
            text="Desenhe o croqui técnico do local",
            font=("Segoe UI", 8),
            bg=COLORS["white"],
            fg="#7f8c8d"
        ).pack(side="left", padx=10)

        # =======================================
        # TERCEIRA LINHA - ORÇAMENTO
        # =======================================
        actions_frame3 = tk.Frame(self.details_frame, bg=COLORS["white"])
        actions_frame3.pack(fill="x", padx=5, pady=(5, 0))
        
        # Botão Criar Orçamento
        btn_orcamento = tk.Button(
            actions_frame3,
            text="💰 Criar Orçamento",
            command=lambda: self.abrir_grid_orcamento(os["id"]),
            bg="#f39c12",
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        btn_orcamento.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Label informativa
        tk.Label(
            actions_frame3,
            text="Monte o orçamento de produtos/serviços",
            font=("Segoe UI", 8),
            bg=COLORS["white"],
            fg="#7f8c8d"
        ).pack(side="left", padx=10)

    def create_detail_field(self, parent, label: str, value: str, bold: bool = False):
        """Criar campo de detalhe (label: value)"""
        field_frame = tk.Frame(parent, bg=COLORS["white"])
        field_frame.pack(fill="x", pady=3)

        label_widget = tk.Label(
            field_frame,
            text=label,
            font=("Segoe UI", 9, "bold"),
            bg=COLORS["white"],
            fg="#7f8c8d",
            width=15,
            anchor="w"
        )
        label_widget.pack(side="left")

        value_font = ("Segoe UI", 9, "bold" if bold else "normal")
        value_widget = tk.Label(
            field_frame,
            text=value,
            font=value_font,
            bg=COLORS["white"],
            fg=COLORS["dark"],
            anchor="w"
        )
        value_widget.pack(side="left", fill="x", expand=True)

    def create_detail_field_colored(self, parent, label: str, value: str, color: str):
        """Criar campo de detalhe com cor customizada"""
        field_frame = tk.Frame(parent, bg=COLORS["white"])
        field_frame.pack(fill="x", pady=3)

        label_widget = tk.Label(
            field_frame,
            text=label,
            font=("Segoe UI", 9, "bold"),
            bg=COLORS["white"],
            fg="#7f8c8d",
            width=15,
            anchor="w"
        )
        label_widget.pack(side="left")

        value_widget = tk.Label(
            field_frame,
            text=value,
            font=("Segoe UI", 9, "bold"),
            bg=color,
            fg=COLORS["white"],
            anchor="center",
            padx=10,
            pady=3,
            relief="flat"
        )
        value_widget.pack(side="left")

    def on_os_selected(self, event):
        """Evento quando uma OS é selecionada"""
        selection = self.tree.selection()
        if not selection:
            self.show_empty_details()
            return

        # Pegar dados da OS selecionada
        item_id = selection[0]
        item_values = self.tree.item(item_id, "values")

        if not item_values:
            return

        # Buscar OS completa nos dados
        os_numero = item_values[0]
        os_completa = next((os for os in self.os_data if os.get("numero_os") == os_numero), None)

        if os_completa:
            self.selected_os = os_completa
            self.show_os_details(os_completa)

    def load_os_list(self):
        """Carregar lista de OS do backend"""
        def _load():
            try:
                headers = create_auth_header()
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/os",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    self.os_data = response.json()
                    self.root.after(0, self.populate_tree)
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao carregar OS: {response.status_code}"
                    ))
            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erro de Conexão",
                    "Não foi possível conectar ao servidor.\nVerifique se o backend está rodando."
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro ao carregar OS: {str(e)}"
                ))

        thread = threading.Thread(target=_load, daemon=True)
        thread.start()

    def populate_tree(self):
        """Preencher árvore com dados de OS"""
        # Limpar árvore
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filtrar dados
        filtered_data = self.filter_os_data(self.os_data)

        # Preencher com dados filtrados
        for os in filtered_data:
            # Formatar data
            data_solicitacao = os.get("data_solicitacao", "N/A")
            if data_solicitacao != "N/A":
                try:
                    dt = datetime.fromisoformat(data_solicitacao.replace("Z", "+00:00"))
                    data_formatada = dt.strftime("%d/%m/%Y")
                except:
                    data_formatada = "N/A"
            else:
                data_formatada = "N/A"

            # Formatar valor
            try:
                valor = float(os.get("valor_total", 0))
                valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                valor_formatado = "R$ 0,00"

            # Obter labels de status e prioridade
            status_key = os.get("status", "solicitacao")
            status_label = STATUS_OS.get(status_key, STATUS_OS["solicitacao"])["label"]

            prioridade_key = os.get("prioridade", "normal")
            prioridade_label = PRIORIDADES.get(prioridade_key, PRIORIDADES["normal"])["label"]

            self.tree.insert(
                "",
                "end",
                values=(
                    os.get("numero_os", "N/A"),
                    os.get("cliente_nome", "N/A"),
                    os.get("titulo", "N/A"),
                    status_label,
                    prioridade_label,
                    data_formatada,
                    valor_formatado
                )
            )

        # Atualizar status bar
        total = len(filtered_data)
        self.root.title(f"Dashboard de Ordens de Serviço - {total} OS encontradas - ERP Primotex")

    def filter_os_data(self, data: List[Dict]) -> List[Dict]:
        """Filtrar dados de OS baseado nos filtros ativos"""
        filtered = data

        # Filtro de status
        status_filter = self.status_filter_var.get()
        if status_filter != "todos":
            # Encontrar chave do status pelo label
            status_key = None
            for k, v in STATUS_OS.items():
                if v["label"] == status_filter:
                    status_key = k
                    break

            if status_key:
                filtered = [os for os in filtered if os.get("status") == status_key]

        # Filtro de prioridade
        prioridade_filter = self.prioridade_filter_var.get()
        if prioridade_filter != "todos":
            # Encontrar chave da prioridade pelo label
            prioridade_key = None
            for k, v in PRIORIDADES.items():
                if v["label"] == prioridade_filter:
                    prioridade_key = k
                    break

            if prioridade_key:
                filtered = [os for os in filtered if os.get("prioridade") == prioridade_key]

        return filtered

    def apply_filters(self):
        """Aplicar filtros e recarregar lista"""
        self.populate_tree()

    def show_nova_os_dialog(self):
        """Mostrar dialog para criar nova OS"""
        messagebox.showinfo(
            "Em Desenvolvimento",
            "Funcionalidade de criação de OS em desenvolvimento.\n\n"
            "Por enquanto, use a API diretamente ou o módulo de agendamento."
        )

    def edit_os(self, os_id: int):
        """Editar OS selecionada"""
        messagebox.showinfo(
            "Em Desenvolvimento",
            f"Funcionalidade de edição de OS #{os_id} em desenvolvimento.\n\n"
            "Por enquanto, use a API diretamente."
        )

    def abrir_canvas_croqui(self, os_id: int):
        """Abrir canvas de croqui para desenho técnico"""
        from frontend.desktop.canvas_croqui import CanvasCroqui
        
        try:
            # Criar janela toplevel para o canvas
            canvas_window = tk.Toplevel(self.root)
            canvas_window.title(f"Croqui Técnico - OS #{os_id}")
            
            # Instanciar canvas
            CanvasCroqui(canvas_window, os_id=os_id)
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir Canvas Croqui:\n{str(e)}",
                parent=self.root
            )

    def abrir_grid_orcamento(self, os_id: int):
        """Abrir grid de orçamento para esta OS"""
        from frontend.desktop.grid_orcamento import GridOrcamento
        
        try:
            # Criar janela toplevel para o grid
            orcamento_window = tk.Toplevel(self.root)
            orcamento_window.title(f"Orçamento - OS #{os_id}")
            orcamento_window.geometry("1100x750")
            
            # Instanciar grid
            grid = GridOrcamento(orcamento_window, os_id=os_id)
            grid.pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir Grid Orçamento:\n{str(e)}",
                parent=self.root
            )

    def change_status(self, os: Dict[str, Any]):
        """Alterar status da OS"""
        # Dialog de seleção de status
        dialog = tk.Toplevel(self.root)
        dialog.title("Alterar Status da OS")
        dialog.geometry("400x350")
        dialog.resizable(False, False)

        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"400x350+{x}+{y}")

        dialog.configure(bg=COLORS["white"])
        dialog.transient(self.root)
        dialog.grab_set()

        # Título
        title_label = tk.Label(
            dialog,
            text=f"Alterar Status - OS {os.get('numero_os')}",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["white"],
            fg=COLORS["primary"]
        )
        title_label.pack(pady=20)

        # Status atual
        current_status_key = os.get("status", "solicitacao")
        current_status = STATUS_OS.get(current_status_key, STATUS_OS["solicitacao"])

        tk.Label(
            dialog,
            text=f"Status atual: {current_status['label']}",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            fg="#7f8c8d"
        ).pack(pady=(0, 20))

        # Novo status
        tk.Label(
            dialog,
            text="Novo status:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["dark"]
        ).pack(pady=(0, 10))

        status_var = tk.StringVar(value=current_status_key)

        # Radiobuttons para cada status
        for status_key, status_info in STATUS_OS.items():
            rb_frame = tk.Frame(dialog, bg=COLORS["white"])
            rb_frame.pack(fill="x", padx=40, pady=2)

            rb = tk.Radiobutton(
                rb_frame,
                text=status_info["label"],
                variable=status_var,
                value=status_key,
                font=("Segoe UI", 10),
                bg=COLORS["white"],
                fg=COLORS["dark"],
                selectcolor=status_info["color"],
                activebackground=COLORS["white"]
            )
            rb.pack(anchor="w")

        # Botões
        btn_frame = tk.Frame(dialog, bg=COLORS["white"])
        btn_frame.pack(pady=30)

        def confirmar():
            new_status = status_var.get()
            if new_status == current_status_key:
                messagebox.showinfo("Info", "Status não foi alterado.")
                dialog.destroy()
                return

            # Chamar API para atualizar status
            self.update_os_status(os["id"], new_status, dialog)

        btn_confirm = tk.Button(
            btn_frame,
            text="✅ Confirmar",
            command=confirmar,
            bg=COLORS["success"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        btn_confirm.pack(side="left", padx=10)

        btn_cancel = tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=dialog.destroy,
            bg=COLORS["danger"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        btn_cancel.pack(side="left", padx=10)

    def update_os_status(self, os_id: int, new_status: str, dialog_window):
        """Atualizar status da OS via API"""
        def _update():
            try:
                headers = create_auth_header()
                response = requests.put(
                    f"{API_BASE_URL}/api/v1/os/{os_id}/status",
                    headers=headers,
                    json={"status": new_status},
                    timeout=10
                )

                if response.status_code == 200:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Sucesso",
                        "Status da OS atualizado com sucesso!"
                    ))
                    self.root.after(0, dialog_window.destroy)
                    self.root.after(0, self.load_os_list)
                else:
                    error_msg = response.json().get("detail", "Erro desconhecido")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao atualizar status: {error_msg}"
                    ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro ao atualizar status: {str(e)}"
                ))

        thread = threading.Thread(target=_update, daemon=True)
        thread.start()

    def run(self):
        """Iniciar aplicação"""
        self.root.mainloop()

# =======================================
# PONTO DE ENTRADA
# =======================================

if __name__ == "__main__":
    app = OSDashboard()
    app.run()
