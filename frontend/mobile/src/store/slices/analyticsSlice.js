import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import moment from 'moment';

/**
 * Analytics e Relatórios - Redux Slice
 * Gerencia dados de performance, KPIs e geração de relatórios
 */

// ============================================================================
// ASYNC THUNKS - Ações Assíncronas
// ============================================================================

/**
 * Buscar estatísticas gerais do dashboard
 */
export const fetchDashboardStats = createAsyncThunk(
  'analytics/fetchDashboardStats',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState();
      const { os, agendamento } = state;
      
      // Simular dados baseados no estado atual
      const today = moment().startOf('day');
      const thisWeek = moment().startOf('week');
      const thisMonth = moment().startOf('month');
      
      const stats = {
        osStats: {
          total: os.items?.length || 0,
          completed: os.items?.filter(item => item.status === 'completed').length || 0,
          inProgress: os.items?.filter(item => item.status === 'in_progress').length || 0,
          pending: os.items?.filter(item => item.status === 'pending').length || 0,
          overdue: os.items?.filter(item => 
            item.status !== 'completed' && 
            moment(item.deadline).isBefore(today)
          ).length || 0,
        },
        agendaStats: {
          total: agendamento.appointments?.length || 0,
          today: agendamento.appointments?.filter(appt => 
            moment(appt.date).isSame(today, 'day')
          ).length || 0,
          thisWeek: agendamento.appointments?.filter(appt => 
            moment(appt.date).isAfter(thisWeek)
          ).length || 0,
          thisMonth: agendamento.appointments?.filter(appt => 
            moment(appt.date).isAfter(thisMonth)
          ).length || 0,
        },
        performance: {
          completionRate: calculateCompletionRate(os.items || []),
          averageTime: calculateAverageCompletionTime(os.items || []),
          onTimeDelivery: calculateOnTimeDelivery(os.items || []),
          customerSatisfaction: 4.5, // Mock data
        },
        trends: generateTrendData(os.items || [], agendamento.appointments || []),
      };
      
      return stats;
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error);
      return rejectWithValue(error.message);
    }
  }
);

/**
 * Gerar relatório em PDF
 */
export const generateReport = createAsyncThunk(
  'analytics/generateReport',
  async ({ reportType, dateRange, includeCharts = true }, { getState, rejectWithValue }) => {
    try {
      const state = getState();
      const { os, agendamento, analytics } = state;
      
      const reportData = {
        type: reportType,
        dateRange,
        generatedAt: new Date().toISOString(),
        data: {
          os: filterDataByDateRange(os.items || [], dateRange),
          appointments: filterDataByDateRange(agendamento.appointments || [], dateRange),
          stats: analytics.dashboardStats,
        },
        includeCharts,
      };
      
      // Aqui seria chamada a API para gerar o PDF
      // Por enquanto simulamos
      const reportId = `report_${Date.now()}`;
      
      return {
        id: reportId,
        ...reportData,
        filePath: `reports/${reportId}.pdf`,
        status: 'completed',
      };
    } catch (error) {
      console.error('Erro ao gerar relatório:', error);
      return rejectWithValue(error.message);
    }
  }
);

/**
 * Buscar dados para gráficos de performance
 */
export const fetchPerformanceCharts = createAsyncThunk(
  'analytics/fetchPerformanceCharts',
  async ({ period = '30d', chartType = 'all' }, { getState, rejectWithValue }) => {
    try {
      const state = getState();
      const { os, agendamento } = state;
      
      const endDate = moment();
      const startDate = moment().subtract(
        period === '7d' ? 7 : period === '30d' ? 30 : 90, 
        'days'
      );
      
      const filteredOS = (os.items || []).filter(item => 
        moment(item.createdAt).isBetween(startDate, endDate, 'day', '[]')
      );
      
      const filteredAppointments = (agendamento.appointments || []).filter(appt => 
        moment(appt.date).isBetween(startDate, endDate, 'day', '[]')
      );
      
      const charts = {
        osCompletionTrend: generateCompletionTrendData(filteredOS, startDate, endDate),
        appointmentsTrend: generateAppointmentsTrendData(filteredAppointments, startDate, endDate),
        performanceMetrics: generatePerformanceMetricsData(filteredOS),
        categoryDistribution: generateCategoryDistributionData(filteredOS),
        timeAnalysis: generateTimeAnalysisData(filteredOS),
      };
      
      return {
        period,
        chartType,
        data: charts,
        generatedAt: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Erro ao buscar dados dos gráficos:', error);
      return rejectWithValue(error.message);
    }
  }
);

/**
 * Exportar dados para compartilhamento
 */
export const exportData = createAsyncThunk(
  'analytics/exportData',
  async ({ format, dataType, dateRange }, { getState, rejectWithValue }) => {
    try {
      const state = getState();
      const { os, agendamento } = state;
      
      let exportData;
      
      switch (dataType) {
        case 'os':
          exportData = filterDataByDateRange(os.items || [], dateRange);
          break;
        case 'appointments':
          exportData = filterDataByDateRange(agendamento.appointments || [], dateRange);
          break;
        case 'combined':
          exportData = {
            os: filterDataByDateRange(os.items || [], dateRange),
            appointments: filterDataByDateRange(agendamento.appointments || [], dateRange),
          };
          break;
        default:
          throw new Error('Tipo de dados inválido');
      }
      
      const exportFile = {
        id: `export_${Date.now()}`,
        format,
        dataType,
        dateRange,
        data: exportData,
        generatedAt: new Date().toISOString(),
        filePath: `exports/data_${Date.now()}.${format}`,
      };
      
      return exportFile;
    } catch (error) {
      console.error('Erro ao exportar dados:', error);
      return rejectWithValue(error.message);
    }
  }
);

// ============================================================================
// UTILITY FUNCTIONS - Funções Auxiliares
// ============================================================================

const calculateCompletionRate = (osItems) => {
  if (!osItems.length) return 0;
  const completed = osItems.filter(item => item.status === 'completed').length;
  return Math.round((completed / osItems.length) * 100);
};

const calculateAverageCompletionTime = (osItems) => {
  const completedOS = osItems.filter(item => 
    item.status === 'completed' && item.completedAt && item.createdAt
  );
  
  if (!completedOS.length) return 0;
  
  const totalTime = completedOS.reduce((sum, item) => {
    const start = moment(item.createdAt);
    const end = moment(item.completedAt);
    return sum + end.diff(start, 'hours');
  }, 0);
  
  return Math.round(totalTime / completedOS.length);
};

const calculateOnTimeDelivery = (osItems) => {
  const completedOS = osItems.filter(item => 
    item.status === 'completed' && item.deadline && item.completedAt
  );
  
  if (!completedOS.length) return 0;
  
  const onTime = completedOS.filter(item => 
    moment(item.completedAt).isSameOrBefore(moment(item.deadline))
  ).length;
  
  return Math.round((onTime / completedOS.length) * 100);
};

const generateTrendData = (osItems, appointments) => {
  const last7Days = Array.from({ length: 7 }, (_, i) => {
    const date = moment().subtract(i, 'days');
    return {
      date: date.format('YYYY-MM-DD'),
      label: date.format('ddd'),
      osCompleted: osItems.filter(item => 
        item.status === 'completed' && 
        moment(item.completedAt).isSame(date, 'day')
      ).length,
      appointmentsScheduled: appointments.filter(appt => 
        moment(appt.date).isSame(date, 'day')
      ).length,
    };
  }).reverse();
  
  return last7Days;
};

const filterDataByDateRange = (data, dateRange) => {
  const { startDate, endDate } = dateRange;
  return data.filter(item => {
    const itemDate = moment(item.createdAt || item.date);
    return itemDate.isBetween(startDate, endDate, 'day', '[]');
  });
};

const generateCompletionTrendData = (osItems, startDate, endDate) => {
  const days = [];
  const current = moment(startDate);
  
  while (current.isSameOrBefore(endDate, 'day')) {
    const dayData = {
      date: current.format('YYYY-MM-DD'),
      label: current.format('DD/MM'),
      completed: osItems.filter(item => 
        item.status === 'completed' && 
        moment(item.completedAt).isSame(current, 'day')
      ).length,
      created: osItems.filter(item => 
        moment(item.createdAt).isSame(current, 'day')
      ).length,
    };
    days.push(dayData);
    current.add(1, 'day');
  }
  
  return days;
};

const generateAppointmentsTrendData = (appointments, startDate, endDate) => {
  const days = [];
  const current = moment(startDate);
  
  while (current.isSameOrBefore(endDate, 'day')) {
    const dayData = {
      date: current.format('YYYY-MM-DD'),
      label: current.format('DD/MM'),
      scheduled: appointments.filter(appt => 
        moment(appt.date).isSame(current, 'day')
      ).length,
      completed: appointments.filter(appt => 
        appt.status === 'completed' && 
        moment(appt.date).isSame(current, 'day')
      ).length,
    };
    days.push(dayData);
    current.add(1, 'day');
  }
  
  return days;
};

const generatePerformanceMetricsData = (osItems) => {
  const statusCounts = osItems.reduce((acc, item) => {
    acc[item.status] = (acc[item.status] || 0) + 1;
    return acc;
  }, {});
  
  return [
    { label: 'Concluídas', value: statusCounts.completed || 0, color: '#4CAF50' },
    { label: 'Em Progresso', value: statusCounts.in_progress || 0, color: '#2196F3' },
    { label: 'Pendentes', value: statusCounts.pending || 0, color: '#FF9800' },
    { label: 'Atrasadas', value: statusCounts.overdue || 0, color: '#F44336' },
  ];
};

const generateCategoryDistributionData = (osItems) => {
  const categories = osItems.reduce((acc, item) => {
    const category = item.category || 'Outros';
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {});
  
  const colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0', '#00BCD4'];
  
  return Object.entries(categories).map(([label, value], index) => ({
    label,
    value,
    color: colors[index % colors.length],
  }));
};

const generateTimeAnalysisData = (osItems) => {
  const completedOS = osItems.filter(item => 
    item.status === 'completed' && item.completedAt && item.createdAt
  );
  
  const timeRanges = {
    '0-4h': 0,
    '4-8h': 0,
    '8-24h': 0,
    '1-3d': 0,
    '3d+': 0,
  };
  
  completedOS.forEach(item => {
    const hours = moment(item.completedAt).diff(moment(item.createdAt), 'hours');
    
    if (hours <= 4) timeRanges['0-4h']++;
    else if (hours <= 8) timeRanges['4-8h']++;
    else if (hours <= 24) timeRanges['8-24h']++;
    else if (hours <= 72) timeRanges['1-3d']++;
    else timeRanges['3d+']++;
  });
  
  return Object.entries(timeRanges).map(([label, value]) => ({
    label,
    value,
  }));
};

// ============================================================================
// SLICE DEFINITION - Definição do Slice
// ============================================================================

const initialState = {
  // Dashboard Stats
  dashboardStats: {
    osStats: {
      total: 0,
      completed: 0,
      inProgress: 0,
      pending: 0,
      overdue: 0,
    },
    agendaStats: {
      total: 0,
      today: 0,
      thisWeek: 0,
      thisMonth: 0,
    },
    performance: {
      completionRate: 0,
      averageTime: 0,
      onTimeDelivery: 0,
      customerSatisfaction: 0,
    },
    trends: [],
  },
  
  // Charts Data
  performanceCharts: {
    period: '30d',
    data: {
      osCompletionTrend: [],
      appointmentsTrend: [],
      performanceMetrics: [],
      categoryDistribution: [],
      timeAnalysis: [],
    },
    generatedAt: null,
  },
  
  // Reports
  reports: [],
  currentReport: null,
  
  // Exports
  exports: [],
  
  // UI State
  loading: {
    stats: false,
    charts: false,
    report: false,
    export: false,
  },
  
  error: null,
  
  // Settings
  settings: {
    defaultPeriod: '30d',
    autoRefresh: true,
    refreshInterval: 300000, // 5 minutos
    chartAnimations: true,
    includeChartsInReports: true,
  },
};

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    // Clear Error
    clearError: (state) => {
      state.error = null;
    },
    
    // Update Settings
    updateSettings: (state, action) => {
      state.settings = {
        ...state.settings,
        ...action.payload,
      };
    },
    
    // Clear Reports
    clearReports: (state) => {
      state.reports = [];
      state.currentReport = null;
    },
    
    // Remove Report
    removeReport: (state, action) => {
      state.reports = state.reports.filter(report => report.id !== action.payload);
      if (state.currentReport?.id === action.payload) {
        state.currentReport = null;
      }
    },
    
    // Clear Exports
    clearExports: (state) => {
      state.exports = [];
    },
    
    // Remove Export
    removeExport: (state, action) => {
      state.exports = state.exports.filter(exp => exp.id !== action.payload);
    },
    
    // Set Current Report
    setCurrentReport: (state, action) => {
      state.currentReport = action.payload;
    },
    
    // Reset Analytics Data
    resetAnalytics: (state) => {
      return {
        ...initialState,
        settings: state.settings, // Manter configurações
      };
    },
  },
  
  extraReducers: (builder) => {
    // Fetch Dashboard Stats
    builder
      .addCase(fetchDashboardStats.pending, (state) => {
        state.loading.stats = true;
        state.error = null;
      })
      .addCase(fetchDashboardStats.fulfilled, (state, action) => {
        state.loading.stats = false;
        state.dashboardStats = action.payload;
      })
      .addCase(fetchDashboardStats.rejected, (state, action) => {
        state.loading.stats = false;
        state.error = action.payload;
      })
      
      // Generate Report
      .addCase(generateReport.pending, (state) => {
        state.loading.report = true;
        state.error = null;
      })
      .addCase(generateReport.fulfilled, (state, action) => {
        state.loading.report = false;
        state.reports.unshift(action.payload);
        state.currentReport = action.payload;
      })
      .addCase(generateReport.rejected, (state, action) => {
        state.loading.report = false;
        state.error = action.payload;
      })
      
      // Fetch Performance Charts
      .addCase(fetchPerformanceCharts.pending, (state) => {
        state.loading.charts = true;
        state.error = null;
      })
      .addCase(fetchPerformanceCharts.fulfilled, (state, action) => {
        state.loading.charts = false;
        state.performanceCharts = action.payload;
      })
      .addCase(fetchPerformanceCharts.rejected, (state, action) => {
        state.loading.charts = false;
        state.error = action.payload;
      })
      
      // Export Data
      .addCase(exportData.pending, (state) => {
        state.loading.export = true;
        state.error = null;
      })
      .addCase(exportData.fulfilled, (state, action) => {
        state.loading.export = false;
        state.exports.unshift(action.payload);
      })
      .addCase(exportData.rejected, (state, action) => {
        state.loading.export = false;
        state.error = action.payload;
      });
  },
});

// ============================================================================
// EXPORTS - Ações e Seletores
// ============================================================================

export const {
  clearError,
  updateSettings,
  clearReports,
  removeReport,
  clearExports,
  removeExport,
  setCurrentReport,
  resetAnalytics,
} = analyticsSlice.actions;

// Seletores
export const selectDashboardStats = (state) => state.analytics.dashboardStats;
export const selectPerformanceCharts = (state) => state.analytics.performanceCharts;
export const selectReports = (state) => state.analytics.reports;
export const selectCurrentReport = (state) => state.analytics.currentReport;
export const selectExports = (state) => state.analytics.exports;
export const selectAnalyticsLoading = (state) => state.analytics.loading;
export const selectAnalyticsError = (state) => state.analytics.error;
export const selectAnalyticsSettings = (state) => state.analytics.settings;

// Seletores Computados
export const selectOSStats = (state) => state.analytics.dashboardStats.osStats;
export const selectAgendaStats = (state) => state.analytics.dashboardStats.agendaStats;
export const selectPerformanceStats = (state) => state.analytics.dashboardStats.performance;
export const selectTrends = (state) => state.analytics.dashboardStats.trends;

export const selectRecentReports = (state) => 
  state.analytics.reports.slice(0, 5);

export const selectChartData = (chartType) => (state) => 
  state.analytics.performanceCharts.data[chartType] || [];

export default analyticsSlice.reducer;