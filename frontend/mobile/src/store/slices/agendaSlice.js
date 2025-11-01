import { createSlice } from '@reduxjs/toolkit';
import moment from 'moment';

/**
 * Slice para Agenda
 * Gerencia calendário, agendamentos, sincronização e notificações
 */
const initialState = {
  // Agendamentos
  appointments: [],
  selectedDate: moment().format('YYYY-MM-DD'),
  viewMode: 'month', // month, week, day, list
  
  // Estados de loading
  isLoading: false,
  isLoadingAppointments: false,
  isSyncing: false,
  
  // Filtros
  filters: {
    types: ['os', 'visita', 'manutencao', 'reuniao'], // Tipos visíveis
    priorities: ['baixa', 'media', 'alta', 'urgente'], // Prioridades visíveis
    showCompleted: false,
    technician: 'all', // 'all' ou ID específico
  },
  
  // Configurações do calendário
  calendarSettings: {
    startHour: 8,
    endHour: 18,
    workDays: [1, 2, 3, 4, 5], // Segunda a sexta
    timeSlotDuration: 30, // minutos
    showWeekends: true,
    defaultView: 'month',
    reminderMinutes: 15,
  },
  
  // Cache e offline
  lastSync: null,
  pendingChanges: [],
  cachedDates: [], // Datas com dados em cache
  
  // Estatísticas
  stats: {
    totalAppointments: 0,
    completedToday: 0,
    pendingToday: 0,
    overdueCount: 0,
    weeklyStats: {
      scheduled: 0,
      completed: 0,
      cancelled: 0,
    },
  },
  
  // Notificações
  notifications: {
    enabled: true,
    reminderTime: 15, // minutos antes
    soundEnabled: true,
    vibrationEnabled: true,
    upcomingAppointments: [],
  },
  
  // Errors
  error: null,
  
  // UI States
  showCreateModal: false,
  selectedAppointment: null,
  draggedAppointment: null,
};

const agendaSlice = createSlice({
  name: 'agenda',
  initialState,
  reducers: {
    // Carregar agendamentos
    loadAppointmentsStart: (state) => {
      state.isLoadingAppointments = true;
      state.error = null;
    },
    
    loadAppointmentsSuccess: (state, action) => {
      const { appointments, date } = action.payload;
      
      state.appointments = appointments;
      state.isLoadingAppointments = false;
      state.error = null;
      state.lastSync = new Date().toISOString();
      
      // Adicionar data ao cache
      if (date && !state.cachedDates.includes(date)) {
        state.cachedDates.push(date);
      }
      
      // Atualizar estatísticas
      updateStats(state, appointments);
    },
    
    loadAppointmentsFailure: (state, action) => {
      state.isLoadingAppointments = false;
      state.error = action.payload;
    },
    
    // Criar agendamento
    createAppointmentStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    
    createAppointmentSuccess: (state, action) => {
      state.appointments.push(action.payload);
      state.isLoading = false;
      state.error = null;
      state.showCreateModal = false;
      
      // Adicionar às alterações pendentes para sync offline
      state.pendingChanges.push({
        type: 'create',
        appointment: action.payload,
        timestamp: new Date().toISOString(),
      });
    },
    
    createAppointmentFailure: (state, action) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    
    // Atualizar agendamento
    updateAppointmentStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    
    updateAppointmentSuccess: (state, action) => {
      const { id, updates } = action.payload;
      const index = state.appointments.findIndex(apt => apt.id === id);
      
      if (index !== -1) {
        state.appointments[index] = { ...state.appointments[index], ...updates };
      }
      
      state.isLoading = false;
      state.error = null;
      
      // Adicionar às alterações pendentes
      state.pendingChanges.push({
        type: 'update',
        appointmentId: id,
        updates,
        timestamp: new Date().toISOString(),
      });
    },
    
    updateAppointmentFailure: (state, action) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    
    // Deletar agendamento
    deleteAppointmentSuccess: (state, action) => {
      const id = action.payload;
      state.appointments = state.appointments.filter(apt => apt.id !== id);
      
      // Adicionar às alterações pendentes
      state.pendingChanges.push({
        type: 'delete',
        appointmentId: id,
        timestamp: new Date().toISOString(),
      });
    },
    
    // Navegação do calendário
    setSelectedDate: (state, action) => {
      state.selectedDate = action.payload;
    },
    
    setViewMode: (state, action) => {
      state.viewMode = action.payload;
    },
    
    goToNextPeriod: (state) => {
      const current = moment(state.selectedDate);
      let next;
      
      switch (state.viewMode) {
        case 'day':
          next = current.add(1, 'day');
          break;
        case 'week':
          next = current.add(1, 'week');
          break;
        case 'month':
        default:
          next = current.add(1, 'month');
          break;
      }
      
      state.selectedDate = next.format('YYYY-MM-DD');
    },
    
    goToPreviousPeriod: (state) => {
      const current = moment(state.selectedDate);
      let prev;
      
      switch (state.viewMode) {
        case 'day':
          prev = current.subtract(1, 'day');
          break;
        case 'week':
          prev = current.subtract(1, 'week');
          break;
        case 'month':
        default:
          prev = current.subtract(1, 'month');
          break;
      }
      
      state.selectedDate = prev.format('YYYY-MM-DD');
    },
    
    goToToday: (state) => {
      state.selectedDate = moment().format('YYYY-MM-DD');
    },
    
    // Filtros
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    
    toggleAppointmentType: (state, action) => {
      const type = action.payload;
      const types = state.filters.types;
      
      if (types.includes(type)) {
        state.filters.types = types.filter(t => t !== type);
      } else {
        state.filters.types.push(type);
      }
    },
    
    // Configurações
    updateCalendarSettings: (state, action) => {
      state.calendarSettings = { ...state.calendarSettings, ...action.payload };
    },
    
    // UI States
    toggleCreateModal: (state) => {
      state.showCreateModal = !state.showCreateModal;
    },
    
    setSelectedAppointment: (state, action) => {
      state.selectedAppointment = action.payload;
    },
    
    setDraggedAppointment: (state, action) => {
      state.draggedAppointment = action.payload;
    },
    
    // Drag & Drop
    moveAppointment: (state, action) => {
      const { appointmentId, newDate, newTime } = action.payload;
      const appointment = state.appointments.find(apt => apt.id === appointmentId);
      
      if (appointment) {
        appointment.date = newDate;
        appointment.startTime = newTime;
        
        // Calcular novo endTime baseado na duração
        const duration = moment(appointment.endTime, 'HH:mm')
          .diff(moment(appointment.startTime, 'HH:mm'), 'minutes');
        
        appointment.endTime = moment(newTime, 'HH:mm')
          .add(duration, 'minutes')
          .format('HH:mm');
        
        // Adicionar às alterações pendentes
        state.pendingChanges.push({
          type: 'move',
          appointmentId,
          newDate,
          newTime,
          timestamp: new Date().toISOString(),
        });
      }
    },
    
    // Notificações
    updateNotificationSettings: (state, action) => {
      state.notifications = { ...state.notifications, ...action.payload };
    },
    
    addUpcomingAppointment: (state, action) => {
      const appointment = action.payload;
      if (!state.notifications.upcomingAppointments.find(apt => apt.id === appointment.id)) {
        state.notifications.upcomingAppointments.push(appointment);
      }
    },
    
    removeUpcomingAppointment: (state, action) => {
      const id = action.payload;
      state.notifications.upcomingAppointments = 
        state.notifications.upcomingAppointments.filter(apt => apt.id !== id);
    },
    
    // Sincronização
    syncStart: (state) => {
      state.isSyncing = true;
    },
    
    syncSuccess: (state) => {
      state.isSyncing = false;
      state.pendingChanges = [];
      state.lastSync = new Date().toISOString();
    },
    
    syncFailure: (state, action) => {
      state.isSyncing = false;
      state.error = action.payload;
    },
    
    // Limpar dados
    clearAgendaData: (state) => {
      return { ...initialState, calendarSettings: state.calendarSettings };
    },
    
    clearError: (state) => {
      state.error = null;
    },
  },
});

// Helper function para atualizar estatísticas
function updateStats(state, appointments) {
  const today = moment().format('YYYY-MM-DD');
  const startOfWeek = moment().startOf('week').format('YYYY-MM-DD');
  const endOfWeek = moment().endOf('week').format('YYYY-MM-DD');
  
  const todayAppointments = appointments.filter(apt => apt.date === today);
  const weekAppointments = appointments.filter(apt => 
    moment(apt.date).isBetween(startOfWeek, endOfWeek, null, '[]')
  );
  
  state.stats = {
    totalAppointments: appointments.length,
    completedToday: todayAppointments.filter(apt => apt.status === 'completed').length,
    pendingToday: todayAppointments.filter(apt => 
      ['scheduled', 'in_progress'].includes(apt.status)
    ).length,
    overdueCount: appointments.filter(apt => 
      moment(apt.date).isBefore(today) && apt.status !== 'completed'
    ).length,
    weeklyStats: {
      scheduled: weekAppointments.filter(apt => apt.status === 'scheduled').length,
      completed: weekAppointments.filter(apt => apt.status === 'completed').length,
      cancelled: weekAppointments.filter(apt => apt.status === 'cancelled').length,
    },
  };
}

export const {
  loadAppointmentsStart,
  loadAppointmentsSuccess,
  loadAppointmentsFailure,
  createAppointmentStart,
  createAppointmentSuccess,
  createAppointmentFailure,
  updateAppointmentStart,
  updateAppointmentSuccess,
  updateAppointmentFailure,
  deleteAppointmentSuccess,
  setSelectedDate,
  setViewMode,
  goToNextPeriod,
  goToPreviousPeriod,
  goToToday,
  setFilters,
  toggleAppointmentType,
  updateCalendarSettings,
  toggleCreateModal,
  setSelectedAppointment,
  setDraggedAppointment,
  moveAppointment,
  updateNotificationSettings,
  addUpcomingAppointment,
  removeUpcomingAppointment,
  syncStart,
  syncSuccess,
  syncFailure,
  clearAgendaData,
  clearError,
} = agendaSlice.actions;

// Seletores
export const selectAppointments = (state) => state.agenda.appointments;
export const selectSelectedDate = (state) => state.agenda.selectedDate;
export const selectViewMode = (state) => state.agenda.viewMode;
export const selectAgendaLoading = (state) => state.agenda.isLoadingAppointments;
export const selectAgendaError = (state) => state.agenda.error;
export const selectFilters = (state) => state.agenda.filters;
export const selectCalendarSettings = (state) => state.agenda.calendarSettings;
export const selectAgendaStats = (state) => state.agenda.stats;
export const selectNotificationSettings = (state) => state.agenda.notifications;
export const selectPendingChanges = (state) => state.agenda.pendingChanges;
export const selectShowCreateModal = (state) => state.agenda.showCreateModal;
export const selectSelectedAppointment = (state) => state.agenda.selectedAppointment;

// Seletores computados
export const selectAppointmentsByDate = (state, date) => 
  state.agenda.appointments.filter(apt => apt.date === date);

export const selectFilteredAppointments = (state) => {
  const { appointments, filters } = state.agenda;
  
  return appointments.filter(apt => {
    // Filtro por tipo
    if (!filters.types.includes(apt.type)) return false;
    
    // Filtro por prioridade
    if (!filters.priorities.includes(apt.priority)) return false;
    
    // Filtro por status (completadas)
    if (!filters.showCompleted && apt.status === 'completed') return false;
    
    // Filtro por técnico
    if (filters.technician !== 'all' && apt.technicianId !== filters.technician) return false;
    
    return true;
  });
};

export const selectTodayAppointments = (state) => {
  const today = moment().format('YYYY-MM-DD');
  return selectAppointmentsByDate(state, today);
};

export const selectUpcomingAppointments = (state) => {
  const now = moment();
  const endOfDay = moment().endOf('day');
  
  return state.agenda.appointments.filter(apt => {
    const aptDateTime = moment(`${apt.date} ${apt.startTime}`, 'YYYY-MM-DD HH:mm');
    return aptDateTime.isBetween(now, endOfDay) && apt.status === 'scheduled';
  });
};

export default agendaSlice.reducer;