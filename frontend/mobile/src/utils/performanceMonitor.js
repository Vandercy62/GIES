/**
 * Sistema de Monitoramento de Performance para Produção
 * Métricas, logs e alertas de performance
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

class PerformanceMonitor {
  constructor() {
    this.metrics = {
      appStartTime: Date.now(),
      screenTransitions: [],
      apiCalls: [],
      memoryUsage: [],
      crashReports: [],
      userActions: []
    };
    this.isProduction = __DEV__ === false;
  }

  // Métricas de Inicialização
  recordAppStart() {
    const startTime = Date.now() - this.metrics.appStartTime;
    this.logMetric('app_start', { duration: startTime });
    return startTime;
  }

  // Métricas de Navegação
  recordScreenTransition(fromScreen, toScreen) {
    const transition = {
      from: fromScreen,
      to: toScreen,
      timestamp: Date.now(),
      duration: 0
    };
    
    this.metrics.screenTransitions.push(transition);
    this.logMetric('screen_transition', transition);
  }

  // Métricas de API
  recordApiCall(endpoint, method, duration, status) {
    const apiCall = {
      endpoint,
      method,
      duration,
      status,
      timestamp: Date.now()
    };
    
    this.metrics.apiCalls.push(apiCall);
    
    // Log lentidão de API
    if (duration > 5000) {
      this.logWarning('slow_api_call', apiCall);
    }
    
    // Log erro de API
    if (status >= 400) {
      this.logError('api_error', apiCall);
    }
  }

  // Métricas de Memória
  recordMemoryUsage() {
    if (Platform.OS === 'android') {
      // Simulação de memória no Android
      const memoryInfo = {
        used: Math.floor(Math.random() * 100) + 50, // MB
        total: 512, // MB
        timestamp: Date.now()
      };
      
      this.metrics.memoryUsage.push(memoryInfo);
      
      // Alerta de memória alta
      if (memoryInfo.used > 80) {
        this.logWarning('high_memory_usage', memoryInfo);
      }
    }
  }

  // Ações do Usuário
  recordUserAction(action, context = {}) {
    const userAction = {
      action,
      context,
      timestamp: Date.now()
    };
    
    this.metrics.userActions.push(userAction);
    this.logMetric('user_action', userAction);
  }

  // Relatórios de Crash
  recordCrash(error, context = {}) {
    const crashReport = {
      message: error.message,
      stack: error.stack,
      context,
      timestamp: Date.now(),
      platform: Platform.OS,
      version: Platform.Version
    };
    
    this.metrics.crashReports.push(crashReport);
    this.logError('app_crash', crashReport);
    
    // Salvar crash em storage para envio posterior
    this.saveCrashReport(crashReport);
  }

  // Logging
  logMetric(type, data) {
    if (this.isProduction) {
      // Em produção, apenas logs críticos
      if (type === 'app_crash' || type === 'api_error') {
        console.error(`🚨 ${type}:`, data);
      }
    } else {
      console.log(`📊 ${type}:`, data);
    }
  }

  logWarning(type, data) {
    console.warn(`⚠️ ${type}:`, data);
  }

  logError(type, data) {
    console.error(`❌ ${type}:`, data);
  }

  // Persistência
  async saveCrashReport(crashReport) {
    try {
      const existingCrashes = await AsyncStorage.getItem('crash_reports');
      const crashes = existingCrashes ? JSON.parse(existingCrashes) : [];
      crashes.push(crashReport);
      
      // Manter apenas os últimos 10 crashes
      if (crashes.length > 10) {
        crashes.splice(0, crashes.length - 10);
      }
      
      await AsyncStorage.setItem('crash_reports', JSON.stringify(crashes));
    } catch (error) {
      console.error('Erro ao salvar crash report:', error);
    }
  }

  // Relatórios Periódicos
  async generatePerformanceReport() {
    const report = {
      timestamp: Date.now(),
      platform: Platform.OS,
      metrics: {
        totalScreenTransitions: this.metrics.screenTransitions.length,
        averageApiResponseTime: this.calculateAverageApiTime(),
        slowApiCalls: this.metrics.apiCalls.filter(call => call.duration > 5000).length,
        totalCrashes: this.metrics.crashReports.length,
        memoryPeakUsage: this.calculatePeakMemoryUsage(),
        topUserActions: this.getTopUserActions()
      }
    };
    
    // Salvar relatório
    await AsyncStorage.setItem('performance_report', JSON.stringify(report));
    
    return report;
  }

  // Cálculos Auxiliares
  calculateAverageApiTime() {
    if (this.metrics.apiCalls.length === 0) return 0;
    
    const totalTime = this.metrics.apiCalls.reduce((sum, call) => sum + call.duration, 0);
    return Math.round(totalTime / this.metrics.apiCalls.length);
  }

  calculatePeakMemoryUsage() {
    if (this.metrics.memoryUsage.length === 0) return 0;
    
    return Math.max(...this.metrics.memoryUsage.map(usage => usage.used));
  }

  getTopUserActions() {
    const actionCounts = {};
    this.metrics.userActions.forEach(action => {
      actionCounts[action.action] = (actionCounts[action.action] || 0) + 1;
    });
    
    return Object.entries(actionCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([action, count]) => ({ action, count }));
  }

  // Cleanup Periódico
  cleanup() {
    const now = Date.now();
    const oneHourAgo = now - (60 * 60 * 1000);
    
    // Limpar métricas antigas (mais de 1 hora)
    this.metrics.screenTransitions = this.metrics.screenTransitions.filter(
      transition => transition.timestamp > oneHourAgo
    );
    
    this.metrics.apiCalls = this.metrics.apiCalls.filter(
      call => call.timestamp > oneHourAgo
    );
    
    this.metrics.memoryUsage = this.metrics.memoryUsage.filter(
      usage => usage.timestamp > oneHourAgo
    );
    
    this.metrics.userActions = this.metrics.userActions.filter(
      action => action.timestamp > oneHourAgo
    );
    
    console.log('🧹 Performance metrics cleaned up');
  }

  // Inicialização automática
  startMonitoring() {
    // Monitorar memória a cada 30 segundos
    setInterval(() => {
      this.recordMemoryUsage();
    }, 30000);
    
    // Cleanup a cada hora
    setInterval(() => {
      this.cleanup();
    }, 60 * 60 * 1000);
    
    // Relatório a cada 6 horas
    setInterval(() => {
      this.generatePerformanceReport();
    }, 6 * 60 * 60 * 1000);
    
    console.log('📊 Performance monitoring started');
  }
}

// Instância global
const performanceMonitor = new PerformanceMonitor();

// HOC para monitorar componentes
export const withPerformanceMonitoring = (WrappedComponent, componentName) => {
  return React.forwardRef((props, ref) => {
    React.useEffect(() => {
      const startTime = Date.now();
      performanceMonitor.recordUserAction('component_mount', { component: componentName });
      
      return () => {
        const duration = Date.now() - startTime;
        performanceMonitor.recordUserAction('component_unmount', { 
          component: componentName, 
          duration 
        });
      };
    }, []);
    
    return <WrappedComponent {...props} ref={ref} />;
  });
};

export default performanceMonitor;