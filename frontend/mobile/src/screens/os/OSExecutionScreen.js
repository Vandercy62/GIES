import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Switch,
  Modal,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { theme } from '../../styles/theme';
import {
  startOSExecution,
  finishOSExecution,
  addPhotoToOS,
  addSignatureToOS,
  updateOSObservations,
} from '../../store/slices/osSlice';

const EXECUTION_PHASES = [
  {
    id: 'check_in',
    title: 'Check-in',
    icon: 'location-on',
    description: 'Confirmar chegada no local',
    required: true,
  },
  {
    id: 'photos_before',
    title: 'Fotos do Local',
    icon: 'photo-camera',
    description: 'Documentar estado inicial',
    required: true,
  },
  {
    id: 'execution',
    title: 'Execução',
    icon: 'build',
    description: 'Realizar o serviço',
    required: true,
  },
  {
    id: 'photos_after',
    title: 'Fotos do Resultado',
    icon: 'photo-library',
    description: 'Documentar serviço concluído',
    required: true,
  },
  {
    id: 'signature',
    title: 'Assinatura',
    icon: 'draw',
    description: 'Coletar assinatura do cliente',
    required: true,
  },
  {
    id: 'check_out',
    title: 'Check-out',
    icon: 'check-circle',
    description: 'Finalizar atendimento',
    required: true,
  },
];

export default function OSExecutionScreen({ route, navigation }) {
  const { os, mode = 'execution' } = route.params || {};
  const dispatch = useDispatch();
  
  const [currentPhase, setCurrentPhase] = useState(0);
  const [completedPhases, setCompletedPhases] = useState([]);
  const [osStarted, setOSStarted] = useState(false);
  const [observations, setObservations] = useState('');
  const [showObservationsModal, setShowObservationsModal] = useState(false);
  const [executionData, setExecutionData] = useState({
    checkInTime: null,
    checkOutTime: null,
    photos: [],
    signature: null,
    clientSatisfaction: true,
    materialsUsed: [],
    additionalServices: [],
  });

  useEffect(() => {
    // Se a OS já está em execução, marcar como iniciada
    if (os?.fase_atual === 'execucao') {
      setOSStarted(true);
      setCompletedPhases(['check_in']);
      setCurrentPhase(1);
    }
  }, [os]);

  const handleStartOS = () => {
    Alert.alert(
      'Iniciar Execução',
      `Deseja iniciar ${mode === 'visit' ? 'a visita técnica' : 'a execução'} da OS ${os?.numero}?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Iniciar',
          onPress: () => {
            const now = new Date().toISOString();
            
            dispatch(startOSExecution({
              osId: os.id,
              checkInData: {
                timestamp: now,
                location: null, // TODO: Implementar GPS
              }
            }));

            setOSStarted(true);
            setExecutionData(prev => ({
              ...prev,
              checkInTime: now,
            }));
            setCompletedPhases(['check_in']);
            setCurrentPhase(1);

            Alert.alert('Sucesso', `${mode === 'visit' ? 'Visita' : 'Execução'} iniciada!`);
          }
        },
      ]
    );
  };

  const handlePhaseAction = (phaseId) => {
    switch (phaseId) {
      case 'check_in':
        handleStartOS();
        break;
      
      case 'photos_before':
      case 'photos_after':
        handlePhotoAction(phaseId);
        break;
      
      case 'execution':
        handleExecutionAction();
        break;
      
      case 'signature':
        handleSignatureAction();
        break;
      
      case 'check_out':
        handleCheckOut();
        break;
      
      default:
        break;
    }
  };

  const handlePhotoAction = (phaseId) => {
    Alert.alert(
      'Tirar Fotos',
      `Deseja ${phaseId === 'photos_before' ? 'documentar o estado inicial' : 'documentar o resultado'}?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Câmera',
          onPress: () => {
            // Simular captura de foto
            const newPhoto = {
              id: Date.now(),
              uri: `photo_${Date.now()}.jpg`,
              type: phaseId,
              timestamp: new Date().toISOString(),
            };

            dispatch(addPhotoToOS({
              osId: os.id,
              photo: newPhoto,
            }));

            setExecutionData(prev => ({
              ...prev,
              photos: [...prev.photos, newPhoto],
            }));

            completePhase(phaseId);
            Alert.alert('Sucesso', 'Foto adicionada!');
          }
        },
      ]
    );
  };

  const handleExecutionAction = () => {
    setShowObservationsModal(true);
  };

  const handleSignatureAction = () => {
    Alert.alert(
      'Coletar Assinatura',
      'Deseja coletar a assinatura do cliente?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Coletar',
          onPress: () => {
            // Simular coleta de assinatura
            const signature = {
              id: Date.now(),
              timestamp: new Date().toISOString(),
              clientName: os.cliente_nome,
            };

            dispatch(addSignatureToOS({
              osId: os.id,
              signature,
            }));

            setExecutionData(prev => ({
              ...prev,
              signature,
            }));

            completePhase('signature');
            Alert.alert('Sucesso', 'Assinatura coletada!');
          }
        },
      ]
    );
  };

  const handleCheckOut = () => {
    if (completedPhases.length < EXECUTION_PHASES.length - 1) {
      Alert.alert(
        'Fases Pendentes',
        'Algumas fases ainda não foram concluídas. Deseja continuar mesmo assim?',
        [
          { text: 'Cancelar', style: 'cancel' },
          { text: 'Continuar', onPress: () => finalizeOS() },
        ]
      );
    } else {
      finalizeOS();
    }
  };

  const finalizeOS = () => {
    Alert.alert(
      'Finalizar OS',
      'Deseja finalizar a execução desta OS?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Finalizar',
          onPress: () => {
            const now = new Date().toISOString();
            
            dispatch(finishOSExecution({
              osId: os.id,
              checkOutData: {
                timestamp: now,
                observations,
                clientSatisfaction: executionData.clientSatisfaction,
                materialsUsed: executionData.materialsUsed,
              }
            }));

            setExecutionData(prev => ({
              ...prev,
              checkOutTime: now,
            }));

            Alert.alert(
              'Sucesso',
              'OS finalizada com sucesso!',
              [
                {
                  text: 'OK',
                  onPress: () => navigation.navigate('OSList')
                }
              ]
            );
          }
        },
      ]
    );
  };

  const completePhase = (phaseId) => {
    if (!completedPhases.includes(phaseId)) {
      setCompletedPhases(prev => [...prev, phaseId]);
      
      // Avançar para próxima fase se não for a última
      const currentIndex = EXECUTION_PHASES.findIndex(p => p.id === phaseId);
      if (currentIndex < EXECUTION_PHASES.length - 1) {
        setCurrentPhase(currentIndex + 1);
      }
    }
  };

  const saveObservations = () => {
    dispatch(updateOSObservations({
      osId: os.id,
      observacoes: observations,
    }));

    completePhase('execution');
    setShowObservationsModal(false);
    Alert.alert('Sucesso', 'Observações salvas!');
  };

  const isPhaseCompleted = (phaseId) => completedPhases.includes(phaseId);
  const isPhaseActive = (phaseIndex) => phaseIndex === currentPhase;
  const canExecutePhase = (phaseIndex) => phaseIndex <= currentPhase || isPhaseCompleted(EXECUTION_PHASES[phaseIndex].id);

  const getPhaseStatus = (phase, index) => {
    if (isPhaseCompleted(phase.id)) return 'completed';
    if (isPhaseActive(index)) return 'active';
    if (canExecutePhase(index)) return 'available';
    return 'disabled';
  };

  const renderPhaseCard = (phase, index) => {
    const status = getPhaseStatus(phase, index);
    
    return (
      <TouchableOpacity
        key={phase.id}
        style={[
          styles.phaseCard,
          status === 'completed' && styles.phaseCardCompleted,
          status === 'active' && styles.phaseCardActive,
          status === 'disabled' && styles.phaseCardDisabled,
        ]}
        onPress={() => {
          if (status === 'available' || status === 'active') {
            handlePhaseAction(phase.id);
          }
        }}
        disabled={status === 'disabled'}
        activeOpacity={0.7}
      >
        <View style={styles.phaseHeader}>
          <View style={[
            styles.phaseIconContainer,
            status === 'completed' && styles.phaseIconCompleted,
            status === 'active' && styles.phaseIconActive,
          ]}>
            <Icon 
              name={status === 'completed' ? 'check' : phase.icon} 
              size={24} 
              color={
                status === 'completed' ? '#FFFFFF' :
                status === 'active' ? theme.colors.primary :
                status === 'disabled' ? theme.colors.disabled :
                theme.colors.text
              } 
            />
          </View>
          
          <View style={styles.phaseInfo}>
            <Text style={[
              styles.phaseTitle,
              status === 'completed' && styles.phaseTitleCompleted,
              status === 'active' && styles.phaseTitleActive,
              status === 'disabled' && styles.phaseTitleDisabled,
            ]}>
              {phase.title}
            </Text>
            <Text style={[
              styles.phaseDescription,
              status === 'disabled' && styles.phaseDescriptionDisabled,
            ]}>
              {phase.description}
            </Text>
          </View>

          {phase.required && (
            <View style={styles.requiredBadge}>
              <Text style={styles.requiredText}>Obrigatório</Text>
            </View>
          )}
        </View>

        {status === 'active' && (
          <View style={styles.activeIndicator}>
            <Text style={styles.activeText}>Toque para executar</Text>
          </View>
        )}
      </TouchableOpacity>
    );
  };

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

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>
          {mode === 'visit' ? 'Visita Técnica' : 'Execução'} - OS {os.numero}
        </Text>
        <Text style={styles.subtitle}>{os.cliente_nome}</Text>
        
        {osStarted && (
          <View style={styles.progressContainer}>
            <Text style={styles.progressText}>
              Progresso: {completedPhases.length}/{EXECUTION_PHASES.length}
            </Text>
            <View style={styles.progressBar}>
              <View style={[
                styles.progressFill,
                { width: `${(completedPhases.length / EXECUTION_PHASES.length) * 100}%` }
              ]} />
            </View>
          </View>
        )}
      </View>

      {/* Fases de execução */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {!osStarted ? (
          <View style={styles.startContainer}>
            <Icon name="play-circle-filled" size={64} color={theme.colors.primary} />
            <Text style={styles.startTitle}>
              Pronto para {mode === 'visit' ? 'a visita' : 'iniciar'}?
            </Text>
            <Text style={styles.startDescription}>
              {mode === 'visit' 
                ? 'Realize a visita técnica para avaliar o local e confirmar o serviço'
                : 'Siga as etapas para executar o serviço de forma organizada'
              }
            </Text>
            <TouchableOpacity
              style={styles.startButton}
              onPress={handleStartOS}
            >
              <Icon name="play-arrow" size={20} color="#FFFFFF" />
              <Text style={styles.startButtonText}>
                {mode === 'visit' ? 'Iniciar Visita' : 'Iniciar Execução'}
              </Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.phasesContainer}>
            {EXECUTION_PHASES.map((phase, index) => renderPhaseCard(phase, index))}
          </View>
        )}
      </ScrollView>

      {/* Modal de observações */}
      <Modal
        visible={showObservationsModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowObservationsModal(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowObservationsModal(false)}>
              <Icon name="close" size={24} color={theme.colors.text} />
            </TouchableOpacity>
            <Text style={styles.modalTitle}>Observações da Execução</Text>
            <TouchableOpacity onPress={saveObservations}>
              <Text style={styles.saveText}>Salvar</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalContent}>
            <Text style={styles.inputLabel}>Descreva como foi a execução do serviço:</Text>
            <TextInput
              style={styles.observationsInput}
              placeholder="Ex: Serviço executado conforme especificado, cliente satisfeito..."
              placeholderTextColor={theme.colors.textSecondary}
              value={observations}
              onChangeText={setObservations}
              multiline
              numberOfLines={6}
              textAlignVertical="top"
            />

            <View style={styles.satisfactionContainer}>
              <Text style={styles.inputLabel}>Cliente satisfeito com o resultado?</Text>
              <View style={styles.switchRow}>
                <Text style={styles.switchLabel}>
                  {executionData.clientSatisfaction ? 'Sim' : 'Não'}
                </Text>
                <Switch
                  value={executionData.clientSatisfaction}
                  onValueChange={(value) => 
                    setExecutionData(prev => ({ ...prev, clientSatisfaction: value }))
                  }
                  trackColor={{ false: theme.colors.disabled, true: theme.colors.success + '40' }}
                  thumbColor={executionData.clientSatisfaction ? theme.colors.success : '#FFFFFF'}
                />
              </View>
            </View>
          </ScrollView>
        </View>
      </Modal>
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
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    marginTop: 4,
  },
  progressContainer: {
    marginTop: 12,
  },
  progressText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginBottom: 4,
  },
  progressBar: {
    height: 4,
    backgroundColor: theme.colors.disabled + '30',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: theme.colors.primary,
    borderRadius: 2,
  },
  content: {
    flex: 1,
  },
  startContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  startTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginTop: 24,
    marginBottom: 12,
    textAlign: 'center',
  },
  startDescription: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  startButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 24,
    paddingVertical: 14,
    borderRadius: 8,
  },
  startButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 16,
    marginLeft: 8,
  },
  phasesContainer: {
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  phaseCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    marginBottom: 12,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  phaseCardCompleted: {
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.success,
  },
  phaseCardActive: {
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.primary,
    elevation: 4,
  },
  phaseCardDisabled: {
    opacity: 0.6,
  },
  phaseHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  phaseIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: theme.colors.background,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  phaseIconCompleted: {
    backgroundColor: theme.colors.success,
  },
  phaseIconActive: {
    backgroundColor: theme.colors.primary + '20',
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  phaseInfo: {
    flex: 1,
  },
  phaseTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 2,
  },
  phaseTitleCompleted: {
    color: theme.colors.success,
  },
  phaseTitleActive: {
    color: theme.colors.primary,
  },
  phaseTitleDisabled: {
    color: theme.colors.textSecondary,
  },
  phaseDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  phaseDescriptionDisabled: {
    color: theme.colors.disabled,
  },
  requiredBadge: {
    backgroundColor: theme.colors.warning + '20',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  requiredText: {
    fontSize: 10,
    color: theme.colors.warning,
    fontWeight: '600',
  },
  activeIndicator: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: theme.colors.disabled + '30',
  },
  activeText: {
    fontSize: 12,
    color: theme.colors.primary,
    fontWeight: '600',
    textAlign: 'center',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.disabled + '30',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  saveText: {
    fontSize: 16,
    color: theme.colors.primary,
    fontWeight: '600',
  },
  modalContent: {
    flex: 1,
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 8,
  },
  observationsInput: {
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    padding: 16,
    fontSize: 16,
    color: theme.colors.text,
    minHeight: 120,
    borderWidth: 1,
    borderColor: theme.colors.disabled + '30',
    marginBottom: 24,
  },
  satisfactionContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    padding: 16,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  switchLabel: {
    fontSize: 16,
    color: theme.colors.text,
    fontWeight: '500',
  },
});