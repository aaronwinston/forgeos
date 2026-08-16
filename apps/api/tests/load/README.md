# Performance Testing Guide

This document outlines the performance testing strategy for ForgeOS, including load testing and profiling.

## Load Testing with k6

### Installation

```bash
brew install k6
```

Or download from: https://k6.io/docs/get-started/installation/

### Running Load Tests

All load test scripts are in `apps/api/tests/load/`.

#### 1. Auth Flow Test (Signup/Signin)

Ramps up to 100 concurrent users testing signup and login endpoints.

```bash
# Start the API
cd apps/api
uvicorn main:app --reload

# In another terminal, run the test
cd tests/load
k6 run auth_flow.js
```

**Expected Results:**
- p95 latency < 750ms
- Error rate < 1%
- Peak: 100 concurrent users

**Key Metrics:**
- `http_req_duration{test:signin}` - Login endpoint latency
- `http_req_duration{test:profile}` - Profile fetch latency

#### 2. Project Operations Test

Ramps up to 500 concurrent requests testing CRUD operations on projects.

```bash
k6 run project_operations.js
```

**Expected Results:**
- p95 latency < 750ms
- Throughput: 50+ requests/sec
- Error rate < 1%

**Endpoints Tested:**
- POST /api/projects (create)
- GET /api/projects (list)
- GET /api/projects/{id} (read)
- PUT /api/projects/{id} (update)
- DELETE /api/projects/{id} (delete)

#### 3. Chat Operations Test

Ramps up to 1000 concurrent messages simulating real-time chat.

```bash
k6 run chat_operations.js
```

**Expected Results:**
- p95 latency < 750ms
- Can handle 1000 concurrent chat sessions
- Error rate < 1%

**Endpoints Tested:**
- POST /api/chat/sessions/{id}/messages (send message)
- GET /api/chat/sessions/{id}/messages (list messages)
- GET /api/chat/sessions/{id} (get session)

#### 4. Dashboard Loading Test

Tests parallel loading of multiple dashboard endpoints.

```bash
k6 run dashboard_loading.js
```

**Expected Results:**
- Dashboard load time < 2.5s (all endpoints in parallel)
- p95 latency < 600ms per endpoint
- No cascading failures

**Endpoints Tested:**
- GET /api/dashboard
- GET /api/projects
- GET /api/chat/sessions
- GET /api/settings
- GET /api/usage

### Running All Tests with Custom Configuration

```bash
# Set custom base URL
BASE_URL=https://api.forgeos.dev k6 run auth_flow.js

# Set test token
TEST_TOKEN=$(cat /path/to/test/token) k6 run project_operations.js

# View results in real-time
k6 run auth_flow.js --out json=results.json
```

### Output Formats

```bash
# JSON output
k6 run auth_flow.js --out json=results.json

# CSV output (requires k6 extension)
k6 run auth_flow.js -o json=results.json

# HTML report (post-process)
npm install -g @grafana/k6-reporter
k6 run auth_flow.js --out json=results.json
k6-reporter results.json
```

### Interpreting Results

**Response Time Metrics:**
- **p50 (median):** 50th percentile - typical response time
- **p95:** 95th percentile - acceptable threshold for most users
- **p99:** 99th percentile - edge cases, slowest requests

**Threshold Examples:**
```
p(50) < 200ms   # Good
p(95) < 500ms   # Acceptable
p(99) < 1000ms  # Maximum acceptable
```

**Error Rate:**
- < 0.1% = Excellent
- < 1% = Acceptable
- > 1% = Performance issue

## Performance Profiling

### CPU Profiling with cProfile

Profile slow endpoints to identify bottlenecks.

```bash
cd apps/api
python3 -m cProfile -o profile_output.prof -m pytest tests/test_security.py::TestAuthenticationJWT
```

### Memory Profiling

```bash
pip3 install memory-profiler
python3 -m memory_profiler main.py
```

### Database Query Analysis

Enable slow query logging in FastAPI:

```python
# In main.py
from middleware.request_logging import RequestLoggingMiddleware

# This middleware logs all requests with response times
app.add_middleware(RequestLoggingMiddleware)
```

Check logs for queries taking > 100ms:
```bash
grep "duration_ms>100" logs/api.log
```

## Performance Optimization Checklist

- [ ] Database indexes created for frequently queried columns
- [ ] Queries analyzed and optimized (see docs/archive/implementation/IMPROVEMENT_PLAN.md P4.1)
- [ ] Response caching implemented (redis)
- [ ] API pagination implemented (limit/offset)
- [ ] Images optimized (compression, CDN)
- [ ] Frontend bundle split and lazy-loaded
- [ ] Service Worker for offline support
- [ ] Lighthouse score > 80

## Frontend Performance (Lighthouse)

### Installation

```bash
npm install -g lighthouse
# or
npm install -D lighthouse
```

### Running Lighthouse

```bash
cd apps/web

# Local testing
lighthouse http://localhost:3000/dashboard --output-path=report.html

# Production URL
lighthouse https://app.forgeos.dev/dashboard --output-path=report.html
```

### Target Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Performance Score | > 80 | TBD |
| LCP (Largest Contentful Paint) | < 2.5s | TBD |
| FID (First Input Delay) | < 100ms | TBD |
| CLS (Cumulative Layout Shift) | < 0.1 | TBD |
| TTB (Time to Boot) | < 3s | TBD |

### Performance Optimizations

1. **Code Splitting:**
   ```javascript
   // Use dynamic imports
   const Dashboard = lazy(() => import('./pages/Dashboard'));
   ```

2. **Image Optimization:**
   ```javascript
   // Use next/image component
   import Image from 'next/image';
   <Image src="/photo.jpg" width={400} height={300} />
   ```

3. **Service Worker:**
   ```bash
   npm install -D next-pwa
   ```

## Continuous Monitoring

### Production Metrics to Track

1. **API Latency:**
   - p50, p95, p99 response times
   - Error rates
   - Request throughput

2. **Database Performance:**
   - Query execution time
   - Slow queries (> 100ms)
   - Connection pool usage

3. **Frontend Performance:**
   - Page load time
   - Time to interactive (TTI)
   - Lighthouse scores

4. **Resource Usage:**
   - CPU usage
   - Memory usage
   - Disk I/O

### Monitoring Tools

- **APM:** Arize AX (already integrated)
- **Logs:** CloudWatch / ELK Stack
- **Metrics:** Prometheus / Grafana
- **Frontend:** Web Vitals, Sentry

## Performance Regression Prevention

Every PR should:

1. Run load tests against new endpoints
2. Compare metrics to baseline
3. Alert if > 10% regression
4. Require performance approval for high-impact changes

## Related Documentation

- **Query Optimization:** [IMPROVEMENT_PLAN.md P4.1](../../../../docs/archive/implementation/IMPROVEMENT_PLAN.md#p41-database-query-optimization)
- **Caching Strategy:** [CELERY_QUICKSTART.md](./CELERY_QUICKSTART.md)
- **Monitoring Setup:** [README.md](./README.md)
- **Security Testing:** [SECURITY.md](../../../../SECURITY.md)
