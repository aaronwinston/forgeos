# Vercel deployment steps (ForgeOS)

## 1. Link project

```bash
cd /Users/aaronwinston/forgeos
vercel login
vercel link
```

When configuring in Vercel UI/CLI, set:
- Root Directory: `apps/web`
- Framework: Next.js
- Install Command: `npm ci`
- Build Command: `npm run build`

## 2. Set environment variables

```bash
vercel env add NEXT_PUBLIC_API_BASE_URL production
vercel env add NEXT_PUBLIC_API_BASE_URL preview
```

Use your API host(s), for example:
- Production: `https://api.yourdomain.com`
- Preview: `https://api-preview.yourdomain.com`

## 3. Deploy

```bash
vercel deploy --prod
```

## 4. Verify runtime wiring

1. Open deployed URL and verify pages render.
2. Confirm API requests target `NEXT_PUBLIC_API_BASE_URL`.
3. Confirm backend CORS includes deployed frontend origin(s).

## 5. If deployment fails

Check:
1. Vercel project root directory is `apps/web` (not repo root).
2. `apps/web/vercel.json` is present in the deployed commit.
3. `apps/web/next.config.mjs` is dynamic runtime mode (no `output: 'export'`).
4. Backend `CORS_ALLOWED_ORIGINS` contains your Vercel domain.
