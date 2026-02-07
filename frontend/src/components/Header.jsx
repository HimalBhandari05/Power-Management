
export default function Header({ risk }) {
    const safeRisk = (risk || "SAFE").toString();
    const tone = safeRisk.toLowerCase();
    const toneClasses =
        tone === "critical"
            ? "bg-red-100 text-red-700"
            : tone === "warning"
              ? "bg-amber-100 text-amber-700"
              : "bg-emerald-100 text-emerald-700";

    return (
        <header className="mb-6 flex items-center justify-between">
            <h1 className="text-xl font-semibold tracking-tight">
                Power Monitoring Dashboard
            </h1>
            <span
                className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${toneClasses}`}
            >
                {safeRisk}
            </span>
        </header>
    );
}
