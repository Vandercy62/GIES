"""
SISTEMA ERP PRIMOTEX - WIZARD DE CLIENTES
==========================================

Janela principal do wizard de cadastro de clientes.
Interface moderna em 4 abas com navegação facilitada.

ESTRUTURA:
- Aba 1: Lista de clientes (busca e filtros)
- Aba 2: Dados básicos (nome, CPF/CNPJ, tipo)
- Aba 3: Complementares (endereço, contatos, dados comerciais)
- Aba 4: Observações (notas, histórico, anexos)

NAVEGAÇÃO:
- Botões: Anterior | Próximo | Cancelar | Salvar
- Atalhos: F3=Próximo | F4=Anterior | F2=Salvar | ESC=Cancelar
- Cores: Verde=Next, Azul=Prev, Vermelho=Cancel, Verde Escuro=Save

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 100
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
import json

from frontend.desktop.auth_middleware import (
    require_login,
    get_token_for_api,
    create_auth_header,
    get_current_user_info
)
from frontend.desktop.clientes_components.aba_lista import AbaLista
from frontend.desktop.clientes_components.aba_dados_basicos import (
    AbaDadosBasicos
)
from frontend.desktop.clientes_components.aba_complementares import (
    AbaComplementares
)
from frontend.desktop.clientes_components.aba_observacoes import (
    AbaObservacoes
)


@require_login()
class ClientesWizard:
    """
    Wizard completo de cadastro de clientes com 4 abas.
    Interface otimizada para idosos com fontes grandes e botões claros.
    """

    # Cores do sistema (design FASE 100)
    COR_PROXIMO = "#28a745"      # Verde
    COR_ANTERIOR = "#007bf"     # Azul
    COR_CANCELAR = "#dc3545"     # Vermelho
    COR_SALVAR = "#155724"       # Verde escuro
    COR_FUNDO = "#f8f9fa"        # Cinza claro
    COR_DESTAQUE = "#e9ece"     # Cinza médio

    # Fontes do sistema
    FONTE_TITULO = ("Segoe UI", 18, "bold")
    FONTE_LABEL = ("Segoe UI", 14, "bold")
    FONTE_CAMPO = ("Segoe UI", 16)
    FONTE_BOTAO = ("Segoe UI", 14, "bold")

    def __init__(self, parent: tk.Tk):
        """
        Inicializa wizard de clientes.

        Args:
            parent: Janela pai (dashboard)
        """
        self.parent = parent
        self.token = get_token_for_api()
        self.user_info = get_current_user_info()

        # Dados do cliente em edição
        self.cliente_id: Optional[int] = None
        self.dados_cliente: Dict[str, Any] = {}
        self.modo_edicao = False

        # Criar janela principal
        self.window = tk.Toplevel(parent)
        self.window.title("📋 Cadastro de Clientes - ERP Primotex")
        self.window.geometry("1400x900")
        self.window.configure(bg=self.COR_FUNDO)

        # Centralizar janela
        self._centralizar_janela()

        # Criar interface
        self._criar_header()
        self._criar_notebook()
        self._criar_rodape()

        # Configurar atalhos de teclado
        self._configurar_atalhos()

        # Configurar fechamento da janela
        self.window.protocol("WM_DELETE_WINDOW", self._confirmar_fechar)

    def _centralizar_janela(self):
        """Centraliza janela na tela"""
        self.window.update_idletasks()
        largura = 1400
        altura = 900
        x = (self.window.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.window.winfo_screenheight() // 2) - (altura // 2)
        self.window.geometry(f"{largura}x{altura}+{x}+{y}")

    def _criar_header(self):
        """Cria cabeçalho com título e breadcrumb"""
        header_frame = tk.Frame(self.window, bg=self.COR_DESTAQUE, height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Título principal
        titulo = tk.Label(
            header_frame,
            text="📋 CADASTRO DE CLIENTES",
            font=self.FONTE_TITULO,
            bg=self.COR_DESTAQUE,
            fg="#212529"
        )
        titulo.pack(pady=(15, 5))

        # Indicador de progresso
        self.label_progresso = tk.Label(
            header_frame,
            text="ABA 1 de 4 - LISTA DE CLIENTES",
            font=("Segoe UI", 12),
            bg=self.COR_DESTAQUE,
            fg="#6c757d"
        )
        self.label_progresso.pack(pady=(0, 10))

    def _criar_notebook(self):
        """Cria notebook com as 4 abas"""
        # Frame para notebook
        notebook_frame = tk.Frame(self.window, bg=self.COR_FUNDO)
        notebook_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Criar notebook
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Criar abas (por enquanto vazias - serão implementadas depois)
        self.aba_lista = self._criar_aba_lista()
        self.aba_dados_basicos = self._criar_aba_dados_basicos()
        self.aba_complementares = self._criar_aba_complementares()
        self.aba_observacoes = self._criar_aba_observacoes()

        # Adicionar abas ao notebook
        self.notebook.add(self.aba_lista, text="  1. LISTA  ")
        self.notebook.add(self.aba_dados_basicos, text="  2. DADOS BÁSICOS  ")
        self.notebook.add(
            self.aba_complementares,
            text="  3. COMPLEMENTARES  "
        )
        self.notebook.add(self.aba_observacoes, text="  4. OBSERVAÇÕES  ")

        # Configurar evento de mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self._ao_mudar_aba)

    def _criar_aba_lista(self) -> tk.Frame:
        """Cria aba 1 - Lista de clientes"""
        frame = tk.Frame(self.notebook, bg=self.COR_FUNDO)

        # Criar componente de lista
        self.lista = AbaLista(
            parent_frame=frame,
            on_novo_click=self._criar_novo_cliente,
            on_editar_click=self._carregar_cliente_para_edicao,
            token=self.token
        )

        return frame

    def _criar_aba_dados_basicos(self) -> tk.Frame:
        """Cria aba 2 - Dados básicos"""
        frame = tk.Frame(self.notebook, bg=self.COR_FUNDO)

        # Criar componente de dados básicos
        self.dados_basicos = AbaDadosBasicos(parent_frame=frame)

        return frame

    def _criar_aba_complementares(self) -> tk.Frame:
        """Cria aba 3 - Dados complementares"""
        frame = tk.Frame(self.notebook, bg=self.COR_FUNDO)

        # Criar componente de dados complementares
        self.complementares = AbaComplementares(parent_frame=frame)

        return frame

    def _criar_aba_observacoes(self) -> tk.Frame:
        """Cria aba 4 - Observações"""
        frame = tk.Frame(self.notebook, bg=self.COR_FUNDO)

        # Criar componente de observações
        self.observacoes = AbaObservacoes(parent_frame=frame)

        return frame

    def _criar_rodape(self):
        """Cria rodapé com botões de navegação"""
        rodape_frame = tk.Frame(self.window, bg=self.COR_DESTAQUE, height=100)
        rodape_frame.pack(fill=tk.X, padx=0, pady=0)
        rodape_frame.pack_propagate(False)

        # Frame para botões
        btn_frame = tk.Frame(rodape_frame, bg=self.COR_DESTAQUE)
        btn_frame.pack(pady=20)

        # Botão Anterior (F4)
        self.btn_anterior = tk.Button(
            btn_frame,
            text="◀ ANTERIOR (F4)",
            font=self.FONTE_BOTAO,
            bg=self.COR_ANTERIOR,
            fg="white",
            width=18,
            height=2,
            cursor="hand2",
            command=self._aba_anterior
        )
        self.btn_anterior.grid(row=0, column=0, padx=10)

        # Botão Próximo (F3)
        self.btn_proximo = tk.Button(
            btn_frame,
            text="PRÓXIMO ▶ (F3)",
            font=self.FONTE_BOTAO,
            bg=self.COR_PROXIMO,
            fg="white",
            width=18,
            height=2,
            cursor="hand2",
            command=self._proxima_aba
        )
        self.btn_proximo.grid(row=0, column=1, padx=10)

        # Botão Cancelar (ESC)
        self.btn_cancelar = tk.Button(
            btn_frame,
            text="✖ CANCELAR (ESC)",
            font=self.FONTE_BOTAO,
            bg=self.COR_CANCELAR,
            fg="white",
            width=18,
            height=2,
            cursor="hand2",
            command=self._confirmar_fechar
        )
        self.btn_cancelar.grid(row=0, column=2, padx=10)

        # Botão Salvar (F2) - visível apenas nas abas de edição
        self.btn_salvar = tk.Button(
            btn_frame,
            text="💾 SALVAR (F2)",
            font=self.FONTE_BOTAO,
            bg=self.COR_SALVAR,
            fg="white",
            width=18,
            height=2,
            cursor="hand2",
            command=self._salvar_cliente
        )
        self.btn_salvar.grid(row=0, column=3, padx=10)

        # Atualizar estado dos botões
        self._atualizar_botoes()

    def _configurar_atalhos(self):
        """Configura atalhos de teclado"""
        self.window.bind("<F2>", lambda e: self._salvar_cliente())
        self.window.bind("<F3>", lambda e: self._proxima_aba())
        self.window.bind("<F4>", lambda e: self._aba_anterior())
        self.window.bind("<Escape>", lambda e: self._confirmar_fechar())

    def _ao_mudar_aba(self, event):
        """Executado quando muda de aba"""
        aba_atual = self.notebook.index(self.notebook.select())

        # Atualizar label de progresso
        titulos = [
            "ABA 1 de 4 - LISTA DE CLIENTES",
            "ABA 2 de 4 - DADOS BÁSICOS",
            "ABA 3 de 4 - DADOS COMPLEMENTARES",
            "ABA 4 de 4 - OBSERVAÇÕES E HISTÓRICO"
        ]
        self.label_progresso.config(text=titulos[aba_atual])

        # Atualizar estado dos botões
        self._atualizar_botoes()

    def _atualizar_botoes(self):
        """Atualiza estado dos botões de navegação"""
        aba_atual = self.notebook.index(self.notebook.select())

        # Botão Anterior (desabilitado na primeira aba)
        if aba_atual == 0:
            self.btn_anterior.config(state=tk.DISABLED)
        else:
            self.btn_anterior.config(state=tk.NORMAL)

        # Botão Próximo (desabilitado na última aba)
        if aba_atual == 3:
            self.btn_proximo.config(state=tk.DISABLED)
        else:
            self.btn_proximo.config(state=tk.NORMAL)

        # Botão Salvar (visível apenas nas abas 2, 3 e 4)
        if aba_atual == 0:
            self.btn_salvar.config(state=tk.DISABLED)
        else:
            self.btn_salvar.config(state=tk.NORMAL)

    def _aba_anterior(self):
        """Navega para aba anterior"""
        aba_atual = self.notebook.index(self.notebook.select())
        if aba_atual > 0:
            self.notebook.select(aba_atual - 1)

    def _proxima_aba(self):
        """Navega para próxima aba"""
        aba_atual = self.notebook.index(self.notebook.select())
        if aba_atual < 3:
            self.notebook.select(aba_atual + 1)

    def _criar_novo_cliente(self):
        """Cria novo cliente (abre Aba 2)"""
        # Limpar dados
        self.cliente_id = None
        self.dados_cliente = {}
        self.modo_edicao = False

        # Ir para Aba 2
        self.notebook.select(1)

    def _carregar_cliente_para_edicao(self, cliente_id: int):
        """Carrega cliente para edição (abre Aba 2)"""
        # Definir modo edição
        self.cliente_id = cliente_id
        self.modo_edicao = True

        # TODO: Carregar dados do cliente via API
        messagebox.showinfo(
            "Editar Cliente",
            f"Carregando cliente ID {cliente_id}...\n\n"
            "(Função será implementada nas próximas tarefas)",
            parent=self.window
        )

        # Ir para Aba 2
        self.notebook.select(1)

    def _salvar_cliente(self):
        """Salva dados do cliente"""
        # Validar dados básicos
        valido, msg_erro = self.dados_basicos.validar_dados()
        if not valido:
            messagebox.showerror(
                "❌ Erro de Validação",
                msg_erro,
                parent=self.window
            )
            # Ir para aba 2 onde está o erro
            self.notebook.select(1)
            return

        # Coletar dados de todas as abas
        dados = {
            **self.dados_basicos.obter_dados(),
            **self.complementares.obter_dados(),
            **self.observacoes.obter_dados()
        }

        # Mostrar resumo
        messagebox.showinfo(
            "✅ Dados Validados!",
            "Cliente pronto para salvar:\n\n"
            f"👤 {dados['nome']}\n"
            f"📍 {dados['cidade']}/{dados['estado']}\n"
            f"📞 {dados['telefone_principal']}\n"
            f"✉️ {dados['email_principal']}\n\n"
            f"Total de campos: {len(dados)}\n\n"
            "(Salvamento via API será implementado na integração)",
            parent=self.window
        )

    def _confirmar_fechar(self):
        """Confirma fechamento da janela"""
        if messagebox.askyesno(
            "❓ Confirmar",
            "Deseja realmente fechar?\n\n"
            "Alterações não salvas serão perdidas.",
            parent=self.window
        ):
            self.window.destroy()


# Teste rápido
if __name__ == "__main__":
    print("🧪 Testando wizard de clientes...")

    root = tk.Tk()
    root.withdraw()  # Esconde janela principal

    wizard = ClientesWizard(root)
    root.mainloop()
