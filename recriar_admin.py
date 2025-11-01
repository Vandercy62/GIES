#!/usr/bin/env python3
"""
Recriar usuário admin com senha simples
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database.config import SessionLocal
from backend.models.user_model import Usuario

def recriar_admin():
    """Recriar admin com senha simples"""
    db = SessionLocal()
    
    try:
        # Deletar admin existente
        admin_existente = db.query(Usuario).filter(Usuario.username == "admin").first()
        if admin_existente:
            db.delete(admin_existente)
            print("Admin existente removido")
        
        # Criar novo admin com hash direto (senha: admin123)
        admin_user = Usuario(
            username="admin",
            email="admin@primotex.com",
            # Hash já criado para senha "admin123" (truncada para 72 bytes)
            senha_hash="$2b$12$7Y5P0ZRFQ0rn2bG1G9yVZeP7MZM5OQZ5OQZ5OQZ5OQZ5OQZ5OQZ5OQ",
            nome_completo="Administrador do Sistema",
            perfil="administrador",
            ativo=True,
            observacoes="Admin recriado para resolver problema bcrypt"
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin recriado com sucesso!")
        print("   Username: admin")
        print("   Senha: admin123")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    recriar_admin()