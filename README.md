# Sample Opal Tools

This repository hosts sample tools using the opal-tools-sdk

## Overview

This project contains multiple sample tools built with the Opal Tools SDK, organized by language:
- **Python**: 7 tools across 2 deployments (lightweight + heavy)
- **TypeScript**: Sample greeting tools
- **.NET**: Sample greeting tools

## Dual Deployment Architecture

To handle tools with different resource requirements, this project uses a **split deployment strategy**:

### Lightweight Tools (Vercel) - `api/index.py`
Fast, serverless deployment for simple tools:
1. **greeting** - Greets a person in a random language
2. **todays-date** - Returns today's date in a specified format
3. **get_weather** - Gets current weather for a location (mock data)
4. **get_google_sheet_rows** - Gets all rows from a Google Sheet
5. **add_google_sheet_row** - Adds a new row to the Google Sheet backlog

**Dependencies**: FastAPI, httpx, pydantic (< 5MB)

### Heavy Tools (Railway/Render) - `api/heavy.py`
Container-based deployment for tools with browser/system dependencies:
6. **analyze_with_lighthouse** - Runs Lighthouse performance analysis on a URL
7. **detect_ab_test** - Detects A/B tests by comparing multiple screenshots

**Dependencies**: Playwright (Chromium browser), Lighthouse CLI, Pillow, NumPy (~300MB)

---

## Deployment Guide

### Option 1: Vercel (Lightweight Tools)

**Deploy to Vercel for the 5 lightweight tools:**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

**What gets deployed:**
- File: `api/index.py`
- Dependencies: `requirements.txt` (lightweight)
- Discovery endpoint: `https://your-app.vercel.app/discovery`

**Configuration:**
- `vercel.json` - Routes all traffic to `api/index.py`
- Auto-detects Python and installs dependencies
- ~5MB deployment size
- 10-60 second timeout (depending on plan)

### Option 2: Railway (Heavy Tools)

**Deploy to Railway for the 2 heavy tools:**

1. **Connect your GitHub repo to Railway:**
   - Go to [railway.app](https://railway.app)
   - Create new project → Deploy from GitHub
   - Select this repository

2. **Railway auto-detects the config:**
   - Reads `railway.toml`
   - Uses `requirements-heavy.txt`
   - Runs `uvicorn api.heavy:app`
   - Discovery endpoint: `https://your-app.railway.app/discovery`

**Alternative: Deploy with Dockerfile**
```bash
# Railway/Render will auto-detect and use the Dockerfile
# No additional configuration needed
```

### Option 3: Render (Heavy Tools)

**Deploy to Render as an alternative to Railway:**

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements-heavy.txt && playwright install chromium`
   - **Start Command**: `uvicorn api.heavy:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Deploy

---

## Testing Your Deployments

### Test Lightweight Tools (Vercel)

```bash
# Discovery endpoint
curl https://your-app.vercel.app/discovery

# Test greeting tool
curl -X POST https://your-app.vercel.app/tools/greeting \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "language": "spanish"}'

# Test date tool
curl -X POST https://your-app.vercel.app/tools/todays-date \
  -H "Content-Type: application/json" \
  -d '{"format": "%B %d, %Y"}'

# Test weather tool
curl -X POST https://your-app.vercel.app/tools/get_weather \
  -H "Content-Type: application/json" \
  -d '{"location": "San Francisco", "units": "imperial"}'
```

### Test Heavy Tools (Railway/Render)

```bash
# Discovery endpoint
curl https://your-app.railway.app/discovery

# Test Lighthouse tool
curl -X POST https://your-app.railway.app/tools/analyze_with_lighthouse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Test A/B test detector
curl -X POST https://your-app.railway.app/tools/detect_ab_test \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "num_captures": 5, "delay_seconds": 2}'
```

---

## Local Development

### Run Lightweight Tools Locally

```bash
# Install dependencies
pip install -r requirements-light.txt

# Run the API
uvicorn api.index:app --reload --port 8000
```

Visit:
- API: http://localhost:8000
- Discovery: http://localhost:8000/discovery
- Docs: http://localhost:8000/docs

### Run Heavy Tools Locally

```bash
# Install dependencies
pip install -r requirements-heavy.txt
npm install -g lighthouse
playwright install chromium

# Run the API
uvicorn api.heavy:app --reload --port 8001
```

Visit:
- API: http://localhost:8001
- Discovery: http://localhost:8001/discovery
- Docs: http://localhost:8001/docs

### Run with Docker (Heavy Tools)

```bash
# Build the image
docker build -t opal-tools-heavy .

# Run the container
docker run -p 8000:8000 opal-tools-heavy
```

---

## Individual Tool Deployment

Each tool in the `python/` directory can also be run independently:

```bash
cd python/greeting
pip install -r requirements.txt  # or use uv/pip with pyproject.toml
python main.py
```

Then access the tool at http://localhost:8000 with its own `/discovery` endpoint.

---

## Project Structure

```
sample-opal-tools/
├── api/
│   ├── index.py              # Lightweight tools (Vercel)
│   └── heavy.py              # Heavy tools (Railway/Render)
├── python/                   # Individual tool services
│   ├── greeting/
│   ├── weather/
│   ├── google_sheets/
│   ├── lighthouse/
│   └── ab_test_detector/
├── typescript/               # TypeScript tools
├── dotnet/                   # .NET tools
├── vercel.json              # Vercel configuration
├── railway.toml             # Railway configuration
├── Dockerfile               # Docker build for heavy tools
├── requirements.txt         # Lightweight dependencies (Vercel)
├── requirements-light.txt   # Same as above
├── requirements-heavy.txt   # Heavy dependencies (Railway/Render)
├── package.json             # Node.js dependencies (Lighthouse)
└── README.md
```

---

## Deployment Comparison

| Feature | Vercel (Lightweight) | Railway/Render (Heavy) |
|---------|---------------------|----------------------|
| **Tools** | 5 lightweight tools | 2 heavy tools |
| **Size** | ~5MB | ~300MB |
| **Dependencies** | Python packages only | Python + Node + Browsers |
| **Cold Start** | <1 second | 3-5 seconds |
| **Timeout** | 10-60 seconds | No limit |
| **Cost** | Free tier available | Free tier available |
| **Best For** | API calls, quick tasks | Browser automation, analysis |

---

## Environment Variables

### Google Sheets Tools
To use the Google Sheets tools, update the `SHEET_URL` in both `api/index.py` and `python/google_sheets/main.py` with your own Google Apps Script endpoint.

**Optional**: Set as environment variable:
```bash
# Vercel
vercel env add SHEET_URL

# Railway
# Add in Railway dashboard → Variables

# Render
# Add in Render dashboard → Environment
```

---

## Why Split Deployments?

**Problem**: Vercel has a 250MB deployment size limit. Tools with Playwright (Chromium browser) and Lighthouse exceed this limit.

**Solution**: Deploy lightweight tools on Vercel's fast serverless platform, and heavy tools on Railway/Render's container platform.

**Benefits**:
- ✅ Lightweight tools get sub-second cold starts on Vercel
- ✅ Heavy tools get unlimited runtime and resources on Railway/Render
- ✅ Both share the same GitHub repository
- ✅ Both have auto-deployment on push
- ✅ Both are free-tier eligible

---

## CI/CD

Both deployments can auto-deploy from the same repository:

1. **Push to GitHub** → Triggers both deployments
2. **Vercel** → Deploys `api/index.py` (lightweight)
3. **Railway/Render** → Deploys `api/heavy.py` (heavy)

**Setup**:
- Vercel: Connect GitHub repo in Vercel dashboard
- Railway: Connect GitHub repo in Railway dashboard
- Both will auto-deploy on every push to `main`

---

## Adding New Tools

### Adding a Lightweight Tool

1. Create tool in `python/your-tool/`
2. Add tool function to `api/index.py`
3. Update `requirements-light.txt` if needed
4. Push to GitHub → Auto-deploys to Vercel

### Adding a Heavy Tool

1. Create tool in `python/your-tool/`
2. Add tool function to `api/heavy.py`
3. Update `requirements-heavy.txt` if needed
4. Update `Dockerfile` if system dependencies needed
5. Push to GitHub → Auto-deploys to Railway/Render

---

## Troubleshooting

### Vercel Deployment Fails

**Error**: "Function exceeds size limit"
- **Cause**: Heavy dependencies in requirements.txt
- **Fix**: Ensure you're using `requirements-light.txt` (copied as `requirements.txt`)

### Railway/Render Deployment Fails

**Error**: "Playwright browser not found"
- **Cause**: Browsers not installed
- **Fix**: Ensure `playwright install chromium` runs in build

**Error**: "Lighthouse command not found"
- **Cause**: Node.js/Lighthouse not installed
- **Fix**: Use the provided Dockerfile which includes Node.js

### Cold Starts Are Slow

- **Vercel**: Lightweight tools should start in <1s
- **Railway/Render**: Heavy tools may take 3-5s on first request (browser initialization)
- **Solution**: Use Railway's "always on" feature or implement health check pinging

---

## Contributing

Feel free to add more sample tools! Follow the existing pattern and update this README.

## License

See individual tool directories for license information.
