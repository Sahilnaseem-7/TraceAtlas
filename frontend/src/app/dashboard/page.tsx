'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { authApi, datasetApi } from '@/lib/api';

export default function Dashboard() {
  const [workspaces, setWorkspaces] = useState<any[]>([]);
  const [datasets, setDatasets] = useState<any[]>([]);
  const [versionCount, setVersionCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      router.replace('/');
      return;
    }

    const fetchData = async () => {
      try {
        const workspaceResponse = await authApi.getWorkspaces();
        setWorkspaces(workspaceResponse.data);
        if (workspaceResponse.data.length > 0) {
          const datasetResponse = await datasetApi.list(workspaceResponse.data[0].id);
          setDatasets(datasetResponse.data);
          const versionResponses = await Promise.all(datasetResponse.data.map((dataset: any) => datasetApi.versions(dataset.id)));
          setVersionCount(versionResponses.reduce((sum: number, response: any) => sum + response.data.length, 0));
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Could not load dashboard data.');
        if (err.response?.status === 401 || err.response?.status === 403) {
          localStorage.removeItem('token');
          router.replace('/');
        }
      } finally {
        setLoading(false);
      }
    };
    void fetchData();
  }, [router]);

  const cards = [
    { label: 'Registered datasets', value: datasets.length, note: 'Datasets in your first workspace' },
    { label: 'Workspaces', value: workspaces.length, note: 'Workspaces you can access' },
    { label: 'Dataset versions', value: versionCount, note: 'Uploaded and profiled file versions' },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <main className="mx-auto max-w-7xl p-6 md:p-8">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-700">Workspace overview</p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Your data, with a traceable history.</h1>
            <p className="mt-2 text-slate-600">Manage dataset passports, inspect quality profiles, and map dependencies.</p>
          </div>
          <button onClick={() => router.push('/datasets')} className="rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-800">Open dataset registry →</button>
        </div>

        {error && <div role="alert" className="mb-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        <section className="grid gap-4 md:grid-cols-3">
          {cards.map((card) => (
            <div key={card.label} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-sm font-medium text-slate-500">{card.label}</p>
              <p className="mt-3 text-4xl font-bold tracking-tight text-slate-950">{loading ? '—' : card.value}</p>
              <p className="mt-2 text-xs text-slate-500">{card.note}</p>
            </div>
          ))}
        </section>

        <section className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
            <div><h2 className="font-semibold text-slate-900">Recently registered datasets</h2><p className="mt-1 text-sm text-slate-500">Open a passport to inspect versions and profiling results.</p></div>
            <button onClick={() => router.push('/datasets')} className="text-sm font-semibold text-blue-700 hover:underline">View all</button>
          </div>
          {loading ? <p className="p-6 text-sm text-slate-500">Loading datasets…</p> : datasets.length === 0 ? (
            <div className="p-10 text-center"><p className="font-medium text-slate-800">No datasets registered yet</p><p className="mt-1 text-sm text-slate-500">Create your first dataset to start tracking provenance.</p><button onClick={() => router.push('/datasets')} className="mt-4 rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800">Register dataset</button></div>
          ) : (
            <div className="divide-y divide-slate-100">
              {datasets.slice(0, 6).map((dataset) => (
                <button key={dataset.id} onClick={() => router.push(`/datasets/${dataset.id}`)} className="flex w-full flex-wrap items-center justify-between gap-3 px-6 py-4 text-left hover:bg-slate-50">
                  <span><span className="block font-semibold text-slate-900">{dataset.name}</span><span className="mt-1 block text-xs text-slate-500">{dataset.source || 'Source not specified'}</span></span>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{(dataset.governance_status || 'not_reviewed').replaceAll('_', ' ')}</span>
                </button>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
