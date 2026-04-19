import os

# Load ANTHROPIC_API_KEY and FINANCIAL_DATASETS_API_KEY from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import logging
from contextlib import asynccontextmanager  # keeps MCP session open for app lifetime

# FastAPI — web framework for routes and request handling
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse

# MCP client — connects to the remote Financial Datasets MCP server over HTTPS
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

# Local modules: Claude agentic loop and HTML UI
from agent import run_agentic_turn
from views import render_home

logging.basicConfig(level=logging.INFO)
logging.getLogger("mcp.client.streamable_http").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

MCP_URL = "https://mcp.financialdatasets.ai/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.getenv("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        raise RuntimeError("FINANCIAL_DATASETS_API_KEY is not set")
    async with httpx.AsyncClient(headers={"X-API-KEY": api_key}) as http:
        async with streamable_http_client(MCP_URL, http_client=http) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                app.state.mcp_session = session
                app.state.mcp_tools = await session.list_tools()  # cache once at startup
                logger.info("MCP session ready — %d tools loaded", len(app.state.mcp_tools.tools))
                yield


app = FastAPI(title="AI Investing Advisor", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def index():
    return render_home()


@app.get("/api/tools")
async def list_tools(request: Request):
    return [{"name": t.name, "description": t.description} for t in request.app.state.mcp_tools.tools]


@app.post("/chat")
async def chat(request: Request, message: str = Form(...)):
    if not message.strip():
        return JSONResponse({"error": "Message cannot be empty."}, status_code=400)
    if len(message) > 2000:
        return JSONResponse({"error": "Message too long."}, status_code=400)
    try:
        final_message, tool_calls = await run_agentic_turn(message, request.app.state.mcp_session, request.app.state.mcp_tools)
        return {"message": final_message, "tools": [tc.name for tc in tool_calls]}
    except Exception as e:
        logger.error("Chat error: %s", e)
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=os.getenv("ENV") == "development")
