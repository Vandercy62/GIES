import * as Camera from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';
import * as ImagePicker from 'expo-image-picker';
import { Alert } from 'react-native';

class CameraService {
  constructor() {
    this.hasPermissions = false;
  }

  // Solicitar permissões de câmera e galeria
  async requestPermissions() {
    try {
      const cameraPermission = await Camera.requestCameraPermissionsAsync();
      const mediaPermission = await MediaLibrary.requestPermissionsAsync();
      const imagePermission = await ImagePicker.requestMediaLibraryPermissionsAsync();

      this.hasPermissions = 
        cameraPermission.status === 'granted' &&
        mediaPermission.status === 'granted' &&
        imagePermission.status === 'granted';

      return this.hasPermissions;
    } catch (error) {
      console.error('Erro ao solicitar permissões:', error);
      return false;
    }
  }

  // Verificar se já tem permissões
  async checkPermissions() {
    try {
      const cameraPermission = await Camera.getCameraPermissionsAsync();
      const mediaPermission = await MediaLibrary.getPermissionsAsync();
      const imagePermission = await ImagePicker.getMediaLibraryPermissionsAsync();

      this.hasPermissions = 
        cameraPermission.status === 'granted' &&
        mediaPermission.status === 'granted' &&
        imagePermission.status === 'granted';

      return this.hasPermissions;
    } catch (error) {
      console.error('Erro ao verificar permissões:', error);
      return false;
    }
  }

  // Tirar foto com a câmera
  async takePhoto(options = {}) {
    try {
      if (!this.hasPermissions) {
        const granted = await this.requestPermissions();
        if (!granted) {
          Alert.alert('Erro', 'Permissões de câmera são necessárias.');
          return null;
        }
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: options.allowsEditing || true,
        aspect: options.aspect || [4, 3],
        quality: options.quality || 0.8,
        base64: options.base64 || false,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const asset = result.assets[0];
        return {
          uri: asset.uri,
          width: asset.width,
          height: asset.height,
          type: 'image/jpeg',
          name: `photo_${Date.now()}.jpg`,
          base64: asset.base64,
        };
      }

      return null;
    } catch (error) {
      console.error('Erro ao tirar foto:', error);
      Alert.alert('Erro', 'Falha ao tirar foto. Tente novamente.');
      return null;
    }
  }

  // Selecionar imagem da galeria
  async pickImage(options = {}) {
    try {
      if (!this.hasPermissions) {
        const granted = await this.requestPermissions();
        if (!granted) {
          Alert.alert('Erro', 'Permissões de galeria são necessárias.');
          return null;
        }
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: options.allowsEditing || true,
        aspect: options.aspect || [4, 3],
        quality: options.quality || 0.8,
        base64: options.base64 || false,
        allowsMultipleSelection: options.multiple || false,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        if (options.multiple) {
          return result.assets.map(asset => ({
            uri: asset.uri,
            width: asset.width,
            height: asset.height,
            type: 'image/jpeg',
            name: `image_${Date.now()}_${Math.random().toString(36).substr(2, 9)}.jpg`,
            base64: asset.base64,
          }));
        } else {
          const asset = result.assets[0];
          return {
            uri: asset.uri,
            width: asset.width,
            height: asset.height,
            type: 'image/jpeg',
            name: `image_${Date.now()}.jpg`,
            base64: asset.base64,
          };
        }
      }

      return null;
    } catch (error) {
      console.error('Erro ao selecionar imagem:', error);
      Alert.alert('Erro', 'Falha ao selecionar imagem. Tente novamente.');
      return null;
    }
  }

  // Mostrar opções de imagem (câmera ou galeria)
  async showImageOptions(options = {}) {
    return new Promise((resolve) => {
      Alert.alert(
        'Selecionar Imagem',
        'Escolha uma opção:',
        [
          {
            text: 'Cancelar',
            style: 'cancel',
            onPress: () => resolve(null),
          },
          {
            text: 'Câmera',
            onPress: async () => {
              const result = await this.takePhoto(options);
              resolve(result);
            },
          },
          {
            text: 'Galeria',
            onPress: async () => {
              const result = await this.pickImage(options);
              resolve(result);
            },
          },
        ],
        { cancelable: true, onDismiss: () => resolve(null) }
      );
    });
  }

  // Salvar imagem na galeria
  async saveToGallery(uri) {
    try {
      if (!this.hasPermissions) {
        const granted = await this.requestPermissions();
        if (!granted) {
          Alert.alert('Erro', 'Permissões de galeria são necessárias.');
          return false;
        }
      }

      const asset = await MediaLibrary.createAssetAsync(uri);
      await MediaLibrary.createAlbumAsync('Primotex ERP', asset, false);
      
      Alert.alert('Sucesso', 'Imagem salva na galeria!');
      return true;
    } catch (error) {
      console.error('Erro ao salvar na galeria:', error);
      Alert.alert('Erro', 'Falha ao salvar imagem na galeria.');
      return false;
    }
  }

  // Redimensionar imagem
  async resizeImage(uri, options = {}) {
    try {
      const { manipulateAsync, SaveFormat } = await import('expo-image-manipulator');
      
      const manipulatorOptions = [];
      
      if (options.width || options.height) {
        manipulatorOptions.push({
          resize: {
            width: options.width,
            height: options.height,
          },
        });
      }

      if (options.rotate) {
        manipulatorOptions.push({
          rotate: options.rotate,
        });
      }

      const result = await manipulateAsync(
        uri,
        manipulatorOptions,
        {
          compress: options.compress || 0.8,
          format: SaveFormat.JPEG,
          base64: options.base64 || false,
        }
      );

      return {
        uri: result.uri,
        width: result.width,
        height: result.height,
        base64: result.base64,
      };
    } catch (error) {
      console.error('Erro ao redimensionar imagem:', error);
      return null;
    }
  }
}

export const cameraService = new CameraService();
export default cameraService;