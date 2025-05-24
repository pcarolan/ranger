import os
import requests

class OpenAIServerModel:
    @staticmethod
    def check_status() -> str:
        """Check the status of the OpenAI API."""
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            return "❌ Not configured"
        try:
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {openai_key}"},
                timeout=5
            )
            if response.status_code == 200:
                return "✅ Connected"
            else:
                return f"❌ Error connecting (status {response.status_code})"
        except Exception as e:
            return f"❌ Error: {str(e)}" 