"""
Dialog Seletor de Produtos para Grid Orçamento
Sistema ERP Primotex - FASE 104 TAREFA 3

Permite buscar e selecionar produtos do estoque para adicionar ao orçamento.

Features:
- Busca com autocomplete em tempo real
- TreeView paginado (20 produtos por página)
- Filtro por categoria
- Double-click seleciona produto
- Mostra: código, nome, preço, estoque disponível
- Integra com SessionManager para autenticação

Autor: GitHub Copilot
Data: 19/11/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
from typing import Callable, Optional, Dict, Any, List
import threading
from datetime import datetime

# Importa autenticação global
from frontend.desktop.auth_middleware import (
    get_token_for_api,
    create_auth_header
)

# Configuração API
API_BASE_URL = "http://127.0.0.1:8002"


class DialogProdutoSelector:
    """
    Dialog para seleção de produtos com busca e paginação.
    
    Uso:
        dialog = DialogProdutoSelector(
            parent=root,
            callback=lambda produto: print(produto)
        )
    """
    
    def __init__(
        self,
        parent: tk.Tk,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Inicializa dialog de seleção de produtos.
        
        Args:
            parent: Janela pai (Toplevel ou Tk)
            callback: Função chamada ao selecionar produto (recebe dict com dados)
        """
        self.parent = parent
        self.callback = callback
        self.token = get_token_for_api()
        
        # Estado
        self.produtos: List[Dict[str, Any]] = []
        self.produto_selecionado: Optional[Dict[str, Any]] = None
        self.current_page = 1
        self.total_pages = 1
        self.items_per_page = 20
        self.search_term = ""
        self.categoria_filtro = "Todas"
        self.categorias: List[str] = ["Todas"]
        
        # Cria janela modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Selecionar Produto")
        self.dialog.geometry("900x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centraliza na tela
        self._centralizar_janela()
        
        # Constrói interface
        self._criar_interface()
        
        # Carrega categorias
        self._carregar_categorias()
        
        # Carrega produtos iniciais
        self._carregar_produtos()
        
    def _centralizar_janela(self):
        """Centraliza dialog na tela."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def _criar_interface(self):
        """Cria todos os elementos da interface."""
        # Frame principal
        main_frame = tk.Frame(self.dialog, bg="white")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="🔍 Buscar Produto no Estoque",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 15))
        
        # Frame de busca e filtros
        search_frame = tk.Frame(main_frame, bg="white")
        search_frame.pack(fill="x", pady=(0, 10))
        
        # Busca
        tk.Label(
            search_frame,
            text="Buscar:",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(side="left", padx=(0, 5))
        
        self.search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 10),
            width=40
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        
        # Filtro categoria
        tk.Label(
            search_frame,
            text="Categoria:",
            font=("Segoe UI", 10),
            bg="white"
        ).pack(side="left", padx=(0, 5))
        
        self.categoria_combo = ttk.Combobox(
            search_frame,
            values=self.categorias,
            state="readonly",
            width=20,
            font=("Segoe UI", 9)
        )
        self.categoria_combo.set("Todas")
        self.categoria_combo.pack(side="left", padx=(0, 10))
        self.categoria_combo.bind("<<ComboboxSelected>>", self._on_categoria_change)
        
        # Botão limpar
        btn_limpar = tk.Button(
            search_frame,
            text="🗑️ Limpar",
            command=self._limpar_filtros,
            bg="#95a5a6",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=5
        )
        btn_limpar.pack(side="left")
        
        # Frame TreeView
        tree_frame = tk.Frame(main_frame, bg="white")
        tree_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")
        
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # TreeView
        columns = ("codigo", "nome", "categoria", "preco", "estoque")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=15
        )
        
        # Configurar colunas
        self.tree.heading("codigo", text="Código", anchor="w")
        self.tree.heading("nome", text="Nome do Produto", anchor="w")
        self.tree.heading("categoria", text="Categoria", anchor="w")
        self.tree.heading("preco", text="Preço Unit.", anchor="e")
        self.tree.heading("estoque", text="Estoque", anchor="e")
        
        self.tree.column("codigo", width=100, anchor="w")
        self.tree.column("nome", width=350, anchor="w")
        self.tree.column("categoria", width=150, anchor="w")
        self.tree.column("preco", width=120, anchor="e")
        self.tree.column("estoque", width=100, anchor="e")
        
        self.tree.pack(fill="both", expand=True)
        
        # Conectar scrollbars
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Bindings
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Return>", self._on_double_click)
        
        # Frame paginação
        pag_frame = tk.Frame(main_frame, bg="white")
        pag_frame.pack(fill="x", pady=(10, 0))
        
        self.btn_prev = tk.Button(
            pag_frame,
            text="◀ Anterior",
            command=self._pagina_anterior,
            state="disabled",
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=5
        )
        self.btn_prev.pack(side="left", padx=(0, 10))
        
        self.page_label = tk.Label(
            pag_frame,
            text="Página 1 de 1",
            font=("Segoe UI", 10),
            bg="white",
            fg="#7f8c8d"
        )
        self.page_label.pack(side="left", expand=True)
        
        self.btn_next = tk.Button(
            pag_frame,
            text="Próxima ▶",
            command=self._proxima_pagina,
            state="disabled",
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=5
        )
        self.btn_next.pack(side="right", padx=(10, 0))
        
        # Frame botões ação
        action_frame = tk.Frame(main_frame, bg="white")
        action_frame.pack(fill="x", pady=(15, 0))
        
        btn_cancelar = tk.Button(
            action_frame,
            text="❌ Cancelar",
            command=self._cancelar,
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        btn_cancelar.pack(side="right", padx=(10, 0))
        
        self.btn_selecionar = tk.Button(
            action_frame,
            text="✅ Selecionar",
            command=self._selecionar_produto,
            state="disabled",
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.btn_selecionar.pack(side="right")
        
        # Info label
        self.info_label = tk.Label(
            action_frame,
            text="💡 Dica: Double-click em um produto para selecioná-lo rapidamente",
            font=("Segoe UI", 9, "italic"),
            bg="white",
            fg="#95a5a6"
        )
        self.info_label.pack(side="left")
        
    def _carregar_categorias(self):
        """Carrega lista de categorias únicas via API."""
        def task():
            try:
                headers = create_auth_header()
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/produtos",
                    headers=headers,
                    params={"limit": 1000},  # Pega todos para extrair categorias
                    timeout=10
                )
                
                if response.status_code == 200:
                    produtos = response.json()
                    categorias_set = set()
                    
                    for p in produtos:
                        cat = p.get("categoria", "").strip()
                        if cat:
                            categorias_set.add(cat)
                    
                    categorias_list = ["Todas"] + sorted(list(categorias_set))
                    
                    # Atualiza UI no main thread
                    self.dialog.after(0, lambda: self._atualizar_categorias(categorias_list))
                    
            except Exception as e:
                print(f"Erro ao carregar categorias: {e}")
        
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
        
    def _atualizar_categorias(self, categorias: List[str]):
        """Atualiza combo de categorias (thread-safe)."""
        self.categorias = categorias
        self.categoria_combo["values"] = categorias
        
    def _carregar_produtos(self):
        """Carrega produtos da API com filtros e paginação."""
        def task():
            try:
                headers = create_auth_header()
                
                # Parâmetros
                params = {
                    "limit": self.items_per_page,
                    "skip": (self.current_page - 1) * self.items_per_page
                }
                
                if self.search_term:
                    params["search"] = self.search_term
                
                if self.categoria_filtro != "Todas":
                    params["categoria"] = self.categoria_filtro
                
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/produtos",
                    headers=headers,
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    produtos = response.json()
                    
                    # Calcular total de páginas (aproximado)
                    # API não retorna total, então estimamos
                    total_produtos = len(produtos)
                    self.total_pages = max(1, (total_produtos + self.items_per_page - 1) // self.items_per_page)
                    
                    # Atualiza UI no main thread
                    self.dialog.after(0, lambda: self._atualizar_tree(produtos))
                    
                else:
                    self.dialog.after(0, lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao carregar produtos: {response.status_code}"
                    ))
                    
            except Exception as e:
                self.dialog.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro ao conectar com API: {str(e)}"
                ))
        
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
        
    def _atualizar_tree(self, produtos: List[Dict[str, Any]]):
        """Atualiza TreeView com produtos (thread-safe)."""
        # Limpa tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.produtos = produtos
        
        # Popula tree
        for produto in produtos:
            codigo = produto.get("codigo", "")
            nome = produto.get("nome", "")
            categoria = produto.get("categoria", "")
            preco = produto.get("preco_venda", 0.0)
            estoque = produto.get("estoque_atual", 0)
            
            # Formata valores
            preco_fmt = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            estoque_fmt = f"{estoque:,}".replace(",", ".")
            
            self.tree.insert(
                "",
                "end",
                values=(codigo, nome, categoria, preco_fmt, estoque_fmt),
                tags=("produto",)
            )
        
        # Atualiza label paginação
        self._atualizar_paginacao()
        
        # Atualiza estado dos botões
        self.btn_prev["state"] = "normal" if self.current_page > 1 else "disabled"
        self.btn_next["state"] = "normal" if len(produtos) == self.items_per_page else "disabled"
        
    def _atualizar_paginacao(self):
        """Atualiza label de paginação."""
        total_produtos = len(self.produtos)
        inicio = (self.current_page - 1) * self.items_per_page + 1
        fim = inicio + total_produtos - 1
        
        self.page_label.config(
            text=f"Mostrando {inicio}-{fim} | Página {self.current_page}"
        )
        
    def _on_search_change(self, event):
        """Callback quando texto de busca muda."""
        # Debounce: espera 500ms após última tecla
        if hasattr(self, "_search_timer"):
            self.dialog.after_cancel(self._search_timer)
        
        self._search_timer = self.dialog.after(500, self._aplicar_busca)
        
    def _aplicar_busca(self):
        """Aplica busca e recarrega produtos."""
        self.search_term = self.search_entry.get().strip()
        self.current_page = 1
        self._carregar_produtos()
        
    def _on_categoria_change(self, event):
        """Callback quando categoria muda."""
        self.categoria_filtro = self.categoria_combo.get()
        self.current_page = 1
        self._carregar_produtos()
        
    def _limpar_filtros(self):
        """Limpa todos os filtros."""
        self.search_entry.delete(0, tk.END)
        self.categoria_combo.set("Todas")
        self.search_term = ""
        self.categoria_filtro = "Todas"
        self.current_page = 1
        self._carregar_produtos()
        
    def _pagina_anterior(self):
        """Navega para página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            self._carregar_produtos()
            
    def _proxima_pagina(self):
        """Navega para próxima página."""
        self.current_page += 1
        self._carregar_produtos()
        
    def _on_double_click(self, event):
        """Callback para double-click no TreeView."""
        selection = self.tree.selection()
        if selection:
            self._selecionar_produto()
            
    def _selecionar_produto(self):
        """Seleciona produto e fecha dialog."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "Aviso",
                "Selecione um produto primeiro"
            )
            return
        
        # Pega índice do item selecionado
        item = selection[0]
        index = self.tree.index(item)
        
        if 0 <= index < len(self.produtos):
            self.produto_selecionado = self.produtos[index]
            
            # Chama callback
            if self.callback:
                self.callback(self.produto_selecionado)
            
            # Fecha dialog
            self.dialog.destroy()
        
    def _cancelar(self):
        """Cancela seleção e fecha dialog."""
        self.produto_selecionado = None
        self.dialog.destroy()


# ============================================================================
# TESTE STANDALONE
# ============================================================================

def teste_dialog():
    """Função de teste standalone."""
    def on_produto_selecionado(produto):
        print("\n" + "="*60)
        print("PRODUTO SELECIONADO:")
        print("="*60)
        for key, value in produto.items():
            print(f"{key}: {value}")
        print("="*60 + "\n")
    
    root = tk.Tk()
    root.withdraw()  # Esconde janela principal
    
    dialog = DialogProdutoSelector(
        parent=root,
        callback=on_produto_selecionado
    )
    
    root.wait_window(dialog.dialog)
    root.destroy()


if __name__ == "__main__":
    print("🔍 Testando Dialog Seletor de Produtos...")
    print("📋 Certifique-se de que:")
    print("   1. Backend está rodando (porta 8002)")
    print("   2. Você está autenticado (SessionManager)")
    print("   3. Existem produtos cadastrados no sistema")
    print("\n" + "="*60 + "\n")
    
    teste_dialog()
