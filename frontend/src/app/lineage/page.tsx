'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  Edge,
  Node,
  useEdgesState,
  useNodesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { authApi, datasetApi, lineageApi } from '@/lib/api';

export default function LineageExplorer() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [workspaceId, setWorkspaceId] = useState('');
  const [datasets, setDatasets] = useState<any[]>([]);
  const [sourceId, setSourceId] = useState('');
  const [targetId, setTargetId] = useState('');
  const [relationship, setRelationship] = useState('derived_from');
  const [impactSourceId, setImpactSourceId] = useState('');
  const [impacts, setImpacts] = useState<any[]>([]);
  const [impactAnalyzed, setImpactAnalyzed] = useState(false);
  const [impactBusy, setImpactBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const loadGraph = useCallback(async (wsId: string) => {
    const response = await lineageApi.getGraph(wsId);
    const nodeMap = new Map<string, Node>();
    const graphEdges: Edge[] = [];

    response.data.forEach((edge: any, index: number) => {
      if (!nodeMap.has(edge.source_id)) {
        nodeMap.set(edge.source_id, {
          id: edge.source_id,
          type: 'default',
          data: { label: `${edge.source_type}\n${edge.source_id.substring(0, 8)}` },
          position: { x: nodeMap.size * 250, y: (index % 2) * 150 },
        });
      }
      if (!nodeMap.has(edge.target_id)) {
        nodeMap.set(edge.target_id, {
          id: edge.target_id,
          type: 'default',
          data: { label: `${edge.target_type}\n${edge.target_id.substring(0, 8)}` },
          position: { x: nodeMap.size * 250, y: ((index + 1) % 2) * 150 },
        });
      }
      graphEdges.push({
        id: edge.id || `edge-${index}`,
        source: edge.source_id,
        target: edge.target_id,
        label: edge.relationship_type,
        animated: false,
      });
    });

    setNodes(Array.from(nodeMap.values()));
    setEdges(graphEdges);
  }, [setEdges, setNodes]);

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      router.replace('/');
      return;
    }

    const init = async () => {
      try {
        const workspaceResponse = await authApi.getWorkspaces();
        if (!workspaceResponse.data.length) {
          setError('No workspace is available for this account.');
          return;
        }
        const wsId = workspaceResponse.data[0].id;
        setWorkspaceId(wsId);
        const datasetResponse = await datasetApi.list(wsId);
        setDatasets(datasetResponse.data);
        await loadGraph(wsId);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Could not load lineage data.');
        if (err.response?.status === 401 || err.response?.status === 403) {
          localStorage.removeItem('token');
          router.replace('/');
        }
      } finally {
        setLoading(false);
      }
    };
    void init();
  }, [loadGraph, router]);

  const analyzeImpact = async (event: FormEvent) => {
    event.preventDefault();
    if (!workspaceId || !impactSourceId) return;
    setImpactBusy(true);
    setError('');
    try {
      const response = await lineageApi.getImpact(workspaceId, 'dataset', impactSourceId);
      setImpacts(response.data.impacts || []);
      setImpactAnalyzed(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Could not analyze downstream impact.');
    } finally {
      setImpactBusy(false);
    }
  };

  const createEdge = async (event: FormEvent) => {
    event.preventDefault();
    if (!workspaceId || !sourceId || !targetId || sourceId === targetId) {
      setError('Choose two different datasets.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      await lineageApi.createEdge(workspaceId, {
        source_type: 'dataset',
        source_id: sourceId,
        target_type: 'dataset',
        target_id: targetId,
        relationship_type: relationship.trim() || 'derived_from',
      });
      await loadGraph(workspaceId);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Could not create this lineage edge.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <main className="mx-auto max-w-7xl p-5 md:p-8">
        <div className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-700">Dependencies</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Lineage explorer</h1>
          <p className="mt-2 text-slate-600">Map dataset relationships and understand what may be affected by a source change.</p>
        </div>

        {error && <div role="alert" className="mb-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        <form onSubmit={createEdge} className="mb-5 grid gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-[1fr_1fr_1fr_auto]">
          <label className="text-sm font-medium text-slate-700">Source dataset
            <select value={sourceId} onChange={(event) => setSourceId(event.target.value)} required className="mt-1 w-full rounded-lg border border-slate-300 p-2.5">
              <option value="">Choose source…</option>
              {datasets.map((dataset) => <option key={dataset.id} value={dataset.id}>{dataset.name}</option>)}
            </select>
          </label>
          <label className="text-sm font-medium text-slate-700">Downstream dataset
            <select value={targetId} onChange={(event) => setTargetId(event.target.value)} required className="mt-1 w-full rounded-lg border border-slate-300 p-2.5">
              <option value="">Choose target…</option>
              {datasets.map((dataset) => <option key={dataset.id} value={dataset.id}>{dataset.name}</option>)}
            </select>
          </label>
          <label className="text-sm font-medium text-slate-700">Relationship
            <input value={relationship} onChange={(event) => setRelationship(event.target.value)} maxLength={100} required className="mt-1 w-full rounded-lg border border-slate-300 p-2.5" placeholder="derived_from" />
          </label>
          <button type="submit" disabled={busy || loading || datasets.length < 2} className="self-end rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-50">{busy ? 'Saving…' : 'Add edge'}</button>
        </form>

        <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
            <div><h2 className="font-semibold text-slate-900">Dependency graph</h2><p className="mt-1 text-xs text-slate-500">{nodes.length} assets · {edges.length} relationships</p></div>
            <button onClick={() => workspaceId && loadGraph(workspaceId)} className="text-sm font-semibold text-blue-700 hover:underline">Refresh</button>
          </div>
          {loading ? <div className="p-10 text-center text-sm text-slate-500">Loading lineage graph…</div> : edges.length === 0 ? (
            <div className="p-10 text-center"><p className="font-medium text-slate-800">No lineage edges yet</p><p className="mt-1 text-sm text-slate-500">Register at least two datasets, then use the form above to connect them.</p></div>
          ) : (
            <div className="h-[560px] w-full">
              <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} fitView>
                <Controls />
                <Background />
              </ReactFlow>
            </div>
          )}
        </section>

        <section className="mt-5 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-slate-900">Downstream impact analysis</h2>
          <p className="mt-1 text-sm text-slate-500">Select a source dataset to find all reachable downstream assets in this workspace.</p>
          <form onSubmit={analyzeImpact} className="mt-4 flex flex-wrap gap-3">
            <select value={impactSourceId} onChange={(event) => { setImpactSourceId(event.target.value); setImpactAnalyzed(false); setImpacts([]); }} required className="min-w-64 flex-1 rounded-lg border border-slate-300 p-2.5 text-sm">
              <option value="">Choose a source dataset…</option>
              {datasets.map((dataset) => <option key={dataset.id} value={dataset.id}>{dataset.name}</option>)}
            </select>
            <button type="submit" disabled={impactBusy || loading || !impactSourceId} className="rounded-lg border border-blue-700 px-4 py-2.5 text-sm font-semibold text-blue-700 hover:bg-blue-50 disabled:opacity-50">{impactBusy ? 'Analyzing…' : 'Analyze impact'}</button>
          </form>
          {impactAnalyzed && impacts.length > 0 ? (
            <ul className="mt-4 divide-y divide-slate-100 rounded-lg border border-slate-100">
              {impacts.map((impact, index) => (
                <li key={`${impact.type}-${impact.id}-${index}`} className="flex flex-wrap justify-between gap-2 px-4 py-3 text-sm">
                  <span className="font-medium text-slate-800">{impact.type}</span>
                  <span className="font-mono text-xs text-slate-500">{impact.id}</span>
                </li>
              ))}
            </ul>
          ) : impactAnalyzed && !impactBusy ? (
            <p className="mt-4 text-sm text-slate-500">No downstream dependencies found for the selected source, or no analysis has been run yet.</p>
          ) : null}
        </section>
      </main>
    </div>
  );
}
