"""
SISTEMA ERP PRIMOTEX - GERADOR DE CÓDIGOS DE BARRAS
===================================================

Sistema completo para geração de códigos de barras para produtos
com múltiplos formatos e funcionalidades de visualização e impressão.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import Dict, Any, Optional, List
import os
import tempfile
from datetime import datetime
from PIL import Image, ImageTk
import io

# Importações para códigos de barras
try:
    import barcode
    from barcode import EAN13, EAN8, Code128, Code39, UPCA
    from barcode.writer import ImageWriter, SVGWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False
    messagebox.showerror(
        "Erro",
        "Biblioteca python-barcode não encontrada!\n\nInstale com: pip install python-barcode[images]"
    )

# =======================================
# CONFIGURAÇÕES
# =======================================

API_BASE_URL = "http://127.0.0.1:8002"

# Formatos de código de barras suportados
BARCODE_FORMATS = {
    "EAN13": {"class": EAN13, "digits": 13, "description": "European Article Number (13 dígitos)"},
    "EAN8": {"class": EAN8, "digits": 8, "description": "European Article Number (8 dígitos)"},
    "Code128": {"class": Code128, "digits": "variável", "description": "Code 128 (alfanumérico)"},
    "Code39": {"class": Code39, "digits": "variável", "description": "Code 39 (alfanumérico)"},
    "UPCA": {"class": UPCA, "digits": 12, "description": "Universal Product Code (12 dígitos)"}
}

# =======================================
# CLASSE GERADOR DE CÓDIGOS DE BARRAS
# =======================================

class CodigoBarrasWindow:
    """Sistema de geração de códigos de barras"""
    
    def __init__(self, user_data: Dict[str, Any], parent_window=None):
        self.user_data = user_data
        self.token = user_data.get("access_token")
        self.parent_window = parent_window
        
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.produtos_data = []
        self.produto_selecionado = None
        self.codigo_barras_atual = None
        self.imagem_barcode = None
        
        if not BARCODE_AVAILABLE:
            self.root.destroy()
            return
        
        self.setup_window()
        self.create_widgets()
        self.carregar_produtos()
    
    def setup_window(self):
        """Configurar janela"""
        
        self.root.title("Sistema ERP Primotex - Gerador de Códigos de Barras")
        self.root.geometry("1400x900")
        
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
        
        # === ÁREA ESQUERDA - SELEÇÃO E CONFIGURAÇÃO ===
        left_frame = tk.Frame(main_container, bg='white', relief='raised', bd=1)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        left_frame.configure(width=450)
        left_frame.pack_propagate(False)
        
        self.create_selection_area(left_frame)
        
        # === ÁREA DIREITA - VISUALIZAÇÃO E AÇÕES ===
        right_frame = tk.Frame(main_container, bg='white', relief='raised', bd=1)
        right_frame.pack(side='right', fill='both', expand=True)
        
        self.create_preview_area(right_frame)
    
    def create_top_bar(self):
        """Criar barra superior"""
        
        top_frame = tk.Frame(self.root, bg='#9b59b6', height=50)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)
        
        container = tk.Frame(top_frame, bg='#9b59b6')
        container.pack(fill='both', expand=True, padx=20, pady=8)
        
        # Título
        title_label = tk.Label(
            container,
            text="📊 Gerador de Códigos de Barras",
            font=('Arial', 16, 'bold'),
            bg='#9b59b6',
            fg='white'
        )
        title_label.pack(side='left', pady=5)
        
        # Informações do usuário
        user_info = f"👤 Usuário: {self.user_data.get('user', {}).get('username', 'N/A')}"
        user_label = tk.Label(
            container,
            text=user_info,
            font=('Arial', 10),
            bg='#9b59b6',
            fg='#ecf0f1'
        )
        user_label.pack(side='right', pady=5)
    
    def create_selection_area(self, parent):
        """Criar área de seleção e configuração"""
        
        # === TÍTULO ===
        title_frame = tk.Frame(parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            title_frame,
            text="🔧 Configuração do Código de Barras",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack()
        
        # === SELEÇÃO DE PRODUTO ===
        produto_frame = tk.LabelFrame(
            parent,
            text="📦 Seleção de Produto",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        produto_frame.pack(fill='x', padx=20, pady=10)
        
        # Lista de produtos
        tk.Label(
            produto_frame,
            text="Produto:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.combo_produto = ttk.Combobox(
            produto_frame,
            font=('Arial', 10),
            state="readonly",
            width=40
        )
        self.combo_produto.pack(fill='x', padx=10, pady=(0, 5))
        self.combo_produto.bind('<<ComboboxSelected>>', self.on_produto_selecionado)
        
        # Informações do produto selecionado
        self.info_frame = tk.Frame(produto_frame, bg='white')
        self.info_frame.pack(fill='x', padx=10, pady=10)
        
        self.label_info_produto = tk.Label(
            self.info_frame,
            text="Selecione um produto para ver as informações",
            font=('Arial', 9),
            bg='white',
            fg='#7f8c8d',
            justify='left'
        )
        self.label_info_produto.pack(anchor='w')
        
        # === CONFIGURAÇÕES DO CÓDIGO ===
        config_frame = tk.LabelFrame(
            parent,
            text="⚙️ Configurações",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        config_frame.pack(fill='x', padx=20, pady=10)
        
        # Formato do código de barras
        tk.Label(
            config_frame,
            text="Formato:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.combo_formato = ttk.Combobox(
            config_frame,
            values=list(BARCODE_FORMATS.keys()),
            state="readonly",
            font=('Arial', 10)
        )
        self.combo_formato.set("Code128")
        self.combo_formato.pack(fill='x', padx=10, pady=(0, 5))
        self.combo_formato.bind('<<ComboboxSelected>>', self.on_formato_changed)
        
        # Descrição do formato
        self.label_formato_desc = tk.Label(
            config_frame,
            text=BARCODE_FORMATS["Code128"]["description"],
            font=('Arial', 9),
            bg='white',
            fg='#7f8c8d'
        )
        self.label_formato_desc.pack(anchor='w', padx=10, pady=(0, 10))
        
        # Código personalizado
        tk.Label(
            config_frame,
            text="Código:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.var_codigo_custom = tk.StringVar()
        self.entry_codigo = tk.Entry(
            config_frame,
            textvariable=self.var_codigo_custom,
            font=('Arial', 10),
            bg='#f8f9fa'
        )
        self.entry_codigo.pack(fill='x', padx=10, pady=(0, 5))
        self.entry_codigo.bind('<KeyRelease>', self.on_codigo_changed)
        
        # Texto adicional
        tk.Label(
            config_frame,
            text="Texto Adicional:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.var_texto_adicional = tk.StringVar()
        self.entry_texto = tk.Entry(
            config_frame,
            textvariable=self.var_texto_adicional,
            font=('Arial', 10),
            bg='#f8f9fa'
        )
        self.entry_texto.pack(fill='x', padx=10, pady=(0, 15))
        
        # === OPÇÕES DE TAMANHO ===
        size_frame = tk.LabelFrame(
            parent,
            text="📏 Dimensões",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        size_frame.pack(fill='x', padx=20, pady=10)
        
        # Tamanho
        tk.Label(
            size_frame,
            text="Tamanho:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.combo_tamanho = ttk.Combobox(
            size_frame,
            values=["Pequeno", "Médio", "Grande", "Extra Grande"],
            state="readonly",
            font=('Arial', 10)
        )
        self.combo_tamanho.set("Médio")
        self.combo_tamanho.pack(fill='x', padx=10, pady=(0, 15))
        
        # === BOTÕES DE AÇÃO ===
        self.create_action_buttons(parent)
    
    def create_action_buttons(self, parent):
        """Criar botões de ação"""
        
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        # Botão Gerar
        self.btn_gerar = tk.Button(
            buttons_frame,
            text="🔄 Gerar Código",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            border=0,
            command=self.gerar_codigo_barras
        )
        self.btn_gerar.pack(fill='x', pady=(0, 10))
        
        # Botão Salvar
        self.btn_salvar = tk.Button(
            buttons_frame,
            text="💾 Salvar Imagem",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8,
            border=0,
            state='disabled',
            command=self.salvar_imagem
        )
        self.btn_salvar.pack(fill='x', pady=(0, 5))
        
        # Botão Imprimir
        self.btn_imprimir = tk.Button(
            buttons_frame,
            text="🖨️ Imprimir",
            font=('Arial', 10),
            bg='#e67e22',
            fg='white',
            padx=20,
            pady=8,
            border=0,
            state='disabled',
            command=self.imprimir_codigo
        )
        self.btn_imprimir.pack(fill='x', pady=(0, 5))
        
        # Botão Lote
        self.btn_lote = tk.Button(
            buttons_frame,
            text="📋 Gerar em Lote",
            font=('Arial', 10),
            bg='#9b59b6',
            fg='white',
            padx=20,
            pady=8,
            border=0,
            command=self.gerar_lote
        )
        self.btn_lote.pack(fill='x')
    
    def create_preview_area(self, parent):
        """Criar área de visualização"""
        
        # === TÍTULO ===
        title_frame = tk.Frame(parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            title_frame,
            text="👁️ Visualização do Código de Barras",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack()
        
        # === ÁREA DE PREVIEW ===
        preview_frame = tk.Frame(parent, bg='#f8f9fa', relief='sunken', bd=2)
        preview_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Label para a imagem do código de barras
        self.label_preview = tk.Label(
            preview_frame,
            text="📊\n\nClique em 'Gerar Código' para visualizar",
            font=('Arial', 14),
            bg='#f8f9fa',
            fg='#7f8c8d',
            justify='center'
        )
        self.label_preview.pack(expand=True)
        
        # === INFORMAÇÕES DO CÓDIGO ===
        info_frame = tk.LabelFrame(
            parent,
            text="ℹ️ Informações do Código",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        info_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        self.text_info = tk.Text(
            info_frame,
            font=('Arial', 9),
            height=8,
            bg='#f8f9fa',
            wrap='word',
            state='disabled'
        )
        self.text_info.pack(fill='x', padx=10, pady=10)
    
    # =======================================
    # MÉTODOS DE CONTROLE
    # =======================================
    
    def on_produto_selecionado(self, event=None):
        """Callback quando produto é selecionado"""
        produto_nome = self.combo_produto.get()
        
        # Encontrar produto
        self.produto_selecionado = None
        for produto in self.produtos_data:
            if produto.get('nome') == produto_nome:
                self.produto_selecionado = produto
                break
        
        if self.produto_selecionado:
            # Atualizar informações
            info_text = (
                f"Código: {self.produto_selecionado.get('codigo', 'N/A')}\n"
                f"Categoria: {self.produto_selecionado.get('categoria', 'N/A')}\n"
                f"Preço: R$ {self.produto_selecionado.get('preco_venda', 0):.2f}".replace('.', ',')
            )
            self.label_info_produto.config(text=info_text)
            
            # Sugerir código
            codigo_produto = self.produto_selecionado.get('codigo', '')
            if codigo_produto:
                self.var_codigo_custom.set(codigo_produto)
            
            # Sugerir texto adicional
            nome_produto = self.produto_selecionado.get('nome', '')[:30]
            self.var_texto_adicional.set(nome_produto)
    
    def on_formato_changed(self, event=None):
        """Callback quando formato é alterado"""
        formato = self.combo_formato.get()
        if formato in BARCODE_FORMATS:
            desc = BARCODE_FORMATS[formato]["description"]
            self.label_formato_desc.config(text=desc)
    
    def on_codigo_changed(self, event=None):
        """Callback quando código é alterado"""
        # Validar código conforme formato selecionado
        pass
    
    # =======================================
    # MÉTODOS DE GERAÇÃO
    # =======================================
    
    def gerar_codigo_barras(self):
        """Gerar código de barras"""
        
        def generate():
            try:
                formato = self.combo_formato.get()
                codigo = self.var_codigo_custom.get().strip()
                texto_adicional = self.var_texto_adicional.get().strip()
                
                if not codigo:
                    self.root.after(0, lambda: messagebox.showerror("Erro", "Código é obrigatório!"))
                    return
                
                if formato not in BARCODE_FORMATS:
                    self.root.after(0, lambda: messagebox.showerror("Erro", "Formato inválido!"))
                    return
                
                # Configurar escritor de imagem
                writer = ImageWriter()
                
                # Configurar opções baseadas no tamanho
                tamanho = self.combo_tamanho.get()
                if tamanho == "Pequeno":
                    writer.dpi = 200
                    module_width = 0.2
                    module_height = 8.0
                elif tamanho == "Médio":
                    writer.dpi = 300
                    module_width = 0.3
                    module_height = 12.0
                elif tamanho == "Grande":
                    writer.dpi = 400
                    module_width = 0.4
                    module_height = 16.0
                else:  # Extra Grande
                    writer.dpi = 600
                    module_width = 0.6
                    module_height = 20.0
                
                # Obter classe do código de barras
                barcode_class = BARCODE_FORMATS[formato]["class"]
                
                # Gerar código de barras
                try:
                    code = barcode_class(codigo, writer=writer)
                    
                    # Gerar imagem em buffer
                    buffer = io.BytesIO()
                    code.write(buffer, options={
                        'module_width': module_width,
                        'module_height': module_height,
                        'text_distance': 5.0,
                        'quiet_zone': 6.5
                    })
                    
                    # Converter para imagem PIL
                    buffer.seek(0)
                    pil_image = Image.open(buffer)
                    
                    # Redimensionar para visualização se necessário
                    display_width = 600
                    aspect_ratio = pil_image.height / pil_image.width
                    display_height = int(display_width * aspect_ratio)
                    
                    if pil_image.width > display_width:
                        pil_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
                    
                    # Converter para PhotoImage
                    self.imagem_barcode = pil_image
                    photo = ImageTk.PhotoImage(pil_image)
                    
                    # Atualizar interface na thread principal
                    self.root.after(0, lambda: self.atualizar_preview(photo, codigo, formato, texto_adicional))
                    
                except Exception as e:
                    error_msg = f"Erro ao gerar código: {str(e)}"
                    self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
                
            except Exception as e:
                error_msg = f"Erro na geração: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
        
        # Executar em thread separada
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def atualizar_preview(self, photo, codigo, formato, texto_adicional):
        """Atualizar preview do código de barras"""
        
        # Atualizar imagem
        self.label_preview.config(image=photo, text="")
        self.label_preview.image = photo  # Manter referência
        
        # Atualizar informações
        info_text = f"""Código Gerado: {codigo}
Formato: {formato}
Texto Adicional: {texto_adicional}
Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Produto: {self.produto_selecionado.get('nome', 'N/A') if self.produto_selecionado else 'Não selecionado'}
Categoria: {self.produto_selecionado.get('categoria', 'N/A') if self.produto_selecionado else 'N/A'}

Status: ✅ Código gerado com sucesso!
"""
        
        self.text_info.config(state='normal')
        self.text_info.delete('1.0', tk.END)
        self.text_info.insert('1.0', info_text)
        self.text_info.config(state='disabled')
        
        # Habilitar botões
        self.btn_salvar.config(state='normal')
        self.btn_imprimir.config(state='normal')
    
    def salvar_imagem(self):
        """Salvar imagem do código de barras"""
        
        if not self.imagem_barcode:
            messagebox.showerror("Erro", "Nenhum código de barras gerado!")
            return
        
        # Dialog para salvar arquivo
        filename = filedialog.asksaveasfilename(
            title="Salvar Código de Barras",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                self.imagem_barcode.save(filename)
                messagebox.showinfo("Sucesso", f"Código de barras salvo em:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{str(e)}")
    
    def imprimir_codigo(self):
        """Imprimir código de barras"""
        
        if not self.imagem_barcode:
            messagebox.showerror("Erro", "Nenhum código de barras gerado!")
            return
        
        # Por enquanto, apenas uma mensagem - funcionalidade completa seria implementada posteriormente
        messagebox.showinfo(
            "Imprimir",
            "Funcionalidade de impressão será implementada!\n\n"
            "Por enquanto, use 'Salvar Imagem' e imprima pela aplicação de imagens do sistema."
        )
    
    def gerar_lote(self):
        """Gerar códigos de barras em lote"""
        LoteDialog(self.root, self.produtos_data, self.gerar_lote_callback)
    
    def gerar_lote_callback(self, produtos_selecionados, configuracoes):
        """Callback para geração em lote"""
        
        # Validar
        if not produtos_selecionados:
            messagebox.showerror("Erro", "Selecione pelo menos um produto!")
            return
        
        # Dialog para escolher pasta
        pasta = filedialog.askdirectory(title="Escolha a pasta para salvar os códigos")
        if not pasta:
            return
        
        def generate_batch():
            try:
                total = len(produtos_selecionados)
                for i, produto in enumerate(produtos_selecionados):
                    # Configurar código
                    codigo = produto.get('codigo', f'PROD{produto.get("id", "")}')
                    nome = produto.get('nome', 'Produto')[:30]
                    
                    # Gerar código de barras
                    formato = configuracoes.get('formato', 'Code128')
                    barcode_class = BARCODE_FORMATS[formato]["class"]
                    writer = ImageWriter()
                    
                    code = barcode_class(codigo, writer=writer)
                    
                    # Salvar arquivo
                    filename = os.path.join(pasta, f"{codigo}_{nome.replace('/', '_')}")
                    code.save(filename)
                    
                    # Atualizar progresso
                    progress = int((i + 1) / total * 100)
                    self.root.after(0, lambda p=progress: self.atualizar_progresso_lote(p))
                
                # Finalizar
                self.root.after(0, lambda: messagebox.showinfo(
                    "Sucesso", 
                    f"Lote de {total} códigos gerado com sucesso em:\n{pasta}"
                ))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erro", 
                    f"Erro na geração em lote:\n{str(e)}"
                ))
        
        # Executar em thread
        thread = threading.Thread(target=generate_batch, daemon=True)
        thread.start()
    
    def atualizar_progresso_lote(self, progress):
        """Atualizar progresso da geração em lote"""
        # Aqui seria implementada uma barra de progresso
        pass
    
    # =======================================
    # MÉTODOS DE API (MOCK)
    # =======================================
    
    def carregar_produtos(self):
        """Carregar lista de produtos"""
        
        def load_data():
            try:
                # Mock data - mesmos produtos do módulo de produtos
                self.produtos_data = [
                    {
                        "id": 1,
                        "codigo": "FOR001",
                        "nome": "Forro PVC Branco 20cm",
                        "categoria": "Forros",
                        "preco_venda": 25.00
                    },
                    {
                        "id": 2,
                        "codigo": "DIV001",
                        "nome": "Divisória Eucatex 2,70m",
                        "categoria": "Divisórias",
                        "preco_venda": 250.00
                    },
                    {
                        "id": 3,
                        "codigo": "PER001",
                        "nome": "Perfil Alumínio 30mm",
                        "categoria": "Perfis",
                        "preco_venda": 18.00
                    },
                    {
                        "id": 4,
                        "codigo": "PAR001",
                        "nome": "Parafuso Rosca Soberba 3x25",
                        "categoria": "Parafusos",
                        "preco_venda": 0.12
                    }
                ]
                
                # Atualizar combobox na thread principal
                produtos_nomes = [p['nome'] for p in self.produtos_data]
                self.root.after(0, lambda: self.combo_produto.configure(values=produtos_nomes))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erro",
                    f"Erro ao carregar produtos: {str(e)}"
                ))
        
        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()
    
    def on_closing(self):
        """Tratar fechamento da janela"""
        if messagebox.askyesno("Fechar", "Deseja fechar o gerador de códigos de barras?"):
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
# DIALOG DE GERAÇÃO EM LOTE
# =======================================

class LoteDialog:
    """Dialog para geração de códigos em lote"""
    
    def __init__(self, parent, produtos_data, callback):
        self.parent = parent
        self.produtos_data = produtos_data
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Geração em Lote")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.produtos_selecionados = []
        
        self.create_widgets()
    
    def create_widgets(self):
        """Criar widgets do dialog"""
        
        # Título
        title = tk.Label(
            self.dialog,
            text="📋 Geração de Códigos em Lote",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title.pack(pady=20)
        
        # Lista de produtos
        list_frame = tk.LabelFrame(
            self.dialog,
            text="Selecione os Produtos:",
            font=('Arial', 12, 'bold'),
            bg='white'
        )
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview com checkbox
        self.tree = ttk.Treeview(
            list_frame,
            columns=('codigo', 'nome', 'categoria'),
            show='tree headings',
            height=10
        )
        
        self.tree.heading('#0', text='☑️', width=50)
        self.tree.heading('codigo', text='Código')
        self.tree.heading('nome', text='Nome')
        self.tree.heading('categoria', text='Categoria')
        
        self.tree.column('#0', width=50)
        self.tree.column('codigo', width=100)
        self.tree.column('nome', width=250)
        self.tree.column('categoria', width=120)
        
        # Popular lista
        for produto in self.produtos_data:
            self.tree.insert('', 'end', text='☐', values=(
                produto.get('codigo', ''),
                produto.get('nome', ''),
                produto.get('categoria', '')
            ))
        
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.tree.bind('<Double-1>', self.toggle_selection)
        
        # Configurações
        config_frame = tk.LabelFrame(
            self.dialog,
            text="Configurações:",
            font=('Arial', 12, 'bold'),
            bg='white'
        )
        config_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            config_frame,
            text="Formato:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.combo_formato_lote = ttk.Combobox(
            config_frame,
            values=list(BARCODE_FORMATS.keys()),
            state="readonly"
        )
        self.combo_formato_lote.set("Code128")
        self.combo_formato_lote.grid(row=0, column=1, padx=10, pady=5)
        
        # Botões
        btn_frame = tk.Frame(self.dialog, bg='white')
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        btn_selecionar_todos = tk.Button(
            btn_frame,
            text="☑️ Selecionar Todos",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.selecionar_todos
        )
        btn_selecionar_todos.pack(side='left', padx=(0, 10))
        
        btn_gerar = tk.Button(
            btn_frame,
            text="🔄 Gerar Lote",
            font=('Arial', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=5,
            border=0,
            command=self.gerar_lote
        )
        btn_gerar.pack(side='right', padx=(10, 0))
        
        btn_cancelar = tk.Button(
            btn_frame,
            text="❌ Cancelar",
            font=('Arial', 10),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=5,
            border=0,
            command=self.dialog.destroy
        )
        btn_cancelar.pack(side='right')
    
    def toggle_selection(self, event):
        """Toggle seleção de item"""
        item = self.tree.selection()[0]
        current_text = self.tree.item(item, 'text')
        
        if current_text == '☐':
            self.tree.item(item, text='☑️')
        else:
            self.tree.item(item, text='☐')
    
    def selecionar_todos(self):
        """Selecionar todos os itens"""
        for item in self.tree.get_children():
            self.tree.item(item, text='☑️')
    
    def gerar_lote(self):
        """Executar geração em lote"""
        
        # Coletar produtos selecionados
        produtos_selecionados = []
        for i, item in enumerate(self.tree.get_children()):
            if self.tree.item(item, 'text') == '☑️':
                produtos_selecionados.append(self.produtos_data[i])
        
        if not produtos_selecionados:
            messagebox.showerror("Erro", "Selecione pelo menos um produto!")
            return
        
        # Configurações
        configuracoes = {
            'formato': self.combo_formato_lote.get()
        }
        
        # Chamar callback
        self.callback(produtos_selecionados, configuracoes)
        self.dialog.destroy()

# =======================================
# FUNÇÃO PRINCIPAL
# =======================================

def main():
    """Teste da interface de códigos de barras"""
    
    user_data = {
        "access_token": "mock_token",
        "user": {
            "username": "admin",
            "nome_completo": "Administrador"
        }
    }
    
    app = CodigoBarrasWindow(user_data)
    app.run()

if __name__ == "__main__":
    main()