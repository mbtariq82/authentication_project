interface AttentionConsultant {
  id: number;
  name: string;
  batch: string;
  client: string | null;
  reason: string;
}

interface AttentionTableProps {
  consultants: AttentionConsultant[];
}

export default function AttentionTable({
  consultants,
}: AttentionTableProps) {
  return (
    <section className="attention-section">
      <div className="attention-section-header">
        <div>
          <h2>Consultants requiring attention</h2>
        </div>

        <span className="attention-count">{consultants.length}</span>
      </div>

      {consultants.length === 0 ? (
        <p className="attention-empty">
          No consultants currently require attention.
        </p>
      ) : (
        <div className="attention-table-wrapper">
          <table className="attention-table">
            <thead>
              <tr>
                <th scope="col">Name</th>
                <th scope="col">Batch</th>
                <th scope="col">Client</th>
                <th scope="col">Reason</th>
              </tr>
            </thead>

            <tbody>
              {consultants.map((consultant) => (
                <tr key={consultant.id}>
                  <td className="consultant-name">{consultant.name}</td>
                  <td>{consultant.batch}</td>
                  <td>{consultant.client ?? "Unassigned"}</td>
                  <td>
                    <span className="attention-reason">
                      {consultant.reason}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}