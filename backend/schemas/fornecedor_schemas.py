"""
SISTEMA ERP PRIMOTEX - SCHEMAS DE FORNECEDORES
=============================================

Schemas Pydantic para validação e serialização de dados
de fornecedores na API REST.

SCHEMAS INCLUÍDOS:
- FornecedorBase: Schema base comum
- FornecedorCreate: Para criação de fornecedores
- FornecedorUpdate: Para atualização de fornecedores
- FornecedorResponse: Para resposta da API
- FornecedorFilter: Para filtros de listagem
- FornecedorListResponse: Para listagem paginada

Autor: GitHub Copilot
Data: 01/11/2025
"""

from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, validator, EmailStr


# =======================================
# ENUMS E CONSTANTES
# =======================================

class TipoFornecedor(str, Enum):
    """Tipos de fornecedor"""
    PESSOA_FISICA = "Pessoa Física"
    PESSOA_JURIDICA = "Pessoa Jurídica"


class StatusFornecedor(str, Enum):
    """Status do fornecedor"""
    ATIVO = "Ativo"
    INATIVO = "Inativo"
    BLOQUEADO = "Bloqueado"
    EM_ANALISE = "Em Análise"


class CategoriaFornecedor(str, Enum):
    """Categorias de fornecedor"""
    MATERIAIS_CONSTRUCAO = "Materiais de Construção"
    FERRAGENS_PARAFUSOS = "Ferragens e Parafusos"
    PERFIS_ALUMINIO = "Perfis de Alumínio"
    FORROS_PVC = "Forros PVC"
    DIVISORIAS = "Divisórias"
    GESSO_ACABAMENTOS = "Gesso e Acabamentos"
    EQUIPAMENTOS_FERRAMENTAS = "Equipamentos e Ferramentas"
    SERVICOS_TERCEIRIZADOS = "Serviços Terceirizados"
    TRANSPORTE_LOGISTICA = "Transporte e Logística"
    ESCRITORIO_ADMIN = "Escritório e Administração"
    OUTROS = "Outros"


class PorteEmpresa(str, Enum):
    """Porte da empresa"""
    MEI = "MEI"
    MICROEMPRESA = "Microempresa"
    PEQUENA = "Pequena Empresa"
    MEDIA = "Média Empresa"
    GRANDE = "Grande Empresa"


# =======================================
# SCHEMAS BASE
# =======================================

class FornecedorBase(BaseModel):
    """Schema base para fornecedor"""

    # Identificação básica
    cnpj_cpf: str = Field(
        ...,
        min_length=11,
        max_length=18,
        description="CNPJ ou CPF (apenas números)",
        example="12345678901234"
    )

    razao_social: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Razão social ou nome completo",
        example="Materiais de Construção Silva Ltda"
    )

    nome_fantasia: Optional[str] = Field(
        None,
        max_length=200,
        description="Nome fantasia ou apelido",
        example="Silva Materiais"
    )

    tipo_pessoa: TipoFornecedor = Field(
        default=TipoFornecedor.PESSOA_JURIDICA,
        description="Tipo de pessoa"
    )

    inscricao_estadual: Optional[str] = Field(
        None,
        max_length=20,
        description="Inscrição estadual"
    )

    # Categorização
    categoria: CategoriaFornecedor = Field(
        default=CategoriaFornecedor.OUTROS,
        description="Categoria principal do fornecedor"
    )

    subcategoria: Optional[str] = Field(
        None,
        max_length=100,
        description="Subcategoria específica"
    )

    porte_empresa: Optional[PorteEmpresa] = Field(
        None,
        description="Porte da empresa"
    )

    # Contato
    contato_principal: Optional[str] = Field(
        None,
        max_length=100,
        description="Nome do responsável/vendedor",
        example="João Silva"
    )

    telefone: Optional[str] = Field(
        None,
        max_length=20,
        description="Telefone principal",
        example="(11) 99999-9999"
    )

    telefone_2: Optional[str] = Field(
        None,
        max_length=20,
        description="Telefone secundário"
    )

    email: Optional[EmailStr] = Field(
        None,
        description="Email principal de contato",
        example="contato@silvamateriais.com.br"
    )

    email_2: Optional[EmailStr] = Field(
        None,
        description="Email secundário"
    )

    website: Optional[str] = Field(
        None,
        max_length=200,
        description="Site da empresa"
    )

    # Endereço
    cep: Optional[str] = Field(
        None,
        max_length=9,
        description="CEP formatado",
        example="01234-567"
    )

    logradouro: Optional[str] = Field(
        None,
        max_length=200,
        description="Logradouro"
    )

    numero: Optional[str] = Field(
        None,
        max_length=20,
        description="Número"
    )

    complemento: Optional[str] = Field(
        None,
        max_length=100,
        description="Complemento"
    )

    bairro: Optional[str] = Field(
        None,
        max_length=100,
        description="Bairro"
    )

    cidade: Optional[str] = Field(
        None,
        max_length=100,
        description="Cidade"
    )

    estado: Optional[str] = Field(
        None,
        max_length=2,
        description="UF do estado",
        example="SP"
    )

    # Informações comerciais
    condicoes_pagamento: Optional[str] = Field(
        None,
        max_length=200,
        description="Condições padrão de pagamento",
        example="30 dias"
    )

    prazo_entrega_padrao: Optional[int] = Field(
        None,
        ge=0,
        le=365,
        description="Prazo médio de entrega em dias"
    )

    valor_minimo_pedido: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Valor mínimo para pedidos"
    )

    desconto_padrao: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="Percentual de desconto padrão"
    )

    avaliacao: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Avaliação do fornecedor (1 a 5 estrelas)"
    )

    # Dados bancários
    banco: Optional[str] = Field(
        None,
        max_length=100,
        description="Nome do banco principal"
    )

    agencia: Optional[str] = Field(
        None,
        max_length=20,
        description="Agência bancária"
    )

    conta: Optional[str] = Field(
        None,
        max_length=30,
        description="Número da conta corrente"
    )

    chave_pix: Optional[str] = Field(
        None,
        max_length=100,
        description="Chave PIX"
    )

    # Observações
    observacoes: Optional[str] = Field(
        None,
        description="Observações gerais"
    )

    historico_problemas: Optional[str] = Field(
        None,
        description="Histórico de problemas"
    )

    tags: Optional[str] = Field(
        None,
        description="Tags em formato JSON"
    )

    # Status
    status: StatusFornecedor = Field(
        default=StatusFornecedor.ATIVO,
        description="Status do fornecedor"
    )

    ativo: bool = Field(
        default=True,
        description="Se o fornecedor está ativo"
    )

    motivo_inativacao: Optional[str] = Field(
        None,
        max_length=200,
        description="Motivo da inativação"
    )

    @validator('cnpj_cpf')
    def validate_cnpj_cpf(cls, v):
        """Valida CNPJ/CPF"""
        if not v:
            return v

        # Remove caracteres não numéricos
        doc = ''.join(filter(str.isdigit, v))

        if len(doc) not in [11, 14]:
            raise ValueError(
                "CNPJ deve ter 14 dígitos e CPF deve ter 11 dígitos"
            )

        return doc

    @validator('telefone', 'telefone_2')
    def validate_telefone(cls, v):
        """Valida telefone"""
        if not v:
            return v

        # Remove caracteres não numéricos
        tel = ''.join(filter(str.isdigit, v))

        if len(tel) not in [10, 11]:
            raise ValueError("Telefone deve ter 10 ou 11 dígitos")

        return tel

    @validator('cep')
    def validate_cep(cls, v):
        """Valida CEP"""
        if not v:
            return v

        # Remove caracteres não numéricos
        cep = ''.join(filter(str.isdigit, v))

        if len(cep) != 8:
            raise ValueError("CEP deve ter 8 dígitos")

        return f"{cep[:5]}-{cep[5:]}"

    @validator('estado')
    def validate_estado(cls, v):
        """Valida UF do estado"""
        if not v:
            return v

        estados_validos = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
            'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
            'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]

        if v.upper() not in estados_validos:
            raise ValueError("UF do estado inválida")

        return v.upper()


# =======================================
# SCHEMAS DE CRIAÇÃO
# =======================================

class FornecedorCreate(FornecedorBase):
    """Schema para criação de fornecedor"""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "cnpj_cpf": "12345678901234",
                "razao_social": "Materiais de Construção Silva Ltda",
                "nome_fantasia": "Silva Materiais",
                "tipo_pessoa": "Pessoa Jurídica",
                "categoria": "Materiais de Construção",
                "contato_principal": "João Silva",
                "telefone": "11999999999",
                "email": "contato@silvamateriais.com.br",
                "cep": "01234567",
                "logradouro": "Rua das Flores",
                "numero": "123",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "condicoes_pagamento": "30 dias",
                "prazo_entrega_padrao": 5,
                "observacoes": "Fornecedor confiável com boa qualidade"
            }
        }
    )


# =======================================
# SCHEMAS DE ATUALIZAÇÃO
# =======================================

class FornecedorUpdate(BaseModel):
    """Schema para atualização de fornecedor"""

    razao_social: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200
    )
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    inscricao_estadual: Optional[str] = Field(None, max_length=20)
    categoria: Optional[CategoriaFornecedor] = None
    subcategoria: Optional[str] = Field(None, max_length=100)
    porte_empresa: Optional[PorteEmpresa] = None
    contato_principal: Optional[str] = Field(None, max_length=100)
    telefone: Optional[str] = Field(None, max_length=20)
    telefone_2: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    email_2: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=200)
    cep: Optional[str] = Field(None, max_length=9)
    logradouro: Optional[str] = Field(None, max_length=200)
    numero: Optional[str] = Field(None, max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    condicoes_pagamento: Optional[str] = Field(None, max_length=200)
    prazo_entrega_padrao: Optional[int] = Field(None, ge=0, le=365)
    valor_minimo_pedido: Optional[Decimal] = Field(None, ge=0)
    desconto_padrao: Optional[Decimal] = Field(None, ge=0, le=100)
    avaliacao: Optional[int] = Field(None, ge=1, le=5)
    banco: Optional[str] = Field(None, max_length=100)
    agencia: Optional[str] = Field(None, max_length=20)
    conta: Optional[str] = Field(None, max_length=30)
    chave_pix: Optional[str] = Field(None, max_length=100)
    observacoes: Optional[str] = None
    historico_problemas: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[StatusFornecedor] = None
    ativo: Optional[bool] = None
    motivo_inativacao: Optional[str] = Field(None, max_length=200)

    model_config = ConfigDict(from_attributes=True)


# =======================================
# SCHEMAS DE RESPOSTA
# =======================================

class FornecedorResponse(FornecedorBase):
    """Schema de resposta para fornecedor"""

    id: int
    endereco_completo: Optional[str] = None
    data_cadastro: datetime
    data_atualizacao: Optional[datetime] = None
    usuario_cadastro_id: Optional[int] = None
    usuario_atualizacao_id: Optional[int] = None

    # Campos calculados
    nome_exibicao: Optional[str] = None
    documento_formatado: Optional[str] = None
    telefone_formatado: Optional[str] = None
    contato_completo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# =======================================
# SCHEMAS DE FILTRO E LISTAGEM
# =======================================

class FornecedorFilter(BaseModel):
    """Schema para filtros de listagem"""

    # Filtros de texto
    search: Optional[str] = Field(
        None,
        description="Busca por nome, CNPJ/CPF, email"
    )

    # Filtros específicos
    categoria: Optional[CategoriaFornecedor] = None
    tipo_pessoa: Optional[TipoFornecedor] = None
    status: Optional[StatusFornecedor] = None
    ativo: Optional[bool] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None

    # Filtros por avaliação
    avaliacao_minima: Optional[int] = Field(None, ge=1, le=5)

    # Filtros por data
    data_cadastro_inicio: Optional[datetime] = None
    data_cadastro_fim: Optional[datetime] = None

    # Paginação
    page: int = Field(default=1, ge=1, description="Página")
    size: int = Field(default=50, ge=1, le=200, description="Itens por página")

    # Ordenação
    order_by: Optional[str] = Field(
        default="razao_social",
        description="Campo para ordenação"
    )
    order_direction: Optional[str] = Field(
        default="asc",
        description="Direção da ordenação (asc/desc)"
    )

    model_config = ConfigDict(from_attributes=True)


class FornecedorListItem(BaseModel):
    """Item da lista de fornecedores"""

    id: int
    cnpj_cpf: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    categoria: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    cidade: Optional[str] = None
    status: str
    ativo: bool
    avaliacao: Optional[int] = None
    data_cadastro: datetime

    # Campos calculados
    nome_exibicao: Optional[str] = None
    documento_formatado: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FornecedorListResponse(BaseModel):
    """Resposta da listagem de fornecedores"""

    items: List[FornecedorListItem]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


# =======================================
# SCHEMAS ESPECIAIS
# =======================================

class FornecedorResumo(BaseModel):
    """Resumo do fornecedor para seleção"""

    id: int
    nome_exibicao: str
    documento_formatado: str
    categoria: str
    telefone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EstatisticasFornecedor(BaseModel):
    """Estatísticas dos fornecedores"""

    total_fornecedores: int
    total_ativos: int
    total_inativos: int
    total_por_categoria: dict
    total_por_estado: dict
    avaliacao_media: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


# =======================================
# EXPORTS
# =======================================

__all__ = [
    # Enums
    'TipoFornecedor',
    'StatusFornecedor',
    'CategoriaFornecedor',
    'PorteEmpresa',

    # Schemas principais
    'FornecedorBase',
    'FornecedorCreate',
    'FornecedorUpdate',
    'FornecedorResponse',

    # Schemas de listagem
    'FornecedorFilter',
    'FornecedorListItem',
    'FornecedorListResponse',

    # Schemas especiais
    'FornecedorResumo',
    'EstatisticasFornecedor'
]