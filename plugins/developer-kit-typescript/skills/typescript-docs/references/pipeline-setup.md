# Documentation Pipeline Setup

## TypeDoc Configuration

```json
{
  "entryPoints": ["src/index.ts"],
  "out": "docs/api",
  "theme": "markdown",
  "readme": "README.md",
  "excludePrivate": true,
  "excludeProtected": false,
  "excludeExternals": true,
  "includeVersion": true,
  "sort": ["source-order"],
  "kindSortOrder": [
    "Document",
    "Project",
    "Module",
    "Namespace",
    "Enum",
    "Class",
    "Interface",
    "TypeAlias",
    "Constructor",
    "Property",
    "Method"
  ],
  "categorizeByGroup": true,
  "categoryOrder": [
    "Authentication",
    "Authorization",
    "*",
    "Other"
  ],
  "navigation": {
    "includeCategories": true,
    "includeGroups": true
  }
}
```

## NPM Scripts

```json
{
  "scripts": {
    "docs:generate": "typedoc",
    "docs:serve": "cd docs && python -m http.server 8080",
    "docs:validate": "node scripts/validate-docs.js",
    "docs:deploy": "npm run docs:generate && ./scripts/deploy-docs.sh"
  }
}
```

## GitHub Actions Workflow

```yaml
name: Documentation

on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - 'docs/**'
      - '.github/workflows/docs.yml'

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Generate TypeDoc
        run: npm run docs:generate

      - name: Validate documentation
        run: npm run docs:validate

      - name: Check for documentation changes
        id: changes
        run: |
          if git diff --quiet HEAD~1 docs/; then
            echo "changed=false" >> $GITHUB_OUTPUT
          else
            echo "changed=true" >> $GITHUB_OUTPUT
          fi

      - name: Commit documentation
        if: steps.changes.outputs.changed == 'true'
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/
          git commit -m "docs: update generated documentation [skip ci]"
          git push

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

## Installation

```bash
npm install --save-dev typedoc typedoc-plugin-markdown
npm install --save-dev @compodoc/compodoc  # For Angular
```
