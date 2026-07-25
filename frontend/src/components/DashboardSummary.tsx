import SummaryCard from "./SummaryCard";

interface DashboardSummaryProps {
  total: number;
  placed: number;
  available: number;
  endingSoon: number;
}

export default function DashboardSummary({
  total,
  placed,
  available,
  endingSoon,
}: DashboardSummaryProps) {
  return (
    <section className="dashboard-summary">
      <SummaryCard title="Total consultants" value={total} />
      <SummaryCard title="Placed" value={placed} />
      <SummaryCard title="Available" value={available} />
      <SummaryCard title="Ending soon" value={endingSoon} />
    </section>
  );
}
