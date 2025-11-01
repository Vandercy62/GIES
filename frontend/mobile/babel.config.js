module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      // React Native Reanimated plugin only in production/app mode
      ...(process.env.NODE_ENV !== 'test' ? [
        ['react-native-reanimated/plugin', {
          relativeSourceLocation: true,
        }]
      ] : [])
    ],
  };
};