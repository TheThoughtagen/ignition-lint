---
sidebar_position: 99
title: Credits
---

# Credits and Acknowledgments

## Primary Inspiration

This project extends and builds upon the foundational work of **[Eric Knorr](https://github.com/ia-eknorr)** in [ia-eknorr/ignition-lint](https://github.com/ia-eknorr/ignition-lint).

Eric's original ignition-lint project pioneered naming convention validation for Ignition view.json files, providing:

- The core concept of JSON-based component name validation
- GitHub Actions integration for Ignition projects
- Support for multiple naming styles (PascalCase, camelCase, snake_case, etc.)
- Custom regex pattern support
- Acronym handling options

## Our Extensions

Building on Eric's foundation, we added:

**Core Features**
- Enhanced JsonLinter class with more robust JSON structure traversal
- StyleChecker improvements with better regex handling and error reporting
- CLI tool integration for local development workflows
- Project-wide linting across entire Ignition projects

**New Capabilities**
- Empirical validation with production-tested rule sets from real industrial systems
- Python/Jython script linting beyond view.json files
- FastMCP server integration for AI agent compatibility
- Three-tier lint suppression (CLI, ignore file, inline comments)

**Developer Experience**
- Standard `pip install` installation
- Comprehensive CLI with extensive options
- Detailed usage documentation and migration guides

## Compatibility Promise

We maintain **100% input compatibility** with ia-eknorr/ignition-lint:

- All GitHub Action inputs work identically
- Same naming style definitions and behaviors
- Identical regex pattern handling
- Same acronym allowance logic
- Compatible error reporting format

## License

Both projects use the MIT License, enabling collaborative extension and improvement of the Ignition development ecosystem.

---

Thank you, Eric, for creating the foundation that made this enhanced version possible. The Ignition development community benefits greatly from your original contributions.
