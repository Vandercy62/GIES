"""
SISTEMA ERP PRIMOTEX - CONFIGURAÇÃO DO BANCO DE DADOS
====================================================

Configuração do SQLAlchemy para PostgreSQL e SQLite.
Suporte para desenvolvimento local e produção.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# =======================================
# CONFIGURAÇÕES DO BANCO
# =======================================

# Determinar se estamos em desenvolvimento ou produção
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = os.getenv("DATABASE_URL")

if ENVIRONMENT == "development" or not DATABASE_URL:
    # SQLite para desenvolvimento local
    SQLALCHEMY_DATABASE_URL = "sqlite:///./primotex_erp.db"
    connect_args = {"check_same_thread": False}
    echo = True
else:
    # PostgreSQL para produção
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
    connect_args = {}
    echo = False

# =======================================
# CONFIGURAÇÃO DO SQLAlchemy
# =======================================

# Criar engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    echo=echo  # Log das queries SQL em desenvolvimento
)

# SessionLocal para criar sessões do banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Metadata para migrations
metadata = MetaData()

# =======================================
# DEPENDENCY INJECTION
# =======================================

def get_db() -> Generator:
    """
    Dependency injection para obter sessão do banco de dados.
    Usado nos endpoints FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_database() -> Generator:
    """
    Dependency injection para obter sessão do banco de dados.
    Usado nos endpoints FastAPI.
    (Alias para get_db para compatibilidade)
    """
    return get_db()

# =======================================
# FUNÇÕES AUXILIARES
# =======================================

def init_database():
    """
    Inicializar banco de dados.
    Criar todas as tabelas se não existirem.
    """
    try:
        # Importar todos os modelos para criar as tabelas
        from backend.models import ALL_MODELS
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        
        print("✅ Banco de dados inicializado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        return False

def get_database_info():
    """Obter informações sobre o banco de dados atual"""
    return {
        "url": SQLALCHEMY_DATABASE_URL,
        "environment": ENVIRONMENT,
        "engine": str(engine.url),
        "echo": echo
    }

# =======================================
# CONFIGURAÇÕES DE CONEXÃO
# =======================================

# Pool de conexões para PostgreSQL
if ENVIRONMENT == "production":
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        echo=False
    )

# =======================================
# BACKUP E RESTAURAÇÃO (FUTURO)
# =======================================

def backup_database(backup_path: str) -> bool:
    """Fazer backup do banco de dados"""
    # Implementação futura
    pass

def restore_database(backup_path: str) -> bool:
    """Restaurar banco de dados do backup"""
    # Implementação futura
    pass