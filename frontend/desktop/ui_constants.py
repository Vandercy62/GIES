# -*- coding: utf-8 -*-
"""
Constantes da Interface do Usuário para o Sistema ERP Primotex

Este arquivo centraliza todas as constantes de strings, cores, fontes e outros 
valores utilizados repetidamente na interface desktop do sistema.
"""

# ============================================================================
# FONTES E TIPOGRAFIA
# ============================================================================

# Fonte principal do sistema
FONT_FAMILY = 'Segoe UI'

# Tamanhos de fonte padrão
FONT_SIZES = {
    'small': 8,
    'normal': 9,
    'medium': 10,
    'large': 12,
    'xlarge': 14,
    'xxlarge': 16,
    'title': 20,
    'header': 24
}

# Estilos de fonte
FONT_STYLES = {
    'normal': (FONT_FAMILY, FONT_SIZES['normal']),
    'bold': (FONT_FAMILY, FONT_SIZES['normal'], 'bold'),
    'medium': (FONT_FAMILY, FONT_SIZES['medium']),
    'medium_bold': (FONT_FAMILY, FONT_SIZES['medium'], 'bold'),
    'large': (FONT_FAMILY, FONT_SIZES['large']),
    'large_bold': (FONT_FAMILY, FONT_SIZES['large'], 'bold'),
    'title': (FONT_FAMILY, FONT_SIZES['title'], 'bold'),
    'header': (FONT_FAMILY, FONT_SIZES['header'], 'bold')
}

# ============================================================================
# CORES DO SISTEMA
# ============================================================================

COLORS = {
    'primary': '#2c3e50',
    'secondary': '#34495e',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#3498db',
    'light': '#ecf0f1',
    'dark': '#2c3e50',
    'background': '#f8f9fa',
    'white': '#ffffff',
    'border': '#bdc3c7'
}

# ============================================================================
# TEXTOS RECORRENTES
# ============================================================================

# Títulos de módulos
MODULE_TITLES = {
    'ordem_servico': '📋 Ordem de Serviço',
    'agendamento': '📅 Agendamento',
    'financeiro': '💰 Financeiro',
    'comunicacao': '📞 Comunicação',
    'clientes': '👥 Clientes',
    'produtos': '📦 Produtos',
    'estoque': '📊 Estoque',
    'relatorios': '📈 Relatórios',
    'configuracoes': '⚙️ Configurações'
}

# Mensagens de ação
ACTION_MESSAGES = {
    'title': 'Ação Rápida',
    'nova_os': 'Funcionalidade: Nova Ordem de Serviço',
    'novo_agendamento': 'Funcionalidade: Novo Agendamento',
    'relatorio_vendas': 'Funcionalidade: Relatório de Vendas',
    'backup': 'Funcionalidade: Backup do Sistema',
    'configuracoes': 'Funcionalidade: Configurações'
}

# Tipos de pessoa
PERSON_TYPES = {
    'fisica': 'Física',
    'juridica': 'Jurídica'
}

# Tamanhos padrão
SIZE_OPTIONS = {
    'small': 'Pequeno',
    'medium': 'Médio', 
    'large': 'Grande',
    'xlarge': 'Extra Grande'
}

# Tipos de movimentação de estoque
STOCK_MOVEMENT_TYPES = {
    'all': 'Todos',
    'entrada': 'Entrada',
    'saida': 'Saída',
    'ajuste': 'Ajuste',
    'transferencia': 'Transferência'
}

# ============================================================================
# EVENTOS E BINDINGS
# ============================================================================

# Eventos de mouse
MOUSE_EVENTS = {
    'click': '<Button-1>',
    'right_click': '<Button-3>',
    'double_click': '<Double-Button-1>',
    'enter': '<Enter>',
    'leave': '<Leave>'
}

# Eventos de teclado
KEYBOARD_EVENTS = {
    'key_release': '<KeyRelease>',
    'return': '<Return>',
    'escape': '<Escape>',
    'tab': '<Tab>',
    'ctrl_s': '<Control-s>',
    'ctrl_n': '<Control-n>',
    'ctrl_o': '<Control-o>'
}

# Eventos de combobox
COMBOBOX_EVENTS = {
    'selected': '<<ComboboxSelected>>',
    'virtual_event': '<<VirtualEvent>>'
}

# ============================================================================
# PLACEHOLDERS E TEXTOS DE BUSCA
# ============================================================================

SEARCH_PLACEHOLDERS = {
    'general': 'Buscar clientes, produtos, relatórios...',
    'clientes': 'Buscar por nome, email ou telefone...',
    'produtos': 'Buscar por nome, código ou categoria...',
    'relatorios': 'Buscar relatórios...'
}

# ============================================================================
# MENSAGENS DE ERRO PADRÃO
# ============================================================================

ERROR_MESSAGES = {
    'email_em_uso': 'Email já está em uso',
    'usuario_nao_encontrado': 'Usuário não encontrado',
    'dados_invalidos': 'Dados inválidos',
    'conexao_api': 'Erro de conexão com a API',
    'permissao_negada': 'Permissão negada',
    'token_invalido': 'Token de autenticação inválido'
}

# ============================================================================
# CONFIGURAÇÕES DE LAYOUT
# ============================================================================

# Padding e margens padrão
LAYOUT = {
    'padding_small': 5,
    'padding_medium': 10,
    'padding_large': 20,
    'margin_small': 5,
    'margin_medium': 10,
    'margin_large': 15
}

# Dimensões padrão de janelas
WINDOW_SIZES = {
    'small': '600x400',
    'medium': '800x600',
    'large': '1024x768',
    'xlarge': '1200x800',
    'fullscreen': '1920x1080'
}

# ============================================================================
# ÍCONES E SÍMBOLOS
# ============================================================================

ICONS = {
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'loading': '⏳',
    'check': '✓',
    'cross': '✗',
    'arrow_up': '↑',
    'arrow_down': '↓',
    'star': '⭐',
    'heart': '❤️'
}

# ============================================================================
# CONFIGURAÇÕES DE PERFORMANCE
# ============================================================================

PERFORMANCE = {
    'cache_timeout': 30,  # segundos
    'refresh_interval': 5,  # segundos
    'api_timeout': 10,  # segundos
    'max_retries': 3,
    'batch_size': 100,
    'page_size': 50
}