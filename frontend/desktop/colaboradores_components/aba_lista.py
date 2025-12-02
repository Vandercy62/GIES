"""
COMPONENTE: ABA LISTA DE COLABORADORES
======================================

TreeView com lista completa de colaboradores, busca e filtros.

Funcionalidades:
- TreeView com colunas: ID, Nome, CPF, Cargo, Departamento, Status
- Busca em tempo real por nome ou CPF
- Filtros por status (Ativo, Inativo, Férias, etc.)
- Ações: Novo, Editar, Excluir
- Double-click para editar

Autor: GitHub Copilot
Data: 17/11/2025 - FASE 103 TAREFA 2
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, Any, List
import threading
import requests

from frontend.desktop.auth_middleware import create_auth_header


# Constantes
_FONTE_FAMILIA = "Segoe UI"
API_BASE_URL = "http://127.0.0.1:8002"


class AbaLista(tk.Frame):
    """Componente de lista de colaboradores"""

    def __init__(
        self,
        parent,
        on_novo: Optional[Callable] = None,
        on_editar: Optional[Callable[[int], None]] = None,
        on_excluir: Optional[Callable[[int], None]] = None
    ):
        super().__init__(parent, bg="#f8f9fa")
        
        self.on_novo = on_novo
        self.on_editar = on_editar
        self.on_excluir = on_excluir
        
        self.colaboradores_data: List[Dict[str, Any]] = []
        self.filtro_status = "TODOS"
        
        self._criar_interface()
        self._carregar_dados()

    def _criar_interface(self):
        """Cria interface da aba"""
        
        # Barra de busca e filtros
        barra_frame = tk.Frame(self, bg="#f8f9fa")
        barra_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Busca
        tk.Label(
            barra_frame,
            text="🔍 Buscar:",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa"
        ).pack(side=tk.LEFT, padx=5)
        
        self.entry_busca = tk.Entry(
            barra_frame,
            font=(_FONTE_FAMILIA, 14),
            width=30
        )
        self.entry_busca.pack(side=tk.LEFT, padx=5)
        self.entry_busca.bind('<KeyRelease>', lambda e: self._filtrar())
        
        # Filtro Status
        tk.Label(
            barra_frame,
            text="Status:",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa"
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.combo_status = ttk.Combobox(
            barra_frame,
            values=[
                "TODOS",
                "ATIVO",
                "FERIAS",
                "AFASTADO",
                "INATIVO",
                "DEMITIDO"
            ],
            state="readonly",
            font=(_FONTE_FAMILIA, 12),
            width=15
        )
        self.combo_status.set("TODOS")
        self.combo_status.pack(side=tk.LEFT, padx=5)
        self.combo_status.bind('<<ComboboxSelected>>', lambda e: self._filtrar())
        
        # Botão atualizar
        btn_atualizar = tk.Button(
            barra_frame,
            text="🔄 Atualizar",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#17a2b8",
            fg="white",
            command=self._carregar_dados,
            cursor="hand2"
        )
        btn_atualizar.pack(side=tk.RIGHT, padx=5)
        
        # TreeView
        tree_frame = tk.Frame(self, bg="#f8f9fa")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # TreeView
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("id", "nome", "cpf", "cargo", "depto", "status"),
            show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            height=15
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Colunas
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome Completo")
        self.tree.heading("cpf", text="CPF")
        self.tree.heading("cargo", text="Cargo")
        self.tree.heading("depto", text="Departamento")
        self.tree.heading("status", text="Status")
        
        self.tree.column("id", width=60, anchor=tk.CENTER)
        self.tree.column("nome", width=300)
        self.tree.column("cpf", width=150, anchor=tk.CENTER)
        self.tree.column("cargo", width=200)
        self.tree.column("depto", width=200)
        self.tree.column("status", width=120, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Double-click para editar
        self.tree.bind('<Double-1>', self._on_double_click)
        
        # Botões de ação
        botoes_frame = tk.Frame(self, bg="#f8f9fa")
        botoes_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_novo = tk.Button(
            botoes_frame,
            text="➕ Novo Colaborador",
            font=(_FONTE_FAMILIA, 14, "bold"),
            bg="#28a745",
            fg="white",
            width=20,
            height=2,
            command=self._on_novo_click,
            cursor="hand2"
        )
        btn_novo.pack(side=tk.LEFT, padx=5)
        
        btn_editar = tk.Button(
            botoes_frame,
            text="✏️ Editar",
            font=(_FONTE_FAMILIA, 14, "bold"),
            bg="#007bff",
            fg="white",
            width=15,
            height=2,
            command=self._on_editar_click,
            cursor="hand2"
        )
        btn_editar.pack(side=tk.LEFT, padx=5)
        
        btn_excluir = tk.Button(
            botoes_frame,
            text="🗑️ Excluir",
            font=(_FONTE_FAMILIA, 14, "bold"),
            bg="#dc3545",
            fg="white",
            width=15,
            height=2,
            command=self._on_excluir_click,
            cursor="hand2"
        )
        btn_excluir.pack(side=tk.LEFT, padx=5)
        
        # Contador
        self.lbl_contador = tk.Label(
            botoes_frame,
            text="Total: 0 colaboradores",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa",
            fg="#6c757d"
        )
        self.lbl_contador.pack(side=tk.RIGHT, padx=10)

    def _carregar_dados(self):
        """Carrega colaboradores do backend"""
        def carregar_thread():
            try:
                headers = create_auth_header()
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/colaboradores/",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.colaboradores_data = data.get('items', [])
                    self.after(0, self._atualizar_tree)
                    
            except (ConnectionError, TimeoutError, ValueError) as e:
                print(f"Erro ao carregar colaboradores: {e}")
        
        thread = threading.Thread(target=carregar_thread, daemon=True)
        thread.start()

    def _atualizar_tree(self):
        """Atualiza TreeView"""
        # Limpar
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar dados filtrados
        dados_filtrados = self._aplicar_filtros()
        
        for colab in dados_filtrados:
            self.tree.insert("", tk.END, values=(
                colab.get('id', ''),
                colab.get('nome', ''),
                colab.get('cpf', ''),
                colab.get('cargo_nome', '-'),
                colab.get('departamento_nome', '-'),
                colab.get('status', 'ATIVO')
            ))
        
        # Atualizar contador
        total = len(dados_filtrados)
        self.lbl_contador.config(
            text=f"Total: {total} colaborador{'es' if total != 1 else ''}"
        )

    def _aplicar_filtros(self) -> List[Dict[str, Any]]:
        """Aplica filtros de busca e status"""
        dados = self.colaboradores_data
        
        # Filtro de busca
        termo_busca = self.entry_busca.get().strip().lower()
        if termo_busca:
            dados = [
                c for c in dados
                if termo_busca in c.get('nome', '').lower()
                or termo_busca in c.get('cpf', '').replace('.', '').replace('-', '')
            ]
        
        # Filtro de status
        status = self.combo_status.get()
        if status != "TODOS":
            dados = [c for c in dados if c.get('status') == status]
        
        return dados

    def _filtrar(self):
        """Aplica filtros e atualiza tree"""
        self._atualizar_tree()

    def _on_novo_click(self):
        """Callback para novo colaborador"""
        if self.on_novo:
            self.on_novo()

    def _on_editar_click(self):
        """Callback para editar colaborador"""
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning(
                "Seleção",
                "Selecione um colaborador para editar!",
                parent=self
            )
            return
        
        item = self.tree.item(selecao[0])
        colab_id = int(item['values'][0])
        
        if self.on_editar:
            self.on_editar(colab_id)

    def _on_excluir_click(self):
        """Callback para excluir colaborador"""
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning(
                "Seleção",
                "Selecione um colaborador para excluir!",
                parent=self
            )
            return
        
        item = self.tree.item(selecao[0])
        colab_id = int(item['values'][0])
        nome = item['values'][1]
        
        confirma = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o colaborador:\n\n{nome}?",
            parent=self
        )
        
        if confirma and self.on_excluir:
            self.on_excluir(colab_id)

    def _on_double_click(self, event):
        """Double-click para editar"""
        self._on_editar_click()

    def refresh(self):
        """Atualiza lista"""
        self._carregar_dados()
