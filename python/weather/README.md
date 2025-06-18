# Weather Tool

A FastAPI project for weather tools.

## Requirements
- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (for dependency management and running)

## Setup

1. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```
   Or, if using `pyproject.toml`:
   ```bash
   uv pip install -r <(uv pip compile pyproject.toml)
   ```

2. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

Or, using `uv` as a process manager:

```bash
uv pip install fastapi uvicorn
uvicorn app.main:app --reload
```

## API
- `GET /` - Root endpoint returns a welcome message. 