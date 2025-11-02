#!/usr/bin/env python3
"""
Correção rápida para erro ForwardRef no ERP Primotex
"""

import subprocess
import sys
import os

def corrigir_dependencias():
    """Corrige dependências problemáticas rapidamente"""
    print("🔧 CORREÇÃO RÁPIDA - ERP PRIMOTEX")
    print("=" * 50)
    
    # Comando de correção
    comando = [
        sys.executable, "-m", "pip", "install", 
        "--upgrade", "--force-reinstall",
        "fastapi==0.104.1",
        "pydantic==1.10.12", 
        "uvicorn==0.24.0"
    ]
    
    try:
        print("⚙️ Reinstalando dependências críticas...")
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print("✅ Dependências corrigidas!")
            return True
        else:
            print(f"❌ Erro: {resultado.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def testar_sistema():
    """Teste rápido após correção"""
    try:
        print("\n🧪 Testando sistema...")
        
        # Teste básico de importação
        import fastapi
        import pydantic
        import uvicorn
        
        print(f"✅ FastAPI: {fastapi.__version__}")
        print(f"✅ Pydantic: {pydantic.VERSION}")
        print(f"✅ Uvicorn: {uvicorn.__version__}")
        
        # Teste do backend
        sys.path.append(os.path.join(os.getcwd(), 'backend'))
        from backend.api.main import app
        
        print("✅ Backend carregado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 CORREÇÃO AUTOMÁTICA - ERP PRIMOTEX")
    print("=" * 50)
    
    # Passo 1: Corrigir dependências
    if not corrigir_dependencias():
        print("\n❌ Falha na correção de dependências")
        print("💡 Tente executar manualmente:")
        print("   pip install fastapi==0.104.1 pydantic==1.10.12")
        return False
    
    # Passo 2: Testar sistema
    if not testar_sistema():
        print("\n⚠️ Sistema ainda tem problemas")
        print("💡 Use os sistemas alternativos:")
        print("   python sistema_recepcao_simples.py")
        return False
    
    print("\n🎉 SISTEMA CORRIGIDO!")
    print("=" * 50)
    print("✅ Agora você pode usar:")
    print("   • python configurador_rede.py")
    print("   • python -m uvicorn backend.api.main:app --port 8002")
    print("   • ERP_Primotex_Completo.bat")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main()