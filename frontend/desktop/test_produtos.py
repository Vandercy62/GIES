"""
Teste do módulo de produtos
"""

if __name__ == "__main__":
    print("🧪 Testando módulo de produtos...")
    
    try:
        import produtos_window
        print("✅ Módulo de produtos importado com sucesso!")
        
        # Dados de usuário mock
        user_data = {
            "access_token": "mock_token",
            "user": {
                "username": "admin",
                "nome_completo": "Administrador"
            }
        }
        
        print("✅ Criando janela de produtos...")
        app = produtos_window.ProdutosWindow(user_data)
        
        print("✅ Módulo de produtos funcionando!")
        print("📦 Abrindo interface...")
        
        app.run()
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()