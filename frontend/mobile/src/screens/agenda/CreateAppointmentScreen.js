import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import DateTimePicker from '@react-native-community/datetimepicker';
import { Picker } from '@react-native-picker/picker';
import Icon from 'react-native-vector-icons/MaterialIcons';
import moment from 'moment';

import {
  addAppointment,
  updateAppointment,
  selectLoading,
} from '../../store/slices/agendaSlice';
import { theme } from '../../styles/theme';

const APPOINTMENT_TYPES = [
  { label: 'Visita Técnica', value: 'visita_tecnica' },
  { label: 'Instalação', value: 'instalacao' },
  { label: 'Manutenção', value: 'manutencao' },
  { label: 'Orçamento', value: 'orcamento' },
  { label: 'Entrega', value: 'entrega' },
  { label: 'Reunião', value: 'reuniao' },
  { label: 'Outros', value: 'outros' },
];

const APPOINTMENT_STATUS = [
  { label: 'Pendente', value: 'pendente' },
  { label: 'Confirmado', value: 'confirmado' },
  { label: 'Em Andamento', value: 'em_andamento' },
  { label: 'Realizado', value: 'realizado' },
  { label: 'Cancelado', value: 'cancelado' },
];

const PRIORITY_LEVELS = [
  { label: 'Baixa', value: 'baixa' },
  { label: 'Normal', value: 'normal' },
  { label: 'Alta', value: 'alta' },
  { label: 'Urgente', value: 'urgente' },
];

export default function CreateAppointmentScreen({ navigation, route }) {
  const dispatch = useDispatch();
  const loading = useSelector(selectLoading);
  
  // Props da rota
  const { selectedDate, appointment, isEdit = false } = route.params || {};

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    clientName: '',
    clientPhone: '',
    clientEmail: '',
    location: '',
    type: 'visita_tecnica',
    status: 'pendente',
    priority: 'normal',
    date: selectedDate || moment().format('YYYY-MM-DD'),
    time: moment().format('HH:mm'),
    duration: 60, // em minutos
    notes: '',
    reminderMinutes: 30,
  });

  // UI state
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (isEdit && appointment) {
      // Carregar dados do agendamento para edição
      setFormData({
        title: appointment.title || '',
        description: appointment.description || '',
        clientName: appointment.clientName || '',
        clientPhone: appointment.clientPhone || '',
        clientEmail: appointment.clientEmail || '',
        location: appointment.location || '',
        type: appointment.type || 'visita_tecnica',
        status: appointment.status || 'pendente',
        priority: appointment.priority || 'normal',
        date: appointment.date || moment().format('YYYY-MM-DD'),
        time: appointment.time || moment().format('HH:mm'),
        duration: appointment.duration || 60,
        notes: appointment.notes || '',
        reminderMinutes: appointment.reminderMinutes || 30,
      });
    }

    // Configurar header da tela
    navigation.setOptions({
      title: isEdit ? 'Editar Agendamento' : 'Novo Agendamento',
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
  }, [navigation, isEdit, appointment, loading]);

  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Limpar erro do campo quando usuário começar a digitar
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Título é obrigatório';
    }

    if (!formData.clientName.trim()) {
      newErrors.clientName = 'Nome do cliente é obrigatório';
    }

    if (!formData.date) {
      newErrors.date = 'Data é obrigatória';
    }

    if (!formData.time) {
      newErrors.time = 'Horário é obrigatório';
    }

    // Validar horário não pode ser no passado (apenas para novos agendamentos)
    if (!isEdit) {
      const appointmentDateTime = moment(`${formData.date} ${formData.time}`);
      if (appointmentDateTime.isBefore(moment())) {
        newErrors.time = 'Não é possível agendar no passado';
      }
    }

    // Validar email se fornecido
    if (formData.clientEmail && !isValidEmail(formData.clientEmail)) {
      newErrors.clientEmail = 'Email inválido';
    }

    // Validar telefone se fornecido
    if (formData.clientPhone && !isValidPhone(formData.clientPhone)) {
      newErrors.clientPhone = 'Telefone inválido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const isValidPhone = (phone) => {
    const phoneRegex = /^\(\d{2}\)\s?\d{4,5}-?\d{4}$/;
    return phoneRegex.test(phone);
  };

  const handleSave = async () => {
    if (!validateForm()) {
      Alert.alert('Erro', 'Por favor, corrija os campos marcados');
      return;
    }

    try {
      const appointmentData = {
        ...formData,
        id: isEdit ? appointment.id : undefined,
        updatedAt: new Date().toISOString(),
      };

      if (isEdit) {
        await dispatch(updateAppointment(appointmentData)).unwrap();
        Alert.alert('Sucesso', 'Agendamento atualizado com sucesso');
      } else {
        await dispatch(addAppointment(appointmentData)).unwrap();
        Alert.alert('Sucesso', 'Agendamento criado com sucesso');
      }

      navigation.goBack();
    } catch (error) {
      Alert.alert('Erro', error.message || 'Falha ao salvar agendamento');
    }
  };

  const handleDateChange = (event, selectedDate) => {
    setShowDatePicker(false);
    if (selectedDate) {
      updateFormData('date', moment(selectedDate).format('YYYY-MM-DD'));
    }
  };

  const handleTimeChange = (event, selectedTime) => {
    setShowTimePicker(false);
    if (selectedTime) {
      updateFormData('time', moment(selectedTime).format('HH:mm'));
    }
  };

  const formatPhoneInput = (text) => {
    // Remove todos os caracteres não numéricos
    const numbers = text.replace(/\D/g, '');
    
    // Aplica a máscara (XX) XXXXX-XXXX
    if (numbers.length <= 2) {
      return `(${numbers}`;
    } else if (numbers.length <= 7) {
      return `(${numbers.slice(0, 2)}) ${numbers.slice(2)}`;
    } else {
      return `(${numbers.slice(0, 2)}) ${numbers.slice(2, 7)}-${numbers.slice(7, 11)}`;
    }
  };

  const renderFormField = (label, value, onChangeText, options = {}) => {
    const {
      placeholder,
      keyboardType,
      multiline,
      numberOfLines,
      error,
      editable = true,
      onPress,
      rightIcon,
    } = options;

    return (
      <View style={styles.fieldContainer}>
        <Text style={styles.fieldLabel}>{label}</Text>
        <TouchableOpacity
          style={[
            styles.fieldInput,
            error && styles.fieldInputError,
            !editable && styles.fieldInputDisabled,
          ]}
          onPress={onPress}
          disabled={editable}
          activeOpacity={onPress ? 0.7 : 1}
        >
          <TextInput
            style={[styles.textInput, multiline && styles.textInputMultiline]}
            value={value}
            onChangeText={onChangeText}
            placeholder={placeholder}
            placeholderTextColor={theme.colors.disabled}
            keyboardType={keyboardType}
            multiline={multiline}
            numberOfLines={numberOfLines}
            editable={editable}
          />
          {rightIcon && (
            <Icon name={rightIcon} size={20} color={theme.colors.textSecondary} />
          )}
        </TouchableOpacity>
        {error && <Text style={styles.fieldError}>{error}</Text>}
      </View>
    );
  };

  const renderPickerField = (label, value, onValueChange, items, error) => (
    <View style={styles.fieldContainer}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <View style={[styles.fieldInput, error && styles.fieldInputError]}>
        <Picker
          selectedValue={value}
          onValueChange={onValueChange}
          style={styles.picker}
        >
          {items.map(item => (
            <Picker.Item
              key={item.value}
              label={item.label}
              value={item.value}
            />
          ))}
        </Picker>
      </View>
      {error && <Text style={styles.fieldError}>{error}</Text>}
    </View>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Informações Básicas */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Informações Básicas</Text>
          
          {renderFormField(
            'Título*',
            formData.title,
            (text) => updateFormData('title', text),
            {
              placeholder: 'Ex: Visita técnica para orçamento',
              error: errors.title,
            }
          )}

          {renderFormField(
            'Descrição',
            formData.description,
            (text) => updateFormData('description', text),
            {
              placeholder: 'Descreva os detalhes do agendamento',
              multiline: true,
              numberOfLines: 3,
            }
          )}

          {renderPickerField(
            'Tipo de Agendamento',
            formData.type,
            (value) => updateFormData('type', value),
            APPOINTMENT_TYPES
          )}

          {renderPickerField(
            'Status',
            formData.status,
            (value) => updateFormData('status', value),
            APPOINTMENT_STATUS
          )}

          {renderPickerField(
            'Prioridade',
            formData.priority,
            (value) => updateFormData('priority', value),
            PRIORITY_LEVELS
          )}
        </View>

        {/* Informações do Cliente */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Cliente</Text>
          
          {renderFormField(
            'Nome do Cliente*',
            formData.clientName,
            (text) => updateFormData('clientName', text),
            {
              placeholder: 'Nome completo do cliente',
              error: errors.clientName,
            }
          )}

          {renderFormField(
            'Telefone',
            formData.clientPhone,
            (text) => updateFormData('clientPhone', formatPhoneInput(text)),
            {
              placeholder: '(11) 99999-9999',
              keyboardType: 'phone-pad',
              error: errors.clientPhone,
            }
          )}

          {renderFormField(
            'Email',
            formData.clientEmail,
            (text) => updateFormData('clientEmail', text.toLowerCase()),
            {
              placeholder: 'cliente@email.com',
              keyboardType: 'email-address',
              error: errors.clientEmail,
            }
          )}
        </View>

        {/* Data e Horário */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Data e Horário</Text>
          
          {renderFormField(
            'Data*',
            moment(formData.date).format('DD/MM/YYYY'),
            null,
            {
              editable: false,
              onPress: () => setShowDatePicker(true),
              rightIcon: 'date-range',
              error: errors.date,
            }
          )}

          {renderFormField(
            'Horário*',
            formData.time,
            null,
            {
              editable: false,
              onPress: () => setShowTimePicker(true),
              rightIcon: 'access-time',
              error: errors.time,
            }
          )}

          {renderFormField(
            'Duração (minutos)',
            formData.duration.toString(),
            (text) => updateFormData('duration', parseInt(text) || 60),
            {
              keyboardType: 'numeric',
              placeholder: '60',
            }
          )}
        </View>

        {/* Localização e Observações */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Detalhes Adicionais</Text>
          
          {renderFormField(
            'Localização',
            formData.location,
            (text) => updateFormData('location', text),
            {
              placeholder: 'Endereço ou local do agendamento',
              multiline: true,
              numberOfLines: 2,
            }
          )}

          {renderFormField(
            'Observações',
            formData.notes,
            (text) => updateFormData('notes', text),
            {
              placeholder: 'Observações adicionais',
              multiline: true,
              numberOfLines: 3,
            }
          )}

          {renderFormField(
            'Lembrete (minutos antes)',
            formData.reminderMinutes.toString(),
            (text) => updateFormData('reminderMinutes', parseInt(text) || 30),
            {
              keyboardType: 'numeric',
              placeholder: '30',
            }
          )}
        </View>

        {/* Botões de Ação */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, styles.saveButton]}
            onPress={handleSave}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <>
                <Icon name="check" size={20} color="#FFFFFF" />
                <Text style={styles.saveButtonText}>
                  {isEdit ? 'Atualizar' : 'Criar'} Agendamento
                </Text>
              </>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.cancelButton]}
            onPress={() => navigation.goBack()}
            disabled={loading}
          >
            <Icon name="close" size={20} color={theme.colors.textSecondary} />
            <Text style={styles.cancelButtonText}>Cancelar</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Date Picker */}
      {showDatePicker && (
        <DateTimePicker
          value={moment(formData.date).toDate()}
          mode="date"
          display="default"
          onChange={handleDateChange}
          minimumDate={new Date()}
        />
      )}

      {/* Time Picker */}
      {showTimePicker && (
        <DateTimePicker
          value={moment(`${formData.date} ${formData.time}`).toDate()}
          mode="time"
          display="default"
          onChange={handleTimeChange}
        />
      )}
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 16,
  },
  fieldContainer: {
    marginBottom: 16,
  },
  fieldLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 8,
  },
  fieldInput: {
    backgroundColor: theme.colors.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.border,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    minHeight: 48,
  },
  fieldInputError: {
    borderColor: theme.colors.error,
  },
  fieldInputDisabled: {
    backgroundColor: theme.colors.disabled + '20',
  },
  textInput: {
    flex: 1,
    fontSize: 16,
    color: theme.colors.text,
    paddingVertical: 12,
  },
  textInputMultiline: {
    paddingVertical: 12,
    textAlignVertical: 'top',
  },
  fieldError: {
    fontSize: 12,
    color: theme.colors.error,
    marginTop: 4,
  },
  picker: {
    flex: 1,
    height: 40,
  },
  buttonContainer: {
    marginTop: 24,
    marginBottom: 32,
    gap: 12,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 8,
    gap: 8,
  },
  saveButton: {
    backgroundColor: theme.colors.primary,
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  cancelButton: {
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.textSecondary,
  },
});