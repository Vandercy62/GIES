"""
SISTEMA ERP PRIMOTEX - TELA DE LOGIN DESKTOP
==========================================

Interface gráfica de login com PyQt6.
Integração com API de autenticação JWT.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import sys
import json
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QMessageBox, QProgressBar,
    QCheckBox, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
from typing import Optional, Dict, Any

# =======================================
# CONFIGURAÇÕES
# =======================================

API_BASE_URL = "http://127.0.0.1:8001"
COMPANY_NAME = "Primotex - Forros e Divisórias Eireli"
SYSTEM_NAME = "Sistema ERP Primotex"
VERSION = "2.0.0 - Fase 2"

# =======================================
# THREAD DE AUTENTICAÇÃO
# =======================================

class AuthThread(QThread):
    """Thread para autenticação sem bloquear a UI"""
    
    # Sinais para comunicação com UI
    login_success = pyqtSignal(dict)  # Dados do usuário
    login_error = pyqtSignal(str)     # Mensagem de erro
    progress = pyqtSignal(int)        # Progresso da operação
    
    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password
    
    def run(self):
        """Executar autenticação na API"""
        try:
            self.progress.emit(20)
            
            # Dados de login
            login_data = {
                "username": self.username,
                "password": self.password
            }
            
            self.progress.emit(50)
            
            # Fazer requisição de login
            response = requests.post(
                f"{API_BASE_URL}/api/v1/auth/login",
                json=login_data,
                timeout=10
            )
            
            self.progress.emit(80)
            
            if response.status_code == 200:
                data = response.json()
                self.progress.emit(100)
                self.login_success.emit(data)
            else:
                error_msg = "Credenciais inválidas"
                if response.status_code == 403:
                    error_msg = "Usuário inativo"
                elif response.status_code >= 500:
                    error_msg = "Erro no servidor"
                
                self.login_error.emit(error_msg)
                
        except requests.exceptions.ConnectionError:
            self.login_error.emit("Erro de conexão com o servidor")
        except requests.exceptions.Timeout:
            self.login_error.emit("Timeout na conexão")
        except Exception as e:
            self.login_error.emit(f"Erro inesperado: {str(e)}")

# =======================================
# TELA DE LOGIN PRINCIPAL
# =======================================

class LoginWindow(QMainWindow):
    """Janela principal de login"""
    
    # Sinal para indicar login bem-sucedido
    login_completed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.user_data = None
        self.auth_thread = None
        
        # Configurar janela
        self.setup_window()
        self.setup_ui()
        self.setup_styles()
        self.setup_animations()
        
        # Focar no campo de usuário
        self.username_input.setFocus()
    
    def setup_window(self):
        """Configurar propriedades da janela"""
        self.setWindowTitle(f"{SYSTEM_NAME} - Login")
        self.setFixedSize(450, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Centralizar na tela
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def setup_ui(self):
        """Configurar elementos da interface"""
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container principal com sombra
        self.main_container = QFrame()
        self.main_container.setObjectName("mainContainer")
        main_layout.addWidget(self.main_container)
        
        # Layout do container
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(20)
        
        # === CABEÇALHO ===
        self.create_header(container_layout)
        
        # === FORMULÁRIO DE LOGIN ===
        self.create_login_form(container_layout)
        
        # === BOTÕES DE AÇÃO ===
        self.create_action_buttons(container_layout)
        
        # === BARRA DE PROGRESSO ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(100)
        container_layout.addWidget(self.progress_bar)
        
        # === RODAPÉ ===
        self.create_footer(container_layout)
        
        # Espaçador para empurrar tudo para cima
        container_layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
    
    def create_header(self, layout: QVBoxLayout):
        """Criar cabeçalho com logo e títulos"""
        
        # Logo/Ícone (placeholder)
        logo_label = QLabel("🏢")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setObjectName("logoLabel")
        layout.addWidget(logo_label)
        
        # Título do sistema
        system_title = QLabel(SYSTEM_NAME)
        system_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_title.setObjectName("systemTitle")
        layout.addWidget(system_title)
        
        # Nome da empresa
        company_label = QLabel(COMPANY_NAME)
        company_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company_label.setObjectName("companyLabel")
        layout.addWidget(company_label)
        
        # Versão
        version_label = QLabel(f"Versão {VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setObjectName("versionLabel")
        layout.addWidget(version_label)
    
    def create_login_form(self, layout: QVBoxLayout):
        """Criar formulário de login"""
        
        # Container do formulário
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        layout.addWidget(form_frame)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Campo de usuário
        user_label = QLabel("Usuário:")
        user_label.setObjectName("fieldLabel")
        form_layout.addWidget(user_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Digite seu nome de usuário ou email")
        self.username_input.setObjectName("inputField")
        self.username_input.returnPressed.connect(self.handle_login)
        form_layout.addWidget(self.username_input)
        
        # Campo de senha
        password_label = QLabel("Senha:")
        password_label.setObjectName("fieldLabel")
        form_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setObjectName("inputField")
        self.password_input.returnPressed.connect(self.handle_login)
        form_layout.addWidget(self.password_input)
        
        # Checkbox "Lembrar-me"
        self.remember_checkbox = QCheckBox("Lembrar-me neste computador")
        self.remember_checkbox.setObjectName("rememberCheckbox")
        form_layout.addWidget(self.remember_checkbox)
    
    def create_action_buttons(self, layout: QVBoxLayout):
        """Criar botões de ação"""
        
        # Layout dos botões
        button_layout = QHBoxLayout()
        
        # Botão de login
        self.login_button = QPushButton("Entrar")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.handle_login)
        button_layout.addWidget(self.login_button)
        
        # Botão cancelar
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def create_footer(self, layout: QVBoxLayout):
        """Criar rodapé com informações"""
        
        # Status de conexão
        self.status_label = QLabel("🔗 Verificando conexão...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)
        
        # Verificar conexão automaticamente
        QTimer.singleShot(1000, self.check_connection)
    
    def setup_styles(self):
        """Configurar estilos CSS"""
        
        style = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        
        #mainContainer {
            background-color: white;
            border-radius: 15px;
            border: 1px solid #e0e0e0;
        }
        
        #logoLabel {
            font-size: 48px;
            margin: 10px;
        }
        
        #systemTitle {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin: 5px;
        }
        
        #companyLabel {
            font-size: 14px;
            color: #7f8c8d;
            margin: 2px;
        }
        
        #versionLabel {
            font-size: 12px;
            color: #95a5a6;
            margin: 2px;
        }
        
        #formFrame {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        
        #fieldLabel {
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        #inputField {
            padding: 12px;
            font-size: 14px;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: white;
        }
        
        #inputField:focus {
            border-color: #3498db;
            outline: none;
        }
        
        #rememberCheckbox {
            font-size: 12px;
            color: #7f8c8d;
            margin-top: 10px;
        }
        
        #loginButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 8px;
            min-width: 120px;
        }
        
        #loginButton:hover {
            background-color: #2980b9;
        }
        
        #loginButton:pressed {
            background-color: #21618c;
        }
        
        #loginButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        
        #cancelButton {
            background-color: #95a5a6;
            color: white;
            border: none;
            padding: 12px 30px;
            font-size: 14px;
            border-radius: 8px;
            min-width: 120px;
        }
        
        #cancelButton:hover {
            background-color: #7f8c8d;
        }
        
        #statusLabel {
            font-size: 12px;
            margin-top: 15px;
        }
        
        QProgressBar {
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            text-align: center;
            font-size: 12px;
        }
        
        QProgressBar::chunk {
            background-color: #3498db;
            border-radius: 4px;
        }
        """
        
        self.setStyleSheet(style)
        
        # Adicionar sombra ao container principal
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.main_container.setGraphicsEffect(shadow)
    
    def setup_animations(self):
        """Configurar animações"""
        
        # Animação de entrada
        self.setWindowOpacity(0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_animation.start()
    
    def check_connection(self):
        """Verificar conexão com o servidor"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.status_label.setText("🟢 Conectado ao servidor")
                self.status_label.setStyleSheet("color: #27ae60;")
            else:
                self.status_label.setText("🟡 Servidor com problemas")
                self.status_label.setStyleSheet("color: #f39c12;")
        except Exception:
            self.status_label.setText("🔴 Sem conexão com servidor")
            self.status_label.setStyleSheet("color: #e74c3c;")
    
    def handle_login(self):
        """Processar tentativa de login"""
        
        # Validar campos
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username:
            self.show_error("Por favor, digite seu usuário")
            self.username_input.setFocus()
            return
        
        if not password:
            self.show_error("Por favor, digite sua senha")
            self.password_input.setFocus()
            return
        
        # Desabilitar interface durante login
        self.set_login_state(True)
        
        # Criar e iniciar thread de autenticação
        self.auth_thread = AuthThread(username, password)
        self.auth_thread.login_success.connect(self.on_login_success)
        self.auth_thread.login_error.connect(self.on_login_error)
        self.auth_thread.progress.connect(self.progress_bar.setValue)
        self.auth_thread.start()
    
    def set_login_state(self, logging_in: bool):
        """Alterar estado da interface durante login"""
        
        # Mostrar/esconder barra de progresso
        self.progress_bar.setVisible(logging_in)
        if logging_in:
            self.progress_bar.setValue(0)
        
        # Desabilitar/habilitar campos
        self.username_input.setEnabled(not logging_in)
        self.password_input.setEnabled(not logging_in)
        self.login_button.setEnabled(not logging_in)
        self.remember_checkbox.setEnabled(not logging_in)
        
        # Alterar texto do botão
        if logging_in:
            self.login_button.setText("Conectando...")
        else:
            self.login_button.setText("Entrar")
    
    def on_login_success(self, data: Dict[str, Any]):
        """Callback para login bem-sucedido"""
        
        self.user_data = data
        
        # Salvar token se "lembrar-me" estiver marcado
        if self.remember_checkbox.isChecked():
            self.save_credentials(data.get("access_token"))
        
        # Mostrar mensagem de sucesso
        user = data.get("user", {})
        username = user.get("username", "Usuário")
        self.show_success(f"Bem-vindo, {username}!")
        
        # Aguardar um pouco e fechar
        QTimer.singleShot(1500, self.complete_login)
    
    def on_login_error(self, error_message: str):
        """Callback para erro de login"""
        
        self.set_login_state(False)
        self.show_error(error_message)
        
        # Limpar senha e focar no campo
        self.password_input.clear()
        self.password_input.setFocus()
    
    def complete_login(self):
        """Completar processo de login"""
        
        self.set_login_state(False)
        
        # Emitir sinal de login completo
        self.login_completed.emit(self.user_data)
        
        # Fechar janela de login
        self.close()
    
    def save_credentials(self, token: str):
        """Salvar credenciais para lembrar usuário"""
        try:
            # Implementação futura: salvar token de forma segura
            # Por enquanto, apenas log para desenvolvimento
            print(f"Token salvo para sessão: {token[:20]}...")
        except Exception as e:
            print(f"Erro ao salvar credenciais: {e}")
    
    def show_error(self, message: str):
        """Mostrar mensagem de erro"""
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Erro de Login")
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        msg_box.exec()
    
    def show_success(self, message: str):
        """Mostrar mensagem de sucesso"""
        
        self.status_label.setText(f"✅ {message}")
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")

# =======================================
# FUNÇÃO PRINCIPAL
# =======================================

def main():
    """Função principal para testar a tela de login"""
    
    app = QApplication(sys.argv)
    app.setApplicationName(SYSTEM_NAME)
    app.setApplicationVersion(VERSION)
    
    # Criar e mostrar janela de login
    login_window = LoginWindow()
    
    # Conectar sinal de login completo
    def on_login_completed(user_data):
        print("Login realizado com sucesso!")
        print("Dados do usuário:", user_data)
        app.quit()
    
    login_window.login_completed.connect(on_login_completed)
    login_window.show()
    
    # Executar aplicação
    sys.exit(app.exec())

if __name__ == "__main__":
    main()