/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    // Essential for Docker + Windows hot reloading
    webpack: (config, { isServer }) => {
      // Important: this ensures file changes are detected in Docker on Windows
      config.watchOptions = {
        poll: 1000, // Check for changes every second
        aggregateTimeout: 300, // Delay before rebuilding
        ignored: ['node_modules', '.git'],
      };
      return config;
    },
    // Add any other Next.js configuration you need
  };
  
  module.exports = nextConfig;