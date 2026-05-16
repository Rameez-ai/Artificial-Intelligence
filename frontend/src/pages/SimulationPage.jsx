import { useState } from 'react';
import { simulate } from '../api/financial';
import toast from 'react-hot-toast';
import { Loader2, TrendingUp } from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const INITIAL = {
  loan_amount: 500000, interest_rate: 14, loan_term: 36,
  annual_income: 960000, monthly_expenses: 30000, savings_balance: 50000,
};

export default function SimulationPage() {
  const [form, setForm]     = useState(INITIAL);
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(false);

  const set = k => e => setForm(f => ({ ...f, [k]: Number(e.target.value) }));

  async function handleRun(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await simulate(form);
      setData(res.data?.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Simulation failed');
    } finally {
      setLoading(false);
    }
  }

  const fmt = v => `PKR ${Number(v||0).toLocaleString()}`;

  return (
    <div className="p-6 space-y-6 animate-in">
      <div>
        <h1 className="section-title">Financial Simulation</h1>
        <p className="section-subtitle">Project your financial future with and without the loan</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Form */}
        <div className="glass-card xl:col-span-1">
          <h2 className="font-display font-semibold text-white mb-4">Simulation Parameters</h2>
          <form id="sim-form" onSubmit={handleRun} className="space-y-3">
            {[
              { key:'loan_amount',      label:'Loan Amount',        placeholder:'500000' },
              { key:'interest_rate',    label:'Interest Rate (%)',   placeholder:'14' },
              { key:'loan_term',        label:'Term (months)',       placeholder:'36' },
              { key:'annual_income',    label:'Annual Income',       placeholder:'960000' },
              { key:'monthly_expenses', label:'Monthly Expenses',    placeholder:'30000' },
              { key:'savings_balance',  label:'Current Savings',     placeholder:'50000' },
            ].map(({ key, label, placeholder }) => (
              <div key={key} className="input-group">
                <label className="input-label">{label}</label>
                <input id={`sim-${key}`} type="number" required min={0} value={form[key]}
                  onChange={set(key)} placeholder={placeholder} className="input-field" />
              </div>
            ))}
            <button id="run-simulation" type="submit" disabled={loading} className="btn-primary w-full mt-2">
              {loading ? <Loader2 size={18} className="animate-spin" /> : <TrendingUp size={18} />}
              {loading ? 'Running…' : 'Run Simulation'}
            </button>
          </form>
        </div>

        {/* Results */}
        {data ? (
          <div className="xl:col-span-2 space-y-4 animate-in">
            {/* Summary cards */}
            <div className="grid grid-cols-3 gap-4">
              {[
                { label:'Baseline Savings',  value: fmt(data.baseline?.final_savings), color:'text-emerald-400' },
                { label:'Projected Savings', value: fmt(data.projected?.final_savings), color:'text-primary-400' },
                { label:'EMI Impact',        value: fmt(data.comparison?.monthly_difference), color:'text-rose-400' },
              ].map(({ label, value, color }) => (
                <div key={label} className="glass-card text-center">
                  <p className={`text-xl font-display font-bold ${color}`}>{value}</p>
                  <p className="text-xs text-slate-500 mt-1">{label}</p>
                </div>
              ))}
            </div>

            {/* Baseline vs Projected chart */}
            <div className="glass-card">
              <h2 className="font-display font-semibold text-white mb-4">Savings Trajectory (12 months)</h2>
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={data.chart_data || []} margin={{ top:5, right:10, bottom:0, left:0 }}>
                  <defs>
                    <linearGradient id="gbase" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="gproj" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d4e" />
                  <XAxis dataKey="month" tick={{ fill:'#64748b', fontSize:11 }} axisLine={false} />
                  <YAxis tick={{ fill:'#64748b', fontSize:10 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ background:'#1a1a27', border:'1px solid #2d2d4e', borderRadius:'10px', fontSize:'11px' }}
                    formatter={v => [`PKR ${Number(v).toLocaleString()}`]} />
                  <Legend wrapperStyle={{ fontSize:'12px' }} />
                  <Area type="monotone" dataKey="baseline"  stroke="#10b981" fill="url(#gbase)" strokeWidth={2} dot={false} name="Without Loan" />
                  <Area type="monotone" dataKey="projected" stroke="#6366f1" fill="url(#gproj)" strokeWidth={2} dot={false} name="With Loan" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Recommendations */}
            {data.recommendations?.length > 0 && (
              <div className="glass-card space-y-2">
                <h3 className="font-semibold text-white mb-2">Recommendations</h3>
                {data.recommendations.map((r, i) => (
                  <p key={i} className="text-sm text-slate-300 bg-dark-600/50 rounded-lg px-3 py-2">
                    💡 {r.message}
                  </p>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="xl:col-span-2 glass-card flex flex-col items-center justify-center h-64 text-slate-500">
            <TrendingUp size={40} className="mb-3 opacity-30" />
            <p className="text-sm">Run the simulation to see your financial projection</p>
          </div>
        )}
      </div>
    </div>
  );
}
