# Deployment Guide for SmartLoan AI

This guide provides a step-by-step process for deploying the SmartLoan AI web platform completely **for free**.

The application consists of two main components:
1. **FastAPI Backend (Python)**: Hosted on **Render** (Free Web Service tier).
2. **React Frontend (Vite)**: Hosted on **Vercel** (Free Hobby plan).

---

## Prerequisites
1. A **GitHub Account** containing your repository: `https://github.com/Rameez-ai/Artificial-Intelligence`.
2. A **Render Account** (register for free at [render.com](https://render.com)).
3. A **Vercel Account** (register for free at [vercel.com](https://vercel.com)).
4. Access to your **Firebase Project Console** (to retrieve credentials).
5. A **Gemini API Key** (optional, for the AI Chatbot feature).

---

## Phase 1: Prepare Firebase Service Credentials
Because the FastAPI backend runs on a remote server, it needs to access Firebase Firestore. To do this securely without pushing secrets to GitHub, we pass the service account credentials as a single environment variable string.

1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Select your project: `smart-loan-ai-ed653`.
3. Click the gear icon ⚙️ (Project Settings) -> **Service accounts**.
4. Click **Generate new private key** -> **Generate key**.
5. Save the generated `.json` file to your computer.
6. Open this JSON file in any text editor, select everything, and copy it to your clipboard.
7. Remove any line breaks/spaces if possible, or keep the raw copy to paste into Render (Render supports multi-line environment variables).

---

## Phase 2: Deploy the FastAPI Backend to Render (100% Free)
Render is a cloud hosting platform that offers a free tier for web services.

### 1. Create a New Web Service
1. Log in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** -> **Web Service**.
3. Select **Build and deploy from a Git repository**.
4. Connect your GitHub account and select your repository: `Artificial-Intelligence`.

### 2. Configure the Service
Set the following options on the configuration page:
- **Name**: `smart-loan-ai-backend` (or any custom name)
- **Region**: Select the closest region to your target users (e.g., `Singapore` or `Oregon`)
- **Branch**: `main`
- **Root Directory**: `backend` *(Crucial: This tells Render to compile inside the backend directory)*
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Instance Type**: **Free** ($0/month)

### 3. Add Environment Variables
Click **Advanced** -> **Add Environment Variable** and add the following keys:

| Key | Value | Description |
|---|---|---|
| `JWT_SECRET_KEY` | *Generates a random secret string* (e.g., `OosAZbut30XjP7jVZeUmeI2jklxmUxBcryr3DYHK47G`) | Used to secure JWT tokens |
| `FIREBASE_PROJECT_ID` | `smart-loan-ai-ed653` | Your Firebase project identifier |
| `FIREBASE_CREDENTIALS_JSON` | *Paste the entire content of the Firebase service account JSON file you copied in Phase 1* | Securely authenticates with Firestore |
| `GEMINI_API_KEY` | *Your Google AI Studio Gemini API Key* | Required for AI chatbot answers |
| `DEBUG` | `false` | Sets production mode |

### 4. Deploy
1. Click **Create Web Service**.
2. Render will build and deploy your service.
3. Once the build finishes and shows `Live`, copy the URL of your backend (e.g., `https://smart-loan-ai-backend.onrender.com`).
4. **Note on Render Free Tier**: Free services spin down after 15 minutes of inactivity. When a new request arrives, Render will spin it back up, which may cause a 30-50 second delay on the first load ("cold start").

---

## Phase 3: Deploy the React Frontend to Vercel (100% Free)
Vercel is the premier hosting provider for frontends built with Vite.

### 1. Import your Project
1. Log in to the [Vercel Dashboard](https://vercel.com).
2. Click **Add New** -> **Project**.
3. Select your repository: `Artificial-Intelligence`.

### 2. Configure Build Settings
Configure the project details:
- **Framework Preset**: **Vite** (detected automatically)
- **Root Directory**: `frontend` *(Crucial: This tells Vercel that the React app resides here)*
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### 3. Add Environment Variables
Toggle the **Environment Variables** section and add:

| Key | Value | Description |
|---|---|---|
| `VITE_API_BASE_URL` | *Paste your Render backend URL copied in Phase 2* (e.g., `https://smart-loan-ai-backend.onrender.com`) | Connects React frontend to FastAPI backend |
| `VITE_FIREBASE_API_KEY` | `AIzaSyDSaXm-yjR4ZxYNcDCl-h2oywL4f25T32g` | Firebase web API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | `smart-loan-ai-ed653.firebaseapp.com` | Firebase authentication domain |
| `VITE_FIREBASE_PROJECT_ID` | `smart-loan-ai-ed653` | Firebase project ID |
| `VITE_FIREBASE_STORAGE_BUCKET` | `smart-loan-ai-ed653.firebasestorage.app` | Firebase storage bucket |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | `123799283228` | Firebase sender ID |
| `VITE_FIREBASE_APP_ID` | `1:123799283228:web:65af501fd580583ee4a1d9` | Firebase application ID |

### 4. Deploy
1. Click **Deploy**.
2. Vercel will build your static files and deploy them globally.
3. Once completed, you will receive a free custom production URL (e.g., `https://artificial-intelligence.vercel.app`).
4. Vercel deployments do not have "cold start" delays because they are hosted on a global Edge CDN.

---

## Phase 4: Configure CORS on Render
To allow your frontend on Vercel to securely call your Render backend API, configure CORS on the backend.

1. Go back to your **Render Dashboard** and select your `smart-loan-ai-backend` web service.
2. Go to **Environment Variables** and add the following variable:
   - **Key**: `CORS_ORIGINS`
   - **Value**: `["https://your-vercel-deployment-url.vercel.app"]` (Replace with your actual Vercel URL, and keep the array format with square brackets and quotes).
3. Save changes. Render will automatically redeploy the service with updated CORS origins.

---

## Phase 5: Verification
1. Open your Vercel URL in your browser.
2. Sign Up a new user or log in.
3. Test the features:
   - Run a **Loan Eligibility Check**.
   - Use the **EMI Calculator**.
   - Check **Recommendations** and **Bank Comparisons**.
   - Chat with the **AI Assistant** to verify Gemini connectivity.
