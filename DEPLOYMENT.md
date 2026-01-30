# ANTEX Deployment Guide

## Architecture

- **Frontend:** Vercel (React/Vite)
- **Backend:** Render / Railway (FastAPI)
- **Database:** PostgreSQL (Render/Railway managed)

---

## Fresh Vercel Deploy (e.g. after deleting project)

To redeploy from scratch and keep `antexantennadesigner.vercel.app`:

1. **Delete** the existing project: Vercel Dashboard → Project Settings → General → scroll down → **Delete Project**.

2. **Create new project:** [vercel.com/new](https://vercel.com/new) → **Import** your `Prateeeek7/ANTEX` repo.

3. **Configure (important):**
   - **Project Name:** `antexantennadesigner` (so you get antexantennadesigner.vercel.app)
   - **Root Directory:** Leave **empty** (do not set `frontend`)
   - **Framework Preset:** Other
   - **Build Command:** (leave default – uses `vercel.json`)
   - **Output Directory:** (leave default – uses `vercel.json`)

4. **Environment Variables:**
   - `VITE_API_URL` = `https://antex-backend.onrender.com`

5. Click **Deploy**.

6. **Custom domain (if needed):** Project Settings → Domains → add `antexantennadesigner.vercel.app` if it doesn’t appear automatically.

---

## 1. Deploy Backend (Render)

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. **New** → **Blueprint** → Connect your ANTEX repo.
3. Or create manually:
   - **New** → **Web Service** → Connect repo
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

4. **Add PostgreSQL:**
   - **New** → **PostgreSQL**
   - Copy the **Internal Database URL**

5. **Environment Variables:**
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | (from PostgreSQL - Internal URL) |
   | `JWT_SECRET` | (generate a random string) |
   | `CORS_ORIGINS` | `https://your-app.vercel.app` |
   | `USE_MEEP` | `false` |

6. Deploy. Note the backend URL (e.g. `https://antex-backend.onrender.com`).

## 2. Deploy Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) → **Add New** → **Project** → Import ANTEX repo.
2. **Root Directory:** `frontend`
3. **Framework Preset:** Vite (auto-detected)
4. **Environment Variables:**
   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://your-backend.onrender.com` |

5. Deploy.

## 3. Update CORS

In Render dashboard → antex-backend → Environment:
- Set `CORS_ORIGINS` to your exact Vercel URL, e.g. `https://antexantennadesigner-xxx.vercel.app`
- Redeploy if needed.

## Quick Deploy (Railway)

Alternative to Render:

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Add **PostgreSQL** from Railway templates
3. Add **Web Service** → Connect backend, set:
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Root: `backend`
4. Link `DATABASE_URL` from PostgreSQL
5. Add `VITE_API_URL` to your Vercel frontend pointing to Railway URL

## Troubleshooting

### 404 on Vercel (SPA routes)

If you get `404: NOT_FOUND` on `/` or when visiting the app:

1. **Root Directory:** Vercel → Project Settings → General → **Root Directory**
   - **Must be empty** (clear the field completely)
   - If set to `frontend`, the root `package.json` and `vercel.json` won't be used
   - With root empty, the build uses `package.json` (build script) and `vercel.json` (output: `frontend/dist`)
2. **Framework Preset:** Set to **Other** (or leave default) – don't force Vite
3. **Redeploy:** Deployments → ⋮ → Redeploy (do this after changing Root Directory)
4. Check the build logs – the build should run `npm run build` and produce `frontend/dist`.

### CORS errors

If the frontend can't reach the backend, add `CORS_ORIGINS` on Render with your exact Vercel URL.

## Notes

- **Meep FDTD** is disabled in cloud (`USE_MEEP=false`) due to large dependencies. Analytical models are used.
- Render free tier sleeps after 15 min inactivity; first request may take ~30s to wake.
