import agendaSlice, {
  loadAppointments,
  addAppointment,
  updateAppointment,
  deleteAppointment,
  setSelectedDate,
  setCalendarMonth,
  setFilters,
  selectAppointments,
  selectLoading,
  selectSelectedDate,
  selectCalendarMonth,
  selectFilteredAppointments,
} from '../../src/store/slices/agendaSlice';
import { configureStore } from '@reduxjs/toolkit';

// Mock moment
jest.mock('moment', () => {
  const actualMoment = jest.requireActual('moment');
  const moment = (...args) => actualMoment(...args);
  moment.format = actualMoment.format;
  moment.isSame = actualMoment.isSame;
  moment.isBetween = actualMoment.isBetween;
  moment.startOf = actualMoment.startOf;
  moment.endOf = actualMoment.endOf;
  return moment;
});

describe('agendaSlice', () => {
  let store;
  const mockAppointment = {
    id: 1,
    title: 'Visita Técnica',
    description: 'Avaliação para instalação',
    clientName: 'João Silva',
    clientPhone: '(11) 99999-9999',
    clientEmail: 'joao@email.com',
    location: 'Rua das Flores, 123',
    type: 'visita_tecnica',
    status: 'pendente',
    priority: 'normal',
    date: '2024-01-15',
    time: '14:00',
    duration: 60,
    notes: 'Cliente prefere horário da tarde',
    reminderMinutes: 30,
    createdAt: '2024-01-10T10:00:00Z',
    updatedAt: '2024-01-10T10:00:00Z',
  };

  beforeEach(() => {
    store = configureStore({
      reducer: {
        agenda: agendaSlice,
      },
    });
  });

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = store.getState().agenda;
      
      expect(state.appointments).toEqual([]);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.selectedDate).toBe(new Date().toISOString().split('T')[0]);
      expect(state.calendarMonth).toBe(new Date().toISOString().split('T')[0].substring(0, 7));
      expect(state.filters).toEqual({
        status: 'all',
        type: 'all',
        priority: 'all',
        search: '',
      });
      expect(state.viewMode).toBe('month');
      expect(state.notifications).toEqual([]);
      expect(state.statistics).toEqual({
        total: 0,
        pending: 0,
        confirmed: 0,
        completed: 0,
        cancelled: 0,
      });
    });
  });

  describe('reducers', () => {
    it('should handle setSelectedDate', () => {
      const newDate = '2024-02-15';
      store.dispatch(setSelectedDate(newDate));
      
      const state = store.getState().agenda;
      expect(state.selectedDate).toBe(newDate);
    });

    it('should handle setCalendarMonth', () => {
      const newMonth = '2024-02';
      store.dispatch(setCalendarMonth(newMonth));
      
      const state = store.getState().agenda;
      expect(state.calendarMonth).toBe(newMonth);
    });

    it('should handle setFilters', () => {
      const newFilters = {
        status: 'confirmado',
        type: 'instalacao',
        priority: 'alta',
        search: 'João',
      };
      store.dispatch(setFilters(newFilters));
      
      const state = store.getState().agenda;
      expect(state.filters).toEqual(newFilters);
    });

    it('should handle addAppointment.fulfilled', () => {
      const action = {
        type: addAppointment.fulfilled.type,
        payload: mockAppointment,
      };
      store.dispatch(action);
      
      const state = store.getState().agenda;
      expect(state.appointments).toHaveLength(1);
      expect(state.appointments[0]).toEqual(mockAppointment);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should handle updateAppointment.fulfilled', () => {
      // Primeiro adiciona um appointment
      store.dispatch({
        type: addAppointment.fulfilled.type,
        payload: mockAppointment,
      });

      // Depois atualiza
      const updatedAppointment = {
        ...mockAppointment,
        status: 'confirmado',
        title: 'Visita Confirmada',
      };

      store.dispatch({
        type: updateAppointment.fulfilled.type,
        payload: updatedAppointment,
      });
      
      const state = store.getState().agenda;
      expect(state.appointments).toHaveLength(1);
      expect(state.appointments[0].status).toBe('confirmado');
      expect(state.appointments[0].title).toBe('Visita Confirmada');
    });

    it('should handle deleteAppointment.fulfilled', () => {
      // Primeiro adiciona um appointment
      store.dispatch({
        type: addAppointment.fulfilled.type,
        payload: mockAppointment,
      });

      // Depois remove
      store.dispatch({
        type: deleteAppointment.fulfilled.type,
        payload: mockAppointment.id,
      });
      
      const state = store.getState().agenda;
      expect(state.appointments).toHaveLength(0);
    });

    it('should handle loadAppointments.pending', () => {
      store.dispatch({
        type: loadAppointments.pending.type,
      });
      
      const state = store.getState().agenda;
      expect(state.loading).toBe(true);
      expect(state.error).toBeNull();
    });

    it('should handle loadAppointments.fulfilled', () => {
      const appointments = [mockAppointment];
      
      store.dispatch({
        type: loadAppointments.fulfilled.type,
        payload: appointments,
      });
      
      const state = store.getState().agenda;
      expect(state.appointments).toEqual(appointments);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should handle loadAppointments.rejected', () => {
      const error = 'Failed to load appointments';
      
      store.dispatch({
        type: loadAppointments.rejected.type,
        error: { message: error },
      });
      
      const state = store.getState().agenda;
      expect(state.loading).toBe(false);
      expect(state.error).toBe(error);
    });
  });

  describe('selectors', () => {
    beforeEach(() => {
      // Adiciona alguns appointments para teste
      store.dispatch({
        type: loadAppointments.fulfilled.type,
        payload: [
          mockAppointment,
          {
            ...mockAppointment,
            id: 2,
            title: 'Instalação',
            status: 'confirmado',
            type: 'instalacao',
            date: '2024-01-16',
          },
        ],
      });
    });

    it('should select appointments', () => {
      const state = store.getState();
      const appointments = selectAppointments(state);
      
      expect(appointments).toHaveLength(2);
      expect(appointments[0].title).toBe('Visita Técnica');
      expect(appointments[1].title).toBe('Instalação');
    });

    it('should select loading state', () => {
      const state = store.getState();
      const loading = selectLoading(state);
      
      expect(loading).toBe(false);
    });

    it('should select selected date', () => {
      const testDate = '2024-02-15';
      store.dispatch(setSelectedDate(testDate));
      
      const state = store.getState();
      const selectedDate = selectSelectedDate(state);
      
      expect(selectedDate).toBe(testDate);
    });

    it('should select calendar month', () => {
      const testMonth = '2024-02';
      store.dispatch(setCalendarMonth(testMonth));
      
      const state = store.getState();
      const calendarMonth = selectCalendarMonth(state);
      
      expect(calendarMonth).toBe(testMonth);
    });

    it('should filter appointments by status', () => {
      store.dispatch(setFilters({ status: 'confirmado' }));
      
      const state = store.getState();
      const filteredAppointments = selectFilteredAppointments(state);
      
      expect(filteredAppointments).toHaveLength(1);
      expect(filteredAppointments[0].status).toBe('confirmado');
    });

    it('should filter appointments by search term', () => {
      store.dispatch(setFilters({ search: 'Instalação' }));
      
      const state = store.getState();
      const filteredAppointments = selectFilteredAppointments(state);
      
      expect(filteredAppointments).toHaveLength(1);
      expect(filteredAppointments[0].title).toBe('Instalação');
    });
  });

  describe('statistics calculation', () => {
    it('should calculate statistics correctly', () => {
      const appointments = [
        { ...mockAppointment, status: 'pendente' },
        { ...mockAppointment, id: 2, status: 'confirmado' },
        { ...mockAppointment, id: 3, status: 'realizado' },
        { ...mockAppointment, id: 4, status: 'cancelado' },
      ];

      store.dispatch({
        type: loadAppointments.fulfilled.type,
        payload: appointments,
      });
      
      const state = store.getState().agenda;
      expect(state.statistics).toEqual({
        total: 4,
        pending: 1,
        confirmed: 1,
        completed: 1,
        cancelled: 1,
      });
    });
  });

  describe('async thunks', () => {
    it('should create loadAppointments action', () => {
      const action = loadAppointments();
      expect(action.type).toBe('agenda/loadAppointments/pending');
    });

    it('should create addAppointment action', () => {
      const action = addAppointment(mockAppointment);
      expect(action.type).toBe('agenda/addAppointment/pending');
    });

    it('should create updateAppointment action', () => {
      const action = updateAppointment(mockAppointment);
      expect(action.type).toBe('agenda/updateAppointment/pending');
    });

    it('should create deleteAppointment action', () => {
      const action = deleteAppointment(1);
      expect(action.type).toBe('agenda/deleteAppointment/pending');
    });
  });
});