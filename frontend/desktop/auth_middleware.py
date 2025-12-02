"""
Middleware de Autenticação para Interfaces Desktop
Decorators e helpers para controlar acesso às janelas do sistema
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional, Any
import sys
from pathlib import Path
from functools import wraps

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.session_manager import session


def require_login(redirect_to_login: bool = True):
    """
    Decorator para classes/funções que requerem autenticação.

    Args:
        redirect_to_login: Se True, abre tela de login quando não autenticado

    Uso:
        @require_login()
        class MinhaJanela:
            def __init__(self, parent):
                ...
    """
    def decorator(cls_or_func):
        if isinstance(cls_or_func, type):
            # É uma classe
            original_init = cls_or_func.__init__

            @wraps(original_init)
            def new_init(self, *args, **kwargs):
                if not session.is_authenticated():
                    if redirect_to_login:
                        # Abrir tela de login
                        if not open_login_window():
                            # Login falhou ou foi cancelado
                            raise PermissionError("Autenticação necessária")
                    else:
                        raise PermissionError("Autenticação necessária")

                # Chamar __init__ original
                original_init(self, *args, **kwargs)

            cls_or_func.__init__ = new_init
            return cls_or_func
        else:
            # É uma função
            @wraps(cls_or_func)
            def wrapper(*args, **kwargs):
                if not session.is_authenticated():
                    if redirect_to_login:
                        if not open_login_window():
                            raise PermissionError("Autenticação necessária")
                    else:
                        raise PermissionError("Autenticação necessária")

                return cls_or_func(*args, **kwargs)

            return wrapper

    return decorator


def require_permission(permission: str, show_message: bool = True):
    """
    Decorator para classes/funções que requerem permissão específica.

    Args:
        permission: Permissão requerida (admin, gerente, operador, consulta)
        show_message: Se True, mostra mensagem de erro ao usuário

    Uso:
        @require_permission('admin')
        class AdminWindow:
            def __init__(self, parent):
                ...
    """
    def decorator(cls_or_func):
        if isinstance(cls_or_func, type):
            # É uma classe
            original_init = cls_or_func.__init__

            @wraps(original_init)
            def new_init(self, *args, **kwargs):
                if not session.is_authenticated():
                    if show_message:
                        messagebox.showerror(
                            "Não Autenticado",
                            "Você precisa fazer login primeiro."
                        )
                    raise PermissionError("Autenticação necessária")

                if not session.has_permission(permission):
                    user_type = session.get_user_type() or "Desconhecido"
                    if show_message:
                        messagebox.showerror(
                            "Acesso Negado",
                            "Você não tem permissão para acessar este módulo.\n\n"
                            f"Requerido: {permission.title()}\n"
                            f"Seu perfil: {user_type.title()}"
                        )
                    raise PermissionError(f"Permissão '{permission}' necessária")

                # Chamar __init__ original
                original_init(self, *args, **kwargs)

            cls_or_func.__init__ = new_init
            return cls_or_func
        else:
            # É uma função
            @wraps(cls_or_func)
            def wrapper(*args, **kwargs):
                if not session.is_authenticated():
                    if show_message:
                        messagebox.showerror(
                            "Não Autenticado",
                            "Você precisa fazer login primeiro."
                        )
                    raise PermissionError("Autenticação necessária")

                if not session.has_permission(permission):
                    user_type = session.get_user_type() or "Desconhecido"
                    if show_message:
                        messagebox.showerror(
                            "Acesso Negado",
                            "Você não tem permissão para executar esta ação.\n\n"
                            f"Requerido: {permission.title()}\n"
                            f"Seu perfil: {user_type.title()}"
                        )
                    raise PermissionError(f"Permissão '{permission}' necessária")

                return cls_or_func(*args, **kwargs)

            return wrapper

    return decorator


def check_session_or_login(parent_window: Optional[tk.Tk] = None) -> bool:
    """
    Verifica se há sessão ativa, senão abre tela de login.

    Args:
        parent_window: Janela pai (opcional)

    Returns:
        True se autenticado (nova ou existente)
    """
    if session.is_authenticated():
        return True

    return open_login_window(parent_window)


def open_login_window(parent: Optional[tk.Tk] = None) -> bool:
    """
    Abre a janela de login e retorna se login foi bem-sucedido.

    Args:
        parent: Janela pai (opcional)

    Returns:
        True se login bem-sucedido
    """
    try:
        from frontend.desktop.login_tkinter import LoginWindow

        # Criar janela de login
        login_window = LoginWindow(skip_restore=False)

        # Se parent fornecido, esconder durante login
        if parent:
            parent.withdraw()

        # Executar login
        user_data = login_window.run()

        # Restaurar parent
        if parent:
            parent.deiconify()

        # Verificar se login foi bem-sucedido
        return session.is_authenticated()

    except Exception as e:
        print(f"Erro ao abrir janela de login: {e}")
        return False


def get_current_user_info() -> dict:
    """
    Retorna informações do usuário autenticado.

    Returns:
        Dicionário com dados do usuário ou dict vazio
    """
    if not session.is_authenticated():
        return {
            'authenticated': False,
            'username': 'Não autenticado',
            'user_type': 'N/A'
        }

    return {
        'authenticated': True,
        'username': session.get_username(),
        'user_type': session.get_user_type(),
        'token': session.get_token(),
        'time_remaining': str(session.time_until_expiry()),
        'should_refresh': session.should_refresh_token()
    }


def logout_user(show_confirmation: bool = True) -> bool:
    """
    Faz logout do usuário atual.

    Args:
        show_confirmation: Se True, pede confirmação antes de deslogar

    Returns:
        True se logout foi realizado
    """
    if not session.is_authenticated():
        return False

    if show_confirmation:
        username = session.get_username()
        confirm = messagebox.askyesno(
            "Confirmar Logout",
            f"Deseja realmente sair?\n\nUsuário: {username}"
        )
        if not confirm:
            return False

    # Fazer logout
    session.logout()

    messagebox.showinfo(
        "Logout Realizado",
        "Você foi desconectado com sucesso."
    )

    return True


def validate_session_expiry(auto_refresh: bool = False) -> bool:
    """
    Valida se a sessão ainda é válida.

    Args:
        auto_refresh: Se True, tenta renovar token automaticamente

    Returns:
        True se sessão válida
    """
    if not session.is_authenticated():
        return False

    # Verificar se deve renovar
    if auto_refresh and session.should_refresh_token():
        print("⚠️ Token próximo da expiração - renovação necessária")
        # TODO: Implementar refresh automático via API
        # Por enquanto, apenas avisar

    return True


def get_token_for_api() -> Optional[str]:
    """
    Retorna token JWT para uso em chamadas API.

    Returns:
        Token JWT ou None se não autenticado
    """
    if not session.is_authenticated():
        print("⚠️ Tentativa de obter token sem autenticação")
        return None

    return session.get_token()


def create_auth_header() -> dict:
    """
    Cria header de autenticação para requests HTTP.

    Returns:
        Dicionário com header Authorization ou vazio
    """
    token = get_token_for_api()
    if not token:
        return {}

    return {
        'Authorization': f'Bearer {token}'
    }


# Exemplo de uso
if __name__ == "__main__":
    print("=== TESTE MIDDLEWARE DE AUTENTICAÇÃO ===\n")

    # Teste 1: Verificar sessão
    print("1. Verificando sessão...")
    info = get_current_user_info()
    for key, value in info.items():
        print(f"   {key}: {value}")

    # Teste 2: Obter token
    print("\n2. Obtendo token para API...")
    token = get_token_for_api()
    if token:
        print(f"   Token: {token[:50]}...")
    else:
        print("   Nenhum token disponível")

    # Teste 3: Header de autenticação
    print("\n3. Header de autenticação...")
    headers = create_auth_header()
    print(f"   Headers: {headers}")

    # Teste 4: Decorator (exemplo)
    print("\n4. Teste de decorator...")

    @require_login(redirect_to_login=False)
    def funcao_protegida():
        return "Acesso permitido!"

    try:
        resultado = funcao_protegida()
        print(f"   Resultado: {resultado}")
    except PermissionError as e:
        print(f"   Erro: {e}")

    print("\n=== TESTE CONCLUÍDO ===")
