/**
 * Configuração de Integração Mobile-Desktop
 * Conecta o app mobile com o backend ERP existente
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

class ERPIntegrationService {
  constructor() {
    // Configuração do backend ERP existente
    this.baseURL = __DEV__ 
      ? 'http://127.0.0.1:8002'  // Backend local em desenvolvimento
      : 'https://primotex-erp.herokuapp.com'; // Produção (quando configurado)
    
    this.apiVersion = '/api/v1';
    this.timeout = 15000; // 15 segundos
    this.retryAttempts = 3;
    this.isOnline = true;
    
    // Headers padrão
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'User-Agent': `Primotex-Mobile/${Platform.OS}`,
    };
  }

  // ====================================
  // AUTENTICAÇÃO JWT
  // ====================================
  
  async login(username, password) {
    try {
      const response = await this.makeRequest('POST', '/auth/login', {
        username,
        password,
        device_info: {
          platform: Platform.OS,
          version: Platform.Version,
          app_version: '1.0.0'
        }
      });

      if (response.access_token) {
        // Salvar token e dados do usuário
        await AsyncStorage.setItem('auth_token', response.access_token);
        await AsyncStorage.setItem('user_data', JSON.stringify(response.user));
        await AsyncStorage.setItem('session_expires', response.expires_at);
        
        return {
          success: true,
          user: response.user,
          token: response.access_token
        };
      }
      
      throw new Error('Token não recebido');
      
    } catch (error) {
      console.error('Erro no login ERP:', error);
      return {
        success: false,
        error: error.message || 'Erro de autenticação'
      };
    }
  }

  async logout() {
    try {
      // Notificar backend sobre logout
      await this.makeRequest('POST', '/auth/logout');
    } catch (error) {
      console.warn('Erro ao notificar logout:', error);
    } finally {
      // Limpar dados locais
      await AsyncStorage.multiRemove([
        'auth_token',
        'user_data', 
        'session_expires'
      ]);
    }
  }

  async refreshToken() {
    try {
      const response = await this.makeRequest('POST', '/auth/refresh');
      if (response.access_token) {
        await AsyncStorage.setItem('auth_token', response.access_token);
        await AsyncStorage.setItem('session_expires', response.expires_at);
        return response.access_token;
      }
      throw new Error('Não foi possível renovar token');
    } catch (error) {
      console.error('Erro ao renovar token:', error);
      await this.logout();
      throw error;
    }
  }

  // ====================================
  // ORDENS DE SERVIÇO - INTEGRAÇÃO
  // ====================================
  
  async syncOS() {
    try {
      const response = await this.makeRequest('GET', '/ordem-servico');
      
      // Salvar no cache local para offline
      await AsyncStorage.setItem('cached_os', JSON.stringify(response.data));
      
      return {
        success: true,
        ordens: response.data,
        lastSync: new Date().toISOString()
      };
    } catch (error) {
      console.error('Erro ao sincronizar OS:', error);
      
      // Fallback para cache offline
      const cachedOS = await AsyncStorage.getItem('cached_os');
      if (cachedOS) {
        return {
          success: true,
          ordens: JSON.parse(cachedOS),
          fromCache: true
        };
      }
      
      throw error;
    }
  }

  async createOS(osData) {
    try {
      // Adicionar metadados mobile
      const enhancedData = {
        ...osData,
        created_from: 'mobile',
        device_info: {
          platform: Platform.OS,
          timestamp: new Date().toISOString()
        }
      };

      const response = await this.makeRequest('POST', '/ordem-servico', enhancedData);
      
      return {
        success: true,
        ordem: response.data
      };
    } catch (error) {
      console.error('Erro ao criar OS:', error);
      
      // Salvar para sync posterior se offline
      if (!this.isOnline) {
        await this.savePendingSync('create_os', enhancedData);
        return {
          success: true,
          ordem: { ...enhancedData, id: `temp_${Date.now()}` },
          pending: true
        };
      }
      
      throw error;
    }
  }

  async updateOS(osId, updates) {
    try {
      const enhancedUpdates = {
        ...updates,
        updated_from: 'mobile',
        last_modified: new Date().toISOString()
      };

      const response = await this.makeRequest('PUT', `/ordem-servico/${osId}`, enhancedUpdates);
      
      return {
        success: true,
        ordem: response.data
      };
    } catch (error) {
      console.error('Erro ao atualizar OS:', error);
      
      // Salvar para sync posterior se offline
      if (!this.isOnline) {
        await this.savePendingSync('update_os', { osId, updates: enhancedUpdates });
        return {
          success: true,
          pending: true
        };
      }
      
      throw error;
    }
  }

  // ====================================
  // AGENDAMENTOS - INTEGRAÇÃO
  // ====================================
  
  async syncAgendamentos() {
    try {
      const response = await this.makeRequest('GET', '/agendamento');
      
      await AsyncStorage.setItem('cached_agendamentos', JSON.stringify(response.data));
      
      return {
        success: true,
        agendamentos: response.data,
        lastSync: new Date().toISOString()
      };
    } catch (error) {
      console.error('Erro ao sincronizar agendamentos:', error);
      
      const cached = await AsyncStorage.getItem('cached_agendamentos');
      if (cached) {
        return {
          success: true,
          agendamentos: JSON.parse(cached),
          fromCache: true
        };
      }
      
      throw error;
    }
  }

  async createAgendamento(agendamentoData) {
    try {
      const response = await this.makeRequest('POST', '/agendamento', {
        ...agendamentoData,
        created_from: 'mobile'
      });
      
      return {
        success: true,
        agendamento: response.data
      };
    } catch (error) {
      console.error('Erro ao criar agendamento:', error);
      
      if (!this.isOnline) {
        await this.savePendingSync('create_agendamento', agendamentoData);
        return {
          success: true,
          agendamento: { ...agendamentoData, id: `temp_${Date.now()}` },
          pending: true
        };
      }
      
      throw error;
    }
  }

  // ====================================
  // CLIENTES - INTEGRAÇÃO
  // ====================================
  
  async syncClientes() {
    try {
      const response = await this.makeRequest('GET', '/clientes');
      
      await AsyncStorage.setItem('cached_clientes', JSON.stringify(response.data));
      
      return {
        success: true,
        clientes: response.data,
        lastSync: new Date().toISOString()
      };
    } catch (error) {
      console.error('Erro ao sincronizar clientes:', error);
      
      const cached = await AsyncStorage.getItem('cached_clientes');
      if (cached) {
        return {
          success: true,
          clientes: JSON.parse(cached),
          fromCache: true
        };
      }
      
      throw error;
    }
  }

  // ====================================
  // COMUNICAÇÃO E NOTIFICAÇÕES
  // ====================================
  
  async registerForPushNotifications(deviceToken) {
    try {
      await this.makeRequest('POST', '/comunicacao/register-device', {
        device_token: deviceToken,
        platform: Platform.OS,
        app_version: '1.0.0'
      });
      
      return { success: true };
    } catch (error) {
      console.error('Erro ao registrar push notifications:', error);
      return { success: false, error: error.message };
    }
  }

  // ====================================
  // SINCRONIZAÇÃO OFFLINE
  // ====================================
  
  async savePendingSync(action, data) {
    try {
      const pending = await AsyncStorage.getItem('pending_sync');
      const pendingList = pending ? JSON.parse(pending) : [];
      
      pendingList.push({
        id: Date.now().toString(),
        action,
        data,
        timestamp: new Date().toISOString()
      });
      
      await AsyncStorage.setItem('pending_sync', JSON.stringify(pendingList));
    } catch (error) {
      console.error('Erro ao salvar sync pendente:', error);
    }
  }

  async processPendingSync() {
    try {
      const pending = await AsyncStorage.getItem('pending_sync');
      if (!pending) return { success: true, processed: 0 };
      
      const pendingList = JSON.parse(pending);
      let processed = 0;
      
      for (const item of pendingList) {
        try {
          switch (item.action) {
            case 'create_os':
              await this.createOS(item.data);
              break;
            case 'update_os':
              await this.updateOS(item.data.osId, item.data.updates);
              break;
            case 'create_agendamento':
              await this.createAgendamento(item.data);
              break;
            default:
              console.warn(`Ação de sync desconhecida: ${item.action}`);
          }
          processed++;
        } catch (error) {
          console.error(`Erro ao processar sync ${item.action}:`, error);
        }
      }
      
      // Limpar lista de pendências
      await AsyncStorage.removeItem('pending_sync');
      
      return { success: true, processed };
      
    } catch (error) {
      console.error('Erro ao processar sync pendente:', error);
      return { success: false, error: error.message };
    }
  }

  // ====================================
  // MÉTODOS AUXILIARES
  // ====================================
  
  async makeRequest(method, endpoint, data = null, retryCount = 0) {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      
      const headers = {
        ...this.defaultHeaders,
        ...(token && { 'Authorization': `Bearer ${token}` })
      };

      const config = {
        method,
        headers,
        ...(data && { body: JSON.stringify(data) })
      };

      const response = await fetch(`${this.baseURL}${this.apiVersion}${endpoint}`, config);
      
      // Verificar se token expirou
      if (response.status === 401 && token) {
        if (retryCount < 1) {
          await this.refreshToken();
          return this.makeRequest(method, endpoint, data, retryCount + 1);
        } else {
          throw new Error('Sessão expirada');
        }
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
      
    } catch (error) {
      // Retry logic
      if (retryCount < this.retryAttempts - 1) {
        console.warn(`Tentativa ${retryCount + 1} falhou, tentando novamente...`);
        await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)));
        return this.makeRequest(method, endpoint, data, retryCount + 1);
      }
      
      this.isOnline = false;
      throw error;
    }
  }

  async checkConnectivity() {
    try {
      const response = await fetch(`${this.baseURL}/health`, { 
        timeout: 5000 
      });
      this.isOnline = response.ok;
      return this.isOnline;
    } catch (error) {
      this.isOnline = false;
      return false;
    }
  }
}

// Instância global
const erpIntegration = new ERPIntegrationService();

export default erpIntegration;