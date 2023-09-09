import uvicorn
import dotenv
import asyncio
import uuid
from deta import Deta
from fastapi import FastAPI, Form, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.status import HTTP_307_TEMPORARY_REDIRECT
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from markdown import markdown
from chatbot.chatbot import run_conversation
from chatbot.system_messages.system import (
    help_agent,
    )

app = FastAPI(docs_url="/documentation", redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


deta = Deta()
db = deta.Base("conversations")


class RunConvoForm(BaseModel):
    chat: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return FileResponse("static/index.html")

@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/settings/usage", response_class=HTMLResponse)
async def read_usage(request: Request, usage=help_agent):
    usage_html = markdown(usage, extensions=['fenced_code', 'codehilite'])
    return templates.TemplateResponse("settings_tabs/usage.html", {"request": request, "usage_html": usage_html})

@app.get("/settings/settings", response_class=HTMLResponse)
async def read_settings(request: Request):
    return templates.TemplateResponse("settings_tabs/settings.html", {"request": request})

@app.get("/get_history", response_class=HTMLResponse)
async def read_history(request: Request):
    res = db.fetch()
    conversations = res.items

    while res.last:
        res = db.fetch(last=res.last)
        conversations += res.items  
    return templates.TemplateResponse("chat_history.html", {"request": request, "conversations": conversations})

@app.delete("/delete_history", response_class=HTMLResponse)
async def delete_conversation(request: Request, name: str = ""):
    res = db.fetch()
    conversations = res.items
    
    for convo in conversations:
        if convo['key'] == name:
            db.delete(name)
            break
    return Response(headers={"HX-Refresh": f"true"})

@app.post("/update_history_input", response_class=HTMLResponse)
async def update_conversation_input(request: Request, name: str = ""):
    res = db.fetch()
    conversations = res.items
    convo_name = ""
    print(name)
    for convo in conversations:
        if convo['key'] == name:
            print(convo)
            convo_name = convo['name']
            break
        
    return templates.TemplateResponse("input.html", {"request": request, "name": name, "convo_name": convo_name})

@app.put("/update_history_name", response_class=HTMLResponse)
async def update_conversation(request: Request, name: str = Form(...), new_name: str = Form(...)):
    res = db.fetch()
    conversations = res.items
    for convo in conversations:
        if convo['key'] == name:
            print(convo)
            db.update(
                {"name": new_name},
                name,
            )
            print(convo['name'])
            break
        
    return templates.TemplateResponse("chat_history.html", {"request": request, "conversations": conversations})

@app.get("/new_chat", response_class=HTMLResponse)
async def new_chat(request: Request):
    conversation = [{"role": "assistant", "content": "Hello! I am your Personal Assistant. Type /help to see the available commands and functions. "}]
    res = db.fetch()
    conversations = res.items
    conversation_name = f"Conversation {len(conversations) + 1}"
    conversation_key = str(uuid.uuid4())

    db.put({"conversation": conversation, "name": conversation_name}, conversation_key)    
    
    return Response(headers={"HX-Redirect": f"/chat/{conversation_key}"})

@app.get("/chat/{name}", response_class=HTMLResponse)
async def read_conversation(request: Request, name: str = ""):
    res = db.fetch()
    conversations = res.items
    conversation = db.get(name)
    
    for convo in conversations:
        if convo['key'] == name:
            #conversation = convo["conversation"]
            break
    else:
        raise HTTPException(
            status_code=HTTP_307_TEMPORARY_REDIRECT,
            detail="Chat does not exist",
            headers={"Location": "/"},
        )
    
    # Parse the conversation into HTML, turning the content key into html
    conversation_html = []
    for message in conversation['conversation']:
        if message['role'] == 'assistant':
            message_html = markdown(message['content'], extensions=['fenced_code', 'codehilite'])
            conversation_html.append({"role": message['role'], "content": message_html})
        else:
            conversation_html.append({"role": message['role'], "content": message['content']})
            
    return templates.TemplateResponse("chat.html", {"request": request, "conversation": conversation_html, "key": name})


@app.post("/chat", response_class=HTMLResponse)
async def run_convo_route(request: Request, chat: str = Form(...), key: str = Form(...)):
    conversation = []
    result = run_conversation(chat, conversation) 
    completed_conversation = ""
    if isinstance(result, str):  # Result is returned as a string from one of the functions
        completed_conversation = result
    else:  # Result is a stream from OpenAI or Athropic Agents. Iterate through the stream
        for chunk in result:
            # the chunk can either have the key completion or choices depending on the API
            if "choices" in chunk:
                if chunk['choices'][0]['finish_reason'] != "stop":
                    #print(chunk['choices'][0]['delta']['content'])
                    completed_conversation += chunk['choices'][0]['delta']['content']
            else:
                print(chunk.completion)
                completed_conversation += chunk.completion

    conversation.append({
        "role": "user",
        "content": chat,
    })
    user_update = {
        "conversation": db.util.append({
            "role": "user",
            "content": chat
            })
    }
    db.update(user_update, key)
    conversation.append({
        "role": "assistant",
        "content": completed_conversation,
    })
    assistant_update = {
        "conversation": db.util.append({
            "role": "assistant",
            "content": completed_conversation
            })
    }
    db.update(assistant_update, key)
    result_html = markdown(completed_conversation, extensions=['fenced_code', 'codehilite'])
    return templates.TemplateResponse("conversation.html", {"request": request, "result_html": result_html, "chat": chat})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


