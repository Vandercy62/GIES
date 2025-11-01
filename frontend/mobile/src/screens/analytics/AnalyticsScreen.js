import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Dimensions,
  Alert,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';
import LinearGradient from 'react-native-linear-gradient';

import {
  selectDashboardStats,
  selectPerformanceCharts,
  selectAnalyticsLoading,
  selectAnalyticsError,
  selectAnalyticsSettings,
  fetchDashboardStats,
  fetchPerformanceCharts,
  clearError,
} from '../../store/slices/analyticsSlice';
import { theme } from '../../styles/theme';

const { width } = Dimensions.get('window');
const chartWidth = width - 32;

/**
 * Dashboard Analytics - Tela Principal de Relatórios e KPIs
 */
export default function AnalyticsScreen({ navigation }) {
  const dispatch = useDispatch();
  const dashboardStats = useSelector(selectDashboardStats);
  const performanceCharts = useSelector(selectPerformanceCharts);
  const loading = useSelector(selectAnalyticsLoading);
  const error = useSelector(selectAnalyticsError);
  const settings = useSelector(selectAnalyticsSettings);

  const [refreshing, setRefreshing] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [selectedChart, setSelectedChart] = useState('completion');

  // Configurar header
  useEffect(() => {
    navigation.setOptions({
      title: 'Analytics & Relatórios',
      headerRight: () => (
        <View style={styles.headerActions}>
          <TouchableOpacity
            onPress={() => navigation.navigate('ReportsManager')}
            style={styles.headerButton}
          >
            <Icon name="description" size={24} color="#FFFFFF" />
          </TouchableOpacity>
          
          <TouchableOpacity
            onPress={handleExportData}
            style={styles.headerButton}
          >
            <Icon name="share" size={24} color="#FFFFFF" />
          </TouchableOpacity>
        </View>
      ),
    });
  }, [navigation]);

  // Carregar dados quando a tela ganhar foco
  useFocusEffect(
    useCallback(() => {
      loadAnalyticsData();
    }, [selectedPeriod])
  );

  const loadAnalyticsData = async () => {
    try {
      await Promise.all([
        dispatch(fetchDashboardStats()),
        dispatch(fetchPerformanceCharts({ period: selectedPeriod })),
      ]);
    } catch (error) {
      console.error('Erro ao carregar analytics:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAnalyticsData();
    setRefreshing(false);
  };

  const handleExportData = () => {
    Alert.alert(
      'Exportar Dados',
      'Escolha o formato de exportação:',
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'PDF', onPress: () => exportData('pdf') },
        { text: 'Excel', onPress: () => exportData('excel') },
        { text: 'CSV', onPress: () => exportData('csv') },
      ]
    );
  };

  const exportData = (format) => {
    // Implementar exportação
    Alert.alert('Em Desenvolvimento', `Exportação em ${format.toUpperCase()} será implementada.`);
  };

  const formatNumber = (num) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  const formatPercentage = (value) => `${value}%`;

  // Configuração dos gráficos
  const chartConfig = {
    backgroundColor: '#FFFFFF',
    backgroundGradientFrom: '#FFFFFF',
    backgroundGradientTo: '#FFFFFF',
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(33, 150, 243, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '4',
      strokeWidth: '2',
      stroke: theme.colors.primary,
    },
  };

  const renderKPICard = (title, value, subtitle, icon, color, onPress) => (
    <TouchableOpacity
      style={[styles.kpiCard, { borderLeftColor: color }]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.kpiHeader}>
        <View style={[styles.kpiIcon, { backgroundColor: color + '20' }]}>
          <Icon name={icon} size={24} color={color} />
        </View>
        <Text style={styles.kpiTitle}>{title}</Text>
      </View>
      
      <Text style={styles.kpiValue}>{value}</Text>
      {subtitle && <Text style={styles.kpiSubtitle}>{subtitle}</Text>}
    </TouchableOpacity>
  );

  const renderPeriodSelector = () => (
    <View style={styles.periodSelector}>
      {['7d', '30d', '90d'].map((period) => (
        <TouchableOpacity
          key={period}
          style={[
            styles.periodButton,
            selectedPeriod === period && styles.periodButtonActive,
          ]}
          onPress={() => setSelectedPeriod(period)}
        >
          <Text style={[
            styles.periodButtonText,
            selectedPeriod === period && styles.periodButtonTextActive,
          ]}>
            {period === '7d' ? '7 dias' : period === '30d' ? '30 dias' : '90 dias'}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderCompletionChart = () => {
    const trendData = performanceCharts.data?.osCompletionTrend || [];
    
    if (!trendData.length) {
      return renderEmptyChart('Nenhum dado de completude disponível');
    }

    const chartData = {
      labels: trendData.slice(-7).map(item => item.label),
      datasets: [
        {
          data: trendData.slice(-7).map(item => item.completed),
          color: (opacity = 1) => `rgba(76, 175, 80, ${opacity})`,
          strokeWidth: 3,
        },
        {
          data: trendData.slice(-7).map(item => item.created),
          color: (opacity = 1) => `rgba(33, 150, 243, ${opacity})`,
          strokeWidth: 3,
        },
      ],
      legend: ['Concluídas', 'Criadas'],
    };

    return (
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Tendência de OS</Text>
        <LineChart
          data={chartData}
          width={chartWidth}
          height={220}
          chartConfig={chartConfig}
          bezier
          style={styles.chart}
        />
      </View>
    );
  };

  const renderPerformanceChart = () => {
    const performanceData = performanceCharts.data?.performanceMetrics || [];
    
    if (!performanceData.length) {
      return renderEmptyChart('Nenhum dado de performance disponível');
    }

    const chartData = {
      labels: performanceData.map(item => item.label),
      datasets: [{
        data: performanceData.map(item => item.value),
      }],
    };

    return (
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Status das OS</Text>
        <BarChart
          data={chartData}
          width={chartWidth}
          height={220}
          chartConfig={{
            ...chartConfig,
            color: (opacity = 1) => `rgba(76, 175, 80, ${opacity})`,
          }}
          style={styles.chart}
        />
      </View>
    );
  };

  const renderCategoryChart = () => {
    const categoryData = performanceCharts.data?.categoryDistribution || [];
    
    if (!categoryData.length) {
      return renderEmptyChart('Nenhum dado de categoria disponível');
    }

    return (
      <View style={styles.chartContainer}>
        <Text style={styles.chartTitle}>Distribuição por Categoria</Text>
        <PieChart
          data={categoryData}
          width={chartWidth}
          height={220}
          chartConfig={chartConfig}
          accessor="value"
          backgroundColor="transparent"
          paddingLeft="15"
          style={styles.chart}
        />
      </View>
    );
  };

  const renderEmptyChart = (message) => (
    <View style={styles.emptyChart}>
      <Icon name="insert-chart" size={48} color={theme.colors.disabled} />
      <Text style={styles.emptyChartText}>{message}</Text>
    </View>
  );

  const renderChart = () => {
    switch (selectedChart) {
      case 'completion':
        return renderCompletionChart();
      case 'performance':
        return renderPerformanceChart();
      case 'category':
        return renderCategoryChart();
      default:
        return renderCompletionChart();
    }
  };

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Icon name="error" size={64} color={theme.colors.error} />
        <Text style={styles.errorTitle}>Erro ao Carregar Analytics</Text>
        <Text style={styles.errorMessage}>{error}</Text>
        <TouchableOpacity
          style={styles.retryButton}
          onPress={() => {
            dispatch(clearError());
            loadAnalyticsData();
          }}
        >
          <Text style={styles.retryButtonText}>Tentar Novamente</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={onRefresh}
          colors={[theme.colors.primary]}
          tintColor={theme.colors.primary}
        />
      }
      showsVerticalScrollIndicator={false}
    >
      {/* KPIs Grid */}
      <View style={styles.kpiGrid}>
        {renderKPICard(
          'OS Totais',
          dashboardStats.osStats.total,
          `${dashboardStats.osStats.completed} concluídas`,
          'work',
          theme.colors.primary
        )}
        
        {renderKPICard(
          'Taxa de Conclusão',
          formatPercentage(dashboardStats.performance.completionRate),
          'Últimos 30 dias',
          'trending-up',
          theme.colors.success
        )}
        
        {renderKPICard(
          'Tempo Médio',
          `${dashboardStats.performance.averageTime}h`,
          'Para conclusão',
          'schedule',
          theme.colors.warning
        )}
        
        {renderKPICard(
          'Pontualidade',
          formatPercentage(dashboardStats.performance.onTimeDelivery),
          'Entregas no prazo',
          'check-circle',
          theme.colors.success
        )}
      </View>

      {/* Period Selector */}
      {renderPeriodSelector()}

      {/* Chart Type Selector */}
      <View style={styles.chartTypeSelector}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {[
            { key: 'completion', label: 'Completude', icon: 'trending-up' },
            { key: 'performance', label: 'Performance', icon: 'bar-chart' },
            { key: 'category', label: 'Categorias', icon: 'pie-chart' },
          ].map((chart) => (
            <TouchableOpacity
              key={chart.key}
              style={[
                styles.chartTypeButton,
                selectedChart === chart.key && styles.chartTypeButtonActive,
              ]}
              onPress={() => setSelectedChart(chart.key)}
            >
              <Icon
                name={chart.icon}
                size={20}
                color={selectedChart === chart.key ? '#FFFFFF' : theme.colors.textSecondary}
              />
              <Text style={[
                styles.chartTypeButtonText,
                selectedChart === chart.key && styles.chartTypeButtonTextActive,
              ]}>
                {chart.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Main Chart */}
      {loading.charts ? (
        <View style={styles.loadingChart}>
          <Icon name="hourglass-empty" size={48} color={theme.colors.disabled} />
          <Text style={styles.loadingText}>Carregando gráfico...</Text>
        </View>
      ) : (
        renderChart()
      )}

      {/* Quick Actions */}
      <View style={styles.quickActions}>
        <Text style={styles.sectionTitle}>Ações Rápidas</Text>
        
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('ReportsManager')}
        >
          <Icon name="description" size={24} color={theme.colors.primary} />
          <Text style={styles.actionButtonText}>Gerar Relatório</Text>
          <Icon name="chevron-right" size={24} color={theme.colors.disabled} />
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.actionButton}
          onPress={handleExportData}
        >
          <Icon name="file-download" size={24} color={theme.colors.primary} />
          <Text style={styles.actionButtonText}>Exportar Dados</Text>
          <Icon name="chevron-right" size={24} color={theme.colors.disabled} />
        </TouchableOpacity>
        
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => navigation.navigate('AnalyticsSettings')}
        >
          <Icon name="settings" size={24} color={theme.colors.primary} />
          <Text style={styles.actionButtonText}>Configurações</Text>
          <Icon name="chevron-right" size={24} color={theme.colors.disabled} />
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
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerButton: {
    padding: 8,
    marginLeft: 8,
  },
  kpiGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    gap: 12,
  },
  kpiCard: {
    flex: 1,
    minWidth: (width - 44) / 2,
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  kpiHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  kpiIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  kpiTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: theme.colors.textSecondary,
    flex: 1,
  },
  kpiValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 4,
  },
  kpiSubtitle: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  periodSelector: {
    flexDirection: 'row',
    marginHorizontal: 16,
    marginBottom: 16,
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    padding: 4,
  },
  periodButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    alignItems: 'center',
  },
  periodButtonActive: {
    backgroundColor: theme.colors.primary,
  },
  periodButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: theme.colors.textSecondary,
  },
  periodButtonTextActive: {
    color: '#FFFFFF',
  },
  chartTypeSelector: {
    marginBottom: 16,
  },
  chartTypeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginLeft: 16,
    borderRadius: 20,
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  chartTypeButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  chartTypeButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: theme.colors.textSecondary,
    marginLeft: 6,
  },
  chartTypeButtonTextActive: {
    color: '#FFFFFF',
  },
  chartContainer: {
    backgroundColor: theme.colors.surface,
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 16,
    textAlign: 'center',
  },
  chart: {
    borderRadius: 8,
  },
  emptyChart: {
    height: 220,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 12,
  },
  emptyChartText: {
    fontSize: 16,
    color: theme.colors.disabled,
    marginTop: 8,
    textAlign: 'center',
  },
  loadingChart: {
    height: 220,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 12,
  },
  loadingText: {
    fontSize: 16,
    color: theme.colors.disabled,
    marginTop: 8,
  },
  quickActions: {
    margin: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 16,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '500',
    color: theme.colors.text,
    flex: 1,
    marginLeft: 12,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
    backgroundColor: theme.colors.background,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  errorMessage: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 20,
  },
  retryButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 16,
  },
});