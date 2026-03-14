import dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from agent.agent import create_agent



app = FastAPI()
# Load environment variables from a .env file (if present)
dotenv.load_dotenv()
agent_graph = create_agent()


def run_agent(session_id: str, message: str, context: dict = None):
    config = {
        "configurable": {
            # Use session_id as thread_id for compatibility
            "thread_id": session_id,
        }
    }
    if context:
        config["context"] = context

    events = agent_graph.stream(
        {"messages": ("user", message)},
        config,
        stream_mode="values"
    )

    final_answer = None
    for event in events:
        if "messages" in event:
            final_answer = event["messages"][-1].content
    return final_answer



# POST /chat expects: {message: string, session_id: string, context: JSON}
# Returns: {response: string}
from fastapi import Request
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: str
    context: dict = None

@app.post("/chat")
async def chat(request: ChatRequest):
    response = run_agent(request.session_id, request.message, request.context)
    return {"response": response}
