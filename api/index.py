"""
Lightweight Opal Tools API for Vercel Deployment
Contains only lightweight tools (no Playwright or Lighthouse dependencies)
For heavy tools (lighthouse, ab_test_detector), see api/heavy.py
"""

from opal_tools_sdk import ToolsService, tool
from pydantic import BaseModel, Field
from fastapi import FastAPI
from typing import Optional
import random
import datetime
import httpx

# Create unified FastAPI app
app = FastAPI(title="Opal Tools Service - Lightweight (Vercel)")
tools_service = ToolsService(app)

# ============================================================================
# PARAMETER MODELS
# ============================================================================

# Greeting tool parameters
class GreetingParameters(BaseModel):
    name: str = Field(..., description="Name of the person to greet")
    language: Optional[str] = Field(None, description="Language for greeting (defaults to random)")

class DateParameters(BaseModel):
    format: Optional[str] = Field("%Y-%m-%d", description="Date format (defaults to ISO format)")

# Weather tool parameters
class WeatherParameters(BaseModel):
    location: str
    units: str = "metric"

# Google Sheets tool parameters
class GetRowsParameters(BaseModel):
    pass

class AddRowParameters(BaseModel):
    title: str = Field(description="The title of the backlog item")
    hypothesis: str = Field(default="", description="The hypothesis for this item")
    user_problem: str = Field(default="", description="The user problem being addressed")
    metric: str = Field(default="", description="The metric to track")
    audience: str = Field(default="", description="The target audience")
    impact: int = Field(default=0, description="Impact score")
    confidence: int = Field(default=0, description="Confidence score")
    effort: int = Field(default=0, description="Effort score")
    ice: int = Field(default=0, description="ICE score (Impact × Confidence ÷ Effort)")
    notes: str = Field(default="", description="Additional notes")

# ============================================================================
# TOOL FUNCTIONS - GREETING
# ============================================================================

@tool("greeting", "Greets a person in a random language (English, Spanish, or French)")
async def greeting(parameters: GreetingParameters):
    """Greets a person in a random language."""
    name = parameters.name
    language = parameters.language

    # If language not specified, choose randomly
    if not language:
        language = random.choice(["english", "spanish", "french"])

    # Generate greeting based on language
    if language.lower() == "spanish":
        greeting_text = f"¡Hola, {name}! ¿Cómo estás?"
    elif language.lower() == "french":
        greeting_text = f"Bonjour, {name}! Comment ça va?"
    else:  # Default to English
        greeting_text = f"Hello, {name}! How are you?"

    return {
        "greeting": greeting_text,
        "language": language
    }

@tool("todays-date", "Returns today's date in the specified format")
async def todays_date(parameters: DateParameters):
    """Returns today's date."""
    date_format = parameters.format

    # Get today's date
    today = datetime.datetime.now()

    # Format the date
    formatted_date = today.strftime(date_format)

    return {
        "date": formatted_date,
        "format": date_format,
        "timestamp": today.timestamp()
    }

# ============================================================================
# TOOL FUNCTIONS - WEATHER
# ============================================================================

@tool("get_weather", "Gets current weather for a location")
async def get_weather(parameters: WeatherParameters):
    return {"temperature": 22, "condition": "sunny"}

# ============================================================================
# TOOL FUNCTIONS - GOOGLE SHEETS
# ============================================================================

SHEET_URL = "https://script.google.com/macros/s/AKfycbyB6jwR-3ORsIGR-afJE86vjQvuelkjv1pewpFOWpKzZ0KMm-1Ob6hE9J3YGaKq7s2n/exec"

@tool("get_google_sheet_rows", "Gets all rows from the Google Sheet")
async def get_google_sheet_rows(parameters: GetRowsParameters):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(SHEET_URL)
        response.raise_for_status()
        return response.json()

@tool("add_google_sheet_row", "Adds a new row to the Google Sheet backlog")
async def add_google_sheet_row(parameters: AddRowParameters):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        data = {
            "Title": parameters.title,
            "Hypothesis": parameters.hypothesis,
            "User Problem": parameters.user_problem,
            "Metric": parameters.metric,
            "Audience": parameters.audience,
            "Impact": parameters.impact,
            "Confidence": parameters.confidence,
            "Effort": parameters.effort,
            "ICE": parameters.ice,
            "Notes": parameters.notes
        }
        response = await client.post(SHEET_URL, json=data)
        response.raise_for_status()
        return response.json()

# ============================================================================
# VERCEL SERVERLESS HANDLER
# ============================================================================

# Export the app for Vercel (Vercel will automatically wrap this as an ASGI handler)
# Note: Vercel expects 'app' to be exported at module level
# The app is already created above, no need to reassign
