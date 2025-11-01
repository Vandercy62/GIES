import React, { useEffect } from 'react';
import { StatusBar, Alert, AppState } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import * as SplashScreen from 'expo-splash-screen';

import { store, persistor } from './src/store/store';
import AppNavigator from './src/navigation/AppNavigator';
import LoadingScreen from './src/components/LoadingScreen';
import { theme } from './src/styles/theme';

// Serviços
import offlineDb from './src/services/offlineDatabaseService';
import syncService from './src/services/syncService';
import notificationService from './src/services/notificationService';

// Manter splash screen até carregar
SplashScreen.preventAutoHideAsync();

/**
 * App Principal - Sistema ERP Primotex Mobile
 * Aplicativo para técnicos em campo com funcionalidades offline
 */
export default function App() {
  useEffect(() => {
    initializeApp();
  }, []);

  useEffect(() => {
    // Listener para mudanças de estado do app
    const handleAppStateChange = (nextAppState) => {
      if (nextAppState === 'background') {
        // App foi para background - pode pausar sync
        console.log('App foi para background');
      } else if (nextAppState === 'active') {
        // App voltou ao foreground - pode retomar sync
        console.log('App voltou ao foreground');
        if (syncService.getConnectionStatus().isOnline) {
          syncService.syncAll();
        }
      }
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription?.remove();
  }, []);

  const initializeApp = async () => {
    try {
      console.log('Inicializando Primotex ERP Mobile...');

      // Inicializar banco de dados offline
      await offlineDb.init();
      console.log('Banco offline inicializado');

      // Inicializar serviço de sincronização
      await syncService.init();
      console.log('Serviço de sincronização inicializado');

      // Inicializar serviço de notificações
      await notificationService.init();
      console.log('Serviço de notificações inicializado');

      // Verificar se há dados para sincronizar
      const stats = await offlineDb.getStats();
      if (stats.pendingSync > 0 && syncService.getConnectionStatus().isOnline) {
        console.log(`${stats.pendingSync} itens pendentes para sincronização`);
        // Não bloquear a inicialização, sincronizar em background
        setTimeout(() => syncService.syncAll(), 3000);
      }

      console.log('App inicializado com sucesso');

    } catch (error) {
      console.error('Erro na inicialização:', error);
      Alert.alert(
        'Erro de Inicialização',
        'Ocorreu um erro ao inicializar o aplicativo. Tente reiniciar.',
        [{ text: 'OK' }]
      );
    }
  };

  const onBeforeLift = () => {
    // Chamado quando o Redux store está pronto
    SplashScreen.hideAsync();
  };

  return (
    <Provider store={store}>
      <PersistGate
        loading={<LoadingScreen message="Carregando aplicativo..." />}
        persistor={persistor}
        onBeforeLift={onBeforeLift}
      >
        <NavigationContainer>
          <StatusBar
            barStyle="light-content"
            backgroundColor={theme.colors.primary}
            translucent={false}
          />
          <AppNavigator />
        </NavigationContainer>
      </PersistGate>
    </Provider>
  );
}