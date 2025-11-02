"""
SISTEMA ERP PRIMOTEX - MANIPULADOR JWT
====================================

Sistema de autenticação com JWT (JSON Web Tokens).
Geração, validação e decodificação de tokens.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import os
import jwt
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

# =======================================
# CONFIGURAÇÕES
# =======================================

# Chave secreta para JWT (em produção usar variável de ambiente)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "primotex_secret_key_2025_dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas

# =======================================
# CONFIGURAÇÕES DE HASH SEGURO
# =======================================

# Salt para SHA256 (temporário até corrigir bcrypt)
SECRET_SALT = "primotex_salt_2025_secure_hash"

def _create_secure_hash(password: str) -> str:
    """Cria hash seguro com SHA256 e salt"""
    return hashlib.sha256((password + SECRET_SALT).encode()).hexdigest()

def _verify_secure_hash(password: str, hash_stored: str) -> bool:
    """Verifica hash SHA256"""
    return _create_secure_hash(password) == hash_stored

# =======================================
# FUNÇÕES DE HASH DE SENHA
# =======================================

  
def hash_password(password: str) -> str:
    """
    Fazer hash da senha usando SHA256 seguro.
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha
    """
    return _create_secure_hash(password)

  
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar se a senha está correta.
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha armazenada
        
    Returns:
        True se a senha estiver correta
    """
    return _verify_secure_hash(plain_password, hashed_password)

# =======================================
# FUNÇÕES JWT
# =======================================

  
def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Criar token de acesso JWT.
    
    Args:
        data: Dados para incluir no token
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
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

  
def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodificar e validar token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        Dados do token se válido, None se inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verificar se o token não expirou
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc) > datetime.fromtimestamp(
            exp, tz=timezone.utc
        ):
            return None
            
        return payload
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

  
def get_token_user_id(token: str) -> Optional[int]:
    """
    Obter ID do usuário do token.
    
    Args:
        token: Token JWT
        
    Returns:
        ID do usuário se token válido
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("user_id")
    return None

  
def get_token_username(token: str) -> Optional[str]:
    """
    Obter username do token.
    
    Args:
        token: Token JWT
        
    Returns:
        Username se token válido
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("username")
    return None

  
def is_token_valid(token: str) -> bool:
    """
    Verificar se token é válido.
    
    Args:
        token: Token JWT
        
    Returns:
        True se token válido
    """
    return decode_access_token(token) is not None

# =======================================
# FUNÇÕES AUXILIARES
# =======================================

  
def generate_user_token(
    user_id: int, username: str, email: str, perfil: str
) -> str:
    """
    Gerar token para usuário específico.
    
    Args:
        user_id: ID do usuário
        username: Nome de usuário
        email: Email do usuário
        perfil: Perfil do usuário
        
    Returns:
        Token JWT
    """
    token_data = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "perfil": perfil
    }
    
    return create_access_token(token_data)

  
def refresh_token(token: str) -> Optional[str]:
    """
    Renovar token se ainda válido.
    
    Args:
        token: Token atual
        
    Returns:
        Novo token se válido, None se inválido
    """
    payload = decode_access_token(token)
    if not payload:
        return None
    
    # Remover timestamps antigos
    payload.pop("exp", None)
    payload.pop("iat", None)
    
    return create_access_token(payload)

# =======================================
# VALIDAÇÕES DE SENHA
# =======================================

  
def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validar força da senha.
    
    Args:
        password: Senha para validar
        
    Returns:
        (is_valid, message)
    """
    if len(password) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres"
    
    if len(password) > 50:
        return False, "Senha deve ter no máximo 50 caracteres"
    
    has_digit = any(c.isdigit() for c in password)
    has_letter = any(c.isalpha() for c in password)
    
    if not (has_digit and has_letter):
        return False, "Senha deve conter pelo menos uma letra e um número"
    
    return True, "Senha válida"
