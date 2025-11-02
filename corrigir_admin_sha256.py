#!/usr/bin/env python3
"""
Script para corrigir usuário admin usando SHA256 simples
Substitui bcrypt problemático por solução funcional
"""

import sqlite3
import hashlib

def criar_hash_simples(senha):
    """Cria hash SHA256 com salt"""
    salt = "primotex_salt_2025_secure_hash"
    return hashlib.sha256((senha + salt).encode()).hexdigest()

def corrigir_admin_sha256():
    """Corrige o usuário admin com SHA256"""
    
    try:
        nova_senha = "admin123"
        novo_hash = criar_hash_simples(nova_senha)
        
        print(f"🔧 Gerando hash SHA256 para: {nova_senha}")
        print(f"✅ Hash: {novo_hash[:20]}...")
        
        # Conectar ao banco
        conn = sqlite3.connect('primotex_erp.db')
        cursor = conn.cursor()
        
        # Atualizar senha
        cursor.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE username = 'admin'",
            (novo_hash,)
        )
        
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ Senha atualizada com SHA256!")
            conn.close()
            return True
        else:
            print("❌ Nenhum registro atualizado")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🛠️ CORRIGINDO ADMIN COM SHA256")
    print("=" * 40)
    
    if corrigir_admin_sha256():
        print("\n✅ ADMIN CORRIGIDO!")
        print("⚠️ Agora vou atualizar o sistema para usar SHA256")
    else:
        print("\n❌ FALHA NA CORREÇÃO")