from agents.csv_agent import CSVHandler
from agents.python_agent import PythonRepl
from agents.kb_agent import KnowledgebaseHandler
from agents.history_agent import HistoryHandler
from agents.file_write_agent import FileWriter
from agents.scrape_agent import Scraper
from agents.wikidata_agent import WikidataAgent
from agents.image_agent import ImageAgent
from agents.help_agent import HelpAgent
from agents.write_project import ProjectWriter
from system_messages.system import (
    review_agent, 
    brainstorm_agent, 
    ticket_agent, 
    spec_writer, 
    code_writer
    )


class FunctionMapper:
    def __init__(self):
        self.prompt = ""
        self.csv_handler = CSVHandler()
        self.python_repl = PythonRepl()
        self.kb_handler = KnowledgebaseHandler()
        self.history_handler = HistoryHandler()
        self.file_handler = FileWriter()
        self.scraper = Scraper()
        self.wikidata_agent = WikidataAgent()
        self.image_agent = ImageAgent()
        self.help_agent = HelpAgent()
        self.write_project = ProjectWriter()
        self.functions_that_append_to_conversation = {
            "knowledgebase_read_entry", 
            "knowledgebase_list_entries", 
            "read_history_entry", 
            "list_history_entries", 
            "read_file",
            "read_csv_columns",
            "scrape_webpage",
            "help"
        }

        self.function_map = {
            "python_repl": self.python_repl.python_repl,
            "knowledgebase_read_entry": self.kb_handler.knowledgebase_read_entry,
            "knowledgebase_list_entries": self.kb_handler.knowledgebase_list_entries,
            "knowledgebase_create_entry": self.kb_handler.knowledgebase_create_entry,
            "read_history_entry": self.history_handler.read_history_entry,
            "write_history_entry": self.history_handler.write_history_entry,
            "list_history_entries": self.history_handler.list_history_entries,
            "read_csv_columns": self.csv_handler.read_csv_columns,
            "write_file": self.file_handler.write_file,
            "read_file": self.file_handler.read_file,
            "edit_file": self.file_handler.edit_file,
            "wikidata_sparql_query": self.wikidata_agent.wikidata_sparql_query,
            "scrape_webpage": self.scraper.scrape_webpage,
            "image_to_text": self.image_agent.image_to_text,
            "help": self.help_agent.help,
            "write_files": self.write_project.write_files,
        }

        self.agents = {
                "/csv": {
                    "name": "CSV Agent",
                    "agent": self.csv_handler,
                    "system_message": self.csv_handler.system_message,
                    "function_params": self.csv_handler.read_csv_columns_params,
                    "is_function": True,
                    "command_length": len("/csv")
                },
                "/python": {
                    "name": "Python Agent",
                    "agent": self.python_repl,
                    "system_message": self.python_repl.system_message,
                    "function_params": self.python_repl.python_repl_params,
                    "is_function": True,
                    "command_length": len("/python")
                },
                "/wikidata": {
                    "name": "Wikidata Agent",
                    "agent": self.wikidata_agent,
                    "system_message": self.wikidata_agent.system_message,
                    "function_params": self.wikidata_agent.wikidata_sparql_query_params,
                    "is_function": True,
                    "command_length": len("/wikidata")
                },
                "/kb": {
                    "name": "Knowledgebase Agent",
                    "agent": self.kb_handler,
                    "system_message": self.kb_handler.system_message,
                    "function_params": self.kb_handler.knowledgebase_params,
                    "is_function": True,
                    "command_length": len("/kb")
                },
                "/history": {
                    "name": "History Agent",
                    "agent": self.history_handler,
                    "system_message": self.history_handler.system_message,
                    "function_params": self.history_handler.history_params,
                    "is_function": True,
                    "command_length": len("/history")
                },
                "/scrape": {
                    "name": "Scrape Webpage Agent",
                    "agent": self.scraper,
                    "system_message": self.scraper.system_message,
                    "function_params": self.scraper.scrape_params,
                    "is_function": True,
                    "command_length": len("/scrape")
                },
                "/image": {
                    "name": "Image to Text Agent",
                    "agent": self.image_agent,
                    "system_message": self.image_agent.system_message,
                    "function_params": self.image_agent.image_to_text_params,
                    "is_function": True,
                    "command_length": len("/image")
                },
                "/help": {
                    "name": "Help Agent",
                    "agent": self.help_agent,
                    "system_message": self.help_agent.system_message,
                    "function_params": self.help_agent.help_params,
                    "is_function": True,
                    "command_length": len("/help")
                },
                "/review": {
                    "name": "Review Agent",
                    "system_message": review_agent,
                    "is_function": False,
                    "command_length": len("/review")
                },
                "/brainstorm": {
                    "name": "Brainstorm Agent",
                    "system_message": brainstorm_agent,
                    "is_function": False,
                    "command_length": len("/brainstorm")
                },
                "/ticket": {
                    "name": "Ticket Agent",
                    "system_message": ticket_agent,
                    "is_function": False,
                    "command_length": len("/ticket")
                },
                "/write_spec": {
                    "name": "Write Spec Agent",
                    "system_message": spec_writer,
                    "is_function": False,
                    "command_length": len("/write_spec")
                },
                "/write_code": {
                    "name": "Write Code Agent",
                    "system_message": code_writer,
                    "is_function": False,
                    "command_length": len("/write_code")
                },
                "/write_project": {
                    "name": "Write Project Agent",
                    "agent": self.write_project,
                    "system_message": self.write_project.system_message,
                    "function_params": self.write_project.write_files_params,
                    "is_function": True,
                    "command_length": len("/write_project")
                },
            }
