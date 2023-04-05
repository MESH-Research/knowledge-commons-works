# Invenio ESLint config

This is the ESLint config used by the Invenio team.

## Installation

```shell
npm install --save-dev eslint-config-invenio
# if you use prettier
npm install --save-dev prettier eslint-plugin-prettier
# if you use babel
npm install --save-dev eslint-plugin-babel babel-eslint
```

## Presets

### invenio
The base config. You always want this when using this package.
Requires `eslint-plugin-import`

### invenio/prettier
Enables prettier integration.
Requires `prettier`, `eslint-config-prettier` and `eslint-plugin-prettier`
Make sure to load this after all other `invenio/*` presets.

For convenience, we also include a prettier config, that can be loaded by putting `"eslint-config-invenio/prettier-config"` in your `.prettierrc`.

## Example `.eslintrc.yml`

```yaml
extends:
  - '@inveniosoftware/invenio'
  - '@inveniosoftware/invenio/prettier'

parser: '@babel/eslint-parser'
```

## Example `.prettierrc`

```
"@inveniosoftware/eslint-config-invenio/prettier-config"
```
