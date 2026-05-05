from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Response, Request
import os
import uuid
from http import HTTPStatus
from pydantic import BaseModel
import tasks.celery_task as celeryTask
from celery.result import AsyncResult
import json

TEXT_FOLDER = "files_text"

os.makedirs(TEXT_FOLDER, exist_ok=True)

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
    
app = FastAPI()
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
                response["result"] = json loads(task_result.result)
            except Exception as e:
                response["result"] = task_result.result
        else:
            response["result"] = task_result.result
    elif task_result.state == 'FAILURE':
        response["error"] = str(task_result.info)

    return response