#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODELO ORDEM DE SERVIÇO - SISTEMA ERP PRIMOTEX
==============================================

Modelos SQLAlchemy para o sistema de Ordem de Serviço (OS)
incluindo todas as 7 fases do workflow operacional.

Criado em: 29/10/2025
Autor: GitHub Copilot
"""

from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, text
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship
from backend.database.config import Base


# =============================================================================
# CONSTANTES
# =============================================================================

CASCADE_DELETE_ORPHAN = "all, delete-orphan"
ORDENS_SERVICO_ID_FK = "ordens_servico.id"



class OrdemServico(Base):
    """
    Modelo principal da Ordem de Serviço
    
    Representa o documento central que controla todo o workflow
    operacional da Primotex, desde a abertura até o arquivo.
    """
    __tablename__ = "ordens_servico"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Dados básicos
    numero_os = Column(String(20), unique=True, nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Tipo e categoria
    tipo_servico = Column(String(100), nullable=False)  # Forro, Divisória, etc.
    categoria = Column(String(50), nullable=False)  # Residencial, Comercial, Industrial
    prioridade = Column(String(20), default="Normal")  # Baixa, Normal, Alta, Urgente
    
    # Status e controle de fases
    fase_atual = Column(Integer, default=1, nullable=False)  # 1-7 (7 fases) - ALINHADO COM SCHEMA
    status = Column(String(30), default="ABERTA", nullable=False)  # ABERTA, EM_EXECUCAO, FINALIZADA, etc - ALINHADO COM SCHEMA
    
    # Datas importantes
    data_abertura = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    data_prevista_conclusao = Column(DateTime(timezone=True))
    data_conclusao = Column(DateTime(timezone=True))
    prazo_orcamento = Column(DateTime(timezone=True))
    
    # Responsáveis
    usuario_abertura = Column(String(100), nullable=False)
    usuario_responsavel = Column(String(100))
    tecnico_responsavel = Column(String(100))
    
    # Valores financeiros
    valor_orcamento = Column(DECIMAL(10, 2), default=0.00)
    valor_desconto = Column(DECIMAL(10, 2), default=0.00)
    valor_final = Column(DECIMAL(10, 2), default=0.00)
    forma_pagamento = Column(String(50))
    
    # Croqui técnico (NOVO - FASE 104)
    dados_croqui_json = Column(JSON, nullable=True)  # Armazena objetos do canvas
    
    # Orçamento (NOVO - FASE 104 TAREFA 2)
    dados_orcamento_json = Column(JSON, nullable=True)  # Armazena itens do orçamento
    
    # Medições técnicas (NOVO - FASE 104 TAREFA 5)
    dados_medicoes_json = Column(JSON, nullable=True)  # Armazena medições (área, perímetro, linear, qtd)
    
    # Materiais utilizados (NOVO - FASE 104 TAREFA 6)
    dados_materiais_json = Column(JSON, nullable=True)  # Controle de materiais aplicados/devolvidos
    
    # Equipe alocada (NOVO - FASE 104 TAREFA 7)
    dados_equipe_json = Column(JSON, nullable=True)  # Gerenciamento de equipe na OS
    
    # Localização do serviço
    endereco_execucao = Column(Text)  # Pode ser diferente do endereço do cliente
    cidade_execucao = Column(String(100))
    estado_execucao = Column(String(2))
    cep_execucao = Column(String(10))
    
    # Observações e controle
    observacoes_abertura = Column(Text)
    observacoes_internas = Column(Text)
    motivo_cancelamento = Column(Text)
    
    # Controle de qualidade
    avaliacao_cliente = Column(Integer)  # 1-5 estrelas
    comentario_avaliacao = Column(Text)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), onupdate=text('CURRENT_TIMESTAMP'))
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="ordens_servico")
    fases = relationship("FaseOS", back_populates="ordem_servico", cascade=CASCADE_DELETE_ORPHAN)
    visitas_tecnicas = relationship("VisitaTecnica", back_populates="ordem_servico", cascade=CASCADE_DELETE_ORPHAN)
    orcamentos = relationship("Orcamento", back_populates="ordem_servico", cascade=CASCADE_DELETE_ORPHAN)
    agendamentos = relationship("Agendamento", back_populates="ordem_servico", cascade=CASCADE_DELETE_ORPHAN)
    contas_receber = relationship("ContaReceber", back_populates="ordem_servico", cascade=CASCADE_DELETE_ORPHAN)
    
    def __repr__(self):
        return f"<OrdemServico(numero_os='{self.numero_os}', cliente_id={self.cliente_id}, fase_atual={self.fase_atual}, status='{self.status}')>"


class FaseOS(Base):
    """
    Modelo para controle das 7 fases da Ordem de Serviço
    
    Cada OS possui 7 fases obrigatórias que devem ser cumpridas
    sequencialmente para garantir a qualidade do processo.
    """
    __tablename__ = "fases_os"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamento com OS
    ordem_servico_id = Column(Integer, ForeignKey(ORDENS_SERVICO_ID_FK), nullable=False)
    
    # Dados da fase
    numero_fase = Column(Integer, nullable=False)  # 1-7
    nome_fase = Column(String(100), nullable=False)
    descricao_fase = Column(Text)
    
    # Status e controle
    status = Column(String(30), default="Pendente")  # Pendente, Em Andamento, Concluída, Bloqueada
    obrigatoria = Column(Boolean, default=True)
    pode_pular = Column(Boolean, default=False)
    
    # Datas de controle
    data_inicio = Column(DateTime(timezone=True))
    data_prazo = Column(DateTime(timezone=True))
    data_conclusao = Column(DateTime(timezone=True))
    
    # Responsabilidades
    responsavel = Column(String(100))
    aprovador = Column(String(100))
    data_aprovacao = Column(DateTime(timezone=True))
    
    # Checklist e observações
    checklist_itens = Column(JSON)  # Lista de itens do checklist da fase
    observacoes = Column(Text)
    observacoes_internas = Column(Text)
    
    # Anexos e evidências
    anexos = Column(JSON)  # Lista de caminhos dos arquivos anexados
    fotos = Column(JSON)  # Lista de fotos relacionadas à fase
    assinatura_cliente = Column(Text)  # Base64 da assinatura
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), onupdate=text('CURRENT_TIMESTAMP'))
    
    # Relacionamento
    ordem_servico = relationship("OrdemServico", back_populates="fases")
    
    def __repr__(self):
        return f"<FaseOS(ordem_servico_id={self.ordem_servico_id}, numero_fase={self.numero_fase}, status='{self.status}')>"


class VisitaTecnica(Base):
    """
    Modelo para Visitas Técnicas (Fase 2 da OS)
    
    Controla o agendamento, execução e resultados das
    visitas técnicas realizadas nos clientes.
    """
    __tablename__ = "visitas_tecnicas"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamento com OS
    ordem_servico_id = Column(Integer, ForeignKey(ORDENS_SERVICO_ID_FK), nullable=False)
    
    # Dados da visita
    numero_visita = Column(Integer, default=1)  # Pode haver várias visitas por OS
    tipo_visita = Column(String(50), default="Técnica")  # Técnica, Medição, Vistoria
    
    # Agendamento
    data_agendada = Column(DateTime(timezone=True), nullable=False)
    data_realizada = Column(DateTime(timezone=True))
    duracao_prevista = Column(Integer, default=120)  # em minutos
    duracao_real = Column(Integer)
    
    # Responsáveis
    tecnico_responsavel = Column(String(100), nullable=False)
    tecnico_auxiliar = Column(String(100))
    contato_cliente = Column(String(100))
    
    # Local da visita
    endereco_visita = Column(Text, nullable=False)
    referencia_local = Column(String(200))
    observacoes_acesso = Column(Text)
    
    # Resultados técnicos
    medidas_ambiente = Column(JSON)  # Medidas coletadas
    condicoes_ambiente = Column(Text)  # Descrição das condições
    observacoes_tecnicas = Column(Text, nullable=False)
    
    # Avaliação e recomendações
    viabilidade_execucao = Column(String(20), default="Sim")  # Sim, Não, Condicional
    observacoes_viabilidade = Column(Text)
    recomendacoes = Column(Text)
    restricoes_execucao = Column(Text)
    
    # Documentação
    fotos_ambiente = Column(JSON)  # Lista de fotos tiradas
    croqui_medidas = Column(Text)  # Caminho para arquivo de croqui
    materiais_sugeridos = Column(JSON)  # Lista de materiais necessários
    
    # Status e aprovação
    status = Column(String(30), default="Agendada")  # Agendada, Realizada, Cancelada, Reagendada
    assinatura_cliente = Column(Text)  # Base64 da assinatura
    data_assinatura = Column(DateTime(timezone=True))
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), onupdate=text('CURRENT_TIMESTAMP'))
    
    # Relacionamento
    ordem_servico = relationship("OrdemServico", back_populates="visitas_tecnicas")
    
    def __repr__(self):
        return f"<VisitaTecnica(ordem_servico_id={self.ordem_servico_id}, tecnico='{self.tecnico_responsavel}', status='{self.status}')>"


class Orcamento(Base):
    """
    Modelo para Orçamentos (Fase 3 da OS)
    
    Controla a criação, aprovação e versionamento
    dos orçamentos enviados aos clientes.
    """
    __tablename__ = "orcamentos"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamento com OS
    ordem_servico_id = Column(Integer, ForeignKey(ORDENS_SERVICO_ID_FK), nullable=False)
    
    # Dados do orçamento
    numero_orcamento = Column(String(20), unique=True, nullable=False, index=True)
    versao = Column(Integer, default=1)
    tipo_orcamento = Column(String(50), default="Padrão")  # Padrão, Simplificado, Detalhado
    
    # Validade e status
    data_criacao = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    data_envio = Column(DateTime(timezone=True))
    data_validade = Column(DateTime(timezone=True), nullable=False)
    data_aprovacao = Column(DateTime(timezone=True))
    data_rejeicao = Column(DateTime(timezone=True))
    
    # Status de aprovação
    status_aprovacao = Column(String(30), default="Pendente")  # Pendente, Aprovado, Rejeitado, Vencido, Negociação
    motivo_rejeicao = Column(Text)
    observacoes_cliente = Column(Text)
    
    # Estrutura do orçamento
    itens_orcamento = Column(JSON, nullable=False)  # Lista detalhada de itens
    itens_opcionais = Column(JSON)  # Itens opcionais
    observacoes_tecnicas = Column(Text)
    
    # Valores financeiros
    valor_material = Column(DECIMAL(10, 2), default=0.00)
    valor_mao_obra = Column(DECIMAL(10, 2), default=0.00)
    valor_deslocamento = Column(DECIMAL(10, 2), default=0.00)
    valor_subtotal = Column(DECIMAL(10, 2), default=0.00)
    valor_desconto = Column(DECIMAL(10, 2), default=0.00)
    percentual_desconto = Column(DECIMAL(5, 2), default=0.00)
    valor_total = Column(DECIMAL(10, 2), nullable=False)
    
    # Condições comerciais
    prazo_execucao = Column(Integer)  # Prazo em dias
    forma_pagamento = Column(String(100))
    condicoes_especiais = Column(Text)
    garantia_oferecida = Column(String(100))
    
    # Responsável e aprovação
    usuario_criacao = Column(String(100), nullable=False)
    usuario_aprovacao = Column(String(100))
    
    # Arquivos gerados
    arquivo_pdf = Column(String(500))  # Caminho do PDF gerado
    arquivo_detalhado = Column(String(500))  # Planilha detalhada
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), onupdate=text('CURRENT_TIMESTAMP'))
    
    # Relacionamento
    ordem_servico = relationship("OrdemServico", back_populates="orcamentos")
    
    def __repr__(self):
        return f"<Orcamento(numero='{self.numero_orcamento}', valor_total={self.valor_total}, status='{self.status_aprovacao}')>"


# Constantes para as fases da OS
FASES_OS = {
    1: {
        "nome": "Abertura da OS",
        "descricao": "Cadastro inicial da ordem de serviço com dados básicos do cliente e tipo de serviço",
        "checklist": [
            "Dados do cliente validados",
            "Tipo de serviço definido",
            "Prazo estimado estabelecido",
            "Responsável técnico designado"
        ]
    },
    2: {
        "nome": "Visita Técnica",
        "descricao": "Agendamento e execução da visita técnica para avaliação do local",
        "checklist": [
            "Visita agendada com cliente",
            "Medições realizadas",
            "Fotos do ambiente coletadas",
            "Viabilidade técnica avaliada",
            "Assinatura do cliente obtida"
        ]
    },
    3: {
        "nome": "Orçamento",
        "descricao": "Elaboração e envio do orçamento detalhado ao cliente",
        "checklist": [
            "Materiais necessários calculados",
            "Mão de obra estimada",
            "Valor total definido",
            "Prazo de execução estabelecido",
            "Orçamento enviado ao cliente"
        ]
    },
    4: {
        "nome": "Acompanhamento",
        "descricao": "Acompanhamento da aprovação do orçamento pelo cliente",
        "checklist": [
            "Cliente contactado",
            "Dúvidas esclarecidas",
            "Negociações realizadas",
            "Aprovação ou rejeição confirmada"
        ]
    },
    5: {
        "nome": "Execução",
        "descricao": "Programação e execução do serviço aprovado",
        "checklist": [
            "Data de execução agendada",
            "Materiais providenciados",
            "Equipe técnica escalada",
            "Serviço executado conforme especificação",
            "Fotos do progresso documentadas"
        ]
    },
    6: {
        "nome": "Finalização",
        "descricao": "Entrega final do serviço e aprovação do cliente",
        "checklist": [
            "Serviço concluído",
            "Limpeza do local realizada",
            "Vistoria final com cliente",
            "Assinatura de aprovação obtida",
            "Documentação entregue"
        ]
    },
    7: {
        "nome": "Arquivo",
        "descricao": "Arquivo da OS com documentação completa e avaliação",
        "checklist": [
            "Documentação organizada",
            "Avaliação do cliente coletada",
            "Financeiro atualizado",
            "OS arquivada no sistema"
        ]
    }
}

# Status possíveis para as fases
STATUS_FASES = [
    "Pendente",
    "Em Andamento", 
    "Concluída",
    "Bloqueada"
]

# Status gerais da OS
STATUS_OS = [
    "Aberta",
    "Em Andamento",
    "Concluída", 
    "Cancelada",
    "Suspensa"
]

# Tipos de serviço da Primotex
TIPOS_SERVICO = [
    "Forro PVC",
    "Forro Gesso",
    "Forro Mineral",
    "Divisória Drywall",
    "Divisória Eucatex",
    "Divisória Vidro",
    "Projeto Completo",
    "Manutenção",
    "Outros"
]