"""
SISTEMA ERP PRIMOTEX - MODELOS DO BANCO DE DADOS
===============================================

Este arquivo importa todos os modelos do sistema para facilitar
o uso em outros módulos e garantir que as tabelas sejam criadas
corretamente pelo SQLAlchemy.

MODELOS DISPONÍVEIS:
- Usuario: Usuários do sistema (autenticação)
- Cliente: Clientes da empresa
- Produto: Produtos e serviços
- OrdemServico: Ordem de serviço principal
- OSItem: Itens da ordem de serviço
- OSHistorico: Histórico de mudanças de status

Autor: GitHub Copilot
Data: 29/10/2025
"""

# Importar a base do SQLAlchemy
from backend.database.config import Base

# =======================================
# IMPORTAR TODOS OS MODELOS
# =======================================

# Modelo de usuários (autenticação)
from .user_model import Usuario, PERFIS_SISTEMA

# Modelo de clientes
from .cliente_model import (
    Cliente, 
    TIPOS_PESSOA, 
    STATUS_CLIENTE, 
    ORIGENS_CLIENTE, 
    TIPOS_CLIENTE
)

# Modelo de produtos e serviços
from .produto_model import (
    Produto,
    TIPOS_PRODUTO,
    STATUS_PRODUTO,
    CATEGORIAS_PRODUTO,
    CATEGORIAS_SERVICO,
    UNIDADES_MEDIDA
)

# Modelo de fornecedores
from .fornecedor_model import (
    Fornecedor,
    CATEGORIAS_FORNECEDOR,
    TIPOS_FORNECEDOR,
    STATUS_FORNECEDOR,
    PORTES_EMPRESA
)

# Modelo de colaboradores
from .colaborador_model import (
    Colaborador,
    Departamento,
    Cargo,
    ColaboradorDocumento,
    AvaliacaoDesempenho,
    PontoEletronico,
    PeriodoFerias,
    TipoContrato,
    StatusColaborador,
    NivelEscolaridade,
    TipoDocumento
)

# Modelos de ordem de serviço (Fase 3)
from .ordem_servico_model import (
    OrdemServico,
    FaseOS,
    VisitaTecnica,
    Orcamento,
    FASES_OS,
    STATUS_FASES,
    STATUS_OS,
    TIPOS_SERVICO
)

# Modelos de agendamento (Fase 3)
from .agendamento_model import (
    Agendamento,
    ConfiguracaoAgenda,
    DisponibilidadeUsuario,
    BloqueioAgenda,
    TIPOS_EVENTO,
    STATUS_AGENDAMENTO,
    TIPOS_RECORRENCIA,
    PRIORIDADES,
    CATEGORIAS_EVENTO
)

# Modelos financeiros (Fase 3)
from .financeiro_model import (
    ContaReceber,
    ContaPagar,
    MovimentacaoFinanceira,
    FluxoCaixa,
    CategoriaFinanceira,
    STATUS_CONTA,
    FORMAS_PAGAMENTO,
    TIPOS_CONTA_PAGAR,
    CATEGORIAS_RECEITA,
    CATEGORIAS_DESPESA
)

# Modelos de comunicação (Fase 3)
from .comunicacao import (
    ComunicacaoTemplate,
    ComunicacaoHistorico,
    ComunicacaoConfig,
    ComunicacaoFila,
    ComunicacaoEstatisticas,
    TIPOS_COMUNICACAO,
    STATUS_ENVIO,
    TIPOS_TEMPLATE,
    PRIORIDADE_ENVIO,
    CANAIS_COMUNICACAO
)

# =======================================
# LISTA DE TODOS OS MODELOS
# =======================================

# Esta lista é usada para criar todas as tabelas
ALL_MODELS = [
    Usuario,
    Cliente,
    Produto,
    Fornecedor,
    Colaborador,
    Departamento,
    Cargo,
    ColaboradorDocumento,
    AvaliacaoDesempenho,
    PontoEletronico,
    PeriodoFerias,
    OrdemServico,
    FaseOS,
    VisitaTecnica,
    Orcamento,
    Agendamento,
    ConfiguracaoAgenda,
    DisponibilidadeUsuario,
    BloqueioAgenda,
    ContaReceber,
    ContaPagar,
    MovimentacaoFinanceira,
    FluxoCaixa,
    CategoriaFinanceira,
    ComunicacaoTemplate,
    ComunicacaoHistorico,
    ComunicacaoConfig,
    ComunicacaoFila,
    ComunicacaoEstatisticas
]

# =======================================
# FUNÇÃO PARA CRIAR TODAS AS TABELAS
# =======================================

def create_all_tables(engine):
    """
    Criar todas as tabelas no banco de dados.
    
    Args:
        engine: Engine do SQLAlchemy
    """
    try:
        # Criar todas as tabelas baseadas nos modelos
        Base.metadata.create_all(bind=engine)
        print("✅ Todas as tabelas criadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

# =======================================
# FUNÇÃO PARA LISTAR TODAS AS TABELAS
# =======================================

def get_table_names():
    """Retorna lista com nomes de todas as tabelas"""
    return [model.__tablename__ for model in ALL_MODELS]

# =======================================
# FUNÇÃO PARA VERIFICAR MODELOS
# =======================================

def validate_models():
    """
    Valida se todos os modelos estão corretos.
    Retorna dicionário com informações.
    """
    models_info = {}
    
    for model in ALL_MODELS:
        models_info[model.__name__] = {
            "table_name": model.__tablename__,
            "columns": len(model.__table__.columns) if hasattr(model, '__table__') else 0,
            "has_primary_key": any(col.primary_key for col in model.__table__.columns) if hasattr(model, '__table__') else False
        }
    
    return models_info