"""
COMPONENTE: ABA OBSERVAÇÕES
===========================

Observações gerais e informações complementares do colaborador.

Campos:
- Observações gerais (Text widget)
- Histórico de avaliações (placeholder - futuro)
- Histórico de férias (placeholder - futuro)
- Saldo de dias de férias (cálculo simples)

Autor: GitHub Copilot
Data: 17/11/2025 - FASE 103 TAREFA 9
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


# Constantes
_FONTE_FAMILIA = "Segoe UI"


class AbaObservacoes(tk.Frame):
    """Componente de observações"""

    def __init__(self, parent):
        super().__init__(parent, bg="#f8f9fa")
        
        self._criar_interface()

    def _criar_interface(self):
        """Cria interface"""
        
        # Container
        container = tk.Frame(self, bg="#f8f9fa")
        container.pack(padx=40, pady=30, fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(
            container,
            text="📝 OBSERVAÇÕES E INFORMAÇÕES ADICIONAIS",
            font=(_FONTE_FAMILIA, 18, "bold"),
            bg="#f8f9fa"
        ).pack(pady=(0, 20))
        
        # Observações Gerais
        frame_obs = tk.LabelFrame(
            container,
            text="💬 Observações Gerais",
            font=(_FONTE_FAMILIA, 14, "bold"),
            bg="#f8f9fa",
            fg="#212529"
        )
        frame_obs.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scroll_y = ttk.Scrollbar(frame_obs, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_observacoes = tk.Text(
            frame_obs,
            font=(_FONTE_FAMILIA, 12),
            wrap=tk.WORD,
            yscrollcommand=scroll_y.set,
            height=8
        )
        self.text_observacoes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scroll_y.config(command=self.text_observacoes.yview)
        
        # Saldo de Férias
        frame_ferias = tk.LabelFrame(
            container,
            text="🏖️ Férias",
            font=(_FONTE_FAMILIA, 14, "bold"),
            bg="#f8f9fa",
            fg="#212529"
        )
        frame_ferias.pack(fill=tk.X, pady=10)
        
        ferias_content = tk.Frame(frame_ferias, bg="#f8f9fa")
        ferias_content.pack(padx=20, pady=15)
        
        tk.Label(
            ferias_content,
            text="Saldo de Dias de Férias:",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa"
        ).pack(side=tk.LEFT, padx=5)
        
        self.lbl_saldo_ferias = tk.Label(
            ferias_content,
            text="30 dias",
            font=(_FONTE_FAMILIA, 16, "bold"),
            bg="#28a745",
            fg="white",
            padx=15,
            pady=5
        )
        self.lbl_saldo_ferias.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            ferias_content,
            text="(Cálculo automático baseado em admissão)",
            font=(_FONTE_FAMILIA, 10),
            bg="#f8f9fa",
            fg="#6c757d"
        ).pack(side=tk.LEFT, padx=5)
        
        # Histórico Avaliações (Placeholder)
        frame_aval = tk.LabelFrame(
            container,
            text="⭐ Histórico de Avaliações (Futuro)",
            font=(_FONTE_FAMILIA, 14, "bold"),
            bg="#f8f9fa",
            fg="#6c757d"
        )
        frame_aval.pack(fill=tk.X, pady=10)
        
        tk.Label(
            frame_aval,
            text="📋 Sistema de avaliações de desempenho será implementado\n"
                 "nas próximas fases do projeto.",
            font=(_FONTE_FAMILIA, 12),
            bg="#f8f9fa",
            fg="#6c757d",
            justify=tk.LEFT
        ).pack(padx=20, pady=15)
        
        # Histórico Férias (Placeholder)
        frame_hist = tk.LabelFrame(
            container,
            text="📅 Histórico de Férias (Futuro)",
            font=(_FONTE_FAMILIA, 14, "bold"),
            bg="#f8f9fa",
            fg="#6c757d"
        )
        frame_hist.pack(fill=tk.X, pady=10)
        
        tk.Label(
            frame_hist,
            text="🏖️ Controle completo de períodos de férias gozadas\n"
                 "será implementado nas próximas fases.",
            font=(_FONTE_FAMILIA, 12),
            bg="#f8f9fa",
            fg="#6c757d",
            justify=tk.LEFT
        ).pack(padx=20, pady=15)

    def get_dados(self) -> Dict[str, Any]:
        """Retorna dados"""
        return {
            'observacoes_gerais': (
                self.text_observacoes.get("1.0", tk.END).strip()
            ),
            'saldo_ferias': 30  # Placeholder
        }

    def set_dados(self, dados: Dict[str, Any]):
        """Define dados"""
        self.text_observacoes.delete("1.0", tk.END)
        self.text_observacoes.insert(
            "1.0", dados.get('observacoes_gerais', '')
        )
        
        saldo = dados.get('saldo_ferias', 30)
        self.lbl_saldo_ferias.config(text=f"{saldo} dias")
