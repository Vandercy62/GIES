import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Linking,
  Share,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';
import moment from 'moment';

import {
  updateAppointment,
  deleteAppointment,
  selectLoading,
} from '../../store/slices/agendaSlice';
import { theme } from '../../styles/theme';

const STATUS_CONFIGS = {
  pendente: {
    color: theme.colors.warning,
    icon: 'schedule',
    label: 'Pendente',
  },
  confirmado: {
    color: theme.colors.success,
    icon: 'check-circle',
    label: 'Confirmado',
  },
  em_andamento: {
    color: theme.colors.primary,
    icon: 'play-circle',
    label: 'Em Andamento',
  },
  realizado: {
    color: theme.colors.success,
    icon: 'task-alt',
    label: 'Realizado',
  },
  cancelado: {
    color: theme.colors.error,
    icon: 'cancel',
    label: 'Cancelado',
  },
};

const PRIORITY_CONFIGS = {
  baixa: { color: '#4CAF50', label: 'Baixa' },
  normal: { color: '#2196F3', label: 'Normal' },
  alta: { color: '#FF9800', label: 'Alta' },
  urgente: { color: '#F44336', label: 'Urgente' },
};

export default function AppointmentDetailsScreen({ navigation, route }) {
  const dispatch = useDispatch();
  const loading = useSelector(selectLoading);
  
  const { appointment } = route.params;
  const [currentAppointment, setCurrentAppointment] = useState(appointment);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    // Configurar header da tela
    navigation.setOptions({
      title: 'Detalhes do Agendamento',
      headerRight: () => (
        <View style={styles.headerActions}>
          <TouchableOpacity
            onPress={handleEdit}
            style={styles.headerButton}
            disabled={loading || actionLoading}
          >
            <Icon name="edit" size={24} color={theme.colors.primary} />
          </TouchableOpacity>
          
          <TouchableOpacity
            onPress={handleShare}
            style={styles.headerButton}
            disabled={loading || actionLoading}
          >
            <Icon name="share" size={24} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>
      ),
    });

    setCurrentAppointment(appointment);
  }, [navigation, appointment, loading, actionLoading]);

  const handleEdit = () => {
    navigation.navigate('CreateAppointment', {
      appointment: currentAppointment,
      isEdit: true,
      onSuccess: (updatedAppointment) => {
        setCurrentAppointment(updatedAppointment);
      }
    });
  };

  const handleDelete = () => {
    Alert.alert(
      'Confirmar Exclusão',
      'Tem certeza que deseja excluir este agendamento? Esta ação não pode ser desfeita.',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Excluir',
          style: 'destructive',
          onPress: confirmDelete,
        },
      ]
    );
  };

  const confirmDelete = async () => {
    try {
      setActionLoading(true);
      await dispatch(deleteAppointment(currentAppointment.id)).unwrap();
      Alert.alert('Sucesso', 'Agendamento excluído com sucesso', [
        { text: 'OK', onPress: () => navigation.goBack() }
      ]);
    } catch (error) {
      Alert.alert('Erro', 'Falha ao excluir agendamento');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      setActionLoading(true);
      const updatedAppointment = {
        ...currentAppointment,
        status: newStatus,
        updatedAt: new Date().toISOString(),
      };

      await dispatch(updateAppointment(updatedAppointment)).unwrap();
      setCurrentAppointment(updatedAppointment);
      
      Alert.alert('Sucesso', 'Status atualizado com sucesso');
    } catch (error) {
      Alert.alert('Erro', 'Falha ao atualizar status');
    } finally {
      setActionLoading(false);
    }
  };

  const handleCall = () => {
    if (currentAppointment.clientPhone) {
      const phoneNumber = currentAppointment.clientPhone.replace(/\D/g, '');
      Linking.openURL(`tel:${phoneNumber}`);
    } else {
      Alert.alert('Aviso', 'Telefone não disponível');
    }
  };

  const handleEmail = () => {
    if (currentAppointment.clientEmail) {
      const subject = `Agendamento: ${currentAppointment.title}`;
      const body = `Olá ${currentAppointment.clientName},\n\nSobre o agendamento marcado para ${formatDateTime()}.`;
      
      Linking.openURL(`mailto:${currentAppointment.clientEmail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`);
    } else {
      Alert.alert('Aviso', 'Email não disponível');
    }
  };

  const handleShare = async () => {
    const shareContent = `
📅 Agendamento: ${currentAppointment.title}
👤 Cliente: ${currentAppointment.clientName}
📱 Telefone: ${currentAppointment.clientPhone || 'N/A'}
📧 Email: ${currentAppointment.clientEmail || 'N/A'}
📍 Local: ${currentAppointment.location || 'N/A'}
🗓️ Data/Hora: ${formatDateTime()}
📝 Status: ${STATUS_CONFIGS[currentAppointment.status]?.label || currentAppointment.status}
${currentAppointment.notes ? `\n📋 Observações: ${currentAppointment.notes}` : ''}
    `.trim();

    try {
      await Share.share({
        message: shareContent,
        title: 'Detalhes do Agendamento',
      });
    } catch (error) {
      console.error('Erro ao compartilhar:', error);
    }
  };

  const handleNavigate = () => {
    if (currentAppointment.location) {
      const encodedLocation = encodeURIComponent(currentAppointment.location);
      const url = `https://maps.google.com/?q=${encodedLocation}`;
      Linking.openURL(url);
    } else {
      Alert.alert('Aviso', 'Localização não disponível');
    }
  };

  const formatDateTime = () => {
    const date = moment(currentAppointment.date).format('DD/MM/YYYY');
    const time = currentAppointment.time;
    return `${date} às ${time}`;
  };

  const formatDuration = () => {
    const minutes = currentAppointment.duration || 60;
    if (minutes < 60) {
      return `${minutes} min`;
    } else {
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}min` : `${hours}h`;
    }
  };

  const getNextStatus = (currentStatus) => {
    const statusFlow = {
      pendente: 'confirmado',
      confirmado: 'em_andamento',
      em_andamento: 'realizado',
    };
    return statusFlow[currentStatus];
  };

  const canAdvanceStatus = () => {
    const nextStatus = getNextStatus(currentAppointment.status);
    return nextStatus && currentAppointment.status !== 'realizado' && currentAppointment.status !== 'cancelado';
  };

  const renderInfoCard = (icon, title, content, onPress, showPress = false) => (
    <TouchableOpacity
      style={[styles.infoCard, !onPress && styles.infoCardDisabled]}
      onPress={onPress}
      disabled={!onPress}
      activeOpacity={onPress ? 0.7 : 1}
    >
      <View style={styles.infoCardIcon}>
        <Icon name={icon} size={24} color={theme.colors.primary} />
      </View>
      <View style={styles.infoCardContent}>
        <Text style={styles.infoCardTitle}>{title}</Text>
        <Text style={styles.infoCardText}>{content}</Text>
      </View>
      {onPress && showPress && (
        <Icon name="chevron-right" size={20} color={theme.colors.textSecondary} />
      )}
    </TouchableOpacity>
  );

  const renderStatusBadge = () => {
    const config = STATUS_CONFIGS[currentAppointment.status] || {};
    return (
      <View style={[styles.statusBadge, { backgroundColor: config.color }]}>
        <Icon name={config.icon} size={16} color="#FFFFFF" />
        <Text style={styles.statusText}>{config.label}</Text>
      </View>
    );
  };

  const renderPriorityBadge = () => {
    const config = PRIORITY_CONFIGS[currentAppointment.priority] || PRIORITY_CONFIGS.normal;
    return (
      <View style={[styles.priorityBadge, { borderColor: config.color }]}>
        <Text style={[styles.priorityText, { color: config.color }]}>
          {config.label}
        </Text>
      </View>
    );
  };

  const renderActionButtons = () => (
    <View style={styles.actionSection}>
      <Text style={styles.sectionTitle}>Ações Rápidas</Text>
      
      <View style={styles.actionGrid}>
        {currentAppointment.clientPhone && (
          <TouchableOpacity style={styles.actionButton} onPress={handleCall}>
            <Icon name="phone" size={24} color={theme.colors.success} />
            <Text style={styles.actionButtonText}>Ligar</Text>
          </TouchableOpacity>
        )}

        {currentAppointment.clientEmail && (
          <TouchableOpacity style={styles.actionButton} onPress={handleEmail}>
            <Icon name="email" size={24} color={theme.colors.primary} />
            <Text style={styles.actionButtonText}>Email</Text>
          </TouchableOpacity>
        )}

        {currentAppointment.location && (
          <TouchableOpacity style={styles.actionButton} onPress={handleNavigate}>
            <Icon name="navigation" size={24} color={theme.colors.warning} />
            <Text style={styles.actionButtonText}>Navegar</Text>
          </TouchableOpacity>
        )}

        {canAdvanceStatus() && (
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => handleStatusChange(getNextStatus(currentAppointment.status))}
            disabled={actionLoading}
          >
            {actionLoading ? (
              <ActivityIndicator size="small" color={theme.colors.primary} />
            ) : (
              <Icon name="arrow-forward" size={24} color={theme.colors.primary} />
            )}
            <Text style={styles.actionButtonText}>
              {getNextStatus(currentAppointment.status) === 'confirmado' && 'Confirmar'}
              {getNextStatus(currentAppointment.status) === 'em_andamento' && 'Iniciar'}
              {getNextStatus(currentAppointment.status) === 'realizado' && 'Finalizar'}
            </Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Carregando detalhes...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header do Agendamento */}
      <View style={styles.header}>
        <Text style={styles.title}>{currentAppointment.title}</Text>
        <View style={styles.badgeContainer}>
          {renderStatusBadge()}
          {renderPriorityBadge()}
        </View>
      </View>

      {/* Informações Principais */}
      <View style={styles.section}>
        {renderInfoCard(
          'person',
          'Cliente',
          currentAppointment.clientName,
          null
        )}

        {renderInfoCard(
          'schedule',
          'Data e Horário',
          formatDateTime(),
          null
        )}

        {renderInfoCard(
          'timer',
          'Duração',
          formatDuration(),
          null
        )}

        {currentAppointment.location && renderInfoCard(
          'location-on',
          'Localização',
          currentAppointment.location,
          handleNavigate,
          true
        )}

        {currentAppointment.clientPhone && renderInfoCard(
          'phone',
          'Telefone',
          currentAppointment.clientPhone,
          handleCall,
          true
        )}

        {currentAppointment.clientEmail && renderInfoCard(
          'email',
          'Email',
          currentAppointment.clientEmail,
          handleEmail,
          true
        )}
      </View>

      {/* Descrição e Observações */}
      {(currentAppointment.description || currentAppointment.notes) && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Detalhes</Text>
          
          {currentAppointment.description && (
            <View style={styles.detailsCard}>
              <Text style={styles.detailsTitle}>Descrição</Text>
              <Text style={styles.detailsText}>{currentAppointment.description}</Text>
            </View>
          )}

          {currentAppointment.notes && (
            <View style={styles.detailsCard}>
              <Text style={styles.detailsTitle}>Observações</Text>
              <Text style={styles.detailsText}>{currentAppointment.notes}</Text>
            </View>
          )}
        </View>
      )}

      {/* Ações Rápidas */}
      {renderActionButtons()}

      {/* Botões de Ação Principal */}
      <View style={styles.mainActions}>
        <TouchableOpacity
          style={[styles.mainActionButton, styles.editButton]}
          onPress={handleEdit}
          disabled={actionLoading}
        >
          <Icon name="edit" size={20} color="#FFFFFF" />
          <Text style={styles.mainActionButtonText}>Editar</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.mainActionButton, styles.deleteButton]}
          onPress={handleDelete}
          disabled={actionLoading}
        >
          <Icon name="delete" size={20} color="#FFFFFF" />
          <Text style={styles.mainActionButtonText}>Excluir</Text>
        </TouchableOpacity>
      </View>

      {/* Status Change Buttons */}
      {currentAppointment.status !== 'cancelado' && currentAppointment.status !== 'realizado' && (
        <View style={styles.statusActions}>
          {currentAppointment.status !== 'cancelado' && (
            <TouchableOpacity
              style={[styles.statusButton, styles.cancelButton]}
              onPress={() => handleStatusChange('cancelado')}
              disabled={actionLoading}
            >
              <Icon name="cancel" size={16} color={theme.colors.error} />
              <Text style={[styles.statusButtonText, { color: theme.colors.error }]}>
                Cancelar
              </Text>
            </TouchableOpacity>
          )}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: theme.colors.textSecondary,
  },
  headerActions: {
    flexDirection: 'row',
    gap: 8,
  },
  headerButton: {
    padding: 8,
  },
  header: {
    padding: 16,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 12,
  },
  badgeContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 4,
  },
  statusText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  priorityBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
  },
  priorityText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 16,
  },
  infoCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  infoCardDisabled: {
    opacity: 1,
  },
  infoCardIcon: {
    marginRight: 16,
  },
  infoCardContent: {
    flex: 1,
  },
  infoCardTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.textSecondary,
    marginBottom: 4,
  },
  infoCardText: {
    fontSize: 16,
    color: theme.colors.text,
  },
  detailsCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  detailsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 8,
  },
  detailsText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    lineHeight: 20,
  },
  actionSection: {
    padding: 16,
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    minWidth: 80,
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  actionButtonText: {
    marginTop: 8,
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.text,
    textAlign: 'center',
  },
  mainActions: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  mainActionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 8,
    gap: 8,
  },
  editButton: {
    backgroundColor: theme.colors.primary,
  },
  deleteButton: {
    backgroundColor: theme.colors.error,
  },
  mainActionButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  statusActions: {
    padding: 16,
    paddingTop: 0,
  },
  statusButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    gap: 8,
  },
  cancelButton: {
    borderColor: theme.colors.error,
    backgroundColor: 'transparent',
  },
  statusButtonText: {
    fontSize: 14,
    fontWeight: '600',
  },
});