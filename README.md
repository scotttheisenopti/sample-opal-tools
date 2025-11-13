# Sample Opal Tools

This repository hosts sample tools using the opal-tools-sdk

## Overview

This project contains multiple sample tools built with the Opal Tools SDK, organized by language:
- **Python**: 7 tools across 5 services (greeting, weather, google_sheets, lighthouse, ab_test_detector)
- **TypeScript**: Sample greeting tools
- **.NET**: Sample greeting tools

## Unified API (Vercel Deployment)

The unified API combines all Python tools into a single FastAPI application that can be deployed to Vercel as a serverless function.

### Available Tools

1. **greeting** - Greets a person in a random language (English, Spanish, or French)
2. **todays-date** - Returns today's date in a specified format
3. **get_weather** - Gets current weather for a location (mock data)
4. **get_google_sheet_rows** - Gets all rows from a Google Sheet
5. **add_google_sheet_row** - Adds a new row to the Google Sheet backlog
6. **analyze_with_lighthouse** - Runs Lighthouse performance analysis on a URL
7. **detect_ab_test** - Detects A/B tests by comparing multiple screenshots of a URL

### Deployment to Vercel

#### Prerequisites

- [Vercel CLI](https://vercel.com/docs/cli) installed (`npm i -g vercel`)
- Vercel account (free or Pro recommended for longer function timeouts)
- Git repository connected to Vercel (optional, can deploy via CLI)

#### Quick Deploy

1. **Clone and navigate to the repository:**
   ```bash
   cd sample-opal-tools
   ```

2. **Install Vercel CLI (if not already installed):**
   ```bash
   npm i -g vercel
   ```

3. **Deploy to Vercel:**
   ```bash
   vercel
   ```

   Follow the prompts to link to your Vercel account and configure the project.

4. **For production deployment:**
   ```bash
   vercel --prod
   ```

#### Manual Configuration

If you need to configure manually or understand the setup:

1. **Install dependencies locally (optional, for testing):**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. **Set up Playwright browsers (for ab_test_detector):**
   ```bash
   playwright install chromium
   ```

3. **Deploy to Vercel:**
   - Push your code to GitHub/GitLab/Bitbucket
   - Import the project in Vercel dashboard
   - Vercel will automatically detect the configuration from `vercel.json`

#### Environment Variables

Some tools may require environment variables. Set these in the Vercel dashboard under **Settings → Environment Variables**:

- (Currently no environment variables required, but add here as needed)

### Testing the Deployment

Once deployed, you can test the API:

1. **View all available tools (Discovery endpoint):**
   ```bash
   curl https://your-deployment.vercel.app/discovery
   ```

2. **Invoke a tool:**
   ```bash
   curl -X POST https://your-deployment.vercel.app/tools/greeting \
     -H "Content-Type: application/json" \
     -d '{"name": "Alice", "language": "spanish"}'
   ```

3. **Test other tools:**
   ```bash
   # Get today's date
   curl -X POST https://your-deployment.vercel.app/tools/todays-date \
     -H "Content-Type: application/json" \
     -d '{"format": "%B %d, %Y"}'

   # Run Lighthouse analysis
   curl -X POST https://your-deployment.vercel.app/tools/analyze_with_lighthouse \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'

   # Detect A/B tests
   curl -X POST https://your-deployment.vercel.app/tools/detect_ab_test \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com", "num_captures": 5}'
   ```

### Important Notes & Limitations

#### Vercel Constraints

- **Function timeout**: 10 seconds (Hobby), 60 seconds (Pro)
  - The `ab_test_detector` and `lighthouse` tools may timeout on the Hobby plan
  - Recommended to use Vercel Pro for these heavy tools

- **Deployment size**: 50MB limit
  - Playwright browsers are large (~200MB+)
  - Vercel may struggle to include full Playwright installation
  - Consider using `playwright-chromium` or external hosting for ab_test_detector

- **Cold starts**: First request may be slow due to serverless cold start

#### Tool-Specific Considerations

**Lighthouse Tool:**
- Requires Node.js Lighthouse CLI to be available
- May not work reliably on Vercel due to browser dependencies
- Consider using Lighthouse CI or external service for production

**A/B Test Detector:**
- Requires Playwright and Chromium browser
- May exceed size limits on Vercel
- Recommended to host separately on platforms with better container support (Railway, Render, Fly.io)

**Google Sheets Tools:**
- Requires valid Google Sheets API URL
- Update `SHEET_URL` in `api/index.py` with your own Google Apps Script endpoint

### Local Development

To run the unified API locally:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies (for Lighthouse)
npm install

# Run the API
uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

Then visit:
- API: http://localhost:8000
- Discovery endpoint: http://localhost:8000/discovery
- API docs: http://localhost:8000/docs

## Individual Tool Deployment

Each tool in the `python/` directory can also be run independently:

```bash
cd python/greeting
pip install -r requirements.txt  # or use uv/pip with pyproject.toml
python main.py
```

Then access the tool at http://localhost:8000 with its own `/discovery` endpoint.

## Project Structure

```
sample-opal-tools/
├── api/
│   └── index.py           # Unified API entry point for Vercel
├── python/                # Python tools (individual services)
│   ├── greeting/
│   ├── weather/
│   ├── google_sheets/
│   ├── lighthouse/
│   └── ab_test_detector/
├── typescript/            # TypeScript tools
├── dotnet/                # .NET tools
├── vercel.json           # Vercel deployment configuration
├── requirements.txt      # Python dependencies (unified)
├── package.json          # Node.js dependencies (Lighthouse)
└── README.md
```

## Contributing

Feel free to add more sample tools! Follow the existing pattern:

1. Create a new directory in `python/`, `typescript/`, or `dotnet/`
2. Implement your tool using the appropriate SDK
3. Add the tool to `api/index.py` for unified deployment
4. Update this README

## License

See individual tool directories for license information.
