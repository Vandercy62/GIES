#!/usr/bin/env python3
"""
Criar usuário de teste simples para validação
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database.config import SessionLocal
from backend.models.user_model import Usuario
import hashlib

def criar_usuario_teste():
    """Criar usuário de teste simples"""
    db = SessionLocal()
    
    try:
        # Verificar se já existe
        teste_user = db.query(Usuario).filter(Usuario.username == "teste").first()
        if teste_user:
            print("Usuário teste já existe")
            return
        
        # Hash simples da senha "123456"
        senha_hash = "$2b$12$XGn6KPaFWqQZHm8F7wGFwe1Y1.OwGJKJZmQ8FuB.HDOC6y9pCjviu"
        
        # Criar usuário teste
        novo_user = Usuario(
            username="teste",
            email="teste@primotex.com", 
            senha_hash=senha_hash,
            nome_completo="Usuario Teste",
            perfil="administrador",
            ativo=True,
            observacoes="Usuario para testes"
        )
        
        db.add(novo_user)
        db.commit()
        
        print("✅ Usuário teste criado!")
        print("   Username: teste")
        print("   Senha: 123456")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    criar_usuario_teste()