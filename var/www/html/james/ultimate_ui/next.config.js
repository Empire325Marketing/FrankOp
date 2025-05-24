/** @type {import('next').NextConfig} */
const nextConfig = {
  // Use /james when the app is served from that subdirectory.
  basePath: '/james',
  // The `app` directory is stable in Next.js 14 so no experimental flag is
  // required. Removing `experimental.appDir` avoids a config validation error
  // during `next build`.
};

module.exports = nextConfig;
