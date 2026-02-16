# Ignition Lint GitHub Action

Automatically lint your Ignition SCADA projects in GitHub Actions workflows. Catch errors, enforce naming conventions, and maintain code quality before merging PRs.

## Quick Start

Add to `.github/workflows/ignition-lint.yml`:

```yaml
name: Ignition Lint
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: TheThoughtagen/ignition-lint@v1
        with:
          project_path: .
          lint_type: all
          fail_on: error
```

## Inputs

### Required (choose one)
- **`files`**: Comma-separated glob patterns for specific files (e.g., `"**/view.json"`)
- **`project_path`**: Path to Ignition project directory with standard layout

### Linting Options
- **`lint_type`**: Type of linting (`perspective`, `scripts`, `all`) - default: `perspective`
- **`naming_only`**: Only run naming checks, skip empirical validation - default: `true`

### Naming Convention
- **`component_style`**: Component naming style (`PascalCase`, `camelCase`, `snake_case`) - default: `PascalCase`
- **`parameter_style`**: Parameter naming style - default: `camelCase`
- **`allow_acronyms`**: Allow acronyms in names - default: `false`

### Failure Control
- **`fail_on`**: Minimum severity that fails the workflow (`error`, `warning`, `info`, `style`) - default: `error`

See full input documentation in [action.yml](action.yml)

## License

MIT © 2025 Patrick Mannion
