#!/usr/bin/env python3
"""
Corrigir usuário admin com senha mais simples
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database.config import SessionLocal
from backend.models.user_model import Usuario
from backend.auth.jwt_handler import hash_password

def corrigir_admin():
    """Corrigir senha do admin"""
    db = SessionLocal()
    
    try:
        # Buscar admin
        admin = db.query(Usuario).filter(Usuario.username == "admin").first()
        
        if not admin:
            print("Admin não encontrado")
            return
        
        # Senha mais simples que funciona com bcrypt
        nova_senha = "admin"
        # Truncar para 72 bytes se necessário
        senha_truncada = nova_senha.encode('utf-8')[:72].decode('utf-8')
        
        admin.senha_hash = hash_password(senha_truncada)
        db.commit()
        
        print(f"✅ Senha do admin atualizada para: {nova_senha}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    corrigir_admin()