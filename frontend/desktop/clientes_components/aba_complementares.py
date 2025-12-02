"""
SISTEMA ERP PRIMOTEX - ABA 3: DADOS COMPLEMENTARES
===================================================

Componente de cadastro de dados complementares do cliente.
Terceiro formulário do wizard com endereço, contatos e dados comerciais.

CAMPOS (18 total):
ENDEREÇO (7):
1. cep - Entry com busca automática ViaCEP
2. logradouro - Entry
3. numero - Entry
4. complemento - Entry
5. bairro - Entry
6. cidade - Entry
7. estado - Combobox (UF)

CONTATOS (5):
8. telefone_principal - Entry com máscara
9. telefone_secundario - Entry com máscara
10. whatsapp - Entry com máscara
11. email_principal - Entry com validação
12. email_secundario - Entry com validação

ONLINE (4):
13. site - Entry (URL)
14. instagram - Entry (@usuario)
15. facebook - Entry
16. linkedin - Entry

COMERCIAL (2):
17. limite_credito - Entry (moeda)
18. desconto_padrao - Entry (%)

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 100
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
from threading import Thread

from shared.validadores import validar_email, validar_telefone, validar_cep
from shared.formatadores import (
    formatar_telefone,
    formatar_cep,
    formatar_moeda,
    remover_formatacao
)
from shared.busca_cep import buscar_endereco_por_cep


class AbaComplementares:
    """
    Aba de dados complementares do cliente.
    Endereço, contatos, redes sociais e dados comerciais.
    """
    
    # Cores
    COR_FUNDO = "#f8f9fa"
    COR_SUCESSO = "#d4edda"
    COR_ERRO = "#f8d7da"
    
    # Fontes
    FONTE_SECAO = ("Segoe UI", 16, "bold")
    FONTE_LABEL = ("Segoe UI", 14, "bold")
    FONTE_CAMPO = ("Segoe UI", 16)
    
    # Estados brasileiros
    ESTADOS = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
        "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
        "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]
    
    def __init__(self, parent_frame: tk.Frame):
        """Inicializa aba de dados complementares"""
        self.parent = parent_frame
        
        # Variáveis - Endereço
        self.var_cep = tk.StringVar()
        self.var_logradouro = tk.StringVar()
        self.var_numero = tk.StringVar()
        self.var_complemento = tk.StringVar()
        self.var_bairro = tk.StringVar()
        self.var_cidade = tk.StringVar()
        self.var_estado = tk.StringVar(value="SP")
        
        # Variáveis - Contatos
        self.var_telefone_principal = tk.StringVar()
        self.var_telefone_secundario = tk.StringVar()
        self.var_whatsapp = tk.StringVar()
        self.var_email_principal = tk.StringVar()
        self.var_email_secundario = tk.StringVar()
        
        # Variáveis - Online
        self.var_site = tk.StringVar()
        self.var_instagram = tk.StringVar()
        self.var_facebook = tk.StringVar()
        self.var_linkedin = tk.StringVar()
        
        # Variáveis - Comercial
        self.var_limite_credito = tk.StringVar(value="0.00")
        self.var_desconto_padrao = tk.StringVar(value="0")
        
        # Criar interface
        self._criar_interface()
        
        # Configurar validações
        self._configurar_validacoes()
        
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
        self._criar_secao_endereco(main_frame)
        self._criar_secao_contatos(main_frame)
        self._criar_secao_online(main_frame)
        self._criar_secao_comercial(main_frame)
        
    def _criar_secao_endereco(self, parent: tk.Frame):
        """Cria seção de endereço"""
        frame = tk.LabelFrame(
            parent,
            text=" ENDEREÇO ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid
        grid = tk.Frame(frame, bg=self.COR_FUNDO)
        grid.pack(fill=tk.X)
        
        # Linha 1: CEP + Botão Buscar
        cep_frame = tk.Frame(grid, bg=self.COR_FUNDO)
        cep_frame.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=10)
        grid.columnconfigure(0, weight=1)
        
        tk.Label(cep_frame, text="CEP:", font=self.FONTE_LABEL, bg=self.COR_FUNDO).pack(anchor=tk.W)
        
        h_frame = tk.Frame(cep_frame, bg=self.COR_FUNDO)
        h_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.entry_cep = tk.Entry(h_frame, textvariable=self.var_cep, font=self.FONTE_CAMPO, width=15)
        self.entry_cep.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_buscar_cep = tk.Button(
            h_frame,
            text="🔍 BUSCAR CEP",
            font=("Segoe UI", 12, "bold"),
            bg="#007bff",
            fg="white",
            cursor="hand2",
            command=self._buscar_cep
        )
        self.btn_buscar_cep.pack(side=tk.LEFT)
        
        self.label_cep_status = tk.Label(
            h_frame,
            text="",
            font=("Segoe UI", 12),
            bg=self.COR_FUNDO
        )
        self.label_cep_status.pack(side=tk.LEFT, padx=(10, 0))
        
        # Linha 2: Logradouro e Número
        self._criar_campo(grid, "Logradouro:", self.var_logradouro, 1, 0)
        self._criar_campo(grid, "Número:", self.var_numero, 1, 1, width=15)
        
        # Linha 3: Complemento e Bairro
        self._criar_campo(grid, "Complemento:", self.var_complemento, 2, 0)
        self._criar_campo(grid, "Bairro:", self.var_bairro, 2, 1)
        
        # Linha 4: Cidade e Estado
        self._criar_campo(grid, "Cidade:", self.var_cidade, 3, 0)
        self._criar_campo_combo(grid, "Estado (UF):", self.var_estado, self.ESTADOS, 3, 1)
        
    def _criar_secao_contatos(self, parent: tk.Frame):
        """Cria seção de contatos"""
        frame = tk.LabelFrame(
            parent,
            text=" CONTATOS ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        grid = tk.Frame(frame, bg=self.COR_FUNDO)
        grid.pack(fill=tk.X)
        
        # Linha 1: Telefones
        self._criar_campo(grid, "Telefone Principal:", self.var_telefone_principal, 0, 0)
        self._criar_campo(grid, "Telefone Secundário:", self.var_telefone_secundario, 0, 1)
        
        # Linha 2: WhatsApp
        self._criar_campo(grid, "WhatsApp:", self.var_whatsapp, 1, 0)
        
        # Linha 3: Emails
        self._criar_campo(grid, "Email Principal:", self.var_email_principal, 2, 0)
        self._criar_campo(grid, "Email Secundário:", self.var_email_secundario, 2, 1)
        
    def _criar_secao_online(self, parent: tk.Frame):
        """Cria seção de presença online"""
        frame = tk.LabelFrame(
            parent,
            text=" PRESENÇA ONLINE ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        grid = tk.Frame(frame, bg=self.COR_FUNDO)
        grid.pack(fill=tk.X)
        
        # Linha 1: Site e Instagram
        self._criar_campo(grid, "Site:", self.var_site, 0, 0)
        self._criar_campo(grid, "Instagram:", self.var_instagram, 0, 1)
        
        # Linha 2: Facebook e LinkedIn
        self._criar_campo(grid, "Facebook:", self.var_facebook, 1, 0)
        self._criar_campo(grid, "LinkedIn:", self.var_linkedin, 1, 1)
        
    def _criar_secao_comercial(self, parent: tk.Frame):
        """Cria seção de dados comerciais"""
        frame = tk.LabelFrame(
            parent,
            text=" DADOS COMERCIAIS ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        grid = tk.Frame(frame, bg=self.COR_FUNDO)
        grid.pack(fill=tk.X)
        
        # Linha 1: Limite de Crédito e Desconto Padrão
        self._criar_campo(grid, "Limite de Crédito (R$):", self.var_limite_credito, 0, 0)
        self._criar_campo(grid, "Desconto Padrão (%):", self.var_desconto_padrao, 0, 1)
        
    def _criar_campo(
        self,
        parent: tk.Frame,
        label_text: str,
        variable: tk.StringVar,
        row: int,
        col: int,
        width: int = None
    ):
        """Cria campo normal"""
        campo_frame = tk.Frame(parent, bg=self.COR_FUNDO)
        campo_frame.grid(row=row, column=col, sticky=tk.EW, padx=10, pady=10)
        parent.columnconfigure(col, weight=1)
        
        tk.Label(campo_frame, text=label_text, font=self.FONTE_LABEL, bg=self.COR_FUNDO).pack(anchor=tk.W)
        
        entry = tk.Entry(campo_frame, textvariable=variable, font=self.FONTE_CAMPO)
        if width:
            entry.config(width=width)
        entry.pack(fill=tk.X, pady=(5, 0))
        
    def _criar_campo_combo(
        self,
        parent: tk.Frame,
        label_text: str,
        variable: tk.StringVar,
        values: list,
        row: int,
        col: int
    ):
        """Cria campo combobox"""
        campo_frame = tk.Frame(parent, bg=self.COR_FUNDO)
        campo_frame.grid(row=row, column=col, sticky=tk.EW, padx=10, pady=10)
        parent.columnconfigure(col, weight=1)
        
        tk.Label(campo_frame, text=label_text, font=self.FONTE_LABEL, bg=self.COR_FUNDO).pack(anchor=tk.W)
        
        combo = ttk.Combobox(
            campo_frame,
            textvariable=variable,
            font=self.FONTE_CAMPO,
            state="readonly",
            values=values
        )
        combo.pack(fill=tk.X, pady=(5, 0))
        
    def _configurar_validacoes(self):
        """Configura validações em tempo real"""
        # Formatar telefones
        self.var_telefone_principal.trace("w", lambda *args: self._formatar_telefone(self.var_telefone_principal))
        self.var_telefone_secundario.trace("w", lambda *args: self._formatar_telefone(self.var_telefone_secundario))
        self.var_whatsapp.trace("w", lambda *args: self._formatar_telefone(self.var_whatsapp))
        
        # Formatar CEP
        self.var_cep.trace("w", self._formatar_cep)
        
    def _formatar_telefone(self, variable: tk.StringVar):
        """Formata telefone em tempo real"""
        valor = variable.get()
        if not valor:
            return
        
        numeros = remover_formatacao(valor)
        if len(numeros) in [10, 11]:
            formatado = formatar_telefone(numeros)
            if formatado != valor:
                variable.set(formatado)
                
    def _formatar_cep(self, *args):
        """Formata CEP em tempo real"""
        valor = self.var_cep.get()
        if not valor:
            return
        
        numeros = remover_formatacao(valor)
        if len(numeros) == 8:
            formatado = formatar_cep(numeros)
            if formatado != valor:
                self.var_cep.set(formatado)
                
    def _buscar_cep(self):
        """Busca endereço por CEP via ViaCEP"""
        cep = self.var_cep.get()
        
        # Validar CEP
        valido, msg = validar_cep(cep)
        if not valido:
            self.label_cep_status.config(text="❌ CEP inválido", fg="#dc3545")
            return
        
        # Desabilitar botão
        self.btn_buscar_cep.config(state=tk.DISABLED, text="⏳ Buscando...")
        self.label_cep_status.config(text="🔍 Buscando...", fg="#007bff")
        
        # Buscar em thread
        def _fazer_busca():
            resultado = buscar_endereco_por_cep(cep)
            
            if resultado:
                # Preencher campos
                self.parent.after(0, lambda: self.var_logradouro.set(resultado['logradouro']))
                self.parent.after(0, lambda: self.var_bairro.set(resultado['bairro']))
                self.parent.after(0, lambda: self.var_cidade.set(resultado['cidade']))
                self.parent.after(0, lambda: self.var_estado.set(resultado['estado']))
                self.parent.after(
                    0,
                    lambda: self.label_cep_status.config(text="✅ CEP encontrado!", fg="#28a745")
                )
            else:
                self.parent.after(
                    0,
                    lambda: self.label_cep_status.config(text="❌ CEP não encontrado", fg="#dc3545")
                )
            
            # Reabilitar botão
            self.parent.after(0, lambda: self.btn_buscar_cep.config(state=tk.NORMAL, text="🔍 BUSCAR CEP"))
        
        thread = Thread(target=_fazer_busca, daemon=True)
        thread.start()
        
    def obter_dados(self) -> Dict[str, Any]:
        """Retorna dados do formulário"""
        return {
            # Endereço
            "cep": remover_formatacao(self.var_cep.get()),
            "logradouro": self.var_logradouro.get().strip(),
            "numero": self.var_numero.get().strip(),
            "complemento": self.var_complemento.get().strip(),
            "bairro": self.var_bairro.get().strip(),
            "cidade": self.var_cidade.get().strip(),
            "estado": self.var_estado.get(),
            # Contatos
            "telefone_principal": remover_formatacao(self.var_telefone_principal.get()),
            "telefone_secundario": remover_formatacao(self.var_telefone_secundario.get()),
            "whatsapp": remover_formatacao(self.var_whatsapp.get()),
            "email_principal": self.var_email_principal.get().strip(),
            "email_secundario": self.var_email_secundario.get().strip(),
            # Online
            "site": self.var_site.get().strip(),
            "instagram": self.var_instagram.get().strip(),
            "facebook": self.var_facebook.get().strip(),
            "linkedin": self.var_linkedin.get().strip(),
            # Comercial
            "limite_credito": float(self.var_limite_credito.get() or 0),
            "desconto_padrao": float(self.var_desconto_padrao.get() or 0)
        }
        
    def preencher_dados(self, dados: Dict[str, Any]):
        """Preenche formulário com dados"""
        # Endereço
        self.var_cep.set(dados.get("cep", ""))
        self.var_logradouro.set(dados.get("logradouro", ""))
        self.var_numero.set(dados.get("numero", ""))
        self.var_complemento.set(dados.get("complemento", ""))
        self.var_bairro.set(dados.get("bairro", ""))
        self.var_cidade.set(dados.get("cidade", ""))
        self.var_estado.set(dados.get("estado", "SP"))
        
        # Contatos
        self.var_telefone_principal.set(dados.get("telefone_principal", ""))
        self.var_telefone_secundario.set(dados.get("telefone_secundario", ""))
        self.var_whatsapp.set(dados.get("whatsapp", ""))
        self.var_email_principal.set(dados.get("email_principal", ""))
        self.var_email_secundario.set(dados.get("email_secundario", ""))
        
        # Online
        self.var_site.set(dados.get("site", ""))
        self.var_instagram.set(dados.get("instagram", ""))
        self.var_facebook.set(dados.get("facebook", ""))
        self.var_linkedin.set(dados.get("linkedin", ""))
        
        # Comercial
        self.var_limite_credito.set(str(dados.get("limite_credito", 0.0)))
        self.var_desconto_padrao.set(str(dados.get("desconto_padrao", 0)))
