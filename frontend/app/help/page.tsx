export default function HelpPage() {
  return (
    <div className="space-y-6">
      <section className="panel p-6">
        <p className="kicker">Help</p>
        <h2 className="panel-title">Quick start and troubleshooting</h2>
        <div className="mt-4 space-y-4 text-sm leading-7 text-gov-slate">
          <p>
            If the page does not load, first confirm that both services are running and that the frontend knows where the backend API is located. The MVP expects the backend at <code>NEXT_PUBLIC_API_BASE_URL</code> and will show clearer connection warnings when the API is unavailable.
          </p>
          <ol className="list-decimal space-y-2 pl-5">
            <li>Copy <code>.env.example</code> to <code>.env</code>.</li>
            <li>Run <code>docker compose up --build</code> from the repository root.</li>
            <li>Open the frontend at <code>http://localhost:3000</code>.</li>
            <li>Open backend docs at <code>http://localhost:8000/docs</code>.</li>
          </ol>
        </div>
      </section>

      <section id="live-ingestion" className="panel p-6">
        <p className="kicker">Live ingestion</p>
        <h2 className="panel-title">ACLED and UCDP wiring</h2>
        <div className="mt-4 space-y-4 text-sm leading-7 text-gov-slate">
          <p>
            ACLED requires OAuth-based API access using a myACLED account. UCDP requires a token sent in the <code>x-ucdp-access-token</code> header. Both integrations are now wired into backend sync endpoints, but they need real credentials in the environment before data can be pulled.
          </p>
          <ul className="list-disc space-y-2 pl-5">
            <li><code>ACLED_USERNAME</code> and <code>ACLED_PASSWORD</code></li>
            <li><code>UCDP_ACCESS_TOKEN</code></li>
            <li>Run sync from the Source Verification page after startup.</li>
          </ul>
        </div>
      </section>

      <section id="github-release" className="panel p-6">
        <p className="kicker">Publishing</p>
        <h2 className="panel-title">GitHub push-ready branch and release checklist</h2>
        <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm leading-7 text-gov-slate">
          <li>Create a clean branch such as <code>feat/live-ingestion-help-menu</code>.</li>
          <li>Verify <code>backend pytest</code>, <code>frontend npm run lint</code>, and <code>frontend npm run build</code>.</li>
          <li>Confirm <code>.env</code> is ignored and only <code>.env.example</code> is committed.</li>
          <li>Review README setup, deployment, and credential sections.</li>
          <li>Push branch, open PR, attach screenshots, and summarize live-ingestion prerequisites.</li>
          <li>Tag a release only after smoke-testing dashboard, source sync, assessment generation, and help navigation.</li>
        </ol>
      </section>
    </div>
  );
}
