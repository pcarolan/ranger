import os
import logging
import requests

logger = logging.getLogger(__name__)

class ClaudeServerModel:
    def __init__(self, model_id: str = "claude-sonnet-4-20250514"):
        self.model_id = model_id
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
        self.api_url = "https://api.anthropic.com/v1/messages"
        logger.debug("ClaudeServerModel initialized with model_id: %s", model_id)

    def generate(self, prompt: str, stop_sequences: list = None) -> str:
        """
        Generate a response using the Claude API.
        
        Args:
            prompt: The input prompt for the model.
            stop_sequences: Optional list of sequences where the model should stop generating.
            
        Returns:
            The generated response as a string.
        """
        if not isinstance(prompt, str) or not prompt.strip():
            logger.error("Prompt must be a non-empty string. Got: %r", prompt)
            raise ValueError("Prompt must be a non-empty string.")
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        if stop_sequences:
            payload["stop_sequences"] = stop_sequences
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            if response.status_code != 200:
                logger.error("Anthropic API error %s: %s", response.status_code, response.text)
            response.raise_for_status()
            result = response.json()
            return result.get("content", [{}])[0].get("text", "")
        except Exception as e:
            logger.error("Error generating response from Claude API: %s", str(e))
            raise 