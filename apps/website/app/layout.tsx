import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

const BASE_URL = "https://zerotrust-agents.com";

export const metadata: Metadata = {
  metadataBase: new URL(BASE_URL),
  title: "ZeroTrust Agents | The Security Layer for Autonomous AI",
  description: "Intercept, analyze, and block rogue AI tool executions in real-time. Protect your databases, APIs, and infrastructure from hallucinating LLMs with the open-source Zero-Trust firewall for AI agents.",
  keywords: ["AI security", "zero trust", "LLM firewall", "agent security", "AI agents", "open source"],
  authors: [{ name: "ZeroTrust Agents", url: BASE_URL }],
  openGraph: {
    title: "ZeroTrust Agents | The Security Layer for Autonomous AI",
    description: "Intercept, analyze, and block rogue AI tool executions in real-time.",
    url: BASE_URL,
    siteName: "ZeroTrust Agents",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "ZeroTrust Agents | The Security Layer for Autonomous AI",
    description: "Intercept, analyze, and block rogue AI tool executions in real-time.",
  },
  alternates: {
    canonical: BASE_URL,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-black text-white">{children}</body>
    </html>
  );
}
