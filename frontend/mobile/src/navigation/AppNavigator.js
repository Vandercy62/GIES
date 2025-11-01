import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useSelector } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { selectIsAuthenticated } from '../store/slices/authSlice';
import { theme } from '../styles/theme';

// Screens
import LoginScreen from '../screens/auth/LoginScreen';
import BiometricSetupScreen from '../screens/auth/BiometricSetupScreen';

import DashboardScreen from '../screens/dashboard/DashboardScreen';
import OSListScreen from '../screens/os/OSListScreen';
import OSDetailsScreen from '../screens/os/OSDetailsScreen';
import OSExecutionScreen from '../screens/os/OSExecutionScreen';

import AgendaScreen from '../screens/agenda/AgendaScreen';
import CreateAppointmentScreen from '../screens/agenda/CreateAppointmentScreen';
import AppointmentDetailsScreen from '../screens/agenda/AppointmentDetailsScreen';

import NotificationsScreen from '../screens/notifications/NotificationsScreen';
import NotificationSettingsScreen from '../screens/notifications/NotificationSettingsScreen';

import AnalyticsScreen from '../screens/analytics/AnalyticsScreen';
import ReportsManagerScreen from '../screens/analytics/ReportsManagerScreen';
import AnalyticsSettingsScreen from '../screens/analytics/AnalyticsSettingsScreen';

import SettingsScreen from '../screens/settings/SettingsScreen';

// Placeholder screens
import {
  ProfileScreen,
  OfflineScreen,
  CameraScreen,
  SignatureScreen,
} from '../screens/placeholders';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

/**
 * Navegação por Tabs - Telas Principais
 */
function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'OS':
              iconName = 'work';
              break;
            case 'Agenda':
              iconName = 'event';
              break;
            case 'Perfil':
              iconName = 'person';
              break;
            default:
              iconName = 'help';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textSecondary,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopColor: theme.colors.disabled,
          paddingBottom: 5,
          paddingTop: 5,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          title: 'Início',
          tabBarLabel: 'Início',
        }}
      />
      <Tab.Screen
        name="OS"
        component={OSListScreen}
        options={{
          title: 'Ordens de Serviço',
          tabBarLabel: 'OS',
        }}
      />
      <Tab.Screen
        name="Agenda"
        component={AgendaScreen}
        options={{
          title: 'Minha Agenda',
          tabBarLabel: 'Agenda',
        }}
      />
      <Tab.Screen
        name="Perfil"
        component={ProfileScreen}
        options={{
          title: 'Meu Perfil',
          tabBarLabel: 'Perfil',
        }}
      />
    </Tab.Navigator>
  );
}

/**
 * Navegação Stack - Autenticação
 */
function AuthNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen
        name="Login"
        component={LoginScreen}
        options={{
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="BiometricSetup"
        component={BiometricSetupScreen}
        options={{
          title: 'Configurar Biometria',
          headerBackTitle: 'Voltar',
        }}
      />
    </Stack.Navigator>
  );
}

/**
 * Navegação Stack - App Principal
 */
function AppNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      {/* Tabs principais */}
      <Stack.Screen
        name="MainTabs"
        component={MainTabNavigator}
        options={{
          headerShown: false,
        }}
      />

      {/* Telas de OS */}
      <Stack.Screen
        name="OSDetails"
        component={OSDetailsScreen}
        options={{
          title: 'Detalhes da OS',
          headerBackTitle: 'Voltar',
        }}
      />
      <Stack.Screen
        name="OSExecution"
        component={OSExecutionScreen}
        options={{
          title: 'Executando OS',
          headerBackTitle: 'Voltar',
        }}
      />

      {/* Telas de Agenda */}
      <Stack.Screen
        name="CreateAppointment"
        component={CreateAppointmentScreen}
        options={{
          title: 'Novo Agendamento',
          headerBackTitle: 'Voltar',
        }}
      />
      <Stack.Screen
        name="AgendaDetails"
        component={AppointmentDetailsScreen}
        options={{
          title: 'Detalhes do Agendamento',
          headerBackTitle: 'Voltar',
        }}
      />

      {/* Telas de Notificações */}
      <Stack.Screen
        name="Notifications"
        component={NotificationsScreen}
        options={{
          title: 'Notificações',
          headerBackTitle: 'Voltar',
        }}
      />
      <Stack.Screen
        name="NotificationSettings"
        component={NotificationSettingsScreen}
        options={{
          title: 'Configurações de Notificação',
          headerBackTitle: 'Voltar',
        }}
      />

      {/* Telas de Analytics e Relatórios */}
      <Stack.Screen
        name="Analytics"
        component={AnalyticsScreen}
        options={{
          title: 'Analytics & Relatórios',
          headerBackTitle: 'Voltar',
        }}
      />
      <Stack.Screen
        name="ReportsManager"
        component={ReportsManagerScreen}
        options={{
          title: 'Gerenciar Relatórios',
          headerBackTitle: 'Voltar',
        }}
      />
      <Stack.Screen
        name="AnalyticsSettings"
        component={AnalyticsSettingsScreen}
        options={{
          title: 'Configurações Analytics',
          headerBackTitle: 'Voltar',
        }}
      />

      {/* Telas de Configurações */}
      <Stack.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          title: 'Configurações',
          headerBackTitle: 'Voltar',
        }}
      />
      <Stack.Screen
        name="Offline"
        component={OfflineScreen}
        options={{
          title: 'Modo Offline',
          headerBackTitle: 'Voltar',
        }}
      />

      {/* Telas de Câmera e Assinatura */}
      <Stack.Screen
        name="Camera"
        component={CameraScreen}
        options={{
          title: 'Tirar Foto',
          headerBackTitle: 'Voltar',
        }}
      />
      <Stack.Screen
        name="Signature"
        component={SignatureScreen}
        options={{
          title: 'Assinatura do Cliente',
          headerBackTitle: 'Voltar',
        }}
      />
    </Stack.Navigator>
  );
}

/**
 * Navegador Principal - Decide entre Auth ou App
 */
export default function RootNavigator() {
  const isAuthenticated = useSelector(selectIsAuthenticated);

  return isAuthenticated ? <AppNavigator /> : <AuthNavigator />;
}