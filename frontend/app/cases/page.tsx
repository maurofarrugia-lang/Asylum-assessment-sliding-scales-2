'use client';

import { useEffect, useState } from 'react';

import { api } from '@/lib/api';
import { Assessment } from '@/lib/types';

export default function CasesPage() {
  const [cases, setCases] = useState<Assessment[]>([]);

  useEffect(() => {
    api.getAssessments().then(setCases).catch(console.error);
  }, []);

  return (
    <div className="panel p-6">
      <p className="kicker">Assessment history</p>
      <h2 className="panel-title">Saved cases</h2>
      <div className="mt-6 space-y-4">
        {cases.map((item) => (
          <article key={item.id} className="rounded-2xl border border-gov-line bg-slate-50 p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="font-semibold text-gov-ink">Case #{item.id}</h3>
                <p className="text-sm text-gov-slate">Officer: {item.officer_name} · {new Date(item.created_at).toLocaleString()}</p>
              </div>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-gov-ink">{item.confidence}</span>
            </div>
            <pre className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-800">{item.generated_narrative}</pre>
          </article>
        ))}
        {!cases.length ? <p className="text-sm text-gov-slate">No saved cases yet.</p> : null}
      </div>
    </div>
  );
}
