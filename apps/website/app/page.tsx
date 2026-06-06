import React from 'react';

async function getGithubStars() {
  try {
    const res = await fetch('https://api.github.com/repos/lokeshsk/zerotrust-agents', { next: { revalidate: 3600 } });
    if (!res.ok) return 0;
    const data = await res.json();
    return data.stargazers_count || 0;
  } catch (e) {
    return 0;
  }
}

export default async function Home() {
  const stars = await getGithubStars();
  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-indigo-500/30">
      {/* Navigation */}
      <nav className="border-b border-white/10 bg-black/50 backdrop-blur-md fixed w-full top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span className="font-bold text-xl tracking-tight">ZeroTrust<span className="text-indigo-500">Agents</span></span>
          </div>
          <div className="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-300">
            <a href="#features" className="hover:text-white transition-colors cursor-pointer">Features</a>
            <a href="/docs" className="hover:text-white transition-colors cursor-pointer">Docs</a>
            <a href="#pricing" className="hover:text-white transition-colors cursor-pointer">Pricing</a>
            <a href="https://github.com/lokeshsk/zerotrust-agents" target="_blank" rel="noreferrer" className="hover:text-white transition-colors cursor-pointer flex items-center space-x-1">
              <span>GitHub</span>
              {stars > 0 && (
                <span className="flex items-center space-x-1 bg-white/10 px-2 py-0.5 rounded-full text-xs font-semibold text-slate-200 ml-2">
                  <svg className="w-3 h-3 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  <span>{stars}</span>
                </span>
              )}
            </a>
          </div>
          <div>
            <a href="mailto:hello@zerotrust-agents.com?subject=SaaS%20Waitlist" className="px-5 py-2.5 bg-white/10 text-white border border-white/20 rounded-full font-semibold hover:bg-white/20 transition-colors text-sm cursor-pointer">
              SaaS Coming Soon
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-40 pb-20 px-6 relative overflow-hidden">
        {/* Glow Effects */}
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-indigo-500/20 blur-[120px] rounded-full pointer-events-none"></div>
        
        <div className="max-w-5xl mx-auto text-center relative z-10">
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-tight">
            The Zero-Trust Security Layer <br/> for <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">Autonomous AI Agents</span>
          </h1>
          <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Intercept, analyze, and block rogue AI tool executions in real-time. Protect your databases, APIs, and infrastructure from hallucinating LLMs.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <a href="/docs" className="w-full sm:w-auto px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full font-semibold text-lg transition-all shadow-[0_0_30px_rgba(79,70,229,0.3)] cursor-pointer">
              Start Securing Your Agents
            </a>
            <a href="#pricing" className="w-full sm:w-auto px-8 py-4 bg-white/5 border border-white/10 hover:bg-white/10 text-white rounded-full font-semibold text-lg transition-all cursor-pointer">
              View Enterprise Edition
            </a>
          </div>
        </div>

        {/* Terminal/Code Preview */}
        <div className="max-w-4xl mx-auto mt-20 relative">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl blur opacity-20"></div>
          <div className="relative bg-[#0a0a0a] rounded-2xl border border-white/10 shadow-2xl overflow-hidden">
            <div className="flex items-center px-4 py-3 border-b border-white/5 bg-[#111]">
              <div className="flex space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
              </div>
              <div className="mx-auto text-xs font-mono text-slate-500">Gateway Intercept Log</div>
            </div>
            <div className="p-6 font-mono text-sm text-slate-300">
              <div className="mb-2"><span className="text-indigo-400">INFO</span>: Intercepted tool call from <span className="text-yellow-300">Agent-Alpha</span></div>
              <div className="mb-2"><span className="text-indigo-400">INFO</span>: Target Tool: <span className="text-emerald-400">execute_sql</span></div>
              <div className="mb-4 text-slate-500">Payload: {`{"query": "DROP TABLE users;"}`}</div>
              <div className="mb-2"><span className="text-amber-400">SCAN</span>: Semantic DLP Engine active...</div>
              <div className="mb-2 text-red-400 font-bold">BLOCK: Destructive command detected.</div>
              <div className="text-slate-500">Action: LLM response overridden. Tool execution prevented.</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 px-6 bg-[#050505] border-t border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Enterprise-Grade Protection</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">A comprehensive suite of security and observability tools designed specifically for the era of Agentic AI.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-[#111] p-8 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition-colors">
              <div className="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center mb-6 border border-indigo-500/20">
                <svg className="w-6 h-6 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
              </div>
              <h3 className="text-xl font-bold mb-3">LiteLLM Proxy</h3>
              <p className="text-slate-400 leading-relaxed">Drop-in proxy for OpenAI and Anthropic. We intercept the traffic, evaluate your zero-trust policies, and forward safely.</p>
            </div>
            <div className="bg-[#111] p-8 rounded-2xl border border-white/5 hover:border-emerald-500/30 transition-colors">
              <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center mb-6 border border-emerald-500/20">
                <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              </div>
              <h3 className="text-xl font-bold mb-3">Semantic DLP</h3>
              <p className="text-slate-400 leading-relaxed">Go beyond regex. Use lightweight local LLMs to scan JSON tool arguments for malicious intent, PII leaks, and prompt injections.</p>
            </div>
            <div className="bg-[#111] p-8 rounded-2xl border border-white/5 hover:border-amber-500/30 transition-colors">
              <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center mb-6 border border-amber-500/20">
                <svg className="w-6 h-6 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
              </div>
              <h3 className="text-xl font-bold mb-3">Human-in-the-Loop</h3>
              <p className="text-slate-400 leading-relaxed">Set high-risk tools (like executing payments or dropping databases) to instantly suspend the agent and await human administrator approval.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing / Open Source */}
      <section id="pricing" className="py-24 px-6 relative">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Pricing for Every Scale</h2>
            <p className="text-slate-400">Open source forever for individuals. Enterprise power for teams.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-[#111] border border-white/10 rounded-3xl p-10 relative">
              <h3 className="text-2xl font-bold mb-2">Community</h3>
              <div className="text-4xl font-bold mb-6">Free <span className="text-lg text-slate-500 font-normal">Forever</span></div>
              <p className="text-slate-400 mb-8 h-12">Run the core firewall entirely on your own infrastructure.</p>
              <ul className="space-y-4 mb-10">
                <li className="flex items-center text-slate-300"><svg className="w-5 h-5 text-indigo-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> API Gateway Proxy</li>
                <li className="flex items-center text-slate-300"><svg className="w-5 h-5 text-indigo-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Master Key Authentication</li>
                <li className="flex items-center text-slate-300"><svg className="w-5 h-5 text-indigo-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Basic Telemetry Dashboard</li>
                <li className="flex items-center text-slate-300"><svg className="w-5 h-5 text-indigo-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Prometheus Metrics</li>
              </ul>
              <a href="https://github.com/lokeshsk/zerotrust-agents" className="block w-full py-3 bg-white/5 hover:bg-white/10 text-center rounded-xl font-semibold transition-colors cursor-pointer">Clone Repository</a>
            </div>
            
            <div className="bg-gradient-to-b from-indigo-900/40 to-[#111] border border-indigo-500/30 rounded-3xl p-10 relative shadow-[0_0_40px_rgba(79,70,229,0.1)]">
              <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-indigo-600 text-white px-4 py-1 rounded-full text-sm font-bold tracking-wide">RECOMMENDED</div>
              <h3 className="text-2xl font-bold mb-2">Enterprise</h3>
              <div className="text-4xl font-bold mb-6">Custom</div>
              <p className="text-indigo-200 mb-8 h-12">Advanced controls and scalability for mission-critical AI applications.</p>
              <ul className="space-y-4 mb-10">
                <li className="flex items-center text-white"><svg className="w-5 h-5 text-indigo-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Everything in Community</li>
                <li className="flex items-center text-white"><svg className="w-5 h-5 text-indigo-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Multi-Tenant Workspaces & RBAC</li>
                <li className="flex items-center text-white"><svg className="w-5 h-5 text-indigo-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Active Directory & Auth0 SSO</li>
                <li className="flex items-center text-white"><svg className="w-5 h-5 text-indigo-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Hard Budget & Cost Controls</li>
              </ul>
              <a href="mailto:hello@zerotrust-agents.com?subject=Enterprise%20Inquiry" className="block w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-center rounded-xl font-semibold transition-colors shadow-lg shadow-indigo-500/25 cursor-pointer">Contact Sales</a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-10 text-center text-slate-500">
        <p>© 2026 <a href="https://zerotrust-agents.com" className="hover:text-white transition-colors cursor-pointer">ZeroTrust Agents</a>. Open Core under MIT / Enterprise License.</p>
      </footer>
    </div>
  );
}
