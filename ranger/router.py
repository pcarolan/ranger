from smolagents import CodeAgent
from smolagents.models import OpenAIServerModel
from typing import List, Callable, Tuple
import os
import logging
import sys
import io
from contextlib import contextmanager
from .tools.weather import get_weather, get_travel_duration
from .models.claude import ClaudeServerModel

class Router:
    def __init__(self, debug: bool = False, model_type: str = "openai"):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.debug = debug
        if model_type == "openai":
            model = OpenAIServerModel(model_id="gpt-4")
        elif model_type == "claude":
            model = ClaudeServerModel()
        else:
            raise ValueError("Unsupported model_type. Use 'openai' or 'claude'.")
        self.agent = CodeAgent(
            tools=[get_weather, get_travel_duration],
            model=model,
            additional_authorized_imports=["datetime"]
        )

    @contextmanager
    def _redirect_stdout(self):
        """Context manager to redirect stdout when not in debug mode"""
        if not self.debug:
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                yield
            finally:
                sys.stdout = old_stdout
        else:
            yield

    def route(self, query: str) -> Tuple[str, str, List[str]]:
        """Route the query to the appropriate handler using the agent"""
        self.logger.info(f"Processing query: {query}")
        self.logger.info("Agent thinking process:")
        self.logger.info("-" * 50)
        prompt = f"""
        Analyze this query and use the appropriate tool to answer it:
        Query: {query}
        
        If the query is about weather, use the get_weather tool.
        If the query is about travel time or directions, use the get_travel_duration tool.
        If the query is about both, use both tools and combine the information.
        
        Format your response in a clear, user-friendly way.
        
        Show your thinking process by starting each thought with "Thought:".
        """
        
        with self._redirect_stdout():
            response = self.agent.run(prompt)
            self.logger.debug("Raw agent response: %s", response)
        
        self.logger.info("-" * 50)
        
        # Process the response to extract thoughts, final response, and tools used
        response = response.strip()
        lines = response.split('\n')
        
        final_lines = []
        thoughts = []
        tools_used = []
        
        for line in lines:
            if line.strip().startswith("Thought:"):
                thoughts.append(line.strip())
                self.logger.info(line.strip())
                # Track tools used
                if "using tool:" in line.lower():
                    tool_name = line.lower().split("using tool:")[-1].strip()
                    if tool_name not in tools_used:
                        tools_used.append(tool_name)
            else:
                final_lines.append(line)
        
        final_response = '\n'.join(final_lines)
        
        return final_response, '\n'.join(thoughts), tools_used 