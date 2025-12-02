"""
Grid de Materiais - FASE 104 TAREFA 6
Sistema ERP Primotex

Grid especializado para controle de materiais utilizados em Ordens de Serviço.

Funcionalidades:
- TreeView com 6 colunas (produto, qtd aplicada, qtd devolvida, perdas, estoque atualizado, obs)
- Dialog busca de produtos no estoque
- Controle de baixa/retorno automático no estoque
- Cálculo de perdas
- Totalizadores (aplicado, devolvido, perdas)
- Persistência via API (POST/GET materiais-json)
- Validações de quantidade vs estoque

Autor: GitHub Copilot
Data: 19/11/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Optional
import requests
import threading
from datetime import datetime

# Imports do projeto
from frontend.desktop.auth_middleware import create_auth_header, get_token_for_api
from frontend.desktop.dialog_produto_selector import DialogProdutoSelector


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


# =====================================================================
# CLASSE PRINCIPAL
# =====================================================================

class GridMateriais:
    """
    Grid de Materiais para Ordens de Serviço
    
    Gerencia controle de materiais:
    - Registro de materiais aplicados
    - Devolução de sobras ao estoque
    - Controle de perdas
    - Integração com sistema de estoque
    """
    
    def __init__(self, parent: tk.Tk, os_id: Optional[int] = None):
        """
        Inicializa grid de materiais
        
        Args:
            parent: Janela pai (Tk ou Toplevel)
            os_id: ID da OS (None para rascunho)
        """
        self.parent = parent
        self.os_id = os_id
        self.token = get_token_for_api()
        
        # Dados
        self.materiais: List[Dict[str, Any]] = []
        
        # Setup da janela
        self._setup_window()
        self._criar_widgets()
        
        # Carregar dados existentes
        if self.os_id:
            self._carregar_materiais()
    
    def _setup_window(self):
        """Configura a janela principal"""
        self.root = tk.Toplevel(self.parent)
        self.root.title("📦 Controle de Materiais - OS")
        self.root.geometry("1300x700")
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
            text="📦 CONTROLE DE MATERIAIS",
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
            text="➕ Adicionar Material",
            command=self._adicionar_material_dialog,
            bg=COLORS["success"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            width=18,
            height=2,
            relief=tk.FLAT,
            cursor="hand2"
        )
        btn_adicionar.pack(side=tk.LEFT, padx=5)
        
        # Botão Registrar Devolução
        btn_devolver = tk.Button(
            btn_container,
            text="↩️ Registrar Devolução",
            command=self._registrar_devolucao_dialog,
            bg=COLORS["info"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            width=18,
            height=2,
            relief=tk.FLAT,
            cursor="hand2"
        )
        btn_devolver.pack(side=tk.LEFT, padx=5)
        
        # Botão Excluir
        btn_excluir = tk.Button(
            btn_container,
            text="🗑️ Excluir",
            command=self._excluir_material,
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
            command=self._salvar_materiais,
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
        """Cria TreeView para exibir materiais"""
        # Frame container
        tree_frame = tk.Frame(self.root, bg=COLORS["white"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # TreeView
        colunas = ("produto", "qtd_aplicada", "qtd_devolvida", "perdas", "estoque_atualizado", "obs")
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
        self.tree.heading("produto", text="Produto", anchor=tk.W)
        self.tree.heading("qtd_aplicada", text="Qtd Aplicada", anchor=tk.CENTER)
        self.tree.heading("qtd_devolvida", text="Qtd Devolvida", anchor=tk.CENTER)
        self.tree.heading("perdas", text="Perdas", anchor=tk.CENTER)
        self.tree.heading("estoque_atualizado", text="Estoque Atualizado", anchor=tk.CENTER)
        self.tree.heading("obs", text="Observações", anchor=tk.W)
        
        self.tree.column("produto", width=300, anchor=tk.W)
        self.tree.column("qtd_aplicada", width=120, anchor=tk.CENTER)
        self.tree.column("qtd_devolvida", width=130, anchor=tk.CENTER)
        self.tree.column("perdas", width=100, anchor=tk.CENTER)
        self.tree.column("estoque_atualizado", width=150, anchor=tk.CENTER)
        self.tree.column("obs", width=250, anchor=tk.W)
        
        # Estilo zebra
        self.tree.tag_configure("par", background="#f8f9fa")
        self.tree.tag_configure("impar", background="#ffffff")
        self.tree.tag_configure("alerta", background="#fff3cd", foreground="#856404")
        
        # Bind double-click para edição
        self.tree.bind("<Double-1>", lambda e: self._registrar_devolucao_dialog())
        
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
        self.lbl_total_aplicado = self._criar_label_total(valores_frame, "Total Aplicado:", "0 itens", 0)
        self.lbl_total_devolvido = self._criar_label_total(valores_frame, "Total Devolvido:", "0 itens", 1)
        self.lbl_total_perdas = self._criar_label_total(valores_frame, "Total Perdas:", "0 itens", 2)
    
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
        frame.grid(row=0, column=col, padx=20, pady=10, sticky="w")
        
        lbl_titulo = tk.Label(
            frame,
            text=titulo,
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            fg=COLORS["dark"]
        )
        lbl_titulo.pack(anchor=tk.W)
        
        # Cor baseada no tipo
        cor = COLORS["success"] if "Aplicado" in titulo else (
            COLORS["info"] if "Devolvido" in titulo else COLORS["warning"]
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
    # MÉTODOS DE DADOS
    # =================================================================
    
    def _carregar_materiais(self):
        """Carrega materiais existentes da API"""
        if not self.os_id:
            return
        
        def _request():
            try:
                headers = create_auth_header()
                url = f"{API_BASE_URL}/api/v1/os/{self.os_id}/materiais-json"
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.materiais = data.get("materiais", [])
                    self.root.after(0, self._atualizar_tree)
                    self.root.after(0, self._atualizar_totais)
                elif response.status_code == 404:
                    # Sem materiais ainda
                    self.materiais = []
                else:
                    self.root.after(
                        0,
                        lambda: messagebox.showerror(
                            "Erro",
                            f"Erro ao carregar materiais: {response.status_code}"
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
    
    def _salvar_materiais(self):
        """Salva materiais no backend"""
        if not self.os_id:
            messagebox.showwarning(
                "OS Necessária",
                "Salve a OS antes de salvar os materiais"
            )
            return
        
        def _request():
            try:
                headers = create_auth_header()
                url = f"{API_BASE_URL}/api/v1/os/{self.os_id}/materiais-json"
                
                payload = {
                    "materiais": self.materiais,
                    "timestamp": datetime.now().isoformat()
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.root.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Sucesso",
                            "✅ Materiais salvos com sucesso!"
                        )
                    )
                else:
                    self.root.after(
                        0,
                        lambda: messagebox.showerror(
                            "Erro",
                            f"Erro ao salvar materiais: {response.status_code}\n{response.text}"
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
        """Atualiza TreeView com dados dos materiais"""
        # Limpar
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Preencher
        for idx, material in enumerate(self.materiais):
            tag = "par" if idx % 2 == 0 else "impar"
            
            # Alerta se houver perdas
            perdas = material.get("perdas", 0)
            if perdas > 0:
                tag = "alerta"
            
            valores = (
                material.get("produto_nome", ""),
                self._formatar_quantidade(material.get("qtd_aplicada", 0)),
                self._formatar_quantidade(material.get("qtd_devolvida", 0)),
                self._formatar_quantidade(perdas),
                self._formatar_quantidade(material.get("estoque_atualizado", 0)),
                material.get("observacoes", "")
            )
            
            self.tree.insert("", tk.END, values=valores, tags=(tag,))
    
    def _atualizar_totais(self):
        """Atualiza labels de totalizadores"""
        total_aplicado = len([m for m in self.materiais if m.get("qtd_aplicada", 0) > 0])
        total_devolvido = len([m for m in self.materiais if m.get("qtd_devolvida", 0) > 0])
        total_com_perdas = len([m for m in self.materiais if m.get("perdas", 0) > 0])
        
        self.lbl_total_aplicado.config(text=f"{total_aplicado} itens")
        self.lbl_total_devolvido.config(text=f"{total_devolvido} itens")
        self.lbl_total_perdas.config(text=f"{total_com_perdas} itens com perdas")
    
    def _adicionar_material_dialog(self):
        """Abre dialog para adicionar material (busca no estoque)"""
        DialogProdutoSelector(
            parent=self.root,
            callback=self._adicionar_material_do_estoque
        )
    
    def _adicionar_material_do_estoque(self, produto: Dict[str, Any]):
        """
        Adiciona material selecionado do estoque
        
        Args:
            produto: Dados do produto
        """
        # Dialog para quantidade aplicada
        dialog = DialogQuantidade(
            parent=self.root,
            produto=produto,
            callback=self._confirmar_adicao_material
        )
    
    def _confirmar_adicao_material(self, material_data: Dict[str, Any]):
        """
        Confirma adição de material
        
        Args:
            material_data: Dados do material
        """
        self.materiais.append(material_data)
        self._atualizar_tree()
        self._atualizar_totais()
    
    def _registrar_devolucao_dialog(self):
        """Abre dialog para registrar devolução de material"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selecione", "Selecione um material para registrar devolução")
            return
        
        idx = self.tree.index(selected[0])
        material = self.materiais[idx]
        
        # Dialog de devolução
        dialog = DialogDevolucao(
            parent=self.root,
            material=material,
            callback=lambda dados: self._confirmar_devolucao(idx, dados)
        )
    
    def _confirmar_devolucao(self, idx: int, dados_devolucao: Dict[str, Any]):
        """
        Confirma devolução de material
        
        Args:
            idx: Índice do material
            dados_devolucao: Dados da devolução
        """
        self.materiais[idx].update(dados_devolucao)
        self._atualizar_tree()
        self._atualizar_totais()
    
    def _excluir_material(self):
        """Exclui material selecionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selecione", "Selecione um material para excluir")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este material?"):
            idx = self.tree.index(selected[0])
            del self.materiais[idx]
            self._atualizar_tree()
            self._atualizar_totais()
    
    # =================================================================
    # MÉTODOS AUXILIARES
    # =================================================================
    
    def _formatar_quantidade(self, qtd: float) -> str:
        """
        Formata quantidade para exibição
        
        Args:
            qtd: Quantidade
            
        Returns:
            String formatada
        """
        if qtd == 0:
            return "-"
        
        # Se for inteiro, mostra sem casas decimais
        if qtd == int(qtd):
            return str(int(qtd))
        
        return f"{qtd:.2f}".replace(".", ",")


# =====================================================================
# DIALOG DE QUANTIDADE
# =====================================================================

class DialogQuantidade:
    """Dialog para informar quantidade aplicada"""
    
    def __init__(self, parent: tk.Tk, produto: Dict[str, Any], callback: callable):
        """
        Inicializa dialog
        
        Args:
            parent: Janela pai
            produto: Dados do produto
            callback: Função a chamar ao confirmar
        """
        self.produto = produto
        self.callback = callback
        
        # Setup dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📦 Quantidade Aplicada")
        self.dialog.geometry("450x350")
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
    
    def _criar_widgets(self):
        """Cria widgets do dialog"""
        main_frame = tk.Frame(self.dialog, bg=COLORS["white"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Info do produto
        tk.Label(
            main_frame,
            text="Produto:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        tk.Label(
            main_frame,
            text=self.produto.get("nome", ""),
            font=("Segoe UI", 12),
            bg=COLORS["light"],
            fg=COLORS["dark"],
            relief=tk.SUNKEN,
            padx=10,
            pady=5
        ).pack(fill=tk.X, pady=(0, 15))
        
        # Estoque atual
        estoque_atual = self.produto.get("estoque_atual", 0)
        tk.Label(
            main_frame,
            text=f"Estoque Atual: {estoque_atual:.2f}".replace(".", ","),
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            fg=COLORS["info"]
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Quantidade aplicada
        tk.Label(
            main_frame,
            text="Quantidade Aplicada:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.entry_qtd = tk.Entry(main_frame, font=("Segoe UI", 12), width=20)
        self.entry_qtd.pack(anchor=tk.W, pady=(0, 15))
        self.entry_qtd.focus()
        
        # Observações
        tk.Label(
            main_frame,
            text="Observações:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.entry_obs = tk.Entry(main_frame, font=("Segoe UI", 10), width=40)
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
    
    def _confirmar(self):
        """Valida e confirma quantidade"""
        try:
            qtd = float(self.entry_qtd.get().replace(",", "."))
            if qtd <= 0:
                raise ValueError("Quantidade deve ser maior que zero")
            
            estoque_atual = self.produto.get("estoque_atual", 0)
            if qtd > estoque_atual:
                if not messagebox.askyesno(
                    "Estoque Insuficiente",
                    f"Quantidade aplicada ({qtd:.2f}) é maior que o estoque ({estoque_atual:.2f}).\n\n"
                    "Deseja continuar mesmo assim?"
                ):
                    return
            
            # Criar dados do material
            material_data = {
                "produto_id": self.produto.get("id"),
                "produto_nome": self.produto.get("nome"),
                "produto_codigo": self.produto.get("codigo"),
                "qtd_aplicada": qtd,
                "qtd_devolvida": 0.0,
                "perdas": 0.0,
                "estoque_antes": estoque_atual,
                "estoque_atualizado": estoque_atual - qtd,
                "observacoes": self.entry_obs.get().strip(),
                "data_aplicacao": datetime.now().isoformat()
            }
            
            self.callback(material_data)
            self.dialog.destroy()
        
        except ValueError as e:
            messagebox.showerror("Valor Inválido", str(e))
            self.entry_qtd.focus()


# =====================================================================
# DIALOG DE DEVOLUÇÃO
# =====================================================================

class DialogDevolucao:
    """Dialog para registrar devolução de material"""
    
    def __init__(self, parent: tk.Tk, material: Dict[str, Any], callback: callable):
        """
        Inicializa dialog
        
        Args:
            parent: Janela pai
            material: Dados do material
            callback: Função a chamar ao confirmar
        """
        self.material = material
        self.callback = callback
        
        # Setup dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("↩️ Registrar Devolução")
        self.dialog.geometry("500x450")
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
    
    def _criar_widgets(self):
        """Cria widgets do dialog"""
        main_frame = tk.Frame(self.dialog, bg=COLORS["white"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Info do produto
        tk.Label(
            main_frame,
            text="Material:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        tk.Label(
            main_frame,
            text=self.material.get("produto_nome", ""),
            font=("Segoe UI", 12),
            bg=COLORS["light"],
            fg=COLORS["dark"],
            relief=tk.SUNKEN,
            padx=10,
            pady=5
        ).pack(fill=tk.X, pady=(0, 15))
        
        # Quantidade aplicada
        qtd_aplicada = self.material.get("qtd_aplicada", 0)
        qtd_devolvida = self.material.get("qtd_devolvida", 0)
        
        tk.Label(
            main_frame,
            text=f"Quantidade Aplicada: {qtd_aplicada:.2f}".replace(".", ","),
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            fg=COLORS["dark"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        tk.Label(
            main_frame,
            text=f"Já Devolvida: {qtd_devolvida:.2f}".replace(".", ","),
            font=("Segoe UI", 10),
            bg=COLORS["white"],
            fg=COLORS["info"]
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Quantidade a devolver
        tk.Label(
            main_frame,
            text="Quantidade a Devolver:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.entry_qtd_devolver = tk.Entry(main_frame, font=("Segoe UI", 12), width=20)
        self.entry_qtd_devolver.pack(anchor=tk.W, pady=(0, 15))
        self.entry_qtd_devolver.focus()
        
        # Perdas
        tk.Label(
            main_frame,
            text="Perdas/Quebras:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.entry_perdas = tk.Entry(main_frame, font=("Segoe UI", 12), width=20)
        self.entry_perdas.insert(0, "0")
        self.entry_perdas.pack(anchor=tk.W, pady=(0, 15))
        
        # Observações
        tk.Label(
            main_frame,
            text="Observações:",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["white"]
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.entry_obs = tk.Entry(main_frame, font=("Segoe UI", 10), width=45)
        self.entry_obs.insert(0, self.material.get("observacoes", ""))
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
    
    def _confirmar(self):
        """Valida e confirma devolução"""
        try:
            qtd_devolver = float(self.entry_qtd_devolver.get().replace(",", ".") or 0)
            perdas = float(self.entry_perdas.get().replace(",", ".") or 0)
            
            if qtd_devolver < 0 or perdas < 0:
                raise ValueError("Quantidades não podem ser negativas")
            
            qtd_aplicada = self.material.get("qtd_aplicada", 0)
            qtd_devolvida_anterior = self.material.get("qtd_devolvida", 0)
            
            total_devolver = qtd_devolvida_anterior + qtd_devolver + perdas
            
            if total_devolver > qtd_aplicada:
                messagebox.showerror(
                    "Quantidade Inválida",
                    f"Total devolvido + perdas ({total_devolver:.2f}) não pode ser maior que o aplicado ({qtd_aplicada:.2f})"
                )
                return
            
            # Atualizar dados
            estoque_antes = self.material.get("estoque_antes", 0)
            nova_qtd_devolvida = qtd_devolvida_anterior + qtd_devolver
            
            dados_devolucao = {
                "qtd_devolvida": nova_qtd_devolvida,
                "perdas": perdas,
                "estoque_atualizado": estoque_antes - qtd_aplicada + nova_qtd_devolvida,
                "observacoes": self.entry_obs.get().strip(),
                "data_devolucao": datetime.now().isoformat()
            }
            
            self.callback(dados_devolucao)
            self.dialog.destroy()
        
        except ValueError as e:
            messagebox.showerror("Valor Inválido", str(e))
            self.entry_qtd_devolver.focus()


# =====================================================================
# FUNÇÃO DE TESTE
# =====================================================================

def main():
    """Função de teste standalone"""
    root = tk.Tk()
    root.withdraw()  # Esconder janela principal
    
    # Testar com OS fictícia
    app = GridMateriais(root, os_id=1)
    
    root.mainloop()


if __name__ == "__main__":
    main()
