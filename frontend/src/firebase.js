// Firebase Web SDK v9+ configuration
// Replace the values below with your actual Firebase project config
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey:            import.meta.env.VITE_FIREBASE_API_KEY            || "AIzaSy-placeholder",
  authDomain:        import.meta.env.VITE_FIREBASE_AUTH_DOMAIN        || "smart-loan-ai.firebaseapp.com",
  projectId:         import.meta.env.VITE_FIREBASE_PROJECT_ID         || "smart-loan-ai",
  storageBucket:     import.meta.env.VITE_FIREBASE_STORAGE_BUCKET     || "smart-loan-ai.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID|| "123456789",
  appId:             import.meta.env.VITE_FIREBASE_APP_ID             || "1:123456789:web:abcdef",
};

const app  = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db   = getFirestore(app);
export default app;
