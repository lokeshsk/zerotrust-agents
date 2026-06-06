const DOCS_URL = process.env.DOCS_URL || 'http://localhost:3001';

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/docs',
        destination: `${DOCS_URL}/docs`,
      },
      {
        source: '/docs/:path*',
        destination: `${DOCS_URL}/docs/:path*`,
      },
    ];
  },
};

export default nextConfig;
