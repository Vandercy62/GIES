"""
Grid de Medições - FASE 104 TAREFA 5
Sistema ERP Primotex

Grid especializado para registro e cálculo de medições técnicas em Ordens de Serviço.

Funcionalidades:
- TreeView com 7 colunas (descrição, tipo, medida1, medida2, resultado, unidade, obs)
- 4 tipos de medição: Área, Perímetro, Linear, Quantidade
- Cálculo automático de resultados
- Totalizadores por tipo de medição
- Persistência via API (POST/GET medicoes-json)
- Edição double-click
- Validações de entrada

Autor: GitHub Copilot
Data: 19/11/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, List, Any, Optional
import requests
import threading
from datetime import datetime

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

TIPOS_MEDICAO = [
    "Área",        # Largura × Altura (m²)
    "Perímetro",   # 2 × (Largura + Altura) (m)
    "Linear",      # Comprimento (m)
    "Quantidade"   # Quantidade inteira (un)
]

UNIDADES = {
    "Área": "m²",
    "Perímetro": "m",
    "Linear": "m",
    "Quantidade": "un"
}


# =====================================================================
# CLASSE PRINCIPAL
# =====================================================================

class GridMedicoes:
    """
    Grid de Medições para Ordens de Serviço
    
    Permite registrar e calcular medições técnicas de forma estruturada:
    - Áreas (largura × altura)
    - Perímetros (2 × (largura + altura))
    - Medidas lineares (comprimento)
    - Quantidades (contagem)
    """
    
    def __init__(self, parent: tk.Tk, os_id: Optional[int] = None):
        """
        Inicializa grid de medições
        
        Args:
            parent: Janela pai (Tk ou Toplevel)
            os_id: ID da OS (None para rascunho)
        """
        self.parent = parent
        self.os_id = os_id
        self.token = get_token_for_api()
        
        # Dados
        self.medicoes: List[Dict[str, Any]] = []
        
        # Setup da janela
        self._setup_window()
        self._criar_widgets()
        
        # Carregar dados existentes
        if self.os_id:
            self._carregar_medicoes()
    
    def _setup_window(self):
        """Configura a janela principal"""
        self.root = tk.Toplevel(self.parent)
        self.root.title("📐 Medições Técnicas - OS")
        self.root.geometry("1200x700")
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
            text="📐 MEDIÇÕES TÉCNICAS",
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
            text="➕ Adicionar Medição",
            command=self._adicionar_medicao_dialog,
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
            command=self._editar_medicao_dialog,
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
            command=self._excluir_medicao,
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
            command=self._salvar_medicoes,
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
        """Cria TreeView para exibir medições"""
        # Frame container
        tree_frame = tk.Frame(self.root, bg=COLORS["white"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # TreeView
        colunas = ("descricao", "tipo", "medida1", "medida2", "resultado", "unidade", "obs")
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
        self.tree.heading("descricao", text="Descrição", anchor=tk.W)
        self.tree.heading("tipo", text="Tipo", anchor=tk.CENTER)
        self.tree.heading("medida1", text="Medida 1", anchor=tk.CENTER)
        self.tree.heading("medida2", text="Medida 2", anchor=tk.CENTER)
        self.tree.heading("resultado", text="Resultado", anchor=tk.CENTER)
        self.tree.heading("unidade", text="Unidade", anchor=tk.CENTER)
        self.tree.heading("obs", text="Observações", anchor=tk.W)
        
        self.tree.column("descricao", width=250, anchor=tk.W)
        self.tree.column("tipo", width=100, anchor=tk.CENTER)
        self.tree.column("medida1", width=100, anchor=tk.CENTER)
        self.tree.column("medida2", width=100, anchor=tk.CENTER)
        self.tree.column("resultado", width=120, anchor=tk.CENTER)
        self.tree.column("unidade", width=80, anchor=tk.CENTER)
        self.tree.column("obs", width=300, anchor=tk.W)
        
        # Estilo zebra
        self.tree.tag_configure("par", background="#f8f9fa")
        self.tree.tag_configure("impar", background="#ffffff")
        
        # Bind double-click para edição
        self.tree.bind("<Double-1>", lambda e: self._editar_medicao_dialog())
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
    
    def _criar_totalizadores(self):
        """Cria seção de totalizadores por tipo"""
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
        self.lbl_total_area = self._criar_label_total(valores_frame, "Área Total:", "0,00 m²", 0)
        self.lbl_total_perimetro = self._criar_label_total(valores_frame, "Perímetro Total:", "0,00 m", 1)
        self.lbl_total_linear = self._criar_label_total(valores_frame, "Linear Total:", "0,00 m", 2)
        self.lbl_total_quantidade = self._criar_label_total(valores_frame, "Quantidade Total:", "0 un", 3)
    
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
        
        lbl_valor = tk.Label(
            frame,
            text=valor_inicial,
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["white"],
            fg=COLORS["success"]
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
    # MÉTODOS DE DADOS
    # =================================================================
    
    def _carregar_medicoes(self):
        """Carrega medições existentes da API"""
        if not self.os_id:
            return
        
        def _request():
            try:
                headers = create_auth_header()
                url = f"{API_BASE_URL}/api/v1/os/{self.os_id}/medicoes-json"
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.medicoes = data.get("medicoes", [])
                    self.root.after(0, self._atualizar_tree)
                    self.root.after(0, self._atualizar_totais)
                elif response.status_code == 404:
                    # Sem medições ainda
                    self.medicoes = []
                else:
                    self.root.after(
                        0,
                        lambda: messagebox.showerror(
                            "Erro",
                            f"Erro ao carregar medições: {response.status_code}"
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
    
    def _salvar_medicoes(self):
        """Salva medições no backend"""
        if not self.os_id:
            messagebox.showwarning(
                "OS Necessária",
                "Salve a OS antes de salvar as medições"
            )
            return
        
        def _request():
            try:
                headers = create_auth_header()
                url = f"{API_BASE_URL}/api/v1/os/{self.os_id}/medicoes-json"
                
                payload = {
                    "medicoes": self.medicoes,
                    "timestamp": datetime.now().isoformat()
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.root.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Sucesso",
                            "✅ Medições salvas com sucesso!"
                        )
                    )
                else:
                    self.root.after(
                        0,
                        lambda: messagebox.showerror(
                            "Erro",
                            f"Erro ao salvar medições: {response.status_code}\n{response.text}"
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
        """Atualiza TreeView com dados das medições"""
        # Limpar
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Preencher
        for idx, medicao in enumerate(self.medicoes):
            tag = "par" if idx % 2 == 0 else "impar"
            
            valores = (
                medicao.get("descricao", ""),
                medicao.get("tipo", ""),
                self._formatar_numero(medicao.get("medida1", 0)),
                self._formatar_numero(medicao.get("medida2", 0)),
                self._formatar_resultado(medicao),
                medicao.get("unidade", ""),
                medicao.get("observacoes", "")
            )
            
            self.tree.insert("", tk.END, values=valores, tags=(tag,))
    
    def _atualizar_totais(self):
        """Atualiza labels de totalizadores"""
        totais = {
            "Área": 0.0,
            "Perímetro": 0.0,
            "Linear": 0.0,
            "Quantidade": 0
        }
        
        for medicao in self.medicoes:
            tipo = medicao.get("tipo", "")
            resultado = medicao.get("resultado", 0)
            
            if tipo in totais:
                if tipo == "Quantidade":
                    totais[tipo] += int(resultado)
                else:
                    totais[tipo] += float(resultado)
        
        # Atualizar labels
        self.lbl_total_area.config(text=f"{totais['Área']:,.2f} m²".replace(",", "X").replace(".", ",").replace("X", "."))
        self.lbl_total_perimetro.config(text=f"{totais['Perímetro']:,.2f} m".replace(",", "X").replace(".", ",").replace("X", "."))
        self.lbl_total_linear.config(text=f"{totais['Linear']:,.2f} m".replace(",", "X").replace(".", ",").replace("X", "."))
        self.lbl_total_quantidade.config(text=f"{totais['Quantidade']} un")
    
    def _adicionar_medicao_dialog(self):
        """Abre dialog para adicionar nova medição"""
        dialog = DialogMedicao(self.root, callback=self._adicionar_medicao)
    
    def _adicionar_medicao(self, medicao: Dict[str, Any]):
        """
        Adiciona medição à lista
        
        Args:
            medicao: Dados da medição
        """
        self.medicoes.append(medicao)
        self._atualizar_tree()
        self._atualizar_totais()
    
    def _editar_medicao_dialog(self):
        """Abre dialog para editar medição selecionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selecione", "Selecione uma medição para editar")
            return
        
        idx = self.tree.index(selected[0])
        medicao_atual = self.medicoes[idx]
        
        dialog = DialogMedicao(
            self.root,
            callback=lambda m: self._atualizar_medicao(idx, m),
            medicao_inicial=medicao_atual
        )
    
    def _atualizar_medicao(self, idx: int, medicao: Dict[str, Any]):
        """
        Atualiza medição existente
        
        Args:
            idx: Índice da medição
            medicao: Novos dados
        """
        self.medicoes[idx] = medicao
        self._atualizar_tree()
        self._atualizar_totais()
    
    def _excluir_medicao(self):
        """Exclui medição selecionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selecione", "Selecione uma medição para excluir")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir esta medição?"):
            idx = self.tree.index(selected[0])
            del self.medicoes[idx]
            self._atualizar_tree()
            self._atualizar_totais()
    
    # =================================================================
    # MÉTODOS AUXILIARES
    # =================================================================
    
    def _formatar_numero(self, valor: float) -> str:
        """
        Formata número para exibição
        
        Args:
            valor: Número
            
        Returns:
            String formatada (1.234,56)
        """
        if valor == 0:
            return "-"
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def _formatar_resultado(self, medicao: Dict[str, Any]) -> str:
        """
        Formata resultado da medição
        
        Args:
            medicao: Dados da medição
            
        Returns:
            String formatada
        """
        resultado = medicao.get("resultado", 0)
        tipo = medicao.get("tipo", "")
        
        if tipo == "Quantidade":
            return str(int(resultado))
        else:
            return self._formatar_numero(resultado)
    
    @staticmethod
    def calcular_resultado(tipo: str, medida1: float, medida2: float) -> float:
        """
        Calcula resultado baseado no tipo de medição
        
        Args:
            tipo: Tipo de medição
            medida1: Primeira medida
            medida2: Segunda medida (opcional)
            
        Returns:
            Resultado calculado
        """
        if tipo == "Área":
            return medida1 * medida2
        elif tipo == "Perímetro":
            return 2 * (medida1 + medida2)
        elif tipo == "Linear":
            return medida1
        elif tipo == "Quantidade":
            return int(medida1)
        else:
            return 0.0


# =====================================================================
# DIALOG DE ADIÇÃO/EDIÇÃO
# =====================================================================

class DialogMedicao:
    """Dialog para adicionar/editar medição"""
    
    def __init__(
        self,
        parent: tk.Tk,
        callback: callable,
        medicao_inicial: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa dialog
        
        Args:
            parent: Janela pai
            callback: Função a chamar ao salvar
            medicao_inicial: Dados iniciais (edição)
        """
        self.callback = callback
        self.medicao_inicial = medicao_inicial
        self.is_edit = medicao_inicial is not None
        
        # Setup dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("✏️ Editar Medição" if self.is_edit else "➕ Nova Medição")
        self.dialog.geometry("500x550")
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
        
        # Preencher dados iniciais
        if self.is_edit:
            self._preencher_dados()
    
    def _criar_widgets(self):
        """Cria widgets do dialog"""
        # Frame principal
        main_frame = tk.Frame(self.dialog, bg=COLORS["white"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Descrição
        self._criar_campo(main_frame, "Descrição:", 0)
        self.entry_descricao = tk.Entry(main_frame, font=("Segoe UI", 10), width=50)
        self.entry_descricao.grid(row=1, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        
        # Tipo
        self._criar_campo(main_frame, "Tipo de Medição:", 2)
        self.combo_tipo = ttk.Combobox(
            main_frame,
            values=TIPOS_MEDICAO,
            state="readonly",
            font=("Segoe UI", 10),
            width=48
        )
        self.combo_tipo.grid(row=3, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        self.combo_tipo.bind("<<ComboboxSelected>>", self._on_tipo_changed)
        
        # Medida 1
        self._criar_campo(main_frame, "Medida 1:", 4)
        self.entry_medida1 = tk.Entry(main_frame, font=("Segoe UI", 10), width=23)
        self.entry_medida1.grid(row=5, column=0, pady=(0, 15), sticky="ew")
        self.entry_medida1.bind("<KeyRelease>", self._calcular_resultado_preview)
        
        # Medida 2
        self._criar_campo(main_frame, "Medida 2:", 4, column=1)
        self.entry_medida2 = tk.Entry(main_frame, font=("Segoe UI", 10), width=23)
        self.entry_medida2.grid(row=5, column=1, pady=(0, 15), padx=(10, 0), sticky="ew")
        self.entry_medida2.bind("<KeyRelease>", self._calcular_resultado_preview)
        
        # Label de ajuda
        self.lbl_ajuda = tk.Label(
            main_frame,
            text="",
            font=("Segoe UI", 9, "italic"),
            bg=COLORS["white"],
            fg=COLORS["info"]
        )
        self.lbl_ajuda.grid(row=6, column=0, columnspan=2, pady=(0, 10), sticky="w")
        
        # Resultado (preview)
        self._criar_campo(main_frame, "Resultado:", 7)
        self.lbl_resultado = tk.Label(
            main_frame,
            text="0,00",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["light"],
            fg=COLORS["success"],
            relief=tk.SUNKEN,
            padx=10,
            pady=5
        )
        self.lbl_resultado.grid(row=8, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        
        # Unidade
        self._criar_campo(main_frame, "Unidade:", 9)
        self.lbl_unidade = tk.Label(
            main_frame,
            text="-",
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            fg=COLORS["dark"]
        )
        self.lbl_unidade.grid(row=10, column=0, columnspan=2, pady=(0, 15), sticky="w")
        
        # Observações
        self._criar_campo(main_frame, "Observações:", 11)
        self.entry_obs = tk.Entry(main_frame, font=("Segoe UI", 10), width=50)
        self.entry_obs.grid(row=12, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        
        # Botões
        btn_frame = tk.Frame(main_frame, bg=COLORS["white"])
        btn_frame.grid(row=13, column=0, columnspan=2, pady=(10, 0))
        
        btn_salvar = tk.Button(
            btn_frame,
            text="💾 Salvar",
            command=self._salvar,
            bg=COLORS["success"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            width=15,
            height=2,
            relief=tk.FLAT,
            cursor="hand2"
        )
        btn_salvar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = tk.Button(
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
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def _criar_campo(self, parent: tk.Frame, texto: str, row: int, column: int = 0):
        """Cria label de campo"""
        lbl = tk.Label(
            parent,
            text=texto,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"],
            fg=COLORS["dark"]
        )
        lbl.grid(row=row, column=column, sticky="w", pady=(0, 5))
    
    def _preencher_dados(self):
        """Preenche campos com dados iniciais"""
        if not self.medicao_inicial:
            return
        
        self.entry_descricao.insert(0, self.medicao_inicial.get("descricao", ""))
        self.combo_tipo.set(self.medicao_inicial.get("tipo", ""))
        self.entry_medida1.insert(0, str(self.medicao_inicial.get("medida1", "")))
        self.entry_medida2.insert(0, str(self.medicao_inicial.get("medida2", "")))
        self.entry_obs.insert(0, self.medicao_inicial.get("observacoes", ""))
        
        self._on_tipo_changed()
        self._calcular_resultado_preview()
    
    def _on_tipo_changed(self, event=None):
        """Handler para mudança de tipo"""
        tipo = self.combo_tipo.get()
        
        if tipo == "Área":
            self.lbl_ajuda.config(text="Medida 1 = Largura (m) | Medida 2 = Altura (m)")
            self.entry_medida2.config(state="normal")
        elif tipo == "Perímetro":
            self.lbl_ajuda.config(text="Medida 1 = Largura (m) | Medida 2 = Altura (m)")
            self.entry_medida2.config(state="normal")
        elif tipo == "Linear":
            self.lbl_ajuda.config(text="Medida 1 = Comprimento (m) | Medida 2 não usada")
            self.entry_medida2.delete(0, tk.END)
            self.entry_medida2.config(state="disabled")
        elif tipo == "Quantidade":
            self.lbl_ajuda.config(text="Medida 1 = Quantidade (un) | Medida 2 não usada")
            self.entry_medida2.delete(0, tk.END)
            self.entry_medida2.config(state="disabled")
        
        # Atualizar unidade
        self.lbl_unidade.config(text=UNIDADES.get(tipo, "-"))
        
        self._calcular_resultado_preview()
    
    def _calcular_resultado_preview(self, event=None):
        """Calcula e exibe preview do resultado"""
        tipo = self.combo_tipo.get()
        if not tipo:
            return
        
        try:
            medida1 = float(self.entry_medida1.get() or 0)
            medida2 = float(self.entry_medida2.get() or 0)
            
            resultado = GridMedicoes.calcular_resultado(tipo, medida1, medida2)
            
            if tipo == "Quantidade":
                texto = str(int(resultado))
            else:
                texto = f"{resultado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            self.lbl_resultado.config(text=texto)
        except ValueError:
            self.lbl_resultado.config(text="0,00")
    
    def _salvar(self):
        """Valida e salva medição"""
        # Validar campos
        descricao = self.entry_descricao.get().strip()
        tipo = self.combo_tipo.get()
        
        if not descricao:
            messagebox.showwarning("Campo Obrigatório", "Preencha a descrição")
            self.entry_descricao.focus()
            return
        
        if not tipo:
            messagebox.showwarning("Campo Obrigatório", "Selecione o tipo de medição")
            self.combo_tipo.focus()
            return
        
        try:
            medida1 = float(self.entry_medida1.get() or 0)
            if medida1 <= 0:
                raise ValueError("Medida 1 deve ser maior que zero")
        except ValueError as e:
            messagebox.showwarning("Valor Inválido", f"Medida 1 inválida:\n{str(e)}")
            self.entry_medida1.focus()
            return
        
        # Medida 2 (opcional para alguns tipos)
        medida2 = 0.0
        if tipo in ["Área", "Perímetro"]:
            try:
                medida2 = float(self.entry_medida2.get() or 0)
                if medida2 <= 0:
                    raise ValueError("Medida 2 deve ser maior que zero")
            except ValueError as e:
                messagebox.showwarning("Valor Inválido", f"Medida 2 inválida:\n{str(e)}")
                self.entry_medida2.focus()
                return
        
        # Calcular resultado
        resultado = GridMedicoes.calcular_resultado(tipo, medida1, medida2)
        
        # Criar objeto medição
        medicao = {
            "descricao": descricao,
            "tipo": tipo,
            "medida1": medida1,
            "medida2": medida2,
            "resultado": resultado,
            "unidade": UNIDADES.get(tipo, ""),
            "observacoes": self.entry_obs.get().strip()
        }
        
        # Chamar callback
        self.callback(medicao)
        
        # Fechar dialog
        self.dialog.destroy()


# =====================================================================
# FUNÇÃO DE TESTE
# =====================================================================

def main():
    """Função de teste standalone"""
    root = tk.Tk()
    root.withdraw()  # Esconder janela principal
    
    # Testar com OS fictícia
    app = GridMedicoes(root, os_id=1)
    
    root.mainloop()


if __name__ == "__main__":
    main()
