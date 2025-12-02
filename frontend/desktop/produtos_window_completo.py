"""
MÓDULO DE PRODUTOS - INTERFACE DESKTOP COMPLETA
==============================================

Interface tkinter moderna para gerenciamento completo de produtos.
Integrado com backend FastAPI via SessionManager.

Funcionalidades:
- CRUD completo de produtos
- Busca e filtros
- Validações em tempo real
- Códigos de barras
- Integração com estoque

Autor: GitHub Copilot
Data: 16/11/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict
import threading

# Importações do sistema
from frontend.desktop.auth_middleware import (
    require_login,
    get_token_for_api,
    create_auth_header,
    get_current_user_info
)


@require_login()
class ProdutosWindowCompleto:
    """Janela completa de gerenciamento de produtos"""

    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("📦 Gerenciamento de Produtos - ERP Primotex")
        self.window.geometry("1400x800")

        # API
        self.api_url = "http://127.0.0.1:8002/api/v1"
        self.headers = create_auth_header()

        # Dados
        self.produtos = []
        self.produto_selecionado = None

        # UI
        self.setup_ui()
        self.carregar_produtos()

        # Centralizar janela
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (800 // 2)
        self.window.geometry(f"1400x800+{x}+{y}")

    def setup_ui(self):
        """Configura a interface"""

        # ==========================================
        # HEADER
        # ==========================================
        header_frame = tk.Frame(self.window, bg="#2C3E50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Título
        title_label = tk.Label(
            header_frame,
            text="📦 GERENCIAMENTO DE PRODUTOS",
            font=("Segoe UI", 20, "bold"),
            bg="#2C3E50",
            fg="white"
        )
        title_label.pack(pady=20)

        # ==========================================
        # TOOLBAR
        # ==========================================
        toolbar_frame = tk.Frame(self.window, bg="#ECF0F1", height=60)
        toolbar_frame.pack(fill=tk.X, pady=5, padx=10)
        toolbar_frame.pack_propagate(False)

        # Botões de ação
        btn_novo = tk.Button(
            toolbar_frame,
            text="➕ Novo Produto",
            command=self.novo_produto,
            bg="#27AE60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=15,
            cursor="hand2"
        )
        btn_novo.pack(side=tk.LEFT, padx=5)

        btn_editar = tk.Button(
            toolbar_frame,
            text="✏️ Editar",
            command=self.editar_produto,
            bg="#3498DB",
            fg="white",
            font=("Segoe UI", 10),
            width=12,
            cursor="hand2"
        )
        btn_editar.pack(side=tk.LEFT, padx=5)

        btn_deletar = tk.Button(
            toolbar_frame,
            text="🗑️ Inativar",
            command=self.deletar_produto,
            bg="#E74C3C",
            fg="white",
            font=("Segoe UI", 10),
            width=12,
            cursor="hand2"
        )
        btn_deletar.pack(side=tk.LEFT, padx=5)

        btn_atualizar = tk.Button(
            toolbar_frame,
            text="🔄 Atualizar",
            command=self.carregar_produtos,
            bg="#95A5A6",
            fg="white",
            font=("Segoe UI", 10),
            width=12,
            cursor="hand2"
        )
        btn_atualizar.pack(side=tk.LEFT, padx=5)

        # Busca
        tk.Label(
            toolbar_frame,
            text="🔍",
            font=("Segoe UI", 14),
            bg="#ECF0F1"
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.busca_var = tk.StringVar()
        self.busca_var.trace("w", lambda *args: self.filtrar_produtos())

        busca_entry = tk.Entry(
            toolbar_frame,
            textvariable=self.busca_var,
            font=("Segoe UI", 10),
            width=30
        )
        busca_entry.pack(side=tk.LEFT, padx=5)

        # Filtro categoria
        tk.Label(
            toolbar_frame,
            text="Categoria:",
            font=("Segoe UI", 10),
            bg="#ECF0F1"
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.categoria_var = tk.StringVar(value="Todas")
        categorias = ["Todas", "Forros", "Drywall", "PVC", "Vidro", "Eucatex", "Placas Cimentícias"]

        categoria_combo = ttk.Combobox(
            toolbar_frame,
            textvariable=self.categoria_var,
            values=categorias,
            state="readonly",
            font=("Segoe UI", 10),
            width=20
        )
        categoria_combo.pack(side=tk.LEFT, padx=5)
        categoria_combo.bind("<<ComboboxSelected>>", lambda e: self.filtrar_produtos())

        # ==========================================
        # CONTEÚDO PRINCIPAL
        # ==========================================
        content_frame = tk.Frame(self.window, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ==========================================
        # TABELA DE PRODUTOS
        # ==========================================
        table_frame = tk.Frame(content_frame, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        colunas = ("ID", "Código", "Descrição", "Categoria", "Preço Venda", "Estoque", "Status")

        self.tree = ttk.Treeview(
            table_frame,
            columns=colunas,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            selectmode="browse"
        )

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # Configurar colunas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Código", text="Código")
        self.tree.heading("Descrição", text="Descrição")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.heading("Preço Venda", text="Preço Venda")
        self.tree.heading("Estoque", text="Estoque Atual")
        self.tree.heading("Status", text="Status")

        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Código", width=120, anchor=tk.CENTER)
        self.tree.column("Descrição", width=400, anchor=tk.W)
        self.tree.column("Categoria", width=150, anchor=tk.CENTER)
        self.tree.column("Preço Venda", width=120, anchor=tk.E)
        self.tree.column("Estoque", width=120, anchor=tk.CENTER)
        self.tree.column("Status", width=100, anchor=tk.CENTER)

        # Estilos alternados
        self.tree.tag_configure("oddrow", background="#F8F9FA")
        self.tree.tag_configure("evenrow", background="white")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind duplo clique
        self.tree.bind("<Double-1>", lambda e: self.editar_produto())

        # ==========================================
        # RODAPÉ
        # ==========================================
        footer_frame = tk.Frame(self.window, bg="#ECF0F1", height=40)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)

        self.status_label = tk.Label(
            footer_frame,
            text="📊 Carregando produtos...",
            font=("Segoe UI", 9),
            bg="#ECF0F1",
            fg="#34495E"
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=10)

    def carregar_produtos(self):
        """Carrega produtos da API"""

        def _carregar():
            try:
                self.atualizar_status("🔄 Carregando produtos...")

                response = requests.get(
                    f"{self.api_url}/produtos",
                    headers=self.headers,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()

                    # Verifica formato (lista ou objeto paginado)
                    if isinstance(data, list):
                        self.produtos = data
                    else:
                        self.produtos = data.get("itens", [])

                    # Atualizar UI no thread principal
                    self.window.after(0, self.popular_tabela)
                    self.window.after(0, lambda: self.atualizar_status(
                        f"✅ {len(self.produtos)} produtos carregados"
                    ))
                else:
                    self.window.after(0, lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao carregar produtos: {response.status_code}"
                    ))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro ao conectar com API: {str(e)}"
                ))

        # Executar em thread separada
        threading.Thread(target=_carregar, daemon=True).start()

    def popular_tabela(self):
        """Popula a tabela com produtos"""

        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Popular
        for idx, produto in enumerate(self.produtos):
            valores = (
                produto.get("id", ""),
                produto.get("codigo", "N/A"),
                produto.get("descricao", "Sem descrição"),
                produto.get("categoria", "N/A"),
                f"R$ {float(produto.get('preco_venda', 0)):.2f}",
                produto.get("estoque_atual", 0),
                produto.get("status", "N/A")
            )

            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=valores, tags=(tag,))

    def filtrar_produtos(self):
        """Filtra produtos por busca e categoria"""

        busca = self.busca_var.get().lower()
        categoria = self.categoria_var.get()

        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filtrar e popular
        produtos_filtrados = []

        for produto in self.produtos:
            # Filtro de categoria
            if categoria != "Todas" and produto.get("categoria") != categoria:
                continue

            # Filtro de busca
            if busca:
                descricao = produto.get("descricao", "").lower()
                codigo = produto.get("codigo", "").lower()

                if busca not in descricao and busca not in codigo:
                    continue

            produtos_filtrados.append(produto)

        # Popular tabela filtrada
        for idx, produto in enumerate(produtos_filtrados):
            valores = (
                produto.get("id", ""),
                produto.get("codigo", "N/A"),
                produto.get("descricao", "Sem descrição"),
                produto.get("categoria", "N/A"),
                f"R$ {float(produto.get('preco_venda', 0)):.2f}",
                produto.get("estoque_atual", 0),
                produto.get("status", "N/A")
            )

            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=valores, tags=(tag,))

        self.atualizar_status(f"📊 {len(produtos_filtrados)} produtos encontrados")

    def novo_produto(self):
        """Abre formulário para novo produto"""
        FormularioProduto(self.window, self, modo="criar")

    def editar_produto(self):
        """Abre formulário para editar produto"""

        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para editar")
            return

        # Pegar ID do produto
        valores = self.tree.item(selecionado[0])["values"]
        produto_id = valores[0]

        # Buscar produto completo
        produto = next((p for p in self.produtos if p["id"] == produto_id), None)

        if produto:
            FormularioProduto(self.window, self, modo="editar", produto=produto)
        else:
            messagebox.showerror("Erro", "Produto não encontrado")

    def deletar_produto(self):
        """Inativa produto (soft delete)"""

        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para inativar")
            return

        valores = self.tree.item(selecionado[0])["values"]
        produto_id = valores[0]
        descricao = valores[2]

        # Confirmar
        if not messagebox.askyesno(
            "Confirmar",
            f"Deseja inativar o produto:\n\n{descricao}?"
        ):
            return

        def _deletar():
            try:
                response = requests.delete(
                    f"{self.api_url}/produtos/{produto_id}",
                    headers=self.headers,
                    timeout=10
                )

                if response.status_code in (200, 204):
                    self.window.after(0, lambda: messagebox.showinfo(
                        "Sucesso",
                        "Produto inativado com sucesso!"
                    ))
                    self.window.after(0, self.carregar_produtos)
                else:
                    self.window.after(0, lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao inativar produto: {response.status_code}"
                    ))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro ao conectar com API: {str(e)}"
                ))

        threading.Thread(target=_deletar, daemon=True).start()

    def atualizar_status(self, mensagem: str):
        """Atualiza mensagem de status"""
        self.status_label.config(text=mensagem)


class FormularioProduto:
    """Formulário para criar/editar produto"""

    def __init__(self, parent, produtos_window, modo="criar", produto=None):
        self.parent = parent
        self.produtos_window = produtos_window
        self.modo = modo
        self.produto = produto

        # API
        self.api_url = produtos_window.api_url
        self.headers = produtos_window.headers

        # Janela
        self.window = tk.Toplevel(parent)
        self.window.title(f"{'➕ Novo Produto' if modo == 'criar' else '✏️ Editar Produto'}")
        self.window.geometry("800x700")
        self.window.transient(parent)
        self.window.grab_set()

        self.setup_ui()

        if modo == "editar" and produto:
            self.preencher_formulario(produto)

        # Centralizar
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"800x700+{x}+{y}")

    def setup_ui(self):
        """Configura interface do formulário"""

        # Header
        header = tk.Frame(self.window, bg="#2C3E50", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"{'➕ NOVO PRODUTO' if self.modo == 'criar' else '✏️ EDITAR PRODUTO'}",
            font=("Segoe UI", 16, "bold"),
            bg="#2C3E50",
            fg="white"
        ).pack(pady=15)

        # Conteúdo
        content = tk.Frame(self.window, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Canvas + Scrollbar
        canvas = tk.Canvas(content, bg="white")
        scrollbar = ttk.Scrollbar(content, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Campos do formulário
        self.campos = {}

        campos_config = [
            ("Código *", "codigo", "entry"),
            ("Descrição *", "descricao", "text"),
            ("Código de Barras", "codigo_barras", "entry"),
            ("Categoria *", "categoria", "combo", ["Forros", "Drywall", "PVC", "Vidro", "Eucatex", "Placas Cimentícias"]),
            ("Unidade Medida *", "unidade_medida", "combo", ["un", "m", "m²", "m³", "kg", "l", "cx", "pc"]),
            ("Preço Custo (R$)", "preco_custo", "entry"),
            ("Preço Venda (R$) *", "preco_venda", "entry"),
            ("Margem Lucro (%)", "margem_lucro", "entry"),
            ("Estoque Atual", "estoque_atual", "entry"),
            ("Estoque Mínimo", "estoque_minimo", "entry"),
            ("Estoque Máximo", "estoque_maximo", "entry"),
            ("Localização Estoque", "localizacao_estoque", "entry"),
            ("Observações", "observacoes", "text"),
        ]

        for config in campos_config:
            label_text = config[0]
            campo_key = config[1]
            campo_tipo = config[2]

            # Label
            tk.Label(
                scrollable_frame,
                text=label_text,
                font=("Segoe UI", 10, "bold"),
                bg="white",
                anchor="w"
            ).pack(fill=tk.X, pady=(10, 2))

            # Campo
            if campo_tipo == "entry":
                campo = tk.Entry(
                    scrollable_frame,
                    font=("Segoe UI", 10),
                    width=60
                )
                campo.pack(fill=tk.X, ipady=5)

            elif campo_tipo == "text":
                campo = tk.Text(
                    scrollable_frame,
                    font=("Segoe UI", 10),
                    height=3,
                    width=60
                )
                campo.pack(fill=tk.X)

            elif campo_tipo == "combo":
                valores = config[3] if len(config) > 3 else []
                campo = ttk.Combobox(
                    scrollable_frame,
                    values=valores,
                    font=("Segoe UI", 10),
                    width=58,
                    state="readonly"
                )
                campo.pack(fill=tk.X, ipady=3)

            self.campos[campo_key] = campo

        # Botões
        btn_frame = tk.Frame(self.window, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            btn_frame,
            text="💾 Salvar",
            command=self.salvar,
            bg="#27AE60",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=self.window.destroy,
            bg="#95A5A6",
            fg="white",
            font=("Segoe UI", 11),
            width=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

    def preencher_formulario(self, produto: dict):
        """Preenche formulário com dados do produto"""

        for key, campo in self.campos.items():
            valor = produto.get(key, "")

            if isinstance(campo, tk.Text):
                campo.delete("1.0", tk.END)
                campo.insert("1.0", str(valor) if valor else "")
            elif isinstance(campo, ttk.Combobox):
                campo.set(str(valor) if valor else "")
            else:
                campo.delete(0, tk.END)
                campo.insert(0, str(valor) if valor else "")

    def salvar(self):
        """Salva produto (criar ou atualizar)"""

        # Coletar dados
        dados = {}

        for key, campo in self.campos.items():
            if isinstance(campo, tk.Text):
                valor = campo.get("1.0", tk.END).strip()
            else:
                valor = campo.get().strip()

            # Converter tipos
            if key in ["preco_custo", "preco_venda", "margem_lucro"]:
                try:
                    dados[key] = float(valor) if valor else 0.0
                except ValueError:
                    dados[key] = 0.0

            elif key in ["estoque_atual", "estoque_minimo", "estoque_maximo"]:
                try:
                    dados[key] = int(valor) if valor else 0
                except ValueError:
                    dados[key] = 0
            else:
                dados[key] = valor if valor else None

        # Adicionar status
        if "status" not in dados:
            dados["status"] = "Ativo"

        # Validar campos obrigatórios
        if not dados.get("descricao"):
            messagebox.showerror("Erro", "Descrição é obrigatória")
            return

        if not dados.get("categoria"):
            messagebox.showerror("Erro", "Categoria é obrigatória")
            return

        if not dados.get("unidade_medida"):
            messagebox.showerror("Erro", "Unidade de medida é obrigatória")
            return

        # Salvar
        def _salvar():
            try:
                if self.modo == "criar":
                    response = requests.post(
                        f"{self.api_url}/produtos",
                        json=dados,
                        headers=self.headers,
                        timeout=10
                    )
                else:
                    produto_id = self.produto["id"]
                    response = requests.put(
                        f"{self.api_url}/produtos/{produto_id}",
                        json=dados,
                        headers=self.headers,
                        timeout=10
                    )

                if response.status_code in (200, 201):
                    self.window.after(0, lambda: messagebox.showinfo(
                        "Sucesso",
                        f"Produto {'criado' if self.modo == 'criar' else 'atualizado'} com sucesso!"
                    ))
                    self.window.after(0, self.produtos_window.carregar_produtos)
                    self.window.after(0, self.window.destroy)
                else:
                    erro = response.json().get("detail", "Erro desconhecido")
                    self.window.after(0, lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao salvar produto:\n{erro}"
                    ))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro ao conectar com API:\n{str(e)}"
                ))

        threading.Thread(target=_salvar, daemon=True).start()


# ==========================================
# EXECUÇÃO STANDALONE (para testes)
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Esconder janela principal

    app = ProdutosWindowCompleto(root)
    root.mainloop()
