import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/basic-usage',
      ],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/cli-reference',
        'guides/rule-codes',
        'guides/suppression',
        'guides/mcp-server',
      ],
    },
    {
      type: 'category',
      label: 'Integration',
      items: [
        'integration/github-actions',
        'integration/pre-commit',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      collapsed: true,
      items: [
        'GETTING_STARTED',
        'LINTER_USAGE',
        'SUPPRESSION',
        'PROJECT_OVERVIEW',
        'IGNITION-LINTER-INTEGRATION',
        'LINTER-INTEGRATION-STRATEGY',
        'VALIDATION-LINTING-STRATEGY',
        'AI_DEVELOPMENT_RULES',
        'BINDING_INTEGRATION_SUMMARY',
        'BINDING_PATTERNS_ANALYSIS',
        'ENHANCED_VALIDATION_COMPLETE',
        'JYTHON_VALIDATION_SUMMARY',
        'JYTHON_VALIDATION_TEST_REPORT',
        'MULTI_CODEBASE_SUMMARY',
        'SCHEMA_IMPROVEMENT_SUMMARY',
      ],
    },
    'credits',
  ],
};

export default sidebars;
