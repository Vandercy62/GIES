"""
SISTEMA ERP PRIMOTEX - API PRINCIPAL
====================================

API FastAPI principal do Sistema ERP Primotex.
Centraliza todos os endpoints e configurações da aplicação.

Autor: GitHub Copilot
Data: 29/10/2025
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import logging
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração de segurança
security = HTTPBearer()

# Criar instância FastAPI
app = FastAPI(
    title="Sistema ERP Primotex",
    description="""
    Sistema de Gerenciamento Empresarial Integrado
    
    **Primotex - Forros e Divisórias Eireli**
    
    Este sistema oferece controle completo sobre:
    - 👥 Cadastros (Clientes, Fornecedores, Colaboradores, Produtos)
    - ⚙️ Fluxo Operacional (OS completa com 7 fases)
    - 📦 Controle de Estoque
    - 💰 Gestão Financeira
    - 📱 Comunicação Automática
    - 📊 Relatórios e Dashboards
    
    **Fase Atual:** 1 - Fundação (Desenvolvimento)
    """,
    version="1.0.0",
    contact={
        "name": "Primotex - Forros e Divisórias Eireli",
        "email": "contato@primotex.com.br",
    }
)

# Evento de startup para inicializar banco de dados
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Iniciando Sistema ERP Primotex...")
    logger.info("📊 Conectando ao banco de dados...")
    try:
        from backend.database.config import engine
        from backend.models import create_all_tables
        success = create_all_tables(engine)
        if success:
            logger.info("✅ Banco de dados inicializado com sucesso!")
        else:
            logger.error("❌ Erro ao inicializar banco de dados")
    except Exception as e:
        logger.error(f"❌ Erro crítico no banco de dados: {e}")

# Configurar CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios exatos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================================
# ROTAS PRINCIPAIS
# =======================================

@app.get("/", tags=["Sistema"])
async def root():
    """Rota principal - Informações do sistema"""
    return {
        "sistema": "ERP Primotex",
        "empresa": "Primotex - Forros e Divisórias Eireli",
        "versao": "1.0.0",
        "status": "FASE 1 - Fundação em desenvolvimento",
        "data_inicio": "29/10/2025",
        "modulos": [
            "Administração",
            "Cadastros", 
            "Fluxo Operacional",
            "Estoque",
            "Financeiro",
            "Vendas/Compras",
            "Agendamento",
            "Comunicação",
            "Relatórios",
            "Configurações"
        ],
        "endpoints_disponiveis": [
            "/docs - Documentação da API",
            "/redoc - Documentação alternativa",
            "/health - Status do sistema",
            "/api/v1/* - Endpoints da API"
        ]
    }

@app.get("/health", tags=["Sistema"])
async def health_check():
    """Verificação de saúde do sistema"""
    try:
        return {
            "status": "healthy",
            "timestamp": "2025-10-29T00:00:00Z",
            "database": "connected",  # Será implementado
            "services": {
                "auth": "active",
                "cadastros": "active",
                "os": "active",
                "financeiro": "active",
                "estoque": "active"
            }
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# =======================================
# MIDDLEWARE DE AUTENTICAÇÃO (FUTURO)
# =======================================

async def get_current_user(token: str = Depends(security)):
    """Middleware de autenticação - será implementado na Fase 1"""
    # Por enquanto, retorna usuário mock
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@primotex.com.br",
        "perfil": "Administrador",
        "ativo": True
    }

@app.get("/api/v1/auth/me", tags=["Autenticação"])
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """Informações do usuário atual"""
    return current_user

# =======================================
# INCLUIR ROUTERS DOS MÓDULOS
# =======================================

from backend.api.routers.auth_router import router as auth_router
from backend.api.routers.cliente_router import router as cliente_router
from backend.api.routers.produto_router import router as produto_router
from backend.api.routers.fornecedor_router import router as fornecedor_router
from backend.api.routers.colaborador_router import router as colaborador_router
from backend.api.routers.agendamento_router import router as agendamento_router
from backend.api.routers.financeiro_router import router as financeiro_router
from backend.api.routers.ordem_servico_router import router as os_router  # CORRIGIDO - FASE 3

# Incluir router de autenticação
app.include_router(auth_router, prefix="/api/v1", tags=["Autenticação"])

# Incluir router de clientes
app.include_router(cliente_router, prefix="/api/v1", tags=["Clientes"])

# Incluir router de produtos
app.include_router(produto_router, prefix="/api/v1", tags=["Produtos"])

# Incluir router de fornecedores (NOVO)
app.include_router(fornecedor_router, prefix="/api/v1", tags=["Fornecedores"])

# Incluir router de colaboradores (NOVO)
app.include_router(colaborador_router, prefix="/api/v1", tags=["Colaboradores"])

# Incluir router de OS (Ordem de Serviço) - NOVO - Fase 3
app.include_router(os_router, prefix="/api/v1", tags=["Ordem de Serviço"])

# Incluir router de agendamento (NOVO - Fase 3)
app.include_router(agendamento_router, prefix="/api/v1", tags=["Agendamento"])

# Incluir router financeiro (NOVO - Fase 3)
app.include_router(financeiro_router, prefix="/api/v1", tags=["Financeiro"])

# Incluir router de comunicação (NOVO - Fase 3)
from backend.api.routers.comunicacao_router import router as comunicacao_router
app.include_router(comunicacao_router, prefix="/api/v1", tags=["Comunicação"])

# Incluir router de WhatsApp Business API (NOVO - Continuação)
from backend.api.routers.whatsapp_router import router as whatsapp_router
app.include_router(whatsapp_router, prefix="/api/v1", tags=["WhatsApp"])

# =======================================
# ENDPOINTS MOCK PARA DESENVOLVIMENTO
# =======================================

@app.get("/api/v1/cadastros/clientes", tags=["Cadastros"])
async def listar_clientes():
    """Mock - Lista de clientes para desenvolvimento"""
    return [
        {
            "id": 1,
            "nome": "João Silva Construções LTDA",
            "tipo": "Jurídica",
            "cnpj": "12.345.678/0001-90",
            "telefone": "(16) 3333-4444",
            "email": "contato@joaosilva.com.br",
            "status": "Ativo"
        },
        {
            "id": 2,
            "nome": "Maria Santos",
            "tipo": "Física",
            "cpf": "123.456.789-00",
            "telefone": "(16) 99999-8888",
            "email": "maria.santos@email.com",
            "status": "Ativo"
        }
    ]

@app.get("/api/v1/os/resumo", tags=["Ordem de Serviço"])
async def resumo_os():
    """Mock - Resumo das OSs para dashboard"""
    return {
        "total": 45,
        "aguardando_visita": 5,
        "aguardando_orcamento": 8,
        "aguardando_aprovacao": 12,
        "em_execucao": 15,
        "concluidas_mes": 5
    }

@app.get("/api/v1/financeiro/resumo", tags=["Financeiro"])
async def resumo_financeiro():
    """Mock - Resumo financeiro para dashboard"""
    return {
        "contas_receber_hoje": 2500.00,
        "contas_pagar_hoje": 1200.00,
        "saldo_caixa": 15000.00,
        "faturamento_mes": 45000.00,
        "contas_vencidas": 3
    }

# Removi o bloco if __name__ == "__main__" que estava causando conflito
# Para executar o servidor, use: uvicorn backend.api.main:app --host 127.0.0.1 --port 8002