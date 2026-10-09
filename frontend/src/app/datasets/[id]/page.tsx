'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { datasetApi } from '@/lib/api';

export default function DatasetPassport() {
  const { id } = useParams();
  const [dataset, setDataset] = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]); // Simplified: In real app, fetch versions via dataset detail
  const [file, setFile] = useState<File | null>(null);
  const [tag, setTag] = useState('');

  useEffect(() => {
    if (id) {
      datasetApi.get(id as string).then(res => setDataset(res.data));
    }
  }, [id]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !tag) return;
    await datasetApi.uploadVersion(id as string, tag, file);
    alert('Version uploaded and profiled!');
    setFile(null);
    setTag('');
  };

  if (!dataset) return <div className="p-8">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-2">{dataset.name}</h1>
      <p className="text-gray-600 mb-8">{dataset.description || 'No description'}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Identity & Source</h2>
          <dl className="space-y-2">
            <div><dt className="text-sm text-gray-500">Owner</dt><dd>{dataset.owner || 'Unassigned'}</dd></div>
            <div><dt className="text-sm text-gray-500">Source</dt><dd>{dataset.source || 'Unknown'}</dd></div>
            <div><dt className="text-sm text-gray-500">Format</dt><dd>{dataset.format || 'Unknown'}</dd></div>
            <div><dt className="text-sm text-gray-500">Governance</dt><dd className="font-bold text-yellow-600">{dataset.governance_status}</dd></div>
          </dl>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Upload New Version</h2>
          <form onSubmit={handleUpload} className="space-y-4">
            <input 
              type="text" 
              placeholder="Version Tag (e.g., v1.0)" 
              value={tag} 
              onChange={(e) => setTag(e.target.value)} 
              className="w-full p-2 border rounded" 
              required 
            />
            <input 
              type="file" 
              accept=".csv,.parquet,.pq" 
              onChange={(e) => setFile(e.target.files?.[0] || null)} 
              className="w-full p-2 border rounded" 
              required 
            />
            <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">
              Upload & Profile
            </button>
          </form>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Lineage & Impact</h2>
        <p className="text-gray-500">Use the Lineage Explorer to map dependencies and analyze impact.</p>
        <button className="mt-4 text-blue-600 hover:underline">Open Lineage Explorer →</button>
      </div>
    </div>
  );
}