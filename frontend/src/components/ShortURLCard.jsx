import { useState } from "react";

function ShortURLCard({ shortCode }) {
    const [copied, setCopied] = useState(false);

    const shortURL = `http://127.0.0.1:8000/${shortCode}`;

    async function copyURL() {
        await navigator.clipboard.writeText(shortURL);

        setCopied(true);

        setTimeout(() => {
            setCopied(false);
        }, 2000);
    }

    return (
        <div className="short-url-card">
            <h2>Your shortened URL</h2>

            <div className="short-url-row">
                <input
                    type="text"
                    value={shortURL}
                    readOnly
                />

                <button onClick={copyURL}>
                    {copied ? "Copied ✓" : "Copy"}
                </button>
            </div>
        </div>
    );
}

export default ShortURLCard;