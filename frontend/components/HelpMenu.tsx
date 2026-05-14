'use client';

import Link from 'next/link';
import { useState } from 'react';

const items = [
  { href: '/help', label: 'Quick start & troubleshooting' },
  { href: '/help#live-ingestion', label: 'Live ACLED / UCDP setup' },
  { href: '/help#github-release', label: 'GitHub release checklist' },
];

export function HelpMenu() {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button className="btn-secondary" onClick={() => setOpen((value) => !value)}>
        Help
      </button>
      {open ? (
        <div className="absolute right-0 z-20 mt-2 w-72 rounded-2xl border border-gov-line bg-white p-2 shadow-xl">
          {items.map((item) => (
            <Link key={item.href} href={item.href} className="block rounded-xl px-3 py-2 text-sm text-gov-ink hover:bg-gov-mist" onClick={() => setOpen(false)}>
              {item.label}
            </Link>
          ))}
        </div>
      ) : null}
    </div>
  );
}
