"""
Schemas Pydantic para sistema de Agendamento
Sistema ERP Primotex - Fase 3

Schemas de validação para:
- Agendamento
- ConfiguracaoAgenda
- DisponibilidadeUsuario
- BloqueioAgenda
"""

from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, validator, root_validator
from pydantic.config import ConfigDict


# ================================
# ENUMS E CONSTANTES
# ================================

# Constantes para descrições
ID_USUARIO_DESC = "ID do usuário"
ID_CLIENTE_DESC = "ID do cliente"
DATA_INICIO_DESC = "Data/hora de início"
DATA_FIM_DESC = "Data/hora de fim"
OBSERVACOES_DESC = "Observações adicionais"

class StatusAgendamento(str, Enum):
    """Status do agendamento"""
    AGENDADO = "agendado"
    CONFIRMADO = "confirmado" 
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"
    REAGENDADO = "reagendado"


class TipoAgendamento(str, Enum):
    """Tipo de agendamento"""
    VISITA_TECNICA = "visita_tecnica"
    INSTALACAO = "instalacao"
    MANUTENCAO = "manutencao"
    REUNIAO = "reuniao"
    ENTREGA = "entrega"
    OUTROS = "outros"


class DiaSemana(str, Enum):
    """Dias da semana"""
    SEGUNDA = "segunda"
    TERCA = "terca"
    QUARTA = "quarta"
    QUINTA = "quinta"
    SEXTA = "sexta"
    SABADO = "sabado"
    DOMINGO = "domingo"


class TipoBloqueio(str, Enum):
    """Tipo de bloqueio de agenda"""
    FERIAS = "ferias"
    FERIADO = "feriado"
    REUNIAO_INTERNA = "reuniao_interna"
    TREINAMENTO = "treinamento"
    AUSENCIA = "ausencia"
    MANUTENCAO_SISTEMA = "manutencao_sistema"
    OUTROS = "outros"


# ================================
# SCHEMAS BASE
# ================================

class AgendamentoBase(BaseModel):
    """Schema base para agendamento"""
    data_agendamento: datetime = Field(..., description="Data e hora do agendamento")
    titulo: str = Field(..., min_length=3, max_length=200, description="Título do agendamento")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição detalhada")
    tipo: TipoAgendamento = Field(..., description="Tipo do agendamento")
    duracao_minutos: int = Field(default=60, ge=15, le=480, description="Duração em minutos")
    cliente_id: Optional[int] = Field(None, description="ID do cliente relacionado")
    ordem_servico_id: Optional[int] = Field(None, description="ID da OS relacionada")
    observacoes: Optional[str] = Field(None, max_length=500, description="Observações adicionais")
    
    @validator('data_agendamento')
    @classmethod
    def validar_data_futura(cls, v: datetime) -> datetime:
        """Valida se a data é futura (exceto para admins)"""
        if v and v < datetime.now():
            # Permitir datas passadas apenas para histórico/importação
            pass
        return v
    
    @validator('titulo')
    @classmethod
    def validar_titulo(cls, v: str) -> str:
        """Valida e formata título"""
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Título não pode ser vazio")
        return v


class ConfiguracaoAgendaBase(BaseModel):
    """Schema base para configuração de agenda"""
    usuario_id: int = Field(..., description=ID_USUARIO_DESC)
    horario_inicio: time = Field(..., description="Horário de início do expediente")
    horario_fim: time = Field(..., description="Horário de fim do expediente")
    dias_trabalho: List[DiaSemana] = Field(..., description="Dias de trabalho")
    intervalo_agendamento: int = Field(default=30, ge=15, le=120, description="Intervalo mínimo entre agendamentos (minutos)")
    maximo_agendamentos_dia: int = Field(default=10, ge=1, le=50, description="Máximo de agendamentos por dia")
    antecedencia_minima: int = Field(default=60, ge=0, le=2880, description="Antecedência mínima para agendamento (minutos)")
    permite_fins_semana: bool = Field(default=False, description="Permite agendamentos em fins de semana")
    
    @validator('horario_fim')
    @classmethod
    def validar_horarios(cls, v: time, values) -> time:
        """Valida se horário fim é posterior ao início"""
        if 'horario_inicio' in values and v <= values['horario_inicio']:
            raise ValueError("Horário de fim deve ser posterior ao de início")
        return v
    
    @validator('dias_trabalho')
    @classmethod
    def validar_dias_trabalho(cls, v: List[DiaSemana]) -> List[DiaSemana]:
        """Valida dias de trabalho"""
        if not v:
            raise ValueError("Deve ter pelo menos um dia de trabalho")
        return list(set(v))  # Remove duplicatas


class DisponibilidadeUsuarioBase(BaseModel):
    """Schema base para disponibilidade específica"""
    usuario_id: int = Field(..., description=ID_USUARIO_DESC)
    data_inicio: datetime = Field(..., description=DATA_INICIO_DESC)
    data_fim: datetime = Field(..., description=DATA_FIM_DESC)
    disponivel: bool = Field(..., description="Se está disponível ou não")
    motivo: Optional[str] = Field(None, max_length=200, description="Motivo da indisponibilidade")
    
    @validator('data_fim')
    @classmethod
    def validar_periodo(cls, v: datetime, values) -> datetime:
        """Valida se data fim é posterior ao início"""
        if 'data_inicio' in values and v <= values['data_inicio']:
            raise ValueError("Data fim deve ser posterior à data início")
        return v
    
    @root_validator(pre=True)
    def validar_motivo_indisponibilidade(cls, values):
        """Valida motivo para indisponibilidades"""
        if not values.get('disponivel') and not values.get('motivo'):
            raise ValueError("Motivo é obrigatório para indisponibilidades")
        return values


class BloqueioAgendaBase(BaseModel):
    """Schema base para bloqueio de agenda"""
    titulo: str = Field(..., min_length=3, max_length=200, description="Título do bloqueio")
    descricao: Optional[str] = Field(None, max_length=500, description="Descrição do bloqueio")
    data_inicio: datetime = Field(..., description="Data/hora de início do bloqueio")
    data_fim: datetime = Field(..., description="Data/hora de fim do bloqueio")
    tipo: TipoBloqueio = Field(..., description="Tipo do bloqueio")
    afeta_todos_usuarios: bool = Field(default=False, description="Se afeta todos os usuários")
    usuarios_afetados: Optional[List[int]] = Field(None, description="IDs dos usuários afetados")
    
    @validator('data_fim')
    @classmethod
    def validar_periodo_bloqueio(cls, v: datetime, values) -> datetime:
        """Valida período do bloqueio"""
        if 'data_inicio' in values and v <= values['data_inicio']:
            raise ValueError("Data fim deve ser posterior à data início")
        return v
    
    @root_validator(pre=True)
    def validar_usuarios_bloqueio(cls, values):
        """Valida usuários afetados pelo bloqueio"""
        if not values.get('afeta_todos_usuarios') and not values.get('usuarios_afetados'):
            raise ValueError("Deve especificar usuários afetados ou marcar como global")
        return values


# ================================
# SCHEMAS CREATE
# ================================

class AgendamentoCreate(AgendamentoBase):
    """Schema para criação de agendamento"""
    usuario_responsavel_id: int = Field(..., description="ID do usuário responsável")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "data_agendamento": "2024-12-01T14:30:00",
                "titulo": "Visita técnica - Instalação forro PVC",
                "descricao": "Instalação de forro PVC no escritório",
                "tipo": "visita_tecnica",
                "duracao_minutos": 120,
                "usuario_responsavel_id": 1,
                "cliente_id": 1,
                "ordem_servico_id": 1,
                "observacoes": "Cliente prefere período da tarde"
            }
        }
    )


class ConfiguracaoAgendaCreate(ConfiguracaoAgendaBase):
    """Schema para criação de configuração de agenda"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "usuario_id": 1,
                "horario_inicio": "08:00:00",
                "horario_fim": "18:00:00",
                "dias_trabalho": ["segunda", "terca", "quarta", "quinta", "sexta"],
                "intervalo_agendamento": 30,
                "maximo_agendamentos_dia": 12,
                "antecedencia_minima": 120,
                "permite_fins_semana": False
            }
        }
    )


class DisponibilidadeUsuarioCreate(DisponibilidadeUsuarioBase):
    """Schema para criação de disponibilidade específica"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "usuario_id": 1,
                "data_inicio": "2024-12-01T08:00:00",
                "data_fim": "2024-12-01T18:00:00",
                "disponivel": True,
                "motivo": None
            }
        }
    )


class BloqueioAgendaCreate(BloqueioAgendaBase):
    """Schema para criação de bloqueio de agenda"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "titulo": "Férias de fim de ano",
                "descricao": "Período de férias coletivas",
                "data_inicio": "2024-12-23T00:00:00",
                "data_fim": "2024-01-07T23:59:59",
                "tipo": "ferias",
                "afeta_todos_usuarios": True,
                "usuarios_afetados": None
            }
        }
    )


# ================================
# SCHEMAS UPDATE
# ================================

class AgendamentoUpdate(BaseModel):
    """Schema para atualização de agendamento"""
    data_agendamento: Optional[datetime] = None
    titulo: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = Field(None, max_length=1000)
    tipo: Optional[TipoAgendamento] = None
    status: Optional[StatusAgendamento] = None
    duracao_minutos: Optional[int] = Field(None, ge=15, le=480)
    usuario_responsavel_id: Optional[int] = None
    cliente_id: Optional[int] = None
    ordem_servico_id: Optional[int] = None
    observacoes: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(from_attributes=True)


class ConfiguracaoAgendaUpdate(BaseModel):
    """Schema para atualização de configuração de agenda"""
    horario_inicio: Optional[time] = None
    horario_fim: Optional[time] = None
    dias_trabalho: Optional[List[DiaSemana]] = None
    intervalo_agendamento: Optional[int] = Field(None, ge=15, le=120)
    maximo_agendamentos_dia: Optional[int] = Field(None, ge=1, le=50)
    antecedencia_minima: Optional[int] = Field(None, ge=0, le=2880)
    permite_fins_semana: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


class DisponibilidadeUsuarioUpdate(BaseModel):
    """Schema para atualização de disponibilidade"""
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    disponivel: Optional[bool] = None
    motivo: Optional[str] = Field(None, max_length=200)
    
    model_config = ConfigDict(from_attributes=True)


class BloqueioAgendaUpdate(BaseModel):
    """Schema para atualização de bloqueio"""
    titulo: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = Field(None, max_length=500)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    tipo: Optional[TipoBloqueio] = None
    afeta_todos_usuarios: Optional[bool] = None
    usuarios_afetados: Optional[List[int]] = None
    ativo: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


# ================================
# SCHEMAS RESPONSE
# ================================

class AgendamentoResponse(AgendamentoBase):
    """Schema de resposta para agendamento"""
    id: int
    status: StatusAgendamento
    usuario_responsavel_id: int
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None
    
    # Relacionamentos
    cliente_nome: Optional[str] = None
    usuario_responsavel_nome: Optional[str] = None
    ordem_servico_numero: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ConfiguracaoAgendaResponse(ConfiguracaoAgendaBase):
    """Schema de resposta para configuração de agenda"""
    id: int
    ativo: bool
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None
    
    # Relacionamento
    usuario_nome: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class DisponibilidadeUsuarioResponse(DisponibilidadeUsuarioBase):
    """Schema de resposta para disponibilidade"""
    id: int
    data_criacao: datetime
    
    # Relacionamento
    usuario_nome: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class BloqueioAgendaResponse(BloqueioAgendaBase):
    """Schema de resposta para bloqueio"""
    id: int
    ativo: bool
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ================================
# SCHEMAS ESPECIAIS
# ================================

class AgendamentoFilter(BaseModel):
    """Schema para filtros de agendamento"""
    data_inicio: Optional[date] = Field(None, description="Data de início do período")
    data_fim: Optional[date] = Field(None, description="Data de fim do período")
    usuario_id: Optional[int] = Field(None, description="ID do usuário")
    cliente_id: Optional[int] = Field(None, description="ID do cliente")
    status: Optional[List[StatusAgendamento]] = Field(None, description="Status do agendamento")
    tipo: Optional[List[TipoAgendamento]] = Field(None, description="Tipos de agendamento")
    
    model_config = ConfigDict(from_attributes=True)


class DisponibilidadeConsulta(BaseModel):
    """Schema para consulta de disponibilidade"""
    usuario_id: int = Field(..., description=ID_USUARIO_DESC)
    data_inicio: datetime = Field(..., description=DATA_INICIO_DESC)
    data_fim: datetime = Field(..., description=DATA_FIM_DESC)
    duracao_minutos: int = Field(..., ge=15, le=480, description="Duração desejada em minutos")
    
    model_config = ConfigDict(from_attributes=True)


class HorarioDisponivel(BaseModel):
    """Schema para horário disponível"""
    data_hora: datetime = Field(..., description="Data e hora disponível")
    duracao_maxima: int = Field(..., description="Duração máxima possível em minutos")
    
    model_config = ConfigDict(from_attributes=True)


class CalendarioResponse(BaseModel):
    """Schema de resposta para calendário"""
    data: date = Field(..., description="Data do calendário")
    agendamentos: List[AgendamentoResponse] = Field(default_factory=list)
    bloqueios: List[BloqueioAgendaResponse] = Field(default_factory=list)
    disponibilidades: List[DisponibilidadeUsuarioResponse] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class AgendamentoListResponse(BaseModel):
    """Schema de resposta para listagem de agendamentos"""
    items: List[AgendamentoResponse]
    total: int
    page: int
    size: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True)


class EstatisticasAgendamento(BaseModel):
    """Schema para estatísticas de agendamento"""
    total_agendamentos: int = 0
    agendamentos_hoje: int = 0
    agendamentos_semana: int = 0
    agendamentos_mes: int = 0
    por_status: Dict[str, int] = Field(default_factory=dict)
    por_tipo: Dict[str, int] = Field(default_factory=dict)
    taxa_confirmacao: float = 0.0
    
    model_config = ConfigDict(from_attributes=True)


# ================================
# SCHEMAS DE INTEGRAÇÃO
# ================================

class AgendamentoIntegracaoOS(BaseModel):
    """Schema para integração agendamento-OS"""
    ordem_servico_id: int = Field(..., description="ID da ordem de serviço")
    tipo_agendamento: TipoAgendamento = Field(..., description="Tipo do agendamento")
    data_preferida: Optional[datetime] = Field(None, description="Data preferida pelo cliente")
    usuario_responsavel_id: Optional[int] = Field(None, description="ID do usuário responsável")
    observacoes: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(from_attributes=True)


class NotificacaoAgendamento(BaseModel):
    """Schema para notificações de agendamento"""
    agendamento_id: int = Field(..., description="ID do agendamento")
    tipo_notificacao: str = Field(..., description="Tipo da notificação")
    destinatarios: List[str] = Field(..., description="Lista de destinatários")
    mensagem: str = Field(..., description="Mensagem da notificação")
    data_envio: Optional[datetime] = Field(None, description="Data de envio programada")
    
    model_config = ConfigDict(from_attributes=True)


# ================================
# EXPORTS
# ================================

__all__ = [
    # Enums
    'StatusAgendamento',
    'TipoAgendamento', 
    'DiaSemana',
    'TipoBloqueio',
    
    # Schemas Create
    'AgendamentoCreate',
    'ConfiguracaoAgendaCreate',
    'DisponibilidadeUsuarioCreate',
    'BloqueioAgendaCreate',
    
    # Schemas Update
    'AgendamentoUpdate',
    'ConfiguracaoAgendaUpdate',
    'DisponibilidadeUsuarioUpdate',
    'BloqueioAgendaUpdate',
    
    # Schemas Response
    'AgendamentoResponse',
    'ConfiguracaoAgendaResponse',
    'DisponibilidadeUsuarioResponse',
    'BloqueioAgendaResponse',
    
    # Schemas Especiais
    'AgendamentoFilter',
    'DisponibilidadeConsulta',
    'HorarioDisponivel',
    'CalendarioResponse',
    'AgendamentoListResponse',
    'EstatisticasAgendamento',
    'AgendamentoIntegracaoOS',
    'NotificacaoAgendamento'
]