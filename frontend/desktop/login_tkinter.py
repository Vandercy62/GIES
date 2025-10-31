"""
SISTEMA ERP PRIMOTEX - TELA DE LOGIN DESKTOP (TKINTER)
====================================================

Interface gráfica de login usando tkinter nativo.
Integração com API de autenticação JWT.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import threading
import requests
import json
from typing import Optional, Dict, Any

# =======================================
# CONFIGURAÇÕES
# =======================================

API_BASE_URL = "http://127.0.0.1:8002"
COMPANY_NAME = "Primotex - Forros e Divisórias Eireli"
SYSTEM_NAME = "Sistema ERP Primotex"
VERSION = "2.0.0 - Fase 2"

# =======================================
# CLASSE PRINCIPAL DE LOGIN
# =======================================

class LoginWindow:
    """Janela principal de login usando tkinter"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.user_data = None
        self.token = None
        
        # Configurar janela
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.check_connection()
        
        # Focar no campo de usuário
        self.username_entry.focus()
    
    def setup_window(self):
        """Configurar propriedades da janela"""
        
        self.root.title(f"{SYSTEM_NAME} - Login")
        self.root.geometry("450x600")
        self.root.resizable(False, False)
        
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
            "Login.TEntry",
            font=('Arial', 11),
            padding=8
        )
        
        # Estilo para labels
        style.configure(
            "Title.TLabel",
            font=('Arial', 18, 'bold'),
            background='white',
            foreground='#2c3e50'
        )
        
        style.configure(
            "Subtitle.TLabel",
            font=('Arial', 10),
            background='white',
            foreground='#7f8c8d'
        )
        
        style.configure(
            "Field.TLabel",
            font=('Arial', 10, 'bold'),
            background='#f8f9fa',
            foreground='#2c3e50'
        )
    
    def create_widgets(self):
        """Criar widgets da interface"""
        
        # Container principal
        main_frame = tk.Frame(self.root, bg='white', relief='raised', bd=2)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # === CABEÇALHO ===
        self.create_header(main_frame)
        
        # === FORMULÁRIO ===
        self.create_form(main_frame)
        
        # === BOTÕES ===
        self.create_buttons(main_frame)
        
        # === RODAPÉ ===
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        """Criar cabeçalho"""
        
        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill='x', padx=30, pady=(30, 20))
        
        # Logo/Ícone
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
            style="Title.TLabel"
        )
        title_label.pack(pady=(10, 5))
        
        # Nome da empresa
        company_label = ttk.Label(
            header_frame,
            text=COMPANY_NAME,
            style="Subtitle.TLabel"
        )
        company_label.pack()
        
        # Versão
        version_label = ttk.Label(
            header_frame,
            text=f"Versão {VERSION}",
            style="Subtitle.TLabel"
        )
        version_label.pack(pady=(2, 0))
    
    def create_form(self, parent):
        """Criar formulário de login"""
        
        # Container do formulário
        form_frame = tk.Frame(parent, bg='#f8f9fa', relief='groove', bd=1)
        form_frame.pack(fill='x', padx=30, pady=20)
        
        form_inner = tk.Frame(form_frame, bg='#f8f9fa')
        form_inner.pack(padx=25, pady=25)
        
        # Campo de usuário
        user_label = ttk.Label(
            form_inner,
            text="Usuário:",
            style="Field.TLabel"
        )
        user_label.pack(anchor='w', pady=(0, 5))
        
        self.username_entry = ttk.Entry(
            form_inner,
            font=('Arial', 11),
            width=35,
            style="Login.TEntry"
        )
        self.username_entry.pack(pady=(0, 15))
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        
        # Campo de senha
        password_label = ttk.Label(
            form_inner,
            text="Senha:",
            style="Field.TLabel"
        )
        password_label.pack(anchor='w', pady=(0, 5))
        
        self.password_entry = ttk.Entry(
            form_inner,
            font=('Arial', 11),
            width=35,
            show='*',
            style="Login.TEntry"
        )
        self.password_entry.pack(pady=(0, 15))
        self.password_entry.bind('<Return>', lambda e: self.handle_login())
        
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
            style="Login.TButton",
            command=self.handle_login,
            width=15
        )
        self.login_button.pack(side='left', padx=(0, 10))
        
        # Botão cancelar
        cancel_button = ttk.Button(
            inner_frame,
            text="Cancelar",
            command=self.root.quit,
            width=15
        )
        cancel_button.pack(side='left')
        
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
        footer_frame.pack(fill='x', side='bottom', padx=30, pady=(10, 30))
        
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
        
        def update():
            self.status_label.config(text=text, fg=color)
        
        self.root.after(0, update)
    
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
        
        def update():
            self.progress['value'] = value
        
        self.root.after(0, update)
    
    def on_login_success(self, data):
        """Callback para login bem-sucedido"""
        
        def update():
            self.user_data = data
            self.token = data.get("access_token")
            
            # Salvar token se solicitado
            if self.remember_var.get():
                self.save_credentials(self.token)
            
            # Mostrar mensagem de sucesso
            user = data.get("user", {})
            username = user.get("username", "Usuário")
            
            self.update_status(f"✅ Bem-vindo, {username}!", "#27ae60")
            
            # Aguardar e completar login
            self.root.after(1500, self.complete_login)
        
        self.root.after(0, update)
    
    def on_login_error(self, error_message):
        """Callback para erro de login"""
        
        def update():
            self.set_login_state(False)
            messagebox.showerror("Erro de Login", error_message)
            
            # Limpar senha e focar
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
        
        self.root.after(0, update)
    
    def complete_login(self):
        """Completar processo de login"""
        
        print("Login realizado com sucesso!")
        print("Dados do usuário:", self.user_data)
        
        # Fechar janela de login
        self.root.quit()
    
    def save_credentials(self, token):
        """Salvar credenciais"""
        try:
            print(f"Token salvo para sessão: {token[:20]}...")
        except Exception as e:
            print(f"Erro ao salvar credenciais: {e}")
    
    def run(self):
        """Executar a aplicação"""
        
        try:
            self.root.mainloop()
            return self.user_data
        except KeyboardInterrupt:
            return None
        finally:
            try:
                self.root.destroy()
            except Exception as e:
                print(f"Warning: Erro ao destruir janela de login: {e}")

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
        print(f"🔑 Token: {user_data.get('access_token', '')[:30]}...")
    else:
        print("\n❌ Login cancelado ou falhou")

if __name__ == "__main__":
    main()