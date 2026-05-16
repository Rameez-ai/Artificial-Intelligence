import { createContext, useContext, useState, useEffect } from 'react';
import { auth } from '../firebase';
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile as fbUpdateProfile,
} from 'firebase/auth';
import * as authApi from '../api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]         = useState(null);
  const [profile, setProfile]   = useState(null);
  const [loading, setLoading]   = useState(true);

  // Listen to Firebase auth state — but use backend JWT for API calls
  useEffect(() => {
    const unsub = onAuthStateChanged(auth, async (fbUser) => {
      if (fbUser) {
        setUser(fbUser);
        // Try to load backend profile
        const token = localStorage.getItem('sl_token');
        if (token) {
          try {
            const res = await authApi.getProfile();
            setProfile(res.data?.data || null);
          } catch (_) { /* ignore */ }
        }
      } else {
        setUser(null);
        setProfile(null);
      }
      setLoading(false);
    });
    return unsub;
  }, []);

  // ── Sign up ───────────────────────────────────────────────────────
  async function signup(name, email, password, phone = '') {
    // Register with backend (Firebase admin creates the user)
    const res = await authApi.signup(name, email, password, phone);
    const data = res.data?.data;
    if (data?.access_token) {
      localStorage.setItem('sl_token', data.access_token);
      setProfile(data.user);
    }
    // Also create Firebase client session
    try {
      const cred = await createUserWithEmailAndPassword(auth, email, password);
      await fbUpdateProfile(cred.user, { displayName: name });
    } catch (_) { /* already created server-side */ }
    return data;
  }

  // ── Log in ────────────────────────────────────────────────────────
  async function login(email, password) {
    // Backend JWT
    const res  = await authApi.login(email, password);
    const data = res.data?.data;
    if (data?.access_token) {
      localStorage.setItem('sl_token', data.access_token);
      setProfile(data.user);
    }
    // Firebase client session
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (_) { /* ignore if firebase creds differ */ }
    return data;
  }

  // ── Log out ───────────────────────────────────────────────────────
  async function logout() {
    localStorage.removeItem('sl_token');
    setProfile(null);
    await signOut(auth);
  }

  const isAuthenticated = !!localStorage.getItem('sl_token');

  return (
    <AuthContext.Provider value={{ user, profile, loading, isAuthenticated, signup, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
};
