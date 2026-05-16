import { useState } from 'react';
import { predictLoan } from '../api/loan';
import toast from 'react-hot-toast';
import { CheckCircle, XCircle, Loader2, ChevronDown, TrendingUp, Shield, Lightbulb } from 'lucide-react';

const INITIAL = {
  age:                30,
  annual_income:      '', monthly_expenses: '', existing_debts: '',
  loan_amount:        '', loan_term:         36,
  credit_score:       650,
  employment_status:  'Employed',
  education:          'Bachelor',
  gender:             'Other',
};

const EMPLOYMENT = ['Employed','Self-Employed','Part-Time','Retired','Unemployed'];
const EDUCATION  = ['PhD','Master','Bachelor','Associate','High School'];

export default function LoanCheckerPage() {
  const [form, setForm]     = useState(INITIAL);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const payload = {
        ...form,
        age:              Number(form.age),
        annual_income:    Number(form.annual_income),
        monthly_expenses: Number(form.monthly_expenses),
        existing_debts:   Number(form.existing_debts),
        loan_amount:      Number(form.loan_amount),
        loan_term:        Number(form.loan_term),
        credit_score:     Number(form.credit_score),
      };
      const res = await predictLoan(payload);
      setResult(res.data?.data);
      toast.success('Prediction complete!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  }

  const approved = result?.approved;
  const prob     = result ? Math.round((result.probability || 0) * 100) : 0;

  return (
    <div className="p-6 space-y-6 animate-in">
      <div>
        <h1 className="section-title">Loan Eligibility Checker</h1>
        <p className="section-subtitle">Random Forest ML model predicts your approval probability</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Form */}
        <div className="glass-card">
          <form id="loan-check-form" onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="input-group">
                <label className="input-label">Age</label>
                <input id="inp-age" type="number" required min={18} max={100} value={form.age}
                  onChange={set('age')} placeholder="30" className="input-field" />
              </div>
              <div className="input-group">
                <label className="input-label">Gender</label>
                <select id="inp-gender" value={form.gender} onChange={set('gender')} className="input-field">
                  {['Male', 'Female', 'Other'].map(g => <option key={g}>{g}</option>)}
                </select>
              </div>
              <div className="input-group">
                <label className="input-label">Annual Income (PKR)</label>
                <input id="inp-income" type="number" required min={0} value={form.annual_income}
                  onChange={set('annual_income')} placeholder="600000" className="input-field" />
              </div>
              <div className="input-group">
                <label className="input-label">Monthly Expenses (PKR)</label>
                <input id="inp-expenses" type="number" required min={0} value={form.monthly_expenses}
                  onChange={set('monthly_expenses')} placeholder="30000" className="input-field" />
              </div>
              <div className="input-group">
                <label className="input-label">Existing Debts (PKR)</label>
                <input id="inp-debts" type="number" min={0} value={form.existing_debts}
                  onChange={set('existing_debts')} placeholder="0" className="input-field" />
              </div>
              <div className="input-group">
                <label className="input-label">Loan Amount (PKR)</label>
                <input id="inp-loan-amount" type="number" required min={1000} value={form.loan_amount}
                  onChange={set('loan_amount')} placeholder="500000" className="input-field" />
              </div>
              <div className="input-group">
                <label className="input-label">Loan Term (months)</label>
                <input id="inp-term" type="number" min={6} max={360} value={form.loan_term}
                  onChange={set('loan_term')} className="input-field" />
              </div>
              <div className="input-group">
                <label className="input-label">Credit Score</label>
                <input id="inp-credit" type="number" min={300} max={850} value={form.credit_score}
                  onChange={set('credit_score')} className="input-field" />
              </div>
              <div className="input-group">
                <label className="input-label">Employment Status</label>
                <select id="inp-employment" value={form.employment_status} onChange={set('employment_status')} className="input-field">
                  {EMPLOYMENT.map(e => <option key={e}>{e}</option>)}
                </select>
              </div>
              <div className="input-group">
                <label className="input-label">Education</label>
                <select id="inp-education" value={form.education} onChange={set('education')} className="input-field">
                  {EDUCATION.map(e => <option key={e}>{e}</option>)}
                </select>
              </div>
            </div>

            <button id="submit-loan-check" type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? <Loader2 size={18} className="animate-spin" /> : <TrendingUp size={18} />}
              {loading ? 'Analysing…' : 'Check Eligibility'}
            </button>
          </form>
        </div>

        {/* Result panel */}
        {result ? (
          <div className="space-y-4 animate-in">
            {/* Verdict */}
            <div className={`glass-card text-center border-2 ${
              approved ? 'border-emerald-500/40 shadow-[0_0_30px_rgba(16,185,129,0.2)]'
                       : 'border-rose-500/40 shadow-[0_0_30px_rgba(244,63,94,0.2)]'
            }`}>
              <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full mb-4 ${
                approved ? 'bg-emerald-500/20' : 'bg-rose-500/20'
              }`}>
                {approved
                  ? <CheckCircle size={40} className="text-emerald-400" />
                  : <XCircle    size={40} className="text-rose-400" />}
              </div>
              <h2 className={`text-2xl font-display font-bold ${approved ? 'text-emerald-400':'text-rose-400'}`}>
                {approved ? 'Likely Approved' : 'Needs Improvement'}
              </h2>

              {/* Probability arc */}
              <div className="mt-4">
                <div className="relative inline-flex items-center justify-center w-32 h-32">
                  <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="52" fill="none" stroke="#2d2d4e" strokeWidth="10"/>
                    <circle cx="60" cy="60" r="52" fill="none"
                      stroke={approved ? '#10b981' : '#f43f5e'}
                      strokeWidth="10"
                      strokeDasharray={`${2*Math.PI*52}`}
                      strokeDashoffset={`${2*Math.PI*52*(1-prob/100)}`}
                      strokeLinecap="round"
                      style={{ transition:'stroke-dashoffset 1s ease' }}
                    />
                  </svg>
                  <span className="absolute text-2xl font-display font-bold text-white">{prob}%</span>
                </div>
                <p className="text-slate-400 text-sm mt-1">Approval Probability</p>
              </div>

              <div className="flex justify-center gap-3 mt-3">
                <span className="badge-info">Risk: {result.risk_level}</span>
                <span className="badge-primary">Confidence: {result.ensemble?.confidence}</span>
              </div>
            </div>

            {/* Health score */}
            <div className="glass-card">
              <h3 className="font-semibold text-white flex items-center gap-2 mb-3">
                <Shield size={16} className="text-accent-teal" /> Financial Health
                {result.financial_health?.grade && (
                  <span className="ml-auto badge-primary text-xs">{result.financial_health.grade}</span>
                )}
              </h3>
              <div className="space-y-2">
                {Object.entries(result.financial_health?.components || {}).map(([k, v]) => (
                  <div key={k} className="flex items-center gap-3">
                    <span className="text-xs text-slate-400 w-32 capitalize">{k.replace('_score','').replace(/_/g,' ')}</span>
                    <div className="progress-bar flex-1">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${Math.min(Number(v) / 25 * 100, 100)}%`,
                          background: 'linear-gradient(to right, #4f46e5, #2dd4bf)'
                        }}
                      />
                    </div>
                    <span className="text-xs text-slate-300 w-8 text-right">{Math.round(Number(v))}</span>
                  </div>
                ))}
                {result.financial_health?.metrics && (
                  <div className="mt-3 pt-3 border-t border-dark-500 grid grid-cols-3 gap-2 text-center">
                    {[
                      ['Savings Rate',  `${result.financial_health.metrics.savings_rate ?? 0}%`],
                      ['DTI Ratio',     `${result.financial_health.metrics.debt_to_income_ratio ?? 0}%`],
                      ['Monthly Free',  `PKR ${Number(result.financial_health.metrics.monthly_disposable ?? 0).toLocaleString()}`],
                    ].map(([label, val]) => (
                      <div key={label}>
                        <p className="text-xs font-semibold text-white">{val}</p>
                        <p className="text-[10px] text-slate-500 mt-0.5">{label}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Suggestions */}
            {result.suggestions?.length > 0 && (
              <div className="glass-card space-y-2">
                <h3 className="font-semibold text-white flex items-center gap-2 mb-3">
                  <Lightbulb size={16} className="text-accent-amber" /> Improvement Suggestions
                </h3>
                {result.suggestions.map((s, i) => (
                  <div key={i} className="flex gap-2 text-xs text-slate-300 p-2 rounded-lg bg-dark-600/50">
                    <span className="text-accent-amber shrink-0">→</span>
                    <span>{s.suggestion || s.impact}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="glass-card flex flex-col items-center justify-center text-center h-64 text-slate-500">
            <TrendingUp size={40} className="mb-3 opacity-30" />
            <p className="text-sm">Fill in the form and click<br/><span className="text-primary-400">Check Eligibility</span> to see results</p>
          </div>
        )}
      </div>
    </div>
  );
}
