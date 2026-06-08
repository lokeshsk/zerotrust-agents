"use client";

import React from 'react';
import Link from 'next/link';

export default function EnterprisePricing() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-black text-slate-900 dark:text-white font-sans selection:bg-indigo-500/30">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-100/40 via-slate-50 to-slate-50 dark:from-indigo-900/20 dark:via-black dark:to-black z-0 pointer-events-none"></div>
      
      <div className="relative z-10 max-w-6xl mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <Link href="/" className="inline-flex items-center text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 mb-8 transition-colors">
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
            Back to Dashboard
          </Link>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4">Scale Your AI Security</h1>
          <p className="text-lg text-slate-500 dark:text-slate-400 max-w-2xl mx-auto">
            Upgrade to ZeroTrust Agents Enterprise Edition to unlock SSO, Role-Based Access Control, and multi-tenant capabilities for your AI workforce.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {/* Open Source Tier */}
          <div className="bg-white dark:bg-[#111] rounded-3xl p-8 border border-slate-200 dark:border-white/10 shadow-sm relative flex flex-col">
            <h3 className="text-xl font-bold mb-2">Open Core</h3>
            <p className="text-slate-500 dark:text-slate-400 text-sm mb-6 h-10">For indie hackers and small startups experimenting with AI.</p>
            <div className="text-4xl font-extrabold mb-6">$0<span className="text-lg text-slate-500 font-medium">/mo</span></div>
            <ul className="space-y-4 mb-8 flex-1">
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-emerald-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Unlimited Local Traffic</li>
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-emerald-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Master Key Authentication</li>
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-emerald-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Basic Policy Engine</li>
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-emerald-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Community Support</li>
            </ul>
            <Link href="/" className="w-full py-3 px-4 bg-slate-100 dark:bg-white/5 text-slate-900 dark:text-white font-semibold rounded-xl text-center hover:bg-slate-200 dark:hover:bg-white/10 transition-colors">
              Current Plan
            </Link>
          </div>

          {/* Startup Tier */}
          <div className="bg-white dark:bg-[#111] rounded-3xl p-8 border-2 border-indigo-500 shadow-xl dark:shadow-[0_0_30px_rgba(99,102,241,0.15)] relative flex flex-col transform md:-translate-y-4">
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-indigo-500 text-white px-4 py-1 rounded-full text-xs font-bold uppercase tracking-wider">Most Popular</div>
            <h3 className="text-xl font-bold mb-2">Startup</h3>
            <p className="text-slate-500 dark:text-slate-400 text-sm mb-6 h-10">For teams deploying AI agents in production environments.</p>
            <div className="text-4xl font-extrabold mb-6">$199<span className="text-lg text-slate-500 font-medium">/mo</span></div>
            <ul className="space-y-4 mb-8 flex-1">
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-indigo-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Up to 50 Active AI Agents</li>
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-indigo-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Auto-Discovery Graph</li>
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-indigo-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>30-Day Audit Retention</li>
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-indigo-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Email Support</li>
            </ul>
            <button className="w-full py-3 px-4 bg-indigo-600 text-white font-semibold rounded-xl text-center hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-500/25">
              Start 14-Day Trial
            </button>
          </div>

          {/* Enterprise Tier */}
          <div className="bg-slate-900 dark:bg-black rounded-3xl p-8 border border-slate-800 dark:border-white/10 shadow-sm relative flex flex-col text-white">
            <h3 className="text-xl font-bold mb-2">Enterprise</h3>
            <p className="text-slate-400 text-sm mb-6 h-10">Mission-critical security for enterprise scale AI workflows.</p>
            <div className="text-4xl font-extrabold mb-2">$2,500<span className="text-lg text-slate-500 font-medium">/mo</span></div>
            <p className="text-indigo-400 text-xs font-semibold mb-6 uppercase tracking-wider">Base Platform Fee</p>
            <ul className="space-y-4 mb-8 flex-1">
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-emerald-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Includes 100,000 Events/mo</li>
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-emerald-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>+$10 per 10k additional events</li>
              <li className="flex items-center text-sm font-semibold text-indigo-300"><svg className="w-5 h-5 text-indigo-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>SSO (Auth0, Okta, SAML)</li>
              <li className="flex items-center text-sm font-semibold text-indigo-300"><svg className="w-5 h-5 text-indigo-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>Advanced RBAC & Multi-Tenant</li>
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-emerald-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>SIEM Export (Datadog/Splunk)</li>
              <li className="flex items-center text-sm"><svg className="w-5 h-5 text-emerald-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>24/7 Dedicated SLA Support</li>
            </ul>
            <button className="w-full py-3 px-4 bg-white text-black font-semibold rounded-xl text-center hover:bg-slate-200 transition-colors">
              Contact Sales
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
