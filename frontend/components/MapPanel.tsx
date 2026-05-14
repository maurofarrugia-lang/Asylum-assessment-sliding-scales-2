'use client';

interface DistrictRisk {
  name: string;
  risk: 'low' | 'moderate' | 'high';
}

const defaults: DistrictRisk[] = [
  { name: 'El Fasher', risk: 'high' },
  { name: 'Kutum', risk: 'moderate' },
  { name: 'Khartoum', risk: 'high' },
  { name: 'Omdurman', risk: 'moderate' },
  { name: 'Aleppo', risk: 'moderate' },
  { name: 'Kabul', risk: 'low' },
];

const colorMap = {
  low: '#90c3a8',
  moderate: '#f3c86a',
  high: '#d97989',
};

export function MapPanel() {
  return (
    <div className="panel p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="kicker">Interactive map</p>
          <h2 className="panel-title">District heatmap preview</h2>
        </div>
        <div className="text-xs text-gov-slate">Prototype choropleth layer</div>
      </div>
      <svg viewBox="0 0 600 260" className="w-full rounded-2xl bg-slate-50 p-4">
        {defaults.map((district, index) => {
          const x = 20 + (index % 3) * 185;
          const y = 20 + Math.floor(index / 3) * 105;
          return (
            <g key={district.name}>
              <rect x={x} y={y} width="160" height="80" rx="18" fill={colorMap[district.risk]} opacity="0.9" />
              <text x={x + 16} y={y + 34} fontSize="16" fontWeight="600" fill="#16324F">{district.name}</text>
              <text x={x + 16} y={y + 56} fontSize="12" fill="#16324F">{district.risk.toUpperCase()}</text>
            </g>
          );
        })}
      </svg>
      <div className="mt-4 flex gap-4 text-xs text-gov-slate">
        <span className="flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-[#90c3a8]" /> Low</span>
        <span className="flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-[#f3c86a]" /> Moderate</span>
        <span className="flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-[#d97989]" /> High</span>
      </div>
    </div>
  );
}
