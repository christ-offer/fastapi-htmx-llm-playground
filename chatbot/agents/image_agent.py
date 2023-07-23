import urllib
import requests
from PIL import Image
import os
import torch
import open_clip
from typing import Dict, List, Union

class ImageAgent:
    def __init__(
            self, 
            model: str = "gpt-4-0613", 
            temperature: float = 0.0, 
            top_p: float = 1.0, 
            frequency_penalty: float = 0.0, 
            presence_penalty: float = 0.0
            ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.function_params = self.image_to_text_params
        self.presence_penalty = presence_penalty
        self.system_message = """# Image to Text Agent
This agent creates a caption / description of an image.
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

    def image_to_text(self, image_path_or_url, seq_len=20):
        device = torch.device("cpu")

        try:
            model, _, transform = open_clip.create_model_and_transforms(
                "coca_ViT-L-14",
                pretrained="mscoco_finetuned_laion2B-s13B-b90k"
            )
            model.to(device)

            # Check if the image_path_or_url is a URL or local path
            if urllib.parse.urlparse(image_path_or_url).scheme in ['http', 'https']:
                response = requests.get(image_path_or_url)
                _, ext = os.path.splitext(urllib.parse.urlparse(image_path_or_url).path)
                file_name = urllib.parse.urlparse(image_path_or_url).path.split('/')[-1]
                with open(f'data/{file_name}', 'wb') as f:
                    f.write(response.content)
                image = Image.open(f'data/{file_name}').convert("RGB")
            else:
                image = Image.open(image_path_or_url).convert("RGB")

            im = transform(image).unsqueeze(0).to(device)

            with torch.no_grad(), torch.cuda.amp.autocast():
                generated = model.generate(im, seq_len=seq_len)

            return open_clip.decode(generated[0].detach()).split("<end_of_text>")[0].replace("<start_of_text>", "")

        except FileNotFoundError:
            return f"No file found at {image_path_or_url}"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    @property
    def image_to_text_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
            {
                "name": "image_to_text",
                "description": "Creates a caption / description of an image.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "The filename of the image to describe."},
                    },
                    "required": ["filename"],
                },
            }
        ]
