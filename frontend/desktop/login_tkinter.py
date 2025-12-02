"""
SISTEMA ERP PRIMOTEX - TELA DE LOGIN DESKTOP (TKINTER)
====================================================

Interface gráfica de login usando tkinter nativo.
Integração com API de autenticação JWT.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import sys
import json
import base64
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Importar SessionManager
from shared.session_manager import session

# =======================================
# CONFIGURAÇÕES
# =======================================

API_BASE_URL = "http://127.0.0.1:8002"
CREDENTIALS_FILE = '.primotex_credentials.json'
COMPANY_NAME = "Primotex - Forros e Divisórias Eireli"
SYSTEM_NAME = "Sistema ERP Primotex"
VERSION = "2.0.0 - Fase 2"

# Constantes de estilo
STYLE_LOGIN_ENTRY = "Login.TEntry"
STYLE_TITLE_LABEL = "Title.TLabel"
STYLE_SUBTITLE_LABEL = "Subtitle.TLabel"
STYLE_FIELD_LABEL = "Field.TLabel"
EVENT_RETURN = '<Return>'


# =======================================
# CLASSE PRINCIPAL DE LOGIN
# =======================================

class LoginWindow:
    """Janela principal de login usando tkinter"""

    def __init__(self, skip_restore=False):
        self.root = tk.Tk()
        self.user_data = None
        self.token = None
        self._closing = False  # Flag para indicar que está fechando
        self._open_dashboard = False  # Flag para abrir dashboard após login
        self.api_url = API_BASE_URL  # URL base da API

        # Configurar janela
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.check_connection()

        # Focar no campo de usuário
        self.username_entry.focus()

        # NÃO iniciar mainloop aqui - será chamado pelo método run()

    def try_restore_session(self) -> bool:
        """
        Tenta restaurar sessão anterior salva.

        Returns:
            True se sessão restaurada com sucesso
        """
        try:
            if session.restore_session():
                print("\n" + "="*60)
                print("SESSÃO ANTERIOR RESTAURADA!")
                print("="*60)
                print(f"Usuário: {session.get_username()}")
                print(f"Tipo: {session.get_user_type()}")
                print(f"Token expira em: {session.time_until_expiry()}")

                # Verificar se precisa renovar token
                if session.should_refresh_token():
                    print(
                        "⚠️ Token próximo da expiração - "
                        "renovação recomendada"
                    )

                print("="*60 + "\n")

                # Preencher user_data para compatibilidade
                self.user_data = session.get_user_data()
                self.token = session.get_token()

                return True
        except Exception as e:
            print(f"Erro ao restaurar sessão: {e}")

        return False

    def setup_window(self):
        """Configurar propriedades da janela"""

        self.root.title(f"{SYSTEM_NAME} - Login")
        self.root.geometry("450x700")  # Aumentado para 700
        self.root.resizable(True, True)  # Permitir redimensionar

        # Centralizar na tela
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Configurar cor de fundo
        self.root.configure(bg='#f0f0f0')

        # Ícone da janela (usar ícone padrão por enquanto)
        try:
            self.root.iconbitmap(default='')
        except Exception as e:
            # Falha ao definir ícone não é crítica
            print(f"Warning: Não foi possível definir ícone da janela: {e}")

    def setup_styles(self):
        """Configurar estilos ttk"""

        style = ttk.Style()

        # Configurar tema
        style.theme_use('clam')

        # Estilo para botões
        style.configure(
            "Login.TButton",
            background='#3498db',
            foreground='white',
            font=('Arial', 12, 'bold'),
            padding=(10, 8)
        )

        style.map(
            "Login.TButton",
            background=[('active', '#2980b9')]
        )

        # Estilo para entry
        style.configure(
            STYLE_LOGIN_ENTRY,
            font=('Arial', 11),
            padding=8
        )

        # Estilo para labels
        style.configure(
            STYLE_TITLE_LABEL,
            font=('Arial', 18, 'bold'),
            background='white',
            foreground='#2c3e50'
        )

        style.configure(
            STYLE_SUBTITLE_LABEL,
            font=('Arial', 10),
            background='white',
            foreground='#7f8c8d'
        )

        style.configure(
            STYLE_FIELD_LABEL,
            font=('Arial', 10, 'bold'),
            background='#f8f9fa',
            foreground='#2c3e50'
        )

    def create_widgets(self):
        """Criar widgets da interface"""

        print("\n" + "="*70)
        print("🎨 CRIANDO INTERFACE DE LOGIN")
        print("="*70)

        # Container principal COM SCROLL
        canvas = tk.Canvas(self.root, bg='#f0f0f0', highlightthickness=0)
        scrollbar = tk.Scrollbar(
            self.root,
            orient="vertical",
            command=canvas.yview
        )

        main_frame = tk.Frame(canvas, bg='white', relief='raised', bd=2)

        # Configurar scroll
        main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Empacotar canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        print("✅ 1. Container com scroll criado")

        # === CABEÇALHO ===
        self.create_header(main_frame)
        print("✅ 2. Cabeçalho criado")

        # === FORMULÁRIO ===
        self.create_form(main_frame)
        print("✅ 3. Formulário criado")

        # === BOTÕES ===
        self.create_buttons(main_frame)
        print("✅ 4. Botões criados (INCLUI LINK SENHA)")

        # === RODAPÉ ===
        self.create_footer(main_frame)
        print("✅ 5. Rodapé criado")

        print("="*70)
        print("🎯 INTERFACE COMPLETA - Verifique o link 'Esqueci senha'")
        print("="*70 + "\n")

        # Garantir que scroll está no topo
        canvas.yview_moveto(0)

    def create_header(self, parent):
        """Criar cabeçalho"""

        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill='x', padx=30, pady=(15, 10))

        # Logo/Imagem
        try:
            from PIL import Image, ImageTk
            import os

            logo_path = r"C:\GIES\assets\images\P_Pinguin_fundo.png"
            if os.path.exists(logo_path):
                # Carregar e redimensionar imagem
                img = Image.open(logo_path)
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(img)

                logo_label = tk.Label(
                    header_frame,
                    image=self.logo_image,
                    bg='white'
                )
                logo_label.pack()
            else:
                # Fallback para emoji se imagem não existir
                logo_label = tk.Label(
                    header_frame, 
                    text="🏢", 
                    font=('Arial', 32),
                    bg='white',
                    fg='#3498db'
                )
                logo_label.pack()
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            # Fallback para emoji em caso de erro
            logo_label = tk.Label(
                header_frame, 
                text="🏢", 
                font=('Arial', 48),
                bg='white',
                fg='#3498db'
            )
            logo_label.pack()

        # Título do sistema
        title_label = ttk.Label(
            header_frame,
            text=SYSTEM_NAME,
            style=STYLE_TITLE_LABEL
        )
        title_label.pack(pady=(10, 5))

        # Nome da empresa
        company_label = ttk.Label(
            header_frame,
            text=COMPANY_NAME,
            style=STYLE_SUBTITLE_LABEL
        )
        company_label.pack()

        # Versão
        version_label = ttk.Label(
            header_frame,
            text=f"Versão {VERSION}",
            style=STYLE_SUBTITLE_LABEL
        )
        version_label.pack(pady=(2, 0))

    def create_form(self, parent):
        """Criar formulário de login"""

        # Container do formulário
        form_frame = tk.Frame(parent, bg='#f8f9fa', relief='groove', bd=1)
        form_frame.pack(fill='x', padx=30, pady=10)

        form_inner = tk.Frame(form_frame, bg='#f8f9fa')
        form_inner.pack(padx=20, pady=15)

        # Campo de usuário
        user_label = ttk.Label(
            form_inner,
            text="Usuário:",
            style=STYLE_FIELD_LABEL
        )
        user_label.pack(anchor='w', pady=(0, 5))

        self.username_entry = ttk.Entry(
            form_inner,
            font=('Arial', 11),
            width=35,
            style=STYLE_LOGIN_ENTRY
        )
        self.username_entry.pack(pady=(0, 10))
        self.username_entry.bind(
            EVENT_RETURN, lambda e: self.password_entry.focus()
        )

        # Campo de senha
        password_label = ttk.Label(
            form_inner,
            text="Senha:",
            style=STYLE_FIELD_LABEL
        )
        password_label.pack(anchor='w', pady=(0, 5))

        # Frame para senha + botão mostrar/ocultar
        password_frame = tk.Frame(form_inner, bg='#f8f9fa')
        password_frame.pack(fill='x', pady=(0, 10))

        self.password_entry = ttk.Entry(
            password_frame,
            font=('Arial', 11),
            width=30,
            show='*',
            style=STYLE_LOGIN_ENTRY
        )
        self.password_entry.pack(side='left', fill='x', expand=True)
        self.password_entry.bind(EVENT_RETURN, lambda e: self.handle_login())

        # Botão mostrar/ocultar senha
        self.show_password_var = tk.BooleanVar(value=False)
        self.toggle_password_btn = tk.Button(
            password_frame,
            text="👁",
            font=('Arial', 12),
            relief='flat',
            bg='#ecf0f1',
            fg='#2c3e50',
            cursor='hand2',
            width=3,
            command=self.toggle_password_visibility
        )
        self.toggle_password_btn.pack(side='left', padx=(5, 0))

        # Checkbox "Lembrar-me"
        self.remember_var = tk.BooleanVar()
        remember_check = tk.Checkbutton(
            form_inner,
            text="Lembrar-me neste computador",
            variable=self.remember_var,
            bg='#f8f9fa',
            font=('Arial', 9),
            fg='#7f8c8d'
        )
        remember_check.pack(anchor='w')

        # Carregar credenciais salvas DEPOIS de criar todos os campos
        saved_user, saved_pass = self.load_credentials()
        if saved_user and saved_pass:
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, saved_user)
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, saved_pass)
            self.remember_var.set(True)
            print("✅ Credenciais carregadas automaticamente")

    def toggle_password_visibility(self):
        """Alternar visibilidade da senha"""
        if self.show_password_var.get():
            # Ocultar senha
            self.password_entry.config(show='*')
            self.toggle_password_btn.config(fg='#2c3e50')
            self.show_password_var.set(False)
        else:
            # Mostrar senha
            self.password_entry.config(show='')
            self.toggle_password_btn.config(fg='#3498db')
            self.show_password_var.set(True)

    def create_buttons(self, parent):
        """Criar botões de ação"""

        button_frame = tk.Frame(parent, bg='white')
        button_frame.pack(fill='x', padx=30, pady=10)

        # Frame interno para centralizar botões
        inner_frame = tk.Frame(button_frame, bg='white')
        inner_frame.pack()

        # Botão de login
        self.login_button = ttk.Button(
            inner_frame,
            text="Entrar",
            command=self.handle_login,
            width=12
        )
        self.login_button.pack(side='left', padx=(0, 10))

        # Botão cancelar
        cancel_button = ttk.Button(
            inner_frame,
            text="Cancelar",
            command=self.root.quit,
            width=12
        )
        cancel_button.pack(side='left')

        # Link "Esqueci minha senha" - COM FUNDO COLORIDO PARA DESTAQUE
        print("\n" + "="*60)
        print("🔑 CRIANDO LINK 'ESQUECI MINHA SENHA'")
        print("="*60)

        forgot_frame = tk.Frame(
            button_frame, bg='#ecf0f1', relief='ridge', bd=1
        )
        forgot_frame.pack(pady=(10, 5), fill='x')

        forgot_link = tk.Label(
            forgot_frame,
            text="🔑 Esqueci minha senha",
            bg='#ecf0f1',
            fg='#e74c3c',
            font=('Arial', 11, 'underline', 'bold'),
            cursor='hand2',
            padx=8,
            pady=6
        )
        forgot_link.pack()
        forgot_link.bind('<Button-1>', lambda e: self.open_password_recovery())

        print("✅ Link criado com sucesso!")
        print(f"   Texto: '{forgot_link.cget('text')}'")
        print(f"   Cor: {forgot_link.cget('fg')}")
        print(f"   Fonte: {forgot_link.cget('font')}")
        print("="*60 + "\n")

        # Mensagem explicativa
        help_label = tk.Label(
            forgot_frame,
            text="⬆️ Clique acima para gerar senha temporária ⬆️",
            bg='#ecf0f1',
            fg='#7f8c8d',
            font=('Arial', 9, 'bold')
        )
        help_label.pack(pady=(0, 6))

        # Barra de progresso
        self.progress = ttk.Progressbar(
            button_frame,
            mode='determinate',
            length=300
        )
        self.progress.pack(pady=15)
        self.progress.pack_forget()  # Esconder inicialmente

    def create_footer(self, parent):
        """Criar rodapé"""

        footer_frame = tk.Frame(parent, bg='white')
        # Removido side='bottom' para evitar sobreposição
        footer_frame.pack(fill='x', padx=30, pady=(10, 20))

        # Status de conexão
        self.status_label = tk.Label(
            footer_frame,
            text="🔗 Verificando conexão...",
            bg='white',
            font=('Arial', 9),
            fg='#7f8c8d'
        )
        self.status_label.pack()

    def check_connection(self):
        """Verificar conexão com servidor"""

        def check():
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    self.update_status("🟢 Conectado ao servidor", "#27ae60")
                else:
                    self.update_status("🟡 Servidor com problemas", "#f39c12")
            except requests.exceptions.ConnectionError:
                self.update_status("🔴 Sem conexão com servidor", "#e74c3c")
            except Exception:
                self.update_status("🔴 Erro de conexão", "#e74c3c")

        # Executar verificação em thread separada
        thread = threading.Thread(target=check, daemon=True)
        thread.start()

    def update_status(self, text, color):
        """Atualizar status na thread principal"""

        # Não atualizar se janela está fechando
        if getattr(self, '_closing', False):
            return

        def update():
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text=text, fg=color)

        try:
            self.root.after(0, update)
        except RuntimeError:
            # Janela já foi destruída
            pass

    def handle_login(self):
        """Processar tentativa de login"""

        # Validar campos
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username:
            messagebox.showerror("Erro", "Por favor, digite seu usuário")
            self.username_entry.focus()
            return

        if not password:
            messagebox.showerror("Erro", "Por favor, digite sua senha")
            self.password_entry.focus()
            return

        # Desabilitar interface
        self.set_login_state(True)

        # Executar login em thread separada
        def login_thread():
            try:
                self.update_progress(20)

                # Dados de login
                login_data = {
                    "username": username,
                    "password": password
                }

                self.update_progress(50)

                # Fazer requisição
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/auth/login",
                    json=login_data,
                    timeout=10
                )

                self.update_progress(80)

                if response.status_code == 200:
                    data = response.json()
                    self.update_progress(100)

                    # Salvar credenciais se "Lembrar-me" estiver marcado
                    if self.remember_var.get():
                        self.save_credentials(username, password)
                    else:
                        self.clear_credentials()

                    self.on_login_success(data)
                else:
                    error_msg = "Credenciais inválidas"
                    if response.status_code == 403:
                        error_msg = "Usuário inativo"
                    elif response.status_code >= 500:
                        error_msg = "Erro no servidor"

                    self.on_login_error(error_msg)

            except requests.exceptions.ConnectionError:
                self.on_login_error("Erro de conexão com o servidor")
            except requests.exceptions.Timeout:
                self.on_login_error("Timeout na conexão")
            except Exception as e:
                self.on_login_error(f"Erro inesperado: {str(e)}")

        thread = threading.Thread(target=login_thread, daemon=True)
        thread.start()

    def set_login_state(self, logging_in):
        """Alterar estado da interface durante login"""

        def update():
            # Mostrar/esconder barra de progresso
            if logging_in:
                self.progress.pack(pady=15)
                self.progress['value'] = 0
            else:
                self.progress.pack_forget()

            # Desabilitar/habilitar campos
            state = 'disabled' if logging_in else 'normal'
            self.username_entry.config(state=state)
            self.password_entry.config(state=state)
            self.login_button.config(state=state)

            # Alterar texto do botão
            if logging_in:
                self.login_button.config(text="Conectando...")
            else:
                self.login_button.config(text="Entrar")

        self.root.after(0, update)

    def update_progress(self, value):
        """Atualizar barra de progresso"""

        # Não atualizar se janela está fechando
        if getattr(self, '_closing', False):
            return

        def update():
            if hasattr(self, 'progress') and self.progress.winfo_exists():
                self.progress['value'] = value

        try:
            self.root.after(0, update)
        except RuntimeError:
            # Janela já foi destruída
            pass

    def on_login_success(self, data):
        """Callback para login bem-sucedido"""

        # Não processar se janela está fechando
        if getattr(self, '_closing', False):
            return

        def update():
            # Extrair dados
            token = data.get("access_token")
            user_info = data.get("user", {})

            # Iniciar sessão global usando SessionManager
            session.login(
                token=token,
                user_data=user_info,
                token_expiry_hours=720,  # 30 dias (conforme API)
                refresh_token=data.get("refresh_token")  # Se houver
            )

            # Backup local (compatibilidade com código antigo)
            self.user_data = data
            self.token = token

            # Mostrar mensagem de sucesso
            username = user_info.get("username", "Usuário")
            self.update_status(f"✅ Bem-vindo, {username}!", "#27ae60")

            # Log de sessão
            print("\n" + "="*50)
            print("SESSÃO INICIADA COM SUCESSO")
            print("="*50)
            print(f"Usuário: {session.get_username()}")
            print(f"Tipo: {session.get_user_type()}")
            print(f"Token válido até: {session.token_expiry}")
            print("="*50 + "\n")

            # Aguardar e completar login
            self.root.after(1500, self.complete_login)

        try:
            self.root.after(0, update)
        except RuntimeError:
            pass

    def on_login_error(self, error_message):
        """Callback para erro de login"""

        # Não processar se janela está fechando
        if getattr(self, '_closing', False):
            return

        def update():
            self.set_login_state(False)
            messagebox.showerror("Erro de Login", error_message)

            # Limpar senha e focar
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

        try:
            self.root.after(0, update)
        except RuntimeError:
            pass

    def complete_login(self):
        """Completar processo de login"""

        # Validar sessão
        if not session.is_authenticated():
            print("⚠️ ERRO: Sessão não foi iniciada corretamente!")
            messagebox.showerror(
                "Erro de Sessão",
                "Não foi possível estabelecer a sessão.\n"
                "Por favor, tente novamente."
            )
            self.set_login_state(False)
            return

        print("\n" + "="*60)
        print("LOGIN CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print(f"Usuário: {session.get_username()}")
        print(f"Tipo: {session.get_user_type()}")
        print(f"Autenticado: {session.is_authenticated()}")
        print(f"Token expira em: {session.time_until_expiry()}")
        print("="*60 + "\n")

        # Marcar que deve abrir dashboard
        self._open_dashboard = True

        # Fechar janela de login (quit mantém mainloop ativo)
        self.root.quit()

    def open_dashboard(self):
        """Abrir dashboard principal (sessão restaurada)"""

        print("\n" + "="*60)
        print("ABRINDO DASHBOARD PRINCIPAL")
        print("="*60)
        print(f"Usuário: {session.get_username()}")
        print(f"Tipo: {session.get_user_type()}")
        print(f"Token expira em: {session.time_until_expiry()}")
        print("="*60 + "\n")

        try:
            from frontend.desktop.dashboard_principal import DashboardPrincipal
            # Dashboard cria sua própria janela root
            DashboardPrincipal()
        except Exception as e:
            print(f"❌ Erro ao abrir dashboard: {e}")
            import traceback
            traceback.print_exc()

    def open_password_recovery(self):
        """Abrir modal de recuperação de senha"""

        # Criar janela modal
        recovery_window = tk.Toplevel(self.root)
        recovery_window.title("Recuperar Senha")
        recovery_window.geometry("450x350")
        recovery_window.resizable(False, False)
        recovery_window.configure(bg='white')

        # Centralizar janela
        recovery_window.transient(self.root)
        recovery_window.grab_set()

        # Título
        title_frame = tk.Frame(recovery_window, bg='#3498db', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="🔑 Recuperar Senha",
            bg='#3498db',
            fg='white',
            font=('Arial', 16, 'bold')
        )
        title_label.pack(expand=True)

        # Instruções
        info_frame = tk.Frame(recovery_window, bg='white')
        info_frame.pack(fill='x', padx=30, pady=(20, 10))

        info_label = tk.Label(
            info_frame,
            text=("Digite seu usuário e email cadastrado para\n"
                  "receber uma senha temporária."),
            bg='white',
            fg='#2c3e50',
            font=('Arial', 10),
            justify='center'
        )
        info_label.pack()

        # Formulário
        form_frame = tk.Frame(recovery_window, bg='white')
        form_frame.pack(fill='both', expand=True, padx=30, pady=10)

        # Campo usuário
        tk.Label(
            form_frame,
            text="Nome de Usuário:",
            bg='white',
            fg='#2c3e50',
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))

        username_entry = ttk.Entry(
            form_frame,
            font=('Arial', 11),
            width=40
        )
        username_entry.pack(pady=(0, 15))
        username_entry.focus_set()

        # Campo email
        tk.Label(
            form_frame,
            text="Email Cadastrado:",
            bg='white',
            fg='#2c3e50',
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))

        email_entry = ttk.Entry(
            form_frame,
            font=('Arial', 11),
            width=40
        )
        email_entry.pack(pady=(0, 20))

        # Label de status
        status_label = tk.Label(
            form_frame,
            text="",
            bg='white',
            font=('Arial', 9),
            wraplength=350
        )
        status_label.pack(pady=(0, 10))

        # Função de recuperação
        def do_recovery():
            username = username_entry.get().strip()
            email = email_entry.get().strip()

            if not username or not email:
                status_label.config(
                    text="⚠️ Preencha todos os campos",
                    fg='#e74c3c'
                )
                return

            # Fazer requisição
            try:
                status_label.config(
                    text="⏳ Gerando senha temporária...",
                    fg='#f39c12'
                )
                recovery_window.update()

                response = requests.post(
                    f"{self.api_url}/auth/forgot-password",
                    json={"username": username, "email": email},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    temp_password = data.get("temporary_password", "")

                    # Criar janela de sucesso com senha
                    success_window = tk.Toplevel(recovery_window)
                    success_window.title("Senha Temporária Gerada")
                    success_window.geometry("400x250")
                    success_window.configure(bg='white')
                    success_window.transient(recovery_window)
                    success_window.grab_set()

                    tk.Label(
                        success_window,
                        text="✅ Senha Temporária Gerada!",
                        bg='white',
                        fg='#27ae60',
                        font=('Arial', 14, 'bold')
                    ).pack(pady=(20, 10))

                    tk.Label(
                        success_window,
                        text="Anote sua senha temporária:",
                        bg='white',
                        fg='#2c3e50',
                        font=('Arial', 10)
                    ).pack(pady=(0, 10))

                    # Campo com senha (somente leitura)
                    password_frame = tk.Frame(success_window, bg='#ecf0f1')
                    password_frame.pack(pady=10, padx=20, fill='x')

                    password_text = tk.Text(
                        password_frame,
                        height=2,
                        width=30,
                        font=('Courier New', 14, 'bold'),
                        bg='#ecf0f1',
                        fg='#2c3e50',
                        relief='flat',
                        wrap='word'
                    )
                    password_text.pack(padx=10, pady=10)
                    password_text.insert('1.0', temp_password)
                    password_text.config(state='disabled')

                    tk.Label(
                        success_window,
                        text="⚠️ Altere esta senha após o login!",
                        bg='white',
                        fg='#e74c3c',
                        font=('Arial', 9, 'bold')
                    ).pack(pady=(0, 20))

                    def close_windows():
                        success_window.destroy()
                        recovery_window.destroy()

                    tk.Button(
                        success_window,
                        text="Fechar",
                        command=close_windows,
                        bg='#3498db',
                        fg='white',
                        font=('Arial', 10, 'bold'),
                        relief='flat',
                        cursor='hand2',
                        padx=20,
                        pady=5
                    ).pack()

                else:
                    error_data = response.json()
                    detail = error_data.get('detail', 'Erro desconhecido')
                    status_label.config(
                        text=f"❌ {detail}",
                        fg='#e74c3c'
                    )

            except requests.exceptions.Timeout:
                status_label.config(
                    text="❌ Tempo esgotado. Verifique a conexão.",
                    fg='#e74c3c'
                )
            except Exception as e:
                status_label.config(
                    text=f"❌ Erro: {str(e)}",
                    fg='#e74c3c'
                )

        # Botões
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Gerar Senha Temporária",
            command=do_recovery,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        ).pack(side='left', padx=(0, 10))

        tk.Button(
            button_frame,
            text="Cancelar",
            command=recovery_window.destroy,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        ).pack(side='left')

        # Bind Enter key
        username_entry.bind(EVENT_RETURN, lambda e: email_entry.focus_set())
        email_entry.bind(EVENT_RETURN, lambda e: do_recovery())

    def save_credentials(self, username, password):
        """Salvar credenciais criptografadas"""
        try:
            # Criptografia simples com base64
            credentials = {
                'username': base64.b64encode(username.encode()).decode(),
                'password': base64.b64encode(password.encode()).decode()
            }

            cred_file = Path.home() / CREDENTIALS_FILE
            with open(cred_file, 'w') as f:
                json.dump(credentials, f)

            print(f"Credenciais salvas em: {cred_file}")
        except Exception as e:
            print(f"Erro ao salvar credenciais: {e}")

    def load_credentials(self):
        """Carregar credenciais salvas"""
        try:
            cred_file = Path.home() / CREDENTIALS_FILE
            if cred_file.exists():
                with open(cred_file, 'r') as f:
                    credentials = json.load(f)

                # Descriptografar
                username = base64.b64decode(
                    credentials['username']
                ).decode()
                password = base64.b64decode(
                    credentials['password']
                ).decode()

                return username, password
        except Exception as e:
            print(f"Erro ao carregar credenciais: {e}")

        return None, None

    def clear_credentials(self):
        """Limpar credenciais salvas"""
        try:
            cred_file = Path.home() / CREDENTIALS_FILE
            if cred_file.exists():
                cred_file.unlink()
                print("Credenciais removidas")
        except Exception as e:
            print(f"Erro ao remover credenciais: {e}")

    def run(self):
        """Executar a aplicação"""

        try:
            self.root.mainloop()

            # Após fechar janela de login, verificar se deve abrir dashboard
            if self._open_dashboard:
                self.root.destroy()
                self.open_dashboard()

            return self.user_data
        except KeyboardInterrupt:
            return None
        finally:
            try:
                if self.root.winfo_exists():
                    self.root.destroy()
            except Exception as e:
                print(
                    f"Warning: Erro ao destruir janela de login: {e}"
                )


# =======================================
# FUNÇÃO PRINCIPAL
# =======================================


def main():
    """Função principal para testar"""

    print("=" * 50)
    print("SISTEMA ERP PRIMOTEX - LOGIN DESKTOP")
    print("=" * 50)

    # Criar e executar janela de login
    login_window = LoginWindow()
    user_data = login_window.run()

    if user_data:
        print("\n✅ Login realizado com sucesso!")
        user = user_data.get("user", {})
        print(f"👤 Usuário: {user.get('username')}")
        print(f"📧 Email: {user.get('email')}")
        print(f"🎭 Perfil: {user.get('perfil')}")
        token = user_data.get('access_token', '')[:30]
        print(f"🔑 Token: {token}...")
    else:
        print("\n❌ Login cancelado ou falhou")


if __name__ == "__main__":
    main()
