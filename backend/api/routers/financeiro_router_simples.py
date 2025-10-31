"""
Router FastAPI Financeiro - Versão Simplificada
Sistema ERP Primotex - Endpoints básicos funcionais

Desenvolvido com foco em funcionalidade e testes rápidos.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

# Imports dos schemas Pydantic
from backend.schemas.financeiro_schemas import (
    ContaReceberCreate, ContaReceberUpdate, ContaReceberResponse,
    ContaPagarCreate, ContaPagarUpdate, ContaPagarResponse,
    MovimentacaoFinanceiraCreate, MovimentacaoFinanceiraResponse,
    CategoriaFinanceiraCreate, CategoriaFinanceiraResponse,
    TipoMovimentacao, StatusFinanceiro
)

# Imports dos models SQLAlchemy
from backend.models.financeiro_model import (
    ContaReceber, ContaPagar, MovimentacaoFinanceira, CategoriaFinanceira
)

# Imports de dependências
from backend.database.config import get_db

# Mock function para autenticação (temporário)
def get_current_user():
    return {"id": 1, "username": "admin", "email": "admin@test.com"}

# Configuração do router
router = APIRouter(
    prefix="/api/v1/financeiro",
    tags=["financeiro"],
    dependencies=[Depends(get_current_user)]
)

# Constantes
ERRO_INTERNO = "Erro interno do servidor"
CONTA_NAO_ENCONTRADA = "Conta não encontrada"

# =============================================================================
# ENDPOINTS - CONTAS A RECEBER
# =============================================================================

@router.get("/contas-receber", response_model=List[ContaReceberResponse])
async def listar_contas_receber(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lista contas a receber"""
    try:
        contas = db.query(ContaReceber).filter(
            ContaReceber.ativo == True
        ).offset(skip).limit(limit).all()
        return contas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ERRO_INTERNO}: {str(e)}"
        )

@router.post("/contas-receber", response_model=ContaReceberResponse)
async def criar_conta_receber(
    conta: ContaReceberCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cria nova conta a receber"""
    try:
        db_conta = ContaReceber(**conta.model_dump())
        db_conta.usuario_criacao_id = current_user["id"]
        
        db.add(db_conta)
        db.commit()
        db.refresh(db_conta)
        
        return db_conta
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ERRO_INTERNO}: {str(e)}"
        )

@router.get("/contas-receber/{conta_id}", response_model=ContaReceberResponse)
async def obter_conta_receber(
    conta_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtém uma conta a receber"""
    conta = db.query(ContaReceber).filter(
        ContaReceber.id == conta_id,
        ContaReceber.ativo == True
    ).first()
    
    if not conta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CONTA_NAO_ENCONTRADA
        )
    
    return conta

@router.put("/contas-receber/{conta_id}", response_model=ContaReceberResponse)
async def atualizar_conta_receber(
    conta_id: int,
    conta_update: ContaReceberUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Atualiza conta a receber"""
    try:
        db_conta = db.query(ContaReceber).filter(
            ContaReceber.id == conta_id,
            ContaReceber.ativo == True
        ).first()
        
        if not db_conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTA_NAO_ENCONTRADA
            )
        
        update_data = conta_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_conta, field, value)
        
        db_conta.data_atualizacao = datetime.now()
        db_conta.usuario_atualizacao_id = current_user["id"]
        
        db.commit()
        db.refresh(db_conta)
        
        return db_conta
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ERRO_INTERNO}: {str(e)}"
        )

@router.delete("/contas-receber/{conta_id}")
async def excluir_conta_receber(
    conta_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Exclui conta a receber"""
    try:
        db_conta = db.query(ContaReceber).filter(
            ContaReceber.id == conta_id,
            ContaReceber.ativo == True
        ).first()
        
        if not db_conta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CONTA_NAO_ENCONTRADA
            )
        
        db_conta.ativo = False
        db_conta.data_atualizacao = datetime.now()
        db_conta.usuario_atualizacao_id = current_user["id"]
        
        db.commit()
        
        return {"message": "Conta excluída com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ERRO_INTERNO}: {str(e)}"
        )

# =============================================================================
# ENDPOINTS - CONTAS A PAGAR
# =============================================================================

@router.get("/contas-pagar", response_model=List[ContaPagarResponse])
async def listar_contas_pagar(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lista contas a pagar"""
    try:
        contas = db.query(ContaPagar).filter(
            ContaPagar.ativo == True
        ).offset(skip).limit(limit).all()
        return contas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ERRO_INTERNO}: {str(e)}"
        )

@router.post("/contas-pagar", response_model=ContaPagarResponse)
async def criar_conta_pagar(
    conta: ContaPagarCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cria nova conta a pagar"""
    try:
        db_conta = ContaPagar(**conta.model_dump())
        db_conta.usuario_criacao_id = current_user["id"]
        
        db.add(db_conta)
        db.commit()
        db.refresh(db_conta)
        
        return db_conta
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ERRO_INTERNO}: {str(e)}"
        )

# =============================================================================
# ENDPOINTS - MOVIMENTAÇÕES
# =============================================================================

@router.get("/movimentacoes", response_model=List[MovimentacaoFinanceiraResponse])
async def listar_movimentacoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lista movimentações financeiras"""
    try:
        movimentacoes = db.query(MovimentacaoFinanceira).filter(
            MovimentacaoFinanceira.ativo == True
        ).offset(skip).limit(limit).all()
        return movimentacoes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ERRO_INTERNO}: {str(e)}"
        )

@router.post("/movimentacoes", response_model=MovimentacaoFinanceiraResponse)
async def criar_movimentacao(
    movimentacao: MovimentacaoFinanceiraCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cria nova movimentação"""
    try:
        db_movimentacao = MovimentacaoFinanceira(**movimentacao.model_dump())
        db_movimentacao.usuario_criacao_id = current_user["id"]
        
        db.add(db_movimentacao)
        db.commit()
        db.refresh(db_movimentacao)
        
        return db_movimentacao
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ERRO_INTERNO}: {str(e)}"
        )

# =============================================================================
# ENDPOINTS - CATEGORIAS
# =============================================================================

@router.get("/categorias", response_model=List[CategoriaFinanceiraResponse])
async def listar_categorias(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lista categorias financeiras"""
    categorias = db.query(CategoriaFinanceira).filter(
        CategoriaFinanceira.ativo == True
    ).all()
    return categorias

@router.post("/categorias", response_model=CategoriaFinanceiraResponse)
async def criar_categoria(
    categoria: CategoriaFinanceiraCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Cria nova categoria"""
    try:
        db_categoria = CategoriaFinanceira(**categoria.model_dump())
        db_categoria.usuario_criacao_id = current_user["id"]
        
        db.add(db_categoria)
        db.commit()
        db.refresh(db_categoria)
        
        return db_categoria
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ERRO_INTERNO}: {str(e)}"
        )

# =============================================================================
# ENDPOINTS - DASHBOARD E UTILIDADES
# =============================================================================

@router.get("/dashboard/resumo")
async def obter_resumo_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Resumo do dashboard financeiro"""
    try:
        total_receber = db.query(func.count(ContaReceber.id)).filter(
            ContaReceber.ativo == True
        ).scalar() or 0
        
        total_pagar = db.query(func.count(ContaPagar.id)).filter(
            ContaPagar.ativo == True
        ).scalar() or 0
        
        total_movimentacoes = db.query(func.count(MovimentacaoFinanceira.id)).filter(
            MovimentacaoFinanceira.ativo == True
        ).scalar() or 0
        
        return {
            "total_contas_receber": total_receber,
            "total_contas_pagar": total_pagar,
            "total_movimentacoes": total_movimentacoes,
            "data_atualizacao": datetime.now()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ERRO_INTERNO}: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check do módulo financeiro"""
    return {
        "status": "healthy",
        "module": "financeiro",
        "timestamp": datetime.now(),
        "endpoints_count": 12
    }

@router.get("/estatisticas")
async def obter_estatisticas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Estatísticas básicas"""
    try:
        stats = {
            "contas_receber": db.query(func.count(ContaReceber.id)).filter(ContaReceber.ativo == True).scalar() or 0,
            "contas_pagar": db.query(func.count(ContaPagar.id)).filter(ContaPagar.ativo == True).scalar() or 0,
            "movimentacoes": db.query(func.count(MovimentacaoFinanceira.id)).filter(MovimentacaoFinanceira.ativo == True).scalar() or 0,
            "categorias": db.query(func.count(CategoriaFinanceira.id)).filter(CategoriaFinanceira.ativo == True).scalar() or 0,
            "data_calculo": datetime.now()
        }
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ERRO_INTERNO}: {str(e)}"
        )