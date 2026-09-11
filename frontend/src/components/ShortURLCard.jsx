import { useState } from "react";

function ShortURLCard({ shortCode }) {
    const [copied, setCopied] = useState(false);

    const shortURL = `${import.meta.env.VITE_API_URL}/${shortCode}`;

    async function copyURL() {
        await navigator.clipboard.writeText(shortURL);

        setCopied(true);

        setTimeout(() => {
            setCopied(false);
        }, 2000);
    }

    return (
    <div className="short-url-card">
        <div className="success-icon">
            ✓
        </div>

        <div className="short-url-content">
            <h2>Your shortened URL is ready</h2>

            <p>
                Your link has been successfully shortened.
            </p>

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

            <a
                className="open-link"
                href={shortURL}
                target="_blank"
                rel="noopener noreferrer"
            >
                Open shortened URL →
            </a>
        </div>
    </div>
);
}

export default ShortURLCard;