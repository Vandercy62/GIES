"""
SCHEMAS DE CLIENTES - ERP PRIMOTEX
=================================

Schemas Pydantic para validação de dados de clientes.
Define estruturas para criação, atualização e resposta.

ATUALIZAÇÃO FASE 100:
- Adicionados TODOS os campos do modelo cliente_model.py
- Organizado em seções (ABA 1, 2, 3) conforme documento original
- Corrigidos nomes de campos para match exato com modelo
- Adicionadas validações específicas por tipo de campo

Autor: GitHub Copilot
Data: 16/11/2025 (Atualizado FASE 100)
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List, Dict
from datetime import datetime, date
from decimal import Decimal
import re


class ClienteBase(BaseModel):
    """
    Schema base para clientes - COMPLETO FASE 100

    Contém TODOS os campos do modelo organizados em 3 seções:
    - ABA 1: Dados Básicos
    - ABA 2: Dados Complementares (Endereço, Contatos, Comercial)
    - ABA 3: Observações e Anexos
    """

    # =======================================
    # ABA 1 - DADOS BÁSICOS
    # =======================================
    nome: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nome completo (PF) ou Razão Social (PJ)"
    )
    tipo_pessoa: str = Field(
        ...,
        pattern="^(Física|Jurídica|fisica|juridica)$",
        description="Física ou Jurídica (aceita maiúscula/minúscula)"
    )
    cpf_cnpj: str = Field(
        ...,
        max_length=20,
        description="CPF (PF) ou CNPJ (PJ)"
    )
    rg_ie: Optional[str] = Field(
        None,
        max_length=20,
        description="RG (PF) ou Inscrição Estadual (PJ)"
    )
    data_nascimento_fundacao: Optional[date] = Field(
        None,
        description="Data de nascimento (PF) ou fundação (PJ)"
    )
    foto_path: Optional[str] = Field(
        None,
        max_length=255,
        description="Caminho da foto do cliente"
    )
    status: str = Field(
        default="Ativo",
        pattern="^(Ativo|Inativo|Prospect)$",
        description="Status do cliente"
    )
    origem: Optional[str] = Field(
        None,
        max_length=50,
        description="Origem: Google, Indicação, Facebook, etc."
    )
    tipo_cliente: Optional[str] = Field(
        None,
        max_length=30,
        description="Residencial, Comercial, Industrial, Público"
    )

    # =======================================
    # ABA 2 - DADOS COMPLEMENTARES
    # =======================================

    # Endereço
    endereco_cep: Optional[str] = Field(None, max_length=10, description="CEP")
    endereco_logradouro: Optional[str] = Field(
        None,
        max_length=150,
        description="Rua, avenida, etc."
    )
    endereco_numero: Optional[str] = Field(
        None,
        max_length=10,
        description="Número"
    )
    endereco_complemento: Optional[str] = Field(
        None,
        max_length=100,
        description="Apartamento, sala, etc."
    )
    endereco_bairro: Optional[str] = Field(
        None,
        max_length=100,
        description="Bairro"
    )
    endereco_cidade: Optional[str] = Field(
        None,
        max_length=100,
        description="Cidade"
    )
    endereco_estado: Optional[str] = Field(
        None,
        max_length=2,
        description="Estado (UF)"
    )

    # Contatos
    telefone_fixo: Optional[str] = Field(
        None,
        max_length=20,
        description="Telefone fixo"
    )
    telefone_celular: Optional[str] = Field(
        None,
        max_length=20,
        description="Telefone celular"
    )
    telefone_whatsapp: Optional[str] = Field(
        None,
        max_length=20,
        description="WhatsApp"
    )
    email_principal: Optional[EmailStr] = Field(
        None,
        description="Email principal"
    )
    email_secundario: Optional[EmailStr] = Field(
        None,
        description="Email secundário"
    )
    site: Optional[str] = Field(
        None,
        max_length=100,
        description="Site da empresa"
    )
    redes_sociais: Optional[str] = Field(
        None,
        description="Links das redes sociais (JSON)"
    )
    contatos_adicionais: Optional[str] = Field(
        None,
        description="Contatos extras (JSON)"
    )

    # Dados Bancários
    banco_nome: Optional[str] = Field(
        None,
        max_length=100,
        description="Nome do banco"
    )
    banco_agencia: Optional[str] = Field(
        None,
        max_length=10,
        description="Agência"
    )
    banco_conta: Optional[str] = Field(
        None,
        max_length=20,
        description="Conta"
    )

    # Dados Comerciais
    limite_credito: Optional[Decimal] = Field(
        default=Decimal("0.00"),
        description="Limite de crédito em R$"
    )
    dia_vencimento_preferencial: Optional[int] = Field(
        None,
        ge=1,
        le=31,
        description="Dia preferencial de vencimento (1-31)"
    )

    # =======================================
    # ABA 3 - OBSERVAÇÕES E ANEXOS
    # =======================================
    observacoes_gerais: Optional[str] = Field(
        None,
        description="Observações gerais sobre o cliente"
    )
    historico_interacoes: Optional[str] = Field(
        None,
        description="Histórico de interações (JSON)"
    )
    anexos_paths: Optional[str] = Field(
        None,
        description="Caminhos dos arquivos anexados (JSON)"
    )
    tags_categorias: Optional[str] = Field(
        None,
        description="Tags e categorias personalizadas (JSON)"
    )

    # Validadores
    @field_validator('tipo_pessoa')
    @classmethod
    def validar_tipo_pessoa(cls, v):
        if v not in ['Física', 'Jurídica']:
            raise ValueError('Tipo de pessoa deve ser "Física" ou "Jurídica"')
        return v

    @field_validator('status')
    @classmethod
    def validar_status(cls, v):
        if v not in ['Ativo', 'Inativo', 'Prospect']:
            raise ValueError(
                'Status deve ser "Ativo", "Inativo" ou "Prospect"'
            )
        return v

    @field_validator('endereco_estado')
    @classmethod
    def validar_estado(cls, v):
        if v and len(v) != 2:
            raise ValueError('Estado deve ter exatamente 2 caracteres (UF)')
        return v.upper() if v else v

    @field_validator('cpf_cnpj')
    @classmethod
    def validar_cpf_cnpj(cls, v):
        # Remove caracteres não numéricos
        apenas_numeros = re.sub(r'\D', '', v)
        if len(apenas_numeros) not in [11, 14]:
            raise ValueError(
                'CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos'
            )
        return v


class ClienteCreate(ClienteBase):
    """
    Schema para criação de cliente - FASE 100

    Herda TODOS os campos de ClienteBase.
    Apenas 'nome', 'tipo_pessoa' e 'cpf_cnpj' são obrigatórios.
    Demais campos são opcionais conforme regras de negócio.
    """


class ClienteUpdate(BaseModel):
    """
    Schema para atualização de cliente - FASE 100

    TODOS os campos são opcionais para permitir atualização parcial.
    Organizado nas mesmas 3 seções do modelo.
    """

    # =======================================
    # ABA 1 - DADOS BÁSICOS
    # =======================================
    nome: Optional[str] = Field(None, min_length=2, max_length=200)
    tipo_pessoa: Optional[str] = Field(None, pattern="^(Física|Jurídica)$")
    cpf_cnpj: Optional[str] = Field(None, max_length=20)
    rg_ie: Optional[str] = Field(None, max_length=20)
    data_nascimento_fundacao: Optional[date] = None
    foto_path: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, pattern="^(Ativo|Inativo|Prospect)$")
    origem: Optional[str] = Field(None, max_length=50)
    tipo_cliente: Optional[str] = Field(None, max_length=30)

    # =======================================
    # ABA 2 - DADOS COMPLEMENTARES
    # =======================================

    # Endereço
    endereco_cep: Optional[str] = Field(None, max_length=10)
    endereco_logradouro: Optional[str] = Field(None, max_length=150)
    endereco_numero: Optional[str] = Field(None, max_length=10)
    endereco_complemento: Optional[str] = Field(None, max_length=100)
    endereco_bairro: Optional[str] = Field(None, max_length=100)
    endereco_cidade: Optional[str] = Field(None, max_length=100)
    endereco_estado: Optional[str] = Field(None, max_length=2)

    # Contatos
    telefone_fixo: Optional[str] = Field(None, max_length=20)
    telefone_celular: Optional[str] = Field(None, max_length=20)
    telefone_whatsapp: Optional[str] = Field(None, max_length=20)
    email_principal: Optional[EmailStr] = None
    email_secundario: Optional[EmailStr] = None
    site: Optional[str] = Field(None, max_length=100)
    redes_sociais: Optional[str] = None
    contatos_adicionais: Optional[str] = None

    # Dados Bancários
    banco_nome: Optional[str] = Field(None, max_length=100)
    banco_agencia: Optional[str] = Field(None, max_length=10)
    banco_conta: Optional[str] = Field(None, max_length=20)

    # Dados Comerciais
    limite_credito: Optional[Decimal] = None
    dia_vencimento_preferencial: Optional[int] = Field(None, ge=1, le=31)

    # =======================================
    # ABA 3 - OBSERVAÇÕES E ANEXOS
    # =======================================
    observacoes_gerais: Optional[str] = None
    historico_interacoes: Optional[str] = None
    anexos_paths: Optional[str] = None
    tags_categorias: Optional[str] = None


class ClienteResponse(ClienteBase):
    """
    Schema para resposta de cliente - FASE 100

    Inclui TODOS os campos do modelo + campos de controle do sistema.
    """
    # Campos de identificação e controle
    id: int = Field(..., description="ID único do cliente")
    codigo: str = Field(
        ...,
        description="Código único do cliente (ex: CLI001)"
    )

    # Campos de auditoria (nomes CORRIGIDOS para match com modelo)
    data_criacao: Optional[datetime] = Field(
        None,
        description="Data de criação do cadastro"
    )
    data_atualizacao: Optional[datetime] = Field(
        None,
        description="Data da última atualização"
    )
    usuario_criacao_id: Optional[int] = Field(
        None,
        description="ID do usuário que criou"
    )
    usuario_atualizacao_id: Optional[int] = Field(
        None,
        description="ID do usuário que atualizou"
    )

    model_config = ConfigDict(from_attributes=True)


class FiltrosCliente(BaseModel):
    """
    Schema para filtros de busca - FASE 100

    Filtros disponíveis para a ABA 1 (Lista de Clientes):
    - nome: Busca parcial por nome/razão social
    - tipo_pessoa: Filtro por Física/Jurídica
    - status: Filtro por Ativo/Inativo/Prospect
    - ativo: Filtro boolean para status ativo/inativo
    - origem: Filtro por origem (Google, Indicação, etc.)
    - tipo_cliente: Filtro por tipo (Residencial, Comercial, etc.)
    - cidade: Filtro por cidade
    - busca: Busca global (nome, CPF, telefone, email)
    """
    nome: Optional[str] = Field(None, description="Busca parcial por nome")
    tipo_pessoa: Optional[str] = Field(None, description="Física ou Jurídica")
    status: Optional[str] = Field(
        None,
        description="Ativo, Inativo ou Prospect"
    )
    ativo: Optional[bool] = Field(None, description="Filtro por status ativo/inativo")
    origem: Optional[str] = Field(None, description="Google, Indicação, etc.")
    tipo_cliente: Optional[str] = Field(
        None,
        description="Residencial, Comercial, etc."
    )
    cidade: Optional[str] = Field(None, description="Filtro por cidade")
    busca: Optional[str] = Field(
        None,
        description="Busca global (nome, CPF, telefone, email)"
    )


class ListagemClientes(BaseModel):
    """
    Schema para listagem paginada de clientes - FASE 100

    Usado na ABA 1 (Lista de Clientes) para retornar resultados paginados.
    """
    itens: List[ClienteResponse] = Field(..., description="Lista de clientes")
    total: int = Field(..., description="Total de registros encontrados")
    skip: int = Field(..., description="Registros pulados (offset)")
    limit: int = Field(..., description="Limite de registros por página")


class ClienteResumido(BaseModel):
    """
    Schema resumido para listas e dropdowns - FASE 100

    Contém apenas campos essenciais para exibição rápida.
    Útil para comboboxes, autocomplete, etc.
    """
    id: int
    codigo: str
    nome: str
    tipo_pessoa: str
    cpf_cnpj: str
    telefone_celular: Optional[str] = None
    email_principal: Optional[EmailStr] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


# =======================================
# SCHEMAS AUXILIARES PARA CAMPOS JSON
# =======================================

class ContatoAdicional(BaseModel):
    """Schema para contatos adicionais (JSON)"""
    nome: str = Field(..., description="Nome do contato")
    cargo: Optional[str] = Field(None, description="Cargo/função")
    telefone: Optional[str] = Field(None, description="Telefone")
    email: Optional[EmailStr] = Field(None, description="Email")


class RedesSociais(BaseModel):
    """Schema para redes sociais (JSON)"""
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    outros: Optional[Dict[str, str]] = None


class InteracaoHistorico(BaseModel):
    """Schema para histórico de interações (JSON)"""
    data: datetime = Field(..., description="Data/hora da interação")
    tipo: str = Field(..., description="Tipo: ligação, email, visita, etc.")
    descricao: str = Field(..., description="Descrição da interação")
    usuario_id: Optional[int] = Field(
        None,
        description="ID do usuário que registrou"
    )


class AnexoCliente(BaseModel):
    """Schema para anexos (JSON)"""
    nome_arquivo: str = Field(..., description="Nome do arquivo")
    caminho: str = Field(..., description="Caminho completo do arquivo")
    tipo: str = Field(..., description="Tipo: documento, foto, planta, etc.")
    data_upload: datetime = Field(..., description="Data do upload")
    tamanho_bytes: Optional[int] = Field(
        None,
        description="Tamanho em bytes"
    )
