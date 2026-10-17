
export default function StatCard({
    label,
    value,
    note,
}: {
    label: string;
    value: string;
    note?: string;
}) {
    return (
        <div className="card p-5">
            <div className="text-sm muted">
                {label}
            </div>

            <div className="text-2xl font-bold mt-1">
                {value}
            </div>

            {note && (
                <div className="text-xs muted mt-1">
                    {note}
                </div>
            )}
        </div>
    );
}
