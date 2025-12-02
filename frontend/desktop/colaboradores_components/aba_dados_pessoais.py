"""
COMPONENTE: ABA DADOS PESSOAIS
==============================

Formulário de dados pessoais do colaborador.

Campos:
- Nome completo, CPF, RG
- Data de nascimento, Estado civil, Sexo
- Endereço completo (CEP, Rua, Número, Complemento, Bairro, Cidade, UF)
- Telefone fixo, Telefone celular
- Email pessoal
- Foto 3x4 (placeholder para integração futura)

Autor: GitHub Copilot
Data: 17/11/2025 - FASE 103 TAREFA 3
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
import re
from datetime import datetime


# Constantes
_FONTE_FAMILIA = "Segoe UI"


class AbaDadosPessoais(tk.Frame):
    """Componente de dados pessoais"""

    def __init__(self, parent):
        super().__init__(parent, bg="#f8f9fa")
        
        self.dados: Dict[str, Any] = {}
        self._criar_interface()

    def _criar_interface(self):
        """Cria interface"""
        
        # Container scrollable
        canvas = tk.Canvas(self, bg="#f8f9fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        scroll_frame = tk.Frame(canvas, bg="#f8f9fa")
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Formulário
        form_frame = tk.Frame(scroll_frame, bg="#f8f9fa")
        form_frame.pack(padx=40, pady=20, fill=tk.BOTH, expand=True)
        
        # Seção Identificação
        self._criar_secao(form_frame, "👤 IDENTIFICAÇÃO", 0)
        
        self.entry_nome = self._criar_campo(
            form_frame, "Nome Completo:", 1, obrigatorio=True
        )
        
        row_frame = tk.Frame(form_frame, bg="#f8f9fa")
        row_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.entry_cpf = self._criar_campo_inline(
            row_frame, "CPF:", width=20
        )
        self.entry_rg = self._criar_campo_inline(
            row_frame, "RG:", width=20, padx=20
        )
        
        # Data nascimento, estado civil, sexo
        row_frame2 = tk.Frame(form_frame, bg="#f8f9fa")
        row_frame2.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.entry_data_nasc = self._criar_campo_inline(
            row_frame2, "Data Nascimento:", width=15
        )
        
        tk.Label(
            row_frame2,
            text="Estado Civil:",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa"
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.combo_estado_civil = ttk.Combobox(
            row_frame2,
            values=[
                "Solteiro(a)",
                "Casado(a)",
                "Divorciado(a)",
                "Viúvo(a)",
                "Separado(a)"
            ],
            state="readonly",
            font=(_FONTE_FAMILIA, 12),
            width=15
        )
        self.combo_estado_civil.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            row_frame2,
            text="Sexo:",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa"
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.combo_sexo = ttk.Combobox(
            row_frame2,
            values=["Masculino", "Feminino", "Outro"],
            state="readonly",
            font=(_FONTE_FAMILIA, 12),
            width=12
        )
        self.combo_sexo.pack(side=tk.LEFT, padx=5)
        
        # Seção Endereço
        self._criar_secao(form_frame, "📍 ENDEREÇO", 4)
        
        row_cep = tk.Frame(form_frame, bg="#f8f9fa")
        row_cep.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.entry_cep = self._criar_campo_inline(
            row_cep, "CEP:", width=15
        )
        
        btn_buscar_cep = tk.Button(
            row_cep,
            text="🔍 Buscar",
            font=(_FONTE_FAMILIA, 10, "bold"),
            bg="#17a2b8",
            fg="white",
            command=self._buscar_cep
        )
        btn_buscar_cep.pack(side=tk.LEFT, padx=5)
        
        self.entry_logradouro = self._criar_campo(
            form_frame, "Logradouro:", 6
        )
        
        row_num = tk.Frame(form_frame, bg="#f8f9fa")
        row_num.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.entry_numero = self._criar_campo_inline(
            row_num, "Número:", width=10
        )
        self.entry_complemento = self._criar_campo_inline(
            row_num, "Complemento:", width=25, padx=20
        )
        
        self.entry_bairro = self._criar_campo(
            form_frame, "Bairro:", 8
        )
        
        row_cidade = tk.Frame(form_frame, bg="#f8f9fa")
        row_cidade.grid(row=9, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.entry_cidade = self._criar_campo_inline(
            row_cidade, "Cidade:", width=30
        )
        self.entry_uf = self._criar_campo_inline(
            row_cidade, "UF:", width=5, padx=20
        )
        
        # Seção Contato
        self._criar_secao(form_frame, "📞 CONTATO", 10)
        
        row_tel = tk.Frame(form_frame, bg="#f8f9fa")
        row_tel.grid(row=11, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.entry_telefone = self._criar_campo_inline(
            row_tel, "Telefone:", width=20
        )
        self.entry_celular = self._criar_campo_inline(
            row_tel, "Celular:", width=20, padx=20
        )
        
        self.entry_email = self._criar_campo(
            form_frame, "Email:", 12
        )
        
        # Seção Foto (placeholder)
        self._criar_secao(form_frame, "📷 FOTO 3x4", 13)
        
        foto_frame = tk.Frame(form_frame, bg="#ffffff", relief=tk.RIDGE, bd=2)
        foto_frame.grid(row=14, column=0, columnspan=2, pady=10)
        
        self.lbl_foto = tk.Label(
            foto_frame,
            text="📷\n\nNenhuma foto\n\n(Integração futura)",
            font=(_FONTE_FAMILIA, 12),
            bg="#ffffff",
            fg="#6c757d",
            width=20,
            height=10
        )
        self.lbl_foto.pack(padx=10, pady=10)

    def _criar_secao(self, parent, titulo: str, row: int):
        """Cria seção com título"""
        frame = tk.Frame(parent, bg="#e9ecef", relief=tk.RAISED, bd=1)
        frame.grid(
            row=row, column=0, columnspan=2,
            sticky="ew", pady=(20, 10)
        )
        
        tk.Label(
            frame,
            text=titulo,
            font=(_FONTE_FAMILIA, 14, "bold"),
            bg="#e9ecef",
            fg="#212529"
        ).pack(pady=8)

    def _criar_campo(
        self,
        parent,
        label: str,
        row: int,
        obrigatorio: bool = False
    ) -> tk.Entry:
        """Cria campo de entrada"""
        tk.Label(
            parent,
            text=f"{label} {'*' if obrigatorio else ''}",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa",
            fg="#dc3545" if obrigatorio else "#212529"
        ).grid(row=row, column=0, sticky="w", pady=5)
        
        entry = tk.Entry(
            parent,
            font=(_FONTE_FAMILIA, 14),
            width=50
        )
        entry.grid(row=row, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        return entry

    def _criar_campo_inline(
        self,
        parent,
        label: str,
        width: int = 20,
        padx: int = 0
    ) -> tk.Entry:
        """Cria campo inline"""
        tk.Label(
            parent,
            text=label,
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa"
        ).pack(side=tk.LEFT, padx=(padx, 5))
        
        entry = tk.Entry(
            parent,
            font=(_FONTE_FAMILIA, 14),
            width=width
        )
        entry.pack(side=tk.LEFT, padx=5)
        
        return entry

    def _buscar_cep(self):
        """Busca CEP (placeholder)"""
        messagebox.showinfo(
            "Buscar CEP",
            "⏳ Integração com API de CEP será implementada!",
            parent=self
        )

    def get_dados(self) -> Dict[str, Any]:
        """Retorna dados do formulário"""
        return {
            'nome': self.entry_nome.get().strip(),
            'cpf': self.entry_cpf.get().strip(),
            'rg': self.entry_rg.get().strip(),
            'data_nascimento': self.entry_data_nasc.get().strip(),
            'estado_civil': self.combo_estado_civil.get(),
            'sexo': self.combo_sexo.get(),
            'cep': self.entry_cep.get().strip(),
            'logradouro': self.entry_logradouro.get().strip(),
            'numero': self.entry_numero.get().strip(),
            'complemento': self.entry_complemento.get().strip(),
            'bairro': self.entry_bairro.get().strip(),
            'cidade': self.entry_cidade.get().strip(),
            'uf': self.entry_uf.get().strip(),
            'telefone': self.entry_telefone.get().strip(),
            'celular': self.entry_celular.get().strip(),
            'email': self.entry_email.get().strip()
        }

    def set_dados(self, dados: Dict[str, Any]):
        """Preenche formulário"""
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, dados.get('nome', ''))
        
        self.entry_cpf.delete(0, tk.END)
        self.entry_cpf.insert(0, dados.get('cpf', ''))
        
        self.entry_rg.delete(0, tk.END)
        self.entry_rg.insert(0, dados.get('rg', ''))
        
        # TODO: Preencher demais campos
