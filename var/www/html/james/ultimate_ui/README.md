# Trinity AI Frontend

This directory contains a minimal Next.js 14 application written in TypeScript.
It provides a basic chat interface that communicates with the Flask backend in
`app.py`.

## Development

1. Install dependencies (requires Node.js):
   ```bash
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```

The app expects the Flask API to be running on `http://localhost:5001`.
Set `NEXT_PUBLIC_API_URL` in `.env.local` to point to this base URL so that
`fetch` calls reach the correct backend during development.

This project is configured with `basePath: '/james'` so assets are served under
that URL segment. Update `next.config.js` if deploying elsewhere.

## Production build

Next.js can require a fair amount of memory when compiling. If the build
process fails with an out-of-memory error, run the build with an increased
memory limit:

```bash
NODE_OPTIONS=--max-old-space-size=4096 npm run build
```

This sets the V8 heap to 4&nbsp;GB which prevents the Rust panic observed in
resource constrained environments. After building, start the production server
with:

```bash
npm run start
```
