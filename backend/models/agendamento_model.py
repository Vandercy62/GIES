#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODELO AGENDAMENTO - SISTEMA ERP PRIMOTEX
=========================================

Modelos SQLAlchemy para o sistema de agendamento integrado
com controle de calendário, eventos e lembretes.

Criado em: 29/10/2025
Autor: GitHub Copilot
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.config import Base


class Agendamento(Base):
    """
    Modelo principal para agendamentos
    
    Controla todos os tipos de eventos agendados no sistema,
    incluindo visitas técnicas, execuções e reuniões.
    """
    __tablename__ = "agendamentos"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamentos opcionais
    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    
    # Dados básicos do evento
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text)
    tipo_evento = Column(String(50), nullable=False)  # Visita, Execução, Reunião, etc.
    categoria = Column(String(50), default="Trabalho")  # Trabalho, Pessoal, Administrativo
    
    # Data e horário
    data_inicio = Column(DateTime(timezone=True), nullable=False)
    data_fim = Column(DateTime(timezone=True), nullable=False)
    dia_inteiro = Column(Boolean, default=False)
    fuso_horario = Column(String(50), default="America/Sao_Paulo")
    
    # Local do evento
    local = Column(String(200))
    endereco_completo = Column(Text)
    coordenadas_gps = Column(String(100))  # lat,lng
    
    # Participantes e responsáveis
    organizador = Column(String(100), nullable=False)
    participantes = Column(JSON)  # Lista de participantes
    participantes_obrigatorios = Column(JSON)  # Lista de participantes obrigatórios
    participantes_opcionais = Column(JSON)  # Lista de participantes opcionais
    
    # Status e controle
    status = Column(String(30), default="Agendado")  # Agendado, Confirmado, Em Andamento, Concluído, Cancelado
    confirmado = Column(Boolean, default=False)
    data_confirmacao = Column(DateTime(timezone=True))
    
    # Recorrência
    recorrente = Column(Boolean, default=False)
    tipo_recorrencia = Column(String(20))  # Diária, Semanal, Mensal, Anual
    intervalo_recorrencia = Column(Integer, default=1)
    dias_semana = Column(JSON)  # Para recorrência semanal
    data_fim_recorrencia = Column(DateTime(timezone=True))
    
    # Lembretes
    lembrete_configurado = Column(Boolean, default=True)
    lembretes_minutos = Column(JSON, default=[15, 60])  # Lista de minutos antes
    lembrete_email = Column(Boolean, default=True)
    lembrete_sistema = Column(Boolean, default=True)
    
    # Prioridade e visibilidade
    prioridade = Column(String(20), default="Normal")  # Baixa, Normal, Alta, Urgente
    privado = Column(Boolean, default=False)
    visivel_para = Column(JSON)  # Lista de usuários que podem ver
    
    # Observações e anexos
    observacoes = Column(Text)
    observacoes_internas = Column(Text)
    anexos = Column(JSON)  # Lista de arquivos anexados
    
    # Integração com sistemas externos
    url_reuniao_online = Column(String(500))  # Link para Google Meet, Teams, etc.
    id_evento_externo = Column(String(100))  # ID no Google Calendar, Outlook, etc.
    sincronizado = Column(Boolean, default=False)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=False)
    
    # Relacionamentos
    ordem_servico = relationship("OrdemServico", back_populates="agendamentos")
    cliente = relationship("Cliente", back_populates="agendamentos")
    
    def __repr__(self):
        return f"<Agendamento(titulo='{self.titulo}', data_inicio='{self.data_inicio}', status='{self.status}')>"


class ConfiguracaoAgenda(Base):
    """
    Modelo para configurações personalizadas de agenda
    
    Permite que cada usuário tenha suas próprias configurações
    de visualização e comportamento da agenda.
    """
    __tablename__ = "configuracoes_agenda"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Usuário proprietário
    usuario = Column(String(100), unique=True, nullable=False)
    
    # Configurações de visualização
    visualizacao_padrao = Column(String(20), default="semana")  # dia, semana, mes, ano
    horario_inicio = Column(Integer, default=8)  # Hora de início do dia (0-23)
    horario_fim = Column(Integer, default=18)  # Hora de fim do dia (0-23)
    mostrar_fins_semana = Column(Boolean, default=True)
    mostrar_feriados = Column(Boolean, default=True)
    
    # Configurações de cores
    cores_categorias = Column(JSON)  # Mapeamento categoria -> cor
    cor_padrao = Column(String(7), default="#3498db")  # Cor hexadecimal
    
    # Configurações de notificações
    notificacoes_email = Column(Boolean, default=True)
    notificacoes_sistema = Column(Boolean, default=True)
    notificacoes_sons = Column(Boolean, default=False)
    lembrete_padrao = Column(Integer, default=15)  # Minutos antes
    
    # Configurações de integração
    sincronizar_google = Column(Boolean, default=False)
    sincronizar_outlook = Column(Boolean, default=False)
    fuso_horario = Column(String(50), default="America/Sao_Paulo")
    
    # Configurações de privacidade
    agenda_publica = Column(Boolean, default=False)
    compartilhar_disponibilidade = Column(Boolean, default=True)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ConfiguracaoAgenda(usuario='{self.usuario}', visualizacao='{self.visualizacao_padrao}')>"


class DisponibilidadeUsuario(Base):
    """
    Modelo para controle de disponibilidade dos usuários
    
    Define horários e dias em que cada usuário está disponível
    para agendamentos automáticos.
    """
    __tablename__ = "disponibilidade_usuarios"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Usuário
    usuario = Column(String(100), nullable=False)
    
    # Configuração semanal
    dia_semana = Column(Integer, nullable=False)  # 0=Segunda, 6=Domingo
    horario_inicio = Column(Integer, nullable=False)  # Hora (0-23)
    minuto_inicio = Column(Integer, default=0)  # Minuto (0-59)
    horario_fim = Column(Integer, nullable=False)  # Hora (0-23)
    minuto_fim = Column(Integer, default=0)  # Minuto (0-59)
    
    # Status
    ativo = Column(Boolean, default=True)
    disponivel = Column(Boolean, default=True)
    
    # Configurações especiais
    intervalo_almoco_inicio = Column(Integer)  # Hora do almoço
    intervalo_almoco_fim = Column(Integer)
    tempo_minimo_agendamento = Column(Integer, default=30)  # Minutos
    
    # Observações
    observacoes = Column(String(200))
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<DisponibilidadeUsuario(usuario='{self.usuario}', dia={self.dia_semana}, inicio={self.horario_inicio}:{self.minuto_inicio:02d})>"


class BloqueioAgenda(Base):
    """
    Modelo para bloqueios temporários na agenda
    
    Permite bloquear períodos específicos para feriados,
    férias, viagens ou outros compromissos pessoais.
    """
    __tablename__ = "bloqueios_agenda"
    
    # Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Usuário afetado
    usuario = Column(String(100), nullable=False)
    
    # Período do bloqueio
    data_inicio = Column(DateTime(timezone=True), nullable=False)
    data_fim = Column(DateTime(timezone=True), nullable=False)
    dia_inteiro = Column(Boolean, default=True)
    
    # Dados do bloqueio
    titulo = Column(String(200), nullable=False)
    tipo_bloqueio = Column(String(50), nullable=False)  # Férias, Feriado, Viagem, Compromisso
    descricao = Column(Text)
    
    # Recorrência (para feriados anuais)
    recorrente = Column(Boolean, default=False)
    recorrer_anualmente = Column(Boolean, default=False)
    
    # Status
    ativo = Column(Boolean, default=True)
    aprovado = Column(Boolean, default=True)
    aprovado_por = Column(String(100))
    data_aprovacao = Column(DateTime(timezone=True))
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=False)
    
    def __repr__(self):
        return f"<BloqueioAgenda(usuario='{self.usuario}', titulo='{self.titulo}', tipo='{self.tipo_bloqueio}')>"


# Constantes para tipos de evento
TIPOS_EVENTO = [
    "Visita Técnica",
    "Execução de Serviço",
    "Reunião Cliente",
    "Reunião Interna",
    "Apresentação Orçamento",
    "Vistoria Final",
    "Entrega de Projeto",
    "Manutenção",
    "Treinamento",
    "Administrativo",
    "Pessoal",
    "Outros"
]

# Status de agendamento
STATUS_AGENDAMENTO = [
    "Agendado",
    "Confirmado",
    "Em Andamento",
    "Concluído",
    "Cancelado",
    "Reagendado",
    "Não Compareceu"
]

# Tipos de recorrência
TIPOS_RECORRENCIA = [
    "Diária",
    "Semanal", 
    "Quinzenal",
    "Mensal",
    "Bimestral",
    "Trimestral",
    "Semestral",
    "Anual"
]

# Prioridades
PRIORIDADES = [
    "Baixa",
    "Normal",
    "Alta", 
    "Urgente"
]

# Categorias de evento
CATEGORIAS_EVENTO = [
    "Trabalho",
    "Cliente",
    "Administrativo",
    "Pessoal",
    "Manutenção",
    "Comercial",
    "Financeiro"
]

# Tipos de bloqueio
TIPOS_BLOQUEIO = [
    "Férias",
    "Feriado",
    "Licença",
    "Viagem",
    "Compromisso Pessoal",
    "Treinamento",
    "Reunião Externa",
    "Manutenção Sistema",
    "Outros"
]

# Dias da semana
DIAS_SEMANA = {
    0: "Segunda-feira",
    1: "Terça-feira", 
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo"
}

# Configurações de lembrete padrão
LEMBRETES_PADRAO = [
    {"minutos": 15, "descricao": "15 minutos antes"},
    {"minutos": 30, "descricao": "30 minutos antes"},
    {"minutos": 60, "descricao": "1 hora antes"},
    {"minutos": 120, "descricao": "2 horas antes"},
    {"minutos": 1440, "descricao": "1 dia antes"},
    {"minutos": 2880, "descricao": "2 dias antes"}
]