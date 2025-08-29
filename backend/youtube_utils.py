import re
from youtube_transcript_api import YouTubeTranscriptApi

def extract_id(url: str) -> str:
    video_id_match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if video_id_match:
        return video_id_match.group(1)
    raise ValueError("Invalid Youtube URL")

def get_transcript(video_id: str) -> str:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text = " ".join([entry["text"] for entry in transcript if entry["text"].strip()])
    return text