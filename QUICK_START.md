# Quick Start Guide - AI Antenna Designer

## 🚀 Get Started in 3 Steps

### Step 1: Start Backend
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Start Frontend
```bash
cd frontend
npm run dev
```

### Step 3: Open Browser
```
http://localhost:5173
```

That's it! No login required (development mode).

## 📝 Basic Usage

1. **Create a Project**
   - Click "New Project"
   - Fill in antenna specs (frequency, bandwidth, size, substrate)
   - Click "Create Project"

2. **Start Optimization**
   - Go to project detail page
   - Use "Overview" tab
   - Configure optimization settings
   - Click "Start Optimization"

3. **View Results**
   - **Runs tab**: See all optimization runs
   - **Candidates tab**: Browse design candidates
   - **Simulation tab**: Run openEMS FDTD or upload files

## ⚡ Enable openEMS (Optional)

For CST/HFSS-grade simulations:

1. **Install openEMS:**
   ```bash
   # macOS
   brew install openems
   
   # Or download from: https://github.com/thliebig/openEMS/releases
   ```

2. **Enable in backend `.env`:**
   ```env
   USE_OPENEMS=true
   ```

3. **Restart backend**

4. **Check status:**
   - Go to project → Simulation tab
   - See openEMS status indicator

## 📚 Next Steps

- Read `README.md` for detailed setup
- Check `OPENEMS_INTEGRATION.md` for openEMS setup
- See `FEATURES.md` for complete feature list
- Visit `http://localhost:8000/docs` for API documentation

Happy designing! 🎯




