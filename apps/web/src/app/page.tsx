/// <reference types="react" />
"use client";
import React, { useEffect, useState } from "react";
import LogTable, { AuditLog } from "@/components/LogTable";
import CreatePolicyForm from "@/components/CreatePolicyForm";
import { ThemeToggle } from "@/components/ThemeToggle";
import AnalyticsDashboard from "@/components/AnalyticsDashboard";
import InfrastructureMap from "@/components/InfrastructureMap";
import TenantSettings from "@/components/TenantSettings";
import PolicyCard from "@/components/PolicyCard";

export interface Tenant {
  id: string;
  name: string;
  billing_plan: string;
  events_this_month: number;
}

interface PendingApproval {
  id: number;
  agent_id: string;
  tool_name: string;
  arguments: string;
  status: string;
  created_at: string;
}

export interface Policy {
  id: number;
  agent_id: string;
  tool_name: string;
  action: "allow" | "deny" | "require_approval" | string;
  created_at: string;
  dsl_rules?: string;
}

export default function Home() {
  const [activeTab, setActiveTab] = useState("access_control");
  const [authStatus, setAuthStatus] = useState<"loading" | "needs_setup" | "needs_login" | "authenticated">("loading");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [jwtToken, setJwtToken] = useState("");
  const [selectedTenant, setSelectedTenant] = useState("default");

  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [approvals, setApprovals] = useState<PendingApproval[]>([]);
  const [policySearch, setPolicySearch] = useState("");

  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [newWorkspaceName, setNewWorkspaceName] = useState("");
  const [isCreatingWorkspace, setIsCreatingWorkspace] = useState(false);

  const fetchData = async () => {
    try {
      const headers: Record<string, string> = {
        "x-tenant-id": selectedTenant
      };
      if (jwtToken) {
        headers["Authorization"] = `Bearer ${jwtToken}`;
      }

      const logsRes = await fetch("/api/logs/", { headers });
      if (logsRes.ok) setLogs(await logsRes.json());

      const polRes = await fetch("/api/policies/", { headers });
      if (polRes.ok) setPolicies(await polRes.json());

      const appRes = await fetch("/api/policies/approvals", { headers });
      if (appRes.ok) setApprovals(await appRes.json());
      
      const tenantsRes = await fetch("/api/tenants/", { headers: jwtToken ? { "Authorization": `Bearer ${jwtToken}` } : {} });
      if (tenantsRes.ok) setTenants(await tenantsRes.json());
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateWorkspace = async () => {
    if (!newWorkspaceName.trim()) return;
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (jwtToken) headers["Authorization"] = `Bearer ${jwtToken}`;
      const res = await fetch("/api/tenants/", {
        method: "POST",
        headers,
        body: JSON.stringify({ name: newWorkspaceName })
      });
      if (res.ok) {
        const newTenant = await res.json();
        setTenants([...tenants, newTenant]);
        setSelectedTenant(newTenant.id);
        setNewWorkspaceName("");
        setIsCreatingWorkspace(false);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("/api/auth/setup-status");
        if (res.ok) {
          const data = await res.json();
          if (data.is_setup) {
            setAuthStatus("needs_login");
          } else {
            setAuthStatus("needs_setup");
          }
        } else {
          setAuthStatus("needs_setup");
        }
      } catch (e) {
        setAuthStatus("needs_setup");
      }
    };
    checkAuth();
  }, []);

  useEffect(() => {
    if (authStatus === "authenticated") {
      fetchData();
      
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${protocol}//${window.location.host}/api/ws/events`;
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === "NEW_LOG" || message.type === "NEW_APPROVAL") {
            fetchData();
          }
        } catch (e) {
          console.error("WS Parse error", e);
        }
      };

      return () => {
        ws.close();
      };
    }
  }, [authStatus, selectedTenant, jwtToken]);

  const handleSetup = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError("");
    try {
      const res = await fetch("/api/auth/setup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password })
      });
      if (res.ok) {
        setAuthStatus("authenticated");
        setPassword("");
      } else {
        setAuthError("Failed to setup master key");
      }
    } catch (e) {
      setAuthError("Network error");
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError("");
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password })
      });
      if (res.ok) {
        const data = await res.json();
        setJwtToken(data.token);
        setAuthStatus("authenticated");
        setPassword("");
      } else {
        setAuthError("Invalid master key");
      }
    } catch (e) {
      setAuthError("Network error");
    }
  };

  useEffect(() => {
    // Check if token was passed via OAuth callback
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get("token");
    if (urlToken) {
      setJwtToken(urlToken);
      setAuthStatus("authenticated");
      // Clean up URL without refreshing
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const handleLogout = async () => {
    if (jwtToken) {
      window.location.href = "/api/auth/logout";
      return;
    }
    setAuthStatus("needs_login");
  };

  const resolveApproval = async (id: number, action: "approved" | "rejected") => {
    try {
      const headers: Record<string, string> = {
        "x-tenant-id": selectedTenant
      };
      if (jwtToken) {
        headers["Authorization"] = `Bearer ${jwtToken}`;
      }
      await fetch(`/api/policies/approvals/${id}/resolve?action=${action}`, {
        method: "POST",
        headers
      });
      fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  const filteredPolicies = policies.filter(p =>
    p.agent_id.toLowerCase().includes(policySearch.toLowerCase()) ||
    p.tool_name.toLowerCase().includes(policySearch.toLowerCase())
  );

  if (authStatus === "loading") {
    return <div className="min-h-screen bg-slate-50 dark:bg-black flex items-center justify-center font-sans text-slate-900 dark:text-white">Loading...</div>;
  }

  if (authStatus === "needs_setup" || authStatus === "needs_login") {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-black flex items-center justify-center font-sans text-slate-900 dark:text-white px-4">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-100 via-slate-50 to-slate-50 dark:from-indigo-900/20 dark:via-black dark:to-black z-0"></div>
        <div className="w-full max-w-md bg-white dark:bg-[#0a0a0a] p-8 rounded-2xl shadow-xl dark:shadow-2xl border border-slate-200 dark:border-white/10 z-10 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>
          <div className="flex justify-center mb-6">
            <div className="w-14 h-14 rounded-2xl bg-slate-100 dark:bg-white/5 flex items-center justify-center border border-slate-200 dark:border-white/10 shadow-inner">
              <svg className="w-7 h-7 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-center tracking-tight mb-2 text-slate-900 dark:text-white">
            {authStatus === "needs_setup" ? "Initialize Gateway" : "Gateway Authentication"}
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 text-center mb-8">
            {authStatus === "needs_setup" ? "Create a master key to secure your AI infrastructure." : "Enter your master key to access the control plane."}
          </p>

          <form onSubmit={authStatus === "needs_setup" ? handleSetup : handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Master Key</label>
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 dark:border-white/10 rounded-lg focus:ring-2 focus:ring-indigo-500 bg-white dark:bg-[#111111] text-slate-900 dark:text-white transition-all shadow-sm dark:shadow-none"
                placeholder="Enter access key"
              />
            </div>
            {authError && <p className="text-red-500 text-sm">{authError}</p>}
            <button
              type="submit"
              className="w-full bg-black dark:bg-white text-white dark:text-black py-3 rounded-xl font-semibold hover:bg-slate-800 dark:hover:bg-slate-200 transition-colors shadow-lg dark:shadow-[0_0_20px_rgba(255,255,255,0.1)]"
            >
              {authStatus === "needs_setup" ? "Secure Infrastructure" : "Authenticate"}
            </button>
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200 dark:border-white/10"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white dark:bg-[#0a0a0a] text-slate-500">Or continue with</span>
              </div>
            </div>
            
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                window.location.href = '/api/auth/login/sso';
              }}
              className="w-full flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl transition-colors font-semibold shadow-lg dark:shadow-[0_0_20px_rgba(79,70,229,0.2)]"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <span>Enterprise SSO (Auth0)</span>
            </button>
            <p className="text-center text-xs mt-3 text-slate-500">
              Requires <a href="/enterprise" className="text-indigo-600 hover:underline">Agent Firewall EE</a>
            </p>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#050505] font-sans text-slate-900 dark:text-slate-300 selection:bg-indigo-100 dark:selection:bg-indigo-500/30 flex transition-colors duration-300">
      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-slate-200 dark:border-white/10 bg-white dark:bg-[#0a0a0a] flex flex-col justify-between hidden md:flex sticky top-0 h-screen transition-colors duration-300">
        <div>
          <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-white/10">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mr-3 shadow-lg shadow-indigo-500/20">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight text-slate-900 dark:text-white">ZeroTrust<span className="text-indigo-600 dark:text-indigo-400">AI</span></span>
          </div>
          <div className="px-4 py-3 border-b border-slate-200 dark:border-white/10">
            <div className="flex justify-between items-center mb-1.5">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Workspace</label>
              <button 
                onClick={() => setIsCreatingWorkspace(!isCreatingWorkspace)}
                className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 transition-colors"
                title="Create Workspace"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>
            {isCreatingWorkspace ? (
              <div className="flex items-center space-x-2 mt-2">
                <input 
                  type="text" 
                  value={newWorkspaceName}
                  onChange={(e) => setNewWorkspaceName(e.target.value)}
                  placeholder="New workspace..."
                  className="w-full text-sm px-2 py-1 border border-slate-300 dark:border-white/10 rounded-md bg-white dark:bg-[#111] focus:outline-none"
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateWorkspace()}
                />
                <button onClick={handleCreateWorkspace} className="bg-indigo-600 text-white px-2 py-1 rounded-md text-sm font-semibold">Add</button>
              </div>
            ) : (
              <select 
                value={selectedTenant}
                onChange={(e) => setSelectedTenant(e.target.value)}
                className="w-full bg-slate-50 dark:bg-[#111] border border-slate-200 dark:border-white/10 rounded-lg text-sm px-2 py-1.5 focus:ring-1 focus:ring-indigo-500 outline-none text-slate-700 dark:text-slate-300"
              >
                {tenants.map(t => (
                  <option key={t.id} value={t.id}>{t.name} {t.id === "default" ? "" : `(${t.billing_plan})`}</option>
                ))}
                {!tenants.find(t => t.id === "default") && (
                  <option value="default">Default Organization</option>
                )}
              </select>
            )}
          </div>
          <nav className="p-4 space-y-1">
            <button onClick={() => setActiveTab("access_control")} className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all ${activeTab === "access_control" ? "bg-slate-100 text-slate-900 dark:bg-white/10 dark:text-white shadow-inner border border-slate-200 dark:border-white/5" : "text-slate-500 hover:bg-slate-50 dark:hover:bg-white/5 hover:text-slate-700 dark:hover:text-slate-300"}`}>
              <svg className={`w-5 h-5 ${activeTab === "access_control" ? "text-indigo-600 dark:text-indigo-400" : "text-slate-500"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <span>Access Control</span>
            </button>
            <button onClick={() => setActiveTab("traffic_logs")} className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all ${activeTab === "traffic_logs" ? "bg-slate-100 text-slate-900 dark:bg-white/10 dark:text-white shadow-inner border border-slate-200 dark:border-white/5" : "text-slate-500 hover:bg-slate-50 dark:hover:bg-white/5 hover:text-slate-700 dark:hover:text-slate-300"}`}>
              <svg className={`w-5 h-5 ${activeTab === "traffic_logs" ? "text-indigo-600 dark:text-indigo-400" : "text-slate-500"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
              <span>Traffic Logs</span>
            </button>
            <button onClick={() => setActiveTab("infrastructure")} className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all ${activeTab === "infrastructure" ? "bg-slate-100 text-slate-900 dark:bg-white/10 dark:text-white shadow-inner border border-slate-200 dark:border-white/5" : "text-slate-500 hover:bg-slate-50 dark:hover:bg-white/5 hover:text-slate-700 dark:hover:text-slate-300"}`}>
              <svg className={`w-5 h-5 ${activeTab === "infrastructure" ? "text-indigo-600 dark:text-indigo-400" : "text-slate-500"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
              <span>Infrastructure Map</span>
            </button>
            <button onClick={() => setActiveTab("enterprise")} className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all ${activeTab === "enterprise" ? "bg-slate-100 text-slate-900 dark:bg-white/10 dark:text-white shadow-inner border border-slate-200 dark:border-white/5" : "text-slate-500 hover:bg-slate-50 dark:hover:bg-white/5 hover:text-slate-700 dark:hover:text-slate-300"}`}>
              <svg className={`w-5 h-5 ${activeTab === "enterprise" ? "text-indigo-600 dark:text-indigo-400" : "text-slate-500"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
              <span>Enterprise Hub</span>
            </button>
            <button onClick={() => setActiveTab("settings")} className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all ${activeTab === "settings" ? "bg-slate-100 text-slate-900 dark:bg-white/10 dark:text-white shadow-inner border border-slate-200 dark:border-white/5" : "text-slate-500 hover:bg-slate-50 dark:hover:bg-white/5 hover:text-slate-700 dark:hover:text-slate-300"}`}>
              <svg className={`w-5 h-5 ${activeTab === "settings" ? "text-indigo-600 dark:text-indigo-400" : "text-slate-500"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              <span>Settings</span>
            </button>
          </nav>
        </div>
        <div className="p-4 border-t border-slate-200 dark:border-white/10">
          <button onClick={handleLogout} className="flex items-center space-x-3 px-3 py-2 w-full text-slate-500 hover:bg-red-50 dark:hover:bg-red-500/10 hover:text-red-600 dark:hover:text-red-400 rounded-lg font-medium text-sm transition-colors border border-transparent hover:border-red-200 dark:hover:border-red-500/20">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
            <span>Disconnect</span>
          </button>
        </div>
      </aside>

      <main className="flex-1 pb-12 h-screen overflow-y-auto relative">
        {/* Subtle background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-indigo-500/5 dark:bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none"></div>

        {/* Top Header */}
        <header className="w-full border-b border-slate-200 dark:border-white/10 bg-white/80 dark:bg-[#0a0a0a]/80 backdrop-blur-md px-8 py-4 sticky top-0 z-40 flex justify-between items-center transition-colors duration-300">
          <h1 className="font-semibold text-lg text-slate-900 dark:text-white">
            {activeTab === "access_control" && "Policy Enforcement"}
            {activeTab === "traffic_logs" && "Network Telemetry"}
            {activeTab === "enterprise" && "Enterprise Hub"}
          </h1>
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            <div className="flex items-center space-x-2 px-4 py-1.5 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 rounded-full border border-emerald-200 dark:border-emerald-500/20 shadow-sm dark:shadow-[0_0_15px_rgba(16,185,129,0.1)]">
              <span className="w-2 h-2 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse dark:shadow-[0_0_5px_#34d399]"></span>
              <span className="font-medium text-xs tracking-wider uppercase">Gateway Active</span>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-8 pt-8 space-y-8 relative z-10">
          {/* Human in the Loop Approval Queue */}
          {approvals.length > 0 && (
            <div className="bg-amber-50 dark:bg-[#111111] border border-amber-200 dark:border-amber-500/30 rounded-2xl p-6 shadow-sm dark:shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-amber-400 to-orange-500"></div>
              <div className="flex items-center mb-6">
                <span className="relative flex h-3 w-3 mr-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500 dark:shadow-[0_0_8px_#f59e0b]"></span>
                </span>
                <h2 className="text-lg font-semibold text-amber-900 dark:text-white tracking-tight">Security Intervention Required</h2>
              </div>
              <div className="space-y-4">
                {approvals.map(app => (
                  <div key={app.id} className="bg-white dark:bg-black border border-amber-100 dark:border-white/5 rounded-xl p-5 flex items-center justify-between hover:border-amber-300 dark:hover:border-amber-500/30 transition-all shadow-sm dark:shadow-none cursor-pointer">
                    <div>
                      <p className="font-medium text-slate-700 dark:text-slate-300 text-sm">
                        Agent <span className="font-mono text-indigo-700 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-200 dark:border-indigo-500/20">{app.agent_id}</span> is requesting execution of <span className="font-mono text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-200 dark:border-emerald-500/20">{app.tool_name}</span>
                      </p>
                      <p className="text-xs text-slate-500 mt-2 font-mono truncate max-w-2xl bg-slate-50 dark:bg-white/5 p-2 rounded-md border border-slate-100 dark:border-white/5">Payload: {app.arguments}</p>
                    </div>
                    <div className="flex space-x-3 ml-4">
                      <button onClick={() => resolveApproval(app.id, "rejected")} className="px-5 py-2 rounded-lg border border-red-200 dark:border-red-500/30 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 text-sm font-semibold transition-all">Block</button>
                      <button onClick={() => resolveApproval(app.id, "approved")} className="px-5 py-2 rounded-lg bg-black dark:bg-white text-white dark:text-black hover:bg-slate-800 dark:hover:bg-slate-200 text-sm font-semibold transition-all dark:shadow-[0_0_15px_rgba(255,255,255,0.1)]">Authorize</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Access Control View */}
          {activeTab === "access_control" && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in duration-500">
              <div className="lg:col-span-4 space-y-6">
                <div>
                  <h2 className="text-xl font-semibold tracking-tight text-slate-900 dark:text-white">Rule Configuration</h2>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Deploy zero-trust policies for AI workloads.</p>
                </div>
                <CreatePolicyForm onCreated={fetchData} />
              </div>

              <div className="lg:col-span-8 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-center space-x-3">
                    <h2 className="text-xl font-semibold tracking-tight text-slate-900 dark:text-white">Active Firewall Rules</h2>
                    <span className="text-xs font-mono bg-slate-100 dark:bg-white/10 px-2 py-1 rounded-md text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-white/10">
                      {filteredPolicies.length} Enforced
                    </span>
                  </div>
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Filter rules..."
                      value={policySearch}
                      onChange={(e) => setPolicySearch(e.target.value)}
                      className="pl-10 pr-4 py-2 text-sm bg-white dark:bg-[#111111] border border-slate-200 dark:border-white/10 rounded-lg focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 outline-none w-full sm:w-64 transition-all text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-600 shadow-sm dark:shadow-none"
                    />
                    <svg className="w-4 h-4 text-slate-400 dark:text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[650px] overflow-y-auto pr-2 pb-4 scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-white/10 scrollbar-track-transparent">
                  {filteredPolicies.length === 0 ? (
                    <div className="col-span-2 py-20 border border-dashed border-slate-300 dark:border-white/10 rounded-2xl flex flex-col items-center justify-center text-slate-500 bg-white dark:bg-[#0a0a0a] shadow-sm dark:shadow-none">
                      <svg className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                      <p className="font-medium text-slate-500 dark:text-slate-400">No matching rules found</p>
                    </div>
                  ) : (
                    filteredPolicies.map((policy, idx) => (
                      <PolicyCard key={idx} policy={policy} />
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Traffic Logs View */}
          {activeTab === "traffic_logs" && (
            <div className="space-y-6 animate-in fade-in duration-500">
              <div>
                <h2 className="text-xl font-semibold tracking-tight text-slate-900 dark:text-white">Network Telemetry</h2>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Real-time observability of all agent tool invocations and DLP events.</p>
              </div>
              <AnalyticsDashboard logs={logs} />
              <div className="bg-white dark:bg-[#0a0a0a] rounded-2xl shadow-sm dark:shadow-xl border border-slate-200 dark:border-white/10 overflow-hidden">
                <LogTable logs={logs} />
              </div>
            </div>
          )}

          {/* Infrastructure Map View */}
          {activeTab === "infrastructure" && (
            <div className="space-y-6 animate-in fade-in duration-500">
              <div>
                <h2 className="text-xl font-semibold tracking-tight text-slate-900 dark:text-white">Auto-Discovery Graph</h2>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Live visualization of your AI workforce and their external tool integrations.</p>
              </div>
              <InfrastructureMap policies={policies} />
            </div>
          )}

          {/* Enterprise View */}
          {activeTab === "enterprise" && (
            <div className="space-y-6 animate-in fade-in duration-500">
              <div className="py-24 border border-slate-200 dark:border-white/5 rounded-3xl flex flex-col items-center justify-center text-slate-600 dark:text-slate-400 bg-gradient-to-b from-white to-slate-50 dark:from-[#111] dark:to-[#0a0a0a] shadow-sm dark:shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-50"></div>
                <svg className="w-16 h-16 text-indigo-500/50 mb-6 drop-shadow-[0_0_15px_rgba(99,102,241,0.2)] dark:drop-shadow-[0_0_15px_rgba(99,102,241,0.5)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Enterprise Infrastructure</h2>
                <p className="text-sm mt-3 max-w-md text-center text-slate-500 leading-relaxed">Unlock advanced capabilities including Active Directory SSO, Webhooks, Multi-tenant Workspaces, and Advanced Semantic DLP Analytics.</p>
                <a href="/enterprise" className="mt-8 px-8 py-3 bg-black dark:bg-white text-white dark:text-black rounded-xl font-semibold hover:bg-slate-800 dark:hover:bg-slate-200 transition-all shadow-md dark:shadow-[0_0_20px_rgba(255,255,255,0.1)] inline-block">View Enterprise Pricing</a>
              </div>
            </div>
          )}

          {/* Settings View */}
          {activeTab === "settings" && (
            <div className="space-y-6 animate-in fade-in duration-500">
              <div>
                <h2 className="text-xl font-semibold tracking-tight text-slate-900 dark:text-white">Workspace Settings</h2>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Configure tenant preferences and enterprise integrations.</p>
              </div>
              <TenantSettings tenantId={selectedTenant} jwtToken={jwtToken} />
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
