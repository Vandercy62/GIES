import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { selectUser, logout } from '../../store/slices/authSlice';
import { selectUnreadCount } from '../../store/slices/notificationsSlice';
import { theme } from '../../styles/theme';

/**
 * Tela de Configurações do App
 */
export default function SettingsScreen({ navigation }) {
  const dispatch = useDispatch();
  const user = useSelector(selectUser);
  const unreadNotifications = useSelector(selectUnreadCount);

  const handleLogout = () => {
    Alert.alert(
      'Sair do Aplicativo',
      'Tem certeza que deseja sair? Dados não sincronizados podem ser perdidos.',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Sair',
          style: 'destructive',
          onPress: () => dispatch(logout()),
        },
      ]
    );
  };

  const settingsOptions = [
    {
      id: 'notifications',
      title: 'Notificações',
      description: 'Configure alertas e lembretes',
      icon: 'notifications',
      badge: unreadNotifications,
      onPress: () => navigation.navigate('NotificationSettings'),
    },
    {
      id: 'profile',
      title: 'Meu Perfil',
      description: 'Informações pessoais',
      icon: 'person',
      onPress: () => {
        Alert.alert('Em Desenvolvimento', 'Esta funcionalidade está sendo desenvolvida.');
      },
    },
    {
      id: 'offline',
      title: 'Dados Offline',
      description: 'Gerenciar sincronização',
      icon: 'cloud-sync',
      onPress: () => navigation.navigate('Offline'),
    },
    {
      id: 'security',
      title: 'Segurança',
      description: 'Biometria e senhas',
      icon: 'security',
      onPress: () => {
        Alert.alert('Em Desenvolvimento', 'Esta funcionalidade está sendo desenvolvida.');
      },
    },
    {
      id: 'about',
      title: 'Sobre o App',
      description: 'Versão e informações',
      icon: 'info',
      onPress: () => {
        Alert.alert(
          'Primotex ERP Mobile',
          'Versão 1.0.0\nDesenvolvido para técnicos em campo\n\n© 2024 Primotex - Forros e Divisórias'
        );
      },
    },
  ];

  const renderSettingItem = (option) => (
    <TouchableOpacity
      key={option.id}
      style={styles.settingItem}
      onPress={option.onPress}
      activeOpacity={0.7}
    >
      <View style={styles.settingIcon}>
        <Icon name={option.icon} size={24} color={theme.colors.primary} />
        {option.badge > 0 && (
          <View style={styles.settingBadge}>
            <Text style={styles.settingBadgeText}>
              {option.badge > 99 ? '99+' : option.badge}
            </Text>
          </View>
        )}
      </View>
      
      <View style={styles.settingContent}>
        <Text style={styles.settingTitle}>{option.title}</Text>
        <Text style={styles.settingDescription}>{option.description}</Text>
      </View>
      
      <View style={styles.settingArrow}>
        <Icon name="chevron-right" size={24} color={theme.colors.disabled} />
      </View>
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header do Usuário */}
      <View style={styles.userHeader}>
        <View style={styles.userAvatar}>
          <Icon name="person" size={32} color="#FFFFFF" />
        </View>
        <View style={styles.userInfo}>
          <Text style={styles.userName}>{user?.name || 'Usuário'}</Text>
          <Text style={styles.userRole}>{user?.role || 'Técnico'}</Text>
          <Text style={styles.userEmail}>{user?.email || ''}</Text>
        </View>
      </View>

      {/* Opções de Configuração */}
      <View style={styles.settingsSection}>
        <Text style={styles.sectionTitle}>Configurações</Text>
        {settingsOptions.map(renderSettingItem)}
      </View>

      {/* Seção de Ações */}
      <View style={styles.actionsSection}>
        <Text style={styles.sectionTitle}>Ações</Text>
        
        <TouchableOpacity
          style={[styles.settingItem, styles.actionItem]}
          onPress={handleLogout}
          activeOpacity={0.7}
        >
          <View style={styles.settingIcon}>
            <Icon name="logout" size={24} color={theme.colors.error} />
          </View>
          <View style={styles.settingContent}>
            <Text style={[styles.settingTitle, { color: theme.colors.error }]}>
              Sair do Aplicativo
            </Text>
            <Text style={styles.settingDescription}>
              Fazer logout e voltar à tela de login
            </Text>
          </View>
        </TouchableOpacity>
      </View>

      {/* Rodapé */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Primotex ERP Mobile v1.0.0
        </Text>
        <Text style={styles.footerText}>
          © 2024 Primotex - Forros e Divisórias
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  userHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 24,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  userAvatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: theme.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 4,
  },
  userRole: {
    fontSize: 16,
    color: theme.colors.primary,
    fontWeight: '600',
    marginBottom: 2,
  },
  userEmail: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  settingsSection: {
    marginTop: 24,
  },
  actionsSection: {
    marginTop: 32,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 16,
    marginHorizontal: 24,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 16,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  actionItem: {
    backgroundColor: theme.colors.surface,
  },
  settingIcon: {
    position: 'relative',
    marginRight: 16,
  },
  settingBadge: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: theme.colors.error,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  settingBadgeText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  settingArrow: {
    marginLeft: 8,
  },
  footer: {
    alignItems: 'center',
    padding: 32,
    marginTop: 32,
  },
  footerText: {
    fontSize: 12,
    color: theme.colors.disabled,
    textAlign: 'center',
    marginBottom: 4,
  },
});