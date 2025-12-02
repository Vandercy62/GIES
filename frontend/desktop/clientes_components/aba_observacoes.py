"""
SISTEMA ERP PRIMOTEX - ABA 4: OBSERVAÇÕES E HISTÓRICO
======================================================

Componente de observações, preferências e histórico do cliente.
Última aba do wizard com campos de texto livre e listas.

CAMPOS (4 total):
1. observacoes - Text (notas gerais)
2. preferencias - Text (preferências de atendimento)
3. historico_interacoes - Listview com histórico JSON
4. anexos - Listview com anexos JSON

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 100
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, List
import json
from datetime import datetime
import os


class AbaObservacoes:
    """
    Aba de observações e histórico do cliente.
    Campos de texto livre e listas de interações/anexos.
    """
    
    # Cores
    COR_FUNDO = "#f8f9fa"
    
    # Fontes
    FONTE_SECAO = ("Segoe UI", 16, "bold")
    FONTE_LABEL = ("Segoe UI", 14, "bold")
    FONTE_CAMPO = ("Segoe UI", 14)
    FONTE_TEXTO = ("Segoe UI", 13)
    
    def __init__(self, parent_frame: tk.Frame):
        """Inicializa aba de observações"""
        self.parent = parent_frame
        
        # Dados
        self.historico_interacoes: List[Dict] = []
        self.anexos: List[Dict] = []
        
        # Criar interface
        self._criar_interface()
        
    def _criar_interface(self):
        """Cria interface da aba"""
        # Canvas com scroll
        canvas = tk.Canvas(self.parent, bg=self.COR_FUNDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=self.COR_FUNDO)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame de conteúdo
        main_frame = tk.Frame(scrollable_frame, bg=self.COR_FUNDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Criar seções
        self._criar_secao_observacoes(main_frame)
        self._criar_secao_preferencias(main_frame)
        self._criar_secao_historico(main_frame)
        self._criar_secao_anexos(main_frame)
        
    def _criar_secao_observacoes(self, parent: tk.Frame):
        """Cria seção de observações"""
        frame = tk.LabelFrame(
            parent,
            text=" OBSERVAÇÕES GERAIS ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Label
        tk.Label(
            frame,
            text="Notas e informações relevantes sobre o cliente:",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Text com scroll
        text_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_observacoes = tk.Text(
            text_frame,
            font=self.FONTE_TEXTO,
            height=6,
            wrap=tk.WORD,
            yscrollcommand=scroll.set
        )
        self.text_observacoes.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.text_observacoes.yview)
        
    def _criar_secao_preferencias(self, parent: tk.Frame):
        """Cria seção de preferências"""
        frame = tk.LabelFrame(
            parent,
            text=" PREFERÊNCIAS DE ATENDIMENTO ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Label
        tk.Label(
            frame,
            text="Horários preferenciais, formas de contato, restrições, etc:",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Text com scroll
        text_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_preferencias = tk.Text(
            text_frame,
            font=self.FONTE_TEXTO,
            height=6,
            wrap=tk.WORD,
            yscrollcommand=scroll.set
        )
        self.text_preferencias.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.text_preferencias.yview)
        
    def _criar_secao_historico(self, parent: tk.Frame):
        """Cria seção de histórico de interações"""
        frame = tk.LabelFrame(
            parent,
            text=" HISTÓRICO DE INTERAÇÕES ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botões
        btn_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(
            btn_frame,
            text="➕ NOVA INTERAÇÃO",
            font=("Segoe UI", 12, "bold"),
            bg="#28a745",
            fg="white",
            cursor="hand2",
            command=self._adicionar_interacao
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="🗑️ REMOVER",
            font=("Segoe UI", 12, "bold"),
            bg="#dc3545",
            fg="white",
            cursor="hand2",
            command=self._remover_interacao
        ).pack(side=tk.LEFT)
        
        # Listbox
        list_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox_historico = tk.Listbox(
            list_frame,
            font=self.FONTE_CAMPO,
            height=5,
            yscrollcommand=scroll.set
        )
        self.listbox_historico.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.listbox_historico.yview)
        
    def _criar_secao_anexos(self, parent: tk.Frame):
        """Cria seção de anexos"""
        frame = tk.LabelFrame(
            parent,
            text=" ANEXOS E DOCUMENTOS ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botões
        btn_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(
            btn_frame,
            text="📎 ADICIONAR ANEXO",
            font=("Segoe UI", 12, "bold"),
            bg="#007bff",
            fg="white",
            cursor="hand2",
            command=self._adicionar_anexo
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="🗑️ REMOVER",
            font=("Segoe UI", 12, "bold"),
            bg="#dc3545",
            fg="white",
            cursor="hand2",
            command=self._remover_anexo
        ).pack(side=tk.LEFT)
        
        # Listbox
        list_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox_anexos = tk.Listbox(
            list_frame,
            font=self.FONTE_CAMPO,
            height=5,
            yscrollcommand=scroll.set
        )
        self.listbox_anexos.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.listbox_anexos.yview)
        
    def _adicionar_interacao(self):
        """Adiciona nova interação ao histórico"""
        # Dialog simples
        dialog = tk.Toplevel(self.parent)
        dialog.title("Nova Interação")
        dialog.geometry("500x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Frame
        frame = tk.Frame(dialog, bg=self.COR_FUNDO, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Tipo
        tk.Label(frame, text="Tipo:", font=self.FONTE_LABEL, bg=self.COR_FUNDO).pack(anchor=tk.W)
        var_tipo = tk.StringVar(value="Ligação")
        combo_tipo = ttk.Combobox(
            frame,
            textvariable=var_tipo,
            state="readonly",
            values=["Ligação", "Email", "WhatsApp", "Visita", "Reunião", "Outros"]
        )
        combo_tipo.pack(fill=tk.X, pady=(5, 15))
        
        # Descrição
        tk.Label(frame, text="Descrição:", font=self.FONTE_LABEL, bg=self.COR_FUNDO).pack(anchor=tk.W)
        text_desc = tk.Text(frame, height=6, wrap=tk.WORD)
        text_desc.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
        
        # Botão salvar
        def salvar():
            tipo = var_tipo.get()
            descricao = text_desc.get("1.0", tk.END).strip()
            
            if not descricao:
                messagebox.showwarning("Atenção", "Informe a descrição", parent=dialog)
                return
            
            # Adicionar
            interacao = {
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "tipo": tipo,
                "descricao": descricao
            }
            self.historico_interacoes.append(interacao)
            
            # Atualizar listbox
            self.listbox_historico.insert(
                tk.END,
                f"[{interacao['data']}] {interacao['tipo']}: {interacao['descricao'][:50]}..."
            )
            
            dialog.destroy()
        
        tk.Button(
            frame,
            text="💾 SALVAR",
            font=("Segoe UI", 12, "bold"),
            bg="#28a745",
            fg="white",
            command=salvar
        ).pack()
        
    def _remover_interacao(self):
        """Remove interação selecionada"""
        selecionado = self.listbox_historico.curselection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma interação", parent=self.parent)
            return
        
        # Remover
        idx = selecionado[0]
        self.listbox_historico.delete(idx)
        del self.historico_interacoes[idx]
        
    def _adicionar_anexo(self):
        """Adiciona novo anexo"""
        filepath = filedialog.askopenfilename(
            title="Selecionar Arquivo",
            filetypes=[("Todos os arquivos", "*.*")]
        )
        
        if not filepath:
            return
        
        # Adicionar
        anexo = {
            "nome": os.path.basename(filepath),
            "caminho": filepath,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "tamanho": os.path.getsize(filepath)
        }
        self.anexos.append(anexo)
        
        # Atualizar listbox
        tamanho_kb = anexo['tamanho'] / 1024
        self.listbox_anexos.insert(
            tk.END,
            f"📎 {anexo['nome']} ({tamanho_kb:.1f} KB) - {anexo['data']}"
        )
        
    def _remover_anexo(self):
        """Remove anexo selecionado"""
        selecionado = self.listbox_anexos.curselection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um anexo", parent=self.parent)
            return
        
        # Remover
        idx = selecionado[0]
        self.listbox_anexos.delete(idx)
        del self.anexos[idx]
        
    def obter_dados(self) -> Dict[str, Any]:
        """Retorna dados do formulário"""
        return {
            "observacoes": self.text_observacoes.get("1.0", tk.END).strip(),
            "preferencias": self.text_preferencias.get("1.0", tk.END).strip(),
            "historico_interacoes": json.dumps(self.historico_interacoes, ensure_ascii=False),
            "anexos": json.dumps(self.anexos, ensure_ascii=False)
        }
        
    def preencher_dados(self, dados: Dict[str, Any]):
        """Preenche formulário com dados"""
        # Observações
        self.text_observacoes.delete("1.0", tk.END)
        self.text_observacoes.insert("1.0", dados.get("observacoes", ""))
        
        # Preferências
        self.text_preferencias.delete("1.0", tk.END)
        self.text_preferencias.insert("1.0", dados.get("preferencias", ""))
        
        # Histórico
        try:
            historico_str = dados.get("historico_interacoes", "[]")
            self.historico_interacoes = json.loads(historico_str) if historico_str else []
            
            self.listbox_historico.delete(0, tk.END)
            for interacao in self.historico_interacoes:
                self.listbox_historico.insert(
                    tk.END,
                    f"[{interacao['data']}] {interacao['tipo']}: {interacao['descricao'][:50]}..."
                )
        except:
            pass
        
        # Anexos
        try:
            anexos_str = dados.get("anexos", "[]")
            self.anexos = json.loads(anexos_str) if anexos_str else []
            
            self.listbox_anexos.delete(0, tk.END)
            for anexo in self.anexos:
                tamanho_kb = anexo.get('tamanho', 0) / 1024
                self.listbox_anexos.insert(
                    tk.END,
                    f"📎 {anexo['nome']} ({tamanho_kb:.1f} KB) - {anexo['data']}"
                )
        except:
            pass
