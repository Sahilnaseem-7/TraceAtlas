'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { authApi, datasetApi } from '@/lib/api';

export default function Datasets() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [workspaceId, setWorkspaceId] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newSource, setNewSource] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const loadDatasets = async (wsId: string) => {
    const response = await datasetApi.list(wsId);
    setDatasets(response.data);
  };

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      router.replace('/');
      return;
    }
    const init = async () => {
      try {
        const response = await authApi.getWorkspaces();
        if (response.data.length > 0) {
          setWorkspaceId(response.data[0].id);
          await loadDatasets(response.data[0].id);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Could not load your datasets.');
        if (err.response?.status === 401 || err.response?.status === 403) {
          localStorage.removeItem('token');
          router.replace('/');
        }
      } finally {
        setLoading(false);
      }
    };
    void init();
  }, [router]);

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    if (!workspaceId || !newName.trim()) return;
    setBusy(true);
    setError('');
    try {
      await datasetApi.create(workspaceId, {
        name: newName.trim(),
        description: newDescription.trim() || null,
        source: newSource.trim() || null,
      });
      await loadDatasets(workspaceId);
      setShowCreate(false);
      setNewName('');
      setNewDescription('');
      setNewSource('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Could not register this dataset.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <main className="mx-auto max-w-7xl p-6 md:p-8">
        <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-700">Data assets</p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Dataset registry</h1>
            <p className="mt-2 text-slate-600">A central inventory for dataset sources, owners, versions, and quality profiles.</p>
          </div>
          <button onClick={() => setShowCreate((value) => !value)} className="rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-800">{showCreate ? 'Cancel' : '+ Register dataset'}</button>
        </div>

        {error && <div role="alert" className="mb-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        {showCreate && (
          <form onSubmit={handleCreate} className="mb-6 grid gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm md:grid-cols-2">
            <label className="text-sm font-medium text-slate-700">Dataset name *
              <input value={newName} onChange={(event) => setNewName(event.target.value)} placeholder="e.g. Customer churn training data" maxLength={200} required className="mt-1 w-full rounded-lg border border-slate-300 p-2.5 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
            <label className="text-sm font-medium text-slate-700">Source
              <input value={newSource} onChange={(event) => setNewSource(event.target.value)} placeholder="e.g. Internal CRM, public repository" maxLength={500} className="mt-1 w-full rounded-lg border border-slate-300 p-2.5 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
            <label className="text-sm font-medium text-slate-700 md:col-span-2">Description
              <textarea value={newDescription} onChange={(event) => setNewDescription(event.target.value)} placeholder="What does this dataset contain and how is it intended to be used?" maxLength={5000} rows={3} className="mt-1 w-full rounded-lg border border-slate-300 p-2.5 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
            <div className="md:col-span-2"><button disabled={busy || !newName.trim()} type="submit" className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 disabled:opacity-60">{busy ? 'Registering…' : 'Create dataset'}</button></div>
          </form>
        )}

        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          {loading ? <p className="p-8 text-sm text-slate-500">Loading registry…</p> : datasets.length === 0 ? (
            <div className="p-12 text-center"><div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-xl text-blue-700">＋</div><h2 className="mt-4 font-semibold text-slate-900">No datasets yet</h2><p className="mt-1 text-sm text-slate-500">Register a dataset to create its passport and upload versioned files.</p><button onClick={() => setShowCreate(true)} className="mt-4 text-sm font-semibold text-blue-700 hover:underline">Register your first dataset</button></div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500"><tr><th className="px-6 py-3">Dataset</th><th className="px-6 py-3">Source</th><th className="px-6 py-3">Governance status</th><th className="px-6 py-3">Created</th><th className="px-6 py-3"> </th></tr></thead>
                <tbody className="divide-y divide-slate-100">
                  {datasets.map((dataset) => (
                    <tr key={dataset.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4"><span className="block font-semibold text-slate-900">{dataset.name}</span><span className="mt-1 block max-w-sm truncate text-xs text-slate-500">{dataset.description || 'No description'}</span></td>
                      <td className="px-6 py-4 text-slate-600">{dataset.source || '—'}</td>
                      <td className="px-6 py-4"><span className="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-800">{(dataset.governance_status || 'not_reviewed').replaceAll('_', ' ')}</span></td>
                      <td className="whitespace-nowrap px-6 py-4 text-slate-500">{new Date(dataset.created_at).toLocaleDateString()}</td>
                      <td className="whitespace-nowrap px-6 py-4"><button onClick={() => router.push(`/datasets/${dataset.id}`)} className="font-semibold text-blue-700 hover:underline">Open passport →</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
