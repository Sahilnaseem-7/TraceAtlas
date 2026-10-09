'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import { datasetApi } from '@/lib/api';

export default function DatasetPassport() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [dataset, setDataset] = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [tag, setTag] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const [datasetResponse, versionsResponse] = await Promise.all([
        datasetApi.get(id),
        datasetApi.versions(id),
      ]);
      setDataset(datasetResponse.data);
      setVersions(versionsResponse.data);
      setError('');
    } catch (err: any) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        localStorage.removeItem('token');
        router.push('/');
      } else {
        setError(err.response?.data?.detail || 'Could not load this dataset.');
      }
    } finally {
      setLoading(false);
    }
  }, [id, router]);

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      router.push('/');
      return;
    }
    if (id) void load();
  }, [id, load, router]);

  const handleUpload = async (event: FormEvent) => {
    event.preventDefault();
    if (!file || !tag.trim()) return;
    setBusy(true);
    setError('');
    try {
      await datasetApi.uploadVersion(id, tag.trim(), file);
      setFile(null);
      setTag('');
      const input = document.getElementById('dataset-file') as HTMLInputElement | null;
      if (input) input.value = '';
      await load();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Check the file and try again.');
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <div className="p-8 text-slate-500">Loading dataset passport…</div>;
  if (!dataset) return <div className="min-h-screen bg-slate-50"><Navbar /><main className="mx-auto max-w-5xl p-8"><p className="text-red-600">{error || 'Dataset not found.'}</p><Link className="text-blue-700 underline" href="/datasets">Back to datasets</Link></main></div>;

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <main className="mx-auto max-w-7xl space-y-6 p-6 md:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <Link href="/datasets" className="text-sm text-blue-700 hover:underline">← Dataset registry</Link>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">{dataset.name}</h1>
            <p className="mt-2 max-w-3xl text-slate-600">{dataset.description || 'No description has been provided.'}</p>
          </div>
          <span className="rounded-full bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-800">
            {(dataset.governance_status || 'not_reviewed').replaceAll('_', ' ')}
          </span>
        </div>

        {error && <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        <section className="grid gap-5 md:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">Dataset identity</h2>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-4 text-sm">
              <div><dt className="text-slate-500">Owner</dt><dd className="mt-1 font-medium">{dataset.owner || 'Unassigned'}</dd></div>
              <div><dt className="text-slate-500">Source</dt><dd className="mt-1 font-medium">{dataset.source || 'Unknown'}</dd></div>
              <div><dt className="text-slate-500">Format</dt><dd className="mt-1 font-medium">{dataset.format || 'Set by upload'}</dd></div>
              <div><dt className="text-slate-500">Versions</dt><dd className="mt-1 font-medium">{versions.length}</dd></div>
              <div className="col-span-2"><dt className="text-slate-500">Dataset ID</dt><dd className="mt-1 break-all font-mono text-xs">{dataset.id}</dd></div>
              <div className="col-span-2"><dt className="text-slate-500">Tags</dt><dd className="mt-1">{dataset.tags?.length ? dataset.tags.join(', ') : 'No tags'}</dd></div>
            </dl>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-1 text-lg font-semibold">Upload a dataset version</h2>
            <p className="mb-4 text-sm text-slate-500">CSV and Parquet files up to 50 MB. Each version tag must be unique for this dataset.</p>
            <form onSubmit={handleUpload} className="space-y-4">
              <label className="block text-sm font-medium text-slate-700">Version tag
                <input value={tag} onChange={(event) => setTag(event.target.value)} placeholder="e.g. v1.0" maxLength={100} required className="mt-1 w-full rounded-lg border border-slate-300 p-2.5 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
              </label>
              <label className="block text-sm font-medium text-slate-700">Dataset file
                <input id="dataset-file" type="file" accept=".csv,.parquet,.pq" onChange={(event) => setFile(event.target.files?.[0] || null)} required className="mt-1 block w-full rounded-lg border border-slate-300 p-2 text-sm" />
              </label>
              {file && <p className="text-xs text-slate-500">{file.name} · {(file.size / 1024 / 1024).toFixed(2)} MB</p>}
              <button disabled={busy || !file} type="submit" className="w-full rounded-lg bg-blue-700 px-4 py-2.5 font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60">
                {busy ? 'Uploading and profiling…' : 'Upload & profile'}
              </button>
            </form>
          </div>
        </section>

        <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-6 py-4">
            <h2 className="text-lg font-semibold">Version history</h2>
            <p className="text-sm text-slate-500">File hashes and data-quality metrics captured at upload time.</p>
          </div>
          {versions.length === 0 ? (
            <div className="p-8 text-center text-sm text-slate-500">No versions yet. Upload a CSV or Parquet file to create the first passport snapshot.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr><th className="px-5 py-3">Version</th><th className="px-5 py-3">Rows</th><th className="px-5 py-3">Columns</th><th className="px-5 py-3">Duplicates</th><th className="px-5 py-3">Created</th><th className="px-5 py-3">SHA-256</th></tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {versions.map((version) => (
                    <tr key={version.id}>
                      <td className="px-5 py-3 font-semibold">{version.version_tag}</td>
                      <td className="px-5 py-3">{version.record_count?.toLocaleString() ?? '—'}</td>
                      <td className="px-5 py-3">{version.column_count ?? '—'}</td>
                      <td className="px-5 py-3">{version.profile_results?.duplicate_rows ?? '—'}</td>
                      <td className="px-5 py-3 whitespace-nowrap">{new Date(version.created_at).toLocaleString()}</td>
                      <td className="max-w-xs truncate px-5 py-3 font-mono text-xs" title={version.content_hash || ''}>{version.content_hash || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <div className="rounded-xl border border-blue-100 bg-blue-50 p-5">
          <h2 className="font-semibold text-blue-950">Lineage & impact</h2>
          <p className="mt-1 text-sm text-blue-900">Explore registered dependencies and trace downstream assets affected by a source change.</p>
          <Link href="/lineage" className="mt-3 inline-flex font-semibold text-blue-700 hover:underline">Open Lineage Explorer →</Link>
        </div>
      </main>
    </div>
  );
}
