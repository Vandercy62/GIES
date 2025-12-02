"""
SISTEMA ERP PRIMOTEX - INTERFACE DE PRODUTOS
============================================

Interface completa para gerenciamento de produtos e serviços.
Inclui CRUD, categorização, preços e preparação para códigos de barras.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import requests
from typing import Dict, Any, Optional, List
import re
from decimal import Decimal, InvalidOperation

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

# =======================================
# CLASSE INTERFACE DE PRODUTOS
# =======================================

@require_login()
class ProdutosWindow:
    """Interface de gerenciamento de produtos e serviços"""

    def __init__(self, parent_window=None):
        # NÃO recebe mais user_data - usa SessionManager
        self.token = get_token_for_api()
        self.user_data = get_current_user_info()
        self.parent_window = parent_window

        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.produtos_data = []
        self.produto_selecionado = None

        self.setup_window()
        self.create_widgets()
        self.carregar_produtos()

    def setup_window(self):
        """Configurar janela"""

        self.root.title("Sistema ERP Primotex - Gerenciamento de Produtos")
        self.root.geometry("1500x950")

        if not self.parent_window:
            self.root.state('zoomed')  # Maximizar se for janela principal

        self.root.configure(bg='#f8f9fa')

        # Configurar protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Criar widgets da interface"""

        # === BARRA SUPERIOR ===
        self.create_top_bar()

        # === CONTAINER PRINCIPAL ===
        main_container = tk.Frame(self.root, bg='#f8f9fa')
        main_container.pack(fill='both', expand=True, padx=15, pady=10)

        # === BARRA DE FERRAMENTAS ===
        self.create_toolbar(main_container)

        # === ÁREA PRINCIPAL ===
        content_frame = tk.Frame(main_container, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True, pady=10)

        # === ÁREA DE LISTAGEM (ESQUERDA) ===
        self.create_list_area(content_frame)

        # === ÁREA DE FORMULÁRIO (DIREITA) ===
        self.create_form_area(content_frame)

    def create_top_bar(self):
        """Criar barra superior"""

        top_frame = tk.Frame(self.root, bg='#8e44ad', height=50)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)

        # Container interno
        container = tk.Frame(top_frame, bg='#8e44ad')
        container.pack(fill='both', expand=True, padx=20, pady=8)

        # Título
        title_label = tk.Label(
            container,
            text="📦 Gerenciamento de Produtos",
            font=('Arial', 16, 'bold'),
            bg='#8e44ad',
            fg='white'
        )
        title_label.pack(side='left', pady=5)

        # Informações do usuário (direita)
        user_info = f"🛍️ Usuário: {self.user_data.get('user', {}).get('username', 'N/A')}"
        user_label = tk.Label(
            container,
            text=user_info,
            font=('Arial', 10),
            bg='#8e44ad',
            fg='#ecf0f1'
        )
        user_label.pack(side='right', pady=5)

    def create_toolbar(self, parent):
        """Criar barra de ferramentas"""

        toolbar = tk.Frame(parent, bg='#ecf0f1', relief='raised', bd=1)
        toolbar.pack(fill='x', pady=(0, 10))

        # Container interno
        toolbar_content = tk.Frame(toolbar, bg='#ecf0f1')
        toolbar_content.pack(fill='x', padx=10, pady=8)

        # Botões da esquerda
        left_frame = tk.Frame(toolbar_content, bg='#ecf0f1')
        left_frame.pack(side='left')

        # Botão Novo
        self.btn_novo = tk.Button(
            left_frame,
            text="➕ Novo Produto",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.novo_produto
        )
        self.btn_novo.pack(side='left', padx=(0, 10))

        # Botão Editar
        self.btn_editar = tk.Button(
            left_frame,
            text="✏️ Editar",
            font=('Arial', 10),
            bg='#f39c12',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            state='disabled',
            command=self.editar_produto
        )
        self.btn_editar.pack(side='left', padx=(0, 10))

        # Botão Excluir
        self.btn_excluir = tk.Button(
            left_frame,
            text="🗑️ Excluir",
            font=('Arial', 10),
            bg='#e74c3c',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            state='disabled',
            command=self.excluir_produto
        )
        self.btn_excluir.pack(side='left', padx=(0, 10))

        # Separador
        separator = tk.Frame(left_frame, bg='#bdc3c7', width=2, height=30)
        separator.pack(side='left', padx=15)

        # Botão Atualizar
        self.btn_atualizar = tk.Button(
            left_frame,
            text="🔄 Atualizar",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.carregar_produtos
        )
        self.btn_atualizar.pack(side='left', padx=(0, 10))

        # Botão Código de Barras
        self.btn_barcode = tk.Button(
            left_frame,
            text="📊 Código Barras",
            font=('Arial', 10),
            bg='#9b59b6',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            state='disabled',
            command=self.gerar_codigo_barras
        )
        self.btn_barcode.pack(side='left')

        # Campo de busca (direita)
        right_frame = tk.Frame(toolbar_content, bg='#ecf0f1')
        right_frame.pack(side='right')

        # Filtro por categoria
        tk.Label(
            right_frame,
            text="🏷️ Categoria:",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(side='left', padx=(0, 5))

        self.combo_categoria_filtro = ttk.Combobox(
            right_frame,
            font=('Arial', 9),
            width=15,
            state="readonly"
        )
        self.combo_categoria_filtro.pack(side='left', padx=(0, 15))
        self.combo_categoria_filtro.bind('<<ComboboxSelected>>', self.filtrar_produtos)

        tk.Label(
            right_frame,
            text="🔍 Buscar:",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(side='left', padx=(0, 5))

        self.entry_busca = tk.Entry(
            right_frame,
            font=('Arial', 10),
            width=25,
            bg='white',
            relief='flat',
            bd=5
        )
        self.entry_busca.pack(side='left', padx=(0, 10))
        self.entry_busca.bind('<KeyRelease>', self.filtrar_produtos)

        btn_buscar = tk.Button(
            right_frame,
            text="Buscar",
            font=('Arial', 9),
            bg='#95a5a6',
            fg='white',
            padx=10,
            pady=3,
            border=0,
            command=self.filtrar_produtos
        )
        btn_buscar.pack(side='left')

    def create_list_area(self, parent):
        """Criar área de listagem de produtos"""

        # Frame da listagem
        list_frame = tk.LabelFrame(
            parent,
            text="📋 Lista de Produtos",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            relief='raised',
            bd=1
        )
        list_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Configurar Treeview
        columns = ('id', 'codigo', 'nome', 'categoria', 'tipo', 'preco_venda', 'estoque', 'status')

        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=22
        )

        # Configurar cabeçalhos
        self.tree.heading('id', text='ID')
        self.tree.heading('codigo', text='Código')
        self.tree.heading('nome', text='Nome')
        self.tree.heading('categoria', text='Categoria')
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('preco_venda', text='Preço Venda')
        self.tree.heading('estoque', text='Estoque')
        self.tree.heading('status', text='Status')

        # Configurar larguras das colunas
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('codigo', width=100, anchor='center')
        self.tree.column('nome', width=250, anchor='w')
        self.tree.column('categoria', width=120, anchor='center')
        self.tree.column('tipo', width=80, anchor='center')
        self.tree.column('preco_venda', width=100, anchor='e')
        self.tree.column('estoque', width=80, anchor='center')
        self.tree.column('status', width=80, anchor='center')

        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Pack scrollbars e treeview
        self.tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        v_scroll.pack(side='right', fill='y', pady=10)
        h_scroll.pack(side='bottom', fill='x', padx=(10, 0))

        # Bind eventos
        self.tree.bind('<<TreeviewSelect>>', self.on_produto_selecionado)
        self.tree.bind('<Double-1>', self.editar_produto)

        # Contador de registros
        self.label_contador = tk.Label(
            list_frame,
            text="Total: 0 produtos",
            font=('Arial', 9),
            bg='white',
            fg='#7f8c8d'
        )
        self.label_contador.pack(side='bottom', pady=(0, 10))

    def create_form_area(self, parent):
        """Criar área do formulário"""

        # Frame do formulário
        form_frame = tk.LabelFrame(
            parent,
            text="📝 Dados do Produto",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            relief='raised',
            bd=1,
            width=450
        )
        form_frame.pack(side='right', fill='y')
        form_frame.pack_propagate(False)

        # Scroll area para o formulário
        canvas = tk.Canvas(form_frame, bg='white')
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        self.form_content = tk.Frame(canvas, bg='white')

        self.form_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.form_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Campos do formulário
        self.create_form_fields()

        # Botões do formulário
        self.create_form_buttons()

    def create_form_fields(self):
        """Criar campos do formulário"""

        # ID (oculto para edição)
        self.var_id = tk.StringVar()

        # Código do produto
        tk.Label(
            self.form_content,
            text="Código *",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(10, 2))

        self.var_codigo = tk.StringVar()
        self.entry_codigo = tk.Entry(
            self.form_content,
            textvariable=self.var_codigo,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=5
        )
        self.entry_codigo.pack(fill='x', padx=10, pady=(0, 10))

        # Nome do produto
        tk.Label(
            self.form_content,
            text="Nome *",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(0, 2))

        self.var_nome = tk.StringVar()
        self.entry_nome = tk.Entry(
            self.form_content,
            textvariable=self.var_nome,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=5
        )
        self.entry_nome.pack(fill='x', padx=10, pady=(0, 10))

        # Categoria
        tk.Label(
            self.form_content,
            text="Categoria *",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(0, 2))

        self.var_categoria = tk.StringVar()
        self.combo_categoria = ttk.Combobox(
            self.form_content,
            textvariable=self.var_categoria,
            values=[
                "Forros", "Divisórias", "Perfis", "Acessórios", 
                "Ferramentas", "Parafusos", "Materiais", "Serviços"
            ],
            font=('Arial', 10)
        )
        self.combo_categoria.pack(fill='x', padx=10, pady=(0, 10))

        # Tipo (Produto/Serviço)
        tk.Label(
            self.form_content,
            text="Tipo *",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(0, 2))

        self.var_tipo = tk.StringVar(value="Produto")
        tipo_frame = tk.Frame(self.form_content, bg='white')
        tipo_frame.pack(fill='x', padx=10, pady=(0, 10))

        tk.Radiobutton(
            tipo_frame,
            text="Produto",
            variable=self.var_tipo,
            value="Produto",
            font=('Arial', 9),
            bg='white'
        ).pack(side='left', padx=(0, 20))

        tk.Radiobutton(
            tipo_frame,
            text="Serviço",
            variable=self.var_tipo,
            value="Serviço",
            font=('Arial', 9),
            bg='white'
        ).pack(side='left')

        # Unidade de medida
        tk.Label(
            self.form_content,
            text="Unidade",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(10, 2))

        self.var_unidade = tk.StringVar(value="UN")
        self.combo_unidade = ttk.Combobox(
            self.form_content,
            textvariable=self.var_unidade,
            values=["UN", "M", "M²", "M³", "KG", "L", "HR", "PCT"],
            state="readonly",
            font=('Arial', 10)
        )
        self.combo_unidade.pack(fill='x', padx=10, pady=(0, 10))

        # Preços
        precos_frame = tk.LabelFrame(
            self.form_content,
            text="💰 Preços",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        precos_frame.pack(fill='x', padx=10, pady=(10, 0))

        # Preço de custo
        tk.Label(
            precos_frame,
            text="Preço de Custo (R$)",
            font=('Arial', 9),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=5, pady=(5, 2))

        self.var_preco_custo = tk.StringVar(value="0,00")
        self.entry_preco_custo = tk.Entry(
            precos_frame,
            textvariable=self.var_preco_custo,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=3
        )
        self.entry_preco_custo.pack(fill='x', padx=5, pady=(0, 5))
        self.entry_preco_custo.bind('<KeyRelease>', self.format_preco)

        # Margem de lucro
        tk.Label(
            precos_frame,
            text="Margem de Lucro (%)",
            font=('Arial', 9),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=5, pady=(5, 2))

        self.var_margem = tk.StringVar(value="30")
        margem_frame = tk.Frame(precos_frame, bg='white')
        margem_frame.pack(fill='x', padx=5, pady=(0, 5))

        self.entry_margem = tk.Entry(
            margem_frame,
            textvariable=self.var_margem,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=3,
            width=10
        )
        self.entry_margem.pack(side='left')
        self.entry_margem.bind('<KeyRelease>', self.calcular_preco_venda)

        btn_calc = tk.Button(
            margem_frame,
            text="Calcular",
            font=('Arial', 8),
            bg='#3498db',
            fg='white',
            padx=8,
            pady=2,
            border=0,
            command=self.calcular_preco_venda
        )
        btn_calc.pack(side='right')

        # Preço de venda
        tk.Label(
            precos_frame,
            text="Preço de Venda (R$) *",
            font=('Arial', 9, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=5, pady=(5, 2))

        self.var_preco_venda = tk.StringVar(value="0,00")
        self.entry_preco_venda = tk.Entry(
            precos_frame,
            textvariable=self.var_preco_venda,
            font=('Arial', 10, 'bold'),
            bg='#e8f5e8',
            relief='flat',
            bd=3
        )
        self.entry_preco_venda.pack(fill='x', padx=5, pady=(0, 10))
        self.entry_preco_venda.bind('<KeyRelease>', self.format_preco)

        # Estoque
        estoque_frame = tk.LabelFrame(
            self.form_content,
            text="📦 Controle de Estoque",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        estoque_frame.pack(fill='x', padx=10, pady=(10, 0))

        # Quantidade atual
        tk.Label(
            estoque_frame,
            text="Quantidade Atual",
            font=('Arial', 9),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=5, pady=(5, 2))

        self.var_estoque_atual = tk.StringVar(value="0")
        self.entry_estoque_atual = tk.Entry(
            estoque_frame,
            textvariable=self.var_estoque_atual,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=3
        )
        self.entry_estoque_atual.pack(fill='x', padx=5, pady=(0, 5))

        # Estoque mínimo
        tk.Label(
            estoque_frame,
            text="Estoque Mínimo",
            font=('Arial', 9),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=5, pady=(5, 2))

        self.var_estoque_minimo = tk.StringVar(value="5")
        self.entry_estoque_minimo = tk.Entry(
            estoque_frame,
            textvariable=self.var_estoque_minimo,
            font=('Arial', 10),
            bg='#f8f9fa',
            relief='flat',
            bd=3
        )
        self.entry_estoque_minimo.pack(fill='x', padx=5, pady=(0, 10))

        # Status
        tk.Label(
            self.form_content,
            text="Status",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(10, 2))

        self.var_status = tk.StringVar(value="Ativo")
        status_combo = ttk.Combobox(
            self.form_content,
            textvariable=self.var_status,
            values=["Ativo", "Inativo", "Descontinuado"],
            state="readonly",
            font=('Arial', 10)
        )
        status_combo.pack(fill='x', padx=10, pady=(0, 10))

        # Descrição
        tk.Label(
            self.form_content,
            text="Descrição",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w', padx=10, pady=(10, 2))

        self.text_descricao = tk.Text(
            self.form_content,
            font=('Arial', 9),
            bg='#f8f9fa',
            relief='flat',
            bd=5,
            height=4,
            wrap='word'
        )
        self.text_descricao.pack(fill='x', padx=10, pady=(0, 20))

    def create_form_buttons(self):
        """Criar botões do formulário"""

        buttons_frame = tk.Frame(self.form_content, bg='white')
        buttons_frame.pack(fill='x', padx=10, pady=(10, 20))

        # Botão Salvar
        self.btn_salvar = tk.Button(
            buttons_frame,
            text="💾 Salvar",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8,
            border=0,
            command=self.salvar_produto
        )
        self.btn_salvar.pack(side='left', padx=(0, 10))

        # Botão Cancelar
        self.btn_cancelar = tk.Button(
            buttons_frame,
            text="❌ Cancelar",
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=8,
            border=0,
            command=self.cancelar_edicao
        )
        self.btn_cancelar.pack(side='left')

        # Botão Limpar
        self.btn_limpar = tk.Button(
            buttons_frame,
            text="🧹 Limpar",
            font=('Arial', 10),
            bg='#f39c12',
            fg='white',
            padx=20,
            pady=8,
            border=0,
            command=self.limpar_formulario
        )
        self.btn_limpar.pack(side='right')

    # =======================================
    # MÉTODOS DE CONTROLE
    # =======================================

    def format_preco(self, event=None):
        """Formatar preços com vírgula decimal"""

        widget = event.widget if event else None
        if not widget:
            return

        valor = widget.get().replace("R$", "").replace(" ", "")

        # Remover caracteres não numéricos exceto vírgula
        valor_limpo = re.sub(r'[^\d,]', '', valor)

        # Garantir apenas uma vírgula
        if valor_limpo.count(',') > 1:
            partes = valor_limpo.split(',')
            valor_limpo = partes[0] + ',' + ''.join(partes[1:])

        # Limitar casas decimais
        if ',' in valor_limpo:
            partes = valor_limpo.split(',')
            if len(partes[1]) > 2:
                valor_limpo = partes[0] + ',' + partes[1][:2]

        # Atualizar campo sem disparar evento
        current_pos = widget.index(tk.INSERT)
        widget.delete(0, tk.END)
        widget.insert(0, valor_limpo)

        # Restaurar posição do cursor
        try:
            widget.icursor(current_pos)
        except Exception as e:
            # Falha ao restaurar cursor não é crítica
            print(f"Warning: Erro ao restaurar posição do cursor: {e}")

    def calcular_preco_venda(self, event=None):
        """Calcular preço de venda baseado no custo e margem"""

        try:
            # Obter preço de custo
            custo_str = self.var_preco_custo.get().replace(',', '.')
            custo = float(custo_str) if custo_str else 0

            # Obter margem
            margem_str = self.var_margem.get()
            margem = float(margem_str) if margem_str else 0

            # Calcular preço de venda
            if custo > 0 and margem > 0:
                preco_venda = custo * (1 + margem / 100)
                self.var_preco_venda.set(f"{preco_venda:.2f}".replace('.', ','))

        except (ValueError, InvalidOperation):
            pass

    def gerar_codigo_barras(self):
        """Gerar código de barras para produto selecionado"""

        if not self.produto_selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para gerar código de barras!")
            return

        # Por enquanto, apenas uma mensagem - será implementado na próxima fase
        messagebox.showinfo(
            "Código de Barras",
            "Funcionalidade de código de barras será implementada na próxima versão.\n\n"
            f"Produto: {self.produto_selecionado.get('nome', '')}\n"
            f"Código: {self.produto_selecionado.get('codigo', '')}"
        )

    def on_produto_selecionado(self, event=None):
        """Callback quando produto é selecionado na lista"""

        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            produto_id = item['values'][0]

            # Encontrar produto nos dados
            self.produto_selecionado = None
            for produto in self.produtos_data:
                if produto.get('id') == produto_id:
                    self.produto_selecionado = produto
                    break

            # Habilitar botões
            self.btn_editar.config(state='normal')
            self.btn_excluir.config(state='normal')
            self.btn_barcode.config(state='normal')
        else:
            self.produto_selecionado = None
            self.btn_editar.config(state='disabled')
            self.btn_excluir.config(state='disabled')
            self.btn_barcode.config(state='disabled')

    def filtrar_produtos(self, event=None):
        """Filtrar produtos na lista"""

        termo = self.entry_busca.get().lower()
        categoria_filtro = self.combo_categoria_filtro.get()

        # Filtrar produtos
        produtos_filtrados = []
        for produto in self.produtos_data:
            # Filtro por termo de busca
            match_termo = (
                termo in produto.get('nome', '').lower() or
                termo in produto.get('codigo', '').lower() or
                termo in produto.get('categoria', '').lower()
            )

            # Filtro por categoria
            match_categoria = (
                not categoria_filtro or 
                categoria_filtro == "Todas" or
                produto.get('categoria', '') == categoria_filtro
            )

            if match_termo and match_categoria:
                produtos_filtrados.append(produto)

        self.popular_lista(produtos_filtrados)

    def popular_lista(self, produtos_list=None):
        """Popular lista de produtos"""

        if produtos_list is None:
            produtos_list = self.produtos_data

        # Limpar lista atual
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Adicionar produtos
        for produto in produtos_list:
            # Formatar preço para exibição
            preco = produto.get('preco_venda', 0)
            preco_formatado = f"R$ {preco:.2f}".replace('.', ',') if preco else "R$ 0,00"

            self.tree.insert('', 'end', values=(
                produto.get('id', ''),
                produto.get('codigo', ''),
                produto.get('nome', ''),
                produto.get('categoria', ''),
                produto.get('tipo', ''),
                preco_formatado,
                produto.get('estoque_atual', 0),
                produto.get('status', '')
            ))

        # Atualizar contador
        total = len(produtos_list)
        self.label_contador.config(text=f"Total: {total} produtos")

        # Atualizar filtro de categorias
        self.atualizar_filtro_categorias()

    def atualizar_filtro_categorias(self):
        """Atualizar opções do filtro de categorias"""

        categorias = set()
        for produto in self.produtos_data:
            categoria = produto.get('categoria', '')
            if categoria:
                categorias.add(categoria)

        categorias_list = ["Todas"] + sorted(list(categorias))
        self.combo_categoria_filtro['values'] = categorias_list

        if not self.combo_categoria_filtro.get():
            self.combo_categoria_filtro.set("Todas")

    # =======================================
    # MÉTODOS DE API (MOCK)
    # =======================================

    def carregar_produtos(self):
        """Carregar lista de produtos da API"""

        def load_data():
            try:
                # Mock data - substituir por chamada real à API
                self.produtos_data = [
                    {
                        "id": 1,
                        "codigo": "FOR001",
                        "nome": "Forro PVC Branco 20cm",
                        "categoria": "Forros",
                        "tipo": "Produto",
                        "unidade": "M²",
                        "preco_custo": 15.50,
                        "preco_venda": 25.00,
                        "estoque_atual": 150,
                        "estoque_minimo": 20,
                        "status": "Ativo",
                        "descricao": "Forro em PVC cor branca, largura 20cm"
                    },
                    {
                        "id": 2,
                        "codigo": "DIV001", 
                        "nome": "Divisória Eucatex 2,70m",
                        "categoria": "Divisórias",
                        "tipo": "Produto",
                        "unidade": "UN",
                        "preco_custo": 180.00,
                        "preco_venda": 250.00,
                        "estoque_atual": 45,
                        "estoque_minimo": 10,
                        "status": "Ativo",
                        "descricao": "Divisória eucatex altura 2,70m"
                    },
                    {
                        "id": 3,
                        "codigo": "SRV001",
                        "nome": "Instalação de Forro",
                        "categoria": "Serviços",
                        "tipo": "Serviço", 
                        "unidade": "M²",
                        "preco_custo": 8.00,
                        "preco_venda": 15.00,
                        "estoque_atual": 0,
                        "estoque_minimo": 0,
                        "status": "Ativo",
                        "descricao": "Serviço de instalação de forro por m²"
                    }
                ]

                # Atualizar interface na thread principal
                self.root.after(0, lambda: self.popular_lista())

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro ao carregar produtos: {str(e)}"
                ))

        # Executar em thread separada
        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()

    def salvar_produto(self):
        """Salvar produto (criar ou atualizar)"""

        # Validar campos obrigatórios
        if not self.validar_formulario():
            return

        # Preparar dados
        dados_produto = {
            "codigo": self.var_codigo.get().strip(),
            "nome": self.var_nome.get().strip(),
            "categoria": self.var_categoria.get(),
            "tipo": self.var_tipo.get(),
            "unidade": self.var_unidade.get(),
            "preco_custo": self.parse_preco(self.var_preco_custo.get()),
            "preco_venda": self.parse_preco(self.var_preco_venda.get()),
            "estoque_atual": int(self.var_estoque_atual.get() or 0),
            "estoque_minimo": int(self.var_estoque_minimo.get() or 0),
            "status": self.var_status.get(),
            "descricao": self.text_descricao.get("1.0", tk.END).strip()
        }

        # Mock - simular salvamento
        messagebox.showinfo("Sucesso", "Produto salvo com sucesso!\n(Mock - API será implementada)")
        self.limpar_formulario()
        self.carregar_produtos()

    def parse_preco(self, preco_str):
        """Converter string de preço para float"""
        try:
            return float(preco_str.replace(',', '.'))
        except (ValueError, AttributeError) as e:
            print(f"Warning: Erro ao converter preço '{preco_str}': {e}")
            return 0.0

    def validar_formulario(self):
        """Validar campos do formulário"""

        # Campos obrigatórios
        if not self.var_codigo.get().strip():
            messagebox.showerror("Erro", "Código é obrigatório!")
            self.entry_codigo.focus()
            return False

        if not self.var_nome.get().strip():
            messagebox.showerror("Erro", "Nome é obrigatório!")
            self.entry_nome.focus()
            return False

        if not self.var_categoria.get().strip():
            messagebox.showerror("Erro", "Categoria é obrigatória!")
            self.combo_categoria.focus()
            return False

        if not self.var_preco_venda.get().strip() or self.parse_preco(self.var_preco_venda.get()) <= 0:
            messagebox.showerror("Erro", "Preço de venda é obrigatório e deve ser maior que zero!")
            self.entry_preco_venda.focus()
            return False

        return True

    # =======================================
    # MÉTODOS DE AÇÃO
    # =======================================

    def novo_produto(self):
        """Preparar formulário para novo produto"""

        self.limpar_formulario()
        self.entry_codigo.focus()

    def editar_produto(self, event=None):
        """Editar produto selecionado"""

        if not self.produto_selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para editar!")
            return

        # Preencher formulário com dados do produto
        produto = self.produto_selecionado

        self.var_id.set(str(produto.get('id', '')))
        self.var_codigo.set(produto.get('codigo', ''))
        self.var_nome.set(produto.get('nome', ''))
        self.var_categoria.set(produto.get('categoria', ''))
        self.var_tipo.set(produto.get('tipo', 'Produto'))
        self.var_unidade.set(produto.get('unidade', 'UN'))

        # Formatar preços
        preco_custo = produto.get('preco_custo', 0)
        self.var_preco_custo.set(f"{preco_custo:.2f}".replace('.', ','))

        preco_venda = produto.get('preco_venda', 0)
        self.var_preco_venda.set(f"{preco_venda:.2f}".replace('.', ','))

        self.var_estoque_atual.set(str(produto.get('estoque_atual', 0)))
        self.var_estoque_minimo.set(str(produto.get('estoque_minimo', 0)))
        self.var_status.set(produto.get('status', 'Ativo'))

        self.text_descricao.delete("1.0", tk.END)
        self.text_descricao.insert("1.0", produto.get('descricao', ''))

        # Focar no primeiro campo
        self.entry_codigo.focus()

    def excluir_produto(self):
        """Excluir produto selecionado"""

        if not self.produto_selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir!")
            return

        # Confirmar exclusão
        nome = self.produto_selecionado.get('nome', '')
        resultado = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o produto:\n\n{nome}\n\nEsta ação não pode ser desfeita!"
        )

        if resultado:
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!\n(Mock - API será implementada)")
            self.limpar_formulario()
            self.carregar_produtos()

    def cancelar_edicao(self):
        """Cancelar edição atual"""

        self.limpar_formulario()

    def limpar_formulario(self):
        """Limpar todos os campos do formulário"""

        self.var_id.set("")
        self.var_codigo.set("")
        self.var_nome.set("")
        self.var_categoria.set("")
        self.var_tipo.set("Produto")
        self.var_unidade.set("UN")
        self.var_preco_custo.set("0,00")
        self.var_margem.set("30")
        self.var_preco_venda.set("0,00")
        self.var_estoque_atual.set("0")
        self.var_estoque_minimo.set("5")
        self.var_status.set("Ativo")

        self.text_descricao.delete("1.0", tk.END)

        # Desselecionar na lista
        self.tree.selection_remove(self.tree.selection())
        self.produto_selecionado = None

        # Desabilitar botões
        self.btn_editar.config(state='disabled')
        self.btn_excluir.config(state='disabled')
        self.btn_barcode.config(state='disabled')

    def on_closing(self):
        """Tratar fechamento da janela"""

        if messagebox.askyesno("Fechar", "Deseja fechar o gerenciamento de produtos?"):
            self.root.destroy()

    def run(self):
        """Executar a interface"""

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
# FUNÇÃO PRINCIPAL
# =======================================

def main():
    """Teste da interface de produtos"""

    # Dados de usuário mock para teste
    user_data = {
        "access_token": "mock_token",
        "user": {
            "username": "admin",
            "nome_completo": "Administrador"
        }
    }

    app = ProdutosWindow(user_data)
    app.run()

if __name__ == "__main__":
    main()