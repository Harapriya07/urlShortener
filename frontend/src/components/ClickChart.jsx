import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from "recharts";

function ClickChart({ dailyClicks }) {

    const data = Object.entries(dailyClicks)
    .reverse()
    .map(([date, clicks]) => ({
        date: date.slice(5),
        clicks: clicks
    }));

    return (
    <div className="chart-card">
        <div className="chart-header">
            <div>
                <h2>Click activity</h2>
                <p>Clicks recorded over the last 7 days.</p>
            </div>

            <span className="chart-period">
                Last 7 days
            </span>
        </div>

        <div className="chart-container">
            <ResponsiveContainer width="100%" height={320}>
                <AreaChart
                    data={data}
                    margin={{
                        top: 10,
                        right: 10,
                        left: -15,
                        bottom: 0
                    }}
                >
                    <defs>
                        <linearGradient
                            id="clickGradient"
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                        >
                            <stop
                                offset="0%"
                                stopOpacity={0.25}
                            />

                            <stop
                                offset="100%"
                                stopOpacity={0}
                            />
                        </linearGradient>
                    </defs>

                    <CartesianGrid
                        strokeDasharray="4 4"
                        vertical={false}
                    />

                    <XAxis
                        dataKey="date"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 12 }}
                    />

                    <YAxis
                        allowDecimals={false}
                        axisLine={false}
                        tickLine={false}
                        width={30}
                        tick={{ fontSize: 12 }}
                    />

                    <Tooltip />

                    <Area
                        type="monotone"
                        dataKey="clicks"
                        stroke="#243746"
                        strokeWidth={2.5}
                        fill="url(#clickGradient)"
                        dot={{
                            r: 4,
                            strokeWidth: 2,
                            fill: "#ffffff"
                        }}
                        activeDot={{
                            r: 6
                        }}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    </div>
);
}

export default ClickChart;