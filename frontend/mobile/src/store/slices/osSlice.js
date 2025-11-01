import { createSlice } from '@reduxjs/toolkit';

/**
 * Slice para Ordens de Serviço (OS)
 * Gerencia lista, detalhes, execução e sincronização de OS
 */
const initialState = {
  // Lista de OS do técnico
  osList: [],
  osAtivas: [],
  osHoje: [],
  
  // OS atual em execução
  osAtual: null,
  
  // Estados de loading
  isLoading: false,
  isLoadingDetails: false,
  isSyncing: false,
  
  // Filtros e busca
  filtros: {
    status: 'todas',
    prioridade: 'todas',
    data: null,
  },
  searchTerm: '',
  
  // Errors
  error: null,
  
  // Cache e offline
  lastSync: null,
  pendingActions: [],
  
  // Estatísticas
  stats: {
    totalOS: 0,
    concluidas: 0,
    emAndamento: 0,
    pendentes: 0,
  },
};

const osSlice = createSlice({
  name: 'os',
  initialState,
  reducers: {
    // Carregar lista de OS
    loadOSStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    
    loadOSSuccess: (state, action) => {
      state.osList = action.payload;
      state.osAtivas = action.payload.filter(os => 
        ['visita_tecnica', 'execucao'].includes(os.fase_atual)
      );
      state.osHoje = action.payload.filter(os => {
        const hoje = new Date().toDateString();
        return new Date(os.data_agendamento).toDateString() === hoje;
      });
      state.isLoading = false;
      state.error = null;
      state.lastSync = new Date().toISOString();
      
      // Atualizar estatísticas
      state.stats = {
        totalOS: action.payload.length,
        concluidas: action.payload.filter(os => os.fase_atual === 'pos_venda').length,
        emAndamento: action.payload.filter(os => 
          ['visita_tecnica', 'execucao'].includes(os.fase_atual)
        ).length,
        pendentes: action.payload.filter(os => 
          ['solicitacao', 'orcamento', 'aprovacao'].includes(os.fase_atual)
        ).length,
      };
    },
    
    loadOSFailure: (state, action) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    
    // Carregar detalhes de uma OS
    loadOSDetailsStart: (state) => {
      state.isLoadingDetails = true;
      state.error = null;
    },
    
    loadOSDetailsSuccess: (state, action) => {
      state.osAtual = action.payload;
      state.isLoadingDetails = false;
      state.error = null;
      
      // Atualizar na lista também
      const index = state.osList.findIndex(os => os.id === action.payload.id);
      if (index !== -1) {
        state.osList[index] = action.payload;
      }
    },
    
    loadOSDetailsFailure: (state, action) => {
      state.isLoadingDetails = false;
      state.error = action.payload;
    },
    
    // Iniciar execução de OS
    startOSExecution: (state, action) => {
      const osId = action.payload.osId;
      const checkInData = action.payload.checkInData;
      
      // Atualizar OS atual
      if (state.osAtual && state.osAtual.id === osId) {
        state.osAtual.status = 'em_execucao';
        state.osAtual.check_in = checkInData;
      }
      
      // Atualizar na lista
      const index = state.osList.findIndex(os => os.id === osId);
      if (index !== -1) {
        state.osList[index].status = 'em_execucao';
        state.osList[index].check_in = checkInData;
      }
      
      // Adicionar ação offline se necessário
      state.pendingActions.push({
        type: 'start_execution',
        osId,
        data: checkInData,
        timestamp: new Date().toISOString(),
      });
    },
    
    // Finalizar execução de OS
    finishOSExecution: (state, action) => {
      const osId = action.payload.osId;
      const checkOutData = action.payload.checkOutData;
      
      // Atualizar OS atual
      if (state.osAtual && state.osAtual.id === osId) {
        state.osAtual.status = 'concluida';
        state.osAtual.check_out = checkOutData;
        state.osAtual.fase_atual = 'entrega';
      }
      
      // Atualizar na lista
      const index = state.osList.findIndex(os => os.id === osId);
      if (index !== -1) {
        state.osList[index].status = 'concluida';
        state.osList[index].check_out = checkOutData;
        state.osList[index].fase_atual = 'entrega';
      }
      
      // Adicionar ação offline
      state.pendingActions.push({
        type: 'finish_execution',
        osId,
        data: checkOutData,
        timestamp: new Date().toISOString(),
      });
    },
    
    // Adicionar foto à OS
    addPhotoToOS: (state, action) => {
      const { osId, photo } = action.payload;
      
      if (state.osAtual && state.osAtual.id === osId) {
        if (!state.osAtual.fotos) state.osAtual.fotos = [];
        state.osAtual.fotos.push(photo);
      }
      
      const index = state.osList.findIndex(os => os.id === osId);
      if (index !== -1) {
        if (!state.osList[index].fotos) state.osList[index].fotos = [];
        state.osList[index].fotos.push(photo);
      }
      
      // Adicionar ação offline
      state.pendingActions.push({
        type: 'add_photo',
        osId,
        data: photo,
        timestamp: new Date().toISOString(),
      });
    },
    
    // Adicionar assinatura à OS
    addSignatureToOS: (state, action) => {
      const { osId, signature } = action.payload;
      
      if (state.osAtual && state.osAtual.id === osId) {
        state.osAtual.assinatura_cliente = signature;
      }
      
      const index = state.osList.findIndex(os => os.id === osId);
      if (index !== -1) {
        state.osList[index].assinatura_cliente = signature;
      }
      
      // Adicionar ação offline
      state.pendingActions.push({
        type: 'add_signature',
        osId,
        data: signature,
        timestamp: new Date().toISOString(),
      });
    },
    
    // Atualizar observações da OS
    updateOSObservations: (state, action) => {
      const { osId, observacoes } = action.payload;
      
      if (state.osAtual && state.osAtual.id === osId) {
        state.osAtual.observacoes_tecnico = observacoes;
      }
      
      const index = state.osList.findIndex(os => os.id === osId);
      if (index !== -1) {
        state.osList[index].observacoes_tecnico = observacoes;
      }
      
      // Adicionar ação offline
      state.pendingActions.push({
        type: 'update_observations',
        osId,
        data: { observacoes },
        timestamp: new Date().toISOString(),
      });
    },
    
    // Filtros e busca
    setFiltros: (state, action) => {
      state.filtros = { ...state.filtros, ...action.payload };
    },
    
    setSearchTerm: (state, action) => {
      state.searchTerm = action.payload;
    },
    
    // Sincronização
    syncStart: (state) => {
      state.isSyncing = true;
    },
    
    syncSuccess: (state) => {
      state.isSyncing = false;
      state.pendingActions = [];
      state.lastSync = new Date().toISOString();
    },
    
    syncFailure: (state, action) => {
      state.isSyncing = false;
      state.error = action.payload;
    },
    
    // Limpar dados
    clearOSData: (state) => {
      return initialState;
    },
    
    clearError: (state) => {
      state.error = null;
    },
    
    // Selecionar OS atual
    setOSAtual: (state, action) => {
      state.osAtual = action.payload;
    },
  },
});

export const {
  loadOSStart,
  loadOSSuccess,
  loadOSFailure,
  loadOSDetailsStart,
  loadOSDetailsSuccess,
  loadOSDetailsFailure,
  startOSExecution,
  finishOSExecution,
  addPhotoToOS,
  addSignatureToOS,
  updateOSObservations,
  setFiltros,
  setSearchTerm,
  syncStart,
  syncSuccess,
  syncFailure,
  clearOSData,
  clearError,
  setOSAtual,
} = osSlice.actions;

// Seletores
export const selectOSList = (state) => state.os.osList;
export const selectOSAtivas = (state) => state.os.osAtivas;
export const selectOSHoje = (state) => state.os.osHoje;
export const selectOSAtual = (state) => state.os.osAtual;
export const selectOSStats = (state) => state.os.stats;
export const selectOSLoading = (state) => state.os.isLoading;
export const selectOSError = (state) => state.os.error;
export const selectPendingActions = (state) => state.os.pendingActions;
export const selectLastSync = (state) => state.os.lastSync;

export default osSlice.reducer;