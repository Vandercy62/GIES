import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import { store } from '../store/store';
import {
  addReceivedNotification,
  registerForPushNotifications,
  scheduleAppointmentReminder,
  scheduleOSOverdueNotification,
  scheduleNewOSNotification,
} from '../store/slices/notificationsSlice';

/**
 * Serviço de Notificações
 * Gerencia notificações push e locais
 */
class NotificationService {
  constructor() {
    this.notificationListener = null;
    this.responseListener = null;
    this.initialized = false;
  }

  /**
   * Inicializa o serviço de notificações
   */
  async initialize() {
    if (this.initialized) return;

    try {
      // Configurar handler de notificações
      await this.setupNotificationHandler();

      // Registrar para push notifications se for dispositivo físico
      if (Device.isDevice) {
        await store.dispatch(registerForPushNotifications());
      }

      // Configurar listeners
      this.setupNotificationListeners();

      // Configurar categorias de notificação
      await this.setupNotificationCategories();

      this.initialized = true;
      console.log('NotificationService initialized successfully');
    } catch (error) {
      console.error('Failed to initialize NotificationService:', error);
    }
  }

  /**
   * Configura o handler de notificações
   */
  async setupNotificationHandler() {
    Notifications.setNotificationHandler({
      handleNotification: async (notification) => {
        const { data } = notification.request.content;
        const settings = store.getState().notifications.settings;
        
        // Verificar quiet hours
        if (this.isQuietHours(settings.quietHours)) {
          return {
            shouldShowAlert: false,
            shouldPlaySound: false,
            shouldSetBadge: true,
          };
        }

        // Verificar configurações da categoria
        const categoryId = data?.type || 'system';
        const categories = store.getState().notifications.categories;
        const category = categories[categoryId];

        return {
          shouldShowAlert: category?.enabled ?? true,
          shouldPlaySound: category?.sound && settings.soundEnabled,
          shouldSetBadge: true,
        };
      },
    });
  }

  /**
   * Configura listeners de notificações
   */
  setupNotificationListeners() {
    // Listener para notificações recebidas
    this.notificationListener = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log('Notification received:', notification);
        
        // Adicionar notificação ao estado
        store.dispatch(addReceivedNotification({
          id: notification.request.identifier,
          title: notification.request.content.title,
          body: notification.request.content.body,
          data: notification.request.content.data,
          receivedAt: new Date().toISOString(),
        }));
      }
    );

    // Listener para resposta do usuário à notificação
    this.responseListener = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        console.log('Notification response:', response);
        this.handleNotificationResponse(response);
      }
    );
  }

  /**
   * Configura categorias de notificação
   */
  async setupNotificationCategories() {
    if (Platform.OS === 'ios') {
      await Notifications.setNotificationCategoryAsync('appointment_reminder', [
        {
          identifier: 'view_appointment',
          buttonTitle: 'Ver Agendamento',
          options: {
            opensAppToForeground: true,
          },
        },
        {
          identifier: 'snooze_reminder',
          buttonTitle: 'Lembrar em 10min',
          options: {
            opensAppToForeground: false,
          },
        },
      ]);

      await Notifications.setNotificationCategoryAsync('new_os', [
        {
          identifier: 'view_os',
          buttonTitle: 'Ver OS',
          options: {
            opensAppToForeground: true,
          },
        },
        {
          identifier: 'mark_accepted',
          buttonTitle: 'Aceitar',
          options: {
            opensAppToForeground: false,
          },
        },
      ]);

      await Notifications.setNotificationCategoryAsync('os_overdue', [
        {
          identifier: 'view_os',
          buttonTitle: 'Ver OS',
          options: {
            opensAppToForeground: true,
          },
        },
      ]);
    }
  }

  /**
   * Verifica se está no horário de silêncio
   */
  isQuietHours(quietHours) {
    if (!quietHours.enabled) return false;

    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();
    
    const [startHour, startMin] = quietHours.start.split(':').map(Number);
    const [endHour, endMin] = quietHours.end.split(':').map(Number);
    
    const startTime = startHour * 60 + startMin;
    const endTime = endHour * 60 + endMin;

    if (startTime <= endTime) {
      // Mesmo dia (ex: 22:00 - 07:00 do dia seguinte)
      return currentTime >= startTime && currentTime <= endTime;
    } else {
      // Cruza meia-noite (ex: 22:00 - 07:00)
      return currentTime >= startTime || currentTime <= endTime;
    }
  }

  /**
   * Manipula resposta do usuário à notificação
   */
  handleNotificationResponse(response) {
    const { actionIdentifier, notification } = response;
    const { data } = notification.request.content;

    switch (actionIdentifier) {
      case 'view_appointment':
        // Navegar para detalhes do agendamento
        this.navigateToAppointment(data.appointmentId);
        break;

      case 'view_os':
        // Navegar para detalhes da OS
        this.navigateToOS(data.osId);
        break;

      case 'snooze_reminder':
        // Adiar lembrete por 10 minutos
        this.snoozeReminder(data, 10);
        break;

      case 'mark_accepted':
        // Marcar OS como aceita
        this.acceptOS(data.osId);
        break;

      default:
        // Ação padrão (tap na notificação)
        this.handleDefaultAction(data);
        break;
    }
  }

  /**
   * Navegar para agendamento
   */
  navigateToAppointment(appointmentId) {
    // Implementar navegação via navigation service
    console.log('Navigate to appointment:', appointmentId);
  }

  /**
   * Navegar para OS
   */
  navigateToOS(osId) {
    // Implementar navegação via navigation service
    console.log('Navigate to OS:', osId);
  }

  /**
   * Adiar lembrete
   */
  async snoozeReminder(data, minutes) {
    try {
      const snoozeTime = new Date(Date.now() + minutes * 60 * 1000);
      
      await store.dispatch(scheduleAppointmentReminder({
        appointmentId: data.appointmentId,
        title: `Lembrete Adiado: ${data.title}`,
        date: data.appointmentDate,
        time: data.appointmentTime,
        clientName: data.clientName,
        reminderMinutes: 0, // Será enviado no horário específico
      }));

      console.log(`Reminder snoozed for ${minutes} minutes`);
    } catch (error) {
      console.error('Failed to snooze reminder:', error);
    }
  }

  /**
   * Aceitar OS
   */
  acceptOS(osId) {
    // Implementar lógica para aceitar OS
    console.log('Accept OS:', osId);
  }

  /**
   * Ação padrão ao tocar na notificação
   */
  handleDefaultAction(data) {
    switch (data.type) {
      case 'appointment_reminder':
        this.navigateToAppointment(data.appointmentId);
        break;
      case 'new_os':
      case 'os_overdue':
        this.navigateToOS(data.osId);
        break;
      default:
        console.log('Default notification action:', data);
        break;
    }
  }

  /**
   * Agendar lembrete de agendamento
   */
  async scheduleAppointmentReminder(appointmentData) {
    try {
      return await store.dispatch(scheduleAppointmentReminder(appointmentData));
    } catch (error) {
      console.error('Failed to schedule appointment reminder:', error);
      throw error;
    }
  }

  /**
   * Notificar nova OS
   */
  async notifyNewOS(osData) {
    try {
      return await store.dispatch(scheduleNewOSNotification(osData));
    } catch (error) {
      console.error('Failed to notify new OS:', error);
      throw error;
    }
  }

  /**
   * Notificar OS vencida
   */
  async notifyOSOverdue(osData) {
    try {
      return await store.dispatch(scheduleOSOverdueNotification(osData));
    } catch (error) {
      console.error('Failed to notify OS overdue:', error);
      throw error;
    }
  }

  /**
   * Verificar OSs vencidas periodicamente
   */
  async checkOverdueOS() {
    try {
      const state = store.getState();
      const osList = state.os.osList || [];
      const now = new Date();

      const overdueOS = osList.filter(os => {
        if (os.status === 'completed' || os.status === 'cancelled') return false;
        
        const dueDate = new Date(os.dueDate);
        return dueDate < now;
      });

      for (const os of overdueOS) {
        await this.notifyOSOverdue({
          osId: os.id,
          osNumber: os.number,
          clientName: os.clientName,
          dueDate: os.dueDate,
          priority: 'high',
        });
      }

      console.log(`Checked ${overdueOS.length} overdue OS`);
    } catch (error) {
      console.error('Failed to check overdue OS:', error);
    }
  }

  /**
   * Agendar verificação periódica de OSs vencidas
   */
  async schedulePeriodicOSCheck() {
    try {
      // Cancelar notificação anterior se existir
      await Notifications.cancelScheduledNotificationAsync('periodic_os_check');

      // Agendar verificação diária às 9:00
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(9, 0, 0, 0);

      await Notifications.scheduleNotificationAsync({
        content: {
          title: 'Verificação de OS',
          body: 'Verificando OSs vencidas...',
          data: { type: 'periodic_check' },
        },
        trigger: {
          date: tomorrow,
          repeats: true,
        },
        identifier: 'periodic_os_check',
      });

      console.log('Periodic OS check scheduled');
    } catch (error) {
      console.error('Failed to schedule periodic OS check:', error);
    }
  }

  /**
   * Limpar listeners
   */
  cleanup() {
    if (this.notificationListener) {
      Notifications.removeNotificationSubscription(this.notificationListener);
    }
    if (this.responseListener) {
      Notifications.removeNotificationSubscription(this.responseListener);
    }
    this.initialized = false;
  }

  /**
   * Obter token push para backend
   */
  getPushToken() {
    const state = store.getState();
    return state.notifications.pushToken;
  }

  /**
   * Verificar status de permissões
   */
  async getPermissionStatus() {
    const { status } = await Notifications.getPermissionsAsync();
    return status;
  }

  /**
   * Solicitar permissões
   */
  async requestPermissions() {
    const { status } = await Notifications.requestPermissionsAsync();
    return status;
  }

  /**
   * Limpar badge (iOS)
   */
  async clearBadge() {
    if (Platform.OS === 'ios') {
      await Notifications.setBadgeCountAsync(0);
    }
  }

  /**
   * Definir badge count (iOS)
   */
  async setBadgeCount(count) {
    if (Platform.OS === 'ios') {
      await Notifications.setBadgeCountAsync(count);
    }
  }
}

// Instância singleton
const notificationService = new NotificationService();

export default notificationService;