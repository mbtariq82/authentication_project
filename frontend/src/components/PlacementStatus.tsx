import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface PlacementStatusItem {
  status: string;
  count: number;
}

interface PlacementStatusProps {
  data: PlacementStatusItem[];
}

const STATUS_COLORS = ["#22c55e", "#3b82f6", "#f59e0b"];

export default function PlacementStatus({
  data,
}: PlacementStatusProps) {
  const total = data.reduce((sum, item) => sum + item.count, 0);

  return (
    <div className="doughnut-chart">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="count"
            nameKey="status"
            cx="50%"
            cy="45%"
            innerRadius={65}
            outerRadius={100}
            paddingAngle={3}
          >
            {data.map((item, index) => (
              <Cell
                key={item.status}
                fill={STATUS_COLORS[index % STATUS_COLORS.length]}
              />
            ))}
          </Pie>

          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>

      <div className="doughnut-chart-center">
        <strong>{total}</strong>
        <span>Total</span>
      </div>
    </div>
  );
}