"""
SISTEMA ERP PRIMOTEX - SISTEMA DE NAVEGAÇÃO APRIMORADO
=====================================================

Sistema de navegação com breadcrumbs, histórico e UX otimizada
para melhorar a experiência do usuário no sistema.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

# =======================================
# CLASSE DE NAVEGAÇÃO
# =======================================

class NavigationSystem:
    """Sistema de navegação com breadcrumbs e histórico"""

    def __init__(self, parent_widget: tk.Widget):
        self.parent = parent_widget
        self.navigation_history: List[Dict[str, Any]] = []
        self.current_index = -1
        self.breadcrumb_callbacks: Dict[str, Callable] = {}

        self.setup_navigation_ui()

    def setup_navigation_ui(self):
        """Configurar interface de navegação"""

        # === BARRA DE NAVEGAÇÃO ===
        self.nav_frame = tk.Frame(self.parent, bg='#ecf0f1', height=40)
        self.nav_frame.pack(fill='x', pady=(0, 2))
        self.nav_frame.pack_propagate(False)

        # Container interno
        nav_container = tk.Frame(self.nav_frame, bg='#ecf0f1')
        nav_container.pack(fill='both', expand=True, padx=10, pady=5)

        # === BOTÕES DE NAVEGAÇÃO ===
        nav_buttons_frame = tk.Frame(nav_container, bg='#ecf0f1')
        nav_buttons_frame.pack(side='left')

        # Botão Voltar
        self.btn_back = tk.Button(
            nav_buttons_frame,
            text="◀ Voltar",
            font=('Arial', 9),
            bg='#bdc3c7',
            fg='#2c3e50',
            padx=8,
            pady=2,
            border=0,
            state='disabled',
            command=self.go_back
        )
        self.btn_back.pack(side='left', padx=(0, 5))

        # Botão Avançar
        self.btn_forward = tk.Button(
            nav_buttons_frame,
            text="Avançar ▶",
            font=('Arial', 9),
            bg='#bdc3c7',
            fg='#2c3e50',
            padx=8,
            pady=2,
            border=0,
            state='disabled',
            command=self.go_forward
        )
        self.btn_forward.pack(side='left', padx=(0, 10))

        # === BREADCRUMBS ===
        self.breadcrumb_frame = tk.Frame(nav_container, bg='#ecf0f1')
        self.breadcrumb_frame.pack(side='left', fill='x', expand=True)

        # === AÇÕES RÁPIDAS ===
        actions_frame = tk.Frame(nav_container, bg='#ecf0f1')
        actions_frame.pack(side='right')

        # Botão Home
        btn_home = tk.Button(
            actions_frame,
            text="🏠 Início",
            font=('Arial', 9),
            bg='#3498db',
            fg='white',
            padx=8,
            pady=2,
            border=0,
            command=lambda: self.navigate_to('dashboard', 'Dashboard', {})
        )
        btn_home.pack(side='left', padx=(0, 5))

        # Menu de Favoritos
        self.create_favorites_menu(actions_frame)

    def create_favorites_menu(self, parent):
        """Criar menu de favoritos"""

        # Botão de favoritos
        btn_favorites = tk.Menubutton(
            parent,
            text="⭐ Favoritos",
            font=('Arial', 9),
            bg='#e67e22',
            fg='white',
            padx=8,
            pady=2,
            border=0,
            relief='raised'
        )
        btn_favorites.pack(side='left')

        # Menu
        favorites_menu = tk.Menu(btn_favorites, tearoff=0)
        btn_favorites['menu'] = favorites_menu

        # Itens do menu
        favorites_menu.add_command(
            label="👥 Clientes", 
            command=lambda: self.navigate_to('clientes', 'Clientes', {})
        )
        favorites_menu.add_command(
            label="📦 Produtos", 
            command=lambda: self.navigate_to('produtos', 'Produtos', {})
        )
        favorites_menu.add_command(
            label="📊 Estoque", 
            command=lambda: self.navigate_to('estoque', 'Estoque', {})
        )
        favorites_menu.add_separator()
        favorites_menu.add_command(
            label="📈 Relatórios", 
            command=lambda: self.navigate_to('relatorios', 'Relatórios', {})
        )
        favorites_menu.add_command(
            label="📋 Códigos de Barras", 
            command=lambda: self.navigate_to('codigo_barras', 'Códigos de Barras', {})
        )

    def navigate_to(self, module_id: str, module_name: str, params: Dict[str, Any], callback: Optional[Callable] = None):
        """Navegar para um módulo"""

        # Criar entrada no histórico
        nav_entry = {
            'module_id': module_id,
            'module_name': module_name,
            'params': params,
            'timestamp': datetime.now(),
            'callback': callback
        }

        # Remover entradas futuras se estamos no meio do histórico
        if self.current_index < len(self.navigation_history) - 1:
            self.navigation_history = self.navigation_history[:self.current_index + 1]

        # Adicionar nova entrada
        self.navigation_history.append(nav_entry)
        self.current_index = len(self.navigation_history) - 1

        # Limitar histórico (últimas 50 entradas)
        if len(self.navigation_history) > 50:
            self.navigation_history = self.navigation_history[-50:]
            self.current_index = len(self.navigation_history) - 1

        # Atualizar interface
        self.update_navigation_ui()
        self.update_breadcrumbs()

        # Executar callback se fornecido
        if callback:
            callback()

    def go_back(self):
        """Voltar na navegação"""

        if self.current_index > 0:
            self.current_index -= 1
            current_entry = self.navigation_history[self.current_index]

            # Executar callback
            if current_entry.get('callback'):
                current_entry['callback']()

            self.update_navigation_ui()
            self.update_breadcrumbs()

    def go_forward(self):
        """Avançar na navegação"""

        if self.current_index < len(self.navigation_history) - 1:
            self.current_index += 1
            current_entry = self.navigation_history[self.current_index]

            # Executar callback
            if current_entry.get('callback'):
                current_entry['callback']()

            self.update_navigation_ui()
            self.update_breadcrumbs()

    def update_navigation_ui(self):
        """Atualizar estado dos botões de navegação"""

        # Botão Voltar
        if self.current_index > 0:
            self.btn_back.config(state='normal', bg='#3498db', fg='white')
        else:
            self.btn_back.config(state='disabled', bg='#bdc3c7', fg='#2c3e50')

        # Botão Avançar
        if self.current_index < len(self.navigation_history) - 1:
            self.btn_forward.config(state='normal', bg='#3498db', fg='white')
        else:
            self.btn_forward.config(state='disabled', bg='#bdc3c7', fg='#2c3e50')

    def update_breadcrumbs(self):
        """Atualizar breadcrumbs"""

        # Limpar breadcrumbs existentes
        for widget in self.breadcrumb_frame.winfo_children():
            widget.destroy()

        if not self.navigation_history:
            return

        # Mostrar últimas 4 entradas como breadcrumbs
        start_index = max(0, self.current_index - 3)
        breadcrumb_entries = self.navigation_history[start_index:self.current_index + 1]

        for i, entry in enumerate(breadcrumb_entries):
            # Separador
            if i > 0:
                separator = tk.Label(
                    self.breadcrumb_frame,
                    text="▶",
                    font=('Arial', 8),
                    bg='#ecf0f1',
                    fg='#7f8c8d'
                )
                separator.pack(side='left', padx=3)

            # Item do breadcrumb
            is_current = (start_index + i) == self.current_index

            if is_current:
                # Item atual (não clicável)
                breadcrumb_label = tk.Label(
                    self.breadcrumb_frame,
                    text=entry['module_name'],
                    font=('Arial', 9, 'bold'),
                    bg='#ecf0f1',
                    fg='#2c3e50'
                )
                breadcrumb_label.pack(side='left')
            else:
                # Item clicável
                breadcrumb_btn = tk.Button(
                    self.breadcrumb_frame,
                    text=entry['module_name'],
                    font=('Arial', 9),
                    bg='#ecf0f1',
                    fg='#3498db',
                    border=0,
                    cursor='hand2',
                    command=lambda idx=start_index + i: self.jump_to_history(idx)
                )
                breadcrumb_btn.pack(side='left')

                # Efeito hover
                def on_enter(e, btn=breadcrumb_btn):
                    btn.config(fg='#2980b9', font=('Arial', 9, 'underline'))

                def on_leave(e, btn=breadcrumb_btn):
                    btn.config(fg='#3498db', font=('Arial', 9))

                breadcrumb_btn.bind("<Enter>", on_enter)
                breadcrumb_btn.bind("<Leave>", on_leave)

    def jump_to_history(self, index: int):
        """Pular para uma entrada específica do histórico"""

        if 0 <= index < len(self.navigation_history):
            self.current_index = index
            entry = self.navigation_history[index]

            # Executar callback
            if entry.get('callback'):
                entry['callback']()

            self.update_navigation_ui()
            self.update_breadcrumbs()

    def register_callback(self, module_id: str, callback: Callable):
        """Registrar callback para um módulo"""
        self.breadcrumb_callbacks[module_id] = callback

    def get_current_module(self) -> Optional[Dict[str, Any]]:
        """Obter módulo atual"""
        if 0 <= self.current_index < len(self.navigation_history):
            return self.navigation_history[self.current_index]
        return None

    def clear_history(self):
        """Limpar histórico de navegação"""
        self.navigation_history.clear()
        self.current_index = -1
        self.update_navigation_ui()
        self.update_breadcrumbs()

# =======================================
# CLASSE DE BUSCA RÁPIDA
# =======================================

class QuickSearchWidget:
    """Widget de busca rápida global"""

    def __init__(self, parent_widget: tk.Widget, modules_data: Dict[str, Any]):
        self.parent = parent_widget
        self.modules_data = modules_data
        self.search_results = []

        self.setup_search_ui()

    def setup_search_ui(self):
        """Configurar interface de busca"""

        # === FRAME DE BUSCA ===
        self.search_frame = tk.Frame(self.parent, bg='white', relief='raised', bd=1)
        self.search_frame.pack(fill='x', padx=10, pady=5)

        # Container interno
        search_container = tk.Frame(self.search_frame, bg='white')
        search_container.pack(fill='x', padx=10, pady=8)

        # Ícone de busca
        search_icon = tk.Label(
            search_container,
            text="🔍",
            font=('Arial', 12),
            bg='white'
        )
        search_icon.pack(side='left', padx=(0, 8))

        # Campo de busca
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_container,
            textvariable=self.search_var,
            font=('Arial', 11),
            bg='#f8f9fa',
            border=0,
            relief='flat'
        )
        self.search_entry.pack(side='left', fill='x', expand=True)

        # Placeholder
        self.search_entry.insert(0, "Buscar clientes, produtos, relatórios...")
        self.search_entry.config(fg='#7f8c8d')

        # Botão de busca
        btn_search = tk.Button(
            search_container,
            text="Buscar",
            font=('Arial', 9),
            bg='#3498db',
            fg='white',
            padx=12,
            pady=4,
            border=0,
            command=self.perform_search
        )
        btn_search.pack(side='right', padx=(8, 0))

        # Eventos
        self.search_entry.bind('<FocusIn>', self.on_focus_in)
        self.search_entry.bind('<FocusOut>', self.on_focus_out)
        self.search_entry.bind('<KeyRelease>', self.on_key_release)
        self.search_entry.bind('<Return>', lambda e: self.perform_search())

        # === RESULTADOS ===
        self.results_frame = tk.Frame(self.search_frame, bg='white')
        # Inicialmente oculto

    def on_focus_in(self, event):
        """Ao focar no campo de busca"""
        if self.search_entry.get() == "Buscar clientes, produtos, relatórios...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg='#2c3e50')

    def on_focus_out(self, event):
        """Ao sair do foco do campo de busca"""
        if not self.search_entry.get():
            self.search_entry.insert(0, "Buscar clientes, produtos, relatórios...")
            self.search_entry.config(fg='#7f8c8d')
            self.hide_results()

    def on_key_release(self, event):
        """Ao digitar no campo de busca"""
        query = self.search_entry.get().strip()

        if query and query != "Buscar clientes, produtos, relatórios...":
            if len(query) >= 2:  # Buscar após 2 caracteres
                self.search_suggestions(query)
        else:
            self.hide_results()

    def search_suggestions(self, query: str):
        """Buscar sugestões em tempo real"""

        suggestions = []
        query_lower = query.lower()

        # Buscar em módulos
        modules = [
            ("Clientes", "👥", "clientes"),
            ("Produtos", "📦", "produtos"),
            ("Estoque", "📊", "estoque"),
            ("Relatórios", "📈", "relatorios"),
            ("Códigos de Barras", "📋", "codigo_barras"),
            ("Dashboard", "🏠", "dashboard")
        ]

        for name, icon, module_id in modules:
            if query_lower in name.lower():
                suggestions.append({
                    'type': 'module',
                    'title': name,
                    'icon': icon,
                    'subtitle': f"Ir para {name}",
                    'action': lambda m=module_id, n=name: self.navigate_to_module(m, n)
                })

        # Buscar ações específicas
        actions = [
            ("Novo Cliente", "➕", "Cadastrar novo cliente"),
            ("Novo Produto", "➕", "Cadastrar novo produto"),
            ("Movimentação de Estoque", "🔄", "Registrar movimentação"),
            ("Gerar Relatório", "📄", "Criar novo relatório"),
            ("Código de Barras", "📋", "Gerar código de barras")
        ]

        for name, icon, desc in actions:
            if query_lower in name.lower():
                suggestions.append({
                    'type': 'action',
                    'title': name,
                    'icon': icon,
                    'subtitle': desc,
                    'action': lambda: self.show_action_message(name)
                })

        self.show_suggestions(suggestions[:5])  # Mostrar até 5 sugestões

    def show_suggestions(self, suggestions: List[Dict[str, Any]]):
        """Mostrar sugestões"""

        # Limpar resultados anteriores
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not suggestions:
            self.hide_results()
            return

        # Mostrar frame de resultados
        self.results_frame.pack(fill='x', padx=10, pady=(0, 10))

        for suggestion in suggestions:
            self.create_suggestion_item(suggestion)

    def create_suggestion_item(self, suggestion: Dict[str, Any]):
        """Criar item de sugestão"""

        item_frame = tk.Frame(self.results_frame, bg='#f8f9fa', cursor='hand2')
        item_frame.pack(fill='x', pady=1)

        # Container interno com padding
        container = tk.Frame(item_frame, bg='#f8f9fa')
        container.pack(fill='x', padx=8, pady=4)

        # Ícone
        icon_label = tk.Label(
            container,
            text=suggestion['icon'],
            font=('Arial', 12),
            bg='#f8f9fa'
        )
        icon_label.pack(side='left', padx=(0, 8))

        # Textos
        text_frame = tk.Frame(container, bg='#f8f9fa')
        text_frame.pack(side='left', fill='x', expand=True)

        title_label = tk.Label(
            text_frame,
            text=suggestion['title'],
            font=('Arial', 10, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50',
            anchor='w'
        )
        title_label.pack(fill='x')

        subtitle_label = tk.Label(
            text_frame,
            text=suggestion['subtitle'],
            font=('Arial', 8),
            bg='#f8f9fa',
            fg='#7f8c8d',
            anchor='w'
        )
        subtitle_label.pack(fill='x')

        # Eventos de clique
        def on_click(event=None):
            suggestion['action']()
            self.search_entry.delete(0, tk.END)
            self.hide_results()

        # Efeitos hover e clique
        def on_enter(e):
            item_frame.config(bg='#e8f4fd')
            container.config(bg='#e8f4fd')
            text_frame.config(bg='#e8f4fd')
            icon_label.config(bg='#e8f4fd')
            title_label.config(bg='#e8f4fd')
            subtitle_label.config(bg='#e8f4fd')

        def on_leave(e):
            item_frame.config(bg='#f8f9fa')
            container.config(bg='#f8f9fa')
            text_frame.config(bg='#f8f9fa')
            icon_label.config(bg='#f8f9fa')
            title_label.config(bg='#f8f9fa')
            subtitle_label.config(bg='#f8f9fa')

        # Bind eventos em todos os widgets
        for widget in [item_frame, container, text_frame, icon_label, title_label, subtitle_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    def hide_results(self):
        """Ocultar resultados"""
        self.results_frame.pack_forget()

    def perform_search(self):
        """Executar busca completa"""
        query = self.search_entry.get().strip()

        if query and query != "Buscar clientes, produtos, relatórios...":
            # Aqui seria implementada a busca completa
            self.show_action_message(f"Busca por '{query}'")

    def navigate_to_module(self, module_id: str, module_name: str):
        """Navegar para um módulo"""
        # Este método seria conectado ao sistema de navegação principal
        print(f"Navegando para: {module_name} ({module_id})")

    def show_action_message(self, action: str):
        """Mostrar mensagem de ação"""
        print(f"Executando ação: {action}")

# =======================================
# CLASSE DE ATALHOS DE TECLADO
# =======================================

class KeyboardShortcuts:
    """Sistema de atalhos de teclado"""

    def __init__(self, root_widget: tk.Widget):
        self.root = root_widget
        self.shortcuts = {}

        self.setup_default_shortcuts()
        self.bind_shortcuts()

    def setup_default_shortcuts(self):
        """Configurar atalhos padrão"""

        self.shortcuts = {
            '<Control-h>': ('dashboard', 'Ir para Dashboard'),
            '<Control-c>': ('clientes', 'Abrir Clientes'),
            '<Control-p>': ('produtos', 'Abrir Produtos'),
            '<Control-e>': ('estoque', 'Abrir Estoque'),
            '<Control-r>': ('relatorios', 'Abrir Relatórios'),
            '<Control-b>': ('codigo_barras', 'Abrir Códigos de Barras'),
            '<Control-f>': ('search', 'Focar na Busca'),
            '<F1>': ('help', 'Ajuda'),
            '<F5>': ('refresh', 'Atualizar'),
            '<Alt-Left>': ('back', 'Voltar'),
            '<Alt-Right>': ('forward', 'Avançar')
        }

    def bind_shortcuts(self):
        """Vincular atalhos"""

        for shortcut, (action, description) in self.shortcuts.items():
            self.root.bind_all(shortcut, lambda e, a=action: self.execute_shortcut(a))

    def execute_shortcut(self, action: str):
        """Executar atalho"""

        # Este método seria conectado às ações principais
        print(f"Atalho executado: {action}")

    def add_shortcut(self, key_combo: str, action: str, description: str):
        """Adicionar novo atalho"""

        self.shortcuts[key_combo] = (action, description)
        self.root.bind_all(key_combo, lambda e: self.execute_shortcut(action))

    def get_shortcuts_help(self) -> str:
        """Obter texto de ajuda dos atalhos"""

        help_text = "ATALHOS DE TECLADO:\n" + "="*30 + "\n\n"

        for shortcut, (action, description) in self.shortcuts.items():
            # Formatar atalho para exibição
            display_shortcut = shortcut.replace('<', '').replace('>', '').replace('Control', 'Ctrl')
            help_text += f"{display_shortcut:<15} - {description}\n"

        return help_text

# =======================================
# FUNÇÃO PRINCIPAL DE TESTE
# =======================================

def main():
    """Teste do sistema de navegação"""

    root = tk.Tk()
    root.title("Teste - Sistema de Navegação")
    root.geometry("800x600")

    # Criar sistema de navegação
    nav_system = NavigationSystem(root)

    # Criar busca rápida
    QuickSearchWidget(root, {})

    # Criar atalhos
    KeyboardShortcuts(root)

    # Área de conteúdo de teste
    content_frame = tk.Frame(root, bg='white')
    content_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Botões de teste
    test_frame = tk.Frame(content_frame, bg='white')
    test_frame.pack(pady=20)

    tk.Button(
        test_frame,
        text="Ir para Clientes",
        command=lambda: nav_system.navigate_to('clientes', 'Clientes', {})
    ).pack(side='left', padx=5)

    tk.Button(
        test_frame,
        text="Ir para Produtos",
        command=lambda: nav_system.navigate_to('produtos', 'Produtos', {})
    ).pack(side='left', padx=5)

    tk.Button(
        test_frame,
        text="Ir para Estoque",
        command=lambda: nav_system.navigate_to('estoque', 'Estoque', {})
    ).pack(side='left', padx=5)

    # Informações
    info_label = tk.Label(
        content_frame,
        text="Sistema de Navegação Implementado!\n\n" +
             "Funcionalidades:\n" +
             "• Breadcrumbs inteligentes\n" +
             "• Histórico de navegação\n" +
             "• Busca rápida global\n" +
             "• Atalhos de teclado\n" +
             "• Favoritos\n" +
             "• Botões Voltar/Avançar",
        font=('Arial', 12),
        justify='center',
        bg='white'
    )
    info_label.pack(expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()