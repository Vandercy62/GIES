import React from 'react';
import { render, screen } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import AgendaScreen from '../../src/screens/agenda/AgendaScreen';
import agendaSlice from '../../src/store/slices/agendaSlice';

// Mock das dependências
jest.mock('react-native-calendars', () => ({
  Calendar: () => null,
  LocaleConfig: {
    locales: {},
    defaultLocale: 'pt-br',
  },
}));

jest.mock('@react-navigation/native', () => ({
  useFocusEffect: jest.fn(),
}));

jest.mock('react-native-vector-icons/MaterialIcons', () => 'Icon');

// Mock do navigation
const mockNavigation = {
  navigate: jest.fn(),
  setOptions: jest.fn(),
};

describe('AgendaScreen', () => {
  let store;

  beforeEach(() => {
    store = configureStore({
      reducer: {
        agenda: agendaSlice,
        offline: (state = { isOffline: false }) => state,
      },
    });
  });

  it('should render agenda screen correctly', () => {
    render(
      <Provider store={store}>
        <AgendaScreen navigation={mockNavigation} />
      </Provider>
    );

    // Verifica se elementos básicos estão presentes
    expect(screen.getByText(/nenhum agendamento para este dia/i)).toBeTruthy();
  });

  it('should show loading state', () => {
    // Simula estado de loading
    const loadingStore = configureStore({
      reducer: {
        agenda: (state = { loading: true, appointments: [] }) => state,
        offline: (state = { isOffline: false }) => state,
      },
    });

    render(
      <Provider store={loadingStore}>
        <AgendaScreen navigation={mockNavigation} />
      </Provider>
    );

    expect(screen.getByText(/carregando agenda/i)).toBeTruthy();
  });

  it('should show offline banner when offline', () => {
    const offlineStore = configureStore({
      reducer: {
        agenda: agendaSlice,
        offline: (state = { isOffline: true }) => state,
      },
    });

    render(
      <Provider store={offlineStore}>
        <AgendaScreen navigation={mockNavigation} />
      </Provider>
    );

    expect(screen.getByText(/modo offline/i)).toBeTruthy();
  });
});