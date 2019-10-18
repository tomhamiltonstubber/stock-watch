module.exports = {
  root: true,
  parser: 'babel-eslint',
  parserOptions: {
    sourceType: 'module'
  },
  extends: 'standard',
  'rules': {
    // allow paren-less arrow functions
    'arrow-parens': 0,
    // allow async-await
    'generator-star-spacing': 0,
    // allow debugger during development
    'no-debugger': 0,
    'comma-dangle': 0,
    'camelcase': 0,
    'no-alert': 0,
    'no-multi-spaces': 0,
    'import/first': 0,
  }
}
