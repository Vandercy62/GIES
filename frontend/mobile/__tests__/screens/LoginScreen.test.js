import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import LoginScreen from '../../../src/screens/auth/LoginScreen';
import authSlice from '../../../src/store/slices/authSlice';

// Mock navigation
const mockNavigate = jest.fn();
const mockNavigation = {
  navigate: mockNavigate,
  goBack: jest.fn(),
  reset: jest.fn(),
};

// Mock API Service
jest.mock('../../src/services/apiService', () => ({
  login: jest.fn(),
}));

import apiService from '../../../src/services/apiService';

describe('LoginScreen', () => {
  let store;

  beforeEach(() => {
    store = configureStore({
      reducer: {
        auth: authSlice,
      },
    });
    jest.clearAllMocks();
  });

  const renderLoginScreen = () => {
    return render(
      <Provider store={store}>
        <LoginScreen navigation={mockNavigation} />
      </Provider>
    );
  };

  it('renders correctly', () => {
    const { getByTestId } = renderLoginScreen();
    
    expect(getByTestId('login-screen')).toBeTruthy();
    expect(getByTestId('email-input')).toBeTruthy();
    expect(getByTestId('password-input')).toBeTruthy();
    expect(getByTestId('login-button')).toBeTruthy();
  });

  it('displays Primotex logo and title', () => {
    const { getByText, getByTestId } = renderLoginScreen();
    
    expect(getByText('Primotex Mobile')).toBeTruthy();
    expect(getByText('Sistema para Técnicos')).toBeTruthy();
    expect(getByTestId('logo')).toBeTruthy();
  });

  it('handles email input', () => {
    const { getByTestId } = renderLoginScreen();
    const emailInput = getByTestId('email-input');
    
    fireEvent.changeText(emailInput, 'teste@primotex.com');
    expect(emailInput.props.value).toBe('teste@primotex.com');
  });

  it('handles password input', () => {
    const { getByTestId } = renderLoginScreen();
    const passwordInput = getByTestId('password-input');
    
    fireEvent.changeText(passwordInput, 'senha123');
    expect(passwordInput.props.value).toBe('senha123');
  });

  it('validates email format', async () => {
    const { getByTestId, getByText } = renderLoginScreen();
    const emailInput = getByTestId('email-input');
    const loginButton = getByTestId('login-button');
    
    fireEvent.changeText(emailInput, 'email-invalido');
    fireEvent.press(loginButton);
    
    await waitFor(() => {
      expect(getByText('Email inválido')).toBeTruthy();
    });
  });

  it('validates required fields', async () => {
    const { getByTestId, getByText } = renderLoginScreen();
    const loginButton = getByTestId('login-button');
    
    fireEvent.press(loginButton);
    
    await waitFor(() => {
      expect(getByText('Email é obrigatório')).toBeTruthy();
      expect(getByText('Senha é obrigatória')).toBeTruthy();
    });
  });

  it('handles successful login', async () => {
    const mockUser = {
      id: 1,
      nome: 'Técnico Teste',
      email: 'teste@primotex.com'
    };
    
    apiService.login.mockResolvedValueOnce({
      access_token: 'jwt-token',
      user: mockUser
    });

    const { getByTestId } = renderLoginScreen();
    const emailInput = getByTestId('email-input');
    const passwordInput = getByTestId('password-input');
    const loginButton = getByTestId('login-button');
    
    fireEvent.changeText(emailInput, 'teste@primotex.com');
    fireEvent.changeText(passwordInput, 'senha123');
    fireEvent.press(loginButton);
    
    await waitFor(() => {
      expect(apiService.login).toHaveBeenCalledWith('teste@primotex.com', 'senha123');
      expect(mockNavigate).toHaveBeenCalledWith('Dashboard');
    });
  });

  it('handles login failure', async () => {
    apiService.login.mockRejectedValueOnce(new Error('Credenciais inválidas'));

    const { getByTestId, getByText } = renderLoginScreen();
    const emailInput = getByTestId('email-input');
    const passwordInput = getByTestId('password-input');
    const loginButton = getByTestId('login-button');
    
    fireEvent.changeText(emailInput, 'teste@primotex.com');
    fireEvent.changeText(passwordInput, 'senha-errada');
    fireEvent.press(loginButton);
    
    await waitFor(() => {
      expect(getByText('Credenciais inválidas')).toBeTruthy();
    });
  });

  it('shows loading state during login', async () => {
    apiService.login.mockImplementationOnce(() => 
      new Promise(resolve => setTimeout(() => resolve({ user: {}, access_token: 'token' }), 100))
    );

    const { getByTestId } = renderLoginScreen();
    const emailInput = getByTestId('email-input');
    const passwordInput = getByTestId('password-input');
    const loginButton = getByTestId('login-button');
    
    fireEvent.changeText(emailInput, 'teste@primotex.com');
    fireEvent.changeText(passwordInput, 'senha123');
    fireEvent.press(loginButton);
    
    expect(getByTestId('loading-indicator')).toBeTruthy();
    expect(loginButton).toBeDisabled();
  });

  it('toggles password visibility', () => {
    const { getByTestId } = renderLoginScreen();
    const passwordInput = getByTestId('password-input');
    const toggleButton = getByTestId('password-toggle');
    
    expect(passwordInput.props.secureTextEntry).toBe(true);
    
    fireEvent.press(toggleButton);
    expect(passwordInput.props.secureTextEntry).toBe(false);
    
    fireEvent.press(toggleButton);
    expect(passwordInput.props.secureTextEntry).toBe(true);
  });

  it('has biometric login option', () => {
    const { getByTestId } = renderLoginScreen();
    expect(getByTestId('biometric-login-button')).toBeTruthy();
  });
});