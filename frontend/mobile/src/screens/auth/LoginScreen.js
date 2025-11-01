import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Image,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as LocalAuthentication from 'expo-local-authentication';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { login, selectAuthStatus, selectAuthError } from '../../store/slices/authSlice';
import { theme } from '../../styles/theme';

export default function LoginScreen({ navigation }) {
  const dispatch = useDispatch();
  const authStatus = useSelector(selectAuthStatus);
  const authError = useSelector(selectAuthError);

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [biometricSupported, setBiometricSupported] = useState(false);

  // Verificar suporte à biometria
  useEffect(() => {
    checkBiometricSupport();
    checkBiometricEnabled();
  }, []);

  const checkBiometricSupport = async () => {
    try {
      const compatible = await LocalAuthentication.hasHardwareAsync();
      const enrolled = await LocalAuthentication.isEnrolledAsync();
      setBiometricSupported(compatible && enrolled);
    } catch (error) {
      console.error('Erro ao verificar biometria:', error);
    }
  };

  const checkBiometricEnabled = async () => {
    try {
      const enabled = await AsyncStorage.getItem('@primotex:biometric_enabled');
      setBiometricEnabled(enabled === 'true');
    } catch (error) {
      console.error('Erro ao verificar configuração biométrica:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleLogin = async () => {
    if (!formData.username.trim() || !formData.password.trim()) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos.');
      return;
    }

    try {
      const result = await dispatch(login(formData)).unwrap();
      
      if (result.success) {
        // Salvar credenciais se biometria estiver habilitada
        if (biometricEnabled) {
          await AsyncStorage.setItem('@primotex:saved_credentials', JSON.stringify(formData));
        }
      }
    } catch (error) {
      Alert.alert('Erro', error.message || 'Falha na autenticação');
    }
  };

  const handleBiometricLogin = async () => {
    try {
      // Verificar se há credenciais salvas
      const savedCredentials = await AsyncStorage.getItem('@primotex:saved_credentials');
      if (!savedCredentials) {
        Alert.alert(
          'Biometria não configurada',
          'Configure primeiro o login biométrico em Configurações.',
          [
            { text: 'Cancelar', style: 'cancel' },
            { text: 'Configurar', onPress: () => navigation.navigate('BiometricSetup') },
          ]
        );
        return;
      }

      // Autenticar com biometria
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Autenticar com biometria',
        fallbackLabel: 'Usar senha',
        cancelLabel: 'Cancelar',
      });

      if (result.success) {
        const credentials = JSON.parse(savedCredentials);
        setFormData(credentials);
        dispatch(login(credentials));
      }
    } catch (error) {
      console.error('Erro na autenticação biométrica:', error);
      Alert.alert('Erro', 'Falha na autenticação biométrica');
    }
  };

  const isLoading = authStatus === 'loading';

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.content}>
        {/* Logo */}
        <View style={styles.logoContainer}>
          <View style={styles.logoPlaceholder}>
            <Text style={styles.logoText}>PRIMOTEX</Text>
            <Text style={styles.logoSubtext}>ERP Mobile</Text>
          </View>
        </View>

        {/* Formulário */}
        <View style={styles.formContainer}>
          <Text style={styles.title}>Bem-vindo de volta!</Text>
          <Text style={styles.subtitle}>Faça login para continuar</Text>

          {/* Campo Usuário */}
          <View style={styles.inputContainer}>
            <Icon name="person" size={20} color={theme.colors.textSecondary} style={styles.inputIcon} />
            <TextInput
              style={styles.input}
              placeholder="Usuário"
              placeholderTextColor={theme.colors.textSecondary}
              value={formData.username}
              onChangeText={(value) => handleInputChange('username', value)}
              autoCapitalize="none"
              autoCorrect={false}
              editable={!isLoading}
            />
          </View>

          {/* Campo Senha */}
          <View style={styles.inputContainer}>
            <Icon name="lock" size={20} color={theme.colors.textSecondary} style={styles.inputIcon} />
            <TextInput
              style={[styles.input, styles.passwordInput]}
              placeholder="Senha"
              placeholderTextColor={theme.colors.textSecondary}
              value={formData.password}
              onChangeText={(value) => handleInputChange('password', value)}
              secureTextEntry={!showPassword}
              autoCapitalize="none"
              autoCorrect={false}
              editable={!isLoading}
            />
            <TouchableOpacity
              style={styles.passwordToggle}
              onPress={() => setShowPassword(!showPassword)}
              disabled={isLoading}
            >
              <Icon
                name={showPassword ? 'visibility-off' : 'visibility'}
                size={20}
                color={theme.colors.textSecondary}
              />
            </TouchableOpacity>
          </View>

          {/* Erro */}
          {authError && (
            <View style={styles.errorContainer}>
              <Icon name="error" size={16} color={theme.colors.error} />
              <Text style={styles.errorText}>{authError}</Text>
            </View>
          )}

          {/* Botão Login */}
          <TouchableOpacity
            style={[styles.loginButton, isLoading && styles.buttonDisabled]}
            onPress={handleLogin}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="#FFFFFF" size="small" />
            ) : (
              <Text style={styles.loginButtonText}>Entrar</Text>
            )}
          </TouchableOpacity>

          {/* Login Biométrico */}
          {biometricSupported && biometricEnabled && (
            <TouchableOpacity
              style={styles.biometricButton}
              onPress={handleBiometricLogin}
              disabled={isLoading}
            >
              <Icon name="fingerprint" size={24} color={theme.colors.primary} />
              <Text style={styles.biometricText}>Entrar com biometria</Text>
            </TouchableOpacity>
          )}

          {/* Link Configurar Biometria */}
          {biometricSupported && !biometricEnabled && (
            <TouchableOpacity
              style={styles.linkButton}
              onPress={() => navigation.navigate('BiometricSetup')}
              disabled={isLoading}
            >
              <Text style={styles.linkText}>Configurar login biométrico</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Rodapé */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Primotex - Forros e Divisórias Eirelli
          </Text>
          <Text style={styles.versionText}>v4.0.0 Mobile</Text>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    justifyContent: 'center',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoPlaceholder: {
    width: 120,
    height: 120,
    backgroundColor: theme.colors.primary,
    borderRadius: 60,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  logoSubtext: {
    fontSize: 12,
    color: '#FFFFFF',
    marginTop: 4,
  },
  formContainer: {
    marginBottom: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: theme.colors.text,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: 32,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.colors.disabled,
    marginBottom: 16,
    paddingHorizontal: 16,
    height: 56,
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: theme.colors.text,
  },
  passwordInput: {
    paddingRight: 40,
  },
  passwordToggle: {
    position: 'absolute',
    right: 16,
    padding: 4,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.errorBackground,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorText: {
    color: theme.colors.error,
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  loginButton: {
    backgroundColor: theme.colors.primary,
    height: 56,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  loginButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  biometricButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.colors.surface,
    height: 56,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.colors.primary,
    marginBottom: 16,
  },
  biometricText: {
    color: theme.colors.primary,
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  linkButton: {
    alignItems: 'center',
    padding: 12,
  },
  linkText: {
    color: theme.colors.primary,
    fontSize: 14,
    fontWeight: '500',
  },
  footer: {
    alignItems: 'center',
  },
  footerText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  versionText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginTop: 4,
  },
});