import asyncio
import uuid
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.session import Session
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

from .core import logger
from .agents import (
    create_concept_analyzer,
    create_prerequisite_explorer,
    create_mathematical_enricher,
    create_visual_designer,
    create_narrative_composer,
    create_code_generator
)

def run_agent_sync(agent: Agent, input_text: str) -> str:
    """
    Helper to run an ADK agent synchronously with a text input.
    Constructs the necessary InvocationContext and SessionService.
    """
    async def _run():
        session_service = InMemorySessionService()

        # Create session using the service factory
        session = await session_service.create_session(
            app_name="Gemini3MathToManim",
            user_id="user_default",
            session_id=str(uuid.uuid4())
        )

        # Construct user content properly
        user_content = Content(parts=[Part(text=input_text)])

        # Construct RunConfig
        run_config = RunConfig()

        # Manually construct context
        context = InvocationContext(
            session_service=session_service,
            invocation_id=str(uuid.uuid4()),
            agent=agent,
            session=session,
            user_content=user_content,
            run_config=run_config
        )

        output_text = []

        # Run agent
        try:
            async for event in agent.run_async(context):
                if hasattr(event, 'text') and event.text:
                    output_text.append(event.text)
                    logger.log_agent_thought(agent.name, event.text)

        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            raise e

        return "".join(output_text)

    return asyncio.run(_run())


class Gemini3Pipeline:
    """
    Orchestrates the Math-To-Manim pipeline using Google ADK Agents.
    """
    def __init__(self):
        logger.console.print("[bold blue]Initializing Pipeline Agents...[/bold blue]")
        self.concept_analyzer = create_concept_analyzer()
        self.prerequisite_explorer = create_prerequisite_explorer()
        self.math_enricher = create_mathematical_enricher()
        self.visual_designer = create_visual_designer()
        self.narrative_composer = create_narrative_composer()
        self.code_generator = create_code_generator()
        logger.console.print("[bold green]Pipeline Initialized.[/bold green]")

    def run(self, user_prompt: str) -> str:
        """
        Executes the full pipeline from prompt to code.
        """
        logger.console.rule("[bold red]Pipeline Start[/bold red]")

        # 1. Concept Analysis
        logger.log_agent_start("ConceptAnalyzer", "Analyzing user prompt...")
        analysis_result = run_agent_sync(self.concept_analyzer, user_prompt)
        logger.log_agent_completion("ConceptAnalyzer", str(analysis_result))

        # 2. Prerequisite Exploration
        logger.log_agent_start("PrerequisiteExplorer", "Building knowledge tree...")
        tree_result = run_agent_sync(self.prerequisite_explorer, f"Build a prerequisite tree for this concept analysis: {analysis_result}")
        logger.log_agent_completion("PrerequisiteExplorer", str(tree_result))

        # 3. Mathematical Enrichment
        logger.log_agent_start("MathematicalEnricher", "Enriching tree with LaTeX...")
        enriched_tree = run_agent_sync(self.math_enricher, f"Enrich this knowledge tree with physics/math details: {tree_result}")
        logger.log_agent_completion("MathematicalEnricher", str(enriched_tree))

        # 4. Visual Design
        logger.log_agent_start("VisualDesigner", "Designing visual storyboard...")
        storyboard = run_agent_sync(self.visual_designer, f"Create a visual storyboard for this enriched tree: {enriched_tree}")
        logger.log_agent_completion("VisualDesigner", str(storyboard))

        # 5. Narrative Composition
        logger.log_agent_start("NarrativeComposer", "Composing verbose prompt...")
        verbose_prompt = run_agent_sync(self.narrative_composer, f"Write a verbose animation prompt based on this storyboard: {storyboard}")
        logger.log_agent_completion("NarrativeComposer", str(verbose_prompt))

        # 6. Code Generation
        logger.log_agent_start("CodeGenerator", "Generating Manim code...")
        code_result = run_agent_sync(self.code_generator, f"Generate the Manim code for this description: {verbose_prompt}")
        logger.log_agent_completion("CodeGenerator", str(code_result))

        logger.console.rule("[bold red]Pipeline End[/bold red]")

        return str(code_result)
