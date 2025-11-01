import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as LocalAuthentication from 'expo-local-authentication';
import erpIntegration from '../../services/erpIntegration';

/**
 * Async Thunks para Integração ERP
 */

// Login com integração ERP
export const loginWithERP = createAsyncThunk(
  'auth/loginWithERP',
  async ({ username, password }, { rejectWithValue }) => {
    try {
      const result = await erpIntegration.login(username, password);
      
      if (result.success) {
        return {
          user: result.user,
          token: result.token,
          permissions: result.user.permissions || []
        };
      } else {
        return rejectWithValue(result.error);
      }
    } catch (error) {
      return rejectWithValue(error.message || 'Erro de conexão com o servidor');
    }
  }
);

// Logout com integração ERP
export const logoutFromERP = createAsyncThunk(
  'auth/logoutFromERP',
  async (_, { rejectWithValue }) => {
    try {
      await erpIntegration.logout();
      return true;
    } catch (error) {
      console.warn('Erro ao notificar logout no servidor:', error);
      return true; // Continua logout local mesmo com erro no servidor
    }
  }
);

// Verificar sessão existente
export const checkExistingSession = createAsyncThunk(
  'auth/checkExistingSession',
  async (_, { rejectWithValue }) => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const userData = await AsyncStorage.getItem('user_data');
      const sessionExpires = await AsyncStorage.getItem('session_expires');
      
      if (token && userData && sessionExpires) {
        const expiresAt = new Date(sessionExpires);
        const now = new Date();
        
        if (expiresAt > now) {
          return {
            user: JSON.parse(userData),
            token,
            permissions: JSON.parse(userData).permissions || []
          };
        } else {
          // Sessão expirada, limpar dados
          await AsyncStorage.multiRemove(['auth_token', 'user_data', 'session_expires']);
          return rejectWithValue('Sessão expirada');
        }
      }
      
      return rejectWithValue('Nenhuma sessão encontrada');
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

/**
 * Slice para Autenticação do Usuário
 * Gerencia login, token, biometria e perfil técnico
 */
const initialState = {
  isAuthenticated: false,
  user: null,
  token: null,
  biometricEnabled: false,
  isLoading: false,
  error: null,
  lastLogin: null,
  permissions: [],
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Login com credenciais
    loginStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    
    loginSuccess: (state, action) => {
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.permissions = action.payload.permissions || [];
      state.lastLogin = new Date().toISOString();
      state.isLoading = false;
      state.error = null;
    },
    
    loginFailure: (state, action) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.isLoading = false;
      state.error = action.payload;
    },
    
    // Login biométrico
    biometricLoginStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    
    biometricLoginSuccess: (state) => {
      state.isAuthenticated = true;
      state.isLoading = false;
      state.error = null;
    },
    
    // Configuração biometria
    setBiometricEnabled: (state, action) => {
      state.biometricEnabled = action.payload;
    },
    
    // Logout
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.biometricEnabled = false;
      state.isLoading = false;
      state.error = null;
      state.lastLogin = null;
      state.permissions = [];
    },
    
    // Atualizar perfil
    updateProfile: (state, action) => {
      state.user = { ...state.user, ...action.payload };
    },
    
    // Limpar erros
    clearError: (state) => {
      state.error = null;
    },
    
    // Atualizar token
    updateToken: (state, action) => {
      state.token = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Login com ERP
    builder
      .addCase(loginWithERP.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginWithERP.fulfilled, (state, action) => {
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.permissions = action.payload.permissions;
        state.lastLogin = new Date().toISOString();
        state.isLoading = false;
        state.error = null;
      })
      .addCase(loginWithERP.rejected, (state, action) => {
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.permissions = [];
        state.isLoading = false;
        state.error = action.payload;
      })
      // Logout com ERP
      .addCase(logoutFromERP.fulfilled, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.biometricEnabled = false;
        state.isLoading = false;
        state.error = null;
        state.lastLogin = null;
        state.permissions = [];
      })
      // Verificar sessão existente
      .addCase(checkExistingSession.fulfilled, (state, action) => {
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.permissions = action.payload.permissions;
        state.isLoading = false;
        state.error = null;
      })
      .addCase(checkExistingSession.rejected, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.permissions = [];
        state.isLoading = false;
      });
  },
});

export const {
  loginStart,
  loginSuccess,
  loginFailure,
  biometricLoginStart,
  biometricLoginSuccess,
  setBiometricEnabled,
  logout,
  updateProfile,
  clearError,
  updateToken,
} = authSlice.actions;

// Seletores
export const selectAuth = (state) => state.auth;
export const selectUser = (state) => state.auth.user;
export const selectToken = (state) => state.auth.token;
export const selectIsAuthenticated = (state) => state.auth.isAuthenticated;
export const selectBiometricEnabled = (state) => state.auth.biometricEnabled;
export const selectPermissions = (state) => state.auth.permissions;

export default authSlice.reducer;