
"""
Script para redefinir a senha do usuário admin no ERP Primotex.
Uso: python scripts/reset_admin_password.py
"""

# Corrigir path para permitir import relativo ao rodar como script
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database.config import engine, SessionLocal
from backend.models.user_model import Usuario
from backend.auth.jwt_handler import hash_password

NOVO_HASH = hash_password("admin123")

session = SessionLocal()

try:
    admin = session.query(Usuario).filter(Usuario.username == "admin").first()
    if not admin:
        print("Usuário admin não encontrado!")
    else:
        admin.senha_hash = NOVO_HASH
        session.commit()
        print("Senha do admin redefinida para 'admin123'.")
finally:
    session.close()
