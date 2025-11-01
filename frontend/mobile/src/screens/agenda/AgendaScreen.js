import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { useFocusEffect } from '@react-navigation/native';
import { Calendar, LocaleConfig } from 'react-native-calendars';
import Icon from 'react-native-vector-icons/MaterialIcons';

import {
  selectAppointments,
  selectLoading,
  selectCalendarMonth,
  selectSelectedDate,
  selectFilteredAppointments,
  loadAppointments,
  setSelectedDate,
  setCalendarMonth,
  addAppointment,
} from '../../store/slices/agendaSlice';
import { selectIsOffline } from '../../store/slices/offlineSlice';
import { theme } from '../../styles/theme';

// Configuração do calendário em português
LocaleConfig.locales['pt-br'] = {
  monthNames: [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ],
  monthNamesShort: [
    'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
  ],
  dayNames: [
    'Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira',
    'Quinta-feira', 'Sexta-feira', 'Sábado'
  ],
  dayNamesShort: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'],
  today: 'Hoje'
};
LocaleConfig.defaultLocale = 'pt-br';

export default function AgendaScreen({ navigation }) {
  const dispatch = useDispatch();
  const appointments = useSelector(selectAppointments);
  const loading = useSelector(selectLoading);
  const isOffline = useSelector(selectIsOffline);
  const selectedDate = useSelector(selectSelectedDate);
  const calendarMonth = useSelector(selectCalendarMonth);
  const filteredAppointments = useSelector(selectFilteredAppointments);

  const [dayAppointments, setDayAppointments] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [markedDates, setMarkedDates] = useState({});

  // Carregar agendamentos quando a tela ganhar foco
  useFocusEffect(
    useCallback(() => {
      loadAgendamentos();
    }, [])
  );

  // Atualizar agendamentos do dia selecionado
  useEffect(() => {
    updateDayAppointments();
    updateMarkedDates();
  }, [appointments, selectedDate]);

  const loadAgendamentos = async () => {
    try {
      await dispatch(loadAppointments()).unwrap();
    } catch (error) {
      if (!isOffline) {
        Alert.alert('Erro', 'Falha ao carregar agendamentos');
      }
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadAgendamentos();
    setRefreshing(false);
  };

  const updateDayAppointments = () => {
    const dayAppts = appointments.filter(appt => 
      appt.date?.startsWith(selectedDate)
    );
    
    // Ordenar por horário
    dayAppts.sort((a, b) => {
      const timeA = a.time || '00:00';
      const timeB = b.time || '00:00';
      return timeA.localeCompare(timeB);
    });

    setDayAppointments(dayAppts);
  };

  const updateMarkedDates = () => {
    const marked = {};
    
    // Marcar data selecionada
    marked[selectedDate] = {
      selected: true,
      selectedColor: theme.colors.primary,
    };

    // Marcar datas com agendamentos
    appointments.forEach(appt => {
      if (appt.date) {
        const date = appt.date.split('T')[0];
        
        if (date === selectedDate) {
          // Data selecionada com agendamento
          marked[date] = {
            selected: true,
            selectedColor: theme.colors.primary,
            marked: true,
            dotColor: '#FFFFFF',
          };
        } else {
          // Data com agendamento
          marked[date] = {
            marked: true,
            dotColor: theme.colors.primary,
          };
        }
      }
    });

    setMarkedDates(marked);
  };

  const formatTime = (timeString) => {
    if (!timeString) return '';
    return timeString.substring(0, 5); // HH:MM
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmado': return theme.colors.success;
      case 'pendente': return theme.colors.warning;
      case 'cancelado': return theme.colors.error;
      case 'realizado': return theme.colors.primary;
      default: return theme.colors.textSecondary;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'confirmado': return 'check-circle';
      case 'pendente': return 'schedule';
      case 'cancelado': return 'cancel';
      case 'realizado': return 'task-alt';
      default: return 'help';
    }
  };

  const handleDateSelect = (day) => {
    dispatch(setSelectedDate(day.dateString));
  };

  const handleAppointmentPress = (appointment) => {
    navigation.navigate('AgendaDetails', { appointment });
  };

  const handleNewAppointment = () => {
    navigation.navigate('CreateAppointment', { 
      selectedDate,
      onSuccess: () => {
        // Recarregar appointments após criar
        loadAgendamentos();
      }
    });
  };

  const renderAppointmentItem = (appointment, index) => (
    <TouchableOpacity
      key={appointment.id || index}
      style={styles.appointmentCard}
      onPress={() => handleAppointmentPress(appointment)}
      activeOpacity={0.7}
    >
      <View style={styles.appointmentTime}>
        <Text style={styles.timeText}>{formatTime(appointment.time)}</Text>
        <View style={[
          styles.statusDot,
          { backgroundColor: getStatusColor(appointment.status) }
        ]} />
      </View>

      <View style={styles.appointmentContent}>
        <View style={styles.appointmentHeader}>
          <Text style={styles.appointmentTitle}>{appointment.title}</Text>
          <Icon
            name={getStatusIcon(appointment.status)}
            size={16}
            color={getStatusColor(appointment.status)}
          />
        </View>

        <Text style={styles.clienteName}>{appointment.clientName}</Text>
        
        {appointment.location && (
          <View style={styles.addressContainer}>
            <Icon name="location-on" size={14} color={theme.colors.textSecondary} />
            <Text style={styles.addressText} numberOfLines={1}>
              {appointment.location}
            </Text>
          </View>
        )}

        {appointment.notes && (
          <Text style={styles.observacoes} numberOfLines={2}>
            {appointment.notes}
          </Text>
        )}
      </View>

      <View style={styles.appointmentActions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => {/* TODO: Ação rápida */}}
        >
          <Icon name="phone" size={18} color={theme.colors.primary} />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  const renderEmptyDay = () => (
    <View style={styles.emptyDay}>
      <Icon name="event-available" size={48} color={theme.colors.disabled} />
      <Text style={styles.emptyDayText}>Nenhum agendamento para este dia</Text>
      <TouchableOpacity
        style={styles.newAppointmentButton}
        onPress={handleNewAppointment}
      >
        <Text style={styles.newAppointmentButtonText}>Novo Agendamento</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading && appointments.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Carregando agenda...</Text>
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

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={[theme.colors.primary]}
            tintColor={theme.colors.primary}
          />
        }
      >
        {/* Calendário */}
        <View style={styles.calendarContainer}>
          <Calendar
            current={selectedDate}
            onDayPress={handleDateSelect}
            markedDates={markedDates}
            theme={{
              backgroundColor: theme.colors.surface,
              calendarBackground: theme.colors.surface,
              textSectionTitleColor: theme.colors.text,
              selectedDayBackgroundColor: theme.colors.primary,
              selectedDayTextColor: '#FFFFFF',
              todayTextColor: theme.colors.primary,
              dayTextColor: theme.colors.text,
              textDisabledColor: theme.colors.disabled,
              dotColor: theme.colors.primary,
              selectedDotColor: '#FFFFFF',
              arrowColor: theme.colors.primary,
              monthTextColor: theme.colors.text,
              indicatorColor: theme.colors.primary,
              textDayFontSize: 16,
              textMonthFontSize: 18,
              textDayHeaderFontSize: 14,
            }}
            firstDay={1} // Segunda-feira como primeiro dia
          />
        </View>

        {/* Agendamentos do Dia */}
        <View style={styles.dayAppointmentsContainer}>
          <View style={styles.dayHeader}>
            <Text style={styles.dayTitle}>
              {new Date(selectedDate).toLocaleDateString('pt-BR', {
                weekday: 'long',
                day: 'numeric',
                month: 'long'
              })}
            </Text>
            <Text style={styles.appointmentCount}>
              {dayAppointments.length} agendamento{dayAppointments.length !== 1 ? 's' : ''}
            </Text>
          </View>

          {dayAppointments.length > 0 ? (
            <View style={styles.appointmentsList}>
              {dayAppointments.map((appointment, index) => 
                renderAppointmentItem(appointment, index)
              )}
            </View>
          ) : (
            renderEmptyDay()
          )}
        </View>
      </ScrollView>

      {/* FAB - Novo Agendamento */}
      <TouchableOpacity
        style={styles.fab}
        onPress={handleNewAppointment}
        activeOpacity={0.8}
      >
        <Icon name="add" size={24} color="#FFFFFF" />
      </TouchableOpacity>
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
  scrollView: {
    flex: 1,
  },
  calendarContainer: {
    backgroundColor: theme.colors.surface,
    margin: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  dayAppointmentsContainer: {
    margin: 16,
    marginTop: 0,
  },
  dayHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  dayTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    textTransform: 'capitalize',
  },
  appointmentCount: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  appointmentsList: {
    gap: 12,
  },
  appointmentCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  appointmentTime: {
    alignItems: 'center',
    marginRight: 16,
    minWidth: 60,
  },
  timeText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: 4,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  appointmentContent: {
    flex: 1,
  },
  appointmentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  appointmentTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    flex: 1,
  },
  clienteName: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 4,
  },
  addressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  addressText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginLeft: 4,
    flex: 1,
  },
  observacoes: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    fontStyle: 'italic',
  },
  appointmentActions: {
    marginLeft: 12,
  },
  actionButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  emptyDay: {
    alignItems: 'center',
    paddingVertical: 48,
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
  },
  emptyDayText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    marginTop: 16,
    marginBottom: 24,
  },
  newAppointmentButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  newAppointmentButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
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