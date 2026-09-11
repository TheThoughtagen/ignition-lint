# Editor integration

[Ignition Dev Tools](https://thethoughtagen.github.io/ignition-ide-plugins/) provides editor support for VS Code, Neovim, and Zed. Its language server integrates ignition-lint for diagnostics. Use Python 3.10+ for the linter dependency.

Follow the [editor installation guide](https://thethoughtagen.github.io/ignition-ide-plugins/docs/getting-started/installation/) and open your Ignition project folder. See the editor's output / language server logs if diagnostics are missing.

## JSON schema validation in VS Code

Find the installed schema path:

```sh
python -c "from ignition_lint.schemas import schema_path_for; print(schema_path_for('robust'))"
```

Add a JSON schema association in workspace settings, replacing the example URL with the path printed above:

```json
{
  "json.schemas": [{
    "fileMatch": ["**/perspective/views/**/view.json"],
    "url": "/absolute/path/to/core-ia-components-schema-robust.json"
  }]
}
```

Schema validation and the full linter cover different checks. Run `ignition-lint --target ./my-project` for the configured CLI checks, including scripts and naming.

See [CLI reference](../guides/cli-reference.md), [rule codes](../guides/rule-codes.md), and [suppression](../guides/suppression.md).
