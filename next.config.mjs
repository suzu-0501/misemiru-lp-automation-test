/** @type {import('next').NextConfig} */
const isGitHubPages = process.env.GITHUB_PAGES === "true";

const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  devIndicators: false,
  basePath: isGitHubPages ? "/misemiru-lp-automation-test" : "",
};

export default nextConfig;
