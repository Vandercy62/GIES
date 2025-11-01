/**
 * Configuração de Performance para Produção
 * Lazy Loading, Code Splitting e Otimizações
 */

import React, { lazy, Suspense } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { theme } from '../styles/theme';

// Loading Component para Lazy Loading
const LoadingScreen = () => (
  <View style={{
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background
  }}>
    <ActivityIndicator size="large" color={theme.colors.primary} />
  </View>
);

// Lazy Loading das telas principais
export const LazyOSListScreen = lazy(() => import('../screens/os/OSListScreen'));
export const LazyOSDetailScreen = lazy(() => import('../screens/os/OSDetailScreen'));
export const LazyOSExecutionScreen = lazy(() => import('../screens/os/OSExecutionScreen'));
export const LazyAgendamentoScreen = lazy(() => import('../screens/agendamento/AgendamentoScreen'));
export const LazyCalendarScreen = lazy(() => import('../screens/agendamento/CalendarScreen'));
export const LazyNotificationsScreen = lazy(() => import('../screens/notifications/NotificationsScreen'));
export const LazyNotificationSettingsScreen = lazy(() => import('../screens/notifications/NotificationSettingsScreen'));
export const LazyAnalyticsScreen = lazy(() => import('../screens/analytics/AnalyticsScreen'));
export const LazyReportsManagerScreen = lazy(() => import('../screens/analytics/ReportsManagerScreen'));
export const LazyAnalyticsSettingsScreen = lazy(() => import('../screens/analytics/AnalyticsSettingsScreen'));

// HOC para Lazy Loading com Loading Screen
export const withLazyLoading = (Component) => {
  return (props) => (
    <Suspense fallback={<LoadingScreen />}>
      <Component {...props} />
    </Suspense>
  );
};

// Preload crítico - carrega componentes essenciais
export const preloadCriticalComponents = () => {
  // Preload componentes críticos em background
  import('../screens/dashboard/DashboardScreen');
  import('../screens/auth/LoginScreen');
  import('../screens/os/OSListScreen');
};

// Bundle Analysis Helpers
export const bundleConfig = {
  // Chunks principais
  chunks: {
    'auth': ['LoginScreen', 'BiometricAuthScreen'],
    'dashboard': ['DashboardScreen'],
    'os': ['OSListScreen', 'OSDetailScreen', 'OSExecutionScreen'],
    'agenda': ['AgendamentoScreen', 'CalendarScreen'],
    'notifications': ['NotificationsScreen', 'NotificationSettingsScreen'],
    'analytics': ['AnalyticsScreen', 'ReportsManagerScreen', 'AnalyticsSettingsScreen'],
  },
  
  // Prioridades de carregamento
  priority: {
    critical: ['auth', 'dashboard'],
    high: ['os'],
    medium: ['agenda', 'notifications'],
    low: ['analytics']
  }
};

// Memory Management
export const memoryOptimization = {
  // Limpar cache não essencial
  clearNonEssentialCache: () => {
    // Implementar limpeza de cache não crítico
    console.log('🧹 Clearing non-essential cache...');
  },
  
  // Gerenciar imagens em background
  optimizeImageMemory: () => {
    // Implementar otimização de memória para imagens
    console.log('🖼️ Optimizing image memory...');
  },
  
  // Cleanup de listeners não utilizados
  cleanupListeners: () => {
    // Implementar cleanup de event listeners
    console.log('🎧 Cleaning up unused listeners...');
  }
};

export default {
  LazyOSListScreen,
  LazyOSDetailScreen,
  LazyOSExecutionScreen,
  LazyAgendamentoScreen,
  LazyCalendarScreen,
  LazyNotificationsScreen,
  LazyNotificationSettingsScreen,
  LazyAnalyticsScreen,
  LazyReportsManagerScreen,
  LazyAnalyticsSettingsScreen,
  withLazyLoading,
  preloadCriticalComponents,
  bundleConfig,
  memoryOptimization
};