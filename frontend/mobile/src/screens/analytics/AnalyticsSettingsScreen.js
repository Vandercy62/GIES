import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Slider from '@react-native-community/slider';

import {
  selectAnalyticsSettings,
  updateSettings,
  clearReports,
  clearExports,
  resetAnalytics,
} from '../../store/slices/analyticsSlice';
import { theme } from '../../styles/theme';

/**
 * Configurações de Analytics e Relatórios
 */
export default function AnalyticsSettingsScreen({ navigation }) {
  const dispatch = useDispatch();
  const settings = useSelector(selectAnalyticsSettings);

  const [localSettings, setLocalSettings] = useState(settings);

  const periodOptions = [
    { key: '7d', label: '7 dias' },
    { key: '30d', label: '30 dias' },
    { key: '90d', label: '90 dias' },
  ];

  const refreshIntervals = [
    { key: 60000, label: '1 minuto' },
    { key: 300000, label: '5 minutos' },
    { key: 600000, label: '10 minutos' },
    { key: 1800000, label: '30 minutos' },
    { key: 3600000, label: '1 hora' },
  ];

  const handleSaveSettings = () => {
    dispatch(updateSettings(localSettings));
    Alert.alert('Sucesso', 'Configurações salvas com sucesso!');
    navigation.goBack();
  };

  const handleResetToDefaults = () => {
    Alert.alert(
      'Restaurar Padrões',
      'Tem certeza que deseja restaurar as configurações padrão?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Restaurar',
          onPress: () => {
            const defaultSettings = {
              defaultPeriod: '30d',
              autoRefresh: true,
              refreshInterval: 300000,
              chartAnimations: true,
              includeChartsInReports: true,
            };
            setLocalSettings(defaultSettings);
            dispatch(updateSettings(defaultSettings));
          },
        },
      ]
    );
  };

  const handleClearAllData = () => {
    Alert.alert(
      'Limpar Todos os Dados',
      'Esta ação irá excluir todos os relatórios, exportações e dados de analytics. Esta ação não pode ser desfeita.',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Limpar Tudo',
          style: 'destructive',
          onPress: () => {
            dispatch(clearReports());
            dispatch(clearExports());
            dispatch(resetAnalytics());
            Alert.alert('Concluído', 'Todos os dados foram limpos.');
          },
        },
      ]
    );
  };

  const getRefreshIntervalLabel = (interval) => {
    const option = refreshIntervals.find(opt => opt.key === interval);
    return option ? option.label : '5 minutos';
  };

  const renderSection = (title, children) => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );

  const renderSettingRow = (title, description, children) => (
    <View style={styles.settingRow}>
      <View style={styles.settingInfo}>
        <Text style={styles.settingTitle}>{title}</Text>
        {description && (
          <Text style={styles.settingDescription}>{description}</Text>
        )}
      </View>
      <View style={styles.settingControl}>
        {children}
      </View>
    </View>
  );

  const renderSwitchRow = (title, description, value, onValueChange) => 
    renderSettingRow(
      title,
      description,
      <Switch
        value={value}
        onValueChange={onValueChange}
        thumbColor={value ? theme.colors.primary : theme.colors.disabled}
        trackColor={{ false: theme.colors.border, true: theme.colors.primary + '40' }}
      />
    );

  const renderPeriodSelector = () => (
    <View style={styles.periodContainer}>
      {periodOptions.map((period) => (
        <TouchableOpacity
          key={period.key}
          style={[
            styles.periodOption,
            localSettings.defaultPeriod === period.key && styles.periodOptionActive,
          ]}
          onPress={() => setLocalSettings(prev => ({ ...prev, defaultPeriod: period.key }))}
        >
          <Text style={[
            styles.periodOptionText,
            localSettings.defaultPeriod === period.key && styles.periodOptionTextActive,
          ]}>
            {period.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderRefreshIntervalSlider = () => (
    <View style={styles.sliderContainer}>
      <Slider
        style={styles.slider}
        minimumValue={0}
        maximumValue={refreshIntervals.length - 1}
        step={1}
        value={refreshIntervals.findIndex(opt => opt.key === localSettings.refreshInterval)}
        onValueChange={(value) => {
          const interval = refreshIntervals[Math.round(value)]?.key || 300000;
          setLocalSettings(prev => ({ ...prev, refreshInterval: interval }));
        }}
        minimumTrackTintColor={theme.colors.primary}
        maximumTrackTintColor={theme.colors.border}
        thumbStyle={{ backgroundColor: theme.colors.primary }}
      />
      <Text style={styles.sliderLabel}>
        {getRefreshIntervalLabel(localSettings.refreshInterval)}
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {renderSection(
          'Configurações Gerais',
          <>
            {renderSettingRow(
              'Período Padrão',
              'Período padrão para visualização de dados',
              renderPeriodSelector()
            )}
            
            {renderSwitchRow(
              'Atualização Automática',
              'Atualizar dados automaticamente em intervalos regulares',
              localSettings.autoRefresh,
              (value) => setLocalSettings(prev => ({ ...prev, autoRefresh: value }))
            )}
            
            {localSettings.autoRefresh && renderSettingRow(
              'Intervalo de Atualização',
              'Frequência de atualização automática dos dados',
              renderRefreshIntervalSlider()
            )}
          </>
        )}

        {renderSection(
          'Visualização',
          <>
            {renderSwitchRow(
              'Animações nos Gráficos',
              'Habilitar animações suaves nos gráficos e transições',
              localSettings.chartAnimations,
              (value) => setLocalSettings(prev => ({ ...prev, chartAnimations: value }))
            )}
          </>
        )}

        {renderSection(
          'Relatórios',
          <>
            {renderSwitchRow(
              'Incluir Gráficos por Padrão',
              'Incluir gráficos automaticamente ao gerar relatórios',
              localSettings.includeChartsInReports,
              (value) => setLocalSettings(prev => ({ ...prev, includeChartsInReports: value }))
            )}
          </>
        )}

        {renderSection(
          'Ações de Dados',
          <>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={handleClearAllData}
            >
              <Icon name="delete-forever" size={24} color={theme.colors.error} />
              <View style={styles.actionButtonContent}>
                <Text style={[styles.actionButtonTitle, { color: theme.colors.error }]}>
                  Limpar Todos os Dados
                </Text>
                <Text style={styles.actionButtonDescription}>
                  Excluir relatórios, exportações e dados de analytics
                </Text>
              </View>
              <Icon name="chevron-right" size={24} color={theme.colors.disabled} />
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.actionButton}
              onPress={handleResetToDefaults}
            >
              <Icon name="settings-backup-restore" size={24} color={theme.colors.warning} />
              <View style={styles.actionButtonContent}>
                <Text style={[styles.actionButtonTitle, { color: theme.colors.warning }]}>
                  Restaurar Padrões
                </Text>
                <Text style={styles.actionButtonDescription}>
                  Voltar às configurações originais do sistema
                </Text>
              </View>
              <Icon name="chevron-right" size={24} color={theme.colors.disabled} />
            </TouchableOpacity>
          </>
        )}

        {renderSection(
          'Informações',
          <>
            <View style={styles.infoContainer}>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Versão do Analytics:</Text>
                <Text style={styles.infoValue}>1.0.0</Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Última Atualização:</Text>
                <Text style={styles.infoValue}>
                  {new Date().toLocaleDateString('pt-BR')}
                </Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Cache de Dados:</Text>
                <Text style={styles.infoValue}>Habilitado</Text>
              </View>
            </View>
          </>
        )}
      </ScrollView>

      {/* Botão de Salvar */}
      <View style={styles.footer}>
        <TouchableOpacity
          style={styles.saveButton}
          onPress={handleSaveSettings}
        >
          <Icon name="save" size={20} color="#FFFFFF" />
          <Text style={styles.saveButtonText}>Salvar Configurações</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    flex: 1,
  },
  section: {
    backgroundColor: theme.colors.surface,
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 12,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 16,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
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
    lineHeight: 18,
  },
  settingControl: {
    alignItems: 'flex-end',
  },
  periodContainer: {
    flexDirection: 'row',
    backgroundColor: theme.colors.background,
    borderRadius: 8,
    padding: 4,
  },
  periodOption: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
  periodOptionActive: {
    backgroundColor: theme.colors.primary,
  },
  periodOptionText: {
    fontSize: 14,
    fontWeight: '500',
    color: theme.colors.textSecondary,
  },
  periodOptionTextActive: {
    color: '#FFFFFF',
  },
  sliderContainer: {
    width: 150,
    alignItems: 'center',
  },
  slider: {
    width: '100%',
    height: 40,
  },
  sliderLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginTop: 4,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  actionButtonContent: {
    flex: 1,
    marginLeft: 12,
  },
  actionButtonTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 2,
  },
  actionButtonDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    lineHeight: 18,
  },
  infoContainer: {
    backgroundColor: theme.colors.background,
    borderRadius: 8,
    padding: 16,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  infoLabel: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '500',
    color: theme.colors.text,
  },
  footer: {
    padding: 16,
    backgroundColor: theme.colors.surface,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.colors.primary,
    paddingVertical: 16,
    borderRadius: 12,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});