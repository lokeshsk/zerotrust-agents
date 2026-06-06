export interface Policy {
  id: number;
  agent_id: string;
  tool_name: string;
  action: string;
  created_at: string;
}

export default function PolicyCard({ policy }: { policy: any }) {
  const getBadgeColor = (action: string) => {
    switch (action) {
      case "allow":
        return "bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20";
      case "deny":
        return "bg-red-100 text-red-700 border-red-200 dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/20";
      case "require_approval":
        return "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20";
      default:
        return "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-500/10 dark:text-slate-400 dark:border-slate-500/20";
    }
  };

  const getActionText = (action: string) => {
    switch (action) {
      case "allow": return "Allow";
      case "deny": return "Deny";
      case "require_approval": return "Require Approval";
      default: return action;
    }
  };

  const isDeny = policy.action === "deny";

  return (
    <div className={`bg-white dark:bg-[#111111] border ${isDeny ? 'border-red-200 dark:border-red-500/10' : 'border-slate-200 dark:border-white/5'} p-5 rounded-2xl shadow-sm dark:shadow-lg hover:border-slate-300 dark:hover:border-white/20 transition-all group cursor-pointer`}>
      <div className="flex justify-between items-start mb-4">
        <h3 className="font-mono text-lg font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{policy.tool_name}</h3>
        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getBadgeColor(policy.action)}`}>
          {getActionText(policy.action)}
        </span>
      </div>
      <div className="space-y-3">
        <div className="flex items-center space-x-2">
          <svg className="w-4 h-4 text-slate-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Agent: <span className="font-mono font-medium text-slate-900 dark:text-white">{policy.agent_id}</span>
          </p>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-500 leading-relaxed">
          This policy dictates that when <span className="font-mono text-slate-600 dark:text-slate-400">{policy.agent_id}</span> requests access to <span className="font-mono text-slate-600 dark:text-slate-400">{policy.tool_name}</span>, the gateway will <span className="font-bold text-slate-700 dark:text-slate-300">{getActionText(policy.action).toLowerCase()}</span> the invocation.
        </p>
        {policy.dsl_rules && policy.action === "allow" && (
          <div className="mt-3 p-3 bg-indigo-50 dark:bg-indigo-500/10 rounded-lg border border-indigo-100 dark:border-indigo-500/20">
            <p className="text-xs font-semibold text-indigo-700 dark:text-indigo-400 mb-1">Advanced DSL Condition:</p>
            <p className="font-mono text-xs text-slate-600 dark:text-slate-300">{policy.dsl_rules}</p>
          </div>
        )}
      </div>
    </div>
  );
}
