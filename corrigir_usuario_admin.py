#!/usr/bin/env python3
"""
Script para corrigir o usuário admin
Recria o hash da senha de forma segura
"""

import sqlite3
import sys
sys.path.append('.')

from backend.auth.jwt_handler import hash_password

def corrigir_admin():
    """Corrige o usuário admin com nova senha hash"""
    
    try:
        # Nova senha segura e simples
        nova_senha = "admin123"
        
        print(f"🔧 Gerando novo hash para senha: {nova_senha}")
        novo_hash = hash_password(nova_senha)
        print(f"✅ Hash gerado com {len(novo_hash)} caracteres")
        
        # Conectar ao banco
        conn = sqlite3.connect('primotex_erp.db')
        cursor = conn.cursor()
        
        # Verificar usuário atual
        cursor.execute("SELECT username, LENGTH(senha_hash) FROM usuarios WHERE username = 'admin'")
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"📊 Usuário atual: {resultado[0]}, hash antigo: {resultado[1]} chars")
        else:
            print("❌ Usuário admin não encontrado!")
            return False
        
        # Atualizar senha
        cursor.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE username = 'admin'",
            (novo_hash,)
        )
        
        # Verificar se atualizou
        if cursor.rowcount > 0:
            conn.commit()
            print("✅ Senha do usuário admin atualizada com sucesso!")
            
            # Verificar nova senha
            cursor.execute("SELECT LENGTH(senha_hash) FROM usuarios WHERE username = 'admin'")
            novo_tamanho = cursor.fetchone()[0]
            print(f"📊 Novo hash: {novo_tamanho} caracteres")
            
            conn.close()
            return True
        else:
            print("❌ Nenhum registro foi atualizado")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Erro ao corrigir usuário admin: {e}")
        return False

if __name__ == "__main__":
    print("🛠️ CORRIGINDO USUÁRIO ADMIN")
    print("=" * 40)
    
    sucesso = corrigir_admin()
    
    if sucesso:
        print("\n🎉 CORREÇÃO CONCLUÍDA!")
        print("✅ Credenciais: admin / admin123")
        print("✅ Login deve funcionar agora")
    else:
        print("\n❌ FALHA NA CORREÇÃO")
        print("Verifique os logs de erro acima")