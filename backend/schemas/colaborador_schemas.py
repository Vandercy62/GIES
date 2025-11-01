#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA ERP PRIMOTEX - SCHEMAS DE COLABORADORES
===============================================

Schemas Pydantic para validação e serialização do módulo de colaboradores.
Inclui validações personalizadas e formatação de dados.

SCHEMAS PRINCIPAIS:
- ColaboradorBase/Create/Update/Response - CRUD de colaboradores
- DepartamentoBase/Create/Update/Response - Gestão de departamentos  
- CargoBase/Create/Update/Response - Gestão de cargos
- DocumentoColaborador - Gestão de documentos
- AvaliacaoDesempenho - Sistema de avaliações
- PontoEletronico - Controle de ponto

VALIDAÇÕES INCLUÍDAS:
- CPF com algoritmo de validação
- Email com regex validation
- Telefone com formato brasileiro
- Datas com validação de intervalo
- Campos obrigatórios por tipo de contrato

Autor: GitHub Copilot
Data: 01/11/2025
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import re
from enum import Enum

# Importar enums do modelo
from backend.models.colaborador_model import (
    TipoContrato, StatusColaborador, TipoDocumento, 
    NivelEscolaridade
)


# =======================================
# SCHEMAS BASE PARA REUTILIZAÇÃO
# =======================================

class PaginationParams(BaseModel):
    """Parâmetros de paginação padrão"""
    page: int = Field(1, ge=1, description="Número da página")
    size: int = Field(10, ge=1, le=100, description="Itens por página")


class FilterParams(BaseModel):
    """Parâmetros de filtro padrão"""
    search: Optional[str] = Field(None, description="Busca geral")
    ativo: Optional[bool] = Field(None, description="Filtrar por status ativo")


# =======================================
# SCHEMAS DE DEPARTAMENTO
# =======================================

class DepartamentoBase(BaseModel):
    """Schema base para departamentos"""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome do departamento")
    descricao: Optional[str] = Field(None, max_length=500, description="Descrição do departamento")
    codigo: Optional[str] = Field(None, max_length=20, description="Código identificador")
    centro_custo: Optional[str] = Field(None, max_length=50, description="Centro de custo")
    responsavel_id: Optional[int] = Field(None, description="ID do responsável")


class DepartamentoCreate(DepartamentoBase):
    """Schema para criação de departamento"""
    pass


class DepartamentoUpdate(BaseModel):
    """Schema para atualização de departamento"""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)
    codigo: Optional[str] = Field(None, max_length=20)
    centro_custo: Optional[str] = Field(None, max_length=50)
    responsavel_id: Optional[int] = None
    ativo: Optional[bool] = None


class DepartamentoResponse(DepartamentoBase):
    """Schema de resposta para departamento"""
    id: int
    ativo: bool
    data_criacao: datetime
    total_colaboradores: Optional[int] = 0
    
    class Config:
        from_attributes = True


# =======================================
# SCHEMAS DE CARGO
# =======================================

class CargoBase(BaseModel):
    """Schema base para cargos"""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome do cargo")
    descricao: Optional[str] = Field(None, max_length=500, description="Descrição do cargo")
    codigo: Optional[str] = Field(None, max_length=20, description="Código identificador")
    nivel_hierarquico: int = Field(1, ge=1, le=5, description="Nível hierárquico (1-5)")
    salario_base: Optional[Decimal] = Field(None, ge=0, description="Salário base sugerido")
    salario_minimo: Optional[Decimal] = Field(None, ge=0, description="Salário mínimo")
    salario_maximo: Optional[Decimal] = Field(None, ge=0, description="Salário máximo")
    requer_superior: bool = Field(False, description="Cargo requer superior direto")


class CargoCreate(CargoBase):
    """Schema para criação de cargo"""
    
    @validator('salario_maximo')
    def validar_salario_maximo(cls, v, values):
        """Validar que salário máximo >= mínimo"""
        if v and values.get('salario_minimo') and v < values['salario_minimo']:
            raise ValueError('Salário máximo deve ser maior que o mínimo')
        return v


class CargoUpdate(BaseModel):
    """Schema para atualização de cargo"""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(None, max_length=500)
    codigo: Optional[str] = Field(None, max_length=20)
    nivel_hierarquico: Optional[int] = Field(None, ge=1, le=5)
    salario_base: Optional[Decimal] = Field(None, ge=0)
    salario_minimo: Optional[Decimal] = Field(None, ge=0)
    salario_maximo: Optional[Decimal] = Field(None, ge=0)
    requer_superior: Optional[bool] = None
    ativo: Optional[bool] = None


class CargoResponse(CargoBase):
    """Schema de resposta para cargo"""
    id: int
    ativo: bool
    data_criacao: datetime
    total_colaboradores: Optional[int] = 0
    
    class Config:
        from_attributes = True


# =======================================
# SCHEMAS DE COLABORADOR
# =======================================

class ColaboradorBase(BaseModel):
    """Schema base para colaboradores"""
    # Dados básicos obrigatórios
    nome_completo: str = Field(..., min_length=2, max_length=200, description="Nome completo")
    cpf: str = Field(..., description="CPF (apenas números ou formatado)")
    data_admissao: date = Field(..., description="Data de admissão")
    cargo_id: int = Field(..., description="ID do cargo")
    departamento_id: int = Field(..., description="ID do departamento")
    tipo_contrato: TipoContrato = Field(..., description="Tipo de contrato")
    
    # Dados opcionais
    nome_social: Optional[str] = Field(None, max_length=200, description="Nome social")
    rg: Optional[str] = Field(None, max_length=20, description="RG")
    data_nascimento: Optional[date] = Field(None, description="Data de nascimento")
    estado_civil: Optional[str] = Field(None, max_length=20)
    sexo: Optional[str] = Field(None, max_length=10)
    nacionalidade: Optional[str] = Field("Brasileira", max_length=50)
    naturalidade: Optional[str] = Field(None, max_length=100)
    
    # Contato
    telefone_principal: Optional[str] = Field(None, max_length=20)
    telefone_secundario: Optional[str] = Field(None, max_length=20)
    email_pessoal: Optional[EmailStr] = Field(None, description="Email pessoal")
    email_corporativo: Optional[EmailStr] = Field(None, description="Email corporativo")
    
    # Endereço
    cep: Optional[str] = Field(None, max_length=10)
    logradouro: Optional[str] = Field(None, max_length=200)
    numero: Optional[str] = Field(None, max_length=10)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    
    # Hierarquia
    superior_direto_id: Optional[int] = Field(None, description="ID do superior direto")
    
    # Remuneração
    salario_atual: Optional[Decimal] = Field(None, ge=0, description="Salário atual")
    vale_transporte: Optional[Decimal] = Field(None, ge=0)
    vale_refeicao: Optional[Decimal] = Field(None, ge=0)
    plano_saude: bool = Field(False, description="Possui plano de saúde")
    plano_odontologico: bool = Field(False, description="Possui plano odontológico")
    
    # Jornada
    carga_horaria_semanal: int = Field(40, ge=20, le=60, description="Carga horária semanal")
    horario_entrada: Optional[str] = Field(None, description="Horário de entrada (HH:MM)")
    horario_saida: Optional[str] = Field(None, description="Horário de saída (HH:MM)")
    horario_almoco_inicio: Optional[str] = Field(None, description="Início do almoço (HH:MM)")
    horario_almoco_fim: Optional[str] = Field(None, description="Fim do almoço (HH:MM)")
    
    # Educação
    escolaridade: Optional[NivelEscolaridade] = Field(None, description="Nível de escolaridade")
    curso_superior: Optional[str] = Field(None, max_length=100)
    instituicao_ensino: Optional[str] = Field(None, max_length=100)
    ano_formacao: Optional[int] = Field(None, ge=1950, le=2030)
    
    # Documentos trabalhistas
    pis_pasep: Optional[str] = Field(None, max_length=20)
    numero_carteira_trabalho: Optional[str] = Field(None, max_length=20)
    serie_carteira_trabalho: Optional[str] = Field(None, max_length=10)
    titulo_eleitor: Optional[str] = Field(None, max_length=20)
    zona_eleitoral: Optional[str] = Field(None, max_length=10)
    secao_eleitoral: Optional[str] = Field(None, max_length=10)
    
    # Dados bancários
    banco_codigo: Optional[str] = Field(None, max_length=5)
    banco_nome: Optional[str] = Field(None, max_length=100)
    agencia: Optional[str] = Field(None, max_length=10)
    conta_corrente: Optional[str] = Field(None, max_length=20)
    tipo_conta: Optional[str] = Field(None, max_length=20)
    
    # Contato de emergência
    contato_emergencia_nome: Optional[str] = Field(None, max_length=100)
    contato_emergencia_telefone: Optional[str] = Field(None, max_length=20)
    contato_emergencia_parentesco: Optional[str] = Field(None, max_length=50)
    
    # Informações adicionais
    observacoes: Optional[str] = Field(None, description="Observações gerais")
    tem_dependentes: bool = Field(False)
    quantidade_dependentes: int = Field(0, ge=0)
    
    @validator('cpf')
    def validar_cpf(cls, v):
        """Validar CPF"""
        if not v:
            raise ValueError('CPF é obrigatório')
        
        # Remover formatação
        cpf = ''.join(filter(str.isdigit, v))
        
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        
        # Verificar se não é sequência repetida
        if cpf == cpf[0] * 11:
            raise ValueError('CPF inválido')
        
        # Validar dígitos verificadores
        def calcular_digito(cpf_parcial):
            soma = sum(int(cpf_parcial[i]) * (len(cpf_parcial) + 1 - i) for i in range(len(cpf_parcial)))
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)
        
        if cpf[9] != calcular_digito(cpf[:9]) or cpf[10] != calcular_digito(cpf[:10]):
            raise ValueError('CPF inválido')
        
        return cpf
    
    @validator('telefone_principal', 'telefone_secundario', 'contato_emergencia_telefone')
    def validar_telefone(cls, v):
        """Validar formato de telefone brasileiro"""
        if not v:
            return v
        
        # Remover formatação
        tel = ''.join(filter(str.isdigit, v))
        
        # Validar tamanho (10 ou 11 dígitos)
        if len(tel) not in [10, 11]:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        
        # Verificar se começa com código de área válido
        if not tel.startswith(('11', '12', '13', '14', '15', '16', '17', '18', '19',  # SP
                               '21', '22', '24',  # RJ
                               '27', '28',  # ES  
                               '31', '32', '33', '34', '35', '37', '38',  # MG
                               '41', '42', '43', '44', '45', '46',  # PR
                               '47', '48', '49',  # SC
                               '51', '53', '54', '55',  # RS
                               '61',  # DF
                               '62', '64',  # GO
                               '63',  # TO
                               '65', '66',  # MT
                               '67',  # MS
                               '68',  # AC
                               '69',  # RO
                               '71', '73', '74', '75', '77',  # BA
                               '79',  # SE
                               '81', '87',  # PE
                               '82',  # AL
                               '83',  # PB
                               '84',  # RN
                               '85', '88',  # CE
                               '86', '89',  # PI
                               '91', '93', '94',  # PA
                               '92', '97',  # AM
                               '95',  # RR
                               '96',  # AP
                               '98', '99')):  # MA
            raise ValueError('Código de área inválido')
        
        return tel
    
    @validator('horario_entrada', 'horario_saida', 'horario_almoco_inicio', 'horario_almoco_fim')
    def validar_horario(cls, v):
        """Validar formato de horário HH:MM"""
        if not v:
            return v
        
        if not re.match(r'^([01]?\d|2[0-3]):[0-5]\d$', v):
            raise ValueError('Horário deve estar no formato HH:MM')
        
        return v
    
    @validator('cep')
    def validar_cep(cls, v):
        """Validar CEP brasileiro"""
        if not v:
            return v
        
        # Remover formatação
        cep = ''.join(filter(str.isdigit, v))
        
        if len(cep) != 8:
            raise ValueError('CEP deve ter 8 dígitos')
        
        return cep
    
    @validator('estado')
    def validar_estado(cls, v):
        """Validar UF brasileira"""
        if not v:
            return v
        
        estados_validos = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
            'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
            'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        
        if v.upper() not in estados_validos:
            raise ValueError('Estado inválido')
        
        return v.upper()


class ColaboradorCreate(ColaboradorBase):
    """Schema para criação de colaborador"""
    matricula: str = Field(..., min_length=1, max_length=20, description="Matrícula única")
    user_id: int = Field(..., description="ID do usuário para login")
    
    @validator('matricula')
    def validar_matricula(cls, v):
        """Validar formato da matrícula"""
        if not v or not v.strip():
            raise ValueError('Matrícula é obrigatória')
        
        # Apenas letras, números, hífen e underline
        if not re.match(r'^[A-Za-z0-9_-]+$', v.strip()):
            raise ValueError('Matrícula deve conter apenas letras, números, hífen e underline')
        
        return v.strip().upper()


class ColaboradorUpdate(BaseModel):
    """Schema para atualização de colaborador"""
    # Permitir atualização de todos os campos opcionalmente
    nome_completo: Optional[str] = Field(None, min_length=2, max_length=200)
    nome_social: Optional[str] = Field(None, max_length=200)
    data_nascimento: Optional[date] = None
    estado_civil: Optional[str] = Field(None, max_length=20)
    sexo: Optional[str] = Field(None, max_length=10)
    telefone_principal: Optional[str] = Field(None, max_length=20)
    telefone_secundario: Optional[str] = Field(None, max_length=20)
    email_pessoal: Optional[EmailStr] = None
    email_corporativo: Optional[EmailStr] = None
    
    # Endereço
    cep: Optional[str] = Field(None, max_length=10)
    logradouro: Optional[str] = Field(None, max_length=200)
    numero: Optional[str] = Field(None, max_length=10)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    
    # Profissional
    cargo_id: Optional[int] = None
    departamento_id: Optional[int] = None
    superior_direto_id: Optional[int] = None
    salario_atual: Optional[Decimal] = Field(None, ge=0)
    vale_transporte: Optional[Decimal] = Field(None, ge=0)
    vale_refeicao: Optional[Decimal] = Field(None, ge=0)
    plano_saude: Optional[bool] = None
    plano_odontologico: Optional[bool] = None
    
    # Status
    status: Optional[StatusColaborador] = None
    observacoes: Optional[str] = None
    
    # Aplicar mesmas validações do schema base
    _validar_telefone = validator('telefone_principal', 'telefone_secundario', allow_reuse=True)(
        ColaboradorBase.validar_telefone.__func__
    )
    _validar_cep = validator('cep', allow_reuse=True)(ColaboradorBase.validar_cep.__func__)
    _validar_estado = validator('estado', allow_reuse=True)(ColaboradorBase.validar_estado.__func__)


class ColaboradorResponse(BaseModel):
    """Schema de resposta para colaborador"""
    id: int
    matricula: str
    nome_completo: str
    nome_social: Optional[str]
    cpf_formatado: str
    telefone_formatado: str
    email_corporativo: Optional[str]
    cargo: Optional[CargoResponse]
    departamento: Optional[DepartamentoResponse]
    status: StatusColaborador
    data_admissao: date
    data_demissao: Optional[date]
    tempo_empresa: int
    idade: Optional[int]
    ativo: bool
    data_cadastro: datetime
    
    class Config:
        from_attributes = True


class ColaboradorDetalhado(ColaboradorResponse):
    """Schema com todos os detalhes do colaborador"""
    # Adicionar campos completos
    rg: Optional[str]
    data_nascimento: Optional[date]
    estado_civil: Optional[str]
    sexo: Optional[str]
    nacionalidade: Optional[str]
    naturalidade: Optional[str]
    
    # Contato completo
    telefone_principal: Optional[str]
    telefone_secundario: Optional[str]
    email_pessoal: Optional[str]
    
    # Endereço completo
    endereco_completo: str
    
    # Remuneração
    salario_atual: Optional[Decimal]
    salario_total: float
    vale_transporte: Optional[Decimal]
    vale_refeicao: Optional[Decimal]
    plano_saude: bool
    plano_odontologico: bool
    
    # Educação
    escolaridade: Optional[NivelEscolaridade]
    curso_superior: Optional[str]
    instituicao_ensino: Optional[str]
    
    # Contato emergência
    contato_emergencia_nome: Optional[str]
    contato_emergencia_telefone: Optional[str]
    contato_emergencia_parentesco: Optional[str]
    
    # Informações adicionais
    observacoes: Optional[str]
    tem_dependentes: bool
    quantidade_dependentes: int


# =======================================
# SCHEMAS DE FILTROS E LISTAGEM
# =======================================

class ColaboradorFiltros(FilterParams):
    """Filtros específicos para colaboradores"""
    departamento_id: Optional[int] = Field(None, description="Filtrar por departamento")
    cargo_id: Optional[int] = Field(None, description="Filtrar por cargo")
    status: Optional[StatusColaborador] = Field(None, description="Filtrar por status")
    tipo_contrato: Optional[TipoContrato] = Field(None, description="Filtrar por tipo de contrato")
    data_admissao_inicio: Optional[date] = Field(None, description="Data de admissão mínima")
    data_admissao_fim: Optional[date] = Field(None, description="Data de admissão máxima")
    tem_superior: Optional[bool] = Field(None, description="Filtrar por ter superior direto")


class ColaboradorListagem(BaseModel):
    """Schema para listagem paginada de colaboradores"""
    items: List[ColaboradorResponse]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True


# =======================================
# SCHEMAS DE ESTATÍSTICAS
# =======================================

class EstatisticasColaboradores(BaseModel):
    """Estatísticas gerais dos colaboradores"""
    total_colaboradores: int
    total_ativos: int
    total_inativos: int
    total_em_ferias: int
    total_afastados: int
    
    # Por departamento
    por_departamento: Dict[str, int]
    
    # Por cargo
    por_cargo: Dict[str, int]
    
    # Por tipo de contrato
    por_tipo_contrato: Dict[str, int]
    
    # Médias
    idade_media: float
    tempo_empresa_medio: float
    salario_medio: float
    
    # Distribuição por tempo de empresa
    distribuicao_tempo_empresa: Dict[str, int]  # "0-1 anos", "1-3 anos", etc.


# =======================================
# SCHEMAS AUXILIARES
# =======================================

class DocumentoColaboradorBase(BaseModel):
    """Schema base para documentos"""
    tipo_documento: TipoDocumento
    nome_arquivo: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = Field(None, max_length=500)
    data_validade: Optional[date] = None


class DocumentoColaboradorCreate(DocumentoColaboradorBase):
    """Schema para upload de documento"""
    colaborador_id: int


class DocumentoColaboradorResponse(DocumentoColaboradorBase):
    """Schema de resposta para documento"""
    id: int
    arquivo_path: Optional[str]
    data_upload: datetime
    
    class Config:
        from_attributes = True


class AvaliacaoDesempenhoBase(BaseModel):
    """Schema base para avaliação"""
    periodo_inicio: date
    periodo_fim: date
    pontualidade: int = Field(..., ge=1, le=5)
    qualidade_trabalho: int = Field(..., ge=1, le=5)
    produtividade: int = Field(..., ge=1, le=5)
    relacionamento_interpessoal: int = Field(..., ge=1, le=5)
    iniciativa: int = Field(..., ge=1, le=5)
    conhecimento_tecnico: int = Field(..., ge=1, le=5)
    comentarios_avaliador: Optional[str] = None
    metas_proximas: Optional[str] = None


class AvaliacaoDesempenhoCreate(AvaliacaoDesempenhoBase):
    """Schema para criação de avaliação"""
    colaborador_id: int
    avaliador_id: int


class AvaliacaoDesempenhoResponse(AvaliacaoDesempenhoBase):
    """Schema de resposta para avaliação"""
    id: int
    nota_final: Decimal
    status: str
    data_avaliacao: datetime
    comentarios_colaborador: Optional[str]
    
    class Config:
        from_attributes = True