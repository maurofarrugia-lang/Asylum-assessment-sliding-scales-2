'use client';

import { useEffect, useState } from 'react';

import { api } from '@/lib/api';

interface SourceVerificationResponse {
  configured_integrations: { name: string; purpose: string; configured: boolean; url: string; authentication: string }[];
  sources: { id: number; name: string; dataset_name: string; url: string; publication_date: string | null; accessed_at: string; reporting_period_start: string | null; reporting_period_end: string | null; reliability_note: string | null }[];
}

export default function SourcesPage() {
  const [data, setData] = useState<SourceVerificationResponse | null>(null);
  const [status, setStatus] = useState('');
  const [provider, setProvider] = useState<'acled' | 'ucdp'>('acled');
  const [geoType, setGeoType] = useState<'country' | 'region' | 'district'>('country');
  const [geoId, setGeoId] = useState('1');
  const [startDate, setStartDate] = useState('2026-01-01');
  const [endDate, setEndDate] = useState('2026-05-14');
  const [acledUsername, setAcledUsername] = useState('');
  const [acledPassword, setAcledPassword] = useState('');
  const [ucdpAccessToken, setUcdpAccessToken] = useState('');
  const [ucdpCountryCodeOverride, setUcdpCountryCodeOverride] = useState('');

  const load = () => {
    api.getSources().then((result) => setData(result as SourceVerificationResponse)).catch((error) => {
      setStatus(error instanceof Error ? error.message : 'Unable to load source data.');
    });
  };

  useEffect(() => {
    load();
  }, []);

  async function runSync() {
    setStatus(`Running ${provider.toUpperCase()} sync...`);
    try {
      const result = await api.runSourceSync({
        provider,
        geo_type: geoType,
        geo_id: Number(geoId),
        start_date: startDate,
        end_date: endDate,
        credentials: {
          acled_username: acledUsername || undefined,
          acled_password: acledPassword || undefined,
          ucdp_access_token: ucdpAccessToken || undefined,
          ucdp_country_code_override: ucdpCountryCodeOverride ? Number(ucdpCountryCodeOverride) : undefined,
        },
      });
      setStatus(`Sync completed: ${(result as { inserted: number }).inserted} incidents inserted.`);
      load();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : 'Sync failed.');
    }
  }

  return (
    <div className="space-y-6">
      <section className="panel p-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="kicker">Live source sync</p>
            <h2 className="panel-title">Officer-provided ACLED / UCDP credentials</h2>
          </div>
          <button className="btn-primary" onClick={runSync}>Run sync</button>
        </div>
        <div className="mt-4 grid gap-4 md:grid-cols-5">
          <select className="input" value={provider} onChange={(e) => setProvider(e.target.value as 'acled' | 'ucdp')}>
            <option value="acled">ACLED</option>
            <option value="ucdp">UCDP</option>
          </select>
          <select className="input" value={geoType} onChange={(e) => setGeoType(e.target.value as 'country' | 'region' | 'district')}>
            <option value="country">Country</option>
            <option value="region">Region</option>
            <option value="district">District</option>
          </select>
          <input className="input" value={geoId} onChange={(e) => setGeoId(e.target.value)} placeholder="Geo ID" />
          <input className="input" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          <input className="input" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </div>

        {provider === 'acled' ? (
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <input className="input" value={acledUsername} onChange={(e) => setAcledUsername(e.target.value)} placeholder="ACLED username" />
            <input className="input" type="password" value={acledPassword} onChange={(e) => setAcledPassword(e.target.value)} placeholder="ACLED password" />
          </div>
        ) : (
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <input className="input" value={ucdpAccessToken} onChange={(e) => setUcdpAccessToken(e.target.value)} placeholder="UCDP access token" />
            <input className="input" value={ucdpCountryCodeOverride} onChange={(e) => setUcdpCountryCodeOverride(e.target.value)} placeholder="Optional UCDP country code override" />
          </div>
        )}

        <p className="mt-3 text-sm text-gov-slate">
          Credentials entered here are used for the current sync request, allowing each officer to use their own ACLED or UCDP access without changing deployment-wide environment secrets.
        </p>
        {status ? <p className="mt-2 text-sm text-gov-ink">{status}</p> : null}
      </section>

      <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <section className="panel p-6">
          <p className="kicker">Integrations</p>
          <h2 className="panel-title">Configured source adapters</h2>
          <div className="mt-5 space-y-3">
            {data?.configured_integrations.map((item) => (
              <div key={item.name} className="rounded-2xl border border-gov-line p-4 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <span className="font-semibold text-gov-ink">{item.name}</span>
                  <span className={`rounded-full px-3 py-1 text-xs ${item.configured ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>
                    {item.configured ? 'configured' : 'optional env credential missing'}
                  </span>
                </div>
                <p className="mt-2 text-gov-slate">{item.purpose}</p>
                <p className="mt-1 text-xs text-gov-slate">{item.authentication}</p>
                <a className="mt-2 block text-gov-accent underline" href={item.url} target="_blank" rel="noreferrer">{item.url}</a>
              </div>
            ))}
          </div>
        </section>

        <section className="panel p-6">
          <p className="kicker">Verification</p>
          <h2 className="panel-title">Source reference register</h2>
          <div className="mt-5 overflow-hidden rounded-2xl border border-gov-line">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-left text-gov-slate">
                <tr>
                  <th className="px-4 py-3">Source</th>
                  <th className="px-4 py-3">Dataset</th>
                  <th className="px-4 py-3">Period</th>
                  <th className="px-4 py-3">Accessed</th>
                </tr>
              </thead>
              <tbody>
                {data?.sources.map((source) => (
                  <tr key={source.id} className="border-t border-gov-line align-top">
                    <td className="px-4 py-3"><a className="text-gov-accent underline" href={source.url} target="_blank" rel="noreferrer">{source.name}</a></td>
                    <td className="px-4 py-3">{source.dataset_name}</td>
                    <td className="px-4 py-3">{source.reporting_period_start} → {source.reporting_period_end}</td>
                    <td className="px-4 py-3">{source.accessed_at}</td>
                  </tr>
                ))}
                {!data?.sources.length ? (
                  <tr><td className="px-4 py-6 text-gov-slate" colSpan={4}>No dynamic source references have been saved yet.</td></tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
