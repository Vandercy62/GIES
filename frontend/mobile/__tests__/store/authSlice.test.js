import { configureStore } from '@reduxjs/toolkit';
import authReducer, { 
  loginSuccess, 
  logout, 
  updateProfile,
  updateToken,
} from '../../src/store/slices/authSlice';

// Mock AsyncStorage para testes
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
);

describe('Auth Slice', () => {
  let store;

  beforeEach(() => {
    store = configureStore({
      reducer: {
        auth: authReducer,
      },
    });
  });

  it('should handle initial state', () => {
    const state = store.getState().auth;
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBe(null);
    expect(state.token).toBe(null);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBe(null);
  });

  it('should handle loginSuccess', () => {
    const mockUser = {
      id: 1,
      nome: 'Técnico Teste',
      email: 'teste@primotex.com',
      perfil: 'Operador'
    };
    const mockToken = 'jwt-token-test';
    const mockPermissions = ['read', 'write'];

    store.dispatch(loginSuccess({ 
      user: mockUser, 
      token: mockToken,
      permissions: mockPermissions 
    }));
    
    const state = store.getState().auth;
    expect(state.isAuthenticated).toBe(true);
    expect(state.user).toEqual(mockUser);
    expect(state.token).toBe(mockToken);
    expect(state.permissions).toEqual(mockPermissions);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBe(null);
  });

  it('should handle logout', () => {
    // Primeiro fazer login
    const mockUser = { id: 1, nome: 'Teste' };
    store.dispatch(loginSuccess({ user: mockUser, token: 'token' }));
    
    // Depois logout
    store.dispatch(logout());
    
    const state = store.getState().auth;
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBe(null);
    expect(state.token).toBe(null);
    expect(state.biometricEnabled).toBe(false);
    expect(state.permissions).toEqual([]);
    expect(state.error).toBe(null);
  });

  it('should handle updateProfile', () => {
    // Setup inicial
    const initialUser = { id: 1, nome: 'Nome Antigo' };
    store.dispatch(loginSuccess({ user: initialUser, token: 'token' }));
    
    // Atualizar perfil
    const updatedData = { nome: 'Nome Novo', email: 'novo@email.com' };
    store.dispatch(updateProfile(updatedData));
    
    const state = store.getState().auth;
    expect(state.user.nome).toBe('Nome Novo');
    expect(state.user.email).toBe('novo@email.com');
    expect(state.user.id).toBe(1); // ID deve permanecer
  });

  it('should handle updateToken', () => {
    const newToken = 'new-jwt-token';
    store.dispatch(updateToken(newToken));
    
    const state = store.getState().auth;
    expect(state.token).toBe(newToken);
  });

  it('should maintain state integrity during multiple operations', () => {
    const user1 = { id: 1, nome: 'User 1' };
    const user2Data = { nome: 'User 2 Updated' };
    
    // Login com user1
    store.dispatch(loginSuccess({ user: user1, token: 'token1' }));
    expect(store.getState().auth.user).toEqual(user1);
    
    // Atualizar profile
    store.dispatch(updateProfile(user2Data));
    expect(store.getState().auth.user.nome).toBe('User 2 Updated');
    expect(store.getState().auth.user.id).toBe(1); // ID original mantido
    
    // Logout
    store.dispatch(logout());
    expect(store.getState().auth.isAuthenticated).toBe(false);
  });
});