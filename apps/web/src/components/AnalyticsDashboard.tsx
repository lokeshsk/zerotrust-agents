"use client";
import { useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { AuditLog } from "./LogTable";

export default function AnalyticsDashboard({ logs }: { logs: AuditLog[] }) {
  const chartData = useMemo(() => {
    if (!logs.length) return [];
    const counts: Record<string, { allowed: number; blocked: number }> = {};
    
    logs.forEach(log => {
      const tool = log.tool_name;
      if (!counts[tool]) counts[tool] = { allowed: 0, blocked: 0 };
      if (log.is_allowed) counts[tool].allowed++;
      else counts[tool].blocked++;
    });

    return Object.entries(counts).map(([name, data]) => ({
      name,
      Allowed: data.allowed,
      Blocked: data.blocked
    }));
  }, [logs]);

  if (!logs.length) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div className="bg-white dark:bg-[#111111] border border-slate-200 dark:border-white/10 p-5 rounded-2xl shadow-sm dark:shadow-lg">
        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-widest mb-4">Invocations by Tool</h3>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#333" opacity={0.2} />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#888' }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#888' }} />
              <Tooltip 
                cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                contentStyle={{ backgroundColor: '#000', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
              />
              <Bar dataKey="Allowed" stackId="a" fill="#10b981" radius={[0, 0, 4, 4]} />
              <Bar dataKey="Blocked" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="bg-white dark:bg-[#111111] border border-slate-200 dark:border-white/10 p-5 rounded-2xl shadow-sm dark:shadow-lg flex flex-col justify-center items-center">
         <div className="text-center space-y-2">
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-widest mb-4">Total Intercepts</h3>
            <div className="text-5xl font-black text-slate-900 dark:text-white font-mono">{logs.length}</div>
            <p className="text-sm text-slate-500">Events processed by Gateway</p>
         </div>
         <div className="mt-8 flex space-x-8">
            <div className="text-center">
              <div className="text-2xl font-bold text-emerald-500">{logs.filter(l => l.is_allowed).length}</div>
              <div className="text-xs text-slate-500 uppercase mt-1">Allowed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-500">{logs.filter(l => !l.is_allowed).length}</div>
              <div className="text-xs text-slate-500 uppercase mt-1">Blocked</div>
            </div>
         </div>
      </div>
    </div>
  );
}
