import asyncio
import os
import sys
from dotenv import load_dotenv
from google.genai.types import Content, Part
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.session import Session
import uuid

# Add current directory to sys.path
sys.path.append(os.getcwd())

from Gemini3.src.agents import create_concept_analyzer

load_dotenv()

async def test_agent():
    print("Creating agent...")
    agent = create_concept_analyzer()
    
    session_service = InMemorySessionService()
    session = session_service.create_session(
        app_name="TestApp",
        user_id="test_user",
        session_id=str(uuid.uuid4())
    )
    
    user_prompt = "Explain Brownian Motion"
    user_content = Content(parts=[Part(text=user_prompt)])
    
    context = InvocationContext(
        session_service=session_service,
        invocation_id=str(uuid.uuid4()),
        agent=agent,
        session=session,
        user_content=user_content,
        run_config=RunConfig()
    )
    
    print("Running agent...")
    async for event in agent.run_async(context):
        print(f"Event Type: {type(event)}")
        print(f"Dir Event: {dir(event)}")
        if hasattr(event, 'text'):
            print(f"Event Text: {event.text}")
        if hasattr(event, 'parts'):
            print(f"Event Parts: {event.parts}")

if __name__ == "__main__":
    asyncio.run(test_agent())

