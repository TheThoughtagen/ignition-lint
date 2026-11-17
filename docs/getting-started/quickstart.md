# Run your first check

Install with Python 3.10+:

```sh
python -m pip install ignition-lint-toolkit
ignition-lint --help
ignition-lint --check-linter
```

`--check-linter` checks that the schema assets are available. The CLI does not have a `--version` flag; inspect the package version with `python -m pip show ignition-lint-toolkit`.

## Check a directory

```sh
ignition-lint --target ./my-project --fail-on error
```

Replace `./my-project` with your project directory. Target mode recursively finds `view.json` and `.py` files. For a standard Ignition project layout, use `--project` instead.

Each finding includes a rule code and severity. Read the [rule reference](../guides/rule-codes.md) before deciding whether to fix or suppress it. A clean run means the enabled static checks found no findings at the selected failure threshold. It does not establish that a project is ready for deployment.

## Select checks and output

```sh
ignition-lint --target ./my-project --checks perspective,scripts
ignition-lint --target ./my-project --report-format json > lint-report.json
ignition-lint --target ./my-project --ignore-codes NAMING_PARAMETER
```

Use [suppression rules](../guides/suppression.md) to scope exceptions. See the [CLI reference](../guides/cli-reference.md) for profiles, option precedence, and failure thresholds.

## Add the check to your workflow

Follow the [GitHub Actions guide](../integration/github-actions.md), [pre-commit guide](../integration/pre-commit.md), or [editor integration guide](../integration/editor-integration.md).
