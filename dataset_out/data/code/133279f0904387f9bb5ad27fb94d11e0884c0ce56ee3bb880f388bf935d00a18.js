import js from '@eslint/js';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';
import reactPlugin from 'eslint-plugin-react';
import reactHooksPlugin from 'eslint-plugin-react-hooks';
import prettierPlugin from 'eslint-plugin-prettier';

export default [
    js.configs.recommended,
    {
        files: ['**/*.{ts,tsx}'],
        languageOptions: {
            parser: tsparser,
            parserOptions: {
                ecmaFeatures: {
                    jsx: true,
                },
                ecmaVersion: 2020,
                sourceType: 'module',
            },
        },
        plugins: {
            '@typescript-eslint': tseslint,
            react: reactPlugin,
            'react-hooks': reactHooksPlugin,
            prettier: prettierPlugin,
        },
        rules: {
            ...tseslint.configs.recommended.rules,
            ...reactPlugin.configs.recommended.rules,
            ...reactHooksPlugin.configs.recommended.rules,
            'prettier/prettier': 'error',
            'react/react-in-jsx-scope': 'off',
            'react/prop-types': 'off',
            '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
        },
        settings: {
            react: {
                version: 'detect',
            },
        },
    },
    // Browser environment for React/frontend files
    {
        files: [
            '*.{ts,tsx}',
            'pages/**/*.{ts,tsx}',
            'components/**/*.{ts,tsx}',
            'services/**/*.{ts,tsx}',
        ],
        languageOptions: {
            globals: {
                window: 'readonly',
                document: 'readonly',
                console: 'readonly',
                fetch: 'readonly',
                Response: 'readonly',
                navigator: 'readonly',
                WebSocket: 'readonly',
                FileReader: 'readonly',
                Image: 'readonly',
                AudioContext: 'readonly',
                AudioWorkletNode: 'readonly',
                atob: 'readonly',
                HTMLElement: 'readonly',
                HTMLLabelElement: 'readonly',
                Suspense: 'readonly',
            },
        },
        rules: {
            '@typescript-eslint/no-unused-vars': [
                'error',
                {
                    argsIgnorePattern: '^_',
                    varsIgnorePattern:
                        '^(filteredTools|setFilteredTools|searchQuery|setSearchQuery)$', // Allow these specific variables that may be used in future features
                },
            ],
        },
    },
    // Node.js environment for server and scripts
    {
        files: [
            'server.ts',
            'scripts/**/*.{ts,js,cjs}',
            'src/**/*.{ts,tsx}',
            'vite.config.ts',
            'src/test/**/*.{ts,tsx}',
        ],
        languageOptions: {
            globals: {
                process: 'readonly',
                console: 'readonly',
                Buffer: 'readonly',
                __dirname: 'readonly',
                require: 'readonly',
                module: 'readonly',
                exports: 'readonly',
                global: 'readonly',
                suite: 'readonly',
                test: 'readonly',
            },
        },
        rules: {
            '@typescript-eslint/no-explicit-any': 'off', // Allow any types in VS Code extension files
        },
    },
    {
        ignores: ['node_modules/', 'dist/', 'dev-ui/', 'site/', '.venv/', 'examples/'],
    },
];
