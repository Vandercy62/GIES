"""
SISTEMA ERP PRIMOTEX - SISTEMA DE LOGS ESTRUTURADOS
===================================================

Sistema avançado de logging com:
- Logs estruturados (JSON)
- Múltiplos handlers (arquivo, console, rotação)
- Diferentes níveis por módulo
- Correlação de requests
- Logs de auditoria
- Métricas de performance
- Alertas automáticos

Autor: GitHub Copilot
Data: 30/10/2025
"""

import logging
import logging.handlers
import structlog
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from functools import wraps
import traceback
import uuid

# Configuração do structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

class LogManager:
    """Gerenciador centralizado de logs"""
    
    def __init__(self, config_manager=None):
        self.config = config_manager
        self._loggers: Dict[str, logging.Logger] = {}
        self._request_id: Optional[str] = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Configurar sistema de logging"""
        try:
            # Obter configurações
            log_level = self._get_config('log_level', 'INFO')
            log_file = self._get_config('log_file', './logs/primotex_erp.log')
            log_max_size = self._get_config('log_max_size', 10485760)  # 10MB
            log_backup_count = self._get_config('log_backup_count', 5)
            log_format = self._get_config('log_format', 
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # Criar diretório de logs
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Configurar formatters
            detailed_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            json_formatter = structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
            )
            
            # Handler para arquivo com rotação
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=log_max_size,
                backupCount=log_backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            
            # Handler para arquivo JSON
            json_file = log_file.replace('.log', '.json')
            json_handler = logging.handlers.RotatingFileHandler(
                json_file,
                maxBytes=log_max_size,
                backupCount=log_backup_count,
                encoding='utf-8'
            )
            json_handler.setLevel(logging.INFO)
            json_handler.setFormatter(json_formatter)
            
            # Handler para console
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            console_handler.setFormatter(logging.Formatter(
                '%(levelname)-8s | %(name)-15s | %(message)s'
            ))
            
            # Configurar logger raiz
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            root_logger.handlers.clear()
            root_logger.addHandler(file_handler)
            root_logger.addHandler(json_handler)
            root_logger.addHandler(console_handler)
            
            # Logger específico para auditoria
            audit_logger = logging.getLogger('audit')
            audit_handler = logging.handlers.RotatingFileHandler(
                log_file.replace('.log', '_audit.log'),
                maxBytes=log_max_size,
                backupCount=log_backup_count,
                encoding='utf-8'
            )
            audit_handler.setFormatter(json_formatter)
            audit_logger.addHandler(audit_handler)
            audit_logger.setLevel(logging.INFO)
            audit_logger.propagate = False
            
            print("✓ Sistema de logs configurado com sucesso!")
            
        except Exception as e:
            print(f"X Erro ao configurar logs: {e}")
            traceback.print_exc()
    
    def _get_config(self, key: str, default: Any) -> Any:
        """Obter configuração do config manager"""
        if self.config:
            return self.config.get(key, default)
        return default
    
    def get_logger(self, name: str) -> structlog.BoundLogger:
        """Obter logger estruturado"""
        return structlog.get_logger(name)
    
    def set_request_id(self, request_id: str = None):
        """Definir ID da requisição para correlação"""
        self._request_id = request_id or str(uuid.uuid4())
        return self._request_id
    
    def clear_request_id(self):
        """Limpar ID da requisição"""
        self._request_id = None
    
    def log_request(self, method: str, path: str, status_code: int, 
                   duration_ms: float, user_id: str = None):
        """Log de requisição HTTP"""
        logger = self.get_logger("http")
        logger.info(
            "HTTP Request",
            request_id=self._request_id,
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_database_query(self, query: str, duration_ms: float, 
                          rows_affected: int = None):
        """Log de query de banco de dados"""
        logger = self.get_logger("database")
        logger.debug(
            "Database Query",
            request_id=self._request_id,
            query=query[:500],  # Truncar queries muito longas
            duration_ms=duration_ms,
            rows_affected=rows_affected,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_user_action(self, user_id: str, action: str, resource: str, 
                       details: Dict[str, Any] = None):
        """Log de auditoria de ações do usuário"""
        logger = logging.getLogger('audit')
        audit_data = {
            "event_type": "user_action",
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details or {},
            "request_id": self._request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info(json.dumps(audit_data, ensure_ascii=False))
    
    def log_system_event(self, event_type: str, message: str, 
                        details: Dict[str, Any] = None):
        """Log de eventos do sistema"""
        logger = self.get_logger("system")
        logger.info(
            message,
            event_type=event_type,
            details=details or {},
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log estruturado de erro"""
        logger = self.get_logger("error")
        logger.error(
            "Application Error",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {},
            request_id=self._request_id,
            stack_trace=traceback.format_exc(),
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_performance_metrics(self, module: str, operation: str, 
                               metrics: Dict[str, Any]):
        """Log de métricas de performance"""
        logger = self.get_logger("performance")
        logger.info(
            "Performance Metrics",
            module=module,
            operation=operation,
            metrics=metrics,
            request_id=self._request_id,
            timestamp=datetime.utcnow().isoformat()
        )


# =======================================
# DECORATORS PARA LOGGING
# =======================================

def log_function_call(logger_name: str = None):
    """Decorator para logar chamadas de função"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = log_manager.get_logger(logger_name or func.__module__)
            start_time = datetime.utcnow()
            
            try:
                logger.debug(
                    f"Function call started: {func.__name__}",
                    function=func.__name__,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                    timestamp=start_time.isoformat()
                )
                
                result = func(*args, **kwargs)
                
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds() * 1000
                
                logger.debug(
                    f"Function call completed: {func.__name__}",
                    function=func.__name__,
                    duration_ms=duration,
                    timestamp=end_time.isoformat()
                )
                
                return result
                
            except Exception as e:
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds() * 1000
                
                logger.error(
                    f"Function call failed: {func.__name__}",
                    function=func.__name__,
                    duration_ms=duration,
                    error=str(e),
                    timestamp=end_time.isoformat()
                )
                raise
        
        return wrapper
    return decorator

def log_api_endpoint(func):
    """Decorator para logar endpoints da API"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        request_id = log_manager.set_request_id()
        
        try:
            result = func(*args, **kwargs)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds() * 1000
            
            log_manager.log_request(
                method="API",
                path=func.__name__,
                status_code=200,
                duration_ms=duration
            )
            
            return result
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds() * 1000
            
            log_manager.log_request(
                method="API",
                path=func.__name__,
                status_code=500,
                duration_ms=duration
            )
            
            log_manager.log_error(e, {"endpoint": func.__name__})
            raise
        finally:
            log_manager.clear_request_id()
    
    return wrapper


# =======================================
# UTILITÁRIOS DE LOG
# =======================================

class LogAnalyzer:
    """Analisador de logs para insights"""
    
    def __init__(self, log_file: str):
        self.log_file = log_file
    
    def analyze_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Analisar performance das últimas horas"""
        # Implementação futura: análise de logs JSON
        return {
            "avg_response_time": 0.0,
            "error_rate": 0.0,
            "requests_per_hour": 0,
            "slow_endpoints": []
        }
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obter resumo de erros"""
        # Implementação futura: análise de erros
        return {
            "total_errors": 0,
            "error_types": {},
            "critical_errors": []
        }


# =======================================
# INSTÂNCIA GLOBAL
# =======================================

# Importar config manager se disponível
try:
    from shared.config import config
    log_manager = LogManager(config)
except ImportError:
    log_manager = LogManager()

# =======================================
# FUNÇÕES UTILITÁRIAS
# =======================================

def get_logger(name: str) -> structlog.BoundLogger:
    """Função global para obter logger"""
    return log_manager.get_logger(name)

def init_logging():
    """Inicializar sistema de logging"""
    try:
        print("📊 Inicializando sistema de logs...")
        log_manager._setup_logging()
        
        # Teste de logs
        logger = get_logger("system")
        logger.info("Sistema de logs inicializado", component="logging")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar logs: {e}")
        return False


if __name__ == "__main__":
    # Teste do sistema de logs
    init_logging()
    
    # Teste de diferentes tipos de log
    logger = get_logger("test")
    logger.info("Teste de log INFO", test_data={"value": 123})
    logger.warning("Teste de log WARNING", alert_type="test")
    logger.error("Teste de log ERROR", error_code=404)
    
    # Teste de auditoria
    log_manager.log_user_action(
        user_id="test_user",
        action="login",
        resource="system",
        details={"ip": "127.0.0.1"}
    )
    
    print("✅ Testes de log concluídos!")