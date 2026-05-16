import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Brain, Eye, EyeOff, Mail, Lock, User, Phone, Loader2 } from 'lucide-react';

export default function LoginPage() {
  const [tab, setTab]       = useState('login');
  const [show, setShow]     = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm]     = useState({ name:'', email:'', password:'', phone:'' });
  const { login, signup }   = useAuth();
  const navigate            = useNavigate();

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      if (tab === 'login') {
        await login(form.email, form.password);
        toast.success('Welcome back!');
      } else {
        await signup(form.name, form.email, form.password, form.phone);
        toast.success('Account created!');
      }
      navigate('/');
    } catch (err) {
      toast.error(err.response?.data?.detail || err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-hero-gradient relative overflow-hidden">
      {/* Background glows */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-accent-purple/15 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md animate-in">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-purple shadow-glow-lg mb-4 animate-float">
            <Brain size={28} className="text-white" />
          </div>
          <h1 className="font-display text-3xl font-bold text-gradient">Smart Loan AI</h1>
          <p className="text-slate-400 text-sm mt-1">AI-powered loan intelligence platform</p>
        </div>

        <div className="glass-card">
          {/* Tabs */}
          <div className="flex bg-dark-800 rounded-xl p-1 mb-6">
            {['login','signup'].map(t => (
              <button
                key={t}
                id={`tab-${t}`}
                onClick={() => setTab(t)}
                className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                  tab === t
                    ? 'bg-primary-600 text-white shadow-glow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {t === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            ))}
          </div>

          <form id="auth-form" onSubmit={handleSubmit} className="space-y-4">
            {tab === 'signup' && (
              <>
                <div className="input-group">
                  <label className="input-label">Full Name</label>
                  <div className="relative">
                    <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input id="input-name" type="text" required value={form.name}
                      onChange={set('name')} placeholder="Muhammad Ali"
                      className="input-field pl-10" />
                  </div>
                </div>
                <div className="input-group">
                  <label className="input-label">Phone (optional)</label>
                  <div className="relative">
                    <Phone size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input id="input-phone" type="tel" value={form.phone}
                      onChange={set('phone')} placeholder="+92 300 1234567"
                      className="input-field pl-10" />
                  </div>
                </div>
              </>
            )}

            <div className="input-group">
              <label className="input-label">Email Address</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                <input id="input-email" type="email" required value={form.email}
                  onChange={set('email')} placeholder="you@example.com"
                  className="input-field pl-10" />
              </div>
            </div>

            <div className="input-group">
              <label className="input-label">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
                <input id="input-password" type={show ? 'text' : 'password'} required value={form.password}
                  onChange={set('password')} placeholder="••••••••" minLength={6}
                  className="input-field pl-10 pr-10" />
                <button type="button" onClick={() => setShow(s=>!s)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                  {show ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button id="submit-auth" type="submit" disabled={loading} className="btn-primary w-full mt-2">
              {loading ? <Loader2 size={18} className="animate-spin" /> : null}
              {loading ? 'Please wait…' : tab === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-xs text-slate-500 mt-5">
            {tab === 'login'
              ? "Don't have an account? "
              : "Already have an account? "}
            <button onClick={() => setTab(tab === 'login' ? 'signup' : 'login')}
              className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
              {tab === 'login' ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
