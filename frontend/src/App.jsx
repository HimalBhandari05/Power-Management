import { useEffect, useRef, useState } from "react";
import Header from "./components/Header";
import CurrentLoadCard from "./components/CurrentLoadCard";
import PredictionCard from "./components/PredictionCard";

export default function App() {
  const [layer2, setLayer2] = useState(null);
  const [predict, setPredict] = useState(null);
  const [error, setError] = useState(null);
  const [isStale, setIsStale] = useState(false);
  const [lastRefreshAt, setLastRefreshAt] = useState(null);
  const lastTimestampRef = useRef(null);

  const formatTime = (value) => {
    if (!value) return "—";
    const date = value instanceof Date ? value : new Date(value);
    if (Number.isNaN(date.getTime())) return "—";
    return new Intl.DateTimeFormat("en-US", {
      dateStyle: "medium",
      timeStyle: "medium",
      hour12: true,
    }).format(date);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setError(null);
        const cacheBust = Date.now();
        const [l2Res, pRes] = await Promise.all([
          fetch(`http://localhost:8000/layer2/latest?t=${cacheBust}`, {
            cache: "no-store",
          }),
          fetch(`http://localhost:8000/predict/latest?t=${cacheBust}`, {
            cache: "no-store",
          }),
        ]);

        if (!l2Res.ok || !pRes.ok) {
          throw new Error("Backend returned an error");
        }

        const l2Json = await l2Res.json();
        const pJson = await pRes.json();

        if (l2Json?.error || pJson?.error) {
          throw new Error(l2Json?.error || pJson?.error);
        }

        setLayer2(l2Json);
        setPredict(pJson);

        const incomingTimestamp = l2Json?.timestamp || null;
        if (
          incomingTimestamp &&
          incomingTimestamp === lastTimestampRef.current
        ) {
          setIsStale(true);
        } else {
          setIsStale(false);
          lastTimestampRef.current = incomingTimestamp;
        }

        setLastRefreshAt(new Date());
      } catch (err) {
        setError(err?.message || "Failed to load data");
      }
    };

    fetchData();
    const id = setInterval(fetchData, 5000);
    return () => clearInterval(id);
  }, []);

  const risk = predict?.risk_level || "SAFE";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-6xl px-6 py-6">
        <Header risk={risk} />

        {error && (
          <section className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <p>{error}</p>
          </section>
        )}

        <div className="grid gap-5 md:grid-cols-2">
          <CurrentLoadCard
            totalCurrent={layer2?.total_current}
            timestamp={layer2?.timestamp}
            lastRefresh={lastRefreshAt}
            isStale={isStale}
            formatTime={formatTime}
          />

          <PredictionCard prediction={predict} />
        </div>
      </div>
    </div>
  );
}