"use client";
import { useState, useEffect } from "react";

export default function TenantSettings({ tenantId, jwtToken }: { tenantId: string, jwtToken: string }) {
  const [config, setConfig] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const fetchConfig = async () => {
    try {
      const headers: Record<string, string> = { "x-tenant-id": tenantId };
      if (jwtToken) headers["Authorization"] = `Bearer ${jwtToken}`;
      
      const res = await fetch(`/api/policies/${tenantId}/config`, { headers });
      if (res.ok) {
        setConfig(await res.json());
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchConfig();
  }, [tenantId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      const headers: Record<string, string> = { 
        "Content-Type": "application/json",
        "x-tenant-id": tenantId 
      };
      if (jwtToken) headers["Authorization"] = `Bearer ${jwtToken}`;
      
      const payload = {
        dlp_model: config.dlp_model,
        dlp_api_base: config.dlp_api_base,
        dlp_api_key: config.dlp_api_key,
        monthly_budget: config.monthly_budget,
        siem_webhook_url: config.siem_webhook_url,
        hitl_webhook_url: config.hitl_webhook_url,
        mcp_upstream_url: config.mcp_upstream_url
      };

      const res = await fetch(`/api/policies/${tenantId}/config`, {
        method: "POST",
        headers,
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        setMessage("Settings saved successfully.");
      } else {
        setMessage("Failed to save settings.");
      }
    } catch (err) {
      console.error(err);
      setMessage("Error saving settings.");
    }
    setSaving(false);
  };

  const currentSpend = (config.current_spend || 0) / 100;
  const budget = (config.monthly_budget || 0) / 100;
  const percentUsed = budget > 0 ? Math.min((currentSpend / budget) * 100, 100) : 0;

  if (loading) return <div>Loading settings...</div>;

  return (
    <div className="space-y-6">
      {/* Billing Widget */}
      <div className="bg-white dark:bg-[#0a0a0a] p-6 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm dark:shadow-xl">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Enterprise Cost Controls</h3>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-500">Current Spend</span>
          <span className="text-sm font-bold text-slate-900 dark:text-white">${currentSpend.toFixed(2)} / ${budget > 0 ? budget.toFixed(2) : "∞"}</span>
        </div>
        <div className="w-full bg-slate-200 dark:bg-white/10 rounded-full h-2.5 mb-2">
          <div className={`h-2.5 rounded-full ${percentUsed > 80 ? 'bg-red-500' : 'bg-emerald-500'}`} style={{ width: `${percentUsed}%` }}></div>
        </div>
        {budget > 0 && percentUsed >= 100 && (
          <p className="text-xs text-red-500 mt-2 font-medium">⚠️ Budget exceeded. All non-free tool execution is suspended.</p>
        )}
      </div>

      <form onSubmit={handleSubmit} className="bg-white dark:bg-[#0a0a0a] p-6 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm dark:shadow-xl space-y-6">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white border-b border-slate-200 dark:border-white/10 pb-2">Tenant Configuration</h3>
        
        <div className="mb-6 bg-indigo-50 dark:bg-indigo-900/20 p-4 rounded-xl border border-indigo-100 dark:border-indigo-500/20">
          <label className="block text-xs font-bold uppercase text-indigo-800 dark:text-indigo-300 mb-2">Workspace API Key (For Agents)</label>
          <div className="flex space-x-2">
            <input readOnly type="text" value={config.api_key || "Loading..."} className="w-full px-4 py-2 bg-white dark:bg-black border border-indigo-200 dark:border-indigo-500/30 rounded-lg text-sm font-mono text-slate-700 dark:text-slate-300 outline-none select-all" />
          </div>
          <p className="text-xs text-indigo-600 dark:text-indigo-400 mt-2 font-medium">Agents must pass this key as an <code className="bg-indigo-100 dark:bg-indigo-500/30 px-1 py-0.5 rounded">Authorization: Bearer</code> header.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-500 mb-2">Monthly Budget Limit (Cents)</label>
            <input type="number" value={config.monthly_budget || 0} onChange={(e) => setConfig({...config, monthly_budget: parseInt(e.target.value)})} className="w-full px-4 py-2 bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-xl" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-500 mb-2">DLP LLM Model</label>
            <input type="text" value={config.dlp_model || ""} onChange={(e) => setConfig({...config, dlp_model: e.target.value})} placeholder="e.g. ollama/llama3" className="w-full px-4 py-2 bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-xl" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-500 mb-2">DLP API Base URL (Optional)</label>
            <input type="text" value={config.dlp_api_base || ""} onChange={(e) => setConfig({...config, dlp_api_base: e.target.value})} placeholder="http://localhost:11434" className="w-full px-4 py-2 bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-xl" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-500 mb-2">DLP API Key (Optional)</label>
            <input type="password" value={config.dlp_api_key || ""} onChange={(e) => setConfig({...config, dlp_api_key: e.target.value})} className="w-full px-4 py-2 bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-xl" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-500 mb-2">DLP Sensitivity Level</label>
            <select value={config.dlp_sensitivity || "high"} onChange={(e) => setConfig({...config, dlp_sensitivity: e.target.value})} className="w-full px-4 py-2 bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-xl outline-none">
              <option value="high">High (Strict PII & Danger)</option>
              <option value="medium">Medium (Clear PII & Danger)</option>
              <option value="low">Low (Destructive Commands Only)</option>
            </select>
          </div>
          <div className="md:col-span-2">
            <label className="block text-xs font-semibold uppercase text-slate-500 mb-2">SIEM Log Export Webhook</label>
            <input type="text" value={config.siem_webhook_url || ""} onChange={(e) => setConfig({...config, siem_webhook_url: e.target.value})} placeholder="https://..." className="w-full px-4 py-2 bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-xl" />
          </div>
          <div className="md:col-span-2">
            <label className="block text-xs font-semibold uppercase text-slate-500 mb-2">HITL Alerts Webhook (Slack/Teams)</label>
            <input type="text" value={config.hitl_webhook_url || ""} onChange={(e) => setConfig({...config, hitl_webhook_url: e.target.value})} placeholder="https://..." className="w-full px-4 py-2 bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-xl" />
          </div>
          <div className="md:col-span-2">
            <label className="block text-xs font-semibold uppercase text-slate-500 mb-2">MCP Upstream URL (Optional)</label>
            <input type="text" value={config.mcp_upstream_url || ""} onChange={(e) => setConfig({...config, mcp_upstream_url: e.target.value})} placeholder="http://localhost:8080" className="w-full px-4 py-2 bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-xl" />
          </div>
        </div>

        {message && <p className="text-sm font-medium text-emerald-600 dark:text-emerald-400">{message}</p>}
        
        <button disabled={saving} type="submit" className="px-6 py-2 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-all">
          {saving ? "Saving..." : "Save Settings"}
        </button>
      </form>

      {/* Team Management */}
      <TeamManagement tenantId={tenantId} jwtToken={jwtToken} />
    </div>
  );
}

function TeamManagement({ tenantId, jwtToken }: { tenantId: string, jwtToken: string }) {
  const [members, setMembers] = useState<any[]>([]);
  const [newEmail, setNewEmail] = useState("");
  const [newRole, setNewRole] = useState("developer");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchMembers = async () => {
    try {
      const headers: Record<string, string> = { "x-tenant-id": tenantId };
      if (jwtToken) headers["Authorization"] = `Bearer ${jwtToken}`;
      const res = await fetch(`/api/tenants/${tenantId}/members`, { headers });
      if (res.ok) setMembers(await res.json());
    } catch (e) {}
    setLoading(false);
  };

  useEffect(() => { fetchMembers(); }, [tenantId]);

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const headers: Record<string, string> = { "x-tenant-id": tenantId, "Content-Type": "application/json" };
      if (jwtToken) headers["Authorization"] = `Bearer ${jwtToken}`;
      const res = await fetch(`/api/tenants/${tenantId}/members`, {
        method: "POST",
        headers,
        body: JSON.stringify({ email: newEmail, role: newRole, password: newPassword })
      });
      if (res.ok) {
        setNewEmail("");
        setNewPassword("");
        fetchMembers();
      }
    } catch (e) {}
  };

  if (loading) return null;

  return (
    <div className="bg-white dark:bg-[#0a0a0a] p-6 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm dark:shadow-xl space-y-6">
      <h3 className="text-lg font-bold text-slate-900 dark:text-white border-b border-slate-200 dark:border-white/10 pb-2">Team Management</h3>
      
      <div className="space-y-3">
        {members.map(m => (
          <div key={m.user_id} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-[#111] rounded-xl border border-slate-200 dark:border-white/10">
            <div>
              <p className="font-semibold text-sm text-slate-900 dark:text-white">{m.email}</p>
              <p className="text-xs text-slate-500 font-mono">{m.user_id}</p>
            </div>
            <span className="px-3 py-1 bg-indigo-100 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 text-xs font-bold uppercase rounded-lg border border-indigo-200 dark:border-indigo-500/20">{m.role}</span>
          </div>
        ))}
      </div>

      <form onSubmit={handleAddMember} className="pt-4 border-t border-slate-200 dark:border-white/10 grid grid-cols-1 md:grid-cols-4 gap-4">
        <input required type="email" placeholder="Email" value={newEmail} onChange={e => setNewEmail(e.target.value)} className="w-full px-4 py-2 bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-xl text-sm" />
        <input required type="password" placeholder="Temp Password" value={newPassword} onChange={e => setNewPassword(e.target.value)} className="w-full px-4 py-2 bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-xl text-sm" />
        <select value={newRole} onChange={e => setNewRole(e.target.value)} className="w-full px-4 py-2 bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-xl text-sm outline-none">
          <option value="owner">Owner</option>
          <option value="admin">Admin</option>
          <option value="developer">Developer</option>
          <option value="auditor">Auditor</option>
        </select>
        <button type="submit" className="px-4 py-2 bg-slate-900 dark:bg-white text-white dark:text-black rounded-xl font-semibold hover:bg-slate-800 transition-all text-sm shadow-sm">Add Member</button>
      </form>
    </div>
  );
}
