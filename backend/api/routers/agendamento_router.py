"""
Router FastAPI para sistema de Agendamento
Sistema ERP Primotex - Fase 3

Endpoints para:
- CRUD de Agendamentos
- Configurações de Agenda
- Disponibilidade de Usuários
- Bloqueios de Agenda
- Calendário Integrado
- Consulta de Disponibilidade
"""

from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract

from backend.database.config import get_db
from backend.models.agendamento_model import (
    Agendamento, ConfiguracaoAgenda, DisponibilidadeUsuario, BloqueioAgenda
)
from backend.models.cliente_model import Cliente
from backend.models.ordem_servico_model import OrdemServico
from backend.models.user_model import Usuario
from backend.auth.dependencies import get_current_user
from backend.schemas.agendamento_schemas import (
    # Create schemas
    AgendamentoCreate, ConfiguracaoAgendaCreate, 
    DisponibilidadeUsuarioCreate, BloqueioAgendaCreate,

    # Update schemas
    AgendamentoUpdate, ConfiguracaoAgendaUpdate,
    DisponibilidadeUsuarioUpdate, BloqueioAgendaUpdate,

    # Response schemas
    AgendamentoResponse, ConfiguracaoAgendaResponse,
    DisponibilidadeUsuarioResponse, BloqueioAgendaResponse,
    AgendamentoListResponse, CalendarioResponse,

    # Special schemas
    AgendamentoFilter, DisponibilidadeConsulta, HorarioDisponivel,
    EstatisticasAgendamento, AgendamentoIntegracaoOS,

    # Enums
    StatusAgendamento, TipoAgendamento, DiaSemana, TipoBloqueio
)

# Configurar logging
logger = logging.getLogger(__name__)

# Constantes para mensagens e descrições
ID_USUARIO_DESC = "ID do usuário"
ID_AGENDAMENTO_DESC = "ID do agendamento"
ERRO_INTERNO_MSG = "Erro interno do servidor"
AGENDAMENTO_NAO_ENCONTRADO_MSG = "Agendamento não encontrado"
CLIENTE_NAO_ENCONTRADO_MSG = "Cliente não encontrado"
OS_NAO_ENCONTRADA_MSG = "Ordem de serviço não encontrada"
CONFIG_NAO_ENCONTRADA_MSG = "Configuração não encontrada"

# Criar router
router = APIRouter(
    prefix="/agendamento",
    tags=["Agendamento"],
    responses={404: {"description": "Not found"}}
)


# ================================
# HELPER FUNCTIONS
# ================================

def _apply_agendamento_filters(query, filters: AgendamentoFilter):
    """Aplica filtros na query de agendamentos"""
    if filters.data_inicio:
        query = query.filter(
            func.date(Agendamento.data_agendamento) >= filters.data_inicio
        )

    if filters.data_fim:
        query = query.filter(
            func.date(Agendamento.data_agendamento) <= filters.data_fim
        )

    if filters.usuario_id:
        query = query.filter(Agendamento.usuario_responsavel_id == filters.usuario_id)

    if filters.cliente_id:
        query = query.filter(Agendamento.cliente_id == filters.cliente_id)

    if filters.status:
        query = query.filter(Agendamento.status.in_(filters.status))

    if filters.tipo:
        query = query.filter(Agendamento.tipo.in_(filters.tipo))

    return query


def _verificar_conflito_agendamento(
    db: Session, 
    data_agendamento: datetime, 
    duracao_minutos: int,
    usuario_id: int,
    agendamento_id: Optional[int] = None
) -> bool:
    """Verifica se há conflito de agendamento"""
    data_fim = data_agendamento.replace(
        minute=data_agendamento.minute + duracao_minutos
    )

    query = db.query(Agendamento).filter(
        Agendamento.usuario_responsavel_id == usuario_id,
        Agendamento.status != StatusAgendamento.CANCELADO,
        or_(
            and_(
                Agendamento.data_agendamento <= data_agendamento,
                func.datetime(
                    Agendamento.data_agendamento, 
                    '+' + func.cast(Agendamento.duracao_minutos, str) + ' minutes'
                ) > data_agendamento
            ),
            and_(
                Agendamento.data_agendamento < data_fim,
                func.datetime(
                    Agendamento.data_agendamento,
                    '+' + func.cast(Agendamento.duracao_minutos, str) + ' minutes'
                ) >= data_fim
            )
        )
    )

    if agendamento_id:
        query = query.filter(Agendamento.id != agendamento_id)

    return query.first() is not None


def _verificar_disponibilidade_usuario(
    db: Session,
    usuario_id: int,
    data_inicio: datetime,
    data_fim: datetime
) -> bool:
    """Verifica disponibilidade específica do usuário"""
    # Verificar indisponibilidades específicas
    indisponibilidade = db.query(DisponibilidadeUsuario).filter(
        DisponibilidadeUsuario.usuario_id == usuario_id,
        DisponibilidadeUsuario.disponivel == False,
        DisponibilidadeUsuario.data_inicio <= data_fim,
        DisponibilidadeUsuario.data_fim >= data_inicio
    ).first()

    return indisponibilidade is None


def _verificar_bloqueios_agenda(
    db: Session,
    usuario_id: int,
    data_inicio: datetime,
    data_fim: datetime
) -> bool:
    """Verifica se há bloqueios de agenda"""
    bloqueio = db.query(BloqueioAgenda).filter(
        BloqueioAgenda.ativo == True,
        BloqueioAgenda.data_inicio <= data_fim,
        BloqueioAgenda.data_fim >= data_inicio,
        or_(
            BloqueioAgenda.afeta_todos_usuarios == True,
            BloqueioAgenda.usuarios_afetados.contains(str(usuario_id))
        )
    ).first()

    return bloqueio is None


# ================================
# ENDPOINTS DE AGENDAMENTOS
# ================================

@router.get("/", response_model=AgendamentoListResponse)
async def listar_agendamentos(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    data_inicio: Optional[date] = Query(None, description="Data de início do filtro"),
    data_fim: Optional[date] = Query(None, description="Data de fim do filtro"),
    usuario_id: Optional[int] = Query(None, description=ID_USUARIO_DESC),
    cliente_id: Optional[int] = Query(None, description="ID do cliente"),
    status: Optional[List[StatusAgendamento]] = Query(None, description="Status do agendamento"),
    tipo: Optional[List[TipoAgendamento]] = Query(None, description="Tipo do agendamento"),
    db: Session = Depends(get_db)
):
    """Lista agendamentos com filtros opcionais"""
    try:
        # Criar filtros
        filters = AgendamentoFilter(
            data_inicio=data_inicio,
            data_fim=data_fim,
            usuario_id=usuario_id,
            cliente_id=cliente_id,
            status=status,
            tipo=tipo
        )

        # Query base
        query = db.query(Agendamento)

        # Aplicar filtros
        query = _apply_agendamento_filters(query, filters)

        # Contar total
        total = query.count()

        # Aplicar paginação e ordenação
        agendamentos = query.order_by(Agendamento.data_agendamento.desc())\
                           .offset(skip)\
                           .limit(limit)\
                           .all()

        # Calcular páginas
        pages = (total + limit - 1) // limit

        return AgendamentoListResponse(
            items=agendamentos,
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=pages
        )

    except Exception as e:
        logger.error(f"Erro ao listar agendamentos: {e}")
        raise HTTPException(status_code=500, detail=ERRO_INTERNO_MSG)


# ================================
# ENDPOINT DE DASHBOARD (deve vir antes de /{agendamento_id})
# ================================

@router.get("/dashboard")
async def obter_dashboard_agendamento(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna dados resumidos para o dashboard principal.
    Inclui agendamentos de hoje e da semana.
    """
    try:
        hoje = datetime.now().date()
        fim_semana = hoje + timedelta(days=7)

        # Agendamentos de hoje
        agend_hoje = db.query(Agendamento).filter(
            func.date(Agendamento.data_hora_inicio) == hoje,
            Agendamento.ativo == True
        ).count()

        # Agendamentos da semana
        agend_semana = db.query(Agendamento).filter(
            func.date(Agendamento.data_hora_inicio) >= hoje,
            func.date(Agendamento.data_hora_inicio) <= fim_semana,
            Agendamento.ativo == True
        ).count()

        # Próximos 5 eventos
        proximos_eventos = db.query(Agendamento).filter(
            Agendamento.data_hora_inicio >= datetime.now(),
            Agendamento.ativo == True
        ).order_by(Agendamento.data_hora_inicio).limit(5).all()

        return {
            "agendamentos_hoje": agend_hoje,
            "agendamentos_semana": agend_semana,
            "proximos_eventos": [
                {
                    "id": ag.id,
                    "titulo": ag.titulo,
                    "data_hora": ag.data_hora_inicio.isoformat(),
                    "tipo": ag.tipo_agendamento,
                    "cliente_nome": ag.cliente.nome if ag.cliente else None
                }
                for ag in proximos_eventos
            ],
            "data_atualizacao": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar dados do dashboard: {str(e)}"
        )


@router.get("/{agendamento_id}", response_model=AgendamentoResponse)
async def obter_agendamento(
    agendamento_id: int = Path(..., description=ID_AGENDAMENTO_DESC),
    db: Session = Depends(get_db)
):
    """Obtém um agendamento específico"""
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()

    if not agendamento:
        raise HTTPException(status_code=404, detail=AGENDAMENTO_NAO_ENCONTRADO_MSG)

    return agendamento


@router.post("/", response_model=AgendamentoResponse, status_code=201)
async def criar_agendamento(
    agendamento_data: AgendamentoCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo agendamento"""
    try:
        # Verificar se cliente existe
        if agendamento_data.cliente_id:
            cliente = db.query(Cliente).filter(Cliente.id == agendamento_data.cliente_id).first()
            if not cliente:
                raise HTTPException(status_code=404, detail=CLIENTE_NAO_ENCONTRADO_MSG)

        # Verificar se OS existe
        if agendamento_data.ordem_servico_id:
            os = db.query(OrdemServico).filter(OrdemServico.id == agendamento_data.ordem_servico_id).first()
            if not os:
                raise HTTPException(status_code=404, detail=OS_NAO_ENCONTRADA_MSG)

        # Verificar conflitos de agendamento
        if _verificar_conflito_agendamento(
            db, 
            agendamento_data.data_agendamento,
            agendamento_data.duracao_minutos,
            agendamento_data.usuario_responsavel_id
        ):
            raise HTTPException(
                status_code=409, 
                detail="Conflito de agendamento: já existe um agendamento neste horário"
            )

        # Verificar disponibilidade do usuário
        data_fim = agendamento_data.data_agendamento.replace(
            minute=agendamento_data.data_agendamento.minute + agendamento_data.duracao_minutos
        )

        if not _verificar_disponibilidade_usuario(
            db,
            agendamento_data.usuario_responsavel_id,
            agendamento_data.data_agendamento,
            data_fim
        ):
            raise HTTPException(
                status_code=409,
                detail="Usuário indisponível no horário solicitado"
            )

        # Verificar bloqueios de agenda
        if not _verificar_bloqueios_agenda(
            db,
            agendamento_data.usuario_responsavel_id,
            agendamento_data.data_agendamento,
            data_fim
        ):
            raise HTTPException(
                status_code=409,
                detail="Horário bloqueado na agenda"
            )

        # Criar agendamento
        agendamento = Agendamento(
            **agendamento_data.model_dump(),
            status=StatusAgendamento.AGENDADO
        )

        db.add(agendamento)
        db.commit()
        db.refresh(agendamento)

        logger.info(f"Agendamento criado: ID {agendamento.id}")
        return agendamento

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar agendamento: {e}")
        raise HTTPException(status_code=500, detail=ERRO_INTERNO_MSG)


@router.put("/{agendamento_id}", response_model=AgendamentoResponse)
async def atualizar_agendamento(
    agendamento_id: int = Path(..., description="ID do agendamento"),
    agendamento_data: AgendamentoUpdate = None,
    db: Session = Depends(get_db)
):
    """Atualiza um agendamento existente"""
    try:
        agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()

        if not agendamento:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")

        # Verificar se há mudança de horário/duração
        if (agendamento_data.data_agendamento or agendamento_data.duracao_minutos or 
            agendamento_data.usuario_responsavel_id):

            nova_data = agendamento_data.data_agendamento or agendamento.data_agendamento
            nova_duracao = agendamento_data.duracao_minutos or agendamento.duracao_minutos
            novo_usuario = agendamento_data.usuario_responsavel_id or agendamento.usuario_responsavel_id

            # Verificar conflitos
            if _verificar_conflito_agendamento(
                db, nova_data, nova_duracao, novo_usuario, agendamento_id
            ):
                raise HTTPException(
                    status_code=409,
                    detail="Conflito de agendamento: já existe um agendamento neste horário"
                )

        # Atualizar campos
        update_data = agendamento_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agendamento, field, value)

        agendamento.data_atualizacao = datetime.now()

        db.commit()
        db.refresh(agendamento)

        logger.info(f"Agendamento atualizado: ID {agendamento.id}")
        return agendamento

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar agendamento: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.delete("/{agendamento_id}")
async def deletar_agendamento(
    agendamento_id: int = Path(..., description="ID do agendamento"),
    db: Session = Depends(get_db)
):
    """Deleta um agendamento"""
    try:
        agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()

        if not agendamento:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")

        db.delete(agendamento)
        db.commit()

        logger.info(f"Agendamento deletado: ID {agendamento_id}")
        return {"message": "Agendamento deletado com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar agendamento: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ================================
# ENDPOINTS DE STATUS
# ================================

@router.patch("/{agendamento_id}/status")
async def alterar_status_agendamento(
    agendamento_id: int = Path(..., description="ID do agendamento"),
    novo_status: StatusAgendamento = Query(..., description="Novo status"),
    observacoes: Optional[str] = Query(None, description="Observações da mudança"),
    db: Session = Depends(get_db)
):
    """Altera o status de um agendamento"""
    try:
        agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()

        if not agendamento:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")

        status_anterior = agendamento.status
        agendamento.status = novo_status
        agendamento.data_atualizacao = datetime.now()

        if observacoes:
            agendamento.observacoes = f"{agendamento.observacoes or ''}\n[{datetime.now().strftime('%d/%m/%Y %H:%M')}] Status alterado de {status_anterior} para {novo_status}: {observacoes}".strip()

        db.commit()
        db.refresh(agendamento)

        logger.info(f"Status do agendamento {agendamento_id} alterado de {status_anterior} para {novo_status}")
        return agendamento

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao alterar status do agendamento: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ================================
# ENDPOINTS DE CONFIGURAÇÃO
# ================================

@router.get("/configuracao/", response_model=List[ConfiguracaoAgendaResponse])
async def listar_configuracoes_agenda(
    usuario_id: Optional[int] = Query(None, description="ID do usuário"),
    ativo: bool = Query(True, description="Apenas configurações ativas"),
    db: Session = Depends(get_db)
):
    """Lista configurações de agenda"""
    query = db.query(ConfiguracaoAgenda)

    if usuario_id:
        query = query.filter(ConfiguracaoAgenda.usuario_id == usuario_id)

    if ativo:
        query = query.filter(ConfiguracaoAgenda.ativo == True)

    return query.all()


@router.post("/configuracao/", response_model=ConfiguracaoAgendaResponse, status_code=201)
async def criar_configuracao_agenda(
    config_data: ConfiguracaoAgendaCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova configuração de agenda"""
    try:
        # Verificar se já existe configuração ativa para o usuário
        config_existente = db.query(ConfiguracaoAgenda).filter(
            ConfiguracaoAgenda.usuario_id == config_data.usuario_id,
            ConfiguracaoAgenda.ativo == True
        ).first()

        if config_existente:
            # Desativar configuração anterior
            config_existente.ativo = False
            config_existente.data_atualizacao = datetime.now()

        # Criar nova configuração
        configuracao = ConfiguracaoAgenda(**config_data.model_dump())

        db.add(configuracao)
        db.commit()
        db.refresh(configuracao)

        logger.info(f"Configuração de agenda criada: ID {configuracao.id}")
        return configuracao

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar configuração de agenda: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.put("/configuracao/{config_id}", response_model=ConfiguracaoAgendaResponse)
async def atualizar_configuracao_agenda(
    config_id: int = Path(..., description="ID da configuração"),
    config_data: ConfiguracaoAgendaUpdate = None,
    db: Session = Depends(get_db)
):
    """Atualiza uma configuração de agenda"""
    try:
        configuracao = db.query(ConfiguracaoAgenda).filter(ConfiguracaoAgenda.id == config_id).first()

        if not configuracao:
            raise HTTPException(status_code=404, detail="Configuração não encontrada")

        # Atualizar campos
        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(configuracao, field, value)

        configuracao.data_atualizacao = datetime.now()

        db.commit()
        db.refresh(configuracao)

        logger.info(f"Configuração de agenda atualizada: ID {configuracao.id}")
        return configuracao

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar configuração de agenda: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ================================
# ENDPOINTS DE DISPONIBILIDADE
# ================================

def _gerar_horarios_dia(
    db: Session,
    data: date,
    config: ConfiguracaoAgenda,
    consulta: DisponibilidadeConsulta
) -> List[HorarioDisponivel]:
    """Gera horários disponíveis para um dia específico"""
    horarios_disponiveis = []

    # Verificar se é dia de trabalho
    dia_semana = DiaSemana(data.strftime('%A').lower())
    if dia_semana not in config.dias_trabalho:
        return horarios_disponiveis

    # Gerar horários para o dia
    hora_inicio = datetime.combine(data, config.horario_inicio)
    hora_fim = datetime.combine(data, config.horario_fim)

    hora_atual = hora_inicio
    while hora_atual + timedelta(minutes=consulta.duracao_minutos) <= hora_fim:
        data_fim_slot = hora_atual + timedelta(minutes=consulta.duracao_minutos)

        # Verificar todas as condições
        if (_verifica_slot_disponivel(db, hora_atual, data_fim_slot, consulta)):
            horarios_disponiveis.append(
                HorarioDisponivel(
                    data_hora=hora_atual,
                    duracao_maxima=consulta.duracao_minutos
                )
            )

        hora_atual += timedelta(minutes=config.intervalo_agendamento)

    return horarios_disponiveis


def _verifica_slot_disponivel(
    db: Session,
    hora_inicio: datetime,
    hora_fim: datetime,
    consulta: DisponibilidadeConsulta
) -> bool:
    """Verifica se um slot de horário está disponível"""
    # Verificar conflitos de agendamento
    if _verificar_conflito_agendamento(
        db, hora_inicio, consulta.duracao_minutos, consulta.usuario_id
    ):
        return False

    # Verificar disponibilidade específica
    if not _verificar_disponibilidade_usuario(
        db, consulta.usuario_id, hora_inicio, hora_fim
    ):
        return False

    # Verificar bloqueios
    if not _verificar_bloqueios_agenda(
        db, consulta.usuario_id, hora_inicio, hora_fim
    ):
        return False

    return True


@router.post("/disponibilidade/consultar", response_model=List[HorarioDisponivel])
async def consultar_disponibilidade(
    consulta: DisponibilidadeConsulta,
    db: Session = Depends(get_db)
):
    """Consulta horários disponíveis para agendamento"""
    try:
        # Obter configuração do usuário
        config = db.query(ConfiguracaoAgenda).filter(
            ConfiguracaoAgenda.usuario_id == consulta.usuario_id,
            ConfiguracaoAgenda.ativo == True
        ).first()

        if not config:
            return []

        horarios_disponiveis = []
        data_atual = consulta.data_inicio.date()
        data_final = consulta.data_fim.date()

        # Iterar pelos dias no período solicitado
        while data_atual <= data_final:
            horarios_dia = _gerar_horarios_dia(db, data_atual, config, consulta)
            horarios_disponiveis.extend(horarios_dia)
            data_atual += timedelta(days=1)

        return horarios_disponiveis[:50]  # Limitar a 50 horários

    except Exception as e:
        logger.error(f"Erro ao consultar disponibilidade: {e}")
        raise HTTPException(status_code=500, detail=ERRO_INTERNO_MSG)


@router.post("/disponibilidade/", response_model=DisponibilidadeUsuarioResponse, status_code=201)
async def criar_disponibilidade(
    disponibilidade_data: DisponibilidadeUsuarioCreate,
    db: Session = Depends(get_db)
):
    """Cria uma disponibilidade específica"""
    try:
        disponibilidade = DisponibilidadeUsuario(**disponibilidade_data.model_dump())

        db.add(disponibilidade)
        db.commit()
        db.refresh(disponibilidade)

        logger.info(f"Disponibilidade criada: ID {disponibilidade.id}")
        return disponibilidade

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar disponibilidade: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ================================
# ENDPOINTS DE BLOQUEIOS
# ================================

@router.get("/bloqueios/", response_model=List[BloqueioAgendaResponse])
async def listar_bloqueios(
    ativo: bool = Query(True, description="Apenas bloqueios ativos"),
    data_inicio: Optional[date] = Query(None, description="Data de início do filtro"),
    data_fim: Optional[date] = Query(None, description="Data de fim do filtro"),
    db: Session = Depends(get_db)
):
    """Lista bloqueios de agenda"""
    query = db.query(BloqueioAgenda)

    if ativo:
        query = query.filter(BloqueioAgenda.ativo == True)

    if data_inicio:
        query = query.filter(BloqueioAgenda.data_fim >= data_inicio)

    if data_fim:
        query = query.filter(BloqueioAgenda.data_inicio <= data_fim)

    return query.order_by(BloqueioAgenda.data_inicio).all()


@router.post("/bloqueios/", response_model=BloqueioAgendaResponse, status_code=201)
async def criar_bloqueio(
    bloqueio_data: BloqueioAgendaCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo bloqueio de agenda"""
    try:
        bloqueio = BloqueioAgenda(**bloqueio_data.model_dump())

        db.add(bloqueio)
        db.commit()
        db.refresh(bloqueio)

        logger.info(f"Bloqueio de agenda criado: ID {bloqueio.id}")
        return bloqueio

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar bloqueio: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ================================
# ENDPOINTS DE CALENDÁRIO
# ================================

@router.get("/calendario/{data}", response_model=CalendarioResponse)
async def obter_calendario_dia(
    data: date = Path(..., description="Data do calendário (YYYY-MM-DD)"),
    usuario_id: Optional[int] = Query(None, description="ID do usuário"),
    db: Session = Depends(get_db)
):
    """Obtém o calendário de um dia específico"""
    try:
        # Buscar agendamentos do dia
        query_agendamentos = db.query(Agendamento).filter(
            func.date(Agendamento.data_agendamento) == data
        )

        if usuario_id:
            query_agendamentos = query_agendamentos.filter(
                Agendamento.usuario_responsavel_id == usuario_id
            )

        agendamentos = query_agendamentos.all()

        # Buscar bloqueios do dia
        bloqueios = db.query(BloqueioAgenda).filter(
            BloqueioAgenda.ativo == True,
            BloqueioAgenda.data_inicio <= datetime.combine(data, time.max),
            BloqueioAgenda.data_fim >= datetime.combine(data, time.min)
        ).all()

        # Buscar disponibilidades específicas
        disponibilidades = db.query(DisponibilidadeUsuario).filter(
            func.date(DisponibilidadeUsuario.data_inicio) <= data,
            func.date(DisponibilidadeUsuario.data_fim) >= data
        )

        if usuario_id:
            disponibilidades = disponibilidades.filter(
                DisponibilidadeUsuario.usuario_id == usuario_id
            )

        disponibilidades = disponibilidades.all()

        return CalendarioResponse(
            data=data,
            agendamentos=agendamentos,
            bloqueios=bloqueios,
            disponibilidades=disponibilidades
        )

    except Exception as e:
        logger.error(f"Erro ao obter calendário: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ================================
# ENDPOINTS DE ESTATÍSTICAS
# ================================

@router.get("/estatisticas/", response_model=EstatisticasAgendamento)
async def obter_estatisticas(
    data_inicio: Optional[date] = Query(None, description="Data de início"),
    data_fim: Optional[date] = Query(None, description="Data de fim"),
    usuario_id: Optional[int] = Query(None, description="ID do usuário"),
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de agendamentos"""
    try:
        # Query base
        query = db.query(Agendamento)

        if data_inicio:
            query = query.filter(func.date(Agendamento.data_agendamento) >= data_inicio)

        if data_fim:
            query = query.filter(func.date(Agendamento.data_agendamento) <= data_fim)

        if usuario_id:
            query = query.filter(Agendamento.usuario_responsavel_id == usuario_id)

        # Total de agendamentos
        total_agendamentos = query.count()

        # Agendamentos hoje
        hoje = date.today()
        agendamentos_hoje = query.filter(
            func.date(Agendamento.data_agendamento) == hoje
        ).count()

        # Agendamentos esta semana
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        agendamentos_semana = query.filter(
            func.date(Agendamento.data_agendamento).between(inicio_semana, fim_semana)
        ).count()

        # Agendamentos este mês
        agendamentos_mes = query.filter(
            extract('month', Agendamento.data_agendamento) == hoje.month,
            extract('year', Agendamento.data_agendamento) == hoje.year
        ).count()

        # Por status
        por_status = {}
        for status in StatusAgendamento:
            count = query.filter(Agendamento.status == status).count()
            por_status[status.value] = count

        # Por tipo
        por_tipo = {}
        for tipo in TipoAgendamento:
            count = query.filter(Agendamento.tipo == tipo).count()
            por_tipo[tipo.value] = count

        # Taxa de confirmação
        total_nao_cancelados = query.filter(
            Agendamento.status != StatusAgendamento.CANCELADO
        ).count()
        confirmados = query.filter(
            Agendamento.status.in_([StatusAgendamento.CONFIRMADO, StatusAgendamento.CONCLUIDO])
        ).count()

        taxa_confirmacao = (confirmados / total_nao_cancelados * 100) if total_nao_cancelados > 0 else 0

        return EstatisticasAgendamento(
            total_agendamentos=total_agendamentos,
            agendamentos_hoje=agendamentos_hoje,
            agendamentos_semana=agendamentos_semana,
            agendamentos_mes=agendamentos_mes,
            por_status=por_status,
            por_tipo=por_tipo,
            taxa_confirmacao=round(taxa_confirmacao, 2)
        )

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ================================
# ENDPOINTS DE INTEGRAÇÃO
# ================================

@router.post("/integração/ordem-servico/", response_model=AgendamentoResponse, status_code=201)
async def criar_agendamento_para_os(
    integracao_data: AgendamentoIntegracaoOS,
    db: Session = Depends(get_db)
):
    """Cria agendamento automático para uma OS"""
    try:
        # Verificar se OS existe
        os = db.query(OrdemServico).filter(OrdemServico.id == integracao_data.ordem_servico_id).first()
        if not os:
            raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

        # Criar agendamento baseado na OS
        agendamento_data = AgendamentoCreate(
            data_agendamento=integracao_data.data_preferida or datetime.now() + timedelta(days=1),
            titulo=f"{integracao_data.tipo_agendamento.value.title()} - OS #{os.numero_os}",
            descricao=f"Agendamento automático para {os.descricao}",
            tipo=integracao_data.tipo_agendamento,
            usuario_responsavel_id=integracao_data.usuario_responsavel_id or 1,
            cliente_id=os.cliente_id,
            ordem_servico_id=os.id,
            observacoes=integracao_data.observacoes,
            duracao_minutos=120  # Default 2 horas
        )

        # Usar o endpoint de criação normal
        return await criar_agendamento(agendamento_data, db)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar agendamento para OS: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ================================
# ENDPOINT DE HEALTH CHECK
# ================================

@router.get("/health")
async def health_check():
    """Health check do módulo de agendamento"""
    return {
        "status": "ok",
        "module": "agendamento",
        "version": "1.0.0",
        "endpoints": len(router.routes)
    }