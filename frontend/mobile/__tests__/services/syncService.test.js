// Mock expo-sqlite antes do import
jest.mock('expo-sqlite', () => ({
  openDatabase: jest.fn(() => ({
    transaction: jest.fn(),
    readTransaction: jest.fn(),
  })),
}));

import syncService from '../../src/services/syncService';

// Mock dependencies
jest.mock('../../src/services/apiService');
jest.mock('../../src/services/offlineDatabaseService');
jest.mock('@react-native-community/netinfo');

import apiService from '../../src/services/apiService';
import offlineDB from '../../src/services/offlineDatabaseService';
import NetInfo from '@react-native-community/netinfo';

describe('Sync Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Network Detection', () => {
    it('should detect online status', async () => {
      NetInfo.fetch.mockResolvedValueOnce({
        isConnected: true,
        type: 'wifi'
      });

      const isOnline = await syncService.checkConnection();
      expect(isOnline).toBe(true);
    });

    it('should detect offline status', async () => {
      NetInfo.fetch.mockResolvedValueOnce({
        isConnected: false,
        type: 'none'
      });

      const isOnline = await syncService.checkConnection();
      expect(isOnline).toBe(false);
    });
  });

  describe('Data Synchronization', () => {
    it('should sync pending changes when online', async () => {
      const pendingChanges = [
        { id: 1, type: 'OS_UPDATE', data: { status: 'Concluída' } },
        { id: 2, type: 'OS_CREATE', data: { numero: 'OS-003' } }
      ];

      NetInfo.fetch.mockResolvedValueOnce({ isConnected: true });
      offlineDB.getPendingChanges.mockResolvedValueOnce(pendingChanges);
      apiService.syncData.mockResolvedValueOnce({ success: true });

      const result = await syncService.syncPendingChanges();

      expect(offlineDB.getPendingChanges).toHaveBeenCalled();
      expect(apiService.syncData).toHaveBeenCalledWith(pendingChanges);
      expect(result.success).toBe(true);
    });

    it('should not sync when offline', async () => {
      NetInfo.fetch.mockResolvedValueOnce({ isConnected: false });

      const result = await syncService.syncPendingChanges();

      expect(result.skipped).toBe(true);
      expect(result.reason).toBe('offline');
      expect(apiService.syncData).not.toHaveBeenCalled();
    });

    it('should handle sync errors gracefully', async () => {
      const pendingChanges = [
        { id: 1, type: 'OS_UPDATE', data: { status: 'Concluída' } }
      ];

      NetInfo.fetch.mockResolvedValueOnce({ isConnected: true });
      offlineDB.getPendingChanges.mockResolvedValueOnce(pendingChanges);
      apiService.syncData.mockRejectedValueOnce(new Error('Sync failed'));

      const result = await syncService.syncPendingChanges();

      expect(result.success).toBe(false);
      expect(result.error).toBe('Sync failed');
    });
  });

  describe('Offline Queue Management', () => {
    it('should queue actions when offline', async () => {
      const action = {
        type: 'UPDATE_OS_STATUS',
        payload: { osId: 1, status: 'Em Andamento' }
      };

      offlineDB.queueAction.mockResolvedValueOnce({ id: 1 });

      await syncService.queueOfflineAction(action);

      expect(offlineDB.queueAction).toHaveBeenCalledWith(action);
    });

    it('should process queued actions when back online', async () => {
      const queuedActions = [
        { id: 1, type: 'UPDATE_OS_STATUS', payload: { osId: 1 } },
        { id: 2, type: 'CREATE_OS', payload: { numero: 'OS-004' } }
      ];

      NetInfo.fetch.mockResolvedValueOnce({ isConnected: true });
      offlineDB.getQueuedActions.mockResolvedValueOnce(queuedActions);
      apiService.processAction.mockResolvedValue({ success: true });

      const result = await syncService.processOfflineQueue();

      expect(offlineDB.getQueuedActions).toHaveBeenCalled();
      expect(apiService.processAction).toHaveBeenCalledTimes(2);
      expect(result.processed).toBe(2);
    });
  });

  describe('Conflict Resolution', () => {
    it('should resolve conflicts with server priority', async () => {
      const localData = { id: 1, status: 'Em Andamento', updated_at: '2024-01-01' };
      const serverData = { id: 1, status: 'Concluída', updated_at: '2024-01-02' };

      const resolved = syncService.resolveConflict(localData, serverData, 'server');

      expect(resolved).toEqual(serverData);
    });

    it('should resolve conflicts with local priority', async () => {
      const localData = { id: 1, status: 'Em Andamento', updated_at: '2024-01-02' };
      const serverData = { id: 1, status: 'Concluída', updated_at: '2024-01-01' };

      const resolved = syncService.resolveConflict(localData, serverData, 'local');

      expect(resolved).toEqual(localData);
    });

    it('should merge conflicts when possible', async () => {
      const localData = { id: 1, status: 'Em Andamento', observacoes: 'Local obs' };
      const serverData = { id: 1, status: 'Concluída', tecnico: 'João' };

      const resolved = syncService.resolveConflict(localData, serverData, 'merge');

      expect(resolved.status).toBe('Concluída'); // Server wins
      expect(resolved.observacoes).toBe('Local obs'); // Local preserved
      expect(resolved.tecnico).toBe('João'); // Server preserved
    });
  });

  describe('Sync Status Tracking', () => {
    it('should track last sync timestamp', async () => {
      const timestamp = new Date().toISOString();
      
      await syncService.updateLastSyncTimestamp(timestamp);
      const lastSync = await syncService.getLastSyncTimestamp();

      expect(lastSync).toBe(timestamp);
    });

    it('should track sync errors', async () => {
      const error = { message: 'Connection failed', timestamp: new Date().toISOString() };
      
      await syncService.logSyncError(error);
      const errors = await syncService.getSyncErrors();

      expect(errors).toContain(error);
    });
  });
});