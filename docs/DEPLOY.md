# Deploying to Render (free tier)

This repo deploys as 3 independent Docker web services via the Render
Blueprint (`render.yaml` at the repo root).

## 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## 2. Create the Blueprint on Render

1. Go to the Render dashboard -> **New** -> **Blueprint**
2. Connect your GitHub account and select this repo
3. Render reads `render.yaml` and proposes 3 services:
   `glucose-ml-service`, `glucose-backend`, `glucose-frontend`
4. Click **Apply** -- it builds and deploys all three (first build takes a
   few minutes per service; ml-service is a plain Python image, backend
   builds a Maven multi-stage image, frontend builds Angular + nginx)

## 3. Fill in the two manual environment variables

`render.yaml` deliberately leaves 2 env vars unset (`sync: false`) because
their values depend on the public URLs Render assigns, which you only know
*after* the services exist:

1. Once `glucose-ml-service` is deployed, copy its URL (e.g.
   `https://glucose-ml-service.onrender.com`)
2. On `glucose-backend` -> Environment, set:
   `ML_SERVICE_URL = https://glucose-ml-service.onrender.com`
3. Once `glucose-backend` is deployed, copy its URL (e.g.
   `https://glucose-backend.onrender.com`)
4. On `glucose-frontend` -> Environment, set:
   `API_BASE_URL = https://glucose-backend.onrender.com/api`
5. Redeploy `glucose-backend` and `glucose-frontend` (Render redeploys
   automatically on env var changes, but trigger a manual deploy if it
   doesn't)

## 4. Verify

- `https://glucose-ml-service.onrender.com/health` -> `{"status":"ok"}`
- `https://glucose-backend.onrender.com/api/series` -> list of demo patients
- `https://glucose-frontend.onrender.com` -> the dashboard, loading real
  data and predictions

## Known limitations of the free tier

- Each service spins down after 15 minutes of inactivity; the next request
  triggers a ~30-60s cold start while it wakes up. Don't be alarmed if the
  demo looks "down" after being idle -- just reload after a moment.
- 750 free instance-hours/month shared across the account. Fine for a
  portfolio demo visited occasionally; would need a paid plan for
  always-on production use.
- The filesystem is ephemeral, but this app never writes to disk at
  runtime, so that's a non-issue here.

## Updating the demo dataset or model

`data/demo/*.csv` and `ml-service/app/models/*.onnx` are committed to the
repo and baked into their respective images at build time. To ship a
retrained model or a different demo subset, just commit the new files and
push -- Render rebuilds automatically.
