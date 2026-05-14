'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

import { login } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setStatus('Signing in...');
    try {
      await login(email, password);
      setStatus('Signed in. Redirecting...');
      router.push('/');
    } catch (error) {
      setStatus(error instanceof Error ? error.message : 'Sign-in failed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto max-w-lg px-6 py-16">
      <div className="panel p-8">
        <p className="kicker">Officer access</p>
        <h2 className="panel-title">Sign in with your own casework account</h2>
        <p className="mt-4 text-sm leading-7 text-gov-slate">
          The frontend no longer uses a fixed demo password. Each protection officer, senior officer, or administrator must sign in with an individual account issued for the deployment.
        </p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <label className="block space-y-2 text-sm">
            <span>Email</span>
            <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label className="block space-y-2 text-sm">
            <span>Password</span>
            <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          <button className="btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <div className="mt-6 rounded-2xl bg-gov-mist p-4 text-sm text-gov-ink">
          Seeded demo accounts remain available for local MVP testing: admin@example.org / ChangeMe123!, senior.officer@example.org / ChangeMe123!, officer@example.org / ChangeMe123!.
        </div>
        {status ? <p className="mt-4 text-sm text-gov-ink">{status}</p> : null}
      </div>
    </main>
  );
}
