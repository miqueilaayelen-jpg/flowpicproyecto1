from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import time

app = FastAPI()

os.makedirs("uploads", exist_ok=True)
os.makedirs("stories", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/stories", StaticFiles(directory="stories"), name="stories")

likes_data = {}
stories = []


@app.get("/")
def home():
    return FileResponse("templates/index.html")


# POST NORMAL
@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    path = f"uploads/{file.filename}"

    with open(path, "wb") as buffer:
        buffer.write(await file.read())

    likes_data.setdefault(file.filename, 0)

    return {"ok": True}


# HISTORIAS
@app.post("/story")
async def upload_story(file: UploadFile = File(...)):

    filename = f"{int(time.time())}_{file.filename}"
    path = f"stories/{filename}"

    with open(path, "wb") as buffer:
        buffer.write(await file.read())

    stories.append({
        "url": "/stories/" + filename
    })

    return {"ok": True}


@app.get("/stories_feed")
def get_stories():
    return {"stories": stories}


@app.get("/feed")
def feed():

    files = os.listdir("uploads")

    return {
        "images": [
            {
                "url": "/uploads/" + f,
                "name": f,
                "likes": likes_data.get(f, 0)
            }
            for f in files
        ]
    }


@app.post("/like/{file_name}")
def like(file_name: str):
    likes_data[file_name] = likes_data.get(file_name, 0) + 1
    return {"ok": True}