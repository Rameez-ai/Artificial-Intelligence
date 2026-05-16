import { useEffect, useState } from 'react';
import { getDashboard } from '../api/financial';
import { useAuth } from '../context/AuthContext';
import {
  ResponsiveContainer, AreaChart, Area, BarChart, Bar,
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';
import { TrendingUp, Shield, DollarSign, Activity, AlertCircle, CheckCircle, Info, Loader2 } from 'lucide-react';

const COLORS = { income:'#6366f1', expenses:'#f43f5e', savings:'#10b981', investments:'#f59e0b', net_worth:'#2dd4bf' };

function MetricCard({ icon: Icon, label, value, sub, color = 'text-primary-400', glow }) {
  return (
    <div className={`metric-card ${glow ? 'border-primary-500/40 shadow-glow' : ''}`}>
      <div className="flex items-center justify-between">
        <span className="text-slate-400 text-xs uppercase tracking-wider">{label}</span>
        <div className={`w-9 h-9 rounded-lg bg-dark-600 flex items-center justify-center ${color}`}>
          <Icon size={18} />
        </div>
      </div>
      <p className={`stat-number mt-2 ${color}`}>{value}</p>
      {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
    </div>
  );
}

const InsightIcon = { success: CheckCircle, warning: AlertCircle, info: Info };
const InsightColor = { success: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
                       warning: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
                       info:    'text-blue-400 bg-blue-500/10 border-blue-500/30' };

export default function DashboardPage() {
  const { profile } = useAuth();
  const [data, setData]   = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard()
      .then(r => setData(r.data?.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 size={36} className="animate-spin text-primary-500" />
    </div>
  );

  const d = data || {};
  const lp  = d.loan_probability || 0;
  const hs  = d.health_score     || 0;
  const cs  = d.credit_score     || 650;

  return (
    <div className="p-6 space-y-6 animate-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="section-title">
            Welcome back, <span className="text-gradient">{profile?.name?.split(' ')[0] || 'User'}</span> 👋
          </h1>
          <p className="section-subtitle">Here's your financial overview for today</p>
        </div>
        <div className="badge-primary text-sm px-3 py-1">
          {new Date().toLocaleDateString('en-PK', { weekday:'long', month:'short', day:'numeric' })}
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricCard icon={TrendingUp}   label="Approval Chance"   value={`${lp}%`}  sub="ML model score"        color="text-primary-400"  glow />
        <MetricCard icon={Activity}     label="Financial Health"  value={`${hs}/100`} sub={hs>=80?'Excellent':hs>=60?'Good':'Fair'} color="text-emerald-400" />
        <MetricCard icon={Shield}       label="Credit Score"      value={cs}          sub={cs>=700?'Good standing':'Needs work'} color="text-accent-teal" />
        <MetricCard icon={DollarSign}   label="Monthly Savings"   value={`PKR ${(d.monthly_savings||0).toLocaleString()}`} sub="Net after expenses" color="text-accent-amber" />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Income vs Expenses */}
        <div className="glass-card">
          <h2 className="font-display font-semibold text-white mb-4">Income vs Expenses</h2>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={d.income_vs_expenses || []} margin={{ top:5, right:10, bottom:0, left:0 }}>
              <defs>
                <linearGradient id="gi" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="ge" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#f43f5e" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d2d4e" />
              <XAxis dataKey="month" tick={{ fill:'#64748b', fontSize:12 }} axisLine={false} />
              <YAxis tick={{ fill:'#64748b', fontSize:11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background:'#1a1a27', border:'1px solid #2d2d4e', borderRadius:'10px', fontSize:'12px' }} />
              <Legend wrapperStyle={{ fontSize:'12px' }} />
              <Area type="monotone" dataKey="income"   stroke="#6366f1" fill="url(#gi)" strokeWidth={2} dot={false} />
              <Area type="monotone" dataKey="expenses" stroke="#f43f5e" fill="url(#ge)" strokeWidth={2} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Financial Growth */}
        <div className="glass-card">
          <h2 className="font-display font-semibold text-white mb-4">Financial Growth</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={d.financial_growth || []} margin={{ top:5, right:10, bottom:0, left:0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d2d4e" />
              <XAxis dataKey="month" tick={{ fill:'#64748b', fontSize:12 }} axisLine={false} />
              <YAxis tick={{ fill:'#64748b', fontSize:11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background:'#1a1a27', border:'1px solid #2d2d4e', borderRadius:'10px', fontSize:'12px' }} />
              <Legend wrapperStyle={{ fontSize:'12px' }} />
              <Bar dataKey="savings"     fill="#10b981" radius={[4,4,0,0]} />
              <Bar dataKey="investments" fill="#f59e0b" radius={[4,4,0,0]} />
              <Bar dataKey="net_worth"   fill="#2dd4bf" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Risk radar + Insights + Activity */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Radar */}
        <div className="glass-card">
          <h2 className="font-display font-semibold text-white mb-4">Risk Profile</h2>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={d.risk_radar || []}>
              <PolarGrid stroke="#2d2d4e" />
              <PolarAngleAxis dataKey="category" tick={{ fill:'#64748b', fontSize:11 }} />
              <Radar dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.25} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Insights */}
        <div className="glass-card space-y-3">
          <h2 className="font-display font-semibold text-white">AI Insights</h2>
          {(d.insights || []).map((ins, i) => {
            const Icon = InsightIcon[ins.type] || Info;
            return (
              <div key={i} className={`flex gap-3 p-3 rounded-xl border ${InsightColor[ins.type] || InsightColor.info}`}>
                <Icon size={16} className="shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold">{ins.title}</p>
                  <p className="text-xs opacity-80 mt-0.5">{ins.message}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Recent Activity */}
        <div className="glass-card space-y-3">
          <h2 className="font-display font-semibold text-white">Recent Activity</h2>
          {(d.recent_activity || []).map((act, i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b border-dark-600 last:border-0">
              <div>
                <p className="text-xs text-slate-200 font-medium">{act.message}</p>
                <p className="text-xs text-slate-500">{act.time}</p>
              </div>
              <span className={act.result === 'Approved' ? 'badge-success' : act.result === 'Rejected' ? 'badge-danger' : 'badge-info'}>
                {act.result}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
