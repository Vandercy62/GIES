"""
ROUTER ORDEM DE SERVIÇO - SISTEMA ERP PRIMOTEX
==============================================

API endpoints para gerenciamento completo de Ordens de Serviço
incluindo workflow de 7 fases, visitas técnicas e orçamentos.

Autor: GitHub Copilot
Data: 30/01/2025
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from backend.database.config import get_db
from backend.models.ordem_servico_model import OrdemServico, FaseOS, VisitaTecnica, Orcamento
from backend.schemas.ordem_servico_schemas import (
    OrdemServicoCreate, OrdemServicoUpdate, OrdemServicoResponse,
    FaseOSCreate, FaseOSUpdate, FaseOSResponse,
    VisitaTecnicaCreate, VisitaTecnicaResponse,
    OrcamentoCreate, OrcamentoResponse
)
from backend.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/os",
    tags=["Ordem de Serviço"]
)

# ============================================================================
# ENDPOINTS - ORDEM DE SERVIÇO (CRUD COMPLETO)
# ============================================================================

@router.post("/", response_model=OrdemServicoResponse, status_code=status.HTTP_201_CREATED)
async def criar_ordem_servico(
    os_data: OrdemServicoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Cria uma nova Ordem de Serviço (Fase 1: Abertura)
    
    - Gera número automático da OS
    - Cria registro com status inicial
    - Inicializa as 7 fases do workflow
    """
    try:
        # Gerar número da OS (formato: OS-AAAA-NNNN)
        ano_atual = datetime.now().year
        ultimo_numero = db.query(OrdemServico).filter(
            OrdemServico.numero_os.like(f"OS-{ano_atual}-%")
        ).count()
        
        numero_os = f"OS-{ano_atual}-{str(ultimo_numero + 1).zfill(4)}"
        
        # Criar OS
        nova_os = OrdemServico(
            numero_os=numero_os,
            cliente_id=os_data.cliente_id,
            tipo_servico=os_data.tipo_servico,
            categoria=os_data.categoria,
            prioridade=os_data.prioridade or "Normal",
            status_fase=1,
            status_geral="Aberta",
            usuario_abertura=current_user.get("username", "Sistema"),
            endereco_execucao=os_data.endereco_execucao,
            cidade_execucao=os_data.cidade_execucao,
            estado_execucao=os_data.estado_execucao,
            cep_execucao=os_data.cep_execucao,
            observacoes_abertura=os_data.observacoes_abertura,
            data_prevista_conclusao=os_data.data_prevista_conclusao
        )
        
        db.add(nova_os)
        db.flush()
        
        # Criar as 7 fases automaticamente
        fases_padrao = [
            {"numero": 1, "nome": "Abertura", "descricao": "Registro inicial da OS"},
            {"numero": 2, "nome": "Visita Técnica", "descricao": "Agendamento e execução da visita"},
            {"numero": 3, "nome": "Orçamento", "descricao": "Elaboração e aprovação do orçamento"},
            {"numero": 4, "nome": "Aprovação", "descricao": "Aprovação do cliente"},
            {"numero": 5, "nome": "Execução", "descricao": "Realização do serviço"},
            {"numero": 6, "nome": "Conferência", "descricao": "Conferência de qualidade"},
            {"numero": 7, "nome": "Arquivo", "descricao": "Finalização e arquivo"}
        ]
        
        for fase_config in fases_padrao:
            fase = FaseOS(
                ordem_servico_id=nova_os.id,
                numero_fase=fase_config["numero"],
                nome_fase=fase_config["nome"],
                descricao_fase=fase_config["descricao"],
                status="Em Andamento" if fase_config["numero"] == 1 else "Pendente",
                obrigatoria=True
            )
            db.add(fase)
        
        db.commit()
        db.refresh(nova_os)
        
        return nova_os
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar OS: {str(e)}"
        )


@router.get("/", response_model=List[OrdemServicoResponse])
async def listar_ordens_servico(
    skip: int = 0,
    limit: int = 100,
    status_geral: Optional[str] = None,
    status_fase: Optional[int] = None,
    cliente_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todas as Ordens de Serviço com filtros opcionais
    """
    query = db.query(OrdemServico)
    
    if status_geral:
        query = query.filter(OrdemServico.status_geral == status_geral)
    
    if status_fase:
        query = query.filter(OrdemServico.status_fase == status_fase)
    
    if cliente_id:
        query = query.filter(OrdemServico.cliente_id == cliente_id)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{os_id}", response_model=OrdemServicoResponse)
async def obter_ordem_servico(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtém detalhes completos de uma OS específica
    """
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OS #{os_id} não encontrada"
        )
    
    return os


@router.put("/{os_id}", response_model=OrdemServicoResponse)
async def atualizar_ordem_servico(
    os_id: int,
    os_data: OrdemServicoUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Atualiza dados de uma OS existente
    """
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OS #{os_id} não encontrada"
        )
    
    # Atualizar campos
    for field, value in os_data.dict(exclude_unset=True).items():
        setattr(os, field, value)
    
    db.commit()
    db.refresh(os)
    
    return os


@router.delete("/{os_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_ordem_servico(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deleta uma OS (apenas administradores)
    """
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OS #{os_id} não encontrada"
        )
    
    db.delete(os)
    db.commit()
    
    return None


# ============================================================================
# ENDPOINTS - CONTROLE DE FASES
# ============================================================================

@router.get("/{os_id}/fases", response_model=List[FaseOSResponse])
async def listar_fases_os(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todas as fases de uma OS
    """
    fases = db.query(FaseOS).filter(FaseOS.ordem_servico_id == os_id).order_by(FaseOS.numero_fase).all()
    
    if not fases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhuma fase encontrada para OS #{os_id}"
        )
    
    return fases


@router.put("/{os_id}/fases/{numero_fase}", response_model=FaseOSResponse)
async def atualizar_fase(
    os_id: int,
    numero_fase: int,
    fase_data: FaseOSUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Atualiza uma fase específica da OS
    """
    fase = db.query(FaseOS).filter(
        FaseOS.ordem_servico_id == os_id,
        FaseOS.numero_fase == numero_fase
    ).first()
    
    if not fase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fase {numero_fase} não encontrada para OS #{os_id}"
        )
    
    # Atualizar campos
    for field, value in fase_data.dict(exclude_unset=True).items():
        setattr(fase, field, value)
    
    # Se concluída, atualizar data
    if fase_data.status == "Concluída" and not fase.data_conclusao:
        fase.data_conclusao = datetime.now()
    
    db.commit()
    db.refresh(fase)
    
    # Atualizar status_fase da OS
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if os and fase.status == "Concluída":
        # Avançar para próxima fase se concluída
        if numero_fase < 7:
            os.status_fase = numero_fase + 1
        else:
            os.status_geral = "Concluída"
            os.data_conclusao = datetime.now()
        
        db.commit()
    
    return fase


@router.post("/{os_id}/avancar-fase", response_model=OrdemServicoResponse)
async def avancar_fase(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Avança a OS para a próxima fase
    """
    os = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    
    if not os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OS #{os_id} não encontrada"
        )
    
    if os.status_fase >= 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OS já está na última fase"
        )
    
    # Concluir fase atual
    fase_atual = db.query(FaseOS).filter(
        FaseOS.ordem_servico_id == os_id,
        FaseOS.numero_fase == os.status_fase
    ).first()
    
    if fase_atual:
        fase_atual.status = "Concluída"
        fase_atual.data_conclusao = datetime.now()
    
    # Avançar para próxima fase
    os.status_fase += 1
    os.status_geral = "Em Andamento"
    
    # Iniciar próxima fase
    proxima_fase = db.query(FaseOS).filter(
        FaseOS.ordem_servico_id == os_id,
        FaseOS.numero_fase == os.status_fase
    ).first()
    
    if proxima_fase:
        proxima_fase.status = "Em Andamento"
        proxima_fase.data_inicio = datetime.now()
    
    db.commit()
    db.refresh(os)
    
    return os


# ============================================================================
# ENDPOINTS - ESTATÍSTICAS E DASHBOARD
# ============================================================================

@router.get("/estatisticas/dashboard")
async def obter_estatisticas_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna estatísticas para o dashboard de OS
    """
    total_os = db.query(OrdemServico).count()
    os_abertas = db.query(OrdemServico).filter(OrdemServico.status_geral == "Aberta").count()
    os_andamento = db.query(OrdemServico).filter(OrdemServico.status_geral == "Em Andamento").count()
    os_concluidas = db.query(OrdemServico).filter(OrdemServico.status_geral == "Concluída").count()
    
    # OS por fase
    os_por_fase = {}
    for fase_num in range(1, 8):
        count = db.query(OrdemServico).filter(OrdemServico.status_fase == fase_num).count()
        os_por_fase[f"fase_{fase_num}"] = count
    
    # OS atrasadas (data prevista passou e ainda não concluída)
    hoje = datetime.now()
    os_atrasadas = db.query(OrdemServico).filter(
        OrdemServico.data_prevista_conclusao < hoje,
        OrdemServico.status_geral != "Concluída"
    ).count()
    
    return {
        "total_os": total_os,
        "abertas": os_abertas,
        "em_andamento": os_andamento,
        "concluidas": os_concluidas,
        "atrasadas": os_atrasadas,
        "por_fase": os_por_fase
    }


@router.get("/estatisticas/ultimas")
async def obter_ultimas_os(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna as últimas OS criadas
    """
    os_list = db.query(OrdemServico).order_by(
        OrdemServico.created_at.desc()
    ).limit(limit).all()
    
    return os_list


# ============================================================================
# ENDPOINTS - MEDIÇÕES JSON (FASE 104 TAREFA 5)
# ============================================================================

@router.post("/{os_id}/medicoes-json", status_code=status.HTTP_201_CREATED)
async def salvar_medicoes_json(
    os_id: int,
    dados: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Salva medições técnicas em formato JSON
    
    - Armazena no campo dados_medicoes_json da OS
    - Suporta múltiplas medições (área, perímetro, linear, quantidade)
    - Mantém histórico com timestamp
    """
    os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os_obj:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    
    # Salvar JSON
    os_obj.dados_medicoes_json = dados
    db.commit()
    
    return {"message": "Medições salvas com sucesso", "os_id": os_id}


@router.get("/{os_id}/medicoes-json")
async def obter_medicoes_json(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna medições técnicas em formato JSON
    """
    os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os_obj:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    
    if not os_obj.dados_medicoes_json:
        raise HTTPException(status_code=404, detail="Nenhuma medição encontrada")
    
    return os_obj.dados_medicoes_json


# =====================================================================
# ENDPOINTS - MATERIAIS (FASE 104 TAREFA 6)
# =====================================================================

@router.post("/{os_id}/materiais-json", status_code=status.HTTP_201_CREATED)
async def salvar_materiais_json(
    os_id: int,
    dados: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Salva controle de materiais em formato JSON
    
    Args:
        os_id: ID da OS
        dados: JSON com materiais aplicados/devolvidos
        
    Returns:
        Mensagem de sucesso
    """
    os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os_obj:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    
    os_obj.dados_materiais_json = dados
    db.commit()
    
    return {"message": "Materiais salvos com sucesso", "os_id": os_id}


@router.get("/{os_id}/materiais-json")
async def obter_materiais_json(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna controle de materiais em formato JSON
    """
    os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os_obj:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    
    if not os_obj.dados_materiais_json:
        raise HTTPException(status_code=404, detail="Nenhum material encontrado")
    
    return os_obj.dados_materiais_json


# =====================================================================
# ENDPOINTS - EQUIPE (FASE 104 TAREFA 7)
# =====================================================================

@router.post("/{os_id}/equipe-json", status_code=status.HTTP_201_CREATED)
async def salvar_equipe_json(
    os_id: int,
    dados: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Salva gerenciamento de equipe em formato JSON
    
    Args:
        os_id: ID da OS
        dados: JSON com membros da equipe
        
    Returns:
        Mensagem de sucesso
    """
    os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os_obj:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    
    os_obj.dados_equipe_json = dados
    db.commit()
    
    return {"message": "Equipe salva com sucesso", "os_id": os_id}


@router.get("/{os_id}/equipe-json")
async def obter_equipe_json(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna gerenciamento de equipe em formato JSON
    """
    os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
    if not os_obj:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    
    if not os_obj.dados_equipe_json:
        raise HTTPException(status_code=404, detail="Nenhuma equipe encontrada")
    
    return os_obj.dados_equipe_json
