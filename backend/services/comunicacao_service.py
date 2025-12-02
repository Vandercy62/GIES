"""
SERVIÇOS DE COMUNICAÇÃO
=======================

Sistema ERP Primotex - Serviços para processamento de comunicações
Integração com provedores externos e gestão de templates

Funcionalidades:
- Processamento de templates com variáveis
- Integração WhatsApp Business API
- Envio de emails via SMTP
- Gestão de fila de mensagens
- Histórico e estatísticas
- Sistema de retry automático

Autor: GitHub Copilot
Data: 29/10/2025
"""

import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.comunicacao import (
    ComunicacaoTemplate, ComunicacaoHistorico, ComunicacaoConfig, 
    ComunicacaoFila, TipoComunicacao, StatusComunicacao
)
from backend.schemas.comunicacao import (
    EnvioMensagemRequest, EnvioMensagemResponse,
    ConfiguracaoEmail, ConfiguracaoWhatsApp, ConfiguracaoSMS
)
import logging
import re
from jinja2 import Template, Environment, select_autoescape

logger = logging.getLogger(__name__)

class ComunicacaoService:
    """Serviço principal para comunicações"""

    def __init__(self, db: Session):
        self.db = db
        self.jinja_env = Environment(
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def processar_template(self, template_texto: str, variaveis: Dict[str, Any]) -> str:
        """
        Processa template com variáveis usando Jinja2
        """
        try:
            template = self.jinja_env.from_string(template_texto)
            return template.render(**variaveis)
        except Exception as e:
            logger.error(f"Erro ao processar template: {e}")
            raise ValueError(f"Erro no template: {str(e)}")

    def enviar_mensagem(self, request: EnvioMensagemRequest) -> EnvioMensagemResponse:
        """
        Enviar mensagem usando template ou conteúdo direto
        """
        try:
            # Se tem template, carregar e processar
            if request.template_id:
                template = self.db.query(ComunicacaoTemplate).filter(
                    ComunicacaoTemplate.id == request.template_id,
                    ComunicacaoTemplate.ativo == True
                ).first()

                if not template:
                    return EnvioMensagemResponse(
                        sucesso=False,
                        mensagem="Template não encontrado ou inativo"
                    )

                # Processar template com variáveis
                variaveis = request.variaveis or {}
                conteudo = self.processar_template(template.template_texto, variaveis)
                assunto = template.assunto

                if template.assunto and request.variaveis:
                    assunto = self.processar_template(template.assunto, variaveis)

                tipo_comunicacao = template.canal
            else:
                # Usar conteúdo direto
                conteudo = request.conteudo
                assunto = request.assunto
                tipo_comunicacao = request.tipo_comunicacao

            # Criar registro no histórico
            historico = ComunicacaoHistorico(
                template_id=request.template_id,
                tipo=tipo_comunicacao,
                canal_usado=tipo_comunicacao.value,
                destinatario_nome=request.destinatario_nome,
                destinatario_contato=request.destinatario_contato,
                cliente_id=request.cliente_id,
                assunto=assunto,
                conteudo_texto=conteudo,
                origem_modulo=request.origem_modulo,
                origem_id=request.origem_id,
                agendado_para=request.agendar_para
            )

            # Se é para agendar, adicionar à fila
            if request.agendar_para and request.agendar_para > datetime.now():
                self._adicionar_a_fila(request, conteudo, assunto)
                historico.status = StatusComunicacao.PENDENTE
                self.db.add(historico)
                self.db.commit()

                return EnvioMensagemResponse(
                    sucesso=True,
                    mensagem="Mensagem agendada com sucesso",
                    comunicacao_id=historico.id,
                    agendado=True
                )

            # Enviar imediatamente
            resultado = self._enviar_imediato(tipo_comunicacao, request, conteudo, assunto)

            # Atualizar histórico com resultado
            historico.status = StatusComunicacao.ENVIADO if resultado['sucesso'] else StatusComunicacao.ERRO
            historico.enviado_em = datetime.now() if resultado['sucesso'] else None
            historico.erro_detalhes = resultado.get('erro')
            historico.provider_response = resultado.get('detalhes')

            self.db.add(historico)
            self.db.commit()

            return EnvioMensagemResponse(
                sucesso=resultado['sucesso'],
                mensagem=resultado['mensagem'],
                comunicacao_id=historico.id,
                detalhes=resultado.get('detalhes')
            )

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return EnvioMensagemResponse(
                sucesso=False,
                mensagem=f"Erro interno: {str(e)}"
            )

    def _adicionar_a_fila(self, request: EnvioMensagemRequest, conteudo: str, assunto: str):
        """Adicionar mensagem à fila de processamento"""
        fila_item = ComunicacaoFila(
            template_id=request.template_id,
            prioridade=request.prioridade,
            destinatario_nome=request.destinatario_nome,
            destinatario_contato=request.destinatario_contato,
            cliente_id=request.cliente_id,
            assunto=assunto,
            conteudo=conteudo,
            variaveis_contexto=request.variaveis,
            agendado_para=request.agendar_para,
            origem_modulo=request.origem_modulo,
            origem_id=request.origem_id
        )

        self.db.add(fila_item)
        self.db.commit()

    def _enviar_imediato(self, tipo: TipoComunicacao, request: EnvioMensagemRequest, 
                        conteudo: str, assunto: str) -> Dict[str, Any]:
        """Enviar mensagem imediatamente"""

        if tipo == TipoComunicacao.EMAIL:
            return self._enviar_email(request.destinatario_contato, assunto, conteudo)
        elif tipo == TipoComunicacao.WHATSAPP:
            return self._enviar_whatsapp(request.destinatario_contato, conteudo)
        elif tipo == TipoComunicacao.SMS:
            return self._enviar_sms(request.destinatario_contato, conteudo)
        else:
            return {
                'sucesso': False,
                'mensagem': f"Tipo de comunicação {tipo.value} não suportado",
                'erro': 'TIPO_NAO_SUPORTADO'
            }

    def _enviar_email(self, destinatario: str, assunto: str, conteudo: str) -> Dict[str, Any]:
        """Enviar email via SMTP"""
        try:
            # Buscar configuração de email ativa
            config = self.db.query(ComunicacaoConfig).filter(
                ComunicacaoConfig.tipo == TipoComunicacao.EMAIL,
                ComunicacaoConfig.ativo == True,
                ComunicacaoConfig.padrao == True
            ).first()

            if not config:
                return {
                    'sucesso': False,
                    'mensagem': 'Configuração de email não encontrada',
                    'erro': 'CONFIG_NAO_ENCONTRADA'
                }

            cfg = config.configuracoes

            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = f"{cfg['remetente_nome']} <{cfg['remetente_email']}>"
            msg['To'] = destinatario

            # Adicionar conteúdo
            if '<html>' in conteudo or '<body>' in conteudo:
                msg.attach(MIMEText(conteudo, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(conteudo, 'plain', 'utf-8'))

            # Conectar e enviar
            server = smtplib.SMTP(cfg['servidor_smtp'], cfg['porta'])

            if cfg.get('usar_tls', True):
                server.starttls()

            server.login(cfg['usuario'], cfg['senha'])
            server.send_message(msg)
            server.quit()

            return {
                'sucesso': True,
                'mensagem': 'Email enviado com sucesso',
                'detalhes': {
                    'servidor': cfg['servidor_smtp'],
                    'destinatario': destinatario,
                    'timestamp': datetime.now().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return {
                'sucesso': False,
                'mensagem': f'Erro ao enviar email: {str(e)}',
                'erro': 'ERRO_SMTP'
            }

    def _enviar_whatsapp(self, destinatario: str, conteudo: str) -> Dict[str, Any]:
        """Enviar mensagem via WhatsApp Business API"""
        try:
            # Buscar configuração do WhatsApp
            config = self.db.query(ComunicacaoConfig).filter(
                ComunicacaoConfig.tipo == TipoComunicacao.WHATSAPP,
                ComunicacaoConfig.ativo == True,
                ComunicacaoConfig.padrao == True
            ).first()

            if not config:
                return {
                    'sucesso': False,
                    'mensagem': 'Configuração de WhatsApp não encontrada',
                    'erro': 'CONFIG_NAO_ENCONTRADA'
                }

            cfg = config.configuracoes

            # Limpar número de telefone
            telefone = re.sub(r'[^\d]', '', destinatario)
            if not telefone.startswith('55'):
                telefone = '55' + telefone

            # Preparar payload
            payload = {
                "messaging_product": "whatsapp",
                "to": telefone,
                "type": "text",
                "text": {
                    "body": conteudo
                }
            }

            headers = {
                'Authorization': f"Bearer {cfg['token']}",
                'Content-Type': 'application/json'
            }

            # Enviar requisição
            response = requests.post(
                f"{cfg['api_url']}/{cfg['numero_remetente']}/messages",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'sucesso': True,
                    'mensagem': 'WhatsApp enviado com sucesso',
                    'detalhes': {
                        'message_id': result.get('messages', [{}])[0].get('id'),
                        'telefone': telefone,
                        'timestamp': datetime.now().isoformat()
                    }
                }
            else:
                return {
                    'sucesso': False,
                    'mensagem': f'Erro na API WhatsApp: {response.status_code}',
                    'erro': 'ERRO_API_WHATSAPP',
                    'detalhes': response.text
                }

        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {e}")
            return {
                'sucesso': False,
                'mensagem': f'Erro ao enviar WhatsApp: {str(e)}',
                'erro': 'ERRO_WHATSAPP'
            }

    def _enviar_sms(self, destinatario: str, conteudo: str) -> Dict[str, Any]:
        """Enviar SMS via provedor"""
        try:
            # Buscar configuração de SMS
            config = self.db.query(ComunicacaoConfig).filter(
                ComunicacaoConfig.tipo == TipoComunicacao.SMS,
                ComunicacaoConfig.ativo == True,
                ComunicacaoConfig.padrao == True
            ).first()

            if not config:
                return {
                    'sucesso': False,
                    'mensagem': 'Configuração de SMS não encontrada',
                    'erro': 'CONFIG_NAO_ENCONTRADA'
                }

            # Implementação específica do provedor
            # Por ora, retornar sucesso simulado
            return {
                'sucesso': True,
                'mensagem': 'SMS enviado com sucesso (simulado)',
                'detalhes': {
                    'telefone': destinatario,
                    'timestamp': datetime.now().isoformat(),
                    'simulado': True
                }
            }

        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {e}")
            return {
                'sucesso': False,
                'mensagem': f'Erro ao enviar SMS: {str(e)}',
                'erro': 'ERRO_SMS'
            }

    def processar_fila(self) -> Dict[str, Any]:
        """Processar itens pendentes na fila"""
        try:
            # Buscar itens prontos para envio
            agora = datetime.now()
            itens_fila = self.db.query(ComunicacaoFila).filter(
                ComunicacaoFila.status == "PENDENTE",
                ComunicacaoFila.agendado_para <= agora,
                ComunicacaoFila.tentativas < ComunicacaoFila.max_tentativas
            ).order_by(ComunicacaoFila.prioridade, ComunicacaoFila.criado_em).limit(50).all()

            processados = 0
            sucessos = 0
            erros = 0

            for item in itens_fila:
                try:
                    # Determinar tipo de comunicação baseado no template ou conteúdo
                    tipo_comunicacao = TipoComunicacao.EMAIL  # Default

                    if item.template_id:
                        template = self.db.query(ComunicacaoTemplate).filter(
                            ComunicacaoTemplate.id == item.template_id
                        ).first()
                        if template:
                            tipo_comunicacao = template.canal

                    # Criar request simulado
                    request = EnvioMensagemRequest(
                        template_id=item.template_id,
                        tipo_comunicacao=tipo_comunicacao,
                        destinatario_nome=item.destinatario_nome,
                        destinatario_contato=item.destinatario_contato,
                        cliente_id=item.cliente_id,
                        assunto=item.assunto,
                        conteudo=item.conteudo,
                        variaveis=item.variaveis_contexto,
                        origem_modulo=item.origem_modulo,
                        origem_id=item.origem_id
                    )

                    # Enviar
                    resultado = self._enviar_imediato(tipo_comunicacao, request, item.conteudo, item.assunto)

                    if resultado['sucesso']:
                        item.status = "ENVIADO"
                        item.processado_em = agora
                        sucessos += 1
                    else:
                        item.tentativas += 1
                        item.erro_detalhes = resultado.get('mensagem')

                        if item.tentativas >= item.max_tentativas:
                            item.status = "ERRO"
                            item.processado_em = agora

                        erros += 1

                    processados += 1

                except Exception as e:
                    logger.error(f"Erro ao processar item da fila {item.id}: {e}")
                    item.tentativas += 1
                    item.erro_detalhes = str(e)

                    if item.tentativas >= item.max_tentativas:
                        item.status = "ERRO"
                        item.processado_em = agora

                    erros += 1
                    processados += 1

            self.db.commit()

            return {
                'sucesso': True,
                'processados': processados,
                'sucessos': sucessos,
                'erros': erros,
                'mensagem': f'Processados {processados} itens da fila'
            }

        except Exception as e:
            logger.error(f"Erro ao processar fila: {e}")
            return {
                'sucesso': False,
                'mensagem': f'Erro ao processar fila: {str(e)}'
            }

    def gerar_comunicacao_os(self, os_id: int, status: str, dados_os: Dict[str, Any]):
        """Gerar comunicação automática para OS"""
        try:
            # Mapear status para tipo de template
            template_map = {
                'CRIADA': 'OS_CRIADA',
                'INICIADA': 'OS_INICIADA',
                'CONCLUIDA': 'OS_CONCLUIDA',
                'CANCELADA': 'OS_CANCELADA'
            }

            tipo_template = template_map.get(status)
            if not tipo_template:
                return

            # Buscar template automático
            template = self.db.query(ComunicacaoTemplate).filter(
                ComunicacaoTemplate.tipo == tipo_template,
                ComunicacaoTemplate.automatico == True,
                ComunicacaoTemplate.ativo == True
            ).first()

            if not template:
                return

            # Criar request de envio
            request = EnvioMensagemRequest(
                template_id=template.id,
                tipo_comunicacao=template.canal,
                destinatario_nome=dados_os.get('cliente_nome', ''),
                destinatario_contato=dados_os.get('cliente_contato', ''),
                cliente_id=dados_os.get('cliente_id'),
                variaveis=dados_os,
                origem_modulo='OS',
                origem_id=os_id
            )

            # Enviar
            self.enviar_mensagem(request)

        except Exception as e:
            logger.error(f"Erro ao gerar comunicação OS: {e}")

    def gerar_comunicacao_agendamento(self, agendamento_id: int, tipo: str, dados_agendamento: Dict[str, Any]):
        """Gerar comunicação automática para agendamento"""
        try:
            # Mapear tipo para tipo de template
            template_map = {
                'CONFIRMADO': 'AGENDAMENTO_CONFIRMADO',
                'LEMBRETE': 'AGENDAMENTO_LEMBRETE',
                'CANCELADO': 'AGENDAMENTO_CANCELADO'
            }

            tipo_template = template_map.get(tipo)
            if not tipo_template:
                return

            # Buscar template automático
            template = self.db.query(ComunicacaoTemplate).filter(
                ComunicacaoTemplate.tipo == tipo_template,
                ComunicacaoTemplate.automatico == True,
                ComunicacaoTemplate.ativo == True
            ).first()

            if not template:
                return

            # Agendar lembrete para 1 dia antes se for lembrete
            agendar_para = None
            if tipo == 'LEMBRETE' and dados_agendamento.get('data_agendamento'):
                data_agendamento = datetime.fromisoformat(dados_agendamento['data_agendamento'])
                agendar_para = data_agendamento - timedelta(days=1)

            # Criar request de envio
            request = EnvioMensagemRequest(
                template_id=template.id,
                tipo_comunicacao=template.canal,
                destinatario_nome=dados_agendamento.get('cliente_nome', ''),
                destinatario_contato=dados_agendamento.get('cliente_contato', ''),
                cliente_id=dados_agendamento.get('cliente_id'),
                variaveis=dados_agendamento,
                agendar_para=agendar_para,
                origem_modulo='AGENDAMENTO',
                origem_id=agendamento_id
            )

            # Enviar
            self.enviar_mensagem(request)

        except Exception as e:
            logger.error(f"Erro ao gerar comunicação agendamento: {e}")

class TemplateService:
    """Serviço para gestão de templates"""

    def __init__(self, db: Session):
        self.db = db

    def criar_templates_padrao(self):
        """Criar templates padrão do sistema"""
        templates_padrao = [
            {
                'nome': 'OS Criada - WhatsApp',
                'tipo': 'OS_CRIADA',
                'canal': TipoComunicacao.WHATSAPP,
                'template_texto': '''Olá {{ cliente_nome }}! 

Sua Ordem de Serviço #{{ os_numero }} foi criada com sucesso.

📋 Serviço: {{ descricao }}
📅 Data prevista: {{ data_prevista }}
👨‍🔧 Técnico: {{ tecnico_nome }}

Acompanhe o andamento pelo nosso sistema.

*Primotex - Forros e Divisórias*''',
                'automatico': True,
                'variaveis_disponiveis': {
                    'cliente_nome': 'Nome do cliente',
                    'os_numero': 'Número da OS',
                    'descricao': 'Descrição do serviço',
                    'data_prevista': 'Data prevista',
                    'tecnico_nome': 'Nome do técnico'
                }
            },
            {
                'nome': 'Agendamento Confirmado - Email',
                'tipo': 'AGENDAMENTO_CONFIRMADO',
                'canal': TipoComunicacao.EMAIL,
                'assunto': 'Agendamento Confirmado - Primotex',
                'template_texto': '''Prezado(a) {{ cliente_nome }},

Seu agendamento foi confirmado com sucesso!

Data: {{ data_agendamento }}
Horário: {{ hora_agendamento }}
Endereço: {{ endereco }}
Técnico: {{ tecnico_nome }}

Em caso de dúvidas, entre em contato conosco.

Atenciosamente,
Equipe Primotex''',
                'automatico': True,
                'variaveis_disponiveis': {
                    'cliente_nome': 'Nome do cliente',
                    'data_agendamento': 'Data do agendamento',
                    'hora_agendamento': 'Hora do agendamento',
                    'endereco': 'Endereço do serviço',
                    'tecnico_nome': 'Nome do técnico'
                }
            }
        ]

        for template_data in templates_padrao:
            # Verificar se já existe
            existe = self.db.query(ComunicacaoTemplate).filter(
                ComunicacaoTemplate.nome == template_data['nome']
            ).first()

            if not existe:
                template = ComunicacaoTemplate(**template_data)
                self.db.add(template)

        self.db.commit()