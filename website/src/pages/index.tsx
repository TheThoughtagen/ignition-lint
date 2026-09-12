import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
const cards = [{"title": "Run a first check", "description": "Point the CLI at a project directory and choose which severity should fail the run.", "path": "getting-started/quickstart"}, {"title": "Understand a finding", "description": "Look up rule codes and decide what to fix or suppress.", "path": "guides/rule-codes"}, {"title": "Add a project check", "description": "Run the linter during pull requests with GitHub Actions.", "path": "integration/github-actions"}];
export default function Home(): React.JSX.Element {
 return <Layout title="ignition-lint" description="Static checks for Perspective resources, expressions, naming, and Python scripts.">
  <main><section className="launch-hero"><p className="launch-label">IGNITION / DEVELOPER TOOLS</p><h1>Check Ignition projects before running them.</h1><p className="lead">Static checks for Perspective resources, expressions, naming, and Python scripts.</p>
  <div className="launch-actions"><Link className="button button--primary button--lg" to="/docs/getting-started/installation">Get started</Link><Link className="button button--outline button--primary button--lg" to="/docs/getting-started/quickstart">Try a first workflow</Link></div></section>
  <section className="launch-grid" aria-label="Documentation paths">{cards.map(card => <article key={card.path}><h2>{card.title}</h2><p>{card.description}</p><Link to={'/docs/' + card.path}>Read the guide →</Link></article>)}</section>
  <aside className="launch-maintainer"><p>I’m Patrick Mannion. I work on Ignition development tools and write about the work on FIELDNOTES.</p><p><a href="https://awake-iris-z6ww.here.now/about/">About me</a> · <a href="https://www.linkedin.com/in/mannionpatrick/">LinkedIn</a> · <a href="https://x.com/__pattym__">X</a> · <a href="https://github.com/TheThoughtagen/ignition-lint/graphs/contributors">Project contributors</a></p></aside></main>
 </Layout>;
}
