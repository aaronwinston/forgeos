# Vercel Deployment - Manual Steps

Since VERCEL_TOKEN is not set, follow these steps to deploy ForgeOS to Vercel:

## Step 1: Authenticate with Vercel

```bash
cd /Users/aaronwinston/forgeos
vercel login
```

When prompted:
- Choose authentication method (GitHub recommended)
- Authorize Vercel to access your GitHub account
- You'll be authenticated automatically

## Step 2: Link Project

```bash
vercel link
```

When prompted:
- **Set up and deploy "~/forgeos"?** → Yes (y)
- **Which scope should contain your project?** → Your GitHub username
- **Link to existing project?** → No (n)
- **What's your project's name?** → forgeos
- **In which directory is your code located?** → ./ (root)
- **Want to override the settings?** → No (n) - uses vercel.json

This creates `.vercel/project.json` with your project configuration.

## Step 3: Set Environment Variables

```bash
vercel env add NEXT_PUBLIC_API_BASE_URL
```

When prompted:
- **Enter value:** https://api.yourdomain.com (for production)
- **Select environments:** Production
- Repeat for Preview and Development if needed:
  - Preview: https://staging-api.yourdomain.com (or your preview backend)
  - Development: http://localhost:8000 (for local development)

## Step 4: Deploy to Production

```bash
vercel deploy --prod
```

This will:
1. Install dependencies
2. Build the Next.js application
3. Run security checks
4. Deploy to Vercel edge network
5. Provide you with:
   - Production URL: https://forgeos.vercel.app (or your custom domain)
   - Preview URL for branches

## Step 5: Configure Custom Domain (Optional)

```bash
vercel domains add yourdomain.com
```

Then:
1. Update DNS records (Vercel provides instructions)
2. Vercel auto-provisions SSL certificate
3. Custom domain is live in 1-2 minutes

## Step 6: Configure GitHub Integration (Optional)

1. Go to https://vercel.com/dashboard
2. Select your forgeos project
3. Go to Settings → Git Integration
4. Connect your GitHub repo if not already connected
5. Auto-deploy on push to main branch is now enabled

## Alternative: One-Command Deployment

If you have VERCEL_TOKEN set:

```bash
export VERCEL_TOKEN=your_token_here
vercel deploy --prod --token=$VERCEL_TOKEN
```

## Verification

After deployment:

1. **Check Vercel dashboard:** https://vercel.com/dashboard
2. **Visit your deployment:** https://forgeos.vercel.app (or custom domain)
3. **Check logs:** `vercel logs`
4. **Test API connectivity:** Ensure backend is running and accessible

## Troubleshooting

### Build fails
```bash
vercel logs --follow
```
Check logs for errors and fix locally before redeploying.

### API connection fails
- Verify `NEXT_PUBLIC_API_BASE_URL` is set correctly
- Ensure backend is running at that URL
- Check CORS configuration on backend

### Domain not working
- Verify DNS records are updated
- Wait up to 2 minutes for propagation
- Check Vercel dashboard for certificate status

---

**Next:** Follow the steps above to deploy to Vercel!
