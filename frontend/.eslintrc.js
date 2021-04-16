module.exports = {
  env: {
    browser: true,
    es2020: true,
  },
  extends: ['plugin:react/recommended', 'airbnb'],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 11,
    sourceType: 'module',
  },
  plugins: ['react'],
  rules: {
    'react/jsx-filename-extension': 'off',
    'react/prop-types': 'off',
    'comma-dangle': ['error', 'always-multiline'],
    'react/jsx-wrap-multilines': 'off',
    'react/jsx-one-expression-per-line': 'off',
    'react/no-unescaped-entities': 'off',
    'operator-linebreak': 'off',
    'object-curly-newline': 'off',
  },
};
