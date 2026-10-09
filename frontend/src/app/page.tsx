'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';

export default function Home() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      if (isLogin) {
        const response = await authApi.login(email.trim(), password);
        localStorage.setItem('token', response.data.access_token);
      } else {
        await authApi.register({ email: email.trim(), password, full_name: fullName.trim() });
        const response = await authApi.login(email.trim(), password);
        localStorage.setItem('token', response.data.access_token);
      }
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to connect. Confirm that the TraceAtlas API is running and try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="flex min-h-screen bg-white">
      <section className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-slate-950 p-12 text-white lg:flex">
        <div className="absolute -right-24 -top-24 h-96 w-96 rounded-full bg-blue-600/20 blur-3xl" />
        <div className="absolute -bottom-24 -left-20 h-80 w-80 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="relative flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500 font-bold">T</div>
          <span className="text-xl font-semibold tracking-tight">TraceAtlas</span>
        </div>
        <div className="relative max-w-xl">
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.25em] text-blue-300">Data provenance, made visible</p>
          <h1 className="text-5xl font-bold leading-tight tracking-tight">Know where your data came from.</h1>
          <p className="mt-6 max-w-lg text-lg leading-8 text-slate-300">Keep dataset versions, quality profiles, and downstream dependencies in one traceable workspace.</p>
          <div className="mt-10 grid grid-cols-2 gap-3">
            {['Dataset passports', 'Quality profiling', 'Lineage mapping', 'Impact analysis'].map((feature) => (
              <div key={feature} className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">{feature}</div>
            ))}
          </div>
        </div>
        <p className="relative text-xs text-slate-500">Early-stage MVP · Built for data and ML workflows</p>
      </section>

      <section className="flex w-full items-center justify-center px-6 py-12 lg:w-1/2">
        <div className="w-full max-w-md">
          <div className="mb-8 flex items-center gap-3 lg:hidden">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-700 font-bold text-white">T</div>
            <span className="text-xl font-semibold tracking-tight text-slate-950">TraceAtlas</span>
          </div>
          <p className="text-sm font-semibold text-blue-700">{isLogin ? 'WELCOME BACK' : 'GET STARTED'}</p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">{isLogin ? 'Sign in to TraceAtlas' : 'Create your workspace'}</h2>
          <p className="mt-2 text-sm leading-6 text-slate-500">{isLogin ? 'Continue tracking the datasets and dependencies that matter.' : 'Your account will include a default organization and workspace.'}</p>

          {error && <div role="alert" className="mt-6 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

          <form onSubmit={handleSubmit} className="mt-7 space-y-5">
            {!isLogin && (
              <label className="block text-sm font-medium text-slate-700">Full name
                <input type="text" autoComplete="name" value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Your name" maxLength={120} required className="mt-1.5 w-full rounded-lg border border-slate-300 px-3.5 py-3 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100" />
              </label>
            )}
            <label className="block text-sm font-medium text-slate-700">Email address
              <input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@company.com" required className="mt-1.5 w-full rounded-lg border border-slate-300 px-3.5 py-3 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100" />
            </label>
            <label className="block text-sm font-medium text-slate-700">Password
              <input type="password" autoComplete={isLogin ? 'current-password' : 'new-password'} value={password} onChange={(event) => setPassword(event.target.value)} placeholder={isLogin ? 'Enter your password' : 'At least 8 characters'} minLength={isLogin ? undefined : 8} maxLength={128} required className="mt-1.5 w-full rounded-lg border border-slate-300 px-3.5 py-3 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100" />
            </label>
            <button type="submit" disabled={busy} className="w-full rounded-lg bg-blue-700 px-4 py-3 font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60">
              {busy ? 'Please wait…' : isLogin ? 'Sign in' : 'Create account'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-600">
            {isLogin ? 'New to TraceAtlas?' : 'Already have an account?'}
            <button type="button" onClick={() => { setIsLogin((value) => !value); setError(''); }} className="ml-1 font-semibold text-blue-700 hover:underline">
              {isLogin ? 'Create an account' : 'Sign in'}
            </button>
          </p>
          <p className="mt-10 text-center text-xs leading-5 text-slate-400">Do not upload sensitive or regulated datasets to this MVP. Production-grade security and governance controls are still under development.</p>
        </div>
      </section>
    </main>
  );
}
