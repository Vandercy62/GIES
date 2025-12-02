"""
ROUTER DE CLIENTES - ERP PRIMOTEX
================================

Router completo para gerenciamento de clientes com todas as
funcionalidades CRUD e validações específicas.

Funcionalidades:
- CRUD completo de clientes
- Validação CPF/CNPJ
- Busca avançada e filtros
- Histórico de relacionamento
- Integração com OS

Autor: GitHub Copilot
Data: 01/11/2025
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from backend.database.config import get_db
from backend.auth.dependencies import get_current_user, require_operator
from backend.models.cliente_model import Cliente
from backend.schemas.cliente_schemas import (
    ClienteCreate, ClienteUpdate, ClienteResponse, 
    ListagemClientes, FiltrosCliente
)
import logging

# Configurar router

# =============================================================================
# CONSTANTES
# =============================================================================

CLIENTE_NAO_ENCONTRADO = "Cliente não encontrado"

router = APIRouter(prefix="/clientes", tags=["Clientes"])

# Configurar logging
logger = logging.getLogger(__name__)


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def criar_cliente(
    cliente_data: ClienteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """Criar novo cliente"""
    try:
        # Verificar se CPF/CNPJ já existe
        if cliente_data.cpf_cnpj:
            cliente_existente = db.query(Cliente).filter(
                Cliente.cpf_cnpj == cliente_data.cpf_cnpj
            ).first()

            if cliente_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF/CNPJ já cadastrado"
                )

        # Gerar código único do cliente
        ultimo_cliente = db.query(Cliente).order_by(Cliente.id.desc()).first()
        proximo_numero = (ultimo_cliente.id + 1) if ultimo_cliente else 1
        codigo_cliente = f"CLI{proximo_numero:05d}"  # Ex: CLI00001, CLI00002

        # Criar cliente
        db_cliente = Cliente(**cliente_data.dict())
        setattr(db_cliente, "codigo", codigo_cliente)
        db_cliente.usuario_criacao_id = current_user.id

        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)

        logger.info(f"Cliente {db_cliente.nome} ({codigo_cliente}) criado por {current_user.username}")
        return db_cliente

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar cliente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/", response_model=ListagemClientes)
async def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    filtros: FiltrosCliente = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Listar clientes com filtros e paginação"""
    try:
        query = db.query(Cliente)

        # Aplicar filtros
        if filtros.nome:
            query = query.filter(Cliente.nome.ilike(f"%{filtros.nome}%"))

        if filtros.tipo_pessoa:
            query = query.filter(Cliente.tipo_pessoa == filtros.tipo_pessoa)

        if filtros.cidade:
            query = query.filter(Cliente.cidade.ilike(f"%{filtros.cidade}%"))

        if filtros.ativo is not None:
            query = query.filter(Cliente.ativo == filtros.ativo)

        # Busca geral
        if filtros.busca:
            busca_term = f"%{filtros.busca}%"
            query = query.filter(
                or_(
                    Cliente.nome.ilike(busca_term),
                    Cliente.cpf_cnpj.ilike(busca_term),
                    Cliente.email.ilike(busca_term),
                    Cliente.telefone.ilike(busca_term)
                )
            )

        # Total de registros
        total = query.count()

        # Ordenação
        query = query.order_by(Cliente.nome)

        # Paginação
        clientes = query.offset(skip).limit(limit).all()

        return ListagemClientes(
            itens=[ClienteResponse.from_orm(c) for c in clientes],
            total=total,
            skip=skip,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Erro ao listar clientes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def obter_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obter detalhes de um cliente"""
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CLIENTE_NAO_ENCONTRADO
            )

        return cliente

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter cliente {cliente_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def atualizar_cliente(
    cliente_id: int,
    cliente_update: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """Atualizar dados de um cliente"""
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CLIENTE_NAO_ENCONTRADO
            )

        # Verificar CPF/CNPJ duplicado se alterado
        if cliente_update.cpf_cnpj and cliente_update.cpf_cnpj != cliente.cpf_cnpj:
            cliente_existente = db.query(Cliente).filter(
                and_(
                    Cliente.cpf_cnpj == cliente_update.cpf_cnpj,
                    Cliente.id != cliente_id
                )
            ).first()

            if cliente_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF/CNPJ já cadastrado para outro cliente"
                )

        # Atualizar campos
        update_data = cliente_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(cliente, field, value)

        db.commit()
        db.refresh(cliente)

        logger.info(f"Cliente {cliente.nome} atualizado por {current_user.username}")
        return cliente

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar cliente {cliente_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_operator)
):
    """Deletar um cliente (soft delete)"""
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CLIENTE_NAO_ENCONTRADO
            )

        # Verificar se tem OS vinculadas
        if hasattr(cliente, 'ordens_servico') and cliente.ordens_servico:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cliente possui Ordens de Serviço vinculadas e não pode ser deletado"
            )

        # Soft delete
        cliente.ativo = False
        db.commit()

        logger.info(f"Cliente {cliente.nome} deletado por {current_user.username}")

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao deletar cliente {cliente_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )


@router.get("/{cliente_id}/historico")
async def obter_historico_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obter histórico de relacionamento com cliente"""
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()

        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CLIENTE_NAO_ENCONTRADO
            )

        # Buscar OS do cliente
        from backend.models.ordem_servico_model import OrdemServico

        ordens = db.query(OrdemServico).filter(
            OrdemServico.cliente_id == cliente_id
        ).order_by(OrdemServico.data_abertura.desc()).all()

        return {
            "cliente": cliente,
            "total_os": len(ordens),
            "ordens_servico": ordens
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter histórico do cliente {cliente_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )
