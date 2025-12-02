"""
SISTEMA ERP PRIMOTEX - ABA 1: LISTA DE CLIENTES
================================================

Componente de listagem de clientes com busca e filtros.
Permite visualizar, buscar, filtrar e gerenciar todos os clientes.

FUNCIONALIDADES:
- Treeview com clientes cadastrados
- Busca em tempo real por nome/CPF/CNPJ/email
- Filtros: Status, Tipo (PF/PJ), Origem
- Botões: NOVO | EDITAR | EXCLUIR
- Double-click abre Aba 2 para edição

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 100
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional
import requests
from threading import Thread

from frontend.desktop.auth_middleware import create_auth_header


class AbaLista:
    """
    Aba de listagem de clientes com busca e filtros.
    """
    
    # URLs da API
    API_BASE = "http://127.0.0.1:8002/api/v1"
    
    # Cores do sistema
    COR_FUNDO = "#f8f9fa"
    COR_BOTAO_NOVO = "#28a745"
    COR_BOTAO_EDITAR = "#007bff"
    COR_BOTAO_EXCLUIR = "#dc3545"
    
    # Fontes
    FONTE_LABEL = ("Segoe UI", 14, "bold")
    FONTE_CAMPO = ("Segoe UI", 14)
    FONTE_BOTAO = ("Segoe UI", 13, "bold")
    
    def __init__(
        self,
        parent_frame: tk.Frame,
        on_novo_click,
        on_editar_click,
        token: str
    ):
        """
        Inicializa aba de lista.
        
        Args:
            parent_frame: Frame pai (aba do notebook)
            on_novo_click: Callback para criar novo cliente
            on_editar_click: Callback para editar cliente (recebe cliente_id)
            token: Token JWT para API
        """
        self.parent = parent_frame
        self.on_novo = on_novo_click
        self.on_editar = on_editar_click
        self.token = token
        
        # Dados
        self.clientes: List[Dict[str, Any]] = []
        self.clientes_filtrados: List[Dict[str, Any]] = []
        
        # Criar interface
        self._criar_interface()
        
        # Carregar clientes
        self._carregar_clientes()
        
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
            "Digite nome, CPF, CNPJ ou email..."
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
        
        # Filtro Tipo
        label_tipo = tk.Label(
            frame,
            text="Tipo:",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO
        )
        label_tipo.pack(side=tk.LEFT, padx=(0, 5))
        
        self.combo_tipo = ttk.Combobox(
            frame,
            font=self.FONTE_CAMPO,
            state="readonly",
            width=15,
            values=["Todos", "Pessoa Física", "Pessoa Jurídica"]
        )
        self.combo_tipo.set("Todos")
        self.combo_tipo.pack(side=tk.LEFT, padx=(0, 20))
        self.combo_tipo.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())
        
        # Filtro Origem
        label_origem = tk.Label(
            frame,
            text="Origem:",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO
        )
        label_origem.pack(side=tk.LEFT, padx=(0, 5))
        
        self.combo_origem = ttk.Combobox(
            frame,
            font=self.FONTE_CAMPO,
            state="readonly",
            width=18,
            values=[
                "Todos", "Site", "Telefone", "WhatsApp", "Email",
                "Indicação", "Redes Sociais", "Outros"
            ]
        )
        self.combo_origem.set("Todos")
        self.combo_origem.pack(side=tk.LEFT)
        self.combo_origem.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())
        
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
            columns=("id", "nome", "cpf_cnpj", "telefone", "email", "status"),
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
        self.tree.heading("nome", text="NOME")
        self.tree.heading("cpf_cnpj", text="CPF/CNPJ")
        self.tree.heading("telefone", text="TELEFONE")
        self.tree.heading("email", text="EMAIL")
        self.tree.heading("status", text="STATUS")
        
        # Larguras das colunas
        self.tree.column("id", width=80, anchor=tk.CENTER)
        self.tree.column("nome", width=300, anchor=tk.W)
        self.tree.column("cpf_cnpj", width=150, anchor=tk.CENTER)
        self.tree.column("telefone", width=150, anchor=tk.CENTER)
        self.tree.column("email", width=250, anchor=tk.W)
        self.tree.column("status", width=100, anchor=tk.CENTER)
        
        # Tags para cores
        self.tree.tag_configure("Ativo", foreground="#28a745")
        self.tree.tag_configure("Inativo", foreground="#6c757d")
        self.tree.tag_configure("Suspenso", foreground="#ffc107")
        self.tree.tag_configure("Bloqueado", foreground="#dc3545")
        
        # Double-click para editar
        self.tree.bind("<Double-1>", self._ao_double_click)
        
    def _criar_secao_botoes(self, parent: tk.Frame):
        """Cria seção de botões de ação"""
        frame = tk.Frame(parent, bg=self.COR_FUNDO)
        frame.pack(fill=tk.X)
        
        # Botão NOVO
        btn_novo = tk.Button(
            frame,
            text="➕ NOVO CLIENTE",
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
            text="0 clientes",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        )
        self.label_contagem.pack(side=tk.RIGHT)
        
    def _carregar_clientes(self):
        """Carrega clientes da API em thread separada"""
        def _fazer_requisicao():
            try:
                url = f"{self.API_BASE}/clientes"
                headers = create_auth_header()
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.clientes = response.json()
                    self.clientes_filtrados = self.clientes.copy()
                    self.parent.after(0, self._atualizar_treeview)
                else:
                    self.parent.after(
                        0,
                        lambda: messagebox.showerror(
                            "Erro",
                            f"Erro ao carregar clientes: {response.status_code}",
                            parent=self.parent
                        )
                    )
            except requests.exceptions.Timeout:
                self.parent.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro",
                        "Timeout ao carregar clientes.\n"
                        "Verifique se o servidor está rodando.",
                        parent=self.parent
                    )
                )
            except Exception as e:
                self.parent.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro",
                        f"Erro inesperado: {str(e)}",
                        parent=self.parent
                    )
                )
        
        # Executar em thread
        thread = Thread(target=_fazer_requisicao, daemon=True)
        thread.start()
        
    def _atualizar_treeview(self):
        """Atualiza treeview com clientes filtrados"""
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar clientes filtrados
        for cliente in self.clientes_filtrados:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    cliente.get("id", ""),
                    cliente.get("nome", ""),
                    cliente.get("cpf_cnpj", ""),
                    cliente.get("telefone_principal", ""),
                    cliente.get("email_principal", ""),
                    cliente.get("status", "")
                ),
                tags=(cliente.get("status", ""),)
            )
        
        # Atualizar contagem
        total = len(self.clientes_filtrados)
        texto = f"{total} cliente" if total == 1 else f"{total} clientes"
        self.label_contagem.config(text=texto)
        
    def _aplicar_filtros(self):
        """Aplica filtros de busca e combos"""
        # Obter valores dos filtros
        busca = self.entry_busca.get().lower()
        status = self.combo_status.get()
        tipo = self.combo_tipo.get()
        origem = self.combo_origem.get()
        
        # Filtrar clientes
        self.clientes_filtrados = []
        
        for cliente in self.clientes:
            # Busca textual
            if busca and busca not in "digite nome, cpf, cnpj ou email...":
                nome = cliente.get("nome", "").lower()
                cpf_cnpj = cliente.get("cpf_cnpj", "").lower()
                email = cliente.get("email_principal", "").lower()
                
                if busca not in nome and busca not in cpf_cnpj and busca not in email:
                    continue
            
            # Filtro Status
            if status != "Todos":
                if cliente.get("status") != status:
                    continue
            
            # Filtro Tipo
            if tipo != "Todos":
                tipo_cliente = "Pessoa Física" if cliente.get("tipo_pessoa") == "PF" else "Pessoa Jurídica"
                if tipo != tipo_cliente:
                    continue
            
            # Filtro Origem
            if origem != "Todos":
                if cliente.get("origem") != origem:
                    continue
            
            # Passou em todos os filtros
            self.clientes_filtrados.append(cliente)
        
        # Atualizar treeview
        self._atualizar_treeview()
        
    def _ao_double_click(self, event):
        """Executado ao dar double-click em um item"""
        self._editar_selecionado()
        
    def _editar_selecionado(self):
        """Edita cliente selecionado"""
        selecionado = self.tree.selection()
        
        if not selecionado:
            messagebox.showwarning(
                "Atenção",
                "Selecione um cliente para editar",
                parent=self.parent
            )
            return
        
        # Obter ID do cliente
        valores = self.tree.item(selecionado[0], "values")
        cliente_id = int(valores[0])
        
        # Chamar callback
        self.on_editar(cliente_id)
        
    def _excluir_selecionado(self):
        """Exclui cliente selecionado"""
        selecionado = self.tree.selection()
        
        if not selecionado:
            messagebox.showwarning(
                "Atenção",
                "Selecione um cliente para excluir",
                parent=self.parent
            )
            return
        
        # Obter dados do cliente
        valores = self.tree.item(selecionado[0], "values")
        cliente_id = int(valores[0])
        nome = valores[1]
        
        # Confirmar exclusão
        if not messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o cliente:\n\n"
            f"Código: {cliente_id}\n"
            f"Nome: {nome}\n\n"
            f"Esta ação não pode ser desfeita!",
            parent=self.parent
        ):
            return
        
        # Excluir via API
        def _fazer_exclusao():
            try:
                url = f"{self.API_BASE}/clientes/{cliente_id}"
                headers = create_auth_header()
                
                response = requests.delete(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.parent.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Sucesso",
                            "Cliente excluído com sucesso!",
                            parent=self.parent
                        )
                    )
                    self.parent.after(0, self._carregar_clientes)
                else:
                    self.parent.after(
                        0,
                        lambda: messagebox.showerror(
                            "Erro",
                            f"Erro ao excluir cliente: {response.status_code}",
                            parent=self.parent
                        )
                    )
            except Exception as e:
                self.parent.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro",
                        f"Erro inesperado: {str(e)}",
                        parent=self.parent
                    )
                )
        
        # Executar em thread
        thread = Thread(target=_fazer_exclusao, daemon=True)
        thread.start()
        
    def _set_placeholder(self, entry: tk.Entry, placeholder: str):
        """Define placeholder para Entry"""
        entry.insert(0, placeholder)
        entry.config(fg="#6c757d")
        
        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg="#000000")
        
        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg="#6c757d")
        
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
