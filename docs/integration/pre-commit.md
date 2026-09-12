# Pre-commit

Run the CLI against the project directory using a local pre-commit hook:

```yaml
repos:
  - repo: local
    hooks:
      - id: ignition-lint
        name: Check Ignition project
        entry: ignition-lint --target . --fail-on error
        language: system
        pass_filenames: false
        files: '\.(json|py)$'
```

Install `ignition-lint-toolkit` in the environment used by Git, then run `pre-commit install`. Verify with `pre-commit run ignition-lint --all-files`.

This checks the whole directory when a matching file changes. Change `--target .` to the project directory if your repository contains other applications.

The repository's older remote hook definition passes options that the current CLI does not accept. Use the local configuration above until that hook is updated. Pin the linter package version in your team's development environment for repeatable results.
