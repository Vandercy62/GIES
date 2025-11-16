"""
SISTEMA ERP PRIMOTEX - ROTAS DE AUTENTICAÇÃO
===========================================

Endpoints para autenticação, login, registro e gerenciamento de usuários.
Sistema completo de autenticação JWT.

Autor: GitHub Copilot
Data: 29/10/2025
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from backend.database.config import get_database, get_db
from backend.models.user_model import Usuario, PERFIS_SISTEMA
from backend.schemas.auth_schemas import (
    LoginRequest, LoginResponse, UserCreate, UserUpdate, 
    UserResponse, PasswordChangeRequest, PasswordResetRequest,
    SuccessResponse, ErrorResponse, PerfilResponse,
    ForgotPasswordRequest, PasswordRecoveryResponse
)
from backend.auth.jwt_handler import (
    generate_user_token, verify_password, hash_password,
    ACCESS_TOKEN_EXPIRE_MINUTES, validate_password_strength
)
from backend.auth.dependencies import (
    get_current_user, get_current_active_user, 
    require_admin, require_manager
)

# =======================================
# CONFIGURAÇÃO DO ROUTER
# =======================================

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
    responses={
        401: {"model": ErrorResponse, "description": "Não autorizado"},
        403: {"model": ErrorResponse, "description": "Acesso negado"},
        404: {"model": ErrorResponse, "description": "Não encontrado"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    }
)

# =======================================
# ENDPOINTS DE AUTENTICAÇÃO
# =======================================

from shared.logging_system import LogManager
log_manager = LogManager()
logger = log_manager.get_logger("login")

@router.post("/login", response_model=LoginResponse, summary="Fazer login")
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Autenticar usuário e retornar token de acesso.
    
    - **username**: Nome de usuário ou email
    - **password**: Senha do usuário
    
    Retorna token JWT válido por 8 horas.
    """
    import traceback
    print("[DEBUG] Iniciando login para:", login_data.username)
    try:
        # Buscar usuário por username ou email
        user = db.query(Usuario).filter(
            (Usuario.username == login_data.username) |
            (Usuario.email == login_data.username)
        ).first()

        # Verificar se usuário existe
        if not user:
            logger.warning(f"Usuário não encontrado: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )

        # Verificar senha
        if not verify_password(login_data.password, user.senha_hash):
            logger.warning(f"Senha inválida para usuário: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )

        # Verificar se usuário está ativo
        if not user.ativo:
            logger.warning(f"Usuário inativo: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )

        # Atualizar última atividade
        user.ultima_atividade = datetime.now()
        db.commit()

        # Gerar token
        access_token = generate_user_token(
            user_id=user.id,
            username=user.username,
            email=user.email,
            perfil=user.perfil
        )

        logger.info(f"Login bem-sucedido: {login_data.username}")
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Converter para segundos
            user=UserResponse.model_validate(user)
        )
    except HTTPException:
        # Re-lançar HTTPException sem modificar (401, 403, etc)
        raise
    except Exception as e:
        print("[ERRO LOGIN] Exceção capturada no endpoint de login:", e)
        traceback.print_exc()
        logger.error(f"Erro inesperado no login: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no login: {str(e)}"
        )

@router.post("/logout", response_model=SuccessResponse, summary="Fazer logout")
async def logout(current_user: Usuario = Depends(get_current_active_user)):
    """
    Fazer logout do usuário atual.
    
    Na implementação atual, apenas confirma o logout.
    Em produção, poderia adicionar token blacklist.
    """
    return SuccessResponse(
        message=f"Logout realizado com sucesso para {current_user.username}"
    )

# =======================================
# ENDPOINTS DE PERFIL DO USUÁRIO
# =======================================

@router.get("/me", response_model=UserResponse, summary="Obter perfil atual")
async def get_current_user_profile(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obter informações do usuário logado atual.
    """
    return UserResponse.model_validate(current_user)

@router.put("/me", response_model=UserResponse, summary="Atualizar perfil")
async def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Atualizar dados do próprio perfil.
    
    Usuários podem atualizar apenas seus próprios dados básicos.
    Perfil e status só podem ser alterados por administradores.
    """
    # Campos que usuário comum pode alterar
    if user_update.email is not None:
        # Verificar se email já existe
        existing_user = db.query(Usuario).filter(
            Usuario.email == user_update.email,
            Usuario.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        current_user.email = user_update.email
    
    if user_update.nome_completo is not None:
        current_user.nome_completo = user_update.nome_completo
    
    if user_update.observacoes is not None:
        current_user.observacoes = user_update.observacoes
    
    # Perfil e ativo só admin pode alterar
    if user_update.perfil is not None or user_update.ativo is not None:
        if current_user.perfil != "administrador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem alterar perfil e status"
            )
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)

# =======================================
# ENDPOINTS DE GESTÃO DE SENHA
# =======================================

@router.post("/change-password", response_model=SuccessResponse, summary="Trocar senha")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Trocar senha do usuário atual.
    
    - **current_password**: Senha atual
    - **new_password**: Nova senha
    - **confirm_password**: Confirmação da nova senha
    """
    # Validar senha atual
    if not verify_password(password_data.current_password, current_user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Validar se senhas coincidem
    try:
        password_data.validate_passwords_match()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Validar força da nova senha
    is_valid, message = validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Atualizar senha
    current_user.senha_hash = hash_password(password_data.new_password)
    db.commit()
    
    return SuccessResponse(
        message="Senha alterada com sucesso"
    )

@router.post("/forgot-password", response_model=PasswordRecoveryResponse, summary="Recuperar senha")
async def forgot_password(
    recovery_data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Recuperar senha esquecida gerando senha temporária.
    
    - **username**: Nome de usuário
    - **email**: Email cadastrado
    
    Gera senha temporária para colaboradores que esqueceram a senha.
    Retorna a senha temporária que deve ser alterada no próximo login.
    """
    # Buscar usuário por username e email
    user = db.query(Usuario).filter(
        Usuario.username == recovery_data.username,
        Usuario.email == recovery_data.email
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado ou dados incorretos"
        )
    
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Contate o administrador."
        )
    
    # Gerar senha temporária simples (formato: Primotex@XXXX)
    import random
    import string
    random_suffix = ''.join(random.choices(string.digits, k=4))
    temporary_password = f"Primotex@{random_suffix}"
    
    # Atualizar senha do usuário
    user.senha_hash = hash_password(temporary_password)
    user.ultima_atividade = datetime.now()
    db.commit()
    
    logger.info(f"Senha recuperada para usuário: {user.username}")
    
    return PasswordRecoveryResponse(
        message="Senha temporária gerada com sucesso. Anote e altere após o login.",
        temporary_password=temporary_password,
        username=user.username
    )

# =======================================
# ENDPOINTS DE ADMINISTRAÇÃO
# =======================================

@router.get("/users", response_model=List[UserResponse], summary="Listar usuários")
async def list_users(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_manager)
):
    """
    Listar todos os usuários do sistema.
    
    Acesso restrito a gerentes e administradores.
    """
    users = db.query(Usuario).all()
    return [UserResponse.model_validate(user) for user in users]

@router.post("/users", response_model=UserResponse, summary="Criar usuário")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Criar novo usuário no sistema.
    
    Acesso restrito a administradores.
    """
    # Verificar se username já existe
    existing_user = db.query(Usuario).filter(
        Usuario.username == user_data.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já existe"
        )
    
    # Verificar se email já existe
    existing_email = db.query(Usuario).filter(
        Usuario.email == user_data.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )
    
    # Validar perfil
    if user_data.perfil not in [p["value"] for p in PERFIS_SISTEMA]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil inválido"
        )
    
    # Validar força da senha
    is_valid, message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Criar usuário
    new_user = Usuario(
        username=user_data.username,
        email=user_data.email,
        senha_hash=hash_password(user_data.password),
        nome_completo=user_data.nome_completo,
        perfil=user_data.perfil,
        ativo=user_data.ativo,
        observacoes=user_data.observacoes
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse.model_validate(new_user)

@router.get("/users/{user_id}", response_model=UserResponse, summary="Obter usuário")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_manager)
):
    """
    Obter dados de usuário específico.
    
    Acesso restrito a gerentes e administradores.
    """
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return UserResponse.model_validate(user)

@router.put("/users/{user_id}", response_model=UserResponse, summary="Atualizar usuário")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Atualizar dados de usuário específico.
    
    Acesso restrito a administradores.
    """
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Atualizar campos fornecidos
    if user_update.email is not None:
        # Verificar se email já existe
        existing_user = db.query(Usuario).filter(
            Usuario.email == user_update.email,
            Usuario.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        user.email = user_update.email
    
    if user_update.nome_completo is not None:
        user.nome_completo = user_update.nome_completo
    
    if user_update.perfil is not None:
        if user_update.perfil not in [p["value"] for p in PERFIS_SISTEMA]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Perfil inválido"
            )
        user.perfil = user_update.perfil
    
    if user_update.ativo is not None:
        user.ativo = user_update.ativo
    
    if user_update.observacoes is not None:
        user.observacoes = user_update.observacoes
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)

@router.post("/reset-password", response_model=SuccessResponse, summary="Resetar senha")
async def reset_user_password(
    password_data: PasswordResetRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Resetar senha de usuário específico.
    
    Acesso restrito a administradores.
    """
    user = db.query(Usuario).filter(Usuario.id == password_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Validar se senhas coincidem
    try:
        password_data.validate_passwords_match()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Validar força da nova senha
    is_valid, message = validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Atualizar senha
    user.senha_hash = hash_password(password_data.new_password)
    db.commit()
    
    return SuccessResponse(
        message=f"Senha resetada com sucesso para {user.username}"
    )

# =======================================
# ENDPOINTS DE INFORMAÇÕES
# =======================================

@router.get("/profiles", response_model=List[PerfilResponse], summary="Listar perfis")
async def get_available_profiles():
    """
    Obter lista de perfis disponíveis no sistema.
    """
    return [
        PerfilResponse(
            value=perfil["value"],
            label=perfil["label"],
            description=perfil["description"]
        )
        for perfil in PERFIS_SISTEMA
    ]