"""
WIDGET DE AVALIAÇÃO COM ESTRELAS
=================================

Widget customizado para avaliação de fornecedores com 5 estrelas clicáveis.
Interface intuitiva com feedback visual para usuários de idade avançada.

FUNCIONALIDADES:
- 5 estrelas clicáveis (30px cada)
- Cor dourada (#FFD700) quando preenchida
- Cor cinza (#D3D3D3) quando vazia
- Hover para preview da avaliação
- get_avaliacao() retorna 1-5 ou None
- set_avaliacao(valor) define avaliação inicial

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 101
"""

import tkinter as tk
from typing import Optional, Callable


class AvaliacaoWidget(tk.Frame):
    """
    Widget de avaliação com 5 estrelas clicáveis.
    
    Permite ao usuário avaliar fornecedores de 1 a 5 estrelas.
    """
    
    # Cores
    COR_PREENCHIDA = "#FFD700"  # Dourado
    COR_VAZIA = "#D3D3D3"       # Cinza claro
    COR_HOVER = "#FFA500"       # Laranja (preview)
    COR_FUNDO = "#f8f9fa"
    
    # Unicode das estrelas
    ESTRELA_PREENCHIDA = "★"
    ESTRELA_VAZIA = "☆"
    
    def __init__(
        self,
        parent,
        valor_inicial: Optional[int] = None,
        on_change: Optional[Callable[[Optional[int]], None]] = None,
        size: int = 30,
        bg: str = "#f8f9fa"
    ):
        """
        Inicializa widget de avaliação.
        
        Args:
            parent: Widget pai
            valor_inicial: Avaliação inicial (1-5 ou None)
            on_change: Callback chamado quando avaliação muda
            size: Tamanho da fonte das estrelas (pixels)
            bg: Cor de fundo
        """
        super().__init__(parent, bg=bg)
        
        self.valor: Optional[int] = None
        self.on_change = on_change
        self.size = size
        self.bg_color = bg
        
        # Labels das estrelas
        self.labels_estrelas: list[tk.Label] = []
        
        # Criar interface
        self._criar_interface()
        
        # Definir valor inicial
        if valor_inicial is not None:
            self.set_avaliacao(valor_inicial)
    
    def _criar_interface(self):
        """Cria interface com 5 estrelas"""
        # Container para centralizar estrelas
        container = tk.Frame(self, bg=self.bg_color)
        container.pack()
        
        # Criar 5 labels de estrelas
        for i in range(5):
            label = tk.Label(
                container,
                text=self.ESTRELA_VAZIA,
                font=("Segoe UI", self.size),
                fg=self.COR_VAZIA,
                bg=self.bg_color,
                cursor="hand2"
            )
            label.pack(side=tk.LEFT, padx=2)
            
            # Bind eventos
            label.bind("<Button-1>", lambda e, pos=i+1: self._ao_clicar(pos))
            label.bind("<Enter>", lambda e, pos=i+1: self._ao_hover(pos))
            label.bind("<Leave>", lambda e: self._ao_sair_hover())
            
            self.labels_estrelas.append(label)
    
    def _ao_clicar(self, posicao: int):
        """
        Handler de clique em estrela.
        
        Args:
            posicao: Posição da estrela (1-5)
        """
        # Se clicar na mesma estrela, remove avaliação
        if self.valor == posicao:
            self.valor = None
        else:
            self.valor = posicao
        
        # Atualizar visual
        self._atualizar_estrelas()
        
        # Chamar callback
        if self.on_change:
            self.on_change(self.valor)
    
    def _ao_hover(self, posicao: int):
        """
        Handler de hover sobre estrela.
        
        Args:
            posicao: Posição da estrela (1-5)
        """
        # Mostrar preview até essa posição
        for i in range(5):
            if i < posicao:
                self.labels_estrelas[i].config(
                    text=self.ESTRELA_PREENCHIDA,
                    fg=self.COR_HOVER
                )
            else:
                self.labels_estrelas[i].config(
                    text=self.ESTRELA_VAZIA,
                    fg=self.COR_VAZIA
                )
    
    def _ao_sair_hover(self):
        """Handler ao sair do hover"""
        # Restaurar estado original
        self._atualizar_estrelas()
    
    def _atualizar_estrelas(self):
        """Atualiza visual das estrelas baseado no valor atual"""
        for i in range(5):
            if self.valor is not None and i < self.valor:
                # Estrela preenchida
                self.labels_estrelas[i].config(
                    text=self.ESTRELA_PREENCHIDA,
                    fg=self.COR_PREENCHIDA
                )
            else:
                # Estrela vazia
                self.labels_estrelas[i].config(
                    text=self.ESTRELA_VAZIA,
                    fg=self.COR_VAZIA
                )
    
    def get_avaliacao(self) -> Optional[int]:
        """
        Obtém avaliação atual.
        
        Returns:
            int: Avaliação (1-5) ou None se não avaliado
        """
        return self.valor
    
    def set_avaliacao(self, valor: Optional[int]):
        """
        Define avaliação.
        
        Args:
            valor: Avaliação (1-5 ou None)
        """
        if valor is not None:
            # Validar range
            if not 1 <= valor <= 5:
                raise ValueError("Avaliação deve estar entre 1 e 5")
        
        self.valor = valor
        self._atualizar_estrelas()
    
    def limpar(self):
        """Remove avaliação"""
        self.set_avaliacao(None)
    
    def desabilitar(self):
        """Desabilita interação com as estrelas"""
        for label in self.labels_estrelas:
            label.config(cursor="")
            label.unbind("<Button-1>")
            label.unbind("<Enter>")
            label.unbind("<Leave>")
    
    def habilitar(self):
        """Habilita interação com as estrelas"""
        for i, label in enumerate(self.labels_estrelas):
            label.config(cursor="hand2")
            label.bind("<Button-1>", lambda e, pos=i+1: self._ao_clicar(pos))
            label.bind("<Enter>", lambda e, pos=i+1: self._ao_hover(pos))
            label.bind("<Leave>", lambda e: self._ao_sair_hover())


# =======================================
# FUNÇÃO DE TESTE
# =======================================

def main():
    """Função para testar o widget"""
    root = tk.Tk()
    root.title("Teste - Widget de Avaliação")
    root.geometry("400x300")
    root.configure(bg="#f8f9fa")
    
    # Label de título
    titulo = tk.Label(
        root,
        text="Widget de Avaliação - Teste",
        font=("Segoe UI", 16, "bold"),
        bg="#f8f9fa"
    )
    titulo.pack(pady=20)
    
    # Widget de avaliação
    def ao_mudar(valor):
        if valor is None:
            label_valor.config(text="Sem avaliação")
        else:
            label_valor.config(text=f"Avaliação: {valor} estrela{'s' if valor > 1 else ''}")
    
    avaliacao = AvaliacaoWidget(
        root,
        valor_inicial=None,
        on_change=ao_mudar,
        size=40
    )
    avaliacao.pack(pady=20)
    
    # Label de valor
    label_valor = tk.Label(
        root,
        text="Sem avaliação",
        font=("Segoe UI", 14),
        bg="#f8f9fa",
        fg="#6c757d"
    )
    label_valor.pack(pady=10)
    
    # Botões de teste
    frame_botoes = tk.Frame(root, bg="#f8f9fa")
    frame_botoes.pack(pady=20)
    
    tk.Button(
        frame_botoes,
        text="Definir 3 ⭐",
        command=lambda: avaliacao.set_avaliacao(3)
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        frame_botoes,
        text="Limpar",
        command=avaliacao.limpar
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        frame_botoes,
        text="Obter Valor",
        command=lambda: print(f"Avaliação atual: {avaliacao.get_avaliacao()}")
    ).pack(side=tk.LEFT, padx=5)
    
    root.mainloop()


if __name__ == "__main__":
    main()
