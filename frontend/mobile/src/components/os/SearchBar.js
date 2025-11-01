import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  FlatList,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { theme } from '../../styles/theme';

const SEARCH_FILTERS = [
  { key: 'numero', label: 'Número OS', icon: 'tag' },
  { key: 'cliente', label: 'Cliente', icon: 'person' },
  { key: 'endereco', label: 'Endereço', icon: 'location-on' },
  { key: 'servico', label: 'Serviço', icon: 'build' },
];

export default function SearchBar({ 
  value, 
  onChangeText, 
  onFilterPress,
  placeholder = "Buscar OS, cliente, endereço...",
  showFilters = true,
  activeFilters = [],
  suggestions = [],
  onSuggestionPress,
}) {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  const handleFocus = () => {
    setIsFocused(true);
    setShowSuggestions(true);
  };

  const handleBlur = () => {
    setIsFocused(false);
    // Delay para permitir clique em sugestões
    setTimeout(() => setShowSuggestions(false), 150);
  };

  const handleSuggestionPress = (suggestion) => {
    onSuggestionPress?.(suggestion);
    setShowSuggestions(false);
  };

  const renderSuggestion = ({ item }) => (
    <TouchableOpacity
      style={styles.suggestion}
      onPress={() => handleSuggestionPress(item)}
    >
      <Icon 
        name={item.type === 'cliente' ? 'person' : 'search'} 
        size={16} 
        color={theme.colors.textSecondary} 
      />
      <Text style={styles.suggestionText}>{item.label}</Text>
      {item.subtitle && (
        <Text style={styles.suggestionSubtitle}>{item.subtitle}</Text>
      )}
    </TouchableOpacity>
  );

  const renderFilterChip = ({ item }) => (
    <TouchableOpacity
      style={[
        styles.filterChip,
        activeFilters.includes(item.key) && styles.filterChipActive
      ]}
      onPress={() => onFilterPress?.(item.key)}
    >
      <Icon 
        name={item.icon} 
        size={14} 
        color={activeFilters.includes(item.key) ? '#FFFFFF' : theme.colors.primary} 
      />
      <Text style={[
        styles.filterChipText,
        activeFilters.includes(item.key) && styles.filterChipTextActive
      ]}>
        {item.label}
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* Barra de busca */}
      <View style={[
        styles.searchContainer,
        isFocused && styles.searchContainerFocused
      ]}>
        <Icon 
          name="search" 
          size={20} 
          color={isFocused ? theme.colors.primary : theme.colors.textSecondary} 
        />
        
        <TextInput
          style={styles.searchInput}
          placeholder={placeholder}
          placeholderTextColor={theme.colors.textSecondary}
          value={value}
          onChangeText={onChangeText}
          onFocus={handleFocus}
          onBlur={handleBlur}
          returnKeyType="search"
          autoCorrect={false}
          autoCapitalize="none"
        />
        
        {value.length > 0 && (
          <TouchableOpacity 
            onPress={() => onChangeText('')}
            style={styles.clearButton}
          >
            <Icon name="clear" size={20} color={theme.colors.textSecondary} />
          </TouchableOpacity>
        )}

        <TouchableOpacity 
          style={styles.voiceButton}
          onPress={() => {
            // TODO: Implementar busca por voz
          }}
        >
          <Icon name="mic" size={20} color={theme.colors.textSecondary} />
        </TouchableOpacity>
      </View>

      {/* Filtros rápidos */}
      {showFilters && (
        <View style={styles.filtersContainer}>
          <FlatList
            horizontal
            showsHorizontalScrollIndicator={false}
            data={SEARCH_FILTERS}
            keyExtractor={(item) => item.key}
            renderItem={renderFilterChip}
            contentContainerStyle={styles.filtersList}
          />
        </View>
      )}

      {/* Sugestões */}
      {showSuggestions && suggestions.length > 0 && (
        <View style={styles.suggestionsContainer}>
          <FlatList
            data={suggestions.slice(0, 5)} // Máximo 5 sugestões
            keyExtractor={(item, index) => `${item.type}-${index}`}
            renderItem={renderSuggestion}
            showsVerticalScrollIndicator={false}
          />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    zIndex: 1,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 16,
    marginVertical: 8,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  searchContainerFocused: {
    borderColor: theme.colors.primary,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: theme.colors.text,
    marginLeft: 12,
    padding: 0,
  },
  clearButton: {
    padding: 4,
    marginRight: 8,
  },
  voiceButton: {
    padding: 4,
  },
  filtersContainer: {
    marginBottom: 8,
  },
  filtersList: {
    paddingHorizontal: 12,
  },
  filterChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.primary,
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginHorizontal: 4,
  },
  filterChipActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  filterChipText: {
    fontSize: 12,
    color: theme.colors.primary,
    marginLeft: 4,
    fontWeight: '500',
  },
  filterChipTextActive: {
    color: '#FFFFFF',
  },
  suggestionsContainer: {
    backgroundColor: theme.colors.surface,
    marginHorizontal: 16,
    borderRadius: 8,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    maxHeight: 200,
  },
  suggestion: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.disabled + '30',
  },
  suggestionText: {
    fontSize: 14,
    color: theme.colors.text,
    marginLeft: 12,
    flex: 1,
  },
  suggestionSubtitle: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginLeft: 8,
  },
});