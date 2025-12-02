"""
SISTEMA ERP PRIMOTEX - WIZARD DE COLABORADORES
===============================================

Janela principal do wizard de cadastro de colaboradores/funcionários.
Interface moderna em 4 abas com navegação facilitada e sistema de alertas.

ESTRUTURA:
- Aba 1: Lista de colaboradores (busca e filtros)
- Aba 2: Dados Pessoais (nome, CPF, RG, endereço, foto 3x4)
- Aba 3: Dados Profissionais (cargo, salário, contrato)
- Aba 4: Documentos (CNH, ASO, NR, EPI) ⭐⭐⭐ SISTEMA DE ALERTAS
- Aba 5: Observações (notas, férias, avaliações)

FUNCIONALIDADES CRÍTICAS:
✅ Foto 3x4 (upload/webcam) - Integrado
✅ Sistema de Alertas de Documentos:
   - 🟢 > 30 dias até vencimento
   - 🟡 15-30 dias até vencimento
   - 🟠 1-14 dias até vencimento
   - 🔴 Vencido

NAVEGAÇÃO:
- Botões: Anterior | Próximo | Cancelar | Salvar
- Atalhos: F3=Próximo | F4=Anterior | F2=Salvar | ESC=Cancelar
- Cores: Verde=Next, Azul=Prev, Vermelho=Cancel, Verde Escuro=Save

Autor: GitHub Copilot
Data: 17/11/2025 - FASE 103
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any, List
import threading
import requests

from frontend.desktop.auth_middleware import (
    require_login,
    get_token_for_api,
    create_auth_header,
    get_current_user_info
)


# Constantes globais
_FONTE_FAMILIA_PADRAO = "Segoe UI"


@require_login()
class ColaboradoresWizard:
    """
    Wizard completo de cadastro de colaboradores com 5 abas.
    Interface otimizada com fontes grandes e sistema de alertas visual.
    """

    # Cores do sistema (padrão GIES)
    COR_PROXIMO = "#28a745"        # Verde
    COR_ANTERIOR = "#007bff"       # Azul
    COR_CANCELAR = "#dc3545"       # Vermelho
    COR_SALVAR = "#155724"         # Verde escuro
    COR_FUNDO = "#f8f9fa"          # Cinza claro
    COR_DESTAQUE = "#e9ecef"       # Cinza médio

    # Cores de Alerta (Documentos) ⭐
    COR_ALERTA_OK = "#28a745"  # 🟢 Verde - > 30 dias
    COR_ALERTA_ATENCAO = "#ffc107"  # 🟡 Amarelo - 15-30 dias
    COR_ALERTA_URGENTE = "#fd7e14"  # 🟠 Laranja - 1-14 dias
    COR_ALERTA_VENCIDO = "#dc3545"  # 🔴 Vermelho - Vencido

    # Fontes do sistema
    FONTE_TITULO = (_FONTE_FAMILIA_PADRAO, 18, "bold")
    FONTE_LABEL = (_FONTE_FAMILIA_PADRAO, 14, "bold")
    FONTE_CAMPO = (_FONTE_FAMILIA_PADRAO, 16)
    FONTE_BOTAO = (_FONTE_FAMILIA_PADRAO, 14, "bold")
    FONTE_ALERTA = (_FONTE_FAMILIA_PADRAO, 12, "bold")

    def __init__(self, parent: tk.Tk):
        """
        Inicializa wizard de colaboradores.

        Args:
            parent: Janela pai (dashboard)
        """
        self.parent = parent
        self.token = get_token_for_api()
        self.user_info = get_current_user_info()
        self.API_BASE_URL = "http://127.0.0.1:8002"

        # Dados do colaborador em edição
        self.colaborador_id: Optional[int] = None
        self.dados_colaborador: Dict[str, Any] = {}
        self.modo_edicao = False

        # Listas de departamentos e cargos (carregadas do backend)
        self.departamentos: List[Dict[str, Any]] = []
        self.cargos: List[Dict[str, Any]] = []
        self.colaboradores_lista: List[Dict[str, Any]] = []

        # Criar janela principal
        self.window = tk.Toplevel(parent)
        self.window.title("👥 Cadastro de Colaboradores - ERP Primotex")
        self.window.geometry("1500x950")
        self.window.configure(bg=self.COR_FUNDO)

        # Centralizar janela
        self._centralizar_janela()

        # Carregar dados iniciais
        self._carregar_dados_iniciais()

        # Criar interface
        self._criar_header()
        self._criar_notebook()
        self._criar_rodape()

        # Configurar atalhos de teclado
        self._configurar_atalhos()

        # Configurar fechamento da janela
        self.window.protocol("WM_DELETE_WINDOW", self._confirmar_fechar)

        # Focar na primeira aba
        self.notebook.select(0)

    def _centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        largura = self.window.winfo_width()
        altura = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.window.winfo_screenheight() // 2) - (altura // 2)
        self.window.geometry(f'+{x}+{y}')

    def _carregar_dados_iniciais(self):
        """Carrega departamentos, cargos e colaboradores do backend"""
        def carregar_thread():
            try:
                import requests
                headers = create_auth_header()
                base_url = "http://127.0.0.1:8002"

                # Carregar departamentos
                response = requests.get(
                    f"{base_url}/api/v1/colaboradores/departamentos/",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    self.departamentos = response.json()

                # Carregar cargos
                response = requests.get(
                    f"{base_url}/api/v1/colaboradores/cargos/",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    self.cargos = response.json()

                # Carregar colaboradores ativos (para responsável)
                response = requests.get(
                    f"{base_url}/api/v1/colaboradores/?ativo=true",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    self.colaboradores_lista = data.get('items', [])

            except (ConnectionError, TimeoutError, ValueError) as e:
                print(f"Erro ao carregar dados iniciais: {e}")

        # Executar em thread separada
        thread = threading.Thread(target=carregar_thread, daemon=True)
        thread.start()

    def _criar_header(self):
        """Cria o cabeçalho da janela"""
        header_frame = tk.Frame(
            self.window,
            bg=self.COR_DESTAQUE,
            height=80
        )
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Título
        titulo = tk.Label(
            header_frame,
            text="👥 CADASTRO DE COLABORADORES",
            font=("Segoe UI", 24, "bold"),
            bg=self.COR_DESTAQUE,
            fg="#212529"
        )
        titulo.pack(pady=15)

        # Informações do usuário logado
        user_info_frame = tk.Frame(header_frame, bg=self.COR_DESTAQUE)
        user_info_frame.pack(side=tk.RIGHT, padx=20)

        user_label = tk.Label(
            user_info_frame,
            text=f"👤 {self.user_info.get('username', 'Usuário')}",
            font=("Segoe UI", 12),
            bg=self.COR_DESTAQUE,
            fg="#6c757d"
        )
        user_label.pack()

    def _criar_notebook(self):
        """Cria o notebook com as abas"""
        # Frame para o notebook
        notebook_frame = tk.Frame(self.window, bg=self.COR_FUNDO)
        notebook_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Criar notebook
        style = ttk.Style()
        style.configure(
            'Custom.TNotebook',
            background=self.COR_FUNDO,
            borderwidth=0
        )
        style.configure(
            'Custom.TNotebook.Tab',
            font=self.FONTE_LABEL,
            padding=[20, 10]
        )

        self.notebook = ttk.Notebook(
            notebook_frame,
            style='Custom.TNotebook'
        )
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Criar abas usando componentes reais
        self._criar_aba_lista()
        self._criar_aba_dados_pessoais()
        self._criar_aba_dados_profissionais()
        self._criar_aba_documentos()
        self._criar_aba_observacoes()

    def _criar_aba_lista(self):
        """Cria aba de lista de colaboradores"""
        from frontend.desktop.colaboradores_components import AbaLista
        
        self.aba_lista = AbaLista(
            self.notebook,
            on_novo=self._novo_colaborador,
            on_editar=self._editar_colaborador,
            on_excluir=self._excluir_colaborador
        )
        self.notebook.add(self.aba_lista, text="📋 Lista de Colaboradores")

    def _criar_aba_dados_pessoais(self):
        """Cria aba de dados pessoais"""
        from frontend.desktop.colaboradores_components import AbaDadosPessoais
        
        self.aba_dados_pessoais = AbaDadosPessoais(self.notebook)
        self.notebook.add(self.aba_dados_pessoais, text="👤 Dados Pessoais")

    def _criar_aba_dados_profissionais(self):
        """Cria aba de dados profissionais"""
        from frontend.desktop.colaboradores_components import (
            AbaDadosProfissionais
        )
        
        self.aba_dados_profissionais = AbaDadosProfissionais(self.notebook)
        self.notebook.add(
            self.aba_dados_profissionais,
            text="💼 Dados Profissionais"
        )

    def _criar_aba_documentos(self):
        """Cria aba de documentos ⭐⭐⭐ CRÍTICO"""
        from frontend.desktop.colaboradores_components import AbaDocumentos
        
        self.aba_documentos = AbaDocumentos(self.notebook)
        self.notebook.add(self.aba_documentos, text="📄 Documentos ⭐")

    def _criar_aba_observacoes(self):
        """Cria aba de observações"""
        from frontend.desktop.colaboradores_components import AbaObservacoes
        
        self.aba_observacoes = AbaObservacoes(self.notebook)
        self.notebook.add(self.aba_observacoes, text="📝 Observações")

    def _criar_rodape(self):
        """Cria o rodapé com botões de navegação"""
        rodape_frame = tk.Frame(
            self.window,
            bg=self.COR_DESTAQUE,
            height=80
        )
        rodape_frame.pack(fill=tk.X, side=tk.BOTTOM)
        rodape_frame.pack_propagate(False)

        # Container dos botões
        botoes_frame = tk.Frame(rodape_frame, bg=self.COR_DESTAQUE)
        botoes_frame.pack(expand=True)

        # Botão Anterior
        btn_anterior = tk.Button(
            botoes_frame,
            text="⬅️ Anterior (F4)",
            font=self.FONTE_BOTAO,
            bg=self.COR_ANTERIOR,
            fg="white",
            width=18,
            height=2,
            command=self._aba_anterior,
            cursor="hand2"
        )
        btn_anterior.pack(side=tk.LEFT, padx=10)

        # Botão Próximo
        btn_proximo = tk.Button(
            botoes_frame,
            text="Próximo ➡️ (F3)",
            font=self.FONTE_BOTAO,
            bg=self.COR_PROXIMO,
            fg="white",
            width=18,
            height=2,
            command=self._proxima_aba,
            cursor="hand2"
        )
        btn_proximo.pack(side=tk.LEFT, padx=10)

        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame,
            text="❌ Cancelar (ESC)",
            font=self.FONTE_BOTAO,
            bg=self.COR_CANCELAR,
            fg="white",
            width=18,
            height=2,
            command=self._confirmar_fechar,
            cursor="hand2"
        )
        btn_cancelar.pack(side=tk.LEFT, padx=10)

        # Botão Salvar
        btn_salvar = tk.Button(
            botoes_frame,
            text="💾 Salvar (F2)",
            font=self.FONTE_BOTAO,
            bg=self.COR_SALVAR,
            fg="white",
            width=18,
            height=2,
            command=self._salvar_colaborador,
            cursor="hand2"
        )
        btn_salvar.pack(side=tk.LEFT, padx=10)
        
        # Botão Export PDF
        btn_export = tk.Button(
            botoes_frame,
            text="📄 Exportar PDF",
            font=self.FONTE_BOTAO,
            bg="#6c757d",
            fg="white",
            width=18,
            height=2,
            command=self._exportar_pdf,
            cursor="hand2"
        )
        btn_export.pack(side=tk.LEFT, padx=10)

    def _configurar_atalhos(self):
        """Configura atalhos de teclado"""
        self.window.bind('<F2>', lambda e: self._salvar_colaborador())
        self.window.bind('<F3>', lambda e: self._proxima_aba())
        self.window.bind('<F4>', lambda e: self._aba_anterior())
        self.window.bind('<Escape>', lambda e: self._confirmar_fechar())

    def _proxima_aba(self):
        """Avança para a próxima aba"""
        aba_atual = self.notebook.index(self.notebook.select())
        total_abas = self.notebook.index("end")
        
        if aba_atual < total_abas - 1:
            self.notebook.select(aba_atual + 1)

    def _aba_anterior(self):
        """Volta para a aba anterior"""
        aba_atual = self.notebook.index(self.notebook.select())
        
        if aba_atual > 0:
            self.notebook.select(aba_atual - 1)

    def _salvar_colaborador(self):
        """Salva os dados do colaborador"""
        # Coletar dados de todas as abas
        dados = {
            **self.aba_dados_pessoais.get_dados(),
            **self.aba_dados_profissionais.get_dados(),
            'documentos': self.aba_documentos.get_dados(),
            **self.aba_observacoes.get_dados()
        }
        
        # Validação básica
        if not dados.get('nome'):
            messagebox.showwarning(
                "Validação",
                "Nome é obrigatório!",
                parent=self.window
            )
            return
        
        if not dados.get('cpf'):
            messagebox.showwarning(
                "Validação",
                "CPF é obrigatório!",
                parent=self.window
            )
            return
        
        # Thread para salvar
        def salvar_thread():
            try:
                headers = create_auth_header()
                response = requests.post(
                    f"{self.API_BASE_URL}/api/v1/colaboradores/",
                    json=dados,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in (200, 201):
                    self.window.after(0, lambda: messagebox.showinfo(
                        "Sucesso",
                        "Colaborador salvo com sucesso!",
                        parent=self.window
                    ))
                    self.window.after(0, self.aba_lista._carregar_dados)
                else:
                    raise ValueError(f"Erro HTTP {response.status_code}")
                    
            except (requests.RequestException, ValueError) as err:
                self.window.after(0, lambda e=err: messagebox.showerror(
                    "Erro",
                    f"Erro ao salvar: {str(e)}",
                    parent=self.window
                ))
        
        threading.Thread(target=salvar_thread, daemon=True).start()
    
    def _exportar_pdf(self):
        """Exporta ficha do colaborador em PDF"""
        from frontend.desktop.colaborador_ficha_pdf import (
            gerar_ficha_colaborador
        )
        
        # Coletar dados
        dados = {
            **self.aba_dados_pessoais.get_dados(),
            **self.aba_dados_profissionais.get_dados(),
            'documentos': self.aba_documentos.get_dados(),
            **self.aba_observacoes.get_dados()
        }
        
        if not dados.get('nome'):
            messagebox.showwarning(
                "Atenção",
                "Preencha os dados do colaborador antes de exportar!",
                parent=self.window
            )
            return
        
        # Dialog para salvar arquivo
        nome_arquivo = dados.get('nome', 'colaborador').replace(' ', '_')
        filename = filedialog.asksaveasfilename(
            parent=self.window,
            title="Salvar Ficha PDF",
            defaultextension=".pdf",
            initialfile=f"ficha_{nome_arquivo}.pdf",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")]
        )
        
        if filename:
            # Thread para gerar PDF
            def gerar_thread():
                try:
                    output_path = gerar_ficha_colaborador(dados, filename)
                    
                    if output_path:
                        self.window.after(0, lambda: messagebox.showinfo(
                            "Sucesso",
                            f"PDF gerado com sucesso!\n\n{output_path}",
                            parent=self.window
                        ))
                    else:
                        raise ValueError("Erro ao gerar PDF")
                        
                except (OSError, ValueError) as err:
                    self.window.after(0, lambda e=err: messagebox.showerror(
                        "Erro",
                        f"Erro ao gerar PDF: {str(e)}",
                        parent=self.window
                    ))
            
            threading.Thread(target=gerar_thread, daemon=True).start()

    def _confirmar_fechar(self):
        """Confirma fechamento da janela"""
        if messagebox.askyesno(
            "Confirmar",
            "Deseja realmente fechar esta janela?\n\n"
            "⚠️ Dados não salvos serão perdidos!",
            parent=self.window
        ):
            self.window.destroy()


# =======================================
# TESTE RÁPIDO
# =======================================

if __name__ == "__main__":
    # Mock da sessão para teste
    from shared.session_manager import session
    session.login(
        token="test_token",
        user_data={"username": "admin", "permissions": ["admin"]},
        token_expiry_hours=24
    )

    root = tk.Tk()
    root.withdraw()  # Esconder janela principal
    
    wizard = ColaboradoresWizard(root)
    
    root.mainloop()
