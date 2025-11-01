import { createSlice } from '@reduxjs/toolkit';

/**
 * Slice para Funcionalidade Offline
 * Gerencia cache local, dados offline e sincronização
 */
const initialState = {
  // Status offline
  isOfflineMode: false,
  hasOfflineData: false,
  offlineDataSize: 0,
  
  // Cache local
  cache: {
    os: {},
    agendamentos: {},
    clientes: {},
    produtos: {},
    fotos: {},
  },
  
  // Ações pendentes (offline queue)
  pendingActions: [],
  
  // Configurações offline
  settings: {
    autoDownloadImages: true,
    maxCacheSize: 100, // MB
    cacheExpiration: 7, // dias
    prioritySync: ['os', 'agendamentos'],
  },
  
  // Estatísticas
  stats: {
    totalCachedItems: 0,
    cacheHitRate: 0,
    lastCleanup: null,
    savedRequests: 0,
  },
  
  // Status de limpeza
  isCleaningCache: false,
  
  error: null,
};

const offlineSlice = createSlice({
  name: 'offline',
  initialState,
  reducers: {
    // Ativar/desativar modo offline
    setOfflineMode: (state, action) => {
      state.isOfflineMode = action.payload;
    },
    
    // Adicionar item ao cache
    addToCache: (state, action) => {
      const { type, key, data, timestamp } = action.payload;
      
      if (!state.cache[type]) {
        state.cache[type] = {};
      }
      
      state.cache[type][key] = {
        data,
        timestamp: timestamp || new Date().toISOString(),
        accessed: new Date().toISOString(),
        size: JSON.stringify(data).length,
      };
      
      // Atualizar estatísticas
      state.stats.totalCachedItems += 1;
      state.hasOfflineData = true;
      
      // Calcular tamanho total do cache
      state.offlineDataSize = Object.values(state.cache)
        .reduce((total, typeCache) => {
          return total + Object.values(typeCache)
            .reduce((typeTotal, item) => typeTotal + (item.size || 0), 0);
        }, 0);
    },
    
    // Recuperar item do cache
    getFromCache: (state, action) => {
      const { type, key } = action.payload;
      
      if (state.cache[type] && state.cache[type][key]) {
        // Atualizar último acesso
        state.cache[type][key].accessed = new Date().toISOString();
        
        // Atualizar taxa de hit do cache
        state.stats.cacheHitRate = Math.min(state.stats.cacheHitRate + 0.1, 100);
        
        return state.cache[type][key].data;
      }
      
      return null;
    },
    
    // Remover item do cache
    removeFromCache: (state, action) => {
      const { type, key } = action.payload;
      
      if (state.cache[type] && state.cache[type][key]) {
        delete state.cache[type][key];
        state.stats.totalCachedItems = Math.max(state.stats.totalCachedItems - 1, 0);
        
        // Recalcular tamanho
        state.offlineDataSize = Object.values(state.cache)
          .reduce((total, typeCache) => {
            return total + Object.values(typeCache)
              .reduce((typeTotal, item) => typeTotal + (item.size || 0), 0);
          }, 0);
        
        // Verificar se ainda há dados offline
        state.hasOfflineData = state.stats.totalCachedItems > 0;
      }
    },
    
    // Adicionar ação pendente
    addPendingAction: (state, action) => {
      const action_item = {
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        retries: 0,
        priority: action.payload.priority || 'normal',
      };
      
      // Inserir por prioridade
      if (action_item.priority === 'high') {
        state.pendingActions.unshift(action_item);
      } else {
        state.pendingActions.push(action_item);
      }
    },
    
    // Remover ação pendente
    removePendingAction: (state, action) => {
      state.pendingActions = state.pendingActions.filter(
        item => item.id !== action.payload
      );
    },
    
    // Incrementar tentativas de ação pendente
    incrementActionRetries: (state, action) => {
      const actionItem = state.pendingActions.find(item => item.id === action.payload);
      if (actionItem) {
        actionItem.retries += 1;
        
        // Remover se excedeu tentativas máximas
        if (actionItem.retries >= 3) {
          state.pendingActions = state.pendingActions.filter(
            item => item.id !== action.payload
          );
        }
      }
    },
    
    // Limpar ações pendentes
    clearPendingActions: (state) => {
      state.pendingActions = [];
    },
    
    // Iniciar limpeza do cache
    startCacheCleanup: (state) => {
      state.isCleaningCache = true;
    },
    
    // Limpeza do cache concluída
    cacheCleanupComplete: (state, action) => {
      state.isCleaningCache = false;
      state.stats.lastCleanup = new Date().toISOString();
      
      if (action.payload) {
        state.stats.totalCachedItems = action.payload.remainingItems || 0;
        state.offlineDataSize = action.payload.newCacheSize || 0;
      }
    },
    
    // Limpar todo o cache
    clearCache: (state) => {
      state.cache = {
        os: {},
        agendamentos: {},
        clientes: {},
        produtos: {},
        fotos: {},
      };
      state.hasOfflineData = false;
      state.offlineDataSize = 0;
      state.stats.totalCachedItems = 0;
    },
    
    // Atualizar configurações offline
    updateOfflineSettings: (state, action) => {
      state.settings = { ...state.settings, ...action.payload };
    },
    
    // Registrar request salvo (cache hit)
    recordSavedRequest: (state) => {
      state.stats.savedRequests += 1;
    },
    
    // Pré-carregar dados críticos
    preloadCriticalData: (state, action) => {
      const { os, agendamentos, clientes } = action.payload;
      
      // Adicionar OS críticas ao cache
      if (os) {
        os.forEach(osItem => {
          state.cache.os[osItem.id] = {
            data: osItem,
            timestamp: new Date().toISOString(),
            accessed: new Date().toISOString(),
            size: JSON.stringify(osItem).length,
            critical: true,
          };
        });
      }
      
      // Adicionar agendamentos do dia ao cache
      if (agendamentos) {
        agendamentos.forEach(agenda => {
          state.cache.agendamentos[agenda.id] = {
            data: agenda,
            timestamp: new Date().toISOString(),
            accessed: new Date().toISOString(),
            size: JSON.stringify(agenda).length,
            critical: true,
          };
        });
      }
      
      // Adicionar clientes recentes ao cache
      if (clientes) {
        clientes.forEach(cliente => {
          state.cache.clientes[cliente.id] = {
            data: cliente,
            timestamp: new Date().toISOString(),
            accessed: new Date().toISOString(),
            size: JSON.stringify(cliente).length,
            critical: false,
          };
        });
      }
      
      // Atualizar estatísticas
      state.hasOfflineData = true;
      state.stats.totalCachedItems = Object.values(state.cache)
        .reduce((total, typeCache) => total + Object.keys(typeCache).length, 0);
      
      // Recalcular tamanho do cache
      state.offlineDataSize = Object.values(state.cache)
        .reduce((total, typeCache) => {
          return total + Object.values(typeCache)
            .reduce((typeTotal, item) => typeTotal + (item.size || 0), 0);
        }, 0);
    },
    
    // Limpar erro
    clearError: (state) => {
      state.error = null;
    },
    
    // Definir erro
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const {
  setOfflineMode,
  addToCache,
  getFromCache,
  removeFromCache,
  addPendingAction,
  removePendingAction,
  incrementActionRetries,
  clearPendingActions,
  startCacheCleanup,
  cacheCleanupComplete,
  clearCache,
  updateOfflineSettings,
  recordSavedRequest,
  preloadCriticalData,
  clearError,
  setError,
} = offlineSlice.actions;

// Seletores
export const selectIsOfflineMode = (state) => state.offline.isOfflineMode;
export const selectHasOfflineData = (state) => state.offline.hasOfflineData;
export const selectOfflineDataSize = (state) => state.offline.offlineDataSize;
export const selectCache = (state) => state.offline.cache;
export const selectPendingActions = (state) => state.offline.pendingActions;
export const selectOfflineSettings = (state) => state.offline.settings;
export const selectOfflineStats = (state) => state.offline.stats;
export const selectIsCleaningCache = (state) => state.offline.isCleaningCache;
export const selectOfflineError = (state) => state.offline.error;

// Seletores derivados
export const selectCacheSize = (state) => {
  return Math.round(state.offline.offlineDataSize / (1024 * 1024) * 100) / 100; // MB
};

export const selectHighPriorityPendingActions = (state) => {
  return state.offline.pendingActions.filter(action => action.priority === 'high');
};

export const selectCachedItemsByType = (state, type) => {
  return state.offline.cache[type] || {};
};

export default offlineSlice.reducer;