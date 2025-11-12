from opal_tools_sdk import ToolsService, tool
from pydantic import BaseModel, Field
from fastapi import FastAPI
import subprocess
import json
import tempfile
import os

app = FastAPI()
tools_service = ToolsService(app)

class LighthouseParameters(BaseModel):
    url: str = Field(description="The URL to analyze with Lighthouse")
    format: str = Field(default="json", description="Output format: json or html")

@tool("analyze_with_lighthouse", "Runs a Lighthouse performance analysis on the provided URL")
async def analyze_with_lighthouse(parameters: LighthouseParameters):
    """
    Runs Lighthouse on the provided URL and returns the analysis results.
    """
    try:
        # Create a temporary file for the output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        # Build the lighthouse command
        cmd = [
            'lighthouse',
            parameters.url,
            '--output=json',
            f'--output-path={tmp_path}',
            '--form-factor=desktop',
            '--screenEmulation.disabled',
            '--throttling-method=provided',
            '--chrome-flags="--headless --no-sandbox --disable-gpu --disable-dev-shm-usage"',
            '--quiet'
        ]

        # Run lighthouse
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=False
        )

        if result.returncode != 0:
            return {
                "error": "Lighthouse analysis failed",
                "stderr": result.stderr,
                "stdout": result.stdout
            }

        # Read the JSON output
        with open(tmp_path, 'r') as f:
            lighthouse_data = json.load(f)

        # Clean up the temp file
        os.unlink(tmp_path)

        # Extract key metrics
        categories = lighthouse_data.get('categories', {})
        audits = lighthouse_data.get('audits', {})

        # Build a summary response - convert scores to percentages
        summary = {
            "url": lighthouse_data.get('finalUrl', parameters.url),
            "fetchTime": lighthouse_data.get('fetchTime'),
            "scores": {
                "performance": int(categories.get('performance', {}).get('score', 0) * 100) if categories.get('performance', {}).get('score') is not None else None,
                "accessibility": int(categories.get('accessibility', {}).get('score', 0) * 100) if categories.get('accessibility', {}).get('score') is not None else None,
                "best-practices": int(categories.get('best-practices', {}).get('score', 0) * 100) if categories.get('best-practices', {}).get('score') is not None else None,
                "seo": int(categories.get('seo', {}).get('score', 0) * 100) if categories.get('seo', {}).get('score') is not None else None,
                "pwa": int(categories.get('pwa', {}).get('score', 0) * 100) if categories.get('pwa', {}).get('score') is not None else None
            },
            "metrics": {
                "first-contentful-paint": audits.get('first-contentful-paint', {}).get('displayValue'),
                "largest-contentful-paint": audits.get('largest-contentful-paint', {}).get('displayValue'),
                "total-blocking-time": audits.get('total-blocking-time', {}).get('displayValue'),
                "cumulative-layout-shift": audits.get('cumulative-layout-shift', {}).get('displayValue'),
                "speed-index": audits.get('speed-index', {}).get('displayValue'),
                "interactive": audits.get('interactive', {}).get('displayValue')
            }
        }

        # Convert all audit scores in the full report to percentages for consistency
        if 'audits' in lighthouse_data:
            for audit_id, audit_data in lighthouse_data['audits'].items():
                if 'score' in audit_data and audit_data['score'] is not None:
                    # Convert score from 0-1 to 0-100 for better readability
                    audit_data['scorePercentage'] = int(audit_data['score'] * 100)

        # Always return both summary and full report
        # The full_report contains all audits, recommendations, and detailed metrics
        return {
            "summary": summary,
            "full_report": lighthouse_data
        }

    except Exception as e:
        return {
            "error": f"Failed to run Lighthouse: {str(e)}"
        }

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()