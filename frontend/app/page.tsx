'use client';

import { useEffect, useState } from 'react';

import { MapPanel } from '@/components/MapPanel';
import { StatCard } from '@/components/StatCard';
import { api } from '@/lib/api';
import { Assessment, Country } from '@/lib/types';

export default function DashboardPage() {
  const [countries, setCountries] = useState<Country[]>([]);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [errorText, setErrorText] = useState('');

  useEffect(() => {
    api.health()
      .then(() => setApiStatus('online'))
      .catch(() => {
        setApiStatus('offline');
        setErrorText('The frontend could not reach the backend API. Check NEXT_PUBLIC_API_BASE_URL and confirm the backend is running on port 8000.');
      });

    api.getGeoTree()
      .then(setCountries)
      .catch((error) => setErrorText(error instanceof Error ? error.message : 'Unable to load geography tree.'));
    api.getAssessments().then(setAssessments).catch(() => undefined);
  }, []);

  const districtCount = countries.flatMap((country) => country.regions.flatMap((region) => region.districts)).length;

  return (
    <div className="space-y-8">
      {apiStatus !== 'online' ? (
        <section className="rounded-2xl border border-amber-300 bg-amber-50 p-5 text-sm text-amber-900">
          <p className="font-semibold">Startup guidance</p>
          <p className="mt-2">{apiStatus === 'checking' ? 'Checking backend connectivity...' : errorText}</p>
        </section>
      ) : null}

      <section className="grid gap-4 md:grid-cols-4">
        <StatCard label="Countries" value={String(countries.length)} hint="Seeded examples for MVP" />
        <StatCard label="Regions" value={String(countries.flatMap((country) => country.regions).length)} hint="Hierarchical assessment support" />
        <StatCard label="Districts" value={String(districtCount)} hint="District heatmap enabled" />
        <StatCard label="Saved assessments" value={String(assessments.length)} hint="Full audit trail retained" />
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="panel p-6">
          <p className="kicker">Mission</p>
          <h2 className="panel-title">Operational dashboard</h2>
          <p className="mt-4 text-sm leading-7 text-gov-slate">
            Use this workspace to retrieve violence indicators, verify source lineage, run live ACLED or UCDP sync jobs, and generate sliding-scale reasoning text suitable for asylum and subsidiary protection casework.
          </p>
          <div className="mt-6 rounded-2xl bg-gov-mist p-4 text-sm text-gov-ink">
            This assessment is an analytical support tool and does not replace the legal assessment by the protection officer.
          </div>
          <div className="mt-6 overflow-hidden rounded-2xl border border-gov-line">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-gov-slate">
                <tr>
                  <th className="px-4 py-3">Recent assessments</th>
                  <th className="px-4 py-3">Level</th>
                  <th className="px-4 py-3">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {assessments.slice(0, 5).map((item) => (
                  <tr key={item.id} className="border-t border-gov-line">
                    <td className="px-4 py-3">Case #{item.id}</td>
                    <td className="px-4 py-3">{item.geo_type}</td>
                    <td className="px-4 py-3">{item.confidence}</td>
                  </tr>
                ))}
                {!assessments.length ? (
                  <tr>
                    <td className="px-4 py-6 text-gov-slate" colSpan={3}>No assessments generated yet.</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </div>
        <MapPanel />
      </section>
    </div>
  );
}
