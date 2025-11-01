import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Linking,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { useFocusEffect } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';

import {
  selectOSList,
  selectOSLoading,
  selectOSError,
  loadOSStart,
  loadOSSuccess,
  loadOSFailure,
  startOSExecution,
} from '../../store/slices/osSlice';
import { selectIsOffline } from '../../store/slices/offlineSlice';
import { theme } from '../../styles/theme';

// Componentes modernos
import OSCard from '../../components/os/OSCard';
import SearchBar from '../../components/os/SearchBar';
import FilterModal from '../../components/os/FilterModal';
import EmptyState from '../../components/os/EmptyState';

// Mock data para demonstração - remover quando conectar com API real
const mockOSData = [
  {
    id: 1,
    numero: '2024001',
    cliente_nome: 'João Silva & Cia',
    cliente_telefone: '(11) 99999-1234',
    descricao_servico: 'Instalação de forro de gesso em escritório comercial com luminárias embutidas',
    endereco: 'Rua das Flores, 123 - Centro, São Paulo/SP',
    data_agendamento: '2024-01-15',
    hora_agendamento: '09:00',
    fase_atual: 'visita_tecnica',
    prioridade: 'alta',
    valor_estimado: 2500.00,
    fotos: [],
    created_at: '2024-01-10T10:00:00Z',
  },
  {
    id: 2,
    numero: '2024002',
    cliente_nome: 'Maria Oliveira',
    cliente_telefone: '(11) 88888-5678',
    descricao_servico: 'Divisória de drywall para sala comercial',
    endereco: 'Av. Paulista, 1000 - Bela Vista, São Paulo/SP',
    data_agendamento: '2024-01-15',
    hora_agendamento: '14:00',
    fase_atual: 'execucao',
    prioridade: 'media',
    valor_estimado: 1800.00,
    fotos: ['foto1.jpg', 'foto2.jpg'],
    assinatura_cliente: 'assinatura.png',
    created_at: '2024-01-08T15:30:00Z',
  },
  {
    id: 3,
    numero: '2024003',
    cliente_nome: 'Empresa ABC Ltda',
    cliente_telefone: '(11) 77777-9012',
    descricao_servico: 'Manutenção preventiva em forro existente',
    endereco: 'Rua Comercial, 456 - Vila Madalena, São Paulo/SP',
    data_agendamento: '2024-01-16',
    hora_agendamento: '08:30',
    fase_atual: 'agendamento',
    prioridade: 'baixa',
    valor_estimado: 800.00,
    fotos: [],
    created_at: '2024-01-12T09:15:00Z',
  },
  {
    id: 4,
    numero: '2024004',
    cliente_nome: 'Pedro Santos',
    cliente_telefone: '(11) 66666-3456',
    descricao_servico: 'Reforma completa com novo projeto de forros e divisórias',
    endereco: 'Rua Nova, 789 - Moema, São Paulo/SP',
    data_agendamento: '2024-01-12',
    hora_agendamento: '10:00',
    fase_atual: 'pos_venda',
    prioridade: 'media',
    valor_estimado: 5200.00,
    fotos: ['foto1.jpg', 'foto2.jpg', 'foto3.jpg'],
    assinatura_cliente: 'assinatura.png',
    observacoes_tecnico: 'Serviço concluído com sucesso',
    created_at: '2024-01-05T11:20:00Z',
  },
  {
    id: 5,
    numero: '2024005',
    cliente_nome: 'Loja Fashion Style',
    cliente_telefone: '(11) 55555-7890',
    descricao_servico: 'Instalação urgente de divisórias para nova loja',
    endereco: 'Shopping Center, Loja 45 - Itaim Bibi, São Paulo/SP',
    data_agendamento: '2024-01-14',
    hora_agendamento: '16:00',
    fase_atual: 'orcamento',
    prioridade: 'urgente',
    valor_estimado: 3200.00,
    fotos: [],
    created_at: '2024-01-13T14:45:00Z',
  },
];

export default function OSListScreen({ navigation, route }) {
  const dispatch = useDispatch();
  const allOS = useSelector(selectOSList) || [];
  const loading = useSelector(selectOSLoading);
  const error = useSelector(selectOSError);
  const isOffline = useSelector(selectIsOffline);

  // Estados locais
  const [filteredOS, setFilteredOS] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  
  // Estado dos filtros
  const [filters, setFilters] = useState({
    status: 'todas',
    prioridade: 'todas',
    data: 'todas',
    sortBy: 'data_agendamento',
    sortOrder: 'desc',
    apenasMinhas: false,
    comFotos: false,
    assinadas: false,
  });

  // Verificar se há filtro da rota
  const routeFilter = route?.params?.filter;

  useEffect(() => {
    if (routeFilter) {
      setFilters(prev => ({ ...prev, status: routeFilter }));
    }
  }, [routeFilter]);

  // Carregar OS quando a tela ganhar foco
  useFocusEffect(
    useCallback(() => {
      loadOS();
    }, [])
  );

  // Filtrar OS quando dados mudarem
  useEffect(() => {
    filterAndSortOS();
  }, [allOS, searchQuery, filters]);

  // Gerar sugestões de busca
  useEffect(() => {
    generateSuggestions();
  }, [searchQuery, allOS]);

  const loadOS = async () => {
    try {
      dispatch(loadOSStart());
      // Simular carregamento da API
      await new Promise(resolve => setTimeout(resolve, 1000));
      dispatch(loadOSSuccess(mockOSData));
    } catch (error) {
      dispatch(loadOSFailure(error.message));
      if (!isOffline) {
        Alert.alert('Erro', 'Falha ao carregar ordens de serviço');
      }
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadOS();
    setRefreshing(false);
  };

  const generateSuggestions = () => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setSuggestions([]);
      return;
    }

    const query = searchQuery.toLowerCase();
    const newSuggestions = [];

    // Sugestões de clientes únicos
    const clientesUnicos = [...new Set(allOS.map(os => os.cliente_nome))]
      .filter(nome => nome.toLowerCase().includes(query))
      .slice(0, 3)
      .map(nome => ({
        type: 'cliente',
        label: nome,
        subtitle: 'Cliente',
      }));

    // Sugestões de números de OS
    const numerosOS = allOS
      .filter(os => os.numero.toLowerCase().includes(query))
      .slice(0, 2)
      .map(os => ({
        type: 'os',
        label: `OS ${os.numero}`,
        subtitle: os.cliente_nome,
      }));

    newSuggestions.push(...clientesUnicos, ...numerosOS);
    setSuggestions(newSuggestions);
  };

  const filterAndSortOS = () => {
    let filtered = [...allOS];

    // Filtrar por busca
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(os =>
        os.numero?.toLowerCase().includes(query) ||
        os.cliente_nome?.toLowerCase().includes(query) ||
        os.descricao_servico?.toLowerCase().includes(query) ||
        os.endereco?.toLowerCase().includes(query)
      );
    }

    // Filtrar por status/fase
    if (filters.status !== 'todas') {
      switch (filters.status) {
        case 'today':
          const today = new Date().toISOString().split('T')[0];
          filtered = filtered.filter(os => 
            os.data_agendamento && os.data_agendamento.startsWith(today)
          );
          break;
        case 'in_progress':
          filtered = filtered.filter(os => 
            ['visita_tecnica', 'execucao'].includes(os.fase_atual)
          );
          break;
        case 'pending':
          filtered = filtered.filter(os => 
            ['solicitacao', 'orcamento', 'aprovacao', 'agendamento'].includes(os.fase_atual)
          );
          break;
        case 'completed':
          filtered = filtered.filter(os => os.fase_atual === 'pos_venda');
          break;
        default:
          filtered = filtered.filter(os => os.fase_atual === filters.status);
          break;
      }
    }

    // Filtrar por prioridade
    if (filters.prioridade !== 'todas') {
      filtered = filtered.filter(os => os.prioridade === filters.prioridade);
    }

    // Filtrar por data
    if (filters.data !== 'todas') {
      const hoje = new Date();
      const amanha = new Date(hoje);
      amanha.setDate(hoje.getDate() + 1);

      switch (filters.data) {
        case 'hoje':
          filtered = filtered.filter(os => {
            if (!os.data_agendamento) return false;
            const osDate = new Date(os.data_agendamento);
            return osDate.toDateString() === hoje.toDateString();
          });
          break;
        case 'amanha':
          filtered = filtered.filter(os => {
            if (!os.data_agendamento) return false;
            const osDate = new Date(os.data_agendamento);
            return osDate.toDateString() === amanha.toDateString();
          });
          break;
        case 'esta_semana':
          const inicioSemana = new Date(hoje);
          inicioSemana.setDate(hoje.getDate() - hoje.getDay());
          const fimSemana = new Date(inicioSemana);
          fimSemana.setDate(inicioSemana.getDate() + 6);
          
          filtered = filtered.filter(os => {
            if (!os.data_agendamento) return false;
            const osDate = new Date(os.data_agendamento);
            return osDate >= inicioSemana && osDate <= fimSemana;
          });
          break;
        case 'em_atraso':
          filtered = filtered.filter(os => {
            if (!os.data_agendamento) return false;
            const osDate = new Date(os.data_agendamento);
            return osDate < hoje && os.fase_atual !== 'pos_venda';
          });
          break;
        case 'sem_data':
          filtered = filtered.filter(os => !os.data_agendamento);
          break;
      }
    }

    // Filtros avançados
    if (filters.comFotos) {
      filtered = filtered.filter(os => os.fotos && os.fotos.length > 0);
    }

    if (filters.assinadas) {
      filtered = filtered.filter(os => os.assinatura_cliente);
    }

    // Ordenação
    filtered.sort((a, b) => {
      let valueA, valueB;

      switch (filters.sortBy) {
        case 'data_agendamento':
          valueA = new Date(a.data_agendamento || a.created_at);
          valueB = new Date(b.data_agendamento || b.created_at);
          break;
        case 'prioridade':
          const priorityOrder = { 'urgente': 4, 'alta': 3, 'media': 2, 'baixa': 1 };
          valueA = priorityOrder[a.prioridade] || 0;
          valueB = priorityOrder[b.prioridade] || 0;
          break;
        case 'cliente_nome':
          valueA = a.cliente_nome?.toLowerCase() || '';
          valueB = b.cliente_nome?.toLowerCase() || '';
          break;
        case 'numero':
          valueA = parseInt(a.numero) || 0;
          valueB = parseInt(b.numero) || 0;
          break;
        case 'valor_estimado':
          valueA = parseFloat(a.valor_estimado) || 0;
          valueB = parseFloat(b.valor_estimado) || 0;
          break;
        default:
          valueA = new Date(a.created_at);
          valueB = new Date(b.created_at);
      }

      if (filters.sortOrder === 'asc') {
        return valueA > valueB ? 1 : -1;
      } else {
        return valueA < valueB ? 1 : -1;
      }
    });

    setFilteredOS(filtered);
  };

  const handleOSPress = (os) => {
    navigation.navigate('OSDetails', { os });
  };

  const handleQuickAction = async (os, action) => {
    switch (action) {
      case 'start':
        Alert.alert(
          'Iniciar OS',
          `Deseja iniciar a OS ${os.numero}?`,
          [
            { text: 'Cancelar', style: 'cancel' },
            { 
              text: 'Iniciar', 
              onPress: async () => {
                try {
                  dispatch(startOSExecution({ 
                    osId: os.id,
                    checkInData: {
                      timestamp: new Date().toISOString(),
                      location: null, // TODO: Implementar GPS
                    }
                  }));
                  Alert.alert('Sucesso', 'OS iniciada com sucesso!');
                  navigation.navigate('OSExecution', { os });
                } catch (error) {
                  Alert.alert('Erro', 'Falha ao iniciar OS');
                }
              }
            },
          ]
        );
        break;
      
      case 'visit':
        navigation.navigate('OSExecution', { os, mode: 'visit' });
        break;
      
      case 'navigate':
        const address = encodeURIComponent(os.endereco);
        const url = `https://www.google.com/maps/search/?api=1&query=${address}`;
        
        try {
          const supported = await Linking.canOpenURL(url);
          if (supported) {
            await Linking.openURL(url);
          } else {
            Alert.alert('Erro', 'Não foi possível abrir o mapa');
          }
        } catch (error) {
          Alert.alert('Erro', 'Falha ao abrir navegação');
        }
        break;
      
      case 'call':
        const phoneNumber = os.cliente_telefone.replace(/\D/g, '');
        const phoneUrl = `tel:${phoneNumber}`;
        
        try {
          const supported = await Linking.canOpenURL(phoneUrl);
          if (supported) {
            await Linking.openURL(phoneUrl);
          } else {
            Alert.alert('Erro', 'Não foi possível fazer a ligação');
          }
        } catch (error) {
          Alert.alert('Erro', 'Falha ao iniciar ligação');
        }
        break;
      
      case 'message':
        // TODO: Implementar integração com WhatsApp/SMS
        Alert.alert('Mensagem', 'Funcionalidade em desenvolvimento');
        break;
      
      default:
        break;
    }
  };

  const handleSuggestionPress = (suggestion) => {
    setSearchQuery(suggestion.label);
  };

  const handleFilterPress = (filterKey) => {
    // Toggle do filtro ativo
    // Por enquanto, apenas abre o modal de filtros
    setShowFilterModal(true);
  };

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
  };

  const getEmptyStateType = () => {
    if (error) return 'error';
    if (isOffline) return 'offline';
    if (searchQuery.trim()) return 'search';
    if (filters.status === 'today') return 'today';
    if (filters.status === 'completed') return 'completed';
    if (Object.values(filters).some(value => 
      typeof value === 'boolean' ? value : value !== 'todas'
    )) return 'filter';
    return 'no-os';
  };

  const handleEmptyStateAction = () => {
    const emptyType = getEmptyStateType();
    
    switch (emptyType) {
      case 'error':
      case 'offline':
        loadOS();
        break;
      case 'search':
        setSearchQuery('');
        break;
      case 'filter':
        setShowFilterModal(true);
        break;
      case 'today':
        setFilters(prev => ({ ...prev, status: 'todas' }));
        break;
      default:
        onRefresh();
        break;
    }
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.status !== 'todas') count++;
    if (filters.prioridade !== 'todas') count++;
    if (filters.data !== 'todas') count++;
    if (filters.apenasMinhas) count++;
    if (filters.comFotos) count++;
    if (filters.assinadas) count++;
    return count;
  };

  if (loading && filteredOS.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Carregando ordens de serviço...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Offline Banner */}
      {isOffline && (
        <View style={styles.offlineBanner}>
          <Icon name="cloud-off" size={16} color="#FFFFFF" />
          <Text style={styles.offlineBannerText}>Modo Offline</Text>
        </View>
      )}

      {/* Barra de busca moderna */}
      <SearchBar
        value={searchQuery}
        onChangeText={setSearchQuery}
        onFilterPress={handleFilterPress}
        suggestions={suggestions}
        onSuggestionPress={handleSuggestionPress}
        placeholder="Buscar OS, cliente, endereço..."
      />

      {/* Header com contadores e filtros */}
      <View style={styles.headerContainer}>
        <View style={styles.countersContainer}>
          <Text style={styles.countText}>
            {filteredOS.length} OS {filteredOS.length === 1 ? 'encontrada' : 'encontradas'}
          </Text>
          {allOS.length !== filteredOS.length && (
            <Text style={styles.totalText}>
              de {allOS.length} total
            </Text>
          )}
        </View>

        <View style={styles.headerActions}>
          {/* Botão de filtros */}
          <TouchableOpacity
            style={[
              styles.filterButton,
              getActiveFiltersCount() > 0 && styles.filterButtonActive
            ]}
            onPress={() => setShowFilterModal(true)}
          >
            <Icon 
              name="filter-list" 
              size={20} 
              color={getActiveFiltersCount() > 0 ? '#FFFFFF' : theme.colors.primary} 
            />
            {getActiveFiltersCount() > 0 && (
              <View style={styles.filterBadge}>
                <Text style={styles.filterBadgeText}>{getActiveFiltersCount()}</Text>
              </View>
            )}
          </TouchableOpacity>

          {/* Botão de ordenação */}
          <TouchableOpacity
            style={styles.sortButton}
            onPress={() => setShowFilterModal(true)}
          >
            <Icon name="sort" size={20} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Lista de OS */}
      <FlatList
        data={filteredOS}
        keyExtractor={(item) => item.id?.toString() || item.numero}
        renderItem={({ item }) => (
          <OSCard
            os={item}
            onPress={handleOSPress}
            onQuickAction={handleQuickAction}
            showQuickActions={true}
          />
        )}
        contentContainerStyle={[
          styles.listContainer,
          filteredOS.length === 0 && styles.emptyListContainer
        ]}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[theme.colors.primary]}
            tintColor={theme.colors.primary}
          />
        }
        ListEmptyComponent={
          <EmptyState
            type={getEmptyStateType()}
            searchTerm={searchQuery}
            onActionPress={handleEmptyStateAction}
          />
        }
        showsVerticalScrollIndicator={false}
        initialNumToRender={10}
        maxToRenderPerBatch={5}
        windowSize={10}
        removeClippedSubviews={true}
      />

      {/* FAB - Nova OS */}
      <TouchableOpacity
        style={styles.fab}
        onPress={() => navigation.navigate('OSExecution')}
        activeOpacity={0.8}
      >
        <Icon name="add" size={24} color="#FFFFFF" />
      </TouchableOpacity>

      {/* Modal de filtros */}
      <FilterModal
        visible={showFilterModal}
        onClose={() => setShowFilterModal(false)}
        filters={filters}
        onFiltersChange={handleFiltersChange}
        osCount={filteredOS.length}
      />
    </View>
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
  offlineBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.colors.warning,
    paddingVertical: 8,
  },
  offlineBannerText: {
    color: '#FFFFFF',
    fontWeight: '600',
    marginLeft: 8,
  },
  headerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.disabled + '20',
  },
  countersContainer: {
    flex: 1,
  },
  countText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  totalText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginTop: 2,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  filterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.primary,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginRight: 8,
    position: 'relative',
  },
  filterButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  filterBadge: {
    position: 'absolute',
    top: -6,
    right: -6,
    backgroundColor: theme.colors.error,
    borderRadius: 8,
    width: 16,
    height: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  filterBadgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  sortButton: {
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.primary,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  listContainer: {
    paddingHorizontal: 16,
    paddingBottom: 80, // Espaço para o FAB
    paddingTop: 8,
  },
  emptyListContainer: {
    flexGrow: 1,
  },
  fab: {
    position: 'absolute',
    bottom: 16,
    right: 16,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: theme.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
});