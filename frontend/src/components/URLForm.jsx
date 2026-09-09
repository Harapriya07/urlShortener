import { useState } from "react";
import { shortenURL } from "../services/api";
import ShortURLCard from "./ShortURLCard";
import Analytics from "./Analytics";

function URLForm() {
    const [url, setUrl] = useState("");
    const [shortCode, setShortCode] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(e) {
    e.preventDefault();

    if (!url.trim()) {
        setError("Please enter a URL.");
        return;
    }

    setError("");
    setLoading(true);

    try {
        const data = await shortenURL(url);

        setShortCode(data.short_code);
    } catch (error) {
        console.error("Error shortening URL:", error);
        setError("Failed to shorten URL. Please try again.");
    } finally {
        setLoading(false);
    }
}

    return (
        <div>
            <form className="url-form" onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Enter your long URL"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                />

                <button type="submit" disabled={loading}>
                {loading ? "Shortening..." : "Shorten URL"}
                </button>
            </form>

            {error && (
            <p className="error-message">
             {error}
                 </p>
            )}

            {shortCode && (<>
                <ShortURLCard shortCode={shortCode} />
                <Analytics shortCode={shortCode} />
                </>
            )}
        </div>
    );
}

export default URLForm;