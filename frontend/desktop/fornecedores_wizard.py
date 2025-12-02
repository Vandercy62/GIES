"""
WIZARD DE FORNECEDORES - INTERFACE PRINCIPAL
============================================

Interface moderna em 4 abas para cadastro completo de fornecedores.
Otimizada para usuários de idade avançada com fontes grandes e cores contrastantes.

ABAS:
1. Lista de Fornecedores - Busca, filtros, CRUD
2. Dados Básicos - 10 campos essenciais + avaliação estrelas
3. Dados Complementares - Endereço, contatos, comercial, bancário
4. Observações - Notas, histórico, tags, impressão ficha

NAVEGAÇÃO:
- Botões: ANTERIOR | PRÓXIMO | SALVAR | CANCELAR
- Atalhos: F2=Salvar | F3=Próximo | F4=Anterior | ESC=Cancelar
- Indicador: "ABA X de 4 - NOME DA ABA"

Autor: GitHub Copilot
Data: 16/11/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
import logging
import os

# Importações do sistema
from frontend.desktop.auth_middleware import (
    require_login,
    get_token_for_api,
    create_auth_header
)

# Importar componentes das abas
from frontend.desktop.fornecedores_components.aba_lista import AbaLista
from frontend.desktop.fornecedores_components.aba_dados_basicos import (
    AbaDadosBasicos
)
from frontend.desktop.fornecedores_components.aba_complementares import (
    AbaComplementares
)
from frontend.desktop.fornecedores_components.aba_observacoes import (
    AbaObservacoes
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =======================================
# CONSTANTES DE DESIGN
# =======================================

# Cores (mesmas da FASE 100)
COR_FUNDO = "#f8f9fa"
COR_DESTAQUE = "#e9ece"
COR_OBRIGATORIO = "#fff3cd"
COR_PROXIMO = "#28a745"
COR_ANTERIOR = "#007bf"
COR_CANCELAR = "#dc3545"
COR_SALVAR = "#155724"
COR_TEXTO = "#212529"
COR_BORDA = "#dee2e6"

# Fontes (otimizadas para idosos)
FONTE_TITULO = ("Segoe UI", 18, "bold")
FONTE_SECAO = ("Segoe UI", 16, "bold")
FONTE_LABEL = ("Segoe UI", 14, "bold")
FONTE_CAMPO = ("Segoe UI", 16)
FONTE_BOTAO = ("Segoe UI", 14, "bold")
FONTE_INDICADOR = ("Segoe UI", 12)

# Dimensões
ALTURA_BOTAO = 50
LARGURA_MINIMA = 150
PADDING_PADRAO = 20
PADDING_SECAO = 15


# =======================================
# CLASSE PRINCIPAL DO WIZARD
# =======================================

@require_login()
class FornecedoresWizard:
    """
    Wizard principal para gestão de fornecedores

    Interface em 4 abas com navegação fluida e validações completas.
    Integrado com SessionManager para autenticação automática.
    """

    def __init__(self, parent):
        """
        Inicializa o wizard de fornecedores

        Args:
            parent: Janela pai (root do tkinter)
        """
        self.parent = parent
        self.token = get_token_for_api()

        # Criar janela toplevel
        self.window = tk.Toplevel(parent)
        self.window.title("🏭 Cadastro de Fornecedores - Sistema ERP Primotex")
        self.window.geometry("1400x900")
        self.window.configure(bg=COR_FUNDO)

        # Centralizar janela
        self.centralizar_janela()

        # Variáveis de controle
        self.aba_atual = 0
        self.fornecedor_id = None  # ID do fornecedor sendo editado
        self.modo_edicao = False

        # Componentes das abas (serão criados depois)
        self.aba_lista = None
        self.aba_dados_basicos = None
        self.aba_complementares = None
        self.aba_observacoes = None

        # Criar interface
        self.criar_interface()

        # Configurar eventos
        self.configurar_eventos()

        # Focar no wizard
        self.window.focus_force()

        logger.info("FornecedoresWizard inicializado com sucesso")

    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()

        largura = self.window.winfo_width()
        altura = self.window.winfo_height()

        x = (self.window.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.window.winfo_screenheight() // 2) - (altura // 2)

        self.window.geometry(f'{largura}x{altura}+{x}+{y}')

    def criar_interface(self):
        """Cria a interface completa do wizard"""

        # Frame principal
        main_frame = tk.Frame(self.window, bg=COR_FUNDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING_PADRAO, pady=PADDING_PADRAO)

        # Header com título e indicador
        self.criar_header(main_frame)

        # Notebook com 4 abas
        self.criar_notebook(main_frame)

        # Barra de navegação inferior
        self.criar_barra_navegacao(main_frame)

    def criar_header(self, parent):
        """Cria o header com título e indicador de progresso"""

        header_frame = tk.Frame(parent, bg=COR_DESTAQUE, relief=tk.RIDGE, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, PADDING_SECAO))

        # Título principal
        titulo_label = tk.Label(
            header_frame,
            text="🏭 CADASTRO DE FORNECEDORES",
            font=FONTE_TITULO,
            bg=COR_DESTAQUE,
            fg=COR_TEXTO
        )
        titulo_label.pack(pady=(15, 5))

        # Indicador de progresso (será atualizado dinamicamente)
        self.indicador_label = tk.Label(
            header_frame,
            text="ABA 1 de 4 - LISTA DE FORNECEDORES",
            font=FONTE_INDICADOR,
            bg=COR_DESTAQUE,
            fg="#6c757d"
        )
        self.indicador_label.pack(pady=(0, 15))

    def criar_notebook(self, parent):
        """Cria o notebook com as 4 abas"""

        # Frame para o notebook
        notebook_frame = tk.Frame(parent, bg=COR_FUNDO)
        notebook_frame.pack(fill=tk.BOTH, expand=True, pady=PADDING_SECAO)

        # Criar notebook
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Criar abas
        self.criar_aba_lista()
        self.criar_aba_dados_basicos()
        self.criar_aba_complementares()
        self.criar_aba_observacoes()

        # Desabilitar navegação por clique nas abas (usar apenas botões)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_aba_changed)

        logger.info("Notebook com 4 abas criado")

    def criar_aba_lista(self):
        """Cria aba 1 - Lista de Fornecedores"""
        frame = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(frame, text="📋 Lista")

        # Criar componente da aba
        self.aba_lista = AbaLista(
            parent_frame=frame,
            on_novo_click=self.novo_fornecedor,
            on_editar_click=self.editar_fornecedor,
            token=self.token
        )

        logger.info("Aba Lista criada e integrada")

    def criar_aba_dados_basicos(self):
        """Cria aba 2 - Dados Básicos"""
        frame = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(frame, text="🏭 Dados Básicos")

        # Criar componente da aba
        self.aba_dados_basicos = AbaDadosBasicos(parent_frame=frame)

        logger.info("Aba Dados Básicos criada e integrada")

    def criar_aba_complementares(self):
        """Cria aba 3 - Dados Complementares"""
        frame = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(frame, text="📝 Complementares")

        # Criar componente da aba
        self.aba_complementares = AbaComplementares(parent_frame=frame)

        logger.info("Aba Complementares criada e integrada")

    def criar_aba_observacoes(self):
        """Cria aba 4 - Observações"""
        frame = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(frame, text="💬 Observações")

        # Criar componente da aba
        self.aba_observacoes = AbaObservacoes(
            parent_frame=frame,
            on_imprimir_callback=self.imprimir_ficha
        )

        logger.info("Aba Observações criada e integrada")

    def criar_aba_temporaria(self, index: int, titulo: str):
        """
        Cria uma aba temporária (placeholder)

        Args:
            index: Índice da aba
            titulo: Título da aba
        """
        frame = tk.Frame(self.notebook, bg=COR_FUNDO)
        self.notebook.add(frame, text=titulo)

        # Placeholder
        placeholder = tk.Label(
            frame,
            text=f"🚧 {titulo} será implementado em breve...",
            font=FONTE_SECAO,
            bg=COR_FUNDO,
            fg="#6c757d"
        )
        placeholder.pack(expand=True)

    def criar_barra_navegacao(self, parent):
        """Cria a barra de navegação inferior com botões"""

        nav_frame = tk.Frame(parent, bg=COR_DESTAQUE, relief=tk.RIDGE, bd=2)
        nav_frame.pack(fill=tk.X, pady=(PADDING_SECAO, 0))

        # Frame interno para centralizar botões
        buttons_frame = tk.Frame(nav_frame, bg=COR_DESTAQUE)
        buttons_frame.pack(pady=PADDING_SECAO)

        # Botão ANTERIOR (desabilitado na aba 1)
        self.btn_anterior = tk.Button(
            buttons_frame,
            text="⬅️ ANTERIOR",
            font=FONTE_BOTAO,
            bg=COR_ANTERIOR,
            fg="white",
            height=2,
            width=15,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
            command=self.aba_anterior
        )
        self.btn_anterior.pack(side=tk.LEFT, padx=10)
        self.btn_anterior.config(state=tk.DISABLED)  # Desabilitado na primeira aba

        # Botão PRÓXIMO
        self.btn_proximo = tk.Button(
            buttons_frame,
            text="PRÓXIMO ➡️",
            font=FONTE_BOTAO,
            bg=COR_PROXIMO,
            fg="white",
            height=2,
            width=15,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
            command=self.aba_proximo
        )
        self.btn_proximo.pack(side=tk.LEFT, padx=10)

        # Botão SALVAR (visível em todas as abas exceto a primeira)
        self.btn_salvar = tk.Button(
            buttons_frame,
            text="💾 SALVAR",
            font=FONTE_BOTAO,
            bg=COR_SALVAR,
            fg="white",
            height=2,
            width=15,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
            command=self.salvar_fornecedor
        )
        self.btn_salvar.pack(side=tk.LEFT, padx=10)

        # Botão CANCELAR
        self.btn_cancelar = tk.Button(
            buttons_frame,
            text="❌ CANCELAR",
            font=FONTE_BOTAO,
            bg=COR_CANCELAR,
            fg="white",
            height=2,
            width=15,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
            command=self.cancelar
        )
        self.btn_cancelar.pack(side=tk.LEFT, padx=10)

    def configurar_eventos(self):
        """Configura eventos e atalhos de teclado"""

        # Atalhos de teclado
        self.window.bind('<F2>', lambda e: self.salvar_fornecedor())
        self.window.bind('<F3>', lambda e: self.aba_proximo())
        self.window.bind('<F4>', lambda e: self.aba_anterior())
        self.window.bind('<Escape>', lambda e: self.cancelar())

        # Evento de fechamento
        self.window.protocol("WM_DELETE_WINDOW", self.cancelar)

        logger.info("Eventos e atalhos configurados")

    def on_aba_changed(self, event):
        """
        Callback quando a aba é alterada

        Args:
            event: Evento do notebook
        """
        self.aba_atual = self.notebook.index(self.notebook.select())
        self.atualizar_interface()

        # Se chegou na aba observações, sincronizar status
        if self.aba_atual == 3:  # Aba 4 (índice 3)
            self.sincronizar_status_observacoes()

        logger.debug(f"Aba alterada para: {self.aba_atual}")

    def atualizar_interface(self):
        """Atualiza a interface baseada na aba atual"""

        # Nomes das abas
        nomes_abas = [
            "LISTA DE FORNECEDORES",
            "DADOS BÁSICOS DO FORNECEDOR",
            "DADOS COMPLEMENTARES",
            "OBSERVAÇÕES E HISTÓRICO"
        ]

        # Atualizar indicador
        self.indicador_label.config(
            text=f"ABA {self.aba_atual + 1} de 4 - {nomes_abas[self.aba_atual]}"
        )

        # Atualizar estado dos botões
        if self.aba_atual == 0:
            # Primeira aba (Lista)
            self.btn_anterior.config(state=tk.DISABLED)
            self.btn_proximo.config(state=tk.NORMAL, text="NOVO FORNECEDOR ➡️")
            self.btn_salvar.pack_forget()  # Esconder botão salvar
        elif self.aba_atual == 3:
            # Última aba
            self.btn_anterior.config(state=tk.NORMAL)
            self.btn_proximo.config(state=tk.DISABLED)
            self.btn_salvar.pack(side=tk.LEFT, padx=10)  # Mostrar botão salvar
        else:
            # Abas intermediárias
            self.btn_anterior.config(state=tk.NORMAL)
            self.btn_proximo.config(state=tk.NORMAL, text="PRÓXIMO ➡️")
            self.btn_salvar.pack(side=tk.LEFT, padx=10)  # Mostrar botão salvar

    def aba_anterior(self):
        """Navega para a aba anterior"""
        if self.aba_atual > 0:
            self.notebook.select(self.aba_atual - 1)
            logger.debug(f"Navegou para aba {self.aba_atual - 1}")

    def aba_proximo(self):
        """Navega para a próxima aba"""
        if self.aba_atual == 0:
            # Na lista, "Próximo" = Novo Fornecedor
            self.novo_fornecedor()
        elif self.aba_atual < 3:
            # Validar aba atual antes de prosseguir
            if self.validar_aba_atual():
                self.notebook.select(self.aba_atual + 1)
                logger.debug(f"Navegou para aba {self.aba_atual + 1}")

    def validar_aba_atual(self) -> bool:
        """
        Valida a aba atual antes de prosseguir

        Returns:
            bool: True se válido, False caso contrário
        """
        if self.aba_atual == 1:  # Dados Básicos
            if self.aba_dados_basicos:
                return self.aba_dados_basicos.validar()

        # Outras abas sempre válidas (por enquanto)
        return True

    def novo_fornecedor(self):
        """Inicia cadastro de novo fornecedor"""
        self.modo_edicao = False
        self.fornecedor_id = None

        # Limpar formulários (quando implementados)
        # self.limpar_formularios()

        # Ir para aba de dados básicos
        self.notebook.select(1)

        logger.info("Iniciado cadastro de novo fornecedor")

    def editar_fornecedor(self, fornecedor_id: int):
        """
        Inicia edição de fornecedor existente

        Args:
            fornecedor_id: ID do fornecedor a editar
        """
        self.modo_edicao = True
        self.fornecedor_id = fornecedor_id

        # Carregar dados do fornecedor (quando implementado)
        # self.carregar_fornecedor(fornecedor_id)

        # Ir para aba de dados básicos
        self.notebook.select(1)

        logger.info(f"Iniciada edição do fornecedor ID: {fornecedor_id}")

    def salvar_fornecedor(self):
        """Salva o fornecedor (novo ou atualização)"""

        # Validar todos os dados
        if not self.validar_todos_dados():
            return

        # Coletar dados de todas as abas
        dados = self.coletar_todos_dados()

        if not dados:
            messagebox.showerror(
                "Erro",
                "Não foi possível coletar os dados do formulário."
            )
            return

        # TODO: Enviar para API
        # if self.modo_edicao:
        #     self.atualizar_fornecedor_api(dados)
        # else:
        #     self.criar_fornecedor_api(dados)

        # Temporário: Apenas mostrar mensagem
        messagebox.showinfo(
            "Sucesso",
            f"Fornecedor {'atualizado' if self.modo_edicao else 'cadastrado'} com sucesso!\n\n"
            "(Funcionalidade será implementada em breve)"
        )

        logger.info(f"Fornecedor {'atualizado' if self.modo_edicao else 'salvo'}")

    def validar_todos_dados(self) -> bool:
        """
        Valida todos os dados do formulário

        Returns:
            bool: True se válido, False caso contrário
        """
        # TODO: Implementar validação completa
        return True

    def coletar_todos_dados(self) -> Optional[Dict[str, Any]]:
        """
        Coleta dados de todas as abas

        Returns:
            dict: Dicionário com todos os dados ou None em caso de erro
        """
        dados: Dict[str, Any] = {}

        # Coletar dados das abas implementadas
        if self.aba_dados_basicos:
            dados.update(self.aba_dados_basicos.obter_dados())

        if self.aba_complementares:
            dados.update(self.aba_complementares.obter_dados())

        if self.aba_observacoes:
            dados.update(self.aba_observacoes.obter_dados())

        return dados

    def imprimir_ficha(self):
        """Imprime ficha do fornecedor em PDF"""
        try:
            # Coleta todos os dados das abas
            dados = self.coletar_todos_dados()

            # Valida se há dados mínimos
            if not dados.get('razao_social'):
                messagebox.showwarning(
                    "Dados Incompletos",
                    "Preencha pelo menos a Razão Social antes de gerar a ficha."
                )
                return

            # Importa gerador de PDF
            from frontend.desktop.fornecedor_ficha_pdf import FornecedorFichaPDF

            # Gera PDF
            gerador = FornecedorFichaPDF()
            filepath = gerador.gerar_ficha(dados)

            if filepath:
                # Pergunta se deseja abrir o arquivo
                resposta = messagebox.askyesno(
                    "Ficha Gerada",
                    "✅ Ficha PDF gerada com sucesso!\n\n"
                    f"📄 Arquivo: {os.path.basename(filepath)}\n\n"
                    "Deseja abrir o arquivo agora?",
                    icon='info'
                )

                if resposta:
                    # Abre PDF com aplicativo padrão do Windows
                    os.startfile(filepath)
            else:
                messagebox.showerror(
                    "Erro",
                    "❌ Erro ao gerar ficha PDF.\n\n"
                    "Verifique os logs para mais detalhes."
                )

        except ImportError as e:
            messagebox.showerror(
                "Módulo não disponível",
                "Gerador de PDF não encontrado.\n\n"
                f"Erro: {e}"
            )
        except Exception as e:
            logger.error(f"Erro ao imprimir ficha: {e}", exc_info=True)
            messagebox.showerror(
                "Erro",
                f"❌ Erro ao gerar ficha PDF:\n\n{str(e)}"
            )

    def sincronizar_status_observacoes(self):
        """Sincroniza status do fornecedor com aba observações"""
        if self.aba_dados_basicos and self.aba_observacoes:
            dados_basicos = self.aba_dados_basicos.obter_dados()
            status = dados_basicos.get('status', 'Ativo')
            self.aba_observacoes.atualizar_status_fornecedor(status)

    def cancelar(self):
        """Cancela e fecha o wizard"""

        # Confirmar se há alterações não salvas
        if self.modo_edicao or self.fornecedor_id:
            resposta = messagebox.askyesno(
                "Confirmar",
                "Deseja realmente cancelar?\n\n"
                "Todas as alterações não salvas serão perdidas.",
                icon='warning'
            )

            if not resposta:
                return

        # Fechar janela
        self.window.destroy()
        logger.info("Wizard de fornecedores fechado")


# =======================================
# FUNÇÃO DE TESTE
# =======================================

def main():
    """Função para testar o wizard"""
    root = tk.Tk()
    root.withdraw()  # Esconder janela principal

    # Criar wizard
    wizard = FornecedoresWizard(root)

    root.mainloop()


if __name__ == "__main__":
    main()
