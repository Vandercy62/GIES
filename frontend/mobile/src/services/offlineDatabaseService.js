import * as SQLite from 'expo-sqlite';
import AsyncStorage from '@react-native-async-storage/async-storage';

class OfflineDatabaseService {
  constructor() {
    this.db = null;
    this.isInitialized = false;
  }

  async init() {
    if (this.isInitialized) return;

    try {
      this.db = await SQLite.openDatabaseAsync('primotex_mobile.db');
      await this.createTables();
      this.isInitialized = true;
      console.log('Banco de dados offline inicializado');
    } catch (error) {
      console.error('Erro ao inicializar banco offline:', error);
      throw error;
    }
  }

  async createTables() {
    const tables = [
      // Tabela de Ordens de Serviço
      `CREATE TABLE IF NOT EXISTS os (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        numero TEXT,
        cliente_id INTEGER,
        cliente_nome TEXT,
        cliente_telefone TEXT,
        endereco TEXT,
        descricao_servico TEXT,
        status TEXT DEFAULT 'pendente',
        prioridade TEXT DEFAULT 'normal',
        data_agendamento TEXT,
        hora_agendamento TEXT,
        data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
        data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
        tecnico_id INTEGER,
        observacoes TEXT,
        valor_total REAL DEFAULT 0,
        tempo_estimado INTEGER,
        sync_status TEXT DEFAULT 'pending',
        offline_id TEXT UNIQUE
      )`,

      // Tabela de Agendamentos
      `CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        titulo TEXT NOT NULL,
        cliente_id INTEGER,
        cliente_nome TEXT,
        endereco TEXT,
        data_agendamento TEXT NOT NULL,
        hora_agendamento TEXT,
        status TEXT DEFAULT 'pendente',
        observacoes TEXT,
        tipo TEXT,
        data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
        sync_status TEXT DEFAULT 'pending',
        offline_id TEXT UNIQUE
      )`,

      // Tabela de Clientes
      `CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT,
        whatsapp TEXT,
        cpf_cnpj TEXT,
        endereco TEXT,
        numero TEXT,
        complemento TEXT,
        bairro TEXT,
        cidade TEXT,
        estado TEXT,
        cep TEXT,
        observacoes TEXT,
        data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
        sync_status TEXT DEFAULT 'pending',
        offline_id TEXT UNIQUE
      )`,

      // Tabela de Produtos
      `CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        nome TEXT NOT NULL,
        descricao TEXT,
        categoria TEXT,
        preco REAL DEFAULT 0,
        codigo_barras TEXT,
        unidade TEXT,
        estoque_atual INTEGER DEFAULT 0,
        estoque_minimo INTEGER DEFAULT 0,
        ativo BOOLEAN DEFAULT 1,
        data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
        sync_status TEXT DEFAULT 'pending',
        offline_id TEXT UNIQUE
      )`,

      // Tabela de Fotos/Anexos
      `CREATE TABLE IF NOT EXISTS anexos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        tipo_entidade TEXT NOT NULL,
        entidade_id INTEGER NOT NULL,
        tipo_arquivo TEXT NOT NULL,
        nome_arquivo TEXT NOT NULL,
        caminho_local TEXT NOT NULL,
        tamanho INTEGER,
        data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
        sync_status TEXT DEFAULT 'pending',
        offline_id TEXT UNIQUE
      )`,

      // Tabela de Assinaturas
      `CREATE TABLE IF NOT EXISTS assinaturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        os_id INTEGER NOT NULL,
        nome_cliente TEXT NOT NULL,
        cargo TEXT,
        data_assinatura TEXT DEFAULT CURRENT_TIMESTAMP,
        caminho_assinatura TEXT NOT NULL,
        sync_status TEXT DEFAULT 'pending',
        offline_id TEXT UNIQUE
      )`,

      // Tabela de Sincronização
      `CREATE TABLE IF NOT EXISTS sync_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        table_name TEXT NOT NULL,
        record_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        retry_count INTEGER DEFAULT 0,
        error_message TEXT
      )`,

      // Tabela de Configurações
      `CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )`
    ];

    for (const table of tables) {
      await this.db.execAsync(table);
    }

    // Criar índices para melhor performance
    const indexes = [
      'CREATE INDEX IF NOT EXISTS idx_os_status ON os(status)',
      'CREATE INDEX IF NOT EXISTS idx_os_data_agendamento ON os(data_agendamento)',
      'CREATE INDEX IF NOT EXISTS idx_os_sync_status ON os(sync_status)',
      'CREATE INDEX IF NOT EXISTS idx_agendamentos_data ON agendamentos(data_agendamento)',
      'CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes(nome)',
      'CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome)',
      'CREATE INDEX IF NOT EXISTS idx_sync_queue_timestamp ON sync_queue(timestamp)',
    ];

    for (const index of indexes) {
      await this.db.execAsync(index);
    }
  }

  generateOfflineId() {
    return `offline_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Métodos de OS
  async createOS(osData) {
    await this.init();
    
    const offlineId = this.generateOfflineId();
    const data = {
      ...osData,
      offline_id: offlineId,
      sync_status: 'pending',
      data_criacao: new Date().toISOString(),
    };

    const result = await this.db.runAsync(
      `INSERT INTO os (
        numero, cliente_id, cliente_nome, cliente_telefone, endereco,
        descricao_servico, status, prioridade, data_agendamento, hora_agendamento,
        tecnico_id, observacoes, valor_total, tempo_estimado, sync_status, offline_id
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        data.numero, data.cliente_id, data.cliente_nome, data.cliente_telefone,
        data.endereco, data.descricao_servico, data.status || 'pendente',
        data.prioridade || 'normal', data.data_agendamento, data.hora_agendamento,
        data.tecnico_id, data.observacoes, data.valor_total || 0,
        data.tempo_estimado, data.sync_status, data.offline_id
      ]
    );

    await this.addToSyncQueue('CREATE', 'os', result.lastInsertRowId, data);
    
    return {
      id: result.lastInsertRowId,
      offline_id: offlineId,
      ...data,
    };
  }

  async getOS(filters = {}) {
    await this.init();
    
    let query = 'SELECT * FROM os WHERE 1=1';
    const params = [];

    if (filters.status) {
      query += ' AND status = ?';
      params.push(filters.status);
    }

    if (filters.date) {
      query += ' AND data_agendamento LIKE ?';
      params.push(`${filters.date}%`);
    }

    if (filters.cliente_id) {
      query += ' AND cliente_id = ?';
      params.push(filters.cliente_id);
    }

    query += ' ORDER BY data_agendamento DESC, data_criacao DESC';

    const result = await this.db.getAllAsync(query, params);
    return result;
  }

  async updateOS(id, osData) {
    await this.init();
    
    const data = {
      ...osData,
      data_atualizacao: new Date().toISOString(),
      sync_status: 'pending',
    };

    const setClauses = Object.keys(data)
      .filter(key => key !== 'id')
      .map(key => `${key} = ?`);
    
    const values = Object.keys(data)
      .filter(key => key !== 'id')
      .map(key => data[key]);

    await this.db.runAsync(
      `UPDATE os SET ${setClauses.join(', ')} WHERE id = ?`,
      [...values, id]
    );

    await this.addToSyncQueue('UPDATE', 'os', id, data);
    
    return { id, ...data };
  }

  // Métodos de Agendamentos
  async createAgendamento(agendamentoData) {
    await this.init();
    
    const offlineId = this.generateOfflineId();
    const data = {
      ...agendamentoData,
      offline_id: offlineId,
      sync_status: 'pending',
      data_criacao: new Date().toISOString(),
    };

    const result = await this.db.runAsync(
      `INSERT INTO agendamentos (
        titulo, cliente_id, cliente_nome, endereco, data_agendamento,
        hora_agendamento, status, observacoes, tipo, sync_status, offline_id
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        data.titulo, data.cliente_id, data.cliente_nome, data.endereco,
        data.data_agendamento, data.hora_agendamento, data.status || 'pendente',
        data.observacoes, data.tipo, data.sync_status, data.offline_id
      ]
    );

    await this.addToSyncQueue('CREATE', 'agendamentos', result.lastInsertRowId, data);
    
    return {
      id: result.lastInsertRowId,
      offline_id: offlineId,
      ...data,
    };
  }

  async getAgendamentos(filters = {}) {
    await this.init();
    
    let query = 'SELECT * FROM agendamentos WHERE 1=1';
    const params = [];

    if (filters.date) {
      query += ' AND data_agendamento LIKE ?';
      params.push(`${filters.date}%`);
    }

    if (filters.status) {
      query += ' AND status = ?';
      params.push(filters.status);
    }

    query += ' ORDER BY data_agendamento ASC, hora_agendamento ASC';

    const result = await this.db.getAllAsync(query, params);
    return result;
  }

  // Métodos de Cliente
  async createCliente(clienteData) {
    await this.init();
    
    const offlineId = this.generateOfflineId();
    const data = {
      ...clienteData,
      offline_id: offlineId,
      sync_status: 'pending',
      data_criacao: new Date().toISOString(),
    };

    const result = await this.db.runAsync(
      `INSERT INTO clientes (
        nome, email, telefone, whatsapp, cpf_cnpj, endereco,
        numero, complemento, bairro, cidade, estado, cep,
        observacoes, sync_status, offline_id
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        data.nome, data.email, data.telefone, data.whatsapp, data.cpf_cnpj,
        data.endereco, data.numero, data.complemento, data.bairro,
        data.cidade, data.estado, data.cep, data.observacoes,
        data.sync_status, data.offline_id
      ]
    );

    await this.addToSyncQueue('CREATE', 'clientes', result.lastInsertRowId, data);
    
    return {
      id: result.lastInsertRowId,
      offline_id: offlineId,
      ...data,
    };
  }

  async getClientes(filters = {}) {
    await this.init();
    
    let query = 'SELECT * FROM clientes WHERE 1=1';
    const params = [];

    if (filters.search) {
      query += ' AND (nome LIKE ? OR telefone LIKE ? OR email LIKE ?)';
      const searchTerm = `%${filters.search}%`;
      params.push(searchTerm, searchTerm, searchTerm);
    }

    query += ' ORDER BY nome ASC';

    const result = await this.db.getAllAsync(query, params);
    return result;
  }

  // Métodos de Anexos
  async saveAnexo(anexoData) {
    await this.init();
    
    const offlineId = this.generateOfflineId();
    const data = {
      ...anexoData,
      offline_id: offlineId,
      sync_status: 'pending',
      data_criacao: new Date().toISOString(),
    };

    const result = await this.db.runAsync(
      `INSERT INTO anexos (
        tipo_entidade, entidade_id, tipo_arquivo, nome_arquivo,
        caminho_local, tamanho, sync_status, offline_id
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        data.tipo_entidade, data.entidade_id, data.tipo_arquivo,
        data.nome_arquivo, data.caminho_local, data.tamanho,
        data.sync_status, data.offline_id
      ]
    );

    await this.addToSyncQueue('CREATE', 'anexos', result.lastInsertRowId, data);
    
    return {
      id: result.lastInsertRowId,
      offline_id: offlineId,
      ...data,
    };
  }

  async getAnexos(tipoEntidade, entidadeId) {
    await this.init();
    
    const result = await this.db.getAllAsync(
      'SELECT * FROM anexos WHERE tipo_entidade = ? AND entidade_id = ? ORDER BY data_criacao DESC',
      [tipoEntidade, entidadeId]
    );
    
    return result;
  }

  // Métodos de Assinatura
  async saveAssinatura(assinaturaData) {
    await this.init();
    
    const offlineId = this.generateOfflineId();
    const data = {
      ...assinaturaData,
      offline_id: offlineId,
      sync_status: 'pending',
      data_assinatura: new Date().toISOString(),
    };

    const result = await this.db.runAsync(
      `INSERT INTO assinaturas (
        os_id, nome_cliente, cargo, caminho_assinatura, sync_status, offline_id
      ) VALUES (?, ?, ?, ?, ?, ?)`,
      [
        data.os_id, data.nome_cliente, data.cargo,
        data.caminho_assinatura, data.sync_status, data.offline_id
      ]
    );

    await this.addToSyncQueue('CREATE', 'assinaturas', result.lastInsertRowId, data);
    
    return {
      id: result.lastInsertRowId,
      offline_id: offlineId,
      ...data,
    };
  }

  // Queue de Sincronização
  async addToSyncQueue(action, tableName, recordId, data) {
    await this.db.runAsync(
      `INSERT INTO sync_queue (action, table_name, record_id, data)
       VALUES (?, ?, ?, ?)`,
      [action, tableName, recordId, JSON.stringify(data)]
    );
  }

  async getSyncQueue() {
    await this.init();
    
    const result = await this.db.getAllAsync(
      'SELECT * FROM sync_queue ORDER BY timestamp ASC LIMIT 50'
    );
    
    return result.map(item => ({
      ...item,
      data: JSON.parse(item.data),
    }));
  }

  async removeSyncItem(id) {
    await this.init();
    await this.db.runAsync('DELETE FROM sync_queue WHERE id = ?', [id]);
  }

  async updateSyncItemError(id, errorMessage) {
    await this.init();
    await this.db.runAsync(
      'UPDATE sync_queue SET retry_count = retry_count + 1, error_message = ? WHERE id = ?',
      [errorMessage, id]
    );
  }

  // Configurações
  async setConfig(key, value) {
    await this.init();
    await this.db.runAsync(
      'INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, ?)',
      [key, JSON.stringify(value), new Date().toISOString()]
    );
  }

  async getConfig(key, defaultValue = null) {
    await this.init();
    
    const result = await this.db.getFirstAsync(
      'SELECT value FROM config WHERE key = ?',
      [key]
    );
    
    if (result) {
      try {
        return JSON.parse(result.value);
      } catch {
        return result.value;
      }
    }
    
    return defaultValue;
  }

  // Limpeza de dados
  async clearOldData(days = 30) {
    await this.init();
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    const cutoffISO = cutoffDate.toISOString();

    await this.db.runAsync(
      'DELETE FROM sync_queue WHERE timestamp < ? AND retry_count > 5',
      [cutoffISO]
    );
  }

  // Estatísticas
  async getStats() {
    await this.init();
    
    const osCount = await this.db.getFirstAsync('SELECT COUNT(*) as count FROM os');
    const pendingSync = await this.db.getFirstAsync('SELECT COUNT(*) as count FROM sync_queue');
    const clientesCount = await this.db.getFirstAsync('SELECT COUNT(*) as count FROM clientes');
    
    return {
      totalOS: osCount.count,
      pendingSync: pendingSync.count,
      totalClientes: clientesCount.count,
    };
  }
}

// Instância singleton
const offlineDb = new OfflineDatabaseService();

export default offlineDb;