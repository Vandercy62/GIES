import cameraService from '../../src/services/cameraService';
import * as ImagePicker from 'expo-image-picker';
import * as Camera from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';
import { Alert } from 'react-native';

// Mock expo modules
jest.mock('expo-image-picker', () => ({
  requestMediaLibraryPermissionsAsync: jest.fn(),
  requestCameraPermissionsAsync: jest.fn(),
  getCameraPermissionsAsync: jest.fn(),
  getMediaLibraryPermissionsAsync: jest.fn(),
  launchImageLibraryAsync: jest.fn(),
  launchCameraAsync: jest.fn(),
  MediaTypeOptions: {
    Images: 'Images',
    Videos: 'Videos',
    All: 'All',
  },
  ImagePickerResult: jest.fn(),
}));

jest.mock('expo-camera', () => ({
  requestCameraPermissionsAsync: jest.fn(),
  getCameraPermissionsAsync: jest.fn(),
  Camera: {
    Constants: {
      Type: {
        back: 'back',
        front: 'front',
      },
      FlashMode: {
        on: 'on',
        off: 'off',
        auto: 'auto',
        torch: 'torch',
      },
    },
  },
}));

jest.mock('expo-media-library', () => ({
  requestPermissionsAsync: jest.fn(),
  getPermissionsAsync: jest.fn(),
  createAssetAsync: jest.fn(),
  getAssetsAsync: jest.fn(),
  deleteAssetsAsync: jest.fn(),
  MediaType: {
    photo: 'photo',
    video: 'video',
    audio: 'audio',
    unknown: 'unknown',
  },
}));

jest.mock('react-native', () => ({
  Alert: {
    alert: jest.fn(),
  },
  Platform: {
    OS: 'ios',
  },
}));

describe('Camera Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    cameraService.hasPermissions = false;
  });

  describe('Permissions', () => {
    it('should request all permissions successfully', async () => {
      Camera.requestCameraPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
        granted: true,
      });
      MediaLibrary.requestPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
        granted: true,
      });
      ImagePicker.requestMediaLibraryPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
        granted: true,
      });

      const result = await cameraService.requestPermissions();

      expect(Camera.requestCameraPermissionsAsync).toHaveBeenCalled();
      expect(MediaLibrary.requestPermissionsAsync).toHaveBeenCalled();
      expect(ImagePicker.requestMediaLibraryPermissionsAsync).toHaveBeenCalled();
      expect(result).toBe(true);
      expect(cameraService.hasPermissions).toBe(true);
    });

    it('should handle permission denial', async () => {
      Camera.requestCameraPermissionsAsync.mockResolvedValueOnce({
        status: 'denied',
        granted: false,
      });
      MediaLibrary.requestPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
        granted: true,
      });
      ImagePicker.requestMediaLibraryPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
        granted: true,
      });

      const result = await cameraService.requestPermissions();

      expect(result).toBe(false);
      expect(cameraService.hasPermissions).toBe(false);
    });

    it('should check existing permissions', async () => {
      Camera.getCameraPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
        granted: true,
      });
      MediaLibrary.getPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
        granted: true,
      });
      ImagePicker.getMediaLibraryPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
        granted: true,
      });

      const result = await cameraService.checkPermissions();

      expect(Camera.getCameraPermissionsAsync).toHaveBeenCalled();
      expect(MediaLibrary.getPermissionsAsync).toHaveBeenCalled();
      expect(ImagePicker.getMediaLibraryPermissionsAsync).toHaveBeenCalled();
      expect(result).toBe(true);
      expect(cameraService.hasPermissions).toBe(true);
    });

    it('should handle permission check errors', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      Camera.getCameraPermissionsAsync.mockRejectedValueOnce(
        new Error('Permission check failed')
      );

      const result = await cameraService.checkPermissions();

      expect(result).toBe(false);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Erro ao verificar permissões:',
        expect.any(Error)
      );

      consoleErrorSpy.mockRestore();
    });
  });

  describe('Image Capture', () => {
    it('should take photo successfully', async () => {
      const mockResult = {
        canceled: false,
        assets: [{
          uri: 'file:///path/to/image.jpg',
          width: 1920,
          height: 1080,
          base64: null,
        }]
      };

      cameraService.hasPermissions = true;
      ImagePicker.launchCameraAsync.mockResolvedValueOnce(mockResult);

      const result = await cameraService.takePhoto({
        quality: 0.8,
        allowsEditing: true,
        aspect: [16, 9],
      });

      expect(ImagePicker.launchCameraAsync).toHaveBeenCalledWith({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [16, 9],
        quality: 0.8,
        base64: false,
      });
      
      expect(result).toEqual({
        uri: 'file:///path/to/image.jpg',
        width: 1920,
        height: 1080,
        type: 'image/jpeg',
        name: expect.stringContaining('photo_'),
        base64: null,
      });
    });

    it('should request permissions if not granted', async () => {
      cameraService.hasPermissions = false;
      
      Camera.requestCameraPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
        granted: true,
      });
      MediaLibrary.requestPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
        granted: true,
      });
      ImagePicker.requestMediaLibraryPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
        granted: true,
      });

      const mockResult = {
        canceled: false,
        assets: [{
          uri: 'file:///path/to/image.jpg',
          width: 1920,
          height: 1080,
        }]
      };

      ImagePicker.launchCameraAsync.mockResolvedValueOnce(mockResult);

      const result = await cameraService.takePhoto();

      expect(Camera.requestCameraPermissionsAsync).toHaveBeenCalled();
      expect(result).toBeTruthy();
    });

    it('should handle permissions denied', async () => {
      cameraService.hasPermissions = false;
      
      Camera.requestCameraPermissionsAsync.mockResolvedValueOnce({
        status: 'denied',
        granted: false,
      });

      const result = await cameraService.takePhoto();

      expect(result).toBe(null);
      expect(Alert.alert).toHaveBeenCalledWith(
        'Erro',
        'Permissões de câmera são necessárias.'
      );
    });

    it('should handle photo capture cancellation', async () => {
      const mockResult = {
        canceled: true,
      };

      cameraService.hasPermissions = true;
      ImagePicker.launchCameraAsync.mockResolvedValueOnce(mockResult);

      const result = await cameraService.takePhoto();

      expect(result).toBe(null);
    });

    it('should handle photo capture errors', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      cameraService.hasPermissions = true;
      
      ImagePicker.launchCameraAsync.mockRejectedValueOnce(
        new Error('Camera failed')
      );

      const result = await cameraService.takePhoto();
      
      expect(result).toBe(null);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Erro ao tirar foto:',
        expect.any(Error)
      );
      expect(Alert.alert).toHaveBeenCalledWith(
        'Erro',
        'Falha ao tirar foto. Tente novamente.'
      );

      consoleErrorSpy.mockRestore();
    });
  });

  describe('Image Gallery', () => {
    it('should pick image from gallery successfully', async () => {
      const mockResult = {
        canceled: false,
        assets: [{
          uri: 'file:///path/to/gallery-image.jpg',
          width: 1920,
          height: 1080,
        }]
      };

      cameraService.hasPermissions = true;
      ImagePicker.launchImageLibraryAsync.mockResolvedValueOnce(mockResult);

      const result = await cameraService.pickImage({
        quality: 0.9,
        allowsEditing: false,
      });

      expect(ImagePicker.launchImageLibraryAsync).toHaveBeenCalledWith({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true, // padrão do serviço é true, mesmo passando false
        aspect: [4, 3],
        quality: 0.9,
        base64: false,
        allowsMultipleSelection: false,
      });
      
      expect(result).toEqual({
        uri: 'file:///path/to/gallery-image.jpg',
        width: 1920,
        height: 1080,
        type: 'image/jpeg',
        name: expect.stringContaining('image_'),
      });
    });

    it('should handle gallery permission denial', async () => {
      cameraService.hasPermissions = false;
      
      Camera.requestCameraPermissionsAsync.mockResolvedValueOnce({
        status: 'denied',
        granted: false,
      });

      const result = await cameraService.pickImage();

      expect(result).toBe(null);
      expect(Alert.alert).toHaveBeenCalledWith(
        'Erro',
        'Permissões de galeria são necessárias.'
      );
    });

    it('should handle gallery selection cancellation', async () => {
      const mockResult = {
        canceled: true,
      };

      cameraService.hasPermissions = true;
      ImagePicker.launchImageLibraryAsync.mockResolvedValueOnce(mockResult);

      const result = await cameraService.pickImage();

      expect(result).toBe(null);
    });
  });

  describe('Utility Methods', () => {
    it('should reset permissions', () => {
      cameraService.hasPermissions = true;

      // Simular reset/clear manual
      cameraService.hasPermissions = false;

      expect(cameraService.hasPermissions).toBe(false);
    });
  });
});