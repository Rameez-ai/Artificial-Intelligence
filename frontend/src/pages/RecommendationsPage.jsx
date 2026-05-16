import { useEffect, useState } from 'react';
import { getSuggestions } from '../api/loan';
import { Star, Loader2, ArrowRight } from 'lucide-react';

export default function RecommendationsPage() {
  const [recs, setRecs] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSuggestions()
      .then(r => setRecs(r.data?.data))
      .catch(() => setRecs(null))
      .finally(() => setLoading(false));
  }, []);

  const PRIORITY_COLOR = {
    High:   'border-rose-500/40 bg-rose-500/10',
    Medium: 'border-amber-500/40 bg-amber-500/10',
    Low:    'border-emerald-500/40 bg-emerald-500/10',
  };
  const PRIORITY_BADGE = {
    High:   'badge-danger',
    Medium: 'badge-warning',
    Low:    'badge-success',
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={36} className="animate-spin text-primary-500" />
    </div>
  );

  const suggestions = recs?.suggestions || [];

  return (
    <div className="p-6 space-y-6 animate-in">
      <div>
        <h1 className="section-title">Smart Recommendations</h1>
        <p className="section-subtitle">AI-powered suggestions to improve your loan eligibility</p>
      </div>

      {suggestions.length === 0 ? (
        <div className="glass-card flex flex-col items-center justify-center h-64 text-slate-500">
          <Star size={40} className="mb-3 text-primary-500/40" />
          <p className="text-sm">Run a loan eligibility check first to get personalised recommendations</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {suggestions.map((s, i) => {
            const priority = s.priority || 'Medium';
            return (
              <div key={i} className={`glass-card border-2 ${PRIORITY_COLOR[priority] || PRIORITY_COLOR.Medium}`}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-primary-500/20 flex items-center justify-center text-primary-400 font-bold text-sm">
                      {i+1}
                    </div>
                    <span className="font-semibold text-white text-sm capitalize">
                      {s.category || 'General'}
                    </span>
                  </div>
                  <span className={PRIORITY_BADGE[priority] || 'badge-info'}>{priority} Priority</span>
                </div>
                <p className="text-slate-300 text-sm mb-2">{s.impact || s.message}</p>
                {s.suggestion && (
                  <div className="flex items-start gap-2 mt-2 text-xs text-primary-400 bg-primary-500/10 rounded-lg p-2.5">
                    <ArrowRight size={14} className="shrink-0 mt-0.5" />
                    <span>{s.suggestion}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
