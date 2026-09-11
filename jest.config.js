module.exports = {
  verbose: false,
  testEnvironment: "jsdom",
  // App/instance tests only. Dependency packages have their own suites.
  // (Still importable as modules via moduleNameMapper / relative paths.)
  roots: ["<rootDir>/assets/", "<rootDir>/site/kcworks/assets/"],
  moduleFileExtensions: ["js", "jsx", "json"],
  moduleNameMapper: {
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
    "\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$":
      "<rootDir>/__mocks__/fileMock.js",
    "^@(translations|js)/invenio_rdm_records/(.*)$":
      "<rootDir>/site/kcworks/dependencies/invenio-rdm-records/invenio_rdm_records/assets/semantic-ui/$1/invenio_rdm_records/$2",
    "^@(translations|js)/invenio_communities/(.*)$":
      "<rootDir>/site/kcworks/dependencies/invenio-communities/invenio_communities/assets/semantic-ui/$1/invenio_communities/$2",
    "^@(translations|js)/invenio_app_rdm/(.*)$":
      "<rootDir>/.venv/lib/python3.12/site-packages/invenio_app_rdm/theme/assets/semantic-ui/$1/invenio_app_rdm/$2",
    "^@(translations|js)/(invenio_search_ui|invenio_theme)/(.*)$":
      "<rootDir>/.venv/lib/python3.12/site-packages/$2/assets/semantic-ui/$1/$2/$3",
    "^@translations/invenio_modular_deposit_form/i18next$":
      "<rootDir>/site/kcworks/dependencies/invenio-modular-deposit-form/invenio_modular_deposit_form/assets/semantic-ui/translations/invenio_modular_deposit_form/i18next.js",
    "^@translations/invenio_stats_dashboard/i18next$":
      "<rootDir>/site/kcworks/dependencies/invenio-stats-dashboard/invenio_stats_dashboard/assets/semantic-ui/translations/invenio_stats_dashboard/i18next.js",
    "^@translations/invenio_vocabularies/i18next$":
      "<rootDir>/site/kcworks/dependencies/invenio-vocabularies/invenio_vocabularies/assets/semantic-ui/translations/invenio_vocabularies/i18next.js",
    "^@translations/kcworks/(.*)$":
      "<rootDir>/site/kcworks/assets/semantic-ui/translations/kcworks/$1",
    "^@translations/(.*)$": "<rootDir>/assets/translations/$1",
    "^@js/invenio_rdm_records$":
      "<rootDir>/site/kcworks/dependencies/invenio-rdm-records/invenio_rdm_records/assets/semantic-ui/js/invenio_rdm_records",
    "^@js/invenio_communities$":
      "<rootDir>/site/kcworks/dependencies/invenio-communities/invenio_communities/assets/semantic-ui/js/invenio_communities",
    "^@translations/invenio_rdm_records/i18next$":
      "<rootDir>/site/kcworks/dependencies/invenio-rdm-records/invenio_rdm_records/assets/semantic-ui/translations/invenio_rdm_records/i18next.js",
    "^@custom-test-utils/(.*)$": "<rootDir>/tests/js/$1",
    "^@js/invenio_modular_deposit_form$":
      "<rootDir>/site/kcworks/dependencies/invenio-modular-deposit-form/invenio_modular_deposit_form/assets/semantic-ui/js/invenio_modular_deposit_form",
    "^@js/invenio_modular_deposit_form/(.*)$":
      "<rootDir>/site/kcworks/dependencies/invenio-modular-deposit-form/invenio_modular_deposit_form/assets/semantic-ui/js/invenio_modular_deposit_form/$1",
    // Webpack alias from deposit-form extras entry point (instance transformations).
    "^@js/invenio_modular_deposit_form_transformations$":
      "<rootDir>/site/kcworks/assets/semantic-ui/js/invenio_modular_deposit_form_extras/transformations.js",
    "^@js/invenio_vocabularies$":
      "<rootDir>/site/kcworks/dependencies/invenio-vocabularies/invenio_vocabularies/assets/semantic-ui/js/invenio_vocabularies",
    "^@js/invenio_vocabularies/(.*)$":
      "<rootDir>/site/kcworks/dependencies/invenio-vocabularies/invenio_vocabularies/assets/semantic-ui/$1/invenio_vocabularies/$2",
    "^@js/kcworks/(.*)$": "<rootDir>/site/kcworks/assets/semantic-ui/js/$1",
    // Prefer root installs over broken/incomplete nested trees under editable deps.
    // Duplicate formik (root vs deposit-form nested) breaks Formik context in Field.
    "^formik$": "<rootDir>/node_modules/formik",
    "^i18next$": "<rootDir>/node_modules/i18next",
    "^i18next-browser-languagedetector$":
      "<rootDir>/node_modules/i18next-browser-languagedetector",
    "^react$": "<rootDir>/node_modules/react",
    "^react-dom$": "<rootDir>/node_modules/react-dom",
  },
  setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
  transform: {
    "^.+\\.(js|jsx)$": "babel-jest",
  },
  transformIgnorePatterns: [
    // pnpm paths are node_modules/.pnpm/<pkg>@ver/node_modules/<pkg>/…
    // A naive "/node_modules/(?!…)" still matches the *inner* node_modules and
    // keeps allowlisted ESM packages untransformed (axios import syntax errors).
    "/node_modules/(?!(?:\\.pnpm/[^/]+/node_modules/)?(axios|semantic-ui-react|react-invenio-forms|@babel|@inveniosoftware)(/|$))",
  ],
  testMatch: ["**/*.test.js?(x)", "**/*.spec.js?(x)"],
  testPathIgnorePatterns: [
    // Dependency packages run via scripts/run-js-suites.sh (own Jest / pnpm).
    "<rootDir>/site/kcworks/dependencies/",
    "/\\.venv/",
  ],
  // Keep haste from indexing dep __mocks__, nested node_modules, and package .venvs
  // (duplicate fileMock / package.json name collisions). Source under dependencies
  // remains importable via moduleNameMapper and explicit paths.
  modulePathIgnorePatterns: [
    "<rootDir>/site/kcworks/dependencies/.*/\\.venv/",
    "<rootDir>/site/kcworks/dependencies/.*/node_modules/",
    "<rootDir>/site/kcworks/dependencies/.*/__mocks__/",
  ],
  watchPathIgnorePatterns: [
    "<rootDir>/site/kcworks/dependencies/.*/\\.venv/",
    "<rootDir>/site/kcworks/dependencies/.*/node_modules/",
  ],
  collectCoverageFrom: [
    "assets/**/*.{js,jsx}",
    "site/**/*.{js,jsx}",
    "!**/node_modules/**",
    "!**/vendor/**",
    "!**/*.test.{js,jsx}",
    "!**/*.spec.{js,jsx}",
    "!site/kcworks/dependencies/**",
  ],
  coverageDirectory: "coverage",
  coverageReporters: ["text", "lcov"],
  resetMocks: true,
  restoreMocks: true,
};

