---
sidebar_position: 2
title: Rule Codes
---

# Rule Code Reference

Every issue reported by ignition-lint has a rule code. Use these codes with `--ignore-codes`, `.ignition-lintignore`, or inline comment directives to suppress specific rules.

## Perspective / Schema Rules

| Code | Severity | Description |
|---|---|---|
| `SCHEMA_VALIDATION` | ERROR | Component structure doesn't match the expected schema |
| `GENERIC_COMPONENT_NAME` | STYLE | Component has a non-descriptive default name (e.g., `Label`, `Button`) |
| `MISSING_ICON_PATH` | WARNING | Icon component missing the required `path` prop |
| `SINGLE_CHILD_FLEX` | STYLE | Flex container with only one child — consider removing the wrapper |

## Naming Rules

| Code | Severity | Description |
|---|---|---|
| `NAMING_COMPONENT` | STYLE | Component name doesn't match the configured naming style |
| `NAMING_PARAMETER` | STYLE | Parameter name doesn't match the configured naming style |
| `NAMING_CUSTOM` | STYLE | Custom property key doesn't match the configured naming style |

## Script Rules (standalone `.py` files)

| Code | Severity | Description |
|---|---|---|
| `SYNTAX_ERROR` | ERROR | Python syntax error |
| `FILE_READ_ERROR` | ERROR | Could not read file from disk |
| `LONG_LINE` | STYLE | Line exceeds 120 characters |
| `MISSING_DOCSTRING` | STYLE | Public function missing a docstring |
| `GLOBAL_VARIABLE_USAGE` | WARNING | Usage of the `global` keyword |
| `JYTHON_PRINT_STATEMENT` | WARNING | `print x` statement syntax (Python 2 style) |
| `JYTHON_DEPRECATED_ITERITEMS` | WARNING | `.iteritems()` usage (removed in Python 3) |
| `JYTHON_XRANGE_USAGE` | INFO | `xrange()` usage (renamed to `range` in Python 3) |
| `JYTHON_STRING_TYPES` | WARNING | `basestring` or `unicode` usage |
| `IGNITION_SYSTEM_OVERRIDE` | ERROR | Overriding the `system` variable |
| `IGNITION_HARDCODED_GATEWAY` | WARNING | Hardcoded gateway URL |
| `IGNITION_DEBUG_PRINT` | INFO | Debug `print()` statement left in code |
| `IGNITION_UNKNOWN_SYSTEM_CALL` | WARNING | Unrecognised `system.*` function call |
| `JAVA_INTEGRATION_DETECTED` | INFO | Java imports present in script |
| `PARSE_WARNING` | WARNING | File could not be fully parsed |

## Jython Inline Rules (from `view.json` script bindings)

| Code | Severity | Description |
|---|---|---|
| `JYTHON_SYNTAX_ERROR` | ERROR | Syntax error in an inline script |
| `JYTHON_IGNITION_INDENTATION_REQUIRED` | ERROR | Missing required indentation in inline script |
| `JYTHON_PRINT_STATEMENT` | WARNING | Print statement in inline script |
| `JYTHON_PREFER_PERSPECTIVE_PRINT` | INFO | Prefer `system.perspective.print()` over `print()` in Perspective context |

## Usage

### Suppress globally via CLI

```bash
ignition-lint -p ./project --profile full --ignore-codes NAMING_PARAMETER,LONG_LINE
```

### Suppress per-path via `.ignition-lintignore`

```gitignore
views/_REFERENCE/**:NAMING_COMPONENT,GENERIC_COMPONENT_NAME
scripts/legacy/**:MISSING_DOCSTRING
```

### Suppress inline (Python scripts only)

```python
# ignition-lint: disable-file=MISSING_DOCSTRING
# ignition-lint: disable-next=LONG_LINE
x = build_very_long_configuration_string(a, b, c, d)
y = 1  # ignition-lint: disable=JYTHON_PRINT_STATEMENT
```

See the [Suppression Guide](./suppression.md) for the full reference.
