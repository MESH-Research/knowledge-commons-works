module.exports = {
  input: [
    '../../js/**/*.{js,jsx}',
    // Ignore node_modules and test files
    '!**/node_modules/**',
    '!**/test/**',
    '!**/tests/**',
    '!**/__tests__/**',
    '!**/__mocks__/**',
  ],
  output: './',
  options: {
    debug: true,
    func: {
      list: ['i18next.t', 'i18n.t', 't'],
      extensions: ['.js', '.jsx'],
    },
    trans: {
      component: 'Trans',
      i18nKey: 'i18nKey',
      defaultsKey: 'defaults',
      extensions: ['.js', '.jsx'],
      fallbackKey: function(ns, value) {
        return value;
      },
    },
    lngs: ['en'],
    ns: ['translation'],
    defaultLng: 'en',
    defaultNs: 'translation',
    defaultValue: function(lng, ns, key) {
      return key;
    },
    resource: {
      loadPath: 'messages/{{lng}}/translations.json',
      savePath: 'messages/{{lng}}/translations.json',
      jsonIndent: 2,
    },
    nsSeparator: false,
    keySeparator: false,
  },
};