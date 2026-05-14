'use client';

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';

import { getStoredToken } from '@/lib/api';

export function AuthShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const token = getStoredToken();
    if (!token && pathname !== '/login') {
      router.replace('/login');
      return;
    }
    if (token && pathname === '/login') {
      router.replace('/');
      return;
    }
    setChecked(true);
  }, [pathname, router]);

  if (!checked && pathname !== '/login') {
    return <main className="mx-auto max-w-7xl px-6 py-8 text-sm text-gov-slate">Checking sign-in status...</main>;
  }

  return <>{children}</>;
}
