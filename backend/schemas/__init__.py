#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCHEMAS PYDANTIC - SISTEMA ERP PRIMOTEX
=======================================

Centralização dos schemas de validação para a API.
Importa todos os schemas dos módulos específicos.

Criado em: 29/10/2025
Autor: GitHub Copilot
"""

# Schemas de Ordem de Serviço
from .ordem_servico_schemas import (
    # Enums
    StatusOS,
    PrioridadeOS,
    TipoOS,
    FaseOSEnum,
    StatusFase,

    # Schemas principais
    OrdemServicoBase,
    OrdemServicoCreate,
    OrdemServicoUpdate,
    OrdemServicoResponse,

    # Schemas de fases
    FaseOSBase,
    FaseOSCreate,
    FaseOSUpdate,
    FaseOSResponse,

    # Schemas de visita técnica
    VisitaTecnicaBase,
    VisitaTecnicaCreate,
    VisitaTecnicaUpdate,
    VisitaTecnicaResponse,

    # Schemas de orçamento
    ItemOrcamentoBase,
    OrcamentoBase,
    OrcamentoCreate,
    OrcamentoUpdate,
    OrcamentoResponse,

    # Schemas de listagem
    FiltrosOrdemServico,
    ResumoOrdemServico,
    ListagemOrdemServico,

    # Schemas de ações
    MudancaFaseRequest,
    AtualizacaoStatusRequest,
    HistoricoMudanca,

    # Schemas de relatórios
    EstatisticasOS,
    DashboardOS,
)

# Schemas de Fornecedores
from .fornecedor_schemas import (
    # Enums
    TipoFornecedor,
    StatusFornecedor,
    CategoriaFornecedor,
    PorteEmpresa,

    # Schemas principais
    FornecedorBase,
    FornecedorCreate,
    FornecedorUpdate,
    FornecedorResponse,

    # Schemas de listagem
    FornecedorFilter,
    FornecedorListItem,
    FornecedorListResponse,

    # Schemas especiais
    FornecedorResumo,
    EstatisticasFornecedor
)

# Schemas de Colaboradores
from .colaborador_schemas import (
    # Schemas principais
    ColaboradorBase,
    ColaboradorCreate,
    ColaboradorUpdate,
    ColaboradorResponse,
    ColaboradorDetalhado,
    ColaboradorListagem,

    # Schemas de filtros
    ColaboradorFiltros,
    PaginationParams,

    # Schemas auxiliares
    DepartamentoBase,
    DepartamentoCreate,
    DepartamentoResponse,
    CargoBase,
    CargoCreate,
    CargoResponse,

    # Schemas de estatísticas
    EstatisticasColaboradores
)

__all__ = [
    # Enums
    "StatusOS",
    "PrioridadeOS",
    "TipoOS",
    "FaseOSEnum",
    "StatusFase",

    # Schemas principais
    "OrdemServicoBase",
    "OrdemServicoCreate",
    "OrdemServicoUpdate",
    "OrdemServicoResponse",

    # Schemas de fases
    "FaseOSBase",
    "FaseOSCreate",
    "FaseOSUpdate",
    "FaseOSResponse",

    # Schemas de visita técnica
    "VisitaTecnicaBase",
    "VisitaTecnicaCreate",
    "VisitaTecnicaUpdate",
    "VisitaTecnicaResponse",

    # Schemas de orçamento
    "ItemOrcamentoBase",
    "OrcamentoBase",
    "OrcamentoCreate",
    "OrcamentoUpdate",
    "OrcamentoResponse",

    # Schemas de listagem
    "FiltrosOrdemServico",
    "ResumoOrdemServico",
    "ListagemOrdemServico",

    # Schemas de ações
    "MudancaFaseRequest",
    "AtualizacaoStatusRequest",
    "HistoricoMudanca",

    # Schemas de relatórios
    "EstatisticasOS",
    "DashboardOS",
]