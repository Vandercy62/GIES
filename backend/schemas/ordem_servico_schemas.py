#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCHEMAS PYDANTIC - ORDEM DE SERVIÇO
===================================

Schemas de validação para os endpoints da API de Ordem de Serviço.
Inclui validações de entrada, saída e estruturas de dados.

Criado em: 29/10/2025
Autor: GitHub Copilot
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, validator, root_validator
from pydantic import EmailStr


# Constantes para reutilização
ID_OS_DESCRIPTION = "ID da OS"


# Enums para validação
class StatusOS(str, Enum):
    """Status possíveis de uma OS"""
    ORCAMENTO = "Orçamento"
    APROVADA = "Aprovada"
    EM_EXECUCAO = "Em Execução"
    CONCLUIDA = "Concluída"
    CANCELADA = "Cancelada"
    REAGENDADA = "Reagendada"
    PAUSADA = "Pausada"


class PrioridadeOS(str, Enum):
    """Prioridades da OS"""
    BAIXA = "Baixa"
    NORMAL = "Normal"
    ALTA = "Alta"
    URGENTE = "Urgente"


class TipoOS(str, Enum):
    """Tipos de Ordem de Serviço"""
    INSTALACAO = "Instalação"
    MANUTENCAO = "Manutenção"
    REPARO = "Reparo"
    ORCAMENTO = "Orçamento"
    GARANTIA = "Garantia"
    EMERGENCIA = "Emergência"


class FaseOSEnum(str, Enum):
    """Fases do workflow da OS"""
    CRIACAO = "1-Criação"
    VISITA_TECNICA = "2-Visita Técnica"
    ORCAMENTO = "3-Orçamento"
    APROVACAO = "4-Aprovação"
    EXECUCAO = "5-Execução"
    ENTREGA = "6-Entrega"
    FINALIZACAO = "7-Finalização"


class StatusFase(str, Enum):
    """Status de cada fase"""
    PENDENTE = "Pendente"
    EM_ANDAMENTO = "Em Andamento"
    CONCLUIDA = "Concluída"
    PAUSADA = "Pausada"
    CANCELADA = "Cancelada"


# ================================
# SCHEMAS BASE
# ================================

class OrdemServicoBase(BaseModel):
    """Schema base para Ordem de Serviço"""
    numero_os: str = Field(..., min_length=1, max_length=20, description="Número único da OS")
    cliente_id: int = Field(..., gt=0, description="ID do cliente")
    titulo: str = Field(..., min_length=3, max_length=200, description="Título da OS")
    descricao: str = Field(..., min_length=10, description="Descrição detalhada")
    
    tipo_servico: TipoOS = Field(..., description="Tipo do serviço")
    prioridade: PrioridadeOS = Field(PrioridadeOS.NORMAL, description="Prioridade da OS")
    
    # Endereço do serviço
    endereco_servico: str = Field(..., min_length=10, max_length=500, description="Endereço onde será executado")
    cep_servico: str = Field(..., pattern=r"^\d{5}-?\d{3}$", description="CEP do local")
    cidade_servico: str = Field(..., min_length=2, max_length=100, description="Cidade")
    estado_servico: str = Field(..., min_length=2, max_length=2, description="Estado (UF)")
    
    # Datas importantes
    data_solicitacao: datetime = Field(default_factory=datetime.now, description="Data da solicitação")
    data_prazo: Optional[datetime] = Field(None, description="Prazo para execução")
    
    # Valores (opcionais na criação)
    valor_estimado: Optional[Decimal] = Field(None, ge=0, description="Valor estimado inicial")
    valor_final: Optional[Decimal] = Field(None, ge=0, description="Valor final aprovado")
    
    # Configurações
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações gerais")
    requer_orcamento: bool = Field(True, description="Se requer orçamento formal")
    urgente: bool = Field(False, description="Se é urgente")
    
    @validator('cep_servico')
    @classmethod
    def validar_cep(cls, v):
        """Remove formatação do CEP"""
        if v:
            return v.replace('-', '').replace(' ', '')
        return v
    
    @validator('data_prazo')
    @classmethod
    def validar_prazo(cls, v, values):
        """Valida se o prazo é posterior à solicitação"""
        if v and 'data_solicitacao' in values and v < values['data_solicitacao']:
            raise ValueError('Data do prazo deve ser posterior à solicitação')
        return v


class OrdemServicoCreate(OrdemServicoBase):
    """Schema para criação de OS"""
    # Campos obrigatórios adicionais na criação
    usuario_criacao: str = Field(..., min_length=3, max_length=100, description="Usuário que criou")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "numero_os": "OS-2025-001",
                "cliente_id": 1,
                "titulo": "Instalação de forro PVC - Sala comercial",
                "descricao": "Instalação de forro PVC em sala comercial de 50m², incluindo estrutura metálica e luminárias",
                "tipo_servico": "Instalação",
                "prioridade": "Normal",
                "endereco_servico": "Rua das Flores, 123, Centro",
                "cep_servico": "12345-678",
                "cidade_servico": "São Paulo",
                "estado_servico": "SP",
                "data_prazo": "2025-11-15T14:00:00",
                "valor_estimado": 2500.00,
                "requer_orcamento": True,
                "usuario_criacao": "admin"
            }
        }


class OrdemServicoUpdate(BaseModel):
    """Schema para atualização de OS"""
    titulo: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = Field(None, min_length=10)
    tipo_servico: Optional[TipoOS] = None
    prioridade: Optional[PrioridadeOS] = None
    
    endereco_servico: Optional[str] = Field(None, min_length=10, max_length=500)
    cep_servico: Optional[str] = Field(None, pattern=r"^\d{5}-?\d{3}$")
    cidade_servico: Optional[str] = Field(None, min_length=2, max_length=100)
    estado_servico: Optional[str] = Field(None, min_length=2, max_length=2)
    
    data_prazo: Optional[datetime] = None
    valor_estimado: Optional[Decimal] = Field(None, ge=0)
    valor_final: Optional[Decimal] = Field(None, ge=0)
    
    observacoes: Optional[str] = Field(None, max_length=1000)
    urgente: Optional[bool] = None
    
    # Campos de controle
    usuario_ultima_alteracao: str = Field(..., min_length=3, max_length=100)


class OrdemServicoResponse(OrdemServicoBase):
    """Schema de resposta da OS"""
    id: int
    status: StatusOS
    fase_atual: FaseOSEnum
    progresso_percentual: float = Field(..., ge=0, le=100)
    
    # Dados de controle
    usuario_criacao: str
    usuario_ultima_alteracao: Optional[str] = None
    usuario_responsavel: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relacionamentos (resumidos)
    cliente_nome: Optional[str] = None
    total_fases: int = 7
    fases_concluidas: int = 0
    
    class Config:
        from_attributes = True


# ================================
# SCHEMAS PARA FASES
# ================================

class FaseOSBase(BaseModel):
    """Schema base para Fases da OS"""
    numero_fase: int = Field(..., ge=1, le=7, description="Número da fase (1-7)")
    nome_fase: FaseOSEnum = Field(..., description="Nome da fase")
    descricao: str = Field(..., min_length=10, description="Descrição da fase")
    
    # Configurações da fase
    obrigatoria: bool = Field(True, description="Se a fase é obrigatória")
    requer_aprovacao: bool = Field(False, description="Se requer aprovação")
    
    # Datas e prazos
    data_inicio_prevista: Optional[datetime] = None
    data_fim_prevista: Optional[datetime] = None
    prazo_execucao_dias: Optional[int] = Field(None, ge=1, description="Prazo em dias")
    
    # Responsabilidades
    responsavel_fase: Optional[str] = Field(None, max_length=100)
    
    # Observações
    instrucoes: Optional[str] = Field(None, max_length=1000, description="Instruções específicas")
    observacoes: Optional[str] = Field(None, max_length=1000)


class FaseOSCreate(FaseOSBase):
    """Schema para criação de Fase"""
    ordem_servico_id: int = Field(..., gt=0, description=ID_OS_DESCRIPTION)
    usuario_criacao: str = Field(..., min_length=3, max_length=100)


class FaseOSUpdate(BaseModel):
    """Schema para atualização de Fase"""
    descricao: Optional[str] = Field(None, min_length=10)
    status: Optional[StatusFase] = None
    progresso_percentual: Optional[float] = Field(None, ge=0, le=100)
    
    data_inicio_real: Optional[datetime] = None
    data_fim_real: Optional[datetime] = None
    responsavel_fase: Optional[str] = Field(None, max_length=100)
    
    resultado: Optional[str] = Field(None, max_length=1000, description="Resultado da fase")
    observacoes: Optional[str] = Field(None, max_length=1000)
    
    usuario_alteracao: str = Field(..., min_length=3, max_length=100)


class FaseOSResponse(FaseOSBase):
    """Schema de resposta da Fase"""
    id: int
    ordem_servico_id: int
    status: StatusFase
    progresso_percentual: float
    
    # Datas reais
    data_inicio_real: Optional[datetime] = None
    data_fim_real: Optional[datetime] = None
    
    # Resultados
    resultado: Optional[str] = None
    anexos: Optional[List[str]] = []
    
    # Controle
    usuario_criacao: str
    usuario_ultima_alteracao: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ================================
# SCHEMAS PARA VISITA TÉCNICA
# ================================

class VisitaTecnicaBase(BaseModel):
    """Schema base para Visita Técnica (Fase 2)"""
    data_agendada: datetime = Field(..., description="Data agendada para visita")
    tecnico_responsavel: str = Field(..., min_length=3, max_length=100, description="Técnico responsável")
    
    # Contato para agendamento
    contato_cliente: str = Field(..., min_length=3, max_length=100, description="Pessoa de contato")
    telefone_contato: str = Field(..., pattern=r"^\(\d{2}\)\s\d{4,5}-\d{4}$", description="Telefone para contato")
    
    # Objetivo da visita
    objetivo: str = Field(..., min_length=10, description="Objetivo da visita técnica")
    checklist_verificacao: Dict[str, Any] = Field(default_factory=dict, description="Checklist de verificação")
    
    # Observações
    observacoes_agendamento: Optional[str] = Field(None, max_length=500)


class VisitaTecnicaCreate(VisitaTecnicaBase):
    """Schema para agendamento de Visita Técnica"""
    ordem_servico_id: int = Field(..., gt=0, description=ID_OS_DESCRIPTION)
    usuario_agendamento: str = Field(..., min_length=3, max_length=100)
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "ordem_servico_id": 1,
                "data_agendada": "2025-11-01T14:00:00",
                "tecnico_responsavel": "João Silva",
                "contato_cliente": "Maria Santos",
                "telefone_contato": "(11) 99999-9999",
                "objetivo": "Medição do ambiente e verificação de viabilidade técnica",
                "checklist_verificacao": {
                    "medicoes": False,
                    "fotos": False,
                    "viabilidade": False,
                    "orcamento": False
                },
                "usuario_agendamento": "admin"
            }
        }


class VisitaTecnicaUpdate(BaseModel):
    """Schema para atualização da Visita Técnica"""
    data_agendada: Optional[datetime] = None
    tecnico_responsavel: Optional[str] = Field(None, min_length=3, max_length=100)
    contato_cliente: Optional[str] = Field(None, min_length=3, max_length=100)
    telefone_contato: Optional[str] = Field(None, pattern=r"^\(\d{2}\)\s\d{4,5}-\d{4}$")
    
    # Dados da execução
    data_execucao: Optional[datetime] = None
    status_execucao: Optional[str] = Field(None, max_length=50)
    tempo_duracao: Optional[int] = Field(None, ge=1, description="Duração em minutos")
    
    # Resultados
    medicoes_realizadas: Optional[Dict[str, Any]] = None
    fotos_anexadas: Optional[List[str]] = None
    observacoes_tecnicas: Optional[str] = Field(None, max_length=1000)
    viabilidade_tecnica: Optional[bool] = None
    proximos_passos: Optional[str] = Field(None, max_length=500)
    
    # Checklist atualizado
    checklist_verificacao: Optional[Dict[str, Any]] = None
    
    usuario_alteracao: str = Field(..., min_length=3, max_length=100)


class VisitaTecnicaResponse(VisitaTecnicaBase):
    """Schema de resposta da Visita Técnica"""
    id: int
    ordem_servico_id: int
    
    # Status da visita
    status_execucao: str = "Agendada"
    data_execucao: Optional[datetime] = None
    tempo_duracao: Optional[int] = None
    
    # Resultados
    medicoes_realizadas: Dict[str, Any] = Field(default_factory=dict)
    fotos_anexadas: List[str] = Field(default_factory=list)
    observacoes_tecnicas: Optional[str] = None
    viabilidade_tecnica: Optional[bool] = None
    proximos_passos: Optional[str] = None
    
    # Controle
    usuario_agendamento: str
    usuario_ultima_alteracao: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ================================
# SCHEMAS PARA ORÇAMENTO
# ================================

class ItemOrcamentoBase(BaseModel):
    """Item individual do orçamento"""
    produto_servico: str = Field(..., min_length=3, max_length=200, description="Descrição do item")
    quantidade: Decimal = Field(..., gt=0, description="Quantidade")
    unidade: str = Field(..., min_length=1, max_length=10, description="Unidade (m², un, ml, etc.)")
    valor_unitario: Decimal = Field(..., gt=0, description="Valor unitário")
    valor_total: Decimal = Field(..., ge=0, description="Valor total do item")
    
    categoria: Optional[str] = Field(None, max_length=50, description="Categoria do item")
    observacoes_item: Optional[str] = Field(None, max_length=200)
    
    @root_validator(pre=True)
    @classmethod
    def validar_valor_total(cls, values):
        """Valida se o valor total está correto"""
        if not isinstance(values, dict):
            return values
            
        quantidade = values.get('quantidade')
        valor_unitario = values.get('valor_unitario')
        valor_total = values.get('valor_total')
        
        if all([quantidade, valor_unitario, valor_total]):
            calculado = quantidade * valor_unitario
            if abs(float(calculado) - float(valor_total)) > 0.01:  # Tolerância para arredondamento
                raise ValueError('Valor total não confere com quantidade x valor unitário')
        
        return values


class OrcamentoBase(BaseModel):
    """Schema base para Orçamento (Fase 3)"""
    numero_orcamento: str = Field(..., min_length=1, max_length=20, description="Número do orçamento")
    data_elaboracao: datetime = Field(default_factory=datetime.now, description="Data de elaboração")
    data_validade: datetime = Field(..., description="Data de validade")
    
    # Responsável
    elaborado_por: str = Field(..., min_length=3, max_length=100, description="Elaborado por")
    
    # Itens do orçamento
    itens: List[ItemOrcamentoBase] = Field(..., min_items=1, description="Itens do orçamento")
    
    # Valores totais
    subtotal: Decimal = Field(..., ge=0, description="Subtotal dos itens")
    desconto_percentual: Decimal = Field(0, ge=0, le=100, description="Desconto em %")
    desconto_valor: Decimal = Field(0, ge=0, description="Valor do desconto")
    valor_total: Decimal = Field(..., gt=0, description="Valor total do orçamento")
    
    # Condições
    forma_pagamento: str = Field(..., min_length=3, max_length=100, description="Forma de pagamento")
    prazo_execucao: str = Field(..., min_length=3, max_length=100, description="Prazo de execução")
    garantia: str = Field(..., min_length=3, max_length=100, description="Garantia oferecida")
    
    # Observações
    observacoes_gerais: Optional[str] = Field(None, max_length=1000)
    termos_condicoes: Optional[str] = Field(None, max_length=2000)
    
    @validator('data_validade')
    @classmethod
    def validar_validade(cls, v, values):
        """Valida se a data de validade é futura"""
        if v and 'data_elaboracao' in values and v <= values['data_elaboracao']:
            raise ValueError('Data de validade deve ser posterior à elaboração')
        return v
    
    @root_validator(pre=True)
    @classmethod
    def validar_valores(cls, values):
        """Valida os valores do orçamento"""
        if not isinstance(values, dict):
            return values
            
        subtotal = values.get('subtotal')
        desconto_valor = values.get('desconto_valor', 0)
        valor_total = values.get('valor_total')
        
        if all([subtotal, valor_total]):
            calculado = subtotal - desconto_valor
            if abs(float(calculado) - float(valor_total)) > 0.01:
                raise ValueError('Valor total não confere com subtotal - desconto')
        
        return values


class OrcamentoCreate(OrcamentoBase):
    """Schema para criação de Orçamento"""
    ordem_servico_id: int = Field(..., gt=0, description=ID_OS_DESCRIPTION)
    usuario_criacao: str = Field(..., min_length=3, max_length=100)
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "ordem_servico_id": 1,
                "numero_orcamento": "ORC-2025-001",
                "data_validade": "2025-12-01T23:59:59",
                "elaborado_por": "João Silva",
                "itens": [
                    {
                        "produto_servico": "Forro PVC branco 200mm",
                        "quantidade": 50,
                        "unidade": "m²",
                        "valor_unitario": 35.00,
                        "valor_total": 1750.00,
                        "categoria": "Material"
                    },
                    {
                        "produto_servico": "Mão de obra instalação",
                        "quantidade": 50,
                        "unidade": "m²",
                        "valor_unitario": 15.00,
                        "valor_total": 750.00,
                        "categoria": "Serviço"
                    }
                ],
                "subtotal": 2500.00,
                "desconto_percentual": 5,
                "desconto_valor": 125.00,
                "valor_total": 2375.00,
                "forma_pagamento": "50% entrada + 50% na entrega",
                "prazo_execucao": "10 dias úteis",
                "garantia": "12 meses contra defeitos",
                "usuario_criacao": "admin"
            }
        }


class OrcamentoUpdate(BaseModel):
    """Schema para atualização de Orçamento"""
    data_validade: Optional[datetime] = None
    itens: Optional[List[ItemOrcamentoBase]] = None
    
    subtotal: Optional[Decimal] = Field(None, ge=0)
    desconto_percentual: Optional[Decimal] = Field(None, ge=0, le=100)
    desconto_valor: Optional[Decimal] = Field(None, ge=0)
    valor_total: Optional[Decimal] = Field(None, gt=0)
    
    forma_pagamento: Optional[str] = Field(None, min_length=3, max_length=100)
    prazo_execucao: Optional[str] = Field(None, min_length=3, max_length=100)
    garantia: Optional[str] = Field(None, min_length=3, max_length=100)
    
    observacoes_gerais: Optional[str] = Field(None, max_length=1000)
    termos_condicoes: Optional[str] = Field(None, max_length=2000)
    
    # Status do orçamento
    status_orcamento: Optional[str] = Field(None, max_length=50)
    data_aprovacao: Optional[datetime] = None
    aprovado_por: Optional[str] = Field(None, max_length=100)
    
    usuario_alteracao: str = Field(..., min_length=3, max_length=100)


class OrcamentoResponse(OrcamentoBase):
    """Schema de resposta do Orçamento"""
    id: int
    ordem_servico_id: int
    
    # Status
    status_orcamento: str = "Elaborado"
    data_aprovacao: Optional[datetime] = None
    aprovado_por: Optional[str] = None
    
    # Controle
    usuario_criacao: str
    usuario_ultima_alteracao: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ================================
# SCHEMAS PARA LISTAGEM E FILTROS
# ================================

class FiltrosOrdemServico(BaseModel):
    """Filtros para listagem de OS"""
    cliente_id: Optional[int] = None
    status: Optional[StatusOS] = None
    tipo_servico: Optional[TipoOS] = None
    prioridade: Optional[PrioridadeOS] = None
    fase_atual: Optional[FaseOSEnum] = None
    urgente: Optional[bool] = None
    
    # Filtros de data
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    
    # Filtros de texto
    numero_os: Optional[str] = None
    titulo: Optional[str] = None
    responsavel: Optional[str] = None
    
    # Paginação
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=100)
    
    # Ordenação
    order_by: str = Field("created_at", description="Campo para ordenação")
    order_desc: bool = Field(True, description="Ordem decrescente")


class ResumoOrdemServico(BaseModel):
    """Resumo da OS para listagens"""
    id: int
    numero_os: str
    titulo: str
    cliente_nome: str
    status: StatusOS
    fase_atual: FaseOSEnum
    prioridade: PrioridadeOS
    tipo_servico: TipoOS
    progresso_percentual: float
    data_solicitacao: datetime
    data_prazo: Optional[datetime] = None
    valor_final: Optional[Decimal] = None
    urgente: bool
    
    class Config:
        from_attributes = True


class ListagemOrdemServico(BaseModel):
    """Resposta para listagem paginada"""
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros pulados")
    limit: int = Field(..., description="Limite por página")
    itens: List[ResumoOrdemServico] = Field(..., description="Lista de OS")


# ================================
# SCHEMAS DE AÇÕES ESPECÍFICAS
# ================================

class MudancaFaseRequest(BaseModel):
    """Request para mudança de fase"""
    nova_fase: FaseOSEnum = Field(..., description="Nova fase da OS")
    observacoes: Optional[str] = Field(None, max_length=500, description="Observações da mudança")
    usuario_responsavel: str = Field(..., min_length=3, max_length=100)


class AtualizacaoStatusRequest(BaseModel):
    """Request para atualização de status"""
    novo_status: StatusOS = Field(..., description="Novo status da OS")
    motivo: Optional[str] = Field(None, max_length=500, description="Motivo da mudança")
    usuario_responsavel: str = Field(..., min_length=3, max_length=100)


class HistoricoMudanca(BaseModel):
    """Histórico de mudanças da OS"""
    id: int
    data_mudanca: datetime
    tipo_mudanca: str  # fase, status, dados
    valor_anterior: Optional[str] = None
    valor_novo: str
    observacoes: Optional[str] = None
    usuario_responsavel: str
    
    class Config:
        from_attributes = True


# ================================
# SCHEMAS DE RELATÓRIOS
# ================================

class EstatisticasOS(BaseModel):
    """Estatísticas das OS"""
    total_os: int
    por_status: Dict[str, int]
    por_fase: Dict[str, int]
    por_prioridade: Dict[str, int]
    por_tipo: Dict[str, int]
    prazo_medio_execucao: Optional[float] = None
    valor_total_pendente: Optional[Decimal] = None


class DashboardOS(BaseModel):
    """Dashboard das OS"""
    estatisticas: EstatisticasOS
    os_urgentes: List[ResumoOrdemServico]
    os_atrasadas: List[ResumoOrdemServico]
    os_hoje: List[ResumoOrdemServico]
    fases_pendentes: Dict[str, int]