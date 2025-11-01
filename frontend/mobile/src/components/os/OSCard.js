import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { theme } from '../../styles/theme';

const STATUS_CONFIG = {
  'solicitacao': {
    color: theme.colors.warning,
    icon: 'pending',
    label: 'Solicitação',
    bgColor: '#FF9800',
  },
  'orcamento': {
    color: theme.colors.info,
    icon: 'description',
    label: 'Orçamento',
    bgColor: '#2196F3',
  },
  'aprovacao': {
    color: theme.colors.secondary,
    icon: 'approval',
    label: 'Aprovação',
    bgColor: '#9C27B0',
  },
  'agendamento': {
    color: theme.colors.primary,
    icon: 'schedule',
    label: 'Agendamento',
    bgColor: '#3F51B5',
  },
  'visita_tecnica': {
    color: theme.colors.primary,
    icon: 'engineering',
    label: 'Visita Técnica',
    bgColor: '#3F51B5',
  },
  'execucao': {
    color: theme.colors.success,
    icon: 'build',
    label: 'Execução',
    bgColor: '#4CAF50',
  },
  'entrega': {
    color: theme.colors.success,
    icon: 'local-shipping',
    label: 'Entrega',
    bgColor: '#4CAF50',
  },
  'pos_venda': {
    color: theme.colors.disabled,
    icon: 'check-circle',
    label: 'Concluída',
    bgColor: '#9E9E9E',
  },
};

const PRIORITY_CONFIG = {
  'baixa': { color: theme.colors.success, icon: 'low-priority' },
  'media': { color: theme.colors.warning, icon: 'priority-high' },
  'alta': { color: theme.colors.error, icon: 'warning' },
  'urgente': { color: theme.colors.error, icon: 'emergency' },
};

export default function OSCard({ 
  os, 
  onPress, 
  onQuickAction,
  showQuickActions = true,
  compact = false 
}) {
  const statusConfig = STATUS_CONFIG[os.fase_atual] || STATUS_CONFIG['solicitacao'];
  const priorityConfig = PRIORITY_CONFIG[os.prioridade] || PRIORITY_CONFIG['media'];

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
    });
  };

  const formatTime = (timeString) => {
    if (!timeString) return '';
    return timeString.substring(0, 5);
  };

  const isToday = () => {
    if (!os.data_agendamento) return false;
    const today = new Date().toDateString();
    return new Date(os.data_agendamento).toDateString() === today;
  };

  const isOverdue = () => {
    if (!os.data_agendamento) return false;
    const today = new Date();
    const agendamento = new Date(os.data_agendamento);
    return agendamento < today && os.fase_atual !== 'pos_venda';
  };

  const renderQuickActions = () => {
    if (!showQuickActions) return null;

    const actions = [];

    // Ação baseada na fase atual
    switch (os.fase_atual) {
      case 'visita_tecnica':
      case 'execucao':
        actions.push({
          icon: 'play-arrow',
          label: 'Iniciar',
          action: 'start',
          style: styles.startButton,
          textStyle: styles.startButtonText,
        });
        break;
      case 'agendamento':
        actions.push({
          icon: 'engineering',
          label: 'Visita',
          action: 'visit',
          style: styles.visitButton,
          textStyle: styles.visitButtonText,
        });
        break;
    }

    // Ações sempre disponíveis
    if (os.endereco) {
      actions.push({
        icon: 'directions',
        action: 'navigate',
        style: styles.iconButton,
      });
    }

    if (os.cliente_telefone) {
      actions.push({
        icon: 'phone',
        action: 'call',
        style: styles.iconButton,
      });
    }

    actions.push({
      icon: 'message',
      action: 'message',
      style: styles.iconButton,
    });

    return (
      <View style={styles.quickActions}>
        {actions.map((action, index) => (
          <TouchableOpacity
            key={index}
            style={[styles.actionButton, action.style]}
            onPress={() => onQuickAction?.(os, action.action)}
            activeOpacity={0.7}
          >
            <Icon 
              name={action.icon} 
              size={action.label ? 16 : 18} 
              color={action.textStyle ? '#FFFFFF' : theme.colors.primary} 
            />
            {action.label && (
              <Text style={[styles.actionButtonText, action.textStyle]}>
                {action.label}
              </Text>
            )}
          </TouchableOpacity>
        ))}
      </View>
    );
  };

  return (
    <TouchableOpacity
      style={[
        styles.container,
        compact && styles.compactContainer,
        isOverdue() && styles.overdueContainer,
        isToday() && styles.todayContainer,
      ]}
      onPress={() => onPress?.(os)}
      activeOpacity={0.7}
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.osInfo}>
          <Text style={styles.osNumber}>OS #{os.numero}</Text>
          {os.prioridade && os.prioridade !== 'media' && (
            <View style={styles.priorityBadge}>
              <Icon 
                name={priorityConfig.icon} 
                size={12} 
                color={priorityConfig.color} 
              />
            </View>
          )}
        </View>
        
        <View style={[
          styles.statusBadge, 
          { backgroundColor: statusConfig.bgColor + '20' }
        ]}>
          <Icon 
            name={statusConfig.icon} 
            size={12} 
            color={statusConfig.color} 
          />
          <Text style={[
            styles.statusText, 
            { color: statusConfig.color }
          ]}>
            {statusConfig.label}
          </Text>
        </View>
      </View>

      {/* Cliente */}
      <Text style={styles.clienteName} numberOfLines={1}>
        {os.cliente_nome}
      </Text>

      {/* Serviço */}
      <Text 
        style={styles.serviceDescription} 
        numberOfLines={compact ? 1 : 2}
      >
        {os.descricao_servico}
      </Text>

      {/* Informações adicionais */}
      <View style={styles.infoContainer}>
        {/* Endereço */}
        {os.endereco && (
          <View style={styles.infoRow}>
            <Icon name="location-on" size={14} color={theme.colors.textSecondary} />
            <Text style={styles.infoText} numberOfLines={1}>
              {os.endereco}
            </Text>
          </View>
        )}

        {/* Data e hora */}
        {os.data_agendamento && (
          <View style={styles.infoRow}>
            <Icon 
              name={isToday() ? 'today' : 'schedule'} 
              size={14} 
              color={isToday() ? theme.colors.primary : theme.colors.textSecondary} 
            />
            <Text style={[
              styles.infoText,
              isToday() && { color: theme.colors.primary, fontWeight: '600' }
            ]}>
              {formatDate(os.data_agendamento)}
              {os.hora_agendamento && ` às ${formatTime(os.hora_agendamento)}`}
            </Text>
          </View>
        )}

        {/* Valor estimado */}
        {os.valor_estimado && (
          <View style={styles.infoRow}>
            <Icon name="attach-money" size={14} color={theme.colors.textSecondary} />
            <Text style={styles.infoText}>
              R$ {parseFloat(os.valor_estimado).toFixed(2).replace('.', ',')}
            </Text>
          </View>
        )}
      </View>

      {/* Indicadores visuais */}
      <View style={styles.indicators}>
        {os.fotos && os.fotos.length > 0 && (
          <View style={styles.indicator}>
            <Icon name="photo-camera" size={12} color={theme.colors.primary} />
            <Text style={styles.indicatorText}>{os.fotos.length}</Text>
          </View>
        )}
        
        {os.assinatura_cliente && (
          <View style={styles.indicator}>
            <Icon name="draw" size={12} color={theme.colors.success} />
            <Text style={styles.indicatorText}>Assinado</Text>
          </View>
        )}

        {os.observacoes_tecnico && (
          <View style={styles.indicator}>
            <Icon name="note" size={12} color={theme.colors.warning} />
            <Text style={styles.indicatorText}>Obs</Text>
          </View>
        )}
      </View>

      {/* Ações rápidas */}
      {renderQuickActions()}

      {/* Indicador de atualização pendente */}
      {os._pendingSync && (
        <View style={styles.syncIndicator}>
          <Icon name="sync" size={12} color={theme.colors.warning} />
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  compactContainer: {
    padding: 12,
    marginBottom: 8,
  },
  overdueContainer: {
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.error,
  },
  todayContainer: {
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.primary,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  osInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  osNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  priorityBadge: {
    marginLeft: 8,
    padding: 2,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 11,
    fontWeight: '600',
    marginLeft: 4,
  },
  clienteName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 4,
  },
  serviceDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    lineHeight: 20,
    marginBottom: 12,
  },
  infoContainer: {
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  infoText: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    marginLeft: 6,
    flex: 1,
  },
  indicators: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  indicator: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    marginRight: 8,
    marginBottom: 4,
  },
  indicatorText: {
    fontSize: 11,
    color: theme.colors.textSecondary,
    marginLeft: 2,
    fontWeight: '500',
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
  },
  actionButton: {
    marginLeft: 8,
    paddingVertical: 6,
    paddingHorizontal: 8,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconButton: {
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.disabled,
    width: 32,
    height: 32,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 0,
    paddingHorizontal: 0,
  },
  startButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 12,
  },
  startButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    marginLeft: 4,
  },
  visitButton: {
    backgroundColor: theme.colors.secondary,
    paddingHorizontal: 12,
  },
  visitButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    marginLeft: 4,
  },
  actionButtonText: {
    fontSize: 12,
  },
  syncIndicator: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: theme.colors.warning + '20',
    borderRadius: 10,
    padding: 4,
  },
});