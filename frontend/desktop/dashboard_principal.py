"""
DASHBOARD PRINCIPAL INTEGRADO - ERP PRIMOTEX
Sistema completo com autenticação, navegação e controle de acesso
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import threading
import requests
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.session_manager import session
from frontend.desktop.auth_middleware import (
    require_login, logout_user, get_current_user_info,
    get_token_for_api, create_auth_header
)

# Configurações
API_BASE_URL = "http://127.0.0.1:8002/api/v1"


@require_login(redirect_to_login=True)
class DashboardPrincipal:
    """
    Dashboard principal do sistema com autenticação integrada.

    Features:
    - Autenticação obrigatória
    - Barra de usuário (nome, perfil, logout)
    - 3 Widgets principais (OS, Agendamento, Financeiro)
    - Navegação rápida
    - Controle de permissões
    """

    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_user_bar()
        self.create_main_content()
        self.load_data()

        # Iniciar mainloop
        self.root.mainloop()

    def setup_window(self):
        """Configurar janela principal"""
        self.root.title("ERP Primotex - Dashboard Principal")
        self.root.geometry("1400x800")

        # Centralizar
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.configure(bg='#f0f0f0')

        # Evento de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_user_bar(self):
        """Criar barra superior com informações do usuário"""
        user_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        user_frame.pack(fill='x', side='top')
        user_frame.pack_propagate(False)

        # Info do usuário (esquerda)
        info_frame = tk.Frame(user_frame, bg='#2c3e50')
        info_frame.pack(side='left', padx=20, pady=10)

        user_info = get_current_user_info()
        username = user_info.get('username', 'Usuário')
        user_type = user_info.get('user_type') or 'Usuário'

        # Ícone + Nome
        user_label = tk.Label(
            info_frame,
            text=f"👤 {username}",
            bg='#2c3e50',
            fg='white',
            font=('Arial', 12, 'bold')
        )
        user_label.pack(side='left', padx=(0, 15))

        # Perfil
        perfil_label = tk.Label(
            info_frame,
            text=f"📋 {user_type.title() if user_type else 'Usuário'}",
            bg='#2c3e50',
            fg='#ecf0f1',
            font=('Arial', 10)
        )
        perfil_label.pack(side='left')

        # Botões (direita)
        button_frame = tk.Frame(user_frame, bg='#2c3e50')
        button_frame.pack(side='right', padx=20, pady=10)

        # Botão Logout
        logout_btn = tk.Button(
            button_frame,
            text="🚪 Sair",
            command=self.handle_logout,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        logout_btn.pack(side='right')

        # Botão Refresh
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Atualizar",
            command=self.load_data,
            bg='#3498db',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        refresh_btn.pack(side='right', padx=(0, 10))

    def create_main_content(self):
        """Criar conteúdo principal do dashboard"""
        # Container principal
        main_container = tk.Frame(self.root, bg='#ecf0f1')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Título
        title_frame = tk.Frame(main_container, bg='#ecf0f1')
        title_frame.pack(fill='x', pady=(0, 20))

        title_label = tk.Label(
            title_frame,
            text="Dashboard Principal",
            font=('Arial', 24, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title_label.pack(side='left')

        date_label = tk.Label(
            title_frame,
            text=datetime.now().strftime("%d/%m/%Y %H:%M"),
            font=('Arial', 12),
            bg='#ecf0f1',
            fg='#7f8c8d'
        )
        date_label.pack(side='right')

        # Container dos widgets (3 colunas)
        widgets_container = tk.Frame(main_container, bg='#ecf0f1')
        widgets_container.pack(fill='both', expand=True)

        # Configurar grid
        widgets_container.grid_columnconfigure(0, weight=1)
        widgets_container.grid_columnconfigure(1, weight=1)
        widgets_container.grid_columnconfigure(2, weight=1)
        widgets_container.grid_rowconfigure(0, weight=1)

        # Widget 1: Ordem de Serviço
        self.create_os_widget(widgets_container, 0, 0)

        # Widget 2: Agendamento
        self.create_agendamento_widget(widgets_container, 0, 1)

        # Widget 3: Financeiro
        self.create_financeiro_widget(widgets_container, 0, 2)

        # Navegação Rápida (rodapé)
        self.create_quick_nav(main_container)

    def create_os_widget(self, parent, row, col):
        """Widget de Ordem de Serviço"""
        frame = tk.LabelFrame(
            parent,
            text="📋 Ordens de Serviço",
            bg='white',
            font=('Arial', 12, 'bold'),
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

        # Cards de resumo
        cards_frame = tk.Frame(frame, bg='white')
        cards_frame.pack(fill='x', pady=(0, 15))

        self.os_pendentes_card = self.create_card(
            cards_frame, "Pendentes", "0", "#e74c3c"
        )
        self.os_pendentes_card.pack(side='left', fill='x', expand=True, padx=(0, 10))

        self.os_andamento_card = self.create_card(
            cards_frame, "Em Andamento", "0", "#f39c12"
        )
        self.os_andamento_card.pack(side='left', fill='x', expand=True)

        # Lista de próximas visitas
        list_label = tk.Label(
            frame,
            text="Próximas Visitas:",
            bg='white',
            font=('Arial', 10, 'bold'),
            fg='#7f8c8d'
        )
        list_label.pack(anchor='w', pady=(0, 5))

        self.os_listbox = tk.Listbox(
            frame,
            font=('Arial', 9),
            height=6,
            bg='#f8f9fa',
            relief='flat'
        )
        self.os_listbox.pack(fill='both', expand=True, pady=(0, 10))

        # Botão
        os_btn = tk.Button(
            frame,
            text="Abrir Módulo de OS",
            command=self.abrir_modulo_os,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            pady=8
        )
        os_btn.pack(fill='x')

    def create_agendamento_widget(self, parent, row, col):
        """Widget de Agendamento"""
        frame = tk.LabelFrame(
            parent,
            text="📅 Agendamento",
            bg='white',
            font=('Arial', 12, 'bold'),
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

        # Cards de resumo
        cards_frame = tk.Frame(frame, bg='white')
        cards_frame.pack(fill='x', pady=(0, 15))

        self.agend_hoje_card = self.create_card(
            cards_frame, "Hoje", "0", "#27ae60"
        )
        self.agend_hoje_card.pack(side='left', fill='x', expand=True, padx=(0, 10))

        self.agend_semana_card = self.create_card(
            cards_frame, "Esta Semana", "0", "#16a085"
        )
        self.agend_semana_card.pack(side='left', fill='x', expand=True)

        # Lista de eventos
        list_label = tk.Label(
            frame,
            text="Próximos Eventos:",
            bg='white',
            font=('Arial', 10, 'bold'),
            fg='#7f8c8d'
        )
        list_label.pack(anchor='w', pady=(0, 5))

        self.agend_listbox = tk.Listbox(
            frame,
            font=('Arial', 9),
            height=6,
            bg='#f8f9fa',
            relief='flat'
        )
        self.agend_listbox.pack(fill='both', expand=True, pady=(0, 10))

        # Botão
        agend_btn = tk.Button(
            frame,
            text="Abrir Agendamento",
            command=self.abrir_modulo_agendamento,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            pady=8
        )
        agend_btn.pack(fill='x')

    def create_financeiro_widget(self, parent, row, col):
        """Widget de Financeiro"""
        frame = tk.LabelFrame(
            parent,
            text="💰 Financeiro",
            bg='white',
            font=('Arial', 12, 'bold'),
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

        # Cards de resumo
        cards_frame = tk.Frame(frame, bg='white')
        cards_frame.pack(fill='x', pady=(0, 15))

        self.fin_receber_card = self.create_card(
            cards_frame, "A Receber", "R$ 0,00", "#27ae60"
        )
        self.fin_receber_card.pack(side='left', fill='x', expand=True, padx=(0, 10))

        self.fin_pagar_card = self.create_card(
            cards_frame, "A Pagar", "R$ 0,00", "#e74c3c"
        )
        self.fin_pagar_card.pack(side='left', fill='x', expand=True)

        # Saldo
        saldo_frame = tk.Frame(frame, bg='#3498db', relief='solid', borderwidth=1)
        saldo_frame.pack(fill='x', pady=(0, 15))

        saldo_label = tk.Label(
            saldo_frame,
            text="Saldo Atual",
            bg='#3498db',
            fg='white',
            font=('Arial', 10)
        )
        saldo_label.pack(pady=(5, 0))

        self.saldo_value_label = tk.Label(
            saldo_frame,
            text="R$ 0,00",
            bg='#3498db',
            fg='white',
            font=('Arial', 16, 'bold')
        )
        self.saldo_value_label.pack(pady=(0, 5))

        # Lista de alertas
        list_label = tk.Label(
            frame,
            text="Alertas de Vencimento:",
            bg='white',
            font=('Arial', 10, 'bold'),
            fg='#7f8c8d'
        )
        list_label.pack(anchor='w', pady=(0, 5))

        self.fin_listbox = tk.Listbox(
            frame,
            font=('Arial', 9),
            height=4,
            bg='#f8f9fa',
            relief='flat'
        )
        self.fin_listbox.pack(fill='both', expand=True, pady=(0, 10))

        # Botão
        fin_btn = tk.Button(
            frame,
            text="Abrir Financeiro",
            command=self.abrir_modulo_financeiro,
            bg='#f39c12',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            pady=8
        )
        fin_btn.pack(fill='x')

    def create_card(self, parent, title, value, color):
        """Criar card de estatística"""
        card = tk.Frame(parent, bg=color, relief='flat')

        title_label = tk.Label(
            card,
            text=title,
            bg=color,
            fg='white',
            font=('Arial', 9)
        )
        title_label.pack(pady=(8, 0))

        value_label = tk.Label(
            card,
            text=value,
            bg=color,
            fg='white',
            font=('Arial', 16, 'bold')
        )
        value_label.pack(pady=(0, 8))

        # Armazenar label para atualização
        card.value_label = value_label

        return card

    def create_quick_nav(self, parent):
        """Criar barra de navegação rápida"""
        nav_frame = tk.Frame(parent, bg='white', relief='solid', borderwidth=1)
        nav_frame.pack(fill='x', pady=(20, 0))

        nav_label = tk.Label(
            nav_frame,
            text="Navegação Rápida:",
            bg='white',
            font=('Arial', 11, 'bold'),
            fg='#2c3e50'
        )
        nav_label.pack(side='left', padx=15, pady=10)

        buttons = [
            ("👥 Clientes", self.abrir_clientes),
            ("🏭 Fornecedores", self.abrir_fornecedores),
            ("👷 Colaboradores", self.abrir_colaboradores),
            ("📦 Produtos", self.abrir_produtos),
            ("📊 Estoque", self.abrir_estoque),
            ("📄 Relatórios", self.abrir_relatorios),
        ]

        for text, command in buttons:
            btn = tk.Button(
                nav_frame,
                text=text,
                command=command,
                bg='#ecf0f1',
                fg='#2c3e50',
                font=('Arial', 9, 'bold'),
                relief='flat',
                padx=15,
                pady=5,
                cursor='hand2'
            )
            btn.pack(side='left', padx=5, pady=10)

    def load_data(self):
        """Carregar dados de todos os widgets"""
        self.load_os_data()
        self.load_agendamento_data()
        self.load_financeiro_data()

    def load_os_data(self):
        """Carregar dados de OS em thread separada"""
        def fetch():
            try:
                headers = create_auth_header()
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/os/estatisticas/dashboard",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    self.update_os_ui(data)
                else:
                    print(f"Erro ao carregar OS: {response.status_code}")

            except Exception as e:
                print(f"Erro ao carregar OS: {e}")

        threading.Thread(target=fetch, daemon=True).start()

    def load_agendamento_data(self):
        """Carregar dados de agendamento"""
        def fetch():
            try:
                headers = create_auth_header()
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/agendamento/dashboard",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    self.update_agendamento_ui(data)
                else:
                    print(f"Erro ao carregar Agendamento: {response.status_code}")

            except Exception as e:
                print(f"Erro ao carregar Agendamento: {e}")

        threading.Thread(target=fetch, daemon=True).start()

    def load_financeiro_data(self):
        """Carregar dados financeiros"""
        def fetch():
            try:
                headers = create_auth_header()
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/financeiro/dashboard",
                    headers=headers,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    self.update_financeiro_ui(data)
                else:
                    print(f"Erro ao carregar Financeiro: {response.status_code}")

            except Exception as e:
                print(f"Erro ao carregar Financeiro: {e}")

        threading.Thread(target=fetch, daemon=True).start()

    def update_os_ui(self, data):
        """Atualizar interface de OS"""
        def update():
            try:
                stats = data.get('estatisticas', {})
                self.os_pendentes_card.value_label.config(
                    text=str(stats.get('total_abertas', 0))
                )
                self.os_andamento_card.value_label.config(
                    text=str(stats.get('em_andamento', 0))
                )

                # Atualizar lista
                self.os_listbox.delete(0, tk.END)
                proximas = data.get('os_proximas_visitas', [])[:5]
                for os in proximas:
                    self.os_listbox.insert(tk.END, f"OS #{os.get('id')} - {os.get('cliente_nome', 'N/A')}")

            except Exception as e:
                print(f"Erro ao atualizar UI de OS: {e}")

        self.root.after(0, update)

    def update_agendamento_ui(self, data):
        """Atualizar interface de agendamento"""
        def update():
            try:
                # Para agendamento, precisamos processar a lista
                eventos = data if isinstance(data, list) else []

                self.agend_hoje_card.value_label.config(text=str(len(eventos)))
                self.agend_semana_card.value_label.config(text=str(len(eventos)))

                # Atualizar lista
                self.agend_listbox.delete(0, tk.END)
                for evento in eventos[:5]:
                    titulo = evento.get('titulo', 'Sem título')
                    self.agend_listbox.insert(tk.END, f"📅 {titulo}")

            except Exception as e:
                print(f"Erro ao atualizar UI de Agendamento: {e}")

        self.root.after(0, update)

    def update_financeiro_ui(self, data):
        """Atualizar interface financeira"""
        def update():
            try:
                resumo = data.get('resumo', {})

                receber = resumo.get('total_receber', 0)
                pagar = resumo.get('total_pagar', 0)
                saldo = receber - pagar

                self.fin_receber_card.value_label.config(
                    text=f"R$ {receber:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
                )
                self.fin_pagar_card.value_label.config(
                    text=f"R$ {pagar:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
                )
                self.saldo_value_label.config(
                    text=f"R$ {saldo:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
                )

                # Atualizar alertas
                self.fin_listbox.delete(0, tk.END)
                alertas = data.get('alertas_vencimento', [])[:4]
                for alerta in alertas:
                    self.fin_listbox.insert(tk.END, f"⚠️ {alerta.get('descricao', 'N/A')}")

            except Exception as e:
                print(f"Erro ao atualizar UI Financeiro: {e}")

        self.root.after(0, update)

    # Métodos de navegação
    def abrir_modulo_os(self):
        """Abrir módulo de OS"""
        try:
            from frontend.desktop.os_dashboard import OSDashboard
            token = get_token_for_api()
            OSDashboard(self.root, token)
        except ImportError as e:
            messagebox.showwarning("Módulo não disponível", f"OS Dashboard: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir OS: {e}")

    def abrir_modulo_agendamento(self):
        """Abrir módulo de agendamento"""
        try:
            from frontend.desktop.agendamento_window import AgendamentoWindow
            token = get_token_for_api()
            AgendamentoWindow(self.root, token)
        except ImportError as e:
            messagebox.showwarning("Módulo não disponível", f"Agendamento: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Agendamento: {e}")

    def abrir_modulo_financeiro(self):
        """Abrir módulo financeiro"""
        try:
            from frontend.desktop.financeiro_window import FinanceiroWindow
            FinanceiroWindow(parent=None)
        except ImportError as e:
            messagebox.showwarning("Módulo não disponível", f"Financeiro: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Financeiro: {e}")

    def abrir_clientes(self):
        """Abrir módulo de clientes (wizard moderno)"""
        try:
            from frontend.desktop.clientes_wizard import ClientesWizard
            ClientesWizard(self.root)  # Passa root como parent
        except ImportError as e:
            messagebox.showwarning(
                "Módulo não disponível",
                f"Wizard de Clientes não encontrado: {e}"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Clientes: {e}")

    def abrir_fornecedores(self):
        """Abrir módulo de fornecedores (wizard moderno)"""
        try:
            from frontend.desktop.fornecedores_wizard import (
                FornecedoresWizard
            )
            FornecedoresWizard(self.root)  # Usa SessionManager automático
        except ImportError as e:
            messagebox.showwarning(
                "Módulo não disponível",
                f"Wizard de Fornecedores não encontrado: {e}"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Fornecedores: {e}")

    def abrir_colaboradores(self):
        """Abrir módulo de colaboradores (wizard FASE 103)"""
        try:
            from frontend.desktop.colaboradores_wizard_fase103 import (
                ColaboradoresWizard
            )
            ColaboradoresWizard(self.root)  # Wizard completo integrado
        except ImportError as e:
            messagebox.showwarning(
                "Módulo não disponível",
                f"Wizard de Colaboradores não encontrado: {e}"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Colaboradores: {e}")

    def abrir_produtos(self):
        """Abrir módulo de produtos"""
        try:
            from frontend.desktop.produtos_window_completo import (
                ProdutosWindowCompleto
            )
            ProdutosWindowCompleto(self.root)  # Usa SessionManager automático
        except ImportError as e:
            messagebox.showwarning("Módulo não disponível", f"Produtos: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Produtos: {e}")

    def abrir_estoque(self):
        """Abrir módulo de estoque"""
        try:
            from frontend.desktop.estoque_window import EstoqueWindow
            EstoqueWindow()  # Usa SessionManager, não precisa de user_data
        except ImportError as e:
            messagebox.showwarning("Módulo não disponível", f"Estoque: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Estoque: {e}")

    def abrir_relatorios(self):
        """Abrir módulo de relatórios"""
        try:
            from frontend.desktop.relatorios_window import RelatoriosWindow
            user_data = get_current_user_info()
            RelatoriosWindow(user_data)
        except ImportError as e:
            messagebox.showwarning("Módulo não disponível", f"Relatórios: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Relatórios: {e}")

    def handle_logout(self):
        """Processar logout"""
        if logout_user(show_confirmation=True):
            # Fechar dashboard
            self.root.destroy()

    def on_closing(self):
        """Evento de fechamento da janela"""
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            self.root.destroy()

    def run(self):
        """Executar dashboard"""
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = DashboardPrincipal()
        app.run()
    except PermissionError:
        print("\n❌ Autenticação cancelada ou falhou")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
