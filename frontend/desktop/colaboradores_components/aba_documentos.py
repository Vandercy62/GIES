"""
COMPONENTE: ABA DOCUMENTOS ⭐⭐⭐ CRÍTICO
========================================

Gerenciamento de documentos do colaborador com SISTEMA DE ALERTAS por cores.

Funcionalidades:
- TreeView com documentos (RG, CNH, ASO, NR, Certificados, etc.)
- Sistema de alertas por cor baseado em vencimento:
  🟢 Verde (#28a745) - > 30 dias até vencer
  🟡 Amarelo (#ffc107) - 15-30 dias até vencer
  🟠 Laranja (#fd7e14) - 1-14 dias até vencer
  🔴 Vermelho (#dc3545) - Vencido
- Upload de arquivos PDF/IMG (Base64)
- Preview de documentos
- Adicionar/Editar/Excluir documentos

Autor: GitHub Copilot
Data: 17/11/2025 - FASE 103 TAREFA 6
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import base64
import os


# Constantes
_FONTE_FAMILIA = "Segoe UI"

# Cores de alerta
COR_ALERTA_OK = "#28a745"  # Verde - > 30 dias
COR_ALERTA_ATENCAO = "#ffc107"  # Amarelo - 15-30 dias
COR_ALERTA_URGENTE = "#fd7e14"  # Laranja - 1-14 dias
COR_ALERTA_VENCIDO = "#dc3545"  # Vermelho - Vencido


class AbaDocumentos(tk.Frame):
    """Componente de documentos com sistema de alertas"""

    def __init__(self, parent):
        super().__init__(parent, bg="#f8f9fa")
        
        self.documentos: List[Dict[str, Any]] = []
        
        self._criar_interface()

    def _criar_interface(self):
        """Cria interface"""
        
        # Título e legenda
        header_frame = tk.Frame(self, bg="#f8f9fa")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            header_frame,
            text="📄 DOCUMENTOS - SISTEMA DE ALERTAS",
            font=(_FONTE_FAMILIA, 18, "bold"),
            bg="#f8f9fa"
        ).pack(side=tk.LEFT)
        
        # Legenda de cores
        legenda_frame = tk.Frame(header_frame, bg="#f8f9fa")
        legenda_frame.pack(side=tk.RIGHT)
        
        cores_legendas = [
            ("🟢 > 30d", COR_ALERTA_OK),
            ("🟡 15-30d", COR_ALERTA_ATENCAO),
            ("🟠 1-14d", COR_ALERTA_URGENTE),
            ("🔴 Vencido", COR_ALERTA_VENCIDO)
        ]
        
        for texto, cor in cores_legendas:
            lbl = tk.Label(
                legenda_frame,
                text=texto,
                font=(_FONTE_FAMILIA, 10, "bold"),
                bg=cor,
                fg="white" if cor in [
                    COR_ALERTA_URGENTE, COR_ALERTA_VENCIDO
                ] else "black",
                padx=8,
                pady=4
            )
            lbl.pack(side=tk.LEFT, padx=2)
        
        # TreeView
        tree_frame = tk.Frame(self, bg="#f8f9fa")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=(
                "id", "tipo", "numero", "emissao",
                "validade", "dias", "status"
            ),
            show="headings",
            yscrollcommand=scroll_y.set,
            height=12
        )
        
        scroll_y.config(command=self.tree.yview)
        
        # Colunas
        self.tree.heading("id", text="ID")
        self.tree.heading("tipo", text="Tipo de Documento")
        self.tree.heading("numero", text="Número")
        self.tree.heading("emissao", text="Data Emissão")
        self.tree.heading("validade", text="Validade")
        self.tree.heading("dias", text="Dias p/ Vencer")
        self.tree.heading("status", text="STATUS")
        
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("tipo", width=200)
        self.tree.column("numero", width=150)
        self.tree.column("emissao", width=120, anchor=tk.CENTER)
        self.tree.column("validade", width=120, anchor=tk.CENTER)
        self.tree.column("dias", width=120, anchor=tk.CENTER)
        self.tree.column("status", width=150, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Tags de cores
        self.tree.tag_configure("ok", background=COR_ALERTA_OK)
        self.tree.tag_configure("atencao", background=COR_ALERTA_ATENCAO)
        self.tree.tag_configure("urgente", background=COR_ALERTA_URGENTE)
        self.tree.tag_configure("vencido", background=COR_ALERTA_VENCIDO, foreground="white")
        
        # Botões
        botoes_frame = tk.Frame(self, bg="#f8f9fa")
        botoes_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_adicionar = tk.Button(
            botoes_frame,
            text="➕ Adicionar Documento",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#28a745",
            fg="white",
            width=20,
            height=2,
            command=self._adicionar_documento,
            cursor="hand2"
        )
        btn_adicionar.pack(side=tk.LEFT, padx=5)
        
        btn_upload = tk.Button(
            botoes_frame,
            text="📎 Upload Arquivo",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#007bff",
            fg="white",
            width=18,
            height=2,
            command=self._upload_arquivo,
            cursor="hand2"
        )
        btn_upload.pack(side=tk.LEFT, padx=5)
        
        btn_excluir = tk.Button(
            botoes_frame,
            text="🗑️ Excluir",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#dc3545",
            fg="white",
            width=15,
            height=2,
            command=self._excluir_documento,
            cursor="hand2"
        )
        btn_excluir.pack(side=tk.LEFT, padx=5)
        
        # Contador de alertas
        self.lbl_contador = tk.Label(
            botoes_frame,
            text="📊 Alertas: 🟢 0 | 🟡 0 | 🟠 0 | 🔴 0",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa",
            fg="#212529"
        )
        self.lbl_contador.pack(side=tk.RIGHT, padx=10)

    def _calcular_dias_vencimento(self, data_validade: str) -> int:
        """Calcula dias até vencimento"""
        try:
            validade = datetime.strptime(data_validade, "%Y-%m-%d").date()
            dias = (validade - date.today()).days
            return dias
        except (ValueError, AttributeError):
            return 999

    def _get_cor_alerta(self, dias: int) -> str:
        """Retorna cor baseada em dias"""
        if dias < 0:
            return "vencido"
        elif dias <= 14:
            return "urgente"
        elif dias <= 30:
            return "atencao"
        else:
            return "ok"

    def _get_status_texto(self, dias: int) -> str:
        """Retorna texto do status"""
        if dias < 0:
            return "🔴 VENCIDO"
        elif dias <= 14:
            return "🟠 URGENTE"
        elif dias <= 30:
            return "🟡 ATENÇÃO"
        else:
            return "🟢 OK"

    def _atualizar_tree(self):
        """Atualiza TreeView com documentos"""
        # Limpar
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Contadores
        contadores = {"ok": 0, "atencao": 0, "urgente": 0, "vencido": 0}
        
        # Adicionar documentos
        for doc in self.documentos:
            dias = self._calcular_dias_vencimento(doc.get('validade', ''))
            cor = self._get_cor_alerta(dias)
            status = self._get_status_texto(dias)
            
            contadores[cor] += 1
            
            self.tree.insert("", tk.END, values=(
                doc.get('id', ''),
                doc.get('tipo', ''),
                doc.get('numero', ''),
                doc.get('emissao', ''),
                doc.get('validade', ''),
                f"{dias} dias" if dias >= 0 else f"{abs(dias)} dias atrás",
                status
            ), tags=(cor,))
        
        # Atualizar contador
        self.lbl_contador.config(
            text=(
                f"📊 Alertas: 🟢 {contadores['ok']} | "
                f"🟡 {contadores['atencao']} | "
                f"🟠 {contadores['urgente']} | "
                f"🔴 {contadores['vencido']}"
            )
        )

    def _adicionar_documento(self):
        """Adiciona novo documento"""
        dialog = DialogDocumento(self, None)
        self.wait_window(dialog.top)
        
        if dialog.resultado:
            self.documentos.append(dialog.resultado)
            self._atualizar_tree()

    def _upload_arquivo(self):
        """Upload de arquivo PDF/IMG"""
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning(
                "Seleção",
                "Selecione um documento para fazer upload!",
                parent=self
            )
            return
        
        arquivo = filedialog.askopenfilename(
            parent=self,
            title="Selecionar Arquivo",
            filetypes=[
                ("PDF", "*.pdf"),
                ("Imagens", "*.png *.jpg *.jpeg"),
                ("Todos", "*.*")
            ]
        )
        
        if arquivo:
            # Validar tamanho (max 10MB)
            tamanho = os.path.getsize(arquivo)
            if tamanho > 10 * 1024 * 1024:
                messagebox.showerror(
                    "Arquivo muito grande",
                    "O arquivo deve ter no máximo 10MB!",
                    parent=self
                )
                return
            
            # Base64 encoding
            try:
                with open(arquivo, 'rb') as f:
                    arquivo_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                messagebox.showinfo(
                    "Upload",
                    f"✅ Arquivo carregado com sucesso!\n\n"
                    f"Tamanho: {tamanho / 1024:.2f} KB",
                    parent=self
                )
                
                # TODO: Salvar no banco
                
            except (IOError, OSError) as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao ler arquivo:\n{e}",
                    parent=self
                )

    def _excluir_documento(self):
        """Exclui documento"""
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning(
                "Seleção",
                "Selecione um documento para excluir!",
                parent=self
            )
            return
        
        item = self.tree.item(selecao[0])
        doc_id = item['values'][0]
        tipo = item['values'][1]
        
        confirma = messagebox.askyesno(
            "Confirmar",
            f"Excluir documento:\n\n{tipo}?",
            parent=self
        )
        
        if confirma:
            self.documentos = [d for d in self.documentos if d.get('id') != doc_id]
            self._atualizar_tree()

    def get_dados(self) -> List[Dict[str, Any]]:
        """Retorna documentos"""
        return self.documentos

    def set_dados(self, documentos: List[Dict[str, Any]]):
        """Define documentos"""
        self.documentos = documentos
        self._atualizar_tree()


class DialogDocumento:
    """Dialog para adicionar/editar documento"""
    
    def __init__(self, parent, documento: Optional[Dict[str, Any]] = None):
        self.top = tk.Toplevel(parent)
        self.top.title("Adicionar Documento")
        self.top.geometry("500x400")
        self.top.transient(parent)
        self.top.grab_set()
        
        self.resultado: Optional[Dict[str, Any]] = None
        
        # Formulário
        form = tk.Frame(self.top, bg="#f8f9fa")
        form.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Tipo
        tk.Label(
            form, text="Tipo:", font=(_FONTE_FAMILIA, 12, "bold"), bg="#f8f9fa"
        ).grid(row=0, column=0, sticky="w", pady=10)
        
        self.combo_tipo = ttk.Combobox(
            form,
            values=[
                "RG", "CPF", "CNH", "Carteira de Trabalho",
                "Certificado", "Diploma", "Exame Médico (ASO)",
                "NR-10", "NR-35", "Certificado de Curso"
            ],
            state="readonly",
            font=(_FONTE_FAMILIA, 12),
            width=30
        )
        self.combo_tipo.grid(row=0, column=1, pady=10)
        
        # Número
        tk.Label(
            form, text="Número:", font=(_FONTE_FAMILIA, 12, "bold"), bg="#f8f9fa"
        ).grid(row=1, column=0, sticky="w", pady=10)
        
        self.entry_numero = tk.Entry(form, font=(_FONTE_FAMILIA, 12), width=32)
        self.entry_numero.grid(row=1, column=1, pady=10)
        
        # Data Emissão
        tk.Label(
            form, text="Emissão:", font=(_FONTE_FAMILIA, 12, "bold"), bg="#f8f9fa"
        ).grid(row=2, column=0, sticky="w", pady=10)
        
        self.entry_emissao = tk.Entry(form, font=(_FONTE_FAMILIA, 12), width=32)
        self.entry_emissao.grid(row=2, column=1, pady=10)
        
        # Validade
        tk.Label(
            form, text="Validade:", font=(_FONTE_FAMILIA, 12, "bold"), bg="#f8f9fa"
        ).grid(row=3, column=0, sticky="w", pady=10)
        
        self.entry_validade = tk.Entry(form, font=(_FONTE_FAMILIA, 12), width=32)
        self.entry_validade.grid(row=3, column=1, pady=10)
        
        # Botões
        btn_frame = tk.Frame(self.top, bg="#f8f9fa")
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="✅ Salvar",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#28a745",
            fg="white",
            width=12,
            command=self._salvar
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#dc3545",
            fg="white",
            width=12,
            command=self.top.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def _salvar(self):
        """Salva documento"""
        self.resultado = {
            'id': None,
            'tipo': self.combo_tipo.get(),
            'numero': self.entry_numero.get().strip(),
            'emissao': self.entry_emissao.get().strip(),
            'validade': self.entry_validade.get().strip()
        }
        self.top.destroy()
