"""
SISTEMA ERP PRIMOTEX - ABA 3: DADOS COMPLEMENTARES FORNECEDOR
==============================================================

Componente de cadastro de dados complementares do fornecedor.
Terceira aba do wizard com 4 painéis: Endereço, Contatos, Comercial e Bancário.

CAMPOS (21 total):
ENDEREÇO (8):
1. cep - Entry com busca ViaCEP
2. logradouro - Entry
3. numero - Entry
4. complemento - Entry
5. bairro - Entry
6. cidade - Entry
7. estado - Combobox (UF)
8. pais - Entry (default: Brasil)

CONTATOS (5):
9. contato_principal - Entry (nome)
10. telefone1 - Entry com máscara
11. telefone2 - Entry com máscara
12. email_principal - Entry com validação
13. email_secundario - Entry
14. site - Entry (URL)

DADOS COMERCIAIS (4):
15. condicoes_pagamento - Entry
16. prazo_entrega_padrao - Entry (dias)
17. valor_minimo_pedido - Entry (moeda)
18. desconto_padrao - Entry (%)

DADOS BANCÁRIOS (4):
19. banco - Entry
20. agencia - Entry
21. conta - Entry
22. chave_pix - Entry

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 101
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
from threading import Thread
import logging

from shared.validadores import validar_email, validar_telefone, validar_cep
from shared.formatadores import (
    formatar_telefone,
    formatar_cep,
    formatar_moeda,
    remover_formatacao
)
from shared.busca_cep import buscar_endereco_por_cep

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AbaComplementares:
    """
    Aba de dados complementares do fornecedor.
    4 painéis: Endereço, Contatos, Comercial e Bancário.
    """
    
    # Cores
    COR_FUNDO = "#f8f9fa"
    COR_SUCESSO = "#d4edda"
    COR_ERRO = "#f8d7da"
    COR_DESTAQUE = "#e9ecef"
    
    # Fontes
    FONTE_SECAO = ("Segoe UI", 16, "bold")
    FONTE_LABEL = ("Segoe UI", 14, "bold")
    FONTE_CAMPO = ("Segoe UI", 16)
    FONTE_HINT = ("Segoe UI", 11, "italic")
    
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
        self.var_pais = tk.StringVar(value="Brasil")
        
        # Variáveis - Contatos
        self.var_contato_principal = tk.StringVar()
        self.var_telefone1 = tk.StringVar()
        self.var_telefone2 = tk.StringVar()
        self.var_email_principal = tk.StringVar()
        self.var_email_secundario = tk.StringVar()
        self.var_site = tk.StringVar()
        
        # Variáveis - Comercial
        self.var_condicoes_pagamento = tk.StringVar()
        self.var_prazo_entrega = tk.StringVar()
        self.var_valor_minimo = tk.StringVar(value="0,00")
        self.var_desconto_padrao = tk.StringVar(value="0")
        
        # Variáveis - Bancário
        self.var_banco = tk.StringVar()
        self.var_agencia = tk.StringVar()
        self.var_conta = tk.StringVar()
        self.var_chave_pix = tk.StringVar()
        
        # Referências aos campos
        self.entry_cep: Optional[tk.Entry] = None
        self.btn_buscar_cep: Optional[tk.Button] = None
        self.label_cep_status: Optional[tk.Label] = None
        
        # Criar interface
        self._criar_interface()
        
        # Configurar validações
        self._configurar_validacoes()
        
        logger.info("AbaComplementares inicializada")
        
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
        
        # Criar 4 painéis
        self._criar_painel_endereco(main_frame)
        self._criar_painel_contatos(main_frame)
        self._criar_painel_comercial(main_frame)
        self._criar_painel_bancario(main_frame)
        
    def _criar_painel_endereco(self, parent: tk.Frame):
        """Cria painel de endereço com busca CEP"""
        frame = tk.LabelFrame(
            parent,
            text=" 🏠 ENDEREÇO DO FORNECEDOR ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid 2 colunas
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        # ROW 0: CEP + Botão Buscar
        label_cep = tk.Label(
            frame,
            text="CEP:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_cep.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        cep_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        cep_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        
        self.entry_cep = tk.Entry(
            cep_frame,
            textvariable=self.var_cep,
            font=self.FONTE_CAMPO,
            width=15
        )
        self.entry_cep.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_buscar_cep = tk.Button(
            cep_frame,
            text="🔍 BUSCAR CEP",
            font=("Segoe UI", 12, "bold"),
            bg="#007bff",
            fg="white",
            cursor="hand2",
            command=self._buscar_cep
        )
        self.btn_buscar_cep.pack(side=tk.LEFT, padx=(0, 10))
        
        self.label_cep_status = tk.Label(
            cep_frame,
            text="",
            font=("Segoe UI", 12),
            bg=self.COR_FUNDO
        )
        self.label_cep_status.pack(side=tk.LEFT)
        
        # ROW 2: Logradouro
        label_logr = tk.Label(
            frame,
            text="LOGRADOURO:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_logr.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        entry_logr = tk.Entry(
            frame,
            textvariable=self.var_logradouro,
            font=self.FONTE_CAMPO
        )
        entry_logr.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        
        # ROW 4: Número e Complemento
        label_num = tk.Label(
            frame,
            text="NÚMERO:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_num.grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        entry_num = tk.Entry(
            frame,
            textvariable=self.var_numero,
            font=self.FONTE_CAMPO,
            width=15
        )
        entry_num.grid(row=5, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 15))
        
        label_compl = tk.Label(
            frame,
            text="COMPLEMENTO:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_compl.grid(row=4, column=1, sticky=tk.W, pady=(0, 5))
        
        entry_compl = tk.Entry(
            frame,
            textvariable=self.var_complemento,
            font=self.FONTE_CAMPO
        )
        entry_compl.grid(row=5, column=1, sticky=tk.EW, pady=(0, 15))
        
        # ROW 6: Bairro e Cidade
        label_bairro = tk.Label(
            frame,
            text="BAIRRO:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_bairro.grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        
        entry_bairro = tk.Entry(
            frame,
            textvariable=self.var_bairro,
            font=self.FONTE_CAMPO
        )
        entry_bairro.grid(row=7, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 15))
        
        label_cidade = tk.Label(
            frame,
            text="CIDADE:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_cidade.grid(row=6, column=1, sticky=tk.W, pady=(0, 5))
        
        entry_cidade = tk.Entry(
            frame,
            textvariable=self.var_cidade,
            font=self.FONTE_CAMPO
        )
        entry_cidade.grid(row=7, column=1, sticky=tk.EW, pady=(0, 15))
        
        # ROW 8: Estado e País
        label_estado = tk.Label(
            frame,
            text="ESTADO (UF):",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_estado.grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        
        combo_estado = ttk.Combobox(
            frame,
            textvariable=self.var_estado,
            font=self.FONTE_CAMPO,
            state="readonly",
            values=self.ESTADOS,
            width=5
        )
        combo_estado.grid(row=9, column=0, sticky=tk.W, padx=(0, 10))
        
        label_pais = tk.Label(
            frame,
            text="PAÍS:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_pais.grid(row=8, column=1, sticky=tk.W, pady=(0, 5))
        
        entry_pais = tk.Entry(
            frame,
            textvariable=self.var_pais,
            font=self.FONTE_CAMPO
        )
        entry_pais.grid(row=9, column=1, sticky=tk.EW)
        
    def _criar_painel_contatos(self, parent: tk.Frame):
        """Cria painel de contatos"""
        frame = tk.LabelFrame(
            parent,
            text=" 📞 CONTATOS ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid 2 colunas
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        # ROW 0: Contato Principal
        label_contato = tk.Label(
            frame,
            text="CONTATO PRINCIPAL (Nome):",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_contato.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        entry_contato = tk.Entry(
            frame,
            textvariable=self.var_contato_principal,
            font=self.FONTE_CAMPO
        )
        entry_contato.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        
        # ROW 2: Telefones
        label_tel1 = tk.Label(
            frame,
            text="TELEFONE 1:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_tel1.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        entry_tel1 = tk.Entry(
            frame,
            textvariable=self.var_telefone1,
            font=self.FONTE_CAMPO
        )
        entry_tel1.grid(row=3, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 15))
        
        label_tel2 = tk.Label(
            frame,
            text="TELEFONE 2:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_tel2.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        entry_tel2 = tk.Entry(
            frame,
            textvariable=self.var_telefone2,
            font=self.FONTE_CAMPO
        )
        entry_tel2.grid(row=3, column=1, sticky=tk.EW, pady=(0, 15))
        
        # ROW 4: Emails
        label_email1 = tk.Label(
            frame,
            text="EMAIL PRINCIPAL:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_email1.grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        self.entry_email1 = tk.Entry(
            frame,
            textvariable=self.var_email_principal,
            font=self.FONTE_CAMPO
        )
        self.entry_email1.grid(row=5, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 15))
        
        label_email2 = tk.Label(
            frame,
            text="EMAIL SECUNDÁRIO:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_email2.grid(row=4, column=1, sticky=tk.W, pady=(0, 5))
        
        entry_email2 = tk.Entry(
            frame,
            textvariable=self.var_email_secundario,
            font=self.FONTE_CAMPO
        )
        entry_email2.grid(row=5, column=1, sticky=tk.EW, pady=(0, 15))
        
        # ROW 6: Site
        label_site = tk.Label(
            frame,
            text="SITE:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_site.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        entry_site = tk.Entry(
            frame,
            textvariable=self.var_site,
            font=self.FONTE_CAMPO
        )
        entry_site.grid(row=7, column=0, columnspan=2, sticky=tk.EW)
        
    def _criar_painel_comercial(self, parent: tk.Frame):
        """Cria painel de dados comerciais"""
        frame = tk.LabelFrame(
            parent,
            text=" 💰 DADOS COMERCIAIS ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid 2 colunas
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        # ROW 0: Condições de Pagamento
        label_cond = tk.Label(
            frame,
            text="CONDIÇÕES DE PAGAMENTO:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_cond.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        entry_cond = tk.Entry(
            frame,
            textvariable=self.var_condicoes_pagamento,
            font=self.FONTE_CAMPO
        )
        entry_cond.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 5))
        
        hint_cond = tk.Label(
            frame,
            text="Ex: 30/60/90 dias, À vista, Pagamento antecipado, etc.",
            font=self.FONTE_HINT,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        )
        hint_cond.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # ROW 3: Prazo Entrega e Valor Mínimo
        label_prazo = tk.Label(
            frame,
            text="PRAZO ENTREGA PADRÃO (dias):",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_prazo.grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        entry_prazo = tk.Entry(
            frame,
            textvariable=self.var_prazo_entrega,
            font=self.FONTE_CAMPO,
            width=15
        )
        entry_prazo.grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 15))
        
        label_valor_min = tk.Label(
            frame,
            text="VALOR MÍNIMO PEDIDO (R$):",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_valor_min.grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
        
        self.entry_valor_min = tk.Entry(
            frame,
            textvariable=self.var_valor_minimo,
            font=self.FONTE_CAMPO,
            width=20
        )
        self.entry_valor_min.grid(row=4, column=1, sticky=tk.W, pady=(0, 15))
        
        # ROW 5: Desconto Padrão
        label_desc = tk.Label(
            frame,
            text="DESCONTO PADRÃO (%):",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_desc.grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        entry_desc = tk.Entry(
            frame,
            textvariable=self.var_desconto_padrao,
            font=self.FONTE_CAMPO,
            width=10
        )
        entry_desc.grid(row=6, column=0, sticky=tk.W)
        
    def _criar_painel_bancario(self, parent: tk.Frame):
        """Cria painel de dados bancários"""
        frame = tk.LabelFrame(
            parent,
            text=" 🏦 DADOS BANCÁRIOS ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid 2 colunas
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        # ROW 0: Banco e Agência
        label_banco = tk.Label(
            frame,
            text="BANCO:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_banco.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        entry_banco = tk.Entry(
            frame,
            textvariable=self.var_banco,
            font=self.FONTE_CAMPO
        )
        entry_banco.grid(row=1, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 5))
        
        hint_banco = tk.Label(
            frame,
            text="Ex: Banco do Brasil (001), Itaú (341), Bradesco (237)",
            font=self.FONTE_HINT,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        )
        hint_banco.grid(row=2, column=0, sticky=tk.W, pady=(0, 15))
        
        label_agencia = tk.Label(
            frame,
            text="AGÊNCIA:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_agencia.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        entry_agencia = tk.Entry(
            frame,
            textvariable=self.var_agencia,
            font=self.FONTE_CAMPO
        )
        entry_agencia.grid(row=1, column=1, sticky=tk.EW, pady=(0, 15))
        
        # ROW 3: Conta
        label_conta = tk.Label(
            frame,
            text="CONTA (com dígito):",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_conta.grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        entry_conta = tk.Entry(
            frame,
            textvariable=self.var_conta,
            font=self.FONTE_CAMPO
        )
        entry_conta.grid(row=4, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 15))
        
        # ROW 3 col1: Chave PIX
        label_pix = tk.Label(
            frame,
            text="CHAVE PIX:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO
        )
        label_pix.grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
        
        entry_pix = tk.Entry(
            frame,
            textvariable=self.var_chave_pix,
            font=self.FONTE_CAMPO
        )
        entry_pix.grid(row=4, column=1, sticky=tk.EW, pady=(0, 5))
        
        hint_pix = tk.Label(
            frame,
            text="CPF/CNPJ, email, telefone ou chave aleatória",
            font=self.FONTE_HINT,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        )
        hint_pix.grid(row=5, column=1, sticky=tk.W)
        
    def _buscar_cep(self):
        """Busca endereço pelo CEP usando ViaCEP"""
        cep = self.var_cep.get()
        
        if not cep:
            messagebox.showwarning("Aviso", "Digite o CEP antes de buscar.")
            return
        
        # Limpar CEP
        cep_limpo = remover_formatacao(cep)
        
        # Validar formato
        if not validar_cep(cep_limpo):
            messagebox.showerror(
                "CEP Inválido",
                "O CEP deve ter 8 dígitos.\n\nFormato: XXXXX-XXX"
            )
            return
        
        # Desabilitar botão
        self.btn_buscar_cep.config(state=tk.DISABLED, text="BUSCANDO...")
        self.label_cep_status.config(text="⏳ Buscando...", fg="#ffc107")
        
        # Buscar em thread separada
        def _fazer_busca():
            try:
                resultado = buscar_endereco_por_cep(cep_limpo)
                
                if resultado['sucesso']:
                    # Atualizar campos na thread principal
                    self.parent.after(
                        0,
                        lambda: self._preencher_endereco(resultado['dados'])
                    )
                else:
                    # Mostrar erro
                    self.parent.after(
                        0,
                        lambda: self._mostrar_erro_cep(resultado['erro'])
                    )
            except Exception as e:
                logger.exception(f"Erro ao buscar CEP: {e}")
                self.parent.after(
                    0,
                    lambda: self._mostrar_erro_cep(str(e))
                )
            finally:
                # Reabilitar botão
                self.parent.after(
                    0,
                    lambda: self.btn_buscar_cep.config(
                        state=tk.NORMAL,
                        text="🔍 BUSCAR CEP"
                    )
                )
        
        thread = Thread(target=_fazer_busca, daemon=True)
        thread.start()
        
    def _preencher_endereco(self, dados: Dict[str, str]):
        """Preenche campos de endereço com dados do CEP"""
        self.var_logradouro.set(dados.get('logradouro', ''))
        self.var_bairro.set(dados.get('bairro', ''))
        self.var_cidade.set(dados.get('localidade', ''))
        self.var_estado.set(dados.get('uf', ''))
        
        # Formatar CEP
        self.var_cep.set(formatar_cep(dados.get('cep', '')))
        
        # Status de sucesso
        self.label_cep_status.config(
            text="✅ CEP encontrado!",
            fg="#28a745"
        )
        
        # Focar no número
        self.entry_cep.master.master.focus()
        
        logger.info(f"CEP encontrado: {dados.get('localidade', '')}/{dados.get('uf', '')}")
        
    def _mostrar_erro_cep(self, erro: str):
        """Mostra erro na busca de CEP"""
        self.label_cep_status.config(
            text=f"❌ {erro}",
            fg="#dc3545"
        )
        
        messagebox.showerror("Erro ao Buscar CEP", erro)
        
    def _configurar_validacoes(self):
        """Configura validações em tempo real"""
        # Validar email ao perder foco
        if hasattr(self, 'entry_email1'):
            self.entry_email1.bind("<FocusOut>", self._validar_email_principal)
        
        # Formatar valor mínimo como moeda
        if hasattr(self, 'entry_valor_min'):
            self.entry_valor_min.bind("<FocusOut>", self._formatar_valor_minimo)
        
    def _validar_email_principal(self, event=None):
        """Valida email principal"""
        email = self.var_email_principal.get()
        
        if not email:
            return  # Email vazio é permitido
        
        if not validar_email(email):
            messagebox.showerror(
                "Email Inválido",
                "O email informado não é válido.\n\n"
                "Formato esperado: usuario@dominio.com"
            )
            self.entry_email1.focus()
            
    def _formatar_valor_minimo(self, event=None):
        """Formata valor mínimo como moeda"""
        valor = self.var_valor_minimo.get()
        
        if valor:
            try:
                # Remover formatação
                valor_limpo = valor.replace('.', '').replace(',', '.')
                valor_float = float(valor_limpo)
                
                # Formatar como moeda brasileira
                self.var_valor_minimo.set(f"{valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            except ValueError:
                pass
    
    def obter_dados(self) -> Dict[str, Any]:
        """
        Obtém dados do formulário
        
        Returns:
            dict: Dicionário com dados complementares
        """
        # Processar valor mínimo
        valor_min_str = self.var_valor_minimo.get().replace('.', '').replace(',', '.')
        try:
            valor_min = float(valor_min_str)
        except ValueError:
            valor_min = 0.0
        
        # Processar desconto
        try:
            desconto = float(self.var_desconto_padrao.get())
        except ValueError:
            desconto = 0.0
        
        # Processar prazo entrega
        try:
            prazo = int(self.var_prazo_entrega.get()) if self.var_prazo_entrega.get() else None
        except ValueError:
            prazo = None
        
        dados = {
            # Endereço
            'cep': remover_formatacao(self.var_cep.get()) or None,
            'logradouro': self.var_logradouro.get().strip() or None,
            'numero': self.var_numero.get().strip() or None,
            'complemento': self.var_complemento.get().strip() or None,
            'bairro': self.var_bairro.get().strip() or None,
            'cidade': self.var_cidade.get().strip() or None,
            'estado': self.var_estado.get() or None,
            'pais': self.var_pais.get().strip() or None,
            
            # Contatos
            'contato_principal': self.var_contato_principal.get().strip() or None,
            'telefone1': remover_formatacao(self.var_telefone1.get()) or None,
            'telefone2': remover_formatacao(self.var_telefone2.get()) or None,
            'email_principal': self.var_email_principal.get().strip() or None,
            'email_secundario': self.var_email_secundario.get().strip() or None,
            'site': self.var_site.get().strip() or None,
            
            # Comercial
            'condicoes_pagamento': self.var_condicoes_pagamento.get().strip() or None,
            'prazo_entrega_padrao': prazo,
            'valor_minimo_pedido': valor_min,
            'desconto_padrao': desconto,
            
            # Bancário
            'banco': self.var_banco.get().strip() or None,
            'agencia': self.var_agencia.get().strip() or None,
            'conta': self.var_conta.get().strip() or None,
            'chave_pix': self.var_chave_pix.get().strip() or None
        }
        
        return dados
    
    def carregar_dados(self, dados: Dict[str, Any]):
        """
        Carrega dados no formulário
        
        Args:
            dados: Dicionário com dados do fornecedor
        """
        # Endereço
        cep = dados.get('cep', '')
        if cep:
            self.var_cep.set(formatar_cep(cep))
        
        self.var_logradouro.set(dados.get('logradouro', ''))
        self.var_numero.set(dados.get('numero', ''))
        self.var_complemento.set(dados.get('complemento', ''))
        self.var_bairro.set(dados.get('bairro', ''))
        self.var_cidade.set(dados.get('cidade', ''))
        self.var_estado.set(dados.get('estado', 'SP'))
        self.var_pais.set(dados.get('pais', 'Brasil'))
        
        # Contatos
        self.var_contato_principal.set(dados.get('contato_principal', ''))
        
        tel1 = dados.get('telefone1', '')
        if tel1:
            self.var_telefone1.set(formatar_telefone(tel1))
        
        tel2 = dados.get('telefone2', '')
        if tel2:
            self.var_telefone2.set(formatar_telefone(tel2))
        
        self.var_email_principal.set(dados.get('email_principal', ''))
        self.var_email_secundario.set(dados.get('email_secundario', ''))
        self.var_site.set(dados.get('site', ''))
        
        # Comercial
        self.var_condicoes_pagamento.set(dados.get('condicoes_pagamento', ''))
        prazo = dados.get('prazo_entrega_padrao')
        self.var_prazo_entrega.set(str(prazo) if prazo else '')
        
        valor_min = dados.get('valor_minimo_pedido', 0.0)
        self.var_valor_minimo.set(f"{valor_min:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        desconto = dados.get('desconto_padrao', 0.0)
        self.var_desconto_padrao.set(str(desconto))
        
        # Bancário
        self.var_banco.set(dados.get('banco', ''))
        self.var_agencia.set(dados.get('agencia', ''))
        self.var_conta.set(dados.get('conta', ''))
        self.var_chave_pix.set(dados.get('chave_pix', ''))
        
        logger.info("Dados carregados na aba Complementares")
    
    def limpar(self):
        """Limpa todos os campos"""
        # Endereço
        self.var_cep.set("")
        self.var_logradouro.set("")
        self.var_numero.set("")
        self.var_complemento.set("")
        self.var_bairro.set("")
        self.var_cidade.set("")
        self.var_estado.set("SP")
        self.var_pais.set("Brasil")
        
        # Contatos
        self.var_contato_principal.set("")
        self.var_telefone1.set("")
        self.var_telefone2.set("")
        self.var_email_principal.set("")
        self.var_email_secundario.set("")
        self.var_site.set("")
        
        # Comercial
        self.var_condicoes_pagamento.set("")
        self.var_prazo_entrega.set("")
        self.var_valor_minimo.set("0,00")
        self.var_desconto_padrao.set("0")
        
        # Bancário
        self.var_banco.set("")
        self.var_agencia.set("")
        self.var_conta.set("")
        self.var_chave_pix.set("")
        
        # Limpar status CEP
        if self.label_cep_status:
            self.label_cep_status.config(text="")
        
        logger.info("Formulário Complementares limpo")
