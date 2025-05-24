/** @type {import('next').NextConfig} */
const nextConfig = {
  // Serve the UI under the `/james` base path so it can be hosted at
  // https://325automations.com/james.
  basePath: '/james',
  // The `app` directory is stable in Next.js 14 so no experimental flag is
  // required. Removing `experimental.appDir` avoids a config validation error
  // during `next build`.
};

module.exports = nextConfig;
