"use client";

import React, { useMemo } from 'react';
import { ReactFlow, Background, Controls, MiniMap, Node, Edge, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Policy } from './PolicyCard';
import { useTheme } from 'next-themes';

interface InfrastructureMapProps {
  policies: Policy[];
}

export default function InfrastructureMap({ policies }: InfrastructureMapProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const { nodes, edges } = useMemo(() => {
    const agents = new Set<string>();
    const tools = new Set<string>();
    const newNodes: Node[] = [];
    const newEdges: Edge[] = [];

    // Extract unique agents and tools
    policies.forEach((policy) => {
      agents.add(policy.agent_id);
      tools.add(policy.tool_name);
    });

    // Create Agent Nodes
    Array.from(agents).forEach((agent, i) => {
      newNodes.push({
        id: `agent-${agent}`,
        type: 'input',
        position: { x: 100, y: i * 100 + 50 },
        data: { label: `🤖 Agent: ${agent}` },
        style: {
          background: isDark ? '#111' : '#fff',
          color: isDark ? '#fff' : '#000',
          border: '1px solid #6366f1',
          borderRadius: '12px',
          padding: '10px 15px',
          fontWeight: 'bold',
          boxShadow: isDark ? '0 0 15px rgba(99, 102, 241, 0.2)' : '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        }
      });
    });

    // Create Tool Nodes
    Array.from(tools).forEach((tool, i) => {
      newNodes.push({
        id: `tool-${tool}`,
        type: 'output',
        position: { x: 500, y: i * 100 + 50 },
        data: { label: `🛠️ Tool: ${tool}` },
        style: {
          background: isDark ? '#111' : '#fff',
          color: isDark ? '#fff' : '#000',
          border: '1px solid #10b981',
          borderRadius: '12px',
          padding: '10px 15px',
          fontWeight: 'bold',
          boxShadow: isDark ? '0 0 15px rgba(16, 185, 129, 0.2)' : '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
        }
      });
    });

    // Create Edges
    policies.forEach((policy) => {
      let strokeColor = '#94a3b8'; // default slate
      if (policy.action === 'allow') strokeColor = '#10b981'; // emerald
      if (policy.action === 'deny') strokeColor = '#ef4444'; // red
      if (policy.action === 'require_approval') strokeColor = '#f59e0b'; // amber

      newEdges.push({
        id: `edge-${policy.agent_id}-${policy.tool_name}`,
        source: `agent-${policy.agent_id}`,
        target: `tool-${policy.tool_name}`,
        animated: policy.action === 'allow',
        style: { stroke: strokeColor, strokeWidth: 2 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: strokeColor,
        },
      });
    });

    return { nodes: newNodes, edges: newEdges };
  }, [policies, isDark]);

  return (
    <div className="h-[600px] w-full bg-slate-50 dark:bg-black/50 border border-slate-200 dark:border-white/10 rounded-2xl overflow-hidden shadow-sm dark:shadow-xl">
      <ReactFlow 
        nodes={nodes} 
        edges={edges}
        fitView
        className="w-full h-full"
      >
        <Background color={isDark ? '#333' : '#cbd5e1'} gap={16} />
        <Controls className={isDark ? 'fill-white bg-[#111] border-white/10 text-white' : ''} />
        <MiniMap 
          nodeColor={(node) => {
            if (node.id.startsWith('agent')) return '#6366f1';
            return '#10b981';
          }}
          maskColor={isDark ? 'rgba(0,0,0,0.5)' : 'rgba(255,255,255,0.5)'}
          style={{ backgroundColor: isDark ? '#111' : '#fff', border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid #e2e8f0' }}
        />
      </ReactFlow>
    </div>
  );
}
