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
from datetime import datetime, date, timedelta
import aiofiles  # Para operações assíncronas de arquivo
import base64
from pathlib import Path

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
    # Documento schemas ⭐ (TAREFA 5)
    ColaboradorDocumentoCreate, ColaboradorDocumentoResponse,
    ColaboradorDocumentoListagem,
    # Schemas auxiliares
    EstatisticasColaboradores, PaginationParams
)
from backend.auth.dependencies import get_current_user

# Criar router
router = APIRouter(prefix="/colaboradores", tags=["colaboradores"])

# Constantes
COLABORADOR_NAO_ENCONTRADO = "Colaborador não encontrado"
FORMATO_DATA_BR = "%d/%m/%Y"


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
                query = query.filter(
                    Colaborador.superior_direto_id.isnot(None)
                )
            else:
                query = query.filter(
                    Colaborador.superior_direto_id.is_(None)
                )

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
    colaborador_existente = db.query(Colaborador).filter(
        Colaborador.matricula == colaborador_data.matricula
    ).first()
    if colaborador_existente:
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
    usuario_existente = db.query(Colaborador).filter(
        Colaborador.user_id == colaborador_data.user_id
    ).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já vinculado a outro colaborador"
        )

    # Verificar se cargo existe
    cargo = db.query(Cargo).filter(
        Cargo.id == colaborador_data.cargo_id
    ).first()
    if not cargo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cargo não encontrado"
        )

    # Verificar se departamento existe
    departamento = db.query(Departamento).filter(
        Departamento.id == colaborador_data.departamento_id
    ).first()
    if not departamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Departamento não encontrado"
        )

    # Criar colaborador
    colaborador_dict = colaborador_data.dict()
    colaborador_dict['cp'] = cpf_limpo
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
            detail=COLABORADOR_NAO_ENCONTRADO
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

    colaborador = db.query(Colaborador).filter(
        Colaborador.id == colaborador_id
    ).first()

    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLABORADOR_NAO_ENCONTRADO
        )

    # Atualizar apenas campos fornecidos
    update_data = colaborador_data.dict(exclude_unset=True)

    # Verificar mudança de cargo/departamento
    if ('cargo_id' in update_data and
            update_data['cargo_id'] != colaborador.cargo_id):
        cargo = db.query(Cargo).filter(
            Cargo.id == update_data['cargo_id']
        ).first()
        if not cargo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cargo não encontrado"
            )

    if ('departamento_id' in update_data and
            update_data['departamento_id'] != colaborador.departamento_id):
        departamento = db.query(Departamento).filter(
            Departamento.id == update_data['departamento_id']
        ).first()
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

    colaborador = db.query(Colaborador).filter(
        Colaborador.id == colaborador_id
    ).first()

    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLABORADOR_NAO_ENCONTRADO
        )

    status_anterior = colaborador.status
    colaborador.status = novo_status
    colaborador.data_atualizacao = datetime.now()

    # Adicionar observação sobre mudança de status
    if motivo:
        observacao_atual = colaborador.observacoes or ""
        nova_observacao = (
            f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M')}] "
            f"Status alterado de {status_anterior.value} para "
            f"{novo_status.value}. Motivo: {motivo}"
        )
        colaborador.observacoes = observacao_atual + nova_observacao

    try:
        db.commit()
        return {
            "message": f"Status alterado para {novo_status.value}",
            "status_anterior": status_anterior.value
        }

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

    colaborador = db.query(Colaborador).filter(
        Colaborador.id == colaborador_id
    ).first()

    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLABORADOR_NAO_ENCONTRADO
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
        nova_observacao = (
            f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M')}] "
            f"Colaborador inativado. Motivo: {motivo}"
        )
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
            detail=COLABORADOR_NAO_ENCONTRADO
        )

    return colaborador


# ============================================================================
# FUNÇÕES AUXILIARES PARA ESTATÍSTICAS (reduzir Cognitive Complexity)
# ============================================================================

def _calcular_contadores_gerais(db: Session) -> dict:
    """Calcula contadores gerais de colaboradores"""
    return {
        'total': db.query(Colaborador).count(),
        'ativos': db.query(Colaborador).filter(
            Colaborador.ativo.is_(True)
        ).count(),
        'inativos': db.query(Colaborador).filter(
            Colaborador.ativo.is_(False)
        ).count(),
        'ferias': db.query(Colaborador).filter(
            Colaborador.status == StatusColaborador.FERIAS
        ).count(),
        'afastados': db.query(Colaborador).filter(
            Colaborador.status == StatusColaborador.AFASTADO
        ).count()
    }


def _calcular_por_departamento(db: Session) -> dict:
    """Calcula estatísticas por departamento"""
    stats = db.query(
        Departamento.nome,
        func.count(Colaborador.id).label('total')
    ).join(
        Colaborador,
        Colaborador.departamento_id == Departamento.id
    ).group_by(Departamento.nome).all()
    
    return {dept: total for dept, total in stats}


def _calcular_por_cargo(db: Session) -> dict:
    """Calcula estatísticas por cargo"""
    stats = db.query(
        Cargo.nome,
        func.count(Colaborador.id).label('total')
    ).join(Colaborador).group_by(Cargo.nome).all()
    
    return {cargo: total for cargo, total in stats}


def _calcular_por_tipo_contrato(db: Session) -> dict:
    """Calcula estatísticas por tipo de contrato"""
    stats = db.query(
        Colaborador.tipo_contrato,
        func.count(Colaborador.id).label('total')
    ).group_by(Colaborador.tipo_contrato).all()
    
    return {contrato.value if contrato else 'Não informado': total
            for contrato, total in stats}


def _calcular_metricas_colaboradores(db: Session) -> dict:
    """Calcula métricas de idade, tempo empresa e salário"""
    colaboradores_ativos = (
        db.query(Colaborador)
        .filter(Colaborador.ativo.is_(True))
        .all()
    )
    
    # Idade
    idades = [
        c.idade for c in colaboradores_ativos
        if c.idade and c.idade > 0
    ]
    idade_media = sum(idades) / len(idades) if idades else 0
    
    # Tempo de empresa
    tempos_empresa = [
        c.tempo_empresa for c in colaboradores_ativos
        if c.tempo_empresa and c.tempo_empresa > 0
    ]
    tempo_empresa_medio = (
        sum(tempos_empresa) / len(tempos_empresa)
        if tempos_empresa else 0
    )
    
    # Salário
    salarios = [
        float(c.salario_atual)
        for c in colaboradores_ativos
        if (c.salario_atual is not None and
            c.salario_atual > 0)
    ]
    salario_medio = (
        sum(salarios) / len(salarios)
        if salarios else 0
    )
    
    return {
        'idade_media': idade_media,
        'tempo_empresa_medio': tempo_empresa_medio / 365,  # Em anos
        'salario_medio': salario_medio
    }


@router.get("/stats/resumo", response_model=EstatisticasColaboradores)
async def estatisticas_colaboradores(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Obter estatísticas gerais dos colaboradores"""

    try:
        # Usar funções auxiliares para reduzir complexidade
        contadores = _calcular_contadores_gerais(db)
        por_departamento = _calcular_por_departamento(db)
        por_cargo = _calcular_por_cargo(db)
        por_tipo_contrato = _calcular_por_tipo_contrato(db)
        metricas = _calcular_metricas_colaboradores(db)

        return EstatisticasColaboradores(
            total_colaboradores=contadores['total'],
            total_ativos=contadores['ativos'],
            total_inativos=contadores['inativos'],
            total_em_ferias=contadores['ferias'],
            total_afastados=contadores['afastados'],
            por_departamento=por_departamento,
            por_cargo=por_cargo,
            por_tipo_contrato=por_tipo_contrato,
            idade_media=metricas['idade_media'],
            tempo_empresa_medio=metricas['tempo_empresa_medio'],
            salario_medio=metricas['salario_medio']
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar estatísticas: {str(e)}"
        )

    except Exception as e:
        print(f"ERRO NO ENDPOINT DE ESTATÍSTICAS: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular estatísticas: {str(e)}"
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
        "cp": cpf_limpo,
        "disponivel": not bool(existe),
        "message": "CPF disponível" if not existe else "CPF já cadastrado"
    }


# =======================================
# ENDPOINTS DE DOCUMENTOS ⭐ (TAREFA 5)
# =======================================

@router.post("/{colaborador_id}/documentos",
             response_model=ColaboradorDocumentoResponse,
             status_code=status.HTTP_201_CREATED)
async def upload_documento_colaborador(
    colaborador_id: int,
    documento_data: ColaboradorDocumentoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Upload de documento para colaborador

    **Sistema de Alertas (4 cores):**
    - 🟢 Verde: > 30 dias para vencer
    - 🟡 Amarelo: 15-30 dias para vencer
    - 🟠 Laranja: 1-14 dias para vencer
    - 🔴 Vermelho: VENCIDO
    """
    from backend.models.colaborador_model import ColaboradorDocumento
    import base64
    import os
    from pathlib import Path

    # Verificar se colaborador existe
    colaborador = db.query(Colaborador).filter(
        Colaborador.id == colaborador_id
    ).first()

    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLABORADOR_NAO_ENCONTRADO
        )

    # Decodificar arquivo Base64
    try:
        arquivo_bytes = base64.b64decode(documento_data.arquivo_base64)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo Base64 inválido: {str(e)}"
        )

    # Criar diretório se não existir
    upload_dir = Path("uploads") / "colaboradores" / str(colaborador_id) / "documentos"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Gerar nome único para arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo_limpo = documento_data.nome_arquivo.replace(" ", "_")
    arquivo_path = upload_dir / f"{timestamp}_{nome_arquivo_limpo}"

    # Salvar arquivo de forma assíncrona
    try:
        async with aiofiles.open(arquivo_path, "wb") as f:
            await f.write(arquivo_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )

    # Criar registro no banco
    documento_dict = documento_data.dict(exclude={'arquivo_base64'})
    documento_dict['colaborador_id'] = colaborador_id
    documento_dict['arquivo_path'] = str(arquivo_path)
    documento_dict['uploadado_por'] = current_user.id

    documento = ColaboradorDocumento(**documento_dict)

    try:
        db.add(documento)
        db.commit()
        db.refresh(documento)

        # Calcular dias para vencer e status
        if documento.data_validade:
            dias_restantes = (documento.data_validade - date.today()).days
            documento.dias_para_vencer = dias_restantes

            # Calcular status de cor
            if dias_restantes < 0:
                documento.status_validade = "vermelho"
                documento.cor_alerta = "#FF0000"
            elif dias_restantes <= 14:
                documento.status_validade = "laranja"
                documento.cor_alerta = "#FF8C00"
            elif dias_restantes <= 30:
                documento.status_validade = "amarelo"
                documento.cor_alerta = "#FFD700"
            else:
                documento.status_validade = "verde"
                documento.cor_alerta = "#00FF00"

        return documento

    except Exception as e:
        db.rollback()
        # Remover arquivo se falhou salvar no banco
        if arquivo_path.exists():
            arquivo_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar documento: {str(e)}"
        )


@router.get("/{colaborador_id}/documentos",
            response_model=ColaboradorDocumentoListagem)
async def listar_documentos_colaborador(
    colaborador_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Listar todos os documentos de um colaborador com alertas de validade"""
    from backend.models.colaborador_model import ColaboradorDocumento

    # Verificar se colaborador existe
    colaborador = db.query(Colaborador).filter(
        Colaborador.id == colaborador_id
    ).first()

    if not colaborador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COLABORADOR_NAO_ENCONTRADO
        )

    # Buscar documentos
    documentos = db.query(ColaboradorDocumento).filter(
        ColaboradorDocumento.colaborador_id == colaborador_id
    ).order_by(ColaboradorDocumento.data_upload.desc()).all()

    # Calcular estatísticas e status de cada documento
    total_vencidos = 0
    total_vencendo = 0
    total_ok = 0

    for doc in documentos:
        if doc.data_validade:
            dias_restantes = (doc.data_validade - date.today()).days
            doc.dias_para_vencer = dias_restantes

            # Calcular status de cor
            if dias_restantes < 0:
                doc.status_validade = "vermelho"
                doc.cor_alerta = "#FF0000"
                total_vencidos += 1
            elif dias_restantes <= 14:
                doc.status_validade = "laranja"
                doc.cor_alerta = "#FF8C00"
                total_vencendo += 1
            elif dias_restantes <= 30:
                doc.status_validade = "amarelo"
                doc.cor_alerta = "#FFD700"
                total_vencendo += 1
            else:
                doc.status_validade = "verde"
                doc.cor_alerta = "#00FF00"
                total_ok += 1
        else:
            doc.status_validade = "neutro"
            doc.cor_alerta = "#808080"  # Cinza - sem validade

    return ColaboradorDocumentoListagem(
        items=documentos,
        total=len(documentos),
        total_vencidos=total_vencidos,
        total_vencendo=total_vencendo,
        total_ok=total_ok
    )


@router.get("/{colaborador_id}/documentos/{documento_id}/download")
async def download_documento(
    colaborador_id: int,
    documento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Download de documento específico"""
    from backend.models.colaborador_model import ColaboradorDocumento
    from fastapi.responses import FileResponse
    import os

    # Buscar documento
    documento = db.query(ColaboradorDocumento).filter(
        ColaboradorDocumento.id == documento_id,
        ColaboradorDocumento.colaborador_id == colaborador_id
    ).first()

    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado"
        )

    # Verificar se arquivo existe
    if not documento.arquivo_path or not os.path.exists(documento.arquivo_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado no servidor"
        )

    return FileResponse(
        path=documento.arquivo_path,
        filename=documento.nome_arquivo,
        media_type='application/octet-stream'
    )


@router.delete("/{colaborador_id}/documentos/{documento_id}")
async def excluir_documento(
    colaborador_id: int,
    documento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Excluir documento de colaborador"""
    from backend.models.colaborador_model import ColaboradorDocumento
    import os
    from pathlib import Path

    # Buscar documento
    documento = db.query(ColaboradorDocumento).filter(
        ColaboradorDocumento.id == documento_id,
        ColaboradorDocumento.colaborador_id == colaborador_id
    ).first()

    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado"
        )

    # Remover arquivo físico
    if documento.arquivo_path and os.path.exists(documento.arquivo_path):
        try:
            Path(documento.arquivo_path).unlink()
        except Exception as e:
            print(f"Erro ao remover arquivo: {e}")
            # Continua excluindo registro do banco mesmo se falhar remover arquivo

    # Remover do banco
    try:
        db.delete(documento)
        db.commit()
        return {"message": "Documento excluído com sucesso"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir documento: {str(e)}"
        )


@router.get("/alertas/documentos-vencidos")
async def listar_alertas_documentos_vencidos(
    dias_alerta: int = Query(default=30, ge=1, le=90, description="Dias antes do vencimento para alertar"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Listar todos os documentos vencidos ou próximos do vencimento

    **Retorna:**
    - Documentos VENCIDOS (vermelho)
    - Documentos vencendo em até X dias (amarelo/laranja)

    **Parâmetros:**
    - dias_alerta: Quantos dias antes do vencimento mostrar alerta (padrão: 30)
    """
    try:
        from backend.models.colaborador_model import ColaboradorDocumento
        from sqlalchemy import and_
        from sqlalchemy.orm import joinedload

        # Data limite (hoje + X dias)
        data_limite = date.today() + timedelta(days=dias_alerta)

        # Buscar documentos com validade <= data_limite
        documentos_alerta = db.query(ColaboradorDocumento).options(
            joinedload(ColaboradorDocumento.colaborador)
        ).filter(
            and_(
                ColaboradorDocumento.data_validade.isnot(None),
                ColaboradorDocumento.data_validade <= data_limite
            )
        ).order_by(
            ColaboradorDocumento.data_validade.asc()
        ).all()

        # Classificar por cor
        alertas = {
            "vermelho": [],  # Vencidos
            "laranja": [],   # 1-14 dias
            "amarelo": [],   # 15-30 dias
            "total": 0
        }

        for doc in documentos_alerta:
            dias_restantes = (doc.data_validade - date.today()).days

            # Get colaborador name safely
            colaborador_nome = "Colaborador removido"
            if doc.colaborador:
                colaborador_nome = doc.colaborador.nome_completo

            if dias_restantes < 0:
                alertas["vermelho"].append({
                    "documento_id": doc.id,
                    "colaborador_id": doc.colaborador_id,
                    "colaborador_nome": colaborador_nome,
                    "tipo_documento": doc.tipo_documento.value if doc.tipo_documento else "N/A",
                    "nome_arquivo": doc.nome_arquivo,
                    "data_validade": doc.data_validade.strftime(FORMATO_DATA_BR),
                    "dias_atraso": abs(dias_restantes),
                    "urgencia": "VENCIDO"
                })
            elif dias_restantes <= 14:
                alertas["laranja"].append({
                    "documento_id": doc.id,
                    "colaborador_id": doc.colaborador_id,
                    "colaborador_nome": colaborador_nome,
                    "tipo_documento": doc.tipo_documento.value if doc.tipo_documento else "N/A",
                    "nome_arquivo": doc.nome_arquivo,
                    "data_validade": doc.data_validade.strftime(FORMATO_DATA_BR),
                    "dias_restantes": dias_restantes,
                    "urgencia": "URGENTE"
                })
            else:  # dias_restantes <= dias_alerta
                alertas["amarelo"].append({
                    "documento_id": doc.id,
                    "colaborador_id": doc.colaborador_id,
                    "colaborador_nome": colaborador_nome,
                    "tipo_documento": doc.tipo_documento.value if doc.tipo_documento else "N/A",
                    "nome_arquivo": doc.nome_arquivo,
                    "data_validade": doc.data_validade.strftime(FORMATO_DATA_BR),
                    "dias_restantes": dias_restantes,
                    "urgencia": "ATENCAO"
                })

        alertas["total"] = len(alertas["vermelho"]) + len(alertas["laranja"]) + len(alertas["amarelo"])

        return alertas

    except Exception as e:
        print(f"ERRO NO ENDPOINT DE ALERTAS: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar alertas: {str(e)}"
        )


# =======================================
# MODELOS DE TESTE (APENAS DESENVOLVIMENTO)
# =======================================

    return alertas
