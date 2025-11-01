// Mock expo-location
jest.mock('expo-location', () => ({
  requestForegroundPermissionsAsync: jest.fn(),
  getForegroundPermissionsAsync: jest.fn(),
  getCurrentPositionAsync: jest.fn(),
  watchPositionAsync: jest.fn(),
  hasServicesEnabledAsync: jest.fn(),
  reverseGeocodeAsync: jest.fn(),
  Accuracy: {
    High: 4,
    Balanced: 3,
    Low: 2,
  },
  LocationAccuracy: {
    High: 4,
    Balanced: 3,
    Low: 2,
  },
}));

// Mock react-native Alert
jest.mock('react-native', () => ({
  Alert: {
    alert: jest.fn(),
  },
}));

import locationService from '../../src/services/locationService';
import * as Location from 'expo-location';
import { Alert } from 'react-native';

describe('Location Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Permissions', () => {
    it('should request location permissions successfully', async () => {
      Location.requestForegroundPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
      });

      const result = await locationService.requestPermissions();

      expect(Location.requestForegroundPermissionsAsync).toHaveBeenCalled();
      expect(result).toBe(true);
      expect(locationService.hasPermissions).toBe(true);
    });

    it('should handle permission denial', async () => {
      Location.requestForegroundPermissionsAsync.mockResolvedValueOnce({
        status: 'denied',
      });

      const result = await locationService.requestPermissions();

      expect(result).toBe(false);
      expect(locationService.hasPermissions).toBe(false);
      expect(Alert.alert).toHaveBeenCalledWith(
        'Permissão de Localização',
        'O aplicativo precisa acessar sua localização para funcionar corretamente.',
        [{ text: 'OK' }]
      );
    });

    it('should check existing permissions', async () => {
      Location.getForegroundPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
      });

      const result = await locationService.checkPermissions();

      expect(Location.getForegroundPermissionsAsync).toHaveBeenCalled();
      expect(result).toBe(true);
    });

    it('should handle permission check errors', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      Location.getForegroundPermissionsAsync.mockRejectedValueOnce(
        new Error('Permission check failed')
      );

      const result = await locationService.checkPermissions();

      expect(result).toBe(false);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Erro ao verificar permissões:',
        expect.any(Error)
      );

      consoleErrorSpy.mockRestore();
    });
  });

  describe('Current Location', () => {
    beforeEach(() => {
      locationService.hasPermissions = true;
      Location.hasServicesEnabledAsync.mockResolvedValue(true);
    });

    it('should get current location successfully', async () => {
      const mockLocationData = {
        coords: {
          latitude: -23.5505,
          longitude: -46.6333,
          accuracy: 5,
          altitude: 760,
          heading: 0,
          speed: 0,
        },
        timestamp: Date.now(),
      };

      const expectedResult = {
        latitude: -23.5505,
        longitude: -46.6333,
        accuracy: 5,
        altitude: 760,
        heading: 0,
        speed: 0,
        timestamp: mockLocationData.timestamp,
      };

      Location.getCurrentPositionAsync.mockResolvedValueOnce(mockLocationData);

      const result = await locationService.getCurrentLocation();

      expect(Location.hasServicesEnabledAsync).toHaveBeenCalled();
      expect(Location.getCurrentPositionAsync).toHaveBeenCalledWith({
        accuracy: Location.Accuracy.High,
        maximumAge: 10000,
        timeout: 15000,
      });
      expect(result).toEqual(expectedResult);
      expect(locationService.currentLocation).toEqual(expectedResult);
    });

    it('should request permissions if not granted', async () => {
      locationService.hasPermissions = false;
      
      Location.requestForegroundPermissionsAsync.mockResolvedValueOnce({
        status: 'granted',
      });
      
      const mockLocationData = {
        coords: {
          latitude: -23.5505,
          longitude: -46.6333,
          accuracy: 5,
          altitude: 760,
          heading: 0,
          speed: 0,
        },
        timestamp: Date.now(),
      };

      const expectedResult = {
        latitude: -23.5505,
        longitude: -46.6333,
        accuracy: 5,
        altitude: 760,
        heading: 0,
        speed: 0,
        timestamp: mockLocationData.timestamp,
      };
      
      Location.getCurrentPositionAsync.mockResolvedValueOnce(mockLocationData);

      const result = await locationService.getCurrentLocation();

      expect(Location.requestForegroundPermissionsAsync).toHaveBeenCalled();
      expect(result).toEqual(expectedResult);
    });

    it('should throw error if permissions denied', async () => {
      locationService.hasPermissions = false;
      
      Location.requestForegroundPermissionsAsync.mockResolvedValueOnce({
        status: 'denied',
      });

      await expect(locationService.getCurrentLocation()).rejects.toThrow(
        'Permissões de localização não concedidas'
      );
    });

    it('should handle GPS disabled', async () => {
      Location.hasServicesEnabledAsync.mockResolvedValueOnce(false);

      await expect(locationService.getCurrentLocation()).rejects.toThrow();
    });

    it('should use custom options', async () => {
      const customOptions = {
        accuracy: Location.Accuracy.Low,
        timeout: 5000,
      };

      const mockLocation = {
        coords: { latitude: -23.5505, longitude: -46.6333 },
      };

      Location.getCurrentPositionAsync.mockResolvedValueOnce(mockLocation);

      await locationService.getCurrentLocation(customOptions);

      expect(Location.getCurrentPositionAsync).toHaveBeenCalledWith({
        accuracy: Location.Accuracy.Low,
        timeout: 5000,
        maximumAge: 10000, // default value
      });
    });
  });

  describe('Distance Calculation', () => {
    it('should calculate distance between two points', () => {
      const lat1 = -23.5505; // São Paulo
      const lon1 = -46.6333;
      const lat2 = -22.9068; // Rio de Janeiro  
      const lon2 = -43.1729;
      
      const distance = locationService.calculateDistance(lat1, lon1, lat2, lon2);
      
      // Distance should be approximately 357 km
      expect(distance).toBeGreaterThan(350);
      expect(distance).toBeLessThan(370);
    });

    it('should return 0 for same coordinates', () => {
      const lat = -23.5505;
      const lon = -46.6333;
      
      const distance = locationService.calculateDistance(lat, lon, lat, lon);
      
      expect(distance).toBe(0);
    });

    it('should handle edge cases', () => {
      // Test with zero coordinates
      const distance1 = locationService.calculateDistance(0, 0, -23.5505, -46.6333);
      expect(distance1).toBeGreaterThan(0);
      
      // Test with extreme coordinates  
      const distance2 = locationService.calculateDistance(90, 180, -90, -180);
      expect(distance2).toBeGreaterThan(0);
    });
  });

  describe('Location Watching', () => {
    it('should start watching location', async () => {
      const mockWatchObject = {
        remove: jest.fn(),
      };
      
      Location.watchPositionAsync.mockResolvedValueOnce(mockWatchObject);

      const callback = jest.fn();
      const result = await locationService.startWatching(callback);

      expect(Location.watchPositionAsync).toHaveBeenCalledWith(
        {
          accuracy: Location.Accuracy.High,
          timeInterval: 5000,
          distanceInterval: 10,
        },
        expect.any(Function)
      );
      expect(result).toBe(mockWatchObject);
      expect(locationService.watchId).toBe(mockWatchObject);
    });

    it('should handle watch start errors', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      Location.watchPositionAsync.mockRejectedValueOnce(
        new Error('Watch failed')
      );

      const callback = jest.fn();
      
      await expect(locationService.startWatching(callback)).rejects.toThrow('Watch failed');
      
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Erro ao iniciar monitoramento:',
        expect.any(Error)
      );

      consoleErrorSpy.mockRestore();
    });

    it('should stop watching location', async () => {
      const mockWatchObject = {
        remove: jest.fn(),
      };
      
      locationService.watchId = mockWatchObject;

      await locationService.stopWatching();

      expect(mockWatchObject.remove).toHaveBeenCalled();
      expect(locationService.watchId).toBe(null);
    });

    it('should handle stop watching when not watching', () => {
      locationService.watchId = null;

      // Should not throw error
      expect(() => locationService.stopWatching()).not.toThrow();
    });
  });

  describe('Utility Methods', () => {
    it('should check if location is within area', () => {
      const centerLat = -23.5505;
      const centerLon = -46.6333;
      const currentLat = -23.5510; // ~100m away
      const currentLon = -46.6340;
      
      const isWithin = locationService.isWithinArea(
        currentLat, currentLon, centerLat, centerLon, 0.2 // 200m
      );
      
      expect(isWithin).toBe(true);
    });

    it('should reject location outside area', () => {
      const centerLat = -23.5505;
      const centerLon = -46.6333;
      const currentLat = -23.5600; // ~2km away
      const currentLon = -46.6500;
      
      const isWithin = locationService.isWithinArea(
        currentLat, currentLon, centerLat, centerLon, 0.5 // 500m
      );
      
      expect(isWithin).toBe(false);
    });

    it('should format coordinates correctly', () => {
      const lat = -23.55055555;
      const lon = -46.63336666;
      
      const formatted = locationService.formatCoordinates(lat, lon, 4);
      
      expect(formatted).toEqual({
        latitude: -23.5506,
        longitude: -46.6334,
        formatted: '-23.5506, -46.6334'
      });
    });

    it('should generate Google Maps URL', () => {
      const lat = -23.5505;
      const lon = -46.6333;
      const label = 'Teste Local';
      
      const url = locationService.getGoogleMapsUrl(lat, lon, label);
      
      expect(url).toContain('https://www.google.com/maps/search/');
      expect(url).toContain('-23.5505,-46.6333');
      expect(url).toContain('Teste%20Local');
    });

    it('should generate Google Maps URL without label', () => {
      const lat = -23.5505;
      const lon = -46.6333;
      
      const url = locationService.getGoogleMapsUrl(lat, lon);
      
      expect(url).toContain('https://www.google.com/maps/search/');
      expect(url).toContain('-23.5505,-46.6333');
    });
  });

  describe('Address Resolution', () => {
    it('should get address from coordinates', async () => {
      const mockAddress = [
        {
          street: 'Avenida Paulista',
          district: 'Bela Vista',
          city: 'São Paulo',
          region: 'SP',
          postalCode: '01310-100',
          country: 'Brasil',
        },
      ];

      Location.reverseGeocodeAsync.mockResolvedValueOnce(mockAddress);

      const result = await locationService.reverseGeocode(-23.5505, -46.6333);

      expect(Location.reverseGeocodeAsync).toHaveBeenCalledWith({
        latitude: -23.5505,
        longitude: -46.6333,
      });
      expect(result.street).toBe('Avenida Paulista');
      expect(result.city).toBe('São Paulo');
    });

    it('should handle reverse geocode errors', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      Location.reverseGeocodeAsync.mockRejectedValueOnce(
        new Error('Geocode failed')
      );

      const result = await locationService.reverseGeocode(-23.5505, -46.6333);

      expect(result).toBe(null);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Erro no geocoding reverso:',
        expect.any(Error)
      );

      consoleErrorSpy.mockRestore();
    });
  });
});