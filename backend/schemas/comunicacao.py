"""
SCHEMAS DE COMUNICAÇÃO
=====================

Sistema ERP Primotex - Schemas Pydantic para o módulo de Comunicação
Validação e serialização de dados para API REST

Funcionalidades:
- Validação de templates de mensagens
- Serialização de histórico de comunicações
- Schemas para configurações de provedores
- Modelos de fila de envio
- Estatísticas e métricas

Autor: GitHub Copilot
Data: 29/10/2025
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums para validação
class TipoComunicacaoEnum(str, Enum):
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    PUSH = "PUSH"

class StatusComunicacaoEnum(str, Enum):
    PENDENTE = "PENDENTE"
    ENVIANDO = "ENVIANDO"
    ENVIADO = "ENVIADO"
    ENTREGUE = "ENTREGUE"
    LIDO = "LIDO"
    ERRO = "ERRO"
    CANCELADO = "CANCELADO"

class TipoTemplateEnum(str, Enum):
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

# ================================
# SCHEMAS DE TEMPLATE
# ================================

class ComunicacaoTemplateBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: TipoTemplateEnum
    canal: TipoComunicacaoEnum
    assunto: Optional[str] = Field(None, max_length=200)
    template_texto: str = Field(..., min_length=1)
    template_html: Optional[str] = None
    ativo: bool = True
    automatico: bool = False
    variaveis_disponiveis: Optional[Dict[str, Any]] = None
    configuracoes_canal: Optional[Dict[str, Any]] = None

class ComunicacaoTemplateCreate(ComunicacaoTemplateBase):
    criado_por: Optional[str] = None

class ComunicacaoTemplateUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[TipoTemplateEnum] = None
    canal: Optional[TipoComunicacaoEnum] = None
    assunto: Optional[str] = Field(None, max_length=200)
    template_texto: Optional[str] = Field(None, min_length=1)
    template_html: Optional[str] = None
    ativo: Optional[bool] = None
    automatico: Optional[bool] = None
    variaveis_disponiveis: Optional[Dict[str, Any]] = None
    configuracoes_canal: Optional[Dict[str, Any]] = None

class ComunicacaoTemplate(ComunicacaoTemplateBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    criado_por: Optional[str] = None

    class Config:
        from_attributes = True

# ================================
# SCHEMAS DE HISTÓRICO
# ================================

class ComunicacaoHistoricoBase(BaseModel):
    template_id: Optional[int] = None
    tipo: TipoComunicacaoEnum
    canal_usado: str = Field(..., min_length=1, max_length=50)
    destinatario_nome: str = Field(..., min_length=1, max_length=200)
    destinatario_contato: str = Field(..., min_length=1, max_length=100)
    cliente_id: Optional[int] = None
    assunto: Optional[str] = Field(None, max_length=200)
    conteudo_texto: str = Field(..., min_length=1)
    conteudo_html: Optional[str] = None
    origem_modulo: Optional[str] = Field(None, max_length=50)
    origem_id: Optional[int] = None

class ComunicacaoHistoricoCreate(ComunicacaoHistoricoBase):
    agendado_para: Optional[datetime] = None
    max_tentativas: int = Field(default=3, ge=1, le=10)

class ComunicacaoHistoricoUpdate(BaseModel):
    status: Optional[StatusComunicacaoEnum] = None
    tentativas_envio: Optional[int] = Field(None, ge=0)
    enviado_em: Optional[datetime] = None
    entregue_em: Optional[datetime] = None
    lido_em: Optional[datetime] = None
    provider_response: Optional[Dict[str, Any]] = None
    erro_detalhes: Optional[str] = None

class ComunicacaoHistorico(ComunicacaoHistoricoBase):
    id: int
    status: StatusComunicacaoEnum
    tentativas_envio: int
    max_tentativas: int
    agendado_para: Optional[datetime] = None
    enviado_em: Optional[datetime] = None
    entregue_em: Optional[datetime] = None
    lido_em: Optional[datetime] = None
    provider_response: Optional[Dict[str, Any]] = None
    erro_detalhes: Optional[str] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

# ================================
# SCHEMAS DE CONFIGURAÇÃO
# ================================

class ComunicacaoConfigBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: TipoComunicacaoEnum
    configuracoes: Dict[str, Any]
    ativo: bool = True
    padrao: bool = False
    limite_diario: Optional[int] = Field(None, ge=0)
    limite_mensal: Optional[int] = Field(None, ge=0)

class ComunicacaoConfigCreate(ComunicacaoConfigBase):
    criado_por: Optional[str] = None

class ComunicacaoConfigUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    configuracoes: Optional[Dict[str, Any]] = None
    ativo: Optional[bool] = None
    padrao: Optional[bool] = None
    limite_diario: Optional[int] = Field(None, ge=0)
    limite_mensal: Optional[int] = Field(None, ge=0)

class ComunicacaoConfig(ComunicacaoConfigBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    criado_por: Optional[str] = None

    class Config:
        from_attributes = True

# ================================
# SCHEMAS DE FILA
# ================================

class ComunicacaoFilaBase(BaseModel):
    template_id: Optional[int] = None
    prioridade: int = Field(default=5, ge=1, le=10)
    destinatario_nome: str = Field(..., min_length=1, max_length=200)
    destinatario_contato: str = Field(..., min_length=1, max_length=100)
    cliente_id: Optional[int] = None
    assunto: Optional[str] = Field(None, max_length=200)
    conteudo: str = Field(..., min_length=1)
    variaveis_contexto: Optional[Dict[str, Any]] = None
    origem_modulo: Optional[str] = Field(None, max_length=50)
    origem_id: Optional[int] = None

class ComunicacaoFilaCreate(ComunicacaoFilaBase):
    agendado_para: Optional[datetime] = None
    max_tentativas: int = Field(default=3, ge=1, le=10)

class ComunicacaoFilaUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=20)
    tentativas: Optional[int] = Field(None, ge=0)
    processado_em: Optional[datetime] = None
    erro_detalhes: Optional[str] = None

class ComunicacaoFila(ComunicacaoFilaBase):
    id: int
    status: str
    tentativas: int
    max_tentativas: int
    agendado_para: Optional[datetime] = None
    criado_em: datetime
    processado_em: Optional[datetime] = None
    erro_detalhes: Optional[str] = None

    class Config:
        from_attributes = True

# ================================
# SCHEMAS DE ENVIO
# ================================

class EnvioMensagemRequest(BaseModel):
    """Schema para requisição de envio de mensagem"""
    template_id: Optional[int] = None
    tipo_comunicacao: TipoComunicacaoEnum
    destinatario_nome: str = Field(..., min_length=1, max_length=200)
    destinatario_contato: str = Field(..., min_length=1, max_length=100)
    cliente_id: Optional[int] = None
    assunto: Optional[str] = Field(None, max_length=200)
    conteudo: Optional[str] = None
    variaveis: Optional[Dict[str, Any]] = None
    agendar_para: Optional[datetime] = None
    prioridade: int = Field(default=5, ge=1, le=10)
    origem_modulo: Optional[str] = Field(None, max_length=50)
    origem_id: Optional[int] = None

class EnvioMensagemResponse(BaseModel):
    """Schema para resposta de envio de mensagem"""
    sucesso: bool
    mensagem: str
    comunicacao_id: Optional[int] = None
    agendado: bool = False
    detalhes: Optional[Dict[str, Any]] = None

class EnvioLoteRequest(BaseModel):
    """Schema para envio em lote"""
    template_id: int
    destinatarios: List[Dict[str, Any]]
    variaveis_globais: Optional[Dict[str, Any]] = None
    agendar_para: Optional[datetime] = None
    prioridade: int = Field(default=5, ge=1, le=10)

class EnvioLoteResponse(BaseModel):
    """Schema para resposta de envio em lote"""
    total_processados: int
    sucessos: int
    erros: int
    detalhes: List[Dict[str, Any]]

# ================================
# SCHEMAS DE ESTATÍSTICAS
# ================================

class EstatisticasComunicacao(BaseModel):
    """Schema para estatísticas de comunicação"""
    periodo_inicio: datetime
    periodo_fim: datetime
    total_enviados: int
    total_entregues: int
    total_lidos: int
    total_erros: int
    
    # Por tipo
    email_estatisticas: Dict[str, int]
    whatsapp_estatisticas: Dict[str, int]
    sms_estatisticas: Dict[str, int]
    
    # Por módulo
    os_estatisticas: Dict[str, int]
    agendamento_estatisticas: Dict[str, int]
    financeiro_estatisticas: Dict[str, int]
    
    # Métricas
    taxa_entrega: float = Field(..., ge=0, le=1)
    taxa_leitura: float = Field(..., ge=0, le=1)
    taxa_erro: float = Field(..., ge=0, le=1)

class MetricasDashboard(BaseModel):
    """Schema para métricas do dashboard"""
    comunicacoes_hoje: int
    comunicacoes_semana: int
    comunicacoes_mes: int
    taxa_entrega_media: float
    templates_ativos: int
    configuracoes_ativas: int
    fila_pendente: int
    ultimas_comunicacoes: List[ComunicacaoHistorico]

# ================================
# SCHEMAS DE CONFIGURAÇÃO DE PROVEDORES
# ================================

class ConfiguracaoEmail(BaseModel):
    """Configuração específica para email"""
    servidor_smtp: str
    porta: int = Field(..., ge=1, le=65535)
    usuario: str
    senha: str
    usar_tls: bool = True
    usar_ssl: bool = False
    remetente_nome: str
    remetente_email: EmailStr

class ConfiguracaoWhatsApp(BaseModel):
    """Configuração específica para WhatsApp"""
    api_url: str
    token: str
    numero_remetente: str
    webhook_url: Optional[str] = None
    webhook_token: Optional[str] = None

class ConfiguracaoSMS(BaseModel):
    """Configuração específica para SMS"""
    provedor: str
    api_url: str
    usuario: str
    senha: str
    remetente: str

# ================================
# SCHEMAS DE RESPOSTA PADRÃO
# ================================

class ComunicacaoResponse(BaseModel):
    """Schema de resposta padrão"""
    sucesso: bool
    mensagem: str
    dados: Optional[Any] = None
    erro: Optional[str] = None

class ListaComunicacoes(BaseModel):
    """Schema para lista paginada"""
    items: List[ComunicacaoHistorico]
    total: int
    pagina: int
    tamanho_pagina: int
    total_paginas: int

class ListaTemplates(BaseModel):
    """Schema para lista de templates"""
    items: List[ComunicacaoTemplate]
    total: int
    pagina: int
    tamanho_pagina: int
    total_paginas: int