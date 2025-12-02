"""
SISTEMA ERP PRIMOTEX - CANVAS CROQUI VISUAL
============================================

Interface de desenho técnico para criar croquis de ambientes.
Usado na FASE 1 (Abertura) do fluxo de Ordem de Serviço.

FERRAMENTAS:
- Retângulo (ambiente/cômodo)
- Linha (medidas/divisórias)
- Texto (anotações/medidas)
- Borracha (apagar)
- Upload imagem de fundo (planta existente)
- Zoom in/out
- Pan (arrastar canvas)

OUTPUT:
- PNG (preview visual)
- PDF (integrado em documentos)
- JSON (coordenadas para banco de dados)

Autor: GitHub Copilot
Data: 17/11/2025 - FASE 104 TAREFA 1
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from typing import Optional, List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageTk, ImageFont
import json
from pathlib import Path
from datetime import datetime
import io


class CanvasCroqui(tk.Toplevel):
    """
    Canvas interativo para desenho de croquis técnicos.
    
    Features:
    - Ferramentas de desenho (retângulo, linha, texto)
    - Upload de imagem de fundo
    - Zoom e pan
    - Export PNG/PDF
    - Salvar coordenadas em JSON
    """
    
    # Constantes
    COR_FUNDO = "#ffffff"
    COR_GRID = "#e0e0e0"
    COR_DESENHO = "#007bff"
    COR_TEXTO = "#000000"
    COR_MEDIDA = "#dc3545"
    
    LARGURA_CANVAS = 1000
    ALTURA_CANVAS = 700
    TAMANHO_GRID = 20  # pixels
    
    def __init__(self, parent: tk.Tk, os_id: Optional[int] = None):
        """
        Inicializa canvas de croqui.
        
        Args:
            parent: Janela pai
            os_id: ID da OS (opcional, para carregar croqui existente)
        """
        super().__init__(parent)
        
        self.parent = parent
        self.os_id = os_id
        
        # Configuração da janela
        self.title("🎨 Canvas Croqui - ERP Primotex")
        self.geometry("1200x900")
        self.configure(bg="#f8f9fa")
        
        # Estado do canvas
        self.ferramenta_atual = "retangulo"
        self.cor_desenho = self.COR_DESENHO
        self.espessura_linha = 2
        self.zoom_level = 1.0
        
        # Objetos desenhados (para salvar em JSON)
        self.objetos: List[Dict[str, Any]] = []
        
        # Canvas de desenho (PIL Image)
        self.imagem = Image.new(
            "RGB",
            (self.LARGURA_CANVAS, self.ALTURA_CANVAS),
            self.COR_FUNDO
        )
        self.draw = ImageDraw.Draw(self.imagem)
        
        # Imagem de fundo (planta existente)
        self.imagem_fundo: Optional[Image.Image] = None
        
        # Estado de desenho
        self.desenhando = False
        self.x_inicio: Optional[int] = None
        self.y_inicio: Optional[int] = None
        
        # Criar interface
        self._criar_toolbar()
        self._criar_canvas()
        self._criar_painel_info()
        self._criar_rodape()
        
        # Desenhar grid inicial
        self._desenhar_grid()
        self._atualizar_canvas()
        
        # Carregar croqui existente se OS ID fornecido
        if os_id:
            self._carregar_croqui(os_id)
    
    def _criar_toolbar(self):
        """Cria barra de ferramentas superior"""
        toolbar_frame = tk.Frame(self, bg="#343a40", height=60)
        toolbar_frame.pack(fill=tk.X, side=tk.TOP)
        toolbar_frame.pack_propagate(False)
        
        # Container para botões
        botoes_frame = tk.Frame(toolbar_frame, bg="#343a40")
        botoes_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Ferramentas de desenho
        ferramentas = [
            ("📏 Retângulo", "retangulo", "#28a745"),
            ("📐 Linha", "linha", "#007bff"),
            ("✏️ Texto", "texto", "#6c757d"),
            ("🧹 Borracha", "borracha", "#dc3545")
        ]
        
        self.botoes_ferramentas = {}
        for texto, ferramenta, cor in ferramentas:
            btn = tk.Button(
                botoes_frame,
                text=texto,
                font=("Segoe UI", 10, "bold"),
                bg=cor if ferramenta == self.ferramenta_atual else "#495057",
                fg="white",
                width=12,
                command=lambda f=ferramenta: self._selecionar_ferramenta(f),
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.botoes_ferramentas[ferramenta] = btn
        
        # Separador
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=10
        )
        
        # Ações de arquivo
        acoes_frame = tk.Frame(toolbar_frame, bg="#343a40")
        acoes_frame.pack(side=tk.LEFT, padx=5)
        
        btn_upload = tk.Button(
            acoes_frame,
            text="🖼️ Carregar Fundo",
            font=("Segoe UI", 10),
            bg="#17a2b8",
            fg="white",
            command=self._carregar_fundo,
            cursor="hand2"
        )
        btn_upload.pack(side=tk.LEFT, padx=2)
        
        btn_limpar = tk.Button(
            acoes_frame,
            text="🗑️ Limpar Tudo",
            font=("Segoe UI", 10),
            bg="#ffc107",
            fg="black",
            command=self._limpar_canvas,
            cursor="hand2"
        )
        btn_limpar.pack(side=tk.LEFT, padx=2)
        
        # Separador
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=10
        )
        
        # Controles de cor e espessura
        controles_frame = tk.Frame(toolbar_frame, bg="#343a40")
        controles_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            controles_frame,
            text="Cor:",
            font=("Segoe UI", 9),
            bg="#343a40",
            fg="white"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_cor = tk.Button(
            controles_frame,
            bg=self.cor_desenho,
            width=3,
            command=self._escolher_cor,
            cursor="hand2"
        )
        self.btn_cor.pack(side=tk.LEFT, padx=2)
        
        tk.Label(
            controles_frame,
            text="Espessura:",
            font=("Segoe UI", 9),
            bg="#343a40",
            fg="white"
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        self.spin_espessura = tk.Spinbox(
            controles_frame,
            from_=1,
            to=10,
            width=5,
            textvariable=tk.IntVar(value=self.espessura_linha),
            command=self._atualizar_espessura
        )
        self.spin_espessura.pack(side=tk.LEFT, padx=2)
    
    def _criar_canvas(self):
        """Cria área principal de desenho"""
        # Container com scroll
        container_frame = tk.Frame(self, bg="#dee2e6")
        container_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas tkinter (display)
        self.canvas = tk.Canvas(
            container_frame,
            width=self.LARGURA_CANVAS,
            height=self.ALTURA_CANVAS,
            bg=self.COR_FUNDO,
            cursor="crosshair"
        )
        self.canvas.pack()
        
        # Eventos de mouse
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        
        # Zoom com mouse wheel
        self.canvas.bind("<MouseWheel>", self._on_zoom)
    
    def _criar_painel_info(self):
        """Cria painel lateral de informações"""
        info_frame = tk.Frame(self, bg="#f8f9fa", width=250)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        info_frame.pack_propagate(False)
        
        # Título
        tk.Label(
            info_frame,
            text="ℹ️ Informações",
            font=("Segoe UI", 14, "bold"),
            bg="#f8f9fa"
        ).pack(pady=10)
        
        # Coordenadas do mouse
        self.lbl_coords = tk.Label(
            info_frame,
            text="Posição: (0, 0)",
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            anchor="w"
        )
        self.lbl_coords.pack(fill=tk.X, padx=10, pady=5)
        
        # Zoom
        self.lbl_zoom = tk.Label(
            info_frame,
            text=f"Zoom: {self.zoom_level:.1f}x",
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            anchor="w"
        )
        self.lbl_zoom.pack(fill=tk.X, padx=10, pady=5)
        
        # Objetos desenhados
        self.lbl_objetos = tk.Label(
            info_frame,
            text=f"Objetos: {len(self.objetos)}",
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            anchor="w"
        )
        self.lbl_objetos.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Separator(info_frame, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=10, pady=10
        )
        
        # Atalhos
        tk.Label(
            info_frame,
            text="⌨️ Atalhos",
            font=("Segoe UI", 12, "bold"),
            bg="#f8f9fa"
        ).pack(pady=5)
        
        atalhos_text = (
            "R - Retângulo\n"
            "L - Linha\n"
            "T - Texto\n"
            "B - Borracha\n"
            "Ctrl+Z - Desfazer\n"
            "Ctrl+S - Salvar\n"
            "Scroll - Zoom"
        )
        
        tk.Label(
            info_frame,
            text=atalhos_text,
            font=("Segoe UI", 9),
            bg="#f8f9fa",
            justify=tk.LEFT,
            anchor="w"
        ).pack(fill=tk.X, padx=10, pady=5)
    
    def _criar_rodape(self):
        """Cria rodapé com botões de ação"""
        rodape_frame = tk.Frame(self, bg="#e9ecef", height=70)
        rodape_frame.pack(fill=tk.X, side=tk.BOTTOM)
        rodape_frame.pack_propagate(False)
        
        botoes_frame = tk.Frame(rodape_frame, bg="#e9ecef")
        botoes_frame.pack(expand=True)
        
        # Botão Exportar PNG
        btn_export_png = tk.Button(
            botoes_frame,
            text="📷 Exportar PNG",
            font=("Segoe UI", 12, "bold"),
            bg="#17a2b8",
            fg="white",
            width=15,
            height=2,
            command=self._exportar_png,
            cursor="hand2"
        )
        btn_export_png.pack(side=tk.LEFT, padx=5)
        
        # Botão Exportar PDF
        btn_export_pdf = tk.Button(
            botoes_frame,
            text="📄 Exportar PDF",
            font=("Segoe UI", 12, "bold"),
            bg="#6f42c1",
            fg="white",
            width=15,
            height=2,
            command=self._exportar_pdf,
            cursor="hand2"
        )
        btn_export_pdf.pack(side=tk.LEFT, padx=5)
        
        # Botão Salvar e Fechar
        btn_salvar = tk.Button(
            botoes_frame,
            text="💾 Salvar e Fechar",
            font=("Segoe UI", 12, "bold"),
            bg="#28a745",
            fg="white",
            width=15,
            height=2,
            command=self._salvar_e_fechar,
            cursor="hand2"
        )
        btn_salvar.pack(side=tk.LEFT, padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame,
            text="❌ Cancelar",
            font=("Segoe UI", 12, "bold"),
            bg="#dc3545",
            fg="white",
            width=15,
            height=2,
            command=self.destroy,
            cursor="hand2"
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    def _desenhar_grid(self):
        """Desenha grid de fundo no canvas"""
        for x in range(0, self.LARGURA_CANVAS, self.TAMANHO_GRID):
            self.draw.line(
                [(x, 0), (x, self.ALTURA_CANVAS)],
                fill=self.COR_GRID,
                width=1
            )
        
        for y in range(0, self.ALTURA_CANVAS, self.TAMANHO_GRID):
            self.draw.line(
                [(0, y), (self.LARGURA_CANVAS, y)],
                fill=self.COR_GRID,
                width=1
            )
    
    def _atualizar_canvas(self):
        """Atualiza display do canvas tkinter com imagem PIL"""
        # Converter PIL Image para PhotoImage
        self.photo = ImageTk.PhotoImage(self.imagem)
        
        # Limpar canvas tkinter
        self.canvas.delete("all")
        
        # Desenhar imagem
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
    
    def _selecionar_ferramenta(self, ferramenta: str):
        """Seleciona ferramenta de desenho"""
        self.ferramenta_atual = ferramenta
        
        # Atualizar cores dos botões
        cores = {
            "retangulo": "#28a745",
            "linha": "#007bff",
            "texto": "#6c757d",
            "borracha": "#dc3545"
        }
        
        for nome, btn in self.botoes_ferramentas.items():
            if nome == ferramenta:
                btn.config(bg=cores[nome])
            else:
                btn.config(bg="#495057")
    
    def _escolher_cor(self):
        """Dialog para escolher cor de desenho"""
        cor = colorchooser.askcolor(
            initialcolor=self.cor_desenho,
            title="Escolher Cor"
        )
        
        if cor[1]:  # cor[1] é o hex code
            self.cor_desenho = cor[1]
            self.btn_cor.config(bg=self.cor_desenho)
    
    def _atualizar_espessura(self):
        """Atualiza espessura da linha"""
        try:
            self.espessura_linha = int(self.spin_espessura.get())
        except ValueError:
            self.espessura_linha = 2
    
    def _on_mouse_down(self, event):
        """Evento ao pressionar mouse"""
        self.desenhando = True
        self.x_inicio = event.x
        self.y_inicio = event.y
    
    def _on_mouse_move(self, event):
        """Evento ao mover mouse"""
        # Atualizar coordenadas no painel
        self.lbl_coords.config(text=f"Posição: ({event.x}, {event.y})")
        
        # Desenhar preview se estiver desenhando
        if self.desenhando and self.ferramenta_atual in ["retangulo", "linha"]:
            # Remove preview anterior
            self.canvas.delete("preview")
            
            # Desenha preview baseado na ferramenta
            if self.ferramenta_atual == "retangulo":
                self.canvas.create_rectangle(
                    self.x_inicio, self.y_inicio, event.x, event.y,
                    outline=self.cor_desenho,
                    width=self.espessura_linha,
                    tags="preview",
                    dash=(5, 5)  # Linha tracejada
                )
            elif self.ferramenta_atual == "linha":
                self.canvas.create_line(
                    self.x_inicio, self.y_inicio, event.x, event.y,
                    fill=self.cor_desenho,
                    width=self.espessura_linha,
                    tags="preview",
                    dash=(5, 5)
                )
    
    def _on_mouse_up(self, event):
        """Evento ao soltar mouse"""
        if not self.desenhando:
            return
        
        self.desenhando = False
        
        x_fim = event.x
        y_fim = event.y
        
        # Desenhar conforme ferramenta
        if self.ferramenta_atual == "retangulo":
            self._desenhar_retangulo(
                self.x_inicio, self.y_inicio, x_fim, y_fim
            )
        elif self.ferramenta_atual == "linha":
            self._desenhar_linha(
                self.x_inicio, self.y_inicio, x_fim, y_fim
            )
        elif self.ferramenta_atual == "texto":
            self._desenhar_texto(self.x_inicio, self.y_inicio)
        
        # Atualizar display
        self._atualizar_canvas()
    
    def _on_zoom(self, event):
        """Event de zoom com mouse wheel"""
        # Scroll up = zoom in, scroll down = zoom out
        if event.delta > 0:
            self.zoom_level = min(self.zoom_level * 1.1, 3.0)
        else:
            self.zoom_level = max(self.zoom_level / 1.1, 0.5)
        
        # Atualiza label
        self.lbl_zoom.config(text=f"Zoom: {self.zoom_level:.1f}x")
        
        # Redimensiona canvas
        nova_largura = int(self.LARGURA_CANVAS * self.zoom_level)
        nova_altura = int(self.ALTURA_CANVAS * self.zoom_level)
        
        # Cria nova imagem redimensionada
        imagem_zoom = self.imagem.resize(
            (nova_largura, nova_altura),
            Image.Resampling.LANCZOS
        )
        
        # Atualiza display
        self.photo = ImageTk.PhotoImage(imagem_zoom)
        self.canvas.config(scrollregion=(0, 0, nova_largura, nova_altura))
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
    
    def _desenhar_retangulo(self, x1: int, y1: int, x2: int, y2: int):
        """Desenha retângulo no canvas"""
        self.draw.rectangle(
            [(x1, y1), (x2, y2)],
            outline=self.cor_desenho,
            width=self.espessura_linha
        )
        
        # Salvar objeto
        self.objetos.append({
            "tipo": "retangulo",
            "coords": [x1, y1, x2, y2],
            "cor": self.cor_desenho,
            "espessura": self.espessura_linha
        })
        
        self._atualizar_info()
    
    def _desenhar_linha(self, x1: int, y1: int, x2: int, y2: int):
        """Desenha linha no canvas"""
        self.draw.line(
            [(x1, y1), (x2, y2)],
            fill=self.cor_desenho,
            width=self.espessura_linha
        )
        
        # Salvar objeto
        self.objetos.append({
            "tipo": "linha",
            "coords": [x1, y1, x2, y2],
            "cor": self.cor_desenho,
            "espessura": self.espessura_linha
        })
        
        self._atualizar_info()
    
    def _desenhar_texto(self, x: int, y: int):
        """Abre dialog para adicionar texto"""
        texto = tk.simpledialog.askstring(
            "Adicionar Texto",
            "Digite o texto:",
            parent=self
        )
        
        if texto:
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except OSError:
                font = ImageFont.load_default()
            
            self.draw.text(
                (x, y),
                texto,
                fill=self.cor_desenho,
                font=font
            )
            
            # Salvar objeto
            self.objetos.append({
                "tipo": "texto",
                "coords": [x, y],
                "texto": texto,
                "cor": self.cor_desenho
            })
            
            self._atualizar_canvas()
            self._atualizar_info()
    
    def _carregar_fundo(self):
        """Carrega imagem de fundo (planta existente)"""
        filename = filedialog.askopenfilename(
            title="Selecionar Imagem de Fundo",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp"),
                ("Todos", "*.*")
            ],
            parent=self
        )
        
        if filename:
            try:
                # Carregar e redimensionar imagem
                self.imagem_fundo = Image.open(filename)
                self.imagem_fundo = self.imagem_fundo.resize(
                    (self.LARGURA_CANVAS, self.ALTURA_CANVAS),
                    Image.Resampling.LANCZOS
                )
                
                # Criar nova imagem com fundo
                self.imagem = self.imagem_fundo.copy()
                self.draw = ImageDraw.Draw(self.imagem)
                
                # Redesenhar grid
                self._desenhar_grid()
                
                # Redesenhar objetos
                for obj in self.objetos:
                    self._redesenhar_objeto(obj)
                
                self._atualizar_canvas()
                
                messagebox.showinfo(
                    "Sucesso",
                    "Imagem de fundo carregada!",
                    parent=self
                )
            except Exception as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao carregar imagem: {e}",
                    parent=self
                )
    
    def _redesenhar_objeto(self, obj: Dict[str, Any]):
        """Redesenha um objeto salvo no canvas"""
        if obj["tipo"] == "retangulo":
            self.draw.rectangle(
                [(obj["coords"][0], obj["coords"][1]),
                 (obj["coords"][2], obj["coords"][3])],
                outline=obj["cor"],
                width=obj["espessura"]
            )
        elif obj["tipo"] == "linha":
            self.draw.line(
                [(obj["coords"][0], obj["coords"][1]),
                 (obj["coords"][2], obj["coords"][3])],
                fill=obj["cor"],
                width=obj["espessura"]
            )
        elif obj["tipo"] == "texto":
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except OSError:
                font = ImageFont.load_default()
            
            self.draw.text(
                (obj["coords"][0], obj["coords"][1]),
                obj["texto"],
                fill=obj["cor"],
                font=font
            )
    
    def _limpar_canvas(self):
        """Limpa todo o canvas"""
        if messagebox.askyesno(
            "Confirmar",
            "Deseja realmente limpar todo o desenho?",
            parent=self
        ):
            # Resetar imagem
            self.imagem = Image.new(
                "RGB",
                (self.LARGURA_CANVAS, self.ALTURA_CANVAS),
                self.COR_FUNDO
            )
            self.draw = ImageDraw.Draw(self.imagem)
            
            # Limpar objetos
            self.objetos.clear()
            
            # Redesenhar grid
            self._desenhar_grid()
            
            # Atualizar
            self._atualizar_canvas()
            self._atualizar_info()
    
    def _atualizar_info(self):
        """Atualiza painel de informações"""
        self.lbl_objetos.config(text=f"Objetos: {len(self.objetos)}")
    
    def _exportar_png(self):
        """Exporta canvas como PNG"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Todos", "*.*")],
            initialfile=f"croqui_os_{self.os_id or 'novo'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            parent=self
        )
        
        if filename:
            try:
                self.imagem.save(filename, "PNG")
                messagebox.showinfo(
                    "Sucesso",
                    f"PNG exportado:\n{filename}",
                    parent=self
                )
            except Exception as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao exportar PNG: {e}",
                    parent=self
                )
    
    def _exportar_pdf(self):
        """Exporta canvas como PDF usando ReportLab"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Image as RLImage, Spacer, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import cm
            import io
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialfile=f"croqui_os_{self.os_id or 'novo'}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                parent=self
            )
            
            if filename:
                # Salva canvas como PNG temporário em memória
                temp_png = io.BytesIO()
                self.imagem.save(temp_png, "PNG")
                temp_png.seek(0)
                
                # Cria PDF
                doc = SimpleDocTemplate(filename, pagesize=A4)
                story = []
                styles = getSampleStyleSheet()
                
                # Título
                story.append(Paragraph(
                    f"Croqui Técnico - OS #{self.os_id or 'Novo'}",
                    styles['Title']
                ))
                story.append(Spacer(1, 12))
                
                # Data
                story.append(Paragraph(
                    f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                    styles['Normal']
                ))
                story.append(Spacer(1, 12))
                
                # Imagem do canvas
                img = RLImage(temp_png, width=18*cm, height=12.6*cm)
                story.append(img)
                
                # Informações
                story.append(Spacer(1, 12))
                story.append(Paragraph(
                    f"Total de objetos desenhados: {len(self.objetos)}",
                    styles['Normal']
                ))
                
                # Gera PDF
                doc.build(story)
                
                messagebox.showinfo(
                    "Sucesso",
                    f"PDF exportado:\n{filename}",
                    parent=self
                )
        except ImportError:
            messagebox.showerror(
                "Erro",
                "ReportLab não instalado!\nExecute: pip install reportlab",
                parent=self
            )
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao exportar PDF:\n{str(e)}",
                parent=self
            )
    
    def _salvar_e_fechar(self):
        """Salva dados do croqui via API backend"""
        import requests
        from frontend.desktop.auth_middleware import create_auth_header
        
        dados_croqui = {
            "os_id": self.os_id,
            "objetos": self.objetos,
            "timestamp": datetime.now().isoformat(),
            "largura": self.LARGURA_CANVAS,
            "altura": self.ALTURA_CANVAS
        }
        
        if self.os_id:
            try:
                # Salvar via API
                headers = create_auth_header()
                response = requests.post(
                    f"http://127.0.0.1:8002/api/v1/os/{self.os_id}/croqui",
                    json=dados_croqui,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    # Também salvar PNG localmente
                    output_dir = Path.home() / "Documents" / "Primotex_Croquis"
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    png_path = output_dir / f"croqui_os_{self.os_id}.png"
                    self.imagem.save(png_path, "PNG")
                    
                    messagebox.showinfo(
                        "Sucesso",
                        f"Croqui salvo!\n\nObjetos: {len(self.objetos)}\nArquivo: {png_path}",
                        parent=self
                    )
                    self.destroy()
                else:
                    raise ValueError(f"HTTP {response.status_code}")
            
            except Exception as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao salvar:\n{str(e)}\n\nSalvando localmente...",
                    parent=self
                )
                self._salvar_local(dados_croqui)
        else:
            messagebox.showwarning(
                "Aviso",
                "OS ID não fornecido!",
                parent=self
            )
            self._salvar_local(dados_croqui)
    
    def _salvar_local(self, dados_croqui: dict):
        """Fallback para salvar localmente"""
        output_dir = Path.home() / "Documents" / "Primotex_Croquis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = output_dir / f"croqui_os_{self.os_id or 'novo'}.json"
        png_path = output_dir / f"croqui_os_{self.os_id or 'novo'}.png"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(dados_croqui, f, ensure_ascii=False, indent=2)
        
        self.imagem.save(png_path, "PNG")
        
        messagebox.showinfo(
            "Salvo Localmente",
            f"Arquivos:\n{json_path}\n{png_path}",
            parent=self
        )
        self.destroy()
    
    def _carregar_croqui(self, os_id: int):
        """Carrega croqui existente via API backend"""
        import requests
        from frontend.desktop.auth_middleware import create_auth_header
        
        try:
            headers = create_auth_header()
            response = requests.get(
                f"http://127.0.0.1:8002/api/v1/os/{os_id}/croqui",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                dados = response.json()
                objetos = dados.get("objetos", [])
                
                if objetos:
                    self.objetos = objetos
                    
                    # Redesenhar todos os objetos
                    for obj in self.objetos:
                        self._redesenhar_objeto(obj)
                    
                    self._atualizar_canvas()
                    self._atualizar_info()
                    
                    messagebox.showinfo(
                        "Croqui Carregado",
                        f"OS #{os_id}: {len(objetos)} objetos",
                        parent=self
                    )
        
        except Exception as e:
                print(f"Erro ao carregar croqui: {e}")


# =======================================
# TESTE RÁPIDO
# =======================================

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    canvas = CanvasCroqui(root, os_id=123)
    
    root.mainloop()
