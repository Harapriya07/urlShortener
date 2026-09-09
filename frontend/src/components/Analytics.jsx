import { useEffect, useState } from "react";
import { getAnalytics } from "../services/api";
import StatsCard from "./StatsCard";
import ClickChart from "./ClickChart";

function Analytics({ shortCode }) {
    const [analytics, setAnalytics] = useState(null);

    useEffect(() => {
        async function fetchAnalytics() {
            try {
                const data = await getAnalytics(shortCode);

                setAnalytics(data);
            } catch (error) {
                console.error("Error fetching analytics:", error);
            }
        }

        fetchAnalytics();

        const interval = setInterval(fetchAnalytics, 5000);

        return () => clearInterval(interval);
    }, [shortCode]);

    if (!analytics) {
        return <p>Loading analytics...</p>;
    }

    return (
    <div className="analytics" id="analytics">
        <h2>Analytics</h2>

        <div className="stats-grid">
            <StatsCard
                title="Total Clicks"
                value={analytics.clicks}
            />

            <StatsCard
                title="Today's Clicks"
                value={analytics.today_clicks}
            />
        </div>

        <ClickChart
            dailyClicks={analytics.daily_clicks}
        />
    </div>
);
}

export default Analytics;