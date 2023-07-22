import logging
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from dotenv import load_dotenv
import os

class AnthropicAgent:
    def __init__(
            self,
            prompt: str = "",
            model: str = "claude-2",
            conversation: dict = [],
            max_tokens_to_sample: int = 1000000):
            
        self.model = model
        self.max_tokens_to_sample = max_tokens_to_sample
        self.prompt = prompt
        self.conversation = conversation
        load_dotenv()
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def max_tokens_to_sample(self):
        return self._max_tokens_to_sample

    @max_tokens_to_sample.setter
    def max_tokens_to_sample(self, value):
        self._max_tokens_to_sample = value

    @property
    def prompt(self):
        return self._prompt
    
    @prompt.setter
    def prompt(self, value):
        self._prompt = value

    def call(self, prompt: str = "", model: str = "claude-2", max_tokens_to_sample: int = 1000000, conversation: dict = []):
        try:
            completion = self.anthropic.completions.create(
                model=model,
                max_tokens_to_sample=max_tokens_to_sample,
                prompt=f"Conversation history: {conversation} - {HUMAN_PROMPT} {prompt} {AI_PROMPT}",
            )
            return completion.completion
        except Exception as e:
            logging.error(f"Anthropic API call failed: {str(e)}")
            return "Anthropic API call failed due to an internal server error."
