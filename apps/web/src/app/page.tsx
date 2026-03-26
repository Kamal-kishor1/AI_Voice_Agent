const foundationTracks = [
  {
    label: "Backend",
    detail: "FastAPI app, async PostgreSQL session, Celery wiring, health endpoints.",
  },
  {
    label: "Database",
    detail: "Alembic bootstraps PostgreSQL tables, indexes, extensions, and RLS policies.",
  },
  {
    label: "Frontend",
    detail: "Next.js dashboard shell aligned to the project’s dark-mode UI direction.",
  },
];

const principles = [
  "Free mode remains the default path for every later feature.",
  "Database names and shapes follow DATABASE.md rather than ad-hoc code decisions.",
  "External actions will route through the permission system before any send is allowed.",
];

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Alex • Phase 1 Foundation</p>
          <h1>Build the operating system before the intelligence layer.</h1>
          <p className="lede">
            This workspace now contains the first runnable scaffold for Alex:
            monorepo layout, backend foundation, schema migration, and the
            initial dashboard shell.
          </p>
        </div>
        <div className="hero-card">
          <span className="status-dot" />
          <p className="status-label">Current focus</p>
          <strong>Repository, infrastructure, and database baseline</strong>
          <p>
            Start the backend stack with <code>docker compose -f
            infra/docker-compose.yml up --build</code>, then open{" "}
            <code>/health</code>.
          </p>
        </div>
      </section>

      <section className="grid">
        {foundationTracks.map((track) => (
          <article className="panel" key={track.label}>
            <h2>{track.label}</h2>
            <p>{track.detail}</p>
          </article>
        ))}
      </section>

      <section className="panel principles">
        <h2>Locked Principles</h2>
        <ul>
          {principles.map((principle) => (
            <li key={principle}>{principle}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
