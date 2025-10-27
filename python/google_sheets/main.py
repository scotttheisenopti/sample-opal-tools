from opal_tools_sdk import ToolsService, tool
from pydantic import BaseModel, Field
from fastapi import FastAPI
import httpx

app = FastAPI()
tools_service = ToolsService(app)

SHEET_URL = "https://script.google.com/macros/s/AKfycbyB6jwR-3ORsIGR-afJE86vjQvuelkjv1pewpFOWpKzZ0KMm-1Ob6hE9J3YGaKq7s2n/exec"

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

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
