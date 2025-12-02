"""
SISTEMA ERP PRIMOTEX - ABA 2: DADOS BÁSICOS FORNECEDOR
=======================================================

Componente de cadastro de dados básicos do fornecedor.
Segunda aba do wizard com campos essenciais.

CAMPOS (10 total):
1. tipo_fornecedor - Radio (PF/PJ)
2. razao_social - Entry obrigatório
3. nome_fantasia - Entry opcional
4. cnpj_cpf - Entry com validação
5. inscricao_estadual - Entry opcional
6. categoria - Combobox obrigatório
7. subcategoria - Entry opcional
8. porte_empresa - Combobox
9. status - Combobox
10. avaliacao - Widget 5 estrelas

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 101
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
import logging

from shared.validadores import (
    validar_cpf,
    validar_cnpj
)
from shared.formatadores import (
    formatar_cpf,
    formatar_cnpj,
    remover_formatacao
)
from frontend.desktop.fornecedores_components.avaliacao_widget import AvaliacaoWidget

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AbaDadosBasicos:
    """
    Aba de dados básicos do fornecedor.
    Segunda etapa do wizard com informações essenciais.
    """
    
    # Cores
    COR_FUNDO = "#f8f9fa"
    COR_OBRIGATORIO = "#fff3cd"
    COR_DESTAQUE = "#e9ecef"
    
    # Fontes
    FONTE_SECAO = ("Segoe UI", 16, "bold")
    FONTE_LABEL = ("Segoe UI", 14, "bold")
    FONTE_CAMPO = ("Segoe UI", 16)
    FONTE_HINT = ("Segoe UI", 11, "italic")
    
    def __init__(self, parent_frame: tk.Frame):
        """
        Inicializa aba de dados básicos.
        
        Args:
            parent_frame: Frame pai (aba do notebook)
        """
        self.parent = parent_frame
        
        # Variáveis dos campos
        self.var_tipo_fornecedor = tk.StringVar(value="PJ")
        self.var_razao_social = tk.StringVar()
        self.var_nome_fantasia = tk.StringVar()
        self.var_cnpj_cpf = tk.StringVar()
        self.var_inscricao_estadual = tk.StringVar()
        self.var_categoria = tk.StringVar()
        self.var_subcategoria = tk.StringVar()
        self.var_porte_empresa = tk.StringVar(value="Médio")
        self.var_status = tk.StringVar(value="Ativo")
        
        # Widget de avaliação (será criado na interface)
        self.widget_avaliacao: Optional[AvaliacaoWidget] = None
        
        # Referências aos campos
        self.entry_razao_social: Optional[tk.Entry] = None
        self.entry_nome_fantasia: Optional[tk.Entry] = None
        self.entry_cnpj_cpf: Optional[tk.Entry] = None
        self.label_doc: Optional[tk.Label] = None
        self.label_razao: Optional[tk.Label] = None
        
        # Criar interface
        self._criar_interface()
        
        # Configurar validações
        self._configurar_validacoes()
        
        logger.info("AbaDadosBasicos inicializada")
        
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
        self._criar_secao_tipo_fornecedor(main_frame)
        self._criar_secao_identificacao(main_frame)
        self._criar_secao_classificacao(main_frame)
        self._criar_secao_avaliacao(main_frame)
        
    def _criar_secao_tipo_fornecedor(self, parent: tk.Frame):
        """Cria seção de tipo de fornecedor"""
        frame = tk.LabelFrame(
            parent,
            text=" TIPO DE FORNECEDOR ",
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
            variable=self.var_tipo_fornecedor,
            value="PF",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO,
            cursor="hand2",
            command=self._ao_mudar_tipo_fornecedor
        )
        rb_pf.pack(side=tk.LEFT, padx=(0, 30))
        
        rb_pj = tk.Radiobutton(
            frame,
            text="🏢 Pessoa Jurídica (CNPJ)",
            variable=self.var_tipo_fornecedor,
            value="PJ",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO,
            cursor="hand2",
            command=self._ao_mudar_tipo_fornecedor
        )
        rb_pj.pack(side=tk.LEFT)
        
    def _criar_secao_identificacao(self, parent: tk.Frame):
        """Cria seção de identificação"""
        frame = tk.LabelFrame(
            parent,
            text=" IDENTIFICAÇÃO DO FORNECEDOR ",
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
        
        # RAZÃO SOCIAL / NOME COMPLETO (obrigatório)
        self.label_razao = tk.Label(
            frame,
            text="RAZÃO SOCIAL: *",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        self.label_razao.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.entry_razao_social = tk.Entry(
            frame,
            textvariable=self.var_razao_social,
            font=self.FONTE_CAMPO,
            bg=self.COR_OBRIGATORIO,
            width=40
        )
        self.entry_razao_social.grid(row=1, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 15))
        
        # NOME FANTASIA (opcional)
        label_fantasia = tk.Label(
            frame,
            text="NOME FANTASIA:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        label_fantasia.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        self.entry_nome_fantasia = tk.Entry(
            frame,
            textvariable=self.var_nome_fantasia,
            font=self.FONTE_CAMPO,
            width=40
        )
        self.entry_nome_fantasia.grid(row=1, column=1, sticky=tk.EW, pady=(0, 15))
        
        # CNPJ/CPF (obrigatório)
        self.label_doc = tk.Label(
            frame,
            text="CNPJ: *",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        self.label_doc.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.entry_cnpj_cpf = tk.Entry(
            frame,
            textvariable=self.var_cnpj_cpf,
            font=self.FONTE_CAMPO,
            bg=self.COR_OBRIGATORIO,
            width=40
        )
        self.entry_cnpj_cpf.grid(row=3, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 15))
        
        # INSCRIÇÃO ESTADUAL (opcional)
        label_ie = tk.Label(
            frame,
            text="INSCRIÇÃO ESTADUAL:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        label_ie.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        entry_ie = tk.Entry(
            frame,
            textvariable=self.var_inscricao_estadual,
            font=self.FONTE_CAMPO,
            width=40
        )
        entry_ie.grid(row=3, column=1, sticky=tk.EW, pady=(0, 15))
        
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
        
        # Grid 2 colunas
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        # CATEGORIA (obrigatório)
        label_categoria = tk.Label(
            frame,
            text="CATEGORIA: *",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        label_categoria.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        combo_categoria = ttk.Combobox(
            frame,
            textvariable=self.var_categoria,
            font=self.FONTE_CAMPO,
            state="readonly",
            values=[
                "Materiais",
                "Ferramentas",
                "Equipamentos",
                "Serviços",
                "Insumos",
                "Transporte",
                "Outros"
            ]
        )
        combo_categoria.grid(row=1, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 15))
        
        # SUBCATEGORIA (opcional)
        label_subcategoria = tk.Label(
            frame,
            text="SUBCATEGORIA:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        label_subcategoria.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        entry_subcategoria = tk.Entry(
            frame,
            textvariable=self.var_subcategoria,
            font=self.FONTE_CAMPO,
            width=40
        )
        entry_subcategoria.grid(row=1, column=1, sticky=tk.EW, pady=(0, 15))
        
        # PORTE DA EMPRESA
        label_porte = tk.Label(
            frame,
            text="PORTE DA EMPRESA:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        label_porte.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        combo_porte = ttk.Combobox(
            frame,
            textvariable=self.var_porte_empresa,
            font=self.FONTE_CAMPO,
            state="readonly",
            values=[
                "Microempresa",
                "Pequeno",
                "Médio",
                "Grande"
            ]
        )
        combo_porte.grid(row=3, column=0, sticky=tk.EW, padx=(0, 10), pady=(0, 15))
        
        # STATUS
        label_status = tk.Label(
            frame,
            text="STATUS:",
            font=self.FONTE_LABEL,
            bg=self.COR_FUNDO,
            fg="#212529"
        )
        label_status.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        combo_status = ttk.Combobox(
            frame,
            textvariable=self.var_status,
            font=self.FONTE_CAMPO,
            state="readonly",
            values=[
                "Ativo",
                "Inativo",
                "Suspenso",
                "Bloqueado"
            ]
        )
        combo_status.grid(row=3, column=1, sticky=tk.EW, pady=(0, 15))
        
    def _criar_secao_avaliacao(self, parent: tk.Frame):
        """Cria seção de avaliação"""
        frame = tk.LabelFrame(
            parent,
            text=" AVALIAÇÃO DO FORNECEDOR ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Label explicativa
        label_hint = tk.Label(
            frame,
            text="Clique nas estrelas para avaliar a qualidade do fornecedor (1 a 5 estrelas)",
            font=self.FONTE_HINT,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        )
        label_hint.pack(pady=(0, 10))
        
        # Widget de avaliação
        self.widget_avaliacao = AvaliacaoWidget(
            frame,
            valor_inicial=None,
            on_change=self._ao_mudar_avaliacao,
            size=35,
            bg=self.COR_FUNDO
        )
        self.widget_avaliacao.pack(pady=10)
        
        # Label de texto da avaliação
        self.label_avaliacao_texto = tk.Label(
            frame,
            text="Sem avaliação",
            font=self.FONTE_CAMPO,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        )
        self.label_avaliacao_texto.pack(pady=(5, 0))
        
    def _ao_mudar_tipo_fornecedor(self):
        """Handler quando tipo de fornecedor muda"""
        tipo = self.var_tipo_fornecedor.get()
        
        if tipo == "PF":
            self.label_doc.config(text="CPF: *")
            self.label_razao.config(text="NOME COMPLETO: *")
        else:
            self.label_doc.config(text="CNPJ: *")
            self.label_razao.config(text="RAZÃO SOCIAL: *")
        
        # Limpar campo de documento ao mudar tipo
        self.var_cnpj_cpf.set("")
        
        logger.debug(f"Tipo fornecedor alterado para: {tipo}")
        
    def _ao_mudar_avaliacao(self, valor: Optional[int]):
        """
        Handler quando avaliação muda
        
        Args:
            valor: Nova avaliação (1-5 ou None)
        """
        if valor is None:
            texto = "Sem avaliação"
            cor = "#6c757d"
        else:
            estrelas = ["Péssimo", "Ruim", "Regular", "Bom", "Excelente"]
            texto = f"{valor} estrela{'s' if valor > 1 else ''} - {estrelas[valor-1]}"
            
            # Cores baseadas na avaliação
            cores = {
                1: "#dc3545",  # Vermelho
                2: "#fd7e14",  # Laranja
                3: "#ffc107",  # Amarelo
                4: "#28a745",  # Verde
                5: "#20c997"   # Verde turquesa
            }
            cor = cores.get(valor, "#6c757d")
        
        self.label_avaliacao_texto.config(text=texto, fg=cor)
        logger.debug(f"Avaliação alterada para: {valor}")
        
    def _configurar_validacoes(self):
        """Configura validações em tempo real"""
        # Validação de CNPJ/CPF ao perder foco
        self.entry_cnpj_cpf.bind("<FocusOut>", self._validar_documento)
        
        # Limitar caracteres
        self.entry_cnpj_cpf.config(
            validate="key",
            validatecommand=(
                self.parent.register(lambda text: len(text) <= 18),
                "%P"
            )
        )
        
    def _validar_documento(self, event=None):
        """Valida CPF/CNPJ"""
        documento = self.var_cnpj_cpf.get()
        
        if not documento:
            return  # Campo vazio é permitido durante digitação
        
        # Remover formatação
        doc_limpo = remover_formatacao(documento)
        
        # Validar baseado no tipo
        tipo = self.var_tipo_fornecedor.get()
        
        if tipo == "PF":
            if validar_cpf(doc_limpo):
                # Formatar CPF
                self.var_cnpj_cpf.set(formatar_cpf(doc_limpo))
                self.entry_cnpj_cpf.config(bg="white")
            else:
                messagebox.showerror(
                    "CPF Inválido",
                    "O CPF informado é inválido.\n\n"
                    "Por favor, verifique e tente novamente."
                )
                self.entry_cnpj_cpf.config(bg="#ffe6e6")
                self.entry_cnpj_cpf.focus()
        else:  # PJ
            if validar_cnpj(doc_limpo):
                # Formatar CNPJ
                self.var_cnpj_cpf.set(formatar_cnpj(doc_limpo))
                self.entry_cnpj_cpf.config(bg="white")
            else:
                messagebox.showerror(
                    "CNPJ Inválido",
                    "O CNPJ informado é inválido.\n\n"
                    "Por favor, verifique e tente novamente."
                )
                self.entry_cnpj_cpf.config(bg="#ffe6e6")
                self.entry_cnpj_cpf.focus()
    
    def obter_dados(self) -> Dict[str, Any]:
        """
        Obtém dados do formulário
        
        Returns:
            dict: Dicionário com dados do fornecedor
        """
        # Obter avaliação
        avaliacao = None
        if self.widget_avaliacao:
            avaliacao = self.widget_avaliacao.get_avaliacao()
        
        dados = {
            'tipo_fornecedor': self.var_tipo_fornecedor.get(),
            'razao_social': self.var_razao_social.get().strip(),
            'nome_fantasia': self.var_nome_fantasia.get().strip() or None,
            'cnpj_cpf': remover_formatacao(self.var_cnpj_cpf.get()),
            'inscricao_estadual': self.var_inscricao_estadual.get().strip() or None,
            'categoria': self.var_categoria.get(),
            'subcategoria': self.var_subcategoria.get().strip() or None,
            'porte_empresa': self.var_porte_empresa.get(),
            'status': self.var_status.get(),
            'avaliacao': avaliacao
        }
        
        return dados
    
    def validar(self) -> bool:
        """
        Valida todos os campos obrigatórios
        
        Returns:
            bool: True se válido, False caso contrário
        """
        # RAZÃO SOCIAL obrigatório
        if not self.var_razao_social.get().strip():
            messagebox.showerror(
                "Campo Obrigatório",
                "O campo Razão Social é obrigatório."
            )
            self.entry_razao_social.focus()
            return False
        
        # CNPJ/CPF obrigatório
        if not self.var_cnpj_cpf.get().strip():
            messagebox.showerror(
                "Campo Obrigatório",
                "O campo CNPJ/CPF é obrigatório."
            )
            self.entry_cnpj_cpf.focus()
            return False
        
        # Validar documento
        doc_limpo = remover_formatacao(self.var_cnpj_cpf.get())
        tipo = self.var_tipo_fornecedor.get()
        
        if tipo == "PF":
            if not validar_cpf(doc_limpo):
                messagebox.showerror(
                    "CPF Inválido",
                    "O CPF informado é inválido."
                )
                self.entry_cnpj_cpf.focus()
                return False
        else:
            if not validar_cnpj(doc_limpo):
                messagebox.showerror(
                    "CNPJ Inválido",
                    "O CNPJ informado é inválido."
                )
                self.entry_cnpj_cpf.focus()
                return False
        
        # CATEGORIA obrigatória
        if not self.var_categoria.get():
            messagebox.showerror(
                "Campo Obrigatório",
                "O campo Categoria é obrigatório."
            )
            return False
        
        return True
    
    def carregar_dados(self, dados: Dict[str, Any]):
        """
        Carrega dados no formulário
        
        Args:
            dados: Dicionário com dados do fornecedor
        """
        self.var_tipo_fornecedor.set(dados.get('tipo_fornecedor', 'PJ'))
        self.var_razao_social.set(dados.get('razao_social', ''))
        self.var_nome_fantasia.set(dados.get('nome_fantasia', ''))
        
        # CNPJ/CPF formatado
        doc = dados.get('cnpj_cpf', '')
        if doc:
            tipo = dados.get('tipo_fornecedor', 'PJ')
            if tipo == 'PF':
                self.var_cnpj_cpf.set(formatar_cpf(doc))
            else:
                self.var_cnpj_cpf.set(formatar_cnpj(doc))
        
        self.var_inscricao_estadual.set(dados.get('inscricao_estadual', ''))
        self.var_categoria.set(dados.get('categoria', ''))
        self.var_subcategoria.set(dados.get('subcategoria', ''))
        self.var_porte_empresa.set(dados.get('porte_empresa', 'Médio'))
        self.var_status.set(dados.get('status', 'Ativo'))
        
        # Avaliação
        avaliacao = dados.get('avaliacao')
        if self.widget_avaliacao and avaliacao:
            self.widget_avaliacao.set_avaliacao(avaliacao)
        
        # Atualizar labels baseado no tipo
        self._ao_mudar_tipo_fornecedor()
        
        logger.info("Dados carregados na aba Dados Básicos")
    
    def limpar(self):
        """Limpa todos os campos do formulário"""
        self.var_tipo_fornecedor.set("PJ")
        self.var_razao_social.set("")
        self.var_nome_fantasia.set("")
        self.var_cnpj_cpf.set("")
        self.var_inscricao_estadual.set("")
        self.var_categoria.set("")
        self.var_subcategoria.set("")
        self.var_porte_empresa.set("Médio")
        self.var_status.set("Ativo")
        
        if self.widget_avaliacao:
            self.widget_avaliacao.limpar()
        
        # Resetar cores de fundo
        if self.entry_cnpj_cpf:
            self.entry_cnpj_cpf.config(bg=self.COR_OBRIGATORIO)
        
        logger.info("Formulário de Dados Básicos limpo")
