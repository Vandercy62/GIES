import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import LoadingScreen from '../../src/components/LoadingScreen';

describe('LoadingScreen Component', () => {
  it('renders correctly', () => {
    const { getByTestId } = render(<LoadingScreen />);
    expect(getByTestId('loading-screen')).toBeTruthy();
  });

  it('displays loading text', () => {
    const { getByText } = render(<LoadingScreen />);
    expect(getByText('Carregando...')).toBeTruthy();
  });

  it('shows activity indicator', () => {
    const { getByTestId } = render(<LoadingScreen />);
    expect(getByTestId('loading-indicator')).toBeTruthy();
  });

  it('accepts custom message prop', () => {
    const customMessage = 'Aguarde um momento...';
    const { getByText } = render(<LoadingScreen message={customMessage} />);
    expect(getByText(customMessage)).toBeTruthy();
  });

  it('has correct styling', async () => {
    const { getByTestId } = render(<LoadingScreen />);
    const container = getByTestId('loading-screen');
    
    await waitFor(() => {
      expect(container).toHaveStyle({
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
      });
    });
  });
});