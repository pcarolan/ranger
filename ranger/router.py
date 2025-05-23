from smolagents import CodeAgent
from smolagents.models import OpenAIServerModel
from typing import List, Callable
import os
import logging
from ranger.weather import get_weather, get_travel_duration

class Router:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agent = CodeAgent(
            tools=[get_weather, get_travel_duration],
            model=OpenAIServerModel(model_id="gpt-4"),
            additional_authorized_imports=["datetime"]
        )

    def route(self, query: str) -> str:
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
        
        Show your thinking process by starting each thought with \"Thought:\".
        When you output code, always use this format:
        Thoughts: <your thoughts>
        Code:
        ```py
        # your code here
        ```
        <end_code>
        Always include the <end_code> marker after your code block.
        """
        response = self.agent.run(prompt)
        self.logger.info("-" * 50)
        # Split and log thoughts, return only the final answer
        lines = response.splitlines()
        final_lines = []
        for line in lines:
            if line.strip().startswith("Thought:"):
                self.logger.info(line.strip())
            elif line.strip():
                final_lines.append(line)
        final_response = "\n".join(final_lines).strip()
        self.logger.info(f"Final response: {final_response}")
        return final_response 