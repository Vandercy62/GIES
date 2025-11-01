"""
SISTEMA ERP PRIMOTEX - MODELO DE USUÁRIOS
=========================================

Este arquivo define a estrutura da tabela 'usuarios' no banco de dados.
Tabela responsável por armazenar informações dos usuários do sistema.

CAMPOS DA TABELA:
- id: Chave primária (número único para cada usuário)
- username: Nome de usuário para login (único)
- email: Email do usuário (único)
- senha_hash: Senha criptografada (nunca armazenamos senha em texto)
- nome_completo: Nome completo do usuário
- perfil: Tipo de acesso (Administrador, Gerente, Vendedor, etc.)
- ativo: Se o usuário está ativo no sistema (True/False)
- data_criacao: Quando o usuário foi criado
- ultima_atividade: Último acesso ao sistema

Autor: GitHub Copilot
Data: 29/10/2025
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from backend.database.config import Base

class Usuario(Base):
    """
    Modelo da tabela de usuários do sistema.
    
    Esta classe representa um usuário que pode acessar o sistema ERP.
    Cada usuário tem um perfil que define suas permissões.
    """
    
    # Nome da tabela no banco de dados
    __tablename__ = "usuarios"
    
    # =======================================
    # DEFINIÇÃO DOS CAMPOS DA TABELA
    # =======================================
    
    # Campo ID - Chave primária (número único)
    id = Column(
        Integer, 
        primary_key=True,           # Este campo é a chave primária
        index=True,                 # Criar índice para busca rápida
        comment="ID único do usuário"
    )
    
    # Campo USERNAME - Nome para login (deve ser único)
    username = Column(
        String(50),                 # Máximo 50 caracteres
        unique=True,                # Não pode repetir
        nullable=False,             # Obrigatório
        index=True,                 # Índice para busca rápida
        comment="Nome de usuário para login"
    )
    
    # Campo EMAIL - Email do usuário (deve ser único)
    email = Column(
        String(100),                # Máximo 100 caracteres
        unique=True,                # Não pode repetir
        nullable=False,             # Obrigatório
        index=True,                 # Índice para busca rápida
        comment="Email do usuário"
    )
    
    # Campo SENHA_HASH - Senha criptografada
    senha_hash = Column(
        String(255),                # Espaço para hash da senha
        nullable=False,             # Obrigatório
        comment="Senha criptografada do usuário"
    )
    
    # Campo NOME_COMPLETO - Nome completo do usuário
    nome_completo = Column(
        String(150),                # Máximo 150 caracteres
        nullable=False,             # Obrigatório
        comment="Nome completo do usuário"
    )
    
    # Campo PERFIL - Tipo de acesso do usuário
    perfil = Column(
        String(30),                 # Máximo 30 caracteres
        nullable=False,             # Obrigatório
        default="Vendedor",         # Valor padrão
        comment="Perfil de acesso: Administrador, Gerente, Vendedor, Financeiro, Técnico"
    )
    
    # Campo ATIVO - Se o usuário está ativo
    ativo = Column(
        Boolean,                    # True/False
        default=True,               # Por padrão, usuário ativo
        nullable=False,             # Obrigatório
        comment="Se o usuário está ativo no sistema"
    )
    
    # Campo DATA_CRIACAO - Quando foi criado automaticamente
    data_criacao = Column(
        DateTime(timezone=True),    # Data e hora com fuso horário
        server_default=func.now(),  # Valor automático = agora
        nullable=False,             # Obrigatório
        comment="Data e hora de criação do usuário"
    )
    
    # Campo ULTIMA_ATIVIDADE - Último acesso
    ultima_atividade = Column(
        DateTime(timezone=True),    # Data e hora com fuso horário
        onupdate=func.now(),        # Atualiza automaticamente
        comment="Data e hora do último acesso"
    )
    
    # Campo OBSERVACOES - Notas sobre o usuário
    observacoes = Column(
        Text,                       # Texto longo
        comment="Observações sobre o usuário"
    )
    
    # =======================================
    # MÉTODOS DA CLASSE
    # =======================================
    
    def __repr__(self):
        """
        Representação do objeto quando impresso.
        Útil para debug e logs.
        """
        return f"<Usuario(id={self.id}, username='{self.username}', perfil='{self.perfil}')>"
    
    def to_dict(self):
        """
        Converter o objeto para dicionário.
        Útil para retornar dados via API (sem senha).
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nome_completo": self.nome_completo,
            "perfil": self.perfil,
            "ativo": self.ativo,
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None,
            "ultima_atividade": self.ultima_atividade.isoformat() if self.ultima_atividade else None,
            "observacoes": self.observacoes
        }
    
    def is_admin(self):
        """Verificar se o usuário é administrador"""
        return self.perfil == "Administrador"
    
    def is_gerente(self):
        """Verificar se o usuário é gerente"""
        return self.perfil in ["Administrador", "Gerente"]
    
    def can_access_financeiro(self):
        """Verificar se pode acessar módulo financeiro"""
        return self.perfil in ["Administrador", "Gerente", "Financeiro"]

# =======================================
# PERFIS DISPONÍVEIS NO SISTEMA
# =======================================

PERFIS_SISTEMA = [
    {
        "value": "administrador",
        "label": "Administrador",
        "description": "Acesso total ao sistema, incluindo configurações e gerenciamento de usuários"
    },
    {
        "value": "gerente",
        "label": "Gerente",
        "description": "Acesso gerencial com controle de processos e relatórios"
    },
    {
        "value": "vendedor",
        "label": "Vendedor",
        "description": "Acesso a vendas, cadastros de clientes e acompanhamento de ordens"
    },
    {
        "value": "financeiro",
        "label": "Financeiro",
        "description": "Controle financeiro, contas a pagar/receber e relatórios"
    },
    {
        "value": "tecnico",
        "label": "Técnico",
        "description": "Execução de serviços técnicos e atualização de ordens de serviço"
    },
    {
        "value": "estoquista",
        "label": "Estoquista",
        "description": "Controle de estoque, entrada e saída de materiais"
    },
    {
        "value": "consulta",
        "label": "Consulta",
        "description": "Acesso apenas para consulta e visualização de informações"
    }
]