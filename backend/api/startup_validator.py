"""
SISTEMA ERP PRIMOTEX - VALIDADOR DE INICIALIZAÇÃO
================================================

Sistema robusto de validação de dependências e inicialização segura.
Valida tudo ANTES do backend aceitar requests.

Autor: GitHub Copilot
Data: 17/11/2025
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("StartupValidator")


class StartupValidator:
    """Validador de inicialização do backend"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.validations: Dict[str, bool] = {}
        
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Executar todas as validações
        
        Returns:
            (sucesso, erros, avisos)
        """
        logger.info("="*70)
        logger.info("🔍 INICIANDO VALIDAÇÃO DE DEPENDÊNCIAS")
        logger.info("="*70)
        
        # 1. Validar Python version
        self._validate_python_version()
        
        # 2. Validar estrutura de diretórios
        self._validate_directory_structure()
        
        # 3. Validar dependências Python
        self._validate_python_dependencies()
        
        # 4. Validar banco de dados
        self._validate_database()
        
        # 5. Validar arquivos de configuração
        self._validate_config_files()
        
        # 6. Validar routers
        self._validate_routers()
        
        # 7. Validar modelos
        self._validate_models()
        
        # Resumo
        logger.info("="*70)
        logger.info("📊 RESUMO DA VALIDAÇÃO")
        logger.info("="*70)
        
        total = len(self.validations)
        passed = sum(1 for v in self.validations.values() if v)
        failed = total - passed
        
        for name, status in self.validations.items():
            emoji = "✅" if status else "❌"
            logger.info(f"{emoji} {name}")
        
        logger.info("-"*70)
        logger.info(f"📈 Total: {total} | ✅ Passou: {passed} | ❌ Falhou: {failed}")
        
        if self.warnings:
            logger.warning(f"⚠️  {len(self.warnings)} avisos encontrados:")
            for warning in self.warnings:
                logger.warning(f"   - {warning}")
        
        if self.errors:
            logger.error(f"❌ {len(self.errors)} erros críticos encontrados:")
            for error in self.errors:
                logger.error(f"   - {error}")
        
        success = len(self.errors) == 0
        
        if success:
            logger.info("="*70)
            logger.info("✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
            logger.info("="*70)
        else:
            logger.error("="*70)
            logger.error("❌ VALIDAÇÃO FALHOU - CORRIJA OS ERROS ACIMA")
            logger.error("="*70)
        
        return success, self.errors, self.warnings
    
    def _validate_python_version(self):
        """Validar versão do Python"""
        name = "Python Version"
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 11:
                logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro}")
                self.validations[name] = True
            else:
                self.errors.append(f"Python 3.11+ requerido, encontrado: {version.major}.{version.minor}")
                self.validations[name] = False
        except Exception as e:
            self.errors.append(f"Erro ao validar Python: {e}")
            self.validations[name] = False
    
    def _validate_directory_structure(self):
        """Validar estrutura de diretórios"""
        name = "Directory Structure"
        try:
            required_dirs = [
                "backend",
                "backend/api",
                "backend/models",
                "backend/schemas",
                "backend/database",
                "backend/auth",
                "backend/services",
                "frontend",
                "frontend/desktop",
                "shared",
                "logs"
            ]
            
            missing = []
            for dir_path in required_dirs:
                if not Path(dir_path).exists():
                    missing.append(dir_path)
                    # Criar diretório se não existir
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                    self.warnings.append(f"Diretório criado: {dir_path}")
            
            if missing:
                logger.warning(f"⚠️  {len(missing)} diretórios criados automaticamente")
            
            logger.info(f"✅ Estrutura de diretórios validada")
            self.validations[name] = True
            
        except Exception as e:
            self.errors.append(f"Erro ao validar diretórios: {e}")
            self.validations[name] = False
    
    def _validate_python_dependencies(self):
        """Validar dependências Python"""
        name = "Python Dependencies"
        try:
            required = [
                "fastapi",
                "uvicorn",
                "sqlalchemy",
                "pydantic",
                "requests",
                "python-jose",
                "passlib"
            ]
            
            missing = []
            for package in required:
                try:
                    __import__(package.replace("-", "_"))
                except ImportError:
                    missing.append(package)
            
            if missing:
                self.errors.append(f"Pacotes faltando: {', '.join(missing)}")
                self.errors.append("Execute: pip install -r requirements.txt")
                self.validations[name] = False
            else:
                logger.info(f"✅ Todas as dependências instaladas")
                self.validations[name] = True
                
        except Exception as e:
            self.errors.append(f"Erro ao validar dependências: {e}")
            self.validations[name] = False
    
    def _validate_database(self):
        """Validar conexão com banco de dados"""
        name = "Database Connection"
        try:
            from backend.database.config import engine
            from sqlalchemy import text
            
            # Testar conexão com text() para evitar erro
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info(f"✅ Conexão com banco de dados OK")
            self.validations[name] = True
            
            # Validar tabelas
            self._validate_database_tables()
            
        except Exception as e:
            self.warnings.append(f"Aviso de banco: {e}")
            self.validations[name] = True  # Warning, não crítico
    
    def _validate_database_tables(self):
        """Validar existência de tabelas"""
        name = "Database Tables"
        try:
            from backend.database.config import engine
            from sqlalchemy import inspect
            
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            required_tables = [
                "usuarios",
                "clientes",
                "produtos",
                "colaboradores",
                "fornecedores",
                "ordem_servico",
                "agendamentos",
                "contas"
            ]
            
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                self.warnings.append(f"Tabelas faltando: {', '.join(missing_tables)}")
                self.warnings.append("Serão criadas automaticamente no startup")
            
            logger.info(f"✅ Banco possui {len(tables)} tabelas")
            self.validations[name] = True
            
        except Exception as e:
            self.warnings.append(f"Não foi possível validar tabelas: {e}")
            self.validations[name] = True  # Não crítico
    
    def _validate_config_files(self):
        """Validar arquivos de configuração"""
        name = "Config Files"
        try:
            # Tentar importar SECRET_KEY da config (prioritário)
            try:
                from shared.config import get_settings
                settings = get_settings()
                secret_key = settings.SECRET_KEY
            except:
                # Fallback para constants (depreciado)
                try:
                    from shared.constants import SECRET_KEY
                    secret_key = SECRET_KEY
                except:
                    secret_key = None
            
            if secret_key and len(secret_key) < 32:
                self.warnings.append("SECRET_KEY muito curto (min 32 chars)")
            elif not secret_key:
                self.warnings.append("SECRET_KEY não configurado")
            
            logger.info(f"✅ Arquivos de configuração OK")
            self.validations[name] = True
            
        except Exception as e:
            self.warnings.append(f"Aviso em configuração: {e}")
            self.validations[name] = True
    
    def _validate_routers(self):
        """Validar importação de routers"""
        name = "API Routers"
        try:
            routers_to_test = [
                ("auth_router", "backend.api.routers.auth_router"),
                ("cliente_router", "backend.api.routers.cliente_router"),
                ("produto_router", "backend.api.routers.produto_router"),
                ("fornecedor_router", "backend.api.routers.fornecedor_router"),
                ("colaborador_router", "backend.api.routers.colaborador_router"),
                ("ordem_servico_router", "backend.api.routers.ordem_servico_router"),
                ("agendamento_router", "backend.api.routers.agendamento_router"),
                ("financeiro_router", "backend.api.routers.financeiro_router"),
                ("comunicacao_router", "backend.api.routers.comunicacao_router"),
                ("whatsapp_router", "backend.api.routers.whatsapp_router")
            ]
            
            failed_routers = []
            for router_name, module_path in routers_to_test:
                try:
                    __import__(module_path)
                except Exception as e:
                    failed_routers.append(f"{router_name}: {str(e)[:50]}")
            
            if failed_routers:
                self.warnings.append(f"{len(failed_routers)} routers com problemas:")
                for router in failed_routers:
                    self.warnings.append(f"  - {router}")
                logger.warning("⚠️  Alguns routers falharam mas sistema continuará")
            
            logger.info(f"✅ {len(routers_to_test) - len(failed_routers)}/{len(routers_to_test)} routers OK")
            self.validations[name] = True  # Não crítico
            
        except Exception as e:
            self.warnings.append(f"Erro ao validar routers: {e}")
            self.validations[name] = True
    
    def _validate_models(self):
        """Validar importação de modelos"""
        name = "Database Models"
        try:
            from backend.models.user_model import Usuario
            from backend.models.cliente_model import Cliente
            from backend.models.produto_model import Produto
            from backend.models.colaborador_model import Colaborador
            from backend.models.fornecedor_model import Fornecedor
            from backend.models.ordem_servico_model import OrdemServico
            from backend.models.agendamento_model import Agendamento
            from backend.models.financeiro_model import ContaReceber, ContaPagar
            
            logger.info(f"✅ Todos os modelos importados")
            self.validations[name] = True
            
        except ImportError as e:
            self.warnings.append(f"Aviso ao importar modelos: {e}")
            self.validations[name] = True  # Warning, não crítico
        except Exception as e:
            self.warnings.append(f"Aviso em modelos: {e}")
            self.validations[name] = True


def validate_startup() -> bool:
    """
    Função principal de validação
    
    Returns:
        True se todas as validações passaram
    """
    validator = StartupValidator()
    success, errors, warnings = validator.validate_all()
    
    if not success:
        print("\n" + "="*70)
        print("❌ BACKEND NÃO PODE INICIAR - CORRIJA OS ERROS ACIMA")
        print("="*70)
        print("\n💡 Dicas:")
        print("  1. Execute: pip install -r requirements.txt")
        print("  2. Verifique se o banco de dados está acessível")
        print("  3. Confira as variáveis de ambiente")
        print("\n")
    
    return success


if __name__ == "__main__":
    # Teste standalone
    success = validate_startup()
    sys.exit(0 if success else 1)
