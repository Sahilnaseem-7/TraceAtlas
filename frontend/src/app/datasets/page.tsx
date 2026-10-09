'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, datasetApi } from '@/lib/api';

export default function Datasets() {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [workspaceId, setWorkspaceId] = useState<string>('');
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const router = useRouter();

  useEffect(() => {
    const init = async () => {
      const wsRes = await authApi.getWorkspaces();
      if (wsRes.data.length > 0) {
        setWorkspaceId(wsRes.data[0].id);
        const dsRes = await datasetApi.list(wsRes.data[0].id);
        setDatasets(dsRes.data);
      }
    };
    init();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await datasetApi.create(workspaceId, { name: newName });
    const dsRes = await datasetApi.list(workspaceId);
    setDatasets(dsRes.data);
    setShowCreate(false);
    setNewName('');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Dataset Registry</h1>
        <button onClick={() => setShowCreate(!showCreate)} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Register Dataset
        </button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="bg-white p-4 rounded-lg shadow mb-6 flex gap-4">
          <input 
            type="text" 
            placeholder="Dataset Name" 
            value={newName} 
            onChange={(e) => setNewName(e.target.value)} 
            className="flex-1 p-2 border rounded" 
            required 
          />
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded">Save</button>
        </form>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {datasets.map((ds) => (
              <tr key={ds.id}>
                <td className="px-6 py-4 whitespace-nowrap font-medium">{ds.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-500">{ds.source || '-'}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                    {ds.governance_status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button onClick={() => router.push(`/datasets/${ds.id}`)} className="text-blue-600 hover:underline">
                    View Passport
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}