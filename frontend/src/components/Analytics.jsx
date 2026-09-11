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
        <div className="analytics-header">
            <div>
                <h2>Analytics</h2>
                <p>Track how your shortened link is performing.</p>
            </div>
        </div>

        <div className="stats-grid">
            <StatsCard
                title="Total Clicks"
                value={analytics.clicks}
            />

            <StatsCard
                title="Today's Clicks"
                value={analytics.today_clicks}
            />

            <StatsCard
                title="Last 7 Days"
                value={Object.values(analytics.daily_clicks).reduce(
                    (total, clicks) => total + clicks,
                    0
                )}
            />
        </div>

        <ClickChart
            dailyClicks={analytics.daily_clicks}
        />
    </div>
);
}

export default Analytics;