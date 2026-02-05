import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

const ASCII_ART = `  ██╗ ██████╗ ███╗   ██╗██╗████████╗██╗ ██████╗ ███╗   ██╗
  ██║██╔════╝ ████╗  ██║██║╚══██╔══╝██║██╔═══██╗████╗  ██║
  ██║██║  ███╗██╔██╗ ██║██║   ██║   ██║██║   ██║██╔██╗ ██║
  ██║██║   ██║██║╚██╗██║██║   ██║   ██║██║   ██║██║╚██╗██║
  ██║╚██████╔╝██║ ╚████║██║   ██║   ██║╚██████╔╝██║ ╚████║
  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                    ██╗     ██╗███╗   ██╗████████╗
                    ██║     ██║████╗  ██║╚══██╔══╝
                    ██║     ██║██╔██╗ ██║   ██║
                    ██║     ██║██║╚██╗██║   ██║
                    ███████╗██║██║ ╚████║   ██║
                    ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝`;

const features = [
  {
    title: '$ perspective',
    description:
      'Schema-aware validation of view.json files against production-tested rules from 12,000+ industrial components.',
  },
  {
    title: '$ naming',
    description:
      'Enforce PascalCase, camelCase, snake_case, or custom regex patterns on component and parameter names.',
  },
  {
    title: '$ scripts',
    description:
      'Lint Jython inline scripts and standalone Python files for syntax errors, deprecated APIs, and best practices.',
  },
  {
    title: '$ suppress',
    description:
      'Three-tier suppression: CLI flags, .ignition-lintignore files, and inline comment directives.',
  },
  {
    title: '$ integrate',
    description:
      'Drop-in GitHub Action, pre-commit hooks, and a FastMCP server for AI agent workflows.',
  },
  {
    title: '$ analyze',
    description:
      'Detailed reports with severity levels, component paths, line numbers, and actionable fix suggestions.',
  },
];

export default function Home(): React.JSX.Element {
  return (
    <Layout
      title="Lint your Ignition projects"
      description="A comprehensive linting toolkit for Ignition SCADA projects"
    >
      {/* ASCII Hero */}
      <section className="hero-ascii">
        <pre>{ASCII_ART}</pre>
        <div className="hero-tagline">
          {'> lint your ignition projects like a pro'}
          <span className="cursor" />
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <div className="features-grid">
          {features.map((feature) => (
            <div key={feature.title} className="feature-card">
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="cta-terminal">
          <div className="terminal-header">
            <span className="terminal-dot red" />
            <span className="terminal-dot yellow" />
            <span className="terminal-dot green" />
          </div>
          <code>
            <span className="comment"># install</span>
            {'\n'}
            <span className="prompt">$</span> pip install ignition-lint
            {'\n\n'}
            <span className="comment"># lint a project</span>
            {'\n'}
            <span className="prompt">$</span> ignition-lint --project ./my-project --profile full
            {'\n\n'}
            <span className="comment"># or use the github action</span>
            {'\n'}
            <span className="prompt">$</span> uses: whiskeyhouse/ignition-lint@v1
          </code>
        </div>
        <div className="cta-buttons">
          <Link className="primary" to="/docs/getting-started/installation">
            Get Started
          </Link>
          <Link
            className="secondary"
            href="https://github.com/WhiskeyHouse/ignition-lint"
          >
            View on GitHub
          </Link>
        </div>
      </section>
    </Layout>
  );
}
