from smolagents import CodeAgent
from smolagents.models import OpenAIServerModel
from typing import List, Callable, Tuple
import os
import logging
import sys
import io
from contextlib import contextmanager
from .tools.weather import get_weather, get_travel_duration

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
        
        # Split and separate thoughts from final answer
        lines = response.splitlines()
        print("DEBUG: lines =", lines)  # Debug print
        thoughts = []
        final_lines = []
        tools_used = set()  # Use a set to avoid duplicates
        
        for line in lines:
            print("DEBUG: processing line =", line)  # Debug print
            if line.strip().startswith("Thought:"):
                thoughts.append(line.strip())
                self.logger.info(line.strip())
                # Track tools used
                if "using tool:" in line.lower():
                    # Extract just the tool name after "using tool:"
                    tool_name = line.lower().split("using tool:")[-1].strip()
                    print("DEBUG: extracted tool_name =", tool_name)  # Debug print
                    tools_used.add(tool_name)
                    self.logger.info(f"Found tool used: {tool_name}")
            elif line.strip():
                print("DEBUG: adding to final_lines =", line)  # Debug print
                final_lines.append(line)
        
        print("DEBUG: final_lines =", final_lines)  # Debug print
        final_response = "\n".join(final_lines).strip()
        print("DEBUG: final_response =", final_response)  # Debug print
        thoughts_text = "\n".join(thoughts)
        
        # Convert set to list for return
        tools_used = list(tools_used)
        print("DEBUG: tools_used =", tools_used)  # Debug print
        
        self.logger.info(f"Tools used: {tools_used}")
        self.logger.info(f"Final response: {final_response}")
        return final_response, thoughts_text, tools_used 