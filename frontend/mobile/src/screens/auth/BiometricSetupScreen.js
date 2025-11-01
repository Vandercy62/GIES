import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Switch,
  ScrollView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as LocalAuthentication from 'expo-local-authentication';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { theme } from '../../styles/theme';

export default function BiometricSetupScreen({ navigation }) {
  const [biometricType, setBiometricType] = useState('');
  const [isEnabled, setIsEnabled] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [isEnrolled, setIsEnrolled] = useState(false);

  useEffect(() => {
    checkBiometricCapabilities();
    loadCurrentSettings();
  }, []);

  const checkBiometricCapabilities = async () => {
    try {
      const compatible = await LocalAuthentication.hasHardwareAsync();
      const enrolled = await LocalAuthentication.isEnrolledAsync();
      const supportedTypes = await LocalAuthentication.supportedAuthenticationTypesAsync();

      setIsSupported(compatible);
      setIsEnrolled(enrolled);

      // Determinar tipo de biometria
      if (supportedTypes.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)) {
        setBiometricType('Face ID');
      } else if (supportedTypes.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
        setBiometricType('Touch ID');
      } else if (supportedTypes.includes(LocalAuthentication.AuthenticationType.IRIS)) {
        setBiometricType('Iris');
      } else {
        setBiometricType('Biometria');
      }
    } catch (error) {
      console.error('Erro ao verificar capacidades biométricas:', error);
    }
  };

  const loadCurrentSettings = async () => {
    try {
      const enabled = await AsyncStorage.getItem('@primotex:biometric_enabled');
      setIsEnabled(enabled === 'true');
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
    }
  };

  const handleBiometricToggle = async (value) => {
    if (value) {
      await enableBiometric();
    } else {
      await disableBiometric();
    }
  };

  const enableBiometric = async () => {
    try {
      // Verificar se há credenciais salvas
      const savedCredentials = await AsyncStorage.getItem('@primotex:saved_credentials');
      
      if (!savedCredentials) {
        Alert.alert(
          'Credenciais não encontradas',
          'Você precisa fazer login normalmente primeiro para configurar a biometria.',
          [
            {
              text: 'OK',
              onPress: () => navigation.navigate('Login'),
            },
          ]
        );
        return;
      }

      // Testar autenticação biométrica
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: `Configurar ${biometricType}`,
        fallbackLabel: 'Cancelar',
        cancelLabel: 'Cancelar',
      });

      if (result.success) {
        await AsyncStorage.setItem('@primotex:biometric_enabled', 'true');
        setIsEnabled(true);
        
        Alert.alert(
          'Sucesso!',
          `${biometricType} configurado com sucesso. Agora você pode usar sua biometria para fazer login.`,
          [
            {
              text: 'OK',
              onPress: () => navigation.goBack(),
            },
          ]
        );
      } else {
        Alert.alert('Erro', 'Não foi possível configurar a biometria.');
      }
    } catch (error) {
      console.error('Erro ao habilitar biometria:', error);
      Alert.alert('Erro', 'Falha ao configurar biometria.');
    }
  };

  const disableBiometric = async () => {
    try {
      await AsyncStorage.setItem('@primotex:biometric_enabled', 'false');
      setIsEnabled(false);
      
      Alert.alert(
        'Biometria desabilitada',
        'A autenticação biométrica foi desabilitada. Você pode reativá-la a qualquer momento.',
      );
    } catch (error) {
      console.error('Erro ao desabilitar biometria:', error);
      Alert.alert('Erro', 'Falha ao desabilitar biometria.');
    }
  };

  const testBiometric = async () => {
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: `Testar ${biometricType}`,
        fallbackLabel: 'Cancelar',
        cancelLabel: 'Cancelar',
      });

      if (result.success) {
        Alert.alert('Sucesso!', `${biometricType} está funcionando corretamente.`);
      } else {
        Alert.alert('Falha', 'Não foi possível autenticar com biometria.');
      }
    } catch (error) {
      console.error('Erro ao testar biometria:', error);
      Alert.alert('Erro', 'Falha no teste de biometria.');
    }
  };

  const clearBiometricData = async () => {
    Alert.alert(
      'Limpar dados biométricos',
      'Isso irá remover todas as configurações biométricas salvas. Deseja continuar?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Limpar',
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.removeItem('@primotex:biometric_enabled');
              await AsyncStorage.removeItem('@primotex:saved_credentials');
              setIsEnabled(false);
              Alert.alert('Sucesso', 'Dados biométricos removidos.');
            } catch (error) {
              console.error('Erro ao limpar dados:', error);
              Alert.alert('Erro', 'Falha ao limpar dados biométricos.');
            }
          },
        },
      ]
    );
  };

  const getStatusIcon = () => {
    if (!isSupported) return { name: 'block', color: theme.colors.error };
    if (!isEnrolled) return { name: 'warning', color: theme.colors.warning };
    if (isEnabled) return { name: 'check-circle', color: theme.colors.success };
    return { name: 'radio-button-unchecked', color: theme.colors.textSecondary };
  };

  const getStatusText = () => {
    if (!isSupported) return 'Não suportado neste dispositivo';
    if (!isEnrolled) return 'Nenhuma biometria cadastrada no dispositivo';
    if (isEnabled) return 'Configurado e ativo';
    return 'Disponível para configuração';
  };

  const statusIcon = getStatusIcon();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.iconContainer}>
          <Icon name="fingerprint" size={48} color={theme.colors.primary} />
        </View>
        <Text style={styles.title}>Configurar {biometricType}</Text>
        <Text style={styles.subtitle}>
          Configure a autenticação biométrica para acessar o app de forma rápida e segura
        </Text>
      </View>

      {/* Status */}
      <View style={styles.statusContainer}>
        <View style={styles.statusRow}>
          <Icon name={statusIcon.name} size={24} color={statusIcon.color} />
          <Text style={styles.statusText}>{getStatusText()}</Text>
        </View>
      </View>

      {/* Configurações */}
      {isSupported && isEnrolled && (
        <View style={styles.settingsContainer}>
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingTitle}>Ativar {biometricType}</Text>
              <Text style={styles.settingDescription}>
                Permite fazer login usando sua biometria
              </Text>
            </View>
            <Switch
              value={isEnabled}
              onValueChange={handleBiometricToggle}
              trackColor={{
                false: theme.colors.disabled,
                true: theme.colors.primary + '40',
              }}
              thumbColor={isEnabled ? theme.colors.primary : theme.colors.surface}
            />
          </View>
        </View>
      )}

      {/* Ações */}
      <View style={styles.actionsContainer}>
        {isSupported && isEnrolled && isEnabled && (
          <TouchableOpacity style={styles.actionButton} onPress={testBiometric}>
            <Icon name="play-arrow" size={20} color={theme.colors.primary} />
            <Text style={styles.actionButtonText}>Testar {biometricType}</Text>
          </TouchableOpacity>
        )}

        {isEnabled && (
          <TouchableOpacity
            style={[styles.actionButton, styles.dangerButton]}
            onPress={clearBiometricData}
          >
            <Icon name="delete" size={20} color={theme.colors.error} />
            <Text style={[styles.actionButtonText, styles.dangerText]}>
              Limpar dados biométricos
            </Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Informações */}
      <View style={styles.infoContainer}>
        <Text style={styles.infoTitle}>Informações importantes:</Text>
        <Text style={styles.infoText}>
          • Suas credenciais são armazenadas de forma segura no dispositivo
        </Text>
        <Text style={styles.infoText}>
          • A biometria é usada apenas para desbloqueio rápido
        </Text>
        <Text style={styles.infoText}>
          • Você sempre pode usar sua senha normal
        </Text>
        <Text style={styles.infoText}>
          • Os dados biométricos nunca são enviados para nossos servidores
        </Text>
      </View>

      {/* Requisitos */}
      {!isSupported || !isEnrolled ? (
        <View style={styles.requirementsContainer}>
          <Text style={styles.requirementsTitle}>Requisitos:</Text>
          
          <View style={styles.requirementRow}>
            <Icon
              name={isSupported ? 'check' : 'close'}
              size={16}
              color={isSupported ? theme.colors.success : theme.colors.error}
            />
            <Text style={styles.requirementText}>
              Dispositivo com sensor biométrico
            </Text>
          </View>
          
          <View style={styles.requirementRow}>
            <Icon
              name={isEnrolled ? 'check' : 'close'}
              size={16}
              color={isEnrolled ? theme.colors.success : theme.colors.error}
            />
            <Text style={styles.requirementText}>
              Biometria cadastrada nas configurações do dispositivo
            </Text>
          </View>

          {!isEnrolled && (
            <Text style={styles.helpText}>
              Para cadastrar sua biometria, vá em Configurações {'>'} Segurança {'>'} {biometricType}
            </Text>
          )}
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    padding: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
  },
  iconContainer: {
    width: 80,
    height: 80,
    backgroundColor: theme.colors.primary + '20',
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
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
    lineHeight: 24,
  },
  statusContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusText: {
    fontSize: 16,
    color: theme.colors.text,
    marginLeft: 12,
    flex: 1,
  },
  settingsContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    marginBottom: 24,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
  },
  settingInfo: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  actionsContainer: {
    marginBottom: 24,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  dangerButton: {
    backgroundColor: theme.colors.errorBackground,
  },
  actionButtonText: {
    fontSize: 16,
    color: theme.colors.primary,
    marginLeft: 12,
    fontWeight: '500',
  },
  dangerText: {
    color: theme.colors.error,
  },
  infoContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 12,
  },
  infoText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 8,
    lineHeight: 20,
  },
  requirementsContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
  },
  requirementsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 12,
  },
  requirementRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  requirementText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginLeft: 8,
    flex: 1,
  },
  helpText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: 12,
    fontStyle: 'italic',
    lineHeight: 20,
  },
});