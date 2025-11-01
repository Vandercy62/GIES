import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';

import authSlice from './slices/authSlice';
import osSlice from './slices/osSlice';
import syncSlice from './slices/syncSlice';
import agendamentoSlice from './slices/agendamentoSlice';
import agendaSlice from './slices/agendaSlice';
import offlineSlice from './slices/offlineSlice';
import notificationsSlice from './slices/notificationsSlice';
import analyticsSlice from './slices/analyticsSlice';
import erpSyncSlice from './slices/erpSyncSlice';

// Configuração de persistência
const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['auth', 'offline', 'agenda', 'notifications', 'analytics', 'erpSync'], // ERP Sync também será persistida
  blacklist: ['sync'], // Sync não deve ser persistido
};

// Combinando reducers
const rootReducer = combineReducers({
  auth: authSlice,
  os: osSlice,
  sync: syncSlice,
  agendamento: agendamentoSlice,
  agenda: agendaSlice,
  offline: offlineSlice,
  notifications: notificationsSlice,
  analytics: analyticsSlice,
  erpSync: erpSyncSlice,
});

// Reducer persistido
const persistedReducer = persistReducer(persistConfig, rootReducer);

/**
 * Store Redux para Estado Global do App
 * Gerencia autenticação, OS, sincronização e offline com persistência
 */
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

// Configurando o persistor
export const persistor = persistStore(store);