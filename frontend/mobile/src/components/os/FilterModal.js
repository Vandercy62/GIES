import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  ScrollView,
  Switch,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { theme } from '../../styles/theme';

const STATUS_OPTIONS = [
  { key: 'todas', label: 'Todas as OS', icon: 'list' },
  { key: 'solicitacao', label: 'Solicitação', icon: 'pending', color: '#FF9800' },
  { key: 'orcamento', label: 'Orçamento', icon: 'description', color: '#2196F3' },
  { key: 'aprovacao', label: 'Aprovação', icon: 'approval', color: '#9C27B0' },
  { key: 'agendamento', label: 'Agendamento', icon: 'schedule', color: '#3F51B5' },
  { key: 'visita_tecnica', label: 'Visita Técnica', icon: 'engineering', color: '#3F51B5' },
  { key: 'execucao', label: 'Execução', icon: 'build', color: '#4CAF50' },
  { key: 'entrega', label: 'Entrega', icon: 'local-shipping', color: '#4CAF50' },
  { key: 'pos_venda', label: 'Concluída', icon: 'check-circle', color: '#9E9E9E' },
];

const PRIORITY_OPTIONS = [
  { key: 'todas', label: 'Todas as prioridades' },
  { key: 'baixa', label: 'Baixa', color: theme.colors.success },
  { key: 'media', label: 'Média', color: theme.colors.warning },
  { key: 'alta', label: 'Alta', color: theme.colors.error },
  { key: 'urgente', label: 'Urgente', color: theme.colors.error },
];

const DATE_OPTIONS = [
  { key: 'todas', label: 'Todas as datas' },
  { key: 'hoje', label: 'Hoje' },
  { key: 'amanha', label: 'Amanhã' },
  { key: 'esta_semana', label: 'Esta semana' },
  { key: 'proxima_semana', label: 'Próxima semana' },
  { key: 'este_mes', label: 'Este mês' },
  { key: 'em_atraso', label: 'Em atraso' },
  { key: 'sem_data', label: 'Sem data definida' },
];

const SORT_OPTIONS = [
  { key: 'data_agendamento', label: 'Data de agendamento', icon: 'schedule' },
  { key: 'prioridade', label: 'Prioridade', icon: 'priority-high' },
  { key: 'cliente_nome', label: 'Nome do cliente', icon: 'person' },
  { key: 'numero', label: 'Número da OS', icon: 'tag' },
  { key: 'valor_estimado', label: 'Valor estimado', icon: 'attach-money' },
  { key: 'created_at', label: 'Data de criação', icon: 'add-circle' },
];

export default function FilterModal({ 
  visible, 
  onClose, 
  filters, 
  onFiltersChange,
  osCount = 0 
}) {
  const [localFilters, setLocalFilters] = useState(filters);

  const handleFilterChange = (key, value) => {
    setLocalFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleApply = () => {
    onFiltersChange(localFilters);
    onClose();
  };

  const handleReset = () => {
    const resetFilters = {
      status: 'todas',
      prioridade: 'todas',
      data: 'todas',
      sortBy: 'data_agendamento',
      sortOrder: 'desc',
      apenasMinhas: false,
      comFotos: false,
      assinadas: false,
    };
    setLocalFilters(resetFilters);
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (localFilters.status !== 'todas') count++;
    if (localFilters.prioridade !== 'todas') count++;
    if (localFilters.data !== 'todas') count++;
    if (localFilters.apenasMinhas) count++;
    if (localFilters.comFotos) count++;
    if (localFilters.assinadas) count++;
    return count;
  };

  const renderSection = (title, children) => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );

  const renderOption = (option, selectedValue, onSelect, showColor = false) => (
    <TouchableOpacity
      key={option.key}
      style={[
        styles.option,
        selectedValue === option.key && styles.optionSelected
      ]}
      onPress={() => onSelect(option.key)}
    >
      <View style={styles.optionContent}>
        {option.icon && (
          <Icon 
            name={option.icon} 
            size={20} 
            color={option.color || (selectedValue === option.key ? theme.colors.primary : theme.colors.textSecondary)} 
          />
        )}
        
        {showColor && option.color && (
          <View style={[styles.colorIndicator, { backgroundColor: option.color }]} />
        )}
        
        <Text style={[
          styles.optionText,
          selectedValue === option.key && styles.optionTextSelected
        ]}>
          {option.label}
        </Text>
      </View>
      
      {selectedValue === option.key && (
        <Icon name="check" size={20} color={theme.colors.primary} />
      )}
    </TouchableOpacity>
  );

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onClose} style={styles.headerButton}>
            <Icon name="close" size={24} color={theme.colors.text} />
          </TouchableOpacity>
          
          <View style={styles.headerTitleContainer}>
            <Text style={styles.headerTitle}>Filtros</Text>
            {getActiveFiltersCount() > 0 && (
              <View style={styles.badge}>
                <Text style={styles.badgeText}>{getActiveFiltersCount()}</Text>
              </View>
            )}
          </View>
          
          <TouchableOpacity onPress={handleReset} style={styles.headerButton}>
            <Text style={styles.resetText}>Limpar</Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* Status */}
          {renderSection(
            'Status da OS',
            STATUS_OPTIONS.map(option => 
              renderOption(
                option, 
                localFilters.status, 
                (value) => handleFilterChange('status', value),
                true
              )
            )
          )}

          {/* Prioridade */}
          {renderSection(
            'Prioridade',
            PRIORITY_OPTIONS.map(option => 
              renderOption(
                option, 
                localFilters.prioridade, 
                (value) => handleFilterChange('prioridade', value),
                true
              )
            )
          )}

          {/* Data */}
          {renderSection(
            'Data de Agendamento',
            DATE_OPTIONS.map(option => 
              renderOption(
                option, 
                localFilters.data, 
                (value) => handleFilterChange('data', value)
              )
            )
          )}

          {/* Ordenação */}
          {renderSection(
            'Ordenar por',
            <View>
              {SORT_OPTIONS.map(option => 
                renderOption(
                  option, 
                  localFilters.sortBy, 
                  (value) => handleFilterChange('sortBy', value)
                )
              )}
              
              <View style={styles.sortOrderContainer}>
                <Text style={styles.sortOrderLabel}>Ordem:</Text>
                <View style={styles.sortOrderOptions}>
                  <TouchableOpacity
                    style={[
                      styles.sortOrderButton,
                      localFilters.sortOrder === 'asc' && styles.sortOrderButtonActive
                    ]}
                    onPress={() => handleFilterChange('sortOrder', 'asc')}
                  >
                    <Icon name="arrow-upward" size={16} color={
                      localFilters.sortOrder === 'asc' ? '#FFFFFF' : theme.colors.textSecondary
                    } />
                    <Text style={[
                      styles.sortOrderButtonText,
                      localFilters.sortOrder === 'asc' && styles.sortOrderButtonTextActive
                    ]}>
                      Crescente
                    </Text>
                  </TouchableOpacity>
                  
                  <TouchableOpacity
                    style={[
                      styles.sortOrderButton,
                      localFilters.sortOrder === 'desc' && styles.sortOrderButtonActive
                    ]}
                    onPress={() => handleFilterChange('sortOrder', 'desc')}
                  >
                    <Icon name="arrow-downward" size={16} color={
                      localFilters.sortOrder === 'desc' ? '#FFFFFF' : theme.colors.textSecondary
                    } />
                    <Text style={[
                      styles.sortOrderButtonText,
                      localFilters.sortOrder === 'desc' && styles.sortOrderButtonTextActive
                    ]}>
                      Decrescente
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>
          )}

          {/* Filtros avançados */}
          {renderSection(
            'Filtros Avançados',
            <View>
              <View style={styles.switchOption}>
                <View style={styles.switchContent}>
                  <Icon name="person" size={20} color={theme.colors.textSecondary} />
                  <Text style={styles.switchLabel}>Apenas minhas OS</Text>
                </View>
                <Switch
                  value={localFilters.apenasMinhas}
                  onValueChange={(value) => handleFilterChange('apenasMinhas', value)}
                  trackColor={{ false: theme.colors.disabled, true: theme.colors.primary + '40' }}
                  thumbColor={localFilters.apenasMinhas ? theme.colors.primary : '#FFFFFF'}
                />
              </View>

              <View style={styles.switchOption}>
                <View style={styles.switchContent}>
                  <Icon name="photo-camera" size={20} color={theme.colors.textSecondary} />
                  <Text style={styles.switchLabel}>Com fotos anexadas</Text>
                </View>
                <Switch
                  value={localFilters.comFotos}
                  onValueChange={(value) => handleFilterChange('comFotos', value)}
                  trackColor={{ false: theme.colors.disabled, true: theme.colors.primary + '40' }}
                  thumbColor={localFilters.comFotos ? theme.colors.primary : '#FFFFFF'}
                />
              </View>

              <View style={styles.switchOption}>
                <View style={styles.switchContent}>
                  <Icon name="draw" size={20} color={theme.colors.textSecondary} />
                  <Text style={styles.switchLabel}>Com assinatura do cliente</Text>
                </View>
                <Switch
                  value={localFilters.assinadas}
                  onValueChange={(value) => handleFilterChange('assinadas', value)}
                  trackColor={{ false: theme.colors.disabled, true: theme.colors.primary + '40' }}
                  thumbColor={localFilters.assinadas ? theme.colors.primary : '#FFFFFF'}
                />
              </View>
            </View>
          )}
        </ScrollView>

        {/* Footer */}
        <View style={styles.footer}>
          <View style={styles.resultCount}>
            <Text style={styles.resultCountText}>
              {osCount} OS {osCount === 1 ? 'encontrada' : 'encontradas'}
            </Text>
          </View>
          
          <TouchableOpacity
            style={styles.applyButton}
            onPress={handleApply}
          >
            <Text style={styles.applyButtonText}>Aplicar Filtros</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.disabled + '30',
  },
  headerButton: {
    padding: 8,
  },
  headerTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  badge: {
    backgroundColor: theme.colors.primary,
    borderRadius: 10,
    width: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  resetText: {
    fontSize: 16,
    color: theme.colors.primary,
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  section: {
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.disabled + '20',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 12,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 4,
  },
  optionSelected: {
    backgroundColor: theme.colors.primary + '10',
  },
  optionContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  colorIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 12,
  },
  optionText: {
    fontSize: 15,
    color: theme.colors.text,
    marginLeft: 12,
  },
  optionTextSelected: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  sortOrderContainer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: theme.colors.disabled + '30',
  },
  sortOrderLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 8,
  },
  sortOrderOptions: {
    flexDirection: 'row',
    gap: 8,
  },
  sortOrderButton: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.disabled,
    backgroundColor: theme.colors.surface,
  },
  sortOrderButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  sortOrderButtonText: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    marginLeft: 4,
  },
  sortOrderButtonTextActive: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  switchOption: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
  },
  switchContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  switchLabel: {
    fontSize: 15,
    color: theme.colors.text,
    marginLeft: 12,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderTopWidth: 1,
    borderTopColor: theme.colors.disabled + '30',
    backgroundColor: theme.colors.surface,
  },
  resultCount: {
    flex: 1,
  },
  resultCountText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  applyButton: {
    backgroundColor: theme.colors.primary,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  applyButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
});