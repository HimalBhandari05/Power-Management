
export default function PredictionCard({ prediction }) {
    const risk = prediction?.risk_level || "SAFE";
    const tone = risk.toLowerCase();
    const borderTone =
        tone === "critical"
            ? "border-l-red-500"
            : tone === "warning"
                ? "border-l-amber-500"
                : "border-l-emerald-500";
    const textTone =
        tone === "critical"
            ? "text-red-700"
            : tone === "warning"
                ? "text-amber-700"
                : "text-emerald-700";

    return (
        <section
            className={`rounded-xl border border-slate-200 border-l-4 bg-white p-5 shadow-sm ${borderTone}`}
        >
            <h2 className="mb-4 text-base font-semibold text-slate-900">
                Prediction
            </h2>

            <div className="mb-3 flex items-baseline justify-between">
                <span className="text-sm text-slate-500">
                    Predicted Next Load
                </span>
                <strong className="text-2xl font-semibold text-slate-900">
                    {prediction?.predicted_total_current ?? "—"} A
                </strong>
            </div>

            <p className={`text-sm font-semibold ${textTone}`}>
                Risk Level: {risk}
            </p>

            {risk === "WARNING" && (
                <p className="mt-2 text-sm font-medium text-amber-700">
                    Approaching transformer limit
                </p>
            )}

            {risk === "CRITICAL" && (
                <p className="mt-2 text-sm font-semibold text-red-700">
                    Power cut to house {prediction?.target_house}
                </p>
            )}
        </section>
    );
}
