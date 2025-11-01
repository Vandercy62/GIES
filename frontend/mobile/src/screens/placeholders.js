// Placeholder screens - will be implemented in detail later

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../../styles/theme';

export function AgendaDetailsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Detalhes do Agendamento</Text>
      <Text style={styles.subtitle}>Em desenvolvimento</Text>
    </View>
  );
}

export function ProfileScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Meu Perfil</Text>
      <Text style={styles.subtitle}>Em desenvolvimento</Text>
    </View>
  );
}

export function SettingsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Configurações</Text>
      <Text style={styles.subtitle}>Em desenvolvimento</Text>
    </View>
  );
}

export function OfflineScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Modo Offline</Text>
      <Text style={styles.subtitle}>Em desenvolvimento</Text>
    </View>
  );
}

export function CameraScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Câmera</Text>
      <Text style={styles.subtitle}>Em desenvolvimento</Text>
    </View>
  );
}

export function SignatureScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Assinatura</Text>
      <Text style={styles.subtitle}>Em desenvolvimento</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
});

// Export individual screens
export default {
  AgendaDetailsScreen,
  ProfileScreen,
  SettingsScreen,
  OfflineScreen,
  CameraScreen,
  SignatureScreen,
};