import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import { Alert } from 'react-native';

class FileService {
  constructor() {
    this.uploadQueue = [];
    this.isUploading = false;
  }

  // Selecionar arquivo do dispositivo
  async pickFile(options = {}) {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: options.type || '*/*',
        copyToCacheDirectory: options.copyToCacheDirectory !== false,
        multiple: options.multiple || false,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        if (options.multiple) {
          return result.assets.map(asset => this.normalizeFileInfo(asset));
        } else {
          return this.normalizeFileInfo(result.assets[0]);
        }
      }

      return null;
    } catch (error) {
      console.error('Erro ao selecionar arquivo:', error);
      Alert.alert('Erro', 'Falha ao selecionar arquivo. Tente novamente.');
      return null;
    }
  }

  // Normalizar informações do arquivo
  normalizeFileInfo(asset) {
    const extension = asset.name ? asset.name.split('.').pop().toLowerCase() : '';
    
    return {
      uri: asset.uri,
      name: asset.name || `file_${Date.now()}.${extension}`,
      size: asset.size || 0,
      type: asset.mimeType || this.getMimeType(extension),
      extension,
      lastModified: Date.now(),
    };
  }

  // Obter MIME type baseado na extensão
  getMimeType(extension) {
    const mimeTypes = {
      // Imagens
      jpg: 'image/jpeg',
      jpeg: 'image/jpeg',
      png: 'image/png',
      gif: 'image/gif',
      webp: 'image/webp',
      bmp: 'image/bmp',
      
      // Documentos
      pdf: 'application/pdf',
      doc: 'application/msword',
      docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      xls: 'application/vnd.ms-excel',
      xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      ppt: 'application/vnd.ms-powerpoint',
      pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      
      // Texto
      txt: 'text/plain',
      csv: 'text/csv',
      json: 'application/json',
      xml: 'application/xml',
      
      // Vídeo
      mp4: 'video/mp4',
      avi: 'video/x-msvideo',
      mov: 'video/quicktime',
      wmv: 'video/x-ms-wmv',
      
      // Áudio
      mp3: 'audio/mpeg',
      wav: 'audio/wav',
      ogg: 'audio/ogg',
      
      // Arquivos compactados
      zip: 'application/zip',
      rar: 'application/x-rar-compressed',
      '7z': 'application/x-7z-compressed',
    };

    return mimeTypes[extension] || 'application/octet-stream';
  }

  // Verificar se o arquivo é uma imagem
  isImage(file) {
    return file.type && file.type.startsWith('image/');
  }

  // Verificar se o arquivo é um documento
  isDocument(file) {
    const documentTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ];
    return documentTypes.includes(file.type);
  }

  // Formatar tamanho do arquivo
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Validar arquivo
  validateFile(file, options = {}) {
    const errors = [];

    // Validar tamanho máximo
    if (options.maxSize && file.size > options.maxSize) {
      errors.push(`Arquivo muito grande. Máximo: ${this.formatFileSize(options.maxSize)}`);
    }

    // Validar tipos permitidos
    if (options.allowedTypes && !options.allowedTypes.includes(file.type)) {
      errors.push(`Tipo de arquivo não permitido: ${file.type}`);
    }

    // Validar extensões permitidas
    if (options.allowedExtensions && !options.allowedExtensions.includes(file.extension)) {
      errors.push(`Extensão não permitida: ${file.extension}`);
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  // Ler arquivo como base64
  async readAsBase64(uri) {
    try {
      const base64 = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64,
      });
      return base64;
    } catch (error) {
      console.error('Erro ao ler arquivo como base64:', error);
      throw error;
    }
  }

  // Copiar arquivo para diretório de documentos
  async copyToDocuments(uri, filename) {
    try {
      const documentsDir = FileSystem.documentDirectory;
      const newPath = `${documentsDir}${filename}`;
      
      await FileSystem.copyAsync({
        from: uri,
        to: newPath,
      });

      return newPath;
    } catch (error) {
      console.error('Erro ao copiar arquivo:', error);
      throw error;
    }
  }

  // Deletar arquivo
  async deleteFile(uri) {
    try {
      const fileInfo = await FileSystem.getInfoAsync(uri);
      if (fileInfo.exists) {
        await FileSystem.deleteAsync(uri);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Erro ao deletar arquivo:', error);
      return false;
    }
  }

  // Adicionar arquivo à fila de upload
  addToUploadQueue(file, uploadData = {}) {
    const uploadItem = {
      id: Date.now().toString(),
      file,
      uploadData,
      status: 'pending', // pending, uploading, completed, error
      progress: 0,
      error: null,
      createdAt: new Date(),
    };

    this.uploadQueue.push(uploadItem);
    return uploadItem.id;
  }

  // Processar fila de upload
  async processUploadQueue(uploadFunction) {
    if (this.isUploading) {
      return;
    }

    this.isUploading = true;

    try {
      for (const item of this.uploadQueue) {
        if (item.status === 'pending') {
          item.status = 'uploading';
          
          try {
            const result = await uploadFunction(item.file, item.uploadData, (progress) => {
              item.progress = progress;
            });
            
            item.status = 'completed';
            item.result = result;
          } catch (error) {
            item.status = 'error';
            item.error = error.message;
            console.error(`Erro no upload do arquivo ${item.file.name}:`, error);
          }
        }
      }
    } finally {
      this.isUploading = false;
    }

    // Remover itens concluídos
    this.uploadQueue = this.uploadQueue.filter(
      item => item.status !== 'completed'
    );
  }

  // Obter status da fila de upload
  getUploadQueueStatus() {
    const pending = this.uploadQueue.filter(item => item.status === 'pending').length;
    const uploading = this.uploadQueue.filter(item => item.status === 'uploading').length;
    const errors = this.uploadQueue.filter(item => item.status === 'error').length;

    return {
      total: this.uploadQueue.length,
      pending,
      uploading,
      errors,
      isProcessing: this.isUploading,
    };
  }

  // Limpar fila de upload
  clearUploadQueue() {
    this.uploadQueue = [];
    this.isUploading = false;
  }

  // Obter informações do arquivo
  async getFileInfo(uri) {
    try {
      return await FileSystem.getInfoAsync(uri);
    } catch (error) {
      console.error('Erro ao obter informações do arquivo:', error);
      return null;
    }
  }

  // Criar diretório se não existir
  async ensureDirectoryExists(path) {
    try {
      const dirInfo = await FileSystem.getInfoAsync(path);
      if (!dirInfo.exists) {
        await FileSystem.makeDirectoryAsync(path, { intermediates: true });
      }
      return true;
    } catch (error) {
      console.error('Erro ao criar diretório:', error);
      return false;
    }
  }
}

export const fileService = new FileService();
export default fileService;