"""
ROUTER WHATSAPP BUSINESS API
===========================

Sistema ERP Primotex - Router específico para integração WhatsApp Business API
Endpoints dedicados para configuração, envio e webhook

Funcionalidades:
- Configuração de tokens e números WhatsApp
- Envio de mensagens texto e templates aprovados
- Webhook para recebimento de status
- Validação de número de telefone brasileiro
- Templates pré-aprovados Meta

Autor: GitHub Copilot
Data: 01/11/2025
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import json
import re
import requests

from backend.database.config import get_db
from backend.models.comunicacao import (
    ComunicacaoConfig, ComunicacaoHistorico, TipoComunicacao, StatusComunicacao
)

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

# ============================================================================
# CONFIGURAÇÃO WHATSAPP
# ============================================================================


@router.post("/configurar")
async def configurar_whatsapp(
    config: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Configurar WhatsApp Business API
    
    Campos obrigatórios:
    - token: Token permanente do WhatsApp Business API
    - numero_remetente: Número do telefone business (apenas números)
    - webhook_verify_token: Token para verificação do webhook
    - api_url: URL base da API (ex: https://graph.facebook.com/v18.0)
    """
    try:
        # Validar campos obrigatórios
        campos_obrigatorios = [
            'token', 'numero_remetente', 'webhook_verify_token', 'api_url'
        ]
        for campo in campos_obrigatorios:
            if campo not in config:
                raise HTTPException(
                    status_code=400,
                    detail=f"Campo obrigatório não informado: {campo}"
                )
        
        # Validar formato do número
        numero = re.sub(r'[^\d]', '', config['numero_remetente'])
        if len(numero) < 10 or len(numero) > 15:
            raise HTTPException(
                status_code=400,
                detail="Número de telefone inválido"
            )
        
        # Testar conectividade com a API
        teste_resultado = await testar_conectividade_whatsapp(config)
        if not teste_resultado['sucesso']:
            raise HTTPException(
                status_code=400,
                detail="Erro ao conectar com WhatsApp API: " +
                       teste_resultado['erro']
            )
        
        # Buscar configuração existente ou criar nova
        config_existente = db.query(ComunicacaoConfig).filter(
            ComunicacaoConfig.tipo == TipoComunicacao.WHATSAPP,
            ComunicacaoConfig.nome == "whatsapp_business_default"
        ).first()
        
        if config_existente:
            # Atualizar existente
            config_existente.configuracoes = config
            config_existente.ativo = True
            config_existente.atualizado_em = datetime.now()
            db.commit()
            
            return {
                "sucesso": True,
                "mensagem": "Configuração WhatsApp atualizada com sucesso",
                "teste_api": teste_resultado
            }
        else:
            # Criar nova configuração
            nova_config = ComunicacaoConfig(
                nome="whatsapp_business_default",
                tipo=TipoComunicacao.WHATSAPP,
                configuracoes=config,
                ativo=True,
                padrao=True
            )
            
            db.add(nova_config)
            db.commit()
            
            return {
                "sucesso": True,
                "mensagem": "Configuração WhatsApp criada com sucesso",
                "teste_api": teste_resultado
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.get("/configuracao")
async def obter_configuracao_whatsapp(db: Session = Depends(get_db)):
    """Obter configuração atual do WhatsApp"""
    config = db.query(ComunicacaoConfig).filter(
        ComunicacaoConfig.tipo == TipoComunicacao.WHATSAPP,
        ComunicacaoConfig.ativo == True,
        ComunicacaoConfig.padrao == True
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="Configuração WhatsApp não encontrada"
        )
    
    # Remover token da resposta por segurança
    config_segura = config.configuracoes.copy()
    if 'token' in config_segura:
        config_segura['token'] = config_segura['token'][:8] + "..." if len(config_segura['token']) > 8 else "***"
    
    return {
        "id": config.id,
        "nome": config.nome,
        "ativo": config.ativo,
        "configuracoes": config_segura,
        "criado_em": config.criado_em,
        "atualizado_em": config.atualizado_em
    }

@router.post("/testar")
async def testar_whatsapp(db: Session = Depends(get_db)):
    """Testar conectividade com WhatsApp Business API"""
    config = db.query(ComunicacaoConfig).filter(
        ComunicacaoConfig.tipo == TipoComunicacao.WHATSAPP,
        ComunicacaoConfig.ativo == True,
        ComunicacaoConfig.padrao == True
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="Configuração WhatsApp não encontrada"
        )
    
    resultado = await testar_conectividade_whatsapp(config.configuracoes)
    
    return resultado

# ============================================================================
# ENVIO DE MENSAGENS
# ============================================================================

@router.post("/enviar-mensagem")
async def enviar_mensagem_whatsapp(
    dados: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Enviar mensagem de texto via WhatsApp
    
    Campos:
    - telefone: Número do destinatário (formato brasileiro)
    - mensagem: Texto da mensagem
    - cliente_id: ID do cliente (opcional)
    """
    try:
        # Validar campos
        if 'telefone' not in dados or 'mensagem' not in dados:
            raise HTTPException(
                status_code=400,
                detail="Campos obrigatórios: telefone, mensagem"
            )
        
        # Buscar configuração WhatsApp
        config = db.query(ComunicacaoConfig).filter(
            ComunicacaoConfig.tipo == TipoComunicacao.WHATSAPP,
            ComunicacaoConfig.ativo == True,
            ComunicacaoConfig.padrao == True
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="WhatsApp não configurado"
            )
        
        cfg = config.configuracoes
        
        # Normalizar telefone
        telefone = normalizar_telefone_brasileiro(dados['telefone'])
        if not telefone:
            raise HTTPException(
                status_code=400,
                detail="Número de telefone inválido"
            )
        
        # Preparar payload para WhatsApp API
        payload = {
            "messaging_product": "whatsapp",
            "to": telefone,
            "type": "text",
            "text": {
                "body": dados['mensagem']
            }
        }
        
        headers = {
            'Authorization': f"Bearer {cfg['token']}",
            'Content-Type': 'application/json'
        }
        
        # Criar registro no histórico
        historico = ComunicacaoHistorico(
            tipo=TipoComunicacao.WHATSAPP,
            canal_usado="WHATSAPP_BUSINESS_API",
            destinatario_nome=dados.get('destinatario_nome', ''),
            destinatario_contato=dados['telefone'],
            cliente_id=dados.get('cliente_id'),
            conteudo_texto=dados['mensagem'],
            origem_modulo=dados.get('origem_modulo', 'MANUAL'),
            origem_id=dados.get('origem_id')
        )
        
        # Enviar para WhatsApp API
        response = requests.post(
            f"{cfg['api_url']}/{cfg['numero_remetente']}/messages",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id')
            
            # Atualizar histórico com sucesso
            historico.status = StatusComunicacao.ENVIADO
            historico.enviado_em = datetime.now()
            historico.provider_response = result
            
            db.add(historico)
            db.commit()
            
            return {
                "sucesso": True,
                "mensagem": "WhatsApp enviado com sucesso",
                "message_id": message_id,
                "telefone_normalizado": telefone,
                "historico_id": historico.id
            }
        else:
            # Erro na API
            error_response = response.text
            
            # Atualizar histórico com erro
            historico.status = StatusComunicacao.ERRO
            historico.erro_detalhes = f"API Error {response.status_code}: {error_response}"
            historico.provider_response = {"error": error_response, "status_code": response.status_code}
            
            db.add(historico)
            db.commit()
            
            raise HTTPException(
                status_code=400,
                detail=f"Erro na API WhatsApp: {response.status_code} - {error_response}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        # Erro geral
        if 'historico' in locals():
            historico.status = StatusComunicacao.ERRO
            historico.erro_detalhes = str(e)
            db.add(historico)
            db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/enviar-template")
async def enviar_template_whatsapp(
    dados: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Enviar template pré-aprovado via WhatsApp
    
    Campos:
    - telefone: Número do destinatário
    - template_name: Nome do template aprovado
    - parametros: Lista de parâmetros do template (opcional)
    """
    try:
        if 'telefone' not in dados or 'template_name' not in dados:
            raise HTTPException(
                status_code=400,
                detail="Campos obrigatórios: telefone, template_name"
            )
        
        # Buscar configuração
        config = db.query(ComunicacaoConfig).filter(
            ComunicacaoConfig.tipo == TipoComunicacao.WHATSAPP,
            ComunicacaoConfig.ativo == True,
            ComunicacaoConfig.padrao == True
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="WhatsApp não configurado")
        
        cfg = config.configuracoes
        telefone = normalizar_telefone_brasileiro(dados['telefone'])
        
        # Preparar payload do template
        payload = {
            "messaging_product": "whatsapp",
            "to": telefone,
            "type": "template",
            "template": {
                "name": dados['template_name'],
                "language": {
                    "code": "pt_BR"
                }
            }
        }
        
        # Adicionar parâmetros se fornecidos
        if 'parametros' in dados and dados['parametros']:
            payload["template"]["components"] = [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(param)} 
                        for param in dados['parametros']
                    ]
                }
            ]
        
        headers = {
            'Authorization': f"Bearer {cfg['token']}",
            'Content-Type': 'application/json'
        }
        
        # Enviar
        response = requests.post(
            f"{cfg['api_url']}/{cfg['numero_remetente']}/messages",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "sucesso": True,
                "mensagem": "Template WhatsApp enviado com sucesso",
                "message_id": result.get('messages', [{}])[0].get('id'),
                "telefone_normalizado": telefone
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Erro na API WhatsApp: {response.status_code} - {response.text}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ============================================================================
# WEBHOOK PARA STATUS
# ============================================================================

@router.get("/webhook")
async def verificar_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None,
    db: Session = Depends(get_db)
):
    """Verificação do webhook pelo WhatsApp"""
    # Buscar token de verificação
    config = db.query(ComunicacaoConfig).filter(
        ComunicacaoConfig.tipo == TipoComunicacao.WHATSAPP,
        ComunicacaoConfig.ativo == True
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    
    webhook_token = config.configuracoes.get('webhook_verify_token')
    
    if (hub_mode == "subscribe" and 
        hub_verify_token == webhook_token and 
        hub_challenge):
        return int(hub_challenge)
    
    raise HTTPException(status_code=403, detail="Token de verificação inválido")

@router.post("/webhook")
async def receber_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Receber atualizações de status do WhatsApp"""
    try:
        body = await request.body()
        data = json.loads(body)
        
        # Processar em background para resposta rápida
        background_tasks.add_task(processar_webhook_whatsapp, data, db)
        
        return {"status": "received"}
        
    except Exception as e:
        # Log do erro mas retorna sucesso para não reenvio
        print(f"Erro no webhook WhatsApp: {e}")
        return {"status": "error", "message": str(e)}

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

async def testar_conectividade_whatsapp(config: Dict[str, Any]) -> Dict[str, Any]:
    """Testar conectividade com WhatsApp Business API"""
    try:
        headers = {
            'Authorization': f"Bearer {config['token']}",
            'Content-Type': 'application/json'
        }
        
        # Testar endpoint de informações do número
        response = requests.get(
            f"{config['api_url']}/{config['numero_remetente']}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "sucesso": True,
                "mensagem": "Conectividade WhatsApp OK",
                "detalhes": {
                    "numero": data.get('display_phone_number'),
                    "verified": data.get('verified_name'),
                    "status": "conectado"
                }
            }
        else:
            return {
                "sucesso": False,
                "erro": f"API retornou {response.status_code}: {response.text}",
                "detalhes": {"status_code": response.status_code}
            }
            
    except Exception as e:
        return {
            "sucesso": False,
            "erro": f"Erro de conectividade: {str(e)}",
            "detalhes": {"exception": str(e)}
        }

def normalizar_telefone_brasileiro(telefone: str) -> Optional[str]:
    """Normalizar telefone brasileiro para formato WhatsApp"""
    # Remover caracteres não numéricos
    telefone = re.sub(r'[^\d]', '', telefone)
    
    # Validações básicas
    if len(telefone) < 10 or len(telefone) > 13:
        return None
    
    # Adicionar código do país se necessário
    if len(telefone) == 10:  # Telefone fixo sem DDD
        return None  # Inválido
    elif len(telefone) == 11:  # Celular sem código do país
        telefone = "55" + telefone
    elif len(telefone) == 13 and telefone.startswith("55"):  # Já formatado
        pass
    else:
        return None
    
    # Validar formato brasileiro
    if not telefone.startswith("55"):
        return None
    
    # Validar DDD (11 a 99)
    ddd = telefone[2:4]
    if not (11 <= int(ddd) <= 99):
        return None
    
    # Validar celular (9 dígitos começando com 9)
    numero = telefone[4:]
    if len(numero) == 9 and numero.startswith("9"):
        return telefone
    
    return None

def processar_webhook_whatsapp(data: Dict[str, Any], db: Session):
    """Processar webhook do WhatsApp em background"""
    try:
        # Estrutura típica do webhook WhatsApp
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('field') == 'messages':
                    for status in change.get('value', {}).get('statuses', []):
                        message_id = status.get('id')
                        new_status = status.get('status')
                        timestamp = status.get('timestamp')
                        
                        # Buscar comunicação pelo message_id
                        comunicacao = db.query(ComunicacaoHistorico).filter(
                            ComunicacaoHistorico.provider_response.contains(f'"id": "{message_id}"')
                        ).first()
                        
                        if comunicacao:
                            # Mapear status WhatsApp para nosso enum
                            status_map = {
                                'sent': StatusComunicacao.ENVIADO,
                                'delivered': StatusComunicacao.ENTREGUE,
                                'read': StatusComunicacao.LIDO,
                                'failed': StatusComunicacao.ERRO
                            }
                            
                            if new_status in status_map:
                                comunicacao.status = status_map[new_status]
                                
                                if new_status == 'delivered':
                                    comunicacao.entregue_em = datetime.fromtimestamp(int(timestamp))
                                elif new_status == 'read':
                                    comunicacao.lido_em = datetime.fromtimestamp(int(timestamp))
                                
                                db.commit()
                                
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")