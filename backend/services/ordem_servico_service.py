#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVIÇO ORDEM DE SERVIÇO - SISTEMA ERP PRIMOTEX
===============================================

Serviço responsável por toda a lógica de negócio das Ordens de Serviço,
incluindo o controle das 7 fases do workflow e integração com comunicação.

Criado em: 30/10/2025
Autor: GitHub Copilot
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
import logging

from backend.models.ordem_servico_model import (
    OrdemServico, FaseOS, FASES_OS
)
from backend.models.cliente_model import Cliente
from backend.schemas.ordem_servico_schemas import (
    OrdemServicoCreate, OrdemServicoUpdate, OrdemServicoResponse,
    FiltrosOrdemServico, ResumoOrdemServico, ListagemOrdemServico,
    MudancaFaseRequest, EstatisticasOS, DashboardOS
)
from backend.services.comunicacao_service import ComunicacaoService

logger = logging.getLogger(__name__)

# Constantes para status
STATUS_EM_ANDAMENTO = "Em Andamento"
STATUS_CONCLUIDA = "Concluída"
STATUS_PENDENTE = "Pendente"
STATUS_ABERTA = "Aberta"
STATUS_CANCELADA = "Cancelada"


class OrdemServicoService:
    """
    Serviço completo para gerenciamento de Ordens de Serviço

    Inclui:
    - CRUD completo de OS
    - Controle das 7 fases do workflow
    - Integração com WhatsApp
    - Relatórios e estatísticas
    - Validações de negócio
    """

    def __init__(self, db: Session):
        self.db = db
        self.comunicacao_service = ComunicacaoService()

    # ================================
    # CRUD BÁSICO DE ORDEM DE SERVIÇO
    # ================================

    def criar_ordem_servico(self, os_data: OrdemServicoCreate) -> OrdemServicoResponse:
        """
        Cria uma nova Ordem de Serviço com todas as fases inicializadas

        Args:
            os_data: Dados da OS para criação

        Returns:
            OrdemServicoResponse: OS criada com dados completos

        Raises:
            ValueError: Se dados inválidos ou cliente não encontrado
        """
        try:
            # Verificar se cliente existe
            cliente = self.db.query(Cliente).filter(Cliente.id == os_data.cliente_id).first()
            if not cliente:
                raise ValueError(f"Cliente com ID {os_data.cliente_id} não encontrado")

            # Gerar número da OS se não fornecido
            if not os_data.numero_os:
                os_data.numero_os = self._gerar_numero_os()

            # Verificar se número da OS já existe
            existing_os = self.db.query(OrdemServico).filter(
                OrdemServico.numero_os == os_data.numero_os
            ).first()
            if existing_os:
                raise ValueError(f"Número de OS {os_data.numero_os} já existe")

            # Criar a OS
            nova_os = OrdemServico(
                numero_os=os_data.numero_os,
                cliente_id=os_data.cliente_id,
                titulo=os_data.titulo,
                descricao=os_data.descricao,
                tipo_servico=os_data.tipo_servico,
                prioridade=os_data.prioridade,
                endereco_execucao=os_data.endereco_servico,
                cidade_execucao=os_data.cidade_servico,
                estado_execucao=os_data.estado_servico,
                cep_execucao=os_data.cep_servico,
                data_prevista_conclusao=os_data.data_prazo,
                valor_orcamento=os_data.valor_estimado or Decimal('0.00'),
                observacoes_abertura=os_data.observacoes,
                usuario_responsavel=os_data.usuario_criacao,
                status_fase=1,
                status_geral=STATUS_ABERTA
            )

            self.db.add(nova_os)
            self.db.flush()  # Para obter o ID

            # Criar todas as 7 fases automaticamente
            self._criar_fases_iniciais(nova_os.id)

            # Commit das alterações
            self.db.commit()
            self.db.refresh(nova_os)

            # Enviar notificação via WhatsApp
            try:
                self._notificar_nova_os(nova_os, cliente)
            except Exception as e:
                logger.warning(f"Erro ao enviar notificação WhatsApp: {e}")

            logger.info(f"OS {nova_os.numero_os} criada com sucesso")
            return self._converter_para_response(nova_os)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao criar OS: {e}")
            raise

    def listar_ordens_servico(self, filtros: FiltrosOrdemServico) -> ListagemOrdemServico:
        """
        Lista ordens de serviço com filtros e paginação

        Args:
            filtros: Filtros para aplicar na busca

        Returns:
            ListagemOrdemServico: Lista paginada de OS
        """
        try:
            # Query base
            query = self.db.query(OrdemServico).join(Cliente)

            # Aplicar filtros
            if filtros.cliente_id:
                query = query.filter(OrdemServico.cliente_id == filtros.cliente_id)

            if filtros.status:
                query = query.filter(OrdemServico.status_geral == filtros.status.value)

            if filtros.tipo_servico:
                query = query.filter(OrdemServico.tipo_servico == filtros.tipo_servico.value)

            if filtros.prioridade:
                query = query.filter(OrdemServico.prioridade == filtros.prioridade.value)

            if filtros.fase_atual:
                fase_num = int(filtros.fase_atual.value.split('-')[0])
                query = query.filter(OrdemServico.status_fase == fase_num)

            if filtros.urgente is not None:
                if filtros.urgente:
                    query = query.filter(OrdemServico.prioridade == "Urgente")
                else:
                    query = query.filter(OrdemServico.prioridade != "Urgente")

            if filtros.numero_os:
                query = query.filter(OrdemServico.numero_os.ilike(f"%{filtros.numero_os}%"))

            if filtros.titulo:
                query = query.filter(OrdemServico.titulo.ilike(f"%{filtros.titulo}%"))

            if filtros.responsavel:
                query = query.filter(
                    or_(
                        OrdemServico.usuario_responsavel.ilike(f"%{filtros.responsavel}%"),
                        OrdemServico.tecnico_responsavel.ilike(f"%{filtros.responsavel}%")
                    )
                )

            # Filtros de data
            if filtros.data_inicio:
                query = query.filter(OrdemServico.data_abertura >= filtros.data_inicio)

            if filtros.data_fim:
                query = query.filter(OrdemServico.data_abertura <= filtros.data_fim)

            # Contar total
            total = query.count()

            # Ordenação
            if filtros.order_by == "numero_os":
                order_col = OrdemServico.numero_os
            elif filtros.order_by == "cliente":
                order_col = Cliente.nome
            elif filtros.order_by == "status":
                order_col = OrdemServico.status_geral
            elif filtros.order_by == "prioridade":
                order_col = OrdemServico.prioridade
            else:
                order_col = OrdemServico.created_at

            if filtros.order_desc:
                query = query.order_by(desc(order_col))
            else:
                query = query.order_by(asc(order_col))

            # Paginação
            itens = query.offset(filtros.skip).limit(filtros.limit).all()

            # Converter para resumo
            resumos = []
            for os in itens:
                resumo = ResumoOrdemServico(
                    id=os.id,
                    numero_os=os.numero_os,
                    titulo=os.titulo,
                    cliente_nome=os.cliente.nome if os.cliente else "N/A",
                    status=os.status_geral,
                    fase_atual=self._get_fase_enum(os.status_fase),
                    prioridade=os.prioridade,
                    tipo_servico=os.tipo_servico,
                    progresso_percentual=self._calcular_progresso(os.status_fase),
                    data_solicitacao=os.data_abertura,
                    data_prazo=os.data_prevista_conclusao,
                    valor_final=os.valor_final,
                    urgente=(os.prioridade == "Urgente")
                )
                resumos.append(resumo)

            return ListagemOrdemServico(
                total=total,
                skip=filtros.skip,
                limit=filtros.limit,
                itens=resumos
            )

        except Exception as e:
            logger.error(f"Erro ao listar OS: {e}")
            raise

    def obter_ordem_servico(self, os_id: int) -> Optional[OrdemServicoResponse]:
        """
        Obtém uma OS específica com dados completos

        Args:
            os_id: ID da OS

        Returns:
            OrdemServicoResponse ou None se não encontrada
        """
        try:
            os = self.db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
            if not os:
                return None

            return self._converter_para_response(os)

        except Exception as e:
            logger.error(f"Erro ao obter OS {os_id}: {e}")
            raise

    def atualizar_ordem_servico(self, os_id: int, os_data: OrdemServicoUpdate) -> Optional[OrdemServicoResponse]:
        """
        Atualiza dados de uma OS existente

        Args:
            os_id: ID da OS
            os_data: Dados para atualização

        Returns:
            OrdemServicoResponse atualizada ou None se não encontrada
        """
        try:
            os = self.db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
            if not os:
                return None

            # Atualizar campos fornecidos
            update_data = os_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if field != "usuario_ultima_alteracao" and hasattr(os, field):
                    setattr(os, field, value)

            # Campos de controle
            os.updated_at = datetime.now()
            if hasattr(os_data, 'usuario_ultima_alteracao'):
                os.usuario_responsavel = os_data.usuario_ultima_alteracao

            self.db.commit()
            self.db.refresh(os)

            logger.info(f"OS {os.numero_os} atualizada")
            return self._converter_para_response(os)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar OS {os_id}: {e}")
            raise

    def excluir_ordem_servico(self, os_id: int) -> bool:
        """
        Exclui uma OS (soft delete - marca como cancelada)

        Args:
            os_id: ID da OS

        Returns:
            bool: True se excluída com sucesso
        """
        try:
            os = self.db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
            if not os:
                return False

            # Soft delete - marca como cancelada
            os.status_geral = STATUS_CANCELADA
            os.updated_at = datetime.now()

            self.db.commit()

            logger.info(f"OS {os.numero_os} cancelada")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao cancelar OS {os_id}: {e}")
            raise

    # ================================
    # CONTROLE DE FASES
    # ================================

    def mudar_fase(self, os_id: int, mudanca: MudancaFaseRequest) -> Optional[OrdemServicoResponse]:
        """
        Muda a fase atual da OS e executa ações específicas da fase

        Args:
            os_id: ID da OS
            mudanca: Dados da mudança de fase

        Returns:
            OrdemServicoResponse atualizada
        """
        try:
            os = self.db.query(OrdemServico).filter(OrdemServico.id == os_id).first()
            if not os:
                raise ValueError(f"OS {os_id} não encontrada")

            nova_fase_num = int(mudanca.nova_fase.value.split('-')[0])
            fase_atual = os.status_fase

            # Validar se pode mudar para a nova fase
            if nova_fase_num < fase_atual:
                raise ValueError("Não é possível retroceder fases")

            if nova_fase_num > fase_atual + 1:
                raise ValueError("Não é possível pular fases")

            # Atualizar fase da OS
            os.status_fase = nova_fase_num
            os.updated_at = datetime.now()

            # Atualizar fase correspondente
            fase = self.db.query(FaseOS).filter(
                and_(
                    FaseOS.ordem_servico_id == os_id,
                    FaseOS.numero_fase == nova_fase_num
                )
            ).first()

            if fase:
                fase.status = STATUS_EM_ANDAMENTO
                fase.data_inicio = datetime.now()
                fase.responsavel = mudanca.usuario_responsavel
                if mudanca.observacoes:
                    fase.observacoes = mudanca.observacoes

            # Marcar fase anterior como concluída
            if nova_fase_num > 1:
                fase_anterior = self.db.query(FaseOS).filter(
                    and_(
                        FaseOS.ordem_servico_id == os_id,
                        FaseOS.numero_fase == nova_fase_num - 1
                    )
                ).first()

                if fase_anterior:
                    fase_anterior.status = STATUS_CONCLUIDA
                    fase_anterior.data_conclusao = datetime.now()

            # Atualizar status geral se necessário
            if nova_fase_num == 7:  # Última fase
                os.status_geral = STATUS_CONCLUIDA
                os.data_conclusao = datetime.now()
            elif nova_fase_num > 1:
                os.status_geral = STATUS_EM_ANDAMENTO

            self.db.commit()
            self.db.refresh(os)

            # Executar ações específicas da nova fase
            self._executar_acoes_fase(os, nova_fase_num)

            logger.info(f"OS {os.numero_os} mudou para fase {nova_fase_num}")
            return self._converter_para_response(os)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao mudar fase da OS {os_id}: {e}")
            raise

    def obter_fases_os(self, os_id: int) -> List[Dict[str, Any]]:
        """
        Obtém todas as fases de uma OS com status atual

        Args:
            os_id: ID da OS

        Returns:
            Lista de fases com dados completos
        """
        try:
            fases = self.db.query(FaseOS).filter(
                FaseOS.ordem_servico_id == os_id
            ).order_by(FaseOS.numero_fase).all()

            fases_data = []
            for fase in fases:
                fase_info = FASES_OS.get(fase.numero_fase, {})

                fases_data.append({
                    "id": fase.id,
                    "numero_fase": fase.numero_fase,
                    "nome_fase": fase.nome_fase,
                    "descricao": fase_info.get("descricao", ""),
                    "status": fase.status,
                    "obrigatoria": fase.obrigatoria,
                    "data_inicio": fase.data_inicio,
                    "data_prazo": fase.data_prazo,
                    "data_conclusao": fase.data_conclusao,
                    "responsavel": fase.responsavel,
                    "checklist": fase_info.get("checklist", []),
                    "checklist_status": fase.checklist_itens or {},
                    "observacoes": fase.observacoes,
                    "anexos": fase.anexos or [],
                    "progresso": self._calcular_progresso_fase(fase)
                })

            return fases_data

        except Exception as e:
            logger.error(f"Erro ao obter fases da OS {os_id}: {e}")
            raise

    # ================================
    # ESTATÍSTICAS E DASHBOARD
    # ================================

    def obter_estatisticas(self) -> EstatisticasOS:
        """
        Obtém estatísticas gerais das OS

        Returns:
            EstatisticasOS: Estatísticas completas
        """
        try:
            # Total de OS
            total_os = self.db.query(OrdemServico).count()

            # Por status
            por_status = {}
            status_counts = self.db.query(
                OrdemServico.status_geral,
                func.count(OrdemServico.id)
            ).group_by(OrdemServico.status_geral).all()

            for status, count in status_counts:
                por_status[status] = count

            # Por fase
            por_fase = {}
            fase_counts = self.db.query(
                OrdemServico.status_fase,
                func.count(OrdemServico.id)
            ).group_by(OrdemServico.status_fase).all()

            for fase, count in fase_counts:
                fase_nome = FASES_OS.get(fase, {}).get("nome", f"Fase {fase}")
                por_fase[fase_nome] = count

            # Por prioridade
            por_prioridade = {}
            prioridade_counts = self.db.query(
                OrdemServico.prioridade,
                func.count(OrdemServico.id)
            ).group_by(OrdemServico.prioridade).all()

            for prioridade, count in prioridade_counts:
                por_prioridade[prioridade] = count

            # Por tipo
            por_tipo = {}
            tipo_counts = self.db.query(
                OrdemServico.tipo_servico,
                func.count(OrdemServico.id)
            ).group_by(OrdemServico.tipo_servico).all()

            for tipo, count in tipo_counts:
                por_tipo[tipo] = count

            # Valor total pendente
            valor_pendente = self.db.query(
                func.sum(OrdemServico.valor_final)
            ).filter(
                OrdemServico.status_geral.in_([STATUS_ABERTA, STATUS_EM_ANDAMENTO])
            ).scalar() or Decimal('0.00')

            return EstatisticasOS(
                total_os=total_os,
                por_status=por_status,
                por_fase=por_fase,
                por_prioridade=por_prioridade,
                por_tipo=por_tipo,
                valor_total_pendente=valor_pendente
            )

        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            raise

    def obter_dashboard(self) -> DashboardOS:
        """
        Obtém dados completos para o dashboard

        Returns:
            DashboardOS: Dados do dashboard
        """
        try:
            # Estatísticas gerais
            estatisticas = self.obter_estatisticas()

            # OS urgentes
            os_urgentes = self.db.query(OrdemServico).filter(
                OrdemServico.prioridade == "Urgente",
                OrdemServico.status_geral.in_([STATUS_ABERTA, STATUS_EM_ANDAMENTO])
            ).order_by(desc(OrdemServico.created_at)).limit(10).all()

            # OS atrasadas (prazo vencido)
            hoje = datetime.now()
            os_atrasadas = self.db.query(OrdemServico).filter(
                OrdemServico.data_prevista_conclusao < hoje,
                OrdemServico.status_geral.in_([STATUS_ABERTA, STATUS_EM_ANDAMENTO])
            ).order_by(asc(OrdemServico.data_prevista_conclusao)).limit(10).all()

            # OS para hoje
            inicio_dia = hoje.replace(hour=0, minute=0, second=0, microsecond=0)
            fim_dia = inicio_dia + timedelta(days=1)

            os_hoje = self.db.query(OrdemServico).filter(
                OrdemServico.data_prevista_conclusao >= inicio_dia,
                OrdemServico.data_prevista_conclusao < fim_dia,
                OrdemServico.status_geral.in_([STATUS_ABERTA, STATUS_EM_ANDAMENTO])
            ).order_by(asc(OrdemServico.data_prevista_conclusao)).all()

            # Fases pendentes
            fases_pendentes = {}
            for fase_num, fase_info in FASES_OS.items():
                count = self.db.query(OrdemServico).filter(
                    OrdemServico.status_fase == fase_num,
                    OrdemServico.status_geral.in_(
                        [STATUS_ABERTA, STATUS_EM_ANDAMENTO]
                    )
                ).count()
                fases_pendentes[fase_info["nome"]] = count

            # Converter para resumos
            def os_para_resumo(os_list):
                resumos = []
                for os in os_list:
                    resumo = ResumoOrdemServico(
                        id=os.id,
                        numero_os=os.numero_os,
                        titulo=os.titulo,
                        cliente_nome=os.cliente.nome if os.cliente else "N/A",
                        status=os.status_geral,
                        fase_atual=self._get_fase_enum(os.status_fase),
                        prioridade=os.prioridade,
                        tipo_servico=os.tipo_servico,
                        progresso_percentual=self._calcular_progresso(os.status_fase),
                        data_solicitacao=os.data_abertura,
                        data_prazo=os.data_prevista_conclusao,
                        valor_final=os.valor_final,
                        urgente=(os.prioridade == "Urgente")
                    )
                    resumos.append(resumo)
                return resumos

            return DashboardOS(
                estatisticas=estatisticas,
                os_urgentes=os_para_resumo(os_urgentes),
                os_atrasadas=os_para_resumo(os_atrasadas),
                os_hoje=os_para_resumo(os_hoje),
                fases_pendentes=fases_pendentes
            )

        except Exception as e:
            logger.error(f"Erro ao obter dashboard: {e}")
            raise

    # ================================
    # MÉTODOS AUXILIARES PRIVADOS
    # ================================

    def _gerar_numero_os(self) -> str:
        """Gera um número único para a OS"""
        try:
            # Buscar último número do ano atual
            ano_atual = datetime.now().year
            ultimo_numero = self.db.query(OrdemServico).filter(
                OrdemServico.numero_os.like(f"OS-{ano_atual}-%")
            ).order_by(desc(OrdemServico.numero_os)).first()

            if ultimo_numero:
                # Extrair o número sequencial
                parts = ultimo_numero.numero_os.split('-')
                if len(parts) == 3:
                    seq = int(parts[2]) + 1
                else:
                    seq = 1
            else:
                seq = 1

            return f"OS-{ano_atual}-{seq:04d}"

        except Exception:
            # Fallback: usar timestamp
            timestamp = int(datetime.now().timestamp())
            return f"OS-{timestamp}"

    def _criar_fases_iniciais(self, os_id: int):
        """Cria todas as 7 fases para uma nova OS"""
        try:
            for fase_num, fase_info in FASES_OS.items():
                nova_fase = FaseOS(
                    ordem_servico_id=os_id,
                    numero_fase=fase_num,
                    nome_fase=fase_info["nome"],
                    descricao_fase=fase_info["descricao"],
                    status=STATUS_PENDENTE if fase_num > 1 else STATUS_EM_ANDAMENTO,
                    obrigatoria=True,
                    checklist_itens=dict.fromkeys(fase_info["checklist"], False)
                )

                # Primeira fase inicia automaticamente
                if fase_num == 1:
                    nova_fase.data_inicio = datetime.now()

                self.db.add(nova_fase)

        except Exception as e:
            logger.error(f"Erro ao criar fases iniciais: {e}")
            raise

    def _converter_para_response(self, os: OrdemServico) -> OrdemServicoResponse:
        """Converte modelo OrdemServico para schema de resposta"""
        try:
            # Calcular dados derivados
            fases_concluidas = self.db.query(FaseOS).filter(
                and_(
                    FaseOS.ordem_servico_id == os.id,
                    FaseOS.status == "Concluída"
                )
            ).count()

            progresso = self._calcular_progresso(os.status_fase)

            return OrdemServicoResponse(
                id=os.id,
                numero_os=os.numero_os,
                cliente_id=os.cliente_id,
                titulo=os.titulo,
                descricao=os.observacoes_abertura or "",
                tipo_servico=os.tipo_servico,
                prioridade=os.prioridade,
                endereco_servico=os.endereco_execucao or "",
                cep_servico=os.cep_execucao or "",
                cidade_servico=os.cidade_execucao or "",
                estado_servico=os.estado_execucao or "",
                data_solicitacao=os.data_abertura,
                data_prazo=os.data_prevista_conclusao,
                valor_estimado=os.valor_orcamento,
                valor_final=os.valor_final,
                observacoes=os.observacoes_internas,
                requer_orcamento=True,  # Default
                urgente=(os.prioridade == "Urgente"),
                status=os.status_geral,
                fase_atual=self._get_fase_enum(os.status_fase),
                progresso_percentual=progresso,
                usuario_criacao=os.usuario_abertura,
                usuario_ultima_alteracao=os.usuario_responsavel,
                usuario_responsavel=os.tecnico_responsavel,
                created_at=os.created_at,
                updated_at=os.updated_at,
                cliente_nome=os.cliente.nome if os.cliente else "N/A",
                total_fases=7,
                fases_concluidas=fases_concluidas
            )

        except Exception as e:
            logger.error(f"Erro ao converter OS para response: {e}")
            raise

    def _get_fase_enum(self, fase_num: int) -> str:
        """Converte número da fase para enum"""
        mapping = {
            1: "1-Criação",
            2: "2-Visita Técnica", 
            3: "3-Orçamento",
            4: "4-Aprovação",
            5: "5-Execução",
            6: "6-Entrega",
            7: "7-Finalização"
        }
        return mapping.get(fase_num, "1-Criação")

    def _calcular_progresso(self, fase_atual: int) -> float:
        """Calcula percentual de progresso baseado na fase"""
        if fase_atual <= 0:
            return 0.0
        if fase_atual >= 7:
            return 100.0

        # Cada fase representa ~14.3% (100/7)
        return (fase_atual / 7) * 100

    def _calcular_progresso_fase(self, fase: FaseOS) -> float:
        """Calcula progresso individual de uma fase"""
        if fase.status == "Concluída":
            return 100.0
        elif fase.status == "Em Andamento":
            # Calcular baseado no checklist
            if fase.checklist_itens:
                total_itens = len(fase.checklist_itens)
                itens_concluidos = sum(1 for v in fase.checklist_itens.values() if v)
                return (itens_concluidos / total_itens) * 100 if total_itens > 0 else 0.0
            else:
                return 50.0  # Default para em andamento
        else:
            return 0.0

    def _executar_acoes_fase(self, os: OrdemServico, fase: int):
        """Executa ações específicas para cada fase"""
        try:
            if fase == 2:  # Visita Técnica
                self._notificar_agendamento_visita(os)
            elif fase == 3:  # Orçamento
                self._notificar_orcamento_disponivel(os)
            elif fase == 4:  # Acompanhamento
                self._notificar_acompanhamento_orcamento(os)
            elif fase == 5:  # Execução
                self._notificar_inicio_execucao(os)
            elif fase == 6:  # Finalização
                self._notificar_finalizacao_servico(os)
            elif fase == 7:  # Arquivo
                self._notificar_conclusao_os(os)

        except Exception as e:
            logger.warning(f"Erro ao executar ações da fase {fase}: {e}")

    def _notificar_nova_os(self, os: OrdemServico, cliente: Cliente):
        """Envia notificação de nova OS via WhatsApp"""
        try:
            if cliente.telefone:
                template_data = {
                    "numero_os": os.numero_os,
                    "cliente_nome": cliente.nome,
                    "tipo_servico": os.tipo_servico,
                    "data_abertura": os.data_abertura.strftime("%d/%m/%Y %H:%M")
                }

                self.comunicacao_service.enviar_whatsapp(
                    numero=cliente.telefone,
                    template="nova_os",
                    dados=template_data
                )

        except Exception as e:
            logger.warning(f"Erro ao notificar nova OS: {e}")

    def _notificar_agendamento_visita(self, os: OrdemServico):
        """Notifica necessidade de agendamento de visita técnica"""
        try:
            if os.cliente and os.cliente.telefone:
                template_data = {
                    "numero_os": os.numero_os,
                    "cliente_nome": os.cliente.nome
                }

                self.comunicacao_service.enviar_whatsapp(
                    numero=os.cliente.telefone,
                    template="agendamento_visita",
                    dados=template_data
                )

        except Exception as e:
            logger.warning(f"Erro ao notificar agendamento: {e}")

    def _notificar_orcamento_disponivel(self, os: OrdemServico):
        """Notifica que orçamento está disponível"""
        try:
            if os.cliente and os.cliente.telefone:
                template_data = {
                    "numero_os": os.numero_os,
                    "cliente_nome": os.cliente.nome
                }

                self.comunicacao_service.enviar_whatsapp(
                    numero=os.cliente.telefone,
                    template="orcamento_disponivel",
                    dados=template_data
                )

        except Exception as e:
            logger.warning(f"Erro ao notificar orçamento: {e}")

    def _notificar_acompanhamento_orcamento(self, os: OrdemServico):
        """Notifica acompanhamento do orçamento"""
        try:
            if os.cliente and os.cliente.telefone:
                template_data = {
                    "numero_os": os.numero_os,
                    "cliente_nome": os.cliente.nome
                }

                self.comunicacao_service.enviar_whatsapp(
                    numero=os.cliente.telefone,
                    template="acompanhamento_orcamento",
                    dados=template_data
                )

        except Exception as e:
            logger.warning(f"Erro ao notificar acompanhamento: {e}")

    def _notificar_inicio_execucao(self, os: OrdemServico):
        """Notifica início da execução do serviço"""
        try:
            if os.cliente and os.cliente.telefone:
                template_data = {
                    "numero_os": os.numero_os,
                    "cliente_nome": os.cliente.nome
                }

                self.comunicacao_service.enviar_whatsapp(
                    numero=os.cliente.telefone,
                    template="inicio_execucao",
                    dados=template_data
                )

        except Exception as e:
            logger.warning(f"Erro ao notificar execução: {e}")

    def _notificar_finalizacao_servico(self, os: OrdemServico):
        """Notifica finalização do serviço"""
        try:
            if os.cliente and os.cliente.telefone:
                template_data = {
                    "numero_os": os.numero_os,
                    "cliente_nome": os.cliente.nome
                }

                self.comunicacao_service.enviar_whatsapp(
                    numero=os.cliente.telefone,
                    template="finalizacao_servico",
                    dados=template_data
                )

        except Exception as e:
            logger.warning(f"Erro ao notificar finalização: {e}")

    def _notificar_conclusao_os(self, os: OrdemServico):
        """Notifica conclusão total da OS"""
        try:
            if os.cliente and os.cliente.telefone:
                template_data = {
                    "numero_os": os.numero_os,
                    "cliente_nome": os.cliente.nome
                }

                self.comunicacao_service.enviar_whatsapp(
                    numero=os.cliente.telefone,
                    template="conclusao_os",
                    dados=template_data
                )

        except Exception as e:
            logger.warning(f"Erro ao notificar conclusão: {e}")