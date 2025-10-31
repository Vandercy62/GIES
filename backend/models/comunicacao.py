"""
MODELOS DE COMUNICAÇÃO
======================

Sistema ERP Primotex - Modelos SQLAlchemy para o módulo de Comunicação
Suporte completo para templates, mensagens, histórico e integrações

Funcionalidades:
- Templates de mensagens automáticas
- Histórico completo de comunicações
- Integração WhatsApp Business API
- Sistema de email automatizado
- Notificações de OS e Agendamento
- Log detalhado de envios

Autor: GitHub Copilot
Data: 29/10/2025
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.config import Base
import enum

class TipoComunicacao(str, enum.Enum):
    """Tipos de comunicação disponíveis"""
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    PUSH = "PUSH"

class StatusComunicacao(str, enum.Enum):
    """Status das comunicações"""
    PENDENTE = "PENDENTE"
    ENVIANDO = "ENVIANDO"
    ENVIADO = "ENVIADO"
    ENTREGUE = "ENTREGUE"
    LIDO = "LIDO"
    ERRO = "ERRO"
    CANCELADO = "CANCELADO"

class TipoTemplate(str, enum.Enum):
    """Tipos de templates disponíveis"""
    OS_CRIADA = "OS_CRIADA"
    OS_INICIADA = "OS_INICIADA"
    OS_CONCLUIDA = "OS_CONCLUIDA"
    OS_CANCELADA = "OS_CANCELADA"
    AGENDAMENTO_CONFIRMADO = "AGENDAMENTO_CONFIRMADO"
    AGENDAMENTO_LEMBRETE = "AGENDAMENTO_LEMBRETE"
    AGENDAMENTO_CANCELADO = "AGENDAMENTO_CANCELADO"
    COBRANCA_VENCIMENTO = "COBRANCA_VENCIMENTO"
    COBRANCA_VENCIDA = "COBRANCA_VENCIDA"
    PAGAMENTO_CONFIRMADO = "PAGAMENTO_CONFIRMADO"
    ORCAMENTO_ENVIADO = "ORCAMENTO_ENVIADO"
    CLIENTE_BOAS_VINDAS = "CLIENTE_BOAS_VINDAS"
    PROMOCIONAL = "PROMOCIONAL"
    PERSONALIZADO = "PERSONALIZADO"

class PrioridadeEnvio(str, enum.Enum):
    """Prioridades de envio das mensagens"""
    BAIXA = "BAIXA"
    NORMAL = "NORMAL"
    ALTA = "ALTA"
    URGENTE = "URGENTE"

class ComunicacaoTemplate(Base):
    """
    Modelo para templates de comunicação
    """
    __tablename__ = "comunicacao_templates"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoTemplate), nullable=False)
    canal = Column(Enum(TipoComunicacao), nullable=False)
    
    # Conteúdo do template
    assunto = Column(String(200), nullable=True)  # Para email
    template_texto = Column(Text, nullable=False)
    template_html = Column(Text, nullable=True)  # Para email
    
    # Configurações
    ativo = Column(Boolean, default=True)
    automatico = Column(Boolean, default=False)  # Envio automático
    
    # Variáveis disponíveis (JSON)
    variaveis_disponiveis = Column(JSON, nullable=True)
    
    # Configurações específicas do canal
    configuracoes_canal = Column(JSON, nullable=True)
    
    # Metadados
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(String(100), nullable=True)
    
    # Relacionamentos
    comunicacoes = relationship("ComunicacaoHistorico", back_populates="template")

class ComunicacaoHistorico(Base):
    """
    Modelo para histórico de comunicações enviadas
    """
    __tablename__ = "comunicacao_historico"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação da comunicação
    template_id = Column(Integer, ForeignKey("comunicacao_templates.id"), nullable=True)
    tipo = Column(Enum(TipoComunicacao), nullable=False)
    canal_usado = Column(String(50), nullable=False)
    
    # Destinatário
    destinatario_nome = Column(String(200), nullable=False)
    destinatario_contato = Column(String(100), nullable=False)  # email, telefone, etc.
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    
    # Conteúdo enviado
    assunto = Column(String(200), nullable=True)
    conteudo_texto = Column(Text, nullable=False)
    conteudo_html = Column(Text, nullable=True)
    
    # Status e tracking
    status = Column(Enum(StatusComunicacao), default=StatusComunicacao.PENDENTE)
    tentativas_envio = Column(Integer, default=0)
    max_tentativas = Column(Integer, default=3)
    
    # Timestamps
    agendado_para = Column(DateTime(timezone=True), nullable=True)
    enviado_em = Column(DateTime(timezone=True), nullable=True)
    entregue_em = Column(DateTime(timezone=True), nullable=True)
    lido_em = Column(DateTime(timezone=True), nullable=True)
    
    # Origem da comunicação
    origem_modulo = Column(String(50), nullable=True)  # OS, AGENDAMENTO, FINANCEIRO
    origem_id = Column(Integer, nullable=True)  # ID do registro de origem
    
    # Dados da resposta do provedor
    provider_response = Column(JSON, nullable=True)
    erro_detalhes = Column(Text, nullable=True)
    
    # Metadados
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    template = relationship("ComunicacaoTemplate", back_populates="comunicacoes")
    cliente = relationship("Cliente", back_populates="comunicacoes")

class ComunicacaoConfig(Base):
    """
    Modelo para configurações de comunicação
    """
    __tablename__ = "comunicacao_config"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação
    nome = Column(String(100), unique=True, nullable=False)
    tipo = Column(Enum(TipoComunicacao), nullable=False)
    
    # Configurações específicas
    configuracoes = Column(JSON, nullable=False)
    
    # Status
    ativo = Column(Boolean, default=True)
    padrao = Column(Boolean, default=False)  # Configuração padrão para o tipo
    
    # Limites e controles
    limite_diario = Column(Integer, nullable=True)
    limite_mensal = Column(Integer, nullable=True)
    
    # Metadados
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(String(100), nullable=True)

class ComunicacaoFila(Base):
    """
    Modelo para fila de comunicações a serem processadas
    """
    __tablename__ = "comunicacao_fila"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação
    template_id = Column(Integer, ForeignKey("comunicacao_templates.id"), nullable=True)
    prioridade = Column(Integer, default=5)
    
    # Destinatário
    destinatario_nome = Column(String(200), nullable=False)
    destinatario_contato = Column(String(100), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    
    # Conteúdo
    assunto = Column(String(200), nullable=True)
    conteudo = Column(Text, nullable=False)
    variaveis_contexto = Column(JSON, nullable=True)
    
    # Agendamento
    agendado_para = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(20), default="PENDENTE")
    tentativas = Column(Integer, default=0)
    max_tentativas = Column(Integer, default=3)
    
    # Origem
    origem_modulo = Column(String(50), nullable=True)
    origem_id = Column(Integer, nullable=True)
    
    # Metadados
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    processado_em = Column(DateTime(timezone=True), nullable=True)
    erro_detalhes = Column(Text, nullable=True)

class ComunicacaoEstatisticas(Base):
    """
    Modelo para estatísticas de comunicação
    """
    __tablename__ = "comunicacao_estatisticas"

    id = Column(Integer, primary_key=True, index=True)
    
    # Período
    data_referencia = Column(DateTime(timezone=True), nullable=False)
    periodo_tipo = Column(String(20), nullable=False)  # DIA, SEMANA, MES, ANO
    
    # Métricas por tipo
    email_enviados = Column(Integer, default=0)
    email_entregues = Column(Integer, default=0)
    email_lidos = Column(Integer, default=0)
    email_erros = Column(Integer, default=0)
    
    whatsapp_enviados = Column(Integer, default=0)
    whatsapp_entregues = Column(Integer, default=0)
    whatsapp_lidos = Column(Integer, default=0)
    whatsapp_erros = Column(Integer, default=0)
    
    sms_enviados = Column(Integer, default=0)
    sms_entregues = Column(Integer, default=0)
    sms_erros = Column(Integer, default=0)
    
    # Métricas por módulo
    os_comunicacoes = Column(Integer, default=0)
    agendamento_comunicacoes = Column(Integer, default=0)
    financeiro_comunicacoes = Column(Integer, default=0)
    promocional_comunicacoes = Column(Integer, default=0)
    
    # Custos (se aplicável)
    custo_total = Column(String(20), nullable=True)  # Decimal como string
    
    # Metadados
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

# Adicionar relacionamento ao modelo Cliente
def add_comunicacao_relationship():
    """
    Adiciona relacionamento de comunicação ao modelo Cliente
    """
    try:
        from backend.models.cliente import Cliente
        if not hasattr(Cliente, 'comunicacoes'):
            Cliente.comunicacoes = relationship("ComunicacaoHistorico", back_populates="cliente")
    except ImportError:
        pass

# =======================================
# CONSTANTES PARA IMPORTAÇÃO
# =======================================

# Exportar enums como constantes para facilitar uso
TIPOS_COMUNICACAO = TipoComunicacao
STATUS_ENVIO = StatusComunicacao
TIPOS_TEMPLATE = TipoTemplate
PRIORIDADE_ENVIO = PrioridadeEnvio
CANAIS_COMUNICACAO = TipoComunicacao

# Executar quando o módulo for importado
add_comunicacao_relationship()