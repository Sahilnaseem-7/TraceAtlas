'use client';
import { useEffect, useState, useCallback } from 'react';
import ReactFlow, { 
  Controls, 
  Background, 
  useNodesState, 
  useEdgesState,
  Node,
  Edge
} from 'reactflow';
import 'reactflow/dist/style.css';
import { authApi, lineageApi } from '@/lib/api';

export default function LineageExplorer() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [workspaceId, setWorkspaceId] = useState<string>('');

  useEffect(() => {
    const init = async () => {
      const wsRes = await authApi.getWorkspaces();
      if (wsRes.data.length > 0) {
        const wsId = wsRes.data[0].id;
        setWorkspaceId(wsId);
        
        const graphRes = await lineageApi.getGraph(wsId);
        const rawEdges = graphRes.data;

        // Convert backend edges to ReactFlow nodes and edges
        const nodeMap = new Map<string, Node>();
        const rfEdges: Edge[] = [];

        rawEdges.forEach((e: any, idx: number) => {
          if (!nodeMap.has(e.source_id)) {
            nodeMap.set(e.source_id, {
              id: e.source_id,
              type: 'default',
              data: { label: `${e.source_type}\n${e.source_id.substring(0, 8)}` },
              position: { x: Math.random() * 500, y: Math.random() * 500 },
            });
          }
          if (!nodeMap.has(e.target_id)) {
            nodeMap.set(e.target_id, {
              id: e.target_id,
              type: 'default',
              data: { label: `${e.target_type}\n${e.target_id.substring(0, 8)}` },
              position: { x: Math.random() * 500, y: Math.random() * 500 },
            });
          }
          rfEdges.push({
            id: `e-${idx}`,
            source: e.source_id,
            target: e.target_id,
            label: e.relationship_type,
            animated: true,
          });
        });

        setNodes(Array.from(nodeMap.values()));
        setEdges(rfEdges);
      }
    };
    init();
  }, []);

  return (
    <div className="h-screen w-full flex flex-col">
      <div className="p-4 bg-white border-b">
        <h1 className="text-2xl font-bold">Lineage Explorer</h1>
      </div>
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
        >
          <Controls />
          <Background />
        </ReactFlow>
      </div>
    </div>
  );
}