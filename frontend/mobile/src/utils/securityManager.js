/**
 * Sistema de Segurança para Produção
 * Validação, criptografia e proteção de dados
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import CryptoJS from 'crypto-js';
import { Platform } from 'react-native';

class SecurityManager {
  constructor() {
    this.secretKey = 'PRIMOTEX_SECURITY_KEY_2024';
    this.maxLoginAttempts = 5;
    this.sessionTimeout = 30 * 60 * 1000; // 30 minutos
    this.isProduction = __DEV__ === false;
  }

  // Criptografia de dados sensíveis
  encrypt(data) {
    try {
      const encrypted = CryptoJS.AES.encrypt(JSON.stringify(data), this.secretKey).toString();
      return encrypted;
    } catch (error) {
      console.error('Erro na criptografia:', error);
      return null;
    }
  }

  decrypt(encryptedData) {
    try {
      const bytes = CryptoJS.AES.decrypt(encryptedData, this.secretKey);
      const decrypted = bytes.toString(CryptoJS.enc.Utf8);
      return JSON.parse(decrypted);
    } catch (error) {
      console.error('Erro na descriptografia:', error);
      return null;
    }
  }

  // Validação de entrada
  sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    
    // Remover caracteres potencialmente perigosos
    return input
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+="[^"]*"/gi, '')
      .trim();
  }

  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  validateCPF(cpf) {
    const cleanCPF = cpf.replace(/\D/g, '');
    if (cleanCPF.length !== 11) return false;
    
    // Validação básica de CPF
    let sum = 0;
    for (let i = 0; i < 9; i++) {
      sum += parseInt(cleanCPF.charAt(i)) * (10 - i);
    }
    let remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cleanCPF.charAt(9))) return false;
    
    sum = 0;
    for (let i = 0; i < 10; i++) {
      sum += parseInt(cleanCPF.charAt(i)) * (11 - i);
    }
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cleanCPF.charAt(10))) return false;
    
    return true;
  }

  validateCNPJ(cnpj) {
    const cleanCNPJ = cnpj.replace(/\D/g, '');
    if (cleanCNPJ.length !== 14) return false;
    
    // Validação básica de CNPJ
    const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    
    let sum = 0;
    for (let i = 0; i < 12; i++) {
      sum += parseInt(cleanCNPJ.charAt(i)) * weights1[i];
    }
    let remainder = sum % 11;
    const digit1 = remainder < 2 ? 0 : 11 - remainder;
    
    if (digit1 !== parseInt(cleanCNPJ.charAt(12))) return false;
    
    sum = 0;
    for (let i = 0; i < 13; i++) {
      sum += parseInt(cleanCNPJ.charAt(i)) * weights2[i];
    }
    remainder = sum % 11;
    const digit2 = remainder < 2 ? 0 : 11 - remainder;
    
    return digit2 === parseInt(cleanCNPJ.charAt(13));
  }

  // Controle de tentativas de login
  async recordLoginAttempt(username, success) {
    try {
      const attemptsKey = `login_attempts_${username}`;
      const attempts = await AsyncStorage.getItem(attemptsKey);
      let attemptData = attempts ? JSON.parse(attempts) : { count: 0, lastAttempt: null };
      
      if (success) {
        // Reset em caso de sucesso
        await AsyncStorage.removeItem(attemptsKey);
        return { blocked: false, remainingAttempts: this.maxLoginAttempts };
      } else {
        // Incrementar tentativas falhadas
        attemptData.count += 1;
        attemptData.lastAttempt = Date.now();
        
        await AsyncStorage.setItem(attemptsKey, JSON.stringify(attemptData));
        
        const isBlocked = attemptData.count >= this.maxLoginAttempts;
        const remainingAttempts = Math.max(0, this.maxLoginAttempts - attemptData.count);
        
        return { blocked: isBlocked, remainingAttempts };
      }
    } catch (error) {
      console.error('Erro ao registrar tentativa de login:', error);
      return { blocked: false, remainingAttempts: this.maxLoginAttempts };
    }
  }

  async checkLoginBlock(username) {
    try {
      const attemptsKey = `login_attempts_${username}`;
      const attempts = await AsyncStorage.getItem(attemptsKey);
      
      if (!attempts) return { blocked: false, remainingAttempts: this.maxLoginAttempts };
      
      const attemptData = JSON.parse(attempts);
      const isBlocked = attemptData.count >= this.maxLoginAttempts;
      
      // Verificar se o bloqueio expirou (24 horas)
      const blockExpired = Date.now() - attemptData.lastAttempt > 24 * 60 * 60 * 1000;
      
      if (isBlocked && blockExpired) {
        await AsyncStorage.removeItem(attemptsKey);
        return { blocked: false, remainingAttempts: this.maxLoginAttempts };
      }
      
      const remainingAttempts = Math.max(0, this.maxLoginAttempts - attemptData.count);
      return { blocked: isBlocked, remainingAttempts };
      
    } catch (error) {
      console.error('Erro ao verificar bloqueio de login:', error);
      return { blocked: false, remainingAttempts: this.maxLoginAttempts };
    }
  }

  // Validação de sessão
  async validateSession() {
    try {
      const sessionData = await AsyncStorage.getItem('user_session');
      if (!sessionData) return false;
      
      const session = JSON.parse(sessionData);
      const now = Date.now();
      
      // Verificar expiração da sessão
      if (now - session.lastActivity > this.sessionTimeout) {
        await this.clearSession();
        return false;
      }
      
      // Atualizar última atividade
      session.lastActivity = now;
      await AsyncStorage.setItem('user_session', JSON.stringify(session));
      
      return true;
    } catch (error) {
      console.error('Erro ao validar sessão:', error);
      return false;
    }
  }

  async clearSession() {
    try {
      await AsyncStorage.multiRemove([
        'user_session',
        'auth_token',
        'user_data'
      ]);
    } catch (error) {
      console.error('Erro ao limpar sessão:', error);
    }
  }

  // Logs de segurança
  logSecurityEvent(event, details = {}) {
    const securityLog = {
      event,
      details,
      timestamp: Date.now(),
      platform: Platform.OS,
      deviceInfo: {
        os: Platform.OS,
        version: Platform.Version
      }
    };
    
    if (this.isProduction) {
      // Em produção, apenas logs críticos
      if (event === 'login_blocked' || event === 'session_expired' || event === 'invalid_access') {
        console.warn('🔒 Security Event:', securityLog);
      }
    } else {
      console.log('🔒 Security Event:', securityLog);
    }
    
    // Salvar em storage para auditoria
    this.saveSecurityLog(securityLog);
  }

  async saveSecurityLog(logEntry) {
    try {
      const logsKey = 'security_logs';
      const existingLogs = await AsyncStorage.getItem(logsKey);
      const logs = existingLogs ? JSON.parse(existingLogs) : [];
      
      logs.push(logEntry);
      
      // Manter apenas os últimos 50 logs
      if (logs.length > 50) {
        logs.splice(0, logs.length - 50);
      }
      
      await AsyncStorage.setItem(logsKey, JSON.stringify(logs));
    } catch (error) {
      console.error('Erro ao salvar log de segurança:', error);
    }
  }

  // Validação de permissões
  validatePermission(userRole, requiredPermission) {
    const permissions = {
      'admin': ['read', 'write', 'delete', 'manage'],
      'tecnico': ['read', 'write'],
      'supervisor': ['read', 'write', 'manage'],
      'consulta': ['read']
    };
    
    const userPermissions = permissions[userRole] || [];
    return userPermissions.includes(requiredPermission);
  }

  // Sanitização de dados para API
  sanitizeApiData(data) {
    if (typeof data !== 'object' || data === null) {
      return this.sanitizeInput(data);
    }
    
    const sanitized = {};
    for (const [key, value] of Object.entries(data)) {
      if (Array.isArray(value)) {
        sanitized[key] = value.map(item => this.sanitizeApiData(item));
      } else if (typeof value === 'object' && value !== null) {
        sanitized[key] = this.sanitizeApiData(value);
      } else {
        sanitized[key] = this.sanitizeInput(value);
      }
    }
    
    return sanitized;
  }

  // Rate Limiting
  async checkRateLimit(action, limit = 10, windowMs = 60000) {
    try {
      const rateLimitKey = `rate_limit_${action}`;
      const rateLimitData = await AsyncStorage.getItem(rateLimitKey);
      
      let attempts = rateLimitData ? JSON.parse(rateLimitData) : { count: 0, resetTime: Date.now() + windowMs };
      
      // Reset se a janela de tempo passou
      if (Date.now() > attempts.resetTime) {
        attempts = { count: 0, resetTime: Date.now() + windowMs };
      }
      
      // Verificar limite
      if (attempts.count >= limit) {
        return { allowed: false, resetTime: attempts.resetTime };
      }
      
      // Incrementar contador
      attempts.count += 1;
      await AsyncStorage.setItem(rateLimitKey, JSON.stringify(attempts));
      
      return { allowed: true, remaining: limit - attempts.count };
      
    } catch (error) {
      console.error('Erro ao verificar rate limit:', error);
      return { allowed: true, remaining: limit };
    }
  }
}

// Instância global
const securityManager = new SecurityManager();

export default securityManager;