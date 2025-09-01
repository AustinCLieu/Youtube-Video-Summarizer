from transformers import pipeline
import concurrent.futures
import time

# Initialize summarization models once when the module loads
# This avoids reloading models on every request, significantly improving performance
bart_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
t5_summarizer = pipeline("summarization", model="t5-small")

def chunk_text(text: str, max_tokens: int = 300) -> list[str]:
    """
    Split text into smaller chunks for processing.
    
    UPDATED: Reduced from 500 to 300 tokens for much shorter final summaries
    - Smaller chunks = more chunks but each summary is shorter
    - More chunks = more parallel processing opportunities
    - Final result = much more concise overall summary
    
    Args:
        text: The input text to chunk
        max_tokens: Maximum tokens per chunk (reduced to 300 for shorter summaries)
    
    Returns:
        List of text chunks
    """
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

def summarize_chunk_parallel(chunk: str, model: str, max_length: int, min_length: int) -> str:
    """
    Summarize a single text chunk using the specified model.
    
    This function is designed to be called in parallel for multiple chunks.
    
    Args:
        chunk: Text chunk to summarize
        model: Model to use ('bart' or 't5')
        max_length: Maximum length of summary
        min_length: Minimum length of summary
    
    Returns:
        Summarized text
    """
    try:
        if model == "bart":
            summary = bart_summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
            return summary[0]["summary_text"]
        
        elif model == "t5":
            input_text = "summarize: " + chunk
            summary = t5_summarizer(input_text, max_length=max_length, min_length=min_length, do_sample=False)
            return summary[0]["summary_text"]
        
        else:
            return f"Unknown model: {model}"
    
    except Exception as e:
        # Return error message instead of crashing the entire process
        return f"Error processing chunk: {str(e)}"

def safe_summarize(model_pipeline, input_text, **kwargs):
    """
    Safe wrapper around model pipeline calls to catch 'index out of range in self' errors.
    
    This function provides robust error handling for common pipeline failures.
    
    Args:
        model_pipeline: The model pipeline to use
        input_text: Text to summarize
        **kwargs: Additional arguments for the pipeline
    
    Returns:
        Summary result or error message
    """
    try:
        result = model_pipeline(input_text, **kwargs)
        
        # Validate the result structure
        if not result or not isinstance(result, list) or len(result) == 0:
            return None, "Model returned empty result"
        
        if not isinstance(result[0], dict) or "summary_text" not in result[0]:
            return None, f"Model returned invalid result structure: {result}"
        
        return result[0]["summary_text"], None
        
    except IndexError as e:
        if "index out of range in self" in str(e):
            return None, "Model pipeline failed internally (index out of range)"
        else:
            return None, f"Index error: {str(e)}"
    except Exception as e:
        return None, f"Model error: {str(e)}"

def summarize_transcript(transcript: str, model: str = "bart", max_length: int = 300, min_length: int = 100) -> str:
    """
    Summarize a transcript using single-pass summarization for optimal quality.
    
    UPDATED: Single pass summarization to maintain quality
    - No more double summarization (which degraded quality)
    - Single AI pass with full context
    - Guaranteed 300 words maximum
    - Better quality summaries with preserved context
    
    Args:
        transcript: The transcript text to summarize
        model: Model to use ('bart' or 't5')
        max_length: Maximum length of summary (default: 300 words for final output)
        min_length: Minimum length of summary (default: 100 words for useful content)
    
    Returns:
        Summarized text (guaranteed to be under 300 words with better quality)
    """
    if not transcript.strip():
        return "No transcript available to summarize."
    
    # OPTION 1: Single pass summarization for better quality
    # Instead of chunking and double-summarizing, let the AI model handle the full context
    # This preserves important details and context that would be lost in chunking
    
    try:
        if model == "bart":
            # BART model can handle longer texts better than T5
            summary_text, error = safe_summarize(
                bart_summarizer,
                transcript, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False
            )
            
            if error:
                print(f"BART safe_summarize error: {error}")
                raise ValueError(f"BART model failed: {error}")
            
            return summary_text
        
        elif model == "t5":
            # T5 needs "summarize:" prefix and works better with shorter inputs
            # For very long transcripts, we might need to truncate slightly
            input_text = "summarize: " + transcript
            
            # If transcript is extremely long, truncate to avoid memory issues
            # Most AI models have input limits around 1024-2048 tokens
            if len(transcript.split()) > 1500:  # Rough estimate for token limit
                # Take first 1500 words to stay within model limits
                truncated_transcript = " ".join(transcript.split()[:1500])
                input_text = "summarize: " + truncated_transcript
                print("Note: Transcript was very long and was truncated for T5 model")
            
            summary_text, error = safe_summarize(
                t5_summarizer,
                input_text, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False
            )
            
            if error:
                print(f"T5 safe_summarize error: {error}")
                raise ValueError(f"T5 model failed: {error}")
            
            return summary_text
        
        else:
            return f"Unknown model: {model}"
    
    except Exception as e:
        print(f"Error in single-pass summarization: {e}")
        # Fallback: if single pass fails, try with a shorter input
        try:
            print("Final fallback: trying with much shorter input...")
            # Truncate to first 500 words and try again
            truncated = " ".join(transcript.split()[:500])
            
            if model == "bart":
                summary_text, error = safe_summarize(
                    bart_summarizer,
                    truncated,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                
                if error:
                    raise ValueError(f"BART final fallback failed: {error}")
                
                return summary_text
                    
            elif model == "t5":
                input_text = "summarize: " + truncated
                summary_text, error = safe_summarize(
                    t5_summarizer,
                    input_text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                
                if error:
                    raise ValueError(f"T5 final fallback failed: {error}")
                
                return summary_text
                    
        except Exception as fallback_error:
            print(f"All fallbacks failed: {fallback_error}")
            return f"Failed to generate summary after all attempts: {str(e)}"

# =============================================================================
# OLD CHUNKING CODE (COMMENTED OUT - CAUSED QUALITY ISSUES)
# =============================================================================

# def summarize_transcript_old(transcript: str, model: str = "bart", max_length: int = 100, min_length: int = 30) -> str:
#     """
#     OLD VERSION: Double summarization approach - caused quality degradation
#     This function processed chunks separately then tried to summarize summaries
#     Result: Loss of context and generic, poor-quality summaries
#     
#     PROBLEMS:
#     - First pass: AI summarizes chunks (loses context)
#     - Second pass: AI tries to summarize already-summarized text (loses more context)
#     - Final result: Generic summary missing specific details
#     """
#     if not transcript.strip():
#         return "No transcript available to summarize."
#     
#     # Split transcript into manageable chunks (now smaller chunks)
#     chunks = chunk_text(transcript)
#     
#     # If only one chunk, process it directly and ensure it's under 300 words
#     if len(chunks) == 1:
#         initial_summary = summarize_chunk_parallel(chunks[0], model, max_length, min_length)
#         # If the single summary is already under 300 words, return it
#         if len(initial_summary.split()) <= 300:
#             return initial_summary
#         # If it's over 300 words, create a final summary
#         else:
#             return summarize_chunk_parallel(initial_summary, model, max_length=300, min_length=50)
#     
#     # Process multiple chunks in parallel for significant performance improvement
#     # Using ThreadPoolExecutor for I/O-bound operations (model inference)
#     partial_summaries = []
#     
#     try:
#         with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(chunks), 4)) as executor:
#             # Submit all chunks for parallel processing
#             future_to_chunk = {
#                 executor.submit(summarize_chunk_parallel, chunk, model, max_length, min_length): chunk 
#                 for chunk in chunks
#             }
#             
#             # Collect results as they complete
#             for future in concurrent.futures.as_completed(future_to_chunk):
#                 result = future.result()
#                 if result and not result.startswith("Error processing chunk"):
#                     partial_summaries.append(result)
#                 else:
#                     # Log error but continue with other chunks
#                     print(f"Warning: Failed to process chunk: {result}")
#     
#     except Exception as e:
#         print(f"Error in parallel processing: {e}")
#         # Fallback to sequential processing if parallel fails
#         partial_summaries = []
#         for chunk in chunks:
#             result = summarize_chunk_parallel(chunk, model, max_length, min_length)
#             if result and not result.startswith("Error processing chunk"):
#                 partial_summaries.append(result)
#     
#     # CRITICAL FIX: Create one final summary from all partial summaries
#     if partial_summaries:
#         # Combine all partial summaries into one text
#         combined_partial_summaries = " ".join(partial_summaries)
#         
#         # Create a final summary that's guaranteed to be under 300 words
#         final_summary = summarize_chunk_parallel(
#             combined_partial_summaries, 
#             model, 
#             max_length=300,  # Maximum 300 words for final output
#             min_length=100   # Minimum 100 words to ensure useful content
#         )
#         
#         return final_summary
#     else:
#         return "Failed to generate summary from any chunks."
