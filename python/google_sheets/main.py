from opal_tools_sdk import ToolsService, tool
from pydantic import BaseModel
from fastapi import FastAPI
import httpx

app = FastAPI()
tools_service = ToolsService(app)

SHEET_URL = "https://script.google.com/macros/s/AKfycbyB6jwR-3ORsIGR-afJE86vjQvuelkjv1pewpFOWpKzZ0KMm-1Ob6hE9J3YGaKq7s2n/exec"

class GetRowsParameters(BaseModel):
    pass

@tool("get_google_sheet_rows", "Gets all rows from the Google Sheet")
async def get_google_sheet_rows(parameters: GetRowsParameters):
    async with httpx.AsyncClient() as client:
        response = await client.get(SHEET_URL)
        response.raise_for_status()
        return response.json()

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
