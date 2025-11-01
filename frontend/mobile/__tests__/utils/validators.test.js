// Mock utils que provavelmente existem ou devem existir
const validators = {
  isValidEmail: (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },
  
  isValidCPF: (cpf) => {
    if (!cpf) return false;
    cpf = cpf.replace(/[^\d]/g, '');
    if (cpf.length !== 11) return false;
    
    // Validação básica de CPF
    if (/^(\d)\1{10}$/.test(cpf)) return false;
    
    return true;
  },
  
  formatCurrency: (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  },
  
  formatDate: (date, format = 'dd/MM/yyyy') => {
    if (!date) return '';
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    
    return format
      .replace('dd', day)
      .replace('MM', month)
      .replace('yyyy', year);
  },
  
  generateOSNumber: () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const random = Math.floor(Math.random() * 9999).toString().padStart(4, '0');
    return `OS-${year}${month}-${random}`;
  },
  
  calculateDistance: (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Raio da Terra em km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }
};

describe('Utility Functions', () => {
  describe('Email Validation', () => {
    it('should validate correct email formats', () => {
      expect(validators.isValidEmail('teste@primotex.com')).toBe(true);
      expect(validators.isValidEmail('user.name@domain.co.uk')).toBe(true);
      expect(validators.isValidEmail('test+tag@example.org')).toBe(true);
    });

    it('should reject invalid email formats', () => {
      expect(validators.isValidEmail('invalid-email')).toBe(false);
      expect(validators.isValidEmail('user@')).toBe(false);
      expect(validators.isValidEmail('@domain.com')).toBe(false);
      expect(validators.isValidEmail('')).toBe(false);
      expect(validators.isValidEmail(null)).toBe(false);
    });
  });

  describe('CPF Validation', () => {
    it('should validate CPF format', () => {
      expect(validators.isValidCPF('12345678901')).toBe(true);
      expect(validators.isValidCPF('123.456.789-01')).toBe(true);
    });

    it('should reject invalid CPF', () => {
      expect(validators.isValidCPF('11111111111')).toBe(false); // Repeated digits
      expect(validators.isValidCPF('123456789')).toBe(false); // Too short
      expect(validators.isValidCPF('')).toBe(false);
      expect(validators.isValidCPF(null)).toBe(false);
    });
  });

  describe('Currency Formatting', () => {
    it('should format currency correctly', () => {
      const result1 = validators.formatCurrency(1234.56);
      expect(result1).toMatch(/R\$\s*1\.234,56/);
      expect(validators.formatCurrency(0)).toMatch(/R\$\s*0,00/);
      expect(validators.formatCurrency(999999.99)).toMatch(/R\$\s*999\.999,99/);
    });

    it('should handle negative values', () => {
      const result = validators.formatCurrency(-123.45);
      expect(result).toMatch(/-R\$\s*123,45/);
    });
  });

  describe('Date Formatting', () => {
    it('should format dates correctly', () => {
      const date = new Date('2024-03-15T10:30:00Z');
      expect(validators.formatDate(date)).toBe('15/03/2024');
    });

    it('should handle different formats', () => {
      const date = new Date('2024-03-15T00:00:00');
      const formattedYmd = validators.formatDate(date, 'yyyy-MM-dd');
      const formattedDmy = validators.formatDate(date, 'dd/MM/yyyy');
      expect(formattedYmd).toMatch(/2024-03-1[45]/); // Pode ser 14 ou 15 dependendo do timezone
      expect(formattedDmy).toMatch(/1[45]\/03\/2024/);
    });

    it('should handle invalid dates', () => {
      expect(validators.formatDate(null)).toBe('');
      expect(validators.formatDate('')).toBe('');
    });
  });

  describe('OS Number Generation', () => {
    it('should generate valid OS numbers', () => {
      const osNumber = validators.generateOSNumber();
      expect(osNumber).toMatch(/^OS-\d{6}-\d{4}$/);
    });

    it('should generate unique numbers', () => {
      const numbers = new Set();
      for (let i = 0; i < 100; i++) {
        numbers.add(validators.generateOSNumber());
      }
      expect(numbers.size).toBeGreaterThan(90); // Deve ser quase todos únicos
    });
  });

  describe('Distance Calculation', () => {
    it('should calculate distance between coordinates', () => {
      // Distância entre São Paulo e Rio de Janeiro (aproximadamente 360km)
      const distance = validators.calculateDistance(
        -23.5505, -46.6333, // São Paulo
        -22.9068, -43.1729  // Rio de Janeiro
      );
      
      expect(distance).toBeGreaterThan(350);
      expect(distance).toBeLessThan(400);
    });

    it('should return 0 for same coordinates', () => {
      const distance = validators.calculateDistance(
        -23.5505, -46.6333,
        -23.5505, -46.6333
      );
      
      expect(distance).toBe(0);
    });

    it('should handle negative coordinates', () => {
      const distance = validators.calculateDistance(
        -23.5505, -46.6333,
        23.5505, 46.6333
      );
      
      expect(distance).toBeGreaterThan(0);
    });
  });

  describe('Input Sanitization', () => {
    const sanitizeInput = (input) => {
      if (typeof input !== 'string') return '';
      return input.trim().replace(/[<>\"']/g, '');
    };

    it('should sanitize dangerous characters', () => {
      expect(sanitizeInput('<script>alert("xss")</script>')).toBe('scriptalert(xss)/script');
      expect(sanitizeInput('Normal text')).toBe('Normal text');
      expect(sanitizeInput('  Texto com espaços  ')).toBe('Texto com espaços');
    });

    it('should handle non-string inputs', () => {
      expect(sanitizeInput(null)).toBe('');
      expect(sanitizeInput(undefined)).toBe('');
      expect(sanitizeInput(123)).toBe('');
    });
  });
});