// Mock expo-sqlite antes do import
jest.mock('expo-sqlite', () => ({
  openDatabase: jest.fn(() => ({
    transaction: jest.fn(),
    readTransaction: jest.fn(),
  })),
}));

// Mock react-native-community/netinfo
jest.mock('@react-native-community/netinfo', () => ({
  fetch: jest.fn(),
  addEventListener: jest.fn(),
}));

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
}));

// Mock services
jest.mock('../../src/services/apiService', () => ({
  syncOrdemServico: jest.fn(),
  getOSList: jest.fn(),
  updateOS: jest.fn(),
  uploadFiles: jest.fn(),
}));

jest.mock('../../src/services/offlineDatabaseService', () => ({
  getPendingSync: jest.fn(),
  clearPendingSync: jest.fn(),
  savePendingData: jest.fn(),
  getLocalData: jest.fn(),
}));

import syncService from '../../src/services/syncService';
import apiService from '../../src/services/apiService';
import offlineDb from '../../src/services/offlineDatabaseService';
import NetInfo from '@react-native-community/netinfo';
import AsyncStorage from '@react-native-async-storage/async-storage';

describe('Sync Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    syncService.isSyncing = false;
    syncService.isOnline = true;
  });

  describe('Connectivity Management', () => {
    it('should initialize with online status', async () => {
      NetInfo.fetch.mockResolvedValueOnce({
        isConnected: true,
        type: 'wifi'
      });

      await syncService.init();

      expect(NetInfo.fetch).toHaveBeenCalled();
      expect(syncService.isOnline).toBe(true);
    });

    it('should handle offline status', async () => {
      NetInfo.fetch.mockResolvedValueOnce({
        isConnected: false,
        type: 'none'
      });

      await syncService.init();

      expect(syncService.isOnline).toBe(false);
    });

    it('should check current connectivity', async () => {
      NetInfo.fetch.mockResolvedValueOnce({
        isConnected: true,
        type: 'cellular'
      });

      const isOnline = await syncService.checkConnectivity();

      expect(NetInfo.fetch).toHaveBeenCalled();
      expect(isOnline).toBe(true);
    });
  });

  describe('Data Synchronization', () => {
    it('should sync pending changes when online', async () => {
      const pendingData = [
        { id: 1, type: 'os_update', data: { status: 'Em Andamento' } },
        { id: 2, type: 'os_create', data: { cliente: 'Test' } }
      ];

      offlineDb.getPendingSync.mockResolvedValueOnce(pendingData);
      apiService.syncOrdemServico.mockResolvedValueOnce({ success: true });

      const result = await syncService.syncPendingChanges();

      expect(offlineDb.getPendingSync).toHaveBeenCalled();
      expect(apiService.syncOrdemServico).toHaveBeenCalledWith(pendingData[0].data);
      expect(result.success).toBe(true);
    });

    it('should not sync when offline', async () => {
      syncService.isOnline = false;

      const result = await syncService.syncPendingChanges();

      expect(result.success).toBe(false);
      expect(result.message).toContain('offline');
    });

    it('should handle sync errors gracefully', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      
      const pendingData = [
        { id: 1, type: 'os_update', data: { status: 'Em Andamento' } }
      ];

      offlineDb.getPendingSync.mockResolvedValueOnce(pendingData);
      apiService.syncOrdemServico.mockRejectedValueOnce(new Error('Sync failed'));

      const result = await syncService.syncPendingChanges();

      expect(result.success).toBe(false);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Erro na sincronização:',
        expect.any(Error)
      );

      consoleErrorSpy.mockRestore();
    });

    it('should sync all data types', async () => {
      apiService.getOSList.mockResolvedValueOnce({ data: [] });
      offlineDb.getPendingSync.mockResolvedValueOnce([]);

      const result = await syncService.syncAll();

      expect(apiService.getOSList).toHaveBeenCalled();
      expect(offlineDb.getPendingSync).toHaveBeenCalled();
      expect(result.success).toBe(true);
    });
  });

  describe('Offline Storage', () => {
    it('should save data when offline', async () => {
      syncService.isOnline = false;
      
      const osData = {
        id: 1,
        status: 'Em Andamento',
        observacoes: 'Test offline'
      };

      offlineDb.savePendingData.mockResolvedValueOnce({ id: 1 });

      await syncService.saveOfflineData('os_update', osData);

      expect(offlineDb.savePendingData).toHaveBeenCalledWith({
        type: 'os_update',
        data: osData,
        timestamp: expect.any(String)
      });
    });

    it('should handle offline save errors', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      
      offlineDb.savePendingData.mockRejectedValueOnce(new Error('Save failed'));

      const result = await syncService.saveOfflineData('os_update', {});

      expect(result.success).toBe(false);
      expect(consoleErrorSpy).toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });
  });

  describe('Sync Status Tracking', () => {
    it('should track last sync timestamp', async () => {
      const timestamp = new Date().toISOString();
      AsyncStorage.setItem.mockResolvedValueOnce();
      AsyncStorage.getItem.mockResolvedValueOnce(timestamp);

      await syncService.setLastSyncTime(timestamp);
      const lastSync = await syncService.getLastSyncTime();

      expect(AsyncStorage.setItem).toHaveBeenCalledWith('lastSyncTime', timestamp);
      expect(lastSync).toBe(timestamp);
    });

    it('should handle missing last sync time', async () => {
      AsyncStorage.getItem.mockResolvedValueOnce(null);

      const lastSync = await syncService.getLastSyncTime();

      expect(lastSync).toBe(null);
    });

    it('should track sync status', () => {
      expect(syncService.isSyncing).toBe(false);
      
      syncService.isSyncing = true;
      expect(syncService.getSyncStatus()).toEqual({
        isSyncing: true,
        isOnline: true,
        lastSyncTime: null
      });
    });
  });

  describe('Event Listeners', () => {
    it('should add sync listeners', () => {
      const listener = jest.fn();
      
      syncService.addSyncListener(listener);
      
      expect(syncService.syncListeners).toContain(listener);
    });

    it('should remove sync listeners', () => {
      const listener = jest.fn();
      
      syncService.addSyncListener(listener);
      syncService.removeSyncListener(listener);
      
      expect(syncService.syncListeners).not.toContain(listener);
    });

    it('should notify listeners of sync events', () => {
      const listener = jest.fn();
      
      syncService.addSyncListener(listener);
      syncService.notifyListeners({ type: 'sync_complete', success: true });
      
      expect(listener).toHaveBeenCalledWith({
        type: 'sync_complete',
        success: true
      });
    });
  });

  describe('File Synchronization', () => {
    it('should sync files when online', async () => {
      const files = [
        { id: 1, path: '/path/to/file1.jpg', uploaded: false },
        { id: 2, path: '/path/to/file2.pdf', uploaded: false }
      ];

      offlineDb.getLocalData.mockResolvedValueOnce(files);
      apiService.uploadFiles.mockResolvedValueOnce({ success: true });

      const result = await syncService.syncFiles();

      expect(offlineDb.getLocalData).toHaveBeenCalledWith('pending_files');
      expect(apiService.uploadFiles).toHaveBeenCalledWith(files);
      expect(result.success).toBe(true);
    });

    it('should handle file sync errors', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      
      offlineDb.getLocalData.mockRejectedValueOnce(new Error('File access failed'));

      const result = await syncService.syncFiles();

      expect(result.success).toBe(false);
      expect(consoleErrorSpy).toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });
  });

  describe('Utility Methods', () => {
    it('should clear all sync data', async () => {
      offlineDb.clearPendingSync.mockResolvedValueOnce();
      AsyncStorage.removeItem.mockResolvedValueOnce();

      await syncService.clearSyncData();

      expect(offlineDb.clearPendingSync).toHaveBeenCalled();
      expect(AsyncStorage.removeItem).toHaveBeenCalledWith('lastSyncTime');
    });

    it('should force sync when needed', async () => {
      offlineDb.getPendingSync.mockResolvedValueOnce([]);
      apiService.getOSList.mockResolvedValueOnce({ data: [] });

      const result = await syncService.forceSync();

      expect(result.success).toBe(true);
      expect(syncService.isSyncing).toBe(false); // Reset after sync
    });
  });
});