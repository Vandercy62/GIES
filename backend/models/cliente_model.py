"""
SISTEMA ERP PRIMOTEX - MODELO DE CLIENTES
=========================================

Este arquivo define a estrutura da tabela 'clientes' no banco de dados.
Esta é uma das tabelas mais importantes do sistema, pois armazena 
todas as informações dos clientes da Primotex.

ESTRUTURA BASEADA NAS 3 ABAS DO CADASTRO:
ABA 1 - Dados Básicos: Informações principais de identificação
ABA 2 - Dados Complementares: Endereço, contatos, dados bancários
ABA 3 - Observações e Anexos: Notas, histórico, arquivos

CAMPOS PRINCIPAIS:
- Dados de identificação (nome, CPF/CNPJ, tipo)
- Endereço completo
- Contatos (telefones, emails)
- Informações comerciais
- Dados bancários
- Controle de sistema (data criação, status)

Autor: GitHub Copilot
Data: 29/10/2025
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.config import Base

class Cliente(Base):
    """
    Modelo da tabela de clientes.
    
    Armazena todas as informações dos clientes da Primotex,
    organizadas conforme as 3 abas do sistema de cadastro.
    """
    
    # Nome da tabela no banco de dados
    __tablename__ = "clientes"
    
    # =======================================
    # ABA 1 - DADOS BÁSICOS
    # =======================================
    
    # Chave primária
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="ID único do cliente"
    )
    
    # Código do cliente (pode ser personalizado)
    codigo = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Código único do cliente (ex: CLI001, CLI002)"
    )
    
    # Tipo de pessoa
    tipo_pessoa = Column(
        String(20),
        nullable=False,
        default="Física",
        comment="Tipo: Física ou Jurídica"
    )
    
    # Nome/Razão Social
    nome = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Nome completo (PF) ou Razão Social (PJ)"
    )
    
    # CPF ou CNPJ
    cpf_cnpj = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="CPF (pessoa física) ou CNPJ (pessoa jurídica)"
    )
    
    # RG ou Inscrição Estadual
    rg_ie = Column(
        String(20),
        comment="RG (pessoa física) ou Inscrição Estadual (pessoa jurídica)"
    )
    
    # Data de nascimento ou fundação
    data_nascimento_fundacao = Column(
        Date,
        comment="Data de nascimento (PF) ou fundação (PJ)"
    )
    
    # Caminho para foto do cliente
    foto_path = Column(
        String(255),
        comment="Caminho para arquivo de foto do cliente"
    )
    
    # Status do cliente
    status = Column(
        String(20),
        nullable=False,
        default="Ativo",
        comment="Status: Ativo, Inativo, Prospect"
    )
    
    # Origem do cliente (marketing)
    origem = Column(
        String(50),
        comment="Origem: Google, Indicação, Redes Sociais, etc."
    )
    
    # Tipo de cliente por segmento
    tipo_cliente = Column(
        String(30),
        comment="Tipo: Residencial, Comercial, Industrial, Público"
    )
    
    # =======================================
    # ABA 2 - DADOS COMPLEMENTARES
    # =======================================
    
    # Endereço completo
    endereco_cep = Column(
        String(10),
        comment="CEP do endereço"
    )
    
    endereco_logradouro = Column(
        String(150),
        comment="Rua, avenida, etc."
    )
    
    endereco_numero = Column(
        String(10),
        comment="Número do endereço"
    )
    
    endereco_complemento = Column(
        String(100),
        comment="Apartamento, sala, etc."
    )
    
    endereco_bairro = Column(
        String(100),
        comment="Bairro"
    )
    
    endereco_cidade = Column(
        String(100),
        comment="Cidade"
    )
    
    endereco_estado = Column(
        String(2),
        comment="Estado (sigla: SP, RJ, etc.)"
    )
    
    # Contatos
    telefone_fixo = Column(
        String(20),
        comment="Telefone fixo"
    )
    
    telefone_celular = Column(
        String(20),
        comment="Telefone celular"
    )
    
    telefone_whatsapp = Column(
        String(20),
        comment="WhatsApp (pode ser igual ao celular)"
    )
    
    email_principal = Column(
        String(100),
        index=True,
        comment="Email principal"
    )
    
    email_secundario = Column(
        String(100),
        comment="Email secundário"
    )
    
    # Site e redes sociais
    site = Column(
        String(100),
        comment="Site da empresa"
    )
    
    redes_sociais = Column(
        Text,
        comment="Links das redes sociais (JSON ou texto)"
    )
    
    # Contatos adicionais (JSON)
    contatos_adicionais = Column(
        Text,
        comment="JSON com contatos extras: [{'nome':'João', 'cargo':'Gerente', 'telefone':'xxx'}]"
    )
    
    # Dados bancários
    banco_nome = Column(
        String(100),
        comment="Nome do banco"
    )
    
    banco_agencia = Column(
        String(10),
        comment="Agência bancária"
    )
    
    banco_conta = Column(
        String(20),
        comment="Número da conta"
    )
    
    # Dados comerciais
    limite_credito = Column(
        Numeric(10, 2),
        default=0.00,
        comment="Limite de crédito em reais"
    )
    
    dia_vencimento_preferencial = Column(
        Integer,
        comment="Dia preferencial de vencimento (1-31)"
    )
    
    # =======================================
    # ABA 3 - OBSERVAÇÕES E ANEXOS
    # =======================================
    
    observacoes_gerais = Column(
        Text,
        comment="Observações gerais sobre o cliente"
    )
    
    historico_interacoes = Column(
        Text,
        comment="Histórico de interações (JSON)"
    )
    
    anexos_paths = Column(
        Text,
        comment="Caminhos dos arquivos anexados (JSON)"
    )
    
    tags_categorias = Column(
        Text,
        comment="Tags e categorias personalizadas (JSON)"
    )
    
    # =======================================
    # CAMPOS DE CONTROLE DO SISTEMA
    # =======================================
    
    data_criacao = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Data de criação do cadastro"
    )
    
    data_atualizacao = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Data da última atualização"
    )
    
    usuario_criacao_id = Column(
        Integer,
        comment="ID do usuário que criou o cadastro"
    )
    
    usuario_atualizacao_id = Column(
        Integer,
        comment="ID do usuário que fez a última atualização"
    )
    
    # =======================================
    # RELACIONAMENTOS (FASE 3)
    # =======================================
    
    # Relacionamento com Ordens de Serviço
    ordens_servico = relationship("OrdemServico", back_populates="cliente")
    
    # Relacionamento com Agendamentos
    agendamentos = relationship("Agendamento", back_populates="cliente")
    
    # Relacionamento com Contas a Receber
    contas_receber = relationship("ContaReceber", back_populates="cliente")
    
    # =======================================
    # MÉTODOS DA CLASSE
    # =======================================
    
    def __repr__(self):
        """Representação do objeto"""
        return f"<Cliente(id={self.id}, codigo='{self.codigo}', nome='{self.nome}')>"
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            # Dados básicos
            "id": self.id,
            "codigo": self.codigo,
            "tipo_pessoa": self.tipo_pessoa,
            "nome": self.nome,
            "cpf_cnpj": self.cpf_cnpj,
            "rg_ie": self.rg_ie,
            "data_nascimento_fundacao": self.data_nascimento_fundacao.isoformat() if self.data_nascimento_fundacao else None,
            "foto_path": self.foto_path,
            "status": self.status,
            "origem": self.origem,
            "tipo_cliente": self.tipo_cliente,
            
            # Endereço
            "endereco": {
                "cep": self.endereco_cep,
                "logradouro": self.endereco_logradouro,
                "numero": self.endereco_numero,
                "complemento": self.endereco_complemento,
                "bairro": self.endereco_bairro,
                "cidade": self.endereco_cidade,
                "estado": self.endereco_estado
            },
            
            # Contatos
            "contatos": {
                "telefone_fixo": self.telefone_fixo,
                "telefone_celular": self.telefone_celular,
                "telefone_whatsapp": self.telefone_whatsapp,
                "email_principal": self.email_principal,
                "email_secundario": self.email_secundario,
                "site": self.site
            },
            
            # Dados comerciais
            "limite_credito": float(self.limite_credito) if self.limite_credito else 0.00,
            "dia_vencimento_preferencial": self.dia_vencimento_preferencial,
            
            # Observações
            "observacoes_gerais": self.observacoes_gerais,
            
            # Controle
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None,
            "data_atualizacao": self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }
    
    def get_endereco_completo(self):
        """Retorna endereço formatado"""
        endereco_parts = []
        
        if self.endereco_logradouro:
            endereco_parts.append(self.endereco_logradouro)
        
        if self.endereco_numero:
            endereco_parts.append(f"nº {self.endereco_numero}")
            
        if self.endereco_complemento:
            endereco_parts.append(self.endereco_complemento)
            
        if self.endereco_bairro:
            endereco_parts.append(f"- {self.endereco_bairro}")
            
        if self.endereco_cidade and self.endereco_estado:
            endereco_parts.append(f"- {self.endereco_cidade}/{self.endereco_estado}")
            
        if self.endereco_cep:
            endereco_parts.append(f"CEP: {self.endereco_cep}")
        
        return ", ".join(endereco_parts)
    
    def is_pessoa_fisica(self):
        """Verifica se é pessoa física"""
        return self.tipo_pessoa == "Física"
    
    def is_pessoa_juridica(self):
        """Verifica se é pessoa jurídica"""
        return self.tipo_pessoa == "Jurídica"
    
    def is_ativo(self):
        """Verifica se cliente está ativo"""
        return self.status == "Ativo"

# =======================================
# CONSTANTES PARA O SISTEMA
# =======================================

TIPOS_PESSOA = ["Física", "Jurídica"]
STATUS_CLIENTE = ["Ativo", "Inativo", "Prospect"]
ORIGENS_CLIENTE = [
    "Google", "Indicação", "Facebook", "Instagram", 
    "WhatsApp", "Site", "Telefone", "Visita", "Outros"
]
TIPOS_CLIENTE = ["Residencial", "Comercial", "Industrial", "Público"]