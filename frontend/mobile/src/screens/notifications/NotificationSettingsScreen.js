import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';

import {
  selectNotificationSettings,
  selectNotificationCategories,
  selectPushPermissionStatus,
  selectNotificationsLoading,
  updateSettings,
  updateCategory,
  registerForPushNotifications,
  getScheduledNotifications,
  cancelAllScheduledNotifications,
} from '../../store/slices/notificationsSlice';
import { theme } from '../../styles/theme';
import notificationService from '../../services/notificationService';

const REMINDER_OPTIONS = [
  { label: '5 minutos antes', value: 5 },
  { label: '15 minutos antes', value: 15 },
  { label: '30 minutos antes', value: 30 },
  { label: '1 hora antes', value: 60 },
  { label: '2 horas antes', value: 120 },
];

export default function NotificationSettingsScreen({ navigation }) {
  const dispatch = useDispatch();
  const settings = useSelector(selectNotificationSettings);
  const categories = useSelector(selectNotificationCategories);
  const pushPermissionStatus = useSelector(selectPushPermissionStatus);
  const loading = useSelector(selectNotificationsLoading);

  const [localSettings, setLocalSettings] = useState(settings);
  const [showReminderPicker, setShowReminderPicker] = useState(false);

  useEffect(() => {
    // Configurar header
    navigation.setOptions({
      title: 'Configurações de Notificações',
      headerRight: () => (
        <TouchableOpacity onPress={handleSave} disabled={loading}>
          <Icon 
            name="check" 
            size={24} 
            color={loading ? theme.colors.disabled : theme.colors.primary} 
          />
        </TouchableOpacity>
      ),
    });

    // Carregar notificações agendadas
    dispatch(getScheduledNotifications());
  }, [navigation, loading]);

  useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  const handleSave = async () => {
    try {
      await dispatch(updateSettings(localSettings)).unwrap();
      Alert.alert('Sucesso', 'Configurações salvas com sucesso');
      navigation.goBack();
    } catch (error) {
      Alert.alert('Erro', 'Falha ao salvar configurações');
    }
  };

  const handlePushToggle = async (enabled) => {
    if (enabled) {
      try {
        await dispatch(registerForPushNotifications()).unwrap();
        setLocalSettings(prev => ({ ...prev, pushEnabled: true }));
      } catch (error) {
        Alert.alert(
          'Erro',
          'Não foi possível ativar as notificações push. Verifique as permissões do app nas configurações do dispositivo.',
          [
            { text: 'OK' },
            { text: 'Abrir Configurações', onPress: () => Linking.openSettings() },
          ]
        );
      }
    } else {
      setLocalSettings(prev => ({ ...prev, pushEnabled: false }));
    }
  };

  const handleCategoryToggle = async (categoryId, field, value) => {
    const updatedCategory = { ...categories[categoryId], [field]: value };
    await dispatch(updateCategory({ categoryId, settings: updatedCategory }));
  };

  const handleQuietHoursToggle = (enabled) => {
    setLocalSettings(prev => ({
      ...prev,
      quietHours: { ...prev.quietHours, enabled }
    }));
  };

  const handleQuietHourChange = (field, value) => {
    setLocalSettings(prev => ({
      ...prev,
      quietHours: { ...prev.quietHours, [field]: value }
    }));
  };

  const handleTestNotification = async () => {
    try {
      await notificationService.scheduleLocalNotification({
        title: 'Notificação de Teste',
        body: 'Esta é uma notificação de teste do sistema',
        data: { type: 'test' },
        trigger: { seconds: 1 },
        priority: 'normal',
      });
      
      Alert.alert('Sucesso', 'Notificação de teste enviada');
    } catch (error) {
      Alert.alert('Erro', 'Falha ao enviar notificação de teste');
    }
  };

  const handleClearAllNotifications = async () => {
    Alert.alert(
      'Confirmar',
      'Tem certeza que deseja cancelar todas as notificações agendadas?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Confirmar',
          style: 'destructive',
          onPress: async () => {
            try {
              await dispatch(cancelAllScheduledNotifications()).unwrap();
              Alert.alert('Sucesso', 'Todas as notificações foram canceladas');
            } catch (error) {
              Alert.alert('Erro', 'Falha ao cancelar notificações');
            }
          },
        },
      ]
    );
  };

  const renderSettingItem = (title, description, value, onValueChange, disabled = false) => (
    <View style={[styles.settingItem, disabled && styles.settingItemDisabled]}>
      <View style={styles.settingContent}>
        <Text style={[styles.settingTitle, disabled && styles.settingTitleDisabled]}>
          {title}
        </Text>
        {description && (
          <Text style={[styles.settingDescription, disabled && styles.settingDescriptionDisabled]}>
            {description}
          </Text>
        )}
      </View>
      <Switch
        value={value}
        onValueChange={onValueChange}
        disabled={disabled}
        trackColor={{
          false: theme.colors.disabled,
          true: theme.colors.primary + '80',
        }}
        thumbColor={value ? theme.colors.primary : theme.colors.border}
      />
    </View>
  );

  const renderCategoryItem = (categoryId, category) => (
    <View key={categoryId} style={styles.categoryContainer}>
      <Text style={styles.categoryTitle}>{category.name}</Text>
      
      {renderSettingItem(
        'Ativado',
        'Receber notificações desta categoria',
        category.enabled,
        (value) => handleCategoryToggle(categoryId, 'enabled', value)
      )}
      
      {category.enabled && (
        <>
          {renderSettingItem(
            'Som',
            'Reproduzir som ao receber notificação',
            category.sound && localSettings.soundEnabled,
            (value) => handleCategoryToggle(categoryId, 'sound', value),
            !localSettings.soundEnabled
          )}
          
          {renderSettingItem(
            'Vibração',
            'Vibrar ao receber notificação',
            category.vibration && localSettings.vibrationEnabled,
            (value) => handleCategoryToggle(categoryId, 'vibration', value),
            !localSettings.vibrationEnabled
          )}
        </>
      )}
    </View>
  );

  const renderReminderOption = (option) => (
    <TouchableOpacity
      key={option.value}
      style={[
        styles.reminderOption,
        localSettings.reminderMinutes === option.value && styles.reminderOptionSelected
      ]}
      onPress={() => {
        setLocalSettings(prev => ({ ...prev, reminderMinutes: option.value }));
        setShowReminderPicker(false);
      }}
    >
      <Text style={[
        styles.reminderOptionText,
        localSettings.reminderMinutes === option.value && styles.reminderOptionTextSelected
      ]}>
        {option.label}
      </Text>
      {localSettings.reminderMinutes === option.value && (
        <Icon name="check" size={20} color={theme.colors.primary} />
      )}
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Carregando configurações...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Configurações Gerais */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Configurações Gerais</Text>
        
        {renderSettingItem(
          'Notificações Push',
          pushPermissionStatus === 'granted' 
            ? 'Notificações remotas do servidor'
            : 'Permissão necessária para notificações remotas',
          localSettings.pushEnabled && pushPermissionStatus === 'granted',
          handlePushToggle
        )}
        
        {renderSettingItem(
          'Som',
          'Reproduzir som nas notificações',
          localSettings.soundEnabled,
          (value) => setLocalSettings(prev => ({ ...prev, soundEnabled: value }))
        )}
        
        {renderSettingItem(
          'Vibração',
          'Vibrar ao receber notificações',
          localSettings.vibrationEnabled,
          (value) => setLocalSettings(prev => ({ ...prev, vibrationEnabled: value }))
        )}
      </View>

      {/* Lembretes de Agendamento */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Lembretes de Agendamento</Text>
        
        {renderSettingItem(
          'Lembretes Automáticos',
          'Enviar lembretes antes dos agendamentos',
          localSettings.appointmentReminders,
          (value) => setLocalSettings(prev => ({ ...prev, appointmentReminders: value }))
        )}
        
        {localSettings.appointmentReminders && (
          <TouchableOpacity
            style={styles.pickerButton}
            onPress={() => setShowReminderPicker(!showReminderPicker)}
          >
            <Text style={styles.pickerButtonLabel}>Tempo de Antecedência</Text>
            <View style={styles.pickerButtonValue}>
              <Text style={styles.pickerButtonText}>
                {REMINDER_OPTIONS.find(opt => opt.value === localSettings.reminderMinutes)?.label || '30 minutos antes'}
              </Text>
              <Icon 
                name={showReminderPicker ? "expand-less" : "expand-more"} 
                size={24} 
                color={theme.colors.textSecondary} 
              />
            </View>
          </TouchableOpacity>
        )}
        
        {showReminderPicker && (
          <View style={styles.reminderPicker}>
            {REMINDER_OPTIONS.map(renderReminderOption)}
          </View>
        )}
      </View>

      {/* Horário de Silêncio */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Horário de Silêncio</Text>
        
        {renderSettingItem(
          'Ativar Horário de Silêncio',
          'Silenciar notificações em horários específicos',
          localSettings.quietHours.enabled,
          handleQuietHoursToggle
        )}
        
        {localSettings.quietHours.enabled && (
          <>
            <View style={styles.timePickerContainer}>
              <Text style={styles.timePickerLabel}>Início</Text>
              <TouchableOpacity style={styles.timePickerButton}>
                <Text style={styles.timePickerText}>{localSettings.quietHours.start}</Text>
                <Icon name="schedule" size={20} color={theme.colors.textSecondary} />
              </TouchableOpacity>
            </View>
            
            <View style={styles.timePickerContainer}>
              <Text style={styles.timePickerLabel}>Fim</Text>
              <TouchableOpacity style={styles.timePickerButton}>
                <Text style={styles.timePickerText}>{localSettings.quietHours.end}</Text>
                <Icon name="schedule" size={20} color={theme.colors.textSecondary} />
              </TouchableOpacity>
            </View>
          </>
        )}
      </View>

      {/* Categorias de Notificação */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tipos de Notificação</Text>
        {Object.entries(categories).map(([categoryId, category]) =>
          renderCategoryItem(categoryId, category)
        )}
      </View>

      {/* Ações */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Ações</Text>
        
        <TouchableOpacity style={styles.actionButton} onPress={handleTestNotification}>
          <Icon name="notifications" size={24} color={theme.colors.primary} />
          <Text style={styles.actionButtonText}>Enviar Notificação de Teste</Text>
          <Icon name="chevron-right" size={20} color={theme.colors.textSecondary} />
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton} onPress={handleClearAllNotifications}>
          <Icon name="clear-all" size={24} color={theme.colors.error} />
          <Text style={[styles.actionButtonText, { color: theme.colors.error }]}>
            Cancelar Todas as Notificações
          </Text>
          <Icon name="chevron-right" size={20} color={theme.colors.textSecondary} />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: theme.colors.textSecondary,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 16,
    marginHorizontal: 16,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 16,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  settingItemDisabled: {
    opacity: 0.6,
  },
  settingContent: {
    flex: 1,
    marginRight: 16,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 4,
  },
  settingTitleDisabled: {
    color: theme.colors.disabled,
  },
  settingDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    lineHeight: 20,
  },
  settingDescriptionDisabled: {
    color: theme.colors.disabled,
  },
  categoryContainer: {
    marginBottom: 16,
  },
  categoryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: theme.colors.background,
  },
  pickerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 16,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  pickerButtonLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
  },
  pickerButtonValue: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  pickerButtonText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    marginRight: 8,
  },
  reminderPicker: {
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  reminderOption: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 32,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  reminderOptionSelected: {
    backgroundColor: theme.colors.primary + '10',
  },
  reminderOptionText: {
    fontSize: 16,
    color: theme.colors.text,
  },
  reminderOptionTextSelected: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  timePickerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  timePickerLabel: {
    fontSize: 16,
    color: theme.colors.text,
  },
  timePickerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: theme.colors.background,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  timePickerText: {
    fontSize: 16,
    color: theme.colors.text,
    marginRight: 8,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 16,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  actionButtonText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginLeft: 16,
  },
});