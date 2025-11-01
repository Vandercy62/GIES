import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import moment from 'moment';

import {
  selectNotifications,
  selectUnreadCount,
  selectNotificationsByCategory,
  selectRecentNotifications,
  selectNotificationsLoading,
  markAsRead,
  markAllAsRead,
  removeNotification,
  clearAllNotifications,
} from '../../store/slices/notificationsSlice';
import { theme } from '../../styles/theme';

const NOTIFICATION_ICONS = {
  appointment_reminder: 'event',
  new_os: 'work',
  os_overdue: 'warning',
  system: 'info',
  test: 'notifications',
};

const NOTIFICATION_COLORS = {
  appointment_reminder: theme.colors.primary,
  new_os: theme.colors.success,
  os_overdue: theme.colors.error,
  system: theme.colors.warning,
  test: theme.colors.textSecondary,
};

export default function NotificationsScreen({ navigation }) {
  const dispatch = useDispatch();
  const notifications = useSelector(selectNotifications);
  const unreadCount = useSelector(selectUnreadCount);
  const notificationsByCategory = useSelector(selectNotificationsByCategory);
  const recentNotifications = useSelector(selectRecentNotifications);
  const loading = useSelector(selectNotificationsLoading);

  const [filter, setFilter] = useState('all'); // all, unread, today
  const [refreshing, setRefreshing] = useState(false);
  const [selectedNotifications, setSelectedNotifications] = useState(new Set());
  const [selectionMode, setSelectionMode] = useState(false);

  useFocusEffect(
    useCallback(() => {
      // Marcar badge como lido quando tela ganhar foco
      if (unreadCount > 0) {
        // notificationService.clearBadge();
      }
    }, [unreadCount])
  );

  useEffect(() => {
    // Configurar header da tela
    navigation.setOptions({
      title: 'Notificações',
      headerRight: () => (
        <View style={styles.headerActions}>
          {selectionMode ? (
            <>
              <TouchableOpacity
                onPress={handleMarkSelectedAsRead}
                style={styles.headerButton}
                disabled={selectedNotifications.size === 0}
              >
                <Icon 
                  name="mark-email-read" 
                  size={24} 
                  color={selectedNotifications.size > 0 ? theme.colors.primary : theme.colors.disabled} 
                />
              </TouchableOpacity>
              
              <TouchableOpacity
                onPress={handleDeleteSelected}
                style={styles.headerButton}
                disabled={selectedNotifications.size === 0}
              >
                <Icon 
                  name="delete" 
                  size={24} 
                  color={selectedNotifications.size > 0 ? theme.colors.error : theme.colors.disabled} 
                />
              </TouchableOpacity>
              
              <TouchableOpacity
                onPress={exitSelectionMode}
                style={styles.headerButton}
              >
                <Icon name="close" size={24} color={theme.colors.text} />
              </TouchableOpacity>
            </>
          ) : (
            <>
              <TouchableOpacity
                onPress={handleMarkAllAsRead}
                style={styles.headerButton}
                disabled={unreadCount === 0}
              >
                <Icon 
                  name="done-all" 
                  size={24} 
                  color={unreadCount > 0 ? theme.colors.primary : theme.colors.disabled} 
                />
              </TouchableOpacity>
              
              <TouchableOpacity
                onPress={() => setSelectionMode(true)}
                style={styles.headerButton}
                disabled={notifications.length === 0}
              >
                <Icon 
                  name="checklist" 
                  size={24} 
                  color={notifications.length > 0 ? theme.colors.primary : theme.colors.disabled} 
                />
              </TouchableOpacity>
            </>
          )}
        </View>
      ),
    });
  }, [navigation, unreadCount, selectionMode, selectedNotifications, notifications.length]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    // Aqui você pode adicionar lógica para recarregar notificações do servidor
    setTimeout(() => setRefreshing(false), 1000);
  }, []);

  const getFilteredNotifications = () => {
    switch (filter) {
      case 'unread':
        return notifications.filter(n => !n.read);
      case 'today':
        return recentNotifications;
      default:
        return notifications;
    }
  };

  const handleNotificationPress = (notification) => {
    if (selectionMode) {
      toggleNotificationSelection(notification.id);
    } else {
      // Marcar como lida se não estiver
      if (!notification.read) {
        dispatch(markAsRead(notification.id));
      }
      
      // Navegar baseado no tipo de notificação
      handleNotificationNavigation(notification);
    }
  };

  const handleNotificationLongPress = (notification) => {
    if (!selectionMode) {
      setSelectionMode(true);
      setSelectedNotifications(new Set([notification.id]));
    }
  };

  const toggleNotificationSelection = (notificationId) => {
    const newSelection = new Set(selectedNotifications);
    if (newSelection.has(notificationId)) {
      newSelection.delete(notificationId);
    } else {
      newSelection.add(notificationId);
    }
    setSelectedNotifications(newSelection);
  };

  const exitSelectionMode = () => {
    setSelectionMode(false);
    setSelectedNotifications(new Set());
  };

  const handleMarkAllAsRead = () => {
    Alert.alert(
      'Marcar Todas como Lidas',
      `Tem certeza que deseja marcar todas as ${unreadCount} notificações como lidas?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Confirmar',
          onPress: () => dispatch(markAllAsRead()),
        },
      ]
    );
  };

  const handleMarkSelectedAsRead = () => {
    selectedNotifications.forEach(id => {
      dispatch(markAsRead(id));
    });
    exitSelectionMode();
  };

  const handleDeleteSelected = () => {
    Alert.alert(
      'Excluir Notificações',
      `Tem certeza que deseja excluir ${selectedNotifications.size} notificação(ões)?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Excluir',
          style: 'destructive',
          onPress: () => {
            selectedNotifications.forEach(id => {
              dispatch(removeNotification(id));
            });
            exitSelectionMode();
          },
        },
      ]
    );
  };

  const handleClearAll = () => {
    Alert.alert(
      'Limpar Todas',
      'Tem certeza que deseja excluir todas as notificações? Esta ação não pode ser desfeita.',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Limpar Todas',
          style: 'destructive',
          onPress: () => dispatch(clearAllNotifications()),
        },
      ]
    );
  };

  const handleNotificationNavigation = (notification) => {
    const { data } = notification;
    
    switch (data?.type) {
      case 'appointment_reminder':
        navigation.navigate('AgendaDetails', { 
          appointment: { id: data.appointmentId }
        });
        break;
        
      case 'new_os':
      case 'os_overdue':
        navigation.navigate('OSDetails', { 
          osId: data.osId 
        });
        break;
        
      default:
        // Notificação genérica - apenas marcar como lida
        break;
    }
  };

  const formatNotificationTime = (receivedAt) => {
    const now = moment();
    const time = moment(receivedAt);
    
    if (time.isSame(now, 'day')) {
      return time.format('HH:mm');
    } else if (time.isSame(now.subtract(1, 'day'), 'day')) {
      return 'Ontem';
    } else if (time.isAfter(now.subtract(7, 'days'))) {
      return time.format('ddd');
    } else {
      return time.format('DD/MM');
    }
  };

  const getNotificationIcon = (type) => {
    return NOTIFICATION_ICONS[type] || 'notifications';
  };

  const getNotificationColor = (type) => {
    return NOTIFICATION_COLORS[type] || theme.colors.textSecondary;
  };

  const renderNotificationItem = ({ item: notification }) => {
    const isSelected = selectedNotifications.has(notification.id);
    const notificationType = notification.data?.type || 'system';
    
    return (
      <TouchableOpacity
        style={[
          styles.notificationItem,
          !notification.read && styles.notificationItemUnread,
          isSelected && styles.notificationItemSelected,
        ]}
        onPress={() => handleNotificationPress(notification)}
        onLongPress={() => handleNotificationLongPress(notification)}
        activeOpacity={0.7}
      >
        <View style={styles.notificationIcon}>
          <Icon 
            name={getNotificationIcon(notificationType)} 
            size={24} 
            color={getNotificationColor(notificationType)} 
          />
          {!notification.read && <View style={styles.unreadDot} />}
        </View>
        
        <View style={styles.notificationContent}>
          <View style={styles.notificationHeader}>
            <Text 
              style={[
                styles.notificationTitle,
                !notification.read && styles.notificationTitleUnread,
              ]} 
              numberOfLines={1}
            >
              {notification.title}
            </Text>
            <Text style={styles.notificationTime}>
              {formatNotificationTime(notification.receivedAt)}
            </Text>
          </View>
          
          <Text 
            style={[
              styles.notificationBody,
              !notification.read && styles.notificationBodyUnread,
            ]} 
            numberOfLines={2}
          >
            {notification.body}
          </Text>
        </View>
        
        {selectionMode && (
          <View style={styles.notificationSelection}>
            <Icon 
              name={isSelected ? "check-circle" : "radio-button-unchecked"} 
              size={24} 
              color={isSelected ? theme.colors.primary : theme.colors.disabled} 
            />
          </View>
        )}
      </TouchableOpacity>
    );
  };

  const renderFilterButton = (filterType, label, count) => (
    <TouchableOpacity
      style={[
        styles.filterButton,
        filter === filterType && styles.filterButtonActive,
      ]}
      onPress={() => setFilter(filterType)}
    >
      <Text style={[
        styles.filterButtonText,
        filter === filterType && styles.filterButtonTextActive,
      ]}>
        {label}
        {count > 0 && ` (${count})`}
      </Text>
    </TouchableOpacity>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Icon name="notifications-none" size={64} color={theme.colors.disabled} />
      <Text style={styles.emptyStateTitle}>
        {filter === 'unread' ? 'Nenhuma notificação não lida' : 'Nenhuma notificação'}
      </Text>
      <Text style={styles.emptyStateDescription}>
        {filter === 'unread' 
          ? 'Todas as suas notificações foram lidas'
          : 'Suas notificações aparecerão aqui'
        }
      </Text>
    </View>
  );

  const filteredNotifications = getFilteredNotifications();

  return (
    <View style={styles.container}>
      {/* Filtros */}
      <View style={styles.filtersContainer}>
        {renderFilterButton('all', 'Todas', notifications.length)}
        {renderFilterButton('unread', 'Não lidas', unreadCount)}
        {renderFilterButton('today', 'Hoje', recentNotifications.length)}
      </View>

      {/* Lista de Notificações */}
      {filteredNotifications.length > 0 ? (
        <FlatList
          data={filteredNotifications}
          keyExtractor={(item) => item.id}
          renderItem={renderNotificationItem}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              colors={[theme.colors.primary]}
              tintColor={theme.colors.primary}
            />
          }
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.listContainer}
        />
      ) : (
        renderEmptyState()
      )}

      {/* Botão de Limpar Todas (apenas se houver notificações) */}
      {notifications.length > 0 && !selectionMode && (
        <TouchableOpacity style={styles.clearAllButton} onPress={handleClearAll}>
          <Icon name="clear-all" size={20} color={theme.colors.error} />
          <Text style={styles.clearAllButtonText}>Limpar Todas</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerButton: {
    padding: 8,
    marginLeft: 8,
  },
  filtersContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginRight: 12,
    borderRadius: 20,
    backgroundColor: theme.colors.background,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  filterButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  filterButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: theme.colors.textSecondary,
  },
  filterButtonTextActive: {
    color: '#FFFFFF',
  },
  listContainer: {
    flexGrow: 1,
  },
  notificationItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingHorizontal: 16,
    paddingVertical: 16,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  notificationItemUnread: {
    backgroundColor: theme.colors.primary + '05',
  },
  notificationItemSelected: {
    backgroundColor: theme.colors.primary + '10',
  },
  notificationIcon: {
    position: 'relative',
    marginRight: 16,
    marginTop: 2,
  },
  unreadDot: {
    position: 'absolute',
    top: -2,
    right: -2,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: theme.colors.error,
  },
  notificationContent: {
    flex: 1,
  },
  notificationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 4,
  },
  notificationTitle: {
    flex: 1,
    fontSize: 16,
    color: theme.colors.text,
    marginRight: 8,
  },
  notificationTitleUnread: {
    fontWeight: 'bold',
  },
  notificationTime: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  notificationBody: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    lineHeight: 20,
  },
  notificationBodyUnread: {
    color: theme.colors.text,
  },
  notificationSelection: {
    marginLeft: 16,
    marginTop: 2,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  emptyStateTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyStateDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
  clearAllButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 24,
    margin: 16,
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.error + '30',
  },
  clearAllButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.error,
    marginLeft: 8,
  },
});