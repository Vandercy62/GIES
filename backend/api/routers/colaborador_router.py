#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA ERP PRIMOTEX - ROUTER DE COLABORADORES
==============================================

Router FastAPI para gestão completa de colaboradores.
Implementa CRUD completo com filtros, paginação e funcionalidades avançadas.

ENDPOINTS PRINCIPAIS:
- GET /colaboradores - Listagem com filtros
- POST /colaboradores - Criar colaborador
- GET /colaboradores/{id} - Buscar por ID
- PUT /colaboradores/{id} - Atualizar colaborador
- DELETE /colaboradores/{id} - Inativar colaborador
- PATCH /colaboradores/{id}/status - Alterar status
- GET /colaboradores/stats/resumo - Estatísticas
- GET /colaboradores/matricula/{matricula} - Buscar por matrícula

ENDPOINTS AUXILIARES:
- GET /departamentos - Gestão de departamentos
- GET /cargos - Gestão de cargos
- POST /colaboradores/{id}/documentos - Upload documentos
- GET /colaboradores/{id}/avaliacoes - Avaliações de desempenho

Autor: GitHub Copilot
Data: 01/11/2025
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime, date

# Imports do projeto
from backend.database.config import get_db
from backend.models.colaborador_model import (
    Colaborador, Departamento, Cargo, StatusColaborador
)
from backend.schemas.colaborador_schemas import (
    # Colaborador schemas
    ColaboradorCreate, ColaboradorUpdate, ColaboradorResponse,
    ColaboradorDetalhado, ColaboradorListagem, ColaboradorFiltros,
    # Departamento schemas
    DepartamentoCreate, DepartamentoResponse,
    # Cargo schemas
    CargoCreate, CargoResponse,
    # Schemas auxiliares
    EstatisticasColaboradores, PaginationParams
)
from backend.auth.dependencies import get_current_user

# Criar router
router = APIRouter(prefix="/colaboradores", tags=["colaboradores"])


# =======================================
# ENDPOINTS DE COLABORADORES
# =======================================

@router.get("/", response_model=ColaboradorListagem)
async def listar_colaboradores(
    filtros: ColaboradorFiltros = Depends(),
    paginacao: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Listar colaboradores com filtros e paginação
    
    **Filtros disponíveis:**
    - search: Busca por nome, matrícula, CPF, email
    - departamento_id: Filtrar por departamento
    - cargo_id: Filtrar por cargo
    - status: Filtrar por status
    - ativo: Filtrar por ativo/inativo
    """
    try:
        # Query base com joins otimizados
        query = db.query(Colaborador).options(
            joinedload(Colaborador.cargo),
            joinedload(Colaborador.departamento),
            joinedload(Colaborador.usuario)
        )
        
        # Aplicar filtros
        if filtros.search:
            search_term = f"%{filtros.search}%"
            query = query.filter(
                or_(
                    Colaborador.nome_completo.ilike(search_term),
                    Colaborador.matricula.ilike(search_term),
                    Colaborador.cpf.ilike(search_term),
                    Colaborador.email_corporativo.ilike(search_term)
                )
            )
        
        if filtros.departamento_id:
            query = query.filter(
                Colaborador.departamento_id == filtros.departamento_id
            )
        
        if filtros.cargo_id:
            query = query.filter(Colaborador.cargo_id == filtros.cargo_id)
        
        if filtros.status:
            query = query.filter(Colaborador.status == filtros.status)
        
        if filtros.tipo_contrato:
            query = query.filter(
                Colaborador.tipo_contrato == filtros.tipo_contrato
            )
        
        if filtros.ativo is not None:
            query = query.filter(Colaborador.ativo == filtros.ativo)
        
        if filtros.data_admissao_inicio:
            query = query.filter(
                Colaborador.data_admissao >= filtros.data_admissao_inicio
            )
        
        if filtros.data_admissao_fim:
            query = query.filter(
                Colaborador.data_admissao <= filtros.data_admissao_fim
            )
        
        if filtros.tem_superior is not None:
            if filtros.tem_superior:
                query = query.filter(Colaborador.superior_direto_id.isnot(None))
            else:
                query = query.filter(Colaborador.superior_direto_id.is_(None))
        
        # Contar total
        total = query.count()
        
        # Aplicar paginação
        offset = (paginacao.page - 1) * paginacao.size
        # Buscar colaboradores com paginação
        colaboradores = (
            query
            .order_by(Colaborador.nome_completo)
            .offset(offset)
            .limit(paginacao.size)
            .all()
        )
        
        # Calcular páginas
        pages = (total + paginacao.size - 1) // paginacao.size
        
        return ColaboradorListagem(
            items=colaboradores,
            total=total,
            page=paginacao.page,
            size=paginacao.size,
            pages=pages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar colaboradores: {str(e)}"
        )


@router.post("/",
             response_model=ColaboradorResponse,
             status_code=status.HTTP_201_CREATED)
async def criar_colaborador(
    colaborador_data: ColaboradorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Criar novo colaborador
    
    **Campos obrigatórios:**
    - nome_completo
    - cpf (validado)
    - matricula (única)
    - user_id (usuário para login)
    - data_admissao
    - cargo_id
    - departamento_id
    - tipo_contrato
    """
    
    # Verificar se matrícula já existe
    if db.query(Colaborador).filter(Colaborador.matricula == colaborador_data.matricula).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Matrícula já existe"
        )
    
    # Verificar se CPF já existe
    cpf_limpo = ''.join(filter(str.isdigit, colaborador_data.cpf))
    if db.query(Colaborador).filter(Colaborador.cpf == cpf_limpo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )
    
    # Verificar se user_id já existe
    if db.query(Colaborador).filter(Colaborador.user_id == colaborador_data.user_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já vinculado a outro colaborador"
        )
    
    # Verificar se cargo existe
    cargo = db.query(Cargo).filter(Cargo.id == colaborador_data.cargo_id).first()
    if not cargo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cargo não encontrado"
        )
    
    # Verificar se departamento existe
    departamento = db.query(Departamento).filter(Departamento.id == colaborador_data.departamento_id).first()
    if not departamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Departamento não encontrado"
        )
    
    # Criar colaborador
    colaborador_dict = colaborador_data.dict()
    colaborador_dict['cpf'] = cpf_limpo
    colaborador_dict['cadastrado_por'] = current_user["id"]
    
    colaborador = Colaborador(**colaborador_dict)
    
    try:
        db.add(colaborador)
        db.commit()
        db.refresh(colaborador)
        
        return colaborador
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar colaborador: {str(e)}"
        )


@router.get("/{colaborador_id}", response_model=ColaboradorDetalhado)
async def buscar_colaborador(
    colaborador_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Buscar colaborador por ID com todos os detalhes"""
    
    colaborador = db.query(Colaborador).options(
        joinedload(Colaborador.cargo),
        joinedload(Colaborador.departamento),
        joinedload(Colaborador.usuario),
        joinedload(Colaborador.superior_direto)
    ).filter(Colaborador.id == colaborador_id).first()
    
    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado"
        )
    
    return colaborador


@router.put("/{colaborador_id}", response_model=ColaboradorResponse)
async def atualizar_colaborador(
    colaborador_id: int,
    colaborador_data: ColaboradorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Atualizar dados do colaborador"""
    
    colaborador = db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()
    
    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado"
        )
    
    # Atualizar apenas campos fornecidos
    update_data = colaborador_data.dict(exclude_unset=True)
    
    # Verificar mudança de cargo/departamento
    if 'cargo_id' in update_data and update_data['cargo_id'] != colaborador.cargo_id:
        cargo = db.query(Cargo).filter(Cargo.id == update_data['cargo_id']).first()
        if not cargo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cargo não encontrado"
            )
    
    if 'departamento_id' in update_data and update_data['departamento_id'] != colaborador.departamento_id:
        departamento = db.query(Departamento).filter(Departamento.id == update_data['departamento_id']).first()
        if not departamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Departamento não encontrado"
            )
    
    # Aplicar atualizações
    for field, value in update_data.items():
        setattr(colaborador, field, value)
    
    colaborador.data_atualizacao = datetime.now()
    
    try:
        db.commit()
        db.refresh(colaborador)
        return colaborador
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar colaborador: {str(e)}"
        )


@router.patch("/{colaborador_id}/status")
async def alterar_status_colaborador(
    colaborador_id: int,
    novo_status: StatusColaborador,
    motivo: Optional[str] = Query(None, description="Motivo da alteração"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Alterar status do colaborador (Ativo, Inativo, Férias, etc.)"""
    
    colaborador = db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()
    
    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado"
        )
    
    status_anterior = colaborador.status
    colaborador.status = novo_status
    colaborador.data_atualizacao = datetime.now()
    
    # Adicionar observação sobre mudança de status
    if motivo:
        observacao_atual = colaborador.observacoes or ""
        nova_observacao = f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M')}] Status alterado de {status_anterior.value} para {novo_status.value}. Motivo: {motivo}"
        colaborador.observacoes = observacao_atual + nova_observacao
    
    try:
        db.commit()
        return {"message": f"Status alterado para {novo_status.value}", "status_anterior": status_anterior.value}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar status: {str(e)}"
        )


@router.delete("/{colaborador_id}")
async def inativar_colaborador(
    colaborador_id: int,
    motivo: Optional[str] = Query(None, description="Motivo da inativação"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Inativar colaborador (soft delete)"""
    
    colaborador = db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()
    
    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado"
        )
    
    if not colaborador.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Colaborador já está inativo"
        )
    
    # Inativar colaborador
    colaborador.ativo = False
    colaborador.status = StatusColaborador.INATIVO
    colaborador.data_demissao = date.today()
    colaborador.data_atualizacao = datetime.now()
    
    # Adicionar observação
    if motivo:
        observacao_atual = colaborador.observacoes or ""
        nova_observacao = f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M')}] Colaborador inativado. Motivo: {motivo}"
        colaborador.observacoes = observacao_atual + nova_observacao
    
    try:
        db.commit()
        return {"message": "Colaborador inativado com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao inativar colaborador: {str(e)}"
        )


@router.get("/matricula/{matricula}", response_model=ColaboradorResponse)
async def buscar_por_matricula(
    matricula: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Buscar colaborador por matrícula"""
    
    colaborador = db.query(Colaborador).options(
        joinedload(Colaborador.cargo),
        joinedload(Colaborador.departamento)
    ).filter(Colaborador.matricula == matricula.upper()).first()
    
    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado"
        )
    
    return colaborador


@router.get("/stats/resumo", response_model=EstatisticasColaboradores)
async def estatisticas_colaboradores(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Obter estatísticas gerais dos colaboradores"""
    
    # Contadores gerais
    total_colaboradores = db.query(Colaborador).count()
    total_ativos = db.query(Colaborador).filter(Colaborador.ativo == True).count()
    total_inativos = db.query(Colaborador).filter(Colaborador.ativo == False).count()
    total_em_ferias = db.query(Colaborador).filter(Colaborador.status == StatusColaborador.FERIAS).count()
    total_afastados = db.query(Colaborador).filter(Colaborador.status == StatusColaborador.AFASTADO).count()
    
    # Por departamento
    por_departamento = {}
    departamentos_stats = db.query(
        Departamento.nome,
        func.count(Colaborador.id).label('total')
    ).join(Colaborador).group_by(Departamento.nome).all()
    
    for dept, total in departamentos_stats:
        por_departamento[dept] = total
    
    # Por cargo
    por_cargo = {}
    cargos_stats = db.query(
        Cargo.nome,
        func.count(Colaborador.id).label('total')
    ).join(Colaborador).group_by(Cargo.nome).all()
    
    for cargo, total in cargos_stats:
        por_cargo[cargo] = total
    
    # Por tipo de contrato
    por_tipo_contrato = {}
    contratos_stats = db.query(
        Colaborador.tipo_contrato,
        func.count(Colaborador.id).label('total')
    ).group_by(Colaborador.tipo_contrato).all()
    
    for contrato, total in contratos_stats:
        por_tipo_contrato[contrato.value] = total
    
    # Médias
    colaboradores_ativos = db.query(Colaborador).filter(Colaborador.ativo == True).all()
    
    if colaboradores_ativos:
        idades = [c.idade for c in colaboradores_ativos if c.idade > 0]
        idade_media = sum(idades) / len(idades) if idades else 0
        
        tempos_empresa = [c.tempo_empresa for c in colaboradores_ativos if c.tempo_empresa > 0]
        tempo_empresa_medio = sum(tempos_empresa) / len(tempos_empresa) if tempos_empresa else 0
        
        salarios = [float(c.salario_atual) for c in colaboradores_ativos if c.salario_atual]
        salario_medio = sum(salarios) / len(salarios) if salarios else 0
    else:
        idade_media = 0
        tempo_empresa_medio = 0
        salario_medio = 0
    
    # Distribuição por tempo de empresa
    distribuicao_tempo_empresa = {
        "0-1 anos": 0,
        "1-3 anos": 0,
        "3-5 anos": 0,
        "5-10 anos": 0,
        "10+ anos": 0
    }
    
    for colaborador in colaboradores_ativos:
        tempo_anos = colaborador.tempo_empresa / 365
        if tempo_anos < 1:
            distribuicao_tempo_empresa["0-1 anos"] += 1
        elif tempo_anos < 3:
            distribuicao_tempo_empresa["1-3 anos"] += 1
        elif tempo_anos < 5:
            distribuicao_tempo_empresa["3-5 anos"] += 1
        elif tempo_anos < 10:
            distribuicao_tempo_empresa["5-10 anos"] += 1
        else:
            distribuicao_tempo_empresa["10+ anos"] += 1
    
    return EstatisticasColaboradores(
        total_colaboradores=total_colaboradores,
        total_ativos=total_ativos,
        total_inativos=total_inativos,
        total_em_ferias=total_em_ferias,
        total_afastados=total_afastados,
        por_departamento=por_departamento,
        por_cargo=por_cargo,
        por_tipo_contrato=por_tipo_contrato,
        idade_media=idade_media,
        tempo_empresa_medio=tempo_empresa_medio / 365,  # Converter para anos
        salario_medio=salario_medio,
        distribuicao_tempo_empresa=distribuicao_tempo_empresa
    )


# =======================================
# ENDPOINTS DE DEPARTAMENTOS
# =======================================

@router.get("/departamentos/", response_model=List[DepartamentoResponse])
async def listar_departamentos(
    ativo: Optional[bool] = Query(None, description="Filtrar por ativo"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Listar departamentos"""
    
    query = db.query(Departamento)
    
    if ativo is not None:
        query = query.filter(Departamento.ativo == ativo)
    
    departamentos = query.order_by(Departamento.nome).all()
    
    # Adicionar total de colaboradores
    for dept in departamentos:
        dept.total_colaboradores = db.query(Colaborador).filter(
            Colaborador.departamento_id == dept.id,
            Colaborador.ativo == True
        ).count()
    
    return departamentos


@router.post("/departamentos/", response_model=DepartamentoResponse, status_code=status.HTTP_201_CREATED)
async def criar_departamento(
    departamento_data: DepartamentoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Criar novo departamento"""
    
    # Verificar se nome já existe
    if db.query(Departamento).filter(Departamento.nome == departamento_data.nome).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Departamento com este nome já existe"
        )
    
    departamento = Departamento(**departamento_data.dict())
    
    try:
        db.add(departamento)
        db.commit()
        db.refresh(departamento)
        return departamento
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar departamento: {str(e)}"
        )


# =======================================
# ENDPOINTS DE CARGOS
# =======================================

@router.get("/cargos/", response_model=List[CargoResponse])
async def listar_cargos(
    ativo: Optional[bool] = Query(None, description="Filtrar por ativo"),
    nivel_hierarquico: Optional[int] = Query(None, ge=1, le=5, description="Filtrar por nível"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Listar cargos"""
    
    query = db.query(Cargo)
    
    if ativo is not None:
        query = query.filter(Cargo.ativo == ativo)
    
    if nivel_hierarquico:
        query = query.filter(Cargo.nivel_hierarquico == nivel_hierarquico)
    
    cargos = query.order_by(Cargo.nivel_hierarquico.desc(), Cargo.nome).all()
    
    # Adicionar total de colaboradores
    for cargo in cargos:
        cargo.total_colaboradores = db.query(Colaborador).filter(
            Colaborador.cargo_id == cargo.id,
            Colaborador.ativo == True
        ).count()
    
    return cargos


@router.post("/cargos/", response_model=CargoResponse, status_code=status.HTTP_201_CREATED)
async def criar_cargo(
    cargo_data: CargoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Criar novo cargo"""
    
    # Verificar se nome já existe
    if db.query(Cargo).filter(Cargo.nome == cargo_data.nome).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cargo com este nome já existe"
        )
    
    cargo = Cargo(**cargo_data.dict())
    
    try:
        db.add(cargo)
        db.commit()
        db.refresh(cargo)
        return cargo
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar cargo: {str(e)}"
        )


# =======================================
# ENDPOINTS DE VALIDAÇÃO
# =======================================

@router.get("/validate/matricula/{matricula}")
async def validar_matricula(
    matricula: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Validar se matrícula está disponível"""
    
    existe = db.query(Colaborador).filter(Colaborador.matricula == matricula.upper()).first()
    
    return {
        "matricula": matricula.upper(),
        "disponivel": not bool(existe),
        "message": "Matrícula disponível" if not existe else "Matrícula já existe"
    }


@router.get("/validate/cpf/{cpf}")
async def validar_cpf_unico(
    cpf: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Validar se CPF está disponível"""
    
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    existe = db.query(Colaborador).filter(Colaborador.cpf == cpf_limpo).first()
    
    return {
        "cpf": cpf_limpo,
        "disponivel": not bool(existe),
        "message": "CPF disponível" if not existe else "CPF já cadastrado"
    }