/**
 * Configuração de Produção para Primotex Mobile
 * Otimizações para build final Android/iOS
 */

// Configurações do Metro para produção
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Otimizações de Bundle
config.resolver.platforms = ['ios', 'android', 'native', 'web'];

// Tree Shaking e Dead Code Elimination
config.transformer.minifierConfig = {
  keep_fnames: false,
  mangle: {
    keep_fnames: false,
  },
  output: {
    comments: false,
  },
};

// Lazy Loading de Assets
config.resolver.assetExts = [
  ...config.resolver.assetExts,
  'ttf',
  'otf',
  'jpg',
  'jpeg',
  'png',
  'gif',
  'webp',
  'svg',
  'pdf',
];

// Code Splitting para módulos grandes
config.transformer.experimentalImportSupport = true;

// Otimização de imagens
config.transformer.enableBabelRCLookup = false;
config.transformer.enableBabelRuntime = false;

// Cache otimizado
config.transformer.cacheVersion = '1.0.0';

module.exports = config;