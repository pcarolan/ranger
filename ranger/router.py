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
        
        IMPORTANT: When using a tool, you MUST start your thought with "Thought: Using tool: [tool_name]"
        For example: "Thought: Using tool: get_weather"
        
        Show your thinking process by starting each thought with "Thought:".
        """
        
        with self._redirect_stdout():
            response = self.agent.run(prompt)
            print("DEBUG: raw response =", response)  # Debug print
        
        self.logger.info("-" * 50)
        
        # Process the response to extract tool calls
        response = response.strip()
        self.logger.debug("raw response = %s", response)
        
        # Split into lines and process each line
        lines = response.split('\n')
        self.logger.debug("lines = %s", lines)
        
        final_lines = []
        tools_used = []
        thoughts = []
        
        for line in lines:
            self.logger.debug("processing line = %s", line)
            
            if line.strip().startswith("Thought:"):
                thoughts.append(line.strip())
                self.logger.info(line.strip())
                # Track tools used
                if "using tool:" in line.lower():
                    # Extract just the tool name after "using tool:"
                    tool_name = line.lower().split("using tool:")[-1].strip()
                    self.logger.debug("extracted tool_name = %s", tool_name)
                    if tool_name not in tools_used:
                        tools_used.append(tool_name)
            else:
                self.logger.debug("adding to final_lines = %s", line)
                final_lines.append(line)
        
        self.logger.debug("final_lines = %s", final_lines)
        final_response = '\n'.join(final_lines)
        self.logger.debug("final_response = %s", final_response)
        
        self.logger.debug("tools_used = %s", tools_used)
        thoughts_text = '\n'.join(thoughts)
        
        self.logger.info(f"Tools used: {tools_used}")
        self.logger.info(f"Final response: {final_response}")
        return final_response, thoughts_text, tools_used 