import NetInfo from '@react-native-community/netinfo';
import AsyncStorage from '@react-native-async-storage/async-storage';
import apiService from './apiService';
import offlineDb from './offlineDatabaseService';

class SyncService {
  constructor() {
    this.isOnline = true;
    this.isSyncing = false;
    this.syncListeners = [];
    this.lastSyncTime = null;
    this.autoSyncInterval = null;
    
    this.init();
  }

  async init() {
    // Verificar conectividade
    const state = await NetInfo.fetch();
    this.isOnline = state.isConnected;

    // Monitorar mudanças de conectividade
    NetInfo.addEventListener(state => {
      const wasOnline = this.isOnline;
      this.isOnline = state.isConnected;

      console.log('Status de conectividade:', this.isOnline ? 'Online' : 'Offline');

      // Se voltou online, tentar sincronizar
      if (!wasOnline && this.isOnline) {
        this.notifyListeners({ type: 'connectivity', online: true });
        setTimeout(() => this.syncAll(), 2000); // Aguardar estabilizar
      } else if (wasOnline && !this.isOnline) {
        this.notifyListeners({ type: 'connectivity', online: false });
      }
    });

    // Carregar último sync
    this.lastSyncTime = await this.getLastSyncTime();

    // Configurar sync automático a cada 5 minutos quando online
    this.setupAutoSync();
  }

  setupAutoSync() {
    if (this.autoSyncInterval) {
      clearInterval(this.autoSyncInterval);
    }

    this.autoSyncInterval = setInterval(() => {
      if (this.isOnline && !this.isSyncing) {
        this.syncAll();
      }
    }, 5 * 60 * 1000); // 5 minutos
  }

  addSyncListener(listener) {
    this.syncListeners.push(listener);
    
    return () => {
      const index = this.syncListeners.indexOf(listener);
      if (index > -1) {
        this.syncListeners.splice(index, 1);
      }
    };
  }

  notifyListeners(event) {
    this.syncListeners.forEach(listener => {
      try {
        listener(event);
      } catch (error) {
        console.error('Erro ao notificar listener:', error);
      }
    });
  }

  async getLastSyncTime() {
    try {
      const time = await AsyncStorage.getItem('@primotex:last_sync');
      return time ? new Date(time) : null;
    } catch (error) {
      console.error('Erro ao recuperar último sync:', error);
      return null;
    }
  }

  async setLastSyncTime(time = new Date()) {
    try {
      await AsyncStorage.setItem('@primotex:last_sync', time.toISOString());
      this.lastSyncTime = time;
    } catch (error) {
      console.error('Erro ao salvar último sync:', error);
    }
  }

  // Sincronização completa
  async syncAll(force = false) {
    if (this.isSyncing && !force) {
      console.log('Sincronização já em andamento');
      return { success: false, message: 'Sincronização já em andamento' };
    }

    if (!this.isOnline) {
      console.log('Sem conexão para sincronizar');
      return { success: false, message: 'Sem conexão com internet' };
    }

    this.isSyncing = true;
    this.notifyListeners({ type: 'sync_start' });

    console.log('Iniciando sincronização completa...');

    try {
      // 1. Enviar dados locais para servidor
      const uploadResult = await this.uploadPendingData();
      
      // 2. Baixar dados atualizados do servidor
      const downloadResult = await this.downloadServerData();

      // 3. Limpar dados antigos
      await offlineDb.clearOldData();

      await this.setLastSyncTime();

      const result = {
        success: true,
        uploaded: uploadResult.count,
        downloaded: downloadResult.count,
        timestamp: new Date(),
      };

      this.notifyListeners({ type: 'sync_complete', result });
      console.log('Sincronização concluída:', result);

      return result;

    } catch (error) {
      console.error('Erro na sincronização:', error);
      
      const result = {
        success: false,
        error: error.message,
        timestamp: new Date(),
      };

      this.notifyListeners({ type: 'sync_error', result });
      return result;

    } finally {
      this.isSyncing = false;
    }
  }

  // Upload de dados pendentes
  async uploadPendingData() {
    const syncQueue = await offlineDb.getSyncQueue();
    let successCount = 0;
    let errorCount = 0;

    console.log(`Enviando ${syncQueue.length} itens pendentes...`);

    for (const item of syncQueue) {
      try {
        await this.processSyncItem(item);
        await offlineDb.removeSyncItem(item.id);
        successCount++;
        
        this.notifyListeners({
          type: 'sync_progress',
          progress: successCount + errorCount,
          total: syncQueue.length,
          item: 'upload'
        });

      } catch (error) {
        console.error(`Erro ao processar item ${item.id}:`, error);
        await offlineDb.updateSyncItemError(item.id, error.message);
        errorCount++;
      }
    }

    console.log(`Upload concluído: ${successCount} enviados, ${errorCount} erros`);
    return { count: successCount, errors: errorCount };
  }

  async processSyncItem(item) {
    const { action, table_name, data } = item;

    switch (table_name) {
      case 'os':
        return this.syncOS(action, data);
      case 'agendamentos':
        return this.syncAgendamento(action, data);
      case 'clientes':
        return this.syncCliente(action, data);
      case 'anexos':
        return this.syncAnexo(action, data);
      case 'assinaturas':
        return this.syncAssinatura(action, data);
      default:
        throw new Error(`Tipo de sincronização não suportado: ${table_name}`);
    }
  }

  async syncOS(action, data) {
    switch (action) {
      case 'CREATE':
        const newOS = await apiService.createOS(data);
        // Atualizar ID local com ID do servidor
        if (data.offline_id) {
          await offlineDb.updateOS(data.id, { server_id: newOS.id, sync_status: 'synced' });
        }
        return newOS;

      case 'UPDATE':
        if (data.server_id) {
          return await apiService.updateOS(data.server_id, data);
        } else {
          throw new Error('OS sem ID do servidor para atualização');
        }

      default:
        throw new Error(`Ação não suportada: ${action}`);
    }
  }

  async syncAgendamento(action, data) {
    switch (action) {
      case 'CREATE':
        const newAgendamento = await apiService.createAgendamento(data);
        if (data.offline_id) {
          // Atualizar referência local
          await offlineDb.updateAgendamento(data.id, { 
            server_id: newAgendamento.id, 
            sync_status: 'synced' 
          });
        }
        return newAgendamento;

      case 'UPDATE':
        if (data.server_id) {
          return await apiService.updateAgendamento(data.server_id, data);
        } else {
          throw new Error('Agendamento sem ID do servidor para atualização');
        }

      default:
        throw new Error(`Ação não suportada: ${action}`);
    }
  }

  async syncCliente(action, data) {
    switch (action) {
      case 'CREATE':
        const newCliente = await apiService.createCliente(data);
        if (data.offline_id) {
          await offlineDb.updateCliente(data.id, { 
            server_id: newCliente.id, 
            sync_status: 'synced' 
          });
        }
        return newCliente;

      case 'UPDATE':
        if (data.server_id) {
          return await apiService.updateCliente(data.server_id, data);
        } else {
          throw new Error('Cliente sem ID do servidor para atualização');
        }

      default:
        throw new Error(`Ação não suportada: ${action}`);
    }
  }

  async syncAnexo(action, data) {
    // TODO: Implementar upload de arquivos
    console.log('Sync de anexos ainda não implementado');
    return null;
  }

  async syncAssinatura(action, data) {
    // TODO: Implementar upload de assinaturas
    console.log('Sync de assinaturas ainda não implementado');
    return null;
  }

  // Download de dados do servidor
  async downloadServerData() {
    let totalDownloaded = 0;

    console.log('Baixando dados do servidor...');

    try {
      // Download OS
      const osData = await apiService.getOS();
      await this.mergeServerData('os', osData);
      totalDownloaded += osData.length;

      // Download Agendamentos
      const agendamentosData = await apiService.getAgendamentos();
      await this.mergeServerData('agendamentos', agendamentosData);
      totalDownloaded += agendamentosData.length;

      // Download Clientes
      const clientesData = await apiService.getClientes();
      await this.mergeServerData('clientes', clientesData);
      totalDownloaded += clientesData.length;

      console.log(`Download concluído: ${totalDownloaded} registros`);
      return { count: totalDownloaded };

    } catch (error) {
      console.error('Erro no download:', error);
      throw error;
    }
  }

  async mergeServerData(tableName, serverData) {
    // Estratégia: Server wins (dados do servidor sobrescrevem locais)
    // TODO: Implementar merge inteligente com conflict resolution
    
    for (const serverItem of serverData) {
      // Verificar se já existe localmente pelo server_id
      const localItems = await offlineDb.db.getAllAsync(
        `SELECT * FROM ${tableName} WHERE server_id = ?`,
        [serverItem.id]
      );

      if (localItems.length > 0) {
        // Atualizar registro local
        const localItem = localItems[0];
        const updateData = {
          ...serverItem,
          id: localItem.id, // Manter ID local
          server_id: serverItem.id,
          sync_status: 'synced',
        };

        await this.updateLocalRecord(tableName, localItem.id, updateData);
      } else {
        // Criar novo registro local
        const insertData = {
          ...serverItem,
          server_id: serverItem.id,
          sync_status: 'synced',
        };

        await this.insertLocalRecord(tableName, insertData);
      }
    }
  }

  async updateLocalRecord(tableName, localId, data) {
    const setClauses = Object.keys(data)
      .filter(key => key !== 'id')
      .map(key => `${key} = ?`);
    
    const values = Object.keys(data)
      .filter(key => key !== 'id')
      .map(key => data[key]);

    await offlineDb.db.runAsync(
      `UPDATE ${tableName} SET ${setClauses.join(', ')} WHERE id = ?`,
      [...values, localId]
    );
  }

  async insertLocalRecord(tableName, data) {
    const columns = Object.keys(data).filter(key => key !== 'id');
    const placeholders = columns.map(() => '?').join(', ');
    const values = columns.map(key => data[key]);

    await offlineDb.db.runAsync(
      `INSERT INTO ${tableName} (${columns.join(', ')}) VALUES (${placeholders})`,
      values
    );
  }

  // Métodos auxiliares
  getConnectionStatus() {
    return {
      isOnline: this.isOnline,
      isSyncing: this.isSyncing,
      lastSync: this.lastSyncTime,
    };
  }

  async forcePullFromServer() {
    if (!this.isOnline) {
      throw new Error('Sem conexão com internet');
    }

    console.log('Forçando download do servidor...');
    return this.downloadServerData();
  }

  async forcePushToServer() {
    if (!this.isOnline) {
      throw new Error('Sem conexão com internet');
    }

    console.log('Forçando upload para servidor...');
    return this.uploadPendingData();
  }

  // Cleanup
  destroy() {
    if (this.autoSyncInterval) {
      clearInterval(this.autoSyncInterval);
    }
    this.syncListeners = [];
  }
}

// Instância singleton
const syncService = new SyncService();

export default syncService;