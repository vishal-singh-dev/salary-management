import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    PUBLIC_API_BASE_URL: process.env.PUBLIC_API_BASE_URL,
  },
  reactStrictMode: true,
};

export default nextConfig;
