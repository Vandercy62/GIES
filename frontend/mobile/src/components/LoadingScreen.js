import React from 'react';
import {
  View,
  Text,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { theme } from '../styles/theme';

export default function LoadingScreen({ message = 'Carregando...' }) {
  return (
    <View style={styles.container}>
      <View style={styles.content}>
        {/* Logo Placeholder */}
        <View style={styles.logoContainer}>
          <View style={styles.logo}>
            <Text style={styles.logoText}>PRIMOTEX</Text>
            <Text style={styles.logoSubtext}>ERP Mobile</Text>
          </View>
        </View>

        {/* Loading Indicator */}
        <ActivityIndicator
          size="large"
          color={theme.colors.primary}
          style={styles.spinner}
        />

        {/* Mensagem */}
        <Text style={styles.message}>{message}</Text>

        {/* Versão */}
        <Text style={styles.version}>v4.0.0 Mobile</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  logoContainer: {
    marginBottom: 48,
  },
  logo: {
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
  spinner: {
    marginBottom: 24,
  },
  message: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: 32,
  },
  version: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    opacity: 0.7,
  },
});