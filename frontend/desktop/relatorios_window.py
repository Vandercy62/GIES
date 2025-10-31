"""
SISTEMA ERP PRIMOTEX - GERADOR DE RELATÓRIOS PDF
===============================================

Sistema completo para geração de relatórios em PDF com templates
personalizados para diferentes módulos do sistema.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import Dict, Any, Optional, List
import os

# Constantes da UI centralizadas
from ui_constants import MOUSE_EVENTS
import tempfile
from datetime import datetime, timedelta
from io import BytesIO

# Importações para PDF
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.units import inch, cm
    from reportlab.lib.utils import ImageReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    messagebox.showerror(
        "Erro",
        "Biblioteca ReportLab não encontrada!\n\nInstale com: pip install reportlab"
    )

# =======================================
# CONFIGURAÇÕES
# =======================================

API_BASE_URL = "http://127.0.0.1:8002"

# Templates de relatórios disponíveis
TEMPLATES_RELATORIOS = {
    "clientes": {
        "nome": "Relatório de Clientes",
        "descricao": "Lista completa de clientes cadastrados",
        "icone": "👥"
    },
    "produtos": {
        "nome": "Relatório de Produtos",
        "descricao": "Catálogo de produtos e serviços",
        "icone": "📦"
    },
    "estoque": {
        "nome": "Relatório de Estoque",
        "descricao": "Situação atual do estoque",
        "icone": "📊"
    },
    "movimentacoes": {
        "nome": "Movimentações de Estoque",
        "descricao": "Histórico de movimentações",
        "icone": "🔄"
    },
    "vendas": {
        "nome": "Relatório de Vendas",
        "descricao": "Resumo de vendas por período",
        "icone": "💰"
    },
    "financeiro": {
        "nome": "Relatório Financeiro",
        "descricao": "Situação financeira geral",
        "icone": "💳"
    }
}

# =======================================
# CLASSE GERADOR DE RELATÓRIOS
# =======================================

class RelatoriosWindow:
    """Sistema de geração de relatórios em PDF"""
    
    def __init__(self, user_data: Dict[str, Any], parent_window=None):
        self.user_data = user_data
        self.token = user_data.get("access_token")
        self.parent_window = parent_window
        
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.dados_relatorio = {}
        
        if not PDF_AVAILABLE:
            self.root.destroy()
            return
        
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """Configurar janela"""
        
        self.root.title("Sistema ERP Primotex - Gerador de Relatórios")
        self.root.geometry("1200x800")
        
        if not self.parent_window:
            self.root.state('zoomed')
        
        self.root.configure(bg='#f8f9fa')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Criar widgets da interface"""
        
        # === BARRA SUPERIOR ===
        self.create_top_bar()
        
        # === CONTAINER PRINCIPAL ===
        main_container = tk.Frame(self.root, bg='#f8f9fa')
        main_container.pack(fill='both', expand=True, padx=15, pady=10)
        
        # === ÁREA ESQUERDA - SELEÇÃO DE RELATÓRIO ===
        left_frame = tk.Frame(main_container, bg='white', relief='raised', bd=1)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        left_frame.configure(width=400)
        left_frame.pack_propagate(False)
        
        self.create_selection_area(left_frame)
        
        # === ÁREA DIREITA - CONFIGURAÇÕES E PREVIEW ===
        right_frame = tk.Frame(main_container, bg='white', relief='raised', bd=1)
        right_frame.pack(side='right', fill='both', expand=True)
        
        self.create_config_area(right_frame)
    
    def create_top_bar(self):
        """Criar barra superior"""
        
        top_frame = tk.Frame(self.root, bg='#1abc9c', height=50)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)
        
        container = tk.Frame(top_frame, bg='#1abc9c')
        container.pack(fill='both', expand=True, padx=20, pady=8)
        
        # Título
        title_label = tk.Label(
            container,
            text="📈 Gerador de Relatórios",
            font=('Arial', 16, 'bold'),
            bg='#1abc9c',
            fg='white'
        )
        title_label.pack(side='left', pady=5)
        
        # Informações do usuário
        user_info = f"👤 Usuário: {self.user_data.get('user', {}).get('username', 'N/A')}"
        user_label = tk.Label(
            container,
            text=user_info,
            font=('Arial', 10),
            bg='#1abc9c',
            fg='#ecf0f1'
        )
        user_label.pack(side='right', pady=5)
    
    def create_selection_area(self, parent):
        """Criar área de seleção de relatórios"""
        
        # === TÍTULO ===
        title_frame = tk.Frame(parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            title_frame,
            text="📋 Tipos de Relatórios",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack()
        
        # === LISTA DE RELATÓRIOS ===
        reports_frame = tk.Frame(parent, bg='white')
        reports_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Scrollbar para a lista
        canvas = tk.Canvas(reports_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(reports_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Criar botões para cada tipo de relatório
        self.selected_template = tk.StringVar()
        for template_key, template_info in TEMPLATES_RELATORIOS.items():
            self.create_report_button(scrollable_frame, template_key, template_info)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === AÇÕES RÁPIDAS ===
        actions_frame = tk.LabelFrame(
            parent,
            text="⚡ Ações Rápidas",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        actions_frame.pack(fill='x', padx=20, pady=20)
        
        # Botão Gerar Todos
        btn_gerar_todos = tk.Button(
            actions_frame,
            text="📊 Gerar Todos os Relatórios",
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=8,
            border=0,
            command=self.gerar_todos_relatorios
        )
        btn_gerar_todos.pack(fill='x', padx=10, pady=10)
        
        # Botão Configurações Avançadas
        btn_config = tk.Button(
            actions_frame,
            text="⚙️ Configurações Avançadas",
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=8,
            border=0,
            command=self.abrir_configuracoes
        )
        btn_config.pack(fill='x', padx=10, pady=(0, 10))
    
    def create_report_button(self, parent, template_key, template_info):
        """Criar botão para um tipo de relatório"""
        
        # Frame do relatório
        report_frame = tk.Frame(parent, bg='#f8f9fa', relief='raised', bd=1)
        report_frame.pack(fill='x', padx=5, pady=5)
        
        # Radiobutton invisível para seleção
        radio = tk.Radiobutton(
            report_frame,
            variable=self.selected_template,
            value=template_key,
            bg='#f8f9fa',
            command=lambda: self.on_template_selected(template_key)
        )
        radio.pack(side='left', padx=5)
        
        # Ícone e informações
        info_frame = tk.Frame(report_frame, bg='#f8f9fa')
        info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # Linha 1: Ícone + Nome
        title_frame = tk.Frame(info_frame, bg='#f8f9fa')
        title_frame.pack(fill='x')
        
        icon_label = tk.Label(
            title_frame,
            text=template_info["icone"],
            font=('Arial', 16),
            bg='#f8f9fa'
        )
        icon_label.pack(side='left')
        
        name_label = tk.Label(
            title_frame,
            text=template_info["nome"],
            font=('Arial', 12, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        name_label.pack(side='left', padx=(10, 0))
        
        # Linha 2: Descrição
        desc_label = tk.Label(
            info_frame,
            text=template_info["descricao"],
            font=('Arial', 9),
            bg='#f8f9fa',
            fg='#7f8c8d',
            justify='left'
        )
        desc_label.pack(anchor='w', pady=(5, 0))
        
        # Tornar todo o frame clicável
        def select_template(event=None):
            self.selected_template.set(template_key)
            self.on_template_selected(template_key)
        
        report_frame.bind(MOUSE_EVENTS['click'], select_template)
        info_frame.bind(MOUSE_EVENTS['click'], select_template)
        title_frame.bind(MOUSE_EVENTS['click'], select_template)
        icon_label.bind(MOUSE_EVENTS['click'], select_template)
        name_label.bind(MOUSE_EVENTS['click'], select_template)
        desc_label.bind(MOUSE_EVENTS['click'], select_template)
    
    def create_config_area(self, parent):
        """Criar área de configurações"""
        
        # === TÍTULO ===
        title_frame = tk.Frame(parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            title_frame,
            text="⚙️ Configurações do Relatório",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack()
        
        # === CONFIGURAÇÕES ===
        config_frame = tk.LabelFrame(
            parent,
            text="📝 Parâmetros",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        config_frame.pack(fill='x', padx=20, pady=10)
        
        # Período
        tk.Label(
            config_frame,
            text="Período:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).grid(row=0, column=0, sticky='w', padx=10, pady=(10, 5))
        
        periodo_frame = tk.Frame(config_frame, bg='white')
        periodo_frame.grid(row=0, column=1, sticky='w', padx=10, pady=(10, 5))
        
        tk.Label(periodo_frame, text="De:", bg='white').pack(side='left')
        self.data_inicio = tk.Entry(periodo_frame, font=('Arial', 10), width=12)
        self.data_inicio.pack(side='left', padx=(5, 10))
        self.data_inicio.insert(0, (datetime.now() - timedelta(days=30)).strftime('%d/%m/%Y'))
        
        tk.Label(periodo_frame, text="Até:", bg='white').pack(side='left')
        self.data_fim = tk.Entry(periodo_frame, font=('Arial', 10), width=12)
        self.data_fim.pack(side='left', padx=5)
        self.data_fim.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        # Formato de saída
        tk.Label(
            config_frame,
            text="Formato:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        self.combo_formato = ttk.Combobox(
            config_frame,
            values=["PDF", "PDF + Excel", "Apenas Excel"],
            state="readonly",
            font=('Arial', 10)
        )
        self.combo_formato.set("PDF")
        self.combo_formato.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        # Orientação
        tk.Label(
            config_frame,
            text="Orientação:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        
        self.combo_orientacao = ttk.Combobox(
            config_frame,
            values=["Retrato", "Paisagem"],
            state="readonly",
            font=('Arial', 10)
        )
        self.combo_orientacao.set("Retrato")
        self.combo_orientacao.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        # Incluir gráficos
        self.var_graficos = tk.BooleanVar(value=True)
        check_graficos = tk.Checkbutton(
            config_frame,
            text="Incluir gráficos e estatísticas",
            variable=self.var_graficos,
            font=('Arial', 10),
            bg='white'
        )
        check_graficos.grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # === PREVIEW ===
        preview_frame = tk.LabelFrame(
            parent,
            text="👁️ Preview",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        preview_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.text_preview = tk.Text(
            preview_frame,
            font=('Courier', 9),
            height=15,
            bg='#f8f9fa',
            wrap='word',
            state='disabled'
        )
        
        # Scrollbar para o preview
        scroll_preview = ttk.Scrollbar(preview_frame, orient="vertical", command=self.text_preview.yview)
        self.text_preview.configure(yscrollcommand=scroll_preview.set)
        
        self.text_preview.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scroll_preview.pack(side='right', fill='y', pady=10)
        
        # === BOTÕES DE AÇÃO ===
        self.create_action_buttons(parent)
    
    def create_action_buttons(self, parent):
        """Criar botões de ação"""
        
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        # Botão Preview
        btn_preview = tk.Button(
            buttons_frame,
            text="👁️ Gerar Preview",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=8,
            border=0,
            command=self.gerar_preview
        )
        btn_preview.pack(side='left', padx=(0, 10))
        
        # Botão Gerar
        btn_gerar = tk.Button(
            buttons_frame,
            text="📄 Gerar Relatório",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            border=0,
            command=self.gerar_relatorio
        )
        btn_gerar.pack(side='right')
        
        # Botão Configurar Template
        btn_template = tk.Button(
            buttons_frame,
            text="🎨 Configurar Template",
            font=('Arial', 10),
            bg='#9b59b6',
            fg='white',
            padx=15,
            pady=8,
            border=0,
            command=self.configurar_template
        )
        btn_template.pack(side='right', padx=(0, 10))
    
    # =======================================
    # MÉTODOS DE CONTROLE
    # =======================================
    
    def on_template_selected(self, template_key):
        """Callback quando template é selecionado"""
        template_info = TEMPLATES_RELATORIOS.get(template_key, {})
        
        # Atualizar preview
        preview_text = f"""RELATÓRIO SELECIONADO: {template_info.get('nome', 'N/A')}
{'-' * 50}

Descrição: {template_info.get('descricao', 'N/A')}
Template: {template_key}

Configurações Atuais:
• Período: {self.data_inicio.get()} até {self.data_fim.get()}
• Formato: {self.combo_formato.get()}
• Orientação: {self.combo_orientacao.get()}
• Gráficos: {'Sim' if self.var_graficos.get() else 'Não'}

Status: Pronto para gerar
"""
        
        self.text_preview.config(state='normal')
        self.text_preview.delete('1.0', tk.END)
        self.text_preview.insert('1.0', preview_text)
        self.text_preview.config(state='disabled')
    
    def gerar_preview(self):
        """Gerar preview do relatório"""
        
        template_key = self.selected_template.get()
        if not template_key:
            messagebox.showwarning("Aviso", "Selecione um tipo de relatório!")
            return
        
        def generate():
            try:
                # Simular carregamento de dados
                self.root.after(0, lambda: self.atualizar_preview("Carregando dados..."))
                
                # Mock de dados baseado no template
                dados = self.gerar_dados_mock(template_key)
                
                # Gerar preview
                preview = self.criar_preview_texto(template_key, dados)
                
                self.root.after(0, lambda: self.atualizar_preview(preview))
                
            except Exception as e:
                error_msg = f"Erro ao gerar preview: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def gerar_relatorio(self):
        """Gerar relatório final"""
        
        template_key = self.selected_template.get()
        if not template_key:
            messagebox.showwarning("Aviso", "Selecione um tipo de relatório!")
            return
        
        # Dialog para salvar arquivo
        filename = filedialog.asksaveasfilename(
            title="Salvar Relatório",
            defaultextension=".pdf",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return
        
        def generate():
            try:
                # Carregar dados
                dados = self.gerar_dados_mock(template_key)
                
                # Gerar PDF
                self.root.after(0, lambda: self.atualizar_preview("Gerando PDF..."))
                
                self.criar_pdf(template_key, dados, filename)
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso",
                    f"Relatório gerado com sucesso!\n\nArquivo: {filename}"
                ))
                
            except Exception as e:
                error_msg = f"Erro ao gerar relatório: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def gerar_todos_relatorios(self):
        """Gerar todos os relatórios disponíveis"""
        
        # Dialog para escolher pasta
        pasta = filedialog.askdirectory(title="Escolha a pasta para salvar os relatórios")
        if not pasta:
            return
        
        def generate_all():
            try:
                total = len(TEMPLATES_RELATORIOS)
                
                for i, template_key in enumerate(TEMPLATES_RELATORIOS.keys()):
                    template_info = TEMPLATES_RELATORIOS[template_key]
                    
                    # Atualizar status
                    status = f"Gerando {template_info['nome']} ({i+1}/{total})..."
                    self.root.after(0, lambda s=status: self.atualizar_preview(s))
                    
                    # Gerar dados e PDF
                    dados = self.gerar_dados_mock(template_key)
                    filename = os.path.join(pasta, f"{template_key}_relatorio.pdf")
                    self.criar_pdf(template_key, dados, filename)
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso",
                    f"Todos os relatórios foram gerados em:\n{pasta}"
                ))
                
            except Exception as e:
                error_msg = f"Erro na geração em lote: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
        
        thread = threading.Thread(target=generate_all, daemon=True)
        thread.start()
    
    def configurar_template(self):
        """Abrir configurações avançadas do template"""
        messagebox.showinfo(
            "Configurar Template",
            "Funcionalidade de configuração de templates será implementada!\n\n"
            "Permitirá personalizar:\n"
            "• Cores e fontes\n"
            "• Logotipo da empresa\n"
            "• Campos personalizados\n"
            "• Layout das páginas"
        )
    
    def abrir_configuracoes(self):
        """Abrir configurações avançadas"""
        ConfiguracoesDialog(self.root)
    
    # =======================================
    # MÉTODOS DE GERAÇÃO DE DADOS MOCK
    # =======================================
    
    def gerar_dados_mock(self, template_key):
        """Gerar dados mock para teste"""
        
        if template_key == "clientes":
            return {
                "total_clientes": 150,
                "clientes": [
                    {"nome": "João Silva", "email": "joao@email.com", "telefone": "(11) 99999-0001"},
                    {"nome": "Maria Santos", "email": "maria@email.com", "telefone": "(11) 99999-0002"},
                    {"nome": "Pedro Costa", "email": "pedro@email.com", "telefone": "(11) 99999-0003"}
                ]
            }
        elif template_key == "produtos":
            return {
                "total_produtos": 85,
                "produtos": [
                    {"codigo": "FOR001", "nome": "Forro PVC Branco 20cm", "categoria": "Forros", "preco": 25.00},
                    {"codigo": "DIV001", "nome": "Divisória Eucatex 2,70m", "categoria": "Divisórias", "preco": 250.00},
                    {"codigo": "PER001", "nome": "Perfil Alumínio 30mm", "categoria": "Perfis", "preco": 18.00}
                ]
            }
        elif template_key == "estoque":
            return {
                "total_itens": 85,
                "valor_total": 45000.00,
                "estoque": [
                    {"codigo": "FOR001", "nome": "Forro PVC Branco 20cm", "quantidade": 500, "valor_unitario": 25.00},
                    {"codigo": "DIV001", "nome": "Divisória Eucatex 2,70m", "quantidade": 25, "valor_unitario": 250.00},
                    {"codigo": "PER001", "nome": "Perfil Alumínio 30mm", "quantidade": 200, "valor_unitario": 18.00}
                ]
            }
        else:
            return {"dados": "Mock data para " + template_key}
    
    def criar_preview_texto(self, template_key, dados):
        """Criar texto de preview"""
        
        template_info = TEMPLATES_RELATORIOS.get(template_key, {})
        
        preview = f"""PRIMOTEX FORROS E DIVISÓRIAS EIRELLI
{template_info.get('nome', 'Relatório')}
Período: {self.data_inicio.get()} a {self.data_fim.get()}
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{'=' * 60}

"""
        
        if template_key == "clientes":
            preview += f"""RESUMO:
• Total de Clientes: {dados['total_clientes']}
• Clientes Ativos: {dados['total_clientes'] - 5}
• Novos este mês: 12

AMOSTRA DE CLIENTES:
"""
            for cliente in dados['clientes']:
                preview += f"• {cliente['nome']} - {cliente['email']} - {cliente['telefone']}\n"
        
        elif template_key == "produtos":
            preview += f"""RESUMO:
• Total de Produtos: {dados['total_produtos']}
• Categorias: 8
• Produtos Ativos: {dados['total_produtos'] - 3}

AMOSTRA DE PRODUTOS:
"""
            for produto in dados['produtos']:
                preview += f"• [{produto['codigo']}] {produto['nome']} - R$ {produto['preco']:.2f}\n".replace('.', ',')
        
        elif template_key == "estoque":
            preview += f"""RESUMO:
• Total de Itens: {dados['total_itens']}
• Valor Total: R$ {dados['valor_total']:,.2f}
• Itens com Estoque Baixo: 5

AMOSTRA DO ESTOQUE:
"""
            for item in dados['estoque']:
                valor_total = item['quantidade'] * item['valor_unitario']
                preview += f"• [{item['codigo']}] {item['nome']}\n"
                preview += f"  Qtd: {item['quantidade']} | Valor Unit: R$ {item['valor_unitario']:.2f} | Total: R$ {valor_total:.2f}\n".replace('.', ',')
        
        preview += f"\n\n{'=' * 60}\nRelatório gerado pelo Sistema ERP Primotex"
        
        return preview
    
    def criar_pdf(self, template_key, dados, filename):
        """Criar arquivo PDF"""
        
        # Configurar documento
        if self.combo_orientacao.get() == "Paisagem":
            pagesize = (A4[1], A4[0])  # Landscape
        else:
            pagesize = A4
        
        doc = SimpleDocTemplate(filename, pagesize=pagesize)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Cabeçalho
        story.append(Paragraph("PRIMOTEX FORROS E DIVISÓRIAS EIRELLI", title_style))
        story.append(Paragraph(TEMPLATES_RELATORIOS[template_key]['nome'], styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Informações do relatório
        info_text = f"""
        <b>Período:</b> {self.data_inicio.get()} a {self.data_fim.get()}<br/>
        <b>Gerado em:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br/>
        <b>Usuário:</b> {self.user_data.get('user', {}).get('username', 'N/A')}
        """
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 24))
        
        # Conteúdo específico do template
        if template_key == "clientes":
            self.adicionar_conteudo_clientes(story, dados, styles)
        elif template_key == "produtos":
            self.adicionar_conteudo_produtos(story, dados, styles)
        elif template_key == "estoque":
            self.adicionar_conteudo_estoque(story, dados, styles)
        else:
            story.append(Paragraph(f"Conteúdo do relatório {template_key} será implementado.", styles['Normal']))
        
        # Rodapé
        story.append(Spacer(1, 24))
        story.append(Paragraph("Relatório gerado pelo Sistema ERP Primotex", styles['Normal']))
        
        # Gerar PDF
        doc.build(story)
    
    def adicionar_conteudo_clientes(self, story, dados, styles):
        """Adicionar conteúdo específico de clientes"""
        
        story.append(Paragraph("RESUMO DE CLIENTES", styles['Heading3']))
        
        resumo_text = f"""
        <b>Total de Clientes:</b> {dados['total_clientes']}<br/>
        <b>Clientes Ativos:</b> {dados['total_clientes'] - 5}<br/>
        <b>Novos este mês:</b> 12
        """
        story.append(Paragraph(resumo_text, styles['Normal']))
        story.append(Spacer(1, 18))
        
        # Tabela de clientes
        data = [['Nome', 'Email', 'Telefone']]
        for cliente in dados['clientes']:
            data.append([cliente['nome'], cliente['email'], cliente['telefone']])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    
    def adicionar_conteudo_produtos(self, story, dados, styles):
        """Adicionar conteúdo específico de produtos"""
        
        story.append(Paragraph("CATÁLOGO DE PRODUTOS", styles['Heading3']))
        
        # Tabela de produtos
        data = [['Código', 'Nome', 'Categoria', 'Preço (R$)']]
        for produto in dados['produtos']:
            preco_formatado = f"{produto['preco']:.2f}".replace('.', ',')
            data.append([produto['codigo'], produto['nome'], produto['categoria'], preco_formatado])
        
        table = Table(data, colWidths=[1*inch, 3*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    
    def adicionar_conteudo_estoque(self, story, dados, styles):
        """Adicionar conteúdo específico de estoque"""
        
        story.append(Paragraph("RELATÓRIO DE ESTOQUE", styles['Heading3']))
        
        resumo_text = f"""
        <b>Total de Itens:</b> {dados['total_itens']}<br/>
        <b>Valor Total:</b> R$ {dados['valor_total']:,.2f}
        """.replace('.', ',')
        story.append(Paragraph(resumo_text, styles['Normal']))
        story.append(Spacer(1, 18))
        
        # Tabela de estoque
        data = [['Código', 'Produto', 'Quantidade', 'Valor Unit. (R$)', 'Total (R$)']]
        for item in dados['estoque']:
            valor_total = item['quantidade'] * item['valor_unitario']
            data.append([
                item['codigo'], 
                item['nome'], 
                str(item['quantidade']),
                f"{item['valor_unitario']:.2f}".replace('.', ','),
                f"{valor_total:.2f}".replace('.', ',')
            ])
        
        table = Table(data, colWidths=[0.8*inch, 2.5*inch, 0.8*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    
    def atualizar_preview(self, texto):
        """Atualizar área de preview"""
        self.text_preview.config(state='normal')
        self.text_preview.delete('1.0', tk.END)
        self.text_preview.insert('1.0', texto)
        self.text_preview.config(state='disabled')
    
    def on_closing(self):
        """Tratar fechamento da janela"""
        if messagebox.askyesno("Fechar", "Deseja fechar o gerador de relatórios?"):
            self.root.destroy()
    
    def run(self):
        """Executar a interface"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            try:
                self.root.destroy()
            except tk.TclError:
                pass

# =======================================
# DIALOG DE CONFIGURAÇÕES
# =======================================

class ConfiguracoesDialog:
    """Dialog para configurações avançadas"""
    
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configurações Avançadas")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Criar widgets do dialog"""
        
        # Título
        title = tk.Label(
            self.dialog,
            text="⚙️ Configurações Avançadas",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title.pack(pady=20)
        
        # Configurações
        config_frame = tk.LabelFrame(
            self.dialog,
            text="Configurações Gerais:",
            font=('Arial', 12, 'bold')
        )
        config_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Logo da empresa
        tk.Label(config_frame, text="Logo da Empresa:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        logo_frame = tk.Frame(config_frame)
        logo_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Entry(logo_frame, width=40).pack(side='left', padx=(0, 10))
        tk.Button(logo_frame, text="Procurar", bg='#3498db', fg='white', border=0).pack(side='left')
        
        # Formato padrão
        tk.Label(config_frame, text="Formato Padrão:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        ttk.Combobox(config_frame, values=["PDF", "Excel", "Word"], state="readonly").pack(anchor='w', padx=10, pady=5)
        
        # Botões
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(
            btn_frame,
            text="💾 Salvar",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=5,
            border=0,
            command=self.salvar_config
        ).pack(side='right', padx=(10, 0))
        
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.dialog.destroy
        ).pack(side='right')
    
    def salvar_config(self):
        """Salvar configurações"""
        messagebox.showinfo("Salvar", "Configurações salvas com sucesso!")
        self.dialog.destroy()

# =======================================
# FUNÇÃO PRINCIPAL
# =======================================

def main():
    """Teste da interface de relatórios"""
    
    user_data = {
        "access_token": "mock_token",
        "user": {
            "username": "admin",
            "nome_completo": "Administrador"
        }
    }
    
    app = RelatoriosWindow(user_data)
    app.run()

if __name__ == "__main__":
    main()