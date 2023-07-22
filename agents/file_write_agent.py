from typing import List, Dict, Union
import os
from utils import ensure_directory_exists, is_valid_filename

from constants import DATA_DIR

class FileWriter:
    def __init__(
            self, model: str = "gpt-4-0613", 
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
        self.function_params = self.write_file_params + self.read_file_params + self.edit_file_params
        self.write_system_message = """# Write File Agent
This agent is responsible for writing files.
Available directories:
For general files:
'data/'
For general code files:
'data/code/'
For code projects:
'data/code/projects/'
"""
        self.read_system_message = """# Read File Agent
This agent is responsible for reading files.
"""
        self.edit_system_message = """# Edit File Agent
This agent is responsible for editing files.
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
    
    def write_file(self, filename: str, content: str, directory: str = None) -> str:
        if not is_valid_filename(filename):
            return f"Invalid filename: {filename}"

        if directory is None:
            directory = DATA_DIR

        ensure_directory_exists(directory)    
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return f"File '{filename}' has been successfully written to {directory}."
        except Exception as e:
            return f"An error occurred while writing the file: {str(e)}"

    def read_file(self, filename: str) -> str:
        content = None
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            content = f"The file '{filename}' does not exist."
        except Exception as e:
            content = f"An error occurred while reading the file: {str(e)}"
        return content

    def edit_file(self, filepath: str, changes: List[Dict]) -> str:
        try:
            # Read the file into a list of lines
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Apply the changes
            for change in changes:
                start, end = change['range']  # get the start and end line numbers

                # Ensure the line numbers are valid
                if end > len(lines):
                    return f"Line number {end} is out of range in file {filepath}."

                # Replace the range of lines with the replacement content
                lines[start-1:end] = [change['replacementcontent'] + '\n']

            # Write the modified lines back to the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            return f"File '{filepath}' has been successfully edited."

        except FileNotFoundError:
            return f"The file '{filepath}' does not exist."
        except Exception as e:
            return f"An error occurred while editing the file: {str(e)}"



    @property
    def write_file_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
            {
                "name": "write_file",
                "description": "Writes a file to the system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "The filename for the new entry."},
                        "content": {"type": "string", "description": "The content for the new entry."},
                        "directory": {"type": "string", "description": "The directory to write the file to. The directories 'data/', 'data/code/', and 'data/code/projects/' are available."}
                    },
                    "required": ["filename", "content"],
                },
            }
        ]
    
    @property
    def read_file_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
            {
                "name": "read_file",
                "description": "Reads a file from the system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "The filename to read."},
                    },
                    "required": ["filename"],
                },
            }
        ]
    
    @property
    def edit_file_params(self) -> List[Dict[str, Union[str, Dict]]]:
        return [
            {
                "name": "edit_file",
                "description": "Edits the provided file by replacing the specified lines with the provided content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "The path to the file to edit."},
                        "changes": {
                            "type": "array",
                            "description": "The changes to apply to the file.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "range": {
                                        "type": "array",
                                        "description": "The line numbers to replace.",
                                        "items": {"type": "integer"},
                                    },
                                    "replacementcontent": {
                                        "type": "string",
                                        "description": "The content to replace the lines with.",
                                    },
                                },
                                "required": ["range", "replacementcontent"],
                            },
                        },
                    },
                    "required": ["filepath", "changes"],
                },
            }
        ]