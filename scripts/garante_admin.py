"""
Script para garantir a existência do usuário admin com senha padrão segura.
Se não existir, cria. Se existir, atualiza senha e ativa.
"""


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database.config import SessionLocal
from backend.models.user_model import Usuario
from backend.auth.jwt_handler import hash_password

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@primotex.com.br"
ADMIN_PASSWORD = "admin123"

session = SessionLocal()

user = session.query(Usuario).filter(Usuario.username == ADMIN_USERNAME).first()

if user:
    user.senha_hash = hash_password(ADMIN_PASSWORD)
    user.ativo = True
    user.email = ADMIN_EMAIL
    print(f"Usuário admin já existia. Senha e status atualizados.")
else:
    user = Usuario(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        senha_hash=hash_password(ADMIN_PASSWORD),
        nome_completo="Administrador do Sistema",
        perfil="Administrador",
        ativo=True
    )
    session.add(user)
    print(f"Usuário admin criado.")

session.commit()
session.close()
print("Operação concluída.")
