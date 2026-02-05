---
sidebar_position: 1
title: CLI Reference
---

# CLI Reference

## Synopsis

```bash
ignition-lint [OPTIONS]
```

## Options

| Option | Short | Description | Default |
|---|---|---|---|
| `--project` | `-p` | Path to Ignition project directory | — |
| `--files` | `-f` | Comma-separated file globs to lint | `**/view.json` |
| `--profile` | | Lint profile (`full`, `naming`, `perspective`, `scripts`) | — |
| `--naming-only` | | Only run naming convention checks | `false` |
| `--component-style` | | Naming style for components | `PascalCase` |
| `--parameter-style` | | Naming style for parameters | `camelCase` |
| `--component-style-rgx` | | Custom regex for component names | — |
| `--parameter-style-rgx` | | Custom regex for parameter names | — |
| `--allow-acronyms` | | Allow acronyms in names | `false` |
| `--component-type` | `-c` | Filter to a specific component type | — |
| `--schema` | | Custom schema file path | robust mode |
| `--verbose` | `-v` | Show detailed output | `false` |
| `--output` | `-o` | Save report to file | stdout |
| `--ignore-codes` | | Comma-separated rule codes to suppress | — |
| `--ignore-file` | | Path to ignore file | `.ignition-lintignore` |

## Naming Styles

| Style | Pattern | Example |
|---|---|---|
| `PascalCase` | Each word capitalized, no separators | `UserStatusLabel` |
| `camelCase` | First word lowercase, rest capitalized | `userStatusLabel` |
| `snake_case` | All lowercase, underscore separators | `user_status_label` |
| `UPPER_SNAKE_CASE` | All uppercase, underscore separators | `USER_STATUS_LABEL` |
| Custom regex | Any pattern via `--component-style-rgx` | — |

## Examples

### Full project lint

```bash
ignition-lint --project /path/to/project --profile full
```

### Naming only with custom styles

```bash
ignition-lint \
  --files "**/view.json" \
  --component-style PascalCase \
  --parameter-style camelCase \
  --allow-acronyms
```

### Filter by component type

```bash
ignition-lint \
  --project /path/to/project \
  --profile full \
  --component-type ia.display.label
```

### Suppress rules during adoption

```bash
ignition-lint -p ./project --profile full \
  --ignore-codes NAMING_PARAMETER,NAMING_COMPONENT,MISSING_DOCSTRING,LONG_LINE
```

### Save report to file

```bash
ignition-lint --project /path/to/project --profile full --output report.txt
```

### Verbose output

```bash
ignition-lint --project /path/to/project --profile full --verbose
```

## Understanding the Report

### Summary Section

```
📊 LINT RESULTS
============================================================
📁 Files processed: 226
🧩 Components analyzed: 2,660
✅ Valid components: 2,533 (95.2%)
❌ Invalid components: 127
📈 Schema compliance: 95.2%
```

### Issue Details

```
📄 path/to/view.json
   ❌ SCHEMA_VALIDATION: fontSize should be string not number
      Component: ia.display.label at root.children[0]
      Suggestion: Path: props.textStyle.fontSize
```

Each issue includes:
- **File path** — exact location of the problematic file
- **Severity + Code** — issue category and rule identifier
- **Message** — description of the problem
- **Component path** — location within the view structure
- **Suggestion** — specific guidance for resolution

### Suppression Summary

When rules are suppressed, the report includes a count:

```
🔇 716 issues suppressed
```
