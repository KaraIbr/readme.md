import { defineConfig } from 'vitest/config'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import path from 'node:path'

export default defineConfig({
  test: {
    pool: 'threads',
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: false,
    include: ['src/**/*.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      include: [
        'src/features/**/*.{ts,tsx}',
        'src/shared/**/*.{ts,tsx}',
        'src/lib/**/*.{ts,tsx}',
        'src/services/**/*.{ts,tsx}',
      ],
      exclude: [
        'src/**/__tests__/**',
        'src/**/*.test.{ts,tsx}',
        'src/test/**',
        'src/features/system/**',
      ],
      thresholds: {
        statements: 15,
        branches: 6,
        functions: 35,
        lines: 20,
      },
    },
  },
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset()] }),
  ],
  server: {
    proxy: {
      '/api/v1/identity': {
        target: 'http://localhost:8100',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/v1\/identity/, '/api/v1'),
      },
      '/api/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@app': path.resolve(__dirname, 'src/app'),
      '@ds': path.resolve(__dirname, 'src/design-system'),
      '@tokens': path.resolve(__dirname, 'src/design-system/tokens'),
      '@atoms': path.resolve(__dirname, 'src/design-system/atoms'),
      '@molecules': path.resolve(__dirname, 'src/design-system/molecules'),
      '@organisms': path.resolve(__dirname, 'src/design-system/organisms'),
      '@templates': path.resolve(__dirname, 'src/design-system/templates'),
      '@features': path.resolve(__dirname, 'src/features'),
      '@shared': path.resolve(__dirname, 'src/shared'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@lib': path.resolve(__dirname, 'src/lib'),
      '@store': path.resolve(__dirname, 'src/store'),
      '@src': path.resolve(__dirname, 'src'),
      '@assets': path.resolve(__dirname, 'src/assets'),
      '@public': path.resolve(__dirname, 'public'),
    },
  },
})
