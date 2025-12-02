"""
SISTEMA ERP PRIMOTEX - ABA 4: OBSERVAÇÕES FORNECEDOR
====================================================

Componente de observações, histórico e tags do fornecedor.
Última aba do wizard com campos de texto livre, tags e impressão.

CAMPOS (4 total):
1. observacoes - Text (notas gerais, 6 linhas)
2. historico_problemas - Text (problemas reportados, 6 linhas)
3. tags - List[str] (chips editáveis)
4. motivo_inativacao - Entry (condicional se status='Inativo')

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 101
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AbaObservacoes:
    """
    Aba de observações do fornecedor.
    Texto livre, histórico de problemas, tags e motivo inativação.
    """
    
    # Cores
    COR_FUNDO = "#f8f9fa"
    COR_TAG = "#007bff"
    COR_TAG_TEXTO = "white"
    COR_BOTAO_ADD = "#28a745"
    COR_BOTAO_REMOVER = "#dc3545"
    COR_BOTAO_PDF = "#155724"
    COR_ALERTA = "#fff3cd"
    
    # Fontes
    FONTE_SECAO = ("Segoe UI", 16, "bold")
    FONTE_LABEL = ("Segoe UI", 14, "bold")
    FONTE_CAMPO = ("Segoe UI", 16)
    FONTE_TEXTO = ("Segoe UI", 14)
    FONTE_TAG = ("Segoe UI", 13, "bold")
    FONTE_HINT = ("Segoe UI", 11, "italic")
    
    def __init__(self, parent_frame: tk.Frame, on_imprimir_callback=None):
        """
        Inicializa aba de observações
        
        Args:
            parent_frame: Frame pai
            on_imprimir_callback: Callback para impressão de ficha PDF
        """
        self.parent = parent_frame
        self.on_imprimir_callback = on_imprimir_callback
        
        # Dados
        self.tags: List[str] = []
        
        # Referências a widgets
        self.text_observacoes: Optional[tk.Text] = None
        self.text_historico: Optional[tk.Text] = None
        self.tags_frame: Optional[tk.Frame] = None
        self.entry_nova_tag: Optional[tk.Entry] = None
        self.var_motivo_inativacao: tk.StringVar = tk.StringVar()
        self.frame_motivo: Optional[tk.Frame] = None
        
        # Status do fornecedor (será atualizado externamente)
        self.status_fornecedor: str = "Ativo"
        
        # Criar interface
        self._criar_interface()
        
        logger.info("AbaObservacoes inicializada")
        
    def _criar_interface(self):
        """Cria interface da aba"""
        # Canvas com scroll
        canvas = tk.Canvas(self.parent, bg=self.COR_FUNDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            self.parent,
            orient=tk.VERTICAL,
            command=canvas.yview
        )
        
        scrollable_frame = tk.Frame(canvas, bg=self.COR_FUNDO)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame de conteúdo
        main_frame = tk.Frame(scrollable_frame, bg=self.COR_FUNDO)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Criar seções
        self._criar_secao_observacoes(main_frame)
        self._criar_secao_historico_problemas(main_frame)
        self._criar_secao_tags(main_frame)
        self._criar_secao_motivo_inativacao(main_frame)
        self._criar_secao_acoes(main_frame)
        
    def _criar_secao_observacoes(self, parent: tk.Frame):
        """Cria seção de observações gerais"""
        frame = tk.LabelFrame(
            parent,
            text=" 📝 OBSERVAÇÕES GERAIS ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Hint
        tk.Label(
            frame,
            text="Notas e informações relevantes sobre o fornecedor:",
            font=self.FONTE_HINT,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Text com scroll
        text_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_observacoes = tk.Text(
            text_frame,
            font=self.FONTE_TEXTO,
            height=6,
            wrap=tk.WORD,
            yscrollcommand=scroll.set
        )
        self.text_observacoes.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.text_observacoes.yview)
        
    def _criar_secao_historico_problemas(self, parent: tk.Frame):
        """Cria seção de histórico de problemas"""
        frame = tk.LabelFrame(
            parent,
            text=" 🚨 HISTÓRICO DE PROBLEMAS ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Hint
        tk.Label(
            frame,
            text="Registro de problemas, atrasos, não-conformidades, etc:",
            font=self.FONTE_HINT,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Text com scroll
        text_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_historico = tk.Text(
            text_frame,
            font=self.FONTE_TEXTO,
            height=6,
            wrap=tk.WORD,
            yscrollcommand=scroll.set
        )
        self.text_historico.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.text_historico.yview)
        
    def _criar_secao_tags(self, parent: tk.Frame):
        """Cria seção de tags (chips editáveis)"""
        frame = tk.LabelFrame(
            parent,
            text=" 🏷️ TAGS E CATEGORIAS ",
            font=self.FONTE_SECAO,
            bg=self.COR_FUNDO,
            fg="#212529",
            padx=20,
            pady=15
        )
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Hint
        tk.Label(
            frame,
            text="Etiquetas para organização (ex: Confiável, Atraso Frequente, VIP):",
            font=self.FONTE_HINT,
            bg=self.COR_FUNDO,
            fg="#6c757d"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Frame de entrada + botão
        input_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.entry_nova_tag = tk.Entry(
            input_frame,
            font=self.FONTE_CAMPO,
            width=30
        )
        self.entry_nova_tag.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_nova_tag.bind("<Return>", lambda e: self._adicionar_tag())
        
        tk.Button(
            input_frame,
            text="➕ ADICIONAR TAG",
            font=("Segoe UI", 12, "bold"),
            bg=self.COR_BOTAO_ADD,
            fg="white",
            cursor="hand2",
            command=self._adicionar_tag
        ).pack(side=tk.LEFT)
        
        # Frame para exibir chips de tags
        self.tags_frame = tk.Frame(frame, bg=self.COR_FUNDO)
        self.tags_frame.pack(fill=tk.X)
        
    def _criar_secao_motivo_inativacao(self, parent: tk.Frame):
        """Cria seção de motivo de inativação (condicional)"""
        self.frame_motivo = tk.LabelFrame(
            parent,
            text=" 🚫 MOTIVO DE INATIVAÇÃO ",
            font=self.FONTE_SECAO,
            bg=self.COR_ALERTA,
            fg="#856404",
            padx=20,
            pady=15
        )
        # Inicialmente oculto
        # self.frame_motivo.pack(fill=tk.X, pady=(0, 20))
        
        # Hint
        tk.Label(
            self.frame_motivo,
            text="Por que este fornecedor foi inativado?",
            font=self.FONTE_HINT,
            bg=self.COR_ALERTA,
            fg="#856404"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Entry
        entry_motivo = tk.Entry(
            self.frame_motivo,
            textvariable=self.var_motivo_inativacao,
            font=self.FONTE_CAMPO,
            bg="white"
        )
        entry_motivo.pack(fill=tk.X)
        
    def _criar_secao_acoes(self, parent: tk.Frame):
        """Cria seção de ações (botão imprimir ficha)"""
        frame = tk.Frame(parent, bg=self.COR_FUNDO)
        frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botão IMPRIMIR FICHA PDF
        btn_imprimir = tk.Button(
            frame,
            text="🖨️ IMPRIMIR FICHA DO FORNECEDOR (PDF)",
            font=("Segoe UI", 16, "bold"),
            bg=self.COR_BOTAO_PDF,
            fg="white",
            height=2,
            cursor="hand2",
            relief=tk.RAISED,
            bd=3,
            command=self._imprimir_ficha
        )
        btn_imprimir.pack(fill=tk.X)
        
    def _adicionar_tag(self):
        """Adiciona nova tag à lista"""
        nova_tag = self.entry_nova_tag.get().strip()
        
        if not nova_tag:
            return
        
        # Verificar duplicata
        if nova_tag.lower() in [t.lower() for t in self.tags]:
            messagebox.showwarning(
                "Tag Duplicada",
                f"A tag '{nova_tag}' já existe."
            )
            return
        
        # Adicionar à lista
        self.tags.append(nova_tag)
        
        # Limpar campo
        self.entry_nova_tag.delete(0, tk.END)
        
        # Atualizar visualização
        self._atualizar_tags()
        
        logger.info(f"Tag adicionada: {nova_tag}")
        
    def _remover_tag(self, tag: str):
        """
        Remove tag da lista
        
        Args:
            tag: Tag a ser removida
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self._atualizar_tags()
            logger.info(f"Tag removida: {tag}")
        
    def _atualizar_tags(self):
        """Atualiza visualização dos chips de tags"""
        # Limpar frame
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
        
        if not self.tags:
            # Mensagem vazia
            tk.Label(
                self.tags_frame,
                text="Nenhuma tag adicionada",
                font=self.FONTE_HINT,
                bg=self.COR_FUNDO,
                fg="#6c757d"
            ).pack(anchor=tk.W, pady=10)
            return
        
        # Criar chips
        for tag in self.tags:
            chip = tk.Frame(
                self.tags_frame,
                bg=self.COR_TAG,
                relief=tk.RAISED,
                bd=2
            )
            chip.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Label da tag
            tk.Label(
                chip,
                text=f"  {tag}  ",
                font=self.FONTE_TAG,
                bg=self.COR_TAG,
                fg=self.COR_TAG_TEXTO
            ).pack(side=tk.LEFT, padx=(5, 0))
            
            # Botão remover
            btn_remover = tk.Label(
                chip,
                text=" ✖ ",
                font=("Segoe UI", 11, "bold"),
                bg=self.COR_TAG,
                fg=self.COR_TAG_TEXTO,
                cursor="hand2"
            )
            btn_remover.pack(side=tk.LEFT, padx=(0, 5))
            btn_remover.bind("<Button-1>", lambda e, t=tag: self._remover_tag(t))
            
    def _imprimir_ficha(self):
        """Imprime ficha do fornecedor em PDF"""
        if self.on_imprimir_callback:
            self.on_imprimir_callback()
        else:
            messagebox.showinfo(
                "Impressão",
                "Funcionalidade de impressão será implementada em breve.\n\n"
                "Arquivo: fornecedor_ficha_pdf.py"
            )
    
    def atualizar_status_fornecedor(self, status: str):
        """
        Atualiza status do fornecedor e mostra/oculta motivo inativação
        
        Args:
            status: Status atual ('Ativo', 'Inativo', 'Suspenso', 'Bloqueado')
        """
        self.status_fornecedor = status
        
        if status == "Inativo":
            # Mostrar campo motivo
            self.frame_motivo.pack(fill=tk.X, pady=(0, 20))
        else:
            # Ocultar campo motivo
            self.frame_motivo.pack_forget()
            self.var_motivo_inativacao.set("")  # Limpar
        
        logger.info(f"Status atualizado: {status}, Motivo visível: {status == 'Inativo'}")
    
    def obter_dados(self) -> Dict[str, Any]:
        """
        Obtém dados do formulário
        
        Returns:
            dict: Dicionário com dados de observações
        """
        # Obter texto dos campos Text
        observacoes = self.text_observacoes.get("1.0", tk.END).strip()
        historico = self.text_historico.get("1.0", tk.END).strip()
        
        dados = {
            'observacoes': observacoes if observacoes else None,
            'historico_problemas': historico if historico else None,
            'tags': self.tags.copy() if self.tags else [],
            'motivo_inativacao': self.var_motivo_inativacao.get().strip() or None
        }
        
        return dados
    
    def carregar_dados(self, dados: Dict[str, Any]):
        """
        Carrega dados no formulário
        
        Args:
            dados: Dicionário com dados do fornecedor
        """
        # Observações
        observacoes = dados.get('observacoes', '')
        if observacoes:
            self.text_observacoes.delete("1.0", tk.END)
            self.text_observacoes.insert("1.0", observacoes)
        
        # Histórico problemas
        historico = dados.get('historico_problemas', '')
        if historico:
            self.text_historico.delete("1.0", tk.END)
            self.text_historico.insert("1.0", historico)
        
        # Tags
        tags = dados.get('tags', [])
        if isinstance(tags, list):
            self.tags = tags.copy()
        else:
            self.tags = []
        self._atualizar_tags()
        
        # Motivo inativação
        motivo = dados.get('motivo_inativacao', '')
        self.var_motivo_inativacao.set(motivo if motivo else '')
        
        # Atualizar visibilidade do motivo baseado no status
        status = dados.get('status', 'Ativo')
        self.atualizar_status_fornecedor(status)
        
        logger.info("Dados carregados na aba Observações")
    
    def limpar(self):
        """Limpa todos os campos"""
        # Limpar Text widgets
        if self.text_observacoes:
            self.text_observacoes.delete("1.0", tk.END)
        
        if self.text_historico:
            self.text_historico.delete("1.0", tk.END)
        
        # Limpar tags
        self.tags = []
        self._atualizar_tags()
        
        # Limpar motivo
        self.var_motivo_inativacao.set("")
        
        # Ocultar frame motivo
        if self.frame_motivo:
            self.frame_motivo.pack_forget()
        
        # Limpar campo entrada tag
        if self.entry_nova_tag:
            self.entry_nova_tag.delete(0, tk.END)
        
        logger.info("Formulário Observações limpo")


# =======================================
# TESTE STANDALONE
# =======================================

if __name__ == "__main__":
    """Teste standalone do componente"""
    
    root = tk.Tk()
    root.title("Teste - Aba Observações Fornecedor")
    root.geometry("900x800")
    
    # Frame principal
    frame = tk.Frame(root, bg="#f8f9fa")
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Criar componente
    aba = AbaObservacoes(
        parent_frame=frame,
        on_imprimir_callback=lambda: print("Impressão solicitada!")
    )
    
    # Dados de teste
    dados_teste = {
        'observacoes': 'Fornecedor confiável.\nSempre entrega no prazo.\nPreços competitivos.',
        'historico_problemas': '15/10/2024 - Atraso de 2 dias no pedido #1234\n20/09/2024 - Produto defeituoso lote X',
        'tags': ['Confiável', 'Pontual', 'Preço Bom', 'VIP'],
        'motivo_inativacao': '',
        'status': 'Ativo'
    }
    
    # Botões de teste
    btn_frame = tk.Frame(root, bg="#e9ecef", pady=10)
    btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
    
    def carregar_teste():
        aba.carregar_dados(dados_teste)
    
    def obter_teste():
        dados = aba.obter_dados()
        print("\n=== DADOS OBTIDOS ===")
        for k, v in dados.items():
            print(f"{k}: {v}")
    
    def limpar_teste():
        aba.limpar()
    
    def ativar():
        aba.atualizar_status_fornecedor("Ativo")
    
    def inativar():
        aba.atualizar_status_fornecedor("Inativo")
    
    tk.Button(btn_frame, text="Carregar Teste", command=carregar_teste).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Obter Dados", command=obter_teste).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Limpar", command=limpar_teste).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Status: Ativo", command=ativar, bg="#28a745", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Status: Inativo", command=inativar, bg="#dc3545", fg="white").pack(side=tk.LEFT, padx=5)
    
    root.mainloop()
