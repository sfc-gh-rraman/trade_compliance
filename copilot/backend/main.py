from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json

from config import get_settings
from database import get_db
from models.schemas import HealthResponse, AgentRequest
from routers import exceptions, rules, brokers, analyst, kpi
from services.agent_service import AgentService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"Starting {settings.app_name}...")
    print(f"Database: {settings.snowflake_database}")
    print(f"Schema: {settings.snowflake_schema}")
    
    try:
        db = get_db()
        db.get_connection()
        print("Snowflake connection established")
    except Exception as e:
        print(f"Warning: Could not connect to Snowflake: {e}")
    
    yield
    
    print("Shutting down...")
    db = get_db()
    db.close()
    print("Snowflake connection closed")


app = FastAPI(
    title="Trade Compliance Platform API",
    description="API for trade compliance exception management and AI-powered validation",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exceptions.router)
app.include_router(rules.router)
app.include_router(brokers.router)
app.include_router(analyst.router)
app.include_router(kpi.router)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and Snowflake connection state.
    """
    snowflake_connected = False
    try:
        db = get_db()
        conn = db.get_connection()
        snowflake_connected = not conn.is_closed()
    except Exception:
        pass
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        snowflake_connected=snowflake_connected,
        timestamp=datetime.utcnow(),
    )


@app.post("/api/chat")
async def chat(request: AgentRequest):
    """
    Chat endpoint for agent interaction.
    
    Processes natural language queries and returns agent responses.
    """
    agent = AgentService()
    
    final_response = None
    async for event in agent.run_agent(
        request.message, 
        [{"role": m.role, "content": m.content} for m in request.conversation_history]
    ):
        if event.get("type") == "text":
            final_response = event.get("content")
    
    return {
        "response": final_response or "Unable to process request",
        "conversation_id": None,
    }


@app.post("/api/chat/stream")
async def chat_stream(request: AgentRequest):
    """
    Streaming chat endpoint for agent interaction.
    
    Returns Server-Sent Events for real-time streaming responses.
    """
    agent = AgentService()
    
    async def event_generator():
        try:
            async for event in agent.run_agent(
                request.message,
                [{"role": m.role, "content": m.content} for m in request.conversation_history]
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns API information.
    """
    return {
        "name": "Trade Compliance Platform API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
