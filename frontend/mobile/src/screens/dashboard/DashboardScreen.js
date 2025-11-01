import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Alert,
  Dimensions,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { selectUser } from '../../store/slices/authSlice';
import { 
  selectOSToday,
  selectOSPending,
  selectOSInProgress,
  fetchDashboardStats 
} from '../../store/slices/osSlice';
import { 
  selectTodayAppointments,
  fetchTodayAgenda 
} from '../../store/slices/agendamentoSlice';
import { 
  selectUnreadCount,
  fetchNotifications 
} from '../../store/slices/notificationsSlice';
import { selectSyncStatus } from '../../store/slices/syncSlice';
import { theme } from '../../styles/theme';

const { width } = Dimensions.get('window');

export default function DashboardScreen({ navigation }) {
  const dispatch = useDispatch();
  const user = useSelector(selectUser);
  const osToday = useSelector(selectOSToday);
  const osPending = useSelector(selectOSPending);
  const osInProgress = useSelector(selectOSInProgress);
  const todayAppointments = useSelector(selectTodayAppointments);
  const unreadNotifications = useSelector(selectUnreadCount);
  const syncStatus = useSelector(selectSyncStatus);

  const [refreshing, setRefreshing] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Atualizar hora atual
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000); // Atualizar a cada minuto

    return () => clearInterval(timer);
  }, []);

  // Carregar dados quando a tela ganhar foco
  useFocusEffect(
    useCallback(() => {
      loadDashboardData();
    }, [])
  );

  // Configurar header da tela
  useEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <TouchableOpacity
          style={styles.notificationButton}
          onPress={() => navigation.navigate('Notifications')}
        >
          <Icon name="notifications" size={24} color="#FFFFFF" />
          {unreadNotifications > 0 && (
            <View style={styles.notificationBadge}>
              <Text style={styles.notificationBadgeText}>
                {unreadNotifications > 99 ? '99+' : unreadNotifications}
              </Text>
            </View>
          )}
        </TouchableOpacity>
      ),
    });
  }, [navigation, unreadNotifications]);

  const loadDashboardData = async () => {
    try {
      await Promise.all([
        dispatch(fetchDashboardStats()),
        dispatch(fetchTodayAgenda()),
        dispatch(fetchNotifications()),
      ]);
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Bom dia';
    if (hour < 18) return 'Boa tarde';
    return 'Boa noite';
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('pt-BR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
    });
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleQuickAction = (action) => {
    switch (action) {
      case 'new_os':
        navigation.navigate('OSExecution');
        break;
      case 'agenda':
        navigation.navigate('Agenda');
        break;
      case 'os_list':
        navigation.navigate('OS');
        break;
      case 'analytics':
        navigation.navigate('Analytics');
        break;
      case 'profile':
        navigation.navigate('Perfil');
        break;
      default:
        break;
    }
  };

  const renderStatsCard = (title, value, icon, color, onPress) => (
    <TouchableOpacity
      style={[styles.statsCard, { borderLeftColor: color }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.statsCardContent}>
        <View style={styles.statsCardHeader}>
          <Text style={styles.statsCardTitle}>{title}</Text>
          <Icon name={icon} size={24} color={color} />
        </View>
        <Text style={[styles.statsCardValue, { color }]}>{value}</Text>
      </View>
    </TouchableOpacity>
  );

  const renderQuickAction = (title, icon, color, action) => (
    <TouchableOpacity
      style={styles.quickAction}
      onPress={() => handleQuickAction(action)}
      activeOpacity={0.7}
    >
      <View style={[styles.quickActionIcon, { backgroundColor: color + '20' }]}>
        <Icon name={icon} size={28} color={color} />
      </View>
      <Text style={styles.quickActionText}>{title}</Text>
    </TouchableOpacity>
  );

  const renderAgendaItem = (item, index) => (
    <TouchableOpacity
      key={index}
      style={styles.agendaItem}
      onPress={() => navigation.navigate('AgendaDetails', { appointment: item })}
      activeOpacity={0.7}
    >
      <View style={styles.agendaItemTime}>
        <Text style={styles.agendaItemTimeText}>{item.horario}</Text>
      </View>
      <View style={styles.agendaItemContent}>
        <Text style={styles.agendaItemTitle}>{item.titulo}</Text>
        <Text style={styles.agendaItemClient}>{item.cliente}</Text>
        <Text style={styles.agendaItemAddress}>{item.endereco}</Text>
      </View>
      <View style={styles.agendaItemStatus}>
        <View style={[
          styles.agendaItemStatusDot,
          { backgroundColor: item.status === 'confirmado' ? theme.colors.success : theme.colors.warning }
        ]} />
      </View>
    </TouchableOpacity>
  );

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={onRefresh}
          colors={[theme.colors.primary]}
          tintColor={theme.colors.primary}
        />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.greetingContainer}>
          <Text style={styles.greeting}>
            {getGreeting()}, {user?.nome?.split(' ')[0] || 'Usuário'}!
          </Text>
          <Text style={styles.date}>{formatDate(currentTime)}</Text>
          <Text style={styles.time}>{formatTime(currentTime)}</Text>
        </View>
        
        {/* Sync Status */}
        <TouchableOpacity style={styles.syncContainer}>
          <Icon
            name={syncStatus === 'syncing' ? 'sync' : 'cloud-done'}
            size={20}
            color={syncStatus === 'syncing' ? theme.colors.warning : theme.colors.success}
          />
          <Text style={[
            styles.syncText,
            { color: syncStatus === 'syncing' ? theme.colors.warning : theme.colors.success }
          ]}>
            {syncStatus === 'syncing' ? 'Sincronizando...' : 'Sincronizado'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Estatísticas */}
      <View style={styles.statsContainer}>
        <Text style={styles.sectionTitle}>Resumo do Dia</Text>
        <View style={styles.statsGrid}>
          {renderStatsCard(
            'OS de Hoje',
            osToday?.length || 0,
            'today',
            theme.colors.primary,
            () => navigation.navigate('OS', { filter: 'today' })
          )}
          {renderStatsCard(
            'Em Andamento',
            osInProgress?.length || 0,
            'play-circle-filled',
            theme.colors.warning,
            () => navigation.navigate('OS', { filter: 'in_progress' })
          )}
          {renderStatsCard(
            'Pendentes',
            osPending?.length || 0,
            'pending',
            theme.colors.error,
            () => navigation.navigate('OS', { filter: 'pending' })
          )}
          {renderStatsCard(
            'Agendamentos',
            todayAppointments?.length || 0,
            'event',
            theme.colors.success,
            () => navigation.navigate('Agenda')
          )}
        </View>
      </View>

      {/* Ações Rápidas */}
      <View style={styles.quickActionsContainer}>
        <Text style={styles.sectionTitle}>Ações Rápidas</Text>
        <View style={styles.quickActionsGrid}>
          {renderQuickAction(
            'Nova OS',
            'add-task',
            theme.colors.primary,
            'new_os'
          )}
          {renderQuickAction(
            'Minha Agenda',
            'calendar-today',
            theme.colors.success,
            'agenda'
          )}
          {renderQuickAction(
            'Ver OS',
            'list-alt',
            theme.colors.warning,
            'os_list'
          )}
          {renderQuickAction(
            'Analytics',
            'insert-chart',
            '#9C27B0',
            'analytics'
          )}
        </View>
      </View>

      {/* Próximos Agendamentos */}
      {todayAppointments && todayAppointments.length > 0 && (
        <View style={styles.agendaContainer}>
          <View style={styles.agendaHeader}>
            <Text style={styles.sectionTitle}>Próximos Agendamentos</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Agenda')}>
              <Text style={styles.viewAllText}>Ver todos</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.agendaList}>
            {todayAppointments.slice(0, 3).map((item, index) => renderAgendaItem(item, index))}
          </View>
        </View>
      )}

      {/* Dicas Rápidas */}
      <View style={styles.tipsContainer}>
        <Text style={styles.sectionTitle}>Dica do Dia</Text>
        <View style={styles.tipCard}>
          <Icon name="lightbulb" size={24} color={theme.colors.warning} />
          <View style={styles.tipContent}>
            <Text style={styles.tipTitle}>Modo Offline</Text>
            <Text style={styles.tipText}>
              Você pode trabalhar mesmo sem internet. Seus dados serão sincronizados quando a conexão for restabelecida.
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    padding: 16,
  },
  header: {
    marginBottom: 24,
  },
  greetingContainer: {
    marginBottom: 12,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 4,
  },
  date: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    marginBottom: 2,
    textTransform: 'capitalize',
  },
  time: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  syncContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: theme.colors.surface,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  syncText: {
    fontSize: 12,
    marginLeft: 6,
    fontWeight: '500',
  },
  statsContainer: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statsCard: {
    width: (width - 48) / 2,
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
  },
  statsCardContent: {
    justifyContent: 'space-between',
    height: 60,
  },
  statsCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  statsCardTitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    fontWeight: '500',
    flex: 1,
  },
  statsCardValue: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  quickActionsContainer: {
    marginBottom: 24,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickAction: {
    width: (width - 48) / 2,
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  quickActionIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  quickActionText: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.text,
    textAlign: 'center',
  },
  agendaContainer: {
    marginBottom: 24,
  },
  agendaHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  viewAllText: {
    fontSize: 14,
    color: theme.colors.primary,
    fontWeight: '600',
  },
  agendaList: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
  },
  agendaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.disabled,
  },
  agendaItemTime: {
    width: 60,
    marginRight: 16,
  },
  agendaItemTimeText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  agendaItemContent: {
    flex: 1,
  },
  agendaItemTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 2,
  },
  agendaItemClient: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 2,
  },
  agendaItemAddress: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  agendaItemStatus: {
    marginLeft: 12,
  },
  agendaItemStatusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  tipsContainer: {
    marginBottom: 24,
  },
  tipCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  tipContent: {
    flex: 1,
    marginLeft: 12,
  },
  tipTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 4,
  },
  tipText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    lineHeight: 20,
  },
  notificationButton: {
    position: 'relative',
    padding: 8,
    marginRight: 8,
  },
  notificationBadge: {
    position: 'absolute',
    top: 0,
    right: 0,
    backgroundColor: theme.colors.error,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  notificationBadgeText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
});