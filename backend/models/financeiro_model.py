#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODELO FINANCEIRO - SISTEMA ERP PRIMOTEX
========================================

Modelos SQLAlchemy para o módulo financeiro básico
incluindo contas a receber, pagar e fluxo de caixa.

Criado em: 29/10/2025
Autor: GitHub Copilot
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.config import Base


class ContaReceber(Base):
    """
    Modelo para Contas a Receber
    
    Controla os valores a receber de clientes,
    principalmente originados de Ordens de Serviço.
    """
    __tablename__ = "contas_receber"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamentos
    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Dados básicos
    numero_documento = Column(String(50), unique=True, nullable=False, index=True)
    descricao = Column(String(200), nullable=False)
    observacoes = Column(Text)
    
    # Valores financeiros
    valor_original = Column(DECIMAL(10, 2), nullable=False)
    valor_desconto = Column(DECIMAL(10, 2), default=0.00)
    valor_juros = Column(DECIMAL(10, 2), default=0.00)
    valor_multa = Column(DECIMAL(10, 2), default=0.00)
    valor_final = Column(DECIMAL(10, 2), nullable=False)
    valor_pago = Column(DECIMAL(10, 2), default=0.00)
    valor_saldo = Column(DECIMAL(10, 2), nullable=False)
    
    # Datas importantes
    data_emissao = Column(DateTime(timezone=True), server_default=func.now())
    data_vencimento = Column(DateTime(timezone=True), nullable=False)
    data_pagamento = Column(DateTime(timezone=True))
    dias_atraso = Column(Integer, default=0)
    
    # Status e controle
    status = Column(String(30), default="Pendente")  # Pendente, Pago, Vencido, Cancelado, Renegociado
    situacao = Column(String(30), default="Normal")  # Normal, Vencido, Negociação, Jurídico
    ativo = Column(Boolean, default=True, nullable=False)  # Campo para soft delete
    
    # Formas de pagamento
    forma_pagamento_prevista = Column(String(50))  # Dinheiro, PIX, Cartão, Boleto
    forma_pagamento_realizada = Column(String(50))
    numero_parcela = Column(Integer, default=1)
    total_parcelas = Column(Integer, default=1)
    
    # Dados do pagamento
    data_ultimo_pagamento = Column(DateTime(timezone=True))
    valor_ultimo_pagamento = Column(DECIMAL(10, 2), default=0.00)
    comprovante_pagamento = Column(String(500))  # Caminho do arquivo
    
    # Controle de cobrança
    tentativas_cobranca = Column(Integer, default=0)
    data_ultima_cobranca = Column(DateTime(timezone=True))
    proxima_cobranca = Column(DateTime(timezone=True))
    
    # Responsáveis
    usuario_criacao = Column(String(100), nullable=False)
    usuario_baixa = Column(String(100))
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    ordem_servico = relationship("OrdemServico", back_populates="contas_receber")
    cliente = relationship("Cliente", back_populates="contas_receber")
    movimentacoes = relationship("MovimentacaoFinanceira", back_populates="conta_receber", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ContaReceber(numero='{self.numero_documento}', valor={self.valor_final}, status='{self.status}')>"


class ContaPagar(Base):
    """
    Modelo para Contas a Pagar
    
    Controla os valores a pagar para fornecedores,
    funcionários e outros credores.
    """
    __tablename__ = "contas_pagar"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamentos
    fornecedor_id = Column(Integer, nullable=True)  # ForeignKey("fornecedores.id") - Tabela ainda não criada
    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id"), nullable=True)
    
    # Dados básicos
    numero_documento = Column(String(50), unique=True, nullable=False, index=True)
    tipo_conta = Column(String(50), nullable=False)  # Fornecedor, Funcionário, Imposto, Aluguel, etc.
    descricao = Column(String(200), nullable=False)
    observacoes = Column(Text)
    
    # Classificação
    categoria = Column(String(50), nullable=False)  # Material, Mão de Obra, Administrativo, etc.
    centro_custo = Column(String(50))
    projeto = Column(String(100))  # Para associar a projetos específicos
    
    # Valores financeiros
    valor_original = Column(DECIMAL(10, 2), nullable=False)
    valor_desconto = Column(DECIMAL(10, 2), default=0.00)
    valor_juros = Column(DECIMAL(10, 2), default=0.00)
    valor_multa = Column(DECIMAL(10, 2), default=0.00)
    valor_final = Column(DECIMAL(10, 2), nullable=False)
    valor_pago = Column(DECIMAL(10, 2), default=0.00)
    valor_saldo = Column(DECIMAL(10, 2), nullable=False)
    
    # Datas importantes
    data_emissao = Column(DateTime(timezone=True), server_default=func.now())
    data_vencimento = Column(DateTime(timezone=True), nullable=False)
    data_pagamento = Column(DateTime(timezone=True))
    dias_atraso = Column(Integer, default=0)
    
    # Status e controle
    status = Column(String(30), default="Pendente")  # Pendente, Pago, Vencido, Cancelado, Renegociado
    prioridade = Column(String(20), default="Normal")  # Baixa, Normal, Alta, Urgente
    ativo = Column(Boolean, default=True, nullable=False)  # Campo para soft delete
    
    # Formas de pagamento
    forma_pagamento_prevista = Column(String(50))  # Dinheiro, PIX, Transferência, Cheque
    forma_pagamento_realizada = Column(String(50))
    numero_parcela = Column(Integer, default=1)
    total_parcelas = Column(Integer, default=1)
    
    # Dados do pagamento
    data_ultimo_pagamento = Column(DateTime(timezone=True))
    valor_ultimo_pagamento = Column(DECIMAL(10, 2), default=0.00)
    comprovante_pagamento = Column(String(500))  # Caminho do arquivo
    
    # Dados do fornecedor (quando não cadastrado)
    nome_favorecido = Column(String(150))
    cpf_cnpj_favorecido = Column(String(18))
    dados_bancarios = Column(JSON)  # Banco, agência, conta
    
    # Aprovação
    aprovado = Column(Boolean, default=False)
    data_aprovacao = Column(DateTime(timezone=True))
    aprovado_por = Column(String(100))
    
    # Responsáveis
    usuario_criacao = Column(String(100), nullable=False)
    usuario_pagamento = Column(String(100))
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    movimentacoes = relationship("MovimentacaoFinanceira", back_populates="conta_pagar", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ContaPagar(numero='{self.numero_documento}', valor={self.valor_final}, status='{self.status}')>"


class MovimentacaoFinanceira(Base):
    """
    Modelo para Movimentações Financeiras
    
    Registra todas as movimentações de entrada e saída
    do caixa da empresa.
    """
    __tablename__ = "movimentacoes_financeiras"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamentos opcionais
    conta_receber_id = Column(Integer, ForeignKey("contas_receber.id"), nullable=True)
    conta_pagar_id = Column(Integer, ForeignKey("contas_pagar.id"), nullable=True)
    
    # Dados básicos
    numero_movimento = Column(String(50), unique=True, nullable=False, index=True)
    tipo_movimentacao = Column(String(20), nullable=False)  # Entrada, Saída
    categoria_movimentacao = Column(String(50), nullable=False)
    
    # Descrição
    descricao = Column(String(200), nullable=False)
    observacoes = Column(Text)
    historico = Column(Text)
    
    # Valores
    valor = Column(DECIMAL(10, 2), nullable=False)
    
    # Datas
    data_movimentacao = Column(DateTime(timezone=True), nullable=False)
    data_competencia = Column(DateTime(timezone=True))
    
    # Forma de pagamento
    forma_pagamento = Column(String(50), nullable=False)
    conta_bancaria = Column(String(100))  # Conta que recebeu/pagou
    
    # Dados complementares
    documento_origem = Column(String(100))  # Número do documento que originou
    pessoa_relacionada = Column(String(150))  # Cliente ou fornecedor
    cpf_cnpj_relacionado = Column(String(18))
    
    # Comprovantes
    comprovante = Column(String(500))  # Caminho do arquivo
    nota_fiscal = Column(String(500))  # Caminho da NF
    
    # Conciliação bancária
    conciliado = Column(Boolean, default=False)
    data_conciliacao = Column(DateTime(timezone=True))
    
    # Responsável
    usuario_responsavel = Column(String(100), nullable=False)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    conta_receber = relationship("ContaReceber", back_populates="movimentacoes")
    conta_pagar = relationship("ContaPagar", back_populates="movimentacoes")
    
    def __repr__(self):
        return f"<MovimentacaoFinanceira(numero='{self.numero_movimento}', tipo='{self.tipo_movimentacao}', valor={self.valor})>"


class FluxoCaixa(Base):
    """
    Modelo para controle do Fluxo de Caixa
    
    Mantém o saldo consolidado por período e
    projeções de entradas e saídas.
    """
    __tablename__ = "fluxo_caixa"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Período de referência
    data_referencia = Column(DateTime(timezone=True), nullable=False, unique=True)
    periodo_tipo = Column(String(20), default="Diário")  # Diário, Semanal, Mensal
    
    # Saldos
    saldo_inicial = Column(DECIMAL(10, 2), default=0.00)
    saldo_final = Column(DECIMAL(10, 2), default=0.00)
    
    # Entradas
    entradas_realizadas = Column(DECIMAL(10, 2), default=0.00)
    entradas_previstas = Column(DECIMAL(10, 2), default=0.00)
    entradas_total = Column(DECIMAL(10, 2), default=0.00)
    
    # Saídas
    saidas_realizadas = Column(DECIMAL(10, 2), default=0.00)
    saidas_previstas = Column(DECIMAL(10, 2), default=0.00)
    saidas_total = Column(DECIMAL(10, 2), default=0.00)
    
    # Resultado
    resultado_realizado = Column(DECIMAL(10, 2), default=0.00)
    resultado_previsto = Column(DECIMAL(10, 2), default=0.00)
    
    # Detalhamento por categoria
    detalhamento_entradas = Column(JSON)  # Breakdown por categoria
    detalhamento_saidas = Column(JSON)  # Breakdown por categoria
    
    # Status
    fechado = Column(Boolean, default=False)
    data_fechamento = Column(DateTime(timezone=True))
    
    # Observações
    observacoes = Column(Text)
    
    # Responsável
    usuario_responsavel = Column(String(100))
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<FluxoCaixa(data='{self.data_referencia}', saldo_final={self.saldo_final})>"


class CategoriaFinanceira(Base):
    """
    Modelo para Categorias Financeiras
    
    Define as categorias para classificação das
    receitas e despesas da empresa.
    """
    __tablename__ = "categorias_financeiras"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Dados básicos
    nome = Column(String(100), unique=True, nullable=False)
    descricao = Column(Text)
    tipo = Column(String(20), nullable=False)  # Receita, Despesa
    
    # Hierarquia
    categoria_pai_id = Column(Integer, ForeignKey("categorias_financeiras.id"), nullable=True)
    nivel = Column(Integer, default=1)
    caminho = Column(String(500))  # Path completo da categoria
    
    # Configurações
    ativo = Column(Boolean, default=True)
    cor = Column(String(7), default="#3498db")  # Cor hexadecimal
    icone = Column(String(50))  # Nome do ícone
    
    # Meta financeira
    meta_mensal = Column(DECIMAL(10, 2))
    meta_anual = Column(DECIMAL(10, 2))
    
    # Observações
    observacoes = Column(Text)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    categoria_pai = relationship("CategoriaFinanceira", remote_side=[id])
    subcategorias = relationship("CategoriaFinanceira")
    
    def __repr__(self):
        return f"<CategoriaFinanceira(nome='{self.nome}', tipo='{self.tipo}')>"


# Constantes para status das contas
STATUS_CONTA = [
    "Pendente",
    "Pago",
    "Vencido",
    "Cancelado",
    "Renegociado",
    "Parcelado"
]

# Formas de pagamento
FORMAS_PAGAMENTO = [
    "Dinheiro",
    "PIX",
    "Transferência Bancária",
    "Cartão Débito",
    "Cartão Crédito",
    "Boleto Bancário",
    "Cheque",
    "Débito Automático",
    "Outros"
]

# Tipos de conta a pagar
TIPOS_CONTA_PAGAR = [
    "Fornecedor",
    "Funcionário",
    "Imposto",
    "Aluguel",
    "Financiamento",
    "Energia Elétrica",
    "Telefonia",
    "Internet",
    "Combustível",
    "Manutenção",
    "Seguro",
    "Outros"
]

# Categorias financeiras padrão
CATEGORIAS_RECEITA = [
    "Vendas de Serviços",
    "Produtos",
    "Comissões",
    "Rendimentos",
    "Outras Receitas"
]

CATEGORIAS_DESPESA = [
    "Materiais",
    "Mão de Obra",
    "Administrativo",
    "Vendas e Marketing",
    "Impostos",
    "Financeiras",
    "Outras Despesas"
]

# Prioridades de pagamento
PRIORIDADES_PAGAMENTO = [
    "Baixa",
    "Normal", 
    "Alta",
    "Urgente"
]

# Tipos de movimentação
TIPOS_MOVIMENTACAO = [
    "Entrada",
    "Saída"
]

# Situações das contas
SITUACOES_CONTA = [
    "Normal",
    "Vencido",
    "Em Negociação",
    "Jurídico",
    "Perdas"
]