import { useState } from "react";
import "./VideoInput.css"

export default function VideoInput() {
    const [videoLink, setVideoLink] = useState("");
    const [response, setResponse] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
    }

    return (
        <section>
            <h2>Enter Video Link</h2>
            <p>Paste a link from TikTok, Instagram, YouTube, or any other social media platform </p>
            <form onSubmit={handleSubmit}>
                <input type="url"
                    placeholder="Paste url here"
                    value={videoLink}
                    onChange={(e) => setVideoLink(e.target.value)}
                />
                <button type="submit">Summarize</button>
            </form>
        </section>
    )
}