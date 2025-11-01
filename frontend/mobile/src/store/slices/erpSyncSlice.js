/**
 * Redux Slice para Integração ERP
 * Gerencia sincronização e estado de conectividade
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import erpIntegration from '../../services/erpIntegration';

// Async thunks para sincronização
export const syncAllData = createAsyncThunk(
  'erpSync/syncAllData',
  async (_, { rejectWithValue }) => {
    try {
      const results = await Promise.allSettled([
        erpIntegration.syncOS(),
        erpIntegration.syncAgendamentos(),
        erpIntegration.syncClientes()
      ]);

      const syncResults = {
        os: results[0].status === 'fulfilled' ? results[0].value : null,
        agendamentos: results[1].status === 'fulfilled' ? results[1].value : null,
        clientes: results[2].status === 'fulfilled' ? results[2].value : null,
        errors: results.filter(r => r.status === 'rejected').map(r => r.reason)
      };

      return syncResults;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const processPendingSync = createAsyncThunk(
  'erpSync/processPendingSync',
  async (_, { rejectWithValue }) => {
    try {
      const result = await erpIntegration.processPendingSync();
      return result;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const checkConnectivity = createAsyncThunk(
  'erpSync/checkConnectivity',
  async () => {
    return await erpIntegration.checkConnectivity();
  }
);

const initialState = {
  isOnline: true,
  lastSync: null,
  syncInProgress: false,
  pendingSync: 0,
  syncError: null,
  connectivity: {
    isChecking: false,
    lastCheck: null
  },
  data: {
    os: [],
    agendamentos: [],
    clientes: []
  }
};

const erpSyncSlice = createSlice({
  name: 'erpSync',
  initialState,
  reducers: {
    setOnlineStatus: (state, action) => {
      state.isOnline = action.payload;
    },
    
    clearSyncError: (state) => {
      state.syncError = null;
    },
    
    setPendingSync: (state, action) => {
      state.pendingSync = action.payload;
    },
    
    updateSyncData: (state, action) => {
      const { type, data } = action.payload;
      if (state.data[type]) {
        state.data[type] = data;
      }
    }
  },
  
  extraReducers: (builder) => {
    // Sync completo
    builder
      .addCase(syncAllData.pending, (state) => {
        state.syncInProgress = true;
        state.syncError = null;
      })
      .addCase(syncAllData.fulfilled, (state, action) => {
        state.syncInProgress = false;
        state.lastSync = new Date().toISOString();
        state.syncError = null;
        
        // Atualizar dados se disponíveis
        const { os, agendamentos, clientes } = action.payload;
        if (os?.ordens) state.data.os = os.ordens;
        if (agendamentos?.agendamentos) state.data.agendamentos = agendamentos.agendamentos;
        if (clientes?.clientes) state.data.clientes = clientes.clientes;
        
        // Log de erros se houver
        if (action.payload.errors.length > 0) {
          console.warn('Erros durante sync:', action.payload.errors);
        }
      })
      .addCase(syncAllData.rejected, (state, action) => {
        state.syncInProgress = false;
        state.syncError = action.payload;
        state.isOnline = false;
      })
      
      // Processar sync pendente
      .addCase(processPendingSync.fulfilled, (state, action) => {
        state.pendingSync = Math.max(0, state.pendingSync - action.payload.processed);
      })
      
      // Verificar conectividade
      .addCase(checkConnectivity.pending, (state) => {
        state.connectivity.isChecking = true;
      })
      .addCase(checkConnectivity.fulfilled, (state, action) => {
        state.isOnline = action.payload;
        state.connectivity.isChecking = false;
        state.connectivity.lastCheck = new Date().toISOString();
      })
      .addCase(checkConnectivity.rejected, (state) => {
        state.isOnline = false;
        state.connectivity.isChecking = false;
        state.connectivity.lastCheck = new Date().toISOString();
      });
  }
});

export const {
  setOnlineStatus,
  clearSyncError,
  setPendingSync,
  updateSyncData
} = erpSyncSlice.actions;

// Selectors
export const selectIsOnline = (state) => state.erpSync.isOnline;
export const selectSyncInProgress = (state) => state.erpSync.syncInProgress;
export const selectLastSync = (state) => state.erpSync.lastSync;
export const selectPendingSync = (state) => state.erpSync.pendingSync;
export const selectSyncError = (state) => state.erpSync.syncError;
export const selectSyncData = (state) => state.erpSync.data;

export default erpSyncSlice.reducer;