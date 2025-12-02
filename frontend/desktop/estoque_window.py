"""
SISTEMA ERP PRIMOTEX - CONTROLE DE ESTOQUE
==========================================

Sistema completo de controle de estoque com movimentações,
inventário, alertas e histórico detalhado.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import requests

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
# CLASSE CONTROLE DE ESTOQUE
# =======================================

@require_login()
class EstoqueWindow:
    """Sistema de controle de estoque"""

    def __init__(self, parent_window=None):
        # NÃO recebe mais user_data - usa SessionManager
        self.token = get_token_for_api()
        self.user_data = get_current_user_info()
        self.parent_window = parent_window

        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.estoque_data = []
        self.movimentacoes_data = []
        self.produtos_data = []
        self.item_selecionado = None

        self.setup_window()
        self.create_widgets()
        self.carregar_dados_iniciais()

    def setup_window(self):
        """Configurar janela"""

        self.root.title("Sistema ERP Primotex - Controle de Estoque")
        self.root.geometry("1600x1000")

        if not self.parent_window:
            self.root.state('zoomed')

        self.root.configure(bg='#f8f9fa')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Criar widgets da interface"""

        # === BARRA SUPERIOR ===
        self.create_top_bar()

        # === CONTAINER PRINCIPAL ===
        main_container = tk.Frame(self.root, bg='#f8f9fa')
        main_container.pack(fill='both', expand=True, padx=15, pady=10)

        # === NOTEBOOK COM ABAS ===
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)

        # === ABA ESTOQUE ATUAL ===
        self.create_estoque_tab()

        # === ABA MOVIMENTAÇÕES ===
        self.create_movimentacoes_tab()

        # === ABA ALERTAS ===
        self.create_alertas_tab()

        # === ABA INVENTÁRIO ===
        self.create_inventario_tab()

    def create_top_bar(self):
        """Criar barra superior"""

        top_frame = tk.Frame(self.root, bg='#e67e22', height=50)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)

        container = tk.Frame(top_frame, bg='#e67e22')
        container.pack(fill='both', expand=True, padx=20, pady=8)

        # Título
        title_label = tk.Label(
            container,
            text="📦 Controle de Estoque",
            font=('Arial', 16, 'bold'),
            bg='#e67e22',
            fg='white'
        )
        title_label.pack(side='left', pady=5)

        # Status e última atualização
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        status_text = f"📊 Última atualização: {now} | 👤 {self.user_data.get('user', {}).get('username', 'N/A')}"

        status_label = tk.Label(
            container,
            text=status_text,
            font=('Arial', 10),
            bg='#e67e22',
            fg='#ecf0f1'
        )
        status_label.pack(side='right', pady=5)

    def create_estoque_tab(self):
        """Criar aba de estoque atual"""

        # Frame principal da aba
        estoque_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(estoque_frame, text="📦 Estoque Atual")

        # === BARRA DE FERRAMENTAS ===
        toolbar = tk.Frame(estoque_frame, bg='#ecf0f1', relief='raised', bd=1)
        toolbar.pack(fill='x', pady=(0, 10))

        toolbar_content = tk.Frame(toolbar, bg='#ecf0f1')
        toolbar_content.pack(fill='x', padx=10, pady=8)

        # Botões da esquerda
        left_frame = tk.Frame(toolbar_content, bg='#ecf0f1')
        left_frame.pack(side='left')

        # Botão Nova Movimentação
        btn_nova_mov = tk.Button(
            left_frame,
            text="➕ Nova Movimentação",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.nova_movimentacao
        )
        btn_nova_mov.pack(side='left', padx=(0, 10))

        # Botão Atualizar
        btn_atualizar = tk.Button(
            left_frame,
            text="🔄 Atualizar",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.carregar_estoque
        )
        btn_atualizar.pack(side='left', padx=(0, 10))

        # Separador
        separator = tk.Frame(left_frame, bg='#bdc3c7', width=2, height=30)
        separator.pack(side='left', padx=15)

        # Botão Exportar
        btn_exportar = tk.Button(
            left_frame,
            text="📊 Exportar",
            font=('Arial', 10),
            bg='#9b59b6',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.exportar_estoque
        )
        btn_exportar.pack(side='left')

        # Campo de busca (direita)
        right_frame = tk.Frame(toolbar_content, bg='#ecf0f1')
        right_frame.pack(side='right')

        tk.Label(
            right_frame,
            text="🔍 Buscar:",
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(side='left', padx=(0, 5))

        self.entry_busca_estoque = tk.Entry(
            right_frame,
            font=('Arial', 10),
            width=25,
            bg='white',
            relief='flat',
            bd=5
        )
        self.entry_busca_estoque.pack(side='left', padx=(0, 10))
        self.entry_busca_estoque.bind('<KeyRelease>', self.filtrar_estoque)

        # === LISTA DE ESTOQUE ===
        list_frame = tk.Frame(estoque_frame, bg='white')
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Configurar Treeview
        columns = ('codigo', 'produto', 'categoria', 'atual', 'minimo', 'disponivel', 'reservado', 'status', 'valor_total')

        self.tree_estoque = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=20
        )

        # Configurar cabeçalhos
        self.tree_estoque.heading('codigo', text='Código')
        self.tree_estoque.heading('produto', text='Produto')
        self.tree_estoque.heading('categoria', text='Categoria')
        self.tree_estoque.heading('atual', text='Qty Atual')
        self.tree_estoque.heading('minimo', text='Qty Mínima')
        self.tree_estoque.heading('disponivel', text='Disponível')
        self.tree_estoque.heading('reservado', text='Reservado')
        self.tree_estoque.heading('status', text='Status')
        self.tree_estoque.heading('valor_total', text='Valor Total')

        # Configurar larguras
        self.tree_estoque.column('codigo', width=100, anchor='center')
        self.tree_estoque.column('produto', width=250, anchor='w')
        self.tree_estoque.column('categoria', width=120, anchor='center')
        self.tree_estoque.column('atual', width=80, anchor='center')
        self.tree_estoque.column('minimo', width=80, anchor='center')
        self.tree_estoque.column('disponivel', width=80, anchor='center')
        self.tree_estoque.column('reservado', width=80, anchor='center')
        self.tree_estoque.column('status', width=100, anchor='center')
        self.tree_estoque.column('valor_total', width=120, anchor='e')

        # Scrollbars
        v_scroll_estoque = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree_estoque.yview)
        h_scroll_estoque = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree_estoque.xview)

        self.tree_estoque.configure(yscrollcommand=v_scroll_estoque.set, xscrollcommand=h_scroll_estoque.set)

        # Pack
        self.tree_estoque.pack(side='left', fill='both', expand=True)
        v_scroll_estoque.pack(side='right', fill='y')
        h_scroll_estoque.pack(side='bottom', fill='x')

        # Eventos
        self.tree_estoque.bind('<<TreeviewSelect>>', self.on_estoque_selecionado)
        self.tree_estoque.bind('<Double-1>', self.ver_detalhes_produto)

        # Rodapé com estatísticas
        self.create_estoque_footer(estoque_frame)

    def create_movimentacoes_tab(self):
        """Criar aba de movimentações"""

        mov_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(mov_frame, text="🔄 Movimentações")

        # === BARRA DE FERRAMENTAS ===
        toolbar = tk.Frame(mov_frame, bg='#ecf0f1', relief='raised', bd=1)
        toolbar.pack(fill='x', pady=(0, 10))

        toolbar_content = tk.Frame(toolbar, bg='#ecf0f1')
        toolbar_content.pack(fill='x', padx=10, pady=8)

        # Filtros
        filter_frame = tk.Frame(toolbar_content, bg='#ecf0f1')
        filter_frame.pack(side='left')

        # Filtro por tipo
        tk.Label(
            filter_frame,
            text="Tipo:",
            font=('Arial', 9),
            bg='#ecf0f1'
        ).pack(side='left', padx=(0, 5))

        self.combo_tipo_mov = ttk.Combobox(
            filter_frame,
            values=["Todos", "Entrada", "Saída", "Ajuste", "Transferência"],
            width=12,
            state="readonly"
        )
        self.combo_tipo_mov.set("Todos")
        self.combo_tipo_mov.pack(side='left', padx=(0, 15))
        self.combo_tipo_mov.bind('<<ComboboxSelected>>', self.filtrar_movimentacoes)

        # Filtro por período
        tk.Label(
            filter_frame,
            text="Período:",
            font=('Arial', 9),
            bg='#ecf0f1'
        ).pack(side='left', padx=(0, 5))

        self.combo_periodo = ttk.Combobox(
            filter_frame,
            values=["Hoje", "Última semana", "Último mês", "Últimos 3 meses", "Todos"],
            width=15,
            state="readonly"
        )
        self.combo_periodo.set("Última semana")
        self.combo_periodo.pack(side='left', padx=(0, 15))
        self.combo_periodo.bind('<<ComboboxSelected>>', self.filtrar_movimentacoes)

        # Botão atualizar
        btn_atualizar_mov = tk.Button(
            filter_frame,
            text="🔄 Atualizar",
            font=('Arial', 9),
            bg='#3498db',
            fg='white',
            padx=10,
            pady=3,
            border=0,
            command=self.carregar_movimentacoes
        )
        btn_atualizar_mov.pack(side='left')

        # === LISTA DE MOVIMENTAÇÕES ===
        mov_list_frame = tk.Frame(mov_frame, bg='white')
        mov_list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns_mov = ('data', 'tipo', 'produto', 'quantidade', 'valor_unit', 'valor_total', 'usuario', 'observacoes')

        self.tree_movimentacoes = ttk.Treeview(
            mov_list_frame,
            columns=columns_mov,
            show='headings',
            height=20
        )

        # Cabeçalhos
        self.tree_movimentacoes.heading('data', text='Data/Hora')
        self.tree_movimentacoes.heading('tipo', text='Tipo')
        self.tree_movimentacoes.heading('produto', text='Produto')
        self.tree_movimentacoes.heading('quantidade', text='Quantidade')
        self.tree_movimentacoes.heading('valor_unit', text='Valor Unit.')
        self.tree_movimentacoes.heading('valor_total', text='Valor Total')
        self.tree_movimentacoes.heading('usuario', text='Usuário')
        self.tree_movimentacoes.heading('observacoes', text='Observações')

        # Larguras
        self.tree_movimentacoes.column('data', width=130, anchor='center')
        self.tree_movimentacoes.column('tipo', width=80, anchor='center')
        self.tree_movimentacoes.column('produto', width=200, anchor='w')
        self.tree_movimentacoes.column('quantidade', width=80, anchor='center')
        self.tree_movimentacoes.column('valor_unit', width=90, anchor='e')
        self.tree_movimentacoes.column('valor_total', width=90, anchor='e')
        self.tree_movimentacoes.column('usuario', width=100, anchor='center')
        self.tree_movimentacoes.column('observacoes', width=200, anchor='w')

        # Scrollbars
        v_scroll_mov = ttk.Scrollbar(mov_list_frame, orient='vertical', command=self.tree_movimentacoes.yview)
        h_scroll_mov = ttk.Scrollbar(mov_list_frame, orient='horizontal', command=self.tree_movimentacoes.xview)

        self.tree_movimentacoes.configure(yscrollcommand=v_scroll_mov.set, xscrollcommand=h_scroll_mov.set)

        # Pack
        self.tree_movimentacoes.pack(side='left', fill='both', expand=True)
        v_scroll_mov.pack(side='right', fill='y')
        h_scroll_mov.pack(side='bottom', fill='x')

    def create_alertas_tab(self):
        """Criar aba de alertas"""

        alertas_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(alertas_frame, text="⚠️ Alertas")

        # Título
        title = tk.Label(
            alertas_frame,
            text="⚠️ Alertas de Estoque",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#e74c3c'
        )
        title.pack(pady=20)

        # === ALERTAS DE ESTOQUE BAIXO ===
        baixo_frame = tk.LabelFrame(
            alertas_frame,
            text="🔻 Produtos com Estoque Baixo",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#e74c3c'
        )
        baixo_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns_baixo = ('produto', 'atual', 'minimo', 'diferenca', 'valor_perdido')

        self.tree_baixo = ttk.Treeview(
            baixo_frame,
            columns=columns_baixo,
            show='headings',
            height=8
        )

        self.tree_baixo.heading('produto', text='Produto')
        self.tree_baixo.heading('atual', text='Qty Atual')
        self.tree_baixo.heading('minimo', text='Qty Mínima')
        self.tree_baixo.heading('diferenca', text='Diferença')
        self.tree_baixo.heading('valor_perdido', text='Valor em Risco')

        self.tree_baixo.column('produto', width=300, anchor='w')
        self.tree_baixo.column('atual', width=100, anchor='center')
        self.tree_baixo.column('minimo', width=100, anchor='center')
        self.tree_baixo.column('diferenca', width=100, anchor='center')
        self.tree_baixo.column('valor_perdido', width=120, anchor='e')

        self.tree_baixo.pack(fill='both', expand=True, padx=10, pady=10)

        # === ALERTAS DE PRODUTOS ZERADOS ===
        zerado_frame = tk.LabelFrame(
            alertas_frame,
            text="🚫 Produtos Zerados",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#c0392b'
        )
        zerado_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns_zerado = ('produto', 'categoria', 'ultima_movimentacao', 'dias_zerado')

        self.tree_zerado = ttk.Treeview(
            zerado_frame,
            columns=columns_zerado,
            show='headings',
            height=8
        )

        self.tree_zerado.heading('produto', text='Produto')
        self.tree_zerado.heading('categoria', text='Categoria')
        self.tree_zerado.heading('ultima_movimentacao', text='Última Movimentação')
        self.tree_zerado.heading('dias_zerado', text='Dias Zerado')

        self.tree_zerado.column('produto', width=300, anchor='w')
        self.tree_zerado.column('categoria', width=150, anchor='center')
        self.tree_zerado.column('ultima_movimentacao', width=150, anchor='center')
        self.tree_zerado.column('dias_zerado', width=100, anchor='center')

        self.tree_zerado.pack(fill='both', expand=True, padx=10, pady=10)

    def create_inventario_tab(self):
        """Criar aba de inventário"""

        inv_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(inv_frame, text="📋 Inventário")

        # === CABEÇALHO ===
        header = tk.Frame(inv_frame, bg='white')
        header.pack(fill='x', padx=20, pady=20)

        title = tk.Label(
            header,
            text="📋 Controle de Inventário",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title.pack(side='left')

        # Botões
        btn_frame = tk.Frame(header, bg='white')
        btn_frame.pack(side='right')

        btn_novo_inv = tk.Button(
            btn_frame,
            text="📝 Novo Inventário",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.novo_inventario
        )
        btn_novo_inv.pack(side='left', padx=(0, 10))

        btn_importar = tk.Button(
            btn_frame,
            text="📄 Importar",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.importar_inventario
        )
        btn_importar.pack(side='left')

        # === FORMULÁRIO DE INVENTÁRIO ===
        form_frame = tk.LabelFrame(
            inv_frame,
            text="🔧 Ajuste de Inventário",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        form_frame.pack(fill='x', padx=20, pady=10)

        form_content = tk.Frame(form_frame, bg='white')
        form_content.pack(fill='x', padx=10, pady=10)

        # Produto
        tk.Label(
            form_content,
            text="Produto:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).grid(row=0, column=0, sticky='w', padx=(0, 10))

        self.combo_produto_inv = ttk.Combobox(
            form_content,
            font=('Arial', 10),
            width=40,
            state="readonly"
        )
        self.combo_produto_inv.grid(row=0, column=1, sticky='w', padx=(0, 20))

        # Quantidade atual
        tk.Label(
            form_content,
            text="Qty Atual:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).grid(row=0, column=2, sticky='w', padx=(0, 10))

        self.var_qty_atual = tk.StringVar(value="0")
        self.entry_qty_atual = tk.Entry(
            form_content,
            textvariable=self.var_qty_atual,
            font=('Arial', 10),
            width=10,
            state='readonly',
            bg='#f8f9fa'
        )
        self.entry_qty_atual.grid(row=0, column=3, padx=(0, 20))

        # Nova quantidade
        tk.Label(
            form_content,
            text="Nova Qty:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(10, 0))

        self.var_nova_qty = tk.StringVar()
        self.entry_nova_qty = tk.Entry(
            form_content,
            textvariable=self.var_nova_qty,
            font=('Arial', 10),
            width=10
        )
        self.entry_nova_qty.grid(row=1, column=1, sticky='w', pady=(10, 0))

        # Motivo
        tk.Label(
            form_content,
            text="Motivo:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).grid(row=1, column=2, sticky='w', padx=(0, 10), pady=(10, 0))

        self.combo_motivo = ttk.Combobox(
            form_content,
            values=["Inventário", "Avaria", "Perda", "Furto", "Ajuste", "Devolução"],
            font=('Arial', 10),
            width=15
        )
        self.combo_motivo.grid(row=1, column=3, sticky='w', pady=(10, 0))

        # Observações
        tk.Label(
            form_content,
            text="Observações:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).grid(row=2, column=0, sticky='nw', padx=(0, 10), pady=(10, 0))

        self.text_obs_inv = tk.Text(
            form_content,
            font=('Arial', 9),
            width=60,
            height=3,
            wrap='word'
        )
        self.text_obs_inv.grid(row=2, column=1, columnspan=3, sticky='w', pady=(10, 0))

        # Botões do formulário
        btn_form_frame = tk.Frame(form_content, bg='white')
        btn_form_frame.grid(row=3, column=0, columnspan=4, pady=15)

        btn_aplicar = tk.Button(
            btn_form_frame,
            text="✅ Aplicar Ajuste",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=5,
            border=0,
            command=self.aplicar_ajuste_inventario
        )
        btn_aplicar.pack(side='left', padx=(0, 10))

        btn_limpar_inv = tk.Button(
            btn_form_frame,
            text="🧹 Limpar",
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=5,
            border=0,
            command=self.limpar_formulario_inventario
        )
        btn_limpar_inv.pack(side='left')

        # Eventos
        self.combo_produto_inv.bind('<<ComboboxSelected>>', self.on_produto_inventario_selecionado)

    def create_estoque_footer(self, parent):
        """Criar rodapé com estatísticas do estoque"""

        footer = tk.Frame(parent, bg='#34495e', height=60)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)

        stats_frame = tk.Frame(footer, bg='#34495e')
        stats_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Estatísticas
        self.label_total_produtos = tk.Label(
            stats_frame,
            text="Total de Produtos: 0",
            font=('Arial', 10, 'bold'),
            bg='#34495e',
            fg='white'
        )
        self.label_total_produtos.pack(side='left')

        self.label_valor_total = tk.Label(
            stats_frame,
            text="Valor Total: R$ 0,00",
            font=('Arial', 10, 'bold'),
            bg='#34495e',
            fg='#f1c40'
        )
        self.label_valor_total.pack(side='left', padx=(30, 0))

        self.label_alertas = tk.Label(
            stats_frame,
            text="Alertas: 0",
            font=('Arial', 10, 'bold'),
            bg='#34495e',
            fg='#e74c3c'
        )
        self.label_alertas.pack(side='right')

    # =======================================
    # MÉTODOS DE CONTROLE E EVENTOS
    # =======================================

    def on_estoque_selecionado(self, event=None):
        """Callback quando item de estoque é selecionado"""
        selection = self.tree_estoque.selection()
        if selection:
            item = self.tree_estoque.item(selection[0])
            self.item_selecionado = item['values']

    def on_produto_inventario_selecionado(self, event=None):
        """Callback quando produto é selecionado no inventário"""
        produto_nome = self.combo_produto_inv.get()

        # Buscar quantidade atual do produto
        for produto in self.produtos_data:
            if produto.get('nome') == produto_nome:
                self.var_qty_atual.set(str(produto.get('estoque_atual', 0)))
                break

    def filtrar_estoque(self, event=None):
        """Filtrar itens do estoque"""
        termo = self.entry_busca_estoque.get().lower()

        # Limpar lista atual
        for item in self.tree_estoque.get_children():
            self.tree_estoque.delete(item)

        # Filtrar e exibir apenas itens que contêm o termo
        try:
            dados_estoque = self.obter_dados_estoque()
            for item in dados_estoque:
                # Verificar se o termo está no código, nome ou categoria
                if (termo in item.get('codigo', '').lower() or 
                    termo in item.get('nome', '').lower() or 
                    termo in item.get('categoria', '').lower()):

                    self.tree_estoque.insert('', 'end', values=(
                        item.get('codigo', ''),
                        item.get('nome', ''),
                        item.get('categoria', ''),
                        item.get('quantidade', 0),
                        item.get('unidade', ''),
                        f"R$ {item.get('valor_unitario', 0):.2f}",
                        f"R$ {item.get('valor_total', 0):.2f}"
                    ))
        except Exception as e:
            print(f"Erro ao filtrar estoque: {e}")

    def filtrar_movimentacoes(self, event=None):
        """Filtrar movimentações por tipo e período"""
        tipo = self.combo_tipo_mov.get()
        # período será usado quando implementarmos filtro por data

        # Limpar lista atual
        for item in self.tree_movimentacoes.get_children():
            self.tree_movimentacoes.delete(item)

        try:
            dados_movimentacoes = self.obter_dados_movimentacoes()
            for mov in dados_movimentacoes:
                # Filtrar por tipo se especificado
                if tipo != "Todos" and mov.get('tipo', '') != tipo:
                    continue

                # TODO: Implementar filtro por período quando houver campo de data
                # Por enquanto, mostrar todas as movimentações do tipo selecionado

                self.tree_movimentacoes.insert('', 'end', values=(
                    mov.get('data', ''),
                    mov.get('produto', ''),
                    mov.get('tipo', ''),
                    mov.get('quantidade', 0),
                    mov.get('observacao', '')
                ))
        except Exception as e:
            print(f"Erro ao filtrar movimentações: {e}")

    def obter_dados_estoque(self):
        """Obter dados simulados de estoque"""
        # Dados simulados - em produção viria da API
        return [
            {'codigo': 'PROD001', 'nome': 'Forro PVC Branco', 'categoria': 'Forros', 
             'quantidade': 150, 'unidade': 'm²', 'valor_unitario': 25.50, 'valor_total': 3825.00},
            {'codigo': 'PROD002', 'nome': 'Divisória Eucatex', 'categoria': 'Divisórias', 
             'quantidade': 80, 'unidade': 'm²', 'valor_unitario': 45.00, 'valor_total': 3600.00},
            {'codigo': 'SERV001', 'nome': 'Instalação de Forro', 'categoria': 'Serviços', 
             'quantidade': 0, 'unidade': 'un', 'valor_unitario': 15.00, 'valor_total': 0.00}
        ]

    def obter_dados_movimentacoes(self):
        """Obter dados simulados de movimentações"""
        # Dados simulados - em produção viria da API
        return [
            {'data': '28/10/2025', 'produto': 'PROD001 - Forro PVC Branco', 'tipo': 'Entrada', 
             'quantidade': 100, 'observacao': 'Compra fornecedor XYZ'},
            {'data': '29/10/2025', 'produto': 'PROD001 - Forro PVC Branco', 'tipo': 'Saída', 
             'quantidade': 25, 'observacao': 'Obra residencial cliente ABC'},
            {'data': '29/10/2025', 'produto': 'PROD002 - Divisória Eucatex', 'tipo': 'Entrada', 
             'quantidade': 50, 'observacao': 'Reposição estoque'}
        ]

    # =======================================
    # MÉTODOS DE API (MOCK)
    # =======================================

    def carregar_dados_iniciais(self):
        """Carregar dados iniciais"""
        def load_data():
            try:
                self.carregar_produtos()
                self.carregar_estoque()
                self.carregar_movimentacoes()
                self.carregar_alertas()

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro ao carregar dados: {str(e)}"
                ))

        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()

    def carregar_produtos(self):
        """Carregar lista de produtos"""
        # Mock data
        self.produtos_data = [
            {
                "id": 1,
                "codigo": "FOR001",
                "nome": "Forro PVC Branco 20cm",
                "categoria": "Forros",
                "preco_custo": 15.50,
                "preco_venda": 25.00,
                "estoque_atual": 150,
                "estoque_minimo": 20,
                "estoque_reservado": 5
            },
            {
                "id": 2,
                "codigo": "DIV001",
                "nome": "Divisória Eucatex 2,70m",
                "categoria": "Divisórias",
                "preco_custo": 180.00,
                "preco_venda": 250.00,
                "estoque_atual": 45,
                "estoque_minimo": 10,
                "estoque_reservado": 2
            },
            {
                "id": 3,
                "codigo": "PER001",
                "nome": "Perfil Alumínio 30mm",
                "categoria": "Perfis",
                "preco_custo": 12.00,
                "preco_venda": 18.00,
                "estoque_atual": 8,
                "estoque_minimo": 15,
                "estoque_reservado": 0
            },
            {
                "id": 4,
                "codigo": "PAR001",
                "nome": "Parafuso Rosca Soberba 3x25",
                "categoria": "Parafusos",
                "preco_custo": 0.05,
                "preco_venda": 0.12,
                "estoque_atual": 0,
                "estoque_minimo": 500,
                "estoque_reservado": 0
            }
        ]

        # Atualizar combobox do inventário
        produtos_nomes = [p['nome'] for p in self.produtos_data]
        self.root.after(0, lambda: self.combo_produto_inv.configure(values=produtos_nomes))

    def carregar_estoque(self):
        """Carregar dados do estoque"""
        def update_ui():
            # Limpar árvore
            for item in self.tree_estoque.get_children():
                self.tree_estoque.delete(item)

            total_produtos = 0
            valor_total = 0
            alertas = 0

            for produto in self.produtos_data:
                atual = produto.get('estoque_atual', 0)
                minimo = produto.get('estoque_minimo', 0)
                reservado = produto.get('estoque_reservado', 0)
                disponivel = max(0, atual - reservado)

                # Status
                if atual == 0:
                    status = "🚫 Zerado"
                    alertas += 1
                elif atual <= minimo:
                    status = "⚠️ Baixo"
                    alertas += 1
                elif atual <= minimo * 1.5:
                    status = "🟡 Atenção"
                else:
                    status = "✅ Normal"

                # Valor total
                preco_custo = produto.get('preco_custo', 0)
                valor_item = atual * preco_custo
                valor_total += valor_item

                self.tree_estoque.insert('', 'end', values=(
                    produto.get('codigo', ''),
                    produto.get('nome', ''),
                    produto.get('categoria', ''),
                    atual,
                    minimo,
                    disponivel,
                    reservado,
                    status,
                    f"R$ {valor_item:.2f}".replace('.', ',')
                ))

                total_produtos += 1

            # Atualizar rodapé
            self.label_total_produtos.config(text=f"Total de Produtos: {total_produtos}")
            self.label_valor_total.config(text=f"Valor Total: R$ {valor_total:,.2f}".replace('.', ','))
            self.label_alertas.config(text=f"Alertas: {alertas}")

        self.root.after(0, update_ui)

    def carregar_movimentacoes(self):
        """Carregar movimentações"""
        def update_ui():
            # Mock data
            movimentacoes = [
                {
                    "data": "29/10/2025 14:30",
                    "tipo": "Entrada",
                    "produto": "Forro PVC Branco 20cm",
                    "quantidade": 50,
                    "valor_unit": 15.50,
                    "valor_total": 775.00,
                    "usuario": "admin",
                    "observacoes": "Compra fornecedor ABC"
                },
                {
                    "data": "29/10/2025 10:15",
                    "tipo": "Saída",
                    "produto": "Divisória Eucatex 2,70m",
                    "quantidade": 3,
                    "valor_unit": 180.00,
                    "valor_total": 540.00,
                    "usuario": "admin",
                    "observacoes": "Venda OS #001"
                },
                {
                    "data": "28/10/2025 16:45",
                    "tipo": "Ajuste",
                    "produto": "Perfil Alumínio 30mm",
                    "quantidade": -2,
                    "valor_unit": 12.00,
                    "valor_total": -24.00,
                    "usuario": "admin",
                    "observacoes": "Inventário - avaria"
                }
            ]

            # Limpar árvore
            for item in self.tree_movimentacoes.get_children():
                self.tree_movimentacoes.delete(item)

            for mov in movimentacoes:
                self.tree_movimentacoes.insert('', 'end', values=(
                    mov['data'],
                    mov['tipo'],
                    mov['produto'],
                    mov['quantidade'],
                    f"R$ {mov['valor_unit']:.2f}".replace('.', ','),
                    f"R$ {mov['valor_total']:.2f}".replace('.', ','),
                    mov['usuario'],
                    mov['observacoes']
                ))

        self.root.after(0, update_ui)

    def carregar_alertas(self):
        """Carregar alertas de estoque"""
        def update_ui():
            # Limpar árvores
            for item in self.tree_baixo.get_children():
                self.tree_baixo.delete(item)

            for item in self.tree_zerado.get_children():
                self.tree_zerado.delete(item)

            for produto in self.produtos_data:
                atual = produto.get('estoque_atual', 0)
                minimo = produto.get('estoque_minimo', 0)
                preco = produto.get('preco_venda', 0)

                # Produtos com estoque baixo
                if 0 < atual <= minimo:
                    diferenca = minimo - atual
                    valor_risco = diferenca * preco

                    self.tree_baixo.insert('', 'end', values=(
                        produto.get('nome', ''),
                        atual,
                        minimo,
                        diferenca,
                        f"R$ {valor_risco:.2f}".replace('.', ',')
                    ))

                # Produtos zerados
                elif atual == 0:
                    self.tree_zerado.insert('', 'end', values=(
                        produto.get('nome', ''),
                        produto.get('categoria', ''),
                        "28/10/2025",  # Mock
                        "1 dia"  # Mock
                    ))

        self.root.after(0, update_ui)

    # =======================================
    # MÉTODOS DE AÇÃO
    # =======================================

    def nova_movimentacao(self):
        """Abrir janela de nova movimentação"""
        MovimentacaoDialog(self.root, self.produtos_data, self.on_movimentacao_criada)

    def on_movimentacao_criada(self, dados_movimentacao):
        """Callback quando movimentação é criada"""
        messagebox.showinfo("Sucesso", "Movimentação registrada com sucesso!")
        self.carregar_estoque()
        self.carregar_movimentacoes()
        self.carregar_alertas()

    def ver_detalhes_produto(self, event=None):
        """Ver detalhes do produto selecionado"""
        if self.item_selecionado:
            codigo = self.item_selecionado[0]
            messagebox.showinfo(
                "Detalhes do Produto",
                f"Código: {codigo}\n\nDetalhes completos serão implementados!"
            )

    def exportar_estoque(self):
        """Exportar dados do estoque"""
        messagebox.showinfo(
            "Exportar",
            "Funcionalidade de exportação será implementada!\n\nFormatos disponíveis:\n- Excel\n- PDF\n- CSV"
        )

    def novo_inventario(self):
        """Iniciar novo inventário completo"""
        resultado = messagebox.askyesno(
            "Novo Inventário",
            "Deseja iniciar um novo inventário completo?\n\nIsso irá bloquear o sistema para contagem."
        )
        if resultado:
            messagebox.showinfo("Inventário", "Funcionalidade será implementada!")

    def importar_inventario(self):
        """Importar dados de inventário"""
        messagebox.showinfo(
            "Importar",
            "Funcionalidade de importação será implementada!\n\nFormatos suportados:\n- Excel\n- CSV"
        )

    def aplicar_ajuste_inventario(self):
        """Aplicar ajuste de inventário"""
        if not self.combo_produto_inv.get():
            messagebox.showerror("Erro", "Selecione um produto!")
            return

        if not self.var_nova_qty.get():
            messagebox.showerror("Erro", "Informe a nova quantidade!")
            return

        try:
            nova_qty = int(self.var_nova_qty.get())
            atual_qty = int(self.var_qty_atual.get())
            diferenca = nova_qty - atual_qty

            resultado = messagebox.askyesno(
                "Confirmar Ajuste",
                f"Produto: {self.combo_produto_inv.get()}\n"
                f"Quantidade atual: {atual_qty}\n"
                f"Nova quantidade: {nova_qty}\n"
                f"Diferença: {diferenca:+d}\n\n"
                "Confirma o ajuste?"
            )

            if resultado:
                messagebox.showinfo("Sucesso", "Ajuste aplicado com sucesso!")
                self.limpar_formulario_inventario()
                self.carregar_estoque()
                self.carregar_movimentacoes()

        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro!")

    def limpar_formulario_inventario(self):
        """Limpar formulário de inventário"""
        self.combo_produto_inv.set("")
        self.var_qty_atual.set("0")
        self.var_nova_qty.set("")
        self.combo_motivo.set("")
        self.text_obs_inv.delete("1.0", tk.END)

    def on_closing(self):
        """Tratar fechamento da janela"""
        if messagebox.askyesno("Fechar", "Deseja fechar o controle de estoque?"):
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
            except Exception as e:
                print(f"Warning: Erro ao destruir janela de estoque: {e}")

# =======================================
# DIALOG DE MOVIMENTAÇÃO
# =======================================

class MovimentacaoDialog:
    """Dialog para criar nova movimentação"""

    def __init__(self, parent, produtos_data, callback):
        self.parent = parent
        self.produtos_data = produtos_data
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nova Movimentação")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Criar widgets do dialog"""

        # Título
        title = tk.Label(
            self.dialog,
            text="➕ Nova Movimentação de Estoque",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title.pack(pady=20)

        # Formulário
        form_frame = tk.Frame(self.dialog, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20)

        # Tipo de movimentação
        tk.Label(
            form_frame,
            text="Tipo de Movimentação:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))

        self.combo_tipo = ttk.Combobox(
            form_frame,
            values=["Entrada", "Saída", "Ajuste", "Transferência"],
            state="readonly",
            font=('Arial', 10)
        )
        self.combo_tipo.pack(fill='x', pady=(0, 15))

        # Produto
        tk.Label(
            form_frame,
            text="Produto:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))

        produtos_nomes = [p['nome'] for p in self.produtos_data]
        self.combo_produto = ttk.Combobox(
            form_frame,
            values=produtos_nomes,
            state="readonly",
            font=('Arial', 10)
        )
        self.combo_produto.pack(fill='x', pady=(0, 15))

        # Quantidade
        tk.Label(
            form_frame,
            text="Quantidade:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))

        self.var_quantidade = tk.StringVar()
        entry_qty = tk.Entry(
            form_frame,
            textvariable=self.var_quantidade,
            font=('Arial', 10)
        )
        entry_qty.pack(fill='x', pady=(0, 15))

        # Valor unitário
        tk.Label(
            form_frame,
            text="Valor Unitário (R$):",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))

        self.var_valor = tk.StringVar()
        entry_valor = tk.Entry(
            form_frame,
            textvariable=self.var_valor,
            font=('Arial', 10)
        )
        entry_valor.pack(fill='x', pady=(0, 15))

        # Observações
        tk.Label(
            form_frame,
            text="Observações:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))

        self.text_obs = tk.Text(
            form_frame,
            font=('Arial', 9),
            height=4,
            wrap='word'
        )
        self.text_obs.pack(fill='x', pady=(0, 20))

        # Botões
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.pack(fill='x')

        btn_salvar = tk.Button(
            btn_frame,
            text="💾 Salvar",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=5,
            border=0,
            command=self.salvar_movimentacao
        )
        btn_salvar.pack(side='left', padx=(0, 10))

        btn_cancelar = tk.Button(
            btn_frame,
            text="❌ Cancelar",
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=5,
            border=0,
            command=self.dialog.destroy
        )
        btn_cancelar.pack(side='left')

    def salvar_movimentacao(self):
        """Salvar movimentação"""

        # Validações básicas
        if not self.combo_tipo.get():
            messagebox.showerror("Erro", "Selecione o tipo de movimentação!")
            return

        if not self.combo_produto.get():
            messagebox.showerror("Erro", "Selecione o produto!")
            return

        if not self.var_quantidade.get():
            messagebox.showerror("Erro", "Informe a quantidade!")
            return

        try:
            quantidade = int(self.var_quantidade.get())
            valor = float(self.var_valor.get().replace(',', '.')) if self.var_valor.get() else 0

            dados = {
                "tipo": self.combo_tipo.get(),
                "produto": self.combo_produto.get(),
                "quantidade": quantidade,
                "valor_unitario": valor,
                "observacoes": self.text_obs.get("1.0", tk.END).strip()
            }

            self.callback(dados)
            self.dialog.destroy()

        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos!")

# =======================================
# FUNÇÃO PRINCIPAL
# =======================================

def main():
    """Teste da interface de estoque"""

    user_data = {
        "access_token": "mock_token",
        "user": {
            "username": "admin",
            "nome_completo": "Administrador"
        }
    }

    app = EstoqueWindow(user_data)
    app.run()

if __name__ == "__main__":
    main()