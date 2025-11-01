import apiService from '../../src/services/apiService';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
}));

// Mock global fetch
global.fetch = jest.fn();

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch.mockClear();
  });

  describe('Authentication', () => {
    it('should login with valid credentials', async () => {
      const mockResponse = {
        access_token: 'mock-token',
        user: {
          id: 1,
          email: 'teste@primotex.com',
          nome: 'Teste'
        }
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.login({
        email: 'teste@primotex.com',
        password: 'senha123'
      });
      
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/auth/login'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: expect.stringContaining('teste@primotex.com'),
        })
      );
      
      expect(result.success).toBe(true);
      expect(result.data.access_token).toBe('mock-token');
    });

    it('should handle login failure', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid credentials' }),
      });

      const result = await apiService.login({
        email: 'invalid@email.com', 
        password: 'wrongpass'
      });
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Sessão expirada');
    });
  });

  describe('Ordem de Serviço', () => {
    it('should fetch OS list', async () => {
      const mockOS = [
        { id: 1, numero: 'OS001', cliente: 'Cliente 1' },
        { id: 2, numero: 'OS002', cliente: 'Cliente 2' },
      ];

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockOS,
      });

      const result = await apiService.getOS();
      
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/os'),
        expect.objectContaining({
          method: 'GET',
        })
      );
      
      expect(result).toEqual(mockOS);
    });

    it('should update OS status', async () => {
      const osId = 1;
      const newStatus = 'em_andamento';
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      await apiService.updateOSStatus(osId, newStatus);
      
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/v1/os/${osId}/status`),
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify({ status: newStatus }),
        })
      );
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network request failed'));

      await expect(
        apiService.getOS()
      ).rejects.toThrow('Erro de conexão. Verifique sua internet.');
    });

    it('should handle HTTP errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Server error' }),
      });

      await expect(
        apiService.getOS()
      ).rejects.toThrow('Server error');
    });
  });

  describe('Token Management', () => {
    it('should include token in requests', async () => {
      const mockToken = 'test-token';
      require('@react-native-async-storage/async-storage').getItem.mockResolvedValue(mockToken);

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await apiService.getOS();

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': `Bearer ${mockToken}`,
          }),
        })
      );
    });

    it('should handle token removal on logout', async () => {
      const removeItemMock = require('@react-native-async-storage/async-storage').removeItem;
      
      const result = await apiService.logout();
      
      expect(removeItemMock).toHaveBeenCalledWith('@primotex:token');
      expect(result.success).toBe(true);
    });

    it('should refresh token successfully', async () => {
      const newToken = 'new-access-token';
      const setItemMock = require('@react-native-async-storage/async-storage').setItem;
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: newToken }),
      });

      const result = await apiService.refreshToken();

      expect(setItemMock).toHaveBeenCalledWith('@primotex:token', newToken);
      expect(result.success).toBe(true);
      expect(result.token).toBe(newToken);
    });

    it('should handle refresh token failure', async () => {
      const removeItemMock = require('@react-native-async-storage/async-storage').removeItem;
      
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await apiService.refreshToken();

      expect(removeItemMock).toHaveBeenCalledWith('@primotex:token');
      expect(result.success).toBe(false);
      expect(result.error).toBe('Network error');
    });
  });

  describe('OS Management', () => {
    it('should get OS by ID', async () => {
      const osId = 123;
      const mockOS = { id: osId, numero: 'OS-123', status: 'Pendente' };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockOS,
      });

      const result = await apiService.getOSById(osId);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/v1/os/${osId}`),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result).toEqual(mockOS);
    });

    it('should create new OS', async () => {
      const osData = {
        cliente_id: 1,
        servico: 'Instalação',
        endereco: 'Rua Teste, 123'
      };
      const mockResponse = { id: 456, ...osData, status: 'Criada' };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.createOS(osData);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/os'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(osData),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should update OS data', async () => {
      const osId = 789;
      const updateData = { observacoes: 'Atualização teste' };
      const mockResponse = { success: true, message: 'OS atualizada' };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.updateOS(osId, updateData);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/v1/os/${osId}`),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(updateData),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should get dashboard stats', async () => {
      const mockStats = {
        total_os: 50,
        pendentes: 10,
        em_andamento: 5,
        concluidas: 35
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats,
      });

      const result = await apiService.getDashboardStats();

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/os/dashboard-stats'),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result).toEqual(mockStats);
    });
  });

  describe('Agendamento Management', () => {
    it('should get agendamentos list', async () => {
      const filters = { date: '2024-01-01' };
      const mockAgendamentos = [
        { id: 1, titulo: 'Reunião', data: '2024-01-01' },
        { id: 2, titulo: 'Visita', data: '2024-01-01' }
      ];

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAgendamentos,
      });

      const result = await apiService.getAgendamentos(filters);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/agendamentos?date=2024-01-01'),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result).toEqual(mockAgendamentos);
    });

    it('should create new agendamento', async () => {
      const agendamentoData = {
        titulo: 'Nova Reunião',
        data: '2024-01-02',
        hora: '10:00'
      };
      const mockResponse = { id: 999, ...agendamentoData };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.createAgendamento(agendamentoData);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/agendamentos'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(agendamentoData),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should get today agenda', async () => {
      const today = new Date().toISOString().split('T')[0];
      const mockTodayAgenda = [
        { id: 1, titulo: 'Evento Hoje', data: today }
      ];

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTodayAgenda,
      });

      const result = await apiService.getTodayAgenda();

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/v1/agendamentos?date=${today}`),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result).toEqual(mockTodayAgenda);
    });
  });

  describe('Cliente Management', () => {
    it('should get clientes list', async () => {
      const filters = { ativo: true };
      const mockClientes = [
        { id: 1, nome: 'Cliente A', email: 'clientea@test.com' },
        { id: 2, nome: 'Cliente B', email: 'clienteb@test.com' }
      ];

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockClientes,
      });

      const result = await apiService.getClientes(filters);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/clientes?ativo=true'),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result).toEqual(mockClientes);
    });

    it('should get cliente by ID', async () => {
      const clienteId = 555;
      const mockCliente = { 
        id: clienteId, 
        nome: 'Cliente Teste', 
        telefone: '(11) 99999-9999' 
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockCliente,
      });

      const result = await apiService.getClienteById(clienteId);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/v1/clientes/${clienteId}`),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result).toEqual(mockCliente);
    });
  });

  describe('Health Check', () => {
    it('should perform health check successfully', async () => {
      const mockHealth = { status: 'ok', timestamp: '2024-01-01T10:00:00Z' };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealth,
      });

      const result = await apiService.healthCheck();

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/health'),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockHealth);
    });

    it('should handle health check failure', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Service unavailable'));

      const result = await apiService.healthCheck();

      expect(result.success).toBe(false);
      expect(result.error).toBe('Service unavailable');
    });
  });

  describe('Communication', () => {
    it('should send WhatsApp message', async () => {
      const whatsappData = {
        to: '+5511999999999',
        message: 'Teste de mensagem',
        type: 'text'
      };
      const mockResponse = { messageId: 'msg_123', sent: true };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.sendWhatsApp(whatsappData);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/comunicacao/whatsapp'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(whatsappData),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should get communication templates', async () => {
      const mockTemplates = [
        { id: 1, name: 'Boas-vindas', content: 'Olá {nome}!' },
        { id: 2, name: 'Confirmação', content: 'Agendamento confirmado' }
      ];

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTemplates,
      });

      const result = await apiService.getCommunicationTemplates();

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/comunicacao/templates'),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result).toEqual(mockTemplates);
    });
  });
});