"""
Schemas Pydantic para módulo Financeiro
Sistema ERP Primotex - Fase 3

Schemas de validação para:
- ContaReceber
- ContaPagar  
- MovimentacaoFinanceira
- FluxoCaixa
- CategoriaFinanceira
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
from decimal import Decimal

from pydantic import BaseModel, Field, validator, root_validator
from pydantic.config import ConfigDict


# ================================
# ENUMS E CONSTANTES
# ================================

# Constantes para descrições
ID_CLIENTE_DESC = "ID do cliente"
ID_USUARIO_DESC = "ID do usuário"
ID_CATEGORIA_DESC = "ID da categoria"
VALOR_DESC = "Valor da operação"
OBSERVACOES_DESC = "Observações adicionais"
DATA_VENCIMENTO_DESC = "Data de vencimento"
DATA_PAGAMENTO_DESC = "Data de pagamento"

# Constantes para mensagens de validação
VALOR_POSITIVO_MSG = "Valor deve ser maior que zero"
CAMPO_VAZIO_MSG = "Campo não pode ser vazio"

class StatusFinanceiro(str, Enum):
    """Status das movimentações financeiras"""
    PENDENTE = "pendente"
    PAGO = "pago"
    PARCIAL = "parcial"
    VENCIDO = "vencido"
    CANCELADO = "cancelado"


class TipoMovimentacao(str, Enum):
    """Tipo de movimentação financeira"""
    RECEITA = "receita"
    DESPESA = "despesa"
    TRANSFERENCIA = "transferencia"


class FormaPagamento(str, Enum):
    """Formas de pagamento aceitas"""
    DINHEIRO = "dinheiro"
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    BOLETO = "boleto"
    TRANSFERENCIA = "transferencia"
    CHEQUE = "cheque"
    OUTROS = "outros"


class TipoCategoria(str, Enum):
    """Tipo de categoria financeira"""
    RECEITA = "receita"
    DESPESA = "despesa"
    AMBOS = "ambos"


class PeriodoFluxo(str, Enum):
    """Período para fluxo de caixa"""
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"
    ANUAL = "anual"


# ================================
# SCHEMAS BASE
# ================================

class ContaReceberBase(BaseModel):
    """Schema base para contas a receber"""
    cliente_id: int = Field(..., description=ID_CLIENTE_DESC)
    descricao: str = Field(..., min_length=3, max_length=200, description="Descrição da conta")
    valor_total: Decimal = Field(..., ge=0, description="Valor total da conta")
    data_vencimento: date = Field(..., description=DATA_VENCIMENTO_DESC)
    categoria_id: Optional[int] = Field(None, description=ID_CATEGORIA_DESC)
    ordem_servico_id: Optional[int] = Field(None, description="ID da OS relacionada")
    observacoes: Optional[str] = Field(None, max_length=500, description=OBSERVACOES_DESC)
    
    @validator('valor_total')
    def validar_valor_positivo(cls, v: Decimal) -> Decimal:
        """Valida se o valor é positivo"""
        if v <= 0:
            raise ValueError(VALOR_POSITIVO_MSG)
        return v
    
    @validator('descricao')
    def validar_descricao(cls, v: str) -> str:
        """Valida e formata descrição"""
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Descrição não pode ser vazia")
        return v


class ContaPagarBase(BaseModel):
    """Schema base para contas a pagar"""
    fornecedor: str = Field(..., min_length=3, max_length=200, description="Nome do fornecedor")
    descricao: str = Field(..., min_length=3, max_length=200, description="Descrição da conta")
    valor_total: Decimal = Field(..., ge=0, description="Valor total da conta")
    data_vencimento: date = Field(..., description=DATA_VENCIMENTO_DESC)
    categoria_id: Optional[int] = Field(None, description=ID_CATEGORIA_DESC)
    observacoes: Optional[str] = Field(None, max_length=500, description=OBSERVACOES_DESC)
    
    @validator('valor_total')
    def validar_valor_positivo(cls, v: Decimal) -> Decimal:
        """Valida se o valor é positivo"""
        if v <= 0:
            raise ValueError(VALOR_POSITIVO_MSG)
        return v
    
    @validator('fornecedor', 'descricao')
    def validar_textos(cls, v: str) -> str:
        """Valida e formata textos"""
        if v:
            v = v.strip()
            if not v:
                raise ValueError(CAMPO_VAZIO_MSG)
        return v


class MovimentacaoFinanceiraBase(BaseModel):
    """Schema base para movimentações financeiras"""
    tipo: TipoMovimentacao = Field(..., description="Tipo da movimentação")
    valor: Decimal = Field(..., ge=0, description=VALOR_DESC)
    descricao: str = Field(..., min_length=3, max_length=200, description="Descrição da movimentação")
    data_movimento: datetime = Field(..., description="Data da movimentação")
    forma_pagamento: FormaPagamento = Field(..., description="Forma de pagamento")
    categoria_id: Optional[int] = Field(None, description=ID_CATEGORIA_DESC)
    conta_receber_id: Optional[int] = Field(None, description="ID da conta a receber")
    conta_pagar_id: Optional[int] = Field(None, description="ID da conta a pagar")
    observacoes: Optional[str] = Field(None, max_length=500, description=OBSERVACOES_DESC)
    
    @validator('valor')
    def validar_valor_positivo(cls, v: Decimal) -> Decimal:
        """Valida se o valor é positivo"""
        if v <= 0:
            raise ValueError(VALOR_POSITIVO_MSG)
        return v
    
    @validator('descricao')
    def validar_descricao(cls, v: str) -> str:
        """Valida e formata descrição"""
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Descrição não pode ser vazia")
        return v


class CategoriaFinanceiraBase(BaseModel):
    """Schema base para categorias financeiras"""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome da categoria")
    tipo: TipoCategoria = Field(..., description="Tipo da categoria")
    cor: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Cor da categoria (hex)")
    icone: Optional[str] = Field(None, max_length=50, description="Ícone da categoria")
    descricao: Optional[str] = Field(None, max_length=200, description="Descrição da categoria")
    ativo: bool = Field(default=True, description="Se a categoria está ativa")
    
    @validator('nome')
    def validar_nome(cls, v: str) -> str:
        """Valida e formata nome"""
        if v:
            v = v.strip().title()
            if not v:
                raise ValueError("Nome não pode ser vazio")
        return v


# ================================
# SCHEMAS CREATE
# ================================

class ContaReceberCreate(ContaReceberBase):
    """Schema para criação de conta a receber"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "cliente_id": 1,
                "descricao": "Instalação de forro PVC - OS #001",
                "valor_total": "2500.00",
                "data_vencimento": "2024-12-15",
                "categoria_id": 1,
                "ordem_servico_id": 1,
                "observacoes": "Pagamento à vista com 5% de desconto"
            }
        }
    )


class ContaPagarCreate(ContaPagarBase):
    """Schema para criação de conta a pagar"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "fornecedor": "Materiais de Construção Ltda",
                "descricao": "Compra de materiais para OS #001",
                "valor_total": "1200.00",
                "data_vencimento": "2024-12-10",
                "categoria_id": 2,
                "observacoes": "Pagamento em 30 dias"
            }
        }
    )


class MovimentacaoFinanceiraCreate(MovimentacaoFinanceiraBase):
    """Schema para criação de movimentação financeira"""
    usuario_id: int = Field(..., description=ID_USUARIO_DESC)
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "tipo": "receita",
                "valor": "2500.00",
                "descricao": "Recebimento de OS #001",
                "data_movimento": "2024-12-01T14:30:00",
                "forma_pagamento": "pix",
                "categoria_id": 1,
                "conta_receber_id": 1,
                "usuario_id": 1,
                "observacoes": "Pagamento à vista"
            }
        }
    )


class CategoriaFinanceiraCreate(CategoriaFinanceiraBase):
    """Schema para criação de categoria financeira"""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "nome": "Vendas de Serviços",
                "tipo": "receita",
                "cor": "#4CAF50",
                "icone": "money-check-alt",
                "descricao": "Receitas provenientes de serviços executados"
            }
        }
    )


# ================================
# SCHEMAS UPDATE
# ================================

class ContaReceberUpdate(BaseModel):
    """Schema para atualização de conta a receber"""
    cliente_id: Optional[int] = None
    descricao: Optional[str] = Field(None, min_length=3, max_length=200)
    valor_total: Optional[Decimal] = Field(None, ge=0)
    data_vencimento: Optional[date] = None
    status: Optional[StatusFinanceiro] = None
    categoria_id: Optional[int] = None
    ordem_servico_id: Optional[int] = None
    observacoes: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(from_attributes=True)


class ContaPagarUpdate(BaseModel):
    """Schema para atualização de conta a pagar"""
    fornecedor: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = Field(None, min_length=3, max_length=200)
    valor_total: Optional[Decimal] = Field(None, ge=0)
    data_vencimento: Optional[date] = None
    status: Optional[StatusFinanceiro] = None
    categoria_id: Optional[int] = None
    observacoes: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(from_attributes=True)


class MovimentacaoFinanceiraUpdate(BaseModel):
    """Schema para atualização de movimentação financeira"""
    tipo: Optional[TipoMovimentacao] = None
    valor: Optional[Decimal] = Field(None, ge=0)
    descricao: Optional[str] = Field(None, min_length=3, max_length=200)
    data_movimento: Optional[datetime] = None
    forma_pagamento: Optional[FormaPagamento] = None
    categoria_id: Optional[int] = None
    observacoes: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(from_attributes=True)


class CategoriaFinanceiraUpdate(BaseModel):
    """Schema para atualização de categoria financeira"""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    tipo: Optional[TipoCategoria] = None
    cor: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icone: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = Field(None, max_length=200)
    ativo: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


# ================================
# SCHEMAS RESPONSE
# ================================

class ContaReceberResponse(ContaReceberBase):
    """Schema de resposta para conta a receber"""
    id: int
    status: StatusFinanceiro
    valor_pago: Decimal
    valor_pendente: Decimal
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None
    
    # Relacionamentos
    cliente_nome: Optional[str] = None
    categoria_nome: Optional[str] = None
    ordem_servico_numero: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ContaPagarResponse(ContaPagarBase):
    """Schema de resposta para conta a pagar"""
    id: int
    status: StatusFinanceiro
    valor_pago: Decimal
    valor_pendente: Decimal
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None
    
    # Relacionamentos
    categoria_nome: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class MovimentacaoFinanceiraResponse(MovimentacaoFinanceiraBase):
    """Schema de resposta para movimentação financeira"""
    id: int
    data_criacao: datetime
    
    # Relacionamentos
    categoria_nome: Optional[str] = None
    usuario_nome: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class CategoriaFinanceiraResponse(CategoriaFinanceiraBase):
    """Schema de resposta para categoria financeira"""
    id: int
    data_criacao: datetime
    data_atualizacao: Optional[datetime] = None
    
    # Estatísticas
    total_movimentacoes: int = 0
    valor_total_periodo: Decimal = Field(default=Decimal('0'), description="Valor total no período")
    
    model_config = ConfigDict(from_attributes=True)


# ================================
# SCHEMAS ESPECIAIS
# ================================

class ContaReceberFilter(BaseModel):
    """Schema para filtros de contas a receber"""
    cliente_id: Optional[int] = None
    status: Optional[List[StatusFinanceiro]] = None
    data_vencimento_inicio: Optional[date] = None
    data_vencimento_fim: Optional[date] = None
    categoria_id: Optional[int] = None
    valor_minimo: Optional[Decimal] = None
    valor_maximo: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)


class ContaPagarFilter(BaseModel):
    """Schema para filtros de contas a pagar"""
    fornecedor: Optional[str] = None
    status: Optional[List[StatusFinanceiro]] = None
    data_vencimento_inicio: Optional[date] = None
    data_vencimento_fim: Optional[date] = None
    categoria_id: Optional[int] = None
    valor_minimo: Optional[Decimal] = None
    valor_maximo: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)


class MovimentacaoFilter(BaseModel):
    """Schema para filtros de movimentações"""
    tipo: Optional[List[TipoMovimentacao]] = None
    forma_pagamento: Optional[List[FormaPagamento]] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    categoria_id: Optional[int] = None
    valor_minimo: Optional[Decimal] = None
    valor_maximo: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)


class FluxoCaixaRequest(BaseModel):
    """Schema para requisição de fluxo de caixa"""
    data_inicio: date = Field(..., description="Data de início do período")
    data_fim: date = Field(..., description="Data de fim do período")
    periodo: PeriodoFluxo = Field(default=PeriodoFluxo.DIARIO, description="Período de agrupamento")
    incluir_previsoes: bool = Field(default=True, description="Incluir previsões futuras")
    categorias: Optional[List[int]] = Field(None, description="IDs das categorias")
    
    @validator('data_fim')
    def validar_periodo(cls, v: date, values) -> date:
        """Valida se data fim é posterior ao início"""
        if 'data_inicio' in values and v < values['data_inicio']:
            raise ValueError("Data fim deve ser posterior à data início")
        return v
    
    model_config = ConfigDict(from_attributes=True)


class FluxoCaixaItem(BaseModel):
    """Schema para item do fluxo de caixa"""
    data: date = Field(..., description="Data do item")
    receitas: Decimal = Field(default=Decimal('0'), description="Total de receitas")
    despesas: Decimal = Field(default=Decimal('0'), description="Total de despesas")
    saldo: Decimal = Field(default=Decimal('0'), description="Saldo do período")
    saldo_acumulado: Decimal = Field(default=Decimal('0'), description="Saldo acumulado")
    
    model_config = ConfigDict(from_attributes=True)


class FluxoCaixaResponse(BaseModel):
    """Schema de resposta para fluxo de caixa"""
    periodo: PeriodoFluxo
    data_inicio: date
    data_fim: date
    items: List[FluxoCaixaItem]
    resumo: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(from_attributes=True)


class DashboardFinanceiro(BaseModel):
    """Schema para dashboard financeiro"""
    receitas_mes: Decimal = Field(default=Decimal('0'), description="Receitas do mês")
    despesas_mes: Decimal = Field(default=Decimal('0'), description="Despesas do mês")
    saldo_mes: Decimal = Field(default=Decimal('0'), description="Saldo do mês")
    contas_receber_vencidas: int = 0
    contas_pagar_vencidas: int = 0
    contas_receber_hoje: int = 0
    contas_pagar_hoje: int = 0
    valor_receber_total: Decimal = Field(default=Decimal('0'))
    valor_pagar_total: Decimal = Field(default=Decimal('0'))
    
    model_config = ConfigDict(from_attributes=True)


class PagamentoRequest(BaseModel):
    """Schema para registro de pagamento"""
    valor_pago: Decimal = Field(..., ge=0, description="Valor pago")
    data_pagamento: date = Field(..., description=DATA_PAGAMENTO_DESC)
    forma_pagamento: FormaPagamento = Field(..., description="Forma de pagamento")
    observacoes: Optional[str] = Field(None, max_length=500, description=OBSERVACOES_DESC)
    
    @validator('valor_pago')
    def validar_valor_positivo(cls, v: Decimal) -> Decimal:
        """Valida se o valor é positivo"""
        if v <= 0:
            raise ValueError(VALOR_POSITIVO_MSG)
        return v
    
    model_config = ConfigDict(from_attributes=True)


# ================================
# SCHEMAS DE LISTAGEM
# ================================

class ContaReceberListResponse(BaseModel):
    """Schema de resposta para listagem de contas a receber"""
    items: List[ContaReceberResponse]
    total: int
    page: int
    size: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True)


class ContaPagarListResponse(BaseModel):
    """Schema de resposta para listagem de contas a pagar"""
    items: List[ContaPagarResponse]
    total: int
    page: int
    size: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True)


class MovimentacaoListResponse(BaseModel):
    """Schema de resposta para listagem de movimentações"""
    items: List[MovimentacaoFinanceiraResponse]
    total: int
    page: int
    size: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True)


# ================================
# EXPORTS
# ================================

__all__ = [
    # Enums
    'StatusFinanceiro',
    'TipoMovimentacao',
    'FormaPagamento',
    'TipoCategoria',
    'PeriodoFluxo',
    
    # Schemas Create
    'ContaReceberCreate',
    'ContaPagarCreate',
    'MovimentacaoFinanceiraCreate',
    'CategoriaFinanceiraCreate',
    
    # Schemas Update
    'ContaReceberUpdate',
    'ContaPagarUpdate',
    'MovimentacaoFinanceiraUpdate',
    'CategoriaFinanceiraUpdate',
    
    # Schemas Response
    'ContaReceberResponse',
    'ContaPagarResponse',
    'MovimentacaoFinanceiraResponse',
    'CategoriaFinanceiraResponse',
    
    # Schemas Especiais
    'ContaReceberFilter',
    'ContaPagarFilter',
    'MovimentacaoFilter',
    'FluxoCaixaRequest',
    'FluxoCaixaItem',
    'FluxoCaixaResponse',
    'DashboardFinanceiro',
    'PagamentoRequest',
    
    # Schemas de Listagem
    'ContaReceberListResponse',
    'ContaPagarListResponse',
    'MovimentacaoListResponse'
]