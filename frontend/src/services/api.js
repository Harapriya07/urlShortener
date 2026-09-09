import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000"
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