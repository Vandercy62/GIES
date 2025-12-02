"""
Grid de Orçamento - FASE 104 TAREFA 2
Sistema de orçamento editável com cálculos automáticos

Funcionalidades:
- TreeView editável (Produto, Qtd, Unidade, Preço Unit, Desc%, Total)
- Seletor de produtos com autocomplete
- Cálculos automáticos (subtotal, impostos, total)
- Salvamento via API backend
- Export PDF profissional
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
import json
from pathlib import Path
import threading

# Imports locais
from frontend.desktop.auth_middleware import (
    require_login,
    get_token_for_api,
    create_auth_header
)
from frontend.desktop.dialog_produto_selector import DialogProdutoSelector
from frontend.desktop.pdf_orcamento_generator import PDFOrcamentoGenerator

# Constantes
API_BASE_URL = "http://127.0.0.1:8002"

COLORS = {
    "primary": "#2c3e50",
    "secondary": "#34495e",
    "success": "#27ae60",
    "danger": "#e74c3c",
    "warning": "#f39c12",
    "info": "#3498db",
    "light": "#ecf0f1",
    "dark": "#2c3e50",
    "white": "#ffffff",
    "bg_grid": "#f8f9fa",
    "border": "#dee2e6"
}


@require_login()
class GridOrcamento(tk.Frame):
    """Grid de orçamento editável com cálculos automáticos"""
    
    def __init__(self, parent, os_id: Optional[int] = None):
        """
        Inicializar grid de orçamento
        
        Args:
            parent: Widget pai (tkinter parent)
            os_id: ID da Ordem de Serviço (opcional)
        """
        super().__init__(parent, bg=COLORS["white"])
        self.parent = parent
        self.os_id = os_id
        self.token = get_token_for_api()
        
        # Estado do grid
        self.itens: List[Dict[str, Any]] = []
        self.item_editando: Optional[str] = None
        self.coluna_editando: Optional[str] = None
        
        # Criar interface
        self._criar_interface()
        
        # Carregar dados se os_id fornecido
        if self.os_id:
            self._carregar_orcamento()
    
    def _criar_interface(self):
        """Criar interface principal do grid"""
        # Título
        header_frame = tk.Frame(self, bg=COLORS["primary"], height=60)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_text = f"Orçamento - OS #{self.os_id}" if self.os_id else "Orçamento"
        tk.Label(
            header_frame,
            text=title_text,
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["primary"],
            fg=COLORS["white"]
        ).pack(side="left", padx=20, pady=15)
        
        # Toolbar
        self._criar_toolbar()
        
        # Grid principal
        self._criar_grid()
        
        # Painel de totais
        self._criar_painel_totais()
        
        # Barra de ações inferior
        self._criar_acoes_inferiores()
    
    def _criar_toolbar(self):
        """Criar barra de ferramentas"""
        toolbar = tk.Frame(self, bg=COLORS["light"], height=50)
        toolbar.pack(fill="x", padx=10, pady=(0, 5))
        toolbar.pack_propagate(False)
        
        # Botões Adicionar (Buscar no Estoque OU Manual)
        btn_buscar = tk.Button(
            toolbar,
            text="🔍 Buscar no Estoque",
            command=self._buscar_produto_estoque,
            bg=COLORS["success"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=5
        )
        btn_buscar.pack(side="left", padx=(5, 2), pady=8)
        
        btn_manual = tk.Button(
            toolbar,
            text="✏️ Entrada Manual",
            command=self._adicionar_item_dialog,
            bg=COLORS["info"],
            fg=COLORS["white"],
            font=("Segoe UI", 9),
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=5
        )
        btn_manual.pack(side="left", padx=(2, 5), pady=8)
        
        # Botão Remover Item
        btn_remove = tk.Button(
            toolbar,
            text="➖ Remover Item",
            command=self._remover_item,
            bg=COLORS["danger"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=5
        )
        btn_remove.pack(side="left", padx=5, pady=8)
        
        # Botão Limpar Tudo
        btn_limpar = tk.Button(
            toolbar,
            text="🗑️ Limpar Tudo",
            command=self._limpar_grid,
            bg=COLORS["warning"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=5
        )
        btn_limpar.pack(side="left", padx=5, pady=8)
        
        # Separador
        ttk.Separator(toolbar, orient="vertical").pack(
            side="left", fill="y", padx=10, pady=5
        )
        
        # Botão Importar Produtos
        btn_importar = tk.Button(
            toolbar,
            text="📦 Importar Produtos",
            command=self._importar_produtos_dialog,
            bg=COLORS["info"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=5
        )
        btn_importar.pack(side="left", padx=5, pady=8)
        
        # Info
        tk.Label(
            toolbar,
            text="💡 Duplo-clique para editar Qtd, Preço ou Desconto",
            font=("Segoe UI", 9, "italic"),
            bg=COLORS["light"],
            fg=COLORS["secondary"]
        ).pack(side="right", padx=10)
    
    def _criar_grid(self):
        """Criar TreeView do grid de orçamento"""
        # Frame container
        grid_frame = tk.Frame(self, bg=COLORS["white"])
        grid_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(grid_frame, orient="vertical")
        h_scroll = ttk.Scrollbar(grid_frame, orient="horizontal")
        
        # TreeView
        self.tree = ttk.Treeview(
            grid_frame,
            columns=(
                "codigo", "produto", "qtd", "unidade",
                "preco_unit", "desconto", "total"
            ),
            show="headings",
            height=12,
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )
        
        # Configurar scrollbars
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        # Definir colunas
        colunas = {
            "codigo": ("Código", 100, "w"),
            "produto": ("Produto/Serviço", 300, "w"),
            "qtd": ("Qtd", 80, "center"),
            "unidade": ("Unidade", 80, "center"),
            "preco_unit": ("Preço Unit. (R$)", 120, "e"),
            "desconto": ("Desc. (%)", 100, "center"),
            "total": ("Total (R$)", 120, "e")
        }
        
        for col, (texto, largura, anchor) in colunas.items():
            self.tree.heading(col, text=texto)
            self.tree.column(col, width=largura, anchor=anchor)
        
        # Estilo zebra
        self.tree.tag_configure("oddrow", background=COLORS["white"])
        self.tree.tag_configure("evenrow", background=COLORS["bg_grid"])
        
        # Posicionar elementos
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        grid_frame.grid_rowconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(0, weight=1)
        
        # Bindings
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Delete>", lambda e: self._remover_item())
    
    def _criar_painel_totais(self):
        """Criar painel de totais"""
        totais_frame = tk.Frame(self, bg=COLORS["light"], height=120)
        totais_frame.pack(fill="x", padx=10, pady=10)
        totais_frame.pack_propagate(False)
        
        # Título
        tk.Label(
            totais_frame,
            text="TOTAIS",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["light"],
            fg=COLORS["primary"]
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Grid de totais
        grid = tk.Frame(totais_frame, bg=COLORS["light"])
        grid.pack(fill="x", padx=15, pady=5)
        
        # Subtotal
        tk.Label(
            grid,
            text="Subtotal:",
            font=("Segoe UI", 10),
            bg=COLORS["light"],
            fg=COLORS["dark"]
        ).grid(row=0, column=0, sticky="w", pady=2)
        
        self.lbl_subtotal = tk.Label(
            grid,
            text="R$ 0,00",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["light"],
            fg=COLORS["dark"]
        )
        self.lbl_subtotal.grid(row=0, column=1, sticky="e", padx=20, pady=2)
        
        # Impostos (17%)
        tk.Label(
            grid,
            text="Impostos (17%):",
            font=("Segoe UI", 10),
            bg=COLORS["light"],
            fg=COLORS["dark"]
        ).grid(row=1, column=0, sticky="w", pady=2)
        
        self.lbl_impostos = tk.Label(
            grid,
            text="R$ 0,00",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["light"],
            fg=COLORS["warning"]
        )
        self.lbl_impostos.grid(row=1, column=1, sticky="e", padx=20, pady=2)
        
        # Separador
        ttk.Separator(grid, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=5
        )
        
        # Total Geral
        tk.Label(
            grid,
            text="TOTAL GERAL:",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["light"],
            fg=COLORS["primary"]
        ).grid(row=3, column=0, sticky="w", pady=2)
        
        self.lbl_total = tk.Label(
            grid,
            text="R$ 0,00",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["light"],
            fg=COLORS["success"]
        )
        self.lbl_total.grid(row=3, column=1, sticky="e", padx=20, pady=2)
        
        grid.grid_columnconfigure(1, weight=1)
    
    def _criar_acoes_inferiores(self):
        """Criar barra de ações inferiores"""
        actions_frame = tk.Frame(self, bg=COLORS["white"], height=60)
        actions_frame.pack(fill="x", padx=10, pady=10)
        actions_frame.pack_propagate(False)
        
        # Botão Salvar
        btn_salvar = tk.Button(
            actions_frame,
            text="💾 Salvar Orçamento",
            command=self._salvar_orcamento,
            bg=COLORS["primary"],
            fg=COLORS["white"],
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=10
        )
        btn_salvar.pack(side="left", padx=5)
        
        # Botão Exportar PDF
        btn_pdf = tk.Button(
            actions_frame,
            text="📄 Exportar PDF",
            command=self._exportar_pdf,
            bg=COLORS["danger"],
            fg=COLORS["white"],
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=10
        )
        btn_pdf.pack(side="left", padx=5)
        
        # Botão Cancelar/Fechar
        btn_fechar = tk.Button(
            actions_frame,
            text="❌ Fechar",
            command=self._fechar,
            bg=COLORS["secondary"],
            fg=COLORS["white"],
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=10
        )
        btn_fechar.pack(side="right", padx=5)
    
    def _buscar_produto_estoque(self):
        """Abre dialog de busca no estoque para selecionar produto."""
        try:
            # Abre dialog seletor
            DialogProdutoSelector(
                parent=self.root if hasattr(self, 'root') else self.master,
                callback=self._adicionar_produto_do_estoque
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao abrir seletor de produtos: {str(e)}"
            )
    
    def _adicionar_produto_do_estoque(self, produto: Dict[str, Any]):
        """Adiciona produto selecionado do estoque ao orçamento.
        
        Args:
            produto: Dict com dados do produto selecionado
        """
        try:
            # Extrai dados do produto
            codigo = produto.get("codigo", "")
            nome = produto.get("nome", "")
            preco_venda = produto.get("preco_venda", 0.0)
            
            # Cria dialog simplificado para qtd e desconto
            dialog = tk.Toplevel(self)
            dialog.title(f"Adicionar: {nome}")
            dialog.geometry("420x280")
            dialog.resizable(False, False)
            dialog.transient(self)
            dialog.grab_set()
            
            # Centraliza
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - 210
            y = (dialog.winfo_screenheight() // 2) - 140
            dialog.geometry(f"420x280+{x}+{y}")
            
            # Frame principal
            main_frame = tk.Frame(dialog, bg=COLORS["white"], padx=20, pady=15)
            main_frame.pack(fill="both", expand=True)
            
            # Título
            tk.Label(
                main_frame,
                text=f"📦 {nome}",
                font=("Segoe UI", 12, "bold"),
                bg=COLORS["white"],
                fg=COLORS["dark"]
            ).pack(pady=(0, 5))
            
            preco_fmt = f"R$ {preco_venda:,.2f}".replace(
                ",", "X"
            ).replace(".", ",").replace("X", ".")
            tk.Label(
                main_frame,
                text=f"Código: {codigo} | Preço: {preco_fmt}",
                font=("Segoe UI", 9),
                bg=COLORS["white"],
                fg=COLORS["muted"]
            ).pack(pady=(0, 15))
            
            # Form
            form_frame = tk.Frame(main_frame, bg=COLORS["white"])
            form_frame.pack(fill="both", expand=True)
            
            fields = {}
            
            # Quantidade
            tk.Label(
                form_frame,
                text="Quantidade:",
                font=("Segoe UI", 10),
                bg=COLORS["white"]
            ).grid(row=0, column=0, sticky="w", pady=8)
            fields["qtd"] = tk.Entry(
                form_frame, font=("Segoe UI", 10), width=15
            )
            fields["qtd"].insert(0, "1")
            fields["qtd"].grid(
                row=0, column=1, sticky="ew", pady=8, padx=(10, 0)
            )
            fields["qtd"].focus_set()
            
            # Unidade
            tk.Label(
                form_frame,
                text="Unidade:",
                font=("Segoe UI", 10),
                bg=COLORS["white"]
            ).grid(row=1, column=0, sticky="w", pady=8)
            fields["unidade"] = ttk.Combobox(
                form_frame,
                values=["UN", "M", "M²", "M³", "KG", "L", "CX", "PC"],
                font=("Segoe UI", 10),
                width=13,
                state="readonly"
            )
            fields["unidade"].set("UN")
            fields["unidade"].grid(
                row=1, column=1, sticky="ew", pady=8, padx=(10, 0)
            )
            
            # Desconto
            tk.Label(
                form_frame,
                text="Desconto (%):",
                font=("Segoe UI", 10),
                bg=COLORS["white"]
            ).grid(row=2, column=0, sticky="w", pady=8)
            fields["desconto"] = tk.Entry(
                form_frame, font=("Segoe UI", 10), width=15
            )
            fields["desconto"].insert(0, "0")
            fields["desconto"].grid(
                row=2, column=1, sticky="ew", pady=8, padx=(10, 0)
            )
            
            form_frame.grid_columnconfigure(1, weight=1)
            
            # Botões
            btn_frame = tk.Frame(main_frame, bg=COLORS["white"])
            btn_frame.pack(pady=(15, 0))
            
            def confirmar():
                try:
                    qtd = float(fields["qtd"].get())
                    unidade = fields["unidade"].get()
                    desconto = float(fields["desconto"].get())
                    
                    if qtd <= 0:
                        messagebox.showwarning(
                            "Atenção",
                            "Quantidade deve ser maior que zero!",
                            parent=dialog
                        )
                        return
                    
                    if desconto < 0 or desconto > 100:
                        messagebox.showwarning(
                            "Atenção",
                            "Desconto deve estar entre 0 e 100%!",
                            parent=dialog
                        )
                        return
                    
                    # Calcular total
                    total = qtd * preco_venda * (1 - desconto / 100)
                    
                    # Adicionar item
                    item = {
                        "codigo": codigo,
                        "produto": nome,
                        "qtd": qtd,
                        "unidade": unidade,
                        "preco_unit": preco_venda,
                        "desconto": desconto,
                        "total": total
                    }
                    
                    self.itens.append(item)
                    self._atualizar_tree()
                    self._calcular_totais()
                    
                    dialog.destroy()
                    
                except ValueError:
                    messagebox.showerror(
                        "Erro",
                        "Valores inválidos!",
                        parent=dialog
                    )
            
            tk.Button(
                btn_frame,
                text="✅ Confirmar",
                command=confirmar,
                bg=COLORS["success"],
                fg="white",
                font=("Segoe UI", 10, "bold"),
                relief="flat",
                cursor="hand2",
                padx=20,
                pady=8
            ).pack(side="left", padx=5)
            
            tk.Button(
                btn_frame,
                text="❌ Cancelar",
                command=dialog.destroy,
                bg=COLORS["danger"],
                fg="white",
                font=("Segoe UI", 10),
                relief="flat",
                cursor="hand2",
                padx=20,
                pady=8
            ).pack(side="left", padx=5)
            
            # Bind Enter
            dialog.bind("<Return>", lambda e: confirmar())
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao adicionar produto: {str(e)}"
            )
    
    def _adicionar_item_dialog(self):
        """Abrir dialog para adicionar item manualmente (entrada manual)"""
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Item")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.configure(bg=COLORS["white"])
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 150
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Título
        tk.Label(
            dialog,
            text="Adicionar Item ao Orçamento",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["white"],
            fg=COLORS["primary"]
        ).pack(pady=20)
        
        # Form
        form_frame = tk.Frame(dialog, bg=COLORS["white"])
        form_frame.pack(fill="both", expand=True, padx=30)
        
        fields = {}
        
        # Código Produto
        tk.Label(
            form_frame,
            text="Código:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).grid(row=0, column=0, sticky="w", pady=5)
        fields["codigo"] = tk.Entry(form_frame, font=("Segoe UI", 10), width=20)
        fields["codigo"].grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Descrição
        tk.Label(
            form_frame,
            text="Descrição:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).grid(row=1, column=0, sticky="w", pady=5)
        fields["descricao"] = tk.Entry(form_frame, font=("Segoe UI", 10), width=40)
        fields["descricao"].grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Quantidade
        tk.Label(
            form_frame,
            text="Quantidade:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).grid(row=2, column=0, sticky="w", pady=5)
        fields["qtd"] = tk.Entry(form_frame, font=("Segoe UI", 10), width=10)
        fields["qtd"].insert(0, "1")
        fields["qtd"].grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Unidade
        tk.Label(
            form_frame,
            text="Unidade:",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).grid(row=3, column=0, sticky="w", pady=5)
        fields["unidade"] = ttk.Combobox(
            form_frame,
            values=["UN", "M", "M²", "M³", "KG", "L", "CX", "PC"],
            font=("Segoe UI", 10),
            width=8,
            state="readonly"
        )
        fields["unidade"].set("UN")
        fields["unidade"].grid(row=3, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Preço Unitário
        tk.Label(
            form_frame,
            text="Preço Unit. (R$):",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).grid(row=4, column=0, sticky="w", pady=5)
        fields["preco"] = tk.Entry(form_frame, font=("Segoe UI", 10), width=15)
        fields["preco"].insert(0, "0.00")
        fields["preco"].grid(row=4, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Desconto
        tk.Label(
            form_frame,
            text="Desconto (%):",
            font=("Segoe UI", 10),
            bg=COLORS["white"]
        ).grid(row=5, column=0, sticky="w", pady=5)
        fields["desconto"] = tk.Entry(form_frame, font=("Segoe UI", 10), width=10)
        fields["desconto"].insert(0, "0")
        fields["desconto"].grid(row=5, column=1, sticky="w", pady=5, padx=(10, 0))
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Botões
        btn_frame = tk.Frame(dialog, bg=COLORS["white"])
        btn_frame.pack(pady=20)
        
        def adicionar():
            try:
                # Validar campos
                codigo = fields["codigo"].get().strip()
                descricao = fields["descricao"].get().strip()
                qtd = float(fields["qtd"].get())
                unidade = fields["unidade"].get()
                preco = float(fields["preco"].get())
                desconto = float(fields["desconto"].get())
                
                if not descricao:
                    messagebox.showwarning(
                        "Atenção",
                        "Descrição é obrigatória!",
                        parent=dialog
                    )
                    return
                
                if qtd <= 0:
                    messagebox.showwarning(
                        "Atenção",
                        "Quantidade deve ser maior que zero!",
                        parent=dialog
                    )
                    return
                
                if preco < 0:
                    messagebox.showwarning(
                        "Atenção",
                        "Preço não pode ser negativo!",
                        parent=dialog
                    )
                    return
                
                if desconto < 0 or desconto > 100:
                    messagebox.showwarning(
                        "Atenção",
                        "Desconto deve estar entre 0 e 100%!",
                        parent=dialog
                    )
                    return
                
                # Calcular total
                total = qtd * preco * (1 - desconto / 100)
                
                # Adicionar ao grid
                item = {
                    "codigo": codigo or "-",
                    "produto": descricao,
                    "qtd": qtd,
                    "unidade": unidade,
                    "preco_unit": preco,
                    "desconto": desconto,
                    "total": total
                }
                
                self.itens.append(item)
                self._atualizar_tree()
                self._calcular_totais()
                
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror(
                    "Erro",
                    "Valores inválidos! Verifique Qtd, Preço e Desconto.",
                    parent=dialog
                )
        
        tk.Button(
            btn_frame,
            text="✅ Adicionar",
            command=adicionar,
            bg=COLORS["success"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8
        ).pack(side="left", padx=5)
        
        tk.Button(
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
        ).pack(side="left", padx=5)
    
    def _remover_item(self):
        """Remover item selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "Atenção",
                "Selecione um item para remover!"
            )
            return
        
        # Confirmar
        result = messagebox.askyesno(
            "Confirmar Remoção",
            "Deseja realmente remover este item?"
        )
        
        if result:
            # Obter índice
            item_id = selection[0]
            index = self.tree.index(item_id)
            
            # Remover da lista
            del self.itens[index]
            
            # Atualizar tree
            self._atualizar_tree()
            self._calcular_totais()
    
    def _limpar_grid(self):
        """Limpar todos os itens do grid"""
        if not self.itens:
            messagebox.showinfo("Info", "Grid já está vazio!")
            return
        
        result = messagebox.askyesno(
            "Confirmar Limpeza",
            f"Deseja realmente remover todos os {len(self.itens)} itens?"
        )
        
        if result:
            self.itens.clear()
            self._atualizar_tree()
            self._calcular_totais()
    
    def _importar_produtos_dialog(self):
        """Importar produtos em lote"""
        messagebox.showinfo(
            "Em Desenvolvimento",
            "Funcionalidade de importação em lote em desenvolvimento.\n\n"
            "Por enquanto, use 'Adicionar Item' individualmente."
        )
    
    def _on_double_click(self, event):
        """Handler para duplo-clique (editar célula)"""
        # Identificar item e coluna
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if not item_id or not column:
            return
        
        # Colunas editáveis: qtd (#2), preco_unit (#4), desconto (#5)
        colunas_editaveis = ["#2", "#4", "#5"]
        
        if column not in colunas_editaveis:
            return
        
        # Obter índice do item
        index = self.tree.index(item_id)
        item_data = self.itens[index]
        
        # Mapear coluna para campo
        campo_map = {
            "#2": "qtd",
            "#4": "preco_unit",
            "#5": "desconto"
        }
        campo = campo_map[column]
        
        # Abrir dialog de edição
        self._editar_campo(index, campo, item_data[campo])
    
    def _editar_campo(self, index: int, campo: str, valor_atual):
        """Editar campo específico de um item"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Editar {campo.replace('_', ' ').title()}")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.configure(bg=COLORS["white"])
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 150
        y = (dialog.winfo_screenheight() // 2) - 75
        dialog.geometry(f"300x150+{x}+{y}")
        
        tk.Label(
            dialog,
            text=f"Editar {campo.replace('_', ' ').title()}:",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["white"]
        ).pack(pady=15)
        
        entry = tk.Entry(dialog, font=("Segoe UI", 12), width=20)
        entry.insert(0, str(valor_atual))
        entry.pack(pady=10)
        entry.focus_set()
        entry.select_range(0, tk.END)
        
        def salvar():
            try:
                novo_valor = float(entry.get())
                
                # Validações
                if campo == "qtd" and novo_valor <= 0:
                    messagebox.showerror(
                        "Erro",
                        "Quantidade deve ser maior que zero!",
                        parent=dialog
                    )
                    return
                
                if campo == "preco_unit" and novo_valor < 0:
                    messagebox.showerror(
                        "Erro",
                        "Preço não pode ser negativo!",
                        parent=dialog
                    )
                    return
                
                if campo == "desconto" and (novo_valor < 0 or novo_valor > 100):
                    messagebox.showerror(
                        "Erro",
                        "Desconto deve estar entre 0 e 100%!",
                        parent=dialog
                    )
                    return
                
                # Atualizar item
                self.itens[index][campo] = novo_valor
                
                # Recalcular total do item
                item = self.itens[index]
                item["total"] = item["qtd"] * item["preco_unit"] * (
                    1 - item["desconto"] / 100
                )
                
                # Atualizar visualização
                self._atualizar_tree()
                self._calcular_totais()
                
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror(
                    "Erro",
                    "Valor inválido! Digite um número.",
                    parent=dialog
                )
        
        btn_frame = tk.Frame(dialog, bg=COLORS["white"])
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="✅ Salvar",
            command=salvar,
            bg=COLORS["success"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=dialog.destroy,
            bg=COLORS["danger"],
            fg=COLORS["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=5
        ).pack(side="left", padx=5)
        
        # Enter para salvar
        entry.bind("<Return>", lambda e: salvar())
    
    def _atualizar_tree(self):
        """Atualizar TreeView com itens atuais"""
        # Limpar tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar itens
        for idx, item in enumerate(self.itens):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                "end",
                values=(
                    item["codigo"],
                    item["produto"],
                    f"{item['qtd']:.2f}",
                    item["unidade"],
                    f"{item['preco_unit']:.2f}",
                    f"{item['desconto']:.1f}",
                    f"{item['total']:.2f}"
                ),
                tags=(tag,)
            )
    
    def _calcular_totais(self):
        """Calcular e atualizar totais"""
        # Subtotal
        subtotal = sum(item["total"] for item in self.itens)
        
        # Impostos (17%)
        impostos = subtotal * 0.17
        
        # Total geral
        total = subtotal + impostos
        
        # Atualizar labels
        self.lbl_subtotal.config(text=f"R$ {subtotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.lbl_impostos.config(text=f"R$ {impostos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.lbl_total.config(text=f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    def _carregar_orcamento(self):
        """Carregar orçamento do backend"""
        def _load():
            try:
                headers = create_auth_header()
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/os/{self.os_id}/orcamento-json",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.itens = data.get("itens", [])
                    self.after(0, self._atualizar_tree)
                    self.after(0, self._calcular_totais)
                elif response.status_code == 404:
                    # Orçamento não existe ainda, OK
                    pass
                else:
                    self.after(
                        0,
                        lambda: messagebox.showwarning(
                            "Aviso",
                            f"Erro ao carregar orçamento: {response.status_code}"
                        )
                    )
            except Exception as e:
                print(f"Erro ao carregar orçamento: {e}")
        
        threading.Thread(target=_load, daemon=True).start()
    
    def _salvar_orcamento(self):
        """Salvar orçamento no backend"""
        if not self.itens:
            messagebox.showwarning(
                "Atenção",
                "Adicione pelo menos um item ao orçamento!"
            )
            return
        
        def _save():
            try:
                headers = create_auth_header()
                
                # Calcular totais
                subtotal = sum(item["total"] for item in self.itens)
                impostos = subtotal * 0.17
                total = subtotal + impostos
                
                payload = {
                    "os_id": self.os_id,
                    "itens": self.itens,
                    "subtotal": subtotal,
                    "impostos": impostos,
                    "total_geral": total,
                    "timestamp": datetime.now().isoformat()
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/os/{self.os_id}/orcamento-json",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Sucesso",
                            "Orçamento salvo com sucesso!"
                        )
                    )
                else:
                    error_msg = response.json().get("detail", "Erro desconhecido")
                    self.after(
                        0,
                        lambda: messagebox.showerror(
                            "Erro",
                            f"Erro ao salvar orçamento:\n{error_msg}"
                        )
                    )
            except Exception as e:
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao salvar orçamento:\n{str(e)}"
                    )
                )
        
        threading.Thread(target=_save, daemon=True).start()
    
    def _exportar_pdf(self):
        """Exportar orçamento para PDF"""
        if not self.itens:
            messagebox.showwarning(
                "Atenção",
                "Adicione pelo menos um item para exportar!"
            )
            return
        
        try:
            # Dialog para escolher local de salvamento
            os_numero = f"OS-{self.os_id}" if self.os_id else "NOVO"
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"Orcamento_{os_numero}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                title="Salvar Orçamento como PDF"
            )
            
            if not filename:
                return  # Usuário cancelou
            
            # Buscar dados da OS
            os_data = self._buscar_dados_os()
            
            # Preparar dados do orçamento
            subtotal = sum(item["total"] for item in self.itens)
            impostos = subtotal * 0.17
            total_geral = subtotal + impostos
            
            orcamento_data = {
                "itens": self.itens,
                "subtotal": subtotal,
                "impostos": impostos,
                "total_geral": total_geral,
                "timestamp": datetime.now().isoformat()
            }
            
            # Gerar PDF
            generator = PDFOrcamentoGenerator()
            sucesso = generator.gerar_pdf(
                output_path=filename,
                os_data=os_data,
                orcamento_data=orcamento_data
            )
            
            if sucesso:
                messagebox.showinfo(
                    "Sucesso",
                    f"PDF gerado com sucesso!\n\nArquivo: {filename}"
                )
                
                # Perguntar se deseja abrir
                abrir = messagebox.askyesno(
                    "Abrir PDF",
                    "Deseja abrir o PDF agora?"
                )
                
                if abrir:
                    import os
                    os.startfile(filename)  # Abre com visualizador padrão
            else:
                messagebox.showerror(
                    "Erro",
                    "Erro ao gerar PDF. Verifique os logs."
                )
                
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao exportar PDF: {str(e)}"
            )
    
    def _buscar_dados_os(self) -> Dict[str, Any]:
        """Busca dados da OS via API para usar no PDF."""
        try:
            if not self.os_id:
                # Sem OS, retorna dados genéricos
                return {
                    "numero": "RASCUNHO",
                    "cliente": "Cliente não especificado",
                    "data": datetime.now().isoformat()
                }
            
            headers = create_auth_header()
            response = requests.get(
                f"{API_BASE_URL}/api/v1/os/{self.os_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                os_obj = response.json()
                return {
                    "numero": os_obj.get("numero_os", f"OS-{self.os_id}"),
                    "cliente": os_obj.get("cliente_nome", "Cliente não especificado"),
                    "data": os_obj.get("data_abertura", datetime.now().isoformat())
                }
            else:
                # Erro ao buscar, retorna dados genéricos
                return {
                    "numero": f"OS-{self.os_id}",
                    "cliente": "Erro ao carregar cliente",
                    "data": datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Erro ao buscar dados da OS: {e}")
            return {
                "numero": f"OS-{self.os_id}" if self.os_id else "RASCUNHO",
                "cliente": "Erro ao carregar dados",
                "data": datetime.now().isoformat()
            }
    
    def _fechar(self):
        """Fechar janela"""
        if self.itens:
            result = messagebox.askyesnocancel(
                "Fechar",
                "Deseja salvar o orçamento antes de fechar?"
            )
            
            if result is None:  # Cancelar
                return
            elif result:  # Sim, salvar
                self._salvar_orcamento()
        
        # Fechar janela
        if isinstance(self.parent, tk.Toplevel):
            self.parent.destroy()
        else:
            self.destroy()


# Teste standalone
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Grid Orçamento - Teste")
    root.geometry("1000x700")
    
    # Criar grid (sem os_id para teste)
    grid = GridOrcamento(root, os_id=1)
    grid.pack(fill="both", expand=True)
    
    root.mainloop()
