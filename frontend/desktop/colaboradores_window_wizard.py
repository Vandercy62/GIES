"""
COLABORADORES WIZARD - ERP PRIMOTEX
====================================

Interface desktop completa para gestão de colaboradores/funcionários.

ESTRUTURA: Wizard 4 Abas
- Aba 1: Dados Pessoais + Foto 3x4
- Aba 2: Dados Profissionais
- Aba 3: Documentos + Alertas Vencimento
- Aba 4: Observações

RECURSOS:
- CRUD completo com threading
- Upload foto 3x4 (100x130px)
- Validação CPF/RG/PIS
- Sistema alertas vencimento docs (verde/amarelo/vermelho)
- Integração SessionManager
- PDF Ficha Colaborador

Autor: GitHub Copilot
Data: 17/11/2025
FASE: 102 - Módulo 2.3
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, List, Any
import requests
from datetime import datetime, date, timedelta
from threading import Thread
import json
from pathlib import Path
import re
from PIL import Image, ImageTk
import io

# Imports do sistema
from frontend.desktop.auth_middleware import (
    require_login,
    get_token_for_api,
    create_auth_header,
    get_current_user_info
)


# =====================================
# CONSTANTES E CONFIGURAÇÕES
# =====================================

API_BASE_URL = "http://127.0.0.1:8002/api/v1"
FOTO_TAMANHO = (100, 130)  # 3x4 proporcional
FOTO_PLACEHOLDER_PATH = "assets/images/placeholder_colaborador.png"

# Cores para alertas de vencimento
COR_VENCIDO = "#FF4444"        # Vermelho
COR_VENCE_BREVE = "#FFB84D"    # Laranja
COR_OK = "#4CAF50"             # Verde
COR_NEUTRO = "#999999"         # Cinza

# Dias para alerta
DIAS_ALERTA_AMARELO = 30       # Vence em até 30 dias
DIAS_ALERTA_VERMELHO = 0       # Já venceu


# =====================================
# UTILITÁRIOS DE VALIDAÇÃO
# =====================================

def validar_cpf(cpf: str) -> bool:
    """Valida CPF usando algoritmo oficial"""
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Validar dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = ((soma * 10) % 11) % 10
        if int(cpf[i]) != digito:
            return False

    return True


def formatar_cpf(cpf: str) -> str:
    """Formata CPF: xxx.xxx.xxx-xx"""
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf


def formatar_telefone(tel: str) -> str:
    """Formata telefone: (XX) XXXXX-XXXX"""
    tel = ''.join(filter(str.isdigit, tel))
    if len(tel) == 11:
        return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
    elif len(tel) == 10:
        return f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
    return tel


def formatar_cep(cep: str) -> str:
    """Formata CEP: XXXXX-XXX"""
    cep = ''.join(filter(str.isdigit, cep))
    if len(cep) == 8:
        return f"{cep[:5]}-{cep[5:]}"
    return cep


def calcular_cor_vencimento(data_validade) -> str:
    """Calcula cor do alerta baseado na data de vencimento

    Args:
        data_validade: string (YYYY-MM-DD) ou date object

    Returns:
        str: Cor hexadecimal (#RRGGBB)
    """
    if not data_validade:
        return COR_NEUTRO

    try:
        # Aceitar tanto string quanto date object
        if isinstance(data_validade, str):
            validade = datetime.strptime(data_validade, "%Y-%m-%d").date()
        elif isinstance(data_validade, date):
            validade = data_validade
        else:
            return COR_NEUTRO

        hoje = date.today()
        dias_restantes = (validade - hoje).days

        if dias_restantes < DIAS_ALERTA_VERMELHO:
            return COR_VENCIDO  # Vermelho
        elif dias_restantes <= DIAS_ALERTA_AMARELO:
            return COR_VENCE_BREVE  # Laranja
        else:
            return COR_OK  # Verde

    except:
        return COR_NEUTRO


# =====================================
# WIDGET: FOTO 3x4
# =====================================

class FotoWidget(tk.Frame):
    """Widget para exibir e gerenciar foto 3x4 do colaborador"""

    def __init__(self, parent):
        super().__init__(parent, relief=tk.RIDGE, borderwidth=2)
        self.foto_path: Optional[str] = None
        self.foto_dados: Optional[bytes] = None

        self._setup_ui()

    def _setup_ui(self):
        """Configura interface do widget"""
        # Label para exibir foto
        self.label_foto = tk.Label(
            self,
            width=FOTO_TAMANHO[0],
            height=FOTO_TAMANHO[1],
            bg="#F0F0F0",
            text="Sem foto\n\nClique para\nselecionar",
            cursor="hand2"
        )
        self.label_foto.pack(pady=5)

        # Bind clique para upload
        self.label_foto.bind("<Button-1>", lambda e: self.selecionar_foto())

        # Botões de ação
        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(
            frame_botoes,
            text="📁 Upload",
            command=self.selecionar_foto,
            width=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            frame_botoes,
            text="🗑️ Limpar",
            command=self.limpar_foto,
            width=10
        ).pack(side=tk.RIGHT, padx=2)

    def selecionar_foto(self):
        """Abre dialog para selecionar arquivo de foto"""
        filepath = filedialog.askopenfilename(
            title="Selecionar Foto 3x4",
            filetypes=[
                ("Imagens", "*.jpg *.jpeg *.png *.bmp"),
                ("Todos", "*.*")
            ]
        )

        if filepath:
            self.carregar_foto(filepath)

    def carregar_foto(self, filepath: str):
        """Carrega e exibe foto do arquivo

        Args:
            filepath: Caminho absoluto do arquivo
        """
        try:
            # Abrir imagem
            img = Image.open(filepath)

            # Redimensionar mantendo proporção
            img.thumbnail(FOTO_TAMANHO, Image.Resampling.LANCZOS)

            # Converter para Tkinter PhotoImage
            photo = ImageTk.PhotoImage(img)

            # Atualizar label
            self.label_foto.configure(image=photo, text="")
            self.label_foto.image = photo  # Manter referência

            # Salvar path e dados
            self.foto_path = filepath

            # Converter para bytes (para upload futuro)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            self.foto_dados = buffer.getvalue()

        except Exception as e:
            messagebox.showerror(
                "Erro ao Carregar Foto",
                f"Não foi possível carregar a foto:\n{e}"
            )

    def limpar_foto(self):
        """Remove foto atual"""
        self.label_foto.configure(
            image="",
            text="Sem foto\n\nClique para\nselecionar"
        )
        self.foto_path = None
        self.foto_dados = None

    def get_foto_dados(self) -> Optional[bytes]:
        """Retorna dados da foto em bytes (para upload)"""
        return self.foto_dados


# =====================================
# WIZARD PRINCIPAL
# =====================================

@require_login()
class ColaboradoresWindow:
    """Janela principal do wizard de colaboradores"""

    def __init__(self, parent):
        self.parent = parent
        self.token = get_token_for_api()

        # Janela principal
        self.window = tk.Toplevel(parent)
        self.window.title("Gestão de Colaboradores - ERP Primotex")
        self.window.geometry("1400x900")

        # Dados do colaborador em edição
        self.colaborador_atual: Optional[Dict[str, Any]] = None
        self.modo_edicao = False

        # Listas auxiliares
        self.lista_cargos: List[Dict] = []
        self.lista_departamentos: List[Dict] = []

        # Setup
        self._carregar_dados_auxiliares()
        self._setup_ui()
        self._carregar_cargos()
        self._carregar_departamentos()
        self._carregar_colaboradores_lista()
        self._carregar_colaboradores()

    def _setup_ui(self):
        """Configura interface completa"""
        # Título
        header = tk.Frame(self.window, bg="#2C3E50", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="👥 GESTÃO DE COLABORADORES",
            font=("Segoe UI", 16, "bold"),
            bg="#2C3E50",
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=10)

        # Barra de ferramentas
        toolbar = tk.Frame(self.window, bg="#ECF0F1", height=50)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        # Botões de ação
        tk.Button(
            toolbar,
            text="➕ Novo Colaborador",
            command=self.novo_colaborador,
            bg="#27AE60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=18
        ).pack(side=tk.LEFT, padx=5, pady=8)

        tk.Button(
            toolbar,
            text="✏️ Editar",
            command=self.editar_colaborador,
            width=12
        ).pack(side=tk.LEFT, padx=5, pady=8)

        tk.Button(
            toolbar,
            text="🗑️ Excluir",
            command=self.excluir_colaborador,
            bg="#E74C3C",
            fg="white",
            width=12
        ).pack(side=tk.LEFT, padx=5, pady=8)

        tk.Button(
            toolbar,
            text="🔄 Atualizar",
            command=self._carregar_colaboradores,
            width=12
        ).pack(side=tk.LEFT, padx=5, pady=8)

        tk.Button(
            toolbar,
            text="📄 Gerar PDF",
            command=self.gerar_pdf_ficha,
            width=12
        ).pack(side=tk.LEFT, padx=5, pady=8)

        # Container principal com painel divisor
        container = tk.PanedWindow(self.window, orient=tk.HORIZONTAL, sashwidth=5)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # PAINEL ESQUERDO: Lista de colaboradores
        painel_esquerdo = tk.Frame(container, width=400)
        container.add(painel_esquerdo, minsize=350)

        self._criar_painel_lista(painel_esquerdo)

        # PAINEL DIREITO: Formulário wizard (4 abas)
        painel_direito = tk.Frame(container)
        container.add(painel_direito, minsize=600)

        self._criar_painel_formulario(painel_direito)

    def _criar_painel_lista(self, parent):
        """Cria painel com lista de colaboradores"""
        # Título
        tk.Label(
            parent,
            text="Lista de Colaboradores",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=5)

        # Busca rápida
        frame_busca = tk.Frame(parent)
        frame_busca.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(frame_busca, text="🔍 Buscar:").pack(side=tk.LEFT, padx=5)

        self.entry_busca = tk.Entry(frame_busca)
        self.entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry_busca.bind("<KeyRelease>", lambda e: self._filtrar_colaboradores())

        # Treeview
        frame_tree = tk.Frame(parent)
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars
        scroll_y = tk.Scrollbar(frame_tree)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_x = tk.Scrollbar(frame_tree, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        self.tree = ttk.Treeview(
            frame_tree,
            columns=("matricula", "nome", "cargo", "status"),
            show="tree headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        self.tree.pack(fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Configurar colunas
        self.tree.heading("#0", text="ID")
        self.tree.heading("matricula", text="Matrícula")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("cargo", text="Cargo")
        self.tree.heading("status", text="Status")

        self.tree.column("#0", width=50, anchor=tk.CENTER)
        self.tree.column("matricula", width=100, anchor=tk.CENTER)
        self.tree.column("nome", width=200)
        self.tree.column("cargo", width=150)
        self.tree.column("status", width=80, anchor=tk.CENTER)

        # Bind duplo clique
        self.tree.bind("<Double-1>", lambda e: self.editar_colaborador())

        # Resumo
        self.label_total = tk.Label(
            parent,
            text="Total: 0 colaboradores",
            font=("Segoe UI", 9)
        )
        self.label_total.pack(pady=5)

    def _criar_painel_formulario(self, parent):
        """Cria painel com notebook de 4 abas"""
        # Título
        tk.Label(
            parent,
            text="Cadastro de Colaborador",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=5)

        # Notebook (Wizard 4 abas)
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ABA 1: Dados Pessoais + Foto
        self.aba_pessoais = tk.Frame(self.notebook)
        self.notebook.add(self.aba_pessoais, text="👤 Dados Pessoais")
        self._criar_aba_dados_pessoais()

        # ABA 2: Dados Profissionais
        self.aba_profissionais = tk.Frame(self.notebook)
        self.notebook.add(self.aba_profissionais, text="💼 Dados Profissionais")
        self._criar_aba_dados_profissionais()

        # ABA 3: Documentos + Alertas
        self.aba_documentos = tk.Frame(self.notebook)
        self.notebook.add(self.aba_documentos, text="📄 Documentos")
        self._criar_aba_documentos()

        # ABA 4: Observações
        self.aba_observacoes = tk.Frame(self.notebook)
        self.notebook.add(self.aba_observacoes, text="📝 Observações")
        self._criar_aba_observacoes()

        # Barra de ações do formulário
        frame_acoes = tk.Frame(parent, bg="#ECF0F1", height=60)
        frame_acoes.pack(fill=tk.X, side=tk.BOTTOM)
        frame_acoes.pack_propagate(False)

        tk.Button(
            frame_acoes,
            text="💾 Salvar",
            command=self.salvar_colaborador,
            bg="#27AE60",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=15
        ).pack(side=tk.LEFT, padx=10, pady=15)

        tk.Button(
            frame_acoes,
            text="❌ Cancelar",
            command=self.cancelar_edicao,
            width=15
        ).pack(side=tk.LEFT, padx=5, pady=15)

        tk.Button(
            frame_acoes,
            text="🗑️ Limpar Formulário",
            command=self.limpar_formulario,
            width=18
        ).pack(side=tk.RIGHT, padx=10, pady=15)

    def _criar_aba_dados_pessoais(self):
        """ABA 1: Formulário de dados pessoais + foto 3x4"""
        # Container com scroll
        canvas = tk.Canvas(self.aba_pessoais)
        scrollbar = tk.Scrollbar(self.aba_pessoais, orient=tk.VERTICAL, command=canvas.yview)
        frame_scroll = tk.Frame(canvas)

        frame_scroll.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame_scroll, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Container principal com 2 colunas
        container = tk.Frame(frame_scroll)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # COLUNA ESQUERDA: Foto
        col_esquerda = tk.Frame(container)
        col_esquerda.grid(row=0, column=0, sticky=tk.N, padx=10)

        tk.Label(
            col_esquerda,
            text="Foto 3x4",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=5)

        self.widget_foto = FotoWidget(col_esquerda)
        self.widget_foto.pack(pady=10)

        # COLUNA DIREITA: Formulário
        col_direita = tk.Frame(container)
        col_direita.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E), padx=10)
        col_direita.columnconfigure(1, weight=1)
        col_direita.columnconfigure(3, weight=1)

        row = 0

        # Matrícula (gerada automaticamente)
        tk.Label(col_direita, text="Matrícula:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_matricula = tk.Entry(col_direita, state="readonly", width=15)
        self.entry_matricula.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # Nome Completo *
        tk.Label(col_direita, text="Nome Completo: *", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_nome = tk.Entry(col_direita, width=50)
        self.entry_nome.grid(row=row, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # Nome Social
        tk.Label(col_direita, text="Nome Social:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_nome_social = tk.Entry(col_direita, width=50)
        self.entry_nome_social.grid(row=row, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # CPF * e RG
        tk.Label(col_direita, text="CPF: *", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_cpf = tk.Entry(col_direita, width=20)
        self.entry_cpf.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.entry_cpf.bind("<FocusOut>", self._validar_cpf)

        tk.Label(col_direita, text="RG:").grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.entry_rg = tk.Entry(col_direita, width=20)
        self.entry_rg.grid(row=row, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # Data Nascimento e Sexo
        tk.Label(col_direita, text="Data Nascimento:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_data_nasc = tk.Entry(col_direita, width=15)
        self.entry_data_nasc.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        tk.Label(col_direita, text="Sexo:").grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.combo_sexo = ttk.Combobox(
            col_direita,
            values=["Masculino", "Feminino", "Não Binário", "Prefiro não informar"],
            state="readonly",
            width=18
        )
        self.combo_sexo.grid(row=row, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # Telefones
        tk.Label(col_direita, text="Telefone Principal:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_telefone = tk.Entry(col_direita, width=20)
        self.entry_telefone.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.entry_telefone.bind("<FocusOut>", lambda e: self._formatar_telefone(self.entry_telefone))

        tk.Label(col_direita, text="Telefone Secundário:").grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.entry_telefone2 = tk.Entry(col_direita, width=20)
        self.entry_telefone2.grid(row=row, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.entry_telefone2.bind("<FocusOut>", lambda e: self._formatar_telefone(self.entry_telefone2))
        row += 1

        # Emails
        tk.Label(col_direita, text="Email Pessoal:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_email_pessoal = tk.Entry(col_direita, width=40)
        self.entry_email_pessoal.grid(row=row, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        tk.Label(col_direita, text="Email Corporativo:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_email_corp = tk.Entry(col_direita, width=40)
        self.entry_email_corp.grid(row=row, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # Separador: Endereço
        ttk.Separator(col_direita, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=15
        )
        row += 1

        tk.Label(col_direita, text="ENDEREÇO RESIDENCIAL", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, columnspan=4, sticky=tk.W, pady=5
        )
        row += 1

        # CEP
        tk.Label(col_direita, text="CEP:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_cep = tk.Entry(col_direita, width=15)
        self.entry_cep.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.entry_cep.bind("<FocusOut>", self._buscar_cep)

        tk.Button(col_direita, text="🔍 Buscar", command=self._buscar_cep, width=10).grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=5
        )
        row += 1

        # Logradouro
        tk.Label(col_direita, text="Logradouro:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_logradouro = tk.Entry(col_direita, width=50)
        self.entry_logradouro.grid(row=row, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # Número e Complemento
        tk.Label(col_direita, text="Número:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_numero = tk.Entry(col_direita, width=10)
        self.entry_numero.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        tk.Label(col_direita, text="Complemento:").grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.entry_complemento = tk.Entry(col_direita, width=30)
        self.entry_complemento.grid(row=row, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # Bairro
        tk.Label(col_direita, text="Bairro:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_bairro = tk.Entry(col_direita, width=30)
        self.entry_bairro.grid(row=row, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # Cidade e Estado
        tk.Label(col_direita, text="Cidade:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_cidade = tk.Entry(col_direita, width=30)
        self.entry_cidade.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        tk.Label(col_direita, text="UF:").grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.entry_estado = ttk.Combobox(
            col_direita,
            values=["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
                    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
                    "RS", "RO", "RR", "SC", "SP", "SE", "TO"],
            state="readonly",
            width=5
        )
        self.entry_estado.grid(row=row, column=3, sticky=tk.W, pady=5, padx=5)
        row += 1

    def _criar_aba_dados_profissionais(self):
        """ABA 2: Dados profissionais completos"""
        # Container com scroll
        canvas = tk.Canvas(self.aba_profissionais)
        scrollbar = tk.Scrollbar(self.aba_profissionais, orient=tk.VERTICAL, command=canvas.yview)
        frame_scroll = tk.Frame(canvas)

        frame_scroll.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame_scroll, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Formulário
        form = tk.Frame(frame_scroll)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        row = 0

        # ===== SEÇÃO 1: CARGO E DEPARTAMENTO =====
        tk.Label(form, text="CARGO E LOTAÇÃO", font=("Segoe UI", 11, "bold"), fg="#2C3E50").grid(
            row=row, column=0, columnspan=4, sticky=tk.W, pady=(0, 10)
        )
        row += 1

        # Cargo *
        tk.Label(form, text="Cargo: *", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.combo_cargo = ttk.Combobox(form, state="readonly", width=30)
        self.combo_cargo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        tk.Button(form, text="➕ Novo Cargo", command=self._novo_cargo, width=12).grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=5
        )
        row += 1

        # Departamento/Setor *
        tk.Label(form, text="Departamento: *", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.combo_departamento = ttk.Combobox(form, state="readonly", width=30)
        self.combo_departamento.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        tk.Button(form, text="➕ Novo Depto", command=self._novo_departamento, width=12).grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=5
        )
        row += 1

        # Superior Direto
        tk.Label(form, text="Superior Direto:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.combo_superior = ttk.Combobox(form, state="readonly", width=40)
        self.combo_superior.grid(row=row, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # Separador
        ttk.Separator(form, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=15
        )
        row += 1

        # ===== SEÇÃO 2: CONTRATO E ADMISSÃO =====
        tk.Label(form, text="CONTRATO E VÍNCULO", font=("Segoe UI", 11, "bold"), fg="#2C3E50").grid(
            row=row, column=0, columnspan=4, sticky=tk.W, pady=(0, 10)
        )
        row += 1

        # Tipo de Contrato *
        tk.Label(form, text="Tipo Contrato: *", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.combo_tipo_contrato = ttk.Combobox(
            form,
            values=["CLT", "Pessoa Jurídica", "Estagiário", "Terceirizado", "Freelancer", "Temporário"],
            state="readonly",
            width=20
        )
        self.combo_tipo_contrato.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Data Admissão *
        tk.Label(form, text="Data Admissão: *", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.entry_data_admissao = tk.Entry(form, width=15)
        self.entry_data_admissao.grid(row=row, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        tk.Label(form, text="(DD/MM/AAAA)", font=("Segoe UI", 8), fg="#666").grid(
            row=row, column=3, sticky=tk.E, pady=5, padx=5
        )
        row += 1

        # Status *
        tk.Label(form, text="Status: *", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.combo_status = ttk.Combobox(
            form,
            values=["ATIVO", "INATIVO", "FERIAS", "LICENCA", "AFASTADO", "DEMITIDO"],
            state="readonly",
            width=15
        )
        self.combo_status.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.combo_status.set("ATIVO")

        # Data Demissão (condicional)
        tk.Label(form, text="Data Demissão:").grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.entry_data_demissao = tk.Entry(form, width=15, state="disabled")
        self.entry_data_demissao.grid(row=row, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Bind para habilitar data demissão quando status = DEMITIDO
        self.combo_status.bind("<<ComboboxSelected>>", self._toggle_data_demissao)
        row += 1

        # Separador
        ttk.Separator(form, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=15
        )
        row += 1

        # ===== SEÇÃO 3: REMUNERAÇÃO =====
        tk.Label(form, text="REMUNERAÇÃO E BENEFÍCIOS", font=("Segoe UI", 11, "bold"), fg="#2C3E50").grid(
            row=row, column=0, columnspan=4, sticky=tk.W, pady=(0, 10)
        )
        row += 1

        # Salário Base
        tk.Label(form, text="Salário Base (R$):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_salario = tk.Entry(form, width=20)
        self.entry_salario.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.entry_salario.bind("<FocusOut>", lambda e: self._formatar_valor(self.entry_salario))

        # Vale Transporte
        tk.Label(form, text="Vale Transporte (R$):").grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.entry_vale_transporte = tk.Entry(form, width=15)
        self.entry_vale_transporte.grid(row=row, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.entry_vale_transporte.bind("<FocusOut>", lambda e: self._formatar_valor(self.entry_vale_transporte))
        row += 1

        # Vale Refeição
        tk.Label(form, text="Vale Refeição (R$):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_vale_refeicao = tk.Entry(form, width=20)
        self.entry_vale_refeicao.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.entry_vale_refeicao.bind("<FocusOut>", lambda e: self._formatar_valor(self.entry_vale_refeicao))
        row += 1

        # Checkboxes de benefícios
        frame_beneficios = tk.Frame(form)
        frame_beneficios.grid(row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)

        self.var_plano_saude = tk.BooleanVar()
        tk.Checkbutton(
            frame_beneficios,
            text="🏥 Plano de Saúde",
            variable=self.var_plano_saude,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=10)

        self.var_plano_odonto = tk.BooleanVar()
        tk.Checkbutton(
            frame_beneficios,
            text="🦷 Plano Odontológico",
            variable=self.var_plano_odonto,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=10)
        row += 1

        # Total (calculado automaticamente)
        frame_total = tk.Frame(form, bg="#E8F5E9", relief=tk.RIDGE, borderwidth=2)
        frame_total.grid(row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)

        tk.Label(
            frame_total,
            text="💰 Remuneração Total:",
            font=("Segoe UI", 10, "bold"),
            bg="#E8F5E9"
        ).pack(side=tk.LEFT, padx=10, pady=8)

        self.label_total_remuneracao = tk.Label(
            frame_total,
            text="R$ 0,00",
            font=("Segoe UI", 12, "bold"),
            fg="#27AE60",
            bg="#E8F5E9"
        )
        self.label_total_remuneracao.pack(side=tk.LEFT, padx=10, pady=8)

        # Bind para calcular total automaticamente
        self.entry_salario.bind("<KeyRelease>", self._calcular_total_remuneracao)
        self.entry_vale_transporte.bind("<KeyRelease>", self._calcular_total_remuneracao)
        self.entry_vale_refeicao.bind("<KeyRelease>", self._calcular_total_remuneracao)
        row += 1

        # Separador
        ttk.Separator(form, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=15
        )
        row += 1

        # ===== SEÇÃO 4: JORNADA DE TRABALHO =====
        tk.Label(form, text="JORNADA DE TRABALHO", font=("Segoe UI", 11, "bold"), fg="#2C3E50").grid(
            row=row, column=0, columnspan=4, sticky=tk.W, pady=(0, 10)
        )
        row += 1

        # Carga Horária Semanal
        tk.Label(form, text="Carga Horária Semanal:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_carga_horaria = tk.Entry(form, width=10)
        self.entry_carga_horaria.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_carga_horaria.insert(0, "40")

        tk.Label(form, text="horas", font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=70
        )
        row += 1

        # Horários
        tk.Label(form, text="Horário Entrada:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_horario_entrada = tk.Entry(form, width=10)
        self.entry_horario_entrada.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_horario_entrada.insert(0, "08:00")
        tk.Label(form, text="(HH:MM)", font=("Segoe UI", 8), fg="#666").grid(
            row=row, column=1, sticky=tk.W, pady=5, padx=70
        )

        tk.Label(form, text="Horário Saída:").grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.entry_horario_saida = tk.Entry(form, width=10)
        self.entry_horario_saida.grid(row=row, column=3, sticky=tk.W, pady=5, padx=5)
        self.entry_horario_saida.insert(0, "17:00")
        tk.Label(form, text="(HH:MM)", font=("Segoe UI", 8), fg="#666").grid(
            row=row, column=3, sticky=tk.W, pady=5, padx=70
        )
        row += 1

        # Horário Almoço
        tk.Label(form, text="Almoço Início:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_almoco_inicio = tk.Entry(form, width=10)
        self.entry_almoco_inicio.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_almoco_inicio.insert(0, "12:00")

        tk.Label(form, text="Almoço Fim:").grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.entry_almoco_fim = tk.Entry(form, width=10)
        self.entry_almoco_fim.grid(row=row, column=3, sticky=tk.W, pady=5, padx=5)
        self.entry_almoco_fim.insert(0, "13:00")
        row += 1

        # Separador
        ttk.Separator(form, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=15
        )
        row += 1

        # ===== SEÇÃO 5: DADOS BANCÁRIOS =====
        tk.Label(form, text="DADOS BANCÁRIOS PARA PAGAMENTO", font=("Segoe UI", 11, "bold"), fg="#2C3E50").grid(
            row=row, column=0, columnspan=4, sticky=tk.W, pady=(0, 10)
        )
        row += 1

        # Banco
        tk.Label(form, text="Banco:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.combo_banco = ttk.Combobox(
            form,
            values=[
                "001 - Banco do Brasil", "033 - Santander", "104 - Caixa Econômica",
                "237 - Bradesco", "341 - Itaú", "756 - Sicoob", "748 - Sicredi",
                "077 - Banco Inter", "260 - Nubank", "290 - PagSeguro", "323 - Mercado Pago"
            ],
            width=30
        )
        self.combo_banco.grid(row=row, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # Agência e Conta
        tk.Label(form, text="Agência:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_agencia = tk.Entry(form, width=15)
        self.entry_agencia.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        tk.Label(form, text="Conta:").grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.entry_conta = tk.Entry(form, width=20)
        self.entry_conta.grid(row=row, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # Tipo de Conta
        tk.Label(form, text="Tipo de Conta:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.combo_tipo_conta = ttk.Combobox(
            form,
            values=["Conta Corrente", "Conta Poupança", "Conta Salário"],
            state="readonly",
            width=20
        )
        self.combo_tipo_conta.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.combo_tipo_conta.set("Conta Corrente")
        row += 1

        # Separador
        ttk.Separator(form, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=15
        )
        row += 1

        # ===== SEÇÃO 6: DOCUMENTOS TRABALHISTAS =====
        tk.Label(form, text="DOCUMENTOS TRABALHISTAS", font=("Segoe UI", 11, "bold"), fg="#2C3E50").grid(
            row=row, column=0, columnspan=4, sticky=tk.W, pady=(0, 10)
        )
        row += 1

        # PIS/PASEP
        tk.Label(form, text="PIS/PASEP:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_pis = tk.Entry(form, width=20)
        self.entry_pis.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

        # CTPS
        tk.Label(form, text="CTPS Nº:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.entry_ctps_numero = tk.Entry(form, width=20)
        self.entry_ctps_numero.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        tk.Label(form, text="Série:").grid(
            row=row, column=2, sticky=tk.W, pady=5, padx=10
        )
        self.entry_ctps_serie = tk.Entry(form, width=15)
        self.entry_ctps_serie.grid(row=row, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        row += 1

    def _toggle_data_demissao(self, event=None):
        """Habilita/desabilita data demissão baseado no status"""
        status = self.combo_status.get()
        if status == "DEMITIDO":
            self.entry_data_demissao.config(state="normal")
        else:
            self.entry_data_demissao.config(state="disabled")
            self.entry_data_demissao.delete(0, tk.END)

    def _formatar_valor(self, entry: tk.Entry):
        """Formata valor monetário (R$ 1.234,56)"""
        try:
            valor = entry.get().replace("R$", "").replace(".", "").replace(",", "").strip()
            if not valor:
                return

            valor_float = float(valor) / 100
            entry.delete(0, tk.END)
            entry.insert(0, f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        except ValueError:
            pass

    def _calcular_total_remuneracao(self, event=None):
        """Calcula total de remuneração automaticamente"""
        try:
            salario = self.entry_salario.get().replace("R$", "").replace(".", "").replace(",", ".").strip()
            vale_transporte = self.entry_vale_transporte.get().replace("R$", "").replace(".", "").replace(",", ".").strip()
            vale_refeicao = self.entry_vale_refeicao.get().replace("R$", "").replace(".", "").replace(",", ".").strip()

            total = 0.0
            if salario:
                total += float(salario)
            if vale_transporte:
                total += float(vale_transporte)
            if vale_refeicao:
                total += float(vale_refeicao)

            self.label_total_remuneracao.config(
                text=f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        except ValueError:
            pass

    def _novo_cargo(self):
        """Abre dialog para criar novo cargo"""
        # TODO: Implementar dialog de cadastro de cargo (TAREFA 6)
        messagebox.showinfo("Em Desenvolvimento", "Cadastro de novos cargos será implementado em breve")

    def _novo_departamento(self):
        """Abre dialog para criar novo departamento"""
        # TODO: Implementar dialog de cadastro de departamento (TAREFA 6)
        messagebox.showinfo("Em Desenvolvimento", "Cadastro de novos departamentos será implementado em breve")

    def _carregar_cargos(self):
        """Carrega lista de cargos do backend"""
        # TODO: Implementar requisição GET /api/v1/cargos (TAREFA 8)
        # Por enquanto, usar dados mockados
        self.combo_cargo['values'] = [
            "Gerente Administrativo",
            "Auxiliar Administrativo",
            "Instalador Sênior",
            "Instalador Júnior",
            "Vendedor",
            "Faturista",
            "Almoxarife"
        ]

    def _carregar_departamentos(self):
        """Carrega lista de departamentos do backend"""
        # TODO: Implementar requisição GET /api/v1/departamentos (TAREFA 8)
        # Por enquanto, usar dados mockados
        self.combo_departamento['values'] = [
            "Administrativo",
            "Comercial",
            "Operações",
            "Financeiro",
            "Recursos Humanos",
            "Estoque"
        ]

    def _carregar_colaboradores_lista(self):
        """Carrega lista de colaboradores para superior direto"""
        # TODO: Implementar requisição GET /api/v1/colaboradores?status=ATIVO (TAREFA 8)
        # Por enquanto, usar dados mockados
        self.combo_superior['values'] = [
            "João Silva - Gerente Administrativo",
            "Maria Santos - Gerente Comercial",
            "Pedro Costa - Supervisor de Operações"
        ]

    def _criar_aba_documentos(self):
        """ABA 3: Documentos + Alertas de Vencimento"""
        # Container principal
        main_frame = tk.Frame(self.aba_documentos)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ===== SEÇÃO 1: PAINEL DE ALERTAS =====
        frame_alertas = tk.LabelFrame(
            main_frame,
            text=" ⚠️  ALERTAS DE DOCUMENTOS PRÓXIMOS DO VENCIMENTO ",
            font=("Segoe UI", 10, "bold"),
            fg="#E74C3C"
        )
        frame_alertas.pack(fill=tk.X, padx=5, pady=(0, 10))

        # Container de alertas (scrollable)
        canvas_alertas = tk.Canvas(frame_alertas, height=80, bg="#FFF")
        scrollbar_alertas = tk.Scrollbar(frame_alertas, orient=tk.VERTICAL, command=canvas_alertas.yview)
        self.frame_alertas_lista = tk.Frame(canvas_alertas, bg="#FFF")

        self.frame_alertas_lista.bind(
            "<Configure>",
            lambda e: canvas_alertas.configure(scrollregion=canvas_alertas.bbox("all"))
        )

        canvas_alertas.create_window((0, 0), window=self.frame_alertas_lista, anchor=tk.NW)
        canvas_alertas.configure(yscrollcommand=scrollbar_alertas.set)

        canvas_alertas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar_alertas.pack(side=tk.RIGHT, fill=tk.Y)

        # Mensagem inicial (sem alertas)
        tk.Label(
            self.frame_alertas_lista,
            text="✅ Nenhum documento próximo do vencimento",
            font=("Segoe UI", 9),
            fg="#27AE60",
            bg="#FFF"
        ).pack(pady=10)

        # ===== SEÇÃO 2: TOOLBAR =====
        toolbar = tk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        tk.Button(
            toolbar,
            text="➕ Adicionar Documento",
            command=self._adicionar_documento,
            font=("Segoe UI", 9, "bold"),
            bg="#3498DB",
            fg="white",
            width=20,
            relief=tk.RAISED
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="👁️ Visualizar",
            command=self._visualizar_documento,
            font=("Segoe UI", 9),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="💾 Download",
            command=self._download_documento,
            font=("Segoe UI", 9),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="🗑️ Excluir",
            command=self._excluir_documento,
            font=("Segoe UI", 9),
            fg="#E74C3C",
            width=12
        ).pack(side=tk.LEFT, padx=5)

        # ===== SEÇÃO 3: LISTA DE DOCUMENTOS =====
        frame_lista = tk.Frame(main_frame)
        frame_lista.pack(fill=tk.BOTH, expand=True)

        # Treeview
        colunas = ("id", "tipo", "numero", "data_emissao", "data_validade", "arquivo", "status")
        self.tree_documentos = ttk.Treeview(
            frame_lista,
            columns=colunas,
            show="headings",
            height=15
        )

        # Headers
        self.tree_documentos.heading("id", text="ID")
        self.tree_documentos.heading("tipo", text="Tipo Documento")
        self.tree_documentos.heading("numero", text="Número")
        self.tree_documentos.heading("data_emissao", text="Data Emissão")
        self.tree_documentos.heading("data_validade", text="Validade")
        self.tree_documentos.heading("arquivo", text="Arquivo")
        self.tree_documentos.heading("status", text="Status")

        # Larguras
        self.tree_documentos.column("id", width=50, anchor=tk.CENTER)
        self.tree_documentos.column("tipo", width=150, anchor=tk.W)
        self.tree_documentos.column("numero", width=120, anchor=tk.CENTER)
        self.tree_documentos.column("data_emissao", width=100, anchor=tk.CENTER)
        self.tree_documentos.column("data_validade", width=100, anchor=tk.CENTER)
        self.tree_documentos.column("arquivo", width=200, anchor=tk.W)
        self.tree_documentos.column("status", width=100, anchor=tk.CENTER)

        # Scrollbars
        scroll_y = tk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree_documentos.yview)
        scroll_x = tk.Scrollbar(frame_lista, orient=tk.HORIZONTAL, command=self.tree_documentos.xview)
        self.tree_documentos.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree_documentos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Tags de cores (status baseado em vencimento)
        self.tree_documentos.tag_configure("VENCIDO", background="#FFCCCC", foreground="#C0392B")
        self.tree_documentos.tag_configure("VENCE_BREVE", background="#FFE6B3", foreground="#D68910")
        self.tree_documentos.tag_configure("VALIDO", background="#D5F4E6", foreground="#27AE60")

        # Carregar documentos mockados para teste
        self._carregar_documentos_exemplo()

    def _carregar_documentos_exemplo(self):
        """Carrega documentos de exemplo para teste visual"""
        from datetime import datetime, timedelta

        # Limpar lista
        for item in self.tree_documentos.get_children():
            self.tree_documentos.delete(item)

        # Exemplos com diferentes status
        hoje = datetime.now()

        # Documento VENCIDO
        self.tree_documentos.insert(
            "", tk.END,
            values=(
                "1",
                "CNH - Carteira Nacional de Habilitação",
                "12345678901",
                (hoje - timedelta(days=1825)).strftime("%d/%m/%Y"),  # 5 anos atrás
                (hoje - timedelta(days=30)).strftime("%d/%m/%Y"),  # Vencida há 30 dias
                "cnh_colaborador.pd",
                "VENCIDO"
            ),
            tags=("VENCIDO",)
        )

        # Documento VENCE_BREVE (15 dias)
        self.tree_documentos.insert(
            "", tk.END,
            values=(
                "2",
                "Atestado de Saúde Ocupacional (ASO)",
                "ASO-2024-001",
                (hoje - timedelta(days=350)).strftime("%d/%m/%Y"),
                (hoje + timedelta(days=15)).strftime("%d/%m/%Y"),
                "aso_colaborador.pd",
                "VENCE EM 15 DIAS"
            ),
            tags=("VENCE_BREVE",)
        )

        # Documento VÁLIDO
        self.tree_documentos.insert(
            "", tk.END,
            values=(
                "3",
                "CTPS - Carteira de Trabalho",
                "987654/0001-SP",
                (hoje - timedelta(days=3650)).strftime("%d/%m/%Y"),
                "INDETERMINADO",
                "ctps_colaborador.pd",
                "VÁLIDO"
            ),
            tags=("VALIDO",)
        )

        # Atualizar painel de alertas
        self._atualizar_painel_alertas()

    def _atualizar_painel_alertas(self):
        """Atualiza painel de alertas com documentos vencidos/próximos"""
        # Limpar alertas existentes
        for widget in self.frame_alertas_lista.winfo_children():
            widget.destroy()

        # Buscar documentos com problemas
        alertas = []
        for item in self.tree_documentos.get_children():
            valores = self.tree_documentos.item(item)['values']
            status = valores[6]

            if status == "VENCIDO":
                alertas.append({
                    "tipo": valores[1],
                    "status": "VENCIDO",
                    "data": valores[4],
                    "cor_bg": "#FFCCCC",
                    "cor_fg": "#C0392B",
                    "icone": "🚨"
                })
            elif "VENCE EM" in str(status):
                alertas.append({
                    "tipo": valores[1],
                    "status": status,
                    "data": valores[4],
                    "cor_bg": "#FFE6B3",
                    "cor_fg": "#D68910",
                    "icone": "⚠️"
                })

        # Se não há alertas
        if not alertas:
            tk.Label(
                self.frame_alertas_lista,
                text="✅ Nenhum documento próximo do vencimento",
                font=("Segoe UI", 9),
                fg="#27AE60",
                bg="#FFF"
            ).pack(pady=10)
            return

        # Exibir alertas
        for alerta in alertas:
            frame_alerta = tk.Frame(
                self.frame_alertas_lista,
                bg=alerta["cor_bg"],
                relief=tk.RIDGE,
                borderwidth=1
            )
            frame_alerta.pack(fill=tk.X, padx=5, pady=2)

            tk.Label(
                frame_alerta,
                text=f"{alerta['icone']} {alerta['tipo']} - {alerta['status']} (Validade: {alerta['data']})",
                font=("Segoe UI", 9, "bold"),
                fg=alerta["cor_fg"],
                bg=alerta["cor_bg"]
            ).pack(side=tk.LEFT, padx=10, pady=5)

    def _adicionar_documento(self):
        """Abre dialog para adicionar novo documento"""
        messagebox.showinfo("Em Desenvolvimento", "Upload de documentos será implementado na TAREFA 6")

    def _visualizar_documento(self):
        """Abre documento selecionado"""
        selecionado = self.tree_documentos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um documento para visualizar")
            return
        messagebox.showinfo("Em Desenvolvimento", "Visualização será implementada na TAREFA 6")

    def _download_documento(self):
        """Faz download do documento selecionado"""
        selecionado = self.tree_documentos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um documento para download")
            return
        messagebox.showinfo("Em Desenvolvimento", "Download será implementado na TAREFA 6")

    def _excluir_documento(self):
        """Exclui documento selecionado"""
        selecionado = self.tree_documentos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um documento para excluir")
            return

        valores = self.tree_documentos.item(selecionado[0])['values']
        tipo = valores[1]

        if messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir o documento:\n\n{tipo}?"):
            self.tree_documentos.delete(selecionado[0])
            self._atualizar_painel_alertas()
            messagebox.showinfo("Sucesso", "Documento excluído!")

    def _criar_aba_observacoes(self):
        """ABA 4: Campo de observações gerais"""
        # Container principal
        main_frame = tk.Frame(self.aba_observacoes)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        tk.Label(
            main_frame,
            text="📝 OBSERVAÇÕES GERAIS",
            font=("Segoe UI", 12, "bold"),
            fg="#2C3E50"
        ).pack(pady=(0, 15))

        # Info
        tk.Label(
            main_frame,
            text="Use este espaço para registrar informações adicionais, notas importantes ou observações sobre o colaborador.",
            font=("Segoe UI", 9),
            fg="#666",
            wraplength=700,
            justify=tk.LEFT
        ).pack(pady=(0, 10))

        # Frame do texto
        frame_texto = tk.Frame(main_frame)
        frame_texto.pack(fill=tk.BOTH, expand=True)

        # Text widget com scrollbar
        scroll_y = tk.Scrollbar(frame_texto)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_observacoes = tk.Text(
            frame_texto,
            font=("Segoe UI", 10),
            wrap=tk.WORD,
            yscrollcommand=scroll_y.set,
            relief=tk.RIDGE,
            borderwidth=2
        )
        self.text_observacoes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.text_observacoes.yview)

        # Contador de caracteres
        frame_rodape = tk.Frame(main_frame)
        frame_rodape.pack(fill=tk.X, pady=(10, 0))

        self.label_caracteres = tk.Label(
            frame_rodape,
            text="0 / 5000 caracteres",
            font=("Segoe UI", 8),
            fg="#666"
        )
        self.label_caracteres.pack(side=tk.LEFT)

        self.label_ultima_alteracao = tk.Label(
            frame_rodape,
            text="Última alteração: --",
            font=("Segoe UI", 8),
            fg="#666"
        )
        self.label_ultima_alteracao.pack(side=tk.RIGHT)

        # Bind para contador
        self.text_observacoes.bind("<KeyRelease>", self._atualizar_contador_caracteres)

    def _atualizar_contador_caracteres(self, event=None):
        """Atualiza contador de caracteres"""
        texto = self.text_observacoes.get("1.0", tk.END).strip()
        total = len(texto)

        # Atualizar label
        self.label_caracteres.config(text=f"{total} / 5000 caracteres")

        # Mudar cor se ultrapassar limite
        if total > 5000:
            self.label_caracteres.config(fg="#E74C3C")
        else:
            self.label_caracteres.config(fg="#666")

        # Atualizar timestamp
        from datetime import datetime
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.label_ultima_alteracao.config(text=f"Última alteração: {now}")

    def _criar_aba_observacoes_OLD(self):
        """ABA 4: Campo de observações gerais"""
        # TODO: Implementar próxima tarefa
        tk.Label(
            self.aba_observacoes,
            text="🚧 ABA EM DESENVOLVIMENTO\n\nTarefa 5: Observações (4h)",
            font=("Segoe UI", 12),
            fg="#666"
        ).pack(expand=True)

    # =====================================
    # MÉTODOS DE VALIDAÇÃO E FORMATAÇÃO
    # =====================================

    def _validar_cpf(self, event=None):
        """Valida CPF ao sair do campo"""
        cpf = self.entry_cpf.get()
        if cpf and not validar_cpf(cpf):
            messagebox.showwarning(
                "CPF Inválido",
                "O CPF informado não é válido!\n\nVerifique os dígitos."
            )
            self.entry_cpf.focus()
            return False

        # Formatar CPF
        if cpf:
            self.entry_cpf.delete(0, tk.END)
            self.entry_cpf.insert(0, formatar_cpf(cpf))

        return True

    def _formatar_telefone(self, entry_widget):
        """Formata telefone ao sair do campo"""
        tel = entry_widget.get()
        if tel:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, formatar_telefone(tel))

    def _buscar_cep(self, event=None):
        """Busca endereço pelo CEP (ViaCEP API)"""
        cep = self.entry_cep.get()
        cep_limpo = ''.join(filter(str.isdigit, cep))

        if len(cep_limpo) != 8:
            return

        # Formatar CEP
        self.entry_cep.delete(0, tk.END)
        self.entry_cep.insert(0, formatar_cep(cep_limpo))

        # Buscar em thread separada
        def buscar():
            try:
                response = requests.get(
                    f"https://viacep.com.br/ws/{cep_limpo}/json/",
                    timeout=5
                )

                if response.status_code == 200:
                    dados = response.json()

                    if "erro" not in dados:
                        # Preencher campos
                        self.entry_logradouro.delete(0, tk.END)
                        self.entry_logradouro.insert(0, dados.get("logradouro", ""))

                        self.entry_bairro.delete(0, tk.END)
                        self.entry_bairro.insert(0, dados.get("bairro", ""))

                        self.entry_cidade.delete(0, tk.END)
                        self.entry_cidade.insert(0, dados.get("localidade", ""))

                        self.entry_estado.set(dados.get("u", ""))

                        # Focar no número
                        self.entry_numero.focus()
                    else:
                        messagebox.showwarning("CEP Não Encontrado", "CEP não encontrado na base de dados.")

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar CEP:\n{e}")

        Thread(target=buscar, daemon=True).start()

    # =====================================
    # MÉTODOS DE DADOS AUXILIARES
    # =====================================

    def _carregar_dados_auxiliares(self):
        """Carrega listas de cargos e departamentos da API"""
        # TODO: Implementar requisições API
        self.lista_cargos = []
        self.lista_departamentos = []

    # =====================================
    # MÉTODOS CRUD
    # =====================================

    def _carregar_colaboradores(self):
        """Carrega lista de colaboradores da API"""
        # TODO: Implementar requisição API
        self.tree.delete(*self.tree.get_children())
        self.label_total.config(text="Total: 0 colaboradores")

    def _filtrar_colaboradores(self):
        """Filtra colaboradores por texto de busca"""
        # TODO: Implementar filtro
        pass

    def novo_colaborador(self):
        """Inicia cadastro de novo colaborador"""
        self.limpar_formulario()
        self.modo_edicao = False
        self.colaborador_atual = None
        self.notebook.select(0)  # Ir para primeira aba

    def editar_colaborador(self):
        """Carrega dados do colaborador selecionado para edição"""
        # TODO: Implementar edição
        messagebox.showinfo("Em Desenvolvimento", "Função de edição será implementada na Tarefa 8")

    def excluir_colaborador(self):
        """Exclui colaborador selecionado"""
        # TODO: Implementar exclusão
        messagebox.showinfo("Em Desenvolvimento", "Função de exclusão será implementada na Tarefa 8")

    def salvar_colaborador(self):
        """Salva dados do colaborador (novo ou edição)"""
        # TODO: Implementar salvamento
        messagebox.showinfo("Em Desenvolvimento", "Função de salvamento será implementada na Tarefa 8")

    def cancelar_edicao(self):
        """Cancela edição e limpa formulário"""
        if messagebox.askyesno("Confirmar", "Descartar alterações?"):
            self.limpar_formulario()

    def limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        # Aba 1: Dados Pessoais
        self.entry_matricula.config(state="normal")
        self.entry_matricula.delete(0, tk.END)
        self.entry_matricula.config(state="readonly")

        self.entry_nome.delete(0, tk.END)
        self.entry_nome_social.delete(0, tk.END)
        self.entry_cpf.delete(0, tk.END)
        self.entry_rg.delete(0, tk.END)
        self.entry_data_nasc.delete(0, tk.END)
        self.combo_sexo.set("")
        self.entry_telefone.delete(0, tk.END)
        self.entry_telefone2.delete(0, tk.END)
        self.entry_email_pessoal.delete(0, tk.END)
        self.entry_email_corp.delete(0, tk.END)

        self.entry_cep.delete(0, tk.END)
        self.entry_logradouro.delete(0, tk.END)
        self.entry_numero.delete(0, tk.END)
        self.entry_complemento.delete(0, tk.END)
        self.entry_bairro.delete(0, tk.END)
        self.entry_cidade.delete(0, tk.END)
        self.entry_estado.set("")

        self.widget_foto.limpar_foto()

        # Resetar modo edição
        self.modo_edicao = False
        self.colaborador_atual = None

    def gerar_pdf_ficha(self):
        """Gera PDF da ficha do colaborador selecionado"""
        selecionado = self.tree_lista.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um colaborador para gerar PDF")
            return

        valores = self.tree_lista.item(selecionado[0])['values']
        colaborador_id = valores[0]
        colaborador_nome = valores[2]

        # Solicitar caminho para salvar
        from tkinter import filedialog
        from datetime import datetime

        filename_sugerido = f"Ficha_Colaborador_{colaborador_nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pd"

        filepath = filedialog.asksaveasfilename(
            title="Salvar Ficha PDF",
            defaultextension=".pd",
            filetypes=[("PDF", "*.pd")],
            initialfile=filename_sugerido
        )

        if not filepath:
            return

        # Gerar PDF em thread
        def gerar_thread():
            try:
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.lib import colors
                from reportlab.lib.units import inch, cm
                from reportlab.platypus import (
                    SimpleDocTemplate, Table, TableStyle, Paragraph, 
                    Spacer, Image, PageBreak
                )
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
                from reportlab.pdfgen import canvas
                from io import BytesIO
                import qrcode

                # Criar documento
                doc = SimpleDocTemplate(
                    filepath,
                    pagesize=A4,
                    rightMargin=2*cm,
                    leftMargin=2*cm,
                    topMargin=2*cm,
                    bottomMargin=2*cm
                )

                # Container de elementos
                elements = []

                # Estilos
                styles = getSampleStyleSheet()

                style_titulo = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#2C3E50'),
                    spaceAfter=30,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Bold'
                )

                style_secao = ParagraphStyle(
                    'CustomSection',
                    parent=styles['Heading2'],
                    fontSize=14,
                    textColor=colors.HexColor('#34495E'),
                    spaceAfter=12,
                    spaceBefore=20,
                    fontName='Helvetica-Bold'
                )

                style_normal = ParagraphStyle(
                    'CustomNormal',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.black,
                    fontName='Helvetica'
                )

                # ===== CABEÇALHO =====
                elements.append(Paragraph("FICHA DE COLABORADOR", style_titulo))
                elements.append(Paragraph("PRIMOTEX - FORROS E DIVISÓRIAS EIRELLI", style_normal))
                elements.append(Spacer(1, 0.5*cm))

                # Data de emissão
                data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")
                elements.append(Paragraph(f"<b>Data de Emissão:</b> {data_emissao}", style_normal))
                elements.append(Spacer(1, 1*cm))

                # ===== SEÇÃO 1: DADOS PESSOAIS =====
                elements.append(Paragraph("📋 DADOS PESSOAIS", style_secao))

                dados_pessoais = [
                    ["<b>Matrícula:</b>", valores[1]],
                    ["<b>Nome Completo:</b>", valores[2]],
                    ["<b>Cargo:</b>", valores[3]],
                    ["<b>Status:</b>", valores[4]],
                ]

                # Pegar dados do formulário (se estiver preenchido)
                if hasattr(self, 'entry_cp'):
                    cpf = self.entry_cpf.get()
                    if cpf:
                        dados_pessoais.append(["<b>CPF:</b>", cpf])

                    rg = self.entry_rg.get()
                    if rg:
                        dados_pessoais.append(["<b>RG:</b>", rg])

                    data_nasc = self.entry_data_nascimento.get()
                    if data_nasc:
                        dados_pessoais.append(["<b>Data Nascimento:</b>", data_nasc])

                    telefone = self.entry_telefone_principal.get()
                    if telefone:
                        dados_pessoais.append(["<b>Telefone:</b>", telefone])

                    email = self.entry_email_pessoal.get()
                    if email:
                        dados_pessoais.append(["<b>Email Pessoal:</b>", email])

                table_pessoais = Table(dados_pessoais, colWidths=[5*cm, 12*cm])
                table_pessoais.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
                ]))
                elements.append(table_pessoais)
                elements.append(Spacer(1, 1*cm))

                # ===== SEÇÃO 2: ENDEREÇO =====
                elements.append(Paragraph("📍 ENDEREÇO", style_secao))

                dados_endereco = []
                if hasattr(self, 'entry_cep'):
                    cep = self.entry_cep.get()
                    logradouro = self.entry_logradouro.get()
                    numero = self.entry_numero.get()
                    complemento = self.entry_complemento.get()
                    bairro = self.entry_bairro.get()
                    cidade = self.entry_cidade.get()
                    uf = self.combo_uf.get()

                    if cep:
                        dados_endereco.append(["<b>CEP:</b>", cep])
                    if logradouro:
                        endereco_completo = f"{logradouro}, {numero}"
                        if complemento:
                            endereco_completo += f" - {complemento}"
                        dados_endereco.append(["<b>Logradouro:</b>", endereco_completo])
                    if bairro:
                        dados_endereco.append(["<b>Bairro:</b>", bairro])
                    if cidade and uf:
                        dados_endereco.append(["<b>Cidade/UF:</b>", f"{cidade} - {uf}"])

                if dados_endereco:
                    table_endereco = Table(dados_endereco, colWidths=[5*cm, 12*cm])
                    table_endereco.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
                    ]))
                    elements.append(table_endereco)
                    elements.append(Spacer(1, 1*cm))

                # ===== SEÇÃO 3: DADOS PROFISSIONAIS =====
                elements.append(Paragraph("💼 DADOS PROFISSIONAIS", style_secao))

                dados_profissionais = []
                if hasattr(self, 'combo_cargo'):
                    cargo = self.combo_cargo.get()
                    departamento = self.combo_departamento.get()
                    contrato = self.combo_tipo_contrato.get()
                    data_admissao = self.entry_data_admissao.get()

                    if cargo:
                        dados_profissionais.append(["<b>Cargo:</b>", cargo])
                    if departamento:
                        dados_profissionais.append(["<b>Departamento:</b>", departamento])
                    if contrato:
                        dados_profissionais.append(["<b>Tipo Contrato:</b>", contrato])
                    if data_admissao:
                        dados_profissionais.append(["<b>Data Admissão:</b>", data_admissao])

                    salario = self.entry_salario.get()
                    if salario:
                        dados_profissionais.append(["<b>Salário Base:</b>", salario])

                    total_remuneracao = self.label_total_remuneracao.cget("text")
                    if total_remuneracao:
                        dados_profissionais.append(["<b>Remuneração Total:</b>", total_remuneracao])

                if dados_profissionais:
                    table_profissionais = Table(dados_profissionais, colWidths=[5*cm, 12*cm])
                    table_profissionais.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
                    ]))
                    elements.append(table_profissionais)
                    elements.append(Spacer(1, 1*cm))

                # ===== SEÇÃO 4: DOCUMENTOS =====
                elements.append(Paragraph("📄 DOCUMENTOS VINCULADOS", style_secao))

                # Listar documentos da Aba Documentos
                if hasattr(self, 'tree_documentos'):
                    docs_data = [["Tipo", "Número", "Validade", "Status"]]

                    for item in self.tree_documentos.get_children():
                        vals = self.tree_documentos.item(item)['values']
                        docs_data.append([
                            vals[1],  # tipo
                            vals[2],  # numero
                            vals[4],  # validade
                            vals[6]   # status
                        ])

                    if len(docs_data) > 1:
                        table_docs = Table(docs_data, colWidths=[6*cm, 4*cm, 3*cm, 4*cm])
                        table_docs.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
                        ]))
                        elements.append(table_docs)
                    else:
                        elements.append(Paragraph("<i>Nenhum documento anexado</i>", style_normal))

                elements.append(Spacer(1, 1*cm))

                # ===== SEÇÃO 5: OBSERVAÇÕES =====
                if hasattr(self, 'text_observacoes'):
                    observacoes = self.text_observacoes.get("1.0", tk.END).strip()
                    if observacoes:
                        elements.append(Paragraph("📝 OBSERVAÇÕES", style_secao))
                        elements.append(Paragraph(observacoes, style_normal))
                        elements.append(Spacer(1, 1*cm))

                # ===== RODAPÉ: QR CODE =====
                # Gerar QR Code com link para ficha digital
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr_data = f"COLABORADOR:{colaborador_id}|NOME:{colaborador_nome}|DATA:{datetime.now().strftime('%Y%m%d')}"
                qr.add_data(qr_data)
                qr.make(fit=True)

                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_buffer = BytesIO()
                qr_img.save(qr_buffer, format='PNG')
                qr_buffer.seek(0)

                qr_image = Image(qr_buffer, width=3*cm, height=3*cm)

                elements.append(Spacer(1, 2*cm))
                elements.append(Paragraph("QR CODE - IDENTIFICAÇÃO DIGITAL", style_secao))
                elements.append(qr_image)

                # Gerar PDF
                doc.build(elements)

                # Sucesso
                self.parent.after(0, lambda: messagebox.showinfo(
                    "Sucesso",
                    f"PDF gerado com sucesso!\n\n{filepath}"
                ))

            except Exception as e:
                self.parent.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro ao gerar PDF:\n\n{str(e)}"
                ))

        # Iniciar thread
        import threading
        thread = threading.Thread(target=gerar_thread, daemon=True)
        thread.start()


# =====================================
# PONTO DE ENTRADA
# =====================================

if __name__ == "__main__":
    # Teste standalone
    root = tk.Tk()
    root.withdraw()

    app = ColaboradoresWindow(root)
    root.mainloop()
