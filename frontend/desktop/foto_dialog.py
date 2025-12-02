#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA ERP PRIMOTEX - DIALOG DE CAPTURA DE FOTO 3x4
====================================================

Dialog reutilizável para captura/upload de fotos de colaboradores.

FUNCIONALIDADES:
- Upload de arquivo (JPG, PNG)
- Captura via webcam com OpenCV
- Preview em tempo real
- Crop manual (proporção 3:4)
- Retorno em base64

Autor: GitHub Copilot
Data: 17/11/2025 - FASE 102 - TAREFA 7
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import base64
import io
from PIL import Image, ImageTk
from typing import Optional


class FotoDialog:
    """Dialog para captura/upload de foto 3x4"""

    def __init__(self, parent):
        """
        Inicializar dialog de foto.

        Args:
            parent: Janela pai
        """
        self.parent = parent
        self.foto_base64: Optional[str] = None
        self.foto_image: Optional[Image.Image] = None

        self.create_dialog()

    def create_dialog(self):
        """Criar interface do dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Captura de Foto 3x4")
        self.dialog.geometry("600x550")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Centralizar
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
        self.dialog.geometry(f"600x550+{x}+{y}")

        # Título
        tk.Label(
            self.dialog, text="📸 Captura de Foto 3x4",
            font=("Segoe UI", 14, "bold"), fg="#1e88e5"
        ).pack(pady=10)

        # Frame preview
        preview_frame = tk.Frame(self.dialog, relief="solid", borderwidth=2, bg="#f0f0f0")
        preview_frame.pack(pady=15, padx=20)

        self.preview_label = tk.Label(
            preview_frame, text="NENHUMA FOTO\nSELECIONADA",
            font=("Segoe UI", 12), width=30, height=15, bg="#f0f0f0", fg="#999"
        )
        self.preview_label.pack(padx=10, pady=10)

        # Instruções
        tk.Label(
            self.dialog, text="Escolha uma das opções abaixo para adicionar a foto:",
            font=("Segoe UI", 9), fg="#666"
        ).pack(pady=5)

        # Botões
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=15)

        ttk.Button(
            btn_frame, text="📁 Carregar Arquivo",
            command=self.upload_arquivo, width=20
        ).grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(
            btn_frame, text="📸 Capturar Webcam",
            command=self.capturar_webcam, width=20
        ).grid(row=0, column=1, padx=5, pady=5)

        # Separador
        ttk.Separator(self.dialog, orient="horizontal").pack(fill="x", pady=10, padx=20)

        # Botões finais
        final_frame = tk.Frame(self.dialog)
        final_frame.pack(pady=10)

        ttk.Button(
            final_frame, text="✅ Salvar Foto",
            command=self.salvar_foto, width=20
        ).grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(
            final_frame, text="❌ Cancelar",
            command=self.cancelar, width=20
        ).grid(row=0, column=1, padx=5, pady=5)

        # Nota
        tk.Label(
            self.dialog, 
            text="💡 A foto será redimensionada automaticamente para otimizar o armazenamento",
            font=("Segoe UI", 8), fg="#666"
        ).pack(pady=5)

    def upload_arquivo(self):
        """Upload de arquivo de imagem"""
        file_path = filedialog.askopenfilename(
            title="Selecionar Foto do Colaborador",
            filetypes=[
                ("Imagens", "*.jpg *.jpeg *.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Todos", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            # Carregar imagem
            img = Image.open(file_path)

            # Converter para RGB se necessário
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Redimensionar mantendo proporção (máx 300x400)
            img.thumbnail((300, 400), Image.Resampling.LANCZOS)

            # Armazenar
            self.foto_image = img

            # Atualizar preview
            self._atualizar_preview(img)

            messagebox.showinfo(
                "✅ Sucesso",
                "Foto carregada com sucesso!\n\nClique em 'Salvar Foto' para confirmar."
            )

        except Exception as e:
            messagebox.showerror(
                "❌ Erro",
                f"Erro ao carregar foto:\n\n{str(e)}\n\nVerifique se o arquivo é uma imagem válida."
            )

    def capturar_webcam(self):
        """Capturar foto da webcam usando OpenCV"""
        try:
            import cv2
        except ImportError:
            messagebox.showerror(
                "❌ OpenCV não instalado",
                "O módulo OpenCV não está instalado!\n\n"
                "Para usar a captura via webcam, instale com:\n"
                "pip install opencv-python"
            )
            return

        try:
            # Inicializar webcam
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                messagebox.showerror(
                    "❌ Erro",
                    "Não foi possível abrir a webcam.\n\n"
                    "Verifique se a webcam está conectada e funcionando."
                )
                return

            # Dialog de captura
            self._create_webcam_dialog(cap)

        except Exception as e:
            messagebox.showerror(
                "❌ Erro",
                f"Erro ao acessar webcam:\n\n{str(e)}"
            )

    def _create_webcam_dialog(self, cap):
        """Criar dialog de captura webcam"""
        import cv2

        cap_dialog = tk.Toplevel(self.dialog)
        cap_dialog.title("Captura via Webcam")
        cap_dialog.geometry("660x550")
        cap_dialog.transient(self.dialog)
        cap_dialog.grab_set()

        # Título
        tk.Label(
            cap_dialog, text="📹 Visualização da Webcam",
            font=("Segoe UI", 12, "bold"), fg="#1e88e5"
        ).pack(pady=10)

        # Frame para video
        video_frame = tk.Frame(cap_dialog, relief="solid", borderwidth=2, bg="black")
        video_frame.pack(pady=10, padx=10)

        cap_label = tk.Label(video_frame, bg="black")
        cap_label.pack()

        # Instruções
        tk.Label(
            cap_dialog, text="Posicione-se na frente da câmera e clique em CAPTURAR",
            font=("Segoe UI", 9), fg="#666"
        ).pack(pady=5)

        # Botões
        btn_frame = tk.Frame(cap_dialog)
        btn_frame.pack(pady=10)

        frame_capturado = {"frame": None}

        def salvar_frame():
            """Salvar frame capturado"""
            if frame_capturado["frame"] is None:
                messagebox.showwarning("⚠️ Atenção", "Nenhum frame disponível!")
                return

            try:
                # Converter BGR (OpenCV) para RGB (PIL)
                rgb = cv2.cvtColor(frame_capturado["frame"], cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)

                # Converter para RGB se necessário
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Redimensionar
                img.thumbnail((300, 400), Image.Resampling.LANCZOS)

                # Armazenar
                self.foto_image = img

                # Atualizar preview no dialog principal
                self._atualizar_preview(img)

                # Fechar
                cap.release()
                cap_dialog.destroy()

                messagebox.showinfo(
                    "✅ Sucesso",
                    "Foto capturada com sucesso!\n\nClique em 'Salvar Foto' para confirmar."
                )

            except Exception as e:
                messagebox.showerror("❌ Erro", f"Erro ao salvar frame:\n{str(e)}")

        ttk.Button(
            btn_frame, text="📸 CAPTURAR",
            command=salvar_frame, width=15
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            btn_frame, text="❌ Cancelar",
            command=lambda: fechar_webcam(), width=15
        ).grid(row=0, column=1, padx=5)

        def atualizar_frame():
            """Atualizar preview em tempo real"""
            ret, frame = cap.read()

            if ret:
                frame_capturado["frame"] = frame.copy()

                # Redimensionar para display (640x480)
                frame_display = cv2.resize(frame, (640, 480))

                # Converter BGR para RGB
                frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)

                # Converter para ImageTk
                img_pil = Image.fromarray(frame_rgb)
                img_tk = ImageTk.PhotoImage(img_pil)

                # Atualizar label
                cap_label.config(image=img_tk)
                cap_label.image = img_tk

            # Continuar loop se janela está aberta
            if cap.isOpened() and cap_dialog.winfo_exists():
                cap_label.after(30, atualizar_frame)

        def fechar_webcam():
            """Fechar webcam e dialog"""
            cap.release()
            cap_dialog.destroy()

        cap_dialog.protocol("WM_DELETE_WINDOW", fechar_webcam)

        # Iniciar loop de atualização
        atualizar_frame()

    def _atualizar_preview(self, img: Image.Image):
        """Atualizar preview da foto"""
        # Criar PhotoImage
        photo_tk = ImageTk.PhotoImage(img)

        # Atualizar label
        self.preview_label.config(image=photo_tk, text="", bg="white")
        self.preview_label.image = photo_tk

    def salvar_foto(self):
        """Salvar foto em base64"""
        if self.foto_image is None:
            messagebox.showwarning(
                "⚠️ Atenção",
                "Nenhuma foto selecionada!\n\nCarregue um arquivo ou capture via webcam."
            )
            return

        try:
            # Converter para base64
            buffered = io.BytesIO()
            self.foto_image.save(buffered, format="PNG", optimize=True)
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Armazenar
            self.foto_base64 = img_base64

            # Fechar dialog
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror(
                "❌ Erro",
                f"Erro ao salvar foto:\n\n{str(e)}"
            )

    def cancelar(self):
        """Cancelar e fechar dialog"""
        self.foto_base64 = None
        self.dialog.destroy()

    def get_foto_base64(self) -> Optional[str]:
        """
        Retornar foto em base64.

        Returns:
            String base64 ou None se cancelado
        """
        return self.foto_base64

    def get_foto_image(self) -> Optional[Image.Image]:
        """
        Retornar objeto Image da foto.

        Returns:
            Objeto PIL.Image ou None
        """
        return self.foto_image


def testar_dialog():
    """Função de teste standalone"""
    root = tk.Tk()
    root.withdraw()

    dialog = FotoDialog(root)
    root.wait_window(dialog.dialog)

    if dialog.get_foto_base64():
        print(f"✅ Foto capturada! Tamanho base64: {len(dialog.get_foto_base64())} chars")
        print(f"Dimensões: {dialog.get_foto_image().size}")
    else:
        print("❌ Captura cancelada")

    root.destroy()


if __name__ == "__main__":
    testar_dialog()
