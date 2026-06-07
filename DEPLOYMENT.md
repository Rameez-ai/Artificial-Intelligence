# Deployment Guide for SmartLoan AI

This guide provides a step-by-step process for deploying the SmartLoan AI web platform completely **for free**.

The application consists of two main components:
1. **FastAPI Backend (Python)**: Hosted on **Hugging Face Spaces** (Free Docker Space tier).
2. **React Frontend (Vite)**: Hosted on **Vercel** (Free Hobby plan).

---

## Prerequisites
1. A **GitHub Account** containing your repository: `https://github.com/Rameez-ai/Artificial-Intelligence`.
2. A **Hugging Face Account** (register for free at [huggingface.co](https://huggingface.co)).
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
7. Remove any line breaks/spaces if possible, or keep the raw copy to paste into Hugging Face Secrets.

---

## Phase 2: Deploy the FastAPI Backend to Hugging Face Spaces (100% Free & No Card Required)
Hugging Face Spaces allows you to host Docker containers for free without requiring any credit card or payment verification.

### 1. Create a Hugging Face Account
1. Go to [Hugging Face](https://huggingface.co/) and sign up for a free account.
2. Verify your email address.

### 2. Create a New Space
1. Log in and click on your profile picture in the top-right corner, then select **New Space**.
2. Configure your Space:
   - **Space Name**: `smart-loan-ai-backend` (or any custom name)
   - **License**: `mit`
   - **Select the Space SDK**: **Docker**
   - **Docker Template**: **Blank**
   - **Space Hardware**: **Cpu basic • 2 vCPU • 16 GB • Free**
   - **Visibility**: **Public** (required so your React frontend can access the API)
3. Click **Create Space**.

### 3. Add Environment Variables (Secrets)
Before pushing the code, configure your secrets so they are ready:
1. Inside your Space, click the **Settings** tab.
2. Scroll down to the **Variables and Secrets** section.
3. Click **New secret** to add the following variables:
   - **Name**: `FIREBASE_PROJECT_ID` | **Value**: `smart-loan-ai-ed653`
   - **Name**: `FIREBASE_CREDENTIALS_JSON` | **Value**: *(Paste the entire text contents of your Firebase serviceAccountKey.json)*
   - **Name**: `JWT_SECRET_KEY` | **Value**: `OosAZbut30XjP7jVZeUmeI2jklxmUxBcryr3DYHK47G`
   - **Name**: `GEMINI_API_KEY` | **Value**: *(Your Gemini API key)*
   - **Name**: `DEBUG` | **Value**: `false`

### 4. Deploy your Code to the Space
Since Hugging Face spaces use their own Git remote, you can sync your existing repository easily:
1. Open terminal on your computer in the root directory of your project (`Smart Loan AI`).
2. Add the Hugging Face space repository as a Git remote (copy the exact git command from the Space landing page, under "Use via Git"):
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/smart-loan-ai-backend
   ```
3. Push your backend code to Hugging Face:
   ```bash
   git push hf main --force
   ```
4. Hugging Face will automatically read the `backend/Dockerfile` (which has been configured to expose port `7860`) and build/run your FastAPI application.
5. Once the build status changes from `Building` to `Running`, your API is live!
6. Copy the URL of your Space app (click **Embed this Space** under the three dots menu at the top-right, and copy the direct link URL. It should look like: `https://YOUR_USERNAME-smart-loan-ai-backend.hf.space`). This is your backend API URL.

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
| `VITE_API_BASE_URL` | *Paste your Hugging Face Space URL copied in Phase 2* (e.g., `https://username-smart-loan-ai-backend.hf.space`) | Connects React frontend to FastAPI backend |
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

## Phase 4: Configure CORS on Hugging Face
To allow your frontend on Vercel to securely call your Hugging Face API, configure CORS on the backend by setting the CORS_ORIGINS secret.

1. Go back to your **Hugging Face Space** -> **Settings** tab.
2. Scroll to the **Variables and Secrets** section.
3. Click **New secret**:
   - **Name**: `CORS_ORIGINS`
   - **Value**: `["https://your-vercel-deployment-url.vercel.app"]` (Replace with your actual Vercel URL, and keep the array format with square brackets and quotes).
4. Save the secret. Hugging Face will automatically restart the space with the updated CORS configuration.

---

## Phase 5: Verification
1. Open your Vercel URL in your browser.
2. Sign Up a new user or log in.
3. Test the features:
   - Run a **Loan Eligibility Check**.
   - Use the **EMI Calculator**.
   - Check **Recommendations** and **Bank Comparisons**.
   - Chat with the **AI Assistant** to verify Gemini connectivity.
