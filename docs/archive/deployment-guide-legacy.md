# ForgeOS Deployment Guide

## Current Status
- All code changes committed to `main` branch ✅
- All tests passing ✅
- Production-ready (8-9/10 readiness) ✅

## Frontend Deployment (GitHub Pages)

The repository is configured with automated GitHub Pages deployment via `.github/workflows/deploy.yml`.

**Current configuration:**
- Builds Next.js app as static export
- Deploys to GitHub Pages on push to `main` branch
- URL: https://aaronwinston.github.io/forgeos/

**To manually trigger:**
```bash
gh workflow run deploy.yml --ref main
```

## Backend Deployment Options

### Option 1: Docker Compose (Local/Self-Hosted)
```bash
cd /Users/aaronwinston/forgeos
docker-compose up -d
```

Services:
- Redis (localhost:6379)
- Celery Worker (background jobs)
- Celery Beat (scheduling)
- Flower (monitoring at localhost:5555)
- API (requires separate FastAPI server setup)

### Option 2: Railway / Render / Fly.io (Recommended for SaaS)
1. Connect GitHub repository
2. Configure environment variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `REDIS_URL`: Redis connection string
   - `SENTRY_DSN`: Sentry error tracking
   - `JWT_SECRET_KEY`: Secure random string
   - `CORS_ALLOWED_ORIGINS`: Production domains
   - etc. (see `.env.example`)
3. Deploy API and Celery workers as separate services

### Option 3: AWS / GCP / Azure (Enterprise)
1. Create EC2/VM instances
2. Configure RDS/Cloud SQL for PostgreSQL
3. Configure Elasticache/Memorystore for Redis
4. Deploy with Docker or native Python
5. Configure CloudWatch/Stackdriver for monitoring
6. Set up auto-scaling groups

## Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database migrations run: `alembic upgrade head`
- [ ] Redis available and accessible
- [ ] Sentry DSN configured for error tracking
- [ ] CORS origins configured for production domain
- [ ] JWT_SECRET_KEY set to secure random value
- [ ] SSL/TLS certificate installed
- [ ] Backups configured
- [ ] Monitoring and alerting configured
- [ ] Load testing completed (k6 results baseline)

## Post-Deployment Verification

```bash
# Check API health
curl https://your-domain.com/api/health

# Check Sentry events
# Log in to Sentry dashboard, verify events appearing

# Run smoke tests
k6 run apps/api/tests/load/auth_flow.js --vus 10 --duration 60s

# Verify database migrations
SELECT * FROM alembic_version;

# Check Celery workers
celery -A celery_app inspect active
```

## Security Checklist (Pre-Production)

- [ ] All Phase 1 security fixes applied ✅
- [ ] CSRF tokens validated ✅
- [ ] Rate limiting active ✅
- [ ] CSP headers configured ✅
- [ ] CORS properly restricted ✅
- [ ] Secrets not in git ✅
- [ ] OWASP Top 10 assessment complete ✅
- [ ] Penetration testing completed ✅

## Monitoring & Alerting

**Sentry (Error Tracking)**
- Set up teams and alerts
- Alert on errors > 5% of requests
- Alert on new error types

**Application Metrics (OpenTelemetry)**
- Latency: p50 < 100ms, p95 < 500ms, p99 < 1000ms
- Error rate: < 1%
- Throughput: baseline from k6 tests
- Database query time: < 100ms (90th percentile)

**Infrastructure**
- Redis memory usage < 80%
- Database connection pool utilization < 80%
- Celery worker queue depth < 100
- Disk usage < 80%

## Rollback Procedure

```bash
# If deployment has critical issues:
git revert <commit-hash>
git push origin main
# Redeploy from updated main branch
```

## Next Steps

1. **Choose deployment platform** (Railway, Render, self-hosted, etc.)
2. **Configure production database** (PostgreSQL recommended, not SQLite)
3. **Set up monitoring** (Sentry, DataDog, New Relic, etc.)
4. **Run load tests** against production to baseline
5. **Configure alerting** for errors, latency, resource usage
6. **Document runbooks** for common operational tasks

## Support

For deployment issues, check:
- `IMPROVEMENT_PLAN.md` - Phase 4 sections for detailed technical info
- `SECURITY.md` - Security configuration and best practices
- `apps/api/TESTING.md` - Test execution procedures
- `apps/api/README.md` - Database, Celery, and monitoring setup

