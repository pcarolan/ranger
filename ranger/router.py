from smolagents import CodeAgent
from smolagents.models import OpenAIServerModel
from typing import List, Callable, Tuple
import os
import logging
import sys
import io
from contextlib import contextmanager
from ranger.weather import get_weather, get_travel_duration

class Router:
    def __init__(self, debug: bool = False):
        self.logger = logging.getLogger(__name__)
        self.debug = debug
        self.agent = CodeAgent(
            tools=[get_weather, get_travel_duration],
            model=OpenAIServerModel(model_id="gpt-4"),
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

    def route(self, query: str) -> Tuple[str, str]:
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
        
        self.logger.info("-" * 50)
        
        # Split and separate thoughts from final answer
        lines = response.splitlines()
        thoughts = []
        final_lines = []
        for line in lines:
            if line.strip().startswith("Thought:"):
                thoughts.append(line.strip())
                self.logger.info(line.strip())
            elif line.strip():
                final_lines.append(line)
        
        final_response = "\n".join(final_lines).strip()
        thoughts_text = "\n".join(thoughts)
        
        self.logger.info(f"Final response: {final_response}")
        return final_response, thoughts_text 