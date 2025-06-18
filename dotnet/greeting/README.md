# Opal Tools SDK Sample for C#

This is a sample application that demonstrates how to use the Opal Tools SDK for C#.

## Running the Sample

To run the sample:

```bash
cd sdks/samples/csharp
dotnet run
```

The server will start at http://localhost:5000 by default.

## Available Endpoints

- `/discovery` - Returns information about all available tools
- `/tools/greeting` - Greets a person in a random language
- `/tools/todays-date` - Returns today's date in the specified format
- `/tools/auth-example` - Example tool that requires authentication

## Testing with cURL

### Discovery Endpoint

```bash
curl -X GET http://localhost:5000/discovery
```

### Greeting Tool

```bash
curl -X POST http://localhost:5000/tools/greeting \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"name": "John", "language": "spanish"}}'
```

### Today's Date Tool

```bash
curl -X POST http://localhost:5000/tools/todays-date \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"format": "yyyy-MM-dd"}}'
```

### Authentication Example Tool

```bash
curl -X POST http://localhost:5000/tools/auth-example \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {"name": "John"},
    "auth": {
      "provider": "google",
      "credentials": {
        "token": "sample_token"
      }
    }
  }'
```

## Implementation Details

This sample demonstrates:

1. Creating tool parameter models with validation attributes
2. Implementing ´IOpalTool<TParameter>´ methods with the `[Display]` attribute
3. Using the `[OpalAuthorization]` attribute for authentication
4. Processing tool requests and returning responses
5. Handling different parameter types

See the `Program.cs` file for the complete implementation.