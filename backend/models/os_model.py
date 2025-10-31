"""
SISTEMA ERP PRIMOTEX - MODELO DE ORDEM DE SERVIÇO (OS)
======================================================

Este arquivo define a estrutura das tabelas relacionadas à Ordem de Serviço.
Este é o CORAÇÃO DO SISTEMA, onde acontece todo o fluxo operacional.

FLUXO DA OS (7 FASES):
1. Abertura da OS
2. Ficha de Visita Técnica  
3. Orçamento
4. Envio e Acompanhamento
5. Execução
6. Finalização
7. Arquivo

TABELAS RELACIONADAS:
- ordem_servico: Dados principais da OS
- os_itens: Itens (produtos/serviços) do orçamento
- os_historico: Histórico de mudanças de status

Autor: GitHub Copilot
Data: 29/10/2025
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Date
from sqlalchemy.sql import func
from backend.database.config import Base

class OrdemServico(Base):
    """
    Modelo principal da Ordem de Serviço.
    
    Armazena todas as informações principais da OS,
    desde a abertura até a finalização.
    """
    
    # Nome da tabela no banco de dados
    __tablename__ = "ordem_servico"
    
    # =======================================
    # IDENTIFICAÇÃO DA OS
    # =======================================
    
    # Chave primária
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="ID único da OS"
    )
    
    # Número da OS (sequencial)
    numero_os = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Número sequencial da OS: OS00001, OS00002, etc."
    )
    
    # Cliente da OS
    cliente_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="ID do cliente (FK para tabela clientes)"
    )
    
    # =======================================
    # FASE 1 - ABERTURA DA OS
    # =======================================
    
    # Data/hora de abertura
    data_abertura = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Data e hora de abertura da OS"
    )
    
    # Usuário que abriu a OS
    usuario_abertura_id = Column(
        Integer,
        nullable=False,
        comment="ID do usuário que abriu a OS"
    )
    
    # Tipo de solicitação
    tipo_solicitacao = Column(
        String(50),
        nullable=False,
        comment="Tipo: Instalação, Manutenção, Venda, Orçamento, etc."
    )
    
    # Prioridade
    prioridade = Column(
        String(20),
        nullable=False,
        default="Normal",
        comment="Prioridade: Baixa, Normal, Alta, Urgente"
    )
    
    # Observações iniciais
    observacoes_iniciais = Column(
        Text,
        comment="Observações na abertura da OS"
    )
    
    # =======================================
    # FASE 2 - VISITA TÉCNICA
    # =======================================
    
    # Data agendada para visita
    data_visita_agendada = Column(
        DateTime(timezone=True),
        comment="Data e hora agendadas para visita técnica"
    )
    
    # Data efetiva da visita
    data_visita_realizada = Column(
        DateTime(timezone=True),
        comment="Data e hora em que a visita foi realizada"
    )
    
    # Técnico responsável pela visita
    tecnico_visita_id = Column(
        Integer,
        comment="ID do colaborador/técnico que fez a visita"
    )
    
    # Endereço da visita (pode ser diferente do cadastro)
    endereco_visita = Column(
        Text,
        comment="Endereço completo onde será feita a visita"
    )
    
    # Medidas e observações técnicas
    medidas_observacoes = Column(
        Text,
        comment="Medidas tomadas e observações técnicas da visita"
    )
    
    # Caminho para arquivo de croqui/desenho
    croqui_path = Column(
        String(255),
        comment="Caminho para arquivo do croqui digitalizado"
    )
    
    # Fotos do local (JSON)
    fotos_visita_paths = Column(
        Text,
        comment="JSON com caminhos das fotos tiradas na visita"
    )
    
    # =======================================
    # FASE 3 - ORÇAMENTO
    # =======================================
    
    # Data de geração do orçamento
    data_orcamento = Column(
        DateTime(timezone=True),
        comment="Data de geração do orçamento"
    )
    
    # Usuário que gerou o orçamento
    usuario_orcamento_id = Column(
        Integer,
        comment="ID do usuário que gerou o orçamento"
    )
    
    # Tipo de proposta/documento
    tipo_proposta = Column(
        String(50),
        comment="Tipo: Básica, Executiva, Pública, Licitação, etc."
    )
    
    # Valores do orçamento
    subtotal_materiais = Column(
        Numeric(10, 2),
        default=0.00,
        comment="Subtotal dos materiais"
    )
    
    subtotal_servicos = Column(
        Numeric(10, 2),
        default=0.00,
        comment="Subtotal dos serviços"
    )
    
    subtotal_geral = Column(
        Numeric(10, 2),
        default=0.00,
        comment="Subtotal geral (materiais + serviços)"
    )
    
    desconto_percentual = Column(
        Numeric(5, 2),
        default=0.00,
        comment="Desconto em percentual"
    )
    
    desconto_valor = Column(
        Numeric(10, 2),
        default=0.00,
        comment="Desconto em valor"
    )
    
    valor_total = Column(
        Numeric(10, 2),
        default=0.00,
        comment="Valor total final do orçamento"
    )
    
    # Condições de pagamento
    condicoes_pagamento = Column(
        Text,
        comment="Condições de pagamento (à vista, parcelado, etc.)"
    )
    
    # Prazo de execução
    prazo_execucao_dias = Column(
        Integer,
        comment="Prazo de execução em dias úteis"
    )
    
    # Validade do orçamento
    validade_orcamento_dias = Column(
        Integer,
        default=15,
        comment="Validade do orçamento em dias"
    )
    
    # =======================================
    # FASE 4 - ENVIO E ACOMPANHAMENTO
    # =======================================
    
    # Data de envio do orçamento
    data_envio_orcamento = Column(
        DateTime(timezone=True),
        comment="Data de envio do orçamento ao cliente"
    )
    
    # Forma de envio
    forma_envio = Column(
        String(50),
        comment="Como foi enviado: Email, WhatsApp, Físico, Online"
    )
    
    # Data de resposta do cliente
    data_resposta_cliente = Column(
        DateTime(timezone=True),
        comment="Data da resposta do cliente"
    )
    
    # Resposta do cliente
    resposta_cliente = Column(
        String(50),
        comment="Resposta: Aprovado, Reprovado, Negociação, Alteração"
    )
    
    # Observações sobre negociação
    observacoes_negociacao = Column(
        Text,
        comment="Observações sobre negociações com o cliente"
    )
    
    # =======================================
    # FASE 5 - EXECUÇÃO
    # =======================================
    
    # Data de início da execução
    data_inicio_execucao = Column(
        DateTime(timezone=True),
        comment="Data de início da execução do serviço"
    )
    
    # Data prevista de término
    data_previsao_termino = Column(
        DateTime(timezone=True),
        comment="Data prevista para término"
    )
    
    # Equipe responsável (JSON)
    equipe_execucao = Column(
        Text,
        comment="JSON com IDs dos colaboradores na execução"
    )
    
    # Responsável principal pela execução
    responsavel_execucao_id = Column(
        Integer,
        comment="ID do colaborador responsável principal"
    )
    
    # Registro de horas trabalhadas
    horas_trabalhadas = Column(
        Numeric(6, 2),
        default=0.00,
        comment="Total de horas trabalhadas"
    )
    
    # Observações da execução
    observacoes_execucao = Column(
        Text,
        comment="Observações durante a execução"
    )
    
    # Fotos do andamento (JSON)
    fotos_execucao_paths = Column(
        Text,
        comment="JSON com fotos do andamento da execução"
    )
    
    # =======================================
    # FASE 6 - FINALIZAÇÃO
    # =======================================
    
    # Data de conclusão
    data_conclusao = Column(
        DateTime(timezone=True),
        comment="Data de conclusão do serviço"
    )
    
    # Termo de aceite (caminho do arquivo)
    termo_aceite_path = Column(
        String(255),
        comment="Caminho para arquivo do termo de aceite assinado"
    )
    
    # Fotos do trabalho finalizado (JSON)
    fotos_finalizacao_paths = Column(
        Text,
        comment="JSON com fotos do trabalho concluído"
    )
    
    # Avaliação do cliente
    avaliacao_cliente = Column(
        Integer,
        comment="Avaliação do cliente de 1 a 5"
    )
    
    # Comentários da avaliação
    comentarios_avaliacao = Column(
        Text,
        comment="Comentários do cliente na avaliação"
    )
    
    # =======================================
    # CONTROLE DE STATUS
    # =======================================
    
    # Status atual da OS
    status = Column(
        String(50),
        nullable=False,
        default="AGUARDANDO VISITA TÉCNICA",
        index=True,
        comment="Status atual da OS"
    )
    
    # Data da última mudança de status
    data_ultimo_status = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Data da última mudança de status"
    )
    
    # Usuário da última mudança
    usuario_ultimo_status_id = Column(
        Integer,
        comment="ID do usuário que fez a última mudança"
    )
    
    # =======================================
    # CAMPOS DE CONTROLE
    # =======================================
    
    # Data de atualização
    data_atualizacao = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Data da última atualização"
    )
    
    # Observações gerais
    observacoes_gerais = Column(
        Text,
        comment="Observações gerais sobre a OS"
    )
    
    # Motivo de cancelamento (se aplicável)
    motivo_cancelamento = Column(
        Text,
        comment="Motivo do cancelamento (se status = CANCELADO)"
    )
    
    # =======================================
    # MÉTODOS DA CLASSE
    # =======================================
    
    def __repr__(self):
        """Representação do objeto"""
        return f"<OrdemServico(id={self.id}, numero='{self.numero_os}', status='{self.status}')>"
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            "id": self.id,
            "numero_os": self.numero_os,
            "cliente_id": self.cliente_id,
            "status": self.status,
            "tipo_solicitacao": self.tipo_solicitacao,
            "prioridade": self.prioridade,
            
            # Datas importantes
            "data_abertura": self.data_abertura.isoformat() if self.data_abertura else None,
            "data_visita_agendada": self.data_visita_agendada.isoformat() if self.data_visita_agendada else None,
            "data_orcamento": self.data_orcamento.isoformat() if self.data_orcamento else None,
            "data_inicio_execucao": self.data_inicio_execucao.isoformat() if self.data_inicio_execucao else None,
            "data_conclusao": self.data_conclusao.isoformat() if self.data_conclusao else None,
            
            # Valores
            "valor_total": float(self.valor_total) if self.valor_total else 0.00,
            "subtotal_materiais": float(self.subtotal_materiais) if self.subtotal_materiais else 0.00,
            "subtotal_servicos": float(self.subtotal_servicos) if self.subtotal_servicos else 0.00,
            "desconto_valor": float(self.desconto_valor) if self.desconto_valor else 0.00,
            
            # Outros
            "prazo_execucao_dias": self.prazo_execucao_dias,
            "horas_trabalhadas": float(self.horas_trabalhadas) if self.horas_trabalhadas else 0.00,
            "avaliacao_cliente": self.avaliacao_cliente,
            "observacoes_iniciais": self.observacoes_iniciais
        }
    
    def is_status(self, status):
        """Verifica se está em determinado status"""
        return self.status == status
    
    def pode_gerar_orcamento(self):
        """Verifica se pode gerar orçamento"""
        return self.status in ["VISITA REALIZADA", "AGUARDANDO ORÇAMENTO"]
    
    def pode_executar(self):
        """Verifica se pode iniciar execução"""
        return self.status == "APROVADO - AGUARDANDO EXECUÇÃO"

# =======================================
# TABELA DE ITENS DA OS
# =======================================

class OSItem(Base):
    """
    Modelo dos itens (produtos/serviços) da OS.
    
    Cada linha representa um produto ou serviço
    incluído no orçamento da OS.
    """
    
    __tablename__ = "os_itens"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # OS relacionada
    os_id = Column(
        Integer, 
        nullable=False,
        comment="ID da OS (FK para ordem_servico)"
    )
    
    # Produto/serviço
    produto_id = Column(
        Integer, 
        nullable=False,
        comment="ID do produto/serviço (FK para produtos)"
    )
    
    # Quantidade
    quantidade = Column(
        Numeric(10, 4),
        nullable=False,
        comment="Quantidade do item"
    )
    
    # Valor unitário (pode ser diferente do cadastro)
    valor_unitario = Column(
        Numeric(10, 4),
        nullable=False,
        comment="Valor unitário específico para esta OS"
    )
    
    # Subtotal do item
    subtotal = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Subtotal (quantidade × valor_unitário)"
    )
    
    # Observações específicas do item
    observacoes = Column(
        Text,
        comment="Observações específicas deste item na OS"
    )
    
    def __repr__(self):
        return f"<OSItem(os_id={self.os_id}, produto_id={self.produto_id}, qtd={self.quantidade})>"

# =======================================
# TABELA DE HISTÓRICO DE STATUS
# =======================================

class OSHistorico(Base):
    """
    Modelo do histórico de mudanças de status da OS.
    
    Registra todas as mudanças de status com
    data, hora, usuário e observações.
    """
    
    __tablename__ = "os_historico"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # OS relacionada
    os_id = Column(
        Integer, 
        nullable=False,
        comment="ID da OS (FK para ordem_servico)"
    )
    
    # Status anterior
    status_anterior = Column(
        String(50),
        comment="Status antes da mudança"
    )
    
    # Status novo
    status_novo = Column(
        String(50),
        nullable=False,
        comment="Novo status"
    )
    
    # Data da mudança
    data_mudanca = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Data e hora da mudança"
    )
    
    # Usuário responsável
    usuario_id = Column(
        Integer,
        nullable=False,
        comment="ID do usuário que fez a mudança"
    )
    
    # Observações sobre a mudança
    observacoes = Column(
        Text,
        comment="Observações sobre a mudança de status"
    )

# =======================================
# STATUS POSSÍVEIS DA OS
# =======================================

STATUS_OS = [
    "AGUARDANDO VISITA TÉCNICA",
    "VISITA REALIZADA",
    "AGUARDANDO ORÇAMENTO", 
    "ORÇAMENTO GERADO",
    "ORÇAMENTO ENVIADO",
    "AGUARDANDO RETORNO DO CLIENTE",
    "EM NEGOCIAÇÃO",
    "EM REVISÃO",
    "APROVADO - AGUARDANDO EXECUÇÃO",
    "EM EXECUÇÃO",
    "CONCLUÍDO",
    "CANCELADO",
    "REPROVADO"
]

TIPOS_SOLICITACAO = [
    "Instalação", "Manutenção", "Venda", "Orçamento",
    "Garantia", "Reparo", "Substituição", "Outros"
]

PRIORIDADES = ["Baixa", "Normal", "Alta", "Urgente"]

TIPOS_PROPOSTA = [
    "Proposta Básica", "Pedido de Materiais", "Pedido de Serviços",
    "Proposta Executiva", "Proposta Pública", "Proposta para Licitação",
    "Contrato de Serviço (com materiais)", "Contrato de Serviço (sem materiais)"
]