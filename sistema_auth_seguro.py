#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE AUTENTICAÇÃO SEGURO - VERSÃO CORRIGIDA
================================================

Reescrita completa do sistema de autenticação com foco em segurança.

PROBLEMAS IDENTIFICADOS E CORRIGIDOS:
1. Encoding UTF-8 incorreto no bcrypt
2. Truncamento de senha mal implementado  
3. Configuração do passlib inadequada
4. Validação de bytes vs caracteres

Data: 01/11/2025
Status: Implementação Segura
"""

import os
import jwt
import bcrypt
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple


class SistemaAutenticacaoSeguro:
    """Sistema de autenticação com segurança aprimorada"""
    
    def __init__(self):
        self.SECRET_KEY = os.getenv("JWT_SECRET_KEY", "primotex_secret_key_2025_dev")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas
        self.MAX_PASSWORD_BYTES = 72  # Limite real do bcrypt
        
    def _truncate_password_safely(self, password: str) -> str:
        """
        Truncar senha respeitando limite de bytes do bcrypt.
        
        Args:
            password: Senha original
            
        Returns:
            Senha truncada seguramente
        """
        # Converter para bytes UTF-8
        password_bytes = password.encode('utf-8')
        
        # Se está dentro do limite, retornar original
        if len(password_bytes) <= self.MAX_PASSWORD_BYTES:
            return password
        
        # Truncar em bytes e decodificar seguramente
        truncated_bytes = password_bytes[:self.MAX_PASSWORD_BYTES]
        
        # Garantir que não cortamos no meio de um caractere UTF-8
        try:
            return truncated_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Se cortou no meio de um caractere, remover último byte
            for i in range(1, 5):  # UTF-8 máximo 4 bytes por caractere
                try:
                    return truncated_bytes[:-i].decode('utf-8')
                except UnicodeDecodeError:
                    continue
            # Fallback: usar apenas ASCII
            return password.encode('ascii', 'ignore').decode('ascii')[:72]
    
    def hash_password(self, password: str) -> str:
        """
        Hash seguro de senha usando bcrypt direto.
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash bcrypt da senha
        """
        # Truncar senha seguramente
        safe_password = self._truncate_password_safely(password)
        
        # Converter para bytes UTF-8
        password_bytes = safe_password.encode('utf-8')
        
        # Gerar salt e hash com bcrypt direto
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verificar senha usando bcrypt direto.
        
        Args:
            plain_password: Senha em texto plano
            hashed_password: Hash armazenado
            
        Returns:
            True se senha estiver correta
        """
        try:
            # Truncar senha seguramente
            safe_password = self._truncate_password_safely(plain_password)
            
            # Converter para bytes
            password_bytes = safe_password.encode('utf-8')
            hash_bytes = hashed_password.encode('utf-8')
            
            # Verificar com bcrypt direto
            return bcrypt.checkpw(password_bytes, hash_bytes)
            
        except Exception as e:
            print(f"❌ Erro na verificação de senha: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Validar força da senha com critérios de segurança.
        
        Args:
            password: Senha para validar
            
        Returns:
            (is_valid, message)
        """
        # Verificar comprimento mínimo
        if len(password) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres"
        
        # Verificar limite de bytes
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > self.MAX_PASSWORD_BYTES:
            return False, f"Senha muito longa (máximo {self.MAX_PASSWORD_BYTES} bytes)"
        
        # Verificar se tem pelo menos uma letra
        if not re.search(r'[a-zA-Z]', password):
            return False, "Senha deve conter pelo menos uma letra"
        
        # Verificar se tem pelo menos um número
        if not re.search(r'\d', password):
            return False, "Senha deve conter pelo menos um número"
        
        # Verificar caracteres proibidos
        if re.search(r'[<>\'\"&]', password):
            return False, "Senha contém caracteres não permitidos"
        
        return True, "Senha válida"
    
    def create_access_token(self, data: Dict[str, Any], 
                          expires_delta: Optional[timedelta] = None) -> str:
        """
        Criar token JWT seguro.
        
        Args:
            data: Dados para o payload
            expires_delta: Tempo de expiração customizado
            
        Returns:
            Token JWT
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = (
                datetime.now(timezone.utc) + 
                timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
        
        to_encode.update({
            "exp": expire, 
            "iat": datetime.now(timezone.utc),
            "iss": "primotex-erp",  # Issuer
            "aud": "primotex-users"  # Audience
        })
        
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decodificar e validar token JWT.
        
        Args:
            token: Token JWT
            
        Returns:
            Payload se válido, None se inválido
        """
        try:
            payload = jwt.decode(
                token, 
                self.SECRET_KEY, 
                algorithms=[self.ALGORITHM],
                audience="primotex-users",
                issuer="primotex-erp"
            )
            return payload
        except jwt.ExpiredSignatureError:
            print("❌ Token expirado")
            return None
        except jwt.InvalidTokenError as e:
            print(f"❌ Token inválido: {e}")
            return None
    
    def generate_user_token(self, user_id: int, username: str, 
                          email: str, perfil: str) -> str:
        """
        Gerar token específico para usuário.
        
        Args:
            user_id: ID do usuário
            username: Nome de usuário
            email: Email do usuário  
            perfil: Perfil do usuário
            
        Returns:
            Token JWT
        """
        token_data = {
            "sub": str(user_id),
            "username": username,
            "email": email,
            "perfil": perfil,
            "token_type": "access"
        }
        
        return self.create_access_token(token_data)


def testar_sistema_seguro():
    """Testar o sistema de autenticação seguro"""
    print("🔐 TESTANDO SISTEMA DE AUTENTICAÇÃO SEGURO")
    print("=" * 60)
    
    auth = SistemaAutenticacaoSeguro()
    
    # Teste 1: Senhas problemáticas
    senhas_teste = [
        "admin123",      # Senha original problemática
        "teste123",      # Senha simples
        "açúcar123",     # Caracteres UTF-8
        "emoji😀123",    # Emoji (multi-byte)
        "a" * 100,      # Senha muito longa
        "123",          # Muito curta
        "semdigito",    # Sem número
        "123456"        # Apenas números
    ]
    
    for senha in senhas_teste:
        print(f"\n🔍 Testando senha: '{senha}'")
        
        # Validar força
        is_valid, message = auth.validate_password_strength(senha)
        print(f"   Validação: {'✅' if is_valid else '❌'} {message}")
        
        if is_valid:
            try:
                # Gerar hash
                hash_senha = auth.hash_password(senha)
                print(f"   Hash: ✅ Gerado com sucesso")
                
                # Verificar senha
                verificacao = auth.verify_password(senha, hash_senha)
                print(f"   Verificação: {'✅' if verificacao else '❌'}")
                
                # Teste com senha incorreta
                verificacao_falsa = auth.verify_password("senhaerrada", hash_senha)
                print(f"   Senha incorreta: {'❌' if not verificacao_falsa else '⚠️'}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    # Teste 2: Token JWT
    print(f"\n🎫 TESTANDO TOKENS JWT")
    token = auth.generate_user_token(1, "admin", "admin@test.com", "administrador")
    print(f"   Token gerado: ✅")
    
    payload = auth.decode_access_token(token)
    print(f"   Token decodificado: {'✅' if payload else '❌'}")
    
    if payload:
        print(f"   Username: {payload.get('username')}")
        print(f"   Perfil: {payload.get('perfil')}")
    
    print(f"\n✅ TESTE DO SISTEMA SEGURO CONCLUÍDO")


if __name__ == "__main__":
    testar_sistema_seguro()