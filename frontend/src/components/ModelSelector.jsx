import "./ModelSelector.css"

export default function ModelSelector({ model, setModel }) {
    return (
        <div>
            <button
                type="button"
                className={model === "bart" ? "active" : ""}
                onClick={() => setModel("bart")}
            >
                Use Bart
            </button>
            <button
                type="button"
                className={model === "t5" ? "active" : ""}
                onClick={() => setModel("t5")}
            >
                Use T5
            </button>
        </div>
    )
}