from opal_tools_sdk import ToolsService, tool
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()
tools_service = ToolsService(app)

class WeatherParameters(BaseModel):
    location: str
    units: str = "metric"

@tool("get_weather", "Gets current weather for a location")
async def get_weather(parameters: WeatherParameters):
    return {"temperature": 22, "condition": "sunny"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()