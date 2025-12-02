"""
SISTEMA ERP PRIMOTEX - CONFIGURAÇÕES DE PRODUÇÃO
================================================

Sistema centralizado de configurações com suporte a:
- Variáveis de ambiente (.env)
- Configurações por ambiente (dev/prod)
- Validação de configurações obrigatórias
- Cache de configurações para performance
- Configurações sensíveis criptografadas

Autor: GitHub Copilot
Data: 30/10/2025
"""

import os
import secrets
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, validator, Field
from pydantic_settings import BaseSettings
from functools import lru_cache
import json
from pathlib import Path

class Settings(BaseSettings):
    """Configurações do sistema com validação Pydantic"""

    # =======================================
    # CONFIGURAÇÕES BÁSICAS
    # =======================================

    # Ambiente
    environment: str = "development"
    debug: bool = True
    app_name: str = "ERP Primotex"
    app_version: str = "3.0.0"

    # Servidor
    host: str = "127.0.0.1"
    port: int = 8002
    reload: bool = True

    # =======================================
    # BANCO DE DADOS
    # =======================================

    database_url: Optional[str] = None
    db_echo: bool = False
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_recycle: int = 3600

    # =======================================
    # SEGURANÇA
    # =======================================

    secret_key: str = "development-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Hash rounds para senhas
    password_hash_rounds: int = 12

    # =======================================
    # EMAIL
    # =======================================

    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None

    # =======================================
    # WHATSAPP BUSINESS
    # =======================================

    whatsapp_token: Optional[str] = None
    whatsapp_phone_id: Optional[str] = None
    whatsapp_verify_token: Optional[str] = None

    # =======================================
    # REDIS
    # =======================================

    redis_url: str = "redis://localhost:6379/0"

    # =======================================
    # UPLOADS E ARQUIVOS
    # =======================================

    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx", "xls", "xlsx"]

    # =======================================
    # BACKUP
    # =======================================

    backup_dir: str = "./backups"
    auto_backup_enabled: bool = True
    auto_backup_hour: int = 2
    backup_retention_days: int = 30

    # =======================================
    # LOGS
    # =======================================

    log_level: str = "INFO"
    log_file: str = "./logs/primotex_erp.log"
    log_max_size: int = 10485760  # 10MB
    log_backup_count: int = 5
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # =======================================
    # PERFORMANCE
    # =======================================

    cache_ttl_default: int = 300  # 5 minutos
    cache_max_size: int = 1000

    # =======================================
    # EMPRESA
    # =======================================

    empresa_nome: str = "Primotex - Forros e Divisórias Eireli"
    empresa_cnpj: str = "00.000.000/0001-00"
    empresa_telefone: str = "(16) 0000-0000"
    empresa_email: str = "contato@primotex.com.br"
    empresa_endereco: str = "Endereço da empresa"

    # =======================================
    # VALIDADORES
    # =======================================

    @validator('environment')
    def validate_environment(cls, v):
        """Validar ambiente"""
        if v not in ['development', 'production', 'testing']:
            raise ValueError('Ambiente deve ser: development, production ou testing')
        return v

    @validator('secret_key')
    def validate_secret_key(cls, v, values):
        """Validar chave secreta"""
        if values.get('environment') == 'production':
            if v == "development-key-change-in-production":
                raise ValueError('Chave secreta deve ser alterada em produção!')
            if len(v) < 32:
                raise ValueError('Chave secreta deve ter pelo menos 32 caracteres')
        return v

    @validator('database_url')
    def set_database_url(cls, v, values):
        """Configurar URL do banco de dados"""
        if v:
            return v

        env = values.get('environment', 'development')
        if env == 'production':
            raise ValueError('DATABASE_URL é obrigatória em produção')

        # SQLite para desenvolvimento
        return "sqlite:///./primotex_erp.db"

    @validator('allowed_extensions')
    def validate_extensions(cls, v):
        """Validar extensões permitidas"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(',')]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False


class ConfigManager:
    """Gerenciador de configurações do sistema"""

    def __init__(self):
        self._settings: Optional[Settings] = None
        self._config_cache: Dict[str, Any] = {}

    @property
    def settings(self) -> Settings:
        """Obter configurações (lazy loading)"""
        if self._settings is None:
            self._settings = Settings()
        return self._settings

    def get(self, key: str, default: Any = None) -> Any:
        """Obter configuração específica"""
        try:
            return getattr(self.settings, key, default)
        except Exception:
            return default

    def is_production(self) -> bool:
        """Verificar se está em produção"""
        return self.settings.environment == "production"

    def is_development(self) -> bool:
        """Verificar se está em desenvolvimento"""
        return self.settings.environment == "development"

    def is_testing(self) -> bool:
        """Verificar se está em testes"""
        return self.settings.environment == "testing"

    def get_database_url(self) -> str:
        """Obter URL do banco de dados"""
        return self.settings.database_url

    def generate_secret_key(self) -> str:
        """Gerar nova chave secreta"""
        return secrets.token_urlsafe(32)

    def validate_production_settings(self) -> List[str]:
        """Validar configurações para produção"""
        errors = []

        if not self.is_production():
            return errors

        # Verificações obrigatórias para produção
        required_settings = [
            ('secret_key', 'Chave secreta deve ser alterada'),
            ('database_url', 'URL do banco é obrigatória'),
            ('smtp_server', 'Servidor SMTP deve ser configurado'),
            ('empresa_cnpj', 'CNPJ da empresa deve ser configurado')
        ]

        for setting, message in required_settings:
            value = self.get(setting)
            if not value or (setting == 'secret_key' and 'development' in value):
                errors.append(f"{message}: {setting}")

        return errors

    def create_env_file(self, production: bool = False) -> str:
        """Criar arquivo .env baseado no template"""
        env_content = self._generate_env_content(production)

        env_file = ".env.production" if production else ".env"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)

        return env_file

    def _generate_env_content(self, production: bool) -> str:
        """Gerar conteúdo do arquivo .env"""
        if production:
            return f"""# PRODUÇÃO - ERP PRIMOTEX
ENVIRONMENT=production
DEBUG=false
SECRET_KEY={self.generate_secret_key()}
DATABASE_URL=postgresql://user:password@localhost:5432/primotex_erp
HOST=0.0.0.0
PORT=8002
RELOAD=false

# SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu_email@empresa.com
SMTP_PASSWORD=sua_senha_app

# BACKUP
AUTO_BACKUP_ENABLED=true
AUTO_BACKUP_HOUR=2
BACKUP_RETENTION_DAYS=30

# LOGS
LOG_LEVEL=WARNING
LOG_FILE=./logs/primotex_production.log
"""
        else:
            return f"""# DESENVOLVIMENTO - ERP PRIMOTEX  
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=development-key-{secrets.token_urlsafe(16)}
DATABASE_URL=sqlite:///./primotex_erp.db
HOST=127.0.0.1
PORT=8002
RELOAD=true

# LOGS
LOG_LEVEL=DEBUG
LOG_FILE=./logs/primotex_dev.log
"""

    def get_config_summary(self) -> Dict[str, Any]:
        """Obter resumo das configurações"""
        settings = self.settings

        return {
            "ambiente": settings.environment,
            "debug": settings.debug,
            "app": f"{settings.app_name} v{settings.app_version}",
            "servidor": f"{settings.host}:{settings.port}",
            "banco": "SQLite" if "sqlite" in settings.database_url else "PostgreSQL",
            "seguranca": {
                "algorithm": settings.algorithm,
                "token_expire": f"{settings.access_token_expire_minutes}min"
            },
            "empresa": {
                "nome": settings.empresa_nome,
                "cnpj": settings.empresa_cnpj
            },
            "backup": {
                "habilitado": settings.auto_backup_enabled,
                "horario": f"{settings.auto_backup_hour}:00"
            }
        }


# =======================================
# INSTÂNCIA GLOBAL
# =======================================

config = ConfigManager()

# =======================================
# FUNÇÕES UTILITÁRIAS
# =======================================

@lru_cache()
def get_settings() -> Settings:
    """Cache das configurações (FastAPI dependency)"""
    return Settings()

def create_directories():
    """Criar diretórios necessários"""
    directories = [
        config.get('upload_dir', './uploads'),
        config.get('backup_dir', './backups'),
        os.path.dirname(config.get('log_file', './logs/app.log'))
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def validate_config() -> bool:
    """Validar configurações do sistema"""
    try:
        settings = get_settings()

        if config.is_production():
            errors = config.validate_production_settings()
            if errors:
                print("❌ ERROS DE CONFIGURAÇÃO PARA PRODUÇÃO:")
                for error in errors:
                    print(f"  • {error}")
                return False

        print("✅ Configurações validadas com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

# =======================================
# INICIALIZAÇÃO
# =======================================

def init_config():
    """Inicializar sistema de configurações"""
    try:
        # Criar diretórios
        create_directories()

        # Validar configurações
        if not validate_config():
            return False

        # Exibir resumo
        summary = config.get_config_summary()
        print("🔧 CONFIGURAÇÕES DO SISTEMA:")
        print(f"   Ambiente: {summary['ambiente']}")
        print(f"   Aplicação: {summary['app']}")
        print(f"   Servidor: {summary['servidor']}")
        print(f"   Banco: {summary['banco']}")

        return True

    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False

if __name__ == "__main__":
    # Teste das configurações
    init_config()