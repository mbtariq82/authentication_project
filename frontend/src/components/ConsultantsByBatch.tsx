import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import { colors } from "../theme/colors";

interface BatchCount {
  batch: string;
  count: number;
}

interface ConsultantsByBatchProps {
  data: BatchCount[];
}

const CHART_COLORS = [
  colors.primary,
  colors.chartPurple,
  colors.chartTeal,
  colors.warning,
];

export default function ConsultantsByBatch({ data }: ConsultantsByBatchProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          dataKey="count"
          nameKey="batch"
          cx="50%"
          cy="50%"
          outerRadius={100}
          label
        >
          {data.map((item, index) => (
            <Cell
              key={item.batch}
              fill={CHART_COLORS[index % CHART_COLORS.length]}
            />
          ))}
        </Pie>

        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
