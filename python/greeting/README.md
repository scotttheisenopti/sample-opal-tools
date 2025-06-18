# Sample Python Tools Service

This is a sample tools service for Opal using the Python SDK. It provides two tools:

1. **Greeting Tool**: Greets a person in a random language (English, Spanish, or French)
2. **Today's Date Tool**: Returns today's date in the specified format

## Running the Service

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py
```

### Docker

```bash
# Build the Docker image
docker build -t opal-sample-tools-python .

# Run the container
docker run -p 8000:8000 opal-sample-tools-python
```

## Testing the Service

Once the service is running, you can access:

- OpenAPI documentation: http://localhost:8000/docs
- Discovery endpoint: http://localhost:8000/discovery
- Tools endpoints:
  - Greeting tool: http://localhost:8000/tools/greeting
  - Today's date tool: http://localhost:8000/tools/todays-date

## Example Requests

### Greeting Tool

```bash
curl -X POST http://localhost:8000/tools/greeting \
  -H "Content-Type: application/json" \
  -d '{"name":"John"}'
```

Response:
```json
{
  "greeting": "Hello, John! How are you?",
  "language": "english"
}
```

### Today's Date Tool

```bash
curl -X POST http://localhost:8000/tools/todays-date \
  -H "Content-Type: application/json" \
  -d '{"format":"%B %d, %Y"}'
```

Response:
```json
{
  "date": "March 18, 2023",
  "format": "%B %d, %Y",
  "timestamp": 1679145600.0
}
```
