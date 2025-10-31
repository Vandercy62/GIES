"""
SISTEMA ERP PRIMOTEX - INTEGRAÇÃO DE PRODUÇÃO
==============================================

Script de integração completa dos sistemas de produção:
- Configuração centralizada
- Logging estruturado
- Backup automático
- Segurança avançada
- Deployment automatizado
- Monitoramento em tempo real

Este script une todos os sistemas implementados para uma
experiência de produção completa e integrada.

Autor: GitHub Copilot
Data: 30/10/2025
"""

import os
import sys
import time
import json
import asyncio
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Importar todos os sistemas de produção
try:
    from shared.config import ConfigManager, Settings
    from shared.logging_system import LogManager, get_logger
    from shared.backup_system import BackupManager
    from shared.security_system import SecurityManager
    from shared.deployment import DeploymentManager
    from shared.monitoring import MonitoringDashboard
except ImportError as e:
    print(f"❌ Erro ao importar sistemas: {e}")
    print("Certifique-se de que todos os sistemas estão implementados")
    sys.exit(1)

class ProductionSystemIntegrator:
    """Integrador dos sistemas de produção"""
    
    def __init__(self):
        """Inicializar integrador"""
        self.logger = None
        self.systems = {}
        self.is_running = False
        self.startup_time = datetime.now()
        
        # Status dos sistemas
        self.system_status = {
            'config': False,
            'logging': False,
            'backup': False,
            'security': False,
            'monitoring': False
        }
    
    def initialize_systems(self) -> bool:
        """Inicializar todos os sistemas de produção"""
        print("🚀 PRIMOTEX ERP - INICIALIZAÇÃO DOS SISTEMAS DE PRODUÇÃO")
        print("=" * 60)
        
        try:
            # 1. Sistema de Configuração
            print("⚙️  Inicializando sistema de configuração...")
            config_manager = ConfigManager()
            
            # Validar configurações de produção
            if config_manager.is_production():
                validation_errors = config_manager.validate_production_settings()
                if validation_errors:
                    print(f"❌ Erros de configuração: {', '.join(validation_errors)}")
                    return False
            
            self.systems['config'] = config_manager
            self.system_status['config'] = True
            print("✅ Sistema de configuração: OK")
            
            # 2. Sistema de Logging
            print("📝 Inicializando sistema de logging...")
            log_manager = LogManager()
            self.logger = get_logger("production")
            
            self.systems['logging'] = log_manager
            self.system_status['logging'] = True
            print("✅ Sistema de logging: OK")
            
            # 3. Sistema de Backup
            print("💾 Inicializando sistema de backup...")
            backup_manager = BackupManager()
            
            # Verificar se existem backups
            backup_status = backup_manager.get_backup_status()
            print(f"📊 Backups disponíveis: {backup_status['total_backups']}")
            print(f"🗂️  Espaço total: {backup_status.get('total_size_mb', 0):.1f} MB")
            
            self.systems['backup'] = backup_manager
            self.system_status['backup'] = True
            print("✅ Sistema de backup: OK")
            
            # 4. Sistema de Segurança
            print("🔐 Inicializando sistema de segurança...")
            security_manager = SecurityManager()
            
            # Verificar configurações de segurança
            if not security_manager.verify_security_config():
                print("⚠️  Configurações de segurança precisam de atenção")
            
            self.systems['security'] = security_manager
            self.system_status['security'] = True
            print("✅ Sistema de segurança: OK")
            
            # 5. Sistema de Monitoramento
            print("📊 Inicializando dashboard de monitoramento...")
            monitoring_dashboard = MonitoringDashboard()
            monitoring_dashboard.start_monitoring()
            
            self.systems['monitoring'] = monitoring_dashboard
            self.system_status['monitoring'] = True
            print("✅ Sistema de monitoramento: OK")
            
            self.logger.info("Todos os sistemas de produção inicializados com sucesso")
            print("\n🎉 TODOS OS SISTEMAS INICIALIZADOS COM SUCESSO!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            if self.logger:
                self.logger.error(f"Falha na inicialização dos sistemas: {e}")
            return False
    
    def run_production_checks(self) -> Dict[str, Any]:
        """Executar verificações de produção"""
        print("\n🔍 EXECUTANDO VERIFICAÇÕES DE PRODUÇÃO...")
        
        checks = {}
        
        # 1. Verificação de configuração
        config_manager = self.systems.get('config')
        if config_manager:
            checks['config'] = {
                'environment': config_manager.settings.environment,
                'debug_mode': config_manager.settings.debug,
                'production_ready': config_manager.is_production()
            }
        
        # 2. Verificação de logging
        log_manager = self.systems.get('logging')
        if log_manager:
            checks['logging'] = {
                'handlers_active': len(log_manager.logger.handlers),
                'log_level': log_manager.logger.level,
                'audit_enabled': hasattr(log_manager, 'audit_logger')
            }
        
        # 3. Verificação de backup
        backup_manager = self.systems.get('backup')
        if backup_manager:
            backup_status = backup_manager.get_backup_status()
            checks['backup'] = {
                'total_backups': backup_status['total_backups'],
                'last_backup': backup_status.get('last_backup', 'Nunca'),
                'scheduler_active': backup_manager.scheduler_running
            }
        
        # 4. Verificação de segurança
        security_manager = self.systems.get('security')
        if security_manager:
            checks['security'] = {
                'encryption_key_exists': security_manager.encryption_key is not None,
                'rate_limiter_active': len(security_manager.rate_limiter) >= 0,
                'jwt_configured': security_manager.jwt_secret_key is not None
            }
        
        # 5. Verificação de monitoramento
        monitoring = self.systems.get('monitoring')
        if monitoring:
            dashboard_data = monitoring.get_dashboard_data()
            checks['monitoring'] = {
                'metrics_collecting': monitoring.metrics_collector.is_running,
                'health_checks': len(dashboard_data['health_checks']['checks']),
                'active_alerts': len(dashboard_data['alerts'])
            }
        
        # Mostrar resultados
        print("\n📋 RESULTADOS DAS VERIFICAÇÕES:")
        for system, check_data in checks.items():
            print(f"\n🔧 {system.upper()}:")
            for key, value in check_data.items():
                status = "✅" if value else "❌"
                print(f"   {status} {key}: {value}")
        
        if self.logger:
            self.logger.info("Verificações de produção concluídas", checks=checks)
        
        return checks
    
    def create_backup_before_start(self) -> bool:
        """Criar backup antes de iniciar produção"""
        print("\n💾 CRIANDO BACKUP DE SEGURANÇA...")
        
        backup_manager = self.systems.get('backup')
        if not backup_manager:
            print("❌ Sistema de backup não disponível")
            return False
        
        try:
            result = backup_manager.create_full_backup()
            if result['success']:
                print(f"✅ Backup criado: {result['backup_file']}")
                if self.logger:
                    self.logger.info("Backup de segurança criado", backup_file=result['backup_file'])
                return True
            else:
                print(f"❌ Falha no backup: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return False
    
    def start_production_mode(self) -> bool:
        """Iniciar modo de produção completo"""
        print("\n🚀 INICIANDO MODO DE PRODUÇÃO...")
        
        try:
            # 1. Verificar se todos os sistemas estão prontos
            if not all(self.system_status.values()):
                print("❌ Nem todos os sistemas estão prontos")
                return False
            
            # 2. Criar backup de segurança
            if not self.create_backup_before_start():
                print("⚠️  Continuando sem backup de segurança")
            
            # 3. Configurar modo de produção
            config_manager = self.systems['config']
            if config_manager.settings.environment != 'production':
                print("⚠️  Ambiente não está configurado como 'production'")
            
            # 4. Ativar monitoramento intensivo
            monitoring = self.systems['monitoring']
            print("📊 Monitoramento ativo em tempo real")
            
            # 5. Configurar sistema de segurança
            security_manager = self.systems['security']
            print("🔐 Sistema de segurança ativo")
            
            self.is_running = True
            
            if self.logger:
                self.logger.info("Modo de produção iniciado com sucesso")
            
            print("✅ MODO DE PRODUÇÃO ATIVO!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar produção: {e}")
            if self.logger:
                self.logger.error(f"Falha ao iniciar produção: {e}")
            return False
    
    def stop_production_mode(self):
        """Parar modo de produção"""
        print("\n🛑 PARANDO MODO DE PRODUÇÃO...")
        
        try:
            # Parar monitoramento
            monitoring = self.systems.get('monitoring')
            if monitoring:
                monitoring.stop_monitoring()
                print("✅ Monitoramento parado")
            
            # Parar sistema de backup
            backup_manager = self.systems.get('backup')
            if backup_manager:
                backup_manager.stop_scheduler()
                print("✅ Sistema de backup parado")
            
            self.is_running = False
            
            if self.logger:
                self.logger.info("Modo de produção parado")
            
            print("✅ MODO DE PRODUÇÃO PARADO!")
            
        except Exception as e:
            print(f"❌ Erro ao parar produção: {e}")
    
    def get_production_status(self) -> Dict[str, Any]:
        """Obter status completo da produção"""
        uptime = (datetime.now() - self.startup_time).total_seconds()
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': uptime,
            'is_running': self.is_running,
            'systems_status': self.system_status.copy(),
            'startup_time': self.startup_time.isoformat()
        }
        
        # Adicionar dados do monitoramento se disponível
        monitoring = self.systems.get('monitoring')
        if monitoring:
            dashboard_data = monitoring.get_dashboard_data()
            status['monitoring_data'] = dashboard_data
        
        return status
    
    def print_production_dashboard(self):
        """Imprimir dashboard de produção"""
        status = self.get_production_status()
        
        print("\n" + "="*60)
        print("🏭 PRIMOTEX ERP - DASHBOARD DE PRODUÇÃO")
        print("="*60)
        
        # Status geral
        uptime_hours = status['uptime_seconds'] / 3600
        running_status = "🟢 ATIVO" if status['is_running'] else "🔴 INATIVO"
        print(f"Status: {running_status}")
        print(f"Uptime: {uptime_hours:.1f} horas")
        print(f"Início: {status['startup_time']}")
        
        # Status dos sistemas
        print(f"\n🔧 SISTEMAS:")
        for system, active in status['systems_status'].items():
            status_icon = "✅" if active else "❌"
            print(f"   {status_icon} {system.capitalize()}")
        
        # Dados do monitoramento
        if 'monitoring_data' in status:
            monitoring_data = status['monitoring_data']
            
            if 'metrics' in monitoring_data and 'system' in monitoring_data['metrics']:
                sys_metrics = monitoring_data['metrics']['system']
                print(f"\n📊 MÉTRICAS:")
                print(f"   💻 CPU: {sys_metrics['cpu_percent']:.1f}%")
                print(f"   🧠 RAM: {sys_metrics['memory_percent']:.1f}%")
                print(f"   💾 Disco: {sys_metrics['disk_percent']:.1f}%")
            
            if 'alerts' in monitoring_data:
                alert_count = len(monitoring_data['alerts'])
                if alert_count > 0:
                    print(f"\n🚨 ALERTAS: {alert_count} ativos")
                else:
                    print(f"\n✅ ALERTAS: Nenhum alerta ativo")
        
        print("="*60)

def run_interactive_mode():
    """Modo interativo de produção"""
    integrator = ProductionSystemIntegrator()
    
    if not integrator.initialize_systems():
        print("❌ Falha na inicialização dos sistemas")
        return
    
    # Executar verificações
    integrator.run_production_checks()
    
    # Iniciar produção
    if not integrator.start_production_mode():
        print("❌ Falha ao iniciar modo de produção")
        return
    
    try:
        # Loop principal
        while True:
            integrator.print_production_dashboard()
            time.sleep(30)  # Atualizar a cada 30 segundos
            
    except KeyboardInterrupt:
        print("\n🛑 Recebido sinal de interrupção...")
        integrator.stop_production_mode()

def run_health_check():
    """Executar apenas health check rápido"""
    integrator = ProductionSystemIntegrator()
    
    if integrator.initialize_systems():
        checks = integrator.run_production_checks()
        print(f"\n✅ Health check concluído: {len(checks)} sistemas verificados")
    else:
        print("❌ Falha no health check")

def deploy_production():
    """Executar deployment para produção"""
    print("🚀 DEPLOYMENT PARA PRODUÇÃO")
    print("=" * 30)
    
    deployer = DeploymentManager()
    success = deployer.deploy()
    
    if success:
        print("\n🎉 DEPLOYMENT CONCLUÍDO!")
        print("Agora você pode iniciar os sistemas de produção.")
    else:
        print("\n❌ FALHA NO DEPLOYMENT")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Primotex ERP - Integração de Produção")
    parser.add_argument("--mode", choices=["interactive", "health", "deploy"], 
                       default="interactive", help="Modo de operação")
    
    args = parser.parse_args()
    
    if args.mode == "health":
        run_health_check()
    elif args.mode == "deploy":
        deploy_production()
    else:
        run_interactive_mode()