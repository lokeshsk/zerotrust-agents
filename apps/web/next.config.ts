import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone", // Required for Docker multi-stage builds
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `http://api:8001/:path*`, // Proxy to Backend
      },
    ];
  },
};

export default nextConfig;
