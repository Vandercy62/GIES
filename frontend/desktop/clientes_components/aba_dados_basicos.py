"""
SISTEMA ERP PRIMOTEX - ABA 2: DADOS BÁSICOS
============================================

Componente de cadastro de dados básicos do cliente.
Primeiro formulário do wizard com campos essenciais.

CAMPOS (9 total):
1. tipo_pessoa - Radio (PF/PJ)
2. nome - Entry obrigatório
3. cpf_cnpj - Entry com validação
4. rg_ie - Entry opcional
5. data_nascimento_fundacao - Entry com máscara
6. status - Combobox
7. origem - Combobox
8. tipo_cliente - Combobox
9. foto_path - Upload de imagem

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 100
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional
from datetime import datetime
import os

from shared.validadores import (
    validar_cpf,
    validar_cnpj,
    validar_email
)
from shared.formatadores import (
    formatar_cpf,
    formatar_cnpj,
    remover_formatacao
)


class AbaDadosBasicos:
    """
    Aba de dados básicos do cliente.
    Primeira etapa do cadastro com informações essenciais.
    """
    
    # Cores
    COR_FUNDO = "#f8f9fa"
    COR_OBRIGATORIO = "#fff3cd"
    
    # Fontes
    FONTE_SECAO = ("Segoe UI", 16, "bold")
    FONTE_LABEL = ("Segoe UI", 14, "bold")
    FONTE_CAMPO = ("Segoe UI", 16)
    
    def __init__(self, parent_frame: tk.Frame):
        """
        Inicializa aba de dados básicos.
        
        Args:
            parent_frame: Frame pai (aba do notebook)
        """
        self.parent = parent_frame
        
        # Variáveis dos campos
        self.var_tipo_pessoa = tk.StringVar(value="PF")
        self.var_nome = tk.StringVar()
        self.var_cpf_cnpj = tk.StringVar()
        self.var_rg_ie = tk.StringVar()
        self.var_data_nasc_fund = tk.StringVar()
        self.var_status = tk.StringVar(value="Ativo")
        self.var_origem = tk.StringVar(value="Site")
        self.var_tipo_cliente = tk.StringVar(value="Varejo")
        self.foto_path = ""
        
        # Criar interface
        self._criar_interface()
        
        # Configurar validações
        self._configurar_validacoes()
        
    def _criar_interface(self):
        """Cria interface da aba"""
        # Frame principal com scroll
        canvas = tk.Canvas(self.parent, bg=self.COR_FUNDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            self.parent,
            orient=tk.VERTICAL,
            command=canvas.yview
        )
        
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
        self._criar_secao_tipo_pessoa(main_frame)
        self._criar_secao_identificacao(main_frame)
        self._criar_secao_classificacao(main_frame)
        self._criar_secao_foto(main_frame)
        
    def _criar_secao_tipo_pessoa(self, parent: tk.Frame):
        """Cria seção de tipo de pessoa"""
        frame = tk.LabelFrame(
            parent,
            text=" TIPO DE PESSOA ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Radio buttons
        rb_pf = tk.Radiobutton(
            frame,
            text="👤 Pessoa Física (CPF)",
            variable=self.var_tipo_pessoa,
            value="PF",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO,
            cursor="hand2",
            command=self._ao_mudar_tipo_pessoa
        )
        rb_pf.pack(side=tk.LEFT, padx=(0, 30))
        
        rb_pj = tk.Radiobutton(
            frame,
            text="🏢 Pessoa Jurídica (CNPJ)",
            variable=self.var_tipo_pessoa,
            value="PJ",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO,
            cursor="hand2",
            command=self._ao_mudar_tipo_pessoa
        )
        rb_pj.pack(side=tk.LEFT)
        
    def _criar_secao_identificacao(self, parent: tk.Frame):
        """Cria seção de identificação"""
        frame = tk.LabelFrame(
            parent,
            text=" IDENTIFICAÇÃO ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid de campos
        grid_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        grid_frame.pack(fill=tk.X)
        
        # Linha 1: Nome
        self._criar_campo_obrigatorio(
            grid_frame,
            "Nome Completo / Razão Social:",
            self.var_nome,
            row=0,
            colspan=2
        )
        
        # Linha 2: CPF/CNPJ e RG/IE
        self.label_cpf_cnpj = self._criar_campo_obrigatorio(
            grid_frame,
            "CPF:",
            self.var_cpf_cnpj,
            row=1,
            col=0
        )
        
        self.label_rg_ie = self._criar_campo(
            grid_frame,
            "RG:",
            self.var_rg_ie,
            row=1,
            col=1
        )
        
        # Linha 3: Data Nascimento/Fundação
        self.label_data = self._criar_campo(
            grid_frame,
            "Data de Nascimento:",
            self.var_data_nasc_fund,
            row=2,
            col=0
        )
        
    def _criar_secao_classificacao(self, parent: tk.Frame):
        """Cria seção de classificação"""
        frame = tk.LabelFrame(
            parent,
            text=" CLASSIFICAÇÃO ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid de campos
        grid_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        grid_frame.pack(fill=tk.X)
        
        # Linha 1: Status e Origem
        self._criar_campo_combo(
            grid_frame,
            "Status:",
            self.var_status,
            ["Ativo", "Inativo", "Suspenso", "Bloqueado"],
            row=0,
            col=0
        )
        
        self._criar_campo_combo(
            grid_frame,
            "Origem:",
            self.var_origem,
            ["Site", "Telefone", "WhatsApp", "Email", "Indicação",
             "Redes Sociais", "Outros"],
            row=0,
            col=1
        )
        
        # Linha 2: Tipo Cliente
        self._criar_campo_combo(
            grid_frame,
            "Tipo de Cliente:",
            self.var_tipo_cliente,
            ["Varejo", "Atacado", "Revendedor", "Especial", "Outros"],
            row=1,
            col=0
        )
        
    def _criar_secao_foto(self, parent: tk.Frame):
        """Cria seção de foto"""
        frame = tk.LabelFrame(
            parent,
            text=" FOTO / LOGOTIPO ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Frame horizontal
        h_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        h_frame.pack(fill=tk.X)
        
        # Label do arquivo
        self.label_foto = tk.Label(
            h_frame,
            text="Nenhuma foto selecionada",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        )
        self.label_foto.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botão upload
        btn_upload = tk.Button(
            h_frame,
            text="📁 ESCOLHER ARQUIVO",
            font=("Segoe UI", 14, "bold"),
            bg="#007bff",
            fg="white",
            width=20,
            height=2,
            cursor="hand2",
            command=self._selecionar_foto
        )
        btn_upload.pack(side=tk.RIGHT, padx=(10, 0))
        
    def _criar_campo_obrigatorio(
        self,
        parent: tk.Frame,
        label_text: str,
        variable: tk.StringVar,
        row: int,
        col: int = 0,
        colspan: int = 1
    ) -> tk.Label:
        """Cria campo obrigatório com fundo amarelo"""
        # Frame do campo
        campo_frame = tk.Frame(parent, bg=self.COR_FUNDO)
        campo_frame.grid(
            row=row,
            column=col,
            columnspan=colspan,
            sticky=tk.EW,
            padx=10,
            pady=10
        )
        parent.columnconfigure(col, weight=1)
        
        # Label
        label = tk.Label(
            campo_frame,
            text=label_text + " *",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        label.pack(anchor=tk.W)
        
        # Entry
        entry = tk.Entry(
            campo_frame,
            textvariable=variable,
            font=self.FONTE_CAMPO,
            bg=self.COR_OBRIGATORIO
        )
        entry.pack(fill=tk.X, pady=(5, 0))
        
        return label
        
    def _criar_campo(
        self,
        parent: tk.Frame,
        label_text: str,
        variable: tk.StringVar,
        row: int,
        col: int = 0
    ) -> tk.Label:
        """Cria campo normal"""
        # Frame do campo
        campo_frame = tk.Frame(parent, bg=self.COR_FUNDO)
        campo_frame.grid(row=row, column=col, sticky=tk.EW, padx=10, pady=10)
        parent.columnconfigure(col, weight=1)
        
        # Label
        label = tk.Label(
            campo_frame,
            text=label_text,
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        label.pack(anchor=tk.W)
        
        # Entry
        entry = tk.Entry(
            campo_frame,
            textvariable=variable,
            font=self.FONTE_CAMPO
        )
        entry.pack(fill=tk.X, pady=(5, 0))
        
        return label
        
    def _criar_campo_combo(
        self,
        parent: tk.Frame,
        label_text: str,
        variable: tk.StringVar,
        values: list,
        row: int,
        col: int = 0
    ):
        """Cria campo combobox"""
        # Frame do campo
        campo_frame = tk.Frame(parent, bg=self.COR_FUNDO)
        campo_frame.grid(row=row, column=col, sticky=tk.EW, padx=10, pady=10)
        parent.columnconfigure(col, weight=1)
        
        # Label
        label = tk.Label(
            campo_frame,
            text=label_text,
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        label.pack(anchor=tk.W)
        
        # Combobox
        combo = ttk.Combobox(
            campo_frame,
            textvariable=variable,
            font=self.FONTE_CAMPO,
            state="readonly",
            values=values
        )
        combo.pack(fill=tk.X, pady=(5, 0))
        
    def _ao_mudar_tipo_pessoa(self):
        """Executado ao mudar tipo de pessoa"""
        tipo = self.var_tipo_pessoa.get()
        
        # Atualizar labels
        if tipo == "PF":
            self.label_cpf_cnpj.config(text="CPF: *")
            self.label_rg_ie.config(text="RG:")
            self.label_data.config(text="Data de Nascimento:")
        else:
            self.label_cpf_cnpj.config(text="CNPJ: *")
            self.label_rg_ie.config(text="Inscrição Estadual:")
            self.label_data.config(text="Data de Fundação:")
        
        # Limpar campo CPF/CNPJ
        self.var_cpf_cnpj.set("")
        
    def _configurar_validacoes(self):
        """Configura validações em tempo real"""
        # Validação de CPF/CNPJ ao sair do campo
        self.var_cpf_cnpj.trace("w", self._formatar_cpf_cnpj)
        
    def _formatar_cpf_cnpj(self, *args):
        """Formata CPF/CNPJ em tempo real"""
        valor = self.var_cpf_cnpj.get()
        if not valor:
            return
        
        # Remove formatação
        numeros = remover_formatacao(valor)
        
        # Formata de acordo com tipo
        if self.var_tipo_pessoa.get() == "PF":
            if len(numeros) == 11:
                formatado = formatar_cpf(numeros)
                if formatado != valor:
                    self.var_cpf_cnpj.set(formatado)
        else:
            if len(numeros) == 14:
                formatado = formatar_cnpj(numeros)
                if formatado != valor:
                    self.var_cpf_cnpj.set(formatado)
                    
    def _selecionar_foto(self):
        """Abre dialog para selecionar foto"""
        filepath = filedialog.askopenfilename(
            title="Selecionar Foto/Logotipo",
            filetypes=[
                ("Imagens", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if filepath:
            self.foto_path = filepath
            nome_arquivo = os.path.basename(filepath)
            self.label_foto.config(
                text=f"📷 {nome_arquivo}",
                fg="#28a745"
            )
            
    def validar_dados(self) -> tuple[bool, str]:
        """
        Valida todos os dados do formulário.
        
        Returns:
            (True/False, mensagem de erro)
        """
        # Nome obrigatório
        if not self.var_nome.get().strip():
            return False, "Nome é obrigatório"
        
        # CPF/CNPJ obrigatório e válido
        cpf_cnpj = self.var_cpf_cnpj.get()
        if not cpf_cnpj.strip():
            return False, "CPF/CNPJ é obrigatório"
        
        # Validar de acordo com tipo
        if self.var_tipo_pessoa.get() == "PF":
            valido, msg = validar_cpf(cpf_cnpj)
            if not valido:
                return False, f"CPF inválido: {msg}"
        else:
            valido, msg = validar_cnpj(cpf_cnpj)
            if not valido:
                return False, f"CNPJ inválido: {msg}"
        
        return True, ""
        
    def obter_dados(self) -> Dict[str, Any]:
        """
        Retorna dados do formulário.
        
        Returns:
            Dict com todos os campos
        """
        return {
            "tipo_pessoa": self.var_tipo_pessoa.get(),
            "nome": self.var_nome.get().strip(),
            "cpf_cnpj": remover_formatacao(self.var_cpf_cnpj.get()),
            "rg_ie": self.var_rg_ie.get().strip(),
            "data_nascimento_fundacao": self.var_data_nasc_fund.get().strip(),
            "status": self.var_status.get(),
            "origem": self.var_origem.get(),
            "tipo_cliente": self.var_tipo_cliente.get(),
            "foto_path": self.foto_path
        }
        
    def preencher_dados(self, dados: Dict[str, Any]):
        """
        Preenche formulário com dados.
        
        Args:
            dados: Dict com dados do cliente
        """
        self.var_tipo_pessoa.set(dados.get("tipo_pessoa", "PF"))
        self._ao_mudar_tipo_pessoa()
        
        self.var_nome.set(dados.get("nome", ""))
        self.var_cpf_cnpj.set(dados.get("cpf_cnpj", ""))
        self.var_rg_ie.set(dados.get("rg_ie", ""))
        self.var_data_nasc_fund.set(dados.get("data_nascimento_fundacao", ""))
        self.var_status.set(dados.get("status", "Ativo"))
        self.var_origem.set(dados.get("origem", "Site"))
        self.var_tipo_cliente.set(dados.get("tipo_cliente", "Varejo"))
        
        if dados.get("foto_path"):
            self.foto_path = dados["foto_path"]
            self.label_foto.config(
                text=f"📷 {os.path.basename(self.foto_path)}",
                fg="#28a745"
            )
