from typing import Dict, List, Union

class HelpAgent:
    def __init__(
            self, 
            model: str = "gpt-4-0613", 
            temperature: float = 0.1, 
            top_p: float = 1.0, 
            frequency_penalty: float = 0.0, 
            presence_penalty: float = 0.0
            ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.function_params = self.help_params
        self.system_message = """# Help Agent
You call the help function and return the list of available commands.
"""

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    @property
    def top_p(self):
        return self._top_p

    @top_p.setter
    def top_p(self, value):
        self._top_p = value

    @property
    def frequency_penalty(self):
        return self._frequency_penalty

    @frequency_penalty.setter
    def frequency_penalty(self, value):
        self._frequency_penalty = value

    @property
    def presence_penalty(self):
        return self._presence_penalty

    @presence_penalty.setter
    def presence_penalty(self, value):
        self._presence_penalty = value
        
    @property
    def system_message(self) -> str:
        return self._system_message
    
    @system_message.setter
    def system_message(self, value):
        self._system_message = value

    def help(self) -> str:
        return """
### Available commands:
* /python - python interpreter
* /wikidata - wikidata sparql handler
* /review - performs a review of code following a strict response format
* /brainstorm [n] - returns a list of n ideas for the topic following a strict response format
* /write_spec - Writes a spec for the brainstorm n following a strict response format
* /ticket - creates a ticket for the brainstorm/spec following a strict response format
* /write_tests - writes tests for the ticket / file from ticket
* /write_code - writes code for the ticket / file from ticket
"""

    @property
    def help_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
            {
                "name": "help",
                "description": "Displays help message",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]
