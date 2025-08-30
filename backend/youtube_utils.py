import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

def extract_video_id(url: str) -> str:
    video_id_match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if video_id_match:
        return video_id_match.group(1)
    raise ValueError("Invalid Youtube URL")

# def get_transcript(video_id: str) -> str:
#     transcript = YouTubeTranscriptApi().get_transcript(video_id)
#     text = " ".join([entry["text"] for entry in transcript if entry["text"].strip()])
#     return text

def get_transcript(video_id: str) -> str:
    api = YouTubeTranscriptApi()          # create an instance
    try:
        transcript = api.fetch(video_id)  # ✅ use fetch, not get_transcript
        return " ".join([entry.text.strip() for entry in transcript if entry.text.strip()])
    except (TranscriptsDisabled, NoTranscriptFound):
        return "No transcript available for this video."