"""
SISTEMA ERP PRIMOTEX - ABA 1: LISTA DE FORNECEDORES
====================================================

Componente de listagem de fornecedores com busca e filtros.
Permite visualizar, buscar, filtrar e gerenciar todos os fornecedores.

FUNCIONALIDADES:
- Treeview com fornecedores cadastrados (6 colunas)
- Busca em tempo real por razão social/CNPJ/fantasia/email
- Filtros: Status, Categoria, Avaliação (estrelas)
- Botões: NOVO | EDITAR | EXCLUIR (50px altura)
- Double-click abre Aba 2 para edição
- Campo avaliação mostra estrelas ⭐ (1-5)

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 101
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional, Callable
import requests
from threading import Thread
import logging

from frontend.desktop.auth_middleware import create_auth_header

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AbaLista:
    """
    Aba de listagem de fornecedores com busca e filtros.
    """
    
    # URLs da API
    API_BASE = "http://127.0.0.1:8002/api/v1"
    
    # Cores do sistema
    COR_FUNDO = "#f8f9fa"
    COR_BOTAO_NOVO = "#28a745"
    COR_BOTAO_EDITAR = "#007bff"
    COR_BOTAO_EXCLUIR = "#dc3545"
    COR_DESTAQUE = "#e9ecef"
    
    # Fontes (otimizadas para idosos)
    FONTE_LABEL = ("Segoe UI", 14, "bold")
    FONTE_CAMPO = ("Segoe UI", 14)
    FONTE_BOTAO = ("Segoe UI", 13, "bold")
    FONTE_TREE = ("Segoe UI", 12)
    
    # Mapeamento de avaliação para estrelas
    ESTRELAS_MAP = {
        None: "",
        0: "",
        1: "⭐",
        2: "⭐⭐",
        3: "⭐⭐⭐",
        4: "⭐⭐⭐⭐",
        5: "⭐⭐⭐⭐⭐"
    }
    
    def __init__(
        self,
        parent_frame: tk.Frame,
        on_novo_click: Callable,
        on_editar_click: Callable[[int], None],
        token: str
    ):
        """
        Inicializa aba de lista.
        
        Args:
            parent_frame: Frame pai (aba do notebook)
            on_novo_click: Callback para criar novo fornecedor
            on_editar_click: Callback para editar fornecedor (recebe fornecedor_id)
            token: Token JWT para API
        """
        self.parent = parent_frame
        self.on_novo = on_novo_click
        self.on_editar = on_editar_click
        self.token = token
        
        # Dados
        self.fornecedores: List[Dict[str, Any]] = []
        self.fornecedores_filtrados: List[Dict[str, Any]] = []
        
        # Criar interface
        self._criar_interface()
        
        # Carregar fornecedores
        self._carregar_fornecedores()
        
        logger.info("AbaLista inicializada")
        
    def _criar_interface(self):
        """Cria interface da aba"""
        # Frame principal
        main_frame = tk.Frame(self.parent, bg=self.COR_FUNDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Criar seções
        self._criar_secao_busca(main_frame)
        self._criar_secao_filtros(main_frame)
        self._criar_secao_lista(main_frame)
        self._criar_secao_botoes(main_frame)
        
    def _criar_secao_busca(self, parent: tk.Frame):
        """Cria seção de busca"""
        frame = tk.Frame(parent, bg=self.COR_FUNDO)
        frame.pack(fill=tk.X, pady=(0, 15))
        
        # Label
        label = tk.Label(
            frame,
            text="🔍 BUSCAR:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Campo de busca
        self.entry_busca = tk.Entry(
            frame,
            font=self.FONTE_CAMPO,
            width=50
        )
        self.entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_busca.bind("<KeyRelease>", lambda e: self._aplicar_filtros())
        
        # Placeholder
        self._set_placeholder(
            self.entry_busca,
            "Digite razão social, CNPJ, nome fantasia ou email..."
        )
        
    def _criar_secao_filtros(self, parent: tk.Frame):
        """Cria seção de filtros"""
        frame = tk.Frame(parent, bg=self.COR_FUNDO)
        frame.pack(fill=tk.X, pady=(0, 15))
        
        # Filtro Status
        label_status = tk.Label(
            frame,
            text="Status:",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO
        )
        label_status.pack(side=tk.LEFT, padx=(0, 5))
        
        self.combo_status = ttk.Combobox(
            frame,
            font=self.FONTE_CAMPO,
            state="readonly",
            width=15,
            values=["Todos", "Ativo", "Inativo", "Suspenso", "Bloqueado"]
        )
        self.combo_status.set("Todos")
        self.combo_status.pack(side=tk.LEFT, padx=(0, 20))
        self.combo_status.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())
        
        # Filtro Categoria
        label_categoria = tk.Label(
            frame,
            text="Categoria:",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO
        )
        label_categoria.pack(side=tk.LEFT, padx=(0, 5))
        
        self.combo_categoria = ttk.Combobox(
            frame,
            font=self.FONTE_CAMPO,
            state="readonly",
            width=18,
            values=[
                "Todos",
                "Materiais",
                "Ferramentas",
                "Equipamentos",
                "Serviços",
                "Insumos",
                "Outros"
            ]
        )
        self.combo_categoria.set("Todos")
        self.combo_categoria.pack(side=tk.LEFT, padx=(0, 20))
        self.combo_categoria.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())
        
        # Filtro Avaliação
        label_avaliacao = tk.Label(
            frame,
            text="Avaliação:",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO
        )
        label_avaliacao.pack(side=tk.LEFT, padx=(0, 5))
        
        self.combo_avaliacao = ttk.Combobox(
            frame,
            font=self.FONTE_CAMPO,
            state="readonly",
            width=15,
            values=[
                "Todos",
                "⭐⭐⭐⭐⭐ (5)",
                "⭐⭐⭐⭐ (4+)",
                "⭐⭐⭐ (3+)",
                "⭐⭐ (2+)",
                "⭐ (1+)",
                "Sem avaliação"
            ]
        )
        self.combo_avaliacao.set("Todos")
        self.combo_avaliacao.pack(side=tk.LEFT)
        self.combo_avaliacao.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())
        
    def _criar_secao_lista(self, parent: tk.Frame):
        """Cria seção com treeview"""
        frame = tk.Frame(parent, bg=self.COR_FUNDO)
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        
        # Treeview
        self.tree = ttk.Treeview(
            frame,
            columns=("id", "razao_social", "cnpj", "categoria", "avaliacao", "status"),
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            height=15
        )
        
        # Configurar scrollbars
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Definir colunas
        self.tree.heading("id", text="CÓDIGO")
        self.tree.heading("razao_social", text="RAZÃO SOCIAL")
        self.tree.heading("cnpj", text="CNPJ")
        self.tree.heading("categoria", text="CATEGORIA")
        self.tree.heading("avaliacao", text="AVALIAÇÃO")
        self.tree.heading("status", text="STATUS")
        
        # Larguras das colunas
        self.tree.column("id", width=80, anchor=tk.CENTER)
        self.tree.column("razao_social", width=350, anchor=tk.W)
        self.tree.column("cnpj", width=150, anchor=tk.CENTER)
        self.tree.column("categoria", width=150, anchor=tk.CENTER)
        self.tree.column("avaliacao", width=150, anchor=tk.CENTER)
        self.tree.column("status", width=120, anchor=tk.CENTER)
        
        # Tags para cores de status
        self.tree.tag_configure("Ativo", foreground="#28a745")
        self.tree.tag_configure("Inativo", foreground="#6c757d")
        self.tree.tag_configure("Suspenso", foreground="#ffc107")
        self.tree.tag_configure("Bloqueado", foreground="#dc3545")
        
        # Estilo para fonte maior
        style = ttk.Style()
        style.configure("Treeview", font=self.FONTE_TREE, rowheight=30)
        style.configure("Treeview.Heading", font=self.FONTE_LABEL)
        
        # Double-click para editar
        self.tree.bind("<Double-1>", self._ao_double_click)
        
    def _criar_secao_botoes(self, parent: tk.Frame):
        """Cria seção de botões de ação"""
        frame = tk.Frame(parent, bg=self.COR_FUNDO)
        frame.pack(fill=tk.X)
        
        # Botão NOVO
        btn_novo = tk.Button(
            frame,
            text="➕ NOVO FORNECEDOR",
            font=self.FONTE_BOTAO,
            bg=self.COR_BOTAO_NOVO,
            fg="white",
            width=20,
            height=2,
            cursor="hand2",
            command=self.on_novo
        )
        btn_novo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão EDITAR
        btn_editar = tk.Button(
            frame,
            text="✏️ EDITAR",
            font=self.FONTE_BOTAO,
            bg=self.COR_BOTAO_EDITAR,
            fg="white",
            width=20,
            height=2,
            cursor="hand2",
            command=self._editar_selecionado
        )
        btn_editar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão EXCLUIR
        btn_excluir = tk.Button(
            frame,
            text="🗑️ EXCLUIR",
            font=self.FONTE_BOTAO,
            bg=self.COR_BOTAO_EXCLUIR,
            fg="white",
            width=20,
            height=2,
            cursor="hand2",
            command=self._excluir_selecionado
        )
        btn_excluir.pack(side=tk.LEFT)
        
        # Label de contagem (alinhado à direita)
        self.label_contagem = tk.Label(
            frame,
            text="0 fornecedores",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        )
        self.label_contagem.pack(side=tk.RIGHT)
        
    def _set_placeholder(self, entry: tk.Entry, placeholder: str):
        """
        Configura placeholder em Entry
        
        Args:
            entry: Widget Entry
            placeholder: Texto do placeholder
        """
        entry.insert(0, placeholder)
        entry.config(fg="#6c757d")
        
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg="#212529")
        
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg="#6c757d")
        
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        
    def _carregar_fornecedores(self):
        """Carrega fornecedores da API em thread separada"""
        def _fazer_requisicao():
            try:
                url = f"{self.API_BASE}/fornecedores"
                headers = create_auth_header()
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Pode retornar lista direta ou objeto com 'items'
                    if isinstance(data, list):
                        self.fornecedores = data
                    elif isinstance(data, dict) and 'items' in data:
                        self.fornecedores = data['items']
                    else:
                        self.fornecedores = []
                    
                    # Atualizar UI na thread principal
                    self.parent.after(0, self._popular_treeview)
                    
                    logger.info(f"{len(self.fornecedores)} fornecedores carregados")
                    
                else:
                    logger.error(f"Erro ao carregar fornecedores: HTTP {response.status_code}")
                    self.parent.after(
                        0,
                        lambda: messagebox.showerror(
                            "Erro",
                            f"Erro ao carregar fornecedores.\n\nHTTP {response.status_code}"
                        )
                    )
                    
            except requests.exceptions.ConnectionError:
                logger.error("Erro de conexão com API")
                self.parent.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro de Conexão",
                        "Não foi possível conectar à API.\n\n"
                        "Verifique se o backend está rodando na porta 8002."
                    )
                )
                
            except Exception as e:
                logger.exception(f"Erro ao carregar fornecedores: {e}")
                self.parent.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao carregar fornecedores:\n\n{str(e)}"
                    )
                )
        
        # Executar em thread separada
        thread = Thread(target=_fazer_requisicao, daemon=True)
        thread.start()
        
    def _popular_treeview(self):
        """Popula treeview com fornecedores"""
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Aplicar filtros
        self._aplicar_filtros()
        
    def _aplicar_filtros(self):
        """Aplica filtros de busca e combos"""
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obter valores dos filtros
        termo_busca = self.entry_busca.get().lower()
        if termo_busca == "digite razão social, cnpj, nome fantasia ou email...":
            termo_busca = ""
        
        filtro_status = self.combo_status.get()
        filtro_categoria = self.combo_categoria.get()
        filtro_avaliacao = self.combo_avaliacao.get()
        
        # Filtrar fornecedores
        self.fornecedores_filtrados = []
        
        for fornecedor in self.fornecedores:
            # Filtro de busca
            if termo_busca:
                razao = fornecedor.get('razao_social', '').lower()
                fantasia = fornecedor.get('nome_fantasia', '').lower()
                cnpj = fornecedor.get('cnpj_cpf', '').lower()
                email = fornecedor.get('email_principal', '').lower()
                
                if not (
                    termo_busca in razao or
                    termo_busca in fantasia or
                    termo_busca in cnpj or
                    termo_busca in email
                ):
                    continue
            
            # Filtro de status
            if filtro_status != "Todos":
                if fornecedor.get('status', '') != filtro_status:
                    continue
            
            # Filtro de categoria
            if filtro_categoria != "Todos":
                if fornecedor.get('categoria', '') != filtro_categoria:
                    continue
            
            # Filtro de avaliação
            if filtro_avaliacao != "Todos":
                avaliacao = fornecedor.get('avaliacao')
                
                if filtro_avaliacao == "Sem avaliação":
                    if avaliacao is not None and avaliacao > 0:
                        continue
                else:
                    # Extrair valor mínimo (ex: "⭐⭐⭐⭐ (4+)" -> 4)
                    if filtro_avaliacao == "⭐⭐⭐⭐⭐ (5)":
                        min_avaliacao = 5
                    elif "(4+)" in filtro_avaliacao:
                        min_avaliacao = 4
                    elif "(3+)" in filtro_avaliacao:
                        min_avaliacao = 3
                    elif "(2+)" in filtro_avaliacao:
                        min_avaliacao = 2
                    elif "(1+)" in filtro_avaliacao:
                        min_avaliacao = 1
                    else:
                        min_avaliacao = 0
                    
                    if not avaliacao or avaliacao < min_avaliacao:
                        continue
            
            # Fornecedor passou nos filtros
            self.fornecedores_filtrados.append(fornecedor)
        
        # Inserir no treeview
        for fornecedor in self.fornecedores_filtrados:
            fornecedor_id = fornecedor.get('id', '')
            razao_social = fornecedor.get('razao_social', '')
            cnpj = self._formatar_cnpj(fornecedor.get('cnpj_cpf', ''))
            categoria = fornecedor.get('categoria', '')
            avaliacao_valor = fornecedor.get('avaliacao')
            avaliacao_texto = self.ESTRELAS_MAP.get(avaliacao_valor, "")
            status = fornecedor.get('status', 'Ativo')
            
            # Inserir item
            self.tree.insert(
                "",
                tk.END,
                values=(
                    fornecedor_id,
                    razao_social,
                    cnpj,
                    categoria,
                    avaliacao_texto,
                    status
                ),
                tags=(status,)
            )
        
        # Atualizar contagem
        total = len(self.fornecedores_filtrados)
        texto = "fornecedor" if total == 1 else "fornecedores"
        self.label_contagem.config(text=f"{total} {texto}")
        
        logger.debug(f"Filtros aplicados: {total} fornecedores exibidos")
        
    def _formatar_cnpj(self, cnpj: str) -> str:
        """
        Formata CNPJ/CPF
        
        Args:
            cnpj: CNPJ/CPF sem formatação
            
        Returns:
            str: CNPJ/CPF formatado
        """
        if not cnpj:
            return ""
        
        # Remover não-dígitos
        numeros = ''.join(filter(str.isdigit, cnpj))
        
        if len(numeros) == 14:
            # CNPJ: 00.000.000/0000-00
            return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
        elif len(numeros) == 11:
            # CPF: 000.000.000-00
            return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        else:
            return cnpj
        
    def _ao_double_click(self, event):
        """Handler de double-click no treeview"""
        item = self.tree.selection()
        if not item:
            return
        
        # Obter ID do fornecedor
        valores = self.tree.item(item[0], 'values')
        fornecedor_id = int(valores[0])
        
        # Chamar callback de edição
        self.on_editar(fornecedor_id)
        
        logger.debug(f"Double-click: editar fornecedor ID {fornecedor_id}")
        
    def _editar_selecionado(self):
        """Edita fornecedor selecionado"""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning(
                "Aviso",
                "Selecione um fornecedor para editar."
            )
            return
        
        # Obter ID do fornecedor
        valores = self.tree.item(item[0], 'values')
        fornecedor_id = int(valores[0])
        
        # Chamar callback de edição
        self.on_editar(fornecedor_id)
        
        logger.info(f"Editar fornecedor ID {fornecedor_id}")
        
    def _excluir_selecionado(self):
        """Exclui fornecedor selecionado"""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning(
                "Aviso",
                "Selecione um fornecedor para excluir."
            )
            return
        
        # Obter dados do fornecedor
        valores = self.tree.item(item[0], 'values')
        fornecedor_id = int(valores[0])
        razao_social = valores[1]
        
        # Confirmar exclusão
        resposta = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o fornecedor?\n\n"
            f"Razão Social: {razao_social}\n"
            f"Código: {fornecedor_id}\n\n"
            f"Esta ação não pode ser desfeita.",
            icon='warning'
        )
        
        if not resposta:
            return
        
        # Excluir via API
        self._excluir_fornecedor_api(fornecedor_id)
        
    def _excluir_fornecedor_api(self, fornecedor_id: int):
        """
        Exclui fornecedor via API
        
        Args:
            fornecedor_id: ID do fornecedor
        """
        def _fazer_requisicao():
            try:
                url = f"{self.API_BASE}/fornecedores/{fornecedor_id}"
                headers = create_auth_header()
                
                response = requests.delete(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # Sucesso
                    self.parent.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Sucesso",
                            "Fornecedor excluído com sucesso!"
                        )
                    )
                    
                    # Recarregar lista
                    self.parent.after(0, self._carregar_fornecedores)
                    
                    logger.info(f"Fornecedor ID {fornecedor_id} excluído")
                    
                else:
                    logger.error(f"Erro ao excluir fornecedor: HTTP {response.status_code}")
                    self.parent.after(
                        0,
                        lambda: messagebox.showerror(
                            "Erro",
                            f"Erro ao excluir fornecedor.\n\nHTTP {response.status_code}"
                        )
                    )
                    
            except Exception as e:
                logger.exception(f"Erro ao excluir fornecedor: {e}")
                self.parent.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro",
                        f"Erro ao excluir fornecedor:\n\n{str(e)}"
                    )
                )
        
        # Executar em thread separada
        thread = Thread(target=_fazer_requisicao, daemon=True)
        thread.start()
        
    def recarregar(self):
        """Recarrega lista de fornecedores"""
        self._carregar_fornecedores()
        logger.info("Lista de fornecedores recarregada")
