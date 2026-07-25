import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer,
} from "recharts";
import type { ModelMetric } from "../types";

export default function MetricsChart({ metric }: { metric: ModelMetric }) {
  const data = [
    { name: "Precision", value: metric.precision },
    { name: "Recall", value: metric.recall },
    { name: "F1", value: metric.f1_score },
  ];

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#232936" vertical={false} />
          <XAxis dataKey="name" stroke="#838D9E" fontSize={12} tickLine={false} axisLine={{ stroke: "#232936" }} />
          <YAxis
            domain={[0, 1]}
            stroke="#838D9E"
            fontSize={12}
            tickLine={false}
            axisLine={{ stroke: "#232936" }}
          />
          <Tooltip
            contentStyle={{ background: "#171C26", border: "1px solid #232936", borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: "#E7E9EE" }}
            formatter={(value: number) => value.toFixed(3)}
          />
          {metric.baseline_precision != null && (
            <ReferenceLine
              y={metric.baseline_precision}
              stroke="#F5A623"
              strokeDasharray="4 4"
              label={{ value: "baseline", position: "insideTopRight", fill: "#F5A623", fontSize: 11 }}
            />
          )}
          <Bar dataKey="value" fill="#5B8DEF" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
