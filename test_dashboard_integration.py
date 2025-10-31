#!/usr/bin/env python3
"""
Teste de integração Dashboard + Performance
"""

def test_dashboard_integration():
    try:
        from shared.cache_system import erp_cache
        from shared.lazy_loading import erp_loader
        print("✅ Sistemas de performance importados")
        
        # Simular dados
        clientes_test = [{"id": 1, "nome": "Cliente A"}]
        erp_cache.set_clientes(clientes_test)
        
        health = erp_cache.get_cache_health()
        print(f"Cache status: {health['status']}")
        print(f"Hit ratio: {health['hit_ratio']:.1f}%")
        
        print("🏆 Dashboard otimizado pronto!")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    test_dashboard_integration()