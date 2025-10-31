"""
SISTEMA ERP PRIMOTEX - SCHEMAS DE AUTENTICAÇÃO
=============================================

Schemas Pydantic para requests e responses de autenticação.
Validação e serialização de dados da API.

Autor: GitHub Copilot
Data: 29/10/2025
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from shared.constants import (
    FIELD_NOME_USUARIO,
    FIELD_EMAIL_USUARIO,
    FIELD_NOME_COMPLETO,
    FIELD_PERFIL_USUARIO,
    FIELD_STATUS_ATIVO,
    FIELD_OBSERVACOES
)

# =======================================
# SCHEMAS DE LOGIN
# =======================================

class LoginRequest(BaseModel):
    """Schema para request de login"""
    username: str = Field(..., min_length=3, max_length=50, description=FIELD_NOME_USUARIO)
    password: str = Field(..., min_length=6, max_length=50, description="Senha")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "123456"
            }
        }

class LoginResponse(BaseModel):
    """Schema para response de login"""
    access_token: str = Field(..., description="Token de acesso JWT")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")
    user: "UserResponse" = Field(..., description="Dados do usuário")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 28800,
                "user": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@primotex.com",
                    "nome_completo": "Administrador",
                    "perfil": "administrador",
                    "ativo": True
                }
            }
        }

# =======================================
# SCHEMAS DE USUÁRIO
# =======================================

class UserBase(BaseModel):
    """Schema base para usuário"""
    username: str = Field(..., min_length=3, max_length=50, description=FIELD_NOME_USUARIO)
    email: EmailStr = Field(..., description=FIELD_EMAIL_USUARIO)
    nome_completo: str = Field(..., min_length=2, max_length=150, description=FIELD_NOME_COMPLETO)
    perfil: str = Field(..., description=FIELD_PERFIL_USUARIO)
    ativo: bool = Field(default=True, description=FIELD_STATUS_ATIVO)
    observacoes: Optional[str] = Field(None, description=FIELD_OBSERVACOES)

class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=6, max_length=50, description="Senha")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "joao.silva",
                "email": "joao@primotex.com",
                "nome_completo": "João Silva",
                "perfil": "operador",
                "password": "123456",
                "ativo": True,
                "observacoes": "Novo operador"
            }
        }

class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    email: Optional[EmailStr] = Field(None, description=FIELD_EMAIL_USUARIO)
    nome_completo: Optional[str] = Field(None, min_length=2, max_length=150, description=FIELD_NOME_COMPLETO)
    perfil: Optional[str] = Field(None, description=FIELD_PERFIL_USUARIO)
    ativo: Optional[bool] = Field(None, description=FIELD_STATUS_ATIVO)
    observacoes: Optional[str] = Field(None, description=FIELD_OBSERVACOES)

class UserResponse(BaseModel):
    """Schema para response de usuário"""
    id: int = Field(..., description="ID do usuário")
    username: str = Field(..., description=FIELD_NOME_USUARIO)
    email: str = Field(..., description=FIELD_EMAIL_USUARIO)
    nome_completo: str = Field(..., description=FIELD_NOME_COMPLETO)
    perfil: str = Field(..., description=FIELD_PERFIL_USUARIO)
    ativo: bool = Field(..., description=FIELD_STATUS_ATIVO)
    data_criacao: datetime = Field(..., description="Data de criação")
    ultima_atividade: Optional[datetime] = Field(None, description="Última atividade")
    observacoes: Optional[str] = Field(None, description=FIELD_OBSERVACOES)
    
    class Config:
        from_attributes = True

# =======================================
# SCHEMAS DE SENHA
# =======================================

class PasswordChangeRequest(BaseModel):
    """Schema para troca de senha"""
    current_password: str = Field(..., min_length=6, max_length=50, description="Senha atual")
    new_password: str = Field(..., min_length=6, max_length=50, description="Nova senha")
    confirm_password: str = Field(..., min_length=6, max_length=50, description="Confirmação da nova senha")
    
    def validate_passwords_match(self):
        """Validar se as senhas coincidem"""
        if self.new_password != self.confirm_password:
            raise ValueError("Nova senha e confirmação não coincidem")
        return True
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "123456",
                "new_password": "novaSenha123",
                "confirm_password": "novaSenha123"
            }
        }

class PasswordResetRequest(BaseModel):
    """Schema para reset de senha (admin)"""
    user_id: int = Field(..., description="ID do usuário")
    new_password: str = Field(..., min_length=6, max_length=50, description="Nova senha")
    confirm_password: str = Field(..., min_length=6, max_length=50, description="Confirmação da nova senha")
    
    def validate_passwords_match(self):
        """Validar se as senhas coincidem"""
        if self.new_password != self.confirm_password:
            raise ValueError("Nova senha e confirmação não coincidem")
        return True

# =======================================
# SCHEMAS DE TOKEN
# =======================================

class TokenData(BaseModel):
    """Schema para dados do token"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    perfil: Optional[str] = None

class TokenRefreshRequest(BaseModel):
    """Schema para refresh de token"""
    refresh_token: str = Field(..., description="Token de refresh")

class TokenValidationResponse(BaseModel):
    """Schema para response de validação de token"""
    valid: bool = Field(..., description="Se o token é válido")
    user_id: Optional[int] = Field(None, description="ID do usuário se válido")
    username: Optional[str] = Field(None, description="Username se válido")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")

# =======================================
# SCHEMAS DE PERFIS
# =======================================

class PerfilResponse(BaseModel):
    """Schema para response de perfis disponíveis"""
    value: str = Field(..., description="Valor do perfil")
    label: str = Field(..., description="Rótulo do perfil")
    description: str = Field(..., description="Descrição do perfil")

# =======================================
# SCHEMAS DE RESPOSTA PADRÃO
# =======================================

class SuccessResponse(BaseModel):
    """Schema para response de sucesso"""
    success: bool = Field(default=True, description="Status de sucesso")
    message: str = Field(..., description="Mensagem de sucesso")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operação realizada com sucesso"
            }
        }

class ErrorResponse(BaseModel):
    """Schema para response de erro"""
    success: bool = Field(default=False, description="Status de sucesso")
    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes do erro")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Erro de autenticação",
                "detail": "Credenciais inválidas"
            }
        }