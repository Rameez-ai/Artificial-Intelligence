import { useState, useMemo } from 'react';
import { Calculator, DollarSign, Calendar, Percent } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function calcEMI(principal, annualRate, months) {
  if (!principal || !months) return 0;
  if (!annualRate) return principal / months;
  const r = annualRate / 100 / 12;
  return (principal * r * Math.pow(1 + r, months)) / (Math.pow(1 + r, months) - 1);
}

export default function EMICalculatorPage() {
  const [loan,     setLoan]     = useState(500000);
  const [rate,     setRate]     = useState(14);
  const [term,     setTerm]     = useState(36);
  const [income,   setIncome]   = useState(80000);

  const emi          = useMemo(() => calcEMI(loan, rate, term), [loan, rate, term]);
  const totalPayment = emi * term;
  const totalInterest= totalPayment - loan;
  const affordable   = emi <= income * 0.4;

  const schedule = useMemo(() => {
    const r = rate / 100 / 12;
    let bal  = loan;
    return Array.from({ length: Math.min(term, 60) }, (_, i) => {
      const interest  = bal * r;
      const principal = emi - interest;
      bal = Math.max(bal - principal, 0);
      return {
        month: `M${i+1}`,
        principal: Math.round(principal),
        interest:  Math.round(interest),
        balance:   Math.round(bal),
      };
    });
  }, [loan, rate, term, emi]);

  const fmt = v => `PKR ${Math.round(v).toLocaleString()}`;

  return (
    <div className="p-6 space-y-6 animate-in">
      <div>
        <h1 className="section-title">EMI Calculator</h1>
        <p className="section-subtitle">Calculate your equated monthly instalment instantly</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Sliders */}
        <div className="glass-card space-y-6 xl:col-span-1">
          <h2 className="font-display font-semibold text-white">Loan Parameters</h2>

          {[
            { label:'Loan Amount',    value:loan,   set:setLoan,   min:10000,  max:10000000, step:10000,  prefix:'PKR', id:'slider-amount' },
            { label:'Annual Rate',    value:rate,   set:setRate,   min:1,      max:36,       step:0.5,    suffix:'%',  id:'slider-rate' },
            { label:'Term (months)',  value:term,   set:setTerm,   min:6,      max:360,      step:6,      suffix:'mo', id:'slider-term' },
            { label:'Monthly Income', value:income, set:setIncome, min:10000,  max:1000000,  step:5000,   prefix:'PKR',id:'slider-income' },
          ].map(({ label, value, set, min, max, step, prefix, suffix, id }) => (
            <div key={id}>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm text-slate-400">{label}</label>
                <span className="text-sm font-semibold text-white">
                  {prefix}{value.toLocaleString()}{suffix}
                </span>
              </div>
              <input id={id} type="range" min={min} max={max} step={step} value={value}
                onChange={e => set(Number(e.target.value))}
                className="w-full h-2 bg-dark-500 rounded-full appearance-none cursor-pointer
                           [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                           [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary-500
                           [&::-webkit-slider-thumb]:shadow-glow [&::-webkit-slider-thumb]:cursor-pointer"
              />
              <div className="flex justify-between text-xs text-slate-600 mt-1">
                <span>{prefix}{min.toLocaleString()}{suffix}</span>
                <span>{prefix}{max.toLocaleString()}{suffix}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Results */}
        <div className="xl:col-span-2 space-y-4">
          {/* EMI display */}
          <div className={`glass-card border-2 text-center ${affordable ? 'border-emerald-500/30' : 'border-rose-500/30'}`}>
            <p className="text-slate-400 text-sm uppercase tracking-wider mb-1">Monthly EMI</p>
            <p className="text-5xl font-display font-bold text-gradient">{fmt(emi)}</p>
            <span className={`badge mt-3 ${affordable ? 'badge-success' : 'badge-danger'}`}>
              {affordable ? '✓ Affordable' : '⚠ High EMI — exceeds 40% of income'}
            </span>

            <div className="grid grid-cols-3 gap-4 mt-5 pt-5 border-t border-dark-500">
              {[
                { icon: DollarSign, label:'Principal',      value: fmt(loan),         color:'text-primary-400' },
                { icon: Percent,    label:'Total Interest', value: fmt(totalInterest), color:'text-accent-rose' },
                { icon: Calendar,   label:'Total Payment',  value: fmt(totalPayment),  color:'text-accent-teal' },
              ].map(({ icon:Icon, label, value, color }) => (
                <div key={label} className="text-center">
                  <Icon size={18} className={`mx-auto mb-1 ${color}`} />
                  <p className={`text-lg font-bold ${color}`}>{value}</p>
                  <p className="text-xs text-slate-500">{label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Amortisation chart */}
          <div className="glass-card">
            <h2 className="font-display font-semibold text-white mb-4">Amortisation Schedule</h2>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={schedule} margin={{ top:5, right:10, bottom:0, left:0 }}>
                <defs>
                  <linearGradient id="gp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="gb" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#2dd4bf" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2d2d4e" />
                <XAxis dataKey="month" tick={{ fill:'#64748b', fontSize:10 }} axisLine={false}
                  interval={Math.floor(schedule.length/6)} />
                <YAxis tick={{ fill:'#64748b', fontSize:10 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background:'#1a1a27', border:'1px solid #2d2d4e', borderRadius:'10px', fontSize:'11px' }}
                  formatter={v => [`PKR ${v.toLocaleString()}`]} />
                <Area type="monotone" dataKey="principal" stroke="#6366f1" fill="url(#gp)" strokeWidth={2} dot={false} name="Principal" />
                <Area type="monotone" dataKey="balance"   stroke="#2dd4bf" fill="url(#gb)" strokeWidth={2} dot={false} name="Balance" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
