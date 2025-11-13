"""
Heavy Opal Tools API for Railway/Render Deployment
Contains tools with heavy dependencies (Playwright, Lighthouse)
For lightweight tools, see api/index.py
"""

from opal_tools_sdk import ToolsService, tool
from pydantic import BaseModel, Field
from fastapi import FastAPI
from typing import List, Dict, Any
import subprocess
import json
import tempfile
import os
import asyncio
from playwright.async_api import async_playwright
from PIL import Image
import io
import numpy as np
from skimage.metrics import structural_similarity as ssim
import imagehash
import base64

# Create FastAPI app for heavy tools
app = FastAPI(title="Opal Tools Service - Heavy (Railway/Render)")
tools_service = ToolsService(app)

# ============================================================================
# PARAMETER MODELS
# ============================================================================

# Lighthouse tool parameters
class LighthouseParameters(BaseModel):
    url: str = Field(description="The URL to analyze with Lighthouse")
    format: str = Field(default="json", description="Output format: json or html")

# A/B Test Detector parameters
class ABTestDetectorParameters(BaseModel):
    url: str = Field(description="The URL to analyze for A/B tests")
    num_captures: int = Field(default=10, description="Number of screenshots to capture")
    delay_seconds: int = Field(default=3, description="Delay between captures in seconds")
    viewport_width: int = Field(default=1920, description="Browser viewport width")
    viewport_height: int = Field(default=1080, description="Browser viewport height")
    threshold: float = Field(default=0.05, description="Minimum difference percentage to flag as A/B test (0.05 = 5%)")

# ============================================================================
# TOOL FUNCTIONS - LIGHTHOUSE
# ============================================================================

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

# ============================================================================
# TOOL FUNCTIONS - A/B TEST DETECTOR
# ============================================================================

@tool("detect_ab_test", "Detects if a website is running an A/B test by comparing multiple screenshots")
async def detect_ab_test(parameters: ABTestDetectorParameters):
    """
    Captures multiple screenshots of a URL and analyzes them for variations
    that might indicate an active A/B test.
    """
    screenshots = []
    screenshot_hashes = []

    try:
        async with async_playwright() as p:
            # Launch browser with container-friendly flags
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions'
                ]
            )

            # Capture screenshots
            for i in range(parameters.num_captures):
                # Create new context for each capture (fresh session)
                context = await browser.new_context(
                    viewport={'width': parameters.viewport_width, 'height': parameters.viewport_height},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )

                page = await context.new_page()

                try:
                    # Navigate to URL with more lenient wait condition
                    await page.goto(parameters.url, wait_until='domcontentloaded', timeout=60000)

                    # Wait a bit for any dynamic content
                    await asyncio.sleep(2)

                    # Capture screenshot
                    screenshot_bytes = await page.screenshot(full_page=False)

                    # Convert to PIL Image for analysis
                    img = Image.open(io.BytesIO(screenshot_bytes))
                    screenshots.append(img)

                    # Calculate perceptual hash for quick comparison
                    hash_val = str(imagehash.phash(img))
                    screenshot_hashes.append(hash_val)

                except Exception as e:
                    print(f"Error capturing screenshot {i+1}: {str(e)}")
                finally:
                    await context.close()

                # Delay between captures (except after last one)
                if i < parameters.num_captures - 1:
                    await asyncio.sleep(parameters.delay_seconds)

            await browser.close()

        # Analyze screenshots for variations
        if len(screenshots) < 2:
            return {"error": "Not enough screenshots captured for comparison"}

        # Find unique variations based on perceptual hashes
        unique_hashes = list(set(screenshot_hashes))
        variation_groups = {hash_val: [] for hash_val in unique_hashes}

        for i, hash_val in enumerate(screenshot_hashes):
            variation_groups[hash_val].append(i)

        # Calculate pixel-level differences
        differences = []
        ssim_scores = []

        # Convert first screenshot to numpy array for comparison
        base_img = np.array(screenshots[0].convert('RGB'))

        for i in range(1, len(screenshots)):
            # Convert to numpy array
            compare_img = np.array(screenshots[i].convert('RGB'))

            # Ensure images are same size
            if base_img.shape != compare_img.shape:
                compare_img = np.array(screenshots[i].resize(screenshots[0].size).convert('RGB'))

            # Calculate pixel difference
            diff = np.abs(base_img.astype(float) - compare_img.astype(float))
            diff_percentage = (diff > 10).sum() / diff.size  # Pixels with >10 intensity difference
            differences.append(diff_percentage)

            # Calculate SSIM (structural similarity)
            gray_base = np.array(screenshots[0].convert('L'))
            gray_compare = np.array(screenshots[i].convert('L'))

            if gray_base.shape == gray_compare.shape:
                score = ssim(gray_base, gray_compare)
                ssim_scores.append(score)

        # Determine if A/B test is likely running
        max_difference = max(differences) if differences else 0
        avg_difference = sum(differences) / len(differences) if differences else 0
        num_variations = len(unique_hashes)

        is_ab_test_likely = (
            max_difference > parameters.threshold or
            num_variations > 1
        )

        # Calculate confidence score
        confidence = 0
        if num_variations == 2:
            # Classic A/B test pattern
            confidence = 0.9
        elif num_variations > 2:
            # Multivariate test or dynamic content
            confidence = 0.7
        elif max_difference > parameters.threshold:
            # Some variation detected
            confidence = 0.5
        else:
            confidence = 0.1

        # Create heatmap data (simplified - areas with most variation)
        if len(screenshots) >= 2:
            # Calculate variance across all screenshots
            all_arrays = [np.array(img.convert('RGB')) for img in screenshots[:5]]  # Limit for performance
            stacked = np.stack(all_arrays)
            variance = np.var(stacked, axis=0).mean(axis=2)  # Average variance across RGB channels

            # Find regions with highest variance
            height, width = variance.shape
            grid_size = 10
            heatmap = []

            for y in range(0, height, height // grid_size):
                for x in range(0, width, width // grid_size):
                    region_variance = variance[y:y+height//grid_size, x:x+width//grid_size].mean()
                    heatmap.append({
                        "x": x,
                        "y": y,
                        "variance": float(region_variance)
                    })

            # Sort by variance to find hot spots
            heatmap.sort(key=lambda x: x["variance"], reverse=True)
            top_variation_areas = heatmap[:5]
        else:
            top_variation_areas = []

        # Prepare response
        result = {
            "url": parameters.url,
            "analysis": {
                "screenshots_captured": len(screenshots),
                "unique_variations_detected": num_variations,
                "is_ab_test_likely": is_ab_test_likely,
                "confidence_score": confidence,
                "max_difference_percentage": float(max_difference * 100),
                "average_difference_percentage": float(avg_difference * 100),
                "threshold_percentage": float(parameters.threshold * 100)
            },
            "variations": {
                "groups": {
                    f"variation_{i+1}": {
                        "screenshot_indices": indices,
                        "frequency": len(indices),
                        "percentage": len(indices) / len(screenshots) * 100
                    }
                    for i, (hash_val, indices) in enumerate(variation_groups.items())
                },
                "total_unique": num_variations
            },
            "similarity_metrics": {
                "average_ssim": sum(ssim_scores) / len(ssim_scores) if ssim_scores else None,
                "min_ssim": min(ssim_scores) if ssim_scores else None,
                "max_ssim": max(ssim_scores) if ssim_scores else None
            },
            "hot_spots": top_variation_areas[:3],  # Top 3 areas with most variation
            "recommendations": []
        }

        # Add recommendations based on findings
        if is_ab_test_likely:
            if num_variations == 2:
                result["recommendations"].append(
                    "Strong indication of A/B test detected. Consider monitoring this page regularly to track test duration."
                )
            elif num_variations > 2:
                result["recommendations"].append(
                    "Multiple variations detected. This could be a multivariate test or personalization."
                )
            result["recommendations"].append(
                "Analyze the varying elements to understand competitor's testing priorities."
            )
        else:
            result["recommendations"].append(
                "No clear A/B test detected. The page appears consistent across captures."
            )
            if avg_difference > 0.01:
                result["recommendations"].append(
                    "Minor variations detected, possibly due to dynamic content or ads."
                )

        # Add screenshot samples if variations detected
        if num_variations > 1 and len(screenshots) >= 2:
            # Convert first screenshot from each variation to base64 for preview
            samples = []
            for i, (hash_val, indices) in enumerate(list(variation_groups.items())[:2]):
                if indices:
                    img = screenshots[indices[0]]
                    # Resize for preview
                    img_thumb = img.resize((400, 300), Image.Resampling.LANCZOS)

                    # Convert to base64
                    buffer = io.BytesIO()
                    img_thumb.save(buffer, format='PNG')
                    img_str = base64.b64encode(buffer.getvalue()).decode()

                    samples.append({
                        "variation": f"variation_{i+1}",
                        "preview": f"data:image/png;base64,{img_str[:100]}..."  # Truncated for response
                    })

            result["screenshot_samples"] = samples

        return result

    except Exception as e:
        return {
            "error": f"Failed to analyze URL for A/B tests: {str(e)}"
        }

# ============================================================================
# SERVER HANDLER
# ============================================================================

# Export the app
handler = app

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
