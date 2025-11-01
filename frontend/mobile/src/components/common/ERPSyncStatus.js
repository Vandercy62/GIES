/**
 * Componente de Status de Sincronização
 * Mostra status da conexão com ERP em tempo real
 */

import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { theme } from '../../styles/theme';

import {
  selectIsOnline,
  selectSyncInProgress,
  selectLastSync,
  selectPendingSync,
  syncAllData,
  checkConnectivity,
  processPendingSync
} from '../../store/slices/erpSyncSlice';

export default function ERPSyncStatus() {
  const dispatch = useDispatch();
  const isOnline = useSelector(selectIsOnline);
  const syncInProgress = useSelector(selectSyncInProgress);
  const lastSync = useSelector(selectLastSync);
  const pendingSync = useSelector(selectPendingSync);
  
  const [lastSyncFormatted, setLastSyncFormatted] = useState('');

  useEffect(() => {
    if (lastSync) {
      const syncDate = new Date(lastSync);
      const now = new Date();
      const diffMs = now - syncDate;
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 1) {
        setLastSyncFormatted('Agora');
      } else if (diffMins < 60) {
        setLastSyncFormatted(`${diffMins}min atrás`);
      } else {
        const diffHours = Math.floor(diffMins / 60);
        setLastSyncFormatted(`${diffHours}h atrás`);
      }
    }
  }, [lastSync]);

  const handleSync = () => {
    if (!syncInProgress) {
      dispatch(syncAllData());
    }
  };

  const handleProcessPending = () => {
    if (pendingSync > 0) {
      dispatch(processPendingSync());
    }
  };

  const handleCheckConnectivity = () => {
    dispatch(checkConnectivity());
  };

  const getStatusColor = () => {
    if (syncInProgress) return theme.colors.warning;
    if (!isOnline) return theme.colors.error;
    if (pendingSync > 0) return theme.colors.warning;
    return theme.colors.success;
  };

  const getStatusText = () => {
    if (syncInProgress) return 'Sincronizando...';
    if (!isOnline) return 'Offline';
    if (pendingSync > 0) return `${pendingSync} pendente(s)`;
    return 'Online';
  };

  const getStatusIcon = () => {
    if (syncInProgress) return 'sync';
    if (!isOnline) return 'cloud-off';
    if (pendingSync > 0) return 'cloud-upload';
    return 'cloud-done';
  };

  return (
    <View style={styles.container}>
      <View style={styles.statusRow}>
        <View style={[styles.statusIndicator, { backgroundColor: getStatusColor() }]}>
          <Icon name={getStatusIcon()} size={16} color="white" />
        </View>
        <Text style={styles.statusText}>{getStatusText()}</Text>
        {lastSyncFormatted && (
          <Text style={styles.lastSyncText}>• {lastSyncFormatted}</Text>
        )}
      </View>
      
      <View style={styles.actionsRow}>
        <TouchableOpacity
          style={[styles.actionButton, syncInProgress && styles.actionButtonDisabled]}
          onPress={handleSync}
          disabled={syncInProgress}
        >
          <Icon name="refresh" size={16} color={syncInProgress ? theme.colors.textSecondary : theme.colors.primary} />
          <Text style={[styles.actionButtonText, syncInProgress && styles.actionButtonTextDisabled]}>
            Sync
          </Text>
        </TouchableOpacity>
        
        {pendingSync > 0 && (
          <TouchableOpacity
            style={styles.actionButton}
            onPress={handleProcessPending}
          >
            <Icon name="cloud-upload" size={16} color={theme.colors.warning} />
            <Text style={[styles.actionButtonText, { color: theme.colors.warning }]}>
              Enviar
            </Text>
          </TouchableOpacity>
        )}
        
        <TouchableOpacity
          style={styles.actionButton}
          onPress={handleCheckConnectivity}
        >
          <Icon name="network-check" size={16} color={theme.colors.textSecondary} />
          <Text style={styles.actionButtonText}>
            Teste
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.background,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  
  statusIndicator: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  
  statusText: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.text,
  },
  
  lastSyncText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginLeft: 8,
  },
  
  actionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: theme.colors.surface,
  },
  
  actionButtonDisabled: {
    opacity: 0.5,
  },
  
  actionButtonText: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginLeft: 4,
  },
  
  actionButtonTextDisabled: {
    color: theme.colors.textSecondary,
  },
});