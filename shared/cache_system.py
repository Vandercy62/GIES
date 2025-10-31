# -*- coding: utf-8 -*-
"""
SISTEMA DE CACHE AVANÇADO - ERP PRIMOTEX
========================================

Sistema de cache em memória para otimização de performance com:
- Cache TTL (Time To Live) configurável
- Invalidação automática e manual
- Métricas de hit/miss
- Compressão de dados grandes
- Cache hierárquico por módulo

Autor: GitHub Copilot
Data: 29/10/2025
"""

import time
import pickle
import gzip
import threading
from typing import Any, Dict, Optional, Tuple, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import hashlib


@dataclass
class CacheEntry:
    """Entrada individual do cache"""
    data: Any
    created_at: float
    ttl: float
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    compressed: bool = False
    
    def is_expired(self) -> bool:
        """Verificar se entrada expirou"""
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """Marcar como acessado"""
        self.access_count += 1
        self.last_accessed = time.time()


@dataclass
class CacheStats:
    """Estatísticas do cache"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    entries: int = 0
    memory_usage: int = 0
    
    @property
    def hit_ratio(self) -> float:
        """Taxa de acerto do cache"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class AdvancedCache:
    """
    Sistema de cache avançado com TTL, compressão e métricas
    """
    
    def __init__(self, 
                 max_size: int = 1000,
                 default_ttl: float = 300,  # 5 minutos
                 cleanup_interval: float = 60,  # 1 minuto
                 compression_threshold: int = 1024):  # 1KB
        
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.compression_threshold = compression_threshold
        
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = CacheStats()
        
        # Thread de limpeza automática
        self._cleanup_timer = None
        self._start_cleanup_timer(cleanup_interval)
    
    def _start_cleanup_timer(self, interval: float):
        """Iniciar timer de limpeza automática"""
        def cleanup_task():
            self.cleanup_expired()
            self._start_cleanup_timer(interval)
        
        self._cleanup_timer = threading.Timer(interval, cleanup_task)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()
    
    def _generate_key(self, namespace: str, key: str, params: Dict = None) -> str:
        """Gerar chave única para cache"""
        base_key = f"{namespace}:{key}"
        if params:
            # Criar hash dos parâmetros para chave única
            params_str = json.dumps(params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            base_key += f":{params_hash}"
        return base_key
    
    def _compress_data(self, data: Any) -> Tuple[bytes, bool]:
        """Comprimir dados se necessário"""
        serialized = pickle.dumps(data)
        
        if len(serialized) > self.compression_threshold:
            compressed = gzip.compress(serialized)
            return compressed, True
        
        return serialized, False
    
    def _decompress_data(self, data: bytes, compressed: bool) -> Any:
        """Descomprimir dados"""
        if compressed:
            decompressed = gzip.decompress(data)
            return pickle.loads(decompressed)
        
        return pickle.loads(data)
    
    def get(self, namespace: str, key: str, params: Dict = None) -> Optional[Any]:
        """Obter valor do cache"""
        cache_key = self._generate_key(namespace, key, params)
        
        with self._lock:
            entry = self._cache.get(cache_key)
            
            if entry is None:
                self._stats.misses += 1
                return None
            
            if entry.is_expired():
                del self._cache[cache_key]
                self._stats.misses += 1
                self._stats.evictions += 1
                return None
            
            # Cache hit
            entry.touch()
            self._stats.hits += 1
            
            return self._decompress_data(entry.data, entry.compressed)
    
    def set(self, namespace: str, key: str, value: Any, 
            ttl: Optional[float] = None, params: Dict = None):
        """Armazenar valor no cache"""
        cache_key = self._generate_key(namespace, key, params)
        ttl = ttl or self.default_ttl
        
        # Comprimir se necessário
        compressed_data, is_compressed = self._compress_data(value)
        
        entry = CacheEntry(
            data=compressed_data,
            created_at=time.time(),
            ttl=ttl,
            compressed=is_compressed
        )
        
        with self._lock:
            # Remover entrada antiga se existir
            if cache_key in self._cache:
                del self._cache[cache_key]
            
            # Verificar limite de tamanho
            if len(self._cache) >= self.max_size:
                self._evict_lru()
            
            self._cache[cache_key] = entry
            self._stats.entries = len(self._cache)
    
    def _evict_lru(self):
        """Remover entrada menos recentemente usada"""
        if not self._cache:
            return
        
        # Encontrar entrada mais antiga
        oldest_key = min(self._cache.keys(), 
                        key=lambda k: self._cache[k].last_accessed)
        
        del self._cache[oldest_key]
        self._stats.evictions += 1
    
    def invalidate(self, namespace: str, key: str = None, params: Dict = None):
        """Invalidar cache"""
        with self._lock:
            if key:
                # Invalidar chave específica
                cache_key = self._generate_key(namespace, key, params)
                if cache_key in self._cache:
                    del self._cache[cache_key]
            else:
                # Invalidar todo o namespace
                keys_to_remove = [k for k in self._cache.keys() 
                                if k.startswith(f"{namespace}:")]
                
                for key_to_remove in keys_to_remove:
                    del self._cache[key_to_remove]
            
            self._stats.entries = len(self._cache)
    
    def cleanup_expired(self):
        """Limpar entradas expiradas"""
        with self._lock:
            expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
            
            for key in expired_keys:
                del self._cache[key]
                self._stats.evictions += 1
            
            self._stats.entries = len(self._cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do cache"""
        with self._lock:
            return {
                'hits': self._stats.hits,
                'misses': self._stats.misses,
                'hit_ratio': round(self._stats.hit_ratio * 100, 2),
                'entries': self._stats.entries,
                'evictions': self._stats.evictions,
                'max_size': self.max_size,
                'memory_usage_mb': self._estimate_memory_usage() / (1024 * 1024)
            }
    
    def _estimate_memory_usage(self) -> int:
        """Estimar uso de memória (aproximado)"""
        total_size = 0
        for entry in self._cache.values():
            total_size += len(entry.data) if isinstance(entry.data, bytes) else 1024
        return total_size
    
    def clear(self):
        """Limpar todo o cache"""
        with self._lock:
            self._cache.clear()
            self._stats = CacheStats()
    
    def shutdown(self):
        """Parar timer de limpeza"""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()


# ============================================================================
# CACHE ESPECÍFICO PARA MÓDULOS DO ERP
# ============================================================================

class ERPCache:
    """Cache específico para módulos do ERP Primotex"""
    
    def __init__(self):
        # Cache principal com configurações otimizadas para ERP
        self.cache = AdvancedCache(
            max_size=2000,
            default_ttl=600,  # 10 minutos para dados de ERP
            cleanup_interval=120,  # Limpeza a cada 2 minutos
            compression_threshold=2048  # 2KB para dados maiores
        )
        
        # TTLs específicos por tipo de dado
        self.ttl_config = {
            'clientes': 900,      # 15 min - dados que mudam pouco
            'produtos': 900,      # 15 min
            'estoque': 300,       # 5 min - dados que mudam frequentemente
            'ordem_servico': 180, # 3 min - dados dinâmicos
            'agendamento': 180,   # 3 min
            'financeiro': 120,    # 2 min - dados críticos
            'comunicacao': 300,   # 5 min
            'dashboard': 60,      # 1 min - métricas em tempo real
            'relatorios': 1800,   # 30 min - relatórios demoram para mudar
        }
    
    # Métodos específicos para cada módulo
    def get_clientes(self, filtros: Dict = None) -> Optional[List]:
        """Cache de clientes"""
        return self.cache.get('clientes', 'list', filtros)
    
    def set_clientes(self, data: List, filtros: Dict = None):
        """Armazenar clientes no cache"""
        ttl = self.ttl_config['clientes']
        self.cache.set('clientes', 'list', data, ttl, filtros)
    
    def get_produtos(self, filtros: Dict = None) -> Optional[List]:
        """Cache de produtos"""
        return self.cache.get('produtos', 'list', filtros)
    
    def set_produtos(self, data: List, filtros: Dict = None):
        """Armazenar produtos no cache"""
        ttl = self.ttl_config['produtos']
        self.cache.set('produtos', 'list', data, ttl, filtros)
    
    def get_dashboard_metrics(self, modulo: str) -> Optional[Dict]:
        """Cache de métricas do dashboard"""
        return self.cache.get('dashboard', f'metrics_{modulo}')
    
    def set_dashboard_metrics(self, modulo: str, data: Dict):
        """Armazenar métricas do dashboard"""
        ttl = self.ttl_config['dashboard']
        self.cache.set('dashboard', f'metrics_{modulo}', data, ttl)
    
    def invalidate_module(self, modulo: str):
        """Invalidar cache de um módulo específico"""
        self.cache.invalidate(modulo)
    
    def get_cache_health(self) -> Dict[str, Any]:
        """Verificar saúde do cache"""
        stats = self.cache.get_stats()
        
        # Adicionar informações específicas do ERP
        health = {
            **stats,
            'status': 'healthy' if stats['hit_ratio'] > 70 else 'degraded',
            'modules_cached': len(set(k.split(':')[0] for k in self.cache._cache.keys())),
            'ttl_config': self.ttl_config
        }
        
        return health


# Instância global do cache ERP
erp_cache = ERPCache()


# ============================================================================
# DECORADOR PARA CACHE AUTOMÁTICO
# ============================================================================

def cached(namespace: str, ttl: Optional[float] = None, 
          key_func: Optional[callable] = None):
    """
    Decorador para cache automático de funções
    
    Args:
        namespace: Namespace do cache
        ttl: Time to live específico
        key_func: Função para gerar chave personalizada
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Gerar chave do cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = func.__name__
            
            # Tentar obter do cache
            result = erp_cache.cache.get(namespace, cache_key, kwargs)
            
            if result is not None:
                return result
            
            # Executar função e armazenar resultado
            result = func(*args, **kwargs)
            erp_cache.cache.set(namespace, cache_key, result, ttl, kwargs)
            
            return result
        
        return wrapper
    return decorator


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Teste básico do cache
    cache = ERPCache()
    
    # Simular dados de clientes
    clientes_data = [
        {"id": 1, "nome": "Cliente 1", "email": "cliente1@test.com"},
        {"id": 2, "nome": "Cliente 2", "email": "cliente2@test.com"}
    ]
    
    # Armazenar no cache
    cache.set_clientes(clientes_data)
    
    # Recuperar do cache
    cached_clientes = cache.get_clientes()
    print(f"Clientes do cache: {len(cached_clientes) if cached_clientes else 0}")
    
    # Verificar saúde do cache
    health = cache.get_cache_health()
    print(f"Saúde do cache: {health['status']}")
    print(f"Hit ratio: {health['hit_ratio']}%")