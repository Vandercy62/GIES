"""
SISTEMA ERP PRIMOTEX - ROUTER DE FORNECEDORES
============================================

Router FastAPI para endpoints de fornecedores.
Implementa CRUD completo com validação e filtros.

ENDPOINTS DISPONÍVEIS:
- GET /fornecedores - Lista fornecedores (com filtros)
- POST /fornecedores - Cria novo fornecedor
- GET /fornecedores/{id} - Busca fornecedor por ID
- PUT /fornecedores/{id} - Atualiza fornecedor
- DELETE /fornecedores/{id} - Remove fornecedor
- GET /fornecedores/stats - Estatísticas

Autor: GitHub Copilot
Data: 01/11/2025
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc

# Imports do projeto
from backend.database.config import get_db
from backend.models.fornecedor_model import Fornecedor
from backend.schemas.fornecedor_schemas import (
    FornecedorCreate,
    FornecedorUpdate,
    FornecedorResponse,
    FornecedorListResponse,
    FornecedorListItem,
    FornecedorResumo,
    EstatisticasFornecedor,
    StatusFornecedor,
    CategoriaFornecedor,
    TipoFornecedor
)
from backend.auth.dependencies import get_current_user
from backend.models.user_model import Usuario

# Criar router
router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])


# =======================================
# ENDPOINTS DE LISTAGEM
# =======================================

@router.get("", response_model=FornecedorListResponse)
async def listar_fornecedores(
    # Filtros de busca
    search: Optional[str] = Query(
        None, 
        description="Busca por nome, CNPJ, email"
    ),
    categoria: Optional[CategoriaFornecedor] = Query(None),
    tipo_pessoa: Optional[TipoFornecedor] = Query(None),
    status: Optional[StatusFornecedor] = Query(None),
    ativo: Optional[bool] = Query(None),
    cidade: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    avaliacao_minima: Optional[int] = Query(None, ge=1, le=5),
    
    # Paginação
    page: int = Query(1, ge=1, description="Página"),
    size: int = Query(50, ge=1, le=200, description="Itens por página"),
    
    # Ordenação
    order_by: str = Query("razao_social", description="Campo para ordenação"),
    order_direction: str = Query("asc", description="Direção (asc/desc)"),
    
    # Dependências
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista fornecedores com filtros e paginação"""
    
    try:
        # Query base
        query = db.query(Fornecedor)
        
        # Aplicar filtros
        conditions = []
        
        # Filtro de busca textual
        if search:
            search_term = f"%{search}%"
            conditions.append(
                or_(
                    Fornecedor.razao_social.ilike(search_term),
                    Fornecedor.nome_fantasia.ilike(search_term),
                    Fornecedor.cnpj_cpf.ilike(search_term),
                    Fornecedor.email.ilike(search_term),
                    Fornecedor.contato_principal.ilike(search_term)
                )
            )
        
        # Filtros específicos
        if categoria:
            conditions.append(Fornecedor.categoria == categoria.value)
        
        if tipo_pessoa:
            conditions.append(Fornecedor.tipo_pessoa == tipo_pessoa.value)
        
        if status:
            conditions.append(Fornecedor.status == status.value)
        
        if ativo is not None:
            conditions.append(Fornecedor.ativo == ativo)
        
        if cidade:
            conditions.append(Fornecedor.cidade.ilike(f"%{cidade}%"))
        
        if estado:
            conditions.append(Fornecedor.estado == estado.upper())
        
        if avaliacao_minima:
            conditions.append(Fornecedor.avaliacao >= avaliacao_minima)
        
        # Aplicar condições
        if conditions:
            query = query.filter(and_(*conditions))
        
        # Contar total
        total = query.count()
        
        # Aplicar ordenação
        order_field = getattr(Fornecedor, order_by, Fornecedor.razao_social)
        if order_direction.lower() == "desc":
            query = query.order_by(desc(order_field))
        else:
            query = query.order_by(asc(order_field))
        
        # Aplicar paginação
        offset = (page - 1) * size
        fornecedores = query.offset(offset).limit(size).all()
        
        # Calcular número de páginas
        pages = (total + size - 1) // size
        
        # Converter para formato de resposta
        items = []
        for fornecedor in fornecedores:
            item = FornecedorListItem(
                id=fornecedor.id,
                cnpj_cpf=fornecedor.cnpj_cpf,
                razao_social=fornecedor.razao_social,
                nome_fantasia=fornecedor.nome_fantasia,
                categoria=fornecedor.categoria,
                telefone=fornecedor.telefone,
                email=fornecedor.email,
                cidade=fornecedor.cidade,
                status=fornecedor.status,
                ativo=fornecedor.ativo,
                avaliacao=fornecedor.avaliacao,
                data_cadastro=fornecedor.data_cadastro,
                nome_exibicao=fornecedor.nome_exibicao,
                documento_formatado=fornecedor.documento_formatado
            )
            items.append(item)
        
        return FornecedorListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar fornecedores: {str(e)}"
        )


@router.get("/resumo", response_model=List[FornecedorResumo])
async def listar_fornecedores_resumo(
    ativo: bool = Query(True, description="Apenas ativos"),
    categoria: Optional[CategoriaFornecedor] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista resumo de fornecedores para seleção"""
    
    try:
        query = db.query(Fornecedor)
        
        # Filtros
        if ativo:
            query = query.filter(Fornecedor.ativo == True)
        
        if categoria:
            query = query.filter(Fornecedor.categoria == categoria.value)
        
        # Ordenar por nome
        query = query.order_by(Fornecedor.razao_social)
        
        fornecedores = query.all()
        
        return [
            FornecedorResumo(
                id=f.id,
                nome_exibicao=f.nome_exibicao,
                documento_formatado=f.documento_formatado,
                categoria=f.categoria,
                telefone=f.telefone
            )
            for f in fornecedores
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar resumo: {str(e)}"
        )


# =======================================
# ENDPOINTS CRUD
# =======================================

@router.post("", response_model=FornecedorResponse, status_code=status.HTTP_201_CREATED)
async def criar_fornecedor(
    fornecedor_data: FornecedorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cria novo fornecedor"""
    
    try:
        # Verificar se CNPJ/CPF já existe
        existing = db.query(Fornecedor).filter(
            Fornecedor.cnpj_cpf == fornecedor_data.cnpj_cpf
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ/CPF já cadastrado"
            )
        
        # Criar novo fornecedor
        fornecedor = Fornecedor(**fornecedor_data.model_dump())
        fornecedor.usuario_cadastro_id = current_user.id
        fornecedor.atualizar_endereco_completo()
        
        db.add(fornecedor)
        db.commit()
        db.refresh(fornecedor)
        
        return FornecedorResponse.model_validate(fornecedor)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar fornecedor: {str(e)}"
        )


@router.get("/{fornecedor_id}", response_model=FornecedorResponse)
async def buscar_fornecedor(
    fornecedor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Busca fornecedor por ID"""
    
    try:
        fornecedor = db.query(Fornecedor).filter(
            Fornecedor.id == fornecedor_id
        ).first()
        
        if not fornecedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fornecedor não encontrado"
            )
        
        return FornecedorResponse.model_validate(fornecedor)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar fornecedor: {str(e)}"
        )


@router.put("/{fornecedor_id}", response_model=FornecedorResponse)
async def atualizar_fornecedor(
    fornecedor_id: int,
    fornecedor_data: FornecedorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualiza fornecedor"""
    
    try:
        # Buscar fornecedor
        fornecedor = db.query(Fornecedor).filter(
            Fornecedor.id == fornecedor_id
        ).first()
        
        if not fornecedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fornecedor não encontrado"
            )
        
        # Atualizar campos
        update_data = fornecedor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(fornecedor, field, value)
        
        # Atualizar campos de auditoria
        fornecedor.usuario_atualizacao_id = current_user.id
        fornecedor.atualizar_endereco_completo()
        
        db.commit()
        db.refresh(fornecedor)
        
        return FornecedorResponse.model_validate(fornecedor)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar fornecedor: {str(e)}"
        )


@router.delete("/{fornecedor_id}")
async def remover_fornecedor(
    fornecedor_id: int,
    force: bool = Query(False, description="Forçar remoção"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Remove fornecedor (soft delete por padrão)"""
    
    try:
        # Buscar fornecedor
        fornecedor = db.query(Fornecedor).filter(
            Fornecedor.id == fornecedor_id
        ).first()
        
        if not fornecedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fornecedor não encontrado"
            )
        
        if force:
            # Remoção física (verificar dependências)
            # TODO: Verificar se há contas a pagar vinculadas
            db.delete(fornecedor)
        else:
            # Soft delete
            fornecedor.ativo = False
            fornecedor.status = StatusFornecedor.INATIVO.value
            fornecedor.motivo_inativacao = "Removido pelo usuário"
            fornecedor.usuario_atualizacao_id = current_user.id
        
        db.commit()
        
        return {"message": "Fornecedor removido com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover fornecedor: {str(e)}"
        )


# =======================================
# ENDPOINTS DE ESTATÍSTICAS
# =======================================

@router.get("/stats/resumo", response_model=EstatisticasFornecedor)
async def estatisticas_fornecedores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Estatísticas dos fornecedores"""
    
    try:
        # Total de fornecedores
        total_fornecedores = db.query(Fornecedor).count()
        
        # Total ativos/inativos
        total_ativos = db.query(Fornecedor).filter(
            Fornecedor.ativo == True
        ).count()
        total_inativos = total_fornecedores - total_ativos
        
        # Total por categoria
        categorias = db.query(
            Fornecedor.categoria,
            func.count(Fornecedor.id).label('total')
        ).filter(
            Fornecedor.ativo == True
        ).group_by(Fornecedor.categoria).all()
        
        total_por_categoria = {cat: total for cat, total in categorias}
        
        # Total por estado
        estados = db.query(
            Fornecedor.estado,
            func.count(Fornecedor.id).label('total')
        ).filter(
            Fornecedor.ativo == True,
            Fornecedor.estado.isnot(None)
        ).group_by(Fornecedor.estado).all()
        
        total_por_estado = {est: total for est, total in estados}
        
        # Avaliação média
        avaliacao_media = db.query(
            func.avg(Fornecedor.avaliacao)
        ).filter(
            Fornecedor.ativo == True,
            Fornecedor.avaliacao.isnot(None)
        ).scalar()
        
        return EstatisticasFornecedor(
            total_fornecedores=total_fornecedores,
            total_ativos=total_ativos,
            total_inativos=total_inativos,
            total_por_categoria=total_por_categoria,
            total_por_estado=total_por_estado,
            avaliacao_media=float(avaliacao_media) if avaliacao_media else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular estatísticas: {str(e)}"
        )


# =======================================
# ENDPOINTS AUXILIARES
# =======================================

@router.get("/cnpj/{cnpj}", response_model=dict)
async def validar_cnpj(
    cnpj: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Valida se CNPJ já está cadastrado"""
    
    try:
        # Remover formatação
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        
        # Verificar se existe
        exists = db.query(Fornecedor).filter(
            Fornecedor.cnpj_cpf == cnpj_limpo
        ).first()
        
        return {
            "cnpj": cnpj_limpo,
            "exists": exists is not None,
            "fornecedor_id": exists.id if exists else None,
            "nome": exists.razao_social if exists else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao validar CNPJ: {str(e)}"
        )


@router.patch("/{fornecedor_id}/status")
async def alterar_status_fornecedor(
    fornecedor_id: int,
    novo_status: StatusFornecedor,
    motivo: Optional[str] = Query(None, description="Motivo da alteração"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Altera status do fornecedor"""
    
    try:
        # Buscar fornecedor
        fornecedor = db.query(Fornecedor).filter(
            Fornecedor.id == fornecedor_id
        ).first()
        
        if not fornecedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fornecedor não encontrado"
            )
        
        # Atualizar status
        fornecedor.status = novo_status.value
        fornecedor.ativo = (novo_status == StatusFornecedor.ATIVO)
        
        if motivo:
            if novo_status != StatusFornecedor.ATIVO:
                fornecedor.motivo_inativacao = motivo
            else:
                fornecedor.motivo_inativacao = None
        
        fornecedor.usuario_atualizacao_id = current_user.id
        
        db.commit()
        
        return {
            "message": f"Status alterado para {novo_status.value}",
            "status": novo_status.value,
            "ativo": fornecedor.ativo
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar status: {str(e)}"
        )