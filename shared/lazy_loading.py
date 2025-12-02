# -*- coding: utf-8 -*-
"""
SISTEMA DE LAZY LOADING - ERP PRIMOTEX
======================================

Sistema de carregamento sob demanda para otimização de performance:
- Carregamento tardio de módulos pesados
- Pool de conexões reutilizáveis
- Pré-carregamento inteligente
- Monitoramento de uso de recursos

Autor: GitHub Copilot
Data: 29/10/2025
"""

import threading
import time
import weakref
from typing import Any, Dict, Optional, Callable, List, Type
from dataclasses import dataclass
from datetime import datetime
import importlib
import sys
import psutil
import gc


@dataclass
class ModuleInfo:
    """Informações sobre módulo carregado"""
    name: str
    instance: Any
    loaded_at: float
    access_count: int = 0
    last_accessed: float = 0
    memory_usage: int = 0

    def touch(self):
        """Marcar como acessado"""
        self.access_count += 1
        self.last_accessed = time.time()


class LazyModuleLoader:
    """
    Carregador lazy de módulos com gerenciamento de memória
    """

    def __init__(self, unload_threshold: int = 300):  # 5 minutos
        self._modules: Dict[str, ModuleInfo] = {}
        self._factories: Dict[str, Callable] = {}
        self._lock = threading.RLock()
        self._unload_threshold = unload_threshold

        # Thread para limpeza automática
        self._start_cleanup_thread()

    def register_factory(self, name: str, factory: Callable):
        """Registrar factory para criação lazy de módulo"""
        with self._lock:
            self._factories[name] = factory

    def get_module(self, name: str, *args, **kwargs) -> Any:
        """Obter módulo (carrega se necessário)"""
        with self._lock:
            # Verificar se já está carregado
            if name in self._modules:
                module_info = self._modules[name]
                module_info.touch()
                return module_info.instance

            # Carregar módulo
            if name not in self._factories:
                raise ValueError(f"Módulo '{name}' não registrado")

            print(f"🔄 Carregando módulo lazy: {name}")

            factory = self._factories[name]
            instance = factory(*args, **kwargs)

            # Estimar uso de memória
            memory_usage = self._estimate_memory_usage(instance)

            module_info = ModuleInfo(
                name=name,
                instance=instance,
                loaded_at=time.time(),
                memory_usage=memory_usage
            )
            module_info.touch()

            self._modules[name] = module_info

            print(f"✅ Módulo {name} carregado ({memory_usage / 1024:.1f}KB)")

            return instance

    def unload_module(self, name: str):
        """Descarregar módulo da memória"""
        with self._lock:
            if name in self._modules:
                module_info = self._modules[name]

                # Tentar limpar referências
                instance = module_info.instance
                if hasattr(instance, 'cleanup'):
                    instance.cleanup()

                del self._modules[name]
                del instance

                # Forçar garbage collection
                gc.collect()

                print(f"🗑️ Módulo {name} descarregado da memória")

    def _estimate_memory_usage(self, obj: Any) -> int:
        """Estimar uso de memória de um objeto"""
        try:
            return sys.getsizeof(obj)
        except:
            return 1024  # Estimativa padrão

    def _start_cleanup_thread(self):
        """Iniciar thread de limpeza automática"""
        def cleanup_task():
            while True:
                time.sleep(60)  # Verificar a cada minuto
                self._cleanup_unused_modules()

        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()

    def _cleanup_unused_modules(self):
        """Limpar módulos não utilizados"""
        current_time = time.time()

        with self._lock:
            modules_to_unload = []

            for name, module_info in self._modules.items():
                time_since_access = current_time - module_info.last_accessed

                if time_since_access > self._unload_threshold:
                    modules_to_unload.append(name)

            for name in modules_to_unload:
                self.unload_module(name)

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas dos módulos"""
        with self._lock:
            total_memory = sum(m.memory_usage for m in self._modules.values())

            return {
                'loaded_modules': len(self._modules),
                'registered_factories': len(self._factories),
                'total_memory_kb': total_memory / 1024,
                'modules': {
                    name: {
                        'access_count': info.access_count,
                        'memory_kb': info.memory_usage / 1024,
                        'loaded_at': datetime.fromtimestamp(info.loaded_at).isoformat()
                    }
                    for name, info in self._modules.items()
                }
            }


# ============================================================================
# POOL DE CONEXÕES REUTILIZÁVEIS
# ============================================================================

class ConnectionPool:
    """Pool de conexões reutilizáveis para APIs e banco de dados"""

    def __init__(self, factory: Callable, max_size: int = 10, timeout: float = 30):
        self.factory = factory
        self.max_size = max_size
        self.timeout = timeout

        self._pool: List[Any] = []
        self._active: List[Any] = []
        self._lock = threading.Lock()

        # Pré-criar algumas conexões
        self._initialize_pool()

    def _initialize_pool(self):
        """Inicializar pool com conexões básicas"""
        initial_size = min(3, self.max_size)

        for _ in range(initial_size):
            try:
                connection = self.factory()
                self._pool.append(connection)
            except Exception as e:
                print(f"⚠️ Erro ao criar conexão inicial: {e}")

    def get_connection(self) -> Any:
        """Obter conexão do pool"""
        with self._lock:
            # Tentar reutilizar conexão existente
            if self._pool:
                connection = self._pool.pop()
                self._active.append(connection)
                return connection

            # Criar nova conexão se dentro do limite
            if len(self._active) < self.max_size:
                try:
                    connection = self.factory()
                    self._active.append(connection)
                    return connection
                except Exception as e:
                    print(f"❌ Erro ao criar nova conexão: {e}")
                    raise

            # Pool esgotado
            raise RuntimeError("Pool de conexões esgotado")

    def return_connection(self, connection: Any):
        """Retornar conexão ao pool"""
        with self._lock:
            if connection in self._active:
                self._active.remove(connection)

                # Verificar se conexão ainda é válida
                if self._is_connection_valid(connection):
                    self._pool.append(connection)
                else:
                    # Conexão inválida, criar nova
                    try:
                        new_connection = self.factory()
                        self._pool.append(new_connection)
                    except:
                        pass  # Ignorar se não conseguir criar nova

    def _is_connection_valid(self, connection: Any) -> bool:
        """Verificar se conexão ainda é válida"""
        try:
            # Implementar verificação específica por tipo de conexão
            if hasattr(connection, 'ping'):
                return connection.ping()
            return True
        except:
            return False

    def close_all(self):
        """Fechar todas as conexões"""
        with self._lock:
            all_connections = self._pool + self._active

            for connection in all_connections:
                try:
                    if hasattr(connection, 'close'):
                        connection.close()
                except:
                    pass

            self._pool.clear()
            self._active.clear()


# ============================================================================
# SISTEMA DE PRÉ-CARREGAMENTO INTELIGENTE
# ============================================================================

class IntelligentPreloader:
    """Sistema de pré-carregamento baseado em padrões de uso"""

    def __init__(self, loader: LazyModuleLoader):
        self.loader = loader
        self.usage_patterns: Dict[str, List[float]] = {}
        self._monitoring = False

    def start_monitoring(self):
        """Iniciar monitoramento de padrões de uso"""
        self._monitoring = True

        def monitor_task():
            while self._monitoring:
                time.sleep(30)  # Verificar a cada 30 segundos
                self._analyze_patterns()

        monitor_thread = threading.Thread(target=monitor_task, daemon=True)
        monitor_thread.start()

    def record_access(self, module_name: str):
        """Registrar acesso a módulo"""
        current_time = time.time()

        if module_name not in self.usage_patterns:
            self.usage_patterns[module_name] = []

        self.usage_patterns[module_name].append(current_time)

        # Manter apenas últimos 50 acessos
        if len(self.usage_patterns[module_name]) > 50:
            self.usage_patterns[module_name] = self.usage_patterns[module_name][-50:]

    def _analyze_patterns(self):
        """Analisar padrões e pré-carregar módulos previsíveis"""
        current_time = time.time()

        for module_name, access_times in self.usage_patterns.items():
            if len(access_times) < 3:
                continue

            # Calcular intervalo médio entre acessos
            intervals = [access_times[i] - access_times[i-1] 
                        for i in range(1, len(access_times))]

            if not intervals:
                continue

            avg_interval = sum(intervals) / len(intervals)
            last_access = access_times[-1]

            # Se padrão regular e tempo desde último acesso próximo do intervalo
            time_since_last = current_time - last_access

            if (0.8 * avg_interval <= time_since_last <= 1.2 * avg_interval and
                module_name not in self.loader._modules):

                print(f"🧠 Pré-carregando módulo {module_name} (padrão detectado)")
                try:
                    self.loader.get_module(module_name)
                except Exception as e:
                    print(f"⚠️ Erro no pré-carregamento de {module_name}: {e}")


# ============================================================================
# INTEGRAÇÃO COM ERP PRIMOTEX
# ============================================================================

# Instância global do lazy loader
erp_loader = LazyModuleLoader()
erp_preloader = IntelligentPreloader(erp_loader)

# Pool de conexões HTTP para APIs
import requests

def create_http_session():
    """Factory para sessões HTTP otimizadas"""
    session = requests.Session()

    # Configurações de performance
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=3
    )

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # Headers padrão
    session.headers.update({
        'User-Agent': 'ERP-Primotex/1.0',
        'Accept': 'application/json',
        'Connection': 'keep-alive'
    })

    return session

# Pool global de sessões HTTP
http_pool = ConnectionPool(create_http_session, max_size=15)


# ============================================================================
# DECORADORES PARA LAZY LOADING
# ============================================================================

def lazy_module(module_name: str):
    """Decorador para lazy loading de módulos"""
    def decorator(factory_func):
        erp_loader.register_factory(module_name, factory_func)

        def wrapper(*args, **kwargs):
            erp_preloader.record_access(module_name)
            return erp_loader.get_module(module_name, *args, **kwargs)

        return wrapper
    return decorator


def with_connection_pool(pool: ConnectionPool):
    """Decorador para usar pool de conexões"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            connection = pool.get_connection()
            try:
                return func(connection, *args, **kwargs)
            finally:
                pool.return_connection(connection)

        return wrapper
    return decorator


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Registrar factories de módulos
    @lazy_module('clientes_service')
    def create_clientes_service():
        print("Criando serviço de clientes...")
        # Simular carregamento pesado
        time.sleep(0.5)
        return {"service": "clientes", "loaded": True}

    @lazy_module('produtos_service')  
    def create_produtos_service():
        print("Criando serviço de produtos...")
        return {"service": "produtos", "loaded": True}

    # Iniciar monitoramento
    erp_preloader.start_monitoring()

    # Simular uso
    print("=== Teste de Lazy Loading ===")

    # Primeiro acesso (carrega)
    clientes = erp_loader.get_module('clientes_service')
    print(f"Clientes: {clientes}")

    # Segundo acesso (reutiliza)
    clientes2 = erp_loader.get_module('clientes_service')
    print(f"Clientes2: {clientes2 is clientes}")

    # Estatísticas
    stats = erp_loader.get_stats()
    print(f"\\nEstatísticas: {stats}")