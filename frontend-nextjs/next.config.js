/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  async rewrites() {
    return {
      beforeFiles: [
        // Proxy API calls to backend while in development
        {
          source: '/api/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/:path*`,
        },
      ],
    };
  },
};

module.exports = nextConfig;
