"""
SCHEMAS DE CLIENTES - ERP PRIMOTEX
=================================

Schemas Pydantic para validação de dados de clientes.
Define estruturas para criação, atualização e resposta.

Autor: GitHub Copilot
Data: 01/11/2025
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class ClienteBase(BaseModel):
    """Schema base para clientes"""
    nome: str = Field(..., min_length=2, max_length=150)
    tipo_pessoa: str = Field(..., pattern="^(fisica|juridica)$")
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    email_principal: Optional[EmailStr] = None  # CORRIGIDO - modelo usa email_principal
    telefone_celular: Optional[str] = Field(None, max_length=20)  # CORRIGIDO - modelo usa telefone_celular
    endereco_logradouro: Optional[str] = Field(None, max_length=200)  # CORRIGIDO - modelo usa endereco_logradouro
    endereco_numero: Optional[str] = Field(None, max_length=10)
    endereco_complemento: Optional[str] = Field(None, max_length=50)
    endereco_bairro: Optional[str] = Field(None, max_length=100)
    endereco_cidade: Optional[str] = Field(None, max_length=100)
    endereco_estado: Optional[str] = Field(None, max_length=2)
    endereco_cep: Optional[str] = Field(None, max_length=10)
    observacoes_gerais: Optional[str] = None  # CORRIGIDO - modelo usa observacoes_gerais
    status: str = Field(default="Ativo", pattern="^(Ativo|Inativo|Prospect)$")  # ADICIONADO


class ClienteCreate(ClienteBase):
    """Schema para criação de cliente - herda todos os campos de ClienteBase"""
    ...  # Mantém a classe vazia intencionalmente para herança


class ClienteUpdate(BaseModel):
    """Schema para atualização de cliente"""
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    tipo_pessoa: Optional[str] = Field(None, pattern="^(fisica|juridica)$")
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    email_principal: Optional[EmailStr] = None
    telefone_celular: Optional[str] = Field(None, max_length=20)
    endereco_logradouro: Optional[str] = Field(None, max_length=200)
    endereco_numero: Optional[str] = Field(None, max_length=10)
    endereco_complemento: Optional[str] = Field(None, max_length=50)
    endereco_bairro: Optional[str] = Field(None, max_length=100)
    endereco_cidade: Optional[str] = Field(None, max_length=100)
    endereco_estado: Optional[str] = Field(None, max_length=2)
    endereco_cep: Optional[str] = Field(None, max_length=10)
    observacoes_gerais: Optional[str] = None
    ativo: Optional[bool] = None


class ClienteResponse(ClienteBase):
    """Schema para resposta de cliente"""
    id: int
    codigo: str  # ADICIONADO - campo código do cliente
    data_cadastro: Optional[datetime] = None  # CORRIGIDO - modelo usa data_cadastro
    data_atualizacao: Optional[datetime] = None  # CORRIGIDO - modelo usa data_atualizacao
    
    model_config = ConfigDict(from_attributes=True)


class FiltrosCliente(BaseModel):
    """Schema para filtros de busca"""
    nome: Optional[str] = None
    tipo_pessoa: Optional[str] = None
    cidade: Optional[str] = None
    ativo: Optional[bool] = None
    busca: Optional[str] = None


class ListagemClientes(BaseModel):
    """Schema para listagem paginada de clientes"""
    itens: List[ClienteResponse]
    total: int
    skip: int
    limit: int