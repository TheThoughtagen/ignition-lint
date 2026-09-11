import type {Config} from '@docusaurus/types';
const config: Config = {
  "title": "ignition-lint",
  "tagline": "Static checks for Perspective resources, expressions, naming, and Python scripts.",
  "favicon": "img/favicon.svg",
  "url": "https://thethoughtagen.github.io",
  "baseUrl": "/ignition-lint/",
  "trailingSlash": true,
  "organizationName": "TheThoughtagen",
  "projectName": "ignition-lint",
  "onBrokenLinks": "throw",
  "markdown": {
    "format": "md",
    "hooks": {
      "onBrokenMarkdownLinks": "throw"
    }
  },
  "presets": [
    [
      "classic",
      {
        "docs": {
          "path": "../docs",
          "sidebarPath": "./sidebars.ts",
          "editUrl": "https://github.com/TheThoughtagen/ignition-lint/edit/main/docs/",
          "exclude": [
            "superpowers/**",
            "*_SUMMARY.md",
            "*_REPORT.md",
            "*-STRATEGY.md",
            "*_COMPLETE.md",
            "AI_DEVELOPMENT_RULES.md",
            "BINDING_PATTERNS_ANALYSIS.md",
            "GETTING_STARTED.md",
            "LINTER_USAGE.md",
            "SUPPRESSION.md",
            "PROJECT_OVERVIEW.md",
            "IGNITION-LINTER-INTEGRATION.md"
          ]
        },
        "blog": false,
        "theme": {
          "customCss": "./src/css/custom.css"
        }
      }
    ]
  ],
  "themeConfig": {
    "colorMode": {
      "defaultMode": "dark",
      "respectPrefersColorScheme": true
    },
    "navbar": {
      "title": "ignition-lint",
      "items": [
        {
          "to": "/docs/getting-started/installation",
          "label": "Get started",
          "position": "left"
        },
        {
          "type": "docSidebar",
          "sidebarId": "docsSidebar",
          "label": "Docs",
          "position": "left"
        },
        {
          "label": "Tools",
          "type": "dropdown",
          "items": [
            {
              "label": "Ignition Dev Tools",
              "href": "https://thethoughtagen.github.io/ignition-ide-plugins/"
            },
            {
              "label": "ignition-cli",
              "href": "https://thethoughtagen.github.io/ignition-cli/"
            },
            {
              "label": "ignition-mcp",
              "href": "https://whiskeyhouse.github.io/ignition-mcp/"
            },
            {
              "label": "Ignition Git Module",
              "href": "https://whiskeyhouse.github.io/ignition-git-module/"
            }
          ],
          "position": "left"
        },
        {
          "href": "https://github.com/TheThoughtagen/ignition-lint/releases",
          "label": "Releases",
          "position": "right"
        },
        {
          "href": "https://github.com/TheThoughtagen/ignition-lint",
          "label": "GitHub",
          "position": "right"
        }
      ]
    },
    "footer": {
      "style": "dark",
      "links": [
        {
          "title": "Documentation",
          "items": [
            {
              "label": "Installation",
              "to": "/docs/getting-started/installation"
            },
            {
              "label": "First steps",
              "to": "/docs/getting-started/quickstart"
            },
            {
              "label": "Report an issue",
              "href": "https://github.com/TheThoughtagen/ignition-lint/issues"
            }
          ]
        },
        {
          "title": "Related tools",
          "items": [
            {
              "label": "Ignition Dev Tools",
              "href": "https://thethoughtagen.github.io/ignition-ide-plugins/"
            },
            {
              "label": "ignition-cli",
              "href": "https://thethoughtagen.github.io/ignition-cli/"
            },
            {
              "label": "ignition-mcp",
              "href": "https://whiskeyhouse.github.io/ignition-mcp/"
            },
            {
              "label": "Ignition Git Module",
              "href": "https://whiskeyhouse.github.io/ignition-git-module/"
            }
          ]
        },
        {
          "title": "Patrick Mannion",
          "items": [
            {
              "label": "FIELDNOTES",
              "href": "https://awake-iris-z6ww.here.now/"
            },
            {
              "label": "LinkedIn",
              "href": "https://www.linkedin.com/in/mannionpatrick/"
            },
            {
              "label": "X",
              "href": "https://x.com/__pattym__"
            }
          ]
        }
      ],
      "copyright": "Community tooling for Ignition. See each repository for its license and contributors."
    }
  }
};
export default config;
