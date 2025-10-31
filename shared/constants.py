#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTANTES DO SISTEMA ERP PRIMOTEX
=================================

Centralização de todas as constantes utilizadas
no sistema para evitar duplicação e facilitar manutenção.

Autor: GitHub Copilot
Data: 29/10/2025
"""

# =======================================
# CONFIGURAÇÕES DA APLICAÇÃO
# =======================================

# Informações da empresa
COMPANY_NAME = "Primotex - Forros e Divisórias Eireli"
SYSTEM_NAME = "Sistema ERP Primotex"
VERSION = "2.0.0 - Fase 2"

# API e conectividade
API_BASE_URL = "http://127.0.0.1:8002"
API_TIMEOUT = 10

# =======================================
# ESTILOS TKINTER
# =======================================

# Estilos de botões
STYLE_LOGIN_BUTTON = "Login.TButton"
STYLE_PRIMARY_BUTTON = "Primary.TButton"
STYLE_SECONDARY_BUTTON = "Secondary.TButton"

# Estilos de entrada
STYLE_LOGIN_ENTRY = "Login.TEntry"
STYLE_PRIMARY_ENTRY = "Primary.TEntry"

# Estilos de labels
STYLE_SUBTITLE_LABEL = "Subtitle.TLabel"
STYLE_SUBTITULO_LABEL = "Subtitulo.TLabel"
STYLE_FIELD_LABEL = "Field.TLabel"
STYLE_TITLE_LABEL = "Title.TLabel"

# Estilos de frames
STYLE_CARD_FRAME = "Card.TFrame"

# Fontes comuns
FONT_SEGOE_UI = "Segoe UI"

# =======================================
# EVENTOS TKINTER
# =======================================

EVENT_KEY_RELEASE = '<KeyRelease>'
EVENT_BUTTON_CLICK = '<Button-1>'
EVENT_COMBOBOX_SELECTED = '<<ComboboxSelected>>'
EVENT_RETURN_KEY = '<Return>'

# =======================================
# TIPOS DE PESSOA
# =======================================

TIPO_PESSOA_FISICA = "Física"
TIPO_PESSOA_JURIDICA = "Jurídica"

# =======================================
# TIPOS DE PRODUTO
# =======================================

TIPO_PRODUTO = "Produto"
TIPO_SERVICO = "Serviço"

# =======================================
# TAMANHOS DE CÓDIGOS DE BARRAS
# =======================================

TAMANHO_PEQUENO = "Pequeno"
TAMANHO_MEDIO = "Médio"
TAMANHO_GRANDE = "Grande"
TAMANHO_EXTRA_GRANDE = "Extra Grande"

# =======================================
# TIPOS DE MOVIMENTAÇÃO ESTOQUE
# =======================================

MOVIMENTO_ENTRADA = "Entrada"
MOVIMENTO_SAIDA = "Saída"
MOVIMENTO_AJUSTE = "Ajuste"
MOVIMENTO_TRANSFERENCIA = "Transferência"

# =======================================
# PERFIS DE USUÁRIO
# =======================================

PERFIL_ADMINISTRADOR = "administrador"
PERFIL_GERENTE = "gerente"
PERFIL_OPERADOR = "operador"
PERFIL_CONSULTA = "consulta"

# =======================================
# MENSAGENS DE VALIDAÇÃO
# =======================================

MSG_USUARIO_NAO_ENCONTRADO = "Usuário não encontrado"
MSG_EMAIL_JA_EM_USO = "Email já está em uso"
MSG_CREDENCIAIS_INVALIDAS = "Credenciais inválidas"
MSG_ACESSO_NEGADO = "Acesso negado"

# Strings duplicadas identificadas pelo lint
STR_EMAIL_EM_USO = "Email já está em uso"
STR_USUARIO_NAO_ENCONTRADO = "Usuário não encontrado"

# =======================================
# CAMPOS DE FORMULÁRIO
# =======================================

FIELD_NOME_USUARIO = "Nome de usuário"
FIELD_EMAIL_USUARIO = "Email do usuário"
FIELD_NOME_COMPLETO = "Nome completo"
FIELD_PERFIL_USUARIO = "Perfil do usuário"
FIELD_STATUS_ATIVO = "Status ativo/inativo"
FIELD_OBSERVACOES = "Observações adicionais"

# =======================================
# CORES DO SISTEMA
# =======================================

# Cores principais
COLOR_PRIMARY = "#2E86AB"
COLOR_SECONDARY = "#A23B72"
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FF9800"
COLOR_ERROR = "#F44336"
COLOR_INFO = "#2196F3"

# Cores de fundo
COLOR_BG_MAIN = "#f8f9fa"
COLOR_BG_LIGHT = "#ffffff"
COLOR_BG_DARK = "#343a40"

# =======================================
# CONFIGURAÇÕES DE INTERFACE
# =======================================

# Tamanhos de janela
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 800

# Padding padrão
PADDING_SMALL = 5
PADDING_MEDIUM = 10
PADDING_LARGE = 20

# =======================================
# CONFIGURAÇÕES DE BANCO DE DADOS
# =======================================

# Nome do arquivo do banco
DATABASE_FILE = "primotex_erp.db"

# Configurações de conexão
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20

# =======================================
# CONFIGURAÇÕES DE RELATÓRIOS
# =======================================

# Formatos suportados
REPORT_FORMAT_PDF = "PDF"
REPORT_FORMAT_EXCEL = "Excel"
REPORT_FORMAT_CSV = "CSV"

# Templates disponíveis
TEMPLATE_SIMPLES = "Simples"
TEMPLATE_PROFISSIONAL = "Profissional"
TEMPLATE_MODERNO = "Moderno"
TEMPLATE_CLASSICO = "Clássico"
TEMPLATE_ELEGANTE = "Elegante"
TEMPLATE_CORPORATIVO = "Corporativo"

# =======================================
# FORMATOS DE CÓDIGOS DE BARRAS
# =======================================

BARCODE_EAN13 = "EAN13"
BARCODE_EAN8 = "EAN8"
BARCODE_CODE128 = "Code128"
BARCODE_CODE39 = "Code39"
BARCODE_UPCA = "UPCA"

# =======================================
# CONFIGURAÇÕES DE SEGURANÇA
# =======================================

# JWT
JWT_EXPIRY_DAYS = 30
JWT_ALGORITHM = "HS256"

# Senha
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 50

# =======================================
# MENSAGENS DO SISTEMA
# =======================================

# Sucesso
MSG_OPERACAO_SUCESSO = "Operação realizada com sucesso!"
MSG_DADOS_SALVOS = "Dados salvos com sucesso!"
MSG_LOGIN_SUCESSO = "Login realizado com sucesso!"

# Erro
MSG_ERRO_CONEXAO = "Erro de conexão com o servidor"
MSG_ERRO_DADOS = "Erro ao processar dados"
MSG_ERRO_VALIDACAO = "Dados inválidos fornecidos"

# Avisos
MSG_CONFIRMA_EXCLUSAO = "Tem certeza que deseja excluir este item?"
MSG_DADOS_NAO_SALVOS = "Existem dados não salvos. Deseja continuar?"

# Desenvolvimento
MSG_FUNCIONALIDADE_EM_DESENVOLVIMENTO = "Funcionalidade em desenvolvimento"

# Interface
MSG_SELECIONE_ITEM = "Selecione um item"
MSG_CONFIRMACAO = "Confirmação"
MSG_SELECAO = "Seleção"

# Campos comuns
LABEL_CANAL = "Canal:"
LABEL_DESTINATARIO = "Destinatário"
LABEL_AUTOMATICO = "Automático"
LABEL_APROVACAO = "Aprovação"

# =======================================
# CONFIGURAÇÕES DE NAVEGAÇÃO
# =======================================

# Histórico
MAX_HISTORY_SIZE = 50
MAX_BREADCRUMB_SIZE = 4

# Atalhos de teclado
SHORTCUT_HELP = "Ctrl+H"
SHORTCUT_SEARCH = "Ctrl+F"
SHORTCUT_HOME = "Ctrl+Home"
SHORTCUT_BACK = "Alt+Left"

# =======================================
# UTILITÁRIOS
# =======================================

def get_api_url(endpoint: str) -> str:
    """Constrói URL completa da API"""
    return f"{API_BASE_URL}{endpoint}"

def get_style_name(base: str, variant: str = "") -> str:
    """Constrói nome de estilo consistente"""
    if variant:
        return f"{base}.{variant}"
    return base

def get_window_geometry(width: int = None, height: int = None) -> str:
    """Constrói string de geometria para janelas"""
    w = width or WINDOW_DEFAULT_WIDTH
    h = height or WINDOW_DEFAULT_HEIGHT
    return f"{w}x{h}"

# =======================================
# VALIDAÇÕES REGEX
# =======================================

import re

# Padrões de validação
REGEX_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
REGEX_CPF = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$'
REGEX_CNPJ = r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$'
REGEX_TELEFONE = r'^\(\d{2}\)\s\d{4,5}-\d{4}$'
REGEX_CEP = r'^\d{5}-\d{3}$'

def validar_email(email: str) -> bool:
    """Valida formato de email"""
    return bool(re.match(REGEX_EMAIL, email))

def validar_cpf(cpf: str) -> bool:
    """Valida formato de CPF"""
    return bool(re.match(REGEX_CPF, cpf))

def validar_cnpj(cnpj: str) -> bool:
    """Valida formato de CNPJ"""
    return bool(re.match(REGEX_CNPJ, cnpj))

def validar_telefone(telefone: str) -> bool:
    """Valida formato de telefone"""
    return bool(re.match(REGEX_TELEFONE, telefone))

def validar_cep(cep: str) -> bool:
    """Valida formato de CEP"""
    return bool(re.match(REGEX_CEP, cep))