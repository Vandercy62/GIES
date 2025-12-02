"""
COMPONENTE: ABA DADOS PROFISSIONAIS
===================================

Formulário de dados profissionais do colaborador.

Campos:
- Cargo (dropdown do backend)
- Departamento (dropdown do backend)
- Data de admissão
- Salário
- Tipo de contrato (CLT, PJ, Estagiário, etc.)
- Status (Ativo, Férias, Afastado, etc.)
- Responsável direto (dropdown de colaboradores)
- Observações profissionais

Autor: GitHub Copilot
Data: 17/11/2025 - FASE 103 TAREFA 5
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List
import threading
import requests

from frontend.desktop.auth_middleware import create_auth_header


# Constantes
_FONTE_FAMILIA = "Segoe UI"
API_BASE_URL = "http://127.0.0.1:8002"


class AbaDadosProfissionais(tk.Frame):
    """Componente de dados profissionais"""

    def __init__(self, parent):
        super().__init__(parent, bg="#f8f9fa")
        
        self.cargos: List[Dict[str, Any]] = []
        self.departamentos: List[Dict[str, Any]] = []
        self.colaboradores: List[Dict[str, Any]] = []
        
        self._criar_interface()
        self._carregar_dados_backend()

    def _criar_interface(self):
        """Cria interface"""
        
        # Container
        form_frame = tk.Frame(self, bg="#f8f9fa")
        form_frame.pack(padx=40, pady=30, fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(
            form_frame,
            text="💼 DADOS PROFISSIONAIS",
            font=(_FONTE_FAMILIA, 18, "bold"),
            bg="#f8f9fa",
            fg="#212529"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Cargo
        tk.Label(
            form_frame,
            text="Cargo: *",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa",
            fg="#dc3545"
        ).grid(row=1, column=0, sticky="w", pady=10)
        
        self.combo_cargo = ttk.Combobox(
            form_frame,
            state="readonly",
            font=(_FONTE_FAMILIA, 14),
            width=40
        )
        self.combo_cargo.grid(row=1, column=1, sticky="ew", pady=10, padx=(10, 0))
        
        # Departamento
        tk.Label(
            form_frame,
            text="Departamento: *",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa",
            fg="#dc3545"
        ).grid(row=2, column=0, sticky="w", pady=10)
        
        self.combo_departamento = ttk.Combobox(
            form_frame,
            state="readonly",
            font=(_FONTE_FAMILIA, 14),
            width=40
        )
        self.combo_departamento.grid(
            row=2, column=1, sticky="ew", pady=10, padx=(10, 0)
        )
        
        # Data admissão e Salário
        row_frame = tk.Frame(form_frame, bg="#f8f9fa")
        row_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)
        
        tk.Label(
            row_frame,
            text="Data Admissão: *",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa",
            fg="#dc3545"
        ).pack(side=tk.LEFT)
        
        self.entry_data_admissao = tk.Entry(
            row_frame,
            font=(_FONTE_FAMILIA, 14),
            width=15
        )
        self.entry_data_admissao.pack(side=tk.LEFT, padx=(10, 30))
        
        tk.Label(
            row_frame,
            text="Salário: R$",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.entry_salario = tk.Entry(
            row_frame,
            font=(_FONTE_FAMILIA, 14),
            width=20
        )
        self.entry_salario.pack(side=tk.LEFT, padx=5)
        
        # Tipo Contrato
        tk.Label(
            form_frame,
            text="Tipo de Contrato: *",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa",
            fg="#dc3545"
        ).grid(row=4, column=0, sticky="w", pady=10)
        
        self.combo_tipo_contrato = ttk.Combobox(
            form_frame,
            values=[
                "CLT",
                "Pessoa Jurídica",
                "Estagiário",
                "Terceirizado",
                "Freelancer",
                "Temporário"
            ],
            state="readonly",
            font=(_FONTE_FAMILIA, 14),
            width=40
        )
        self.combo_tipo_contrato.grid(
            row=4, column=1, sticky="ew", pady=10, padx=(10, 0)
        )
        
        # Status
        tk.Label(
            form_frame,
            text="Status: *",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa",
            fg="#dc3545"
        ).grid(row=5, column=0, sticky="w", pady=10)
        
        self.combo_status = ttk.Combobox(
            form_frame,
            values=[
                "ATIVO",
                "FERIAS",
                "AFASTADO",
                "LICENCA",
                "INATIVO",
                "DEMITIDO"
            ],
            state="readonly",
            font=(_FONTE_FAMILIA, 14),
            width=40
        )
        self.combo_status.set("ATIVO")
        self.combo_status.grid(
            row=5, column=1, sticky="ew", pady=10, padx=(10, 0)
        )
        
        # Responsável Direto
        tk.Label(
            form_frame,
            text="Responsável Direto:",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa"
        ).grid(row=6, column=0, sticky="w", pady=10)
        
        self.combo_responsavel = ttk.Combobox(
            form_frame,
            state="readonly",
            font=(_FONTE_FAMILIA, 14),
            width=40
        )
        self.combo_responsavel.grid(
            row=6, column=1, sticky="ew", pady=10, padx=(10, 0)
        )
        
        # Observações
        tk.Label(
            form_frame,
            text="Observações Profissionais:",
            font=(_FONTE_FAMILIA, 12, "bold"),
            bg="#f8f9fa"
        ).grid(row=7, column=0, sticky="nw", pady=10)
        
        self.text_obs = tk.Text(
            form_frame,
            font=(_FONTE_FAMILIA, 12),
            width=40,
            height=6
        )
        self.text_obs.grid(
            row=7, column=1, sticky="ew", pady=10, padx=(10, 0)
        )
        
        # Configurar grid
        form_frame.columnconfigure(1, weight=1)

    def _carregar_dados_backend(self):
        """Carrega cargos, departamentos e colaboradores"""
        def carregar_thread():
            try:
                headers = create_auth_header()
                
                # Cargos
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/colaboradores/cargos/",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    self.cargos = response.json()
                
                # Departamentos
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/colaboradores/departamentos/",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    self.departamentos = response.json()
                
                # Colaboradores ativos
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/colaboradores/?ativo=true",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    self.colaboradores = data.get('items', [])
                
                self.after(0, self._popular_combos)
                
            except (ConnectionError, TimeoutError, ValueError) as e:
                print(f"Erro ao carregar dados: {e}")
        
        thread = threading.Thread(target=carregar_thread, daemon=True)
        thread.start()

    def _popular_combos(self):
        """Popula comboboxes"""
        # Cargos
        valores_cargos = [c.get('nome', '') for c in self.cargos]
        self.combo_cargo['values'] = valores_cargos
        
        # Departamentos
        valores_deptos = [d.get('nome', '') for d in self.departamentos]
        self.combo_departamento['values'] = valores_deptos
        
        # Responsáveis
        valores_resp = [c.get('nome', '') for c in self.colaboradores]
        self.combo_responsavel['values'] = ['(Nenhum)'] + valores_resp

    def get_dados(self) -> Dict[str, Any]:
        """Retorna dados do formulário"""
        cargo_idx = self.combo_cargo.current()
        cargo_id = self.cargos[cargo_idx]['id'] if cargo_idx >= 0 else None
        
        depto_idx = self.combo_departamento.current()
        depto_id = (
            self.departamentos[depto_idx]['id']
            if depto_idx >= 0 else None
        )
        
        resp_idx = self.combo_responsavel.current()
        resp_id = (
            self.colaboradores[resp_idx - 1]['id']
            if resp_idx > 0 else None
        )
        
        return {
            'cargo_id': cargo_id,
            'departamento_id': depto_id,
            'data_admissao': self.entry_data_admissao.get().strip(),
            'salario': self.entry_salario.get().strip(),
            'tipo_contrato': self.combo_tipo_contrato.get(),
            'status': self.combo_status.get(),
            'responsavel_id': resp_id,
            'observacoes_profissionais': self.text_obs.get("1.0", tk.END).strip()
        }

    def set_dados(self, dados: Dict[str, Any]):
        """Preenche formulário"""
        # TODO: Implementar
        pass
