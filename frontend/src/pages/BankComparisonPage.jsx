import { useState, useEffect, useMemo } from 'react';
import { listBanks, matchBanks, policyChat } from '../api/bank';
import toast from 'react-hot-toast';
import {
  Search, SlidersHorizontal, Building2, Star, ChevronDown, ChevronUp,
  X, Send, Loader2, ChevronRight, BadgeCheck, AlertTriangle, MessageSquare
} from 'lucide-react';

/* ── helpers ──────────────────────────────────────────────────────────────── */
function LikelihoodBar({ value }) {
  const color = value >= 70 ? 'bg-emerald-500' : value >= 40 ? 'bg-amber-500' : 'bg-rose-500';
  return (
    <div className="flex items-center gap-2">
      <div className="progress-bar w-20 h-1.5">
        <div className={`progress-fill ${color}`} style={{ width: `${value}%` }} />
      </div>
      <span className={`text-xs font-semibold ${value >= 70 ? 'text-emerald-400' : value >= 40 ? 'text-amber-400' : 'text-rose-400'}`}>
        {value}%
      </span>
    </div>
  );
}

/* ── PolicyChatPanel ──────────────────────────────────────────────────────── */
function PolicyChatPanel({ bank, onClose }) {
  const [q, setQ] = useState('');
  const [msgs, setMsgs] = useState([]);
  const [busy, setBusy] = useState(false);

  async function ask(e) {
    e.preventDefault();
    if (!q.trim()) return;
    const question = q.trim();
    setQ('');
    setMsgs(m => [...m, { role: 'user', text: question }]);
    setBusy(true);
    try {
      const res = await policyChat({ question, bank_name: bank.bank_name });
      setMsgs(m => [...m, { role: 'bot', text: res.data?.data?.answer || 'No answer' }]);
    } catch {
      setMsgs(m => [...m, { role: 'bot', text: 'Could not fetch answer. Is the backend running?' }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div className="flex items-center gap-2">
          <MessageSquare size={16} className="text-accent-purple" />
          <span className="font-semibold text-white text-sm">Policy Q&A — {bank.bank_name}</span>
        </div>
        <button onClick={onClose} className="btn-ghost p-1"><X size={16} /></button>
      </div>
      <div className="flex-1 overflow-y-auto space-y-3 pb-3">
        {msgs.length === 0 && (
          <p className="text-xs text-slate-500 text-center mt-6">
            Ask anything about {bank.bank_name}'s loan policies…
          </p>
        )}
        {msgs.map((m, i) => (
          <div key={i} className={`text-xs px-3 py-2 rounded-xl max-w-[85%] ${m.role === 'user'
              ? 'ml-auto bg-primary-600 text-white'
              : 'bg-dark-600 border border-dark-500 text-slate-300'
            }`}>
            {m.text}
          </div>
        ))}
        {busy && (
          <div className="bg-dark-600 border border-dark-500 px-3 py-2 rounded-xl w-fit">
            <div className="flex gap-1">
              {[0, 1, 2].map(d => (
                <div key={d} className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-bounce"
                  style={{ animationDelay: `${d * 0.15}s` }} />
              ))}
            </div>
          </div>
        )}
      </div>
      <form onSubmit={ask} className="flex gap-2 mt-2 shrink-0">
        <input value={q} onChange={e => setQ(e.target.value)}
          placeholder="Ask about eligibility, docs…" disabled={busy}
          className="input-field flex-1 text-xs py-2" />
        <button type="submit" disabled={busy || !q.trim()} className="btn-primary px-3 py-2">
          <Send size={14} />
        </button>
      </form>
    </div>
  );
}

/* ── BankDetailPanel ──────────────────────────────────────────────────────── */
function BankDetailPanel({ bank, onClose }) {
  const [showChat, setShowChat] = useState(false);

  return (
    <div className="glass-card h-full flex flex-col animate-slide-in">
      {/* Header */}
      <div className="flex items-start justify-between mb-4 shrink-0">
        <div>
          <h3 className="font-display font-bold text-white">{bank.full_name || bank.bank_name}</h3>
          <div className="flex flex-wrap gap-1 mt-1">
            {(bank.loan_types || []).map(t => (
              <span key={t} className="badge-primary text-[10px]">{t}</span>
            ))}
          </div>
        </div>
        <button onClick={onClose} className="btn-ghost p-1 shrink-0"><X size={16} /></button>
      </div>

      {showChat ? (
        <PolicyChatPanel bank={bank} onClose={() => setShowChat(false)} />
      ) : (
        <>
          <div className="space-y-3 flex-1 overflow-y-auto text-sm">
            {[
              ['Min. Income', `PKR ${(bank.min_income || 0).toLocaleString()}/month`],
              ['Min. Credit Score', bank.min_credit_score],
              ['Interest Rate', bank.interest_rate_range],
              ['Max Loan Amount', `PKR ${(bank.max_loan_amount || 0).toLocaleString()}`],
              ['Max Tenure', `${bank.max_tenure_months} months`],
              ['Processing Fee', bank.processing_fee || 'N/A'],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between py-2 border-b border-dark-600">
                <span className="text-slate-400">{k}</span>
                <span className="text-white font-medium text-right ml-2">{v}</span>
              </div>
            ))}

            <div className="pt-1">
              <p className="text-slate-400 text-xs mb-1">Required Documents</p>
              <div className="flex flex-wrap gap-1">
                {(bank.required_documents || []).map(d => (
                  <span key={d} className="badge-info text-[10px]">{d}</span>
                ))}
              </div>
            </div>

            {bank.special_conditions && (
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300">
                ℹ️ {bank.special_conditions}
              </div>
            )}

            {bank.disqualifiers?.length > 0 && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300 space-y-1">
                <p className="font-semibold flex items-center gap-1"><AlertTriangle size={12} /> Eligibility Issues</p>
                {bank.disqualifiers.map((d, i) => <p key={i}>• {d}</p>)}
              </div>
            )}
          </div>

          <button
            id={`policy-chat-${bank.bank_name}`}
            onClick={() => setShowChat(true)}
            className="btn-secondary mt-4 w-full text-sm shrink-0"
          >
            <MessageSquare size={16} className="text-accent-purple" />
            Ask AI about {bank.bank_name} policies
          </button>
        </>
      )}
    </div>
  );
}

/* ── Main Page ────────────────────────────────────────────────────────────── */
export default function BankComparisonPage() {
  const [banks, setBanks] = useState([]);
  const [matched, setMatched] = useState(null);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [banksLoading, setBanksLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [loanType, setLoanType] = useState('all');
  const [sortKey, setSortKey] = useState('approval_likelihood');
  const [sortAsc, setSortAsc] = useState(false);
  const [showFilter, setShowFilter] = useState(false);

  // Profile form for matching
  const [profile, setProfile] = useState({
    income: 60000, loan_amount: 500000, credit_score: 680,
    loan_purpose: 'personal', loan_term: 36, monthly_expenses: 25000, existing_debts: 0,
    employment_status: 'Employed', education: 'Bachelor',
  });
  const [summary, setSummary] = useState('');

  // Load static bank list on mount
  useEffect(() => {
    listBanks()
      .then(r => setBanks(r.data?.data || []))
      .catch(() => toast.error('Could not load banks'))
      .finally(() => setBanksLoading(false));
  }, []);

  // Run matching
  async function runMatch(e) {
    e.preventDefault();
    setLoading(true);
    setMatched(null);
    setSummary('');
    try {
      const res = await matchBanks(profile);
      const d = res.data?.data;
      setMatched(d?.banks || []);
      setSummary(d?.llm_summary || '');
      toast.success(`Matched ${d?.banks?.length || 0} banks!`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Matching failed. Make sure ingest_policies.py has been run.');
    } finally {
      setLoading(false);
    }
  }

  // Display list: use matched (with likelihood) if available, else raw banks
  const displayBanks = matched || banks;

  const allLoanTypes = useMemo(() => {
    const types = new Set();
    banks.forEach(b => b.loan_types?.forEach(t => types.add(t)));
    return ['all', ...types];
  }, [banks]);

  const filtered = useMemo(() => {
    let list = [...displayBanks];
    if (search) list = list.filter(b =>
      b.bank_name.toLowerCase().includes(search.toLowerCase()) ||
      b.full_name?.toLowerCase().includes(search.toLowerCase())
    );
    if (loanType !== 'all') list = list.filter(b => b.loan_types?.includes(loanType));
    list.sort((a, b) => {
      const av = a[sortKey] ?? 0, bv = b[sortKey] ?? 0;
      return sortAsc ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
    });
    return list;
  }, [displayBanks, search, loanType, sortKey, sortAsc]);

  const bestMatch = matched?.[0] || null;

  function toggleSort(key) {
    if (sortKey === key) setSortAsc(a => !a);
    else { setSortKey(key); setSortAsc(false); }
  }

  const SortIcon = ({ k }) => sortKey === k
    ? (sortAsc ? <ChevronUp size={12} /> : <ChevronDown size={12} />)
    : null;

  const setP = k => e => setProfile(p => ({ ...p, [k]: isNaN(e.target.value) ? e.target.value : Number(e.target.value) }));

  return (
    <div className="p-6 space-y-5 animate-in">
      {/* Header */}
      <div>
        <h1 className="section-title">Bank Comparison</h1>
        <p className="section-subtitle">Match your profile against 20 Pakistani banks using AI policy retrieval</p>
      </div>

      {/* Profile form */}
      <div className="glass-card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display font-semibold text-white">Your Financial Profile</h2>
          <button onClick={() => setShowFilter(f => !f)} className="btn-ghost text-xs">
            <SlidersHorizontal size={14} /> {showFilter ? 'Hide' : 'Expand'}
          </button>
        </div>
        <form id="bank-match-form" onSubmit={runMatch}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            {[
              { key: 'income', label: 'Monthly Income (PKR)', type: 'number' },
              { key: 'loan_amount', label: 'Loan Amount (PKR)', type: 'number' },
              { key: 'credit_score', label: 'Credit Score', type: 'number' },
              { key: 'loan_purpose', label: 'Loan Purpose', type: 'select', opts: ['personal', 'home', 'car', 'business', 'agriculture'] },
            ].map(({ key, label, type, opts }) => (
              <div key={key} className="input-group">
                <label className="input-label">{label}</label>
                {type === 'select'
                  ? <select id={`bp-${key}`} value={profile[key]} onChange={setP(key)} className="input-field">
                    {opts.map(o => <option key={o} value={o}>{o.charAt(0).toUpperCase() + o.slice(1)}</option>)}
                  </select>
                  : <input id={`bp-${key}`} type="number" value={profile[key]} onChange={setP(key)} className="input-field" />
                }
              </div>
            ))}
          </div>
          {showFilter && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              {[
                { key: 'loan_term', label: 'Loan Term (months)' },
                { key: 'monthly_expenses', label: 'Monthly Expenses' },
                { key: 'existing_debts', label: 'Existing Debts' },
              ].map(({ key, label }) => (
                <div key={key} className="input-group">
                  <label className="input-label">{label}</label>
                  <input id={`bp-${key}`} type="number" value={profile[key]} onChange={setP(key)} className="input-field" />
                </div>
              ))}
              <div className="input-group">
                <label className="input-label">Employment</label>
                <select id="bp-employment" value={profile.employment_status} onChange={setP('employment_status')} className="input-field">
                  {['Employed', 'Self-Employed', 'Part-Time', 'Retired', 'Unemployed'].map(o => <option key={o}>{o}</option>)}
                </select>
              </div>
            </div>
          )}
          <button id="run-bank-match" type="submit" disabled={loading} className="btn-primary">
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Building2 size={16} />}
            {loading ? 'Matching…' : 'Find Best Banks (AI Match)'}
          </button>
        </form>
      </div>

      {/* LLM summary + Best Match */}
      {(summary || bestMatch) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {summary && (
            <div className="glass-card border-primary-500/30 bg-primary-500/5">
              <p className="text-xs text-primary-400 font-semibold uppercase tracking-wider mb-2 flex items-center gap-1">
                <Star size={12} /> AI Summary
              </p>
              <p className="text-sm text-slate-200">{summary}</p>
            </div>
          )}
          {bestMatch && (
            <div className="glass-card border-2 border-emerald-500/40 bg-emerald-500/5 shadow-[0_0_20px_rgba(16,185,129,0.15)] cursor-pointer"
              onClick={() => setSelected(bestMatch)}>
              <div className="flex items-center gap-2 mb-2">
                <BadgeCheck size={16} className="text-emerald-400" />
                <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Best Match</span>
              </div>
              <h3 className="font-display font-bold text-white">{bestMatch.full_name}</h3>
              <div className="flex items-center gap-4 mt-2">
                <div>
                  <p className="text-xs text-slate-400">Approval Likelihood</p>
                  <LikelihoodBar value={bestMatch.approval_likelihood ?? 0} />
                </div>
                <div>
                  <p className="text-xs text-slate-400">Rate</p>
                  <p className="text-sm font-semibold text-white">{bestMatch.interest_rate_range}</p>
                </div>
              </div>
              <p className="text-xs text-emerald-400/70 mt-2 flex items-center gap-1">
                Click for full details <ChevronRight size={12} />
              </p>
            </div>
          )}
        </div>
      )}

      {/* Filters + Table + Detail panel */}
      <div className={`flex gap-4 ${selected ? 'grid grid-cols-1 xl:grid-cols-3' : ''}`}>
        {/* Table */}
        <div className={`glass-card p-0 overflow-hidden ${selected ? 'xl:col-span-2' : 'w-full'}`}>
          {/* Toolbar */}
          <div className="flex items-center gap-3 p-4 border-b border-dark-600 flex-wrap">
            <div className="relative flex-1 min-w-48">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input id="bank-search" value={search} onChange={e => setSearch(e.target.value)}
                placeholder="Search banks…" className="input-field pl-9 py-2 text-sm" />
            </div>
            <select id="loan-type-filter" value={loanType} onChange={e => setLoanType(e.target.value)}
              className="input-field py-2 text-sm w-40">
              {allLoanTypes.map(t => <option key={t} value={t}>{t === 'all' ? 'All Loan Types' : t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
            </select>
            <span className="text-xs text-slate-500">{filtered.length} banks</span>
          </div>

          {banksLoading ? (
            <div className="flex items-center justify-center h-48">
              <Loader2 size={28} className="animate-spin text-primary-500" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table id="bank-table" className="data-table w-full">
                <thead>
                  <tr>
                    {[
                      { key: 'bank_name', label: 'Bank' },
                      { key: 'min_income', label: 'Min. Income' },
                      { key: 'interest_rate_range', label: 'Rate Range' },
                      { key: 'max_loan_amount', label: 'Max Amount' },
                      { key: 'approval_likelihood', label: 'Approval %' },
                    ].map(({ key, label }) => (
                      <th key={key} className="cursor-pointer select-none hover:text-primary-400 transition-colors"
                        onClick={() => toggleSort(key)}>
                        <div className="flex items-center gap-1">{label} <SortIcon k={key} /></div>
                      </th>
                    ))}
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(bank => (
                    <tr key={bank.bank_name}
                      className={`cursor-pointer transition-colors ${selected?.bank_name === bank.bank_name ? 'bg-primary-500/10' : ''}`}
                      onClick={() => setSelected(bank)}>
                      <td>
                        <div>
                          <p className="font-semibold text-white text-xs">{bank.bank_name}</p>
                          <p className="text-slate-500 text-[10px]">{bank.full_name}</p>
                        </div>
                      </td>
                      <td className="text-xs">PKR {(bank.min_income || 0).toLocaleString()}</td>
                      <td className="text-xs whitespace-nowrap">{bank.interest_rate_range}</td>
                      <td className="text-xs">PKR {(bank.max_loan_amount || 0).toLocaleString()}</td>
                      <td>
                        {bank.approval_likelihood !== undefined
                          ? <LikelihoodBar value={bank.approval_likelihood} />
                          : <span className="text-slate-600 text-xs">Run match</span>
                        }
                      </td>
                      <td>
                        <button className="btn-ghost text-xs px-2 py-1 text-primary-400">
                          Details <ChevronRight size={12} />
                        </button>
                      </td>
                    </tr>
                  ))}
                  {filtered.length === 0 && (
                    <tr><td colSpan={6} className="text-center text-slate-500 py-10 text-sm">No banks match your filter</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Detail panel */}
        {selected && (
          <div className="xl:col-span-1">
            <BankDetailPanel bank={selected} onClose={() => setSelected(null)} />
          </div>
        )}
      </div>
    </div>
  );
}
