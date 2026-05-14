import './globals.css';
import type { Metadata } from 'next';

import { NavBar } from '@/components/NavBar';
import { AuthShell } from '@/components/AuthShell';

export const metadata: Metadata = {
  title: 'Asylum Assessment App',
  description: 'Analytical support application for indiscriminate violence assessments.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AuthShell>
          <NavBar />
          <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        </AuthShell>
      </body>
    </html>
  );
}
