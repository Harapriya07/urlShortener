import axios from "axios";

const API = axios.create({
    baseURL: import.meta.env.VITE_API_URL
});

export async function shortenURL(url) {
    const response = await API.post("/shorten", {
        url: url
    });

    return response.data;
}

export async function getAnalytics(shortCode) {
    const response = await API.get(`/analytics/${shortCode}`);

    return response.data;
}