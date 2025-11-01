import React, { useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  Alert,
  Dimensions,
  PanResponder,
} from 'react-native';
import Svg, { Path } from 'react-native-svg';
import { captureRef } from 'react-native-view-shot';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { theme } from '../../styles/theme';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

export default function SignatureComponent({ 
  visible, 
  onClose, 
  onSignature, 
  title = 'Assinatura Digital' 
}) {
  const signatureRef = useRef(null);
  const [paths, setPaths] = useState([]);
  const [currentPath, setCurrentPath] = useState('');

  const panResponder = PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onMoveShouldSetPanResponder: () => true,

    onPanResponderGrant: (event) => {
      const { locationX, locationY } = event.nativeEvent;
      const newPath = `M${locationX.toFixed(2)},${locationY.toFixed(2)}`;
      setCurrentPath(newPath);
    },

    onPanResponderMove: (event) => {
      const { locationX, locationY } = event.nativeEvent;
      setCurrentPath(prev => `${prev} L${locationX.toFixed(2)},${locationY.toFixed(2)}`);
    },

    onPanResponderRelease: () => {
      if (currentPath) {
        setPaths(prev => [...prev, currentPath]);
        setCurrentPath('');
      }
    },
  });

  const clearSignature = () => {
    setPaths([]);
    setCurrentPath('');
  };

  const saveSignature = async () => {
    if (paths.length === 0 && !currentPath) {
      Alert.alert('Aviso', 'Por favor, faça sua assinatura antes de salvar.');
      return;
    }

    try {
      // Capturar a assinatura como imagem
      const uri = await captureRef(signatureRef, {
        format: 'png',
        quality: 1.0,
        result: 'tmpfile',
      });

      const signatureData = {
        uri,
        timestamp: new Date().toISOString(),
        paths: [...paths, currentPath].filter(Boolean),
        dimensions: {
          width: screenWidth - 40,
          height: 300,
        },
      };

      onSignature(signatureData);
      onClose();
      clearSignature();
    } catch (error) {
      console.error('Erro ao salvar assinatura:', error);
      Alert.alert('Erro', 'Falha ao salvar assinatura. Tente novamente.');
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={false}
      statusBarTranslucent
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Icon name="close" size={24} color={theme.colors.text} />
          </TouchableOpacity>
          <Text style={styles.title}>{title}</Text>
          <View style={styles.placeholder} />
        </View>

        {/* Instrução */}
        <View style={styles.instructionContainer}>
          <Text style={styles.instructionText}>
            Desenhe sua assinatura na área abaixo
          </Text>
        </View>

        {/* Área de assinatura */}
        <View style={styles.signatureContainer}>
          <View
            ref={signatureRef}
            style={styles.signatureArea}
            {...panResponder.panHandlers}
          >
            <Svg
              style={styles.signatureSvg}
              width={screenWidth - 40}
              height={300}
            >
              {/* Renderizar caminhos salvos */}
              {paths.map((path, index) => (
                <Path
                  key={index}
                  d={path}
                  stroke={theme.colors.primary}
                  strokeWidth={3}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  fill="none"
                />
              ))}
              
              {/* Renderizar caminho atual */}
              {currentPath && (
                <Path
                  d={currentPath}
                  stroke={theme.colors.primary}
                  strokeWidth={3}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  fill="none"
                />
              )}
            </Svg>

            {/* Linha de assinatura */}
            <View style={styles.signatureLine} />
            
            {/* Placeholder quando vazio */}
            {paths.length === 0 && !currentPath && (
              <View style={styles.placeholderContainer}>
                <Icon 
                  name="edit" 
                  size={48} 
                  color={theme.colors.disabled} 
                />
                <Text style={styles.placeholderText}>
                  Toque e arraste para assinar
                </Text>
              </View>
            )}
          </View>
        </View>

        {/* Ações */}
        <View style={styles.actionsContainer}>
          <TouchableOpacity
            style={[styles.actionButton, styles.clearButton]}
            onPress={clearSignature}
          >
            <Icon name="clear" size={20} color={theme.colors.error} />
            <Text style={[styles.actionButtonText, styles.clearButtonText]}>
              Limpar
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.saveButton]}
            onPress={saveSignature}
          >
            <Icon name="check" size={20} color={theme.colors.white} />
            <Text style={[styles.actionButtonText, styles.saveButtonText]}>
              Confirmar
            </Text>
          </TouchableOpacity>
        </View>

        {/* Informação */}
        <View style={styles.infoContainer}>
          <Text style={styles.infoText}>
            💡 Use o dedo para desenhar sua assinatura. Você pode limpar e refazer quantas vezes precisar.
          </Text>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  closeButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  placeholder: {
    width: 40,
  },
  instructionContainer: {
    padding: 20,
    alignItems: 'center',
  },
  instructionText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  signatureContainer: {
    flex: 1,
    paddingHorizontal: 20,
    justifyContent: 'center',
  },
  signatureArea: {
    height: 300,
    backgroundColor: theme.colors.white,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: theme.colors.border,
    borderStyle: 'dashed',
    position: 'relative',
    overflow: 'hidden',
  },
  signatureSvg: {
    position: 'absolute',
    top: 0,
    left: 0,
  },
  signatureLine: {
    position: 'absolute',
    bottom: 60,
    left: 40,
    right: 40,
    height: 1,
    backgroundColor: theme.colors.border,
  },
  placeholderContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  placeholderText: {
    fontSize: 16,
    color: theme.colors.disabled,
    marginTop: 12,
  },
  actionsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 20,
    gap: 16,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    gap: 8,
  },
  clearButton: {
    backgroundColor: theme.colors.errorBackground,
    borderWidth: 1,
    borderColor: theme.colors.error,
  },
  saveButton: {
    backgroundColor: theme.colors.primary,
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  clearButtonText: {
    color: theme.colors.error,
  },
  saveButtonText: {
    color: theme.colors.white,
  },
  infoContainer: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  infoText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
});