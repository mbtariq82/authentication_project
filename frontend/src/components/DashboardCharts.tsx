import ConsultantsByBatch from "./ConsultantsByBatch";
import PlacementStatus from "./PlacementStatus";

interface BatchCount {
  batch: string;
  count: number;
}

interface PlacementStatusItem {
  status: string;
  count: number;
}

interface DashboardChartsProps {
  consultantsByBatch: BatchCount[];
  placementStatus: PlacementStatusItem[];
}

export default function DashboardCharts({
  consultantsByBatch,
  placementStatus,
}: DashboardChartsProps) {
  return (
    <section className="dashboard-charts">
      <div className="dashboard-chart-card">
        <h2>Consultants by batch</h2>

        <div className="dashboard-chart-content">
          <ConsultantsByBatch data={consultantsByBatch} />
        </div>
      </div>

      <div className="dashboard-chart-card">
        <h2>Placement status</h2>

        <div className="dashboard-chart-content">
          <PlacementStatus data={placementStatus} />
        </div>
      </div>
    </section>
  );
}