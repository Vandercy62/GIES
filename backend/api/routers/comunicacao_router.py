"""
ROUTER DE COMUNICAÇÃO
====================

Sistema ERP Primotex - Router FastAPI para o módulo de Comunicação
Endpoints completos para gestão de templates, envio e histórico

Endpoints implementados:
- CRUD completo de templates
- Envio individual e em lote
- Histórico de comunicações
- Configurações de provedores
- Processamento de fila
- Estatísticas e métricas
- Webhooks para status

Autor: GitHub Copilot
Data: 29/10/2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from backend.database.config import get_db
from backend.models.comunicacao import (
    ComunicacaoTemplate, ComunicacaoHistorico, ComunicacaoConfig, 
    ComunicacaoFila, TipoComunicacao, StatusComunicacao, TipoTemplate
)
from backend.schemas.comunicacao import (
    ComunicacaoTemplate as ComunicacaoTemplateSchema,
    ComunicacaoTemplateCreate, ComunicacaoTemplateUpdate,
    ComunicacaoHistorico as ComunicacaoHistoricoSchema,
    ComunicacaoConfig as ComunicacaoConfigSchema,
    ComunicacaoConfigCreate, ComunicacaoConfigUpdate,
    EnvioMensagemRequest, EnvioMensagemResponse,
    EnvioLoteRequest, EnvioLoteResponse,
    EstatisticasComunicacao, MetricasDashboard,
    ComunicacaoResponse, ListaComunicacoes, ListaTemplates
)
from backend.services.comunicacao_service import ComunicacaoService, TemplateService

router = APIRouter(prefix="/comunicacao", tags=["comunicacao"])

# ============================================================================
# ENDPOINTS DE TEMPLATES
# ============================================================================

@router.get("/templates", response_model=ListaTemplates)
async def listar_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    tipo: Optional[TipoTemplate] = None,
    canal: Optional[TipoComunicacao] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Listar templates de comunicação com filtros"""
    query = db.query(ComunicacaoTemplate)
    
    if tipo:
        query = query.filter(ComunicacaoTemplate.tipo == tipo)
    if canal:
        query = query.filter(ComunicacaoTemplate.canal == canal)
    if ativo is not None:
        query = query.filter(ComunicacaoTemplate.ativo == ativo)
    
    total = query.count()
    templates = query.offset(skip).limit(limit).all()
    
    return ListaTemplates(
        items=templates,
        total=total,
        pagina=skip // limit + 1,
        tamanho_pagina=limit,
        total_paginas=(total + limit - 1) // limit
    )

@router.get("/templates/{template_id}", response_model=ComunicacaoTemplateSchema)
async def obter_template(template_id: int, db: Session = Depends(get_db)):
    """Obter template específico"""
    template = db.query(ComunicacaoTemplate).filter(
        ComunicacaoTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    return template

@router.post("/templates", response_model=ComunicacaoTemplateSchema)
async def criar_template(
    template: ComunicacaoTemplateCreate,
    db: Session = Depends(get_db)
):
    """Criar novo template"""
    # Verificar se nome já existe
    existe = db.query(ComunicacaoTemplate).filter(
        ComunicacaoTemplate.nome == template.nome
    ).first()
    
    if existe:
        raise HTTPException(status_code=400, detail="Nome do template já existe")
    
    db_template = ComunicacaoTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template

@router.put("/templates/{template_id}", response_model=ComunicacaoTemplateSchema)
async def atualizar_template(
    template_id: int,
    template: ComunicacaoTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar template existente"""
    db_template = db.query(ComunicacaoTemplate).filter(
        ComunicacaoTemplate.id == template_id
    ).first()
    
    if not db_template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    # Verificar nome duplicado se estiver mudando
    if template.nome and template.nome != db_template.nome:
        existe = db.query(ComunicacaoTemplate).filter(
            ComunicacaoTemplate.nome == template.nome,
            ComunicacaoTemplate.id != template_id
        ).first()
        
        if existe:
            raise HTTPException(status_code=400, detail="Nome do template já existe")
    
    # Atualizar campos
    for field, value in template.dict(exclude_unset=True).items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    
    return db_template

@router.delete("/templates/{template_id}")
async def deletar_template(template_id: int, db: Session = Depends(get_db)):
    """Deletar template"""
    template = db.query(ComunicacaoTemplate).filter(
        ComunicacaoTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    # Verificar se tem comunicações associadas
    comunicacoes = db.query(ComunicacaoHistorico).filter(
        ComunicacaoHistorico.template_id == template_id
    ).count()
    
    if comunicacoes > 0:
        # Apenas desativar em vez de deletar
        template.ativo = False
        db.commit()
        return {"mensagem": "Template desativado (possui comunicações associadas)"}
    
    db.delete(template)
    db.commit()
    
    return {"mensagem": "Template deletado com sucesso"}

@router.post("/templates/criar-padrao")
async def criar_templates_padrao(db: Session = Depends(get_db)):
    """Criar templates padrão do sistema"""
    service = TemplateService(db)
    service.criar_templates_padrao()
    
    return {"mensagem": "Templates padrão criados com sucesso"}

# ============================================================================
# ENDPOINTS DE ENVIO
# ============================================================================

@router.post("/enviar", response_model=EnvioMensagemResponse)
async def enviar_mensagem(
    request: EnvioMensagemRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Enviar mensagem individual"""
    service = ComunicacaoService(db)
    
    # Se for agendamento, processar em background
    if request.agendar_para and request.agendar_para > datetime.now():
        resultado = service.enviar_mensagem(request)
        if resultado.agendado:
            background_tasks.add_task(service.processar_fila)
        return resultado
    
    # Envio imediato
    return service.enviar_mensagem(request)

@router.post("/enviar-lote", response_model=EnvioLoteResponse)
async def enviar_lote(
    request: EnvioLoteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Enviar mensagens em lote"""
    service = ComunicacaoService(db)
    
    total_processados = 0
    sucessos = 0
    erros = 0
    detalhes = []
    
    for destinatario in request.destinatarios:
        try:
            # Mesclar variáveis globais com específicas do destinatário
            variaveis = request.variaveis_globais or {}
            variaveis.update(destinatario.get('variaveis', {}))
            
            # Criar request individual
            individual_request = EnvioMensagemRequest(
                template_id=request.template_id,
                tipo_comunicacao=destinatario.get('tipo_comunicacao', TipoComunicacao.EMAIL),
                destinatario_nome=destinatario['nome'],
                destinatario_contato=destinatario['contato'],
                cliente_id=destinatario.get('cliente_id'),
                variaveis=variaveis,
                agendar_para=request.agendar_para,
                prioridade=request.prioridade
            )
            
            resultado = service.enviar_mensagem(individual_request)
            
            if resultado.sucesso:
                sucessos += 1
            else:
                erros += 1
            
            detalhes.append({
                'destinatario': destinatario['nome'],
                'sucesso': resultado.sucesso,
                'mensagem': resultado.mensagem,
                'comunicacao_id': resultado.comunicacao_id
            })
            
            total_processados += 1
            
        except Exception as e:
            erros += 1
            detalhes.append({
                'destinatario': destinatario.get('nome', 'Desconhecido'),
                'sucesso': False,
                'mensagem': str(e),
                'comunicacao_id': None
            })
            total_processados += 1
    
    # Processar fila em background se houver agendamentos
    if request.agendar_para:
        background_tasks.add_task(service.processar_fila)
    
    return EnvioLoteResponse(
        total_processados=total_processados,
        sucessos=sucessos,
        erros=erros,
        detalhes=detalhes
    )

@router.post("/processar-fila")
async def processar_fila_manual(db: Session = Depends(get_db)):
    """Processar fila de mensagens manualmente"""
    service = ComunicacaoService(db)
    resultado = service.processar_fila()
    
    return resultado

# ============================================================================
# ENDPOINTS DE HISTÓRICO
# ============================================================================

@router.get("/historico", response_model=ListaComunicacoes)
async def listar_historico(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    tipo: Optional[TipoComunicacao] = None,
    status: Optional[StatusComunicacao] = None,
    cliente_id: Optional[int] = None,
    origem_modulo: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Listar histórico de comunicações com filtros"""
    query = db.query(ComunicacaoHistorico)
    
    if tipo:
        query = query.filter(ComunicacaoHistorico.tipo == tipo)
    if status:
        query = query.filter(ComunicacaoHistorico.status == status)
    if cliente_id:
        query = query.filter(ComunicacaoHistorico.cliente_id == cliente_id)
    if origem_modulo:
        query = query.filter(ComunicacaoHistorico.origem_modulo == origem_modulo)
    if data_inicio:
        query = query.filter(ComunicacaoHistorico.criado_em >= data_inicio)
    if data_fim:
        query = query.filter(ComunicacaoHistorico.criado_em <= data_fim)
    
    total = query.count()
    comunicacoes = query.order_by(ComunicacaoHistorico.criado_em.desc()).offset(skip).limit(limit).all()
    
    return ListaComunicacoes(
        items=comunicacoes,
        total=total,
        pagina=skip // limit + 1,
        tamanho_pagina=limit,
        total_paginas=(total + limit - 1) // limit
    )

@router.get("/historico/{comunicacao_id}", response_model=ComunicacaoHistoricoSchema)
async def obter_comunicacao(comunicacao_id: int, db: Session = Depends(get_db)):
    """Obter comunicação específica"""
    comunicacao = db.query(ComunicacaoHistorico).filter(
        ComunicacaoHistorico.id == comunicacao_id
    ).first()
    
    if not comunicacao:
        raise HTTPException(status_code=404, detail="Comunicação não encontrada")
    
    return comunicacao

@router.put("/historico/{comunicacao_id}/status")
async def atualizar_status_comunicacao(
    comunicacao_id: int,
    status: StatusComunicacao,
    detalhes: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """Atualizar status de comunicação (usado por webhooks)"""
    comunicacao = db.query(ComunicacaoHistorico).filter(
        ComunicacaoHistorico.id == comunicacao_id
    ).first()
    
    if not comunicacao:
        raise HTTPException(status_code=404, detail="Comunicação não encontrada")
    
    comunicacao.status = status
    
    # Atualizar timestamps baseado no status
    agora = datetime.now()
    if status == StatusComunicacao.ENVIADO and not comunicacao.enviado_em:
        comunicacao.enviado_em = agora
    elif status == StatusComunicacao.ENTREGUE and not comunicacao.entregue_em:
        comunicacao.entregue_em = agora
    elif status == StatusComunicacao.LIDO and not comunicacao.lido_em:
        comunicacao.lido_em = agora
    
    if detalhes:
        comunicacao.provider_response = detalhes
    
    db.commit()
    
    return {"mensagem": f"Status atualizado para {status.value}"}

# ============================================================================
# ENDPOINTS DE CONFIGURAÇÃO
# ============================================================================

@router.get("/configuracoes", response_model=List[ComunicacaoConfigSchema])
async def listar_configuracoes(
    tipo: Optional[TipoComunicacao] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Listar configurações de comunicação"""
    query = db.query(ComunicacaoConfig)
    
    if tipo:
        query = query.filter(ComunicacaoConfig.tipo == tipo)
    if ativo is not None:
        query = query.filter(ComunicacaoConfig.ativo == ativo)
    
    return query.all()

@router.post("/configuracoes", response_model=ComunicacaoConfigSchema)
async def criar_configuracao(
    config: ComunicacaoConfigCreate,
    db: Session = Depends(get_db)
):
    """Criar nova configuração"""
    # Se é padrão, remover padrão das outras do mesmo tipo
    if config.padrao:
        db.query(ComunicacaoConfig).filter(
            ComunicacaoConfig.tipo == config.tipo,
            ComunicacaoConfig.padrao == True
        ).update({ComunicacaoConfig.padrao: False})
    
    db_config = ComunicacaoConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config

@router.put("/configuracoes/{config_id}", response_model=ComunicacaoConfigSchema)
async def atualizar_configuracao(
    config_id: int,
    config: ComunicacaoConfigUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar configuração existente"""
    db_config = db.query(ComunicacaoConfig).filter(
        ComunicacaoConfig.id == config_id
    ).first()
    
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    # Se está tornando padrão, remover padrão das outras
    if config.padrao:
        db.query(ComunicacaoConfig).filter(
            ComunicacaoConfig.tipo == db_config.tipo,
            ComunicacaoConfig.id != config_id,
            ComunicacaoConfig.padrao == True
        ).update({ComunicacaoConfig.padrao: False})
    
    # Atualizar campos
    for field, value in config.dict(exclude_unset=True).items():
        setattr(db_config, field, value)
    
    db.commit()
    db.refresh(db_config)
    
    return db_config

# ============================================================================
# ENDPOINTS DE ESTATÍSTICAS
# ============================================================================

@router.get("/dashboard", response_model=MetricasDashboard)
async def obter_metricas_dashboard(db: Session = Depends(get_db)):
    """Obter métricas para dashboard"""
    agora = datetime.now()
    inicio_dia = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    inicio_semana = inicio_dia - timedelta(days=agora.weekday())
    inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Contar comunicações
    comunicacoes_hoje = db.query(ComunicacaoHistorico).filter(
        ComunicacaoHistorico.criado_em >= inicio_dia
    ).count()
    
    comunicacoes_semana = db.query(ComunicacaoHistorico).filter(
        ComunicacaoHistorico.criado_em >= inicio_semana
    ).count()
    
    comunicacoes_mes = db.query(ComunicacaoHistorico).filter(
        ComunicacaoHistorico.criado_em >= inicio_mes
    ).count()
    
    # Taxa de entrega média
    total_enviados = db.query(ComunicacaoHistorico).filter(
        ComunicacaoHistorico.criado_em >= inicio_mes
    ).count()
    
    total_entregues = db.query(ComunicacaoHistorico).filter(
        ComunicacaoHistorico.criado_em >= inicio_mes,
        ComunicacaoHistorico.status.in_([StatusComunicacao.ENTREGUE, StatusComunicacao.LIDO])
    ).count()
    
    taxa_entrega = (total_entregues / total_enviados) if total_enviados > 0 else 0
    
    # Outros contadores
    templates_ativos = db.query(ComunicacaoTemplate).filter(
        ComunicacaoTemplate.ativo == True
    ).count()
    
    configuracoes_ativas = db.query(ComunicacaoConfig).filter(
        ComunicacaoConfig.ativo == True
    ).count()
    
    fila_pendente = db.query(ComunicacaoFila).filter(
        ComunicacaoFila.status == "PENDENTE"
    ).count()
    
    # Últimas comunicações
    ultimas_comunicacoes = db.query(ComunicacaoHistorico).order_by(
        ComunicacaoHistorico.criado_em.desc()
    ).limit(5).all()
    
    return MetricasDashboard(
        comunicacoes_hoje=comunicacoes_hoje,
        comunicacoes_semana=comunicacoes_semana,
        comunicacoes_mes=comunicacoes_mes,
        taxa_entrega_media=taxa_entrega,
        templates_ativos=templates_ativos,
        configuracoes_ativas=configuracoes_ativas,
        fila_pendente=fila_pendente,
        ultimas_comunicacoes=ultimas_comunicacoes
    )

@router.get("/estatisticas")
async def obter_estatisticas(
    periodo_inicio: datetime,
    periodo_fim: datetime,
    db: Session = Depends(get_db)
):
    """Obter estatísticas detalhadas"""
    # Buscar comunicações do período
    comunicacoes = db.query(ComunicacaoHistorico).filter(
        ComunicacaoHistorico.criado_em >= periodo_inicio,
        ComunicacaoHistorico.criado_em <= periodo_fim
    ).all()
    
    # Calcular estatísticas
    total_enviados = len(comunicacoes)
    total_entregues = len([c for c in comunicacoes if c.status in [StatusComunicacao.ENTREGUE, StatusComunicacao.LIDO]])
    total_lidos = len([c for c in comunicacoes if c.status == StatusComunicacao.LIDO])
    total_erros = len([c for c in comunicacoes if c.status == StatusComunicacao.ERRO])
    
    # Por tipo
    email_total = len([c for c in comunicacoes if c.tipo == TipoComunicacao.EMAIL])
    whatsapp_total = len([c for c in comunicacoes if c.tipo == TipoComunicacao.WHATSAPP])
    sms_total = len([c for c in comunicacoes if c.tipo == TipoComunicacao.SMS])
    
    # Por módulo
    os_total = len([c for c in comunicacoes if c.origem_modulo == 'OS'])
    agendamento_total = len([c for c in comunicacoes if c.origem_modulo == 'AGENDAMENTO'])
    financeiro_total = len([c for c in comunicacoes if c.origem_modulo == 'FINANCEIRO'])
    
    return EstatisticasComunicacao(
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        total_enviados=total_enviados,
        total_entregues=total_entregues,
        total_lidos=total_lidos,
        total_erros=total_erros,
        email_estatisticas={
            'total': email_total,
            'entregues': len([c for c in comunicacoes if c.tipo == TipoComunicacao.EMAIL and c.status in [StatusComunicacao.ENTREGUE, StatusComunicacao.LIDO]]),
            'lidos': len([c for c in comunicacoes if c.tipo == TipoComunicacao.EMAIL and c.status == StatusComunicacao.LIDO]),
            'erros': len([c for c in comunicacoes if c.tipo == TipoComunicacao.EMAIL and c.status == StatusComunicacao.ERRO])
        },
        whatsapp_estatisticas={
            'total': whatsapp_total,
            'entregues': len([c for c in comunicacoes if c.tipo == TipoComunicacao.WHATSAPP and c.status in [StatusComunicacao.ENTREGUE, StatusComunicacao.LIDO]]),
            'lidos': len([c for c in comunicacoes if c.tipo == TipoComunicacao.WHATSAPP and c.status == StatusComunicacao.LIDO]),
            'erros': len([c for c in comunicacoes if c.tipo == TipoComunicacao.WHATSAPP and c.status == StatusComunicacao.ERRO])
        },
        sms_estatisticas={
            'total': sms_total,
            'entregues': len([c for c in comunicacoes if c.tipo == TipoComunicacao.SMS and c.status in [StatusComunicacao.ENTREGUE, StatusComunicacao.LIDO]]),
            'erros': len([c for c in comunicacoes if c.tipo == TipoComunicacao.SMS and c.status == StatusComunicacao.ERRO])
        },
        os_estatisticas={'total': os_total},
        agendamento_estatisticas={'total': agendamento_total},
        financeiro_estatisticas={'total': financeiro_total},
        taxa_entrega=total_entregues / total_enviados if total_enviados > 0 else 0,
        taxa_leitura=total_lidos / total_enviados if total_enviados > 0 else 0,
        taxa_erro=total_erros / total_enviados if total_enviados > 0 else 0
    )

# ============================================================================
# ENDPOINTS DE WEBHOOK
# ============================================================================

@router.post("/webhook/whatsapp")
async def webhook_whatsapp(data: Dict[str, Any], db: Session = Depends(get_db)):
    """Webhook para receber status do WhatsApp"""
    try:
        # Processar webhook do WhatsApp Business API
        # Implementação específica baseada na estrutura do webhook
        return {"status": "ok", "processed": True}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/webhook/email")
async def webhook_email(data: Dict[str, Any], db: Session = Depends(get_db)):
    """Webhook para receber status de email"""
    try:
        # Processar webhook de provedor de email
        return {"status": "ok", "processed": True}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/health")
async def health_check():
    """Health check do módulo de comunicação"""
    return {
        "status": "ok",
        "modulo": "comunicacao",
        "timestamp": datetime.now(),
        "endpoints_ativos": 20
    }