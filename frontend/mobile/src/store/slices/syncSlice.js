import { createSlice } from '@reduxjs/toolkit';

/**
 * Slice para Sincronização Online/Offline
 * Gerencia status da conexão e filas de sincronização
 */
const initialState = {
  isOnline: true,
  isConnected: false,
  connectionType: null, // wifi, cellular, none
  bandwidth: 'high', // high, medium, low
  
  // Filas de sincronização
  uploadQueue: [],
  downloadQueue: [],
  
  // Status sync
  isSyncing: false,
  lastSync: null,
  nextSync: null,
  autoSyncEnabled: true,
  
  // Conflitos
  conflicts: [],
  
  // Estatísticas
  stats: {
    totalUploads: 0,
    totalDownloads: 0,
    failedUploads: 0,
    failedDownloads: 0,
    dataUsage: 0,
  },
  
  error: null,
};

const syncSlice = createSlice({
  name: 'sync',
  initialState,
  reducers: {
    // Status de conexão
    setConnectionStatus: (state, action) => {
      const { isOnline, isConnected, connectionType, bandwidth } = action.payload;
      state.isOnline = isOnline;
      state.isConnected = isConnected;
      state.connectionType = connectionType;
      state.bandwidth = bandwidth;
      
      // Se ficou online, agendar próxima sync
      if (isOnline && state.autoSyncEnabled) {
        state.nextSync = new Date(Date.now() + 30000).toISOString(); // 30s
      }
    },
    
    // Adicionar à fila de upload
    addToUploadQueue: (state, action) => {
      const item = {
        ...action.payload,
        id: Date.now().toString(),
        priority: action.payload.priority || 'normal',
        timestamp: new Date().toISOString(),
        retries: 0,
      };
      
      // Inserir por prioridade
      if (item.priority === 'high') {
        state.uploadQueue.unshift(item);
      } else {
        state.uploadQueue.push(item);
      }
    },
    
    // Adicionar à fila de download
    addToDownloadQueue: (state, action) => {
      const item = {
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        retries: 0,
      };
      state.downloadQueue.push(item);
    },
    
    // Remover da fila de upload
    removeFromUploadQueue: (state, action) => {
      state.uploadQueue = state.uploadQueue.filter(
        item => item.id !== action.payload
      );
    },
    
    // Remover da fila de download
    removeFromDownloadQueue: (state, action) => {
      state.downloadQueue = state.downloadQueue.filter(
        item => item.id !== action.payload
      );
    },
    
    // Iniciar sincronização
    startSync: (state) => {
      state.isSyncing = true;
      state.error = null;
    },
    
    // Sincronização bem-sucedida
    syncSuccess: (state, action) => {
      state.isSyncing = false;
      state.lastSync = new Date().toISOString();
      state.error = null;
      
      // Agendar próxima sync se auto-sync ativado
      if (state.autoSyncEnabled) {
        const interval = state.bandwidth === 'high' ? 300000 : 600000; // 5min ou 10min
        state.nextSync = new Date(Date.now() + interval).toISOString();
      }
      
      // Atualizar estatísticas
      if (action.payload) {
        state.stats.totalUploads += action.payload.uploads || 0;
        state.stats.totalDownloads += action.payload.downloads || 0;
        state.stats.dataUsage += action.payload.dataUsage || 0;
      }
    },
    
    // Falha na sincronização
    syncFailure: (state, action) => {
      state.isSyncing = false;
      state.error = action.payload;
      
      // Incrementar tentativas nos itens da fila
      state.uploadQueue.forEach(item => {
        item.retries += 1;
      });
      
      state.downloadQueue.forEach(item => {
        item.retries += 1;
      });
      
      // Remover itens com muitas tentativas
      state.uploadQueue = state.uploadQueue.filter(item => item.retries < 3);
      state.downloadQueue = state.downloadQueue.filter(item => item.retries < 3);
      
      // Contar falhas
      state.stats.failedUploads += state.uploadQueue.length;
      state.stats.failedDownloads += state.downloadQueue.length;
    },
    
    // Configurar auto-sync
    setAutoSync: (state, action) => {
      state.autoSyncEnabled = action.payload;
      
      if (!action.payload) {
        state.nextSync = null;
      }
    },
    
    // Adicionar conflito
    addConflict: (state, action) => {
      state.conflicts.push({
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
      });
    },
    
    // Resolver conflito
    resolveConflict: (state, action) => {
      state.conflicts = state.conflicts.filter(
        conflict => conflict.id !== action.payload
      );
    },
    
    // Limpar filas
    clearQueues: (state) => {
      state.uploadQueue = [];
      state.downloadQueue = [];
    },
    
    // Limpar conflitos
    clearConflicts: (state) => {
      state.conflicts = [];
    },
    
    // Reset estatísticas
    resetStats: (state) => {
      state.stats = {
        totalUploads: 0,
        totalDownloads: 0,
        failedUploads: 0,
        failedDownloads: 0,
        dataUsage: 0,
      };
    },
    
    // Limpar erro
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setConnectionStatus,
  addToUploadQueue,
  addToDownloadQueue,
  removeFromUploadQueue,
  removeFromDownloadQueue,
  startSync,
  syncSuccess,
  syncFailure,
  setAutoSync,
  addConflict,
  resolveConflict,
  clearQueues,
  clearConflicts,
  resetStats,
  clearError,
} = syncSlice.actions;

// Seletores
export const selectConnectionStatus = (state) => state.sync;
export const selectIsOnline = (state) => state.sync.isOnline;
export const selectUploadQueue = (state) => state.sync.uploadQueue;
export const selectDownloadQueue = (state) => state.sync.downloadQueue;
export const selectIsSyncing = (state) => state.sync.isSyncing;
export const selectConflicts = (state) => state.sync.conflicts;
export const selectSyncStats = (state) => state.sync.stats;
export const selectLastSync = (state) => state.sync.lastSync;
export const selectAutoSyncEnabled = (state) => state.sync.autoSyncEnabled;

export default syncSlice.reducer;