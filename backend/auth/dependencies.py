"""
SISTEMA ERP PRIMOTEX - DEPENDÊNCIAS DE AUTENTICAÇÃO
==================================================

Sistema de dependências para validação de autenticação.
Usado nos endpoints protegidos do FastAPI.

Autor: GitHub Copilot
Data: 29/10/2025
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from backend.database.config import get_database
from backend.models.user_model import Usuario
from backend.auth.jwt_handler import decode_access_token

# =======================================
# CONFIGURAÇÃO DA SEGURANÇA
# =======================================

# Esquema de segurança Bearer Token (auto_error=False para controle manual de erros)
security = HTTPBearer(auto_error=False)

# =======================================
# DEPENDÊNCIAS DE AUTENTICAÇÃO
# =======================================

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_database)
) -> Usuario:
    """
    Dependency para obter usuário atual autenticado.
    
    Args:
        credentials: Token de autorização
        db: Sessão do banco de dados
        
    Returns:
        Usuário autenticado
        
    Raises:
        HTTPException: Se token inválido ou usuário não encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de acesso inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verificar se credenciais foram fornecidas
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Decodificar token
        token = credentials.credentials
        payload = decode_access_token(token)
        
        if payload is None:
            raise credentials_exception
        
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
            
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception
    
    # Buscar usuário no banco
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # Verificar se usuário está ativo
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    return user

def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Dependency para garantir que usuário está ativo.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        Usuário ativo
        
    Raises:
        HTTPException: Se usuário inativo
    """
    if not current_user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    return current_user

# =======================================
# DEPENDÊNCIAS DE AUTORIZAÇÃO
# =======================================

def require_admin(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
    """
    Dependency para exigir perfil de administrador.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        Usuário administrador
        
    Raises:
        HTTPException: Se não for administrador
    """
    if current_user.perfil != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    return current_user

def require_manager(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
    """
    Dependency para exigir perfil de gerente ou superior.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        Usuário gerente ou administrador
        
    Raises:
        HTTPException: Se não tiver permissão
    """
    allowed_profiles = ["administrador", "gerente"]
    if current_user.perfil not in allowed_profiles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a gerentes e administradores"
        )
    return current_user

def require_operator(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
    """
    Dependency para exigir perfil de operador ou superior.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        Usuário com permissão de operação
        
    Raises:
        HTTPException: Se não tiver permissão
    """
    allowed_profiles = ["administrador", "gerente", "operador"]
    if current_user.perfil not in allowed_profiles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a operadores e superiores"
        )
    return current_user

# =======================================
# DEPENDÊNCIAS OPCIONAIS
# =======================================

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_database)
) -> Optional[Usuario]:
    """
    Dependency para obter usuário atual (opcional).
    Não gera erro se não autenticado.
    
    Args:
        credentials: Token de autorização (opcional)
        db: Sessão do banco de dados
        
    Returns:
        Usuário autenticado ou None
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        
        if payload is None:
            return None
        
        user_id: int = payload.get("user_id")
        if user_id is None:
            return None
            
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user and user.ativo:
            return user
            
    except Exception:
        pass
    
    return None

# =======================================
# FUNÇÕES AUXILIARES
# =======================================

def check_user_permission(user: Usuario, required_permission: str) -> bool:
    """
    Verificar se usuário tem permissão específica.
    
    Args:
        user: Usuário para verificar
        required_permission: Permissão necessária
        
    Returns:
        True se tiver permissão
    """
    # Hierarquia de permissões
    permissions_hierarchy = {
        "administrador": ["admin", "manager", "operator", "viewer"],
        "gerente": ["manager", "operator", "viewer"],
        "operador": ["operator", "viewer"],
        "consulta": ["viewer"]
    }
    
    user_permissions = permissions_hierarchy.get(user.perfil, [])
    return required_permission in user_permissions

def extract_token_from_header(authorization: str) -> Optional[str]:
    """
    Extrair token do header Authorization.
    
    Args:
        authorization: Header Authorization
        
    Returns:
        Token extraído ou None
    """
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]