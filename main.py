import uvicorn
import dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel
from fastapi import HTTPException
from starlette.status import HTTP_307_TEMPORARY_REDIRECT
from markdown import markdown
from chatbot.chatbot import run_conversation
from chatbot.system_messages.system import (
    help_agent,
    )
#from db.database import (
#    get_user_conversations,
#    get_conversation_messages,
#    create_conversation,
#    add_message_to_conversation,
#    login_user
#)

#envs = dotenv.dotenv_values(".env")
#SECRET_KEY = envs["SECRET_KEY"]

app = FastAPI(docs_url="/documentation", redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize global conversation history
conversation = []

# Initialize index of conversations
conversations = []

class RunConvoForm(BaseModel):
    chat: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    global conversation
    return FileResponse("static/index.html")

@app.get("/settings", response_class=HTMLResponse)
async def read_settings(request: Request, settings=help_agent):
    help_html = markdown(settings, extensions=['fenced_code', 'codehilite'])
    return templates.TemplateResponse("settings.html", {"request": request, "help_html": help_html})

@app.get("/get_history", response_class=HTMLResponse)
async def read_history(request: Request):
    global conversations
    #convo = get_user_conversations(1)
    return templates.TemplateResponse("chat_history.html", {"request": request, "conversations": conversations})

@app.delete("/delete_history", response_class=HTMLResponse)
async def delete_conversation(request: Request, name: str = None):
    global conversations
    global conversation
    #delete_conversation(name)
    #conversations = get_conversations()
    # Find the conversation with the matching name
    for convo in conversations:
        if convo['name'] == name:
            conversations.remove(convo)
            break
    
    return templates.TemplateResponse("chat_history.html", {"request": request, "conversations": conversations})

@app.post("/update_history_input", response_class=HTMLResponse)
async def update_conversation(request: Request, name: str = None):
    global conversations
    global conversation
    convo_name = ""
    # Find the conversation with the matching name
    for convo in conversations:
        if convo['name'] == name:
            convo_name = convo['name']
            convo['conversation'] = conversation
            break
        
    return templates.TemplateResponse("input.html", {"request": request, "conversation": conversation, "name": name, "convo_name": convo_name})

@app.put("/update_history_name", response_class=HTMLResponse)
async def update_conversation(request: Request, name: str = Form(...), new_name: str = Form(...)):
    global conversations
    global conversation
    query_params = request.query_params
    # Find the conversation with the matching name
    for convo in conversations:
        if convo['name'] == name:
            print(convo['name'])
            convo['name'] = new_name
            print(convo['name'])
            break
        
    return templates.TemplateResponse("chat_history.html", {"request": request, "conversations": conversations})

@app.get("/new_chat", response_class=HTMLResponse)
async def new_chat(request: Request):
    global conversation
    global conversations
    
    conversation = [{"role": "assistant", "content": "Hello! I am your Personal Assistant. Type /help to see the available commands and functions. "}]
    conversation_name = f"Conversation {len(conversations) + 1}"
    conversations.append({"name": conversation_name, "conversation": conversation})
    #create_conversation(1, conversation_name)
    #add_message_to_conversation(1, 7, "assistant", "Hello! I am your Personal Assistant. Type /help to see the available commands and functions. ")
    return templates.TemplateResponse("new_chat.html", {"request": request, "conversation": conversation})

@app.get("/chat/{name}", response_class=HTMLResponse)
async def read_conversation(request: Request, name: str = None):
    global conversations
    global conversation
    #print(name)
    #conv = get_conversation_messages(name, 1)
    #print(conv)
    #if not conv:
    #    raise HTTPException(status_code=404, detail="Conversation or messages not found")
    # Find the conversation with the matching name
    for convo in conversations:
        if convo['name'] == name:
            conversation = convo["conversation"]
            break
    else:
        raise HTTPException(
            status_code=HTTP_307_TEMPORARY_REDIRECT,
            detail="Chat does not exist",
            headers={"Location": "/"},
        )

    # Parse the conversation into HTML, turning the content key into html
    conversation_html = []
    for message in conversation:
        if message['role'] == 'assistant':
            message_html = markdown(message['content'], extensions=['fenced_code', 'codehilite'])
            conversation_html.append({"role": message['role'], "content": message_html})
        else:
            conversation_html.append({"role": message['role'], "content": message['content']})
            
    return templates.TemplateResponse("chat.html", {"request": request, "conversation": conversation_html})


@app.post("/chat", response_class=HTMLResponse)
async def run_convo_route(request: Request, chat: str = Form(...)):
    global conversation
    global conversations
    
    result = run_conversation(chat, conversation) 
    completed_conversation = ""
    # Check if result is iterable
    
    if isinstance(result, str):  # Result is returned as a string from one of the functions
        completed_conversation = result
    else:  # Result is a stream from OpenAI or Athropic Agents. Iterate through the stream
        for chunk in result:
            # the chunk can either have the key completion or choices depending on the API
            if "choices" in chunk:
                if chunk['choices'][0]['finish_reason'] != "stop":
                    print(chunk['choices'][0]['delta']['content'])
                    completed_conversation += chunk['choices'][0]['delta']['content']
                    
            elif "stop_reason" in chunk and chunk['stop_reason'] == None:
                print(chunk['completion'])
                completed_conversation += chunk['completion']
            else:
                print(chunk['completion'])
                completed_conversation += chunk['completion']
    
    #add_message_to_conversation(id, "user", chat)      
    conversation.append({
        "role": "user",
        "content": chat,
    })
    #add_message_to_conversation(id, "assistant", completed_conversation)
    conversation.append({
        "role": "assistant",
        "content": completed_conversation,
    })

    result_html = markdown(completed_conversation, extensions=['fenced_code', 'codehilite'])
    return templates.TemplateResponse("conversation.html", {"request": request, "result_html": result_html, "chat": chat})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


