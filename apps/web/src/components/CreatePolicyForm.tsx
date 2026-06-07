"use client";
import { useState } from "react";

interface Rule {
  field: string;
  operator: string;
  value: string;
}

export default function CreatePolicyForm({ onCreated }: { onCreated: () => void }) {
  const [agentId, setAgentId] = useState("");
  const [toolName, setToolName] = useState("");
  const [action, setAction] = useState("allow");
  const [loading, setLoading] = useState(false);
  
  const [advancedMode, setAdvancedMode] = useState(false);
  const [condition, setCondition] = useState("AND");
  const [rules, setRules] = useState<Rule[]>([{ field: "", operator: "equals", value: "" }]);

  const updateRule = (index: number, key: keyof Rule, value: string) => {
    const newRules = [...rules];
    newRules[index][key] = value;
    setRules(newRules);
  };

  const addRule = () => {
    setRules([...rules, { field: "", operator: "equals", value: "" }]);
  };

  const removeRule = (index: number) => {
    if (rules.length > 1) {
      setRules(rules.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload: any = { agent_id: agentId, tool_name: toolName, action };
      if (action === "allow" && advancedMode) {
        payload.dsl_rules = JSON.stringify({
          condition,
          rules: rules.filter(r => r.field.trim() !== "")
        });
      }
      
      const res = await fetch("/api/policies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setAgentId("");
        setToolName("");
        setRules([{ field: "", operator: "equals", value: "" }]);
        onCreated();
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white dark:bg-[#0a0a0a] p-6 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm dark:shadow-xl relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-400 via-indigo-500 to-purple-500"></div>
      <div className="space-y-5">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2">Agent Identifier</label>
          <input 
            type="text" 
            placeholder="e.g., finance-bot"
            value={agentId} onChange={(e) => setAgentId(e.target.value)}
            className="w-full px-4 py-3 bg-slate-50 dark:bg-black/50 border border-slate-200 dark:border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-600 font-mono text-sm"
            required 
          />
        </div>
        <div>
          <label className="block text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2">Tool Name</label>
          <input 
            type="text" 
            placeholder="e.g., execute_sql"
            value={toolName} onChange={(e) => setToolName(e.target.value)}
            className="w-full px-4 py-3 bg-slate-50 dark:bg-black/50 border border-slate-200 dark:border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-600 font-mono text-sm"
            required 
          />
        </div>
        <div>
          <label className="block text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2">Security Posture</label>
          <select 
            value={action} onChange={(e) => setAction(e.target.value)}
            className="w-full px-4 py-3 bg-slate-50 dark:bg-black/50 border border-slate-200 dark:border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all text-slate-900 dark:text-white font-medium appearance-none"
          >
            <option value="allow">🟢 Allow Execution</option>
            <option value="deny">🔴 Deny Execution</option>
            <option value="require_approval">🟡 Require Human Approval</option>
          </select>
        </div>
        
        {action === "allow" && (
          <div className="bg-slate-50 dark:bg-black/30 border border-slate-200 dark:border-white/10 p-4 rounded-xl space-y-3 mt-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold uppercase tracking-widest text-slate-500">Advanced DSL Rules</label>
              <button type="button" onClick={() => setAdvancedMode(!advancedMode)} className="text-xs font-medium text-indigo-600 dark:text-indigo-400">
                {advancedMode ? "Disable" : "Enable"}
              </button>
            </div>
            
            {advancedMode && (
              <div className="space-y-3 pt-2">
                <div className="flex items-center space-x-2 mb-3">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Match</span>
                  <select value={condition} onChange={(e) => setCondition(e.target.value)} className="px-2 py-1 bg-white dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded text-xs font-semibold text-slate-900 dark:text-white outline-none">
                    <option value="AND">ALL</option>
                    <option value="OR">ANY</option>
                  </select>
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest">of the following rules:</span>
                </div>
                
                {rules.map((rule, index) => (
                  <div key={index} className="flex space-x-2">
                    <input type="text" placeholder="Payload Field" value={rule.field} onChange={(e) => updateRule(index, "field", e.target.value)} className="flex-1 px-3 py-2 bg-white dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-lg text-sm text-slate-900 dark:text-white outline-none focus:border-indigo-500" />
                    <select value={rule.operator} onChange={(e) => updateRule(index, "operator", e.target.value)} className="w-32 px-3 py-2 bg-white dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-lg text-sm text-slate-900 dark:text-white outline-none focus:border-indigo-500">
                      <option value="equals">Equals</option>
                      <option value="not_equals">Not Equals</option>
                      <option value="contains">Contains</option>
                      <option value="not_contains">Not Contains</option>
                      <option value="regex">Matches Regex</option>
                      <option value="greater_than">Greater Than</option>
                      <option value="less_than">Less Than</option>
                    </select>
                    <input type="text" placeholder="Value" value={rule.value} onChange={(e) => updateRule(index, "value", e.target.value)} className="flex-1 px-3 py-2 bg-white dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-lg text-sm text-slate-900 dark:text-white outline-none focus:border-indigo-500" />
                    {rules.length > 1 && (
                      <button type="button" onClick={() => removeRule(index)} className="px-3 py-2 text-red-500 hover:bg-red-500/10 rounded-lg transition-colors">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                      </button>
                    )}
                  </div>
                ))}
                
                <button type="button" onClick={addRule} className="text-xs font-semibold text-indigo-500 hover:text-indigo-400 flex items-center space-x-1 pt-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
                  <span>Add Rule</span>
                </button>
              </div>
            )}
          </div>
        )}
        <button 
          disabled={loading}
          type="submit" 
          className="w-full bg-black dark:bg-white text-white dark:text-black py-3 rounded-xl font-semibold hover:bg-slate-800 dark:hover:bg-slate-200 transition-all dark:shadow-[0_0_20px_rgba(255,255,255,0.1)] mt-2 flex items-center justify-center space-x-2"
        >
          {loading ? (
            <span className="w-5 h-5 border-2 border-white dark:border-black border-t-transparent rounded-full animate-spin"></span>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
              <span>Enforce Rule</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
