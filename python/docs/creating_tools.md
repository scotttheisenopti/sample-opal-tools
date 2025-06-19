# Creating Tools with the Opal Python SDK

## Introduction: What is a Tool?

A tool, within the Opal platform, is a discrete, API-exposed function or service that can be programmatically invoked to perform a specific task. Tools are designed to be discoverable, parameterized, and reusable, enabling automation and integration across workflows. Each tool is defined by its input parameters, execution logic, and output schema, and is registered with the Opal platform for discovery and invocation.

## Prerequisites

- Python 3.8 or higher
- Familiarity with Python programming

## Step-by-Step Guide to Creating a Tool

### 1. Install Required Packages

Install the necessary dependencies:

```bash
pip install fastapi pydantic opal-tools-sdk uvicorn
```

### 2. Initialize FastAPI Application and Tools Service

Create a Python file (e.g., `main.py`). Import the required modules and initialize the FastAPI application and Opal Tools service:

```python
from opal_tools_sdk import ToolsService, tool
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()
tools_service = ToolsService(app)
```

The `ToolsService` attaches Opal tool registration and discovery capabilities to the FastAPI application.

### 3. Define Tool Parameters

Define the input parameters for the tool using a Pydantic model. This ensures type validation and documentation:

```python
class WeatherParameters(BaseModel):
    location: str
    units: str = "metric"
```

### 4. Register the Tool Function

Define the tool's execution logic and register it using the `@tool` decorator. Specify a unique name and a concise description:

```python
@tool("get_weather", "Gets current weather for a location")
async def get_weather(parameters: WeatherParameters):
    # Tool logic implementation
    return {"temperature": 22, "condition": "sunny"}
```

The function receives a validated `parameters` object as defined by the Pydantic model.

### 5. Run the Service

Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

The `--reload` flag enables automatic server restarts on code changes.

### 6. Tool Discovery Endpoint

Upon running the service, a discovery endpoint is available at `/discovery`. This endpoint provides a machine-readable listing of all registered tools, their parameters, and descriptions.

Access the endpoint at: [http://localhost:8000/discovery](http://localhost:8000/discovery)

### 7. Complete Example

```python
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
```

---

## Example: Running and Invoking the Tool

### Running the Service

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The service will be available at `http://localhost:8000`.

### Invoking the Tool Directly via HTTP

To invoke the tool directly, send a POST request to the tool's endpoint. The endpoint path is `/tools/{tool_name}`. For the example above, the endpoint is `/tools/get_weather`.

Example using `curl`:

```bash
curl -X POST \
  http://localhost:8000/tools/get_weather \
  -H 'Content-Type: application/json' \
  -d '{"location": "Berlin", "units": "metric"}'
```

Example using `httpie`:

```bash
http POST http://localhost:8000/tools/get_weather location="Berlin" units="metric"
```

A successful response will return the tool's output, for example:

```json
{
  "temperature": 22,
  "condition": "sunny"
}
```

---

## Interacting with the Tool through Opal

Once the tool service is running and registered with the Opal platform, it can be discovered and invoked through Opal's orchestration mechanisms. The following are typical interaction patterns:

### 1. Tool Discovery via Opal

Opal will automatically discover the tool via the `/discovery` endpoint. Ensure your service is accessible to the Opal platform or agent.

### 2. Invoking the Tool via Opal CLI

If using the Opal CLI, you can invoke the tool as follows (replace placeholders as appropriate):

```bash
opal tool invoke --service-url http://localhost:8000 --tool get_weather --params '{"location": "Berlin", "units": "metric"}'
```

This command will send the request to the tool and display the response.

### 3. Integration in Opal Workflows

Tools can be referenced in Opal workflow definitions or automation scripts. Refer to the Opal platform documentation for details on workflow integration and tool chaining.

---

A full working example of the whether tool can be found in the [sample-opal-tools](https://github.com/newscred/sample-opal-tools/tree/main/python/weather) repository 


## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

- Opal Tools SDK (Python): Refer to the package README for advanced usage.
