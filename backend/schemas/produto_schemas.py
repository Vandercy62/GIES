"""
SCHEMAS DE PRODUTOS - ERP PRIMOTEX
==================================

Schemas Pydantic para validação de dados de produtos.
Define estruturas para criação, atualização e resposta.

Autor: GitHub Copilot
Data: 01/11/2025
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ProdutoBase(BaseModel):
    """Schema base para produtos"""
    codigo: Optional[str] = Field(None, max_length=50)
    nome: str = Field(..., min_length=2, max_length=150)
    descricao: Optional[str] = None
    categoria: str = Field(..., max_length=100)
    unidade_medida: str = Field(..., max_length=10)
    preco_custo: Optional[Decimal] = Field(None, ge=0)
    preco_venda: Optional[Decimal] = Field(None, ge=0)
    margem_lucro: Optional[Decimal] = Field(None, ge=0)
    estoque_atual: int = Field(default=0, ge=0)
    estoque_minimo: int = Field(default=0, ge=0)
    codigo_barras: Optional[str] = Field(None, max_length=50)
    observacoes: Optional[str] = None
    ativo: bool = True


class ProdutoCreate(ProdutoBase):
    """Schema para criação de produto"""
    pass


class ProdutoUpdate(BaseModel):
    """Schema para atualização de produto"""
    codigo: Optional[str] = Field(None, max_length=50)
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    descricao: Optional[str] = None
    categoria: Optional[str] = Field(None, max_length=100)
    unidade_medida: Optional[str] = Field(None, max_length=10)
    preco_custo: Optional[Decimal] = Field(None, ge=0)
    preco_venda: Optional[Decimal] = Field(None, ge=0)
    margem_lucro: Optional[Decimal] = Field(None, ge=0)
    estoque_atual: Optional[int] = Field(None, ge=0)
    estoque_minimo: Optional[int] = Field(None, ge=0)
    codigo_barras: Optional[str] = Field(None, max_length=50)
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None


class ProdutoResponse(ProdutoBase):
    """Schema para resposta de produto"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class FiltrosProduto(BaseModel):
    """Schema para filtros de busca"""
    categoria: Optional[str] = None
    ativo: Optional[bool] = None
    busca: Optional[str] = None


class ListagemProdutos(BaseModel):
    """Schema para listagem paginada de produtos"""
    itens: List[ProdutoResponse]
    total: int
    skip: int
    limit: int