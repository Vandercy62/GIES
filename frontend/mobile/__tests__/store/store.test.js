import { configureStore } from '@reduxjs/toolkit';
import { store, persistor } from '../../src/store/store';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
);

// Mock redux-persist
jest.mock('redux-persist', () => ({
  ...jest.requireActual('redux-persist'),
  persistStore: jest.fn(() => ({
    persist: jest.fn(),
    purge: jest.fn(),
    flush: jest.fn(),
  })),
}));

describe('Redux Store', () => {
  it('should have correct initial state structure', () => {
    const state = store.getState();
    
    expect(state).toHaveProperty('auth');
    expect(state).toHaveProperty('os');
    expect(state).toHaveProperty('sync');
    expect(state).toHaveProperty('agendamento');
    expect(state).toHaveProperty('offline');
  });

  it('should have auth slice with correct initial state', () => {
    const { auth } = store.getState();
    
    expect(auth.isAuthenticated).toBe(false);
    expect(auth.user).toBe(null);
    expect(auth.token).toBe(null);
    expect(auth.isLoading).toBe(false);
    expect(auth.error).toBe(null);
  });

  it('should have os slice with correct initial state', () => {
    const { os } = store.getState();
    
    expect(os.osAtual).toBe(null);
    expect(os.isLoading).toBe(false);
    expect(os.error).toBe(null);
  });

  it('should have sync slice with correct initial state', () => {
    const { sync } = store.getState();
    
    expect(sync.isSyncing).toBe(false);
    expect(sync.lastSync).toBe(null);
    expect(sync.uploadQueue).toEqual([]);
  });

  it('should have agendamento slice with correct initial state', () => {
    const { agendamento } = store.getState();
    
    expect(agendamento.isLoading).toBe(false);
    expect(agendamento.agenda).toEqual([]);
  });

  it('should have offline slice with correct initial state', () => {
    const { offline } = store.getState();
    
    expect(offline.isOfflineMode).toBe(false);
    expect(offline.pendingActions).toEqual([]);
    expect(offline.hasOfflineData).toBe(false);
  });

  it('should be configurable with middleware', () => {
    // Testa se o store foi configurado com middleware apropriado
    expect(store.dispatch).toBeDefined();
    expect(typeof store.dispatch).toBe('function');
    expect(store.getState).toBeDefined();
    expect(typeof store.getState).toBe('function');
  });

  it('should handle actions across multiple slices', () => {
    const initialState = store.getState();
    
    // Simula algumas ações
    store.dispatch({ type: 'auth/loginSuccess', payload: { 
      user: { id: 1, nome: 'Teste' }, 
      token: 'token' 
    }});
    
    store.dispatch({ type: 'offline/setOfflineMode', payload: true });
    
    const newState = store.getState();
    
    // Verifica se as mudanças foram aplicadas
    expect(newState.auth.isAuthenticated).toBe(true);
    expect(newState.offline.isOfflineMode).toBe(true);
  });

  it('should have persistor configured', () => {
    expect(persistor).toBeDefined();
    expect(typeof persistor).toBe('object');
  });

  it('should maintain state consistency', () => {
    const state1 = store.getState();
    const state2 = store.getState();
    
    // Mesmo estado deve ser retornado se não houve mudanças
    expect(state1).toBe(state2);
  });
});