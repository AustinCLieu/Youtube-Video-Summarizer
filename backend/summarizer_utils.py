from transformers import pipeline

bart_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
t5_summarizer = pipeline("summarization", model="t5-small")

def chunk_text(text: str, max_tokens: int = 900) -> list[str]:
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(current_chunk) + len(word.split()) > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
        current_chunk.append(word)
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def summarize_transcript(transcript: str, model: str = "bart", max_length: int = 150, min_length: int = 30) -> str:
    if not transcript.strip():
        return "No transcript available to summarize."
    
    chunks = chunk_text(transcript)
    partial_summaries =[]
    for chunk in chunks:
        if model == "bart":
            summary = bart_summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
            partial_summaries.append(summary[0]["summary_text"])
        
        elif model == "t5":
            input_text = "summarize: " + chunk
            summary = t5_summarizer(input_text, max_length=max_length, min_length=min_length, do_sample=False)
            partial_summaries.append(summary[0]["summary_text"])
    
    if len(partial_summaries) > 1:
        combined = " ".join(partial_summaries)
        return summarize_transcript(combined, model=model, max_length=max_length, min_length=min_length)
    
    return partial_summaries[0]
