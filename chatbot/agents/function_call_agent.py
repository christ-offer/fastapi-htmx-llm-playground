import openai 
from openai import OpenAIError
import logging

class FunctionCallAgent:
    def __init__(
            self, 
            prompt: str = "",
            conversation: dict = [],
            system_message: str = "",
            function_params: dict = [],
            model: str = "gpt-3.5-turbo-16k-0613", 
            temperature: float = 0.0, 
            top_p: float = 1.0, 
            frequency_penalty: float = 0.0, 
            presence_penalty: float = 0.0
            ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.prompt = prompt
        self.conversation = conversation
        self.system_message = system_message
        self.function_params = function_params
    
    def call(
            self,
            prompt: str = "",
            conversation: dict = [],
            system_message: str = "",
            function_params: dict = [],
            model: str = "gpt-3.5-turbo-16k-0613", 
            temperature: float = 0.0, 
            top_p: float = 1.0, 
            frequency_penalty: float = 0.0, 
            presence_penalty: float = 0.0
            ):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                messages=[
                    {"role": "system", "content": system_message}
                ] + conversation + [
                    {"role": "user", "content": prompt}
                ],
                functions=function_params,
                function_call="auto",
            )
        except OpenAIError as error:
            logging.error(f"OpenAI API call failed: {str(error)}")
            return "OpenAI API call failed due to an internal server error.", conversation
        except openai.error.APIConnectionError as e:
            print(f"Failed to connect to OpenAI API: {e}")
            return "Failed to connect to OpenAI.", conversation
        except openai.error.RateLimitError as e:
            print(f"OpenAI API request exceeded rate limit: {e}")
            return "Requests exceed OpenAI rate limit.", conversation
        return response["choices"][0]["message"], conversation
    