import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import LoanCheckerPage from './pages/LoanCheckerPage';
import EMICalculatorPage from './pages/EMICalculatorPage';
import SimulationPage from './pages/SimulationPage';
import ChatbotPage from './pages/ChatbotPage';
import RecommendationsPage from './pages/RecommendationsPage';
import BankComparisonPage from './pages/BankComparisonPage';

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="w-10 h-10 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppLayout({ children, theme, toggleTheme }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar theme={theme} toggleTheme={toggleTheme} />
      <main className="flex-1 min-w-0 overflow-auto">
        {children}
      </main>
    </div>
  );
}

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={
        <ProtectedRoute>
          <AppLayout theme={theme} toggleTheme={toggleTheme}><DashboardPage /></AppLayout>
        </ProtectedRoute>
      } />
      <Route path="/loan-checker" element={
        <ProtectedRoute>
          <AppLayout theme={theme} toggleTheme={toggleTheme}><LoanCheckerPage /></AppLayout>
        </ProtectedRoute>
      } />
      <Route path="/emi-calculator" element={
        <ProtectedRoute>
          <AppLayout theme={theme} toggleTheme={toggleTheme}><EMICalculatorPage /></AppLayout>
        </ProtectedRoute>
      } />
      <Route path="/simulation" element={
        <ProtectedRoute>
          <AppLayout theme={theme} toggleTheme={toggleTheme}><SimulationPage /></AppLayout>
        </ProtectedRoute>
      } />
      <Route path="/chatbot" element={
        <ProtectedRoute>
          <AppLayout theme={theme} toggleTheme={toggleTheme}><ChatbotPage /></AppLayout>
        </ProtectedRoute>
      } />
      <Route path="/recommendations" element={
        <ProtectedRoute>
          <AppLayout theme={theme} toggleTheme={toggleTheme}><RecommendationsPage /></AppLayout>
        </ProtectedRoute>
      } />
      <Route path="/bank-comparison" element={
        <ProtectedRoute>
          <AppLayout theme={theme} toggleTheme={toggleTheme}><BankComparisonPage /></AppLayout>
        </ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
