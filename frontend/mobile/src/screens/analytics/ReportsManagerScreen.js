import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  TextInput,
  Switch,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import moment from 'moment';
import DateTimePicker from '@react-native-community/datetimepicker';

import {
  selectReports,
  selectCurrentReport,
  selectAnalyticsLoading,
  selectAnalyticsError,
  generateReport,
  removeReport,
  clearReports,
  setCurrentReport,
  exportData,
} from '../../store/slices/analyticsSlice';
import { theme } from '../../styles/theme';

/**
 * Gerenciador de Relatórios - Criação, visualização e compartilhamento
 */
export default function ReportsManagerScreen({ navigation }) {
  const dispatch = useDispatch();
  const reports = useSelector(selectReports);
  const currentReport = useSelector(selectCurrentReport);
  const loading = useSelector(selectAnalyticsLoading);
  const error = useSelector(selectAnalyticsError);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [datePickerMode, setDatePickerMode] = useState('start');
  
  // Form State
  const [reportForm, setReportForm] = useState({
    type: 'performance',
    title: '',
    description: '',
    dateRange: {
      startDate: moment().subtract(30, 'days').toDate(),
      endDate: new Date(),
    },
    includeCharts: true,
    includeData: true,
    format: 'pdf',
  });

  useEffect(() => {
    navigation.setOptions({
      title: 'Gerenciar Relatórios',
      headerRight: () => (
        <TouchableOpacity
          onPress={() => setShowCreateModal(true)}
          style={styles.headerButton}
        >
          <Icon name="add" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      ),
    });
  }, [navigation]);

  const reportTypes = [
    { key: 'performance', label: 'Performance Geral', icon: 'trending-up' },
    { key: 'os_summary', label: 'Resumo de OS', icon: 'work' },
    { key: 'appointments', label: 'Relatório de Agenda', icon: 'event' },
    { key: 'custom', label: 'Personalizado', icon: 'settings' },
  ];

  const formatOptions = [
    { key: 'pdf', label: 'PDF', icon: 'picture-as-pdf' },
    { key: 'excel', label: 'Excel', icon: 'table-chart' },
    { key: 'html', label: 'HTML', icon: 'web' },
  ];

  const handleCreateReport = async () => {
    if (!reportForm.title.trim()) {
      Alert.alert('Erro', 'Por favor, digite um título para o relatório.');
      return;
    }

    try {
      await dispatch(generateReport({
        reportType: reportForm.type,
        title: reportForm.title,
        description: reportForm.description,
        dateRange: reportForm.dateRange,
        includeCharts: reportForm.includeCharts,
        format: reportForm.format,
      }));

      setShowCreateModal(false);
      resetForm();
      
      Alert.alert(
        'Sucesso',
        'Relatório gerado com sucesso!',
        [{ text: 'OK' }]
      );
    } catch (error) {
      Alert.alert('Erro', 'Falha ao gerar relatório. Tente novamente.');
    }
  };

  const handleDeleteReport = (reportId) => {
    Alert.alert(
      'Excluir Relatório',
      'Tem certeza que deseja excluir este relatório?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Excluir',
          style: 'destructive',
          onPress: () => dispatch(removeReport(reportId)),
        },
      ]
    );
  };

  const handleShareReport = (report) => {
    Alert.alert(
      'Compartilhar Relatório',
      `Compartilhar "${report.title || report.type}"?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Email', onPress: () => shareViaEmail(report) },
        { text: 'WhatsApp', onPress: () => shareViaWhatsApp(report) },
        { text: 'Mais opções', onPress: () => shareViaOthers(report) },
      ]
    );
  };

  const shareViaEmail = (report) => {
    Alert.alert('Em Desenvolvimento', 'Compartilhamento por email será implementado.');
  };

  const shareViaWhatsApp = (report) => {
    Alert.alert('Em Desenvolvimento', 'Compartilhamento por WhatsApp será implementado.');
  };

  const shareViaOthers = (report) => {
    Alert.alert('Em Desenvolvimento', 'Mais opções de compartilhamento serão implementadas.');
  };

  const resetForm = () => {
    setReportForm({
      type: 'performance',
      title: '',
      description: '',
      dateRange: {
        startDate: moment().subtract(30, 'days').toDate(),
        endDate: new Date(),
      },
      includeCharts: true,
      includeData: true,
      format: 'pdf',
    });
  };

  const handleDateChange = (event, selectedDate) => {
    setShowDatePicker(false);
    
    if (selectedDate) {
      setReportForm(prev => ({
        ...prev,
        dateRange: {
          ...prev.dateRange,
          [datePickerMode === 'start' ? 'startDate' : 'endDate']: selectedDate,
        },
      }));
    }
  };

  const getReportTypeInfo = (type) => {
    return reportTypes.find(t => t.key === type) || reportTypes[0];
  };

  const getFormatInfo = (format) => {
    return formatOptions.find(f => f.key === format) || formatOptions[0];
  };

  const formatDate = (date) => {
    return moment(date).format('DD/MM/YYYY');
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const renderReportCard = (report) => {
    const typeInfo = getReportTypeInfo(report.type);
    const formatInfo = getFormatInfo(report.format);
    
    return (
      <TouchableOpacity
        key={report.id}
        style={styles.reportCard}
        onPress={() => dispatch(setCurrentReport(report))}
        activeOpacity={0.7}
      >
        <View style={styles.reportHeader}>
          <View style={styles.reportIcon}>
            <Icon name={typeInfo.icon} size={20} color={theme.colors.primary} />
          </View>
          
          <View style={styles.reportInfo}>
            <Text style={styles.reportTitle} numberOfLines={1}>
              {report.title || typeInfo.label}
            </Text>
            <Text style={styles.reportSubtitle}>
              {formatDate(report.generatedAt)} • {formatInfo.label}
            </Text>
          </View>
          
          <View style={styles.reportActions}>
            <TouchableOpacity
              onPress={() => handleShareReport(report)}
              style={styles.reportAction}
            >
              <Icon name="share" size={20} color={theme.colors.textSecondary} />
            </TouchableOpacity>
            
            <TouchableOpacity
              onPress={() => handleDeleteReport(report.id)}
              style={styles.reportAction}
            >
              <Icon name="delete" size={20} color={theme.colors.error} />
            </TouchableOpacity>
          </View>
        </View>
        
        {report.description && (
          <Text style={styles.reportDescription} numberOfLines={2}>
            {report.description}
          </Text>
        )}
        
        <View style={styles.reportMeta}>
          <Text style={styles.reportMetaText}>
            {formatDate(report.dateRange.startDate)} - {formatDate(report.dateRange.endDate)}
          </Text>
          <Text style={styles.reportMetaText}>
            {report.status === 'completed' ? 'Pronto' : 'Processando...'}
          </Text>
        </View>
      </TouchableOpacity>
    );
  };

  const renderCreateModal = () => (
    <Modal
      visible={showCreateModal}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setShowCreateModal(false)}
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity
            onPress={() => setShowCreateModal(false)}
            style={styles.modalCloseButton}
          >
            <Icon name="close" size={24} color={theme.colors.text} />
          </TouchableOpacity>
          
          <Text style={styles.modalTitle}>Novo Relatório</Text>
          
          <TouchableOpacity
            onPress={handleCreateReport}
            style={[
              styles.modalSaveButton,
              { opacity: loading.report ? 0.5 : 1 }
            ]}
            disabled={loading.report}
          >
            <Text style={styles.modalSaveButtonText}>
              {loading.report ? 'Gerando...' : 'Gerar'}
            </Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent} showsVerticalScrollIndicator={false}>
          {/* Tipo de Relatório */}
          <Text style={styles.formLabel}>Tipo de Relatório</Text>
          <View style={styles.typeSelector}>
            {reportTypes.map((type) => (
              <TouchableOpacity
                key={type.key}
                style={[
                  styles.typeOption,
                  reportForm.type === type.key && styles.typeOptionActive,
                ]}
                onPress={() => setReportForm(prev => ({ ...prev, type: type.key }))}
              >
                <Icon
                  name={type.icon}
                  size={20}
                  color={reportForm.type === type.key ? '#FFFFFF' : theme.colors.textSecondary}
                />
                <Text style={[
                  styles.typeOptionText,
                  reportForm.type === type.key && styles.typeOptionTextActive,
                ]}>
                  {type.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Título */}
          <Text style={styles.formLabel}>Título do Relatório</Text>
          <TextInput
            style={styles.textInput}
            placeholder="Digite o título do relatório"
            value={reportForm.title}
            onChangeText={(text) => setReportForm(prev => ({ ...prev, title: text }))}
            maxLength={100}
          />

          {/* Descrição */}
          <Text style={styles.formLabel}>Descrição (Opcional)</Text>
          <TextInput
            style={[styles.textInput, styles.textArea]}
            placeholder="Adicione uma descrição..."
            value={reportForm.description}
            onChangeText={(text) => setReportForm(prev => ({ ...prev, description: text }))}
            multiline
            numberOfLines={3}
            maxLength={500}
          />

          {/* Período */}
          <Text style={styles.formLabel}>Período</Text>
          <View style={styles.dateRangeContainer}>
            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => {
                setDatePickerMode('start');
                setShowDatePicker(true);
              }}
            >
              <Icon name="calendar-today" size={20} color={theme.colors.textSecondary} />
              <Text style={styles.dateButtonText}>
                {formatDate(reportForm.dateRange.startDate)}
              </Text>
            </TouchableOpacity>
            
            <Text style={styles.dateSeparator}>até</Text>
            
            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => {
                setDatePickerMode('end');
                setShowDatePicker(true);
              }}
            >
              <Icon name="calendar-today" size={20} color={theme.colors.textSecondary} />
              <Text style={styles.dateButtonText}>
                {formatDate(reportForm.dateRange.endDate)}
              </Text>
            </TouchableOpacity>
          </View>

          {/* Formato */}
          <Text style={styles.formLabel}>Formato de Saída</Text>
          <View style={styles.formatSelector}>
            {formatOptions.map((format) => (
              <TouchableOpacity
                key={format.key}
                style={[
                  styles.formatOption,
                  reportForm.format === format.key && styles.formatOptionActive,
                ]}
                onPress={() => setReportForm(prev => ({ ...prev, format: format.key }))}
              >
                <Icon
                  name={format.icon}
                  size={20}
                  color={reportForm.format === format.key ? '#FFFFFF' : theme.colors.textSecondary}
                />
                <Text style={[
                  styles.formatOptionText,
                  reportForm.format === format.key && styles.formatOptionTextActive,
                ]}>
                  {format.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Opções */}
          <Text style={styles.formLabel}>Opções</Text>
          <View style={styles.optionsContainer}>
            <View style={styles.optionRow}>
              <Text style={styles.optionLabel}>Incluir Gráficos</Text>
              <Switch
                value={reportForm.includeCharts}
                onValueChange={(value) => setReportForm(prev => ({ ...prev, includeCharts: value }))}
                thumbColor={reportForm.includeCharts ? theme.colors.primary : theme.colors.disabled}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary + '40' }}
              />
            </View>
            
            <View style={styles.optionRow}>
              <Text style={styles.optionLabel}>Incluir Dados Detalhados</Text>
              <Switch
                value={reportForm.includeData}
                onValueChange={(value) => setReportForm(prev => ({ ...prev, includeData: value }))}
                thumbColor={reportForm.includeData ? theme.colors.primary : theme.colors.disabled}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary + '40' }}
              />
            </View>
          </View>
        </ScrollView>

        {/* Date Picker */}
        {showDatePicker && (
          <DateTimePicker
            value={reportForm.dateRange[datePickerMode === 'start' ? 'startDate' : 'endDate']}
            mode="date"
            display="default"
            onChange={handleDateChange}
          />
        )}
      </View>
    </Modal>
  );

  if (loading.report && !showCreateModal) {
    return (
      <View style={styles.loadingContainer}>
        <Icon name="hourglass-empty" size={64} color={theme.colors.disabled} />
        <Text style={styles.loadingText}>Gerando relatório...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {reports.length > 0 ? (
        <ScrollView style={styles.reportsList} showsVerticalScrollIndicator={false}>
          <View style={styles.reportsHeader}>
            <Text style={styles.reportsTitle}>Meus Relatórios</Text>
            <Text style={styles.reportsSubtitle}>
              {reports.length} relatório{reports.length !== 1 ? 's' : ''}
            </Text>
          </View>
          
          {reports.map(renderReportCard)}
          
          {reports.length > 0 && (
            <TouchableOpacity
              style={styles.clearAllButton}
              onPress={() => {
                Alert.alert(
                  'Limpar Todos',
                  'Tem certeza que deseja excluir todos os relatórios?',
                  [
                    { text: 'Cancelar', style: 'cancel' },
                    {
                      text: 'Excluir Todos',
                      style: 'destructive',
                      onPress: () => dispatch(clearReports()),
                    },
                  ]
                );
              }}
            >
              <Icon name="clear-all" size={20} color={theme.colors.error} />
              <Text style={styles.clearAllButtonText}>Limpar Todos</Text>
            </TouchableOpacity>
          )}
        </ScrollView>
      ) : (
        <View style={styles.emptyState}>
          <Icon name="description" size={64} color={theme.colors.disabled} />
          <Text style={styles.emptyStateTitle}>Nenhum Relatório</Text>
          <Text style={styles.emptyStateDescription}>
            Toque no botão + para criar seu primeiro relatório
          </Text>
        </View>
      )}

      {renderCreateModal()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  headerButton: {
    padding: 8,
    marginRight: 8,
  },
  reportsList: {
    flex: 1,
  },
  reportsHeader: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  reportsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 4,
  },
  reportsSubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  reportCard: {
    backgroundColor: theme.colors.surface,
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  reportHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  reportIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.colors.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  reportInfo: {
    flex: 1,
  },
  reportTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 2,
  },
  reportSubtitle: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  reportActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  reportAction: {
    padding: 8,
    marginLeft: 4,
  },
  reportDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    lineHeight: 20,
    marginBottom: 8,
  },
  reportMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  reportMetaText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  clearAllButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    margin: 16,
    padding: 16,
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.error + '30',
  },
  clearAllButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.error,
    marginLeft: 8,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginTop: 16,
    marginBottom: 8,
  },
  emptyStateDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  loadingText: {
    fontSize: 16,
    color: theme.colors.disabled,
    marginTop: 16,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    backgroundColor: theme.colors.surface,
  },
  modalCloseButton: {
    padding: 8,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  modalSaveButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  modalSaveButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
  modalContent: {
    flex: 1,
    padding: 16,
  },
  formLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 8,
    marginTop: 16,
  },
  typeSelector: {
    marginBottom: 8,
  },
  typeOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    marginBottom: 8,
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  typeOptionActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  typeOptionText: {
    fontSize: 14,
    fontWeight: '500',
    color: theme.colors.text,
    marginLeft: 8,
  },
  typeOptionTextActive: {
    color: '#FFFFFF',
  },
  textInput: {
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    color: theme.colors.text,
    marginBottom: 8,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  dateRangeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  dateButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
  },
  dateButtonText: {
    fontSize: 16,
    color: theme.colors.text,
    marginLeft: 8,
  },
  dateSeparator: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginHorizontal: 12,
  },
  formatSelector: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  formatOption: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    marginRight: 8,
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  formatOptionActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  formatOptionText: {
    fontSize: 12,
    fontWeight: '500',
    color: theme.colors.text,
    marginLeft: 4,
  },
  formatOptionTextActive: {
    color: '#FFFFFF',
  },
  optionsContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  optionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  optionLabel: {
    fontSize: 16,
    color: theme.colors.text,
  },
});