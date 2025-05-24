from ranger.models.openai import OpenAIServerModel
from ranger.models.claude import ClaudeServerModel

class RangerCore:
    @staticmethod
    def check_status() -> str:
        """Check the status of all APIs."""
        openai_status = OpenAIServerModel.check_status()
        claude_status = ClaudeServerModel.check_status()
        return f"OpenAI: {openai_status}, Claude: {claude_status}"

    @staticmethod
    def get_weather_status() -> str:
        """Check the status of the OpenAI and Claude APIs."""
        return RangerCore.check_status() 