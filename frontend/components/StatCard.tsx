interface Props {
  label: string;
  value: string;
  hint?: string;
}

export function StatCard({ label, value, hint }: Props) {
  return (
    <div className="panel p-5">
      <p className="kicker">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-gov-ink">{value}</p>
      {hint ? <p className="mt-2 text-sm text-gov-slate">{hint}</p> : null}
    </div>
  );
}
