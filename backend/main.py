from fastapi import FastAPI #webframework for create API server
from pydantic import BaseModel #used to define and validate structured data(JSON)
from fastapi.middleware.cors import CORSMiddleware #allows frontend(React) to run on a different port to communicate with backend safely
from youtube_utils import extract_video_id, get_transcript

##Instantiates my API application
app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#Creates a pydantic model to validate incoming JSON
class VideoRequest(BaseModel):
    url: str

@app.post("/summarize") #defines an endpoint for POST requests at /summarize
def summarize_video(request: VideoRequest): #automatically parses the incoming JSON into a Python object)
    return {"summary": f"Summary of video at {request.url}"} #FastAPI converts the Python dictionary to JSON and sends it back to the frontend

@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}