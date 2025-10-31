"""
SISTEMA ERP PRIMOTEX - SCRIPT DE INICIALIZAÇÃO
=============================================

Script para criar dados iniciais do sistema.
Criação do usuário administrador padrão.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database.config import SessionLocal, init_database
from backend.models.user_model import Usuario
from backend.auth.jwt_handler import hash_password

def create_admin_user():
    """Criar usuário administrador padrão"""
    
    # Inicializar banco
    print("🔧 Inicializando banco de dados...")
    success = init_database()
    if not success:
        print("❌ Erro ao inicializar banco de dados")
        return False
    
    # Criar sessão
    db: Session = SessionLocal()
    
    try:
        # Verificar se já existe administrador
        existing_admin = db.query(Usuario).filter(
            Usuario.perfil == "administrador"
        ).first()
        
        if existing_admin:
            print(f"✅ Administrador já existe: {existing_admin.username}")
            return True
        
        # Criar administrador padrão
        admin_user = Usuario(
            username="admin",
            email="admin@primotex.com",
            senha_hash=hash_password("admin123"),
            nome_completo="Administrador do Sistema",
            perfil="administrador",
            ativo=True,
            observacoes="Usuário administrador criado automaticamente"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Usuário administrador criado com sucesso!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print("   Senha: admin123")
        print("   ⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar administrador: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

def main():
    """Função principal"""
    print("=" * 50)
    print("SISTEMA ERP PRIMOTEX - INICIALIZAÇÃO")
    print("=" * 50)
    
    success = create_admin_user()
    
    if success:
        print("\n✅ Inicialização concluída com sucesso!")
        print("\nPara usar o sistema:")
        print("1. Execute: python -m backend.api.main")
        print("2. Acesse: http://localhost:8000/docs")
        print("3. Faça login com:")
        print("   - Username: admin")
        print("   - Senha: admin123")
    else:
        print("\n❌ Erro na inicialização!")
        sys.exit(1)

if __name__ == "__main__":
    main()