'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

import { clearStoredToken } from '@/lib/api';
import { HelpMenu } from '@/components/HelpMenu';

const links = [
  { href: '/', label: 'Dashboard' },
  { href: '/assessment', label: 'Sliding Scale Generator' },
  { href: '/cases', label: 'Saved Cases' },
  { href: '/sources', label: 'Source Verification' },
];

export function NavBar() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <header className="border-b border-gov-line bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div>
          <p className="kicker">Protection Casework</p>
          <h1 className="text-xl font-semibold text-gov-ink">Asylum Assessment App</h1>
        </div>
        <div className="flex items-center gap-3">
          <nav className="flex gap-2">
            {links.map((link) => {
              const active = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`rounded-xl px-4 py-2 text-sm font-medium ${active ? 'bg-gov-ink text-white' : 'text-gov-ink hover:bg-gov-mist'}`}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>
          <HelpMenu />
          <button
            className="btn-secondary"
            onClick={() => {
              clearStoredToken();
              router.push('/login');
            }}
          >
            Sign out
          </button>
        </div>
      </div>
    </header>
  );
}
