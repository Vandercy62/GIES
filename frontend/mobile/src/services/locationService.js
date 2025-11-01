import * as Location from 'expo-location';
import { Alert } from 'react-native';

class LocationService {
  constructor() {
    this.hasPermissions = false;
    this.watchId = null;
    this.currentLocation = null;
  }

  // Solicitar permissões de localização
  async requestPermissions() {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      this.hasPermissions = status === 'granted';

      if (!this.hasPermissions) {
        Alert.alert(
          'Permissão de Localização',
          'O aplicativo precisa acessar sua localização para funcionar corretamente.',
          [{ text: 'OK' }]
        );
      }

      return this.hasPermissions;
    } catch (error) {
      console.error('Erro ao solicitar permissões de localização:', error);
      return false;
    }
  }

  // Verificar se já tem permissões
  async checkPermissions() {
    try {
      const { status } = await Location.getForegroundPermissionsAsync();
      this.hasPermissions = status === 'granted';
      return this.hasPermissions;
    } catch (error) {
      console.error('Erro ao verificar permissões:', error);
      return false;
    }
  }

  // Obter localização atual
  async getCurrentLocation(options = {}) {
    try {
      if (!this.hasPermissions) {
        const granted = await this.requestPermissions();
        if (!granted) {
          throw new Error('Permissões de localização não concedidas');
        }
      }

      // Verificar se o GPS está habilitado
      const enabled = await Location.hasServicesEnabledAsync();
      if (!enabled) {
        Alert.alert(
          'GPS Desabilitado',
          'Por favor, habilite o GPS nas configurações do dispositivo.',
          [{ text: 'OK' }]
        );
        throw new Error('GPS desabilitado');
      }

      const location = await Location.getCurrentPositionAsync({
        accuracy: options.accuracy || Location.Accuracy.High,
        maximumAge: options.maximumAge || 10000, // 10 segundos
        timeout: options.timeout || 15000, // 15 segundos
      });

      this.currentLocation = {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        altitude: location.coords.altitude,
        accuracy: location.coords.accuracy,
        heading: location.coords.heading,
        speed: location.coords.speed,
        timestamp: location.timestamp,
      };

      return this.currentLocation;
    } catch (error) {
      console.error('Erro ao obter localização:', error);
      
      if (error.code === 'E_LOCATION_TIMEOUT') {
        Alert.alert('Erro', 'Timeout ao obter localização. Tente novamente.');
      } else if (error.code === 'E_LOCATION_UNAVAILABLE') {
        Alert.alert('Erro', 'Localização indisponível. Verifique o GPS.');
      } else {
        Alert.alert('Erro', 'Falha ao obter localização atual.');
      }
      
      throw error;
    }
  }

  // Iniciar monitoramento de localização
  async startWatching(callback, options = {}) {
    try {
      if (!this.hasPermissions) {
        const granted = await this.requestPermissions();
        if (!granted) {
          throw new Error('Permissões de localização não concedidas');
        }
      }

      if (this.watchId) {
        await this.stopWatching();
      }

      this.watchId = await Location.watchPositionAsync(
        {
          accuracy: options.accuracy || Location.Accuracy.High,
          timeInterval: options.timeInterval || 5000, // 5 segundos
          distanceInterval: options.distanceInterval || 10, // 10 metros
        },
        (location) => {
          this.currentLocation = {
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
            altitude: location.coords.altitude,
            accuracy: location.coords.accuracy,
            heading: location.coords.heading,
            speed: location.coords.speed,
            timestamp: location.timestamp,
          };

          if (callback) {
            callback(this.currentLocation);
          }
        }
      );

      return this.watchId;
    } catch (error) {
      console.error('Erro ao iniciar monitoramento:', error);
      throw error;
    }
  }

  // Parar monitoramento de localização
  async stopWatching() {
    try {
      if (this.watchId) {
        await this.watchId.remove();
        this.watchId = null;
      }
    } catch (error) {
      console.error('Erro ao parar monitoramento:', error);
    }
  }

  // Calcular distância entre dois pontos
  calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Raio da Terra em km
    const dLat = this.toRadians(lat2 - lat1);
    const dLon = this.toRadians(lon2 - lon1);
    
    const a = 
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c; // Distância em km

    return distance;
  }

  // Converter graus para radianos
  toRadians(degrees) {
    return degrees * (Math.PI / 180);
  }

  // Obter endereço a partir de coordenadas (geocoding reverso)
  async reverseGeocode(latitude, longitude) {
    try {
      const addresses = await Location.reverseGeocodeAsync({
        latitude,
        longitude,
      });

      if (addresses && addresses.length > 0) {
        const address = addresses[0];
        return {
          street: address.street,
          name: address.name,
          district: address.district,
          city: address.city,
          region: address.region,
          country: address.country,
          postalCode: address.postalCode,
          formattedAddress: this.formatAddress(address),
        };
      }

      return null;
    } catch (error) {
      console.error('Erro no geocoding reverso:', error);
      return null;
    }
  }

  // Formatar endereço
  formatAddress(address) {
    const parts = [];
    
    if (address.name) parts.push(address.name);
    if (address.street) parts.push(address.street);
    if (address.district) parts.push(address.district);
    if (address.city) parts.push(address.city);
    if (address.region) parts.push(address.region);
    if (address.postalCode) parts.push(address.postalCode);

    return parts.join(', ');
  }

  // Validar se está em uma área específica
  isWithinArea(currentLat, currentLon, centerLat, centerLon, radiusKm) {
    const distance = this.calculateDistance(
      currentLat, currentLon, 
      centerLat, centerLon
    );
    return distance <= radiusKm;
  }

  // Formatar coordenadas para exibição
  formatCoordinates(latitude, longitude, precision = 6) {
    return {
      latitude: parseFloat(latitude.toFixed(precision)),
      longitude: parseFloat(longitude.toFixed(precision)),
      formatted: `${latitude.toFixed(precision)}, ${longitude.toFixed(precision)}`,
    };
  }

  // Obter URL do Google Maps
  getGoogleMapsUrl(latitude, longitude, label = '') {
    const coords = `${latitude},${longitude}`;
    const query = label ? `${coords}(${encodeURIComponent(label)})` : coords;
    return `https://www.google.com/maps/search/?api=1&query=${query}`;
  }

  // Limpar dados de localização
  clear() {
    this.stopWatching();
    this.currentLocation = null;
    this.hasPermissions = false;
  }
}

export const locationService = new LocationService();
export default locationService;