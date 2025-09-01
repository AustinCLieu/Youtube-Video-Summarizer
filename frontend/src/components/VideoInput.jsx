import { useState } from "react";
import "./VideoInput.css"
import ModelSelector from "./ModelSelector";

export default function VideoInput() {
    const [videoLink, setVideoLink] = useState("");
    const [response, setResponse] = useState("");
    const [model, setModel] = useState("bart");
    
    // Enhanced state management for better user experience
    const [isLoading, setIsLoading] = useState(false);
    const [progress, setProgress] = useState("");
    const [performanceMetrics, setPerformanceMetrics] = useState(null);
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Input validation before submission
        if (!videoLink.trim()) {
            setError("Please enter a YouTube video URL");
            return;
        }

        // Reset previous state and show loading
        setIsLoading(true);
        setError("");
        setResponse("");
        setPerformanceMetrics(null);
        setProgress("Initializing...");

        try {
            // Show progress updates during processing
            setProgress("Extracting video ID...");
            
            const res = await fetch("http://127.0.0.1:8000/summarize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: videoLink, model: model }),
            });

            const data = await res.json();
            
            if (data.error) {
                // Better error handling with specific error messages
                setError(`Backend error: ${data.error}`);
                setResponse("");
            } else {
                // Display both summary and performance metrics
                setResponse(data.summary);
                setPerformanceMetrics(data.performance_metrics);
                setProgress("Summary completed!");
            }
        } catch (err) {
            console.error(err);
            // More specific error messages based on error type
            if (err.name === 'TypeError' && err.message.includes('fetch')) {
                setError("Cannot connect to server. Please check if the backend is running.");
            } else {
                setError("Something went wrong. Please try again.");
            }
            setResponse("");
        } finally {
            // Always hide loading state when done
            setIsLoading(false);
        }
    }

    // Helper function to format time for display
    const formatTime = (seconds) => {
        if (seconds < 1) {
            return `${Math.round(seconds * 1000)}ms`;
        }
        return `${seconds}s`;
    };

    return (
        <div className="app-container">
            {/* Hero Section */}
            <div className="hero-section">
                <div className="hero-content">
                    <div className="hero-features">
                        <div className="feature">
                            <span className="feature-icon">📺</span>
                            <span>YouTube Videos</span>
                        </div>
                        <div className="feature">
                            <span className="feature-icon">🎯</span>
                            <span>Accurate Summaries</span>
                        </div>
                        <div className="feature">
                            <span className="feature-icon">🔒</span>
                            <span>Privacy Focused</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="main-content">
                {/* Input Section */}
                <div className="input-section">
                    <div className="input-card">
                        <h2 className="section-title">Enter YouTube Video Link</h2>
                        <p className="section-description">
                            Paste a YouTube video URL to generate an AI-powered summary
                        </p>
                        
                        {/* Enhanced form with better validation and loading states */}
                        <form onSubmit={handleSubmit} className="video-form">
                            <div className="input-group">
                                <label htmlFor="video-url" className="input-label">
                                    YouTube Video URL
                                </label>
                                <input
                                    id="video-url"
                                    type="url"
                                    placeholder="https://www.youtube.com/watch?v=..."
                                    value={videoLink}
                                    onChange={(e) => setVideoLink(e.target.value)}
                                    disabled={isLoading}
                                    className={`url-input ${error ? "error" : ""}`}
                                />
                                {error && (
                                    <div className="error-message">
                                        <span className="error-icon">⚠️</span>
                                        <span>{error}</span>
                                    </div>
                                )}
                            </div>
                            
                            <div className="model-section">
                                <label className="input-label">AI Model</label>
                                <ModelSelector model={model} setModel={setModel} />
                                <p className="model-description">
                                    {model === "bart" 
                                        ? "BART: High-quality summaries with better context understanding"
                                        : "T5: Faster processing with good accuracy"
                                    }
                                </p>
                            </div>
                            
                            {/* Enhanced submit button with loading state */}
                            <button 
                                type="submit" 
                                disabled={isLoading || !videoLink.trim()}
                                className={`submit-button ${isLoading ? "loading" : ""}`}
                            >
                                {isLoading ? (
                                    <>
                                        <span className="button-spinner"></span>
                                        <span>Processing...</span>
                                    </>
                                ) : (
                                    <>
                                        <span className="button-icon">📺</span>
                                        <span>Generate Summary</span>
                                    </>
                                )}
                            </button>
                        </form>
                    </div>
                </div>

                {/* Loading Section */}
                {isLoading && (
                    <div className="loading-section">
                        <div className="loading-card">
                            <div className="loading-content">
                                <div className="loading-spinner"></div>
                                <h3 className="loading-title">Processing Your YouTube Video</h3>
                                <p className="loading-message">{progress}</p>
                                <div className="loading-steps">
                                    <div className="step">
                                        <div className="step-icon">🔍</div>
                                        <span>Extracting Video ID</span>
                                    </div>
                                    <div className="step">
                                        <div className="step-icon">📝</div>
                                        <span>Retrieving Transcript</span>
                                    </div>
                                    <div className="step">
                                        <div className="step-icon">🤖</div>
                                        <span>Generating Summary</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Results Section */}
                {response && (
                    <div className="results-section">
                        <div className="results-card">
                            <div className="summary-section">
                                <div className="summary-header">
                                    <h3 className="summary-title">
                                        <span className="summary-icon">📋</span>
                                        Video Summary
                                    </h3>
                                    <div className="summary-actions">
                                        <button 
                                            className="action-button copy-button"
                                            onClick={() => navigator.clipboard.writeText(response)}
                                        >
                                            📋 Copy
                                        </button>
                                    </div>
                                </div>
                                <div className="summary-content">
                                    <p>{response}</p>
                                </div>
                            </div>
                            
                            {/* Performance metrics display */}
                            {performanceMetrics && (
                                <div className="metrics-section">
                                    <h4 className="metrics-title">
                                        <span className="metrics-icon">⚡</span>
                                        Performance Metrics
                                    </h4>
                                    <div className="metrics-grid">
                                        <div className="metric-card">
                                            <div className="metric-icon">⏱️</div>
                                            <div className="metric-content">
                                                <span className="metric-label">Total Time</span>
                                                <span className="metric-value">{formatTime(performanceMetrics.total_processing_time)}</span>
                                            </div>
                                        </div>
                                        <div className="metric-card">
                                            <div className="metric-icon">🎯</div>
                                            <div className="metric-content">
                                                <span className="metric-label">Video ID Extraction</span>
                                                <span className="metric-value">{formatTime(performanceMetrics.video_extraction_time)}</span>
                                            </div>
                                        </div>
                                        <div className="metric-card">
                                            <div className="metric-icon">📝</div>
                                            <div className="metric-content">
                                                <span className="metric-label">Transcript Retrieval</span>
                                                <span className="metric-value">{formatTime(performanceMetrics.transcript_retrieval_time)}</span>
                                            </div>
                                        </div>
                                        <div className="metric-card">
                                            <div className="metric-icon">🤖</div>
                                            <div className="metric-content">
                                                <span className="metric-label">Summary Generation</span>
                                                <span className="metric-value">{formatTime(performanceMetrics.summary_generation_time)}</span>
                                            </div>
                                        </div>
                                        <div className="metric-card">
                                            <div className="metric-icon">📊</div>
                                            <div className="metric-content">
                                                <span className="metric-label">Transcript Length</span>
                                                <span className="metric-value">{performanceMetrics.transcript_length} chars</span>
                                            </div>
                                        </div>
                                        <div className="metric-card">
                                            <div className="metric-icon">📏</div>
                                            <div className="metric-content">
                                                <span className="metric-label">Summary Length</span>
                                                <span className="metric-value">{performanceMetrics.summary_length} chars</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="footer">
                <p>Powered by advanced AI models • Built with React & FastAPI</p>
            </div>
        </div>
    )
}
