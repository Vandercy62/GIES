"""
SISTEMA ERP PRIMOTEX - MODELO DE PRODUTOS E SERVIÇOS
===================================================

Este arquivo define a estrutura da tabela 'produtos' no banco de dados.
Armazena tanto PRODUTOS (materiais físicos) quanto SERVIÇOS (mão de obra).

DIFERENÇA ENTRE PRODUTO E SERVIÇO:
- PRODUTO: Item físico que tem estoque (ex: Forro PVC, Perfil de Alumínio)
- SERVIÇO: Mão de obra que não tem estoque (ex: Instalação, Manutenção)

CAMPOS PRINCIPAIS:
- Identificação (código, descrição, código de barras)
- Categoria e tipo
- Preços (custo e venda)
- Estoque (apenas para produtos)
- Fornecedor e especificações técnicas
- Fotos e documentos

Autor: GitHub Copilot
Data: 29/10/2025
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.sql import func
from backend.database.config import Base

class Produto(Base):
    """
    Modelo da tabela de produtos e serviços.
    
    Esta tabela unificada armazena tanto produtos físicos
    quanto serviços oferecidos pela Primotex.
    """
    
    # Nome da tabela no banco de dados
    __tablename__ = "produtos"
    
    # =======================================
    # IDENTIFICAÇÃO BÁSICA
    # =======================================
    
    # Chave primária
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="ID único do produto/serviço"
    )
    
    # Código do produto (único)
    codigo = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
        comment="Código único: FRR-001, SRV-001, etc."
    )
    
    # Código de barras (para produtos físicos)
    codigo_barras = Column(
        String(50),
        unique=True,
        index=True,
        comment="Código de barras (EAN13, CODE128, etc.)"
    )
    
    # Descrição/Nome do produto
    descricao = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Descrição completa do produto/serviço"
    )
    
    # Tipo: Produto ou Serviço
    tipo = Column(
        String(20),
        nullable=False,
        default="Produto",
        comment="Tipo: Produto (físico) ou Serviço (mão de obra)"
    )
    
    # =======================================
    # CATEGORIA E CLASSIFICAÇÃO
    # =======================================
    
    # Categoria principal
    categoria = Column(
        String(50),
        nullable=False,
        comment="Categoria: Forros, Divisórias, Perfis, Instalação, etc."
    )
    
    # Subcategoria
    subcategoria = Column(
        String(50),
        comment="Subcategoria mais específica"
    )
    
    # Unidade de medida
    unidade_medida = Column(
        String(10),
        nullable=False,
        default="UN",
        comment="Unidade: UN, M², M, KG, HR, etc."
    )
    
    # =======================================
    # PREÇOS E CUSTOS
    # =======================================
    
    # Preço de custo
    preco_custo = Column(
        Numeric(10, 4),
        default=0.0000,
        comment="Preço de custo unitário"
    )
    
    # Margem de lucro (%)
    margem_lucro = Column(
        Numeric(5, 2),
        default=0.00,
        comment="Margem de lucro em percentual"
    )
    
    # Preço de venda
    preco_venda = Column(
        Numeric(10, 4),
        nullable=False,
        default=0.0000,
        comment="Preço de venda unitário"
    )
    
    # =======================================
    # CONTROLE DE ESTOQUE (SÓ PARA PRODUTOS)
    # =======================================
    
    # Controla estoque?
    controla_estoque = Column(
        Boolean,
        default=True,
        comment="Se True, controla estoque (produtos). Se False, não controla (serviços)"
    )
    
    # Estoque atual
    estoque_atual = Column(
        Numeric(10, 4),
        default=0.0000,
        comment="Quantidade atual em estoque"
    )
    
    # Estoque mínimo
    estoque_minimo = Column(
        Numeric(10, 4),
        default=0.0000,
        comment="Quantidade mínima para alerta"
    )
    
    # Estoque máximo
    estoque_maximo = Column(
        Numeric(10, 4),
        default=0.0000,
        comment="Quantidade máxima desejada"
    )
    
    # Localização no estoque
    localizacao_estoque = Column(
        String(50),
        comment="Localização física no estoque: Prateleira A1, Galpão 2, etc."
    )
    
    # =======================================
    # FORNECEDOR E COMPRAS
    # =======================================
    
    # ID do fornecedor principal
    fornecedor_principal_id = Column(
        Integer,
        comment="ID do fornecedor principal"
    )
    
    # Código do produto no fornecedor
    codigo_fornecedor = Column(
        String(50),
        comment="Código deste produto no catálogo do fornecedor"
    )
    
    # Prazo de entrega padrão (em dias)
    prazo_entrega_dias = Column(
        Integer,
        default=0,
        comment="Prazo de entrega em dias úteis"
    )
    
    # =======================================
    # ESPECIFICAÇÕES TÉCNICAS
    # =======================================
    
    # Peso
    peso = Column(
        Numeric(8, 3),
        comment="Peso em KG"
    )
    
    # Dimensões (comprimento x largura x altura)
    comprimento = Column(
        Numeric(8, 2),
        comment="Comprimento em metros"
    )
    
    largura = Column(
        Numeric(8, 2),
        comment="Largura em metros"
    )
    
    altura = Column(
        Numeric(8, 2),
        comment="Altura em metros"
    )
    
    # Cor
    cor = Column(
        String(30),
        comment="Cor do produto"
    )
    
    # Material
    material = Column(
        String(50),
        comment="Material: PVC, Alumínio, Madeira, etc."
    )
    
    # =======================================
    # PARA SERVIÇOS ESPECÍFICOS
    # =======================================
    
    # Tempo estimado de execução (em horas)
    tempo_execucao_horas = Column(
        Numeric(5, 2),
        comment="Tempo estimado de execução do serviço em horas"
    )
    
    # Materiais necessários (JSON)
    materiais_necessarios = Column(
        Text,
        comment="JSON com lista de produtos necessários para o serviço"
    )
    
    # Procedimentos/Instruções
    procedimentos = Column(
        Text,
        comment="Instruções de execução do serviço"
    )
    
    # =======================================
    # DOCUMENTAÇÃO E MÍDIA
    # =======================================
    
    # Fotos do produto (JSON com caminhos)
    fotos_paths = Column(
        Text,
        comment="JSON com caminhos das fotos: ['foto1.jpg', 'foto2.jpg']"
    )
    
    # Documentos técnicos
    documentos_paths = Column(
        Text,
        comment="JSON com caminhos de manuais, fichas técnicas, etc."
    )
    
    # =======================================
    # CLASSIFICAÇÃO FISCAL
    # =======================================
    
    # NCM (Nomenclatura Comum do Mercosul)
    ncm = Column(
        String(10),
        comment="Código NCM para nota fiscal"
    )
    
    # =======================================
    # CONTROLE DO SISTEMA
    # =======================================
    
    # Status do produto
    status = Column(
        String(20),
        nullable=False,
        default="Ativo",
        comment="Status: Ativo, Inativo, Descontinuado"
    )
    
    # Data de criação
    data_criacao = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Data de criação do cadastro"
    )
    
    # Data de atualização
    data_atualizacao = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="Data da última atualização"
    )
    
    # Usuário que criou
    usuario_criacao_id = Column(
        Integer,
        comment="ID do usuário que criou o cadastro"
    )
    
    # Observações gerais
    observacoes = Column(
        Text,
        comment="Observações gerais sobre o produto/serviço"
    )
    
    # =======================================
    # MÉTODOS DA CLASSE
    # =======================================
    
    def __repr__(self):
        """Representação do objeto"""
        return f"<Produto(id={self.id}, codigo='{self.codigo}', descricao='{self.descricao}')>"
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            "id": self.id,
            "codigo": self.codigo,
            "codigo_barras": self.codigo_barras,
            "descricao": self.descricao,
            "tipo": self.tipo,
            "categoria": self.categoria,
            "subcategoria": self.subcategoria,
            "unidade_medida": self.unidade_medida,
            
            # Preços
            "preco_custo": float(self.preco_custo) if self.preco_custo else 0.00,
            "margem_lucro": float(self.margem_lucro) if self.margem_lucro else 0.00,
            "preco_venda": float(self.preco_venda) if self.preco_venda else 0.00,
            
            # Estoque
            "controla_estoque": self.controla_estoque,
            "estoque_atual": float(self.estoque_atual) if self.estoque_atual else 0.00,
            "estoque_minimo": float(self.estoque_minimo) if self.estoque_minimo else 0.00,
            "estoque_maximo": float(self.estoque_maximo) if self.estoque_maximo else 0.00,
            "localizacao_estoque": self.localizacao_estoque,
            
            # Especificações
            "peso": float(self.peso) if self.peso else None,
            "dimensoes": {
                "comprimento": float(self.comprimento) if self.comprimento else None,
                "largura": float(self.largura) if self.largura else None,
                "altura": float(self.altura) if self.altura else None
            },
            "cor": self.cor,
            "material": self.material,
            
            # Para serviços
            "tempo_execucao_horas": float(self.tempo_execucao_horas) if self.tempo_execucao_horas else None,
            
            # Sistema
            "status": self.status,
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None,
            "observacoes": self.observacoes
        }
    
    def is_produto(self):
        """Verifica se é produto físico"""
        return self.tipo == "Produto"
    
    def is_servico(self):
        """Verifica se é serviço"""
        return self.tipo == "Serviço"
    
    def is_ativo(self):
        """Verifica se está ativo"""
        return self.status == "Ativo"
    
    def estoque_baixo(self):
        """Verifica se estoque está baixo"""
        if not self.controla_estoque:
            return False
        return self.estoque_atual <= self.estoque_minimo
    
    def calcular_preco_venda(self):
        """Calcula preço de venda baseado no custo e margem"""
        if self.preco_custo and self.margem_lucro:
            return self.preco_custo * (1 + (self.margem_lucro / 100))
        return self.preco_custo or 0

# =======================================
# CONSTANTES DO SISTEMA
# =======================================

TIPOS_PRODUTO = ["Produto", "Serviço"]
STATUS_PRODUTO = ["Ativo", "Inativo", "Descontinuado"]

CATEGORIAS_PRODUTO = [
    "Forros PVC", "Forros Gesso", "Divisórias Eucatex", 
    "Divisórias Drywall", "Perfis Alumínio", "Parafusos",
    "Ferragens", "Acessórios"
]

CATEGORIAS_SERVICO = [
    "Instalação de Forro", "Instalação de Divisória",
    "Manutenção", "Pintura", "Acabamento", "Desmontagem"
]

UNIDADES_MEDIDA = [
    "UN",      # Unidade
    "M²",      # Metro quadrado
    "M",       # Metro linear
    "KG",      # Quilograma
    "HR",      # Hora (para serviços)
    "CX",      # Caixa
    "PC",      # Peça
    "L",       # Litro
    "KIT"      # Kit
]