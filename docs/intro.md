---
sidebar_position: 1
slug: /
title: Introduction
---

# ignition-lint

A comprehensive linting toolkit for Ignition SCADA projects that combines naming convention validation, empirical schema checks, script analysis, and CI/CD automation.

## What It Does

**ignition-lint** validates your Ignition project files across three dimensions:

- **Perspective Linting** — Schema-aware checks against `view.json` files using production-validated rules from 12,000+ real industrial components
- **Naming Validation** — Enforces component, parameter, and custom property naming styles (PascalCase, camelCase, snake_case, or custom regex)
- **Script Analysis** — Lints Jython inline scripts (from `view.json` bindings) and standalone Python files in `script-python` directories

## Why Use It

Ignition projects grow fast in industrial environments. Without consistent validation, teams end up with:

- Generic component names like `Label` or `Button` that make views hard to navigate
- Mixed naming conventions across parameters and properties
- Jython syntax issues that only surface at runtime
- Deprecated API usage (`print` statements, `.iteritems()`, `xrange()`)
- Hardcoded gateway URLs and overridden `system` variables

**ignition-lint** catches these issues early — in your editor, in pre-commit hooks, or in CI.

## Relationship to ia-eknorr/ignition-lint

This project extends the foundational work by [Eric Knorr](https://github.com/ia-eknorr) in [ia-eknorr/ignition-lint](https://github.com/ia-eknorr/ignition-lint), which pioneered naming convention validation for Ignition view.json files.

| Capability | ia-eknorr/ignition-lint | whiskeyhouse/ignition-lint |
|---|---|---|
| View.json naming validation | Yes | Yes (enhanced) |
| GitHub Actions integration | Yes | Yes (enhanced) |
| CLI tool | No | Yes |
| Project-wide linting | No | Yes |
| Script validation | No | Yes |
| Empirical schema validation | No | Yes |
| MCP/AI integration | No | Yes |
| Lint suppression | No | Yes |

Use **ia-eknorr/ignition-lint** if you only need the original naming checks and a lightweight GitHub Action. Use **whiskeyhouse/ignition-lint** for local CLI tooling, schema validation, script linting, MCP integration, or suppression support.

## Tooling Overview

| Command | Purpose |
|---|---|
| `ignition-lint` | CLI entry point for project and file linting |
| `ignition-lint-server` | FastMCP server for AI agent integrations |
| `ignition-lint-action` | Wrapper used by the GitHub Action |

## Next Steps

- [Installation](./getting-started/installation.md) — Get up and running
- [Basic Usage](./getting-started/basic-usage.md) — Lint your first project
- [CLI Reference](./guides/cli-reference.md) — Full command-line options
