"""
ROUTER DE ORDEM DE SERVIÇO - ERP PRIMOTEX
=========================================

Router completo para gerenciamento de Ordens de Serviço com workflow
de 7 fases. Integrado com WhatsApp para notificações automáticas.

Funcionalidades:
- CRUD completo de OS
- Controle de workflow (7 fases)
- Integração com agendamento
- Notificações WhatsApp automáticas
- Relatórios e estatísticas

Autor: GitHub Copilot
Data: 01/11/2025
"""

from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.database.config import get_db
from backend.auth.dependencies import get_current_user, require_operator
from backend.models.ordem_servico_model import (
    OrdemServico, FaseOS, FASES_OS, STATUS_OS
)
from backend.schemas.ordem_servico_schemas import (
    # Create schemas
    OrdemServicoCreate, MudancaFaseRequest,
    
    # Update schemas  
    OrdemServicoUpdate,
    
    # Response schemas
    OrdemServicoResponse, EstatisticasOS, DashboardOS, FaseOSResponse, HistoricoMudanca,
    
    # List schemas
    FiltrosOrdemServico, ListagemOrdemServico
)
from backend.services.comunicacao_service import ComunicacaoService
import logging

# Configurar router
router = APIRouter(prefix="/os", tags=["Ordem de Serviço"])

# Configurar logging
logger = logging.getLogger(__name__)

# Constantes para mensagens
ERRO_OS_NAO_ENCONTRADA = "Ordem de serviço não encontrada"
ERRO_FASE_INVALIDA = "Fase inválida para esta OS"
ERRO_PERMISSAO_NEGADA = "Permissão negada para esta operação"
ERRO_TRANSICAO_INVALIDA = "Transição de fase inválida"
SUCESSO_OS_CRIADA = "OS criada com sucesso"
SUCESSO_FASE_ALTERADA = "Fase alterada com sucesso"

# =============================================================================
# ENDPOINTS PRINCIPAIS - CRUD DE OS
# =============================================================================

@router.post("/", response_model=OrdemServicoResponse, status_code=status.HTTP_201_CREATED)
async def criar_ordem_servico(
    os_data: OrdemServicoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """
    Criar nova Ordem de Serviço.
    
    - **cliente_id**: ID do cliente
    - **tipo_servico**: Tipo do serviço a ser executado
    - **descricao**: Descrição detalhada do serviço
    - **prioridade**: Prioridade da OS (baixa, normal, alta, urgente)
    - **observacoes**: Observações adicionais
    """
    try:
        # Gerar número da OS automaticamente
        ultimo_numero = db.query(func.max(OrdemServico.numero_os)).scalar() or 0
        novo_numero = ultimo_numero + 1
        
        # Criar OS
        db_os = OrdemServico(
            numero_os=novo_numero,
            cliente_id=os_data.cliente_id,
            tipo_servico=os_data.tipo_servico,
            descricao=os_data.descricao,
            prioridade=os_data.prioridade,
            observacoes=os_data.observacoes,
            fase_atual=1,  # Sempre inicia na Fase 1 - Abertura
            status="ABERTA",
            usuario_abertura_id=current_user["id"],
            data_abertura=datetime.now()
        )
        
        db.add(db_os)
        db.flush()  # Para obter o ID
        
        # Criar registro da Fase 1
        fase_abertura = FaseOS(
            ordem_servico_id=db_os.id,
            numero_fase=1,
            nome_fase="Abertura da OS",
            data_inicio=datetime.now(),
            responsavel_id=current_user["id"],
            status="CONCLUIDA",
            observacoes="OS criada automaticamente"
        )
        
        db.add(fase_abertura)
        
        # Criar histórico
        historico = OSHistorico(
            ordem_servico_id=db_os.id,
            fase_anterior=None,
            fase_nova=1,
            usuario_id=current_user["id"],
            observacoes="OS criada - Fase 1 Abertura"
        )
        
        db.add(historico)
        db.commit()
        db.refresh(db_os)
        
        # Enviar notificação WhatsApp
        try:
            comunicacao = ComunicacaoService()
            await comunicacao.enviar_template_os_criada(
                os_numero=novo_numero,
                cliente_nome=db_os.cliente.nome if hasattr(db_os, 'cliente') else "Cliente",
                descricao=os_data.descricao
            )
        except Exception as e:
            logger.warning(f"Erro ao enviar WhatsApp para OS {novo_numero}: {e}")
        
        logger.info(f"OS {novo_numero} criada por usuário {current_user['username']}")
        return db_os
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar OS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/", response_model=ListagemOrdemServico)
async def listar_ordens_servico(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    filtros: FiltrosOrdemServico = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Listar Ordens de Serviço com filtros e paginação.
    
    Filtros disponíveis:
    - **cliente_id**: ID do cliente
    - **status**: Status da OS
    - **fase_atual**: Fase atual da OS
    - **prioridade**: Prioridade
    - **data_inicio**: Data de início
    - **data_fim**: Data de fim
    - **responsavel_id**: ID do responsável
    """
    try:
        query = db.query(OrdemServico)
        
        # Aplicar filtros
        if filtros.cliente_id:
            query = query.filter(OrdemServico.cliente_id == filtros.cliente_id)
            
        if filtros.status:
            query = query.filter(OrdemServico.status.in_(filtros.status))
            
        if filtros.fase_atual:
            query = query.filter(OrdemServico.fase_atual.in_(filtros.fase_atual))
            
        if filtros.prioridade:
            query = query.filter(OrdemServico.prioridade.in_(filtros.prioridade))
            
        if filtros.data_inicio:
            query = query.filter(OrdemServico.data_abertura >= filtros.data_inicio)
            
        if filtros.data_fim:
            query = query.filter(OrdemServico.data_abertura <= filtros.data_fim)
            
        if filtros.responsavel_id:
            query = query.filter(
                or_(
                    OrdemServico.usuario_abertura_id == filtros.responsavel_id,
                    OrdemServico.responsavel_execucao_id == filtros.responsavel_id
                )
            )
        
        # Busca por texto
        if filtros.busca:
            busca_term = f"%{filtros.busca}%"
            query = query.filter(
                or_(
                    OrdemServico.numero_os.ilike(busca_term),
                    OrdemServico.descricao.ilike(busca_term),
                    OrdemServico.tipo_servico.ilike(busca_term)
                )
            )
        
        # Total de registros
        total = query.count()
        
        # Ordenação
        query = query.order_by(OrdemServico.data_abertura.desc())
        
        # Paginação
        ordens = query.offset(skip).limit(limit).all()
        
        return ListagemOrdemServico(
            itens=ordens,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar OS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/{os_id}", response_model=OrdemServicoResponse)
async def obter_ordem_servico(
    os_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obter detalhes completos de uma Ordem de Serviço.
    
    Inclui:
    - Dados da OS
    - Fases executadas
    - Itens da OS
    - Histórico de mudanças
    - Visitas técnicas
    """
    try:
        os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
        
        if not os_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERRO_OS_NAO_ENCONTRADA
            )
        
        return os_obj
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter OS {os_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.put("/{os_id}", response_model=OrdemServicoResponse)
async def atualizar_ordem_servico(
    os_id: int,
    os_update: OrdemServicoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """
    Atualizar dados de uma Ordem de Serviço.
    
    Permite atualizar:
    - Descrição
    - Tipo de serviço
    - Prioridade
    - Observações
    - Responsável da execução
    """
    try:
        os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
        
        if not os_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERRO_OS_NAO_ENCONTRADA
            )
        
        # Atualizar campos permitidos
        update_data = os_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(os_obj, field, value)
        
        os_obj.data_atualizacao = datetime.now()
        
        db.commit()
        db.refresh(os_obj)
        
        logger.info(f"OS {os_obj.numero_os} atualizada por {current_user['username']}")
        return os_obj
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar OS {os_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# =============================================================================
# ENDPOINTS DE WORKFLOW - CONTROLE DE FASES
# =============================================================================

@router.post("/{os_id}/mudar-fase", response_model=OrdemServicoResponse)
async def mudar_fase_os(
    os_id: int,
    mudanca: MudancaFaseRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """
    Mudar fase da Ordem de Serviço.
    
    Workflow das 7 fases:
    1. Abertura da OS
    2. Visita Técnica
    3. Orçamento
    4. Envio e Acompanhamento
    5. Execução
    6. Finalização
    7. Arquivo
    """
    try:
        os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
        
        if not os_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERRO_OS_NAO_ENCONTRADA
            )
        
        # Validar transição de fase
        fase_atual = os_obj.fase_atual
        nova_fase = mudanca.nova_fase
        
        # Regras de transição
        if nova_fase < 1 or nova_fase > 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fase deve estar entre 1 e 7"
            )
        
        # Não permitir retroceder mais de 1 fase (exceto admin)
        if nova_fase < fase_atual - 1 and current_user["perfil"] != "administrador":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível retroceder mais de uma fase"
            )
        
        # Salvar fase anterior
        fase_anterior = os_obj.fase_atual
        
        # Atualizar OS
        os_obj.fase_atual = nova_fase
        os_obj.data_atualizacao = datetime.now()
        
        # Atualizar status baseado na fase
        status_por_fase = {
            1: "ABERTA",
            2: "VISITA_AGENDADA", 
            3: "ORCAMENTO",
            4: "AGUARDANDO_APROVACAO",
            5: "EM_EXECUCAO",
            6: "FINALIZADA",
            7: "ARQUIVADA"
        }
        
        os_obj.status = status_por_fase.get(nova_fase, "ABERTA")
        
        # Criar registro da nova fase
        nome_fases = {
            1: "Abertura da OS",
            2: "Visita Técnica", 
            3: "Orçamento",
            4: "Envio e Acompanhamento",
            5: "Execução",
            6: "Finalização",
            7: "Arquivo"
        }
        
        nova_fase_obj = FaseOS(
            ordem_servico_id=os_id,
            numero_fase=nova_fase,
            nome_fase=nome_fases[nova_fase],
            data_inicio=datetime.now(),
            responsavel_id=current_user["id"],
            status="EM_ANDAMENTO",
            observacoes=mudanca.observacoes
        )
        
        db.add(nova_fase_obj)
        
        # Marcar fase anterior como concluída
        if fase_anterior != nova_fase:
            fase_anterior_obj = db.query(FaseOS).filter(
                and_(
                    FaseOS.ordem_servico_id == os_id,
                    FaseOS.numero_fase == fase_anterior
                )
            ).first()
            
            if fase_anterior_obj:
                fase_anterior_obj.status = "CONCLUIDA"
                fase_anterior_obj.data_conclusao = datetime.now()
        
        # Criar histórico
        historico = OSHistorico(
            ordem_servico_id=os_id,
            fase_anterior=fase_anterior,
            fase_nova=nova_fase,
            usuario_id=current_user["id"],
            observacoes=mudanca.observacoes or f"Mudança da fase {fase_anterior} para {nova_fase}"
        )
        
        db.add(historico)
        db.commit()
        db.refresh(os_obj)
        
        # Enviar notificação WhatsApp baseada na fase
        try:
            comunicacao = ComunicacaoService()
            
            if nova_fase == 2:  # Visita Técnica
                await comunicacao.enviar_template_visita_agendada(
                    os_numero=os_obj.numero_os,
                    cliente_nome=os_obj.cliente.nome if hasattr(os_obj, 'cliente') else "Cliente"
                )
            elif nova_fase == 3:  # Orçamento
                await comunicacao.enviar_template_orcamento_pronto(
                    os_numero=os_obj.numero_os,
                    cliente_nome=os_obj.cliente.nome if hasattr(os_obj, 'cliente') else "Cliente"
                )
            elif nova_fase == 6:  # Finalização
                await comunicacao.enviar_template_servico_concluido(
                    os_numero=os_obj.numero_os,
                    cliente_nome=os_obj.cliente.nome if hasattr(os_obj, 'cliente') else "Cliente"
                )
                
        except Exception as e:
            logger.warning(f"Erro ao enviar WhatsApp para OS {os_obj.numero_os}: {e}")
        
        logger.info(f"OS {os_obj.numero_os} mudou da fase {fase_anterior} para {nova_fase}")
        return os_obj
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao mudar fase da OS {os_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/{os_id}/fases", response_model=List[FaseOSResponse])
async def listar_fases_os(
    os_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Listar todas as fases de uma OS"""
    try:
        os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
        
        if not os_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERRO_OS_NAO_ENCONTRADA
            )
        
        fases = db.query(FaseOS).filter(
            FaseOS.ordem_servico_id == os_id
        ).order_by(FaseOS.numero_fase).all()
        
        return fases
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar fases da OS {os_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/{os_id}/historico", response_model=List[HistoricoMudanca])
async def obter_historico_os(
    os_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obter histórico completo de mudanças da OS"""
    try:
        os_obj = db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
        
        if not os_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERRO_OS_NAO_ENCONTRADA
            )
        
        historico = db.query(OSHistorico).filter(
            OSHistorico.ordem_servico_id == os_id
        ).order_by(OSHistorico.created_at.desc()).all()
        
        return historico
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter histórico da OS {os_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# =============================================================================
# ENDPOINTS DE ESTATÍSTICAS E RELATÓRIOS
# =============================================================================

@router.get("/estatisticas/dashboard", response_model=DashboardOS)
async def obter_dashboard_os(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obter estatísticas para dashboard de OS"""
    try:
        # Contadores gerais
        total_os = db.query(OrdemServico).count()
        
        os_abertas = db.query(OrdemServico).filter(
            OrdemServico.status.in_(["ABERTA", "VISITA_AGENDADA", "ORCAMENTO", "AGUARDANDO_APROVACAO", "EM_EXECUCAO"])
        ).count()
        
        os_finalizadas = db.query(OrdemServico).filter(
            OrdemServico.status == "FINALIZADA"
        ).count()
        
        os_arquivadas = db.query(OrdemServico).filter(
            OrdemServico.status == "ARQUIVADA"
        ).count()
        
        # OS por fase
        os_por_fase = {}
        for fase in range(1, 8):
            count = db.query(OrdemServico).filter(OrdemServico.fase_atual == fase).count()
            os_por_fase[f"fase_{fase}"] = count
        
        # OS por prioridade
        os_por_prioridade = {}
        for prioridade in ["baixa", "normal", "alta", "urgente"]:
            count = db.query(OrdemServico).filter(OrdemServico.prioridade == prioridade).count()
            os_por_prioridade[prioridade] = count
        
        # OS do mês atual
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        os_mes_atual = db.query(OrdemServico).filter(
            OrdemServico.data_abertura >= inicio_mes
        ).count()
        
        return DashboardOS(
            total_os=total_os,
            os_abertas=os_abertas,
            os_finalizadas=os_finalizadas,
            os_arquivadas=os_arquivadas,
            os_por_fase=os_por_fase,
            os_por_prioridade=os_por_prioridade,
            os_mes_atual=os_mes_atual
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter dashboard OS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/estatisticas/geral", response_model=EstatisticasOS)
async def obter_estatisticas_os(
    data_inicio: Optional[date] = Query(None, description="Data de início do período"),
    data_fim: Optional[date] = Query(None, description="Data de fim do período"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obter estatísticas gerais de OS com filtro de período"""
    try:
        query = db.query(OrdemServico)
        
        # Filtrar por período se fornecido
        if data_inicio:
            query = query.filter(OrdemServico.data_abertura >= data_inicio)
        if data_fim:
            query = query.filter(OrdemServico.data_abertura <= data_fim)
        
        # Estatísticas básicas
        total = query.count()
        
        # Média de dias por fase
        # ... implementar cálculos mais complexos
        
        return EstatisticasOS(
            total_os=total,
            periodo_inicio=data_inicio,
            periodo_fim=data_fim,
            # ... outros campos
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas OS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )