from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import time

app = FastAPI()

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# base en memoria
users = {}
likes = {}


# -------------------
# HOME
# -------------------
@app.get("/")
def home():
    return FileResponse("templates/index.html")


# -------------------
# REGISTER
# -------------------
@app.post("/register")
def register(data: dict = Body(default={})):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"ok": False, "msg": "faltan datos"}

    if username in users:
        return {"ok": False, "msg": "usuario ya existe"}

    users[username] = password

    print("USUARIOS:", users)

    return {"ok": True, "msg": "usuario creado"}


# -------------------
# LOGIN
# -------------------
@app.post("/login")
def login(data: dict = Body(default={})):
    username = data.get("username")
    password = data.get("password")

    if username not in users:
        return {"ok": False, "msg": "usuario no registrado"}

    if users[username] != password:
        return {"ok": False, "msg": "contraseña incorrecta"}

    return {"ok": True}


# -------------------
# UPLOAD
# -------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    filename = f"{int(time.time())}_{file.filename}"
    path = f"uploads/{filename}"

    content = await file.read()

    with open(path, "wb") as f:
        f.write(content)

    likes[filename] = 0

    return {"ok": True}


# -------------------
# FEED
# -------------------
@app.get("/feed")
def feed():

    files = os.listdir("uploads")

    return {
        "images": [
            {
                "url": "/uploads/" + f,
                "name": f,
                "likes": likes.get(f, 0)
            }
            for f in files
        ]
    }


# -------------------
# LIKE
# -------------------
@app.post("/like/{name}")
def like(name: str):
    likes[name] = likes.get(name, 0) + 1
    return {"ok": True}
