# ForgeOS Vercel deployment guide

This project should deploy to Vercel from **`apps/web`** using a dynamic Next.js runtime.

## Canonical deployment settings

Configure these in Vercel project settings:

1. **Framework:** Next.js
2. **Root Directory:** `apps/web`
3. **Install Command:** `npm ci`
4. **Build Command:** `npm run build`

`apps/web/vercel.json` is the canonical Vercel config file.

## Required environment variables

Set these in Vercel:

1. **Production**
   - `NEXT_PUBLIC_API_BASE_URL=https://<your-production-api-host>`
2. **Preview**
   - `NEXT_PUBLIC_API_BASE_URL=https://<your-preview-api-host>` (or same production API if intentional)

## Backend CORS requirement

Backend must include deployed frontend origins in `CORS_ALLOWED_ORIGINS`:

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,https://forgeos.vercel.app
```

Add your preview domain(s) if preview deployments call the API directly.

## Deployment verification checklist

After deploying preview or production:

1. App loads at Vercel URL.
2. Browser network calls point to `NEXT_PUBLIC_API_BASE_URL`.
3. `GET <API>/api/health` succeeds.
4. Dashboard, Intelligence, Search, Settings render without API/CORS errors.

## Known source of breakage (fixed)

Previous config mixed static export assumptions with dynamic routes (`/workspace/[deliverableId]`).  
Vercel deploys should run in dynamic mode from `apps/web` only.
