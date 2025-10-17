# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import google.generativeai as genai
import os

# ---------------------------
# Configure Gemini
# ---------------------------
# set your Gemini API key
# (you can set it as environment variable or directly here)
os.environ["GOOGLE_API_KEY"] = "AIzaSyCS979HYonwYLVvZGW-XeOBXkp8fY5EiFs"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

app = FastAPI(title="AI Study Buddy - LLM Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Schemas
# ---------------------------
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str


# ---------------------------
# Endpoint
# ---------------------------
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    question = req.question.strip()
    if not question:
        return {"answer": "Please enter a valid question."}

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            f"You are an AI Study Buddy chatbot that helps students with academic doubts.\n\nQuestion: {question}"
        )
        answer = response.text
    except Exception as e:
        answer = f"Error generating response: {str(e)}"

    return {"answer": answer}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
