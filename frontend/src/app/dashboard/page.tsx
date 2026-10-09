'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, datasetApi } from '@/lib/api';

export default function Dashboard() {
  const [workspaces, setWorkspaces] = useState<any[]>([]);
  const [datasets, setDatasets] = useState<any[]>([]);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) router.push('/');
    
    const fetchData = async () => {
      try {
        const wsRes = await authApi.getWorkspaces();
        setWorkspaces(wsRes.data);
        if (wsRes.data.length > 0) {
          const dsRes = await datasetApi.list(wsRes.data[0].id);
          setDatasets(dsRes.data);
        }
      } catch (err) {
        router.push('/');
      }
    };
    fetchData();
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-gray-500 text-sm">Total Datasets</h2>
          <p className="text-3xl font-bold">{datasets.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-gray-500 text-sm">Workspaces</h2>
          <p className="text-3xl font-bold">{workspaces.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-gray-500 text-sm">Governance Alerts</h2>
          <p className="text-3xl font-bold text-yellow-600">0</p>
        </div>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Recent Datasets</h2>
          <button onClick={() => router.push('/datasets')} className="text-blue-600 hover:underline">View All</button>
        </div>
        <ul className="divide-y">
          {datasets.slice(0, 5).map((ds) => (
            <li key={ds.id} className="py-3 flex justify-between">
              <span className="font-medium">{ds.name}</span>
              <span className="text-gray-500 text-sm">{ds.governance_status}</span>
            </li>
          ))}
          {datasets.length === 0 && <li className="py-3 text-gray-500">No datasets yet.</li>}
        </ul>
      </div>
    </div>
  );
}