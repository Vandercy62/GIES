import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { theme } from '../../styles/theme';

/**
 * Tela placeholder para funcionalidades ainda não implementadas
 */
const PlaceholderScreen = ({ title, description, icon = 'construction' }) => (
  <View style={styles.container}>
    <Icon name={icon} size={64} color={theme.colors.disabled} />
    <Text style={styles.title}>{title}</Text>
    <Text style={styles.description}>{description}</Text>
    <TouchableOpacity style={styles.button} onPress={() => {}}>
      <Text style={styles.buttonText}>Em Desenvolvimento</Text>
    </TouchableOpacity>
  </View>
);

// Screens placeholder
export const ProfileScreen = ({ navigation }) => (
  <PlaceholderScreen
    title="Meu Perfil"
    description="Visualize e edite suas informações pessoais"
    icon="person"
  />
);

export const SettingsScreen = ({ navigation }) => (
  <PlaceholderScreen
    title="Configurações"
    description="Configure as preferências do aplicativo"
    icon="settings"
  />
);

export const OfflineScreen = ({ navigation }) => (
  <PlaceholderScreen
    title="Modo Offline"
    description="Gerencie dados offline e sincronização"
    icon="cloud-off"
  />
);

export const CameraScreen = ({ navigation }) => (
  <PlaceholderScreen
    title="Câmera"
    description="Capture fotos para anexar às OS"
    icon="camera-alt"
  />
);

export const SignatureScreen = ({ navigation }) => (
  <PlaceholderScreen
    title="Assinatura Digital"
    description="Colete assinaturas dos clientes"
    icon="draw"
  />
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
    backgroundColor: theme.colors.background,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  description: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: 32,
    lineHeight: 24,
  },
  button: {
    backgroundColor: theme.colors.disabled,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
});