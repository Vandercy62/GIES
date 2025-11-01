import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Linking,
  Image,
  Dimensions,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { theme } from '../../styles/theme';

const { width } = Dimensions.get('window');

const STATUS_CONFIG = {
  'solicitacao': {
    color: '#FF9800',
    icon: 'pending',
    label: 'Solicitação',
    nextAction: 'Criar Orçamento',
    nextIcon: 'description',
  },
  'orcamento': {
    color: '#2196F3',
    icon: 'description',
    label: 'Orçamento',
    nextAction: 'Aguardar Aprovação',
    nextIcon: 'approval',
  },
  'aprovacao': {
    color: '#9C27B0',
    icon: 'approval',
    label: 'Aprovação',
    nextAction: 'Agendar Visita',
    nextIcon: 'schedule',
  },
  'agendamento': {
    color: '#3F51B5',
    icon: 'schedule',
    label: 'Agendamento',
    nextAction: 'Iniciar Visita',
    nextIcon: 'engineering',
  },
  'visita_tecnica': {
    color: '#3F51B5',
    icon: 'engineering',
    label: 'Visita Técnica',
    nextAction: 'Iniciar Execução',
    nextIcon: 'build',
  },
  'execucao': {
    color: '#4CAF50',
    icon: 'build',
    label: 'Execução',
    nextAction: 'Finalizar',
    nextIcon: 'local-shipping',
  },
  'entrega': {
    color: '#4CAF50',
    icon: 'local-shipping',
    label: 'Entrega',
    nextAction: 'Concluir',
    nextIcon: 'check-circle',
  },
  'pos_venda': {
    color: '#9E9E9E',
    icon: 'check-circle',
    label: 'Concluída',
    nextAction: null,
    nextIcon: null,
  },
};

export default function OSDetailsScreen({ route, navigation }) {
  const { os } = route.params || {};
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  if (!os) {
    return (
      <View style={styles.errorContainer}>
        <Icon name="error-outline" size={64} color={theme.colors.error} />
        <Text style={styles.errorText}>OS não encontrada</Text>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>Voltar</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const statusConfig = STATUS_CONFIG[os.fase_atual] || STATUS_CONFIG['solicitacao'];

  const handleAction = async (action) => {
    switch (action) {
      case 'execute':
        navigation.navigate('OSExecution', { os });
        break;
      
      case 'edit':
        // TODO: Implementar edição de OS
        Alert.alert('Editar OS', 'Funcionalidade em desenvolvimento');
        break;
      
      case 'call':
        if (os.cliente_telefone) {
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
        }
        break;
      
      case 'navigate':
        if (os.endereco) {
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
        }
        break;
      
      case 'share':
        // TODO: Implementar compartilhamento
        Alert.alert('Compartilhar', 'Funcionalidade em desenvolvimento');
        break;
      
      case 'next_phase':
        Alert.alert(
          'Avançar Fase',
          `Deseja ${statusConfig.nextAction?.toLowerCase()}?`,
          [
            { text: 'Cancelar', style: 'cancel' },
            { 
              text: 'Confirmar', 
              onPress: () => {
                Alert.alert('Sucesso', 'Fase avançada com sucesso!');
                // TODO: Implementar mudança de fase
              }
            },
          ]
        );
        break;
      
      default:
        break;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Não definida';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatTime = (timeString) => {
    if (!timeString) return '';
    return timeString.substring(0, 5);
  };

  const formatCurrency = (value) => {
    if (!value) return 'Não informado';
    return `R$ ${parseFloat(value).toFixed(2).replace('.', ',')}`;
  };

  const renderInfoSection = (title, children) => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );

  const renderInfoRow = (icon, label, value, onPress) => (
    <TouchableOpacity
      style={styles.infoRow}
      onPress={onPress}
      disabled={!onPress}
      activeOpacity={onPress ? 0.7 : 1}
    >
      <Icon name={icon} size={20} color={theme.colors.primary} />
      <View style={styles.infoContent}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={[
          styles.infoValue,
          onPress && { color: theme.colors.primary }
        ]}>
          {value}
        </Text>
      </View>
      {onPress && (
        <Icon name="chevron-right" size={20} color={theme.colors.textSecondary} />
      )}
    </TouchableOpacity>
  );

  const renderPhotosSection = () => {
    if (!os.fotos || os.fotos.length === 0) return null;

    return renderInfoSection(
      `Fotos (${os.fotos.length})`,
      <View style={styles.photosContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {os.fotos.map((foto, index) => (
            <TouchableOpacity
              key={index}
              style={styles.photoContainer}
              onPress={() => {
                // TODO: Implementar visualização em tela cheia
                Alert.alert('Foto', 'Visualização em desenvolvimento');
              }}
            >
              <Image
                source={{ uri: foto }}
                style={styles.photo}
                defaultSource={require('../../assets/placeholder-image.png')}
              />
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <Text style={styles.osNumber}>OS #{os.numero}</Text>
          <View style={styles.headerActions}>
            <TouchableOpacity
              style={styles.headerButton}
              onPress={() => handleAction('share')}
            >
              <Icon name="share" size={24} color={theme.colors.text} />
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.headerButton}
              onPress={() => handleAction('edit')}
            >
              <Icon name="edit" size={24} color={theme.colors.text} />
            </TouchableOpacity>
          </View>
        </View>

        <View style={[
          styles.statusBadge, 
          { backgroundColor: statusConfig.color + '20' }
        ]}>
          <Icon 
            name={statusConfig.icon} 
            size={16} 
            color={statusConfig.color} 
          />
          <Text style={[
            styles.statusText, 
            { color: statusConfig.color }
          ]}>
            {statusConfig.label}
          </Text>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Cliente */}
        {renderInfoSection(
          'Cliente',
          <View>
            {renderInfoRow(
              'person',
              'Nome',
              os.cliente_nome || 'Não informado'
            )}
            {os.cliente_telefone && renderInfoRow(
              'phone',
              'Telefone',
              os.cliente_telefone,
              () => handleAction('call')
            )}
            {os.endereco && renderInfoRow(
              'location-on',
              'Endereço',
              os.endereco,
              () => handleAction('navigate')
            )}
          </View>
        )}

        {/* Serviço */}
        {renderInfoSection(
          'Serviço',
          <View>
            {renderInfoRow(
              'build',
              'Descrição',
              os.descricao_servico || 'Não informado'
            )}
            {renderInfoRow(
              'attach-money',
              'Valor Estimado',
              formatCurrency(os.valor_estimado)
            )}
            {os.prioridade && renderInfoRow(
              'priority-high',
              'Prioridade',
              os.prioridade.charAt(0).toUpperCase() + os.prioridade.slice(1)
            )}
          </View>
        )}

        {/* Agendamento */}
        {renderInfoSection(
          'Agendamento',
          <View>
            {renderInfoRow(
              'schedule',
              'Data',
              formatDate(os.data_agendamento)
            )}
            {os.hora_agendamento && renderInfoRow(
              'access-time',
              'Horário',
              formatTime(os.hora_agendamento)
            )}
          </View>
        )}

        {/* Execução */}
        {(os.observacoes_tecnico || os.assinatura_cliente) && renderInfoSection(
          'Execução',
          <View>
            {os.observacoes_tecnico && renderInfoRow(
              'note',
              'Observações do Técnico',
              os.observacoes_tecnico
            )}
            {os.assinatura_cliente && renderInfoRow(
              'draw',
              'Assinatura do Cliente',
              'Coletada',
              () => {
                // TODO: Visualizar assinatura
                Alert.alert('Assinatura', 'Visualização em desenvolvimento');
              }
            )}
          </View>
        )}

        {/* Fotos */}
        {renderPhotosSection()}

        {/* Histórico */}
        {renderInfoSection(
          'Histórico',
          <View>
            {renderInfoRow(
              'add-circle',
              'Criada em',
              new Date(os.created_at).toLocaleDateString('pt-BR')
            )}
          </View>
        )}
      </ScrollView>

      {/* Ações */}
      <View style={styles.actionsContainer}>
        {/* Ação principal baseada na fase */}
        {statusConfig.nextAction && (
          <TouchableOpacity
            style={[styles.actionButton, styles.primaryButton]}
            onPress={() => handleAction('next_phase')}
          >
            <Icon 
              name={statusConfig.nextIcon} 
              size={20} 
              color="#FFFFFF" 
            />
            <Text style={styles.primaryButtonText}>
              {statusConfig.nextAction}
            </Text>
          </TouchableOpacity>
        )}

        {/* Executar OS (sempre disponível para visita técnica e execução) */}
        {['visita_tecnica', 'execucao'].includes(os.fase_atual) && (
          <TouchableOpacity
            style={[styles.actionButton, styles.executeButton]}
            onPress={() => handleAction('execute')}
          >
            <Icon name="play-arrow" size={20} color="#FFFFFF" />
            <Text style={styles.executeButtonText}>
              {os.fase_atual === 'visita_tecnica' ? 'Realizar Visita' : 'Executar Serviço'}
            </Text>
          </TouchableOpacity>
        )}

        {/* Ações secundárias */}
        <View style={styles.secondaryActions}>
          {os.cliente_telefone && (
            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => handleAction('call')}
            >
              <Icon name="phone" size={20} color={theme.colors.primary} />
              <Text style={styles.secondaryButtonText}>Ligar</Text>
            </TouchableOpacity>
          )}

          {os.endereco && (
            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => handleAction('navigate')}
            >
              <Icon name="directions" size={20} color={theme.colors.primary} />
              <Text style={styles.secondaryButtonText}>Navegar</Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => handleAction('share')}
          >
            <Icon name="share" size={20} color={theme.colors.primary} />
            <Text style={styles.secondaryButtonText}>Compartilhar</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
    paddingHorizontal: 32,
  },
  errorText: {
    fontSize: 18,
    color: theme.colors.error,
    marginTop: 16,
    marginBottom: 24,
  },
  backButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  backButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  header: {
    backgroundColor: theme.colors.surface,
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.disabled + '20',
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  osNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  headerActions: {
    flexDirection: 'row',
  },
  headerButton: {
    padding: 8,
    marginLeft: 8,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  statusText: {
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 6,
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
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.disabled + '20',
  },
  infoContent: {
    flex: 1,
    marginLeft: 12,
  },
  infoLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    fontWeight: '500',
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 15,
    color: theme.colors.text,
    lineHeight: 20,
  },
  photosContainer: {
    marginTop: 8,
  },
  photoContainer: {
    marginRight: 12,
    borderRadius: 8,
    overflow: 'hidden',
  },
  photo: {
    width: 80,
    height: 80,
    backgroundColor: theme.colors.disabled + '30',
  },
  actionsContainer: {
    backgroundColor: theme.colors.surface,
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderTopWidth: 1,
    borderTopColor: theme.colors.disabled + '20',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 8,
    marginBottom: 12,
  },
  primaryButton: {
    backgroundColor: theme.colors.primary,
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 16,
    marginLeft: 8,
  },
  executeButton: {
    backgroundColor: theme.colors.success,
  },
  executeButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 16,
    marginLeft: 8,
  },
  secondaryActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  secondaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.primary,
    backgroundColor: theme.colors.surface,
  },
  secondaryButtonText: {
    color: theme.colors.primary,
    fontWeight: '600',
    marginLeft: 6,
  },
});