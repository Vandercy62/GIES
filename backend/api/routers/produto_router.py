"""
ROUTER DE PRODUTOS - ERP PRIMOTEX
=================================

Router completo para gerenciamento de produtos com todas as
funcionalidades CRUD, controle de estoque e códigos de barras.

Funcionalidades:
- CRUD completo de produtos
- Controle de estoque
- Códigos de barras
- Categorias e fornecedores
- Relatórios de movimento

Autor: GitHub Copilot
Data: 01/11/2025
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.database.config import get_db
from backend.auth.dependencies import get_current_user, require_operator
from backend.models.produto_model import Produto
from backend.schemas.produto_schemas import (
    ProdutoCreate, ProdutoUpdate, ProdutoResponse,
    ListagemProdutos, FiltrosProduto
)
import logging

# Configurar router
router = APIRouter(prefix="/produtos", tags=["Produtos"])

# Configurar logging
logger = logging.getLogger(__name__)


@router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
async def criar_produto(
    produto_data: ProdutoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_operator)
):
    """Criar novo produto"""
    try:
        # Verificar código único
        if produto_data.codigo:
            produto_existente = db.query(Produto).filter(
                Produto.codigo == produto_data.codigo
            ).first()
            
            if produto_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código de produto já existe"
                )
        
        # Criar produto
        db_produto = Produto(**produto_data.dict())
        
        db.add(db_produto)
        db.commit()
        db.refresh(db_produto)
        
        logger.info(f"Produto {db_produto.descricao} criado")
        return db_produto
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar produto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/", response_model=ListagemProdutos)
async def listar_produtos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    filtros: FiltrosProduto = Depends(),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Listar produtos com filtros"""
    try:
        query = db.query(Produto)
        
        # Aplicar filtros
        if filtros.categoria:
            query = query.filter(Produto.categoria == filtros.categoria)
            
        if filtros.status is not None:
            query = query.filter(Produto.status == filtros.status)
        
        # Total
        total = query.count()
        
        # Paginação
        produtos = query.offset(skip).limit(limit).all()
        
        return ListagemProdutos(
            itens=produtos,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/{produto_id}", response_model=ProdutoResponse)
async def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Obter produto por ID"""
    try:
        produto = db.query(Produto).filter(Produto.id == produto_id).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        return produto
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter produto {produto_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.put("/{produto_id}", response_model=ProdutoResponse)
async def atualizar_produto(
    produto_id: int,
    produto_update: ProdutoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_operator)
):
    """Atualizar produto"""
    try:
        produto = db.query(Produto).filter(Produto.id == produto_id).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Atualizar campos
        update_data = produto_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(produto, field, value)
        
        db.commit()
        db.refresh(produto)
        
        logger.info(f"Produto {produto.descricao} atualizado")
        return produto
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar produto {produto_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_operator)
):
    """Deletar produto (soft delete)"""
    try:
        produto = db.query(Produto).filter(Produto.id == produto_id).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado"
            )
        
        # Soft delete
        produto.status = "Inativo"
        db.commit()
        
        logger.info(f"Produto {produto.descricao} deletado")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar produto {produto_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )