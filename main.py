"""FastAPI backend for the functional-testing dashboard.

Endpoints:
  GET  /         — Serves the interactive single-page dashboard.
  GET  /health   — Returns {"status": "ok", "commit": "<sha>"}.
  POST /api/execute — Invokes a target.py function with given args.
"""

import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import target

app = FastAPI(title="Functional Testing Dashboard")

# Mount static assets (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Deployed commit SHA (set by CI, Render, or environment)
COMMIT_SHA = (
    os.getenv("GIT_COMMIT_SHA")
    or os.getenv("RENDER_GIT_COMMIT")
    or os.getenv("GITHUB_SHA")
    or "local-dev"
)

# Registry of callable functions from target.py
FUNCTION_REGISTRY = {
    "is_adult": target.is_adult,
    "celsius_to_fahrenheit": target.celsius_to_fahrenheit,
    "count_vowels": target.count_vowels,
    "invert": target.invert,
    "greet": target.greet,
    "find_max": target.find_max,
    "get_price": target.get_price,
    "swap": target.swap,
    "common_items": target.common_items,
    "is_leap_year": target.is_leap_year,
    "to_int": target.to_int,
    "divide": target.divide,
    "power": target.power,
    "square_root": target.square_root,
    "factorial": target.factorial,
    "average": target.average,
}


@app.get("/health")
async def health():
    """Health check returning deployed commit SHA."""
    return {"status": "ok", "commit": COMMIT_SHA}


@app.post("/api/execute")
async def execute_function(request: Request):
    """Execute a target.py function with the provided arguments.

    Body: {"function": "is_adult", "args": [25]}
    Returns: {"success": true, "result": true}
         or: {"success": false, "error": "...", "type": "ValueError"}
    """
    body = await request.json()
    func_name = body.get("function", "")
    args = body.get("args", [])

    if func_name not in FUNCTION_REGISTRY:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": f"Unknown function: {func_name}",
                "type": "ValueError",
            },
        )

    func = FUNCTION_REGISTRY[func_name]

    try:
        result = func(*args)
        # Convert sets to sorted lists for JSON serialization
        if isinstance(result, set):
            result = sorted(result)
        return {"success": True, "result": result}
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "type": type(exc).__name__,
        }


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the interactive dashboard."""
    with open("static/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    # Inject commit SHA into the page
    html = html.replace("{{COMMIT_SHA}}", COMMIT_SHA)
    return HTMLResponse(content=html)
