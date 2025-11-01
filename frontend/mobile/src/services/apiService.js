import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://127.0.0.1:8002';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.timeout = 10000;
  }

  async getToken() {
    try {
      const token = await AsyncStorage.getItem('@primotex:token');
      return token;
    } catch (error) {
      console.error('Erro ao recuperar token:', error);
      return null;
    }
  }

  async setToken(token) {
    try {
      await AsyncStorage.setItem('@primotex:token', token);
    } catch (error) {
      console.error('Erro ao salvar token:', error);
    }
  }

  async removeToken() {
    try {
      await AsyncStorage.removeItem('@primotex:token');
    } catch (error) {
      console.error('Erro ao remover token:', error);
    }
  }

  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const token = await this.getToken();

    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    if (token) {
      defaultHeaders.Authorization = `Bearer ${token}`;
    }

    const config = {
      timeout: this.timeout,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
      ...options,
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        if (response.status === 401) {
          // Token expirado ou inválido
          await this.removeToken();
          throw new Error('Sessão expirada. Faça login novamente.');
        }

        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erro HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Timeout da requisição');
      }
      
      if (error.message.includes('Network request failed')) {
        throw new Error('Erro de conexão. Verifique sua internet.');
      }

      throw error;
    }
  }

  // Métodos HTTP
  async get(endpoint, params = {}) {
    const searchParams = new URLSearchParams(params);
    const url = searchParams.toString() ? `${endpoint}?${searchParams}` : endpoint;
    
    return this.makeRequest(url, {
      method: 'GET',
    });
  }

  async post(endpoint, data = {}) {
    return this.makeRequest(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data = {}) {
    return this.makeRequest(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch(endpoint, data = {}) {
    return this.makeRequest(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.makeRequest(endpoint, {
      method: 'DELETE',
    });
  }

  // Métodos de Autenticação
  async login(credentials) {
    try {
      const response = await this.post('/api/v1/auth/login', credentials);
      
      if (response.access_token) {
        await this.setToken(response.access_token);
      }

      return {
        success: true,
        data: response,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  async logout() {
    try {
      await this.removeToken();
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  async refreshToken() {
    try {
      const response = await this.post('/api/v1/auth/refresh');
      
      if (response.access_token) {
        await this.setToken(response.access_token);
        return { success: true, token: response.access_token };
      }

      return { success: false, error: 'Token não recebido' };
    } catch (error) {
      await this.removeToken();
      return {
        success: false,
        error: error.message,
      };
    }
  }

  // Métodos de OS
  async getOS(filters = {}) {
    return this.get('/api/v1/os', filters);
  }

  async getOSById(id) {
    return this.get(`/api/v1/os/${id}`);
  }

  async createOS(osData) {
    return this.post('/api/v1/os', osData);
  }

  async updateOS(id, osData) {
    return this.put(`/api/v1/os/${id}`, osData);
  }

  async updateOSStatus(id, status) {
    return this.patch(`/api/v1/os/${id}/status`, { status });
  }

  async getDashboardStats() {
    return this.get('/api/v1/os/dashboard-stats');
  }

  // Métodos de Agendamento
  async getAgendamentos(filters = {}) {
    return this.get('/api/v1/agendamentos', filters);
  }

  async getAgendamentoById(id) {
    return this.get(`/api/v1/agendamentos/${id}`);
  }

  async createAgendamento(agendamentoData) {
    return this.post('/api/v1/agendamentos', agendamentoData);
  }

  async updateAgendamento(id, agendamentoData) {
    return this.put(`/api/v1/agendamentos/${id}`, agendamentoData);
  }

  async getTodayAgenda() {
    const today = new Date().toISOString().split('T')[0];
    return this.get('/api/v1/agendamentos', { date: today });
  }

  // Métodos de Cliente
  async getClientes(filters = {}) {
    return this.get('/api/v1/clientes', filters);
  }

  async getClienteById(id) {
    return this.get(`/api/v1/clientes/${id}`);
  }

  async createCliente(clienteData) {
    return this.post('/api/v1/clientes', clienteData);
  }

  async updateCliente(id, clienteData) {
    return this.put(`/api/v1/clientes/${id}`, clienteData);
  }

  // Métodos de Produto
  async getProdutos(filters = {}) {
    return this.get('/api/v1/produtos', filters);
  }

  async getProdutoById(id) {
    return this.get(`/api/v1/produtos/${id}`);
  }

  // Métodos de Upload
  async uploadFile(file, type = 'image') {
    const formData = new FormData();
    formData.append('file', {
      uri: file.uri,
      type: file.type || 'image/jpeg',
      name: file.name || `${type}_${Date.now()}.jpg`,
    });
    formData.append('type', type);

    return this.makeRequest('/api/v1/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      body: formData,
    });
  }

  // Métodos de Comunicação
  async sendWhatsApp(data) {
    return this.post('/api/v1/comunicacao/whatsapp', data);
  }

  async getCommunicationTemplates() {
    return this.get('/api/v1/comunicacao/templates');
  }

  // Health Check
  async healthCheck() {
    try {
      const response = await this.get('/health');
      return { success: true, data: response };
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  // Métodos de Sincronização
  async syncData(data) {
    return this.post('/api/v1/sync', data);
  }

  async getLastSync() {
    return this.get('/api/v1/sync/last');
  }
}

// Instância singleton
const apiService = new ApiService();

export default apiService;