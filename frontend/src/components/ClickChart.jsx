import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from "recharts";

function ClickChart({ dailyClicks }) {

    const data = Object.entries(dailyClicks).map(
        ([date, clicks]) => ({
            date: date.slice(5),
            clicks: clicks
        })
    );

    return (
        <div className="chart-card">
            <h2>Clicks - Last 7 Days</h2>

            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis dataKey="date" />

                    <YAxis />

                    <Tooltip />

                    <Line
                        type="monotone"
                        dataKey="clicks"
                        stroke="#243746"
                        strokeWidth={2}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}

export default ClickChart;