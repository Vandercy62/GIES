"""
Schemas Pydantic para Ordem de Serviço
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import enum

class OrdemServicoFase(str, enum.Enum):
    CRIACAO = "criação"
    PLANEJAMENTO = "planejamento"
    EXECUCAO = "execução"
    QUALIDADE = "qualidade"
    ENTREGA = "entrega"
    FATURAMENTO = "faturamento"
    POS_VENDA = "pós-venda"

class OrdemServicoItemSchema(BaseModel):
    id: Optional[int]
    produto_id: int
    quantidade: float = 1
    valor_unitario: float = 0.0
    valor_total: float = 0.0
    descricao: Optional[str] = None

    class Config:
        orm_mode = True

class OrdemServicoHistoricoSchema(BaseModel):
    id: Optional[int]
    data: Optional[datetime]
    usuario_id: Optional[int]
    fase: OrdemServicoFase
    status: str
    observacao: Optional[str] = None

    class Config:
        orm_mode = True

class OrdemServicoBase(BaseModel):
    cliente_id: int
    responsavel_id: Optional[int]
    descricao: Optional[str]
    data_previsao: Optional[datetime]
    valor_total: Optional[float] = 0.0
    observacoes: Optional[str]

class OrdemServicoCreate(OrdemServicoBase):
    itens: List[OrdemServicoItemSchema] = []

class OrdemServicoUpdate(OrdemServicoBase):
    fase: Optional[OrdemServicoFase]
    status: Optional[str]
    itens: Optional[List[OrdemServicoItemSchema]]

class OrdemServicoSchema(OrdemServicoBase):
    id: int
    numero: str
    fase: OrdemServicoFase
    status: str
    data_criacao: datetime
    data_atualizacao: datetime
    data_conclusao: Optional[datetime]
    itens: List[OrdemServicoItemSchema] = []
    historico: List[OrdemServicoHistoricoSchema] = []

    class Config:
        orm_mode = True
