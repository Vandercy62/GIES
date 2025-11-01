import { DefaultTheme } from 'react-native-paper';

/**
 * Tema personalizado Primotex Mobile
 * Cores e estilos da marca
 */
export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#1976D2',      // Azul Primotex
    secondary: '#FFC107',    // Amarelo/Dourado
    accent: '#FF5722',       // Laranja para alertas
    background: '#F5F5F5',   // Cinza claro de fundo
    surface: '#FFFFFF',      // Branco superfícies
    text: '#212121',         // Preto texto principal
    textSecondary: '#757575', // Cinza texto secundário
    success: '#4CAF50',      // Verde sucesso
    warning: '#FF9800',      // Laranja avisos
    error: '#F44336',        // Vermelho erro
    info: '#2196F3',         // Azul informação
    disabled: '#BDBDBD',     // Cinza desabilitado
    placeholder: '#9E9E9E',  // Cinza placeholder
    
    // Cores específicas Primotex
    primotexBlue: '#1976D2',
    primotexGold: '#FFC107',
    fieldGreen: '#8BC34A',   // Verde para campo
    techOrange: '#FF6F00',   // Laranja técnicos
  },
  fonts: {
    ...DefaultTheme.fonts,
    regular: {
      fontFamily: 'System',
      fontWeight: 'normal',
    },
    medium: {
      fontFamily: 'System',
      fontWeight: '500',
    },
    light: {
      fontFamily: 'System',
      fontWeight: '300',
    },
    thin: {
      fontFamily: 'System',
      fontWeight: '100',
    },
  },
  roundness: 8,
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
};

/**
 * Estilos globais do app
 */
export const globalStyles = {
  // Containers
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  
  containerPadded: {
    flex: 1,
    backgroundColor: theme.colors.background,
    padding: theme.spacing.md,
  },
  
  // Cartões
  card: {
    backgroundColor: theme.colors.surface,
    marginVertical: theme.spacing.sm,
    marginHorizontal: theme.spacing.md,
    borderRadius: theme.roundness,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
  },
  
  cardContent: {
    padding: theme.spacing.md,
  },
  
  // Texto
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  
  subtitle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  
  body: {
    fontSize: 16,
    color: theme.colors.text,
    lineHeight: 24,
  },
  
  caption: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  
  // Botões
  buttonPrimary: {
    backgroundColor: theme.colors.primary,
    marginVertical: theme.spacing.sm,
  },
  
  buttonSecondary: {
    backgroundColor: theme.colors.secondary,
    marginVertical: theme.spacing.sm,
  },
  
  buttonSuccess: {
    backgroundColor: theme.colors.success,
    marginVertical: theme.spacing.sm,
  },
  
  buttonWarning: {
    backgroundColor: theme.colors.warning,
    marginVertical: theme.spacing.sm,
  },
  
  buttonError: {
    backgroundColor: theme.colors.error,
    marginVertical: theme.spacing.sm,
  },
  
  // Formulários
  input: {
    marginVertical: theme.spacing.sm,
    backgroundColor: theme.colors.surface,
  },
  
  // Status badges
  statusBadge: {
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: theme.spacing.xs,
    borderRadius: theme.roundness,
    alignSelf: 'flex-start',
  },
  
  statusSolicitacao: {
    backgroundColor: '#E3F2FD',
    borderColor: theme.colors.info,
  },
  
  statusVisita: {
    backgroundColor: '#FFF3E0',
    borderColor: theme.colors.warning,
  },
  
  statusOrcamento: {
    backgroundColor: '#F3E5F5',
    borderColor: '#9C27B0',
  },
  
  statusAprovacao: {
    backgroundColor: '#E8F5E8',
    borderColor: theme.colors.success,
  },
  
  statusExecucao: {
    backgroundColor: '#FFF8E1',
    borderColor: theme.colors.techOrange,
  },
  
  statusEntrega: {
    backgroundColor: '#E0F2F1',
    borderColor: '#009688',
  },
  
  statusPosVenda: {
    backgroundColor: '#F1F8E9',
    borderColor: theme.colors.fieldGreen,
  },
  
  // Layout
  row: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  
  rowSpaceBetween: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  
  column: {
    flexDirection: 'column',
  },
  
  center: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  
  // Espaçamentos
  marginTop: {
    marginTop: theme.spacing.md,
  },
  
  marginBottom: {
    marginBottom: theme.spacing.md,
  },
  
  marginHorizontal: {
    marginHorizontal: theme.spacing.md,
  },
  
  paddingAll: {
    padding: theme.spacing.md,
  },
  
  // Sombras
  shadow: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  
  shadowLight: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.18,
    shadowRadius: 1.00,
    elevation: 1,
  },
};