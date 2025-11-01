/**
 * Configuração do Metro para Produção
 * Otimizações de bundle, tree shaking e performance
 */

const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Bundle Splitting - Separar dependências grandes
config.resolver.sourceExts = ['js', 'jsx', 'ts', 'tsx', 'json'];

// Lazy Loading Configuration
config.transformer.asyncRequireModulePath = require.resolve(
  'expo/src/transformers/async-require'
);

// Otimizações de Performance
config.transformer.minifierConfig = {
  ecma: 2018,
  keep_fnames: false,
  mangle: {
    keep_fnames: false,
    safari10: true,
  },
  output: {
    ascii_only: true,
    comments: false,
    webkit: true,
  },
  sourceMap: false,
  toplevel: false,
  warnings: false,
};

// Asset Optimization
config.resolver.assetExts = [
  'png',
  'jpg',
  'jpeg', 
  'gif',
  'webp',
  'svg',
  'ttf',
  'otf',
  'woff',
  'woff2',
  'mp4',
  'mov',
  'avi',
  'mp3',
  'wav',
  'pdf',
];

// Cache Configuration
config.cacheVersion = '2.0.0';
config.resetCache = false;

// Tree Shaking para Redux/React Navigation
config.resolver.alias = {
  'react-native-vector-icons': require.resolve('react-native-vector-icons'),
  '@react-navigation': require.resolve('@react-navigation/native'),
  '@reduxjs/toolkit': require.resolve('@reduxjs/toolkit'),
};

// Ignore para reduzir bundle size
config.resolver.blockList = [
  /node_modules\/.*\/package\.json$/,
  /node_modules\/.*\/README\.md$/,
  /node_modules\/.*\/\.git\//,
];

module.exports = config;