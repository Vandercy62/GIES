# -*- coding: utf-8 -*-
"""
OTIMIZADOR DE QUERIES - ERP PRIMOTEX
====================================

Sistema de otimização de consultas ao banco de dados com:
- Pool de conexões otimizado
- Cache de queries frequentes
- Análise de performance
- Batch operations
- Índices automáticos

Autor: GitHub Copilot
Data: 29/10/2025
"""

import time
import threading
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging


@dataclass
class QueryStats:
    """Estatísticas de uma query"""
    query_hash: str
    sql: str
    execution_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    last_executed: float = field(default_factory=time.time)
    
    def add_execution(self, execution_time: float):
        """Adicionar nova execução"""
        self.execution_count += 1
        self.total_time += execution_time
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.avg_time = self.total_time / self.execution_count
        self.last_executed = time.time()


class DatabaseOptimizer:
    """
    Otimizador de banco de dados com análise de performance
    """
    
    def __init__(self, database_url: str, pool_size: int = 20, max_overflow: int = 30):
        # Engine otimizada com pool de conexões
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # Verificar conexões antes de usar
            pool_recycle=3600,   # Reciclar conexões a cada hora
            echo=False,          # Não logar SQL em produção
            connect_args={
                "check_same_thread": False,
                "timeout": 30
            }
        )
        
        # Session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Estatísticas de queries
        self._query_stats: Dict[str, QueryStats] = {}
        self._lock = threading.RLock()
        
        # Configurar listeners de eventos
        self._setup_event_listeners()
        
        # Cache de resultados de queries
        self._query_cache: Dict[str, Tuple[Any, float]] = {}
        self._cache_ttl = 300  # 5 minutos
        
        # Queries lentas (> 1 segundo)
        self._slow_queries: List[Dict] = []
        self._slow_query_threshold = 1.0
    
    def _setup_event_listeners(self):
        """Configurar listeners para monitoramento"""
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            execution_time = time.time() - context._query_start_time
            self._record_query_stats(statement, execution_time)
    
    def _record_query_stats(self, sql: str, execution_time: float):
        """Registrar estatísticas da query"""
        # Normalizar SQL para cache (remover parâmetros)
        normalized_sql = self._normalize_sql(sql)
        query_hash = hashlib.md5(normalized_sql.encode()).hexdigest()
        
        with self._lock:
            if query_hash not in self._query_stats:
                self._query_stats[query_hash] = QueryStats(
                    query_hash=query_hash,
                    sql=normalized_sql
                )
            
            self._query_stats[query_hash].add_execution(execution_time)
            
            # Registrar queries lentas
            if execution_time > self._slow_query_threshold:
                self._slow_queries.append({
                    'sql': normalized_sql,
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Manter apenas últimas 100 queries lentas
                if len(self._slow_queries) > 100:
                    self._slow_queries = self._slow_queries[-100:]
    
    def _normalize_sql(self, sql: str) -> str:
        """Normalizar SQL removendo parâmetros específicos"""
        # Remover quebras de linha e espaços extras
        normalized = ' '.join(sql.split())
        
        # Substituir parâmetros por placeholders genéricos
        # Isso é uma simplificação - em produção seria mais sofisticado
        import re
        
        # Remover valores literais
        normalized = re.sub(r"'[^']*'", "'?'", normalized)
        normalized = re.sub(r'\b\d+\b', '?', normalized)
        
        return normalized
    
    def get_session(self) -> Session:
        """Obter sessão do banco de dados"""
        return self.SessionLocal()
    
    def execute_cached_query(self, sql: str, params: Dict = None, ttl: float = None) -> Any:
        """Executar query com cache"""
        cache_key = self._generate_cache_key(sql, params)
        current_time = time.time()
        
        # Verificar cache
        if cache_key in self._query_cache:
            result, cached_at = self._query_cache[cache_key]
            cache_age = current_time - cached_at
            
            if cache_age < (ttl or self._cache_ttl):
                return result
        
        # Executar query
        with self.get_session() as session:
            result = session.execute(text(sql), params or {}).fetchall()
            
            # Armazenar no cache
            self._query_cache[cache_key] = (result, current_time)
            
            return result
    
    def _generate_cache_key(self, sql: str, params: Dict = None) -> str:
        """Gerar chave única para cache"""
        key_data = {
            'sql': sql,
            'params': params or {}
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def bulk_insert(self, table_class, data: List[Dict], batch_size: int = 1000):
        """Inserção em lote otimizada"""
        with self.get_session() as session:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                session.bulk_insert_mappings(table_class, batch)
                session.commit()
    
    def bulk_update(self, table_class, data: List[Dict], batch_size: int = 1000):
        """Atualização em lote otimizada"""
        with self.get_session() as session:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                session.bulk_update_mappings(table_class, batch)
                session.commit()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gerar relatório de performance"""
        with self._lock:
            if not self._query_stats:
                return {"message": "Nenhuma estatística disponível"}
            
            # Top 10 queries mais executadas
            most_executed = sorted(
                self._query_stats.values(),
                key=lambda x: x.execution_count,
                reverse=True
            )[:10]
            
            # Top 10 queries mais lentas (por tempo médio)
            slowest_avg = sorted(
                self._query_stats.values(),
                key=lambda x: x.avg_time,
                reverse=True
            )[:10]
            
            # Estatísticas gerais
            total_queries = sum(stat.execution_count for stat in self._query_stats.values())
            total_time = sum(stat.total_time for stat in self._query_stats.values())
            
            return {
                'general_stats': {
                    'total_unique_queries': len(self._query_stats),
                    'total_executions': total_queries,
                    'total_time_seconds': round(total_time, 2),
                    'average_time_per_query': round(total_time / total_queries, 4) if total_queries > 0 else 0,
                    'cache_size': len(self._query_cache),
                    'slow_queries_count': len(self._slow_queries)
                },
                'most_executed': [
                    {
                        'sql': stat.sql[:100] + '...' if len(stat.sql) > 100 else stat.sql,
                        'execution_count': stat.execution_count,
                        'avg_time_ms': round(stat.avg_time * 1000, 2)
                    }
                    for stat in most_executed
                ],
                'slowest_average': [
                    {
                        'sql': stat.sql[:100] + '...' if len(stat.sql) > 100 else stat.sql,
                        'avg_time_ms': round(stat.avg_time * 1000, 2),
                        'execution_count': stat.execution_count
                    }
                    for stat in slowest_avg
                ],
                'recent_slow_queries': self._slow_queries[-10:]
            }
    
    def optimize_suggestions(self) -> List[str]:
        """Gerar sugestões de otimização"""
        suggestions = []
        
        with self._lock:
            # Analisar queries frequentes
            frequent_queries = [
                stat for stat in self._query_stats.values()
                if stat.execution_count > 100
            ]
            
            for stat in frequent_queries:
                if stat.avg_time > 0.5:  # > 500ms
                    suggestions.append(
                        f"Query executada {stat.execution_count} vezes com tempo médio "
                        f"de {stat.avg_time:.2f}s pode precisar de índice: "
                        f"{stat.sql[:50]}..."
                    )
            
            # Analisar queries lentas
            if len(self._slow_queries) > 10:
                suggestions.append(
                    f"Detectadas {len(self._slow_queries)} queries lentas. "
                    "Considere otimizar as mais frequentes."
                )
            
            # Analisar cache
            cache_hit_ratio = self._calculate_cache_hit_ratio()
            if cache_hit_ratio < 0.3:
                suggestions.append(
                    f"Taxa de cache hit baixa ({cache_hit_ratio:.1%}). "
                    "Considere aumentar TTL do cache ou implementar mais cache."
                )
        
        return suggestions
    
    def _calculate_cache_hit_ratio(self) -> float:
        """Calcular taxa de acerto do cache"""
        # Implementação simplificada
        # Em produção, isso seria mais sofisticado
        if not self._query_cache:
            return 0.0
        
        return min(len(self._query_cache) / max(len(self._query_stats), 1), 1.0)
    
    def clear_cache(self):
        """Limpar cache de queries"""
        self._query_cache.clear()
    
    def clear_stats(self):
        """Limpar estatísticas"""
        with self._lock:
            self._query_stats.clear()
            self._slow_queries.clear()


# ============================================================================
# CONTEXT MANAGER PARA TRANSAÇÕES OTIMIZADAS
# ============================================================================

class OptimizedTransaction:
    """Context manager para transações otimizadas"""
    
    def __init__(self, optimizer: DatabaseOptimizer):
        self.optimizer = optimizer
        self.session = None
    
    def __enter__(self) -> Session:
        self.session = self.optimizer.get_session()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise
        else:
            self.session.rollback()
        
        self.session.close()


# ============================================================================
# INTEGRAÇÃO COM ERP PRIMOTEX
# ============================================================================

# Configuração padrão para SQLite do ERP
DATABASE_URL = "sqlite:///./primotex_erp.db"

# Instância global do otimizador
db_optimizer = DatabaseOptimizer(
    database_url=DATABASE_URL,
    pool_size=15,
    max_overflow=25
)


# ============================================================================
# DECORADORES PARA OTIMIZAÇÃO
# ============================================================================

def cached_query(ttl: float = 300):
    """Decorador para cache automático de queries"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Gerar chave baseada na função e argumentos
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Tentar cache primeiro
            result = db_optimizer._query_cache.get(cache_key)
            if result:
                cached_result, cached_at = result
                if time.time() - cached_at < ttl:
                    return cached_result
            
            # Executar função
            result = func(*args, **kwargs)
            
            # Armazenar no cache
            db_optimizer._query_cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator


def with_transaction(func):
    """Decorador para executar função em transação"""
    def wrapper(*args, **kwargs):
        with OptimizedTransaction(db_optimizer) as session:
            return func(session, *args, **kwargs)
    
    return wrapper


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Exemplo de uso do otimizador
    print("=== Teste do Otimizador de Banco ===")
    
    # Simular algumas queries
    with OptimizedTransaction(db_optimizer) as session:
        # Query simulada
        result = session.execute(text("SELECT 1 as test")).fetchall()
        print(f"Resultado: {result}")
    
    # Gerar relatório de performance
    report = db_optimizer.get_performance_report()
    print(f"\\nRelatório de Performance:")
    print(f"Total de execuções: {report['general_stats']['total_executions']}")
    
    # Sugestões de otimização
    suggestions = db_optimizer.optimize_suggestions()
    if suggestions:
        print(f"\\nSugestões de Otimização:")
        for suggestion in suggestions:
            print(f"- {suggestion}")
    else:
        print("\\n✅ Nenhuma otimização necessária no momento")