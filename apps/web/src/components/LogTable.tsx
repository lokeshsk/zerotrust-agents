export interface AuditLog {
  id: number;
  agent_id: string;
  tool_name: string;
  arguments: string;
  is_allowed: boolean;
  timestamp: string;
}

export default function LogTable({ logs }: { logs: any[] }) {
  if (!logs || logs.length === 0) {
    return (
      <div className="py-20 flex flex-col items-center justify-center text-slate-500">
        <svg className="w-10 h-10 mb-4 opacity-50 text-slate-400 dark:text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="font-medium text-slate-600 dark:text-slate-400">No telemetry recorded yet.</p>
        <p className="text-sm mt-1">Start routing AI requests through the gateway to view traffic.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="bg-slate-50 dark:bg-black/50 border-b border-slate-200 dark:border-white/10">
            <th className="px-6 py-4 text-xs font-semibold uppercase tracking-widest text-slate-500">Timestamp</th>
            <th className="px-6 py-4 text-xs font-semibold uppercase tracking-widest text-slate-500">Agent Identity</th>
            <th className="px-6 py-4 text-xs font-semibold uppercase tracking-widest text-slate-500">Tool Target</th>
            <th className="px-6 py-4 text-xs font-semibold uppercase tracking-widest text-slate-500">Action</th>
            <th className="px-6 py-4 text-xs font-semibold uppercase tracking-widest text-slate-500">Verdict</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 dark:divide-white/5">
          {logs.map((log, idx) => (
            <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors bg-white dark:bg-transparent cursor-pointer">
              <td className="px-6 py-4 text-sm text-slate-600 dark:text-slate-400 whitespace-nowrap">
                {new Date(log.timestamp).toLocaleString()}
              </td>
              <td className="px-6 py-4">
                <span className="font-mono text-sm font-medium text-slate-900 dark:text-white bg-slate-100 dark:bg-white/5 px-2 py-1 rounded border border-slate-200 dark:border-white/10">
                  {log.agent_id}
                </span>
              </td>
              <td className="px-6 py-4">
                <span className="font-mono text-sm text-indigo-600 dark:text-indigo-400">
                  {log.tool_name}
                </span>
              </td>
              <td className="px-6 py-4">
                <span className={`px-2.5 py-1 text-xs font-bold rounded-full border ${
                  log.is_allowed 
                    ? "bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20" 
                    : "bg-red-100 text-red-700 border-red-200 dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/20"
                }`}>
                  {log.is_allowed ? "ALLOWED" : "BLOCKED"}
                </span>
              </td>
              <td className="px-6 py-4 text-sm font-mono text-slate-500 truncate max-w-[200px]" title={log.arguments}>
                {log.arguments || "{}"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
