"""
Modelo SQLAlchemy: Ordem de Serviço (OrdemServico)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.models.base import Base
import enum

class OrdemServicoFase(enum.Enum):
    CRIACAO = "criação"
    PLANEJAMENTO = "planejamento"
    EXECUCAO = "execução"
    QUALIDADE = "qualidade"
    ENTREGA = "entrega"
    FATURAMENTO = "faturamento"
    POS_VENDA = "pós-venda"

class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    descricao = Column(Text, nullable=True)
    fase = Column(Enum(OrdemServicoFase), default=OrdemServicoFase.CRIACAO, nullable=False)
    status = Column(String(20), default="aberta", nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_previsao = Column(DateTime, nullable=True)
    data_conclusao = Column(DateTime, nullable=True)
    valor_total = Column(Float, default=0.0)
    observacoes = Column(Text, nullable=True)

    cliente = relationship("Cliente", back_populates="ordens_servico")
    responsavel = relationship("Usuario")
    historico = relationship("OrdemServicoHistorico", back_populates="ordem_servico", cascade="all, delete-orphan")
    itens = relationship("OrdemServicoItem", back_populates="ordem_servico", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<OrdemServico #{self.numero} - {self.fase.value}>"

# Histórico de fases/mudanças
class OrdemServicoHistorico(Base):
    __tablename__ = "ordens_servico_historico"
    id = Column(Integer, primary_key=True)
    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id"))
    data = Column(DateTime, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    fase = Column(Enum(OrdemServicoFase))
    status = Column(String(20))
    observacao = Column(Text)

    ordem_servico = relationship("OrdemServico", back_populates="historico")
    usuario = relationship("Usuario")

# Itens/serviços vinculados à OS
class OrdemServicoItem(Base):
    __tablename__ = "ordens_servico_itens"
    id = Column(Integer, primary_key=True)
    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Float, default=1)
    valor_unitario = Column(Float, default=0.0)
    valor_total = Column(Float, default=0.0)
    descricao = Column(Text)

    ordem_servico = relationship("OrdemServico", back_populates="itens")
    produto = relationship("Produto")
