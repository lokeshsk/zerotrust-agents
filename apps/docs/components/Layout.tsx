import React from "react";
import Link from "next/link";
import { useRouter } from "next/router";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const currentPath = router.pathname;

  const menuItems = [
    { name: "Introduction", path: "/" },
    { name: "Quickstart", path: "/quickstart" },
    { name: "Architecture", path: "/architecture" },
    { name: "Supported Proxies", path: "/proxies" },
    { name: "MCP Integration", path: "/mcp" },
    { name: "Enterprise Features", path: "/enterprise" },
  ];

  return (
    <div className="min-h-screen bg-black text-slate-100 font-sans selection:bg-indigo-500/30">
      {/* Background lights */}
      <div className="absolute top-0 left-1/4 w-[600px] h-[300px] bg-indigo-500/5 blur-[120px] rounded-full pointer-events-none z-0"></div>
      <div className="absolute top-1/2 right-1/4 w-[500px] h-[250px] bg-purple-500/5 blur-[120px] rounded-full pointer-events-none z-0"></div>

      {/* Header */}
      <header className="border-b border-white/10 bg-black/60 backdrop-blur-md sticky top-0 z-40 w-full">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <span className="font-bold text-lg tracking-tight text-white">
                ZeroTrust<span className="text-indigo-400">Agents</span>
              </span>
            </Link>
            <span className="text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded font-mono">
              docs
            </span>
          </div>

          <div className="flex items-center space-x-6 text-sm font-medium text-slate-300">
            <a href="http://localhost:3000" className="hover:text-white transition-colors">
              App Console
            </a>
            <a href="https://github.com/lokeshsk/zerotrust-agents" target="_blank" rel="noreferrer" className="hover:text-white transition-colors flex items-center space-x-1.5">
              <span>GitHub</span>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <div className="max-w-7xl mx-auto px-6 flex relative z-10">
        {/* Sidebar */}
        <aside className="w-64 shrink-0 hidden md:block border-r border-white/5 pr-6 py-10 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto">
          <nav className="space-y-1">
            <span className="block text-xs font-semibold text-slate-500 uppercase tracking-wider px-3 mb-3">
              Documentation
            </span>
            {menuItems.map((item) => {
              const isActive = currentPath === item.path;
              return (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`w-full flex items-center px-3 py-2 rounded-lg font-medium text-sm transition-all ${
                    isActive
                      ? "bg-white/10 text-white shadow-inner border border-white/5"
                      : "text-slate-400 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Content Area */}
        <main className="flex-1 min-w-0 py-10 pl-0 md:pl-10">
          <article className="prose prose-invert max-w-3xl prose-indigo prose-headings:font-bold prose-headings:tracking-tight prose-a:text-indigo-400 hover:prose-a:text-indigo-300">
            {children}
          </article>
        </main>
      </div>
    </div>
  );
}
