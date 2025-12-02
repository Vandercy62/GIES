"""
SISTEMA ERP PRIMOTEX - SHARED MODULES
=====================================

Módulos compartilhados do sistema de produção.

Inclui:
- Sistema de configuração
- Logging estruturado  
- Backup automatizado
- Segurança avançada
- Deployment scripts
- Monitoramento em tempo real
- Integração de produção

Autor: GitHub Copilot
Data: 30/10/2025
"""

__version__ = "3.0.0"
__author__ = "GitHub Copilot"
__description__ = "Primotex ERP - Production Systems"

# Importações dos módulos principais
try:
    from .config import ConfigManager, Settings
    from .logging_system import LogManager, get_logger
    from .backup_system import BackupManager
    from .security_system import SecurityManager
    from .deployment import DeploymentManager
    from .monitoring import MonitoringDashboard
    from .production_integration import ProductionSystemIntegrator

    __all__ = [
        'ConfigManager',
        'Settings', 
        'LogManager',
        'get_logger',
        'BackupManager',
        'SecurityManager',
        'DeploymentManager',
        'MonitoringDashboard',
        'ProductionSystemIntegrator'
    ]

except ImportError as e:
    print(f"Aviso: Nem todos os modulos estao disponiveis: {e}")
    __all__ = []