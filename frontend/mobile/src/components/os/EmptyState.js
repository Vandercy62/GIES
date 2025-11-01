import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { theme } from '../../styles/theme';

export default function EmptyState({ 
  type = 'default',
  title,
  message,
  actionText,
  onActionPress,
  illustration,
  searchTerm,
}) {
  const getStateConfig = () => {
    switch (type) {
      case 'search':
        return {
          icon: 'search-off',
          defaultTitle: 'Nenhuma OS encontrada',
          defaultMessage: searchTerm 
            ? `Não encontramos resultados para "${searchTerm}"`
            : 'Tente ajustar os filtros ou termo de busca',
          actionText: 'Limpar filtros',
          iconColor: theme.colors.textSecondary,
        };
      
      case 'no-os':
        return {
          icon: 'assignment',
          defaultTitle: 'Nenhuma OS disponível',
          defaultMessage: 'Você não possui ordens de serviço no momento',
          actionText: 'Atualizar lista',
          iconColor: theme.colors.textSecondary,
        };
      
      case 'offline':
        return {
          icon: 'cloud-off',
          defaultTitle: 'Você está offline',
          defaultMessage: 'Conecte-se à internet para ver as OS mais recentes',
          actionText: 'Tentar novamente',
          iconColor: theme.colors.warning,
        };
      
      case 'error':
        return {
          icon: 'error-outline',
          defaultTitle: 'Erro ao carregar',
          defaultMessage: 'Não foi possível carregar as ordens de serviço',
          actionText: 'Tentar novamente',
          iconColor: theme.colors.error,
        };
      
      case 'filter':
        return {
          icon: 'filter-list-off',
          defaultTitle: 'Filtros muito restritivos',
          defaultMessage: 'Nenhuma OS corresponde aos filtros aplicados',
          actionText: 'Ajustar filtros',
          iconColor: theme.colors.textSecondary,
        };
      
      case 'today':
        return {
          icon: 'today',
          defaultTitle: 'Nenhuma OS para hoje',
          defaultMessage: 'Você não tem agendamentos para hoje',
          actionText: 'Ver todas as OS',
          iconColor: theme.colors.primary,
        };
      
      case 'completed':
        return {
          icon: 'check-circle-outline',
          defaultTitle: 'Parabéns!',
          defaultMessage: 'Todas as suas OS foram concluídas',
          actionText: 'Ver histórico',
          iconColor: theme.colors.success,
        };
      
      default:
        return {
          icon: 'inbox',
          defaultTitle: 'Lista vazia',
          defaultMessage: 'Não há itens para exibir',
          actionText: 'Atualizar',
          iconColor: theme.colors.textSecondary,
        };
    }
  };

  const config = getStateConfig();

  return (
    <View style={styles.container}>
      {/* Ilustração ou ícone */}
      <View style={styles.iconContainer}>
        {illustration ? (
          <Image source={illustration} style={styles.illustration} />
        ) : (
          <Icon 
            name={config.icon} 
            size={64} 
            color={config.iconColor} 
          />
        )}
      </View>

      {/* Título */}
      <Text style={styles.title}>
        {title || config.defaultTitle}
      </Text>

      {/* Mensagem */}
      <Text style={styles.message}>
        {message || config.defaultMessage}
      </Text>

      {/* Ação */}
      {onActionPress && (
        <TouchableOpacity
          style={[
            styles.actionButton,
            type === 'error' && styles.errorButton,
            type === 'offline' && styles.warningButton,
          ]}
          onPress={onActionPress}
          activeOpacity={0.7}
        >
          <Text style={[
            styles.actionButtonText,
            (type === 'error' || type === 'offline') && styles.actionButtonTextWhite,
          ]}>
            {actionText || config.actionText}
          </Text>
        </TouchableOpacity>
      )}

      {/* Dicas contextuais */}
      {type === 'search' && (
        <View style={styles.tipsContainer}>
          <Text style={styles.tipsTitle}>Dicas de busca:</Text>
          <Text style={styles.tipText}>• Use números da OS (ex: 1234)</Text>
          <Text style={styles.tipText}>• Nome do cliente</Text>
          <Text style={styles.tipText}>• Endereço parcial</Text>
          <Text style={styles.tipText}>• Tipo de serviço</Text>
        </View>
      )}

      {type === 'no-os' && (
        <View style={styles.tipsContainer}>
          <Text style={styles.tipsTitle}>O que fazer:</Text>
          <Text style={styles.tipText}>• Verifique sua conexão</Text>
          <Text style={styles.tipText}>• Atualize a lista puxando para baixo</Text>
          <Text style={styles.tipText}>• Entre em contato com o suporte</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
    paddingVertical: 64,
  },
  iconContainer: {
    marginBottom: 24,
    opacity: 0.7,
  },
  illustration: {
    width: 120,
    height: 120,
    resizeMode: 'contain',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
    textAlign: 'center',
    marginBottom: 8,
  },
  message: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 24,
  },
  actionButton: {
    backgroundColor: theme.colors.primary + '10',
    borderWidth: 1,
    borderColor: theme.colors.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    marginBottom: 24,
  },
  errorButton: {
    backgroundColor: theme.colors.error,
    borderColor: theme.colors.error,
  },
  warningButton: {
    backgroundColor: theme.colors.warning,
    borderColor: theme.colors.warning,
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.primary,
    textAlign: 'center',
  },
  actionButtonTextWhite: {
    color: '#FFFFFF',
  },
  tipsContainer: {
    alignSelf: 'stretch',
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.primary,
  },
  tipsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 8,
  },
  tipText: {
    fontSize: 13,
    color: theme.colors.textSecondary,
    lineHeight: 18,
    marginBottom: 2,
  },
});