// src/components/CurrentLoadCard.jsx
export default function CurrentLoadCard({
    totalCurrent,
    timestamp,
    lastRefresh,
    isStale,
    formatTime
}) {
    return (
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="mb-4 text-base font-semibold text-slate-900">
                Current Load
            </h2>

            <div className="mb-3 flex items-baseline justify-between">
                <span className="text-sm text-slate-500">Total Current</span>
                <strong className="text-2xl font-semibold text-slate-900">
                    {totalCurrent ?? "—"} A
                </strong>
            </div>

            <p className="text-sm text-slate-600">
                Latest Data: {formatTime(timestamp)}
            </p>
            <p className="text-sm text-slate-600">
                Last Refresh: {formatTime(lastRefresh)}
            </p>

            {isStale && (
                <p className="mt-2 text-sm font-medium text-amber-700">
                    No new data detected
                </p>
            )}
        </section>
    );
}
