import "./ModelSelector.css"

export default function ModelSelector({ model, setModel }) {
    return (
        <div className="model-selector">
            <div className="model-options">
                <button
                    type="button"
                    className={`model-option ${model === "bart" ? "active" : ""}`}
                    onClick={() => setModel("bart")}
                >
                    <div className="model-icon">🧠</div>
                    <div className="model-info">
                        <span className="model-name">BART</span>
                        <span className="model-description">High Quality</span>
                    </div>
                </button>
                <button
                    type="button"
                    className={`model-option ${model === "t5" ? "active" : ""}`}
                    onClick={() => setModel("t5")}
                >
                    <div className="model-icon">⚡</div>
                    <div className="model-info">
                        <span className="model-name">T5</span>
                        <span className="model-description">Fast Processing</span>
                    </div>
                </button>
            </div>
        </div>
    )
}