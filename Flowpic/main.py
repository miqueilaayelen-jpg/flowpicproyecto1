from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import time

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- STORAGE ----------------
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

users = {}
posts = []
messages = []

# ---------------- HOME ----------------
@app.get("/")
def home():
    return FileResponse("templates/index.html")

# ---------------- REGISTER ----------------
@app.post("/register")
def register(data: dict = Body(...)):

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"ok": False, "msg": "faltan datos"}

    if username in users:
        return {"ok": False, "msg": "usuario ya existe"}

    users[username] = {
        "password": password,
        "avatar": "/uploads/default.png"
    }

    return {"ok": True, "msg": "usuario creado"}

# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: dict = Body(...)):

    username = data.get("username")
    password = data.get("password")

    if username not in users:
        return {"ok": False, "msg": "usuario no registrado"}

    if users[username]["password"] != password:
        return {"ok": False, "msg": "contraseña incorrecta"}

    return {"ok": True}

# ---------------- UPLOAD ----------------
@app.post("/upload")
async def upload(file: UploadFile = File(...), username: str = Body(...)):

    filename = f"{int(time.time())}_{file.filename}"
    path = f"uploads/{filename}"

    content = await file.read()

    with open(path, "wb") as f:
        f.write(content)

    posts.append({
        "user": username,
        "file": filename,
        "likes": 0
    })

    return {"ok": True}

# ---------------- FEED ----------------
@app.get("/feed")
def feed():

    return {
        "images": [
            {
                "url": "/uploads/" + p["file"],
                "name": p["file"],
                "likes": p["likes"],
                "user": p["user"],
                "avatar": users.get(p["user"], {}).get("avatar", "/uploads/default.png")
            }
            for p in reversed(posts)
        ]
    }

# ---------------- PROFILE ----------------
@app.get("/profile/{username}")
def profile(username: str):

    return {
        "images": [
            {
                "url": "/uploads/" + p["file"],
                "likes": p["likes"]
            }
            for p in posts if p["user"] == username
        ]
    }

# ---------------- LIKE ----------------
@app.post("/like/{name}")
def like(name: str):

    for p in posts:
        if p["file"] == name:
            p["likes"] += 1

    return {"ok": True}

# ---------------- AVATAR ----------------
@app.post("/set_avatar")
async def set_avatar(file: UploadFile = File(...), username: str = Body(...)):

    filename = f"avatar_{username}_{int(time.time())}.png"
    path = f"uploads/{filename}"

    content = await file.read()

    with open(path, "wb") as f:
        f.write(content)

    users[username]["avatar"] = "/uploads/" + filename

    return {"ok": True, "avatar": "/uploads/" + filename}

# ---------------- CHAT ----------------
@app.post("/chat/send")
def send_msg(data: dict = Body(...)):

    messages.append({
        "user": data.get("user"),
        "text": data.get("text"),
        "time": time.time()
    })

    return {"ok": True}

@app.get("/chat")
def get_chat():
    return {"messages": messages}
