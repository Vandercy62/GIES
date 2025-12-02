"""
SISTEMA ERP PRIMOTEX - API PRINCIPAL ROBUSTA
===========================================

API FastAPI com sistema robusto de inicialização e recuperação de erros.
Garante estabilidade máxima do backend.

Autor: GitHub Copilot
Data: 17/11/2025
Versão: 2.0 - ROBUSTO
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import sys
import traceback
from datetime import datetime
from typing import Dict, Any

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("backend.main")

# Estado global do sistema
system_state: Dict[str, Any] = {
    "initialized": False,
    "database_connected": False,
    "routers_loaded": {},
    "startup_time": None,
    "errors": []
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida do FastAPI
    Substitui @app.on_event("startup") e @app.on_event("shutdown")
    """
    # ========== STARTUP ==========
    logger.info("="*70)
    logger.info("🚀 INICIANDO BACKEND ERP PRIMOTEX v2.0 - ROBUSTO")
    logger.info("="*70)
    
    try:
        # 1. Validar dependências
        logger.info("📋 Etapa 1/5: Validando dependências...")
        from backend.api.startup_validator import validate_startup
        
        if not validate_startup():
            logger.error("❌ Validação falhou - Backend não pode iniciar")
            system_state["errors"].append("Validação de dependências falhou")
            # Não levanta exceção - permite /health funcionar
        else:
            logger.info("✅ Validação de dependências concluída")
        
        # 2. Inicializar banco de dados
        logger.info("📋 Etapa 2/5: Inicializando banco de dados...")
        try:
            from backend.database.config import engine
            from backend.models import create_all_tables
            from sqlalchemy import text  # FIX: Adicionar text wrapper
            
            # Testar conexão
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))  # FIX: Usar text() wrapper
            
            logger.info("   ✅ Conexão com banco estabelecida")
            system_state["database_connected"] = True
            
            # Criar tabelas
            if create_all_tables(engine):
                logger.info("   ✅ Tabelas criadas/verificadas")
            else:
                logger.warning("   ⚠️  Problema ao criar tabelas (continuando...)")
                
        except Exception as e:
            logger.error(f"   ❌ Erro no banco de dados: {e}")
            system_state["errors"].append(f"Database: {str(e)}")
            system_state["database_connected"] = False
        
        # 3. Criar usuário admin padrão
        logger.info("📋 Etapa 3/5: Verificando usuário admin...")
        try:
            from backend.database.config import SessionLocal
            from backend.models.user_model import Usuario
            from backend.auth.jwt_handler import hash_password
            
            db = SessionLocal()
            try:
                admin = db.query(Usuario).filter(Usuario.username == "admin").first()
                if not admin:
                    admin = Usuario(
                        username="admin",
                        email="admin@primotex.com.br",
                        senha_hash=hash_password("admin123"),
                        nome_completo="Administrador do Sistema",
                        perfil="administrador",
                        ativo=True
                    )
                    db.add(admin)
                    db.commit()
                    logger.info("   ✅ Usuário admin criado (admin/admin123)")
                else:
                    logger.info("   ✅ Usuário admin já existe")
            finally:
                db.close()
                
        except Exception as e:
            logger.warning(f"   ⚠️  Não foi possível criar admin: {e}")
        
        # 4. Carregar routers (com fallback)
        logger.info("📋 Etapa 4/5: Carregando routers...")
        load_routers_safe(app)
        
        # 5. Finalizar startup
        system_state["initialized"] = True
        system_state["startup_time"] = datetime.now()
        
        logger.info("="*70)
        logger.info("✅ BACKEND INICIADO COM SUCESSO!")
        logger.info(f"📍 Tempo de inicialização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📊 Routers carregados: {sum(1 for v in system_state['routers_loaded'].values() if v)}/{len(system_state['routers_loaded'])}")
        logger.info(f"🔗 Database: {'CONECTADO' if system_state['database_connected'] else 'DESCONECTADO'}")
        logger.info("="*70)
        
    except Exception as e:
        logger.error("="*70)
        logger.error(f"❌ ERRO CRÍTICO NO STARTUP: {e}")
        logger.error("="*70)
        traceback.print_exc()
        system_state["errors"].append(f"Startup crítico: {str(e)}")
    
    yield  # Servidor roda aqui
    
    # ========== SHUTDOWN ==========
    logger.info("="*70)
    logger.info("🛑 ENCERRANDO BACKEND ERP PRIMOTEX")
    logger.info("="*70)
    
    try:
        # Fechar conexões de banco
        from backend.database.config import engine
        engine.dispose()
        logger.info("✅ Conexões de banco fechadas")
    except Exception as e:
        logger.error(f"❌ Erro ao fechar banco: {e}")
    
    logger.info("👋 Backend encerrado")


# Criar instância FastAPI com lifespan
app = FastAPI(
    title="Sistema ERP Primotex",
    description="""
    Sistema de Gerenciamento Empresarial Integrado - **VERSÃO ROBUSTA**
    
    **Primotex - Forros e Divisórias Eireli**
    
    Este sistema oferece controle completo sobre:
    - 👥 Cadastros (Clientes, Fornecedores, Colaboradores, Produtos)
    - ⚙️ Fluxo Operacional (OS completa com 7 fases)
    - 📦 Controle de Estoque
    - 💰 Gestão Financeira
    - 📱 Comunicação Automática
    - 📊 Relatórios e Dashboards
    
    **Novidades v2.0:**
    - ✅ Sistema robusto de inicialização
    - ✅ Validação automática de dependências
    - ✅ Recuperação automática de erros
    - ✅ Health check detalhado
    - ✅ Logs estruturados
    """,
    version="2.0.0",
    contact={
        "name": "Primotex - Forros e Divisórias Eireli",
        "email": "contato@primotex.com.br",
    },
    lifespan=lifespan  # Usar lifespan manager
)

# =======================================
# MIDDLEWARE DE TRATAMENTO DE ERROS
# =======================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    logger.error(f"❌ Erro não tratado: {exc}")
    logger.error(f"   URL: {request.url}")
    logger.error(f"   Método: {request.method}")
    traceback.print_exc()
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Erro interno do servidor",
            "detail": str(exc),
            "type": type(exc).__name__,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação"""
    logger.warning(f"⚠️  Erro de validação: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Erro de validação",
            "detail": exc.errors(),
            "body": exc.body
        }
    )

# =======================================
# MIDDLEWARE CORS
# =======================================

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
        "versao": "2.0.0 - ROBUSTO",
        "empresa": "Primotex - Forros e Divisórias Eireli",
        "status": "running" if system_state["initialized"] else "initializing",
        "database": "connected" if system_state["database_connected"] else "disconnected",
        "startup_time": system_state["startup_time"].isoformat() if system_state["startup_time"] else None,
        "routers_loaded": sum(1 for v in system_state["routers_loaded"].values() if v),
        "total_routers": len(system_state["routers_loaded"]),
        "endpoints_disponiveis": [
            "/docs - Documentação interativa",
            "/redoc - Documentação alternativa",
            "/health - Status detalhado do sistema",
            "/api/v1/* - Endpoints da API"
        ]
    }

@app.get("/health", tags=["Sistema"])
async def health_check():
    """Health check detalhado do sistema"""
    try:
        # Verificar banco de dados
        db_status = "healthy"
        db_latency = None
        
        if system_state["database_connected"]:
            try:
                from backend.database.config import engine
                from sqlalchemy import text  # FIX: Adicionar text wrapper
                import time
                
                start = time.time()
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))  # FIX: Usar text() wrapper
                db_latency = round((time.time() - start) * 1000, 2)  # ms
                
            except Exception as e:
                db_status = "unhealthy"
                logger.error(f"Health check DB falhou: {e}")
        else:
            db_status = "disconnected"
        
        # Status geral
        overall_status = "healthy" if system_state["initialized"] and db_status == "healthy" else "degraded"
        
        uptime = None
        if system_state["startup_time"]:
            uptime_seconds = (datetime.now() - system_state["startup_time"]).total_seconds()
            uptime = f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "uptime": uptime,
            "database": {
                "status": db_status,
                "latency_ms": db_latency
            },
            "routers": {
                "loaded": sum(1 for v in system_state["routers_loaded"].values() if v),
                "total": len(system_state["routers_loaded"]),
                "details": system_state["routers_loaded"]
            },
            "errors": system_state["errors"] if system_state["errors"] else None,
            "version": "2.0.0"
        }
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# =======================================
# FUNÇÃO DE CARREGAMENTO SEGURO DE ROUTERS
# =======================================

def load_routers_safe(app: FastAPI):
    """
    Carregar routers com fallback - se um falhar, outros continuam
    """
    routers_config = [
        ("auth", "backend.api.routers.auth_router", "/api/v1", ["Autenticação"]),
        ("cliente", "backend.api.routers.cliente_router", "/api/v1", ["Clientes"]),
        ("produto", "backend.api.routers.produto_router", "/api/v1", ["Produtos"]),
        ("fornecedor", "backend.api.routers.fornecedor_router", "/api/v1", ["Fornecedores"]),
        ("colaborador", "backend.api.routers.colaborador_router", "/api/v1", ["Colaboradores"]),
        ("ordem_servico", "backend.api.routers.ordem_servico_router", "/api/v1", ["Ordem de Serviço"]),
        ("agendamento", "backend.api.routers.agendamento_router", "/api/v1", ["Agendamento"]),
        ("financeiro", "backend.api.routers.financeiro_router", "/api/v1", ["Financeiro"]),
        ("comunicacao", "backend.api.routers.comunicacao_router", "/api/v1", ["Comunicação"]),
        ("whatsapp", "backend.api.routers.whatsapp_router", "/api/v1", ["WhatsApp"])
    ]
    
    for name, module_path, prefix, tags in routers_config:
        try:
            # Importar router
            module = __import__(module_path, fromlist=['router'])
            router = getattr(module, 'router')
            
            # Incluir no app
            app.include_router(router, prefix=prefix, tags=tags)
            
            system_state["routers_loaded"][name] = True
            logger.info(f"   ✅ Router '{name}' carregado")
            
        except Exception as e:
            system_state["routers_loaded"][name] = False
            error_msg = f"Router '{name}' falhou: {str(e)[:100]}"
            system_state["errors"].append(error_msg)
            logger.error(f"   ❌ {error_msg}")
            
            # Continuar mesmo com erro
            continue

# =======================================
# ENDPOINTS MOCK PARA DESENVOLVIMENTO
# =======================================

@app.get("/api/v1/cadastros/clientes", tags=["Cadastros"])
async def listar_clientes_mock():
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
        }
    ]
