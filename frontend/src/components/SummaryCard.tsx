interface SummaryCardProps {
    title: string;
    value: number;
};

export default function SummaryCard({
    title,
    value,
}: SummaryCardProps) {
    return (
        <article className="summary-card">
            <h2>{title}</h2>
            <p>{value}</p>
        </article>
    )
}