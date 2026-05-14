'use client';

import { useEffect, useMemo, useState } from 'react';

import { api } from '@/lib/api';
import { Country, GeoType, SummaryResponse } from '@/lib/types';

const periods = [1, 3, 6, 12];

const initialApplicant = {
  age: 17,
  gender: 'female',
  disability: '',
  medical_vulnerabilities: 'asthma',
  ethnicity: 'Masalit',
  religion: '',
  family_composition: 'single adult with younger sibling',
  single_status: 'single woman',
  child_status: 'minor sibling present',
  minority_profile: 'ethnic minority',
  political_visibility: '',
  occupation: 'student',
  previous_harm: 'family home burned',
  internal_displacement_history: 'multiple displacements',
  support_network: 'limited',
  area_specific_vulnerabilities: 'camp insecurity',
  travel_route_concerns: 'unsafe checkpoints',
  custom_notes: 'traveling without stable male support',
};

const initialCountryInfo = {
  coi_findings: 'Recent reports describe active hostilities and high humanitarian need.',
  security_dynamics: 'Shelling, checkpoints, and fluid front lines affect civilian movement.',
  recent_developments: 'Recent escalation has reduced predictability and access to services.',
  localised_risk_patterns: 'Urban centers and displacement sites remain exposed.',
  humanitarian_conditions: 'Healthcare and shelter access are constrained.',
  state_protection: 'State protection appears limited in practice.',
  internal_relocation: 'Internal relocation may be unreasonable where displacement and insecurity persist.',
};

export function AssessmentWorkbench() {
  const [countries, setCountries] = useState<Country[]>([]);
  const [loading, setLoading] = useState(true);
  const [geoType, setGeoType] = useState<GeoType>('country');
  const [selectedCountry, setSelectedCountry] = useState<number | null>(null);
  const [selectedRegion, setSelectedRegion] = useState<number | null>(null);
  const [selectedDistrict, setSelectedDistrict] = useState<number | null>(null);
  const [customAreaName, setCustomAreaName] = useState('');
  const [months, setMonths] = useState(6);
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [narrative, setNarrative] = useState('');
  const [officerName, setOfficerName] = useState('Protection Officer');
  const [applicant, setApplicant] = useState<Record<string, string | number>>(initialApplicant);
  const [countryInfo, setCountryInfo] = useState<Record<string, string>>(initialCountryInfo);
  const [status, setStatus] = useState<string>('');

  useEffect(() => {
    api.getGeoTree()
      .then((data) => {
        setCountries(data);
        if (data[0]) {
          setSelectedCountry(data[0].id);
        }
      })
      .catch((error) => setStatus(error instanceof Error ? error.message : 'Unable to load geographies.'))
      .finally(() => setLoading(false));
  }, []);

  const regionOptions = useMemo(() => countries.find((c) => c.id === selectedCountry)?.regions ?? [], [countries, selectedCountry]);
  const districtOptions = useMemo(() => regionOptions.find((r) => r.id === selectedRegion)?.districts ?? [], [regionOptions, selectedRegion]);

  useEffect(() => {
    if (!regionOptions.length) {
      setSelectedRegion(null);
      setSelectedDistrict(null);
      return;
    }
    if (!regionOptions.some((region) => region.id === selectedRegion)) {
      setSelectedRegion(regionOptions[0].id);
      setSelectedDistrict(regionOptions[0].districts[0]?.id ?? null);
    }
  }, [regionOptions, selectedRegion]);

  useEffect(() => {
    if (!districtOptions.length) {
      setSelectedDistrict(null);
      return;
    }
    if (!districtOptions.some((district) => district.id === selectedDistrict)) {
      setSelectedDistrict(districtOptions[0].id);
    }
  }, [districtOptions, selectedDistrict]);

  const effectiveGeoId = geoType === 'country' ? selectedCountry : geoType === 'region' ? selectedRegion : geoType === 'district' ? selectedDistrict : null;

  async function refreshSummary() {
    setStatus('Calculating analytical indicators...');
    try {
      const nextSummary = await api.getSummary(geoType, effectiveGeoId, months, customAreaName || undefined);
      setSummary(nextSummary);
      setStatus('Indicators updated.');
    } catch (error) {
      setStatus(error instanceof Error ? error.message : 'Unable to calculate indicators.');
    }
  }

  async function generateAssessment() {
    setStatus('Generating sliding-scale assessment text...');
    try {
      const result = await api.generateAssessment({
        officer_name: officerName,
        geo_type: geoType,
        geo_id: effectiveGeoId,
        custom_area_name: customAreaName || null,
        period_months: months,
        applicant,
        country_information: countryInfo,
      });
      setNarrative(result.generated_narrative);
      setStatus('Assessment generated and saved.');
      await refreshSummary();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : 'Unable to generate assessment.');
    }
  }

  function exportDoc() {
    const blob = new Blob([`<html><body><pre>${narrative}</pre></body></html>`], { type: 'application/msword' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'assessment.doc';
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="panel p-6">
          <div className="mb-4">
            <p className="kicker">Generator</p>
            <h2 className="panel-title">Sliding Scale Assessment Generator</h2>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2 text-sm md:col-span-2">
              <span>Officer name</span>
              <input className="input" value={officerName} onChange={(e) => setOfficerName(e.target.value)} />
            </label>

            <label className="space-y-2 text-sm">
              <span>Geographic level</span>
              <select className="input" value={geoType} onChange={(e) => setGeoType(e.target.value as GeoType)}>
                <option value="country">Country</option>
                <option value="region" disabled={!regionOptions.length}>Region</option>
                <option value="district" disabled={!districtOptions.length}>District</option>
                <option value="custom">Custom area</option>
              </select>
            </label>

            <label className="space-y-2 text-sm">
              <span>Reference period</span>
              <select className="input" value={months} onChange={(e) => setMonths(Number(e.target.value))}>
                {periods.map((period) => <option key={period} value={period}>{period} month(s)</option>)}
              </select>
            </label>

            <label className="space-y-2 text-sm">
              <span>Country</span>
              <select className="input" value={selectedCountry ?? ''} onChange={(e) => setSelectedCountry(Number(e.target.value))}>
                {countries.map((country) => <option key={country.id} value={country.id}>{country.name}</option>)}
              </select>
            </label>

            <label className="space-y-2 text-sm">
              <span>Region</span>
              <select className="input" value={selectedRegion ?? ''} onChange={(e) => setSelectedRegion(Number(e.target.value))} disabled={!regionOptions.length}>
                {!regionOptions.length ? <option value="">No regions seeded</option> : null}
                {regionOptions.map((region) => <option key={region.id} value={region.id}>{region.name}</option>)}
              </select>
            </label>

            <label className="space-y-2 text-sm md:col-span-2">
              <span>District</span>
              <select className="input" value={selectedDistrict ?? ''} onChange={(e) => setSelectedDistrict(Number(e.target.value))} disabled={!districtOptions.length}>
                {!districtOptions.length ? <option value="">No districts seeded</option> : null}
                {districtOptions.map((district) => <option key={district.id} value={district.id}>{district.name}</option>)}
              </select>
            </label>

            {geoType === 'custom' ? (
              <label className="space-y-2 text-sm md:col-span-2">
                <span>Custom area label</span>
                <input className="input" value={customAreaName} onChange={(e) => setCustomAreaName(e.target.value)} />
              </label>
            ) : null}
          </div>

          <div className="mt-6 rounded-2xl bg-slate-50 p-4 text-sm text-gov-slate">
            Countries without seeded administrative divisions can still be assessed at country level and can receive live ACLED or UCDP ingestion once source credentials are provided.
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {Object.entries(applicant).map(([key, value]) => (
              <label key={key} className="space-y-2 text-sm">
                <span>{key.replaceAll('_', ' ')}</span>
                <input className="input" value={value} onChange={(e) => setApplicant({ ...applicant, [key]: e.target.value })} />
              </label>
            ))}
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {Object.entries(countryInfo).map(([key, value]) => (
              <label key={key} className="space-y-2 text-sm md:col-span-2">
                <span>{key.replaceAll('_', ' ')}</span>
                <textarea className="textarea" value={value} onChange={(e) => setCountryInfo({ ...countryInfo, [key]: e.target.value })} />
              </label>
            ))}
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <button className="btn-secondary" onClick={refreshSummary} disabled={loading}>Refresh indicators</button>
            <button className="btn-primary" onClick={generateAssessment} disabled={loading}>Generate assessment</button>
          </div>
          <p className="mt-3 text-sm text-gov-slate">{status || 'This assessment is an analytical support tool and does not replace legal assessment by the protection officer.'}</p>
        </section>

        <section className="space-y-6">
          <div className="panel p-6">
            <p className="kicker">Analytical output</p>
            <h2 className="panel-title">Current indicators</h2>
            {summary ? (
              <dl className="mt-4 space-y-3 text-sm">
                <div className="flex justify-between"><dt>Area</dt><dd>{summary.area_name}</dd></div>
                <div className="flex justify-between"><dt>Risk label</dt><dd className="font-semibold text-gov-ink">{summary.risk_label}</dd></div>
                <div className="flex justify-between"><dt>Trend</dt><dd>{summary.trend}</dd></div>
                <div className="flex justify-between"><dt>Incidents / 100k</dt><dd>{summary.incidents_per_100k ?? 'n/a'}</dd></div>
                <div className="flex justify-between"><dt>Fatalities / 100k</dt><dd>{summary.fatalities_per_100k ?? 'n/a'}</dd></div>
                <div className="flex justify-between"><dt>Civilian harm / 100k</dt><dd>{summary.civilian_harm_per_100k ?? 'n/a'}</dd></div>
                <div className="flex justify-between"><dt>Confidence</dt><dd>{summary.confidence}</dd></div>
              </dl>
            ) : (
              <p className="mt-4 text-sm text-gov-slate">No indicators loaded yet.</p>
            )}
          </div>

          <div className="panel p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="kicker">Narrative output</p>
                <h2 className="panel-title">Legally framed reasoning draft</h2>
              </div>
              <div className="flex gap-2">
                <button className="btn-secondary" onClick={() => navigator.clipboard.writeText(narrative)} disabled={!narrative}>Copy</button>
                <button className="btn-secondary" onClick={exportDoc} disabled={!narrative}>Word</button>
                <button className="btn-secondary" onClick={() => window.print()} disabled={!narrative}>PDF</button>
              </div>
            </div>
            <pre className="mt-4 whitespace-pre-wrap rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-800">{narrative || 'Generate an assessment to populate this panel.'}</pre>
          </div>
        </section>
      </div>
    </div>
  );
}
