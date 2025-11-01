#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORREÇÃO DO PERFIL ADMIN
========================

Atualiza o perfil do usuário admin para o novo formato.

Data: 01/11/2025
Status: Correção
"""

from sqlalchemy import text
from backend.database.config import SessionLocal


def corrigir_perfil_admin():
    """Corrigir perfil do usuário admin"""
    db = SessionLocal()
    
    try:
        print("🔧 CORRIGINDO PERFIL DO ADMIN")
        print("=" * 50)
        
        # Atualizar perfil do admin
        result = db.execute(text("""
            UPDATE usuarios 
            SET perfil = 'administrador' 
            WHERE username = 'admin' AND perfil != 'administrador'
        """))
        
        db.commit()
        
        print(f"✅ {result.rowcount} usuário(s) atualizado(s)")
        
        # Verificar resultado
        admin_user = db.execute(text("""
            SELECT username, perfil FROM usuarios WHERE username = 'admin'
        """)).fetchone()
        
        if admin_user:
            print(f"✅ Admin atual: {admin_user[0]} -> {admin_user[1]}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
        
    finally:
        db.close()


if __name__ == "__main__":
    corrigir_perfil_admin()