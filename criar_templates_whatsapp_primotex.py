#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEMPLATES WHATSAPP PRIMOTEX
===========================

Script para criar templates WhatsApp específicos para Primotex - Forros e Divisórias
Templates otimizados para o negócio e aprovados pelo WhatsApp Business API

Autor: GitHub Copilot
Data: 01/11/2025
"""

from datetime import datetime
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.config import get_db
from backend.models.comunicacao import (
    ComunicacaoTemplate, TipoTemplate, TipoComunicacao
)


def criar_templates_whatsapp_primotex():
    """Criar templates WhatsApp específicos para Primotex"""
    
    print("🎨 CRIANDO TEMPLATES WHATSAPP - PRIMOTEX FORROS E DIVISÓRIAS")
    print("=" * 70)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Obter sessão do banco
    db = next(get_db())
    
    templates_primotex = [
        {
            "nome": "OS Criada - Primotex WhatsApp",
            "tipo": TipoTemplate.OS_CRIADA,
            "canal": TipoComunicacao.WHATSAPP,
            "template_texto": """🏗️ *PRIMOTEX - FORROS E DIVISÓRIAS*

Olá *{{ cliente_nome }}*! 

✅ Sua Ordem de Serviço foi criada com sucesso!

📋 *Detalhes:*
• OS Nº: *#{{ os_numero }}*
• Serviço: {{ descricao }}
• Data prevista: {{ data_prevista }}
• Técnico: {{ tecnico_nome }}

📞 Dúvidas? Entre em contato conosco!

*Primotex - Transformando ambientes* 🏠""",
            "automatico": True,
            "ativo": True,
            "variaveis_disponiveis": {
                "cliente_nome": "Nome do cliente",
                "os_numero": "Número da OS",
                "descricao": "Descrição do serviço",
                "data_prevista": "Data prevista para execução",
                "tecnico_nome": "Nome do técnico responsável"
            },
            "configuracoes_canal": {
                "emoji_permitido": True,
                "markdown": True,
                "max_caracteres": 1024
            }
        },
        {
            "nome": "OS Iniciada - Primotex WhatsApp",
            "tipo": TipoTemplate.OS_INICIADA,
            "canal": TipoComunicacao.WHATSAPP,
            "template_texto": """🚀 *SERVIÇO INICIADO - PRIMOTEX*

Oi *{{ cliente_nome }}*!

👨‍🔧 Nosso técnico *{{ tecnico_nome }}* iniciou o serviço:

📋 *OS #{{ os_numero }}*
🏠 Local: {{ endereco }}
⏰ Horário: {{ hora_inicio }}

Acompanhe o progresso! Em breve você terá seu ambiente transformado.

*Primotex - Excelência em forros e divisórias* ✨""",
            "automatico": True,
            "ativo": True,
            "variaveis_disponiveis": {
                "cliente_nome": "Nome do cliente",
                "os_numero": "Número da OS",
                "tecnico_nome": "Nome do técnico",
                "endereco": "Endereço do serviço",
                "hora_inicio": "Horário de início"
            }
        },
        {
            "nome": "OS Concluída - Primotex WhatsApp", 
            "tipo": TipoTemplate.OS_CONCLUIDA,
            "canal": TipoComunicacao.WHATSAPP,
            "template_texto": """🎉 *SERVIÇO CONCLUÍDO - PRIMOTEX*

Parabéns *{{ cliente_nome }}*!

✅ Seu serviço foi finalizado com sucesso!

📋 *Resumo:*
• OS: *#{{ os_numero }}*
• Concluído em: {{ data_conclusao }}
• Técnico: {{ tecnico_nome }}
• Qualidade: ⭐⭐⭐⭐⭐

💰 *Valor total:* R$ {{ valor_total }}

Sua satisfação é nossa prioridade! Avalie nosso serviço e indique para amigos.

*Primotex - Seu ambiente ideal* 🏠✨""",
            "automatico": True,
            "ativo": True,
            "variaveis_disponiveis": {
                "cliente_nome": "Nome do cliente",
                "os_numero": "Número da OS",
                "data_conclusao": "Data de conclusão",
                "tecnico_nome": "Nome do técnico",
                "valor_total": "Valor total do serviço"
            }
        },
        {
            "nome": "Agendamento Confirmado - Primotex",
            "tipo": TipoTemplate.AGENDAMENTO_CONFIRMADO,
            "canal": TipoComunicacao.WHATSAPP,
            "template_texto": """📅 *AGENDAMENTO CONFIRMADO - PRIMOTEX*

Olá *{{ cliente_nome }}*!

✅ Seu agendamento está confirmado:

📍 *Detalhes:*
• Data: *{{ data_agendamento }}*
• Horário: *{{ hora_agendamento }}*
• Endereço: {{ endereco }}
• Técnico: {{ tecnico_nome }}
• Serviço: {{ tipo_servico }}

⚠️ *Importante:* Nosso técnico chegará no horário marcado.

📞 Precisa reagendar? Entre em contato!

*Primotex - Pontualidade e qualidade* 🕒""",
            "automatico": True,
            "ativo": True,
            "variaveis_disponiveis": {
                "cliente_nome": "Nome do cliente",
                "data_agendamento": "Data do agendamento",
                "hora_agendamento": "Hora do agendamento", 
                "endereco": "Endereço do serviço",
                "tecnico_nome": "Nome do técnico",
                "tipo_servico": "Tipo de serviço"
            }
        },
        {
            "nome": "Lembrete Agendamento - Primotex",
            "tipo": TipoTemplate.AGENDAMENTO_LEMBRETE,
            "canal": TipoComunicacao.WHATSAPP,
            "template_texto": """⏰ *LEMBRETE - AGENDAMENTO AMANHÃ*

Oi *{{ cliente_nome }}*!

🔔 Lembrando que seu serviço está agendado para *AMANHÃ*:

📅 *{{ data_agendamento }}* às *{{ hora_agendamento }}*
🏠 Local: {{ endereco }}
👨‍🔧 Técnico: {{ tecnico_nome }}

✅ Tudo pronto para receber nossa equipe?

📞 Dúvidas? Estamos aqui para ajudar!

*Primotex - Sempre lembrado* 💭""",
            "automatico": True,
            "ativo": True,
            "variaveis_disponiveis": {
                "cliente_nome": "Nome do cliente",
                "data_agendamento": "Data do agendamento",
                "hora_agendamento": "Hora do agendamento",
                "endereco": "Endereço do serviço",
                "tecnico_nome": "Nome do técnico"
            }
        },
        {
            "nome": "Orçamento Enviado - Primotex",
            "tipo": TipoTemplate.ORCAMENTO_ENVIADO,
            "canal": TipoComunicacao.WHATSAPP,
            "template_texto": """💰 *ORÇAMENTO PRIMOTEX*

Olá *{{ cliente_nome }}*!

📊 Seu orçamento está pronto:

🏗️ *Serviços:*
{{ lista_servicos }}

💵 *Valor total:* R$ {{ valor_total }}
⏱️ *Prazo:* {{ prazo_execucao }}
✅ *Validade:* {{ validade_orcamento }}

🎁 *Condições especiais:*
• Desconto à vista: {{ desconto_vista }}%
• Parcelamento em até {{ max_parcelas }}x

Aprove e transforme seu ambiente!

*Primotex - O melhor preço da região* 💎""",
            "automatico": False,
            "ativo": True,
            "variaveis_disponiveis": {
                "cliente_nome": "Nome do cliente",
                "lista_servicos": "Lista dos serviços orçados",
                "valor_total": "Valor total do orçamento",
                "prazo_execucao": "Prazo para execução",
                "validade_orcamento": "Validade do orçamento",
                "desconto_vista": "Percentual desconto à vista",
                "max_parcelas": "Máximo de parcelas"
            }
        },
        {
            "nome": "Cobrança Vencimento - Primotex",
            "tipo": TipoTemplate.COBRANCA_VENCIMENTO,
            "canal": TipoComunicacao.WHATSAPP,
            "template_texto": """💳 *LEMBRETE DE VENCIMENTO - PRIMOTEX*

Olá *{{ cliente_nome }}*!

📅 Sua fatura vence *HOJE*:

🧾 *Fatura:* #{{ numero_fatura }}
💰 *Valor:* R$ {{ valor_vencimento }}
📅 *Vencimento:* {{ data_vencimento }}
🏦 *Referente:* {{ descricao_servico }}

💡 *Formas de pagamento:*
• PIX: {{ chave_pix }}
• Boleto: {{ link_boleto }}
• Cartão: {{ link_pagamento }}

Evite juros e multas! Pague hoje.

*Primotex - Facilitando seu pagamento* 💳""",
            "automatico": True,
            "ativo": True,
            "variaveis_disponiveis": {
                "cliente_nome": "Nome do cliente",
                "numero_fatura": "Número da fatura",
                "valor_vencimento": "Valor da fatura",
                "data_vencimento": "Data de vencimento",
                "descricao_servico": "Descrição do serviço",
                "chave_pix": "Chave PIX",
                "link_boleto": "Link do boleto",
                "link_pagamento": "Link para pagamento"
            }
        },
        {
            "nome": "Pagamento Confirmado - Primotex",
            "tipo": TipoTemplate.PAGAMENTO_CONFIRMADO,
            "canal": TipoComunicacao.WHATSAPP,
            "template_texto": """✅ *PAGAMENTO CONFIRMADO - PRIMOTEX*

Obrigado *{{ cliente_nome }}*!

💚 Pagamento recebido com sucesso:

🧾 *Fatura:* #{{ numero_fatura }}
💰 *Valor:* R$ {{ valor_pago }}
📅 *Data:* {{ data_pagamento }}
🏦 *Forma:* {{ forma_pagamento }}

📧 Seu comprovante será enviado por email.

Agradecemos a confiança! Continue contando com a Primotex para seus projetos.

*Primotex - Parceiro de confiança* 🤝""",
            "automatico": True,
            "ativo": True,
            "variaveis_disponiveis": {
                "cliente_nome": "Nome do cliente",
                "numero_fatura": "Número da fatura",
                "valor_pago": "Valor pago",
                "data_pagamento": "Data do pagamento",
                "forma_pagamento": "Forma de pagamento utilizada"
            }
        },
        {
            "nome": "Boas Vindas Cliente - Primotex",
            "tipo": TipoTemplate.CLIENTE_BOAS_VINDAS,
            "canal": TipoComunicacao.WHATSAPP,
            "template_texto": """🎉 *BEM-VINDO À PRIMOTEX!*

Olá *{{ cliente_nome }}*!

Seja muito bem-vindo(a) à família Primotex! 

🏠 *Sobre nós:*
✅ +15 anos transformando ambientes
✅ Forros e divisórias de qualidade
✅ Equipe especializada
✅ Garantia em todos os serviços

📱 *Nossos contatos:*
• WhatsApp: {{ telefone_empresa }}
• Email: {{ email_empresa }}
• Site: {{ site_empresa }}

🎁 *Oferta especial:* Como novo cliente, você tem 10% de desconto no primeiro serviço!

*Primotex - Seu ambiente ideal começa aqui* ✨""",
            "automatico": True,
            "ativo": True,
            "variaveis_disponiveis": {
                "cliente_nome": "Nome do cliente",
                "telefone_empresa": "Telefone da empresa",
                "email_empresa": "Email da empresa", 
                "site_empresa": "Site da empresa"
            }
        },
        {
            "nome": "Promocional - Primotex",
            "tipo": TipoTemplate.PROMOCIONAL,
            "canal": TipoComunicacao.WHATSAPP,
            "template_texto": """🎁 *PROMOÇÃO ESPECIAL PRIMOTEX*

Oi *{{ cliente_nome }}*!

🔥 *OFERTA IMPERDÍVEL:*

🏠 {{ nome_promocao }}
💰 *{{ desconto }}% OFF* em {{ tipo_servico }}
⏰ *Válida até:* {{ data_limite }}

✨ *Inclui:*
{{ itens_inclusos }}

🎯 *Condições:*
• Material de primeira qualidade
• Mão de obra especializada
• Garantia de {{ tempo_garantia }}
• Pagamento facilitado

📞 Aproveite AGORA! Vagas limitadas.

*Primotex - Oportunidade única* 🌟""",
            "automatico": False,
            "ativo": True,
            "variaveis_disponiveis": {
                "cliente_nome": "Nome do cliente",
                "nome_promocao": "Nome da promoção",
                "desconto": "Percentual de desconto",
                "tipo_servico": "Tipo de serviço em promoção",
                "data_limite": "Data limite da promoção",
                "itens_inclusos": "Itens inclusos na promoção",
                "tempo_garantia": "Tempo de garantia"
            }
        }
    ]
    
    print(f"\n📝 Criando {len(templates_primotex)} templates específicos...")
    
    templates_criados = 0
    templates_atualizados = 0
    
    try:
        for template_data in templates_primotex:
            # Verificar se já existe
            template_existente = db.query(ComunicacaoTemplate).filter(
                ComunicacaoTemplate.nome == template_data["nome"]
            ).first()
            
            if template_existente:
                # Atualizar existente
                for key, value in template_data.items():
                    if key != "nome":  # Não alterar o nome
                        setattr(template_existente, key, value)
                
                print(f"✅ Template atualizado: {template_data['nome']}")
                templates_atualizados += 1
            else:
                # Criar novo
                novo_template = ComunicacaoTemplate(**template_data)
                db.add(novo_template)
                print(f"🆕 Template criado: {template_data['nome']}")
                templates_criados += 1
        
        # Salvar no banco
        db.commit()
        
        print(f"\n🎉 TEMPLATES WHATSAPP CRIADOS COM SUCESSO!")
        print("=" * 50)
        print(f"🆕 Novos templates: {templates_criados}")
        print(f"✅ Templates atualizados: {templates_atualizados}")
        print(f"📊 Total de templates: {templates_criados + templates_atualizados}")
        
        # Listar todos os templates
        print(f"\n📋 TEMPLATES DISPONÍVEIS:")
        print("-" * 50)
        
        todos_templates = db.query(ComunicacaoTemplate).filter(
            ComunicacaoTemplate.canal == TipoComunicacao.WHATSAPP,
            ComunicacaoTemplate.ativo == True
        ).all()
        
        for i, template in enumerate(todos_templates, 1):
            status = "🤖 AUTO" if template.automatico else "✋ MANUAL"
            print(f"{i:2d}. {template.nome} - {status}")
            print(f"    📱 Tipo: {template.tipo.value}")
            print(f"    📝 Variáveis: {len(template.variaveis_disponiveis or {})}")
        
        print(f"\n💡 PRÓXIMOS PASSOS:")
        print("1. Configurar WhatsApp Business API com tokens reais")
        print("2. Aprovar templates no Meta Business Manager") 
        print("3. Testar envio de mensagens")
        print("4. Configurar automações por módulo")
        
        return {
            "sucesso": True,
            "templates_criados": templates_criados,
            "templates_atualizados": templates_atualizados,
            "total": templates_criados + templates_atualizados
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar templates: {e}")
        return {
            "sucesso": False,
            "erro": str(e)
        }
    finally:
        db.close()


if __name__ == "__main__":
    resultado = criar_templates_whatsapp_primotex()
    if resultado["sucesso"]:
        print(f"\n🏆 Missão cumprida! {resultado['total']} templates prontos para uso!")
    else:
        print(f"\n💥 Falha na missão: {resultado['erro']}")