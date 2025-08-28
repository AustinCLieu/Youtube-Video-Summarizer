import { useState } from "react";
import "./VideoInput.css"

export default function VideoInput() {
    const [videoLink, setVideoLink] = useState("");
    const [response, setResponse] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const res = await fetch("http://localhost:8000/summarize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: videoLink }),
            });

            const data = await res.json();
            setResponse(data.summary);
        } catch (err) {
            console.error(err);
            setResponse("Something went wrong. Please try again");
        }
    }

    return (
        <div>
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

            <section>
                {response && (
                    <div>
                        <p>Summary</p>
                        <p>{response}</p>
                    </div>
                )}
            </section>
        </div>

    )
}