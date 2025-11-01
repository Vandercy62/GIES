import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

// Configuração das notificações
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

/**
 * Async Thunks para operações de notificação
 */

// Registrar para push notifications
export const registerForPushNotifications = createAsyncThunk(
  'notifications/registerForPushNotifications',
  async (_, { rejectWithValue }) => {
    try {
      if (!Device.isDevice) {
        throw new Error('Must use physical device for Push Notifications');
      }

      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        throw new Error('Failed to get push token for push notification!');
      }

      const token = await Notifications.getExpoPushTokenAsync({
        projectId: Constants.expoConfig?.extra?.eas?.projectId,
      });

      if (Platform.OS === 'android') {
        Notifications.setNotificationChannelAsync('default', {
          name: 'default',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF231F7C',
        });
      }

      return {
        token: token.data,
        status: finalStatus,
      };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Agendar notificação local
export const scheduleLocalNotification = createAsyncThunk(
  'notifications/scheduleLocalNotification',
  async (notificationData, { rejectWithValue }) => {
    try {
      const {
        title,
        body,
        data = {},
        trigger,
        categoryIdentifier,
        priority = 'high',
      } = notificationData;

      const notificationContent = {
        title,
        body,
        data,
        priority: priority === 'high' 
          ? Notifications.AndroidImportance.HIGH 
          : Notifications.AndroidImportance.DEFAULT,
        sound: true,
        badge: 1,
      };

      if (categoryIdentifier) {
        notificationContent.categoryIdentifier = categoryIdentifier;
      }

      const notificationId = await Notifications.scheduleNotificationAsync({
        content: notificationContent,
        trigger,
      });

      return {
        id: notificationId,
        ...notificationData,
        scheduledAt: new Date().toISOString(),
      };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Cancelar notificação agendada
export const cancelScheduledNotification = createAsyncThunk(
  'notifications/cancelScheduledNotification',
  async (notificationId, { rejectWithValue }) => {
    try {
      await Notifications.cancelScheduledNotificationAsync(notificationId);
      return notificationId;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Cancelar todas as notificações agendadas
export const cancelAllScheduledNotifications = createAsyncThunk(
  'notifications/cancelAllScheduledNotifications',
  async (_, { rejectWithValue }) => {
    try {
      await Notifications.cancelAllScheduledNotificationsAsync();
      return true;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Obter notificações agendadas
export const getScheduledNotifications = createAsyncThunk(
  'notifications/getScheduledNotifications',
  async (_, { rejectWithValue }) => {
    try {
      const scheduledNotifications = await Notifications.getAllScheduledNotificationsAsync();
      return scheduledNotifications;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Marcar notificação como lida
export const markNotificationAsRead = createAsyncThunk(
  'notifications/markNotificationAsRead',
  async (notificationId, { rejectWithValue }) => {
    try {
      // Aqui você pode enviar para o backend que a notificação foi lida
      return notificationId;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Agendar lembrete para agendamento
export const scheduleAppointmentReminder = createAsyncThunk(
  'notifications/scheduleAppointmentReminder',
  async (appointmentData, { dispatch, rejectWithValue }) => {
    try {
      const {
        appointmentId,
        title,
        date,
        time,
        clientName,
        location,
        reminderMinutes = 30,
      } = appointmentData;

      // Calcular quando enviar a notificação
      const appointmentDateTime = new Date(`${date} ${time}`);
      const reminderDateTime = new Date(appointmentDateTime.getTime() - (reminderMinutes * 60 * 1000));

      // Verificar se a data de lembrete já passou
      if (reminderDateTime <= new Date()) {
        throw new Error('Horário de lembrete já passou');
      }

      const notificationData = {
        title: `Lembrete: ${title}`,
        body: `Agendamento com ${clientName} em ${reminderMinutes} minutos${location ? ` - ${location}` : ''}`,
        data: {
          type: 'appointment_reminder',
          appointmentId,
          appointmentDate: date,
          appointmentTime: time,
        },
        trigger: {
          date: reminderDateTime,
        },
        categoryIdentifier: 'appointment_reminder',
        priority: 'high',
      };

      const result = await dispatch(scheduleLocalNotification(notificationData)).unwrap();
      
      return {
        ...result,
        appointmentId,
        reminderMinutes,
      };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Agendar notificação de OS vencida
export const scheduleOSOverdueNotification = createAsyncThunk(
  'notifications/scheduleOSOverdueNotification',
  async (osData, { dispatch, rejectWithValue }) => {
    try {
      const {
        osId,
        osNumber,
        clientName,
        dueDate,
        priority = 'high',
      } = osData;

      const notificationData = {
        title: 'OS Vencida!',
        body: `OS #${osNumber} - ${clientName} está vencida desde ${new Date(dueDate).toLocaleDateString('pt-BR')}`,
        data: {
          type: 'os_overdue',
          osId,
          osNumber,
          dueDate,
        },
        trigger: {
          seconds: 1, // Enviar imediatamente
        },
        categoryIdentifier: 'os_overdue',
        priority,
      };

      return await dispatch(scheduleLocalNotification(notificationData)).unwrap();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Agendar notificação de nova OS
export const scheduleNewOSNotification = createAsyncThunk(
  'notifications/scheduleNewOSNotification',
  async (osData, { dispatch, rejectWithValue }) => {
    try {
      const {
        osId,
        osNumber,
        clientName,
        priority = 'normal',
      } = osData;

      const notificationData = {
        title: 'Nova OS Recebida!',
        body: `OS #${osNumber} - ${clientName} foi atribuída a você`,
        data: {
          type: 'new_os',
          osId,
          osNumber,
        },
        trigger: {
          seconds: 1, // Enviar imediatamente
        },
        categoryIdentifier: 'new_os',
        priority,
      };

      return await dispatch(scheduleLocalNotification(notificationData)).unwrap();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

/**
 * Slice de notificações
 */
const notificationsSlice = createSlice({
  name: 'notifications',
  initialState: {
    // Push Notifications
    pushToken: null,
    pushPermissionStatus: null,
    
    // Notificações
    notifications: [],
    unreadCount: 0,
    scheduledNotifications: [],
    
    // Estados
    loading: false,
    error: null,
    
    // Configurações
    settings: {
      pushEnabled: true,
      appointmentReminders: true,
      osNotifications: true,
      soundEnabled: true,
      vibrationEnabled: true,
      reminderMinutes: 30,
      quietHours: {
        enabled: false,
        start: '22:00',
        end: '07:00',
      },
    },
    
    // Categorias de notificação
    categories: {
      appointment_reminder: {
        name: 'Lembretes de Agendamento',
        enabled: true,
        sound: true,
        vibration: true,
      },
      new_os: {
        name: 'Novas Ordens de Serviço',
        enabled: true,
        sound: true,
        vibration: true,
      },
      os_overdue: {
        name: 'OS Vencidas',
        enabled: true,
        sound: true,
        vibration: true,
      },
      system: {
        name: 'Sistema',
        enabled: true,
        sound: false,
        vibration: false,
      },
    },
  },
  reducers: {
    // Adicionar notificação recebida
    addReceivedNotification: (state, action) => {
      const notification = {
        ...action.payload,
        id: action.payload.id || Date.now().toString(),
        receivedAt: new Date().toISOString(),
        read: false,
      };
      
      state.notifications.unshift(notification);
      state.unreadCount += 1;
      
      // Manter apenas as últimas 100 notificações
      if (state.notifications.length > 100) {
        state.notifications = state.notifications.slice(0, 100);
      }
    },
    
    // Marcar notificação como lida
    markAsRead: (state, action) => {
      const notificationId = action.payload;
      const notification = state.notifications.find(n => n.id === notificationId);
      
      if (notification && !notification.read) {
        notification.read = true;
        state.unreadCount = Math.max(0, state.unreadCount - 1);
      }
    },
    
    // Marcar todas como lidas
    markAllAsRead: (state) => {
      state.notifications.forEach(notification => {
        notification.read = true;
      });
      state.unreadCount = 0;
    },
    
    // Remover notificação
    removeNotification: (state, action) => {
      const notificationId = action.payload;
      const index = state.notifications.findIndex(n => n.id === notificationId);
      
      if (index !== -1) {
        const notification = state.notifications[index];
        if (!notification.read) {
          state.unreadCount = Math.max(0, state.unreadCount - 1);
        }
        state.notifications.splice(index, 1);
      }
    },
    
    // Limpar todas as notificações
    clearAllNotifications: (state) => {
      state.notifications = [];
      state.unreadCount = 0;
    },
    
    // Atualizar configurações
    updateSettings: (state, action) => {
      state.settings = { ...state.settings, ...action.payload };
    },
    
    // Atualizar categoria
    updateCategory: (state, action) => {
      const { categoryId, settings } = action.payload;
      if (state.categories[categoryId]) {
        state.categories[categoryId] = { ...state.categories[categoryId], ...settings };
      }
    },
    
    // Limpar erro
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Register for push notifications
      .addCase(registerForPushNotifications.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(registerForPushNotifications.fulfilled, (state, action) => {
        state.loading = false;
        state.pushToken = action.payload.token;
        state.pushPermissionStatus = action.payload.status;
      })
      .addCase(registerForPushNotifications.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Schedule local notification
      .addCase(scheduleLocalNotification.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(scheduleLocalNotification.fulfilled, (state, action) => {
        state.loading = false;
        state.scheduledNotifications.push(action.payload);
      })
      .addCase(scheduleLocalNotification.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      
      // Cancel scheduled notification
      .addCase(cancelScheduledNotification.fulfilled, (state, action) => {
        const notificationId = action.payload;
        state.scheduledNotifications = state.scheduledNotifications.filter(
          n => n.id !== notificationId
        );
      })
      
      // Cancel all scheduled notifications
      .addCase(cancelAllScheduledNotifications.fulfilled, (state) => {
        state.scheduledNotifications = [];
      })
      
      // Get scheduled notifications
      .addCase(getScheduledNotifications.fulfilled, (state, action) => {
        state.scheduledNotifications = action.payload;
      })
      
      // Mark notification as read
      .addCase(markNotificationAsRead.fulfilled, (state, action) => {
        const notificationId = action.payload;
        const notification = state.notifications.find(n => n.id === notificationId);
        
        if (notification && !notification.read) {
          notification.read = true;
          state.unreadCount = Math.max(0, state.unreadCount - 1);
        }
      });
  },
});

/**
 * Actions
 */
export const {
  addReceivedNotification,
  markAsRead,
  markAllAsRead,
  removeNotification,
  clearAllNotifications,
  updateSettings,
  updateCategory,
  clearError,
} = notificationsSlice.actions;

/**
 * Selectors
 */
export const selectNotifications = (state) => state.notifications.notifications;
export const selectUnreadCount = (state) => state.notifications.unreadCount;
export const selectScheduledNotifications = (state) => state.notifications.scheduledNotifications;
export const selectPushToken = (state) => state.notifications.pushToken;
export const selectPushPermissionStatus = (state) => state.notifications.pushPermissionStatus;
export const selectNotificationSettings = (state) => state.notifications.settings;
export const selectNotificationCategories = (state) => state.notifications.categories;
export const selectNotificationsLoading = (state) => state.notifications.loading;
export const selectNotificationsError = (state) => state.notifications.error;

// Seletores computados
export const selectUnreadNotifications = (state) => 
  state.notifications.notifications.filter(n => !n.read);

export const selectNotificationsByCategory = (state) => {
  const notifications = state.notifications.notifications;
  const grouped = {};
  
  notifications.forEach(notification => {
    const category = notification.data?.type || 'system';
    if (!grouped[category]) {
      grouped[category] = [];
    }
    grouped[category].push(notification);
  });
  
  return grouped;
};

export const selectRecentNotifications = (state) => {
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
  return state.notifications.notifications.filter(
    n => new Date(n.receivedAt) > oneDayAgo
  );
};

export default notificationsSlice.reducer;