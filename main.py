from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from sse_starlette.sse import EventSourceResponse
import asyncio
import uvicorn
from chatbot import run_conversation
from typing import List, Dict, Tuple
from pydantic import BaseModel
from markdown import markdown
import time
from agents.csv_agent import CSVHandler
from system_messages.system import (
    function_res_agent,
    base_system_message,
    help_agent,
    )

csv_handler = CSVHandler()

STREAM_DELAY = 1  # second
RETRY_TIMEOUT = 15000  # milisecond

app = FastAPI(docs_url="/documentation", redoc_url=None)

class RunConvoForm(BaseModel):
    chat: str

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize global conversation history
conversation = [{"role": "assistant", "content": "Hello! I am your Personal Assistant. Type /help to see the available commands and functions. "}]

# Initialize index of conversations
conversations = []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    global conversation
    conversation = [{"role": "assistant", "content": "Hello! I am your Personal Assistant. Type /help to see the available commands and functions. "}]
    return templates.TemplateResponse("index.html", {"request": request, "conversation": conversation})

@app.get("/settings", response_class=HTMLResponse)
async def read_settings(request: Request, settings=help_agent):
    help_html = markdown(settings, extensions=['fenced_code', 'codehilite'])
    return templates.TemplateResponse("settings.html", {"request": request, "help_html": help_html})

@app.get("/get_history", response_class=HTMLResponse)
async def read_history(request: Request):
    global conversation
    global conversations
    return templates.TemplateResponse("chat_history.html", {"request": request, "conversations": conversations})

@app.get("/load_history", response_class=HTMLResponse)
async def read_conversation(request: Request, name: str = None):
    global conversations
    global conversation
    
    # Find the conversation with the matching name
    for convo in conversations:
        if convo['name'] == name:
            conversation = convo["conversation"]
            break
    # Parse the conversation into HTML, turning the content key into html
    conversation_html = []
    for message in conversation:
        if message['role'] == 'assistant':
            message_html = markdown(message['content'], extensions=['fenced_code', 'codehilite'])
            conversation_html.append({"role": message['role'], "content": message_html})
        else:
            conversation_html.append({"role": message['role'], "content": message['content']})
            
    return templates.TemplateResponse("load_history.html", {"request": request, "conversation": conversation_html})

@app.delete("/delete_history", response_class=HTMLResponse)
async def delete_conversation(request: Request, name: str = None):
    global conversations
    global conversation
    
    # Find the conversation with the matching name
    for convo in conversations:
        if convo['name'] == name:
            conversations.remove(convo)
            break
    
    return templates.TemplateResponse("chat_history.html", {"request": request, "conversations": conversations})

@app.get("/new_chat", response_class=HTMLResponse)
async def new_chat(request: Request):
    global conversation
    global conversations
    conversation = [{"role": "assistant", "content": "Hello! I am your Personal Assistant. Type /help to see the available commands and functions. "}]
    conversation_name = f"Conversation {len(conversations) + 1}"
    conversations.append({"name": conversation_name, "conversation": conversation})
    return templates.TemplateResponse("new_chat.html", {"request": request, "conversation": conversation})

@app.post("/run_convo", response_class=HTMLResponse)
async def run_convo_route(request: Request, chat: str = Form(...)):
    global conversation
    global conversations
    result = run_conversation(chat, conversation)
    completed_conversation = ""
    for chunk in result:
        # the chunk can either have the key completion or choices
        if "choices" in chunk:
            if chunk.choices[0].finish_reason != "stop":
                print(chunk.choices[0].delta.content)
                completed_conversation += chunk.choices[0].delta.content
        elif "stop_reason" in chunk and chunk.stop_reason == None:
            print(chunk.completion)
            completed_conversation += chunk.completion
        else:
            print(chunk.completion)
            completed_conversation += chunk.completion
            
            
        
    conversation.append({
        "role": "user",
        "content": chat,
    })
    conversation.append({
        "role": "assistant",
        "content": completed_conversation,
    })

    result_html = markdown(completed_conversation, extensions=['fenced_code', 'codehilite'])
    return templates.TemplateResponse("conversation.html", {"request": request, "result_html": result_html, "chat": chat})

@app.get("/stream")
async def message_stream(request: Request, chat: str = Form(...)):
    global conversation
    
    def event_generator():
        global conversation
        global conversations
        result = run_conversation(chat, conversation)
        completed_conversation = ""
        for chunk in result:
            # the chunk can either have the key completion or choices
            if "choices" in chunk:
                if chunk.choices[0].finish_reason != "stop":
                    print(chunk.choices[0].delta.content)
                    completed_conversation += chunk.choices[0].delta.content
            elif "stop_reason" in chunk and chunk.stop_reason == None:
                print(chunk.completion)
                completed_conversation += chunk.completion
            else:
                print(chunk.completion)
                completed_conversation += chunk.completion
                
                
            
        conversation.append({
            "role": "user",
            "content": chat,
        })
        conversation.append({
            "role": "assistant",
            "content": completed_conversation,
        })
        
        result_html = markdown(completed_conversation, extensions=['fenced_code', 'codehilite'])
        yield {
            "event": "message",
            "data": result_html,
        }
        yield {
            "event": "message",
            "data": chat,
        }

    return EventSourceResponse(event_generator())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
