import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Opt @react-pdf/renderer out of server bundle (used in PDF export API route, Phase B-5)
  serverExternalPackages: ['@react-pdf/renderer'],
};

export default nextConfig;
