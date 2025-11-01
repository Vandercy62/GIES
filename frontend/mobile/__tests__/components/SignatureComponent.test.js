import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import SignatureComponent from '../../src/components/SignatureComponent';

// Mock react-native-view-shot
jest.mock('react-native-view-shot', () => ({
  ViewShot: ({ children, onCapture, ...props }) => {
    const MockedViewShot = require('react-native').View;
    return <MockedViewShot {...props}>{children}</MockedViewShot>;
  },
  captureRef: jest.fn(() => Promise.resolve('mockImageUri')),
}));

describe('SignatureComponent', () => {
  const mockOnSignatureCapture = jest.fn();
  const mockOnClear = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders correctly', () => {
    const { getByTestId } = render(
      <SignatureComponent 
        onSignatureCapture={mockOnSignatureCapture}
        onClear={mockOnClear}
      />
    );
    expect(getByTestId('signature-component')).toBeTruthy();
  });

  it('displays signature pad', () => {
    const { getByTestId } = render(
      <SignatureComponent 
        onSignatureCapture={mockOnSignatureCapture}
        onClear={mockOnClear}
      />
    );
    expect(getByTestId('signature-pad')).toBeTruthy();
  });

  it('shows control buttons', () => {
    const { getByText } = render(
      <SignatureComponent 
        onSignatureCapture={mockOnSignatureCapture}
        onClear={mockOnClear}
      />
    );
    expect(getByText('Limpar')).toBeTruthy();
    expect(getByText('Salvar')).toBeTruthy();
  });

  it('handles clear button press', () => {
    const { getByText } = render(
      <SignatureComponent 
        onSignatureCapture={mockOnSignatureCapture}
        onClear={mockOnClear}
      />
    );
    
    fireEvent.press(getByText('Limpar'));
    expect(mockOnClear).toHaveBeenCalledTimes(1);
  });

  it('handles save button press', () => {
    const { getByText } = render(
      <SignatureComponent 
        onSignatureCapture={mockOnSignatureCapture}
        onClear={mockOnClear}
      />
    );
    
    fireEvent.press(getByText('Salvar'));
    expect(mockOnSignatureCapture).toHaveBeenCalledTimes(1);
  });

  it('disables save when no signature', () => {
    const { getByText } = render(
      <SignatureComponent 
        onSignatureCapture={mockOnSignatureCapture}
        onClear={mockOnClear}
        hasSignature={false}
      />
    );
    
    const saveButton = getByText('Salvar');
    expect(saveButton).toBeDisabled();
  });
});