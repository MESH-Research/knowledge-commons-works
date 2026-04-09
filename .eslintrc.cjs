/**
 * Lints KCWorks-owned UI code only (not site/kcworks/dependencies or .venv).
 */
module.exports = {
  root: true,
  env: {
    browser: true,
    es2020: true,
    jest: true,
    node: true,
  },
  parser: "@babel/eslint-parser",
  parserOptions: {
    requireConfigFile: false,
    babelOptions: {
      presets: ["@babel/preset-react"],
    },
    ecmaVersion: 2020,
    sourceType: "module",
    ecmaFeatures: { jsx: true },
  },
  plugins: ["react", "jsx-a11y", "react-hooks"],
  extends: ["eslint:recommended", "plugin:react/recommended"],
  settings: {
    react: { version: "detect" },
  },
  rules: {
    "react/react-in-jsx-scope": "off",
    "react/prop-types": "off",
    "react/no-unescaped-entities": "off",
    "react/no-unknown-property": ["error", { ignore: ["as"] }],
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "off",
    "no-unused-vars": "off",
    "no-case-declarations": "off",
    "no-empty": ["error", { allowEmptyCatch: true }],
    "no-extra-boolean-cast": "off",
    "no-extra-semi": "off",
    "no-inner-declarations": "off",
    "no-prototype-builtins": "off",
    "no-useless-escape": "off",
    "react/jsx-key": "off",
    "react/jsx-no-undef": "off",
  },
};
