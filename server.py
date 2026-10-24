import os
import logging
from collections import defaultdict
from time import time

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GOD'S PLAN AI API")

# Replace "*" with your actual frontend origin
# before making the service publicly available.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)

MODEL_NAME = "gemini-3.8-flash"

# Simple per-process request limit.
# This is a basic safeguard, not production-grade rate limiting.
request_times = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 10


@app.get("/")
def home():
    return {"message": "GOD'S PLAN AI API is running!"}


@app.post("/chat")
async def chat(
    request: Request,
    question: str = Form(...),
    photo: UploadFile | None = File(default=None),
):
    question = question.strip()

    if not question and photo is None:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question or attach a photo.",
        )

    # Basic request limit by client IP.
    client_ip = request.client.host if request.client else "unknown"
    now = time()

    recent = [
        t for t in request_times[client_ip]
        if now - t < 60
    ]

    if len(recent) >= MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a minute.",
        )

    recent.append(now)
    request_times[client_ip] = recent

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="The server API key is not configured.",
        )

    contents = [
        question or "Please describe the attached photo."
    ]

    if photo is not None:
        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if photo.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Please upload a JPG, PNG, or WebP image.",
            )

        image_bytes = await photo.read()

        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Please choose an image smaller than 10 MB.",
            )

        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=photo.content_type,
            )
        )

    def generate():
        try:
            client = genai.Client(api_key=api_key)

            stream = client.models.generate_content_stream(
                model=MODEL_NAME,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are GOD'S PLAN AI, a helpful assistant. "
                        "Answer clearly and respectfully. "
                        "Understand attached images when possible. "
                        "Keep answers concise unless asked for detail."
                    ),
                    max_output_tokens=512,
                ),
            )

            for chunk in stream:
                if chunk.text:
                    yield chunk.text

        except Exception:
            logger.exception("Gemini generation failed")
            yield "\n\nSorry bro, something went wrong. Please try again."

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache"},
  )
