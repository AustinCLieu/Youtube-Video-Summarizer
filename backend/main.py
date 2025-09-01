from fastapi import FastAPI #webframework for create API server
from pydantic import BaseModel #used to define and validate structured data(JSON)
from fastapi.middleware.cors import CORSMiddleware #allows frontend(React) to run on a different port to communicate with backend safely
from youtube_utils import extract_video_id, get_transcript
from summarizer_utils import summarize_transcript
import time
import logging

# Configure logging for better debugging and performance monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    model: str = "bart"

@app.post("/summarize") #defines an endpoint for POST requests at /summarize
def summarize_video(request: VideoRequest): #automatically parses the incoming JSON into a Python object)
    """
    Enhanced video summarization endpoint with performance monitoring and better error handling.
    
    This endpoint processes video URLs, extracts transcripts, and generates summaries
    using the specified AI model. Performance metrics are logged for optimization.
    
    Args:
        request: VideoRequest object containing URL and model preference
    
    Returns:
        JSON response with summary, model used, and performance metrics
    """
    start_time = time.time()
    
    try:
        # Log the incoming request for monitoring
        logger.info(f"Processing video summarization request: URL={request.url}, Model={request.model}")
        
        # Step 1: Extract video ID (performance monitoring)
        video_extraction_start = time.time()
        video_id = extract_video_id(request.url)
        video_extraction_time = time.time() - video_extraction_start
        logger.info(f"Video ID extracted in {video_extraction_time:.2f}s: {video_id}")
        
        # Step 2: Get transcript (performance monitoring)
        transcript_start = time.time()
        transcript = get_transcript(video_id)
        transcript_time = time.time() - transcript_start
        
        if not transcript or transcript.startswith("No transcript") or transcript.startswith("Transcript error"):
            logger.warning(f"Failed to get transcript: {transcript}")
            return {"error": f"Could not retrieve transcript: {transcript}"}
        
        logger.info(f"Transcript retrieved in {transcript_time:.2f}s, length: {len(transcript)} characters")
        
        # Step 3: Generate summary (performance monitoring)
        summary_start = time.time()
        summary = summarize_transcript(transcript, model=request.model)
        summary_time = time.time() - summary_start
        
        if not summary or summary.startswith("Failed to generate"):
            logger.error(f"Failed to generate summary: {summary}")
            return {"error": f"Summary generation failed: {summary}"}
        
        # Calculate total processing time
        total_time = time.time() - start_time
        
        # Log performance metrics
        logger.info(f"Summary generated in {summary_time:.2f}s, total time: {total_time:.2f}s")
        logger.info(f"Performance breakdown - Video ID: {video_extraction_time:.2f}s, Transcript: {transcript_time:.2f}s, Summary: {summary_time:.2f}s")
        
        # Return enhanced response with performance metrics
        return {
            "summary": summary, 
            "model_used": request.model,
            "performance_metrics": {
                "total_processing_time": round(total_time, 2),
                "video_extraction_time": round(video_extraction_time, 2),
                "transcript_retrieval_time": round(transcript_time, 2),
                "summary_generation_time": round(summary_time, 2),
                "transcript_length": len(transcript),
                "summary_length": len(summary)
            }
        }
    
    except ValueError as e:
        # Handle invalid URL format
        logger.error(f"Invalid URL format: {request.url}, Error: {str(e)}")
        return {"error": f"Invalid video URL format: {str(e)}"}
    
    except Exception as e:
        # Handle any other unexpected errors
        total_time = time.time() - start_time
        logger.error(f"Unexpected error in /summarize after {total_time:.2f}s: {str(e)}", exc_info=True)
        return {"error": f"An unexpected error occurred: {str(e)}"}

@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}

# =============================================================================
# OLD CODE (COMMENTED OUT FOR REFERENCE)
# =============================================================================

# @app.post("/summarize") #defines an endpoint for POST requests at /summarize
# def summarize_video_old(request: VideoRequest): #automatically parses the incoming JSON into a Python object)
#     """
#     OLD VERSION: Basic error handling without performance monitoring
#     This version lacks detailed logging and performance metrics
#     """
#     try:
#         video_id = extract_video_id(request.url)
#         transcript = get_transcript(video_id)
#         summary = summarize_transcript(transcript, model=request.model)
#         return {"summary": summary, "model_used": request.model}
#     
#     except Exception as e:
#         print("Error in /summarize:", e)
#         return {"error": str(e)}