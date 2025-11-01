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
    tipo_pessoa: str = Field(..., regex="^(fisica|juridica)$")
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=200)
    numero: Optional[str] = Field(None, max_length=10)
    complemento: Optional[str] = Field(None, max_length=50)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    observacoes: Optional[str] = None
    ativo: bool = True


class ClienteCreate(ClienteBase):
    """Schema para criação de cliente"""
    pass


class ClienteUpdate(BaseModel):
    """Schema para atualização de cliente"""
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    tipo_pessoa: Optional[str] = Field(None, regex="^(fisica|juridica)$")
    cpf_cnpj: Optional[str] = Field(None, max_length=18)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=200)
    numero: Optional[str] = Field(None, max_length=10)
    complemento: Optional[str] = Field(None, max_length=50)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None


class ClienteResponse(ClienteBase):
    """Schema para resposta de cliente"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
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