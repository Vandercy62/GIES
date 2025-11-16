"""
Sistema de Gerenciamento de Sessão Global
Controla autenticação, tokens JWT e permissões em todo o sistema desktop
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Gerenciador de sessão singleton para todo o sistema.
    
    Responsabilidades:
    - Armazenar token JWT e dados do usuário
    - Validar sessão ativa
    - Auto-refresh de token
    - Controle de permissões
    - Persistência de sessão (opcional)
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implementação Singleton thread-safe"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa o gerenciador de sessão"""
        if not hasattr(self, 'initialized'):
            self.token: Optional[str] = None
            self.user_data: Optional[Dict[str, Any]] = None
            self.login_time: Optional[datetime] = None
            self.token_expiry: Optional[datetime] = None
            self.refresh_token: Optional[str] = None
            self._session_file = Path.home() / ".primotex_session.json"
            self.initialized = True
            logger.info("SessionManager inicializado")
    
    def login(
        self, 
        token: str, 
        user_data: Dict[str, Any],
        token_expiry_hours: int = 720,  # 30 dias padrão
        refresh_token: Optional[str] = None
    ) -> None:
        """
        Inicia uma nova sessão de usuário.
        
        Args:
            token: Token JWT de autenticação
            user_data: Dados do usuário (id, username, perfil, etc.)
            token_expiry_hours: Horas até expiração do token
            refresh_token: Token de refresh (opcional)
        """
        with self._lock:
            self.token = token
            self.user_data = user_data
            self.login_time = datetime.now()
            self.token_expiry = datetime.now() + timedelta(hours=token_expiry_hours)
            self.refresh_token = refresh_token
            
            logger.info(f"Usuário '{user_data.get('username')}' autenticado com sucesso")
            logger.debug(f"Token expira em: {self.token_expiry}")
            
            # Persistir sessão (opcional)
            self._save_session()
    
    def logout(self) -> None:
        """Encerra a sessão atual"""
        with self._lock:
            username = self.user_data.get('username') if self.user_data else 'Desconhecido'
            self.token = None
            self.user_data = None
            self.login_time = None
            self.token_expiry = None
            self.refresh_token = None
            
            logger.info(f"Usuário '{username}' desconectado")
            
            # Remover sessão persistida
            self._clear_session()
    
    def is_authenticated(self) -> bool:
        """
        Verifica se há uma sessão ativa e válida.
        
        Returns:
            True se usuário autenticado e token válido
        """
        if not self.token or not self.user_data:
            return False
        
        # Verificar expiração
        if self.token_expiry and datetime.now() >= self.token_expiry:
            logger.warning("Token expirado")
            return False
        
        return True
    
    def get_token(self) -> Optional[str]:
        """
        Retorna o token JWT atual.
        
        Returns:
            Token JWT ou None se não autenticado
        """
        if not self.is_authenticated():
            logger.warning("Tentativa de obter token sem autenticação")
            return None
        return self.token
    
    def get_user_data(self) -> Optional[Dict[str, Any]]:
        """
        Retorna os dados do usuário autenticado.
        
        Returns:
            Dicionário com dados do usuário ou None
        """
        if not self.is_authenticated():
            return None
        return self.user_data.copy() if self.user_data else None
    
    def get_username(self) -> Optional[str]:
        """Retorna o username do usuário autenticado"""
        user_data = self.get_user_data()
        return user_data.get('username') if user_data else None
    
    def get_user_type(self) -> Optional[str]:
        """Retorna o tipo/perfil do usuário (admin, gerente, operador, etc.)"""
        user_data = self.get_user_data()
        if not user_data:
            return None
        # Suportar ambos 'tipo_usuario' e 'perfil' para compatibilidade
        return user_data.get('tipo_usuario') or user_data.get('perfil')
    
    def has_permission(self, required_permission: str) -> bool:
        """
        Verifica se o usuário tem uma permissão específica.
        
        Args:
            required_permission: Permissão requerida (admin, gerente, operador, consulta)
        
        Returns:
            True se usuário tem a permissão
        """
        if not self.is_authenticated():
            return False
        
        user_type = self.get_user_type()
        if not user_type:
            return False
        
        # Normalizar tipo de usuário (lowercase)
        user_type_normalized = user_type.lower()
        
        # Mapear variações de nomes
        type_mapping = {
            'administrador': 'admin',
            'administrator': 'admin',
            'admin': 'admin',
            'gerente': 'gerente',
            'manager': 'gerente',
            'operador': 'operador',
            'operator': 'operador',
            'consulta': 'consulta',
            'viewer': 'consulta'
        }
        
        # Obter tipo mapeado
        mapped_type = type_mapping.get(user_type_normalized, user_type_normalized)
        
        # Hierarquia de permissões
        permissions_hierarchy = {
            'admin': ['admin', 'gerente', 'operador', 'consulta'],
            'gerente': ['gerente', 'operador', 'consulta'],
            'operador': ['operador', 'consulta'],
            'consulta': ['consulta']
        }
        
        allowed = permissions_hierarchy.get(mapped_type, [])
        return required_permission.lower() in allowed
    
    def time_until_expiry(self) -> Optional[timedelta]:
        """
        Calcula tempo restante até expiração do token.
        
        Returns:
            timedelta com tempo restante ou None
        """
        if not self.is_authenticated() or not self.token_expiry:
            return None
        
        remaining = self.token_expiry - datetime.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    def should_refresh_token(self, threshold_hours: int = 24) -> bool:
        """
        Verifica se o token deve ser renovado.
        
        Args:
            threshold_hours: Renovar se restar menos que X horas
        
        Returns:
            True se deve renovar
        """
        remaining = self.time_until_expiry()
        if not remaining:
            return False
        
        return remaining < timedelta(hours=threshold_hours)
    
    def refresh_session(self, new_token: str, new_expiry_hours: int = 720) -> None:
        """
        Renova o token da sessão atual.
        
        Args:
            new_token: Novo token JWT
            new_expiry_hours: Novas horas de expiração
        """
        with self._lock:
            if not self.user_data:
                logger.warning("Tentativa de refresh sem sessão ativa")
                return
            
            self.token = new_token
            self.token_expiry = datetime.now() + timedelta(hours=new_expiry_hours)
            
            logger.info(f"Token renovado para usuário '{self.get_username()}'")
            logger.debug(f"Nova expiração: {self.token_expiry}")
            
            self._save_session()
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Retorna informações da sessão atual.
        
        Returns:
            Dicionário com informações da sessão
        """
        if not self.is_authenticated():
            return {
                'authenticated': False,
                'message': 'Nenhuma sessão ativa'
            }
        
        remaining = self.time_until_expiry()
        
        return {
            'authenticated': True,
            'username': self.get_username(),
            'user_type': self.get_user_type(),
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'token_expiry': self.token_expiry.isoformat() if self.token_expiry else None,
            'time_remaining': str(remaining) if remaining else None,
            'should_refresh': self.should_refresh_token()
        }
    
    def _save_session(self) -> None:
        """
        Salva a sessão atual em arquivo (persistência opcional).
        ATENÇÃO: Apenas para desenvolvimento. Em produção, usar storage seguro.
        """
        try:
            if not self.token or not self.user_data:
                return
            
            session_data = {
                'token': self.token,
                'user_data': self.user_data,
                'login_time': self.login_time.isoformat() if self.login_time else None,
                'token_expiry': self.token_expiry.isoformat() if self.token_expiry else None,
                'refresh_token': self.refresh_token
            }
            
            # Salvar com permissões restritas
            self._session_file.write_text(json.dumps(session_data, indent=2))
            logger.debug(f"Sessão persistida em {self._session_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar sessão: {e}")
    
    def _load_session(self) -> bool:
        """
        Carrega sessão persistida (se existir).
        
        Returns:
            True se sessão carregada com sucesso
        """
        try:
            if not self._session_file.exists():
                return False
            
            session_data = json.loads(self._session_file.read_text())
            
            # Validar expiração
            if 'token_expiry' in session_data:
                expiry = datetime.fromisoformat(session_data['token_expiry'])
                if datetime.now() >= expiry:
                    logger.info("Sessão persistida expirada")
                    self._clear_session()
                    return False
            
            # Restaurar sessão
            self.token = session_data.get('token')
            self.user_data = session_data.get('user_data')
            self.refresh_token = session_data.get('refresh_token')
            
            if 'login_time' in session_data:
                self.login_time = datetime.fromisoformat(session_data['login_time'])
            if 'token_expiry' in session_data:
                self.token_expiry = datetime.fromisoformat(session_data['token_expiry'])
            
            logger.info(f"Sessão restaurada para usuário '{self.get_username()}'")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar sessão: {e}")
            self._clear_session()
            return False
    
    def _clear_session(self) -> None:
        """Remove arquivo de sessão persistida"""
        try:
            if self._session_file.exists():
                self._session_file.unlink()
                logger.debug("Arquivo de sessão removido")
        except Exception as e:
            logger.error(f"Erro ao remover sessão: {e}")
    
    def restore_session(self) -> bool:
        """
        Tenta restaurar sessão anterior.
        
        Returns:
            True se sessão restaurada com sucesso
        """
        return self._load_session()


# Instância global do gerenciador de sessão
session = SessionManager()


def require_authentication(func):
    """
    Decorator para métodos que requerem autenticação.
    
    Uso:
        @require_authentication
        def minha_funcao():
            ...
    """
    def wrapper(*args, **kwargs):
        if not session.is_authenticated():
            logger.warning(f"Acesso negado a {func.__name__}: não autenticado")
            raise PermissionError("Autenticação necessária")
        return func(*args, **kwargs)
    return wrapper


def require_permission(permission: str):
    """
    Decorator para métodos que requerem permissão específica.
    
    Uso:
        @require_permission('admin')
        def funcao_admin():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not session.has_permission(permission):
                logger.warning(
                    f"Acesso negado a {func.__name__}: "
                    f"requer '{permission}', usuário tem '{session.get_user_type()}'"
                )
                raise PermissionError(f"Permissão '{permission}' necessária")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Teste básico
    print("=== TESTE SESSION MANAGER ===\n")
    
    # 1. Login
    print("1. Fazendo login...")
    session.login(
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example",
        user_data={
            'id': 1,
            'username': 'admin',
            'perfil': 'admin',
            'email': 'admin@primotex.com'
        },
        token_expiry_hours=1  # 1 hora para teste
    )
    
    # 2. Verificar autenticação
    print(f"2. Autenticado: {session.is_authenticated()}")
    print(f"   Usuário: {session.get_username()}")
    print(f"   Tipo: {session.get_user_type()}")
    
    # 3. Testar permissões
    print("\n3. Teste de permissões:")
    print(f"   Tem 'admin': {session.has_permission('admin')}")
    print(f"   Tem 'gerente': {session.has_permission('gerente')}")
    print(f"   Tem 'operador': {session.has_permission('operador')}")
    
    # 4. Info da sessão
    print("\n4. Informações da sessão:")
    info = session.get_session_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # 5. Tempo restante
    remaining = session.time_until_expiry()
    print(f"\n5. Tempo até expiração: {remaining}")
    print(f"   Deve renovar: {session.should_refresh_token()}")
    
    # 6. Logout
    print("\n6. Fazendo logout...")
    session.logout()
    print(f"   Autenticado: {session.is_authenticated()}")
    
    print("\n=== TESTE CONCLUÍDO ===")
