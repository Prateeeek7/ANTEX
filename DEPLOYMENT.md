# ANTEX Deployment Guide

## Architecture

- **Frontend:** Vercel (React/Vite)
- **Backend:** Render / Railway (FastAPI)
- **Database:** PostgreSQL (Render/Railway managed)

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

If you get `404: NOT_FOUND` when visiting the app or refreshing:

1. **Root Directory:** Vercel → Project Settings → General → **Root Directory**
   - **Recommended:** Set to **empty** (clear the field) so the repo root `vercel.json` is used
   - This uses `buildCommand`, `outputDirectory`, and fallback rewrites
2. **Redeploy:** Deployments → ⋮ → Redeploy
3. Fallback rewrites serve `index.html` for all non-asset routes (e.g. `/projects/1`, `/runs/57`).

### CORS errors

If the frontend can't reach the backend, add `CORS_ORIGINS` on Render with your exact Vercel URL.

## Notes

- **Meep FDTD** is disabled in cloud (`USE_MEEP=false`) due to large dependencies. Analytical models are used.
- Render free tier sleeps after 15 min inactivity; first request may take ~30s to wake.
