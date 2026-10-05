// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// Project site: https://probabl-ai.github.io/skills/
export default defineConfig({
  site: 'https://probabl-ai.github.io',
  base: '/skills',
  trailingSlash: 'always',
  vite: {
    plugins: [tailwindcss()],
  },
});
