import { useState } from "react";
import { ChevronDown, ChevronUp, TrendingUp } from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { useTransactions } from "../hooks/useTransactions";

const lineColours = {
  DEPOSIT: "#0f9f8f",
  WITHDRAWAL: "#e07a5f",
  TRANSFER: "#3b82f6",
};

type TrendPoint = {
  date: string;
  DEPOSIT: number;
  WITHDRAWAL: number;
  TRANSFER: number;
};

function buildTrendData(
  transactions: NonNullable<
    ReturnType<typeof useTransactions>["data"]
  >["items"],
): TrendPoint[] {
  const grouped = new Map<string, TrendPoint>();

  for (const transaction of transactions) {
    if (transaction.status !== "COMPLETED") continue;

    const date = new Date(transaction.created_at).toLocaleDateString(
      undefined,
      { month: "short", day: "numeric" },
    );
    const point = grouped.get(date) ?? {
      date,
      DEPOSIT: 0,
      WITHDRAWAL: 0,
      TRANSFER: 0,
    };
    point[transaction.transaction_type] += Number(transaction.amount) || 0;
    grouped.set(date, point);
  }

  return Array.from(grouped.values()).reverse();
}

export default function TransactionsTrendChart() {
  const [isExpanded, setIsExpanded] = useState(true);
  const transactionsQuery = useTransactions({ limit: 100 });
  const trendData = buildTrendData(transactionsQuery.data?.items ?? []);

  return (
    <section className="transactions-trend-card" aria-labelledby="trend-title">
      <div className="transactions-trend-header">
        <div className="transactions-trend-heading">
          <span className="transactions-trend-icon" aria-hidden="true">
            <TrendingUp size={18} strokeWidth={2.2} />
          </span>
          <div>
            <p className="customer-card-label">Activity overview</p>
            <h2 id="trend-title">Money movement trends</h2>
          </div>
        </div>
        <button
          className="transactions-trend-toggle"
          type="button"
          aria-expanded={isExpanded}
          aria-controls="transactions-trend-content"
          aria-label={isExpanded ? "Minimize graph" : "Expand graph"}
          title={isExpanded ? "Minimize graph" : "Expand graph"}
          onClick={() => setIsExpanded((expanded) => !expanded)}
        >
          {isExpanded ? <ChevronUp size={19} /> : <ChevronDown size={19} />}
        </button>
      </div>

      {isExpanded && (
        <div
          id="transactions-trend-content"
          className="transactions-trend-content"
        >
          {transactionsQuery.isLoading && (
            <p className="transactions-trend-state" role="status">
              Loading transaction trends...
            </p>
          )}
          {transactionsQuery.isError && (
            <p
              className="transactions-trend-state transaction-error"
              role="alert"
            >
              {transactionsQuery.error.message}
            </p>
          )}
          {!transactionsQuery.isLoading &&
            !transactionsQuery.isError &&
            trendData.length === 0 && (
              <p className="transactions-trend-state">
                Complete a transaction to start building your trends.
              </p>
            )}
          {!transactionsQuery.isLoading &&
            !transactionsQuery.isError &&
            trendData.length > 0 && (
              <div className="transactions-trend-plot">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={trendData}
                    margin={{ top: 8, right: 10, left: 0, bottom: 4 }}
                  >
                    <CartesianGrid
                      stroke="#e6edf2"
                      strokeDasharray="3 3"
                      vertical={false}
                    />
                    <XAxis
                      dataKey="date"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: "#627d98", fontSize: 12 }}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: "#627d98", fontSize: 12 }}
                      tickFormatter={(value) => `£${value}`}
                      width={58}
                    />
                    <Tooltip
                      formatter={(value) => [
                        `£${Number(value).toFixed(2)}`,
                        "Amount",
                      ]}
                    />
                    <Legend iconType="circle" />
                    <Line
                      type="monotone"
                      dataKey="DEPOSIT"
                      name="Deposits"
                      stroke={lineColours.DEPOSIT}
                      strokeWidth={3}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="WITHDRAWAL"
                      name="Withdrawals"
                      stroke={lineColours.WITHDRAWAL}
                      strokeWidth={3}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="TRANSFER"
                      name="Transfers"
                      stroke={lineColours.TRANSFER}
                      strokeWidth={3}
                      dot={{ r: 3 }}
                      activeDot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
        </div>
      )}
    </section>
  );
}
