"""
SISTEMA ERP PRIMOTEX - MODELO DE FORNECEDORES
============================================

Este arquivo define a estrutura da tabela 'fornecedores' no banco de dados.
Gerencia informações dos fornecedores de materiais e serviços.

CAMPOS PRINCIPAIS:
- Identificação (CNPJ/CPF, razão social, nome fantasia)
- Contato (telefone, email, endereço)
- Categorização e observações
- Controle de ativação/desativação
- Timestamps de auditoria

INTEGRAÇÃO:
- Sistema Financeiro (contas a pagar)
- Sistema de Compras (futuro)
- Gestão de Estoque (entradas)

Autor: GitHub Copilot
Data: 01/11/2025
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Numeric, Index
)
from sqlalchemy.sql import func
from backend.database.config import Base

# =======================================
# CONSTANTES DO SISTEMA
# =======================================

CATEGORIAS_FORNECEDOR = [
    "Materiais de Construção",
    "Ferragens e Parafusos",
    "Perfis de Alumínio",
    "Forros PVC",
    "Divisórias",
    "Gesso e Acabamentos",
    "Equipamentos e Ferramentas",
    "Serviços Terceirizados",
    "Transporte e Logística",
    "Escritório e Administração",
    "Outros"
]

TIPOS_FORNECEDOR = [
    "Pessoa Física",
    "Pessoa Jurídica"
]

STATUS_FORNECEDOR = [
    "Ativo",
    "Inativo",
    "Bloqueado",
    "Em Análise"
]

PORTES_EMPRESA = [
    "MEI",
    "Microempresa",
    "Pequena Empresa",
    "Média Empresa",
    "Grande Empresa"
]


# =======================================
# MODELO FORNECEDOR
# =======================================

class Fornecedor(Base):
    """
    Modelo para Fornecedores
    
    Armazena informações dos fornecedores de materiais,
    produtos e serviços para a empresa.
    """
    __tablename__ = "fornecedores"
    
    # =======================================
    # CHAVE PRIMÁRIA
    # =======================================
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="ID único do fornecedor"
    )
    
    # =======================================
    # IDENTIFICAÇÃO BÁSICA
    # =======================================
    
    # Documento principal (CNPJ ou CPF)
    cnpj_cpf = Column(
        String(18),
        unique=True,
        nullable=False,
        index=True,
        comment="CNPJ ou CPF do fornecedor (apenas números)"
    )
    
    # Razão social ou nome completo
    razao_social = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Razão social (PJ) ou nome completo (PF)"
    )
    
    # Nome fantasia ou apelido
    nome_fantasia = Column(
        String(200),
        nullable=True,
        index=True,
        comment="Nome fantasia da empresa ou apelido"
    )
    
    # Tipo de pessoa
    tipo_pessoa = Column(
        String(20),
        nullable=False,
        default="Pessoa Jurídica",
        comment="Pessoa Física ou Pessoa Jurídica"
    )
    
    # Inscrição estadual (opcional)
    inscricao_estadual = Column(
        String(20),
        nullable=True,
        comment="Inscrição estadual para PJ"
    )
    
    # =======================================
    # CATEGORIZAÇÃO
    # =======================================
    
    # Categoria principal
    categoria = Column(
        String(100),
        nullable=False,
        default="Outros",
        index=True,
        comment="Categoria principal do fornecedor"
    )
    
    # Subcategoria (opcional)
    subcategoria = Column(
        String(100),
        nullable=True,
        comment="Subcategoria específica"
    )
    
    # Porte da empresa
    porte_empresa = Column(
        String(50),
        nullable=True,
        comment="Porte da empresa (MEI, Micro, Pequena, etc.)"
    )
    
    # =======================================
    # INFORMAÇÕES DE CONTATO
    # =======================================
    
    # Contato principal
    contato_principal = Column(
        String(100),
        nullable=True,
        comment="Nome do responsável/vendedor"
    )
    
    # Telefone principal
    telefone = Column(
        String(20),
        nullable=True,
        comment="Telefone principal formatado"
    )
    
    # Telefone secundário
    telefone_2 = Column(
        String(20),
        nullable=True,
        comment="Telefone secundário ou WhatsApp"
    )
    
    # Email principal
    email = Column(
        String(150),
        nullable=True,
        index=True,
        comment="Email principal de contato"
    )
    
    # Email secundário
    email_2 = Column(
        String(150),
        nullable=True,
        comment="Email secundário ou financeiro"
    )
    
    # Site da empresa
    website = Column(
        String(200),
        nullable=True,
        comment="Site ou página da empresa"
    )
    
    # =======================================
    # ENDEREÇO COMPLETO
    # =======================================
    
    # CEP
    cep = Column(
        String(9),
        nullable=True,
        comment="CEP formatado (XXXXX-XXX)"
    )
    
    # Logradouro
    logradouro = Column(
        String(200),
        nullable=True,
        comment="Rua, avenida, etc."
    )
    
    # Número
    numero = Column(
        String(20),
        nullable=True,
        comment="Número do endereço"
    )
    
    # Complemento
    complemento = Column(
        String(100),
        nullable=True,
        comment="Complemento (apto, sala, etc.)"
    )
    
    # Bairro
    bairro = Column(
        String(100),
        nullable=True,
        comment="Bairro"
    )
    
    # Cidade
    cidade = Column(
        String(100),
        nullable=True,
        comment="Cidade"
    )
    
    # Estado (UF)
    estado = Column(
        String(2),
        nullable=True,
        comment="UF do estado (SP, RJ, etc.)"
    )
    
    # Endereço completo (campo calculado)
    endereco_completo = Column(
        Text,
        nullable=True,
        comment="Endereço completo formatado"
    )
    
    # =======================================
    # INFORMAÇÕES COMERCIAIS
    # =======================================
    
    # Condições de pagamento padrão
    condicoes_pagamento = Column(
        String(200),
        nullable=True,
        comment="Condições padrão de pagamento"
    )
    
    # Prazo de entrega padrão (em dias)
    prazo_entrega_padrao = Column(
        Integer,
        nullable=True,
        comment="Prazo médio de entrega em dias"
    )
    
    # Valor mínimo de pedido
    valor_minimo_pedido = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Valor mínimo para pedidos"
    )
    
    # Desconto padrão (%)
    desconto_padrao = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Percentual de desconto padrão"
    )
    
    # Avaliação do fornecedor (1 a 5)
    avaliacao = Column(
        Integer,
        nullable=True,
        comment="Avaliação do fornecedor (1 a 5 estrelas)"
    )
    
    # =======================================
    # DADOS BANCÁRIOS
    # =======================================
    
    # Banco principal
    banco = Column(
        String(100),
        nullable=True,
        comment="Nome do banco principal"
    )
    
    # Agência
    agencia = Column(
        String(20),
        nullable=True,
        comment="Agência bancária"
    )
    
    # Conta corrente
    conta = Column(
        String(30),
        nullable=True,
        comment="Número da conta corrente"
    )
    
    # PIX (chave)
    chave_pix = Column(
        String(100),
        nullable=True,
        comment="Chave PIX (email, telefone, CPF/CNPJ)"
    )
    
    # =======================================
    # OBSERVAÇÕES E NOTAS
    # =======================================
    
    # Observações gerais
    observacoes = Column(
        Text,
        nullable=True,
        comment="Observações gerais sobre o fornecedor"
    )
    
    # Histórico de problemas
    historico_problemas = Column(
        Text,
        nullable=True,
        comment="Registro de problemas ou ocorrências"
    )
    
    # Tags ou palavras-chave (JSON)
    tags = Column(
        Text,
        nullable=True,
        comment="JSON com tags para busca: ['entrega rápida', 'preço baixo']"
    )
    
    # =======================================
    # CONTROLE DE STATUS
    # =======================================
    
    # Status do fornecedor
    status = Column(
        String(20),
        nullable=False,
        default="Ativo",
        index=True,
        comment="Status: Ativo, Inativo, Bloqueado, Em Análise"
    )
    
    # Ativo/Inativo (boolean)
    ativo = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Se False, fornecedor está inativo"
    )
    
    # Motivo da inativação
    motivo_inativacao = Column(
        String(200),
        nullable=True,
        comment="Motivo da inativação ou bloqueio"
    )
    
    # =======================================
    # AUDITORIA E TIMESTAMPS
    # =======================================
    
    # Data de cadastro
    data_cadastro = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Data de cadastro do fornecedor"
    )
    
    # Data da última atualização
    data_atualizacao = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
        comment="Data da última atualização"
    )
    
    # Usuário que cadastrou
    usuario_cadastro_id = Column(
        Integer,
        nullable=True,
        comment="ID do usuário que cadastrou"
    )
    
    # Usuário que fez a última atualização
    usuario_atualizacao_id = Column(
        Integer,
        nullable=True,
        comment="ID do usuário que fez a última atualização"
    )
    
    # =======================================
    # ÍNDICES PARA PERFORMANCE
    # =======================================
    
    # Criar índices compostos para buscas frequentes
    __table_args__ = (
        Index('idx_fornecedor_ativo_categoria', 'ativo', 'categoria'),
        Index('idx_fornecedor_status_tipo', 'status', 'tipo_pessoa'),
        Index('idx_fornecedor_cidade_estado', 'cidade', 'estado'),
        Index('idx_fornecedor_contato', 'contato_principal', 'telefone'),
    )
    
    # =======================================
    # MÉTODOS DE INSTÂNCIA
    # =======================================
    
    def __repr__(self):
        return f"<Fornecedor(id={self.id}, razao_social='{self.razao_social}', cnpj_cpf='{self.cnpj_cpf}')>"
    
    def __str__(self):
        nome = self.nome_fantasia or self.razao_social
        return f"{nome} ({self.cnpj_cpf})"
    
    @property
    def nome_exibicao(self):
        """Nome para exibição (prioriza nome fantasia)"""
        return self.nome_fantasia or self.razao_social
    
    @property
    def documento_formatado(self):
        """CNPJ/CPF formatado para exibição"""
        doc = self.cnpj_cpf
        if not doc:
            return ""
        
        # Remove caracteres não numéricos
        doc = ''.join(filter(str.isdigit, doc))
        
        if len(doc) == 11:  # CPF
            return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
        elif len(doc) == 14:  # CNPJ
            return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
        else:
            return doc
    
    @property
    def telefone_formatado(self):
        """Telefone formatado para exibição"""
        tel = self.telefone
        if not tel:
            return ""
        
        # Remove caracteres não numéricos
        tel = ''.join(filter(str.isdigit, tel))
        
        if len(tel) == 11:  # Celular
            return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
        elif len(tel) == 10:  # Fixo
            return f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
        else:
            return tel
    
    def gerar_endereco_completo(self):
        """Gera o endereço completo formatado"""
        partes = []
        
        if self.logradouro:
            endereco = self.logradouro
            if self.numero:
                endereco += f", {self.numero}"
            if self.complemento:
                endereco += f", {self.complemento}"
            partes.append(endereco)
        
        if self.bairro:
            partes.append(self.bairro)
        
        if self.cidade and self.estado:
            partes.append(f"{self.cidade}/{self.estado}")
        elif self.cidade:
            partes.append(self.cidade)
        
        if self.cep:
            partes.append(f"CEP: {self.cep}")
        
        return " - ".join(partes)
    
    def atualizar_endereco_completo(self):
        """Atualiza o campo endereco_completo automaticamente"""
        self.endereco_completo = self.gerar_endereco_completo()
    
    def is_pessoa_fisica(self):
        """Verifica se é pessoa física"""
        return self.tipo_pessoa == "Pessoa Física"
    
    def is_pessoa_juridica(self):
        """Verifica se é pessoa jurídica"""
        return self.tipo_pessoa == "Pessoa Jurídica"
    
    def get_contato_completo(self):
        """Retorna informações de contato formatadas"""
        contatos = []
        
        if self.contato_principal:
            contatos.append(f"Contato: {self.contato_principal}")
        
        if self.telefone:
            contatos.append(f"Tel: {self.telefone_formatado}")
        
        if self.email:
            contatos.append(f"Email: {self.email}")
        
        return " | ".join(contatos)


# =======================================
# FUNÇÃO DE INICIALIZAÇÃO
# =======================================

def init_fornecedor_data():
    """
    Função para criar dados iniciais de fornecedores
    (pode ser chamada durante setup do sistema)
    """
    return {
        "categorias": CATEGORIAS_FORNECEDOR,
        "tipos": TIPOS_FORNECEDOR,
        "status": STATUS_FORNECEDOR,
        "portes": PORTES_EMPRESA
    }