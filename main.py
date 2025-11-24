# single_api_reset.py
import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("FIREBASE_API_KEY")  # <-- Web API key (from Project Settings)
if not API_KEY:
    raise RuntimeError("Set FIREBASE_API_KEY env var")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your front-end domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResetIn(BaseModel):
    email: EmailStr

@app.post("/api/reset-password")
def reset_password(payload: ResetIn):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
    body = {
        "requestType": "PASSWORD_RESET",
        "email": payload.email
    }

    # optional: include continueUrl to redirect after reset (must be an authorized domain)
    continue_url = os.environ.get("CONTINUE_URL")
    if continue_url:
        body["continueUrl"] = continue_url
        # optionally: body["handleCodeInApp"] = True

    try:
        resp = requests.post(url, json=body, timeout=10)
    except requests.RequestException as e:
        # network error
        return {"ok": False, "message": "Failed to contact Firebase."}

    # On errors Firebase returns JSON with error.message (e.g. EMAIL_NOT_FOUND).
    # For security, return neutral message to avoid telling whether account exists.
    return {"ok": True, "message": "If an account with that email exists, we've sent password reset instructions."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)