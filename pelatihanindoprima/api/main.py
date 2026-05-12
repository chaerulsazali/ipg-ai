from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Response, Request
import os
import uuid
from http import HTTPStatus
from pydantic import BaseModel
import tasks.celery_task as celeryTask
from celery.result import AsyncResult
import json
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from contextlib import asynccontextmanager
from http import HTTPStatus
import logging

TEXT_FOLDER = "files_text"
EXCEL_FOLDER = "files_excel"
IMAGE_FOLDER = "files_image"

os.makedirs(TEXT_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

TOKEN ="8763459920:AAHeb1lNc_vbdfXECTQVZS_a2gZ6_eZc5B0"
WEBHOOK_URL =os.getenv("WEBHOOK_URL", "https://jul-detection-grow-walter.trycloudflare.com/webhook")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo, Bot FastAPI Telegram berhasil berjalan 🚀 by Sazali"
    )

async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_size = update.message.photo[-1]
    file_id = photo_size.file_id
    file_unique_id = photo_size.file_unique_id
    width = photo_size.width
    height = photo_size.height
    file_size = photo_size.file_size

    reply_text = (
        f"<b>Received Image Metadata</b>\n"
        f"• Dimensions: {width}x{height}px\n"
        f"• File Size: {round(file_size / 1024, 2)} KB\n"
        f"• <code>file_id</code>: <code>{file_id}</code>\n"
        f"• <code>file_unique_id</code>: <code>{file_unique_id}</code>"
    )

    await update.message.reply_text(reply_text, parse_mode="HTML")

ptb = (
    Application.builder()
    .updater(None)
    .token(TOKEN)
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)

# Chat Bot
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle managers for the FastAPI app.
    """
    await ptb.bot.set_webhook(WEBHOOK_URL) # Register
    async with ptb:
        await ptb.start()
        yield
    await ptb.stop()

class ResearchInput(BaseModel):
    topic: str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: str | None = None
    error: str | None = None

class ItSupportInput(BaseModel):
    issue_description: str
    priority_level: str
    
app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):

    body = await request.body()

    # cek body kosong
    if not body:
        return {
            "status": "error",
            "message": "Empty request body"
        }

    try:
        req_json = await request.json()
        print("REQ JSON:", req_json)
        update = Update.de_json(req_json, ptb.bot)
        await ptb.process_update(update)
        return {
            "status": "success"
        }

    except Exception as e:
        print("WEBHOOK ERROR:", str(e))

        return {
            "status": "error",
            "message": str(e)
        }

ptb.add_handler(MessageHandler(filters.PHOTO, image_handler))
ptb.add_handler(CommandHandler("start", start_command))

@app.post("/tes")
async def tes():
   return {"message": "Hallo Dunia"}

# CrewAI Content
@app.post("/research")
async def research(researchInput: ResearchInput):
    task = celeryTask.research.delay(researchInput.topic)
    return {"task_id": task.id}

@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id:str):
    task_result = celeryTask.celery_app.AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task_result.state,
        "result": None,
        "error": None
    }

    if task_result.state == 'SUCCESS':
        response["result"] = task_result.result
    elif task_result.state == 'FAILURE':
        response["error"] = str(task_result.info)

    return response

# CrewAI IT Support
@app.post("/it_support")
async def it_support(itSupportInput: ItSupportInput):
    task = celeryTask.it_support.delay(itSupportInput.issue_description, itSupportInput.priority_level)    
    return {"task_id": task.id}

@app.get("/status_support/{task_id}", response_model=TaskStatus)
async def get_status(task_id:str):
    task_result = celeryTask.celery_app.AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task_result.state,
        "result": None,
        "error": None
    }

    if task_result.state == 'SUCCESS':
        response["result"] = task_result.result
    elif task_result.state == 'FAILURE':
        response["error"] = str(task_result.info)

    return response

# Crew AI Analisator
@app.post("/analisator")
async def research(researchInput: ResearchInput):
    task = celeryTask.research.delay(researchInput.topic)
    return {"task_id": task.id}

@app.get("/status_analisator/{task_id}", response_model=TaskStatus)
async def get_status(task_id:str):
    task_result = celeryTask.celery_app.AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task_result.state,
        "result": None,
        "error": None
    }

    if task_result.state == 'SUCCESS':
        response["result"] = task_result.result
    elif task_result.state == 'FAILURE':
        response["error"] = str(task_result.info)

    return response

# Crew AI File Analyzer
@app.post("/txt_analyzer")
async def txt_analyzer(file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="file must be TXT")
    
    file_extention = os.path.splitext(file.filename)[1] or ".txt"
    unique_name = f"{uuid.uuid4().hex}{file_extention}"
    file_loc = os.path.join(TEXT_FOLDER, unique_name)

    content = await file.read()
    with open(file_loc, "wb") as f:
        f.write(content)

    task = celeryTask.file_txt_analyzer.delay(file_loc)

    # response = {
    #     "task_id": task.id,
    #     "file_loc": file_loc
    # }

    # return response
    return {"task_id": task.id,"file_loc": file_loc}

@app.get("/status_file/{task_id}", response_model=TaskStatus)
async def get_status(task_id:str):
    task_result = celeryTask.celery_app.AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task_result.state,
        "result": None,
        "error": None
    }

    if task_result.state == 'SUCCESS':
        if (isinstance(task_result.result, str)):
            try:
                response["result"] = json.load(task_result.result)
            except Exception as e:
                response["result"] = task_result.result
        else:
            response["result"] = task_result.result
    elif task_result.state == 'FAILURE':
        response["error"] = str(task_result.info)

    return response

# Crew Anomali Excel
@app.post("/excel_anomali")
async def excel_anomali(file: UploadFile = File(...)):
    if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        raise HTTPException(status_code=400, detail="file must be Excel")
    
    file_extention = os.path.splitext(file.filename)[1] or ".xlsx"
    unique_name = f"{uuid.uuid4().hex}{file_extention}"
    file_loc = os.path.join(EXCEL_FOLDER, unique_name)

    content = await file.read()
    with open(file_loc, "wb") as f:
        f.write(content)

    task = celeryTask.deteksi_anomali_excel.delay(file_loc)

    # response = {
    #     "task_id": task.id,
    #     "file_loc": file_loc
    # }

    # return response
    return {"task_id": task.id,"file_loc": file_loc}

# Crew Detection Helmet
@app.post("/deteksi_helmet")
async def deteksi_helmet(file: UploadFile = File(...)):
    if file.content_type != "image/jpeg":
        raise HTTPException(status_code=400, detail="file must be images")
    
    file_extention = os.path.splitext(file.filename)[1] or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{file_extention}"
    file_loc = os.path.join(IMAGE_FOLDER, unique_name)

    content = await file.read()
    with open(file_loc, "wb") as f:
        f.write(content)

    task = celeryTask.deteksi_helmet.delay(file_loc)

    # response = {
    #     "task_id": task.id,
    #     "file_loc": file_loc
    # }

    # return response
    return {"task_id": task.id,"file_loc": file_loc}
