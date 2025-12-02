"""
INICIALIZADOR ROBUSTO DO BACKEND ERP PRIMOTEX
=============================================

Sistema de inicialização com:
- Retry automático (3 tentativas)
- Validação pré-startup
- Logs detalhados
- Recuperação de erros
- Graceful shutdown

Autor: GitHub Copilot
Data: 17/11/2025
"""

import sys
import os
import time
import signal
import logging
from typing import Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("backend.startup")

# Estado global
server_process: Optional[object] = None
shutdown_requested = False


def signal_handler(signum, frame):
    """Handler para sinais de interrupção (Ctrl+C)"""
    global shutdown_requested
    logger.info("🛑 Sinal de interrupção recebido - Encerrando graciosamente...")
    shutdown_requested = True


def validate_environment() -> bool:
    """
    Valida ambiente antes de iniciar servidor
    
    Returns:
        True se ambiente OK, False caso contrário
    """
    logger.info("="*70)
    logger.info("🔍 VALIDANDO AMBIENTE")
    logger.info("="*70)
    
    errors = []
    
    # 1. Verificar versão Python
    logger.info("📋 Verificando versão Python...")
    if sys.version_info < (3, 11):
        errors.append(f"Python {sys.version_info.major}.{sys.version_info.minor} não suportado (necessário 3.11+)")
        logger.error(f"   ❌ {errors[-1]}")
    else:
        logger.info(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # 2. Verificar ambiente virtual
    logger.info("📋 Verificando ambiente virtual...")
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.warning("   ⚠️  Ambiente virtual não detectado (recomendado usar .venv)")
    else:
        logger.info(f"   ✅ Ambiente virtual ativo: {sys.prefix}")
    
    # 3. Verificar dependências críticas
    logger.info("📋 Verificando dependências críticas...")
    critical_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic'
    ]
    
    for package in critical_packages:
        try:
            __import__(package)
            logger.info(f"   ✅ {package}")
        except ImportError:
            errors.append(f"Pacote '{package}' não instalado")
            logger.error(f"   ❌ {errors[-1]}")
    
    # 4. Verificar estrutura de diretórios
    logger.info("📋 Verificando estrutura de diretórios...")
    required_dirs = [
        'backend',
        'backend/api',
        'backend/models',
        'backend/database',
        'logs',
        'uploads'
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            logger.warning(f"   ⚠️  Diretório '{dir_path}' não encontrado - criando...")
            try:
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"      ✅ Diretório criado")
            except Exception as e:
                errors.append(f"Não foi possível criar '{dir_path}': {e}")
                logger.error(f"      ❌ {errors[-1]}")
        else:
            logger.info(f"   ✅ {dir_path}")
    
    # 5. Verificar arquivo main
    logger.info("📋 Verificando arquivo principal...")
    if os.path.exists('backend/api/main_robust.py'):
        logger.info("   ✅ main_robust.py encontrado")
        main_module = "backend.api.main_robust:app"
    elif os.path.exists('backend/api/main.py'):
        logger.warning("   ⚠️  Usando main.py (recomendado migrar para main_robust.py)")
        main_module = "backend.api.main:app"
    else:
        errors.append("Arquivo backend/api/main.py não encontrado")
        logger.error(f"   ❌ {errors[-1]}")
        main_module = None
    
    # Resultado
    logger.info("="*70)
    if errors:
        logger.error("❌ VALIDAÇÃO FALHOU")
        for error in errors:
            logger.error(f"   • {error}")
        logger.info("="*70)
        return False
    else:
        logger.info("✅ VALIDAÇÃO CONCLUÍDA - AMBIENTE OK")
        logger.info("="*70)
        return True


def start_server_with_retry(max_retries: int = 3, retry_delay: int = 5) -> bool:
    """
    Inicia servidor com retry automático
    
    Args:
        max_retries: Número máximo de tentativas
        retry_delay: Delay entre tentativas (segundos)
        
    Returns:
        True se servidor iniciado, False caso contrário
    """
    global server_process
    
    # Determinar módulo principal
    if os.path.exists('backend/api/main_robust.py'):
        main_module = "backend.api.main_robust:app"
        logger.info("📍 Usando main_robust.py (versão robusta)")
    else:
        main_module = "backend.api.main:app"
        logger.info("📍 Usando main.py (versão padrão)")
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info("="*70)
            logger.info(f"🚀 TENTATIVA {attempt}/{max_retries} - INICIANDO SERVIDOR")
            logger.info("="*70)
            logger.info(f"📍 Módulo: {main_module}")
            logger.info(f"📍 Host: 127.0.0.1")
            logger.info(f"📍 Porta: 8002")
            logger.info(f"📍 Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*70)
            
            # Importar uvicorn
            import uvicorn
            
            # Configurar e iniciar servidor
            uvicorn.run(
                main_module,
                host="127.0.0.1",
                port=8002,
                reload=False,
                log_level="info",
                access_log=True,
                workers=1  # Single worker para evitar problemas SQLite
            )
            
            # Se chegou aqui, servidor encerrou normalmente
            logger.info("✅ Servidor encerrado normalmente")
            return True
            
        except KeyboardInterrupt:
            logger.info("⌨️  Interrupção pelo usuário (Ctrl+C)")
            return True
            
        except Exception as e:
            logger.error(f"❌ ERRO NA TENTATIVA {attempt}: {e}")
            
            if attempt < max_retries:
                logger.info(f"⏳ Aguardando {retry_delay} segundos antes de tentar novamente...")
                time.sleep(retry_delay)
            else:
                logger.error("="*70)
                logger.error("❌ TODAS AS TENTATIVAS FALHARAM")
                logger.error("="*70)
                logger.error(f"Erro: {str(e)}")
                logger.error("\nSugestões:")
                logger.error("1. Verifique se a porta 8002 está disponível")
                logger.error("2. Execute: pip install -r requirements.txt")
                logger.error("3. Verifique os logs em logs/primotex_erp.json")
                logger.error("4. Consulte a documentação em README.md")
                return False
    
    return False


def main():
    """Função principal"""
    global shutdown_requested
    
    # Registrar handler de sinais
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════════════╗")
    logger.info("║         SISTEMA ERP PRIMOTEX - BACKEND ROBUSTO v2.0               ║")
    logger.info("║         Primotex - Forros e Divisórias Eireli                      ║")
    logger.info("╚════════════════════════════════════════════════════════════════════╝")
    logger.info("")
    
    try:
        # 1. Validar ambiente
        if not validate_environment():
            logger.error("Validação falhou - Encerrando")
            sys.exit(1)
        
        # 2. Iniciar servidor com retry
        if not start_server_with_retry(max_retries=3, retry_delay=5):
            logger.error("Servidor não pôde ser iniciado - Encerrando")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        logger.info("")
        logger.info("="*70)
        logger.info("👋 BACKEND ENCERRADO")
        logger.info("="*70)


if __name__ == "__main__":
    main()
