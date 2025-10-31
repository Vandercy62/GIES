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
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from backend.database.config import get_db
from backend.models.ordem_servico_model import OrdemServico, FaseOS, VisitaTecnica, Orcamento
from backend.models.cliente_model import Cliente
from backend.schemas.ordem_servico_schemas import (
    # Schemas principais
    OrdemServicoCreate,
    OrdemServicoUpdate,
    OrdemServicoResponse,
    ResumoOrdemServico,
    ListagemOrdemServico,
    FiltrosOrdemServico,
    
    # Schemas de fases
    FaseOSCreate,
    FaseOSUpdate,
    FaseOSResponse,
    
    # Schemas específicos
    VisitaTecnicaCreate,
    VisitaTecnicaUpdate,
    VisitaTecnicaResponse,
    OrcamentoCreate,
    OrcamentoUpdate,
    OrcamentoResponse,
    
    # Schemas de ações
    MudancaFaseRequest,
    AtualizacaoStatusRequest,
    HistoricoMudanca,
    
    # Schemas de relatórios
    EstatisticasOS,
    DashboardOS,
    
    # Enums
    StatusOS,
    FaseOSEnum,
    StatusFase,
)

# Criação do router
router = APIRouter(
    prefix="/api/v1/ordem-servico",
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

@router.post("/", response_model=OrdemServicoResponse, status_code=status.HTTP_201_CREATED)
async def criar_ordem_servico(
    os_data: OrdemServicoCreate,
    db: Session = Depends(get_db)
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
    
    # Criar OS
    os_obj = OrdemServico(
        numero_os=os_data.numero_os,
        cliente_id=os_data.cliente_id,
        titulo=os_data.titulo,
        descricao=os_data.descricao,
        tipo_servico=os_data.tipo_servico.value,
        prioridade=os_data.prioridade.value,
        endereco_servico=os_data.endereco_servico,
        cep_servico=os_data.cep_servico,
        cidade_servico=os_data.cidade_servico,
        estado_servico=os_data.estado_servico,
        data_solicitacao=os_data.data_solicitacao,
        data_prazo=os_data.data_prazo,
        valor_estimado=os_data.valor_estimado,
        valor_final=os_data.valor_final,
        observacoes=os_data.observacoes,
        requer_orcamento=os_data.requer_orcamento,
        urgente=os_data.urgente,
        usuario_criacao=os_data.usuario_criacao,
        status=StatusOS.ORCAMENTO.value,
        fase_atual=FaseOSEnum.CRIACAO.value
    )
    
    db.add(os_obj)
    db.commit()
    db.refresh(os_obj)
    
    # Criar fases iniciais
    criar_fases_iniciais(os_obj.id, db)
    
    # Atualizar progresso
    os_obj.progresso_percentual = calcular_progresso_os(os_obj)
    db.commit()
    
    return os_obj


@router.get("/", response_model=ListagemOrdemServico)
async def listar_ordens_servico(
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(50, ge=1, le=100, description="Limite de registros"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    status: Optional[StatusOS] = Query(None, description="Filtrar por status"),
    prioridade: Optional[str] = Query(None, description="Filtrar por prioridade"),
    urgente: Optional[bool] = Query(None, description="Apenas urgentes"),
    numero_os: Optional[str] = Query(None, description="Buscar por número"),
    titulo: Optional[str] = Query(None, description="Buscar no título"),
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
    query = db.query(OrdemServico)
    
    # Aplicar filtros
    if cliente_id:
        query = query.filter(OrdemServico.cliente_id == cliente_id)
    
    if status:
        query = query.filter(OrdemServico.status == status.value)
    
    if prioridade:
        query = query.filter(OrdemServico.prioridade == prioridade)
    
    if urgente is not None:
        query = query.filter(OrdemServico.urgente == urgente)
    
    if numero_os:
        query = query.filter(OrdemServico.numero_os.ilike(f"%{numero_os}%"))
    
    if titulo:
        query = query.filter(OrdemServico.titulo.ilike(f"%{titulo}%"))
    
    # Aplicar ordenação
    order_field = getattr(OrdemServico, order_by, OrdemServico.created_at)
    if order_desc:
        query = query.order_by(desc(order_field))
    else:
        query = query.order_by(asc(order_field))
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação
    itens = query.offset(skip).limit(limit).all()
    
    # Montar resposta
    return ListagemOrdemServico(
        total=total,
        skip=skip,
        limit=limit,
        itens=[
            ResumoOrdemServico(
                id=os.id,
                numero_os=os.numero_os,
                titulo=os.titulo,
                cliente_nome=os.cliente.nome if os.cliente else "N/A",
                status=StatusOS(os.status),
                fase_atual=FaseOSEnum(os.fase_atual),
                prioridade=os.prioridade,
                tipo_servico=os.tipo_servico,
                progresso_percentual=calcular_progresso_os(os),
                data_solicitacao=os.data_solicitacao,
                data_prazo=os.data_prazo,
                valor_final=os.valor_final,
                urgente=os.urgente
            ) for os in itens
        ]
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
    os_obj.updated_at = datetime.now()
    
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
            nome_fase=fase_data["nome"].value,
            descricao=fase_data["descricao"],
            status=StatusFase.CONCLUIDA.value if fase_data["numero"] == 1 else StatusFase.PENDENTE.value,
            obrigatoria=True,
            usuario_criacao="sistema"
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
    fase.updated_at = datetime.now()
    
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
    os_obj.fase_atual = mudanca.nova_fase.value
    os_obj.usuario_ultima_alteracao = mudanca.usuario_responsavel
    os_obj.updated_at = datetime.now()

    # Marcar fase como em andamento
    fase.status = StatusFase.EM_ANDAMENTO.value
    if mudanca.observacoes:
        fase.observacoes = mudanca.observacoes

    # Registrar histórico da mudança de fase
    from backend.models.ordem_servico import OrdemServicoHistorico, OrdemServicoFase
    historico = OrdemServicoHistorico(
        ordem_servico_id=os_id,
        data=datetime.now(),
        usuario_id=None,  # Ajustar se houver usuário autenticado
        fase=OrdemServicoFase(mudanca.nova_fase.value),
        status=fase.status,
        observacao=mudanca.observacoes or "Transição de fase"
    )
    db.add(historico)

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
    
    # Outras estatísticas podem ser adicionadas aqui
    
    return EstatisticasOS(
        total_os=total_os,
        por_status=por_status,
        por_fase=por_fase,
        por_prioridade={},  # Implementar se necessário
        por_tipo={}  # Implementar se necessário
    )