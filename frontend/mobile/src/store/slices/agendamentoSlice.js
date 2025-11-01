import { createSlice } from '@reduxjs/toolkit';

/**
 * Slice para Agendamento e Calendário
 * Gerencia agenda do técnico, compromissos e disponibilidade
 */
const initialState = {
  // Agenda do técnico
  agenda: [],
  agendaHoje: [],
  proximosCompromissos: [],
  
  // Visualização do calendário
  selectedDate: new Date().toISOString().split('T')[0],
  viewMode: 'day', // day, week, month
  
  // Estados de loading
  isLoading: false,
  isCreatingAgendamento: false,
  
  // Filtros
  filtros: {
    tipo: 'todos', // visita, execucao, reuniao
    status: 'todos',
  },
  
  // Disponibilidade do técnico
  disponibilidade: {
    horarioInicio: '08:00',
    horarioFim: '18:00',
    diasTrabalhados: ['seg', 'ter', 'qua', 'qui', 'sex'],
    pausaAlmoco: {
      inicio: '12:00',
      fim: '13:00',
    },
  },
  
  // Navegação GPS
  navegacao: {
    destino: null,
    rota: null,
    tempoEstimado: null,
    distancia: null,
  },
  
  error: null,
  lastSync: null,
};

const agendamentoSlice = createSlice({
  name: 'agendamento',
  initialState,
  reducers: {
    // Carregar agenda
    loadAgendaStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    
    loadAgendaSuccess: (state, action) => {
      state.agenda = action.payload;
      
      // Filtrar agenda de hoje
      const hoje = new Date().toISOString().split('T')[0];
      state.agendaHoje = action.payload.filter(item => 
        item.data_agendamento.startsWith(hoje)
      );
      
      // Próximos compromissos (próximos 7 dias)
      const proximosDias = new Date();
      proximosDias.setDate(proximosDias.getDate() + 7);
      
      state.proximosCompromissos = action.payload
        .filter(item => {
          const dataItem = new Date(item.data_agendamento);
          return dataItem >= new Date() && dataItem <= proximosDias;
        })
        .sort((a, b) => new Date(a.data_agendamento) - new Date(b.data_agendamento))
        .slice(0, 10);
      
      state.isLoading = false;
      state.lastSync = new Date().toISOString();
    },
    
    loadAgendaFailure: (state, action) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    
    // Criar novo agendamento
    createAgendamentoStart: (state) => {
      state.isCreatingAgendamento = true;
      state.error = null;
    },
    
    createAgendamentoSuccess: (state, action) => {
      state.agenda.push(action.payload);
      
      // Atualizar agenda de hoje se necessário
      const hoje = new Date().toISOString().split('T')[0];
      if (action.payload.data_agendamento.startsWith(hoje)) {
        state.agendaHoje.push(action.payload);
      }
      
      // Atualizar próximos compromissos
      const dataItem = new Date(action.payload.data_agendamento);
      const proximosDias = new Date();
      proximosDias.setDate(proximosDias.getDate() + 7);
      
      if (dataItem >= new Date() && dataItem <= proximosDias) {
        state.proximosCompromissos.push(action.payload);
        state.proximosCompromissos.sort(
          (a, b) => new Date(a.data_agendamento) - new Date(b.data_agendamento)
        );
        state.proximosCompromissos = state.proximosCompromissos.slice(0, 10);
      }
      
      state.isCreatingAgendamento = false;
    },
    
    createAgendamentoFailure: (state, action) => {
      state.isCreatingAgendamento = false;
      state.error = action.payload;
    },
    
    // Atualizar agendamento
    updateAgendamento: (state, action) => {
      const { id, updates } = action.payload;
      
      // Atualizar na agenda principal
      const index = state.agenda.findIndex(item => item.id === id);
      if (index !== -1) {
        state.agenda[index] = { ...state.agenda[index], ...updates };
      }
      
      // Atualizar na agenda de hoje
      const hojeIndex = state.agendaHoje.findIndex(item => item.id === id);
      if (hojeIndex !== -1) {
        state.agendaHoje[hojeIndex] = { ...state.agendaHoje[hojeIndex], ...updates };
      }
      
      // Atualizar nos próximos compromissos
      const proximosIndex = state.proximosCompromissos.findIndex(item => item.id === id);
      if (proximosIndex !== -1) {
        state.proximosCompromissos[proximosIndex] = { 
          ...state.proximosCompromissos[proximosIndex], 
          ...updates 
        };
      }
    },
    
    // Check-in no local
    checkInAgendamento: (state, action) => {
      const { id, localizacao, timestamp } = action.payload;
      
      const updateData = {
        status: 'em_andamento',
        check_in: {
          timestamp,
          localizacao,
        },
      };
      
      // Usar a função de update
      agendamentoSlice.caseReducers.updateAgendamento(state, {
        payload: { id, updates: updateData }
      });
    },
    
    // Check-out do local
    checkOutAgendamento: (state, action) => {
      const { id, localizacao, timestamp, observacoes } = action.payload;
      
      const updateData = {
        status: 'concluido',
        check_out: {
          timestamp,
          localizacao,
          observacoes,
        },
      };
      
      agendamentoSlice.caseReducers.updateAgendamento(state, {
        payload: { id, updates: updateData }
      });
    },
    
    // Cancelar agendamento
    cancelAgendamento: (state, action) => {
      const { id, motivo } = action.payload;
      
      const updateData = {
        status: 'cancelado',
        motivo_cancelamento: motivo,
        data_cancelamento: new Date().toISOString(),
      };
      
      agendamentoSlice.caseReducers.updateAgendamento(state, {
        payload: { id, updates: updateData }
      });
    },
    
    // Reagendar
    reagendar: (state, action) => {
      const { id, novaData, motivo } = action.payload;
      
      const updateData = {
        data_agendamento: novaData,
        status: 'reagendado',
        historico_reagendamento: {
          data_anterior: state.agenda.find(item => item.id === id)?.data_agendamento,
          nova_data: novaData,
          motivo,
          timestamp: new Date().toISOString(),
        },
      };
      
      agendamentoSlice.caseReducers.updateAgendamento(state, {
        payload: { id, updates: updateData }
      });
    },
    
    // Configurar navegação GPS
    setNavegacao: (state, action) => {
      state.navegacao = { ...state.navegacao, ...action.payload };
    },
    
    // Limpar navegação
    clearNavegacao: (state) => {
      state.navegacao = {
        destino: null,
        rota: null,
        tempoEstimado: null,
        distancia: null,
      };
    },
    
    // Alterar data selecionada
    setSelectedDate: (state, action) => {
      state.selectedDate = action.payload;
    },
    
    // Alterar modo de visualização
    setViewMode: (state, action) => {
      state.viewMode = action.payload;
    },
    
    // Configurar filtros
    setFiltros: (state, action) => {
      state.filtros = { ...state.filtros, ...action.payload };
    },
    
    // Atualizar disponibilidade
    updateDisponibilidade: (state, action) => {
      state.disponibilidade = { ...state.disponibilidade, ...action.payload };
    },
    
    // Limpar erro
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  loadAgendaStart,
  loadAgendaSuccess,
  loadAgendaFailure,
  createAgendamentoStart,
  createAgendamentoSuccess,
  createAgendamentoFailure,
  updateAgendamento,
  checkInAgendamento,
  checkOutAgendamento,
  cancelAgendamento,
  reagendar,
  setNavegacao,
  clearNavegacao,
  setSelectedDate,
  setViewMode,
  setFiltros,
  updateDisponibilidade,
  clearError,
} = agendamentoSlice.actions;

// Seletores
export const selectAgenda = (state) => state.agendamento.agenda;
export const selectAgendaHoje = (state) => state.agendamento.agendaHoje;
export const selectProximosCompromissos = (state) => state.agendamento.proximosCompromissos;
export const selectSelectedDate = (state) => state.agendamento.selectedDate;
export const selectViewMode = (state) => state.agendamento.viewMode;
export const selectDisponibilidade = (state) => state.agendamento.disponibilidade;
export const selectNavegacao = (state) => state.agendamento.navegacao;
export const selectAgendamentoLoading = (state) => state.agendamento.isLoading;
export const selectAgendamentoError = (state) => state.agendamento.error;

export default agendamentoSlice.reducer;