from smolagents import CodeAgent
from smolagents.models import OpenAIServerModel
from typing import List, Callable
import os
from ranger.weather import get_weather, get_travel_duration

class Router:
    def __init__(self):
        self.agent = CodeAgent(
            tools=[get_weather, get_travel_duration],
            model=OpenAIServerModel(model_id="gpt-4"),
            additional_authorized_imports=["datetime"]
        )

    def route(self, query: str) -> str:
        """Route the query to the appropriate handler using the agent"""
        response = self.agent.run(f"""
        Analyze this query and use the appropriate tool to answer it:
        Query: {query}
        
        If the query is about weather, use the get_weather tool.
        If the query is about travel time or directions, use the get_travel_duration tool.
        If the query is about both, use both tools and combine the information.
        
        Format your response in a clear, user-friendly way.
        """)
        
        return response 