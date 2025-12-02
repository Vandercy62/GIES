"""
Grid de Equipe - FASE 104 TAREFA 7
Sistema ERP Primotex

Grid especializado para gerenciamento de equipe em Ordens de Serviço.

Funcionalidades:
- TreeView com 7 colunas (colaborador, função, data início, data fim, horas, status, obs)
- Dialog para adicionar/editar membros da equipe
- Cálculo automático de horas trabalhadas
- Seleção de colaboradores do banco
- Controle de status (Ativo, Concluído, Afastado)
- Totalizadores (total horas, ativos, concluídos)
- Persistência via API (POST/GET equipe-json)

Autor: GitHub Copilot
Data: 19/11/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Optional
import requests
import threading
from datetime import datetime, timedelta
from tkcalendar import DateEntry


# Imports do projeto
from frontend.desktop.auth_middleware import create_auth_header, get_token_for_api


# =====================================================================
# CONFIGURAÇÕES
# =====================================================================

API_BASE_URL = "http://127.0.0.1:8002"

COLORS = {
    "primary": "#2c3e50",
    "secondary": "#3498db",
    "success": "#27ae60",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#3498db",
    "light": "#ecf0f1",
    "dark": "#34495e",
    "white": "#ffffff"
}

FUNCOES = [
    "Técnico Instalador",
    "Ajudante",
    "Supervisor",
    "Eletricista",
    "Pintor",
    "Auxiliar Geral"
]

STATUS_EQUIPE = [
    "Ativo",
    "Concluído",
    "Afastado",
    "Férias"
]


# =====================================================================
# CLASSE PRINCIPAL
# =====================================================================

class GridEquipe:
    """
    Grid de Equipe para Ordens de Serviço
    
    Gerencia equipe alocada na OS:
    - Registro de colaboradores
    - Controle de datas e horas
    - Status de participação
    - Funções desempenhadas
    """
    
    def __init__(self, parent: tk.Tk, os_id: Optional[int] = None):
        """
        Inicializa grid de equipe
        
        Args:
            parent: Janela pai (Tk ou Toplevel)
            os_id: ID da OS (None para rascunho)
        """
        self.parent = parent
        self.os_id = os_id
        self.token = get_token_for_api()
        
        # Dados
        self.membros: List[Dict[str, Any]] = []
        self.colaboradores_disponiveis: List[Dict[str, Any]] = []
        
        # Setup da janela
        self._setup_window()
        self._criar_widgets()
        
        # Carregar dados
        self._carregar_colaboradores()
        if self.os_id:
            self._carregar_equipe()
    
    def _setup_window(self):
        """Configura a janela principal"""
        self.root = tk.Toplevel(self.parent)
        self.root.title("👥 Gerenciamento de Equipe - OS")
        self.root.geometry("1400x700")
        self.root.configure(bg=COLORS["light"])
        
        # Centralizar
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _criar_widgets(self):
        """Cria todos os widgets da interface"""
        # Header
        self._criar_header()
        
        # Toolbar
        self._criar_toolbar()
        
        # TreeView
        self._criar_treeview()
        
        # Totalizadores
        self._criar_totalizadores()
        
        # Footer
        self._criar_footer()
    
    def _criar_header(self):
        """Cria cabeçalho com título e info da OS"""
        header_frame = tk.Frame(self.root, bg=COLORS["primary"], height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Título
        titulo = tk.Label(
            header_frame,
            text="👥 GERENCIAMENTO DE EQUIPE",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        )
        titulo.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Info OS
        os_info = f"OS #{self.os_id}" if self.os_id else "RASCUNHO"
        info_label = tk.Label(
            header_frame,
            text=os_info,
            font=("Segoe UI", 12),
            bg=COLORS["primary"],
            fg=COLORS["light"]
        )
        info_label.pack(side=tk.LEFT, padx=10, pady=15)
    
    def _criar_toolbar(self):
        """Cria barra de ferramentas com botões de ação"""
        toolbar_frame = tk.Frame(self.root, bg=COLORS["white"], height=60)
        toolbar_frame.pack(fill=tk.X, padx=0, pady=0)
        toolbar_frame.pack_propagate(False)
        
        # Frame interno para centralizar botões
        btn_container = tk.Frame(toolbar_frame, bg=COLORS["white"])
        btn_container.pack(pady=10)
        
        # Botão Adicionar
        btn_adicionar = tk.Button(
            btn_container,
            text="➕ Adicionar Membro",
            command=self._adicionar_membro_dialog,
            bg=COLORS["success"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            width=18,
            height=2,
            relief=tk.FLAT,
            cursor="hand2"
        )
        btn_adicionar.pack(side=tk.LEFT, padx=5)
        
        # Botão Editar
        btn_editar = tk.Button(
            btn_container,
            text="✏️ Editar",
            command=self._editar_membro_dialog,
            bg=COLORS["info"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            width=12,
            height=2,
            relief=tk.FLAT,
            cursor="hand2"
        )
        btn_editar.pack(side=tk.LEFT, padx=5)
        
        # Botão Excluir
        btn_excluir = tk.Button(
            btn_container,
            text="🗑️ Excluir",
            command=self._excluir_membro,
            bg=COLORS["danger"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            width=12,
            height=2,
            relief=tk.FLAT,
            cursor="hand2"
        )
        btn_excluir.pack(side=tk.LEFT, padx=5)
        
        # Botão Salvar
        btn_salvar = tk.Button(
            btn_container,
            text="💾 Salvar",
            command=self._salvar_equipe,
            bg=COLORS["primary"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            width=12,
            height=2,
            relief=tk.FLAT,
            cursor="hand2"
        )
        btn_salvar.pack(side=tk.LEFT, padx=5)
    
    def _criar_treeview(self):
        """Cria TreeView para exibir membros da equipe"""
        # Frame container
        tree_frame = tk.Frame(self.root, bg=COLORS["white"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # TreeView
        colunas = ("colaborador", "funcao", "data_inicio", "data_fim", "horas", "status", "obs")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=colunas,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=15
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configurar colunas
        self.tree.heading("colaborador", text="Colaborador", anchor=tk.W)
        self.tree.heading("funcao", text="Função", anchor=tk.W)
        self.tree.heading("data_inicio", text="Data Início", anchor=tk.CENTER)
        self.tree.heading("data_fim", text="Data Fim", anchor=tk.CENTER)
        self.tree.heading("horas", text="Horas Trabalhadas", anchor=tk.CENTER)
        self.tree.heading("status", text="Status", anchor=tk.CENTER)
        self.tree.heading("obs", text="Observações", anchor=tk.W)
        
        self.tree.column("colaborador", width=250, anchor=tk.W)
        self.tree.column("funcao", width=180, anchor=tk.W)
        self.tree.column("data_inicio", width=120, anchor=tk.CENTER)
        self.tree.column("data_fim", width=120, anchor=tk.CENTER)
        self.tree.column("horas", width=150, anchor=tk.CENTER)
        self.tree.column("status", width=120, anchor=tk.CENTER)
        self.tree.column("obs", width=250, anchor=tk.W)
        
        # Estilo zebra
        self.tree.tag_configure("par", background="#f8f9fa")
        self.tree.tag_configure("impar", background="#ffffff")
        self.tree.tag_configure("ativo", background="#d4edda", foreground="#155724")
        self.tree.tag_configure("concluido", background="#d1ecf1", foreground="#0c5460")
        self.tree.tag_configure("afastado", background="#fff3cd", foreground="#856404")
        
        # Bind double-click para edição
        self.tree.bind("<Double-1>", lambda e: self._editar_membro_dialog())
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
    
    def _criar_totalizadores(self):
        """Cria seção de totalizadores"""
        totais_frame = tk.Frame(self.root, bg=COLORS["light"], height=100)
        totais_frame.pack(fill=tk.X, padx=20, pady=10)
        totais_frame.pack_propagate(False)
        
        # Título
        titulo = tk.Label(
            totais_frame,
            text="📊 TOTALIZADORES",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["light"],
            fg=COLORS["dark"]
        )
        titulo.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Frame dos totais
        valores_frame = tk.Frame(totais_frame, bg=COLORS["white"])
        valores_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Labels dos totais
        self.lbl_total_horas = self._criar_label_total(valores_frame, "Total Horas:", "0h", 0)
        self.lbl_total_ativos = self._criar_label_total(valores_frame, "Ativos:", "0", 1)
        self.lbl_total_concluidos = self._criar_label_total(valores_frame, "Concluídos:", "0", 2)
        self.lbl_total_membros = self._criar_label_total(valores_frame, "Total Membros:", "0", 3)
    
    def _criar_label_total(self, parent: tk.Frame, titulo: str, valor_inicial: str, col: int) -> tk.Label:
        """
        Cria um label de total
        
        Args:
            parent: Frame pai
            titulo: Texto do título
            valor_inicial: Valor inicial
            col: Coluna no grid
            
        Returns:
            Label do valor
        """
        frame = tk.Frame(parent, bg=COLORS["white"])
        frame.grid(row=0, column=col, padx=15, pady=10, sticky="w")
        
        lbl_titulo = tk.Label(
            frame,
            text=titulo,
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            fg=COLORS["dark"]
        )
        lbl_titulo.pack(anchor=tk.W)
        
        # Cor baseada no tipo
        cor = COLORS["primary"] if "Horas" in titulo else (
            COLORS["success"] if "Ativos" in titulo else (
                COLORS["info"] if "Concluídos" in titulo else COLORS["dark"]
            )
        )
        
        lbl_valor = tk.Label(
            frame,
            text=valor_inicial,
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["white"],
            fg=cor
        )
        lbl_valor.pack(anchor=tk.W)
        
        return lbl_valor
    
    def _criar_footer(self):
        """Cria rodapé com botão fechar"""
        footer_frame = tk.Frame(self.root, bg=COLORS["white"], height=60)
        footer_frame.pack(fill=tk.X, padx=0, pady=0)
        footer_frame.pack_propagate(False)
        
        btn_fechar = tk.Button(
            footer_frame,
            text="✖️ Fechar",
            command=self.root.destroy,
            bg=COLORS["dark"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            width=15,
            height=2,
            relief=tk.FLAT,
            cursor="hand2"
        )
        btn_fechar.pack(pady=10)
    
    # =================================================================
    # MÉTODOS DE DADOS - API
    # =================================================================
    
    def _carregar_colaboradores(self):
        """Carrega lista de colaboradores disponíveis"""
        def _request():
            try:
                headers = create_auth_header()
                url = f"{API_BASE_URL}/api/v1/colaboradores"
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    # API retorna formato paginado
                    if isinstance(data, dict) and "itens" in data:
                        self.colaboradores_disponiveis = data["itens"]
                    else:
                        self.colaboradores_disponiveis = data if isinstance(data, list) else []
                else:
                    self.colaboradores_disponiveis = []
            except Exception as e:
                print(f"Erro ao carregar colaboradores: {e}")
                self.colaboradores_disponiveis = []
        
        thread = threading.Thread(target=_request, daemon=True)
        thread.start()
    
    def _carregar_equipe(self):
        """Carrega equipe existente da API"""
        if not self.os_id:
            return
        
        def _request():
            try:
                headers = create_auth_header()
                url = f"{API_BASE_URL}/api/v1/os/{self.os_id}/equipe-json"
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.membros = data.get("membros", [])
                    self.root.after(0, self._atualizar_tree)
                    self.root.after(0, self._atualizar_totais)
                elif response.status_code == 404:
                    # Sem equipe ainda
                    self.membros = []
                else:
                    self.root.after(
                        0,
                        lambda: messagebox.showerror(
                            "Erro",
                            f"Erro ao carregar equipe: {response.status_code}"
                        )
                    )
            except requests.exceptions.RequestException as e:
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro de Conexão",
                        f"Não foi possível conectar ao servidor:\n{str(e)}"
                    )
                )
        
        thread = threading.Thread(target=_request, daemon=True)
        thread.start()
    
    def _salvar_equipe(self):
        """Salva equipe no backend"""
        if not self.os_id:
            messagebox.showwarning(
                "OS Necessária",
                "Salve a OS antes de salvar a equipe"
            )
            return
        
        def _request():
            try:
                headers = create_auth_header()
                url = f"{API_BASE_URL}/api/v1/os/{self.os_id}/equipe-json"
                
                payload = {
                    "membros": self.membros,
                    "timestamp": datetime.now().isoformat()
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.root.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Sucesso",
                            "✅ Equipe salva com sucesso!"
                        )
                    )
                else:
                    self.root.after(
                        0,
                        lambda: messagebox.showerror(
                            "Erro",
                            f"Erro ao salvar equipe: {response.status_code}\n{response.text}"
                        )
                    )
            except requests.exceptions.RequestException as e:
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro de Conexão",
                        f"Não foi possível conectar ao servidor:\n{str(e)}"
                    )
                )
        
        thread = threading.Thread(target=_request, daemon=True)
        thread.start()
    
    # =================================================================
    # MÉTODOS DE INTERFACE
    # =================================================================
    
    def _atualizar_tree(self):
        """Atualiza TreeView com dados da equipe"""
        # Limpar
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Preencher
        for idx, membro in enumerate(self.membros):
            status = membro.get("status", "Ativo")
            
            # Tag baseada no status
            if status == "Ativo":
                tag = "ativo"
            elif status == "Concluído":
                tag = "concluido"
            elif status == "Afastado":
                tag = "afastado"
            else:
                tag = "par" if idx % 2 == 0 else "impar"
            
            valores = (
                membro.get("colaborador_nome", ""),
                membro.get("funcao", ""),
                self._formatar_data(membro.get("data_inicio")),
                self._formatar_data(membro.get("data_fim")),
                self._formatar_horas(membro.get("horas_trabalhadas", 0)),
                status,
                membro.get("observacoes", "")
            )
            
            self.tree.insert("", tk.END, values=valores, tags=(tag,))
    
    def _atualizar_totais(self):
        """Atualiza labels de totalizadores"""
        total_horas = sum(m.get("horas_trabalhadas", 0) for m in self.membros)
        total_ativos = len([m for m in self.membros if m.get("status") == "Ativo"])
        total_concluidos = len([m for m in self.membros if m.get("status") == "Concluído"])
        total_membros = len(self.membros)
        
        self.lbl_total_horas.config(text=f"{total_horas:.1f}h")
        self.lbl_total_ativos.config(text=str(total_ativos))
        self.lbl_total_concluidos.config(text=str(total_concluidos))
        self.lbl_total_membros.config(text=str(total_membros))
    
    def _adicionar_membro_dialog(self):
        """Abre dialog para adicionar membro"""
        DialogMembro(
            parent=self.root,
            colaboradores=self.colaboradores_disponiveis,
            callback=self._confirmar_adicao_membro
        )
    
    def _confirmar_adicao_membro(self, membro_data: Dict[str, Any]):
        """
        Confirma adição de membro
        
        Args:
            membro_data: Dados do membro
        """
        self.membros.append(membro_data)
        self._atualizar_tree()
        self._atualizar_totais()
    
    def _editar_membro_dialog(self):
        """Abre dialog para editar membro"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selecione", "Selecione um membro para editar")
            return
        
        idx = self.tree.index(selected[0])
        membro = self.membros[idx]
        
        DialogMembro(
            parent=self.root,
            colaboradores=self.colaboradores_disponiveis,
            membro_existente=membro,
            callback=lambda dados: self._confirmar_edicao_membro(idx, dados)
        )
    
    def _confirmar_edicao_membro(self, idx: int, membro_data: Dict[str, Any]):
        """
        Confirma edição de membro
        
        Args:
            idx: Índice do membro
            membro_data: Dados atualizados
        """
        self.membros[idx] = membro_data
        self._atualizar_tree()
        self._atualizar_totais()
    
    def _excluir_membro(self):
        """Exclui membro selecionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selecione", "Selecione um membro para excluir")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este membro da equipe?"):
            idx = self.tree.index(selected[0])
            del self.membros[idx]
            self._atualizar_tree()
            self._atualizar_totais()
    
    # =================================================================
    # MÉTODOS AUXILIARES
    # =================================================================
    
    @staticmethod
    def calcular_horas_trabalhadas(data_inicio: str, data_fim: str = None, horas_dia: float = 8.0) -> float:
        """
        Calcula horas trabalhadas entre duas datas
        
        Args:
            data_inicio: Data de início (YYYY-MM-DD)
            data_fim: Data de fim (YYYY-MM-DD, opcional)
            horas_dia: Horas por dia (padrão 8h)
            
        Returns:
            Total de horas trabalhadas
        """
        try:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            
            if data_fim:
                dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
            else:
                dt_fim = datetime.now()
            
            # Diferença em dias
            dias = (dt_fim - dt_inicio).days + 1  # +1 para incluir o dia inicial
            
            return dias * horas_dia
        except:
            return 0.0
    
    def _formatar_data(self, data: str) -> str:
        """
        Formata data para exibição
        
        Args:
            data: Data ISO (YYYY-MM-DD)
            
        Returns:
            Data formatada (DD/MM/YYYY) ou "-"
        """
        if not data:
            return "-"
        
        try:
            dt = datetime.strptime(data, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except:
            return data
    
    def _formatar_horas(self, horas: float) -> str:
        """
        Formata horas para exibição
        
        Args:
            horas: Quantidade de horas
            
        Returns:
            String formatada
        """
        if horas == 0:
            return "-"
        
        return f"{horas:.1f}h"


# =====================================================================
# DIALOG DE MEMBRO
# =====================================================================

class DialogMembro:
    """Dialog para adicionar/editar membro da equipe"""
    
    def __init__(self, parent: tk.Tk, colaboradores: List[Dict[str, Any]], 
                 callback: callable, membro_existente: Dict[str, Any] = None):
        """
        Inicializa dialog
        
        Args:
            parent: Janela pai
            colaboradores: Lista de colaboradores disponíveis
            callback: Função a chamar ao confirmar
            membro_existente: Dados do membro (para edição)
        """
        self.colaboradores = colaboradores
        self.callback = callback
        self.membro_existente = membro_existente
        self.is_edicao = membro_existente is not None
        
        # Setup dialog
        self.dialog = tk.Toplevel(parent)
        titulo = "✏️ Editar Membro" if self.is_edicao else "➕ Adicionar Membro"
        self.dialog.title(titulo)
        self.dialog.geometry("550x650")
        self.dialog.configure(bg=COLORS["light"])
        self.dialog.resizable(False, False)
        
        # Modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centralizar
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Criar widgets
        self._criar_widgets()
        
        # Preencher dados se edição
        if self.is_edicao:
            self._preencher_dados()
    
    def _criar_widgets(self):
        """Cria widgets do dialog"""
        main_frame = tk.Frame(self.dialog, bg=COLORS["white"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Colaborador
        tk.Label(
            main_frame,
            text="Colaborador: *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.combo_colaborador = ttk.Combobox(
            main_frame,
            font=("Segoe UI", 11),
            width=45,
            state="readonly"
        )
        
        # Popular combo com colaboradores
        nomes = [f"{c.get('nome', '')} - {c.get('cpf', '')}" for c in self.colaboradores]
        self.combo_colaborador['values'] = nomes
        self.combo_colaborador.pack(fill=tk.X, pady=(0, 15))
        
        # Função
        tk.Label(
            main_frame,
            text="Função: *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.combo_funcao = ttk.Combobox(
            main_frame,
            font=("Segoe UI", 11),
            width=45,
            state="readonly"
        )
        self.combo_funcao['values'] = FUNCOES
        self.combo_funcao.pack(fill=tk.X, pady=(0, 15))
        
        # Data Início
        tk.Label(
            main_frame,
            text="Data Início: *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.date_inicio = DateEntry(
            main_frame,
            font=("Segoe UI", 11),
            width=43,
            background=COLORS["primary"],
            foreground=COLORS["white"],
            borderwidth=2,
            date_pattern="dd/mm/yyyy"
        )
        self.date_inicio.pack(fill=tk.X, pady=(0, 15))
        
        # Data Fim
        tk.Label(
            main_frame,
            text="Data Fim: (opcional)",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.date_fim = DateEntry(
            main_frame,
            font=("Segoe UI", 11),
            width=43,
            background=COLORS["secondary"],
            foreground=COLORS["white"],
            borderwidth=2,
            date_pattern="dd/mm/yyyy"
        )
        self.date_fim.pack(fill=tk.X, pady=(0, 15))
        
        # Status
        tk.Label(
            main_frame,
            text="Status: *",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.combo_status = ttk.Combobox(
            main_frame,
            font=("Segoe UI", 11),
            width=45,
            state="readonly"
        )
        self.combo_status['values'] = STATUS_EQUIPE
        self.combo_status.current(0)  # Ativo por padrão
        self.combo_status.pack(fill=tk.X, pady=(0, 15))
        
        # Observações
        tk.Label(
            main_frame,
            text="Observações:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.entry_obs = tk.Entry(main_frame, font=("Segoe UI", 10), width=50)
        self.entry_obs.pack(fill=tk.X, pady=(0, 20))
        
        # Botões
        btn_frame = tk.Frame(main_frame, bg=COLORS["white"])
        btn_frame.pack(pady=(10, 0))
        
        tk.Button(
            btn_frame,
            text="✅ Confirmar",
            command=self._confirmar,
            bg=COLORS["success"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            width=15,
            height=2,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="✖️ Cancelar",
            command=self.dialog.destroy,
            bg=COLORS["danger"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            width=15,
            height=2,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
    
    def _preencher_dados(self):
        """Preenche dialog com dados do membro existente"""
        if not self.membro_existente:
            return
        
        # Colaborador
        colab_nome = self.membro_existente.get("colaborador_nome", "")
        for idx, nome in enumerate(self.combo_colaborador['values']):
            if colab_nome in nome:
                self.combo_colaborador.current(idx)
                break
        
        # Função
        funcao = self.membro_existente.get("funcao", "")
        if funcao in FUNCOES:
            self.combo_funcao.current(FUNCOES.index(funcao))
        
        # Data Início
        data_inicio = self.membro_existente.get("data_inicio")
        if data_inicio:
            try:
                dt = datetime.strptime(data_inicio, "%Y-%m-%d")
                self.date_inicio.set_date(dt)
            except:
                pass
        
        # Data Fim
        data_fim = self.membro_existente.get("data_fim")
        if data_fim:
            try:
                dt = datetime.strptime(data_fim, "%Y-%m-%d")
                self.date_fim.set_date(dt)
            except:
                pass
        
        # Status
        status = self.membro_existente.get("status", "Ativo")
        if status in STATUS_EQUIPE:
            self.combo_status.current(STATUS_EQUIPE.index(status))
        
        # Observações
        obs = self.membro_existente.get("observacoes", "")
        self.entry_obs.insert(0, obs)
    
    def _confirmar(self):
        """Valida e confirma dados"""
        # Validar campos obrigatórios
        if not self.combo_colaborador.get():
            messagebox.showerror("Campo Obrigatório", "Selecione um colaborador")
            self.combo_colaborador.focus()
            return
        
        if not self.combo_funcao.get():
            messagebox.showerror("Campo Obrigatório", "Selecione uma função")
            self.combo_funcao.focus()
            return
        
        # Obter colaborador selecionado
        idx_colab = self.combo_colaborador.current()
        if idx_colab < 0 or idx_colab >= len(self.colaboradores):
            messagebox.showerror("Erro", "Colaborador inválido")
            return
        
        colaborador = self.colaboradores[idx_colab]
        
        # Datas
        data_inicio = self.date_inicio.get_date().strftime("%Y-%m-%d")
        data_fim = self.date_fim.get_date().strftime("%Y-%m-%d")
        
        # Validar data_fim >= data_inicio
        if data_fim < data_inicio:
            if not messagebox.askyesno(
                "Data Fim Anterior",
                "Data fim é anterior à data início.\n\nDeseja deixar data fim em branco?"
            ):
                return
            data_fim = None
        
        # Calcular horas trabalhadas
        horas = GridEquipe.calcular_horas_trabalhadas(data_inicio, data_fim)
        
        # Criar dados do membro
        membro_data = {
            "colaborador_id": colaborador.get("id"),
            "colaborador_nome": colaborador.get("nome"),
            "colaborador_cpf": colaborador.get("cpf"),
            "funcao": self.combo_funcao.get(),
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "horas_trabalhadas": horas,
            "status": self.combo_status.get(),
            "observacoes": self.entry_obs.get().strip()
        }
        
        self.callback(membro_data)
        self.dialog.destroy()


# =====================================================================
# FUNÇÃO DE TESTE
# =====================================================================

def main():
    """Função de teste standalone"""
    root = tk.Tk()
    root.withdraw()  # Esconder janela principal
    
    # Testar com OS fictícia
    app = GridEquipe(root, os_id=1)
    
    root.mainloop()


if __name__ == "__main__":
    main()
