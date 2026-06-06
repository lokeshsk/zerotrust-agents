import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent Firewall | Zero-Trust AI Security",
  description: "The definitive security and observability control plane for Autonomous AI Agents.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-black text-white">{children}</body>
    </html>
  );
}
