import io
from contextlib import redirect_stdout
from typing import List, Dict, Union

class PythonRepl:
    def __init__(
            self, 
            model: str = "gpt-4-0613", 
            temperature: float = 0.2, 
            top_p: float = 1.0, 
            frequency_penalty: float = 0.0, 
            presence_penalty: float = 0.0
            ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.function_params = self.python_repl_params
        self.system_message = """# Python REPL Agent
You have access to a Python Interpreter through your python_repl function.
Think steps ahead and make sure the code you execute correctly handles the users request.
If anything is unclear, ask the user for clarification.
When you are certain that the code is safe to execute, and correct, use the python_repl function to execute it.
If it is a calculation, ALWAYS print the result.
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
    def system_message(self):
        return self._system_message
    
    @system_message.setter
    def system_message(self, value):
        self._system_message = value

    def python_repl(self, code: str) -> str:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            try:
                exec(code, {"__name__": "__main__"})
            except Exception as e:
                return f"An error occurred while running the code: {str(e)}"
        return buffer.getvalue()

    @property
    def python_repl_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
            {
                "name": "python_repl",
                "description": "Executes Python code and returns the output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "The Python code to execute."},
                    },
                    "required": ["code"],
                },
            }
        ]
