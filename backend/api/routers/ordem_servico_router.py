#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROUTER FASTAPI - ORDEM DE SERVIÇO
=================================

Endpoints para o sistema de Ordem de Serviço.
Implementa CRUD completo com validações e workflow de fases.

Criado em: 29/10/2025
Autor: GitHub Copilot
"""

from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc, func

from backend.database.config import get_db
from backend.auth.dependencies import require_operator, get_current_user
from backend.models.ordem_servico_model import OrdemServico, FaseOS, VisitaTecnica, Orcamento
from backend.models.cliente_model import Cliente
from backend.schemas.ordem_servico_schemas import (
    # Schemas principais
    OrdemServicoCreate,
    OrdemServicoUpdate,
    OrdemServicoResponse,  # Usado em endpoints GET/PUT
    ResumoOrdemServico,
    ListagemOrdemServico,

    # Schemas de fases
    FaseOSUpdate,
    FaseOSResponse,

    # Schemas específicos
    VisitaTecnicaCreate,
    VisitaTecnicaResponse,
    OrcamentoCreate,
    OrcamentoResponse,

    # Schemas de ações
    MudancaFaseRequest,

    # Schemas de relatórios
    EstatisticasOS,
    DashboardOS,
    HistoricoMudanca,

    # Enums
    StatusOS,
    FaseOSEnum,
    StatusFase,
    PrioridadeOS,
    TipoOS,
)

# Criação do router
router = APIRouter(
    prefix="/os",  # CORRIGIDO - Prefix relativo, /api/v1 adicionado no main.py
    tags=["Ordem de Serviço"],
    responses={404: {"description": "OS não encontrada"}}
)


# ================================
# UTILITÁRIOS E VALIDAÇÕES
# ================================

def get_ordem_servico_or_404(os_id: int, db: Session) -> OrdemServico:
    """Busca OS por ID ou retorna 404"""
    os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ordem de Serviço com ID {os_id} não encontrada"
        )
    return os_obj


def gerar_numero_os(db: Session) -> str:
    """Gera próximo número de OS disponível"""
    # Busca último número
    ultima_os = db.query(OrdemServico).order_by(desc(OrdemServico.id)).first()

    if not ultima_os:
        return "OS-2025-001"

    # Extrai número da última OS
    try:
        partes = ultima_os.numero_os.split('-')
        if len(partes) >= 3:
            numero = int(partes[2]) + 1
            return f"OS-2025-{numero:03d}"
    except (ValueError, IndexError):
        pass

    # Fallback: conta registros
    total = db.query(OrdemServico).count()
    return f"OS-2025-{total + 1:03d}"


def calcular_progresso_os(os_obj: OrdemServico) -> float:
    """Calcula percentual de progresso da OS"""
    if not os_obj.fases:
        return 0.0

    total_fases = len(os_obj.fases)
    fases_concluidas = sum(1 for fase in os_obj.fases if fase.status == StatusFase.CONCLUIDA)

    return (fases_concluidas / total_fases) * 100 if total_fases > 0 else 0.0


# ================================
# ENDPOINTS PRINCIPAIS - CRUD
# ================================

@router.post("/", status_code=status.HTTP_201_CREATED)  # response_model removido temporariamente
async def criar_ordem_servico(
    os_data: OrdemServicoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)  # ADICIONADO - Autenticação
):
    """
    Cria uma nova Ordem de Serviço

    - **numero_os**: Gerado automaticamente se não fornecido
    - **cliente_id**: Deve existir na base de dados
    - **titulo**: Título descritivo da OS
    - **descrição**: Descrição detalhada do serviço
    """
    # Validar se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == os_data.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cliente com ID {os_data.cliente_id} não encontrado"
        )

    # Gerar número da OS se não fornecido
    if not os_data.numero_os:
        os_data.numero_os = gerar_numero_os(db)

    # Verificar se número já existe
    os_existente = db.query(OrdemServico).filter(
        OrdemServico.numero_os == os_data.numero_os
    ).first()
    if os_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Número de OS {os_data.numero_os} já existe"
        )

    # Criar OS - MAPEAMENTO SCHEMA→MODELO
    os_obj = OrdemServico(
        # Campos básicos
        numero_os=os_data.numero_os,
        cliente_id=os_data.cliente_id,
        tipo_servico=os_data.tipo_servico.value,
        categoria="Comercial",  # Valor padrão (campo obrigatório no modelo)
        prioridade=os_data.prioridade.value,

        # Status
        fase_atual=1,  # Fase 1 - Criação
        status_geral="Aberta",

        # Datas
        # data_abertura usa server_default
        data_prevista_conclusao=os_data.data_prazo,
        prazo_orcamento=os_data.data_prazo,

        # Responsáveis
        usuario_abertura=os_data.usuario_criacao,

        # Valores
        valor_orcamento=os_data.valor_estimado or 0.00,
        valor_final=os_data.valor_final or 0.00,

        # Endereço do serviço
        endereco_execucao=os_data.endereco_servico,
        cep_execucao=os_data.cep_servico,
        cidade_execucao=os_data.cidade_servico,
        estado_execucao=os_data.estado_servico,

        # Observações (mapear titulo+descricao para observacoes_abertura)
        observacoes_abertura=f"{os_data.titulo}\n\n{os_data.descricao}\n\n{os_data.observacoes or ''}"
    )

    db.add(os_obj)
    db.commit()
    db.refresh(os_obj)

    # Criar fases iniciais - ✅ REABILITADO
    criar_fases_iniciais(int(os_obj.id), db)

    # Retornar dict simples (response_model incompatível - ver SINCRONIZACAO_SCHEMA_MODEL.md)
    return {
        "id": os_obj.id,
        "numero_os": os_obj.numero_os,
        "cliente_id": os_obj.cliente_id,
        "tipo_servico": os_obj.tipo_servico,
        "status": os_obj.status,  # ALINHADO COM SCHEMA
        "fase_atual": os_obj.fase_atual,  # ALINHADO COM SCHEMA
        "data_abertura": os_obj.data_abertura,
        "usuario_abertura": os_obj.usuario_abertura
    }


@router.get("/")
async def listar_ordens_servico(
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(50, ge=1, le=100, description="Limite de registros"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    prioridade: Optional[str] = Query(None, description="Filtrar por prioridade"),
    urgente: Optional[bool] = Query(None, description="Apenas urgentes"),
    numero_os: Optional[str] = Query(None, description="Buscar por número"),
    order_by: str = Query("created_at", description="Campo para ordenação"),
    order_desc: bool = Query(True, description="Ordem decrescente"),
    db: Session = Depends(get_db)
):
    """
    Lista Ordens de Serviço com filtros e paginação

    - **skip**: Número de registros para pular (paginação)
    - **limit**: Limite de registros por página (máx 100)
    - **cliente_id**: Filtrar por cliente específico
    - **status**: Filtrar por status da OS
    - **urgente**: Mostrar apenas OS urgentes
    """
    try:
        # Query base
        query = db.query(OrdemServico)

        # Aplicar filtros
        if cliente_id:
            query = query.filter(OrdemServico.cliente_id == cliente_id)

        if status:
            query = query.filter(OrdemServico.status == status)

        if prioridade:
            query = query.filter(OrdemServico.prioridade == prioridade)

        if urgente is not None:
            query = query.filter(OrdemServico.urgente == urgente)

        if numero_os:
            query = query.filter(OrdemServico.numero_os.ilike(f"%{numero_os}%"))

        # Ordenação
        order_field = getattr(OrdemServico, order_by, OrdemServico.created_at)
        if order_desc:
            query = query.order_by(desc(order_field))
        else:
            query = query.order_by(asc(order_field))

        # Paginação  
        ordens_servico = query.offset(skip).limit(limit).all()

        # Converter para dict simples para evitar erro de validação
        return [
            {
                "id": os.id,
                "numero_os": os.numero_os,
                "cliente_id": os.cliente_id,
                "tipo_servico": os.tipo_servico,
                "categoria": os.categoria,
                "prioridade": os.prioridade,
                "fase_atual": os.fase_atual,
                "status": os.status,
                "data_abertura": os.data_abertura.isoformat() if os.data_abertura else None,
                "valor_final": float(os.valor_final) if os.valor_final else None,
            }
            for os in ordens_servico
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar Ordens de Serviço: {str(e)}"
        )


@router.get("/{os_id}", response_model=OrdemServicoResponse)
async def obter_ordem_servico(
    os_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém uma Ordem de Serviço específica por ID

    - **os_id**: ID da Ordem de Serviço
    """
    os_obj = get_ordem_servico_or_404(os_id, db)

    # Calcular dados derivados
    os_obj.progresso_percentual = calcular_progresso_os(os_obj)
    os_obj.total_fases = 7
    os_obj.fases_concluidas = sum(1 for fase in os_obj.fases if fase.status == StatusFase.CONCLUIDA)

    return os_obj


@router.put("/{os_id}", response_model=OrdemServicoResponse)
async def atualizar_ordem_servico(
    os_id: int,
    os_data: OrdemServicoUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza uma Ordem de Serviço existente

    - **os_id**: ID da Ordem de Serviço
    - Apenas campos fornecidos serão atualizados
    """
    os_obj = get_ordem_servico_or_404(os_id, db)

    # Atualizar campos fornecidos
    update_data = os_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        if field == "usuario_ultima_alteracao":
            continue  # Tratar separadamente

        if hasattr(os_obj, field):
            if field in ["tipo_servico", "prioridade"] and hasattr(value, 'value'):
                setattr(os_obj, field, value.value)
            else:
                setattr(os_obj, field, value)

    # Definir usuário de alteração
    os_obj.usuario_ultima_alteracao = os_data.usuario_ultima_alteracao
    setattr(os_obj, "updated_at", datetime.now())

    db.commit()
    db.refresh(os_obj)

    return os_obj


@router.delete("/{os_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_ordem_servico(
    os_id: int,
    db: Session = Depends(get_db)
):
    """
    Deleta uma Ordem de Serviço

    - **os_id**: ID da Ordem de Serviço
    - ⚠️ **Atenção**: Esta ação é irreversível
    """
    os_obj = get_ordem_servico_or_404(os_id, db)

    # Verificar se pode ser deletada
    if os_obj.status in [StatusOS.EM_EXECUCAO.value, StatusOS.CONCLUIDA.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível deletar OS com status {os_obj.status}"
        )

    db.delete(os_obj)
    db.commit()


# ================================
# ENDPOINTS DE FASES
# ================================

def criar_fases_iniciais(os_id: int, db: Session):
    """Cria as 7 fases iniciais da OS"""
    fases = [
        {"numero": 1, "nome": FaseOSEnum.CRIACAO, "descricao": "Criação e especificação da OS"},
        {"numero": 2, "nome": FaseOSEnum.VISITA_TECNICA, "descricao": "Visita técnica para medições"},
        {"numero": 3, "nome": FaseOSEnum.ORCAMENTO, "descricao": "Elaboração do orçamento"},
        {"numero": 4, "nome": FaseOSEnum.APROVACAO, "descricao": "Aprovação do cliente"},
        {"numero": 5, "nome": FaseOSEnum.EXECUCAO, "descricao": "Execução do serviço"},
        {"numero": 6, "nome": FaseOSEnum.ENTREGA, "descricao": "Entrega e verificação"},
        {"numero": 7, "nome": FaseOSEnum.FINALIZACAO, "descricao": "Finalização e documentação"}
    ]

    for fase_data in fases:
        fase = FaseOS(
            ordem_servico_id=os_id,
            numero_fase=fase_data["numero"],
            nome_fase=fase_data["nome"].value if hasattr(fase_data["nome"], "value") else str(fase_data["nome"]),
            descricao_fase=fase_data["descricao"],
            status=StatusFase.CONCLUIDA.value if fase_data["numero"] == 1 else StatusFase.PENDENTE.value,
            obrigatoria=True
        )
        db.add(fase)

    db.commit()


@router.get("/{os_id}/fases", response_model=List[FaseOSResponse])
async def listar_fases_os(
    os_id: int,
    db: Session = Depends(get_db)
):
    """
    Lista todas as fases de uma OS

    - **os_id**: ID da Ordem de Serviço
    """
    # Verificar se OS existe
    get_ordem_servico_or_404(os_id, db)

    # Buscar fases
    fases = db.query(FaseOS).filter(FaseOS.ordem_servico_id == os_id).all()
    return fases


@router.put("/{os_id}/fases/{fase_id}", response_model=FaseOSResponse)
async def atualizar_fase_os(
    os_id: int,
    fase_id: int,
    fase_data: FaseOSUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza uma fase específica da OS

    - **os_id**: ID da Ordem de Serviço
    - **fase_id**: ID da fase
    """
    # Verificar se OS existe
    get_ordem_servico_or_404(os_id, db)

    fase = db.query(FaseOS).filter(
        and_(FaseOS.id == fase_id, FaseOS.ordem_servico_id == os_id)
    ).first()

    if not fase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fase {fase_id} não encontrada na OS {os_id}"
        )

    # Atualizar campos
    update_data = fase_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "usuario_alteracao":
            continue
        if hasattr(fase, field):
            setattr(fase, field, value)

    fase.usuario_ultima_alteracao = fase_data.usuario_alteracao
    setattr(fase, "updated_at", datetime.now())

    db.commit()
    db.refresh(fase)

    return fase


@router.post("/{os_id}/mudar-fase", response_model=OrdemServicoResponse)
async def mudar_fase_os(
    os_id: int,
    mudanca: MudancaFaseRequest,
    db: Session = Depends(get_db)
):
    """
    Muda a fase atual da OS

    - **os_id**: ID da Ordem de Serviço
    - **nova_fase**: Nova fase da OS
    - **observacoes**: Observações da mudança
    """
    os_obj = get_ordem_servico_or_404(os_id, db)

    # Validar se a fase existe
    fase = db.query(FaseOS).filter(
        and_(
            FaseOS.ordem_servico_id == os_id,
            FaseOS.nome_fase == mudanca.nova_fase.value
        )
    ).first()

    if not fase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fase {mudanca.nova_fase.value} não encontrada"
        )

    # Atualizar OS
    setattr(os_obj, "fase_atual", mudanca.nova_fase.value)
    os_obj.usuario_ultima_alteracao = mudanca.usuario_responsavel
    setattr(os_obj, "updated_at", datetime.now())

    # Marcar fase como em andamento
    setattr(fase, "status", StatusFase.EM_ANDAMENTO.value)
    if mudanca.observacoes:
        setattr(fase, "observacoes", mudanca.observacoes)

    # Registrar histórico da mudança de fase - DESABILITADO (modelos não existem)
    # NOTE: OrdemServicoHistorico e OrdemServicoFase já existem nos models
    # from backend.models.ordem_servico_model import OrdemServicoHistorico, OrdemServicoFase
    # historico = OrdemServicoHistorico(
    #     ordem_servico_id=os_id,
    #     data=datetime.now(),
    #     usuario_id=None,
    #     fase=OrdemServicoFase(mudanca.nova_fase.value),
    #     status=fase.status,
    #     observacao=mudanca.observacoes or "Transição de fase"
    # )
    # db.add(historico)

    db.commit()
    db.refresh(os_obj)

    return os_obj


# ================================
# ENDPOINTS DE VISITA TÉCNICA
# ================================

@router.post("/{os_id}/visita-tecnica", response_model=VisitaTecnicaResponse, status_code=status.HTTP_201_CREATED)
async def agendar_visita_tecnica(
    os_id: int,
    visita_data: VisitaTecnicaCreate,
    db: Session = Depends(get_db)
):
    """
    Agenda uma visita técnica para a OS

    - **os_id**: ID da Ordem de Serviço
    - **data_agendada**: Data e hora da visita
    - **tecnico_responsavel**: Técnico que fará a visita
    """
    # Verificar se OS existe
    get_ordem_servico_or_404(os_id, db)

    # Verificar se já existe visita
    visita_existente = db.query(VisitaTecnica).filter(
        VisitaTecnica.ordem_servico_id == os_id
    ).first()

    if visita_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma visita técnica agendada para esta OS"
        )

    # Criar visita técnica
    visita = VisitaTecnica(
        ordem_servico_id=os_id,
        data_agendada=visita_data.data_agendada,
        tecnico_responsavel=visita_data.tecnico_responsavel,
        contato_cliente=visita_data.contato_cliente,
        telefone_contato=visita_data.telefone_contato,
        objetivo=visita_data.objetivo,
        checklist_verificacao=visita_data.checklist_verificacao,
        observacoes_agendamento=visita_data.observacoes_agendamento,
        usuario_agendamento=visita_data.usuario_agendamento,
        status_execucao="Agendada"
    )

    db.add(visita)
    db.commit()
    db.refresh(visita)

    return visita


@router.get("/{os_id}/visita-tecnica", response_model=VisitaTecnicaResponse)
async def obter_visita_tecnica(
    os_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém a visita técnica de uma OS

    - **os_id**: ID da Ordem de Serviço
    """
    # Verificar se OS existe
    get_ordem_servico_or_404(os_id, db)

    visita = db.query(VisitaTecnica).filter(
        VisitaTecnica.ordem_servico_id == os_id
    ).first()

    if not visita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita técnica não encontrada para esta OS"
        )

    return visita


# ================================
# ENDPOINTS DE ORÇAMENTO
# ================================

@router.post("/{os_id}/orcamento", response_model=OrcamentoResponse, status_code=status.HTTP_201_CREATED)
async def criar_orcamento(
    os_id: int,
    orcamento_data: OrcamentoCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um orçamento para a OS

    - **os_id**: ID da Ordem de Serviço
    - **itens**: Lista de itens do orçamento
    - **valor_total**: Valor total do orçamento
    """
    # Verificar se OS existe
    get_ordem_servico_or_404(os_id, db)

    # Criar orçamento
    orcamento = Orcamento(
        ordem_servico_id=os_id,
        numero_orcamento=orcamento_data.numero_orcamento,
        data_elaboracao=orcamento_data.data_elaboracao,
        data_validade=orcamento_data.data_validade,
        elaborado_por=orcamento_data.elaborado_por,
        itens=orcamento_data.itens,
        subtotal=orcamento_data.subtotal,
        desconto_percentual=orcamento_data.desconto_percentual,
        desconto_valor=orcamento_data.desconto_valor,
        valor_total=orcamento_data.valor_total,
        forma_pagamento=orcamento_data.forma_pagamento,
        prazo_execucao=orcamento_data.prazo_execucao,
        garantia=orcamento_data.garantia,
        observacoes_gerais=orcamento_data.observacoes_gerais,
        termos_condicoes=orcamento_data.termos_condicoes,
        usuario_criacao=orcamento_data.usuario_criacao,
        status_orcamento="Elaborado"
    )

    db.add(orcamento)
    db.commit()
    db.refresh(orcamento)

    return orcamento


@router.get("/{os_id}/orcamento", response_model=OrcamentoResponse)
async def obter_orcamento(
    os_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém o orçamento de uma OS

    - **os_id**: ID da Ordem de Serviço
    """
    # Verificar se OS existe
    get_ordem_servico_or_404(os_id, db)

    orcamento = db.query(Orcamento).filter(
        Orcamento.ordem_servico_id == os_id
    ).first()

    if not orcamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado para esta OS"
        )

    return orcamento


# ================================
# ENDPOINTS DE RELATÓRIOS
# ================================

@router.get("/dashboard/estatisticas", response_model=EstatisticasOS)
async def obter_estatisticas_os(db: Session = Depends(get_db)):
    """
    Obtém estatísticas gerais das OS

    - Total de OS
    - Distribuição por status, fase, prioridade
    - Métricas de performance
    """
    total_os = db.query(OrdemServico).count()

    # Estatísticas por status
    por_status = {}
    for status_enum in StatusOS:
        count = db.query(OrdemServico).filter(OrdemServico.status == status_enum.value).count()
        por_status[status_enum.value] = count

    # Estatísticas por fase
    por_fase = {}
    for fase_enum in FaseOSEnum:
        count = db.query(OrdemServico).filter(OrdemServico.fase_atual == fase_enum.value).count()
        por_fase[fase_enum.value] = count

    # Estatísticas por prioridade
    por_prioridade = {}
    for prioridade_enum in PrioridadeOS:
        count = db.query(OrdemServico).filter(OrdemServico.prioridade == prioridade_enum.value).count()
        por_prioridade[prioridade_enum.value] = count

    # Estatísticas por tipo
    por_tipo = {}
    for tipo_enum in TipoOS:
        count = db.query(OrdemServico).filter(OrdemServico.tipo_servico == tipo_enum.value).count()
        por_tipo[tipo_enum.value] = count

    return EstatisticasOS(
        total_os=total_os,
        por_status=por_status,
        por_fase=por_fase,
        por_prioridade=por_prioridade,
        por_tipo=por_tipo
    )


# =============================================================================
# ENDPOINTS ADICIONAIS (CONSOLIDADOS DE os_router.py)
# =============================================================================

@router.get("/{os_id}/historico", response_model=List[HistoricoMudanca])
async def obter_historico_os(
    os_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obter histórico completo de mudanças da OS

    Retorna lista vazia temporariamente (OSHistorico modelo comentado)
    """
    try:
        os_obj = db.query(OrdemServico).filter(
            OrdemServico.id == os_id
        ).first()

        if not os_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de serviço não encontrada"
            )

        # Temporariamente retornando lista vazia (OSHistorico comentado)
        return []

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/estatisticas/dashboard", response_model=DashboardOS)
async def obter_dashboard_detalhado(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obter estatísticas detalhadas para dashboard de OS

    Retorna:
    - OS urgentes (prioridade urgente ou alta)
    - OS atrasadas (prazo vencido)
    - OS criadas hoje
    - Fases pendentes (quantidade por fase)
    - Estatísticas gerais consolidadas
    """
    try:
        # OS urgentes (prioridade urgente ou alta)
        os_urgentes = db.query(OrdemServico).filter(
            OrdemServico.prioridade.in_(["urgente", "alta"]),
            OrdemServico.status.in_([
                "ABERTA", "VISITA_AGENDADA", "ORCAMENTO",
                "AGUARDANDO_APROVACAO", "EM_EXECUCAO"
            ])
        ).limit(10).all()

        # OS atrasadas (prazo vencido)
        hoje = datetime.now()
        os_atrasadas = db.query(OrdemServico).filter(
            OrdemServico.prazo_previsto < hoje,
            OrdemServico.status.in_([
                "ABERTA", "VISITA_AGENDADA", "ORCAMENTO",
                "AGUARDANDO_APROVACAO", "EM_EXECUCAO"
            ])
        ).limit(10).all()

        # OS de hoje (criadas hoje)
        inicio_hoje = hoje.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        os_hoje = db.query(OrdemServico).filter(
            OrdemServico.data_abertura >= inicio_hoje
        ).limit(10).all()

        # Fases pendentes (quantidade por fase nas OS abertas)
        fases_pendentes = {}
        for fase_num in range(1, 8):
            count = db.query(OrdemServico).filter(
                OrdemServico.fase_atual == fase_num,
                OrdemServico.status.in_([
                    "ABERTA", "VISITA_AGENDADA", "ORCAMENTO",
                    "AGUARDANDO_APROVACAO", "EM_EXECUCAO"
                ])
            ).count()
            fases_pendentes[str(fase_num)] = count

        # Estatísticas gerais
        total_os = db.query(OrdemServico).count()

        # OS por status
        por_status = {}
        for status_item in [
            "ABERTA", "VISITA_AGENDADA", "ORCAMENTO",
            "AGUARDANDO_APROVACAO", "EM_EXECUCAO",
            "FINALIZADA", "CANCELADA", "ARQUIVADA"
        ]:
            count = db.query(OrdemServico).filter(
                OrdemServico.status == status_item
            ).count()
            por_status[status_item] = count

        # OS por fase
        por_fase = {}
        for fase in range(1, 8):
            count = db.query(OrdemServico).filter(
                OrdemServico.fase_atual == fase
            ).count()
            por_fase[f"fase_{fase}"] = count

        # OS por prioridade
        por_prioridade = {}
        for prioridade in ["baixa", "normal", "alta", "urgente"]:
            count = db.query(OrdemServico).filter(
                OrdemServico.prioridade == prioridade
            ).count()
            por_prioridade[prioridade] = count

        # Valor total pendente
        valor_total = db.query(
            func.sum(OrdemServico.valor_total)
        ).filter(
            OrdemServico.status.in_([
                "ABERTA", "VISITA_AGENDADA", "ORCAMENTO",
                "AGUARDANDO_APROVACAO", "EM_EXECUCAO"
            ])
        ).scalar()
        valor_total_pendente = (
            Decimal(str(valor_total)) if valor_total else None
        )

        # Estatísticas consolidadas
        estatisticas = EstatisticasOS(
            total_os=total_os,
            por_status=por_status,
            por_fase=por_fase,
            por_prioridade=por_prioridade,
            por_tipo={},
            valor_total_pendente=valor_total_pendente
        )

        return DashboardOS(
            estatisticas=estatisticas,
            os_urgentes=[
                ResumoOrdemServico.model_validate(os) for os in os_urgentes
            ],
            os_atrasadas=[
                ResumoOrdemServico.model_validate(os) for os in os_atrasadas
            ],
            os_hoje=[
                ResumoOrdemServico.model_validate(os) for os in os_hoje
            ],
            fases_pendentes=fases_pendentes
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/estatisticas/geral", response_model=EstatisticasOS)
async def obter_estatisticas_periodo(
    data_inicio: Optional[date] = Query(
        None, description="Data de início do período"
    ),
    data_fim: Optional[date] = Query(
        None, description="Data de fim do período"
    ),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obter estatísticas gerais de OS com filtro de período

    Permite filtrar estatísticas por período específico.
    Se não informado período, retorna estatísticas de todas as OS.
    """
    try:
        query = db.query(OrdemServico)

        # Filtrar por período se fornecido
        if data_inicio:
            query = query.filter(
                OrdemServico.data_abertura >= data_inicio
            )
        if data_fim:
            query = query.filter(
                OrdemServico.data_abertura <= data_fim
            )

        # Estatísticas básicas
        total = query.count()

        # OS por status
        por_status = {}
        for status_item in [
            "ABERTA", "VISITA_AGENDADA", "ORCAMENTO",
            "AGUARDANDO_APROVACAO", "EM_EXECUCAO",
            "FINALIZADA", "CANCELADA", "ARQUIVADA"
        ]:
            count = query.filter(
                OrdemServico.status == status_item
            ).count()
            por_status[status_item] = count

        # OS por fase
        por_fase = {}
        for fase in range(1, 8):
            count = query.filter(
                OrdemServico.fase_atual == fase
            ).count()
            por_fase[f"fase_{fase}"] = count

        # OS por prioridade
        por_prioridade = {}
        for prioridade in ["baixa", "normal", "alta", "urgente"]:
            count = query.filter(
                OrdemServico.prioridade == prioridade
            ).count()
            por_prioridade[prioridade] = count

        # Valor total pendente
        valor_total = query.filter(
            OrdemServico.status.in_([
                "ABERTA", "VISITA_AGENDADA", "ORCAMENTO",
                "AGUARDANDO_APROVACAO", "EM_EXECUCAO"
            ])
        ).with_entities(func.sum(OrdemServico.valor_total)).scalar()
        valor_total_pendente = (
            Decimal(str(valor_total)) if valor_total else None
        )

        return EstatisticasOS(
            total_os=total,
            por_status=por_status,
            por_fase=por_fase,
            por_prioridade=por_prioridade,
            por_tipo={},
            valor_total_pendente=valor_total_pendente
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


# ================================
# ENDPOINTS - CROQUI TÉCNICO
# ================================

@router.post("/{os_id}/croqui", status_code=status.HTTP_200_OK)
async def salvar_croqui(
    os_id: int,
    croqui_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_operator)
):
    """
    Salva dados do croqui técnico em ordem_servico.dados_croqui_json
    
    - **os_id**: ID da OS
    - **croqui_data**: Objeto JSON com coordenadas e objetos desenhados
    """
    import json
    
    os_obj = get_ordem_servico_or_404(os_id, db)
    
    try:
        # Validar estrutura básica
        if "objetos" not in croqui_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campo 'objetos' obrigatório"
            )
        
        # Salvar JSON no banco
        os_obj.dados_croqui_json = json.dumps(croqui_data, ensure_ascii=False)
        db.commit()
        
        return {
            "message": "Croqui salvo com sucesso",
            "os_id": os_id,
            "objetos_count": len(croqui_data.get("objetos", []))
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar croqui: {str(e)}"
        )


@router.get("/{os_id}/croqui")
async def carregar_croqui(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Carrega dados do croqui técnico
    
    - **os_id**: ID da OS
    
    Retorna JSON com coordenadas e objetos desenhados
    """
    import json
    
    os_obj = get_ordem_servico_or_404(os_id, db)
    
    if not os_obj.dados_croqui_json:
        return {
            "os_id": os_id,
            "objetos": [],
            "message": "Nenhum croqui encontrado"
        }
    
    try:
        croqui_data = json.loads(os_obj.dados_croqui_json)
        return croqui_data
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao decodificar dados do croqui"
        )


@router.post("/{os_id}/orcamento-json")
async def salvar_orcamento_json(
    os_id: int,
    orcamento_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Salva dados do orçamento simplificado (JSON) da OS
    
    - **os_id**: ID da OS
    - **orcamento_data**: JSON com itens, totais e timestamp
    
    Exemplo:
    ```json
    {
        "os_id": 1,
        "itens": [
            {
                "codigo": "P001",
                "produto": "Forro PVC Branco",
                "qtd": 50.5,
                "unidade": "M²",
                "preco_unit": 45.00,
                "desconto": 10.0,
                "total": 2047.50
            }
        ],
        "subtotal": 2047.50,
        "impostos": 348.08,
        "total_geral": 2395.58,
        "timestamp": "2025-11-18T10:30:00"
    }
    ```
    """
    import json
    
    os_obj = get_ordem_servico_or_404(os_id, db)
    
    try:
        # Validar estrutura
        if "itens" not in orcamento_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campo 'itens' é obrigatório"
            )
        
        if not isinstance(orcamento_data["itens"], list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campo 'itens' deve ser uma lista"
            )
        
        # Salvar JSON no banco
        os_obj.dados_orcamento_json = json.dumps(
            orcamento_data,
            ensure_ascii=False
        )
        
        # Atualizar valor_orcamento (se fornecido)
        if "total_geral" in orcamento_data:
            from decimal import Decimal
            os_obj.valor_orcamento = Decimal(
                str(orcamento_data["total_geral"])
            )
        
        db.commit()
        
        return {
            "message": "Orçamento salvo com sucesso",
            "os_id": os_id,
            "itens_count": len(orcamento_data.get("itens", [])),
            "total_geral": orcamento_data.get("total_geral", 0)
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar orçamento: {str(e)}"
        )


@router.get("/{os_id}/orcamento-json")
async def carregar_orcamento_json(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Carrega dados do orçamento simplificado (JSON) da OS
    
    - **os_id**: ID da OS
    
    Retorna JSON com itens, totais e timestamp
    """
    import json
    
    os_obj = get_ordem_servico_or_404(os_id, db)
    
    if not os_obj.dados_orcamento_json:
        return {
            "os_id": os_id,
            "itens": [],
            "subtotal": 0,
            "impostos": 0,
            "total_geral": 0,
            "message": "Nenhum orçamento encontrado"
        }
    
    try:
        orcamento_data = json.loads(os_obj.dados_orcamento_json)
        return orcamento_data
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao decodificar dados do orçamento"
        )
