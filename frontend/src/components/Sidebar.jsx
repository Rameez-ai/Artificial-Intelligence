import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, CheckCircle, Calculator, TrendingUp,
  MessageSquare, Star, Building2, LogOut, Brain, ChevronRight, Moon, Sun
} from 'lucide-react';

const NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/loan-checker', icon: CheckCircle, label: 'Loan Eligibility' },
  { to: '/emi-calculator', icon: Calculator, label: 'EMI Calculator' },
  { to: '/simulation', icon: TrendingUp, label: 'Simulation' },
  { to: '/recommendations', icon: Star, label: 'Recommendations' },
  { to: '/bank-comparison', icon: Building2, label: 'Bank Comparison' },
  { to: '/chatbot', icon: MessageSquare, label: 'AI Chatbot' },
];

export default function Sidebar({ theme, toggleTheme }) {
  const { profile, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  return (
    <aside className="w-64 shrink-0 bg-dark-800 border-r border-dark-600 flex flex-col min-h-screen sticky top-0">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-dark-600">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent-purple flex items-center justify-center shadow-glow">
            <Brain size={18} className="text-white" />
          </div>
          <div>
            <p className="font-display font-bold text-white text-sm leading-tight">Smart Loan</p>
            <p className="text-xs text-primary-400 font-medium">AI Platform</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV.map(({ to, icon: Icon, label, badge }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${isActive
                ? 'bg-primary-600/20 text-primary-400 border border-primary-500/30 shadow-glow'
                : 'text-slate-400 hover:bg-dark-700 hover:text-slate-200'
              }`
            }
          >
            <Icon size={18} className="shrink-0" />
            <span className="flex-1">{label}</span>
            {badge && (
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-accent-purple/30 text-accent-purple border border-accent-purple/40">
                {badge}
              </span>
            )}
            <ChevronRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
          </NavLink>
        ))}
      </nav>

      {/* User + Logout */}
      <div className="px-3 py-4 border-t border-dark-600 space-y-2">
        <button
          onClick={toggleTheme}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-slate-400
                     hover:bg-primary-500/10 hover:text-primary-400 transition-all duration-200"
        >
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>
        {profile && (
          <div className="px-3 py-2 rounded-xl bg-dark-700 border border-dark-500">
            <p className="text-xs font-semibold text-slate-200 truncate">{profile.name || 'User'}</p>
            <p className="text-xs text-slate-500 truncate">{profile.email}</p>
          </div>
        )}
        <button
          id="logout-btn"
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-slate-400
                     hover:bg-rose-500/10 hover:text-rose-400 transition-all duration-200"
        >
          <LogOut size={16} />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
