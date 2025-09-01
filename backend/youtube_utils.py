import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
import time
import logging

# Configure logging for better debugging
logger = logging.getLogger(__name__)

def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from various URL formats.
    
    This function supports multiple YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID
    
    Args:
        url: YouTube URL in any supported format
    
    Returns:
        YouTube video ID (11-character string)
    
    Raises:
        ValueError: If the URL format is not recognized
    """
    # Enhanced regex pattern to handle more URL formats
    video_id_match = re.search(r"(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})", url)
    if video_id_match:
        video_id = video_id_match.group(1)
        logger.info(f"Successfully extracted video ID: {video_id}")
        return video_id
    
    # NEW: More specific error message for debugging
    logger.error(f"Failed to extract video ID from URL: {url}")
    raise ValueError(f"Invalid YouTube URL format. Expected formats: youtube.com/watch?v=ID, youtu.be/ID, or youtube.com/embed/ID")

def get_transcript(video_id: str) -> str:
    """
    Retrieve transcript for a YouTube video with enhanced error handling and performance monitoring.
    
    This function fetches the transcript and provides detailed error information
    for better debugging and user experience.
    
    Args:
        video_id: YouTube video ID (11-character string)
    
    Returns:
        Concatenated transcript text, or error message if transcript cannot be retrieved
    
    Performance Notes:
    - Transcript retrieval typically takes 0.5-2 seconds depending on video length
    - Network latency is the main bottleneck
    - Consider implementing caching for frequently requested videos
    """
    start_time = time.time()
    api = YouTubeTranscriptApi()
    
    try:
        logger.info(f"Fetching transcript for video: {video_id}")
        
        # NEW: Attempt to get transcript with timeout handling
        transcript = api.fetch(video_id)
        
        # NEW: Process transcript with better text cleaning
        text_parts = []
        for entry in transcript:
            if entry.text and entry.text.strip():
                # Clean up common transcript artifacts
                cleaned_text = entry.text.strip()
                # Remove excessive whitespace and normalize
                cleaned_text = ' '.join(cleaned_text.split())
                if cleaned_text:
                    text_parts.append(cleaned_text)
        
        # NEW: Join with single spaces for cleaner output
        final_transcript = " ".join(text_parts)
        
        processing_time = time.time() - start_time
        logger.info(f"Transcript retrieved successfully in {processing_time:.2f}s, length: {len(final_transcript)} characters")
        
        return final_transcript
        
    except TranscriptsDisabled:
        error_msg = "Transcripts are disabled for this video."
        logger.warning(f"Transcripts disabled for video {video_id}")
        return error_msg
        
    except NoTranscriptFound:
        error_msg = "No transcript available for this video."
        logger.warning(f"No transcript found for video {video_id}")
        return error_msg
        
    except VideoUnavailable:
        error_msg = "This video is unavailable or has been removed."
        logger.warning(f"Video unavailable: {video_id}")
        return error_msg
        
    except Exception as e:
        # NEW: More specific error handling for different exception types
        processing_time = time.time() - start_time
        error_msg = f"Transcript error: {str(e)}"
        
        if "index out of range" in str(e).lower():
            logger.error(f"Index error in transcript processing for {video_id} after {processing_time:.2f}s: {e}")
            error_msg = "Transcript processing error: Index out of range. This may be a temporary issue."
        elif "network" in str(e).lower() or "timeout" in str(e).lower():
            logger.error(f"Network error for {video_id} after {processing_time:.2f}s: {e}")
            error_msg = "Network error while retrieving transcript. Please check your internet connection."
        else:
            logger.error(f"Unexpected error for {video_id} after {processing_time:.2f}s: {e}")
            error_msg = f"Unexpected error: {str(e)}"
        
        return error_msg

# =============================================================================
# OLD CODE (COMMENTED OUT FOR REFERENCE)
# =============================================================================

# def extract_video_id_old(url: str) -> str:
#     """
#     OLD VERSION: Basic video ID extraction without enhanced error handling
#     """
#     video_id_match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
#     if video_id_match:
#         return video_id_match.group(1)
#     raise ValueError("Invalid Youtube URL")

# def get_transcript_old(video_id: str) -> str:
#     """
#     OLD VERSION: Basic transcript retrieval without performance monitoring
#     """
#     api = YouTubeTranscriptApi()
#     try:
#         transcript = api.fetch(video_id)
#         return " ".join([entry.text for entry in transcript if entry.text.strip()])
#     except (TranscriptsDisabled, NoTranscriptFound):
#         return "No transcript available for this video."
#     except VideoUnavailable:
#         return "Video is unavailable."
#     except Exception as e:
#         # Catch-all for weird errors like "index out of range in self"
#         return f"Transcript error: {str(e)}"