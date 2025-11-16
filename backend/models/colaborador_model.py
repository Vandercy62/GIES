#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA ERP PRIMOTEX - MODELO DE COLABORADORES
==============================================

Modelo SQLAlchemy para gestão avançada de colaboradores/funcionários.
Estende o sistema básico de usuários com funcionalidades corporativas:

FUNCIONALIDADES PRINCIPAIS:
- Dados pessoais e profissionais completos
- Gestão de cargos, departamentos e hierarquia
- Controle de salários e benefícios
- Jornada de trabalho e ponto eletrônico
- Histórico profissional e avaliações
- Documentos e certificações
- Controle de férias e licenças

RELACIONAMENTOS:
- colaboradores ←→ usuarios (1:1) - Sistema de autenticação
- colaboradores ←→ cargos (N:1) - Função/posição
- colaboradores ←→ departamentos (N:1) - Setor organizacional
- colaboradores ←→ colaborador_documentos (1:N) - Anexos
- colaboradores ←→ historico_profissional (1:N) - Carreira
- colaboradores ←→ avaliacoes (1:N) - Performance
- colaboradores ←→ ponto_eletronico (1:N) - Controle de horário

Autor: GitHub Copilot
Data: 01/11/2025
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Text, 
    DECIMAL, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, remote
from sqlalchemy.sql import func
from datetime import datetime, date
import enum
from backend.database.config import Base


# =======================================
# ENUMS
# =======================================

class TipoContrato(enum.Enum):
    """Tipos de contrato de trabalho"""
    CLT = "CLT"
    PESSOA_JURIDICA = "Pessoa Jurídica" 
    ESTAGIARIO = "Estagiário"
    TERCEIRIZADO = "Terceirizado"
    FREELANCER = "Freelancer"
    TEMPORARIO = "Temporário"


class StatusColaborador(enum.Enum):
    """Status do colaborador"""
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    FERIAS = "FERIAS"
    LICENCA = "LICENCA"
    AFASTADO = "AFASTADO"
    DEMITIDO = "DEMITIDO"


class TipoDocumento(enum.Enum):
    """Tipos de documentos do colaborador"""
    RG = "RG"
    CPF = "CPF"
    CNH = "CNH"
    TITULO_ELEITOR = "Título de Eleitor"
    CARTEIRA_TRABALHO = "Carteira de Trabalho"
    PIS_PASEP = "PIS/PASEP"
    CERTIFICADO = "Certificado"
    DIPLOMA = "Diploma"
    CURSO = "Certificado de Curso"
    CONTRATO = "Contrato"
    EXAME_MEDICO = "Exame Médico"
    COMPROVANTE_RESIDENCIA = "Comprovante de Residência"


class NivelEscolaridade(enum.Enum):
    """Níveis de escolaridade"""
    FUNDAMENTAL_INCOMPLETO = "Fundamental Incompleto"
    FUNDAMENTAL_COMPLETO = "Fundamental Completo"
    MEDIO_INCOMPLETO = "Médio Incompleto"
    MEDIO_COMPLETO = "Médio Completo"
    SUPERIOR_INCOMPLETO = "Superior Incompleto"
    SUPERIOR_COMPLETO = "Superior Completo"
    ESPECIALIZACAO = "Especialização"
    MESTRADO = "Mestrado"
    DOUTORADO = "Doutorado"


# =======================================
# MODELOS AUXILIARES
# =======================================

class Departamento(Base):
    """Modelo para departamentos da empresa"""
    __tablename__ = "departamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text)
    codigo = Column(String(20), unique=True)
    responsavel_id = Column(Integer, ForeignKey("colaboradores.id"))
    centro_custo = Column(String(50))
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=func.now())
    
    # Relacionamentos
    colaboradores = relationship(
        "Colaborador", 
        back_populates="departamento", 
        primaryjoin="Departamento.id == Colaborador.departamento_id"
    )
    responsavel = relationship(
        "Colaborador", 
        primaryjoin="Departamento.responsavel_id == Colaborador.id"
    )
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}" if self.codigo else self.nome


class Cargo(Base):
    """Modelo para cargos/funções"""
    __tablename__ = "cargos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    codigo = Column(String(20), unique=True)
    nivel_hierarquico = Column(Integer, default=1)  # 1=operacional, 5=executivo
    salario_base = Column(DECIMAL(10, 2))
    salario_minimo = Column(DECIMAL(10, 2))
    salario_maximo = Column(DECIMAL(10, 2))
    requer_superior = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=func.now())
    
    # Relacionamentos
    colaboradores = relationship("Colaborador", back_populates="cargo")
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}" if self.codigo else self.nome


# =======================================
# MODELO PRINCIPAL
# =======================================

class Colaborador(Base):
    """Modelo principal de colaboradores"""
    __tablename__ = "colaboradores"
    
    # Chave primária e relacionamento com usuários
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    matricula = Column(String(20), unique=True, nullable=False, index=True)
    
    # Dados pessoais básicos
    nome_completo = Column(String(200), nullable=False)
    nome_social = Column(String(200))  # Para pessoas trans
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    rg = Column(String(20))
    data_nascimento = Column(Date)
    estado_civil = Column(String(20))
    sexo = Column(String(10))
    nacionalidade = Column(String(50), default="Brasileira")
    naturalidade = Column(String(100))
    
    # Contato
    telefone_principal = Column(String(20))
    telefone_secundario = Column(String(20))
    email_pessoal = Column(String(100))
    email_corporativo = Column(String(100))
    
    # Endereço residencial
    cep = Column(String(10))
    logradouro = Column(String(200))
    numero = Column(String(10))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))
    
    # Dados profissionais
    cargo_id = Column(Integer, ForeignKey("cargos.id"), nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=False)
    superior_direto_id = Column(Integer, ForeignKey("colaboradores.id"))
    
    # Contrato e remuneração
    tipo_contrato = Column(SQLEnum(TipoContrato), nullable=False)
    data_admissao = Column(Date, nullable=False)
    data_demissao = Column(Date)
    salario_atual = Column(DECIMAL(10, 2))
    vale_transporte = Column(DECIMAL(8, 2))
    vale_refeicao = Column(DECIMAL(8, 2))
    plano_saude = Column(Boolean, default=False)
    plano_odontologico = Column(Boolean, default=False)
    
    # Jornada de trabalho
    carga_horaria_semanal = Column(Integer, default=40)  # horas
    horario_entrada = Column(String(5))  # HH:MM
    horario_saida = Column(String(5))    # HH:MM
    horario_almoco_inicio = Column(String(5))  # HH:MM
    horario_almoco_fim = Column(String(5))     # HH:MM
    
    # Educação e qualificações
    escolaridade = Column(SQLEnum(NivelEscolaridade))
    curso_superior = Column(String(100))
    instituicao_ensino = Column(String(100))
    ano_formacao = Column(Integer)
    
    # Documentos trabalhistas
    pis_pasep = Column(String(20))
    numero_carteira_trabalho = Column(String(20))
    serie_carteira_trabalho = Column(String(10))
    titulo_eleitor = Column(String(20))
    zona_eleitoral = Column(String(10))
    secao_eleitoral = Column(String(10))
    
    # Banco para pagamento
    banco_codigo = Column(String(5))
    banco_nome = Column(String(100))
    agencia = Column(String(10))
    conta_corrente = Column(String(20))
    tipo_conta = Column(String(20))  # Corrente, Poupança
    
    # Informações emergenciais
    contato_emergencia_nome = Column(String(100))
    contato_emergencia_telefone = Column(String(20))
    contato_emergencia_parentesco = Column(String(50))
    
    # Status e observações
    status = Column(SQLEnum(StatusColaborador), default=StatusColaborador.ATIVO)
    observacoes = Column(Text)
    tem_dependentes = Column(Boolean, default=False)
    quantidade_dependentes = Column(Integer, default=0)
    
    # Controle de sistema
    ativo = Column(Boolean, default=True)
    data_cadastro = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    cadastrado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    usuario = relationship("Usuario", foreign_keys=[user_id])
    cargo = relationship("Cargo", back_populates="colaboradores")
    departamento = relationship(
        "Departamento", 
        primaryjoin="Colaborador.departamento_id == Departamento.id"
    )
    
    # Relacionamentos com tabelas dependentes
    documentos = relationship("ColaboradorDocumento", back_populates="colaborador")
    historico_profissional = relationship("HistoricoProfissional", back_populates="colaborador")
    pontos = relationship("PontoEletronico", back_populates="colaborador")
    ferias = relationship("PeriodoFerias", back_populates="colaborador")
    
    def __str__(self):
        return f"{self.matricula} - {self.nome_completo}"
    
    @property
    def nome_exibicao(self) -> str:
        """Nome para exibição (prioriza nome social)"""
        return self.nome_social or self.nome_completo
    
    @property
    def idade(self) -> int:
        """Calcular idade atual"""
        if not self.data_nascimento:
            return 0
        
        today = date.today()
        return today.year - self.data_nascimento.year - (
            (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
    
    @property
    def tempo_empresa(self) -> int:
        """Tempo de empresa em dias"""
        if not self.data_admissao:
            return 0
        
        fim = self.data_demissao or date.today()
        return (fim - self.data_admissao).days
    
    @property
    def cpf_formatado(self) -> str:
        """CPF formatado (xxx.xxx.xxx-xx)"""
        if not self.cpf:
            return ""
        
        cpf = ''.join(filter(str.isdigit, self.cpf))
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return self.cpf
    
    @property
    def telefone_formatado(self) -> str:
        """Telefone principal formatado"""
        if not self.telefone_principal:
            return ""
        
        tel = ''.join(filter(str.isdigit, self.telefone_principal))
        if len(tel) == 11:
            return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
        elif len(tel) == 10:
            return f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
        return self.telefone_principal
    
    @property
    def endereco_completo(self) -> str:
        """Endereço formatado completo"""
        parts = []
        
        if self.logradouro:
            endereco = self.logradouro
            if self.numero:
                endereco += f", {self.numero}"
            if self.complemento:
                endereco += f", {self.complemento}"
            parts.append(endereco)
        
        if self.bairro:
            parts.append(self.bairro)
        
        if self.cidade and self.estado:
            parts.append(f"{self.cidade}/{self.estado}")
        
        if self.cep:
            parts.append(f"CEP: {self.cep}")
        
        return " - ".join(parts)
    
    def is_ativo(self) -> bool:
        """Verificar se colaborador está ativo"""
        return self.ativo and self.status in [StatusColaborador.ATIVO, StatusColaborador.FERIAS]
    
    def can_login(self) -> bool:
        """Verificar se colaborador pode fazer login"""
        return self.is_ativo() and self.usuario and self.usuario.ativo
    
    def get_salario_total(self) -> float:
        """Calcular salário total com benefícios"""
        total = float(self.salario_atual or 0)
        total += float(self.vale_transporte or 0)
        total += float(self.vale_refeicao or 0)
        return total


# =======================================
# MODELOS RELACIONADOS
# =======================================

class ColaboradorDocumento(Base):
    """Documentos anexados ao colaborador"""
    __tablename__ = "colaborador_documentos"
    
    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(Integer, ForeignKey("colaboradores.id"), nullable=False)
    tipo_documento = Column(SQLEnum(TipoDocumento), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    arquivo_path = Column(String(500))
    descricao = Column(Text)
    data_validade = Column(Date)
    data_upload = Column(DateTime, default=func.now())
    uploadado_por = Column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamentos
    colaborador = relationship("Colaborador", back_populates="documentos")
    
    def __str__(self):
        return f"{self.tipo_documento.value} - {self.nome_arquivo}"


class HistoricoProfissional(Base):
    """Histórico profissional e mudanças de cargo"""
    __tablename__ = "historico_profissional"
    
    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(Integer, ForeignKey("colaboradores.id"), nullable=False)
    cargo_anterior_id = Column(Integer, ForeignKey("cargos.id"))
    cargo_novo_id = Column(Integer, ForeignKey("cargos.id"), nullable=False)
    departamento_anterior_id = Column(Integer, ForeignKey("departamentos.id"))
    departamento_novo_id = Column(Integer, ForeignKey("departamentos.id"))
    salario_anterior = Column(DECIMAL(10, 2))
    salario_novo = Column(DECIMAL(10, 2))
    data_mudanca = Column(Date, nullable=False)
    motivo = Column(Text)
    aprovado_por = Column(Integer, ForeignKey("usuarios.id"))
    data_aprovacao = Column(DateTime, default=func.now())
    
    # Relacionamentos
    colaborador = relationship("Colaborador", back_populates="historico_profissional")
    cargo_anterior = relationship("Cargo", foreign_keys=[cargo_anterior_id])
    cargo_novo = relationship("Cargo", foreign_keys=[cargo_novo_id])
    departamento_anterior = relationship("Departamento", foreign_keys=[departamento_anterior_id])
    departamento_novo = relationship("Departamento", foreign_keys=[departamento_novo_id])


class AvaliacaoDesempenho(Base):
    """Avaliações de desempenho"""
    __tablename__ = "avaliacoes_desempenho"
    
    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(Integer, ForeignKey("colaboradores.id"), nullable=False)
    avaliador_id = Column(Integer, ForeignKey("colaboradores.id"), nullable=False)
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    
    # Critérios de avaliação (1-5)
    pontualidade = Column(Integer)
    qualidade_trabalho = Column(Integer)
    produtividade = Column(Integer)
    relacionamento_interpessoal = Column(Integer)
    iniciativa = Column(Integer)
    conhecimento_tecnico = Column(Integer)
    
    nota_final = Column(DECIMAL(3, 2))  # Média geral
    comentarios_avaliador = Column(Text)
    comentarios_colaborador = Column(Text)
    metas_proximas = Column(Text)
    
    data_avaliacao = Column(DateTime, default=func.now())
    status = Column(String(20), default="Pendente")  # Pendente, Concluída, Cancelada
    
    # Relacionamentos removidos para evitar ambiguidade


class PontoEletronico(Base):
    """Registro de ponto eletrônico"""
    __tablename__ = "ponto_eletronico"
    
    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(Integer, ForeignKey("colaboradores.id"), nullable=False)
    data_ponto = Column(Date, nullable=False)
    
    # Horários registrados
    entrada_manha = Column(DateTime)
    saida_almoco = Column(DateTime)
    volta_almoco = Column(DateTime)
    saida_tarde = Column(DateTime)
    
    # Horas extras
    entrada_extra = Column(DateTime)
    saida_extra = Column(DateTime)
    
    # Totais calculados
    horas_trabalhadas = Column(DECIMAL(4, 2))  # Total do dia
    horas_extras = Column(DECIMAL(4, 2))
    
    observacoes = Column(Text)
    justificativa_falta = Column(Text)
    tipo_dia = Column(String(20), default="Normal")  # Normal, Feriado, Férias, Falta
    
    data_registro = Column(DateTime, default=func.now())
    
    # Relacionamentos
    colaborador = relationship("Colaborador", back_populates="pontos")


class PeriodoFerias(Base):
    """Períodos de férias dos colaboradores"""
    __tablename__ = "periodos_ferias"
    
    id = Column(Integer, primary_key=True, index=True)
    colaborador_id = Column(Integer, ForeignKey("colaboradores.id"), nullable=False)
    ano_referencia = Column(Integer, nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    dias_direito = Column(Integer, default=30)
    dias_gozados = Column(Integer)
    dias_vendidos = Column(Integer, default=0)
    valor_abono = Column(DECIMAL(10, 2))
    
    status = Column(String(20), default="Programadas")  # Programadas, Em andamento, Concluídas
    observacoes = Column(Text)
    aprovado_por = Column(Integer, ForeignKey("usuarios.id"))
    data_aprovacao = Column(DateTime)
    data_cadastro = Column(DateTime, default=func.now())
    
    # Relacionamentos
    colaborador = relationship("Colaborador", back_populates="ferias")